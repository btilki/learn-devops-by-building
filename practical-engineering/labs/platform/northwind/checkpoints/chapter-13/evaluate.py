from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
INHERITED_OBSERVABILITY = (
    ROOT / "inherited" / "devops-v1.1" / "observability" / "interface.yaml"
)
INHERITED_INCIDENT = ROOT / "inherited" / "devops-v1.1" / "incident" / "interface.yaml"
INHERITED_EVIDENCE = ROOT / "inherited" / "devsecops-v1.0" / "evidence" / "interface.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    model: dict,
    escalation: dict,
    changes: dict,
    incidents: dict,
    users: dict,
    systems: dict,
    ownership: dict,
    subjects: dict,
    plane_product: dict,
    reconciliation: dict,
    brief: dict,
    indicators: dict,
    non_metrics: dict,
    observability: dict,
    incident_interface: dict,
    evidence: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    system_by_id = {item["id"]: item for item in systems.get("systems", [])}
    ownership_by_system = {item["system"]: item for item in ownership.get("ownership", [])}
    plane_ids = {
        item["id"] for item in subjects.get("subjects", []) if item.get("kind") == "plane"
    }
    forbidden_roles = set(plane_product.get("forbidden_roles", [])) | set(
        expectations.get("forbidden_roles", [])
    )
    job_proofs = {item["id"] for item in indicators.get("indicators", [])}
    vanity = {
        item["id"]
        for item in non_metrics.get("non_metrics", [])
        if item.get("category") == "vanity"
    }
    tenant_workload = {
        item["id"]
        for item in non_metrics.get("non_metrics", [])
        if item.get("category") == "tenant-workload"
    } | set(observability.get("outcome_indicators", []))
    tenant_recovery = set(incident_interface.get("required_recovery_evidence", []))
    plane_lkg = next(
        (
            str(item.get("last_known_good"))
            for item in reconciliation.get("upgrades", [])
            if item.get("result") == "failed"
        ),
        None,
    )
    required_budget = set(brief.get("success_evidence", [])) | set(
        expectations.get("required_budget", [])
    )
    required_unsupported = set(expectations.get("required_unsupported", []))
    route_by_system = {item["system"]: item for item in escalation.get("routes", [])}

    if model.get("owner") not in user_ids:
        errors.append(f"model has no known owner: {model.get('owner')}")
    if model.get("plane") != plane_product.get("plane"):
        errors.append("support plane does not match control-plane product")
    if model.get("plane") != expectations.get("required_plane"):
        errors.append("support plane is not kubernetes-control-plane")
    if model.get("communication_cadence") != expectations.get("required_cadence"):
        errors.append("support cadence is not freeze-window")
    if not required_unsupported.issubset(set(model.get("unsupported", []))):
        errors.append("support model missing unsupported path")
    budget = set(model.get("error_budget_indicators", []))
    for indicator_id in required_budget:
        if indicator_id not in budget:
            errors.append(f"job-time budget missing job proof: {indicator_id}")
    for indicator_id in budget:
        if indicator_id in vanity:
            errors.append(f"job-time budget uses vanity: {indicator_id}")
        if indicator_id in tenant_workload:
            errors.append(f"job-time budget uses tenant workload: {indicator_id}")
        if indicator_id not in job_proofs:
            errors.append(f"job-time budget uses unknown indicator: {indicator_id}")

    for system_id, system in system_by_id.items():
        route = route_by_system.get(system_id)
        owned = ownership_by_system.get(system_id, {})
        if route is None:
            errors.append(f"missing escalation route: {system_id}")
            continue
        expected_kind = (
            "platform-product"
            if system.get("kind") == "platform-product"
            else "tenant-application"
        )
        if route.get("kind") != expected_kind:
            errors.append(f"escalation kind mismatch: {system_id}")
        if route.get("owner") != owned.get("owner"):
            errors.append(f"escalation owner mismatch: {system_id}")
        if route.get("escalation") != owned.get("escalation"):
            errors.append(f"escalation contact mismatch: {system_id}")
        if route.get("escalation") == "chat-history":
            errors.append(f"escalation is chat-history: {system_id}")
        if route.get("escalation") in set(model.get("unsupported", [])):
            errors.append(f"escalation is chat-history: {system_id}")

    for change in changes.get("changes", []):
        change_id = change.get("id")
        if change.get("approved_by") not in user_ids:
            errors.append(f"change has no known approver: {change_id}")
        if change.get("approved_by") in plane_ids or change.get("subject") in plane_ids:
            if change.get("result") == "allow":
                errors.append(f"plane self-approval: {change_id}")
        granted = change.get("granted_role")
        if change.get("unofficial") or granted in forbidden_roles:
            errors.append(f"unofficial plane-admin change: {change_id}")
        if (
            change.get("resource") == plane_product.get("plane")
            and plane_lkg
            and str(change.get("last_known_good")) != plane_lkg
        ):
            errors.append(f"missing last known good: {change_id}")
        if (
            plane_product.get("controller_may_rewrite_source") is False
            and change.get("source_rewritten")
        ):
            errors.append(f"controller rewrites source: {change_id}")
        if evidence.get("independent_producer_required") and change.get("result") == "allow":
            if change.get("unofficial"):
                errors.append(f"unofficial plane-admin change: {change_id}")

    for item in incidents.get("incidents", []):
        incident_id = item.get("id")
        system_id = item.get("system")
        route = route_by_system.get(system_id, {})
        if system_id not in system_by_id:
            errors.append(f"incident has no known system: {incident_id}")
        if route and item.get("class") != route.get("kind"):
            errors.append(f"incident class mismatch: {incident_id}")
        if route and item.get("escalation") != route.get("escalation"):
            errors.append(f"incident escalation mismatch: {incident_id}")
        if item.get("owner") not in user_ids:
            errors.append(f"incident has no known owner: {incident_id}")
        closed = item.get("closed_reason")
        if closed in vanity:
            errors.append(f"incident closed for vanity: {incident_id}")
        if closed in tenant_workload:
            errors.append(f"incident closed for tenant workload: {incident_id}")
        if item.get("reported_status") == "green":
            errors.append(f"incident reports green: {incident_id}")
        recovery = set(item.get("recovery_evidence") or [])
        if item.get("class") == "platform-product" and recovery & tenant_recovery:
            errors.append(f"platform incident uses tenant recovery evidence: {incident_id}")
        indicator_id = item.get("indicator")
        if item.get("class") == "platform-product" and indicator_id in tenant_workload:
            errors.append(f"platform incident uses tenant workload: {incident_id}")
    return errors


def completed_inputs() -> tuple:
    checkpoint = ROOT / "checkpoints" / "chapter-13"
    return (
        load(ROOT / "support" / "model.yaml"),
        load(ROOT / "support" / "escalation.yaml"),
        load(ROOT / "support" / "changes.yaml"),
        load(ROOT / "support" / "incidents.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(ROOT / "catalog" / "systems.yaml"),
        load(ROOT / "catalog" / "ownership.yaml"),
        load(ROOT / "control-plane" / "subjects.yaml"),
        load(ROOT / "control-plane" / "product.yaml"),
        load(ROOT / "control-plane" / "reconciliation.yaml"),
        load(ROOT / "product" / "brief.yaml"),
        load(ROOT / "devex" / "indicators.yaml"),
        load(ROOT / "devex" / "non-metrics.yaml"),
        load(INHERITED_OBSERVABILITY),
        load(INHERITED_INCIDENT),
        load(INHERITED_EVIDENCE),
        load(checkpoint / "expectations.yaml"),
    )
