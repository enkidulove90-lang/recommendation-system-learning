"""Stage 8 数据回收（M17 GA4 看板 / M18 事件埋点 Schema / M8 标题线上 A/B）。

选型对齐 docs/content-factory-engineering.md：
  M18 事件埋点 Schema（曝光/滚动/quiz/play/CTA/ab） 【通用设计】
  M17 GA4 事件 + Metabase 看板                  【通用设计】
  M8  标题 A/B：Headline Goat(Wilson+z-test) / Bandito(多臂)  报告 15 / 16

优化（见 docs/content-event-analytics-design.md）：
  P1 事件成为可校验合约（版本 + 公共维度 + emit-time 校验）
  P2 A/B 闭环（稳定随机分配 + 多臂统计宣布胜者）
  P3/P4 全事件带 platform/content_id/session_id/experiment_id，支持归因与漏斗
  P5 snippet 去重 + 可配置滚动档位
  P6 Metabase 改产出可导入原生 SQL + 漏斗/时序卡
  P7 PII/采样合规策略
  P8 quiz/play 字段富集
  P9 多臂 A/B 判定

全部为纯计算 / 结构化产出，无网络依赖。
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "1.0.0"

PLATFORMS = ["xhs", "wechat", "zhihu", "devto", "x_thread", "hn", "reddit", "web"]
SCROLL_BUCKETS = [25, 50, 75, 100]

# Metabase 原生查询模板变量（字面量，勿作 f-string 表达式）
MB_CONTENT_VAR = "{{content_id}}"

# P7 合规策略
PII_POLICY: dict[str, Any] = {
    "session_id": "必须哈希/匿名，禁止明文用户标识",
    "content_id": "仅用内容 hash，不绑个人",
    "sampling_rate": 1.0,
    "consent": "私有部署需补 consent 闸门；开源内容不含",
}

# 公共维度：每个事件必带
COMMON_DIMENSIONS = {
    "event_time": "string",
    "schema_version": "string",
    "platform": "string",
    "content_id": "string",
    "session_id": "string",
    "experiment_id": "string?",
}
COMMON_REQUIRED = ["event_time", "schema_version", "platform", "content_id", "session_id"]


class InvalidEventError(Exception):
    """事件未通过合约校验时抛出（P1）。"""


# ── M18 事件埋点 Schema v1 ───────────────────────────────────────────────
EVENT_SCHEMA: dict[str, dict[str, Any]] = {
    "impression": {
        "description": "文章/组件曝光",
        "fields": {**COMMON_DIMENSIONS, "component": "string"},
        "required": [*COMMON_REQUIRED, "component"],
        "enums": {"platform": PLATFORMS},
    },
    "scroll_depth": {
        "description": "阅读完成度",
        "fields": {**COMMON_DIMENSIONS, "percent": "int"},
        "required": [*COMMON_REQUIRED, "percent"],
        "enums": {"platform": PLATFORMS, "percent": SCROLL_BUCKETS},
    },
    "quiz_answer": {
        "description": "测验作答",
        "fields": {**COMMON_DIMENSIONS, "block_id": "string", "correct": "bool",
                   "question_id": "string?", "option": "string?"},
        "required": [*COMMON_REQUIRED, "block_id", "correct"],
        "enums": {"platform": PLATFORMS},
    },
    "play_run": {
        "description": "代码 playground 运行",
        "fields": {**COMMON_DIMENSIONS, "editor": "string", "ran": "bool",
                   "error": "string?", "code_ref": "string?"},
        "required": [*COMMON_REQUIRED, "editor", "ran"],
        "enums": {"platform": PLATFORMS},
    },
    "cta_click": {
        "description": "CTA 点击（跳转/关注）",
        "fields": {**COMMON_DIMENSIONS, "variant": "string?"},
        "required": [*COMMON_REQUIRED],
        "enums": {"platform": PLATFORMS},
    },
    "ab_assign": {
        "description": "A/B 实验分组分配",
        "fields": {**COMMON_DIMENSIONS, "variant": "string", "algorithm": "string"},
        "required": [*COMMON_REQUIRED, "variant", "algorithm"],
        "enums": {"platform": PLATFORMS, "algorithm": ["hash_stable"]},
    },
}


def _check_type(declared: str, value: Any) -> bool:
    """按字段声明校验 Python 类型（P1）。"""
    if declared.endswith("?"):
        if value is None:
            return True
        declared = declared[:-1]
    if declared.startswith("int"):
        return isinstance(value, int) and not isinstance(value, bool)
    if declared == "bool":
        return isinstance(value, bool)
    if declared.startswith("string"):
        return isinstance(value, str)
    return False


def validate_event(name: str, params: dict[str, Any]) -> dict[str, Any]:
    """校验单个事件是否满足 v1 合约；通过返回规范化副本，否则抛 InvalidEventError。"""
    if name not in EVENT_SCHEMA:
        raise InvalidEventError(f"未知事件类型: {name}")
    meta = EVENT_SCHEMA[name]
    params = dict(params)
    # 必填
    for f in meta["required"]:
        if f not in params or params[f] is None:
            raise InvalidEventError(f"事件 {name} 缺必填字段: {f}")
    # 类型
    for f, val in params.items():
        if f in meta["fields"] and not _check_type(meta["fields"][f], val):
            raise InvalidEventError(f"事件 {name} 字段 {f} 类型不符（期望 {meta['fields'][f]}）")
    # 枚举
    for f, allowed in meta.get("enums", {}).items():
        if f in params and params[f] is not None and params[f] not in allowed:
            raise InvalidEventError(f"事件 {name} 字段 {f}={params[f]!r} 不在允许集 {allowed}")
    return params


@dataclass
class EventSpec:
    name: str
    description: str
    fields: dict[str, str]
    required: list[str]
    sample: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class AnalyticsSpec:
    """M17 + M18：GA4 事件注册 + Metabase 看板 + 埋点 JS 片段 + emit 校验 + A/B 分配。"""

    # ── P1 emit-time 合约强制 ──────────────────────────────────────────
    def emit(self, events: list[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
        """批量产出已校验事件；自动补 schema_version/event_time 缺省值。"""
        out: list[dict[str, Any]] = []
        for name, params in events:
            p = dict(params)
            p.setdefault("schema_version", SCHEMA_VERSION)
            p.setdefault("event_time", _utc_now())
            out.append(validate_event(name, p))
        return out

    # ── P2 A/B 稳定随机分配 ───────────────────────────────────────────
    def assign_ab_variant(self, experiment: str, variants: list[str],
                          session_id: str, salt: str = "") -> tuple[str, dict[str, Any]]:
        """以 session_id 哈希决定变体：同 session 稳定、跨 session 伪随机。"""
        if not variants:
            variant = "control"
        else:
            h = int(hashlib.sha256(
                f"{session_id}|{experiment}|{salt}".encode("utf-8")).hexdigest(), 16)
            variant = variants[h % len(variants)]
        event = validate_event("ab_assign", {
            "platform": "web",
            "content_id": experiment,
            "session_id": session_id,
            "experiment_id": experiment,
            "variant": variant,
            "algorithm": "hash_stable",
            "event_time": _utc_now(),
            "schema_version": SCHEMA_VERSION,
        })
        return variant, event

    # ── M18 事件注册 ──────────────────────────────────────────────────
    def ga4_events(self) -> list[EventSpec]:
        specs: list[EventSpec] = []
        for name, meta in EVENT_SCHEMA.items():
            specs.append(EventSpec(
                name=name, description=meta["description"],
                fields=meta["fields"], required=meta["required"],
                sample=self._sample_for(name),
            ))
        return specs

    @staticmethod
    def _sample_for(name: str) -> dict[str, Any]:
        common = {
            "event_time": "2026-01-01T00:00:00Z", "schema_version": SCHEMA_VERSION,
            "platform": "wechat", "content_id": "cf_2506.07261",
            "session_id": "sid_demo", "experiment_id": "cf_title_ab_2506.07261",
        }
        return {
            "impression": {**common, "component": "title_ab"},
            "scroll_depth": {**common, "percent": 75},
            "quiz_answer": {**common, "block_id": "ix_quiz", "correct": True,
                            "question_id": "q1", "option": "B"},
            "play_run": {**common, "editor": "replit", "ran": True,
                         "error": None, "code_ref": "snippet_A"},
            "cta_click": {**common, "variant": "v2"},
            "ab_assign": {**common, "variant": "v3", "algorithm": "hash_stable"},
        }[name]

    # ── P6 Metabase 看板（可导入原生 SQL + 漏斗/时序卡）─────────────────
    def metabase_dashboard(self, ga4_table: str = "ga4_events") -> dict[str, Any]:
        cards = [
            {"name": "曝光量 by 组件", "visualization": "bar",
             "native_query": f"SELECT component, COUNT(*) AS n FROM {ga4_table} "
                             f"WHERE event='impression' AND content_id={MB_CONTENT_VAR} "
                             f"GROUP BY component ORDER BY n DESC"},
            {"name": "滚动完成度分布", "visualization": "bar",
             "native_query": f"SELECT percent, COUNT(*) AS n FROM {ga4_table} "
                             f"WHERE event='scroll_depth' GROUP BY percent ORDER BY percent"},
            {"name": "测验正确率", "visualization": "bar",
             "native_query": f"SELECT block_id, AVG(CASE WHEN correct THEN 1.0 ELSE 0 END) AS acc "
                             f"FROM {ga4_table} WHERE event='quiz_answer' GROUP BY block_id"},
            {"name": "A/B CTR 对比", "visualization": "bar",
             "native_query": f"SELECT experiment_id, variant, "
                             f"COUNT(*) FILTER (WHERE event='cta_click') * 1.0 / "
                             f"NULLIF(COUNT(*) FILTER (WHERE event='impression'),0) AS ctr "
                             f"FROM {ga4_table} WHERE experiment_id IS NOT NULL "
                             f"GROUP BY experiment_id, variant"},
            {"name": "标题漏斗", "visualization": "funnel",
             "native_query": f"SELECT event, COUNT(DISTINCT session_id) AS sessions "
                             f"FROM {ga4_table} WHERE event IN ('impression','scroll_depth','cta_click') "
                             f"AND content_id={MB_CONTENT_VAR} GROUP BY event"},
            {"name": "每日曝光时序", "visualization": "line",
             "native_query": f"SELECT DATE(event_time) AS day, COUNT(*) AS n "
                             f"FROM {ga4_table} WHERE event='impression' GROUP BY day ORDER BY day"},
        ]
        return {
            "dashboard": "内容工厂回收看板",
            "version": SCHEMA_VERSION,
            "source": ga4_table,
            "cards": cards,
            "regression_tags": ["abt_hook_vs_none", "has_interaction_vs_none"],
        }

    # ── P5 snippet：会话 id + 去重 + A/B 钩子 ──────────────────────────
    def tracking_snippet(self, content_id: str = "", experiment: str = "",
                         variants: list[str] | None = None) -> str:
        variants = variants or []
        ev = "|".join(EVENT_SCHEMA.keys())
        buckets = ",".join(str(b) for b in SCROLL_BUCKETS)
        return (
            "<script>\n"
            f"var CF_CONTENT_ID = {content_id!r};\n"
            f"var CF_EXPERIMENT = {experiment!r};\n"
            "function cfSession(){ if(!localStorage.cf_sid){localStorage.cf_sid="
            "Math.random().toString(36).slice(2);} return localStorage.cf_sid; }\n"
            "function track(event, params){ params=params||{}; "
            "params.event_time=new Date().toISOString(); "
            f"params.schema_version={SCHEMA_VERSION!r}; "
            "params.content_id=CF_CONTENT_ID; params.session_id=cfSession(); "
            "if(window.gtag) gtag('event', event, params); }\n"
            f"// 支持事件：{ev}\n"
            "var cfSent=new Set();\n"
            "document.addEventListener('scroll', function(){\n"
            "  var p=Math.round((window.scrollY+innerHeight)/document.body.scrollHeight*100);\n"
            f"  if([{buckets}].includes(p) && !cfSent.has(p)){{ cfSent.add(p); track('scroll_depth',{{percent:p}}); }}\n"
            "});\n"
            "// A/B：读者首次访问按 session 稳定分配变体，写 ab_assign\n"
            "if(CF_EXPERIMENT && !localStorage[CF_EXPERIMENT]){\n"
            "  var vs=" + str(variants) + "; var idx=Math.floor(Math.random()*vs.length);\n"
            "  localStorage[CF_EXPERIMENT]=vs[idx];\n"
            "  track('ab_assign',{experiment:CF_EXPERIMENT, variant:vs[idx], algorithm:'hash_stable'});\n"
            "}\n"
            "</script>"
        )


# ── M8 标题线上 A/B（Headline Goat 风格：Wilson + z-test）─────────────────
class TitleABTest:
    """两比例 z-test + Wilson 置信区间；95% 置信才宣布胜者。支持多臂（P9）。"""

    Z_95 = 1.96

    @staticmethod
    def _wilson(k: int, n: int, z: float = Z_95) -> tuple[float, float, float]:
        if n <= 0:
            return (0.0, 0.0, 0.0)
        p = k / n
        denom = 1 + z * z / n
        center = (p + z * z / (2 * n)) / denom
        margin = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
        return (p, max(0.0, center - margin), min(1.0, center + margin))

    @classmethod
    def pick_winner(cls, a_clicks: int, a_impr: int,
                    b_clicks: int, b_impr: int, conf: float = 0.95) -> dict[str, Any]:
        z = cls.Z_95 if conf == 0.95 else 1.645
        pa, lo_a, hi_a = cls._wilson(a_clicks, a_impr, z)
        pb, lo_b, hi_b = cls._wilson(b_clicks, b_impr, z)
        p_pool = (a_clicks + b_clicks) / (a_impr + b_impr) if (a_impr + b_impr) else 0.0
        se = math.sqrt(p_pool * (1 - p_pool) * (1 / a_impr + 1 / b_impr)) if (a_impr and b_impr) else 0.0
        z_score = (pb - pa) / se if se > 0 else 0.0
        significant = (lo_a > hi_b) or (lo_b > hi_a)
        winner = "B" if (pb > pa and significant) else ("A" if (pa > pb and significant) else "inconclusive")
        return {
            "A": {"rate": pa, "ci": [lo_a, hi_a], "clicks": a_clicks, "impr": a_impr},
            "B": {"rate": pb, "ci": [lo_b, hi_b], "clicks": b_clicks, "impr": b_impr},
            "z_score": z_score,
            "significant": significant,
            "winner": winner,
            "winner_arm": winner,
            "note": "未达 95% 置信不切换胜者（防假阳性）" if winner == "inconclusive"
                    else f"{winner} 胜出（95% 置信）",
        }

    @classmethod
    def multi_arm_winner(cls, arms: list[tuple[str, int, int]],
                         conf: float = 0.95) -> dict[str, Any]:
        """多臂判定：arms=[(name, clicks, impr), ...]，arms[0] 为 control。
        逐臂与 control 做两比例 z-test，显著且胜出者宣布，否则 inconclusive。"""
        z = cls.Z_95 if conf == 0.95 else 1.645
        computed: list[dict[str, Any]] = []
        for name, clicks, impr in arms:
            p, lo, hi = cls._wilson(clicks, impr, z)
            computed.append({"name": name, "clicks": clicks, "impr": impr,
                             "rate": p, "ci": [lo, hi], "significant_vs_control": False})
        if len(computed) < 2:
            return {"winner": "inconclusive", "arms": computed, "note": "需 ≥2 臂"}
        control = computed[0]
        best: dict[str, Any] | None = None
        for arm in computed[1:]:
            significant = arm["ci"][0] > control["ci"][1]
            lifted = arm["rate"] > control["rate"]
            arm["significant_vs_control"] = bool(significant and lifted)
            if arm["significant_vs_control"] and (best is None or
                                                  arm["rate"] > best["rate"]):
                best = arm
        winner = best["name"] if best else "inconclusive"
        return {
            "winner": winner,
            "control": control,
            "arms": computed,
            "note": (f"{winner} 胜出（95% 置信）" if winner != "inconclusive"
                     else "未达 95% 置信不切换胜者"),
        }


# ════════════════════════════════════════════════════════════════════════
# Phase 2：本地-first 分析引擎（离线即可算漏斗/转化/参与度/AB-lift，无需 GA4/Metabase）
# 建立在 Phase 1 的 v1 合约之上：输入是 validate_event 产出的事件 dict。
# ════════════════════════════════════════════════════════════════════════

class EventCollector:
    """采集已校验事件 → 内存缓冲 + 可选 JSONL 落盘，供本地漏斗/AB 计算与回放。"""

    def __init__(self, path: str | None = None):
        self._path = path
        self._buf: list[dict[str, Any]] = []
        self._errors: list[dict[str, Any]] = []

    def add(self, name: str, params: dict[str, Any]) -> bool:
        try:
            ev = validate_event(name, params)
        except InvalidEventError as e:
            self._errors.append({"event": name, "error": str(e)})
            return False
        # 让落盘事件自带类型名，供 FunnelAnalyzer / _variant_by_session 使用
        # （validate_event 仅校验不写入 event 字段，此处补上以保证事件自描述）
        ev["event"] = name
        self._buf.append(ev)
        return True

    def flush(self) -> int:
        if not self._path:
            return 0
        n = 0
        with open(self._path, "a", encoding="utf-8") as f:
            for ev in self._buf:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
                n += 1
        self._buf = []
        return n

    def load(self, path: str | None = None) -> int:
        p = path or self._path
        if not p or not os.path.exists(p):
            return 0
        n = 0
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                self._buf.append(json.loads(line))
                n += 1
        return n

    def events(self) -> list[dict[str, Any]]:
        return list(self._buf)

    def error_count(self) -> int:
        return len(self._errors)


def _variant_by_session(events: list[dict[str, Any]]) -> dict[str, str]:
    """从 ab_assign 事件建 session_id → variant 映射（A/B 归因用）。"""
    return {e["session_id"]: e.get("variant") for e in events
            if e.get("event") == "ab_assign" and "session_id" in e}


def _sessions_for(events, stage, by=None):
    out = set()
    for e in events:
        if e.get("event") != stage:
            continue
        if by is None:
            out.add(e.get("session_id"))
        else:
            out.add((e.get("session_id"), e.get(by)))
    return out


class FunnelAnalyzer:
    """对一批已采集事件做本地漏斗/转化/参与度/AB-lift 计算。"""

    def __init__(self, events: list[dict[str, Any]]):
        self.events = list(events)

    def funnel(self, stages: list[str], by: str | None = None) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        prev = None
        for st in stages:
            s = _sessions_for(self.events, st, by)
            if by is None:
                count = len(s)
                conv = (count / len(prev)) if prev else 1.0
                out.append({"stage": st, "count": count, "step_conv": round(conv, 4)})
            else:
                sessions = {x[0] for x in s}
                count = len(sessions)
                conv = (count / len(prev)) if prev else 1.0
                breakdown = {}
                for _, val in s:
                    breakdown[val] = breakdown.get(val, 0) + 1
                out.append({"stage": st, "count": count, "step_conv": round(conv, 4),
                            "by_breakdown": breakdown})
            prev = sessions if by else s
        return out

    def conversion(self, from_stage: str, to_stage: str, by: str | None = None):
        f = _sessions_for(self.events, from_stage, by)
        t = _sessions_for(self.events, to_stage, by)
        if by is None:
            fset = {x for x in f}
            tset = {x for x in t}
            return round(len(tset & fset) / len(fset), 4) if fset else 0.0
        fmap, tmap = {}, {}
        for x in f:
            fmap.setdefault(x[1], set()).add(x[0])
        for x in t:
            tmap.setdefault(x[1], set()).add(x[0])
        out = {}
        for val in set(fmap) | set(tmap):
            fs = fmap.get(val, set())
            ts = tmap.get(val, set())
            out[val] = round(len(ts & fs) / len(fs), 4) if fs else 0.0
        return out

    def engagement(self, by: str | None = None) -> dict[str, Any]:
        scrolls = [e["percent"] for e in self.events
                   if e.get("event") == "scroll_depth" and isinstance(e.get("percent"), int)]
        quiz = [e for e in self.events if e.get("event") == "quiz_answer"]
        plays = [e for e in self.events if e.get("event") == "play_run"]
        imp = {e["session_id"] for e in self.events if e.get("event") == "impression"}
        cta = {e["session_id"] for e in self.events if e.get("event") == "cta_click"}
        res = {
            "avg_scroll_percent": round(sum(scrolls) / len(scrolls), 2) if scrolls else 0.0,
            "quiz_correct_rate": round(
                sum(1 for e in quiz if e.get("correct") is True) / len(quiz), 4) if quiz else 0.0,
            "play_ran_rate": round(
                sum(1 for e in plays if e.get("ran") is True) / len(plays), 4) if plays else 0.0,
            "cta_click_rate": round(len(cta & imp) / len(imp), 4) if imp else 0.0,
        }
        if by:
            br: dict[str, Any] = {}
            imp_by, cta_by = {}, {}
            for e in self.events:
                if e.get("event") == "impression":
                    imp_by.setdefault(e.get(by), set()).add(e["session_id"])
                elif e.get("event") == "cta_click":
                    cta_by.setdefault(e.get(by), set()).add(e["session_id"])
            for val in set(imp_by) | set(cta_by):
                fs = imp_by.get(val, set())
                ts = cta_by.get(val, set())
                br[val] = round(len(ts & fs) / len(fs), 4) if fs else 0.0
            res["cta_click_rate_by"] = br
        return res

    def ab_lift(self, metric_event: str = "cta_click") -> dict[str, Any]:
        sv = _variant_by_session(self.events)
        impr: dict[str, int] = {}
        click: dict[str, int] = {}
        for e in self.events:
            if e.get("event") not in ("impression", metric_event):
                continue
            v = sv.get(e.get("session_id"), "control")
            if e.get("event") == "impression":
                impr[v] = impr.get(v, 0) + 1
            else:
                click[v] = click.get(v, 0) + 1
        out = {}
        for v in set(impr) | set(click):
            c = click.get(v, 0)
            i = impr.get(v, 0)
            out[v] = {"clicks": c, "impressions": i, "rate": round(c / i, 4) if i else 0.0}
        return out


def report_ab(events: list[dict[str, Any]]) -> dict[str, Any]:
    """离线 A/B 汇总：按 session 归因 variant → 聚合 impression/cta_click → multi_arm_winner。"""
    sv = _variant_by_session(events)
    impr: dict[str, int] = {}
    click: dict[str, int] = {}
    for e in events:
        if e.get("event") == "impression":
            v = sv.get(e.get("session_id"), "control")
            impr[v] = impr.get(v, 0) + 1
        elif e.get("event") == "cta_click":
            v = sv.get(e.get("session_id"), "control")
            click[v] = click.get(v, 0) + 1
    arms = [(v, click.get(v, 0), impr.get(v, 0)) for v in (set(impr) | set(click))]
    arms.sort(key=lambda a: -a[2])  # 曝光最多者作 control
    return TitleABTest.multi_arm_winner(arms)
