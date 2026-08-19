from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_BLAST_RADIUS = {"the-cluster", "shared-cluster", "all-tenants", "unbounded"}
PROHIBITED_TENANT_ROLES = {"cluster-admin"}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    tenants: dict,
    isolation: dict,
    roles: dict,
    sharing: dict,
    users: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    tenant_by_id = {item["id"]: item for item in tenants.get("tenants", [])}
    dimension_by_id = {item["id"]: item for item in isolation.get("dimensions", [])}
    role_by_id = {item["id"]: item for item in roles.get("roles", [])}
    shared_by_id = {item["id"]: item for item in sharing.get("shared", [])}
    denied_ids = {item["id"] for item in sharing.get("denied", [])}
    prohibited = set(expectations.get("prohibited_tenant_roles", [])) | PROHIBITED_TENANT_ROLES

    for tenant_id in expectations.get("required_tenants", []):
        tenant = tenant_by_id.get(tenant_id)
        if tenant is None:
            errors.append(f"missing required tenant: {tenant_id}")
            continue
        if tenant.get("owner") not in user_ids:
            errors.append(f"tenant has no known owner: {tenant_id}")
        if not tenant.get("blast_radius"):
            errors.append(f"tenant has no blast-radius statement: {tenant_id}")
        elif tenant.get("blast_radius") in FORBIDDEN_BLAST_RADIUS:
            errors.append(f"tenant has unbounded blast radius: {tenant_id}")
        for dimension in expectations.get("required_dimensions", []):
            if dimension not in tenant.get("isolation_dimensions", []):
                errors.append(f"tenant missing isolation dimension: {tenant_id}/{dimension}")
        for role in expectations.get("prohibited_tenant_roles", []):
            if role not in tenant.get("prohibited_inherited_roles", []):
                errors.append(f"missing prohibited inherited role: {tenant_id}/{role}")

    for dimension_id in expectations.get("required_dimensions", []):
        dimension = dimension_by_id.get(dimension_id)
        if dimension is None:
            errors.append(f"missing isolation dimension: {dimension_id}")
            continue
        if not dimension.get("blast_radius"):
            errors.append(f"dimension has no blast-radius statement: {dimension_id}")
        allowed = dimension.get("allowed_sharing", "")
        if allowed not in {"none", ""} and allowed not in shared_by_id:
            errors.append(f"dimension shares unknown surface: {dimension_id}/{allowed}")

    change_authority = dimension_by_id.get("change-authority")
    if change_authority is not None and "cluster-admin" not in change_authority.get(
        "denied_inheritance", []
    ):
        errors.append("change-authority does not deny cluster-admin")

    for role_id, role in role_by_id.items():
        if role.get("scope") != "tenant":
            continue
        never = set(role.get("never_inherit", []))
        for prohibited_role in expectations.get("prohibited_tenant_roles", []):
            if prohibited_role not in never:
                errors.append(f"role may inherit prohibited authority: {role_id}/{prohibited_role}")

    for binding in roles.get("bindings", []):
        principal = binding.get("principal")
        tenant_id = binding.get("tenant")
        role_id = binding.get("role")
        if principal not in user_ids:
            errors.append(f"binding has no known principal: {principal}")
        if tenant_id and tenant_id not in tenant_by_id:
            errors.append(f"binding has no known tenant: {tenant_id}")
        if role_id not in role_by_id and role_id not in prohibited:
            errors.append(f"binding has no known role: {role_id}")
        if tenant_id and role_id in prohibited:
            errors.append(f"tenant inherits prohibited role: {tenant_id}/{role_id}")
        elif tenant_id:
            tenant_prohibited = set(
                tenant_by_id.get(tenant_id, {}).get("prohibited_inherited_roles", [])
            )
            if role_id in tenant_prohibited:
                errors.append(f"tenant inherits prohibited role: {tenant_id}/{role_id}")

    for shared_id in expectations.get("required_sharing", []):
        if shared_id not in shared_by_id:
            errors.append(f"missing required sharing: {shared_id}")
    plane = shared_by_id.get("kubernetes-control-plane")
    if plane is not None and plane.get("mode") != "shared-control-plane":
        errors.append("control plane is not isolated as a shared product")
    if "cluster-admin" in shared_by_id:
        errors.append("sharing permits prohibited role: cluster-admin")
    for denied_id in expectations.get("required_denied", []):
        if denied_id not in denied_ids:
            errors.append(f"sharing does not deny: {denied_id}")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-03"
    return (
        load(ROOT / "tenancy" / "tenants.yaml"),
        load(ROOT / "tenancy" / "isolation.yaml"),
        load(ROOT / "tenancy" / "roles.yaml"),
        load(ROOT / "tenancy" / "sharing.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
