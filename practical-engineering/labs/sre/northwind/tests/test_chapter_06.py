from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-06" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_06_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_oncall_systems_pass() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_slack_as_primary_fails() -> None:
    (
        systems,
        rotations,
        handoffs,
        authority,
        pages,
        tickets,
        catalog_iface,
        authorization,
        expectations,
    ) = MODULE.completed_inputs()
    rotations["rotations"][0]["primary"] = "slack"
    rotations["rotations"][0]["living_primary"] = False
    errors = MODULE.evaluate(
        systems,
        rotations,
        handoffs,
        authority,
        pages,
        tickets,
        catalog_iface,
        authorization,
        expectations,
    )
    assert "slack-as-primary: storefront-oncall-system/slack" in errors
    assert "missing living primary: storefront-oncall-system" in errors


def test_platform_destination_on_storefront_fails() -> None:
    (
        systems,
        rotations,
        handoffs,
        authority,
        pages,
        tickets,
        catalog_iface,
        authorization,
        expectations,
    ) = MODULE.completed_inputs()
    for item in systems["systems"]:
        if item["id"] == "storefront-oncall-system":
            item["catalog_contact"] = "platform-oncall"
        if item["id"] == "platform-oncall-system":
            item["catalog_contact"] = "storefront-oncall"
    errors = MODULE.evaluate(
        systems,
        rotations,
        handoffs,
        authority,
        pages,
        tickets,
        catalog_iface,
        authorization,
        expectations,
    )
    assert "platform destination landed on storefront: storefront-oncall-system" in errors
