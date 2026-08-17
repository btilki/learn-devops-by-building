from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
INHERITED_RELEASE = ROOT / "inherited" / "devops-v1.1" / "release" / "interface.yaml"
INHERITED_IDENTITY = ROOT / "inherited" / "devops-v1.1" / "identity" / "interface.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    catalog: dict,
    versions: dict,
    compatibility: dict,
    tenants: dict,
    isolation: dict,
    users: dict,
    release: dict,
    identity: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    tenant_by_id = {item["id"]: item for item in tenants.get("tenants", [])}
    capability_ids = {item["id"] for item in catalog.get("capabilities", [])}
    version_by_key = {
        (item["capability"], str(item["version"])): item for item in versions.get("versions", [])
    }
    capability_versions: dict[str, set[str]] = {}
    for item in versions.get("versions", []):
        capability_versions.setdefault(item["capability"], set()).add(str(item["version"]))
    breaking = set(compatibility.get("breaking", []))
    required_breaking = set(expectations.get("required_breaking", []))
    dimension_by_id = {item["id"]: item for item in isolation.get("dimensions", [])}
    denied_network = set(dimension_by_id.get("network", {}).get("denied_inheritance", []))

    if required_breaking and not required_breaking.issubset(breaking):
        errors.append("missing compatibility policy")

    for capability_id in expectations.get("required_capabilities", []):
        if capability_id not in capability_ids:
            errors.append(f"missing required capability: {capability_id}")

    for capability in catalog.get("capabilities", []):
        if capability.get("owner") not in user_ids:
            errors.append(f"capability has no known owner: {capability.get('id')}")

    identity_version = version_by_key.get(("workload-identity", "1.0"))
    if identity.get("credential_model") == "short-lived-federated":
        model = (identity_version or {}).get("credential_model")
        if model != "short-lived-federated":
            errors.append("identity contract drops inherited federated identity")

    promotion = version_by_key.get(("artifact-promotion", "1.0"), {})
    if release.get("promotion_identity") == "artifact_digest":
        params = set(promotion.get("tenant_parameters", []))
        hidden = set(promotion.get("hidden_module", []))
        if "artifact-digest" not in params:
            errors.append("artifact contract drops inherited artifact-digest")
        if "artifact-digest" in hidden:
            errors.append("artifact-digest is hidden module internals")

    for version in versions.get("versions", []):
        params = set(version.get("tenant_parameters", []))
        hidden = set(version.get("hidden_module", []))
        overlap = params & hidden
        for field in overlap:
            capability = version.get("capability")
            errors.append(f"hidden module exposed as tenant API: {capability}/{field}")

    for change in compatibility.get("changes", []):
        kind = change.get("kind")
        capability = change.get("capability")
        version = str(change.get("version"))
        versions_for_cap = capability_versions.get(capability, set())
        if kind not in breaking:
            continue
        if not change.get("migration_note"):
            errors.append(f"missing migration note: {capability}/{version}")
        in_place = len(versions_for_cap) < 2 or version == min(versions_for_cap)
        if in_place:
            errors.append(f"breaking change without version: {capability}/{version}")

    required_env = set(expectations.get("required_environments", []))
    bound_env: set[str] = set()
    for binding in catalog.get("bindings", []):
        tenant_id = binding.get("tenant")
        env_id = binding.get("environment")
        capability = binding.get("capability")
        version = str(binding.get("version"))
        tenant = tenant_by_id.get(tenant_id, {})
        bound_env.add(env_id)
        if tenant_id not in tenant_by_id:
            errors.append(f"binding has no known tenant: {env_id}/{capability}")
        elif env_id not in tenant.get("environments", []):
            errors.append(f"binding environment not in tenant inventory: {env_id}")
        if capability not in capability_ids:
            errors.append(f"binding has no known capability: {capability}")
        record = version_by_key.get((capability, version))
        if record is None:
            errors.append(f"binding has no contract version: {capability}/{version}")
            continue
        params = set(record.get("tenant_parameters", []))
        hidden = set(record.get("hidden_module", []))
        for field, value in binding.get("parameters", {}).items():
            if field in hidden:
                errors.append(f"hidden module used as tenant API: {env_id}/{field}")
            elif field not in params:
                errors.append(f"tenant parameter missing: {env_id}/{capability}/{field}")
            if capability == "tenant-network" and str(value) in denied_network:
                errors.append(f"contract violates isolation: {env_id}/{value}")

    for env_id in required_env:
        if env_id not in bound_env:
            errors.append(f"missing required binding: {env_id}")

    return errors


def completed_inputs() -> tuple:
    checkpoint = ROOT / "checkpoints" / "chapter-07"
    return (
        load(ROOT / "contracts" / "catalog.yaml"),
        load(ROOT / "contracts" / "versions.yaml"),
        load(ROOT / "contracts" / "compatibility.yaml"),
        load(ROOT / "tenancy" / "tenants.yaml"),
        load(ROOT / "tenancy" / "isolation.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(INHERITED_RELEASE),
        load(INHERITED_IDENTITY),
        load(checkpoint / "expectations.yaml"),
    )
