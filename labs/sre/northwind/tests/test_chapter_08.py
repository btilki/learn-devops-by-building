from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-08" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_08_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_dependency_contracts_pass() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_payment_no_user_impact_fails() -> None:
    (
        catalog,
        criticality,
        contracts,
        journeys,
        slo_catalog,
        decisions,
        pages,
        expectations,
    ) = MODULE.completed_inputs()
    criticality["assignments"][0]["no_user_impact"] = True
    criticality["assignments"][0]["failure_effect"] = "none"
    errors = MODULE.evaluate(
        catalog,
        criticality,
        contracts,
        journeys,
        slo_catalog,
        decisions,
        pages,
        expectations,
    )
    assert "dependency emits no user impact: payment" in errors
    assert "payment failure does not burn storefront: payment" in errors


def test_email_paged_as_critical_fails() -> None:
    (
        catalog,
        criticality,
        contracts,
        journeys,
        slo_catalog,
        decisions,
        pages,
        expectations,
    ) = MODULE.completed_inputs()
    email = criticality["assignments"][2]
    email["criticality"] = "critical"
    email["failure_effect"] = "page"
    email["destination"] = "storefront-oncall"
    errors = MODULE.evaluate(
        catalog,
        criticality,
        contracts,
        journeys,
        slo_catalog,
        decisions,
        pages,
        expectations,
    )
    assert "email paged as critical: notification-service" in errors
