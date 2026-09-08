"""反馈闭环采集器（content_events/feedback_collector.py）。

对应设计 §6（复用设计 05 全文）：只读采集 + SQLite + 指标(ER/SR/FLR/DDR/FR/QS7) +
贝叶斯分组 lift + UCB 时段选择。仅影响「下一批草稿候选队列」，不绕过人工审核。
安全：采集只读，不点赞/评论/关注/删帖；OpenCLI 不可读→collection_failed，等下一窗口。
"""
from __future__ import annotations

import datetime
import json
import math
import os
import sqlite3
import statistics
from typing import Any, Dict, List, Optional, Tuple

from .schema import ContentEvent, EventType


# ---------- SQLite schema（设计 05 §数据存储） ----------

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
  note_id TEXT PRIMARY KEY,
  paper_id TEXT NOT NULL,
  platform TEXT NOT NULL,
  published_at TEXT NOT NULL,
  time_slot TEXT NOT NULL,
  topics_json TEXT NOT NULL,
  features_json TEXT NOT NULL,
  content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS metric_snapshots (
  note_id TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  age_hours INTEGER NOT NULL,
  views INTEGER, likes INTEGER, collects INTEGER,
  comments INTEGER, replies INTEGER, shares INTEGER, follows INTEGER,
  traffic_json TEXT, audience_json TEXT,
  raw_path TEXT NOT NULL,
  PRIMARY KEY (note_id, age_hours)
);
CREATE TABLE IF NOT EXISTS decisions (
  decision_id TEXT PRIMARY KEY,
  made_at TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_key TEXT NOT NULL,
  previous_value REAL, next_value REAL,
  evidence_json TEXT NOT NULL,
  rollback_at TEXT
);
"""


def init_sqlite(path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


# ---------- 指标（设计 05 §指标定义） ----------

def _safe_div(num: float, denom: float) -> float:
    return num / max(denom, 100)  # max(V,100) 防虚高


def compute_metrics(views: int, likes: int, collects: int, comments: int,
                    replies: int, shares: int, follows: int) -> Dict[str, float]:
    V, L, F, C, R, S, N = views, likes, collects, comments, replies, shares, follows
    ER = _safe_div(L + F + C + S, V)
    SR = _safe_div(F, V)
    FLR = (F / max(L, 1)) if L >= 20 else 0.0
    DDR = _safe_div(C + 0.5 * R, V)
    FR = _safe_div(N, V)
    return {"ER": ER, "SR": SR, "FLR": FLR, "DDR": DDR, "FR": FR}


def _winsorize(values: List[float], lo: float = 0.05, hi: float = 0.95) -> List[float]:
    if not values:
        return []
    s = sorted(values)
    n = len(s)
    lo_i = min(n - 1, max(0, int(lo * n)))
    hi_i = min(n - 1, max(0, int(hi * n)))
    low, high = s[lo_i], s[hi_i]
    return [min(max(v, low), high) for v in values]


def qs7_for_posts(per_post: List[Dict[str, float]]) -> List[float]:
    """对一组帖子的 SR/ER/DDR/FR 做 winsorize 后 z 分数，加权得 QS7（设计 05 §指标定义）。

    per_post: 每项含 SR/ER/DDR/FR。样本<2 时 z 不可计算，返回 0.0 占位。
    """
    if len(per_post) < 2:
        return [0.0 for _ in per_post]
    weights = {"SR": 0.45, "ER": 0.25, "DDR": 0.20, "FR": 0.10}
    zs = {}
    for metric in weights:
        vals = _winsorize([p[metric] for p in per_post])
        m = statistics.mean(vals)
        sd = statistics.pstdev(vals) or 1e-9
        zs[metric] = [(v - m) / sd for v in vals]
    return [sum(weights[met] * zs[met][i] for met in weights) for i in range(len(per_post))]


# ---------- 自优化（设计 05 §自动调优逻辑） ----------

def bayes_group_lift(group_qs7: List[float], account_qs7_mean: float,
                     prior_n: int = 12) -> Tuple[float, str]:
    """分组后验 lift（设计 05 §内容与论文优先级）。返回 (lift, 决策)。"""
    n = len(group_qs7)
    if n < 6:
        return 0.0, "样本不足"
    gmean = statistics.mean(group_qs7)
    lift = (gmean * n + account_qs7_mean * prior_n) / (n + prior_n) - account_qs7_mean
    # 90% 置信下界粗略用 ±1.645*sd/sqrt(n)
    sd = statistics.pstdev(group_qs7) or 1e-9
    se = sd / math.sqrt(n)
    ci_low = lift - 1.645 * se
    ci_high = lift + 1.645 * se
    if ci_low > 0.15:
        return min(0.05, max(-0.05, lift)), "priority_up"
    if ci_high < -0.15:
        return max(-0.05, min(0.05, lift)), "priority_down"
    return 0.0, "stable"


def ucb_slot(slot_means: Dict[str, float], slot_unc: Dict[str, float],
             explore: float = 0.20) -> str:
    """UCB 时段选择（设计 05 §发布时间自优化）。强制 explore 探索概率由调用方决定。"""
    best, best_key = -1e9, ""
    for k in slot_means:
        score = slot_means[k] + explore * slot_unc.get(k, 1.0)
        if score > best:
            best, best_key = score, k
    return best_key


# ---------- 采集（守卫 OpenCLI，设计 05 §只读入口） ----------

def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def collect_once(conn: sqlite3.Connection, opencli_fn=None, event_log=None) -> Dict[str, Any]:
    """采集已发布笔记观察窗口。opencli_fn 为可注入的读取函数（测试/真实皆可）。

    无可用读取器时返回 collection_failed，不循环重试（设计 05 §实施 4）。
    event_log 非空时，成功采样后 emit FEEDBACK_SAMPLED（O8 生命周期事件）。
    """
    if opencli_fn is None:
        return {"status": "collection_failed", "reason": "opencli 不可用（沙箱/未登录）"}
    try:
        raw = opencli_fn()
        # raw: list of (note_id, age_hours, metrics_dict, raw_path)
        for note_id, age_hours, m, raw_path in raw:
            conn.execute(
                "INSERT OR REPLACE INTO metric_snapshots "
                "(note_id, observed_at, age_hours, views, likes, collects, comments, "
                " replies, shares, follows, traffic_json, audience_json, raw_path) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (note_id, _now_iso(), age_hours, m.get("views"), m.get("likes"),
                 m.get("collects"), m.get("comments"), m.get("replies"), m.get("shares"),
                 m.get("follows"), json.dumps(m.get("traffic", {})),
                 json.dumps(m.get("audience", {})), raw_path),
            )
        conn.commit()
        if event_log is not None:
            event_log.append(ContentEvent(EventType.FEEDBACK_SAMPLED, "feedback", _now_iso(),
                                         {"sampled": len(raw)}))
        return {"status": "ok", "sampled": len(raw)}
    except Exception as e:  # noqa: BLE001
        return {"status": "collection_failed", "reason": str(e)}


# ---------- 自优化决策（O8：接通死代码 compute_metrics/qs7/bayes/ucb） ----------

def decide_once(conn: sqlite3.Connection) -> Dict[str, Any]:
    """基于已采集快照做分组 lift + UCB 时段选择，写 decisions 表（设计 05 §自动调优）。

    仅影响「下一批草稿候选队列」，不绕过人工审核（设计 05 §结论）。
    样本不足时返回 applied=False（不写表、不决策）。
    """
    rows = conn.execute(
        """
        SELECT p.note_id, p.time_slot,
               s.views, s.likes, s.collects, s.comments, s.replies, s.shares, s.follows
        FROM posts p
        JOIN metric_snapshots s ON s.note_id = p.note_id
        WHERE s.age_hours = (
            SELECT MAX(s2.age_hours) FROM metric_snapshots s2 WHERE s2.note_id = p.note_id
        )
        """
    ).fetchall()
    if len(rows) < 2:
        return {"applied": False, "reason": "insufficient_posts", "n": len(rows)}

    per_post: List[Dict[str, float]] = []
    slot_vals: Dict[str, List[float]] = {}
    for note_id, slot, views, likes, collects, comments, replies, shares, follows in rows:
        m = compute_metrics(
            views or 0, likes or 0, collects or 0, comments or 0,
            replies or 0, shares or 0, follows or 0,
        )
        per_post.append(m)
        slot_vals.setdefault(slot, []).append(m["ER"])

    qs7 = qs7_for_posts(per_post)
    account_mean = statistics.mean(qs7)
    # 分组 lift：以整体 qs7 作为单一分组近似（设计 05 §内容与论文优先级）
    lift, dec = bayes_group_lift(qs7, account_mean)
    slot_means = {k: statistics.mean(v) for k, v in slot_vals.items()}
    slot_unc = {k: statistics.pstdev(v) or 1.0 for k, v in slot_vals.items()}
    best_slot = ucb_slot(slot_means, slot_unc) if slot_means else "unknown"

    dec_id = "dec_" + _now_iso()
    rollback_at = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).isoformat()
    evidence = json.dumps(
        {"qs7": qs7, "account_mean": account_mean, "lift": lift,
         "decision": dec, "best_slot": best_slot},
        ensure_ascii=False,
    )
    conn.execute(
        "INSERT OR REPLACE INTO decisions "
        "(decision_id, made_at, target_type, target_key, previous_value, next_value, "
        "evidence_json, rollback_at) VALUES (?,?,?,?,?,?,?,?)",
        (dec_id, _now_iso(), "time_slot", best_slot, account_mean,
         account_mean + lift, evidence, rollback_at),
    )
    conn.commit()
    return {
        "applied": True, "decision_id": dec_id, "lift": lift,
        "decision": dec, "best_slot": best_slot, "n": len(rows),
    }
