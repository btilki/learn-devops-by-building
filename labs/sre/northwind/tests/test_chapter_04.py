from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-04" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_04_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_error_budget_policy_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_exhausted_storefront_remaining_is_zero() -> None:
    remaining = MODULE.remaining_fraction(19900, 20000, 0.995)
    assert remaining == 0.0
    bands = [
        {"action": "continue", "remaining_min": 0.5},
        {"action": "slow", "remaining_min": 0.1},
        {"action": "freeze", "remaining_min": 0.0},
    ]
    assert MODULE.band_action(remaining, bands) == "freeze"


def test_unfrozen_fleet_under_exhausted_budget_fails() -> None:
    (
        policy,
        actions,
        exceptions,
        catalog,
        observations,
        fleet,
        release,
        expectations,
    ) = MODULE.completed_inputs()
    for item in actions["actions"]:
        if item["target"] == "storage-1-0-to-2-0":
            item["action"] = "continue"
            item["freeze_reason"] = "platform-upgrade-freeze"
            item["freeze"] = {
                "start": "2026-08-16T00:00:00Z",
                "end": "2026-08-23T00:00:00Z",
            }
            item["rollback"] = "1.0"
    errors = MODULE.evaluate(
        policy, actions, exceptions, catalog, observations, fleet, release, expectations
    )
    assert "unfrozen exhausted budget: storage-1-0-to-2-0" in errors
    assert "fleet freeze copies platform field: freeze" in errors
    assert "fleet freeze copies platform field: rollback" in errors
    assert "fleet freeze relabels platform upgrade freeze: platform-upgrade-freeze" in errors


def test_exception_without_expiry_fails() -> None:
    (
        policy,
        actions,
        exceptions,
        catalog,
        observations,
        fleet,
        release,
        expectations,
    ) = MODULE.completed_inputs()
    exceptions["exceptions"][0].pop("expires_at")
    errors = MODULE.evaluate(
        policy, actions, exceptions, catalog, observations, fleet, release, expectations
    )
    assert "exception has no expiry: exception-notification-template" in errors
