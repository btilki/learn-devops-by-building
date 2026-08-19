from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
INHERITED_GITOPS = ROOT / "inherited" / "devops-v1.1" / "gitops" / "interface.yaml"
INHERITED_IDENTITY = ROOT / "inherited" / "devops-v1.1" / "identity" / "interface.yaml"
INHERITED_RELEASE = ROOT / "inherited" / "devops-v1.1" / "release" / "interface.yaml"
INHERITED_AUTH = ROOT / "inherited" / "devsecops-v1.0" / "authorization" / "interface.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    product: dict,
    subjects: dict,
    admission: dict,
    reconciliation: dict,
    tenants: dict,
    isolation: dict,
    sharing: dict,
    roles: dict,
    users: dict,
    contract_versions: dict,
    env_product: dict,
    gitops: dict,
    identity: dict,
    release: dict,
    authorization: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    tenant_by_id = {item["id"]: item for item in tenants.get("tenants", [])}
    role_by_id = {item["id"]: item for item in roles.get("roles", [])}
    shared_by_id = {item["id"]: item for item in sharing.get("shared", [])}
    denied_sharing = {item["id"] for item in sharing.get("denied", [])}
    dimension_by_id = {item["id"]: item for item in isolation.get("dimensions", [])}
    denied_change = set(
        dimension_by_id.get("change-authority", {}).get("denied_inheritance", [])
    )
    version_keys = {
        (item["capability"], str(item["version"]))
        for item in contract_versions.get("versions", [])
    }
    subject_by_id = {item["id"]: item for item in subjects.get("subjects", [])}
    plane_ids = {item["id"] for item in subjects.get("subjects", []) if item.get("kind") == "plane"}
    forbidden_roles = (
        set(product.get("forbidden_roles", []))
        | set(expectations.get("forbidden_roles", []))
        | denied_sharing
    )
    required_claims = identity.get("required_claims", [])
    required_state = gitops.get("required_state", [])
    auth_fields = authorization.get("required_fields", [])

    if product.get("owner") not in user_ids:
        errors.append(f"product has no known owner: {product.get('owner')}")
    if product.get("plane") != expectations.get("required_plane"):
        errors.append("plane does not use kubernetes-control-plane")
    if product.get("plane") != env_product.get("shared_plane"):
        errors.append("plane does not match environment product")
    plane_share = shared_by_id.get(product.get("plane"), {})
    if plane_share.get("mode") != expectations.get("required_sharing_mode"):
        errors.append("plane is not shared-control-plane")
    if product.get("sharing_mode") != expectations.get("required_sharing_mode"):
        errors.append("plane is not shared-control-plane")
    for job in expectations.get("required_jobs", []):
        if job not in product.get("jobs", []):
            errors.append(f"plane product missing job: {job}")
    if identity.get("credential_model") == "short-lived-federated":
        if product.get("credential_model") != "short-lived-federated":
            errors.append("control plane drops inherited federated identity")
        unsupported = identity.get("unsupported_provider_model")
        if product.get("credential_model") == unsupported:
            errors.append("control plane uses unsupported credential model")
    if gitops.get("controller_may_rewrite_source") is False:
        if product.get("controller_may_rewrite_source") is not False:
            errors.append("controller rewrites source")

    plane_subject_id = expectations.get("plane_subject")
    if plane_subject_id not in plane_ids:
        errors.append(f"missing plane subject: {plane_subject_id}")

    for subject in subjects.get("subjects", []):
        subject_id = subject.get("id")
        kind = subject.get("kind")
        granted = subject.get("granted_role")
        role = role_by_id.get(subject.get("role"), {})
        tenant_id = subject.get("tenant")
        credentials = subject.get("credentials", {})
        if granted in role.get("never_inherit", []):
            errors.append(f"subject inherits prohibited role: {subject_id}/{granted}")
        if granted in forbidden_roles:
            if kind == "plane":
                errors.append(f"shared plane admin: {subject_id}/{granted}")
            else:
                errors.append(f"tenant subject inherits cluster-admin: {subject_id}")
        if kind == "tenant":
            if tenant_id not in tenant_by_id:
                errors.append(f"subject has no known tenant: {subject_id}")
            if granted in denied_change:
                errors.append(f"tenant subject inherits cluster-admin: {subject_id}")
        elif tenant_id:
            errors.append(f"plane subject is tenant-scoped: {subject_id}")
        if subject.get("may_approve_plane_change"):
            errors.append(f"plane self-approval: {subject_id}")
        for claim in required_claims:
            if not credentials.get(claim):
                errors.append(f"subject missing identity claim: {subject_id}/{claim}")
        if credentials.get("audience") != product.get("plane"):
            errors.append(f"subject audience is not the shared plane: {subject_id}")

    admitted = {
        (item["capability"], str(item["version"]))
        for item in admission.get("admitted_versions", [])
    }
    for key in admitted:
        if key not in version_keys:
            capability, version = key
            errors.append(f"admitted unknown contract version: {capability}/{version}")

    for decision in admission.get("decisions", []):
        for field in auth_fields:
            if not decision.get(field):
                action = decision.get("action")
                errors.append(f"authorization missing field: {action}/{field}")
        if (
            authorization.get("self_approval_forbidden")
            and decision.get("action") == "approve-plane-upgrade"
            and decision.get("subject") in plane_ids
            and decision.get("result") == "allow"
        ):
            errors.append(f"plane self-approval: {decision.get('context')}")

    bound_env: set[str] = set()
    for result in reconciliation.get("results", []):
        result_id = result.get("id")
        tenant_id = result.get("tenant")
        env_id = result.get("environment")
        tenant = tenant_by_id.get(tenant_id, {})
        actor = subject_by_id.get(result.get("actor"), {})
        bound_env.add(env_id)
        if tenant_id not in tenant_by_id:
            errors.append(f"reconcile has no known tenant: {env_id}")
        elif env_id not in tenant.get("environments", []):
            errors.append(f"reconcile environment not in tenant inventory: {env_id}")
        key = (result.get("capability"), str(result.get("version")))
        if key not in admitted:
            capability, version = key
            errors.append(f"reconcile not admitted: {capability}/{version}")
        if result.get("admission") != "admitted":
            errors.append(f"reconcile not admitted: {result_id}")
        if gitops.get("controller_may_rewrite_source") is False:
            if result.get("source_rewritten") or result.get("mode") == "rewrite":
                errors.append(f"controller rewrites source: {result_id}")
        for field in required_state:
            if field == "reconciliation_result":
                present = result.get("reconciliation_result")
            elif field == "immutable_artifact":
                present = result.get("immutable_artifact")
            else:
                present = result.get(field)
            if not present:
                errors.append(f"missing gitops state: {result_id}/{field}")
        if (
            release.get("promotion_identity") == "artifact_digest"
            and result.get("immutable_artifact") == "latest"
        ):
            errors.append(f"reconcile drops inherited artifact-digest: {result_id}")
        mutated = set(result.get("mutated_tenants", []))
        extras = mutated - {tenant_id}
        for extra in extras:
            errors.append(f"cross-tenant reconcile: {env_id}/{extra}")
        if actor.get("kind") == "tenant" and actor.get("tenant") != tenant_id:
            errors.append(f"cross-tenant reconcile: {env_id}/{actor.get('tenant')}")

    for env_id in expectations.get("required_environments", []):
        if env_id not in bound_env:
            errors.append(f"missing required reconcile: {env_id}")

    for upgrade in reconciliation.get("upgrades", []):
        upgrade_id = upgrade.get("id")
        if upgrade.get("approved_by") in plane_ids:
            errors.append(f"plane self-approval: {upgrade_id}")
        if upgrade.get("approved_by") not in user_ids:
            errors.append(f"upgrade has no known approver: {upgrade_id}")
        if upgrade.get("result") == "failed":
            from_version = upgrade.get("from_version")
            if (
                upgrade.get("current_version") != from_version
                or upgrade.get("last_known_good") != from_version
            ):
                errors.append(f"missing last known good: {upgrade_id}")

    return errors


def completed_inputs() -> tuple:
    checkpoint = ROOT / "checkpoints" / "chapter-08"
    return (
        load(ROOT / "control-plane" / "product.yaml"),
        load(ROOT / "control-plane" / "subjects.yaml"),
        load(ROOT / "control-plane" / "admission.yaml"),
        load(ROOT / "control-plane" / "reconciliation.yaml"),
        load(ROOT / "tenancy" / "tenants.yaml"),
        load(ROOT / "tenancy" / "isolation.yaml"),
        load(ROOT / "tenancy" / "sharing.yaml"),
        load(ROOT / "tenancy" / "roles.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(ROOT / "contracts" / "versions.yaml"),
        load(ROOT / "environments" / "product.yaml"),
        load(INHERITED_GITOPS),
        load(INHERITED_IDENTITY),
        load(INHERITED_RELEASE),
        load(INHERITED_AUTH),
        load(checkpoint / "expectations.yaml"),
    )
