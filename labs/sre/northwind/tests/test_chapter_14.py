from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-14" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_14_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_failover_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_mixed_replay_recovered_and_reconstruction_fail() -> None:
    (
        plan,
        trace,
        isolation,
        verification,
        architecture,
        objectives,
        constraints,
        policy_actions,
        rotations,
        journeys,
        catalog,
        observations,
        platform_recovery,
        tenancy,
        expectations,
    ) = MODULE.completed_inputs()
    plan["target"] = "region-primary"
    plan["recovery"] = "devops-one-environment-reconstruction"
    plan["last_known_good"] = [{"region": "region-primary", "identity": "newest"}]
    isolation["fulfillment_intent"] = "storefront"
    isolation["mixed_replay"] = "applied"
    isolation["survives_failover"] = False
    verification["status"] = "recovered"
    verification["inherited_restores_insufficient"] = False
    errors = MODULE.evaluate(
        plan,
        trace,
        isolation,
        verification,
        architecture,
        objectives,
        constraints,
        policy_actions,
        rotations,
        journeys,
        catalog,
        observations,
        platform_recovery,
        tenancy,
        expectations,
    )
    assert "mixed-region replay applied" in errors
    assert "mixed-tenant replay accepted" in errors
    assert "verification emits recovered" in errors
    assert "inherited restore claimed as portfolio recovery" in errors


def test_missed_rto_rpo_job_time_and_collapsed_isolation_fail() -> None:
    (
        plan,
        trace,
        isolation,
        verification,
        architecture,
        objectives,
        constraints,
        policy_actions,
        rotations,
        journeys,
        catalog,
        observations,
        platform_recovery,
        tenancy,
        expectations,
    ) = MODULE.completed_inputs()
    trace["elapsed_seconds"] = 86400
    trace["rpo_lost_seconds"] = 7200
    trace["lost_isolated"] = False
    verification["elapsed_seconds"] = 86400
    verification["rpo_lost_seconds"] = 7200
    verification["isolation_holds"] = False
    verification["journeys"] = ["time-to-first-environment"]
    errors = MODULE.evaluate(
        plan,
        trace,
        isolation,
        verification,
        architecture,
        objectives,
        constraints,
        policy_actions,
        rotations,
        journeys,
        catalog,
        observations,
        platform_recovery,
        tenancy,
        expectations,
    )
    assert "rto missed: 86400" in errors
    assert "rpo missed: 7200" in errors
    assert "job-time claimed as portfolio recovery" in errors
    assert "lost region is not isolated" in errors
    assert "isolation collapsed" in errors
    assert "missing required journey in verification" in errors


def test_listed_journeys_do_not_meet_slo_from_observations() -> None:
    (
        plan,
        trace,
        isolation,
        verification,
        architecture,
        objectives,
        constraints,
        policy_actions,
        rotations,
        journeys,
        catalog,
        observations,
        platform_recovery,
        tenancy,
        expectations,
    ) = MODULE.completed_inputs()
    verification["slo_met"] = True
    for item in observations["observations"]:
        item["good_events"] = 500
        item["valid_events"] = 1000
    errors = MODULE.evaluate(
        plan,
        trace,
        isolation,
        verification,
        architecture,
        objectives,
        constraints,
        policy_actions,
        rotations,
        journeys,
        catalog,
        observations,
        platform_recovery,
        tenancy,
        expectations,
    )
    assert "verification emits slo_met" in errors
    assert "journey slo not met: accept-and-complete-order/order_success_ratio" in errors
    assert "journey slo not met: dispatch-fulfillment/dispatch_success_ratio" in errors
