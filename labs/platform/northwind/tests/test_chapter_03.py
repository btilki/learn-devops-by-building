from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-03" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_03_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_tenancy_model_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_temporary_cluster_admin_binding_fails() -> None:
    tenants, isolation, roles, sharing, users, expectations = MODULE.completed_inputs()
    roles["bindings"].append(
        {
            "principal": "fulfillment-team",
            "tenant": "fulfillment",
            "role": "cluster-admin",
            "justification": "temporary-to-ship-faster",
        }
    )
    errors = MODULE.evaluate(tenants, isolation, roles, sharing, users, expectations)
    assert "tenant inherits prohibited role: fulfillment/cluster-admin" in errors


def test_missing_change_authority_dimension_fails() -> None:
    tenants, isolation, roles, sharing, users, expectations = MODULE.completed_inputs()
    fulfillment = next(item for item in tenants["tenants"] if item["id"] == "fulfillment")
    fulfillment["isolation_dimensions"] = [
        dim for dim in fulfillment["isolation_dimensions"] if dim != "change-authority"
    ]
    errors = MODULE.evaluate(tenants, isolation, roles, sharing, users, expectations)
    assert "tenant missing isolation dimension: fulfillment/change-authority" in errors
