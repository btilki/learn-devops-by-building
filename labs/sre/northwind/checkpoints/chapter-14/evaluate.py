from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_RESTORES = {
    "devops-one-environment-reconstruction",
    "platform-plane-restore",
}
REQUIRED_EVIDENCE = {"gameday-regional-loss-tabletop", "mixed-backup"}
REQUIRED_REPLAYS = {"mixed-tenant", "mixed-region"}
REQUIRED_JOURNEYS = {"accept-and-complete-order", "dispatch-fulfillment"}
REQUIRED_LIMITS = {"not-regional-loss", "not-portfolio-rto"}
JOB_TIME = {
    "time-to-first-environment",
    "paved-road-completion",
    "catalog-freshness",
}
FORBIDDEN_COMMANDERS = {"slack", "chat-history", "whoever-answered"}
COLLAPSED_LKG = {"1.0", "tenant-storage-1.0", "newest"}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _walk_recovered(obj: object, errors: list[str], loc: str) -> None:
    if isinstance(obj, dict):
        current = str(obj.get("id") or loc)
        for key, value in obj.items():
            if key == "recovered" or value == "recovered":
                errors.append("verification emits recovered")
            if key == "status" and value == "recovered":
                errors.append("verification emits recovered")
            if key == "slo_met":
                errors.append("verification emits slo_met")
            _walk_recovered(value, errors, current)
    elif isinstance(obj, list):
        for item in obj:
            _walk_recovered(item, errors, loc)


