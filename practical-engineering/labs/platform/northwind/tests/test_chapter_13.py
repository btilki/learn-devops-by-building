from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-13" / "evaluate.py"
FAILURE_PATH = ROOT / "checkpoints" / "chapter-13" / "failure.py"
SPEC = importlib.util.spec_from_file_location("chapter_13_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FAILURE_SPEC = importlib.util.spec_from_file_location("chapter_13_failure", FAILURE_PATH)
assert FAILURE_SPEC and FAILURE_SPEC.loader
FAILURE = importlib.util.module_from_spec(FAILURE_SPEC)
FAILURE_SPEC.loader.exec_module(FAILURE)


def test_completed_support_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_team_recorded_as_subject_and_approver_is_not_self_approval() -> None:
    changes = MODULE.completed_inputs()[2]["changes"]
    note = next(item for item in changes if item["id"] == "reviewed-admission-note")
    assert note["subject"] == "platform-team"
    assert note["approved_by"] == "platform-team"
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_plane_subject_fails_self_approval_even_with_team_approver() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for change in inputs[2]["changes"]:
        if change["id"] == "reviewed-admission-note":
            change["subject"] = "plane-reconciler"
            change["approved_by"] = "platform-team"
    errors = MODULE.evaluate(*inputs)
    assert "plane self-approval: reviewed-admission-note" in errors


def test_unofficial_plane_admin_change_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[2]["changes"].append(
        {
            "id": "live-plane-patch",
            "resource": "kubernetes-control-plane",
            "subject": "plane-reconciler",
            "approved_by": "plane-reconciler",
            "action": "patch-in-place",
            "granted_role": "cluster-admin",
            "last_known_good": "1.0",
            "current_version": "1.1",
            "unofficial": True,
            "source_rewritten": False,
            "result": "allow",
        }
    )
    errors = MODULE.evaluate(*inputs)
    assert "unofficial plane-admin change: live-plane-patch" in errors
    assert "plane self-approval: live-plane-patch" in errors


def test_chat_history_escalation_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for route in inputs[1]["routes"]:
        if route["system"] == "fulfillment-api":
            route["escalation"] = "chat-history"
    errors = MODULE.evaluate(*inputs)
    assert "escalation is chat-history: fulfillment-api" in errors


def test_csat_close_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for item in inputs[3]["incidents"]:
        if item["id"] == "fulfillment-warehouse-delay":
            item["closed_reason"] = "csat"
    errors = MODULE.evaluate(*inputs)
    assert "incident closed for vanity: fulfillment-warehouse-delay" in errors


def test_order_metric_as_error_budget_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[0]["error_budget_indicators"].append("order_success_ratio")
    errors = MODULE.evaluate(*inputs)
    assert "job-time budget uses tenant workload: order_success_ratio" in errors


def test_last_known_good_reads_chapter_08() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for upgrade in inputs[9]["upgrades"]:
        upgrade["last_known_good"] = "0.9"
    errors = MODULE.evaluate(*inputs)
    assert "missing last known good: reviewed-admission-note" in errors


def test_failure_injection_rejects_patch_and_keeps_escalation() -> None:
    errors = MODULE.evaluate(*FAILURE.injected_inputs())
    escalation = FAILURE.injected_inputs()[1]
    incidents = FAILURE.injected_inputs()[3]
    routes = {item["system"]: item["escalation"] for item in escalation["routes"]}
    classes = {item["id"]: item["class"] for item in incidents["incidents"]}
    assert "unofficial plane-admin change: live-plane-patch" in errors
    assert "plane self-approval: live-plane-patch" in errors
    assert "missing last known good: live-plane-patch" in errors
    assert routes["fulfillment-api"] == "fulfillment-oncall"
    assert classes["fulfillment-warehouse-delay"] == "tenant-application"
