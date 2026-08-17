from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
INHERITED_RELEASE = ROOT / "inherited" / "devops-v1.1" / "release" / "interface.yaml"
INHERITED_IDENTITY = ROOT / "inherited" / "devops-v1.1" / "identity" / "interface.yaml"
INHERITED_EXCEPTIONS = ROOT / "inherited" / "devsecops-v1.0" / "exceptions"
INHERITED_CONTROLS = ROOT / "inherited" / "devsecops-v1.0" / "controls" / "interface.yaml"
INHERITED_EVIDENCE = ROOT / "inherited" / "devsecops-v1.0" / "evidence" / "interface.yaml"
COPIED_FIELDS = {
    "owner",
    "scope",
    "rationale",
    "compensating_controls",
    "compensation",
    "evidence",
    "expires_at",
    "expiry",
    "removal_path",
    "status",
}
WAIVERS = {
    "none": set(),
    "waive-artifact-digest": {"artifact-digest"},
}


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
    defaults: dict,
    scorecards: dict,
    bindings: dict,
    contract: dict,
    exits: dict,
    tenants: dict,
    catalog: dict,
    users: dict,
    inherited_exceptions: dict,
    exception_shape: dict,
    controls: dict,
    evidence: dict,
    release: dict,
    identity: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    tenant_by_id = {item["id"]: item for item in tenants.get("tenants", [])}
    catalog_ids = {item["id"] for item in catalog.get("systems", [])}
    exit_by_id = {item["id"]: item for item in exits.get("exits", [])}
    default_ids = {item["id"] for item in defaults.get("defaults", [])}
    contract_defaults = set(contract.get("defaults", []))
    exception_by_id = {
        item["id"]: item for item in inherited_exceptions.get("exceptions", [])
    }
    as_of = parse_timestamp(expectations.get("as_of"))
    required_defaults = list(expectations.get("required_defaults", []))
    remaining = set(expectations.get("required_remaining_guardrails", []))

    if defaults.get("owner") not in user_ids:
        errors.append(f"defaults have no known owner: {defaults.get('owner')}")
    if not defaults.get("exits_allowed") and exit_by_id:
        errors.append("guardrails form a golden cage")
    for default_id in required_defaults:
        if default_id not in default_ids:
            errors.append(f"missing required default: {default_id}")
        if default_id not in contract_defaults:
            errors.append(f"guardrail is not a paved-road default: {default_id}")
    if release.get("promotion_identity") == "artifact_digest":
        if "artifact-digest" not in default_ids:
            errors.append("guardrails drop inherited artifact-digest")
    if identity.get("required_claims") and "workload-identity-claims" not in default_ids:
        errors.append("guardrails drop inherited workload identity")
    if controls.get("platform_may_rebuild") is False:
        for item in defaults.get("defaults", []):
            if item.get("inherited_policy") == "rebuilt-threat-model":
                errors.append("platform rebuilds inherited control")
    for item in defaults.get("defaults", []):
        if item.get("owner") not in user_ids:
            errors.append(f"default has no known owner: {item.get('id')}")
        if item.get("id") in remaining and "exit" not in item.get("applies_to", []):
            errors.append(f"remaining guardrail does not apply on exit: {item.get('id')}")

    binding_by_system = {}
    for binding in bindings.get("bindings", []):
        exception_id = binding.get("exception")
        system_id = binding.get("system")
        tenant_id = binding.get("tenant")
        binding_by_system[system_id] = binding
        if not exception_shape.get("duplicate_lifecycle_fields_in_platform_bindings"):
            for field in COPIED_FIELDS:
                if field in binding:
                    errors.append(f"exception binding copies inherited lifecycle: {field}")
        record = exception_by_id.get(exception_id)
        if record is None:
            errors.append(f"unknown inherited exception: {exception_id}")
            continue
        expires_at = parse_timestamp(record.get("expires_at"))
        expired = as_of is not None and expires_at is not None and expires_at <= as_of
        if expired:
            errors.append(f"expired inherited exception: {exception_id}")
        else:
            waived = set(WAIVERS.get(binding.get("scorecard_effect"), set()))
            kept = set(binding.get("remaining_isolation", []))
            for guardrail in remaining - waived:
                if guardrail not in kept:
                    errors.append(
                        f"exception drops remaining isolation: {exception_id}/{guardrail}"
                    )
        if tenant_id not in tenant_by_id:
            errors.append(f"binding has no known tenant: {system_id}")
        if system_id not in catalog_ids:
            errors.append(f"binding has no known system: {system_id}")
        if binding.get("path") == "exit":
            exit_id = binding.get("exit")
            if exit_id not in exit_by_id:
                errors.append(f"binding has no known exit: {system_id}")

    scored: set[str] = set()
    for card in scorecards.get("scorecards", []):
        system_id = card.get("system")
        tenant_id = card.get("tenant")
        path = card.get("path")
        present = set(card.get("defaults_present", []))
        scored.add(system_id)
        if tenant_id not in tenant_by_id:
            errors.append(f"scorecard has no known tenant: {system_id}")
        if system_id not in catalog_ids:
            errors.append(f"scorecard has no known system: {system_id}")
        if path == "exit":
            exit_id = card.get("exit")
            exit_row = exit_by_id.get(exit_id)
            if exit_row is None:
                errors.append(f"scorecard has no known exit: {system_id}")
            elif exit_row.get("system") != system_id:
                errors.append(f"exit system mismatch: {system_id}")
        binding = binding_by_system.get(system_id)
        waived: set[str] = set()
        if binding is not None:
            record = exception_by_id.get(binding.get("exception"), {})
            expires_at = parse_timestamp(record.get("expires_at"))
            expired = as_of is not None and expires_at is not None and expires_at <= as_of
            if not expired:
                waived = set(WAIVERS.get(binding.get("scorecard_effect"), set()))
        for default_id in required_defaults:
            if default_id in waived:
                continue
            if default_id not in present:
                errors.append(f"guardrail missing: {system_id}/{default_id}")
        if evidence.get("independent_producer_required") and card.get("reported_status") == "green":
            errors.append(f"scorecard reports green without conformance: {system_id}")

    for system_id in expectations.get("required_systems", []):
        if system_id not in scored:
            errors.append(f"missing required scorecard: {system_id}")

    return errors


def completed_inputs() -> tuple:
    checkpoint = ROOT / "checkpoints" / "chapter-09"
    return (
        load(ROOT / "guardrails" / "defaults.yaml"),
        load(ROOT / "guardrails" / "scorecards.yaml"),
        load(ROOT / "guardrails" / "exceptions.yaml"),
        load(ROOT / "paved-road" / "contract.yaml"),
        load(ROOT / "paved-road" / "exits.yaml"),
        load(ROOT / "tenancy" / "tenants.yaml"),
        load(ROOT / "catalog" / "systems.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(INHERITED_EXCEPTIONS / "records.yaml"),
        load(INHERITED_EXCEPTIONS / "interface.yaml"),
        load(INHERITED_CONTROLS),
        load(INHERITED_EVIDENCE),
        load(INHERITED_RELEASE),
        load(INHERITED_IDENTITY),
        load(checkpoint / "expectations.yaml"),
    )
