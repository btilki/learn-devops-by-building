from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-13" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_13_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_gameday_program_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_mixed_backup_complete_and_annual_cadence_fail() -> None:
    (
        program,
        scenarios,
        results,
        policy_actions,
        oncall,
        learning_actions,
        architecture,
        expectations,
    ) = MODULE.completed_inputs()
    program["cadence"] = "annual"
    program["status"] = "complete"
    program["forbidden_complete_on"] = []
    scenarios["scenarios"] = [
        {
            "id": "gameday-mixed-backup",
            "kind": "mixed-backup",
            "joins": "platform-mixed-backup",
            "insufficient_alone": False,
            "max_blast_radius": "declared-scenario",
        }
    ]
    results["results"] = [
        {
            "id": "result-mixed-backup",
            "scenario": "gameday-mixed-backup",
            "disposition": "complete",
            "as_of": "2026-08-16T00:00:00Z",
        }
    ]
    errors = MODULE.evaluate(
        program,
        scenarios,
        results,
        policy_actions,
        oncall,
        learning_actions,
        architecture,
        expectations,
    )
    assert "single mixed-backup completes program" in errors
    assert "cadence is not recurrence: annual" in errors
    assert "missing required scenario: error-budget-freeze" in errors


def test_chapter_14_rehearsal_slack_page_and_email_drill_fail() -> None:
    (
        program,
        scenarios,
        results,
        policy_actions,
        oncall,
        learning_actions,
        architecture,
        expectations,
    ) = MODULE.completed_inputs()
    program["not_chapter_14_failover"] = False
    for item in scenarios["scenarios"]:
        if item["kind"] == "on-call-page-path":
            item["joins"] = "slack"
        elif item["kind"] == "dependency-loss":
            item["joins"] = "notification-service"
        elif item["kind"] == "regional-loss-tabletop":
            item["kind"] = "chapter-14-failover"
            item["mode"] = "executed"
    errors = MODULE.evaluate(
        program,
        scenarios,
        results,
        policy_actions,
        oncall,
        learning_actions,
        architecture,
        expectations,
    )
    assert "regional scenario rehearses chapter 14" in errors
    assert "page path does not join on-call system" in errors
    assert "dependency drill is not payment or warehouse" in errors
    assert "missing required scenario: regional-loss-tabletop" in errors
