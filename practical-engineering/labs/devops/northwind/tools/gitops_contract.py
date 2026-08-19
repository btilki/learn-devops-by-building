#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from tools.config_delivery import analyze as analyze_config_delivery
    from tools.gitops_trace import run_trace
except ModuleNotFoundError:
    from config_delivery import analyze as analyze_config_delivery
    from gitops_trace import run_trace

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "gitops/reconciliation.json"
FAILURE = ROOT / "fixtures/gitops/reviewed-harmful-intent.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(failure: bool = False) -> dict[str, bool]:
    contract = read(CONTRACT)
    scenario = read(FAILURE)
    trace = run_trace(contract, scenario)
    events = trace["events"]
    final_state = trace["final_state"]

    def event(name: str) -> dict[str, object]:
        return next((item for item in events if item["event"] == name), {})

    source = contract["source"]
    promotion = contract["promotion"]
    controller = contract["controller"]
    reconciliation = contract["reconciliation"]
    exception = contract["exception"]
    recovery = contract["recovery"]
    checks = {
        "desired_state_is_declarative": source["declarative"] is True,
        "desired_state_is_versioned": source["versioned"] is True,
        "production_path_is_protected": source["protected_production_path"] is True,
        "artifact_is_immutable": source["artifact_identity"] == "verified-digest",
        "secrets_are_references": source["secrets"] == "references-only",
        "release_automation_only_proposes": promotion["release_automation"] == "propose-change",
        "merge_authority_is_separate": promotion["merge_authority"] == "protected-review",
        "candidate_handoff_is_explicit": promotion["candidate_field"] == "candidate_artifact",
        "stable_transition_uses_rollout_evidence": promotion["stable_transition"]
        == "reviewed-after-rollout-verification",
        "controller_pulls": controller["mode"] == "pull",
        "controller_cannot_approve_itself": (
            controller["repository_access"] == "read" and controller["can_write_source"] is False
        ),
        "controller_scope_is_bounded": controller["cluster_scope"] == "northwind-namespace",
        "controller_uses_workload_identity": controller["workload_identity"] is True,
        "reconciliation_is_continuous": reconciliation["continuous"] is True,
        "drift_is_detected": reconciliation["drift_detection"] is True,
        "self_heal_is_classified": reconciliation["self_heal"] == "safe-drift-only",
        "pruning_is_guarded": reconciliation["prune"] == "allowlisted-with-confirmation",
        "dependencies_are_ordered": reconciliation["ordered_dependencies"] is True,
        "health_wait_is_bounded": reconciliation["health_timeout"] > 0,
        "failed_health_pauses": reconciliation["failed_health_action"] == "pause-and-alert",
        "exceptions_expire": exception["suspension_time_bound"] is True,
        "exceptions_are_audited": exception["audit_required"] is True,
        "emergency_state_is_backported": exception["backport_required"] is True,
        "recovery_is_reviewed_revert": recovery["method"] == "reviewed-revert",
        "failed_revision_is_retained": recovery["preserve_failed_revision_evidence"] is True,
        "stable_health_is_verified": recovery["verify_stable_health"] is True,
        "release_cluster_write_is_denied": event("release_direct_cluster_write").get("decision")
        == "denied",
        "harmful_sync_reaches_pause": bool(event("harmful_sync_paused")),
        "pause_does_not_rewrite_source": event("harmful_sync_paused").get("source_revision")
        == scenario["revision"],
        "controller_source_write_is_denied": event("controller_source_rewrite").get("decision")
        == "denied",
        "recovery_is_new_reviewed_revision": event("recovery_revision_merged").get("revision")
        == scenario["recovery"]["revision"],
        "recovery_trace_is_healthy": (
            final_state["sync_status"] == "synced"
            and final_state["runtime_health"] == "healthy"
            and final_state["source_revision"] == scenario["recovery"]["revision"]
        ),
    }
    if failure:
        harmful = scenario["runtime_health"] == "degraded" or scenario["order_success_ratio"] < 0.995
        checks["review_does_not_equal_safe"] = scenario["reviewed"] is True and harmful
        checks["controller_stops_amplification"] = harmful and bool(event("harmful_sync_paused"))
        checks["stable_traffic_is_preserved"] = scenario["stable_traffic_healthy"] is True
        checks["controller_does_not_rewrite_intent"] = event("controller_source_rewrite").get(
            "decision"
        ) == "denied"
        checks["recovery_requires_health_evidence"] = (
            recovery["verify_stable_health"] is True and final_state["runtime_health"] == "healthy"
        )
    checks.update({f"config_{name}": value for name, value in analyze_config_delivery().items()})
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["reviewed-harmful-intent"])
    args = parser.parse_args()
    checks = analyze(args.scenario == "reviewed-harmful-intent")
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
