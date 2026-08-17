#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from tools.restore_exercise import exercise
except ModuleNotFoundError:
    from restore_exercise import exercise

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def analyze(failure: bool = False) -> dict[str, bool]:
    contract = read("recovery/restore-contract.json")
    report = exercise(
        contract,
        read("recovery/objectives.json"),
        read("fixtures/recovery/disaster.json"),
        read("fixtures/recovery/backup-manifest.json"),
        read("fixtures/recovery/wal.json"),
    )
    events = report["events"]

    def event(name: str) -> dict[str, object]:
        return next((item for item in events if item["event"] == name), {})

    backups = [item for item in events if item["event"] == "backup_verified"]
    dependencies = [item for item in events if item["event"] == "dependency_restored"]
    backup = contract["backup"]
    authority = contract["authority"]
    restore = contract["restore"]
    reconciliation = contract["reconciliation"]
    recovery = event("recovery_evaluated")
    business = event("business_reconciled")
    checks = {
        "objectives_are_measured": contract["objectives"]["measured_from_exercise"] is True,
        "declared_rpo_is_bounded": contract["objectives"]["rpo_minutes"] == 10,
        "declared_rto_is_bounded": contract["objectives"]["rto_minutes"] == 60,
        "backup_is_encrypted": backup["encrypted"] is True,
        "backup_is_immutable": backup["immutable"] is True,
        "backup_identity_is_isolated": backup["isolated_identity"] is True,
        "manifest_is_verified": backup["manifest_verified_before_restore"] is True,
        "restore_is_tested": backup["restore_tested"] is True,
        "wal_continuity_is_required": backup["continuous_wal_required"] is True,
        "emergency_access_is_attributable": authority["break_glass"]
        == "individual-time-bound",
        "source_evidence_is_read_only": authority["source_evidence_read_only"] is True,
        "restore_actions_are_audited": authority["actions_audited"] is True,
        "restore_uses_clean_environment": restore["clean_environment"] is True,
        "dependency_order_is_declared": restore["dependency_order"]
        == [
            "emergency-identity",
            "infrastructure",
            "postgres-and-wal",
            "durable-queue",
            "workloads",
            "gitops-controller",
        ],
        "controller_is_restored_last": restore["gitops_controller_restored_last"] is True,
        "traffic_waits_for_validation": restore["traffic_blocked_until_validation"] is True,
        "business_reconciliation_is_required": all(reconciliation.values()),
        "corrupt_latest_backup_is_rejected": len(backups) == 2
        and backups[0].get("valid") is False
        and backups[1].get("selected") is True,
        "wal_chain_reaches_safe_point": event("recovery_point_selected").get("wal_continuous")
        is True,
        "dependencies_restore_in_order": [item.get("component") for item in dependencies]
        == [
            "emergency-identity",
            "infrastructure",
            "postgres-and-wal",
            "durable-queue",
            "workloads",
            "gitops-controller",
        ],
        "orders_reconcile_to_terminal": business.get("terminal_orders") == 1000,
        "provider_and_inventory_reconcile": business.get("provider_payments") == 1000
        and business.get("duplicate_charges") == 0
        and business.get("inventory_discrepancies") == 0,
        "measured_rpo_passes": recovery.get("rpo_minutes") == 5,
        "measured_rto_passes": recovery.get("rto_minutes") == 52,
        "traffic_releases_only_after_recovery": recovery.get("traffic_released") is True,
    }
    if failure:
        checks["newest_corrupt_backup_is_not_restored"] = backups[0].get("selected") is False
        checks["older_verified_backup_is_selected"] = backups[1].get("selected") is True
        checks["database_and_queue_close_rpo_gap"] = (
            business.get("database_orders") == 995
            and business.get("queue_orders") == 5
            and business.get("terminal_orders") == 1000
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["corrupt-latest-backup"])
    args = parser.parse_args()
    checks = analyze(args.scenario == "corrupt-latest-backup")
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
