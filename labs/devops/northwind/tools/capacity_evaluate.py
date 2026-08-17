#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "fixtures/finops/cheap-but-slow.json"
EXPECTATIONS = ROOT / "finops/decision-expectations.json"
ASSUMPTIONS = ROOT / "finops/unit-cost-assumptions.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(
    scenario: dict[str, object],
    expectations: dict[str, object],
    assumptions: dict[str, object],
) -> dict[str, object]:
    baseline = scenario["baseline"]
    candidate = scenario["candidate"]
    recovery = scenario["recovery"]
    components = assumptions["workload_cost_components"]
    baseline_cost = sum(baseline["workload_costs"][name] for name in components)
    candidate_cost = sum(candidate["workload_costs"][name] for name in components)
    baseline_unit_cost = baseline_cost / baseline["quality_qualified_terminal_orders"]
    candidate_unit_cost = candidate_cost / candidate["quality_qualified_terminal_orders"]
    spend_change = (candidate_cost / baseline_cost - 1) * 100
    unit_cost_change = (candidate_unit_cost / baseline_unit_cost - 1) * 100
    gates = {
        "order_success": candidate["order_success_ratio"]
        >= expectations["minimum_order_success_ratio"],
        "completion_latency": candidate["order_completion_p95_seconds"]
        <= expectations["maximum_order_completion_p95_seconds"],
        "oldest_message_age": candidate["oldest_message_age_seconds"]
        <= expectations["maximum_oldest_message_age_seconds"],
    }

    backlog = recovery["initial_backlog"]
    samples = [backlog]
    provider_limit_respected = (
        recovery["verified_processing_rate_per_minute"] <= recovery["provider_limit_per_minute"]
    )
    for _ in range(recovery["minutes"]):
        backlog = max(
            0,
            backlog
            + recovery["arrival_rate_per_minute"]
            - recovery["verified_processing_rate_per_minute"],
        )
        samples.append(backlog)
    recovery_result = {
        "initial_backlog": samples[0],
        "final_backlog": samples[-1],
        "backlog_drained": samples[-1] == 0,
        "backlog_never_increased": all(later <= earlier for earlier, later in zip(samples, samples[1:])),
        "provider_limit_respected": provider_limit_respected,
    }
    return {
        "calculated": {
            "currency": scenario["currency"],
            "observation_window": scenario["observation_window"],
            "baseline_workload_cost": round(baseline_cost, 2),
            "candidate_workload_cost": round(candidate_cost, 2),
            "baseline_delivery_cost": baseline["delivery_cost"],
            "candidate_delivery_cost": candidate["delivery_cost"],
            "baseline_quality_qualified_orders": baseline[
                "quality_qualified_terminal_orders"
            ],
            "candidate_quality_qualified_orders": candidate[
                "quality_qualified_terminal_orders"
            ],
            "baseline_unit_cost": round(baseline_unit_cost, 4),
            "candidate_unit_cost": round(candidate_unit_cost, 4),
            "spend_change_percent": round(spend_change, 1),
            "unit_cost_change_percent": round(unit_cost_change, 1),
        },
        "gates": gates,
        "decision": "accept" if all(gates.values()) else "reject",
        "recovery": recovery_result,
    }


def main() -> int:
    report = evaluate(read(SCENARIO), read(EXPECTATIONS), read(ASSUMPTIONS))
    print(json.dumps(report, indent=2))
    recovery = report["recovery"]
    return 0 if report["decision"] == "reject" and recovery["backlog_drained"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
