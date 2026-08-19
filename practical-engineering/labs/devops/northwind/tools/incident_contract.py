#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from tools.incident_exercise import exercise
except ModuleNotFoundError:
    from incident_exercise import exercise

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "incident/response-contract.json"
SCENARIO = ROOT / "fixtures/incident/incompatible-queue-release.json"
EXPECTATIONS = ROOT / "incident/recovery-expectations.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(failure: bool = False) -> dict[str, bool]:
    contract = read(CONTRACT)
    scenario = read(SCENARIO)
    report = exercise(contract, scenario, read(EXPECTATIONS))
    events = report["events"]
    impact = scenario["impact"]

    def event(name: str) -> dict[str, object]:
        return next((item for item in events if item["event"] == name), {})

    roles = contract["roles"]
    control = contract["control"]
    communication = contract["communication"]
    mitigation = contract["mitigation"]
    recovery = contract["recovery"]
    learning = contract["learning"]
    updates = [item for item in events if item["event"] == "status_update"]
    expected_update_minutes = [
        0,
        communication["cadence_minutes"],
        communication["cadence_minutes"] * 2,
    ]
    expected_update_impacts = [
        (impact["pending_v2_messages"], impact["oldest_message_age_seconds"]),
        (
            scenario["recovery_samples"][0]["pending_messages"],
            scenario["recovery_samples"][0]["oldest_message_age_seconds"],
        ),
        (
            scenario["recovery_samples"][1]["pending_messages"],
            scenario["recovery_samples"][1]["oldest_message_age_seconds"],
        ),
    ]
    checks = {
        "declaration_uses_user_impact": contract["declaration"]["criteria"] == "user-impact",
        "severity_is_defined": contract["declaration"]["severity_model"] == "SEV-1",
        "roles_are_distinct": len(set(roles.values())) == len(roles) and "none" not in roles.values(),
        "change_freeze_is_available": control["change_freeze"] is True,
        "source_of_truth_exists": control["single_source_of_truth"] is True,
        "hypotheses_are_recorded": control["hypothesis_log"] is True,
        "break_glass_is_individual": control["break_glass"] == "individual-time-bound",
        "communication_has_cadence": communication["cadence_minutes"] == 15,
        "communication_has_audiences": (
            communication["internal_audience"] is True
            and communication["external_audience"] is True
            and communication["next_update_time_required"] is True
        ),
        "mixed_mitigation_is_declared": mitigation["decision"]
        == "rollback-producer-rollforward-consumer",
        "queue_is_preserved": mitigation["preserve_queue"] is True,
        "rollback_uses_verified_artifact": mitigation["rollback_uses_verified_digest"] is True,
        "rollforward_is_reviewed": mitigation["rollforward_is_reviewed"] is True,
        "recovery_requires_sustained_evidence": recovery["minimum_consecutive_samples"] >= 2,
        "recovery_checks_business_outcomes": all(
            recovery[key] is True
            for key in (
                "order_success_required",
                "oldest_message_age_required",
                "terminal_orders_required",
                "duplicate_charge_check",
                "desired_actual_reconciled",
            )
        ),
        "learning_is_blameless": learning["blameless"] is True,
        "timeline_is_preserved": learning["timeline_preserved"] is True,
        "contributing_conditions_are_recorded": learning["contributing_conditions"] is True,
        "actions_are_verifiable": learning["actions_require_owner_deadline_verification"] is True,
        "incident_is_declared_by_trace": event("incident_declaration").get("declared") is True,
        "api_success_does_not_hide_async_failure": event("hypothesis_tested").get(
            "api_success_can_mislead"
        )
        is True,
        "schema_mismatch_is_diagnosed": event("hypothesis_tested").get("supported") is True,
        "full_rollback_is_rejected": event("mitigation_selected").get("full_rollback_unsafe") is True,
        "mixed_recovery_executes": (
            event("mitigation_selected").get("rollback_producer") is True
            and event("mitigation_selected").get("rollforward_consumer") is True
        ),
        "status_updates_execute": (
            len(updates) == 3
            and [item.get("minute") for item in updates] == expected_update_minutes
            and all(item.get("internal") is True and item.get("external") is True for item in updates)
        ),
        "status_updates_include_next_time": len(updates) == 3
        and all(
            item.get("next_update_minute")
            == item.get("minute", 0) + communication["cadence_minutes"]
            for item in updates
        ),
        "status_updates_include_required_content": len(updates) == 3
        and all(
            isinstance(item.get("impact"), dict)
            and (
                item["impact"].get("pending_messages"),
                item["impact"].get("oldest_message_age_seconds"),
            )
            == expected_impact
            and bool(item.get("mitigation_state"))
            and bool(item.get("uncertainty"))
            for item, expected_impact in zip(updates, expected_update_impacts)
        ),
        "recovery_is_sustained": report["recovered"] is True,
    }
    if failure:
        checks["unsafe_queue_purge_is_avoided"] = event("mitigation_selected").get(
            "queue_preserved"
        ) is True
        checks["pending_v2_messages_reach_terminal_state"] = event("recovery_evaluated").get(
            "terminal_orders"
        ) is True
        checks["one_green_sample_is_insufficient"] = event("recovery_evaluated").get(
            "sample_results"
        ) == [False, True, True]
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["incompatible-queue-release"])
    args = parser.parse_args()
    checks = analyze(args.scenario == "incompatible-queue-release")
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
