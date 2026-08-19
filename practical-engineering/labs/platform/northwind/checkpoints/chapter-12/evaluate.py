from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
INHERITED_GITOPS = ROOT / "inherited" / "devops-v1.1" / "gitops" / "interface.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    onboarding: dict,
    upgrades: dict,
    deprecations: dict,
    migrations: dict,
    tenants: dict,
    users: dict,
    systems: dict,
    paved_road: dict,
    subjects: dict,
    catalog: dict,
    versions: dict,
    leases: dict,
    quota: dict,
    exceptions: dict,
    gitops: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    tenant_ids = {item["id"] for item in tenants.get("tenants", [])}
    system_ids = {item["id"] for item in systems.get("systems", [])}
    version_keys = {
        (item["capability"], str(item["version"])) for item in versions.get("versions", [])
    }
    binding_version = {
        (item["tenant"], item["capability"]): str(item["version"])
        for item in catalog.get("bindings", [])
    }
    subject_role = {
        item.get("tenant"): item.get("granted_role")
        for item in subjects.get("subjects", [])
        if item.get("kind") == "tenant"
    }
    lease_tenants = {item["tenant"] for item in leases.get("leases", [])}
    lease_envs = {item["environment"] for item in leases.get("leases", [])}
    quota_tenants = {item["tenant"] for item in quota.get("tenants", [])}
    exception_ids = {item.get("exception") for item in exceptions.get("bindings", [])}
    as_of = expectations.get("as_of", "")
    forbidden_roles = set(expectations.get("forbidden_roles", ["cluster-admin"]))
    required_capability = expectations.get("required_capability", "tenant-storage")

    if onboarding.get("owner") not in user_ids:
        errors.append(f"onboarding has no known owner: {onboarding.get('owner')}")
    onboarded = {item["tenant"]: item for item in onboarding.get("tenants", [])}
    for tenant_id in tenant_ids:
        row = onboarded.get(tenant_id)
        if row is None:
            errors.append(f"missing onboarded tenant: {tenant_id}")
            continue
        if row.get("status") != "complete":
            errors.append(f"onboarding incomplete: {tenant_id}")
        if row.get("granted_role") in forbidden_roles:
            errors.append(f"onboarding grants cluster-admin: {tenant_id}")
        if subject_role.get(tenant_id) in forbidden_roles:
            errors.append(f"onboarding grants cluster-admin: {tenant_id}")
        if row.get("system") not in system_ids:
            errors.append(f"onboarding has no catalog system: {tenant_id}")
        if row.get("paved_road") != paved_road.get("id"):
            errors.append(f"onboarding leaves paved road: {tenant_id}")
        if row.get("environment") not in lease_envs or tenant_id not in lease_tenants:
            errors.append(f"onboarding has no lease: {tenant_id}")
        if tenant_id not in quota_tenants or not row.get("quota_floor_respected"):
            errors.append(f"onboard bursts through peer floor: {tenant_id}")

    migration_by_tenant = {
        (item["tenant"], item["capability"]): item for item in migrations.get("migrations", [])
    }
    for item in migrations.get("migrations", []):
        tenant_id = item.get("tenant")
        capability = item.get("capability")
        if tenant_id not in tenant_ids:
            errors.append(f"migration has no known tenant: {tenant_id}")
        if (capability, str(item.get("to_version"))) not in version_keys:
            target = item.get("to_version")
            errors.append(f"fleet target has no contract version: {capability}/{target}")
        if not item.get("note"):
            errors.append(f"missing migration note: {tenant_id}/{capability}")
        applied = str(item.get("applied_version"))
        to_version = str(item.get("to_version"))
        catalog_version = binding_version.get((tenant_id, capability))
        if applied == to_version and item.get("evidence") != "complete":
            errors.append(f"tenant contract broken without migration: {tenant_id}")
        if (
            catalog_version
            and applied == to_version
            and catalog_version != to_version
            and item.get("evidence") != "complete"
        ):
            errors.append(f"tenant contract broken without migration: {tenant_id}")

    for upgrade in upgrades.get("upgrades", []):
        upgrade_id = upgrade.get("id")
        capability = upgrade.get("capability")
        freeze = upgrade.get("freeze") or {}
        if upgrade.get("approved_by") not in user_ids:
            errors.append(f"upgrade has no known approver: {upgrade_id}")
        if capability != required_capability:
            errors.append(f"upgrade capability mismatch: {upgrade_id}")
        if (capability, str(upgrade.get("to_version"))) not in version_keys:
            errors.append(
                f"fleet target has no contract version: {capability}/{upgrade.get('to_version')}"
            )
        if not freeze.get("starts_at") or not freeze.get("ends_at"):
            errors.append(f"fleet upgrade skipped freeze: {upgrade_id}")
        elif as_of and not (freeze["starts_at"] <= as_of <= freeze["ends_at"]):
            if upgrade.get("result") == "in-progress":
                errors.append(f"fleet upgrade skipped freeze: {upgrade_id}")
        rollback = upgrade.get("rollback") or {}
        if not rollback.get("allowed") or rollback.get("last_known_good") != str(
            upgrade.get("from_version")
        ):
            errors.append(f"missing fleet rollback: {upgrade_id}")
        if gitops.get("controller_may_rewrite_source") is False and upgrade.get("source_rewritten"):
            errors.append(f"controller rewrites source: {upgrade_id}")
        for field in gitops.get("required_state", []):
            if field == "reviewed_intent" and upgrade.get("approved_by") not in user_ids:
                errors.append(f"missing gitops state: {upgrade_id}/{field}")
        cohorts = upgrade.get("cohorts", [])
        seen: set[str] = set()
        complete_tenants: set[str] = set()
        for cohort in cohorts:
            members = set(cohort.get("tenants", []))
            overlap = members & seen
            for tenant_id in overlap:
                errors.append(f"tenant in multiple cohorts: {tenant_id}")
            seen.update(members)
            if cohort.get("status") == "complete":
                complete_tenants.update(members)
            if len(members) >= len(tenant_ids) and cohort.get("status") == "complete":
                errors.append(f"fleet applied all tenants at once: {upgrade_id}")
        if tenant_ids and complete_tenants >= tenant_ids:
            errors.append(f"fleet applied all tenants at once: {upgrade_id}")
            if upgrade.get("result") == "complete":
                errors.append(f"missing fleet rollback: {upgrade_id}")
        for tenant_id in complete_tenants:
            migration = migration_by_tenant.get((tenant_id, capability), {})
            if migration.get("evidence") != "complete":
                errors.append(f"tenant contract broken without migration: {tenant_id}")
            if str(migration.get("applied_version")) != str(upgrade.get("to_version")):
                errors.append(f"tenant contract broken without migration: {tenant_id}")
            if rollback.get("last_known_good") == str(upgrade.get("to_version")):
                errors.append(f"missing fleet rollback: {upgrade_id}")

    for item in deprecations.get("deprecations", []):
        remaining = set(item.get("remaining_tenants") or [])
        window_end = item.get("window_ends_at") or ""
        exception_id = item.get("exception")
        closed = item.get("status") == "closed" or (window_end and as_of > window_end)
        if remaining and closed and exception_id not in exception_ids:
            for tenant_id in remaining:
                errors.append(f"deprecation window closed with remaining tenant: {tenant_id}")
        if remaining and not closed:
            for tenant_id in remaining:
                migration = migration_by_tenant.get((tenant_id, item.get("capability")), {})
                if (
                    migration.get("evidence") == "complete"
                    and str(migration.get("applied_version")) != str(item.get("version"))
                ):
                    errors.append(f"remaining tenant is not on deprecated version: {tenant_id}")
    return errors


def completed_inputs() -> tuple:
    checkpoint = ROOT / "checkpoints" / "chapter-12"
    return (
        load(ROOT / "fleet" / "onboarding.yaml"),
        load(ROOT / "fleet" / "upgrades.yaml"),
        load(ROOT / "fleet" / "deprecations.yaml"),
        load(ROOT / "fleet" / "migrations.yaml"),
        load(ROOT / "tenancy" / "tenants.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(ROOT / "catalog" / "systems.yaml"),
        load(ROOT / "paved-road" / "contract.yaml"),
        load(ROOT / "control-plane" / "subjects.yaml"),
        load(ROOT / "contracts" / "catalog.yaml"),
        load(ROOT / "contracts" / "versions.yaml"),
        load(ROOT / "environments" / "leases.yaml"),
        load(ROOT / "quota" / "tenants.yaml"),
        load(ROOT / "guardrails" / "exceptions.yaml"),
        load(INHERITED_GITOPS),
        load(checkpoint / "expectations.yaml"),
    )
