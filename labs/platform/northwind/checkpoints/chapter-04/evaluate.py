from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
GREEN_CLAIMS = {"green", "complete", "fresh", "ok"}


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
    systems: dict,
    ownership: dict,
    dependencies: dict,
    tenants: dict,
    users: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    tenant_by_id = {item["id"]: item for item in tenants.get("tenants", [])}
    system_by_id = {item["id"]: item for item in systems.get("systems", [])}
    ownership_by_system = {item["system"]: item for item in ownership.get("ownership", [])}
    dependencies_by_system = {
        item["system"]: item for item in dependencies.get("dependencies", [])
    }
    stale_before = parse_timestamp(expectations.get("stale_before"))

    for system_id in expectations.get("required_systems", []):
        if system_id not in system_by_id:
            errors.append(f"missing required system: {system_id}")

    for system_id, system in system_by_id.items():
        owner_entry = ownership_by_system.get(system_id)
        dependency_entry = dependencies_by_system.get(system_id)
        kind = system.get("kind")
        tenant_id = system.get("tenant")

        if owner_entry is None:
            errors.append(f"system has no ownership: {system_id}")
            continue
        if not owner_entry.get("escalation"):
            errors.append(f"system has no escalation contact: {system_id}")

        owner = owner_entry.get("owner")
        living = owner in user_ids
        if not living:
            errors.append(f"owner is not living: {system_id}/{owner}")

        reviewed_at = parse_timestamp(owner_entry.get("last_reviewed_at"))
        stale = reviewed_at is None or (
            stale_before is not None and reviewed_at < stale_before
        )
        if reviewed_at is None:
            errors.append(f"ownership has no review timestamp: {system_id}")
        elif stale:
            errors.append(f"stale ownership: {system_id}")

        reported = owner_entry.get("reported_status", "")
        if reported in GREEN_CLAIMS and (not living or stale):
            errors.append(f"catalog reports green without a living owner: {system_id}")

        if kind == "runnable-service":
            if tenant_id not in tenant_by_id:
                errors.append(f"system has no known tenant: {system_id}")
            else:
                tenant_owner = tenant_by_id[tenant_id].get("owner")
                if living and owner != tenant_owner:
                    errors.append(f"owner does not match tenant owner: {system_id}")
            if dependency_entry is None or not dependency_entry.get("depends_on"):
                errors.append(f"runnable system has no dependencies: {system_id}")
        elif dependency_entry is None:
            errors.append(f"system has no dependency list: {system_id}")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-04"
    return (
        load(ROOT / "catalog" / "systems.yaml"),
        load(ROOT / "catalog" / "ownership.yaml"),
        load(ROOT / "catalog" / "dependencies.yaml"),
        load(ROOT / "tenancy" / "tenants.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
