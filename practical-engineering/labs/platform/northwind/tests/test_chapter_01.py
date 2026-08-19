from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-01" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_01_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_product_model_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_portal_launch_and_missing_owner_fail() -> None:
    brief, users, jobs, non_goals, expectations = MODULE.completed_inputs()
    brief["success_evidence"] = ["portal-launch"]
    jobs["jobs"][0]["owner"] = "unknown-team"
    errors = MODULE.evaluate(brief, users, jobs, non_goals, expectations)
    assert "brief uses vanity success evidence: portal-launch" in errors
    assert "job has no accountable owner: obtain-bounded-environment" in errors


def test_missing_non_goal_fails() -> None:
    brief, users, jobs, non_goals, expectations = MODULE.completed_inputs()
    non_goals["non_goals"] = [
        item for item in non_goals["non_goals"] if item["id"] != "portfolio-slo-governance"
    ]
    errors = MODULE.evaluate(brief, users, jobs, non_goals, expectations)
    assert "missing required non-goal: portfolio-slo-governance" in errors
