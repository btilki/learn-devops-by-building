#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "observability/contract.json"
SCENARIO = ROOT / "fixtures/telemetry/payment-degradation.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(payment_degradation: bool = False) -> dict[str, bool]:
    contract = read(CONTRACT)
    logs = contract["logs"]
    metric = contract["metrics"]["request_counter"]
    traces = contract["traces"]
    attributes = set(contract["resource_attributes"])
    indicators = set(contract["service_level_indicators"])
    objectives = contract.get("service_level_objectives", [])
    alerts = contract["alerts"]
    log_fields = set(logs["fields"])
    labels = set(metric["labels"])
    checks = {
        "structured_logs": logs["format"] == "json",
        "correlation_fields": {"trace_id", "request_id"} <= log_fields,
        "bounded_metric_labels": not labels.intersection({"user_id", "order_id", "request_id"}),
        "route_and_status_dimensions": {"route", "status"} <= labels,
        "trace_context_propagated": "traceparent" in traces["propagate"],
        "release_identity_recorded": {
            "service.version",
            "deployment.environment.name",
        }
        <= attributes,
        "user_visible_indicators": {"order_success_ratio", "order_latency"} <= indicators,
        "order_objective_defined": any(
            item.get("indicator") == "order_success_ratio"
            and 0 < item.get("target", 0) < 1
            and item.get("window")
            for item in objectives
        ),
        "burn_alert_present": any(item.get("signal") == "error_budget_burn" for item in alerts),
    }
    if payment_degradation:
        scenario = read(SCENARIO)
        failed_orders = [r for r in scenario["requests"] if r["route"] == "/orders" and r["status"] >= 500]
        checks["order_failure_detected"] = bool(failed_orders) and "order_success_ratio" in indicators
        checks["payment_dependency_isolated"] = bool(failed_orders) and "traceparent" in traces["propagate"]
        checks["catalog_not_declared_failed"] = all(r["status"] < 500 for r in scenario["requests"] if r["route"] == "/catalog")
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["payment-degradation"])
    args = parser.parse_args()
    checks = analyze(args.scenario == "payment-degradation")
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
