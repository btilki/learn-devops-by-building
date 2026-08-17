#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "gitops/config-delivery.json"
EXPECTATIONS = ROOT / "gitops/config-expectations.json"
SCENARIO = ROOT / "fixtures/gitops/config-promotion.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_trace(
    contract: dict[str, object],
    expectations: dict[str, object],
    scenario: dict[str, object],
) -> dict[str, object]:
    candidate = scenario["candidate"]
    threshold = expectations["minimum_order_success_ratio"]
    state = {
        "artifact": scenario["artifact_before"],
        "active_config": scenario["initial_active_version"],
        "candidate_config": None,
        "promotion_status": "idle",
        "override_active": True,
    }
    events: list[dict[str, object]] = []

    proposal_accepted = (
        contract["source"]["versioned"] is True
        and contract["source"]["protected_review"] is True
        and candidate["reviewed"] is True
        and candidate["schema_valid"] is True
    )
    if proposal_accepted:
        state["candidate_config"] = candidate["version"]
        state["promotion_status"] = "promoting"
    events.append({"event": "config_proposed", "accepted": proposal_accepted})

    observed_order = [item["environment"] for item in scenario["environment_observations"]]
    required_order = contract["promotion"]["order"]
    for observation in scenario["environment_observations"] if proposal_accepted else []:
        healthy = observation["order_success_ratio"] >= threshold
        events.append(
            {
                "event": "environment_evaluated",
                "environment": observation["environment"],
                "healthy": healthy,
            }
        )
        if not healthy:
            if contract["promotion"]["production_failure_action"] == "freeze-candidate":
                state["promotion_status"] = "frozen"
                events.append(
                    {
                        "event": "config_candidate_frozen",
                        "candidate": state["candidate_config"],
                        "active_config": state["active_config"],
                        "environment": observation["environment"],
                    }
                )
            break

    artifact_separate = (
        contract["promotion"]["artifact_and_config_separate"] is True
        and scenario["artifact_before"] == scenario["artifact_after"]
    )
    if artifact_separate:
        state["artifact"] = scenario["artifact_after"]
    events.append({"event": "artifact_identity_checked", "unchanged": artifact_separate})

    recovery = scenario["recovery"]
    recovered = (
        state["promotion_status"] == "frozen"
        and contract["recovery"]["method"] == "reviewed-config-revert"
        and recovery["reviewed"] is True
        and recovery["version"] == expectations["initial_active_version"]
        and recovery["order_success_ratio"] >= threshold
    )
    if recovered:
        state["active_config"] = recovery["version"]
        state["candidate_config"] = None
        state["promotion_status"] = "recovered"
    events.append({"event": "reviewed_config_recovery", "accepted": recovered})

    override = scenario["emergency_override"]
    expired = override["observed_minute"] >= override["expires_minute"]
    duration = override["expires_minute"] - override["created_minute"]
    override_removed = (
        expired
        and duration <= contract["emergency_override"]["maximum_minutes"]
        and contract["emergency_override"]["auto_remove_at_expiry"] is True
        and bool(override["backport_revision"])
    )
    if override_removed:
        state["override_active"] = False
    events.append({"event": "emergency_override_expired", "removed": override_removed})

    return {
        "observed_order": observed_order,
        "required_order": required_order,
        "events": events,
        "final_state": state,
    }


def analyze() -> dict[str, bool]:
    contract = read(CONTRACT)
    expectations = read(EXPECTATIONS)
    scenario = read(SCENARIO)
    trace = run_trace(contract, expectations, scenario)
    events = trace["events"]
    final = trace["final_state"]

    def event(name: str) -> dict[str, object]:
        return next((item for item in events if item["event"] == name), {})

    observations = scenario["environment_observations"]
    return {
        "runtime_contract_is_reused": contract["source"]["runtime_contract"]
        == "config/runtime-contract.json",
        "promotion_order_is_enforced": trace["required_order"]
        == expectations["promotion_order"]
        and trace["observed_order"] == expectations["promotion_order"],
        "review_and_schema_gate_the_candidate": event("config_proposed").get("accepted") is True,
        "development_and_staging_pass": all(
            item["order_success_ratio"] >= expectations["minimum_order_success_ratio"]
            for item in observations[:2]
        ),
        "production_observation_rejects_candidate": observations[2]["order_success_ratio"]
        < expectations["minimum_order_success_ratio"],
        "failed_promotion_keeps_last_known_good": event("config_candidate_frozen").get(
            "active_config"
        )
        == expectations["initial_active_version"]
        and event("config_candidate_frozen").get("candidate")
        == expectations["candidate_version"],
        "binary_and_configuration_are_separate": event("artifact_identity_checked").get(
            "unchanged"
        )
        is True,
        "recovery_is_reviewed_and_verified": event("reviewed_config_recovery").get("accepted")
        is True
        and final["promotion_status"] == "recovered",
        "active_configuration_is_reported": contract["reconciliation"]["report_active_version"]
        is True,
        "emergency_override_expires_and_is_backported": event(
            "emergency_override_expired"
        ).get("removed")
        is True
        and final["override_active"] is False,
    }


def main() -> int:
    checks = analyze()
    report = {"trace": run_trace(read(CONTRACT), read(EXPECTATIONS), read(SCENARIO)), "checks": checks}
    report["ok"] = all(checks.values())
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
