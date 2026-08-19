#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from tools.capacity_evaluate import evaluate
except ModuleNotFoundError:
    from capacity_evaluate import evaluate

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "finops/capacity-contract.json"
FAILURE = ROOT / "fixtures/finops/cheap-but-slow.json"
EXPECTATIONS = ROOT / "finops/decision-expectations.json"
ASSUMPTIONS = ROOT / "finops/unit-cost-assumptions.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(failure: bool = False) -> dict[str, bool]:
    contract = read(CONTRACT)
    scenario = read(FAILURE)
    assumptions = read(ASSUMPTIONS)
    evaluation = evaluate(scenario, read(EXPECTATIONS), assumptions)
    calculated = evaluation["calculated"]
    gates = evaluation["gates"]
    recovery_result = evaluation["recovery"]
    allocation = contract["allocation"]
    economics = contract["economics"]
    reliability = contract["reliability_evidence"]
    capacity = contract["capacity"]
    financial = contract["financial_controls"]
    change = contract["optimization_change"]
    governance = contract["governance"]
    checks = {
        "cost_has_ownership_dimensions": all(
            allocation[key] is True for key in ("owner", "service", "environment", "cost_center")
        ),
        "shared_costs_have_policy": allocation["shared_cost_policy"] == "documented-allocation",
        "unit_economics_use_business_outcome": economics["unit"] == "cost-per-successful-order",
        "unit_denominator_is_quality_gated": economics["denominator_quality_gate"] is True,
        "delivery_cost_is_measured": economics["delivery_cost_measured"] is True,
        "unit_cost_currency_is_explicit": assumptions["currency"] == scenario["currency"],
        "unit_cost_window_is_explicit": assumptions["observation_window"]
        == scenario["observation_window"],
        "unit_cost_basis_is_amortized": assumptions["cost_basis"] == "amortized",
        "unit_cost_components_are_explicit": set(assumptions["workload_cost_components"])
        == set(scenario["baseline"]["workload_costs"])
        == set(scenario["candidate"]["workload_costs"]),
        "delivery_cost_stays_separate": assumptions["delivery_cost_treatment"]
        == "reported-separately"
        and calculated["baseline_delivery_cost"] == 6.0,
        "denominator_is_terminal_outcome": assumptions["denominator"]
        == "quality-qualified-terminal-orders",
        "shared_allocation_is_declared": assumptions["shared_allocation_method"]
        == "documented-fixed-capacity-share",
        "cost_is_joined_to_reliability": all(reliability.values()),
        "requests_are_measured": capacity["requests_based_on_measurement"] is True,
        "autoscaling_includes_work_signal": "oldest-message-age" in capacity["autoscaling_metrics"],
        "minimum_capacity_preserves_recovery": capacity["minimum_capacity"] == "tested-recovery-floor",
        "maximum_capacity_is_tested": capacity["maximum_capacity_tested"] is True,
        "headroom_is_explicit": capacity["headroom_policy"] == "failure-and-growth-tested",
        "dependency_capacity_is_bounded": capacity["dependency_limit"] == "provider-rate-limit",
        "downscale_is_stabilized": capacity["downscale_stabilization"] is True,
        "forecast_exists": financial["forecast"] is True,
        "budget_alerts_are_predictive": financial["budget_alerts"] == "forecast-and-anomaly",
        "anomaly_has_owner": financial["anomaly_owner"] == "service-owner",
        "commitments_follow_baseline": financial["commitments_after_baseline"] is True,
        "optimization_is_reviewed": change["reviewed"] is True,
        "optimization_is_progressive": change["progressive"] is True,
        "optimization_is_reliability_gated": change["reliability_gated"] is True,
        "rollback_capacity_is_known": change["rollback_capacity"] == "last-verified-envelope",
        "evidence_window_is_defined": change["evidence_window"] == "peak-and-recovery",
        "exceptions_expire": governance["exception_expiry"] is True,
        "showback_is_team_scoped": governance["team_showback"] is True,
        "individual_ranking_is_forbidden": governance["individual_ranking_forbidden"] is True,
        "spend_change_is_computed": calculated["spend_change_percent"] == -34.0,
        "unit_cost_change_is_computed": calculated["unit_cost_change_percent"] == -8.0,
        "success_gate_is_evaluated": gates["order_success"] is True,
        "completion_gate_is_evaluated": gates["completion_latency"] is False,
        "backlog_age_gate_is_evaluated": gates["oldest_message_age"] is False,
        "decision_rejects_false_savings": evaluation["decision"] == "reject",
        "verified_capacity_drains_backlog": (
            recovery_result["backlog_drained"] is True
            and recovery_result["backlog_never_increased"] is True
        ),
        "recovery_respects_provider_limit": recovery_result["provider_limit_respected"] is True,
    }
    if failure:
        outcome_harm = not all(gates.values())
        checks["spend_reduction_is_real"] = calculated["spend_change_percent"] < 0
        checks["unit_cost_does_not_prove_health"] = (
            calculated["unit_cost_change_percent"] < 0 and outcome_harm
        )
        checks["backlog_harm_is_detected"] = gates["oldest_message_age"] is False
        checks["optimization_is_rejected"] = evaluation["decision"] == "reject"
        checks["recovery_restores_verified_capacity"] = (
            change["rollback_capacity"] == "last-verified-envelope"
            and recovery_result["backlog_drained"] is True
            and recovery_result["provider_limit_respected"] is True
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["cheap-but-slow"])
    args = parser.parse_args()
    checks = analyze(args.scenario == "cheap-but-slow")
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
