from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-07" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_07_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_toil_bound_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_toil_fraction_is_computed_from_hours() -> None:
    assert MODULE.toil_fraction(14, 20) == 0.7


def test_notification_critical_slo_allowed_fails() -> None:
    definition, inventory, bounds, catalog, expectations = MODULE.completed_inputs()
    bounds["scope_proposals"][0]["decision"] = "allow"
    bounds["scope_proposals"][0]["justification"] = "on-call-already-watches-email"
    errors = MODULE.evaluate(definition, inventory, bounds, catalog, expectations)
    assert "new critical slo allowed: notification-service" in errors
    assert "new critical slo allowed while bound breached: notification-service" in errors
    forbidden = (
        "scope uses forbidden justification: "
        "propose-notification-critical-slo/on-call-already-watches-email"
    )
    assert forbidden in errors
