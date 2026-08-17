from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_RTO = {"as-fast-as-possible", "asap", "unmeasured"}
REQUIRED_RESTORES = {
    "devops-one-environment-reconstruction",
    "platform-plane-restore",
}
REQUIRED_PROVIDERS = {"payment", "warehouse"}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    architecture: dict,
    objectives: dict,
    constraints: dict,
    platform_recovery: dict,
    tenancy: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    regions = {item.get("id") for item in architecture.get("regions") or []}
    if len(regions) < 2:
        errors.append("missing required region: region-standby")
    if architecture.get("mode") != "active-passive":
        errors.append("failover order is not active-passive")
    order = architecture.get("failover_order") or []
    if not order:
        errors.append("missing failover order")
    elif order[0].get("from") == order[0].get("to"):
        errors.append("missing failover order")

    rto = objectives.get("rto_seconds", objectives.get("rto"))
    rpo = objectives.get("rpo_seconds", objectives.get("rpo"))
    if rto in FORBIDDEN_RTO or not isinstance(rto, int) or isinstance(rto, bool):
        errors.append(f"rto is not numeric: {rto}")
    elif rto <= 0:
        errors.append(f"rto is not numeric: {rto}")
    if not isinstance(rpo, int) or isinstance(rpo, bool) or rpo <= 0:
        errors.append(f"rpo is not numeric: {rpo}")
    if "recovered" in objectives or objectives.get("status") == "recovered":
        errors.append("architecture emits recovered")

    isolation = constraints.get("isolation") or {}
    tenants = set(isolation.get("tenants") or [])
    expected_tenants = set(tenancy.get("tenants") or [])
    if not expected_tenants.issubset(tenants) or not isolation.get(
        "survives_failover"
    ):
        errors.append("missing isolation constraint")

    scoped = {
        item.get("provider")
        for item in constraints.get("provider_regionality") or []
        if item.get("constraint") == "region-scoped"
    }
    for provider in REQUIRED_PROVIDERS:
        if provider not in scoped:
            errors.append(f"missing provider regionality: {provider}")

    restores = set(constraints.get("insufficient_restores") or [])
    if constraints.get("claims") == "regional-recovery":
        errors.append("inherited restore claimed as regional recovery")
    if constraints.get("recovery"):
        errors.append("inherited restore claimed as regional recovery")
    if not REQUIRED_RESTORES.issubset(restores):
        errors.append("inherited restore claimed as regional recovery")

    identities = [str(item) for item in constraints.get("insufficient_identities") or []]
    plane = str(platform_recovery.get("plane_last_known_good"))
    contract = str(platform_recovery.get("contract_last_known_good"))
    if plane not in identities or contract not in identities:
        errors.append("collapsed restore identities")
    if plane == contract or len(set(identities)) < 2:
        errors.append("collapsed restore identities")

    consumed = set(constraints.get("limitations_consumed") or [])
    required_limits = set(platform_recovery.get("limitations") or [])
    if not required_limits.issubset(consumed):
        errors.append("inherited restore claimed as regional recovery")

    expected_rto = expectations.get("rto_seconds")
    expected_rpo = expectations.get("rpo_seconds")
    if isinstance(rto, int) and expected_rto and rto != expected_rto:
        errors.append(f"rto is not numeric: {rto}")
    if isinstance(rpo, int) and expected_rpo and rpo != expected_rpo:
        errors.append(f"rpo is not numeric: {rpo}")

    return list(dict.fromkeys(errors))


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-12"
    return (
        load(ROOT / "regions" / "architecture.yaml"),
        load(ROOT / "regions" / "objectives.yaml"),
        load(ROOT / "regions" / "constraints.yaml"),
        load(ROOT / "inherited" / "platform-v1.0" / "recovery" / "interface.yaml"),
        load(ROOT / "inherited" / "platform-v1.0" / "tenancy" / "interface.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
