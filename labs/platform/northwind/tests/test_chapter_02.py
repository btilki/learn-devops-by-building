from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-02" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_02_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_intake_decisions_pass() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_two_teams_asked_productization_fails() -> None:
    method, candidates, decisions, jobs, non_goals, expectations = MODULE.completed_inputs()
    for item in decisions["decisions"]:
        if item["candidate"] == "order-pricing-logic":
            item["treatment"] = "productize"
            item["user_job"] = "ship-on-paved-road"
            item["demand"] = "two-teams-asked"
            item.pop("remaining_owner", None)
    errors = MODULE.evaluate(method, candidates, decisions, jobs, non_goals, expectations)
    assert "non-goal productized: order-pricing-logic" in errors
    assert "productize uses forbidden demand: order-pricing-logic/two-teams-asked" in errors
    assert "missing required decline: order-pricing-logic" in errors


def test_missing_environment_productize_fails() -> None:
    method, candidates, decisions, jobs, non_goals, expectations = MODULE.completed_inputs()
    for item in decisions["decisions"]:
        if item["candidate"] == "environment-provisioning":
            item["treatment"] = "leave"
            item["remaining_owner"] = "storefront-team"
            item.pop("user_job", None)
    errors = MODULE.evaluate(method, candidates, decisions, jobs, non_goals, expectations)
    assert "missing required productize: environment-provisioning" in errors
