#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "delivery/rollout.json"
FAILURE = ROOT / "fixtures/rollout/candidate-payment-failure.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(failure: bool = False) -> dict[str, bool]:
    contract = read(CONTRACT)
    analysis = contract["analysis"]
    rollback = contract["rollback"]
    handoff = contract.get("handoff", {})
    steps = contract["steps"]
    indicators = set(analysis["indicators"])
    checks = {
        "progressive_strategy": contract["strategy"] == "canary",
        "immutable_stable": "@sha256:" in contract["stable_artifact"],
        "immutable_candidate": "@sha256:" in contract["candidate_artifact"],
        "bounded_first_cohort": bool(steps) and 0 < steps[0]["traffic_percent"] <= 10,
        "multiple_evaluation_steps": len(steps) >= 3,
        "traffic_advances_monotonically": [step["traffic_percent"] for step in steps]
        == sorted({step["traffic_percent"] for step in steps}),
        "minimum_evidence_volume": analysis["minimum_requests"] >= 50,
        "user_visible_gates": {"order_success_ratio", "order_latency"} <= indicators,
        "automatic_abort": analysis["automatic_abort"] is True,
        "inconclusive_pauses": analysis.get("inconclusive_action") == "pause",
        "candidate_comes_from_verified_release": handoff.get("candidate_source")
        == "verified-release-digest",
        "candidate_change_is_reviewed": handoff.get("proposal_path")
        == "reviewed-delivery-change",
        "stable_transition_is_reviewed": handoff.get("promotion_path")
        == "controller-authored-reviewed-change",
        "stable_changes_only_after_full_verification": handoff.get("stable_transition")
        == "copy-candidate-after-100-percent-and-recovery-verification",
        "protected_promotion": contract["promotion_authority"] == "production-release-approver",
        "immutable_rollback": "@sha256:" in rollback["target"],
        "rollback_targets_stable": rollback["target"] == contract["stable_artifact"],
        "rollback_verifies_recovery": rollback["verify_indicators"] is True,
    }
    if failure:
        scenario = read(FAILURE)
        candidate = scenario["candidate"]
        enough = candidate["requests"] >= analysis["minimum_requests"]
        bad = candidate["order_success_ratio"] < analysis.get("minimum_success_ratio", 1)
        slow = candidate["order_latency_p95_ms"] > analysis.get("maximum_latency_p95_ms", 0)
        checks["ready_is_not_success"] = candidate["ready"] is True and (bad or slow)
        checks["candidate_aborts"] = enough and (bad or slow) and analysis["automatic_abort"] is True
        checks["stable_remains_healthy"] = scenario["stable"]["order_success_ratio"] >= 0.995
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["candidate-payment-failure"])
    args = parser.parse_args()
    checks = analyze(args.scenario == "candidate-payment-failure")
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
