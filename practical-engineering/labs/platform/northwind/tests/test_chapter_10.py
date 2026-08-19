from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-10" / "evaluate.py"
FAILURE_PATH = ROOT / "checkpoints" / "chapter-10" / "failure.py"
SPEC = importlib.util.spec_from_file_location("chapter_10_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FAILURE_SPEC = importlib.util.spec_from_file_location("chapter_10_failure", FAILURE_PATH)
assert FAILURE_SPEC and FAILURE_SPEC.loader
FAILURE = importlib.util.module_from_spec(FAILURE_SPEC)
FAILURE_SPEC.loader.exec_module(FAILURE)


def test_completed_devex_pass() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_vanity_indicator_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[1]["indicators"].append(
        {
            "id": "adoption-percentage",
            "job": "obtain-bounded-environment",
            "owner": "platform-team",
            "class": "platform-product-sli",
            "evidence_kind": "lagging",
        }
    )
    errors = MODULE.evaluate(*inputs)
    assert "vanity indicator: adoption-percentage" in errors


def test_missing_sample_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[3]["samples"] = [
        item
        for item in inputs[3]["samples"]
        if item["indicator"] != "time-to-first-environment"
    ]
    errors = MODULE.evaluate(*inputs)
    assert "missing sample: time-to-first-environment" in errors


def test_order_metric_as_platform_indicator_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[1]["indicators"].append(
        {
            "id": "order_success_ratio",
            "job": "obtain-bounded-environment",
            "owner": "platform-team",
            "class": "platform-product-sli",
            "evidence_kind": "lagging",
        }
    )
    errors = MODULE.evaluate(*inputs)
    assert "tenant workload used as platform indicator: order_success_ratio" in errors


def test_portfolio_slo_class_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[1]["indicators"][0]["class"] = "portfolio-slo"
    errors = MODULE.evaluate(*inputs)
    assert "platform indicator treated as portfolio slo: time-to-first-environment" in errors


def test_wrong_non_metric_category_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for item in inputs[2]["non_metrics"]:
        if item["id"] == "adoption-percentage":
            item["category"] = "tenant-workload"
        if item["id"] == "order_success_ratio":
            item["category"] = "vanity"
    errors = MODULE.evaluate(*inputs)
    assert "non-metric category mismatch: adoption-percentage" in errors
    assert "non-metric category mismatch: order_success_ratio" in errors


def test_tenant_workload_category_reads_inherited_observability() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[8]["outcome_indicators"] = []
    errors = MODULE.evaluate(*inputs)
    assert "non-metric category mismatch: order_success_ratio" in errors
    assert "non-metric category mismatch: order_latency" in errors


def test_order_metric_reads_inherited_observability() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[1]["indicators"].append(
        {
            "id": "order_success_ratio",
            "job": "obtain-bounded-environment",
            "owner": "platform-team",
            "class": "platform-product-sli",
            "evidence_kind": "lagging",
        }
    )
    inputs[8]["outcome_indicators"] = []
    errors = MODULE.evaluate(*inputs)
    assert "tenant workload used as platform indicator: order_success_ratio" not in errors


def test_adoption_without_worse_wait_is_vanity_only() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[1]["indicators"].append(
        {
            "id": "adoption-percentage",
            "job": "obtain-bounded-environment",
            "owner": "platform-team",
            "class": "platform-product-sli",
            "evidence_kind": "lagging",
        }
    )
    inputs[3]["samples"].append(
        {
            "indicator": "adoption-percentage",
            "observed_at": "2026-08-16T12:00:00Z",
            "value": 100,
            "unit": "percent",
            "unofficial_paths_deleted": True,
        }
    )
    errors = MODULE.evaluate(*inputs)
    assert "vanity indicator: adoption-percentage" in errors
    assert "adoption hides worse job time" not in errors


def test_failure_injection_rejects_adoption_hiding_wait() -> None:
    errors = MODULE.evaluate(*FAILURE.injected_inputs())
    samples = FAILURE.injected_inputs()[3]
    sampled = {item["indicator"] for item in samples["samples"]}
    assert "vanity indicator: adoption-percentage" in errors
    assert "adoption hides worse job time" in errors
    assert "catalog-freshness" in sampled
    assert "paved-road-completion" in sampled
