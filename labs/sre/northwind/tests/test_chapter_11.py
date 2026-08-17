from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-11" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_11_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_learning_program_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_hortatory_action_and_self_verification_fail() -> None:
    (
        program,
        records,
        actions,
        traces,
        shedding,
        bounds,
        evidence,
        expectations,
    ) = MODULE.completed_inputs()
    actions["actions"][0]["id"] = "be-more-careful"
    actions["actions"][0]["change"] = "be-more-careful"
    actions["actions"][0]["verification"]["producer"] = (
        "record-spanning-payment-and-dispatch"
    )
    records["records"][0]["verified"] = True
    errors = MODULE.evaluate(
        program, records, actions, traces, shedding, bounds, evidence, expectations
    )
    assert "hortatory action: be-more-careful" in errors
    assert "missing independent verification" in errors
    assert "record verifies itself: record-spanning-payment-and-dispatch" in errors
    assert "repeated cascade without verified action" in errors


def test_uncovered_platform_incident_fails() -> None:
    (
        program,
        records,
        actions,
        traces,
        shedding,
        bounds,
        evidence,
        expectations,
    ) = MODULE.completed_inputs()
    records["waivers"] = []
    errors = MODULE.evaluate(
        program, records, actions, traces, shedding, bounds, evidence, expectations
    )
    assert "missing required record: platform-product-job-time" in errors
