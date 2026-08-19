from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-14" / "evaluate.py"
FAILURE_PATH = ROOT / "checkpoints" / "chapter-14" / "failure.py"
SPEC = importlib.util.spec_from_file_location("chapter_14_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FAILURE_SPEC = importlib.util.spec_from_file_location("chapter_14_failure", FAILURE_PATH)
assert FAILURE_SPEC and FAILURE_SPEC.loader
FAILURE = importlib.util.module_from_spec(FAILURE_SPEC)
FAILURE_SPEC.loader.exec_module(FAILURE)


def test_completed_recovery_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_team_recorded_as_restore_subject_and_approver_is_not_self_approval() -> None:
    restores = MODULE.completed_inputs()[2]["restores"]
    note = next(item for item in restores if item["id"] == "restore-plane-lkg")
    assert note["subject"] == "platform-team"
    assert note["approved_by"] == "platform-team"
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_plane_subject_fails_self_approval_even_with_team_approver() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for restore in inputs[2]["restores"]:
        if restore["id"] == "restore-plane-lkg":
            restore["subject"] = "plane-reconciler"
            restore["approved_by"] = "platform-team"
    errors = MODULE.evaluate(*inputs)
    assert "plane self-approval: restore-plane-lkg" in errors


def test_mixed_backup_restore_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[2]["restores"][0]["snapshot"] = "plane-newest-corrupt"
    inputs[2]["restores"][0]["mixed_backup"] = True
    errors = MODULE.evaluate(*inputs)
    assert "mixed backup restore: restore-plane-lkg" in errors


def test_fulfillment_replay_into_storefront_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for row in inputs[1]["tenants"]:
        if row["tenant"] == "storefront":
            row["replayed_from"] = "fulfillment"
            row["restored_version"] = "1.0"
    errors = MODULE.evaluate(*inputs)
    assert "cross-tenant replay: storefront/fulfillment" in errors
    assert "restore version mismatch: storefront" in errors


def test_accidental_freeze_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for row in inputs[1]["tenants"]:
        if row["tenant"] == "storefront":
            row["decision"] = "freeze"
            row["source"] = "accident"
    for item in inputs[3]["tenant_decisions"]:
        if item["tenant"] == "storefront":
            item["decision"] = "freeze"
            item["source"] = "accident"
    inputs[3]["traffic_return"] = [
        item for item in inputs[3]["traffic_return"] if item["tenant"] != "storefront"
    ]
    errors = MODULE.evaluate(*inputs)
    assert "accidental tenant freeze: storefront" in errors


def test_explicit_freeze_is_not_accidental() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for row in inputs[1]["tenants"]:
        if row["tenant"] == "storefront":
            row["decision"] = "freeze"
            row["source"] = "explicit-tenant-decision"
    for item in inputs[3]["tenant_decisions"]:
        if item["tenant"] == "storefront":
            item["decision"] = "freeze"
            item["source"] = "explicit-tenant-decision"
    inputs[3]["traffic_return"] = [
        item for item in inputs[3]["traffic_return"] if item["tenant"] != "storefront"
    ]
    assert MODULE.evaluate(*inputs) == []


def test_complete_roots_do_not_make_mixed_backup_legal() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    newest = next(
        item for item in inputs[0]["snapshots"] if item["id"] == "plane-newest-corrupt"
    )
    required = {
        "reviewed_intent",
        "artifact_identity",
        "configuration_identity",
        "durable_data",
        "identity_policy",
    }
    assert set(newest["roots"]) == required
    inputs[2]["restores"][0]["snapshot"] = "plane-newest-corrupt"
    inputs[2]["restores"][0]["mixed_backup"] = False
    inputs[2]["restores"][0]["roots"] = list(newest["roots"])
    errors = MODULE.evaluate(*inputs)
    assert "mixed backup restore: restore-plane-lkg" in errors


def test_last_known_good_reads_chapter_08() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for upgrade in inputs[10]["upgrades"]:
        upgrade["last_known_good"] = "0.9"
    errors = MODULE.evaluate(*inputs)
    assert "missing last known good: restore-plane-lkg" in errors
    assert "plane evidence last known good is not chapter 8 retention" in errors


def test_verification_cannot_emit_recovered() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[3]["status"] = "recovered"
    errors = MODULE.evaluate(*inputs)
    assert "verification reports recovered" in errors


def test_failure_injection_rejects_mixed_backup_and_keeps_fulfillment() -> None:
    errors = MODULE.evaluate(*FAILURE.injected_inputs())
    isolation = FAILURE.injected_inputs()[1]
    rows = {item["tenant"]: item for item in isolation["tenants"]}
    assert "mixed backup restore: restore-newest-mixed" in errors
    assert "cross-tenant replay: storefront/fulfillment" in errors
    assert "missing last known good: restore-newest-mixed" in errors
    assert rows["fulfillment"]["replayed_from"] == "fulfillment"
    assert rows["fulfillment"]["restored_version"] == "1.0"
    assert rows["fulfillment"]["decision"] == "continue"
