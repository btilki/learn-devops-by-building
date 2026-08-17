from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-09" / "evaluate.py"
FAILURE_PATH = ROOT / "checkpoints" / "chapter-09" / "failure.py"
SPEC = importlib.util.spec_from_file_location("chapter_09_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FAILURE_SPEC = importlib.util.spec_from_file_location("chapter_09_failure", FAILURE_PATH)
assert FAILURE_SPEC and FAILURE_SPEC.loader
FAILURE = importlib.util.module_from_spec(FAILURE_SPEC)
FAILURE_SPEC.loader.exec_module(FAILURE)


def test_completed_guardrails_pass() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_green_scorecard_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for card in inputs[1]["scorecards"]:
        if card["system"] == "fulfillment-api":
            card["reported_status"] = "green"
    errors = MODULE.evaluate(*inputs)
    assert "scorecard reports green without conformance: fulfillment-api" in errors


def test_disabled_digest_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for card in inputs[1]["scorecards"]:
        if card["system"] == "fulfillment-api":
            card["defaults_present"] = ["workload-identity-claims", "no-cluster-admin"]
    errors = MODULE.evaluate(*inputs)
    assert "guardrail missing: fulfillment-api/artifact-digest" in errors


def test_copied_lifecycle_fields_fail() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[2]["bindings"].append(
        {
            "exception": "exception-dependency-mirror-2026-08",
            "tenant": "fulfillment",
            "system": "fulfillment-api",
            "path": "paved",
            "remaining_isolation": [
                "artifact-digest",
                "workload-identity-claims",
                "no-cluster-admin",
            ],
            "scorecard_effect": "none",
            "owner": "platform-security",
            "expires_at": "2026-12-01T00:00:00Z",
        }
    )
    errors = MODULE.evaluate(*inputs)
    assert "exception binding copies inherited lifecycle: owner" in errors
    assert "exception binding copies inherited lifecycle: expires_at" in errors


def test_active_exception_may_waive_digest() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for record in inputs[8]["exceptions"]:
        record["expires_at"] = "2026-11-16T00:00:00Z"
    inputs[2]["bindings"].append(
        {
            "exception": "exception-dependency-mirror-2026-08",
            "tenant": "fulfillment",
            "system": "fulfillment-api",
            "path": "paved",
            "remaining_isolation": ["workload-identity-claims", "no-cluster-admin"],
            "scorecard_effect": "waive-artifact-digest",
        }
    )
    for card in inputs[1]["scorecards"]:
        if card["system"] == "fulfillment-api":
            card["defaults_present"] = ["workload-identity-claims", "no-cluster-admin"]
    assert MODULE.evaluate(*inputs) == []


def test_failure_injection_rejects_expired_green_digest() -> None:
    errors = MODULE.evaluate(*FAILURE.injected_inputs())
    assert "scorecard reports green without conformance: fulfillment-api" in errors
    assert "expired inherited exception: exception-dependency-mirror-2026-08" in errors
    assert "guardrail missing: fulfillment-api/artifact-digest" in errors
