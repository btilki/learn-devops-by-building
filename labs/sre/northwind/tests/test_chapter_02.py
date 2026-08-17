from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-02" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_02_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_sli_decisions_pass() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_job_time_as_portfolio_slo_fails() -> None:
    (
        method,
        candidates,
        decisions,
        journeys,
        refusals,
        devex,
        observability,
        expectations,
    ) = MODULE.completed_inputs()
    for item in decisions["decisions"]:
        if item["candidate"] == "time-to-first-environment":
            item["treatment"] = "accept"
            item["class"] = "portfolio-slo"
            item["journey"] = "accept-and-complete-order"
            item["justification"] = "leadership-can-see-it"
            item.pop("remaining_owner", None)
        if item["candidate"] == "order_success_ratio":
            item["treatment"] = "reject"
            item["class"] = "tenant-workload"
            item["remaining_owner"] = "storefront-team"
            item.pop("journey", None)
    errors = MODULE.evaluate(
        method,
        candidates,
        decisions,
        journeys,
        refusals,
        devex,
        observability,
        expectations,
    )
    assert "missing required accept: order_success_ratio" in errors
    assert "missing required adjacent: time-to-first-environment" in errors
    assert (
        "accept uses forbidden justification: "
        "time-to-first-environment/leadership-can-see-it"
    ) in errors
    assert "decision uses forbidden class: time-to-first-environment/portfolio-slo" in errors
    assert "job-time accepted: time-to-first-environment" in errors


def test_missing_dispatch_accept_fails() -> None:
    (
        method,
        candidates,
        decisions,
        journeys,
        refusals,
        devex,
        observability,
        expectations,
    ) = MODULE.completed_inputs()
    for item in decisions["decisions"]:
        if item["candidate"] == "dispatch_success_ratio":
            item["treatment"] = "reject"
            item["class"] = "component-uptime"
            item["remaining_owner"] = "fulfillment-team"
            item.pop("journey", None)
    errors = MODULE.evaluate(
        method,
        candidates,
        decisions,
        journeys,
        refusals,
        devex,
        observability,
        expectations,
    )
    assert "missing required accept: dispatch_success_ratio" in errors
