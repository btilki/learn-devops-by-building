from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-11" / "evaluate.py"
FAILURE_PATH = ROOT / "checkpoints" / "chapter-11" / "failure.py"
SPEC = importlib.util.spec_from_file_location("chapter_11_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FAILURE_SPEC = importlib.util.spec_from_file_location("chapter_11_failure", FAILURE_PATH)
assert FAILURE_SPEC and FAILURE_SPEC.loader
FAILURE = importlib.util.module_from_spec(FAILURE_SPEC)
FAILURE_SPEC.loader.exec_module(FAILURE)


def test_completed_quota_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_fulfillment_burst_starves_storefront() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for entry in inputs[2]["entries"]:
        if entry["tenant"] == "fulfillment" and entry["unit"] == "environment-hour":
            entry["usage"] = 24
            entry["billed_units"] = 24
    errors = MODULE.evaluate(*inputs)
    assert "peer floor starved: storefront" in errors
    assert "tenant exceeds ceiling: fulfillment" in errors


def test_order_metric_as_showback_unit_fails() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[2]["entries"].append(
        {
            "tenant": "fulfillment",
            "unit": "order_success_ratio",
            "usage": 1,
            "billed_units": 1,
            "quality_gate_passed": True,
        }
    )
    errors = MODULE.evaluate(*inputs)
    assert "showback unit is tenant workload: order_success_ratio" in errors


def test_successful_provision_reads_chapter_10_sample() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    inputs[10]["samples"] = [
        item
        for item in inputs[10]["samples"]
        if item["indicator"] != "time-to-first-environment"
    ]
    errors = MODULE.evaluate(*inputs)
    assert "showback quality gate not met: fulfillment/successful-provision" in errors


def test_burst_deny_reads_chapter_03() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for entry in inputs[2]["entries"]:
        if entry["tenant"] == "fulfillment" and entry["unit"] == "environment-hour":
            entry["usage"] = 24
            entry["billed_units"] = 24
    for dimension in inputs[4]["dimensions"]:
        if dimension["id"] == "quota":
            dimension["denied_inheritance"] = []
    errors = MODULE.evaluate(*inputs)
    assert "peer floor starved: storefront" in errors
    assert "unlimited burst into peer quota: fulfillment" not in errors


def test_implied_floor_reads_chapter_06_leases() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for row in inputs[0]["tenants"]:
        row.pop("floor", None)
        row.pop("ceiling", None)
    for entry in inputs[2]["entries"]:
        if entry["tenant"] == "fulfillment" and entry["unit"] == "environment-hour":
            entry["usage"] = 24
            entry["billed_units"] = 24
    for lease in inputs[7]["leases"]:
        if lease["tenant"] == "storefront":
            lease["quota"]["units"] = 0
    errors = MODULE.evaluate(*inputs)
    assert "peer floor starved: storefront" not in errors


def test_ceiling_cannot_consume_peer_floor() -> None:
    inputs = [copy.deepcopy(item) for item in MODULE.completed_inputs()]
    for row in inputs[0]["tenants"]:
        if row["tenant"] == "fulfillment":
            row["ceiling"] = 21
    errors = MODULE.evaluate(*inputs)
    assert "ceiling leaves no peer floor: fulfillment" in errors


def test_failure_injection_rejects_burst_and_keeps_storefront() -> None:
    errors = MODULE.evaluate(*FAILURE.injected_inputs())
    showback = FAILURE.injected_inputs()[2]
    policy = FAILURE.injected_inputs()[0]
    usage = {
        (item["tenant"], item["unit"]): item["usage"] for item in showback["entries"]
    }
    floors = {item["tenant"]: item["floor"] for item in policy["tenants"]}
    assert "tenant exceeds ceiling: fulfillment" in errors
    assert "peer floor starved: storefront" in errors
    assert "unlimited burst into peer quota: fulfillment" in errors
    assert "showback counts starved burst as useful unit: fulfillment" in errors
    assert usage[("storefront", "environment-hour")] == 12
    assert usage[("fulfillment", "successful-provision")] == 1
    assert floors["storefront"] == 12
    assert floors["fulfillment"] == 12
