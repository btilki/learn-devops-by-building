#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "gitops/reconciliation.json"
SCENARIO = ROOT / "fixtures/gitops/reviewed-harmful-intent.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_trace(contract: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    promotion = contract["promotion"]
    controller = contract["controller"]
    reconciliation = contract["reconciliation"]
    recovery_policy = contract["recovery"]
    recovery = scenario["recovery"]
    state = {
        "source_revision": scenario["initial_revision"],
        "applied_revision": scenario["initial_revision"],
        "stable_artifact": scenario["stable_artifact"],
        "candidate_revision": None,
        "sync_status": "synced",
        "runtime_health": "healthy",
    }
    events: list[dict[str, object]] = []

    direct_allowed = promotion["release_automation"] == "direct-cluster-write"
    events.append(
        {
            "event": "release_direct_cluster_write",
            "decision": "allowed" if direct_allowed else "denied",
        }
    )
    if direct_allowed:
        state["applied_revision"] = scenario["revision"]

    proposal_allowed = promotion["release_automation"] == "propose-change"
    events.append(
        {
            "event": "candidate_proposed",
            "revision": scenario["revision"],
            "decision": "accepted" if proposal_allowed else "denied",
        }
    )
    merge_allowed = proposal_allowed and scenario["reviewed"] is True and promotion["merge_authority"] == "protected-review"
    if merge_allowed:
        state["source_revision"] = scenario["revision"]
        state["candidate_revision"] = scenario["revision"]
    events.append(
        {
            "event": "reviewed_revision_merged",
            "revision": scenario["revision"],
            "decision": "accepted" if merge_allowed else "denied",
        }
    )

    pulled = merge_allowed and controller["mode"] == "pull"
    harmful = scenario["runtime_health"] == "degraded" or scenario["order_success_ratio"] < 0.995
    if pulled:
        state["applied_revision"] = scenario["revision"]
        state["runtime_health"] = scenario["runtime_health"]
        events.append({"event": "controller_pulled", "revision": scenario["revision"]})
    if (
        pulled
        and harmful
        and reconciliation["health_timeout"] > 0
        and reconciliation["failed_health_action"] == "pause-and-alert"
    ):
        state["sync_status"] = "paused"
        events.append(
            {
                "event": "harmful_sync_paused",
                "revision": scenario["revision"],
                "source_revision": state["source_revision"],
                "stable_artifact": state["stable_artifact"],
            }
        )

    source_write_allowed = controller["can_write_source"] is True and controller["repository_access"] == "write"
    events.append(
        {
            "event": "controller_source_rewrite",
            "decision": "allowed" if source_write_allowed else "denied",
            "source_revision": state["source_revision"],
        }
    )

    recovery_accepted = (
        recovery_policy["method"] == "reviewed-revert"
        and recovery["reviewed"] is True
        and recovery["revision"] != scenario["revision"]
        and promotion["merge_authority"] == "protected-review"
    )
    if recovery_accepted:
        state["source_revision"] = recovery["revision"]
        events.append(
            {
                "event": "recovery_revision_merged",
                "revision": recovery["revision"],
                "reverts": scenario["revision"],
            }
        )
    if recovery_accepted and controller["mode"] == "pull":
        state["applied_revision"] = recovery["revision"]
        state["candidate_revision"] = None
        state["runtime_health"] = recovery["runtime_health"]
        state["sync_status"] = "synced"
        events.append(
            {
                "event": "recovery_reconciled",
                "revision": recovery["revision"],
                "runtime_health": recovery["runtime_health"],
            }
        )

    return {"events": events, "final_state": state}


def main() -> int:
    trace = run_trace(read(CONTRACT), read(SCENARIO))
    print(json.dumps(trace, indent=2))
    final = trace["final_state"]
    return 0 if final["sync_status"] == "synced" and final["runtime_health"] == "healthy" else 1


if __name__ == "__main__":
    raise SystemExit(main())
