from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

EVALUATE_PATH = Path(__file__).resolve().parent / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_13_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def injected_inputs() -> tuple:
    (
        model,
        escalation,
        changes,
        incidents,
        users,
        systems,
        ownership,
        subjects,
        plane_product,
        reconciliation,
        brief,
        indicators,
        non_metrics,
        observability,
        incident_interface,
        evidence,
        expectations,
    ) = (copy.deepcopy(item) for item in MODULE.completed_inputs())
    changes["changes"].append(
        {
            "id": "live-plane-patch",
            "resource": "kubernetes-control-plane",
            "subject": "plane-reconciler",
            "approved_by": "plane-reconciler",
            "action": "patch-in-place",
            "granted_role": "cluster-admin",
            "ticket": "fulfillment-warehouse-delay",
            "last_known_good": "1.1",
            "current_version": "1.1",
            "unofficial": True,
            "source_rewritten": True,
            "result": "allow",
        }
    )
    return (
        model,
        escalation,
        changes,
        incidents,
        users,
        systems,
        ownership,
        subjects,
        plane_product,
        reconciliation,
        brief,
        indicators,
        non_metrics,
        observability,
        incident_interface,
        evidence,
        expectations,
    )


def main() -> None:
    errors = MODULE.evaluate(*injected_inputs())
    required = {
        "unofficial plane-admin change: live-plane-patch",
        "plane self-approval: live-plane-patch",
        "missing last known good: live-plane-patch",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"failure did not reject unofficial plane-admin patch: {errors}")
    print("chapter 13 failure: unofficial plane-admin patch correctly rejected")


if __name__ == "__main__":
    main()
