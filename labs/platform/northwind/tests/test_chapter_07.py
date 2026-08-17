from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-07" / "evaluate.py"
FAILURE_PATH = ROOT / "checkpoints" / "chapter-07" / "failure.py"
SPEC = importlib.util.spec_from_file_location("chapter_07_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FAILURE_SPEC = importlib.util.spec_from_file_location("chapter_07_failure", FAILURE_PATH)
assert FAILURE_SPEC and FAILURE_SPEC.loader
FAILURE = importlib.util.module_from_spec(FAILURE_SPEC)
FAILURE_SPEC.loader.exec_module(FAILURE)


def test_completed_contracts_pass() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_hidden_module_binding_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for binding in inputs[0]["bindings"]:
        if (
            binding["environment"] == "storefront-nonprod"
            and binding["capability"] == "tenant-storage"
        ):
            binding["parameters"]["terraform-resource-address"] = "google_storage_bucket.storefront"
    errors = MODULE.evaluate(*inputs)
    leaked = "hidden module used as tenant API: storefront-nonprod/terraform-resource-address"
    assert leaked in errors


def test_denied_network_binding_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for binding in inputs[0]["bindings"]:
        if (
            binding["environment"] == "fulfillment-nonprod"
            and binding["capability"] == "tenant-network"
        ):
            binding["parameters"]["isolation"] = "peer-tenant-workload-network"
    errors = MODULE.evaluate(*inputs)
    assert "contract violates isolation: fulfillment-nonprod/peer-tenant-workload-network" in errors


def test_identity_drop_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for version in inputs[1]["versions"]:
        if version["capability"] == "workload-identity":
            version["credential_model"] = "referenced-rotatable-secret"
    errors = MODULE.evaluate(*inputs)
    assert "identity contract drops inherited federated identity" in errors


def test_hidden_module_refactor_without_bump_passes() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for version in inputs[1]["versions"]:
        if version["capability"] == "tenant-storage":
            version["hidden_module"] = ["module-address", "provider-project"]
    inputs[2]["changes"].append(
        {
            "capability": "tenant-storage",
            "version": "1.0",
            "kind": "hidden-module-refactor",
        }
    )
    assert MODULE.evaluate(*inputs) == []


def test_failure_injection_rejects_silent_rename() -> None:
    errors = MODULE.evaluate(*FAILURE.injected_inputs())
    assert "breaking change without version: tenant-storage/1.0" in errors
    assert "missing migration note: tenant-storage/1.0" in errors
    assert "tenant parameter missing: fulfillment-nonprod/tenant-storage/class" in errors
