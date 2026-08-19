#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "recovery/restore-contract.json"
OBJECTIVES = ROOT / "recovery/objectives.json"
DISASTER = ROOT / "fixtures/recovery/disaster.json"
MANIFEST = ROOT / "fixtures/recovery/backup-manifest.json"
WAL = ROOT / "fixtures/recovery/wal.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exercise(
    contract: dict[str, object],
    objectives: dict[str, object],
    disaster: dict[str, object],
    manifest: dict[str, object],
    wal: dict[str, object],
) -> dict[str, object]:
    events: list[dict[str, object]] = []
    selected: dict[str, object] | None = None

    for candidate in manifest["candidates"]:
        actual = digest(ROOT / candidate["path"])
        valid = actual == candidate["expected_sha256"]
        events.append(
            {
                "event": "backup_verified",
                "backup_id": candidate["backup_id"],
                "valid": valid,
                "selected": valid and selected is None,
            }
        )
        if valid and selected is None:
            selected = candidate

    backup_policy = contract["backup"]
    restore_policy = contract["restore"]
    reconciliation = contract["reconciliation"]
    objectives_policy = contract["objectives"]
    selected_backup = read(ROOT / selected["path"]) if selected else None
    wal_continuous = (
        selected_backup is not None
        and wal["base_backup_id"] == selected_backup["backup_id"]
        and wal["continuous_from_minute"] <= selected_backup["base_minute"]
        and wal["continuous_to_minute"] == disaster["last_safe_database_minute"]
    )
    rpo_minutes = disaster["incident_minute"] - wal["continuous_to_minute"]
    events.append(
        {
            "event": "recovery_point_selected",
            "backup_id": selected_backup["backup_id"] if selected_backup else "none",
            "wal_continuous": wal_continuous,
            "recovery_point_minute": wal["continuous_to_minute"],
            "rpo_minutes": rpo_minutes,
        }
    )

    required_order = [
        "emergency-identity",
        "infrastructure",
        "postgres-and-wal",
        "durable-queue",
        "workloads",
        "gitops-controller",
    ]
    declared_order = restore_policy["dependency_order"]
    order_valid = declared_order == required_order
    elapsed_minutes = 0
    for component in declared_order:
        elapsed_minutes += disaster["restore_durations_minutes"].get(component, 0)
        events.append(
            {
            "event": "dependency_restored",
            "component": component,
                "minute": elapsed_minutes,
            }
        )

    terminal_orders = (
        wal["orders_after_replay"] + disaster["durable_queue_orders_after_safe_point"]
    )
    rto_minutes = (
        elapsed_minutes + disaster["restore_durations_minutes"]["business-reconciliation"]
    )
    business_valid = (
        terminal_orders == objectives["required_terminal_orders"]
        and terminal_orders == disaster["accepted_orders"]
        and disaster["provider_payments"] == terminal_orders
        and disaster["duplicate_charges"] <= objectives["maximum_duplicate_charges"]
        and disaster["inventory_discrepancies"]
        <= objectives["maximum_inventory_discrepancies"]
        and disaster["desired_revision"] == disaster["restored_revision"]
    )
    events.append(
        {
            "event": "business_reconciled",
            "database_orders": wal["orders_after_replay"],
            "queue_orders": disaster["durable_queue_orders_after_safe_point"],
            "terminal_orders": terminal_orders,
            "provider_payments": disaster["provider_payments"],
            "duplicate_charges": disaster["duplicate_charges"],
            "inventory_discrepancies": disaster["inventory_discrepancies"],
            "desired_actual_match": disaster["desired_revision"]
            == disaster["restored_revision"],
        }
    )

    policy_ready = (
        all(backup_policy.values())
        and contract["authority"]
        == {
            "break_glass": "individual-time-bound",
            "source_evidence_read_only": True,
            "actions_audited": True,
        }
        and restore_policy["clean_environment"] is True
        and order_valid
        and restore_policy["gitops_controller_restored_last"] is True
        and restore_policy["traffic_blocked_until_validation"] is True
        and all(reconciliation.values())
        and objectives_policy["measured_from_exercise"] is True
    )
    recovered = (
        policy_ready
        and selected_backup is not None
        and wal_continuous
        and business_valid
        and rpo_minutes <= objectives["maximum_rpo_minutes"]
        and rto_minutes <= objectives["maximum_rto_minutes"]
    )
    events.append(
        {
            "event": "recovery_evaluated",
            "rpo_minutes": rpo_minutes,
            "rto_minutes": rto_minutes,
            "business_valid": business_valid,
            "traffic_released": recovered,
        }
    )
    return {"events": events, "recovered": recovered}


def main() -> int:
    report = exercise(
        read(CONTRACT), read(OBJECTIVES), read(DISASTER), read(MANIFEST), read(WAL)
    )
    print(json.dumps(report, indent=2))
    return 0 if report["recovered"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
