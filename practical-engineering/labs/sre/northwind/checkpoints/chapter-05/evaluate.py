from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
INHERITED_FAST = {"short_window": "5m", "long_window": "1h", "threshold": 14.4}
INHERITED_SLOW = {"short_window": "30m", "long_window": "6h", "threshold": 6}
SYMPTOM_SLIS = {"cpu-utilization", "replica-ready", "portal-availability"}
JOB_TIME_PROOFS = {
    "time-to-first-environment",
    "paved-road-completion",
    "catalog-freshness",
}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    burns: dict,
    pages: dict,
    tickets: dict,
    decisions: dict,
    catalog_iface: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    burn_by_id = {item["id"]: item for item in burns.get("burns", [])}
    accepted_slis = {
        item["candidate"]
        for item in decisions.get("decisions", [])
        if item.get("treatment") == "accept"
    }
    contacts = set(catalog_iface.get("escalation_contacts", []))
    pages_by_burn = {item["burn"]: item for item in pages.get("pages", [])}
    tickets_by_burn = {item["burn"]: item for item in tickets.get("tickets", [])}

    volume = burns.get("minimum_evidence_volume", 0)
    if not isinstance(volume, int) or volume <= 1:
        errors.append("minimum evidence volume does not exceed one event")

    window_pairs = burns.get("window_pairs", {})
    if window_pairs.get("fast") != INHERITED_FAST:
        errors.append("inherited fast burn windows rewritten")
    if window_pairs.get("slow") != INHERITED_SLOW:
        errors.append("inherited slow burn windows rewritten")

    for sli in expectations.get("required_page_slis", []):
        matching = [
            item
            for item in burns.get("burns", [])
            if item.get("sli") == sli and item.get("disposition") == "page"
        ]
        pairs = {item.get("window_pair") for item in matching}
        if "fast" not in pairs:
            errors.append(f"missing required page: {sli}/fast")
        if "slow" not in pairs:
            errors.append(f"missing required page: {sli}/slow")

    for burn in burns.get("burns", []):
        burn_id = burn.get("id", "unknown")
        sli = burn.get("sli")
        disposition = burn.get("disposition")
        if disposition == "page":
            if sli not in accepted_slis:
                errors.append(f"page uses unaccepted sli: {burn_id}/{sli}")
            if sli in SYMPTOM_SLIS:
                errors.append(f"symptom pages: {sli}")
            if sli in JOB_TIME_PROOFS:
                errors.append(f"job-time pages: {sli}")
            if burn_id not in pages_by_burn:
                errors.append(f"page disposition has no page row: {burn_id}")
        if disposition == "ticket" and burn_id not in tickets_by_burn:
            errors.append(f"ticket disposition has no ticket row: {burn_id}")
        if disposition == "record":
            if burn_id in pages_by_burn:
                errors.append(f"record disposition is paged: {burn_id}")
            if burn_id in tickets_by_burn:
                errors.append(f"record disposition is ticketed: {burn_id}")

    for page in pages.get("pages", []):
        page_id = page.get("id", "unknown")
        burn_id = page.get("burn")
        destination = page.get("destination")
        if "user_impact" in page:
            errors.append(f"page emits user impact: {page_id}")
        if page.get("destination_kind") != "catalog-contact":
            errors.append(f"page is not a catalog contact: {page_id}")
        if destination not in contacts:
            errors.append(f"page has no known catalog contact: {page_id}/{destination}")
        burn = burn_by_id.get(burn_id)
        if burn is None:
            errors.append(f"page has no known burn: {page_id}/{burn_id}")
            continue
        sli = burn.get("sli")
        expected_dest = expectations.get("page_destinations", {}).get(sli)
        if expected_dest and destination != expected_dest:
            errors.append(f"page destination mismatch: {sli}/{destination}")
        if sli in SYMPTOM_SLIS:
            errors.append(f"symptom pages: {sli}/{destination}")
        if sli in JOB_TIME_PROOFS:
            errors.append(f"job-time pages: {sli}/{destination}")

    job_time_sli = expectations.get("job_time_ticket_sli")
    if job_time_sli:
        matching = [
            item
            for item in burns.get("burns", [])
            if item.get("sli") == job_time_sli and item.get("disposition") == "ticket"
        ]
        if not matching:
            errors.append(f"missing required ticket: {job_time_sli}")
        else:
            ticket = tickets_by_burn.get(matching[0]["id"])
            expected = expectations.get("job_time_ticket_destination")
            if ticket is None or ticket.get("destination") != expected:
                errors.append(f"job-time ticket destination mismatch: {job_time_sli}")

    for sli in expectations.get("forbidden_page_slis", []):
        for page in pages.get("pages", []):
            burn = burn_by_id.get(page.get("burn"), {})
            if burn.get("sli") == sli:
                errors.append(f"symptom pages: {sli}/{page.get('destination')}")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-05"
    return (
        load(ROOT / "alerting" / "burns.yaml"),
        load(ROOT / "alerting" / "pages.yaml"),
        load(ROOT / "alerting" / "tickets.yaml"),
        load(ROOT / "slis" / "decisions.yaml"),
        load(ROOT / "inherited" / "platform-v1.0" / "catalog" / "interface.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
