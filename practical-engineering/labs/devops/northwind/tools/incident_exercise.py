#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "incident/response-contract.json"
SCENARIO = ROOT / "fixtures/incident/incompatible-queue-release.json"
EXPECTATIONS = ROOT / "incident/recovery-expectations.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def exercise(
    contract: dict[str, object], scenario: dict[str, object], expectations: dict[str, object]
) -> dict[str, object]:
    declaration = contract["declaration"]
    roles = contract["roles"]
    control = contract["control"]
    communication = contract["communication"]
    mitigation = contract["mitigation"]
    recovery_policy = contract["recovery"]
    release = scenario["release"]
    impact = scenario["impact"]
    samples = scenario["recovery_samples"]
    events: list[dict[str, object]] = []

    user_impact = (
        impact["oldest_message_age_seconds"] > expectations["maximum_oldest_message_age_seconds"]
        and impact["queue_decode_error_ratio"] > 0
    )
    declared = declaration["criteria"] == "user-impact" and user_impact
    events.append(
        {
            "event": "incident_declaration",
            "declared": declared,
            "severity": declaration["severity_model"] if declared else "none",
        }
    )
    distinct_roles = len(set(roles.values())) == len(roles) and "none" not in roles.values()
    events.append({"event": "roles_assigned", "distinct": distinct_roles})
    events.append({"event": "change_freeze", "active": control["change_freeze"] is True})

    release_correlated = (
        release["candidate_producer_schema"] not in release["stable_consumer_schemas"]
        and impact["queue_decode_error_ratio"] > 0
        and impact["pending_v2_messages"] > 0
    )
    events.append(
        {
            "event": "hypothesis_tested",
            "hypothesis": "producer-consumer-schema-mismatch",
            "supported": release_correlated,
            "api_success_can_mislead": impact["api_order_success_ratio"]
            >= expectations["minimum_order_success_ratio"],
        }
    )

    full_rollback_unsafe = (
        impact["pending_v2_messages"] > 0
        and release["candidate_producer_schema"] not in release["stable_consumer_schemas"]
    )
    mixed_recovery = mitigation["decision"] == "rollback-producer-rollforward-consumer"
    events.append(
        {
            "event": "mitigation_selected",
            "full_rollback_unsafe": full_rollback_unsafe,
            "rollback_producer": mixed_recovery and mitigation["rollback_uses_verified_digest"] is True,
            "rollforward_consumer": mixed_recovery and mitigation["rollforward_is_reviewed"] is True,
            "queue_preserved": mitigation["preserve_queue"] is True,
        }
    )

    if communication["cadence_minutes"] > 0:
        cadence = communication["cadence_minutes"]
        update_states = (
            (
                "change-frozen-schema-mismatch-confirmed",
                "consumer compatibility and safe mitigation are still being evaluated",
            ),
            (
                "stable-producer-reconciled-compatible-consumer-deploying",
                "queue drain rate and duplicate effects are not yet verified",
            ),
            (
                "compatible-consumer-active-queue-draining",
                "sustained recovery and terminal order state are not yet verified",
            ),
        )
        update_impacts = (
            {
                "pending_messages": impact["pending_v2_messages"],
                "oldest_message_age_seconds": impact["oldest_message_age_seconds"],
            },
            {
                "pending_messages": samples[0]["pending_messages"],
                "oldest_message_age_seconds": samples[0]["oldest_message_age_seconds"],
            },
            {
                "pending_messages": samples[1]["pending_messages"],
                "oldest_message_age_seconds": samples[1]["oldest_message_age_seconds"],
            },
        )
        events.extend(
            {
                "event": "status_update",
                "minute": minute,
                "internal": communication["internal_audience"],
                "external": communication["external_audience"],
                "impact": {
                    **observed_impact,
                    "affected_journey": "accepted-orders-awaiting-terminal-state",
                },
                "mitigation_state": mitigation_state,
                "uncertainty": uncertainty,
                "next_update_minute": minute + cadence,
            }
            for minute, (mitigation_state, uncertainty), observed_impact in zip(
                (0, cadence, cadence * 2), update_states, update_impacts, strict=True
            )
        )

    sample_results = [
        (
            sample["order_success_ratio"] >= expectations["minimum_order_success_ratio"]
            and sample["oldest_message_age_seconds"]
            <= expectations["maximum_oldest_message_age_seconds"]
            and sample["duplicate_charges"] <= expectations["maximum_duplicate_charges"]
        )
        for sample in samples
    ]
    required = max(
        expectations["minimum_consecutive_samples"], recovery_policy["minimum_consecutive_samples"]
    )
    sustained = len(sample_results) >= required and all(sample_results[-required:])
    terminal_orders = samples[-1]["pending_messages"] == 0
    recovered = (
        mixed_recovery
        and mitigation["preserve_queue"] is True
        and sustained
        and terminal_orders
        and all(
            recovery_policy[key] is True
            for key in (
                "order_success_required",
                "oldest_message_age_required",
                "terminal_orders_required",
                "duplicate_charge_check",
                "desired_actual_reconciled",
            )
        )
    )
    events.append(
        {
            "event": "recovery_evaluated",
            "sample_results": sample_results,
            "required_consecutive_samples": required,
            "terminal_orders": terminal_orders,
            "recovered": recovered,
        }
    )
    return {"events": events, "recovered": recovered}


def main() -> int:
    report = exercise(read(CONTRACT), read(SCENARIO), read(EXPECTATIONS))
    print(json.dumps(report, indent=2))
    return 0 if report["recovered"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
