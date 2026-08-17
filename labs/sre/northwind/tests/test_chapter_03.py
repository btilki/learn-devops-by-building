from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-03" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_03_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_slo_catalog_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_remaining_budget_is_computed_from_observations() -> None:
    remaining = MODULE.remaining_fraction(19940, 20000, 0.995)
    assert remaining == 0.4
    remaining = MODULE.remaining_fraction(9930, 10000, 0.99)
    assert remaining == 0.3


def test_storefront_only_portfolio_nines_fail() -> None:
    (
        catalog,
        windows,
        budgets,
        observations,
        journeys,
        decisions,
        expectations,
    ) = MODULE.completed_inputs()
    catalog["slos"] = [
        item
        for item in catalog["slos"]
        if item["id"] == "slo-accept-and-complete-order"
    ]
    catalog["slos"][0]["target"] = 0.999
    catalog["slos"][0]["remaining_budget"] = 1.0
    catalog["slos"][0]["sla"] = "99.9 percent availability per customer contract"
    catalog["non_critical"] = []
    catalog["legal_products"] = []
    errors = MODULE.evaluate(
        catalog, windows, budgets, observations, journeys, decisions, expectations
    )
    assert "missing required journey slo: dispatch-fulfillment" in errors
    assert "catalog emits remaining budget: slo-accept-and-complete-order" in errors
    assert "sla text used as slo target: slo-accept-and-complete-order" in errors


def test_copied_fulfillment_target_fails() -> None:
    (
        catalog,
        windows,
        budgets,
        observations,
        journeys,
        decisions,
        expectations,
    ) = MODULE.completed_inputs()
    for item in catalog["slos"]:
        if item["id"] == "slo-dispatch-fulfillment":
            item["target"] = 0.995
            item["window"] = "rolling-30d"
    errors = MODULE.evaluate(
        catalog, windows, budgets, observations, journeys, decisions, expectations
    )
    assert "fulfillment slo copied from storefront" in errors
