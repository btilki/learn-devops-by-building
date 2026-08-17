from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-10" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_10_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_incident_command_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_one_path_close_and_slack_commander_fail() -> None:
    (
        command,
        roles,
        traces,
        inherited_incident,
        inherited_support,
        systems,
        rotations,
        actions,
        journeys,
        expectations,
    ) = MODULE.completed_inputs()
    traces["traces"][0]["commander"] = "slack"
    traces["traces"][0]["status"] = "closed"
    traces["traces"][0]["close_evidence"] = ["order_success_ratio"]
    traces["traces"][0]["affected_journeys"] = ["accept-and-complete-order"]
    errors = MODULE.evaluate(
        command,
        roles,
        traces,
        inherited_incident,
        inherited_support,
        systems,
        rotations,
        actions,
        journeys,
        expectations,
    )
    assert "slack-as-commander: spanning-payment-and-dispatch/slack" in errors
    assert "one-path close: order_success_ratio" in errors
    assert "missing required journey: dispatch-fulfillment" in errors


def test_platform_product_on_storefront_fails() -> None:
    (
        command,
        roles,
        traces,
        inherited_incident,
        inherited_support,
        systems,
        rotations,
        actions,
        journeys,
        expectations,
    ) = MODULE.completed_inputs()
    traces["traces"][1]["oncall_systems"] = ["storefront-oncall-system"]
    errors = MODULE.evaluate(
        command,
        roles,
        traces,
        inherited_incident,
        inherited_support,
        systems,
        rotations,
        actions,
        journeys,
        expectations,
    )
    assert "platform-product landed on storefront" in errors
