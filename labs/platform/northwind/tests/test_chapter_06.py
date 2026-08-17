from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-06" / "evaluate.py"
FAILURE_PATH = ROOT / "checkpoints" / "chapter-06" / "failure.py"
SPEC = importlib.util.spec_from_file_location("chapter_06_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FAILURE_SPEC = importlib.util.spec_from_file_location("chapter_06_failure", FAILURE_PATH)
assert FAILURE_SPEC and FAILURE_SPEC.loader
FAILURE = importlib.util.module_from_spec(FAILURE_SPEC)
FAILURE_SPEC.loader.exec_module(FAILURE)


def test_completed_leases_pass() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_cross_tenant_scale_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for lease in inputs[2]["leases"]:
        if lease["environment"] == "storefront-nonprod":
            lease["mutated_by"] = "fulfillment-team"
    errors = MODULE.evaluate(*inputs)
    assert "cross-tenant mutation: storefront-nonprod/fulfillment-team" in errors


def test_expired_unreclaimed_lease_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for lease in inputs[2]["leases"]:
        if lease["environment"] == "fulfillment-nonprod":
            lease["expires_at"] = "2026-08-16T00:00:00Z"
    errors = MODULE.evaluate(*inputs)
    assert "unreclaimed expired lease: fulfillment-nonprod" in errors


def test_failure_injection_rejects_dev_cluster_admin() -> None:
    errors = MODULE.evaluate(*FAILURE.injected_inputs())
    assert "shared env admin: storefront-nonprod/dev-cluster-admin" in errors
    assert "cross-tenant mutation: storefront-nonprod/fulfillment-team" in errors


def test_denied_network_join_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for lease in inputs[2]["leases"]:
        if lease["environment"] == "fulfillment-nonprod":
            lease["isolation"]["network"] = "peer-tenant-workload-network"
    errors = MODULE.evaluate(*inputs)
    assert "cross-tenant network: fulfillment-nonprod" in errors


def test_network_deny_reads_chapter_03() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for lease in inputs[2]["leases"]:
        if lease["environment"] == "fulfillment-nonprod":
            lease["isolation"]["network"] = "peer-tenant-workload-network"
    for dimension in inputs[4]["dimensions"]:
        if dimension["id"] == "network":
            dimension["denied_inheritance"] = []
    errors = MODULE.evaluate(*inputs)
    assert "cross-tenant network: fulfillment-nonprod" not in errors
