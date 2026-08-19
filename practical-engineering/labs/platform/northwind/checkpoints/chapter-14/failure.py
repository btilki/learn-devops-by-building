from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

EVALUATE_PATH = Path(__file__).resolve().parent / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_14_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def injected_inputs() -> tuple:
    (
        plane_evidence,
        isolation_plan,
        restore_trace,
        verification,
        users,
        tenants,
        isolation,
        leases,
        subjects,
        plane_product,
        reconciliation,
        quota,
        upgrades,
        migrations,
        changes,
        incidents,
        restore_contract,
        expectations,
    ) = (copy.deepcopy(item) for item in MODULE.completed_inputs())
    restore_trace["restores"].append(
        {
            "id": "restore-newest-mixed",
            "snapshot": "plane-newest-corrupt",
            "resource": "kubernetes-control-plane",
            "subject": "plane-reconciler",
            "approved_by": "plane-reconciler",
            "action": "restore-newest",
            "granted_role": "cluster-admin",
            "restored_version": "1.1",
            "last_known_good": "1.1",
            "mixed_backup": True,
            "unofficial": True,
            "source_rewritten": True,
            "result": "allow",
            "roots": [
                "reviewed_intent",
                "artifact_identity",
                "configuration_identity",
                "durable_data",
                "identity_policy",
            ],
        }
    )
    for row in isolation_plan["tenants"]:
        if row["tenant"] == "storefront":
            row["replayed_from"] = "fulfillment"
            row["mutated_tenants"] = ["storefront", "fulfillment"]
            row["restored_version"] = "1.0"
    return (
        plane_evidence,
        isolation_plan,
        restore_trace,
        verification,
        users,
        tenants,
        isolation,
        leases,
        subjects,
        plane_product,
        reconciliation,
        quota,
        upgrades,
        migrations,
        changes,
        incidents,
        restore_contract,
        expectations,
    )


def main() -> None:
    errors = MODULE.evaluate(*injected_inputs())
    required = {
        "mixed backup restore: restore-newest-mixed",
        "cross-tenant replay: storefront/fulfillment",
        "missing last known good: restore-newest-mixed",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"failure did not reject mixed-backup restore: {errors}")
    print("chapter 14 failure: mixed-backup restore correctly rejected")


if __name__ == "__main__":
    main()