def evaluate(
    plan: dict,
    trace: dict,
    isolation: dict,
    verification: dict,
    architecture: dict,
    objectives: dict,
    constraints: dict,
    policy_actions: dict,
    rotations: dict,
    journeys: dict,
    catalog: dict,
    observations: dict,
    platform_recovery: dict,
    tenancy: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    _walk_recovered(plan, errors, "plan")
    _walk_recovered(trace, errors, "trace")
    _walk_recovered(isolation, errors, "isolation")
    _walk_recovered(verification, errors, "verification")

    order = architecture.get("failover_order") or []
    expected_from = order[0].get("from") if order else "region-primary"
    expected_to = order[0].get("to") if order else "region-standby"
    expected_when = order[0].get("when") if order else "region-primary-lost"
    if plan.get("follows") != architecture.get("id"):
        errors.append("plan does not follow architecture")
    if (
        plan.get("lost") != expected_from
        or plan.get("target") != expected_to
        or plan.get("when") != expected_when
        or plan.get("lost") == plan.get("target")
        or plan.get("mode") != "active-passive"
    ):
        errors.append("plan does not follow architecture")
    if (
        trace.get("from") != plan.get("lost")
        or trace.get("to") != plan.get("target")
        or trace.get("when") != plan.get("when")
    ):
        errors.append("plan does not follow architecture")
    if not trace.get("lost_isolated"):
        errors.append("lost region is not isolated")

    primaries = {
        item.get("primary") for item in rotations.get("rotations") or []
    }
    commander = plan.get("commander")
    if commander in FORBIDDEN_COMMANDERS or commander not in primaries:
        errors.append("commander is not an on-call primary")

    restores = set(plan.get("insufficient_restores") or [])
    if plan.get("recovery") or not REQUIRED_RESTORES.issubset(restores):
        errors.append("inherited restore claimed as portfolio recovery")
    if not verification.get("inherited_restores_insufficient"):
        errors.append("inherited restore claimed as portfolio recovery")

    identities = [str(item) for item in plan.get("insufficient_identities") or []]
    plane = str(platform_recovery.get("plane_last_known_good"))
    contract = str(platform_recovery.get("contract_last_known_good"))
    if plane not in identities or contract not in identities:
        errors.append("collapsed restore identities")
    if plane == contract or len(set(identities)) < 2:
        errors.append("collapsed restore identities")

    evidence = set(plan.get("insufficient_evidence") or [])
    if not REQUIRED_EVIDENCE.issubset(evidence):
        errors.append("game day claimed as portfolio recovery")

    for item in plan.get("last_known_good") or []:
        if str(item.get("identity")) in COLLAPSED_LKG:
            errors.append("mixed-region replay applied")

    expected_tenants = set(tenancy.get("tenants") or [])
    tenant_rows = isolation.get("tenants") or []
    tenant_ids = [item.get("id") for item in tenant_rows]
    if isolation.get("fulfillment_intent") == "storefront":
        errors.append("mixed-tenant replay accepted")
    if isolation.get("mixed_replay") == "applied":
        errors.append("mixed-tenant replay accepted")
    if len(set(tenant_ids)) < 2 or not expected_tenants.issubset(set(tenant_ids)):
        errors.append("mixed-tenant replay accepted")
    if not isolation.get("survives_failover"):
        errors.append("isolation collapsed")
    if isolation.get("source") != "explicit-tenant-decision":
        errors.append("missing continue or freeze")
    rejected = set(isolation.get("rejected_replays") or [])
    if not REQUIRED_REPLAYS.issubset(rejected):
        errors.append("mixed-tenant replay accepted")

    policy_ids = {item.get("id") for item in policy_actions.get("actions") or []}
    for item in tenant_rows:
        if not item.get("serving") or not item.get("change"):
            errors.append("missing continue or freeze")
        if item.get("policy_join") not in policy_ids:
            errors.append("missing continue or freeze")
        if str(item.get("last_known_good")) in COLLAPSED_LKG:
            errors.append("mixed-region replay applied")

    constraint_isolation = constraints.get("isolation") or {}
    if not constraint_isolation.get("survives_failover"):
        errors.append("isolation collapsed")

    journey_ids = {item.get("id") for item in journeys.get("journeys") or []}
    verified = set(verification.get("journeys") or [])
    required_journeys = set(expectations.get("required_journeys") or []) | REQUIRED_JOURNEYS
    if not required_journeys.issubset(verified):
        errors.append("missing required journey in verification")
    if not verified.issubset(journey_ids | JOB_TIME):
        errors.append("missing required journey in verification")
    if verified & JOB_TIME:
        errors.append("job-time claimed as portfolio recovery")

    observation_by_slo = {
        item.get("slo"): item for item in observations.get("observations") or []
    }
    for journey_id in sorted(required_journeys):
        matching = [
            item
            for item in catalog.get("slos") or []
            if item.get("journey") == journey_id and item.get("criticality") == "critical"
        ]
        if not matching:
            errors.append(f"missing required journey slo: {journey_id}")
            continue
        for slo in matching:
            slo_id = slo.get("id", "unknown")
            sli = slo.get("sli")
            observation = observation_by_slo.get(slo_id)
            if observation is None:
                errors.append(f"missing failover observation: {slo_id}")
                continue
            try:
                good = int(observation["good_events"])
                valid = int(observation["valid_events"])
                target = Fraction(slo["target"]).limit_denominator(10000)
                if valid <= 0 or good < 0 or good > valid:
                    raise ValueError("out of range")
                if Fraction(good, valid) < target:
                    errors.append(f"journey slo not met: {journey_id}/{sli}")
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                errors.append(f"journey slo not met: {journey_id}/{sli}")

    rto = objectives.get("rto_seconds", expectations.get("rto_seconds"))
    rpo = objectives.get("rpo_seconds", expectations.get("rpo_seconds"))
    elapsed = verification.get("elapsed_seconds", verification.get("elapsed"))
    lost = verification.get("rpo_lost_seconds", verification.get("rpo"))
    if elapsed != trace.get("elapsed_seconds"):
        errors.append("trace and verification disagree")
    if lost != trace.get("rpo_lost_seconds"):
        errors.append("trace and verification disagree")
    if not isinstance(elapsed, int) or isinstance(elapsed, bool) or elapsed > rto:
        errors.append(f"rto missed: {elapsed}")
    if not isinstance(lost, int) or isinstance(lost, bool) or lost > rpo:
        errors.append(f"rpo missed: {lost}")
    if not verification.get("isolation_holds"):
        errors.append("isolation collapsed")
    if verification.get("mixed_replay") != "rejected":
        errors.append("mixed-tenant replay accepted")

    consumed = set(verification.get("limitations_consumed") or [])
    required_limits = set(platform_recovery.get("limitations") or []) | REQUIRED_LIMITS
    if not required_limits.issubset(consumed):
        errors.append("inherited restore claimed as portfolio recovery")

    return list(dict.fromkeys(errors))


def completed_inputs() -> tuple:
    checkpoint = ROOT / "checkpoints" / "chapter-14"
    return (
        load(ROOT / "failover" / "plan.yaml"),
        load(ROOT / "failover" / "trace.yaml"),
        load(ROOT / "failover" / "isolation.yaml"),
        load(ROOT / "failover" / "verification.yaml"),
        load(ROOT / "regions" / "architecture.yaml"),
        load(ROOT / "regions" / "objectives.yaml"),
        load(ROOT / "regions" / "constraints.yaml"),
        load(ROOT / "policy" / "actions.yaml"),
        load(ROOT / "oncall" / "rotations.yaml"),
        load(ROOT / "reliability" / "journeys.yaml"),
        load(ROOT / "slos" / "catalog.yaml"),
        load(ROOT / "fixtures" / "observations" / "chapter-14.yaml"),
        load(ROOT / "inherited" / "platform-v1.0" / "recovery" / "interface.yaml"),
        load(ROOT / "inherited" / "platform-v1.0" / "tenancy" / "interface.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
