from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
INHERITED_RESTORE = ROOT / "inherited" / "devops-v1.1" / "recovery" / "interface.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _denied(isolation: dict, dimension_id: str) -> set[str]:
    dimension = next(
        (item for item in isolation.get("dimensions", []) if item.get("id") == dimension_id),
        {},
    )
    return set(dimension.get("denied_inheritance", []))


def evaluate(
    plane_evidence: dict,
    isolation_plan: dict,
    restore_trace: dict,
    verification: dict,
    users: dict,
    tenants: dict,
    isolation: dict,
    leases: dict,
    subjects: dict,
    plane_product: dict,
    reconciliation: dict,
    quota: dict,
    upgrades: dict,
    migrations: dict,
    changes: dict,
    incidents: dict,
    restore_contract: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    tenant_ids = {item["id"] for item in tenants.get("tenants", [])}
    plane_ids = {
        item["id"] for item in subjects.get("subjects", []) if item.get("kind") == "plane"
    }
    forbidden_roles = set(plane_product.get("forbidden_roles", [])) | set(
        expectations.get("forbidden_roles", [])
    )
    denied_change = _denied(isolation, "change-authority")
    denied_quota = _denied(isolation, "quota")
    required_roots = set(restore_contract.get("required_roots", []))
    traffic_required = set(restore_contract.get("traffic_return_requires", []))
    forbidden_indicators = set(expectations.get("forbidden_indicators", []))
    required_jobs = set(plane_product.get("jobs", [])) | set(
        expectations.get("required_jobs", [])
    )
    required_limits = set(expectations.get("required_limitations", []))
    required_plane = expectations.get("required_plane")
    required_capability = expectations.get("required_capability", "tenant-storage")
    explicit = expectations.get("required_decision_source", "explicit-tenant-decision")
    plane_lkg = next(
        (
            str(item.get("last_known_good"))
            for item in reconciliation.get("upgrades", [])
            if item.get("result") == "failed"
        ),
        None,
    )
    reconcile_version = {
        (item["tenant"], item["capability"]): str(item["version"])
        for item in reconciliation.get("results", [])
    }
    migration_version = {
        (item["tenant"], item["capability"]): str(item["applied_version"])
        for item in migrations.get("migrations", [])
    }
    lease_units: dict[str, int] = {}
    for lease in leases.get("leases", []):
        tenant_id = lease["tenant"]
        lease_units[tenant_id] = lease_units.get(tenant_id, 0) + int(
            lease.get("quota", {}).get("units") or 0
        )
    snapshot_by_id = {item["id"]: item for item in plane_evidence.get("snapshots", [])}
    isolation_by_tenant = {item["tenant"]: item for item in isolation_plan.get("tenants", [])}
    decision_by_tenant = {
        item["tenant"]: item for item in verification.get("tenant_decisions", [])
    }
    traffic_by_tenant = {
        item["tenant"]: set(item.get("evidence") or [])
        for item in verification.get("traffic_return", [])
    }
    unofficial_versions = {
        str(item.get("current_version"))
        for item in changes.get("changes", [])
        if item.get("unofficial")
    }
    tenant_tickets = {
        item["id"]
        for item in incidents.get("incidents", [])
        if item.get("class") == "tenant-application"
    }
    quota_floors = {item["tenant"]: int(item["floor"]) for item in quota.get("tenants", [])}
    capacity = int(quota.get("capacity") or 0)

    if plane_evidence.get("owner") not in user_ids:
        errors.append(f"evidence has no known owner: {plane_evidence.get('owner')}")
    if plane_evidence.get("plane") != plane_product.get("plane"):
        errors.append("recovery plane does not match control-plane product")
    if plane_evidence.get("plane") != required_plane:
        errors.append("recovery plane is not kubernetes-control-plane")
    if plane_lkg and str(plane_evidence.get("last_known_good")) != plane_lkg:
        errors.append("plane evidence last known good is not chapter 8 retention")

    for tenant_id in tenant_ids:
        row = isolation_by_tenant.get(tenant_id)
        if row is None:
            errors.append(f"missing isolation tenant: {tenant_id}")
            continue
        if row.get("source") != explicit:
            if row.get("decision") == "freeze":
                errors.append(f"accidental tenant freeze: {tenant_id}")
            else:
                errors.append(f"tenant decision is not explicit: {tenant_id}")
        if row.get("replayed_from") != tenant_id:
            errors.append(f"cross-tenant replay: {tenant_id}/{row.get('replayed_from')}")
        extras = set(row.get("mutated_tenants") or []) - {tenant_id}
        for extra in extras:
            errors.append(f"cross-tenant replay: {tenant_id}/{extra}")
        granted = row.get("granted_role")
        if granted in forbidden_roles or granted in denied_change:
            errors.append(f"restore grants cluster-admin: {tenant_id}")
        key = (tenant_id, row.get("restored_capability") or required_capability)
        expected = reconcile_version.get(key) or migration_version.get(key)
        if expected and str(row.get("restored_version")) != expected:
            errors.append(f"restore version mismatch: {tenant_id}")
        units = int(row.get("quota_units") or 0)
        if units != lease_units.get(tenant_id, 0):
            errors.append(f"restore quota ignores lease: {tenant_id}")
        peer_floors = [quota_floors[peer] for peer in tenant_ids if peer != tenant_id]
        remaining = capacity - units
        if (
            "unlimited-burst-into-peer-quota" in denied_quota
            and peer_floors
            and remaining < min(peer_floors)
        ):
            errors.append(f"unlimited-burst-into-peer-quota: {tenant_id}")

    for restore in restore_trace.get("restores", []):
        restore_id = restore.get("id")
        snapshot = snapshot_by_id.get(restore.get("snapshot"), {})
        if restore.get("approved_by") not in user_ids:
            errors.append(f"restore has no known approver: {restore_id}")
        if restore.get("approved_by") in plane_ids or restore.get("subject") in plane_ids:
            if restore.get("result") == "allow":
                errors.append(f"plane self-approval: {restore_id}")
        granted = restore.get("granted_role")
        if restore.get("unofficial") or granted in forbidden_roles:
            errors.append(f"unofficial plane-admin restore: {restore_id}")
        if restore.get("resource") != plane_product.get("plane"):
            errors.append(f"restore plane does not match control-plane product: {restore_id}")
        if not snapshot:
            errors.append(f"restore has no known snapshot: {restore_id}")
        allowed = restore.get("result") == "allow"
        if allowed and (restore.get("mixed_backup") or snapshot.get("mixed_tenants")):
            errors.append(f"mixed backup restore: {restore_id}")
        if allowed and snapshot.get("corrupt"):
            errors.append(f"corrupt backup restore: {restore_id}")
        if allowed and snapshot.get("newest"):
            errors.append(f"newest snapshot is not last known good: {restore_id}")
        if allowed and snapshot and not snapshot.get("independently_verified"):
            errors.append(f"unverified plane evidence: {restore_id}")
        if plane_lkg and (
            str(restore.get("last_known_good")) != plane_lkg
            or str(restore.get("restored_version")) != plane_lkg
        ):
            errors.append(f"missing last known good: {restore_id}")
        if required_roots - set(restore.get("roots") or []):
            errors.append(f"restore missing required root: {restore_id}")
        if (
            plane_product.get("controller_may_rewrite_source") is False
            and restore.get("source_rewritten")
        ):
            errors.append(f"controller rewrites source: {restore_id}")
        if restore.get("ticket") in tenant_tickets:
            errors.append(f"restore closes tenant incident: {restore_id}")
        if allowed and str(restore.get("restored_version")) in unofficial_versions:
            errors.append(f"restore uses unofficial patch: {restore_id}")

    if verification.get("plane") != plane_product.get("plane"):
        errors.append("verification plane does not match control-plane product")
    if verification.get("status") in {"recovered", "healthy", "green"}:
        errors.append("verification reports recovered")
    jobs = set(verification.get("platform_jobs") or [])
    for job_id in required_jobs:
        if job_id not in jobs:
            errors.append(f"verification missing platform job: {job_id}")
    if not required_limits.issubset(set(verification.get("limitations") or [])):
        errors.append("recovery claims regional-loss")
    for indicator_id in verification.get("recovered_indicators") or []:
        if indicator_id in forbidden_indicators:
            errors.append(f"platform recovered uses tenant workload: {indicator_id}")
    allowed_restore = next(
        (
            item
            for item in restore_trace.get("restores", [])
            if item.get("result") == "allow"
        ),
        {},
    )
    if allowed_restore:
        if verification.get("restored_snapshot") != allowed_restore.get("snapshot"):
            errors.append("verification snapshot does not match restore")
        if str(verification.get("restored_version")) != str(
            allowed_restore.get("restored_version")
        ):
            errors.append("verification version does not match restore")
    for tenant_id in tenant_ids:
        row = isolation_by_tenant.get(tenant_id, {})
        declared = decision_by_tenant.get(tenant_id)
        if declared is None:
            errors.append(f"verification missing tenant decision: {tenant_id}")
            continue
        if declared.get("decision") != row.get("decision"):
            errors.append(f"verification decision mismatch: {tenant_id}")
        if declared.get("source") != row.get("source"):
            errors.append(f"verification decision mismatch: {tenant_id}")
        evidence = traffic_by_tenant.get(tenant_id, set())
        if evidence & forbidden_indicators:
            indicator_id = sorted(evidence & forbidden_indicators)[0]
            errors.append(f"platform recovered uses tenant workload: {indicator_id}")
        if row.get("decision") == "continue" and traffic_required - evidence:
            errors.append(f"traffic returned without required evidence: {tenant_id}")
        if row.get("decision") == "freeze" and evidence:
            errors.append(f"frozen tenant returned traffic: {tenant_id}")
    return errors


def completed_inputs() -> tuple:
    checkpoint = ROOT / "checkpoints" / "chapter-14"
    return (
        load(ROOT / "recovery" / "plane-evidence.yaml"),
        load(ROOT / "recovery" / "isolation.yaml"),
        load(ROOT / "recovery" / "restore-trace.yaml"),
        load(ROOT / "recovery" / "verification.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(ROOT / "tenancy" / "tenants.yaml"),
        load(ROOT / "tenancy" / "isolation.yaml"),
        load(ROOT / "environments" / "leases.yaml"),
        load(ROOT / "control-plane" / "subjects.yaml"),
        load(ROOT / "control-plane" / "product.yaml"),
        load(ROOT / "control-plane" / "reconciliation.yaml"),
        load(ROOT / "quota" / "tenants.yaml"),
        load(ROOT / "fleet" / "upgrades.yaml"),
        load(ROOT / "fleet" / "migrations.yaml"),
        load(ROOT / "support" / "changes.yaml"),
        load(ROOT / "support" / "incidents.yaml"),
        load(INHERITED_RESTORE),
        load(checkpoint / "expectations.yaml"),
    )
