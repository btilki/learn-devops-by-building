from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-12" / "evaluate.py"
FAILURE_PATH = ROOT / "checkpoints" / "chapter-12" / "failure.py"
SPEC = importlib.util.spec_from_file_location("chapter_12_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FAILURE_SPEC = importlib.util.spec_from_file_location("chapter_12_failure", FAILURE_PATH)
assert FAILURE_SPEC and FAILURE_SPEC.loader
FAILURE = importlib.util.module_from_spec(FAILURE_SPEC)
FAILURE_SPEC.loader.exec_module(FAILURE)


def test_completed_fleet_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_cluster_admin_onboarding_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for row in inputs[0]["tenants"]:
        if row["tenant"] == "fulfillment":
            row["granted_role"] = "cluster-admin"
    errors = MODULE.evaluate(*inputs)
    assert "onboarding grants cluster-admin: fulfillment" in errors


def test_all_at_once_apply_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for upgrade in inputs[1]["upgrades"]:
        for cohort in upgrade["cohorts"]:
            cohort["status"] = "complete"
    errors = MODULE.evaluate(*inputs)
    assert "fleet applied all tenants at once: storage-1-0-to-2-0" in errors


def test_closed_deprecation_without_exception_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for item in inputs[2]["deprecations"]:
        item["window_ends_at"] = "2026-08-15T12:00:00Z"
        item["status"] = "closed"
    errors = MODULE.evaluate(*inputs)
    assert "deprecation window closed with remaining tenant: fulfillment" in errors


def test_gitops_rewrite_join_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for upgrade in inputs[1]["upgrades"]:
        upgrade["source_rewritten"] = True
    errors = MODULE.evaluate(*inputs)
    assert "controller rewrites source: storage-1-0-to-2-0" in errors


def test_rewrite_deny_reads_inherited_gitops() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for upgrade in inputs[1]["upgrades"]:
        upgrade["source_rewritten"] = True
    inputs[14]["controller_may_rewrite_source"] = True
    errors = MODULE.evaluate(*inputs)
    assert "controller rewrites source: storage-1-0-to-2-0" not in errors


def test_failure_injection_rejects_all_at_once_and_keeps_onboarding() -> None:
    errors = MODULE.evaluate(*FAILURE.injected_inputs())
    onboarding = FAILURE.injected_inputs()[0]
    roles = {item["tenant"]: item["granted_role"] for item in onboarding["tenants"]}
    deprecations = FAILURE.injected_inputs()[2]
    assert "fleet applied all tenants at once: storage-1-0-to-2-0" in errors
    assert "tenant contract broken without migration: fulfillment" in errors
    assert "missing fleet rollback: storage-1-0-to-2-0" in errors
    assert roles["fulfillment"] == "tenant-operator"
    assert deprecations["deprecations"][0]["status"] == "open"
