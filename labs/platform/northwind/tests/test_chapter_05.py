from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-05" / "evaluate.py"
FAILURE_PATH = ROOT / "checkpoints" / "chapter-05" / "failure.py"
SPEC = importlib.util.spec_from_file_location("chapter_05_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FAILURE_SPEC = importlib.util.spec_from_file_location("chapter_05_failure", FAILURE_PATH)
assert FAILURE_SPEC and FAILURE_SPEC.loader
FAILURE = importlib.util.module_from_spec(FAILURE_SPEC)
FAILURE_SPEC.loader.exec_module(FAILURE)


def test_completed_paved_road_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_unofficial_fork_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    conformance = inputs[2]
    for entry in conformance["entries"]:
        if entry["system"] == "fulfillment-api":
            entry["path"] = "unofficial"
            entry["defaults_present"] = ["latest-tag"]
    errors = MODULE.evaluate(*inputs)
    assert "unofficial fork: fulfillment-api" in errors
    assert "missing paved default: fulfillment-api/artifact-digest" in errors
    assert "forbidden default: fulfillment-api/latest-tag" in errors


def test_exit_dropping_guardrail_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    exits = inputs[3]
    exits["exits"][0]["remaining_guardrails"] = ["no-cluster-admin"]
    errors = MODULE.evaluate(*inputs)
    dropped = "exit drops remaining guardrail: notification-skip-slow-template/artifact-digest"
    assert dropped in errors


def test_failure_injection_rejects_unofficial_fork() -> None:
    errors = MODULE.evaluate(*FAILURE.injected_inputs())
    assert "unofficial fork: fulfillment-api" in errors
    assert "missing paved default: fulfillment-api/workload-identity-claims" in errors
