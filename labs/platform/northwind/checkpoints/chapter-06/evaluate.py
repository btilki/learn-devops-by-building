from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
INHERITED_IDENTITY = ROOT / "inherited" / "devops-v1.1" / "identity" / "interface.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def evaluate(
    product: dict,
    requests: dict,
    leases: dict,
    tenants: dict,
    isolation_model: dict,
    users: dict,
    jobs: dict,
    identity: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    job_ids = {item["id"] for item in jobs.get("jobs", [])}
    tenant_by_id = {item["id"]: item for item in tenants.get("tenants", [])}
    tenant_owner = {item["id"]: item.get("owner") for item in tenants.get("tenants", [])}
    request_by_id = {item["id"]: item for item in requests.get("requests", [])}
    lease_by_env = {item["environment"]: item for item in leases.get("leases", [])}
    dimension_by_id = {item["id"]: item for item in isolation_model.get("dimensions", [])}
    denied_network = set(dimension_by_id.get("network", {}).get("denied_inheritance", []))
    denied_secrets = set(dimension_by_id.get("secrets", {}).get("denied_inheritance", []))
    as_of = parse_timestamp(expectations.get("as_of"))
    forbidden_roles = set(product.get("forbidden_roles", [])) | set(
        expectations.get("forbidden_roles", [])
    )
    required_claims = identity.get("required_claims", [])

    if product.get("job") not in job_ids:
        errors.append(f"product has no known job: {product.get('job')}")
    if product.get("job") != expectations.get("required_job"):
        errors.append(f"product job is not {expectations.get('required_job')}")
    if product.get("owner") not in user_ids:
        errors.append(f"product has no known owner: {product.get('owner')}")
    if product.get("shared_plane") != expectations.get("required_shared_plane"):
        errors.append("environment product does not use kubernetes-control-plane")
    if product.get("quota_pool") != expectations.get("required_quota_pool"):
        errors.append("environment product does not use cluster-capacity-pool")
    if identity.get("credential_model") == "short-lived-federated":
        if product.get("credential_model") != "short-lived-federated":
            errors.append("environment product drops inherited federated identity")
        unsupported = identity.get("unsupported_provider_model")
        if product.get("credential_model") == unsupported:
            errors.append("environment product uses unsupported credential model")

    for env_id in expectations.get("required_environments", []):
        if env_id not in lease_by_env:
            errors.append(f"missing required lease: {env_id}")

    for lease in leases.get("leases", []):
        env_id = lease.get("environment")
        tenant_id = lease.get("tenant")
        tenant = tenant_by_id.get(tenant_id, {})
        request = request_by_id.get(lease.get("request"))
        if tenant_id not in tenant_by_id:
            errors.append(f"lease has no known tenant: {env_id}")
        elif env_id not in tenant.get("environments", []):
            errors.append(f"environment not in tenant inventory: {env_id}")
        if request is None:
            errors.append(f"lease has no request: {env_id}")
        else:
            if request.get("tenant") != tenant_id:
                errors.append(f"request tenant mismatch: {env_id}")
            if request.get("environment") != env_id:
                errors.append(f"request environment mismatch: {env_id}")
            if request.get("requester") not in user_ids:
                errors.append(f"request has no known requester: {env_id}")
            if request.get("requester") != tenant.get("owner"):
                errors.append(f"requester is not tenant owner: {env_id}")

        role = lease.get("granted_role")
        if role in forbidden_roles:
            errors.append(f"shared env admin: {env_id}/{role}")

        mutated_by = lease.get("mutated_by")
        if mutated_by and mutated_by != tenant_owner.get(tenant_id):
            errors.append(f"cross-tenant mutation: {env_id}/{mutated_by}")

        expires_at = parse_timestamp(lease.get("expires_at"))
        if expires_at is None:
            errors.append(f"missing lease expiry: {env_id}")
        elif as_of is not None and expires_at <= as_of and not lease.get("reclaimed"):
            errors.append(f"unreclaimed expired lease: {env_id}")

        quota = lease.get("quota", {})
        if quota.get("pool") != product.get("quota_pool"):
            errors.append(f"lease quota pool mismatch: {env_id}")
        units = quota.get("units")
        if not isinstance(units, int) or units < 1:
            errors.append(f"missing quota bound: {env_id}")

        credentials = lease.get("credentials", {})
        for claim in required_claims:
            if not credentials.get(claim):
                errors.append(f"lease missing identity claim: {env_id}/{claim}")
        subject = str(credentials.get("subject", ""))
        if tenant_id and tenant_id not in subject and env_id not in subject:
            errors.append(f"credential subject is not tenant-scoped: {env_id}")
        if credentials.get("audience") != product.get("shared_plane"):
            errors.append(f"credential audience is not the shared plane: {env_id}")
        cred_expiry = parse_timestamp(credentials.get("expiry"))
        if expires_at and cred_expiry and cred_expiry > expires_at:
            errors.append(f"credential outlives lease: {env_id}")

        isolation = lease.get("isolation", {})
        if isolation.get("network") in denied_network:
            errors.append(f"cross-tenant network: {env_id}")
        if isolation.get("secrets") in denied_secrets:
            errors.append(f"cross-tenant secret: {env_id}")

    return errors


def completed_inputs() -> tuple:
    checkpoint = ROOT / "checkpoints" / "chapter-06"
    return (
        load(ROOT / "environments" / "product.yaml"),
        load(ROOT / "environments" / "requests.yaml"),
        load(ROOT / "environments" / "leases.yaml"),
        load(ROOT / "tenancy" / "tenants.yaml"),
        load(ROOT / "tenancy" / "isolation.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(ROOT / "product" / "jobs.yaml"),
        load(INHERITED_IDENTITY),
        load(checkpoint / "expectations.yaml"),
    )
