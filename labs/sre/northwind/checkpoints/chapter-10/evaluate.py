from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_COMMANDERS = {"slack", "chat-history", "whoever-answered"}
INSUFFICIENT_SLI = "order_success_ratio"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    command: dict,
    roles: dict,
    traces: dict,
    inherited_incident: dict,
    inherited_support: dict,
    systems: dict,
    rotations: dict,
    actions: dict,
    journeys: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    inherited_evidence = set(inherited_incident.get("required_recovery_evidence") or [])
    insufficient = set(command.get("insufficient_close_evidence") or [])
    for field in inherited_evidence | {INSUFFICIENT_SLI}:
        if field not in insufficient:
            errors.append("inherited one-path evidence treated as portfolio close")
            break

    forbidden = set(command.get("forbidden_commanders") or [])
    for label in FORBIDDEN_COMMANDERS:
        if label not in forbidden:
            errors.append(f"missing forbidden commander: {label}")

    role_ids = {item.get("id") for item in roles.get("roles", [])}
    if "commander" not in role_ids or "operator" not in role_ids:
        errors.append("unofficial single-hero command")
    commander_roles = [
        item for item in roles.get("roles", []) if item.get("id") == "commander"
    ]
    operator_roles = [
        item for item in roles.get("roles", []) if item.get("id") == "operator"
    ]
    if commander_roles and not commander_roles[0].get("may_close"):
        errors.append("unofficial single-hero command")
    if operator_roles and operator_roles[0].get("may_close"):
        errors.append("unofficial single-hero command")

    support_kinds = set(inherited_support.get("kinds") or [])
    system_ids = {item.get("id") for item in systems.get("systems", [])}
    contacts = {item.get("catalog_contact") for item in systems.get("systems", [])}
    living_primaries = {
        item.get("primary")
        for item in rotations.get("rotations", [])
        if item.get("living_primary")
    }
    freeze_ids = {
        item.get("id")
        for item in actions.get("actions", [])
        if item.get("action") == "freeze"
    }
    journey_ids = {item.get("id") for item in journeys.get("journeys", [])}

    spanning_id = expectations.get("spanning_trace_id")
    platform_id = expectations.get("platform_trace_id")
    required_journeys = set(expectations.get("required_spanning_journeys") or [])
    required_systems = set(expectations.get("required_spanning_systems") or [])
    required_freezes = set(expectations.get("required_freeze_joins") or [])
    required_platform = expectations.get("required_platform_system")

    traces_by_id = {item.get("id"): item for item in traces.get("traces", [])}
    for trace in traces.get("traces", []):
        trace_id = trace.get("id", "unknown")
        commander = trace.get("commander", "")
        if commander in FORBIDDEN_COMMANDERS:
            errors.append(f"slack-as-commander: {trace_id}/{commander}")
        elif commander not in living_primaries:
            if commander in contacts or commander in system_ids:
                errors.append(f"catalog contact treated as system: {commander}")
        kind = trace.get("support_kind")
        if kind not in support_kinds:
            errors.append(f"unknown support kind: {trace_id}/{kind}")
        if trace.get("status") == "recovered":
            errors.append(f"trace emits recovered: {trace_id}")
        paged = list(trace.get("oncall_systems") or [])
        for system in paged:
            if system in contacts:
                errors.append(f"catalog contact treated as system: {system}")
            elif system not in system_ids:
                errors.append(f"catalog contact treated as system: {system}")
        close_evidence = set(trace.get("close_evidence") or [])
        if trace.get("status") == "closed" or close_evidence & insufficient:
            if close_evidence & inherited_evidence or INSUFFICIENT_SLI in close_evidence:
                errors.append(f"one-path close: {INSUFFICIENT_SLI}")
            elif trace.get("status") == "closed":
                errors.append(f"one-path close: {INSUFFICIENT_SLI}")

        if kind == "platform-product":
            if required_platform not in paged:
                errors.append("platform-product landed on storefront")
            if "storefront-oncall-system" in paged:
                errors.append("platform-product landed on storefront")

    spanning = traces_by_id.get(spanning_id, {})
    if spanning:
        affected = set(spanning.get("affected_journeys") or [])
        for journey in required_journeys:
            if journey not in affected:
                errors.append(f"missing required journey: {journey}")
            elif journey not in journey_ids:
                errors.append(f"missing required journey: {journey}")
        paged = set(spanning.get("oncall_systems") or [])
        contact_by_system = {
            item.get("id"): item.get("catalog_contact")
            for item in systems.get("systems", [])
        }
        for system_id in required_systems:
            if system_id not in paged:
                contact = contact_by_system.get(system_id)
                if contact in paged:
                    errors.append(f"catalog contact treated as system: {contact}")
        joined = set(spanning.get("freeze_join") or [])
        for freeze_id in required_freezes:
            if freeze_id not in joined and freeze_id in freeze_ids:
                errors.append(f"missing freeze join: {freeze_id}")
        states = {
            item.get("journey"): item.get("state")
            for item in spanning.get("journey_states") or []
        }
        if states.get("dispatch-fulfillment") in {"failing", "degraded"}:
            if spanning.get("status") == "closed":
                errors.append(f"one-path close: {INSUFFICIENT_SLI}")

    platform = traces_by_id.get(platform_id, {})
    if platform and required_platform:
        paged = set(platform.get("oncall_systems") or [])
        if required_platform not in paged:
            errors.append("platform-product landed on storefront")

    return list(dict.fromkeys(errors))


def completed_inputs() -> tuple[
    dict, dict, dict, dict, dict, dict, dict, dict, dict, dict
]:
    checkpoint = ROOT / "checkpoints" / "chapter-10"
    return (
        load(ROOT / "incidents" / "command.yaml"),
        load(ROOT / "incidents" / "roles.yaml"),
        load(ROOT / "incidents" / "traces.yaml"),
        load(ROOT / "inherited" / "devops-v1.1" / "incident" / "interface.yaml"),
        load(ROOT / "inherited" / "platform-v1.0" / "support" / "interface.yaml"),
        load(ROOT / "oncall" / "system.yaml"),
        load(ROOT / "oncall" / "rotations.yaml"),
        load(ROOT / "policy" / "actions.yaml"),
        load(ROOT / "reliability" / "journeys.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
