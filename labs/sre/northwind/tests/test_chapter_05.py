from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-05" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_05_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_burn_alerts_pass() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_cpu_paging_storefront_fails() -> None:
    burns, pages, tickets, decisions, catalog_iface, expectations = (
        MODULE.completed_inputs()
    )
    burns["burns"] = [
        item for item in burns["burns"] if item["sli"] != "order_success_ratio"
    ]
    pages["pages"].append(
        {
            "id": "page-cpu",
            "burn": "cpu-utilization-symptom",
            "destination": "storefront-oncall",
            "destination_kind": "catalog-contact",
            "user_impact": True,
        }
    )
    errors = MODULE.evaluate(
        burns, pages, tickets, decisions, catalog_iface, expectations
    )
    assert "missing required page: order_success_ratio/fast" in errors
    assert "symptom pages: cpu-utilization/storefront-oncall" in errors
    assert "page emits user impact: page-cpu" in errors


def test_job_time_paging_storefront_fails() -> None:
    burns, pages, tickets, decisions, catalog_iface, expectations = (
        MODULE.completed_inputs()
    )
    for item in burns["burns"]:
        if item["sli"] == "time-to-first-environment":
            item["disposition"] = "page"
    pages["pages"].append(
        {
            "id": "page-job-time",
            "burn": "time-to-first-environment-burn",
            "destination": "storefront-oncall",
            "destination_kind": "catalog-contact",
        }
    )
    errors = MODULE.evaluate(
        burns, pages, tickets, decisions, catalog_iface, expectations
    )
    assert "job-time pages: time-to-first-environment/storefront-oncall" in errors
