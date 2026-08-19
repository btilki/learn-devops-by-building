from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-04" / "evaluate.py"
FAILURE_PATH = ROOT / "checkpoints" / "chapter-04" / "failure.py"
SPEC = importlib.util.spec_from_file_location("chapter_04_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FAILURE_SPEC = importlib.util.spec_from_file_location("chapter_04_failure", FAILURE_PATH)
assert FAILURE_SPEC and FAILURE_SPEC.loader
FAILURE = importlib.util.module_from_spec(FAILURE_SPEC)
FAILURE_SPEC.loader.exec_module(FAILURE)


def test_completed_catalog_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_deleted_group_owner_fails() -> None:
    systems, ownership, dependencies, tenants, users, expectations = (
        copy.deepcopy(item) for item in MODULE.completed_inputs()
    )
    for entry in ownership["ownership"]:
        if entry["system"] == "fulfillment-api":
            entry["owner"] = "fulfillment-legacy-group"
            entry["reported_status"] = "green"
    errors = MODULE.evaluate(
        systems, ownership, dependencies, tenants, users, expectations
    )
    assert "owner is not living: fulfillment-api/fulfillment-legacy-group" in errors
    assert "catalog reports green without a living owner: fulfillment-api" in errors


def test_stale_ownership_fails() -> None:
    systems, ownership, dependencies, tenants, users, expectations = (
        copy.deepcopy(item) for item in MODULE.completed_inputs()
    )
    for entry in ownership["ownership"]:
        if entry["system"] == "fulfillment-api":
            entry["last_reviewed_at"] = "2025-12-01T00:00:00Z"
    errors = MODULE.evaluate(
        systems, ownership, dependencies, tenants, users, expectations
    )
    assert "stale ownership: fulfillment-api" in errors


def test_failure_injection_rejects_deleted_group() -> None:
    errors = MODULE.evaluate(*FAILURE.injected_inputs())
    assert "owner is not living: fulfillment-api/fulfillment-legacy-group" in errors
    assert "catalog reports green without a living owner: fulfillment-api" in errors
