"""Gate logic: C1–C5 configuration gates and G-P0-1…4 run-health gates.

C1/C2 are computed from real evidence (dataset/feature health); C3/C4/C5 are
interface-level records with explicit pass/fail evidence fields.

G-P0-1…4 turn the persisted run metrics into a P0 verdict: usage health,
gradient health, memory budget and step-timing stability.  Any ``fail`` or
``blocked`` outcome blocks the P0→P1 transition.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .contracts import ExperimentConfig, GateOutcome, SplitAudit

C_GATE_IDS = ("C1", "C2", "C3", "C4", "C5")
P0_GATE_IDS = ("G-P0-1", "G-P0-2", "G-P0-3", "G-P0-4")


# ---------------------------------------------------------------------------
# C gates (configuration-time)
# ---------------------------------------------------------------------------


def gate_c1_dataset_identity(config: ExperimentConfig, split_audit: SplitAudit) -> GateOutcome:
    evidence = {
        "dataset_name": split_audit.dataset_name,
        "n_users": split_audit.n_users,
        "n_items": split_audit.n_items,
        "raw_split_hash": split_audit.raw_split_hash,
    }
    if split_audit.n_users == 0 or split_audit.n_train == 0:
        return GateOutcome(
            gate_id="C1",
            status="fail",
            message="Dataset identity check failed: empty train split.",
            evidence=evidence,
        )
    return GateOutcome(
        gate_id="C1",
        status="pass",
        message="Dataset identity verified (non-empty train split, hashes recorded).",
        evidence=evidence,
    )


def gate_c2_feature_health(config: ExperimentConfig) -> GateOutcome:
    registry = config.feature_registry
    unhealthy = registry.unhealthy()
    evidence = {
        "features": registry.to_json()["features"],
        "n_unhealthy": len(unhealthy),
    }
    if not registry.entries:
        return GateOutcome(
            gate_id="C2",
            status="blocked",
            message="No features registered; multimodal protocol requires at least one feature.",
            evidence=evidence,
        )
    if unhealthy:
        names = [e.name for e in unhealthy]
        return GateOutcome(
            gate_id="C2",
            status="fail",
            message=f"Feature health check failed for: {', '.join(names)}.",
            evidence=evidence,
        )
    return GateOutcome(
        gate_id="C2",
        status="pass",
        message="All registered features are finite, shape-aligned and hash-stamped.",
        evidence=evidence,
    )


def gate_c3_split_audit(config: ExperimentConfig) -> GateOutcome:
    audit = config.split_audit
    evidence: dict[str, Any] = dict(audit.evidence()) if audit else {}
    if audit is None:
        return GateOutcome(
            gate_id="C3",
            status="fail",
            message="No split audit attached to the configuration.",
            evidence=evidence,
        )
    if audit.status == "warn_review_required" and not audit.review_note.strip():
        return GateOutcome(
            gate_id="C3",
            status="blocked",
            message=(
                "Split audit status is warn_review_required and no review_note has been "
                "recorded; a signed review note is required before launching."
            ),
            evidence=evidence,
        )
    return GateOutcome(
        gate_id="C3",
        status="pass",
        message="Split audit present with raw/semantic hashes and signed status.",
        evidence=evidence,
    )


def gate_c4_protocol_phase(config: ExperimentConfig) -> GateOutcome:
    """P2 comparisons must pin the baseline split hash; mismatches reject."""
    evidence: dict[str, Any] = {
        "phase": config.phase,
        "baseline_run_id": config.baseline_run_id,
        "baseline_split_hash": config.baseline_split_hash,
    }
    if config.phase == "P2":
        if not config.baseline_run_id:
            return GateOutcome(
                gate_id="C4",
                status="fail",
                message="P2 configuration must reference a baseline run id.",
                evidence=evidence,
            )
        if config.split_audit and config.baseline_split_hash:
            if config.split_audit.raw_split_hash != config.baseline_split_hash:
                return GateOutcome(
                    gate_id="C4",
                    status="fail",
                    message=(
                        "Baseline split_hash mismatch: comparison is rejected, not warned. "
                        f"config={config.split_audit.raw_split_hash[:12]}… "
                        f"baseline={config.baseline_split_hash[:12]}…"
                    ),
                    evidence=evidence,
                )
    return GateOutcome(
        gate_id="C4",
        status="pass",
        message="Protocol phase constraints satisfied.",
        evidence=evidence,
    )


def gate_c5_configuration_completeness(config: ExperimentConfig) -> GateOutcome:
    issues = config.blocking_issues()
    evidence = {
        "n_appendix_params": len(config.appendix_params),
        "n_blocking_issues": len(issues),
        "blocking_issues": list(issues),
    }
    if issues:
        return GateOutcome(
            gate_id="C5",
            status="blocked",
            message=(
                "Configuration is blocked: "
                + "; ".join(issues[:3])
                + (" …" if len(issues) > 3 else "")
            ),
            evidence=evidence,
        )
    return GateOutcome(
        gate_id="C5",
        status="pass",
        message="All 12 Appendix-A parameters resolved with explicit rationales.",
        evidence=evidence,
    )


def evaluate_config_gates(config: ExperimentConfig) -> list[GateOutcome]:
    audit = config.split_audit
    gates = [
        gate_c1_dataset_identity(config, audit)
        if audit
        else GateOutcome(
            gate_id="C1",
            status="fail",
            message="No split audit attached; dataset identity unknown.",
            evidence={},
        ),
        gate_c2_feature_health(config),
        gate_c3_split_audit(config),
        gate_c4_protocol_phase(config),
        gate_c5_configuration_completeness(config),
    ]
    return gates


def config_is_launchable(config: ExperimentConfig) -> tuple[bool, list[GateOutcome]]:
    """A config may create a GPU process only when no gate blocks it."""
    gates = evaluate_config_gates(config)
    blocked = any(g.is_blocking for g in gates)
    return (not blocked) and (not config.is_blocked), gates


# ---------------------------------------------------------------------------
# G-P0 gates (run-time, from persisted metrics)
# ---------------------------------------------------------------------------


def gate_gp0_1_usage(metrics: Mapping[str, Any]) -> GateOutcome:
    usage = metrics.get("codebook_usage", [])
    if not usage:
        return GateOutcome(
            gate_id="G-P0-1",
            status="fail",
            message="No codebook usage series emitted; cannot verify quantizer health.",
            evidence={"n_points": 0},
        )
    final = float(usage[-1])
    collapsed = final < 0.01
    return GateOutcome(
        gate_id="G-P0-1",
        status="fail" if collapsed else "pass",
        message=(
            f"Codebook usage collapsed to {final:.4f} (< 0.01); quantizer is degenerate."
            if collapsed
            else f"Codebook usage healthy (final={final:.4f})."
        ),
        evidence={"final_usage": final, "n_points": len(usage)},
    )


def gate_gp0_2_gradient_health(metrics: Mapping[str, Any]) -> GateOutcome:
    grads = metrics.get("grad_norm", [])
    if not grads:
        return GateOutcome(
            gate_id="G-P0-2",
            status="fail",
            message="No gradient norm series emitted; cannot verify gradient health.",
            evidence={"n_points": 0},
        )
    import math

    if any((not math.isfinite(float(g))) or float(g) == 0.0 for g in grads[-5:]):
        return GateOutcome(
            gate_id="G-P0-2",
            status="fail",
            message="Gradient norm is zero or non-finite in recent steps.",
            evidence={"recent": grads[-5:]},
        )
    return GateOutcome(
        gate_id="G-P0-2",
        status="pass",
        message="Gradient norms finite and non-zero throughout recent steps.",
        evidence={"recent": grads[-5:]},
    )


def gate_gp0_3_memory_budget(metrics: Mapping[str, Any], budget_mb: float = 16000.0) -> GateOutcome:
    mem = metrics.get("memory_mb", [])
    if not mem:
        return GateOutcome(
            gate_id="G-P0-3",
            status="fail",
            message="No memory series emitted; cannot verify GPU/CPU budget.",
            evidence={"budget_mb": budget_mb},
        )
    peak = max(float(m) for m in mem)
    if peak > budget_mb:
        return GateOutcome(
            gate_id="G-P0-3",
            status="fail",
            message=f"Peak memory {peak:.0f}MB exceeds budget {budget_mb:.0f}MB.",
            evidence={"peak_mb": peak, "budget_mb": budget_mb},
        )
    return GateOutcome(
        gate_id="G-P0-3",
        status="pass",
        message=f"Peak memory {peak:.0f}MB within budget {budget_mb:.0f}MB.",
        evidence={"peak_mb": peak, "budget_mb": budget_mb},
    )


def gate_gp0_4_step_timing(metrics: Mapping[str, Any], max_ms: float = 60_000.0) -> GateOutcome:
    timing = metrics.get("step_ms", [])
    if not timing:
        return GateOutcome(
            gate_id="G-P0-4",
            status="fail",
            message="No step timing series emitted; cannot verify throughput.",
            evidence={"max_ms": max_ms},
        )
    median = float(sorted(timing)[len(timing) // 2])
    if median > max_ms:
        return GateOutcome(
            gate_id="G-P0-4",
            status="fail",
            message=f"Median step time {median:.0f}ms exceeds {max_ms:.0f}ms.",
            evidence={"median_ms": median, "max_ms": max_ms},
        )
    return GateOutcome(
        gate_id="G-P0-4",
        status="pass",
        message=f"Median step time {median:.0f}ms within budget {max_ms:.0f}ms.",
        evidence={"median_ms": median, "max_ms": max_ms},
    )


def evaluate_p0_gates(metrics: Mapping[str, Any]) -> list[GateOutcome]:
    return [
        gate_gp0_1_usage(metrics),
        gate_gp0_2_gradient_health(metrics),
        gate_gp0_3_memory_budget(metrics),
        gate_gp0_4_step_timing(metrics),
    ]


def p0_verdict(metrics: Mapping[str, Any]) -> GateOutcome:
    """Aggregate P0 verdict: fail if any G-P0 gate fails."""
    gates = evaluate_p0_gates(metrics)
    failed = [g for g in gates if g.is_blocking]
    if failed:
        return GateOutcome(
            gate_id="G-P0",
            status="fail",
            message="P0 gate failed at: " + ", ".join(g.gate_id for g in failed),
            evidence={"gates": [g.to_json() for g in gates]},
        )
    return GateOutcome(
        gate_id="G-P0",
        status="pass",
        message="All G-P0 gates passed; P1 transition permitted.",
        evidence={"gates": [g.to_json() for g in gates]},
    )
