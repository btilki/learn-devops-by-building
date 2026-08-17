from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    policy: dict,
    units: dict,
    showback: dict,
    tenants: dict,
    isolation: dict,
    sharing: dict,
    users: dict,
    leases: dict,
    env_product: dict,
    indicators: dict,
    samples: dict,
    non_metrics: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    tenant_ids = {item["id"] for item in tenants.get("tenants", [])}
    shared_ids = {item["id"] for item in sharing.get("shared", [])}
    quota_dim = next(
        (item for item in isolation.get("dimensions", []) if item.get("id") == "quota"),
        {},
    )
    denied_quota = set(quota_dim.get("denied_inheritance", []))
    required_pool = expectations.get("required_pool")
    lease_units: dict[str, int] = {}
    for lease in leases.get("leases", []):
        quota = lease.get("quota", {})
        if quota.get("pool") == required_pool:
            tenant_id = lease["tenant"]
            lease_units[tenant_id] = lease_units.get(tenant_id, 0) + int(quota["units"])
    sampled_ttf = {
        item.get("tenant")
        for item in samples.get("samples", [])
        if item.get("indicator") == "time-to-first-environment"
    }
    job_proofs = {item["id"] for item in indicators.get("indicators", [])}
    vanity = {
        item["id"]
        for item in non_metrics.get("non_metrics", [])
        if item.get("category") == "vanity"
    }
    tenant_workload = {
        item["id"]
        for item in non_metrics.get("non_metrics", [])
        if item.get("category") == "tenant-workload"
    }
    unit_by_id = {item["id"]: item for item in units.get("units", [])}
    pool = policy.get("pool")
    if pool != required_pool:
        errors.append("quota pool is not cluster-capacity-pool")
    if pool != env_product.get("quota_pool"):
        errors.append("quota pool does not match environment product")
    if pool not in shared_ids:
        errors.append("quota pool is not a chapter 3 shared surface")
    if units.get("pool") != pool:
        errors.append("unit catalog pool mismatch")
    if showback.get("pool") != pool:
        errors.append("showback pool mismatch")
    if policy.get("owner") not in user_ids:
        errors.append(f"policy has no known owner: {policy.get('owner')}")

    capacity = int(policy.get("capacity") or 0)
    policy_tenants = {item["tenant"]: item for item in policy.get("tenants", [])}
    for tenant_id in tenant_ids:
        if tenant_id not in policy_tenants:
            errors.append(f"missing quota tenant: {tenant_id}")
    floor: dict[str, int | None] = {}
    ceiling: dict[str, int | None] = {}
    for tenant_id, row in policy_tenants.items():
        if tenant_id not in tenant_ids:
            errors.append(f"quota tenant is unknown: {tenant_id}")
        floor_val = row.get("floor") if isinstance(row.get("floor"), int) else None
        ceil_val = row.get("ceiling") if isinstance(row.get("ceiling"), int) else None
        floor[tenant_id] = floor_val
        ceiling[tenant_id] = ceil_val
        if floor_val is None or floor_val < 1:
            errors.append(f"missing tenant floor: {tenant_id}")
        if ceil_val is None or ceil_val < 1:
            errors.append(f"missing tenant ceiling: {tenant_id}")
        if floor_val is not None and ceil_val is not None and floor_val > ceil_val:
            errors.append(f"floor exceeds ceiling: {tenant_id}")
        committed = lease_units.get(tenant_id, 0)
        if floor_val is not None and floor_val < committed:
            errors.append(f"floor below lease commitment: {tenant_id}")

    for tenant_id, ceil_val in ceiling.items():
        if ceil_val is None:
            continue
        for peer_id in tenant_ids:
            if peer_id == tenant_id:
                continue
            peer_floor = floor.get(peer_id)
            reserved = peer_floor if peer_floor is not None else lease_units.get(peer_id, 0)
            if reserved and ceil_val + reserved > capacity:
                errors.append(f"ceiling leaves no peer floor: {tenant_id}")
                break

    for required_unit in expectations.get("required_units", []):
        if required_unit not in unit_by_id:
            errors.append(f"missing required unit: {required_unit}")
    expected_gates = expectations.get("quality_gates", {})
    for item in units.get("units", []):
        unit_id = item.get("id")
        if item.get("owner") not in user_ids:
            errors.append(f"unit has no known owner: {unit_id}")
        if unit_id in tenant_workload:
            errors.append(f"unit is tenant workload: {unit_id}")
        if unit_id in vanity:
            errors.append(f"unit is vanity: {unit_id}")
        if unit_id in job_proofs:
            errors.append(f"unit is job proof: {unit_id}")
        if unit_id == "environment-hour" and item.get("meters") != pool:
            errors.append("environment-hour does not meter cluster-capacity-pool")
        expected_gate = expected_gates.get(unit_id)
        if expected_gate and item.get("quality_gate") != expected_gate:
            errors.append(f"unit quality gate mismatch: {unit_id}")

    usage: dict[str, int] = dict(lease_units)
    billed_pool: dict[str, int] = {}
    gated_pool: dict[str, bool] = {}
    for entry in showback.get("entries", []):
        tenant_id = entry.get("tenant")
        unit_id = entry.get("unit")
        billed = int(entry.get("billed_units") or 0)
        used = int(entry.get("usage") or 0)
        passed = bool(entry.get("quality_gate_passed"))
        if tenant_id not in tenant_ids:
            errors.append(f"showback tenant is unknown: {tenant_id}")
        if unit_id in tenant_workload:
            errors.append(f"showback unit is tenant workload: {unit_id}")
        elif unit_id in vanity:
            errors.append(f"showback unit is vanity: {unit_id}")
        elif unit_id in job_proofs:
            errors.append(f"showback unit is job proof: {unit_id}")
        elif unit_id not in unit_by_id:
            errors.append(f"showback unit is undeclared: {unit_id}")
        gate_met = False
        if unit_id == "environment-hour":
            gate_met = lease_units.get(tenant_id, 0) > 0
            usage[tenant_id] = used
            billed_pool[tenant_id] = billed
            gated_pool[tenant_id] = passed
        elif unit_id == "successful-provision":
            gate_met = tenant_id in sampled_ttf
        if passed and not gate_met:
            errors.append(f"showback quality gate not met: {tenant_id}/{unit_id}")
        if passed and billed != used:
            errors.append(f"showback billed units mismatch: {tenant_id}/{unit_id}")
        if not passed and billed:
            errors.append(f"showback bills ungated usage: {tenant_id}/{unit_id}")

    for tenant_id in tenant_ids:
        used = usage.get(tenant_id, 0)
        ceil_val = ceiling.get(tenant_id)
        if ceil_val is not None and used > ceil_val:
            errors.append(f"tenant exceeds ceiling: {tenant_id}")

    starved: set[str] = set()
    for tenant_id in tenant_ids:
        others = sum(usage.get(peer, 0) for peer in tenant_ids if peer != tenant_id)
        remaining = capacity - others
        reserved = floor.get(tenant_id)
        if reserved is None or reserved < 1:
            reserved = lease_units.get(tenant_id, 0)
        if remaining < reserved:
            errors.append(f"peer floor starved: {tenant_id}")
            starved.add(tenant_id)

    burst_denied = expectations.get("denied_burst", "unlimited-burst-into-peer-quota")
    for tenant_id in tenant_ids:
        reserved = floor.get(tenant_id)
        if reserved is None or reserved < 1:
            reserved = lease_units.get(tenant_id, 0)
        bursting = usage.get(tenant_id, 0) > reserved
        peers_starved = starved.difference({tenant_id})
        if bursting and peers_starved:
            if burst_denied in denied_quota:
                errors.append(f"unlimited burst into peer quota: {tenant_id}")
            if billed_pool.get(tenant_id, 0) > 0 and gated_pool.get(tenant_id):
                errors.append(f"showback counts starved burst as useful unit: {tenant_id}")
    return errors


def completed_inputs() -> tuple:
    checkpoint = ROOT / "checkpoints" / "chapter-11"
    return (
        load(ROOT / "quota" / "tenants.yaml"),
        load(ROOT / "quota" / "units.yaml"),
        load(ROOT / "quota" / "showback.yaml"),
        load(ROOT / "tenancy" / "tenants.yaml"),
        load(ROOT / "tenancy" / "isolation.yaml"),
        load(ROOT / "tenancy" / "sharing.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(ROOT / "environments" / "leases.yaml"),
        load(ROOT / "environments" / "product.yaml"),
        load(ROOT / "devex" / "indicators.yaml"),
        load(ROOT / "devex" / "samples.yaml"),
        load(ROOT / "devex" / "non-metrics.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
