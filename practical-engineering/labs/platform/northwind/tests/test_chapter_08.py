from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-08" / "evaluate.py"
FAILURE_PATH = ROOT / "checkpoints" / "chapter-08" / "failure.py"
SPEC = importlib.util.spec_from_file_location("chapter_08_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FAILURE_SPEC = importlib.util.spec_from_file_location("chapter_08_failure", FAILURE_PATH)
assert FAILURE_SPEC and FAILURE_SPEC.loader
FAILURE = importlib.util.module_from_spec(FAILURE_SPEC)
FAILURE_SPEC.loader.exec_module(FAILURE)


def test_completed_plane_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_cluster_admin_plane_subject_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for subject in inputs[1]["subjects"]:
        if subject["id"] == "plane-reconciler":
            subject["granted_role"] = "cluster-admin"
    errors = MODULE.evaluate(*inputs)
    assert "shared plane admin: plane-reconciler/cluster-admin" in errors


def test_cross_tenant_reconcile_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for result in inputs[3]["results"]:
        if result["environment"] == "fulfillment-nonprod":
            result["mutated_tenants"] = ["fulfillment", "storefront"]
    errors = MODULE.evaluate(*inputs)
    assert "cross-tenant reconcile: fulfillment-nonprod/storefront" in errors


def test_failed_upgrade_without_last_known_good_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for upgrade in inputs[3]["upgrades"]:
        upgrade["current_version"] = "1.1"
        upgrade["last_known_good"] = "1.1"
    errors = MODULE.evaluate(*inputs)
    assert "missing last known good: plane-upgrade-1-1" in errors


def test_plane_self_approval_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for upgrade in inputs[3]["upgrades"]:
        upgrade["approved_by"] = "plane-reconciler"
    errors = MODULE.evaluate(*inputs)
    assert "plane self-approval: plane-upgrade-1-1" in errors


def test_sharing_denied_cluster_admin_still_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[0]["forbidden_roles"] = ["dev-cluster-admin"]
    inputs[15]["forbidden_roles"] = ["dev-cluster-admin"]
    for subject in inputs[1]["subjects"]:
        if subject["id"] == "plane-reconciler":
            subject["granted_role"] = "cluster-admin"
    errors = MODULE.evaluate(*inputs)
    assert "shared plane admin: plane-reconciler/cluster-admin" in errors
    inputs[6]["denied"] = [
        item for item in inputs[6]["denied"] if item["id"] != "cluster-admin"
    ]
    errors = MODULE.evaluate(*inputs)
    assert "shared plane admin: plane-reconciler/cluster-admin" not in errors


def test_failure_injection_rejects_cluster_admin_reconcile() -> None:
    errors = MODULE.evaluate(*FAILURE.injected_inputs())
    assert "shared plane admin: plane-reconciler/cluster-admin" in errors
    assert "cross-tenant reconcile: fulfillment-nonprod/storefront" in errors
