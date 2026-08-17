from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-01" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_01_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_reliability_model_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_cluster_uptime_and_missing_owner_fail() -> None:
    brief, owners, journeys, refusals, expectations = MODULE.completed_inputs()
    brief["success_evidence"] = ["cluster-uptime"]
    journeys["journeys"][0]["owner"] = "unknown-team"
    errors = MODULE.evaluate(brief, owners, journeys, refusals, expectations)
    assert "brief uses theater success evidence: cluster-uptime" in errors
    assert "journey has no accountable owner: accept-and-complete-order" in errors


def test_job_time_as_journey_success_fails() -> None:
    brief, owners, journeys, refusals, expectations = MODULE.completed_inputs()
    brief["success_evidence"] = ["time-to-first-environment"]
    journeys["journeys"][0]["later_proof"] = "time-to-first-environment"
    errors = MODULE.evaluate(brief, owners, journeys, refusals, expectations)
    assert "brief uses job-time success evidence: time-to-first-environment" in errors
    assert (
        "journey uses job-time later proof: "
        "accept-and-complete-order/time-to-first-environment"
    ) in errors


def test_missing_refusal_fails() -> None:
    brief, owners, journeys, refusals, expectations = MODULE.completed_inputs()
    refusals["refusals"] = [
        item
        for item in refusals["refusals"]
        if item["id"] != "inherited-restore-as-portfolio-recovery"
    ]
    errors = MODULE.evaluate(brief, owners, journeys, refusals, expectations)
    assert "missing required refusal: inherited-restore-as-portfolio-recovery" in errors
