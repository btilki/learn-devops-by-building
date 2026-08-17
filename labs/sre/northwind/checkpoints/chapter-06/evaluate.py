from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_PRIMARIES = {"slack", "chat-history", "whoever-answered"}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    systems: dict,
    rotations: dict,
    handoffs: dict,
    authority: dict,
    pages: dict,
    tickets: dict,
    catalog_iface: dict,
    authorization: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    contacts = set(catalog_iface.get("escalation_contacts", []))
    system_by_id = {item["id"]: item for item in systems.get("systems", [])}
    system_by_contact = {
        item["catalog_contact"]: item for item in systems.get("systems", [])
    }
    rotation_by_system = {item["system"]: item for item in rotations.get("rotations", [])}
    handoff_by_rotation = {
        item["rotation"]: item for item in handoffs.get("handoffs", [])
    }
    authority_by_system = {item["system"]: item for item in authority.get("authority", [])}

    for system in systems.get("systems", []):
        system_id = system.get("id", "unknown")
        contact = system.get("catalog_contact")
        if system_id == contact:
            errors.append(f"catalog contact treated as system: {system_id}")
        if contact not in contacts:
            errors.append(f"system has no known catalog contact: {system_id}/{contact}")
        if not system.get("page_load_limit"):
            errors.append(f"system has no page load limit: {system_id}")
        rotation = rotation_by_system.get(system_id)
        if rotation is None:
            errors.append(f"missing required rotation: {system_id}")
            continue
        primary = rotation.get("primary", "")
        if primary in FORBIDDEN_PRIMARIES:
            errors.append(f"slack-as-primary: {system_id}/{primary}")
        if not rotation.get("living_primary"):
            errors.append(f"missing living primary: {system_id}")
        if not rotation.get("secondary"):
            errors.append(f"rotation has no secondary: {system_id}")
        if rotation.get("id") not in handoff_by_rotation:
            errors.append(f"missing required handoff: {rotation.get('id')}")
        if system_id not in authority_by_system:
            errors.append(f"missing required authority: {system_id}")

    destinations = [item.get("destination") for item in pages.get("pages", [])]
    destinations.extend(item.get("destination") for item in tickets.get("tickets", []))
    for destination in destinations:
        system = system_by_contact.get(destination)
        if system is None:
            errors.append(f"page destination has no system: {destination}")
            continue
        expected_system = expectations.get("contact_systems", {}).get(destination)
        if expected_system and system.get("id") != expected_system:
            if destination == "platform-oncall":
                errors.append(
                    f"platform destination landed on storefront: {system.get('id')}"
                )
            else:
                errors.append(
                    f"destination system mismatch: {destination}/{system.get('id')}"
                )

    expected_forbidden = authorization.get("self_approval_forbidden")
    for item in authority.get("authority", []):
        auth_id = item.get("id", "unknown")
        if item.get("self_approval_forbidden") is not True:
            errors.append(f"self-approval not forbidden: {auth_id}")
        if expected_forbidden is True and item.get("self_approval_forbidden") is not True:
            errors.append(f"inherited self_approval_forbidden ignored: {auth_id}")
        glass = item.get("break_glass") or {}
        if glass.get("requester") == glass.get("approver"):
            errors.append(f"break-glass is self-approved: {auth_id}")
        if not glass.get("after_action_review"):
            errors.append(f"break-glass has no after-action review: {auth_id}")
        if not glass.get("expiry"):
            errors.append(f"break-glass has no expiry: {auth_id}")

    for system_id in expectations.get("required_systems", []):
        if system_id not in system_by_id:
            errors.append(f"missing required system: {system_id}")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-06"
    return (
        load(ROOT / "oncall" / "system.yaml"),
        load(ROOT / "oncall" / "rotations.yaml"),
        load(ROOT / "oncall" / "handoffs.yaml"),
        load(ROOT / "oncall" / "authority.yaml"),
        load(ROOT / "alerting" / "pages.yaml"),
        load(ROOT / "alerting" / "tickets.yaml"),
        load(ROOT / "inherited" / "platform-v1.0" / "catalog" / "interface.yaml"),
        load(ROOT / "inherited" / "devsecops-v1.0" / "authorization" / "interface.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
