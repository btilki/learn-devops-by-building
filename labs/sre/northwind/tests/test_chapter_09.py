from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-09" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_09_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_degradation_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_unbounded_retries_fail() -> None:
    modes, shedding, cascade, contracts, journeys, pages, expectations = (
        MODULE.completed_inputs()
    )
    shedding["rules"][0]["retry_limit"] = "unbounded"
    shedding["rules"][0]["action"] = "accept-anyway"
    errors = MODULE.evaluate(
        modes, shedding, cascade, contracts, journeys, pages, expectations
    )
    assert "unbounded retries: payment" in errors
    assert "missing required shed: payment" in errors


def test_degraded_success_and_fulfillment_page_fail() -> None:
    modes, shedding, cascade, contracts, journeys, pages, expectations = (
        MODULE.completed_inputs()
    )
    modes["modes"][0]["accounting"] = "success"
    modes["modes"][0]["user_visible"] = "silent-drop"
    cascade["page_cause"] = "fulfillment-oncall"
    cascade["denials"][0]["must_not_page"] = "storefront-oncall"
    errors = MODULE.evaluate(
        modes, shedding, cascade, contracts, journeys, pages, expectations
    )
    assert "degraded success counted as success" in errors
    assert "missing user-visible degraded mode" in errors
    assert "fulfillment paged as payment cause" in errors
