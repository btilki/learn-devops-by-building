from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
HORTATORY = {"be-more-careful", "be more careful"}
REQUIRED_SUBSTITUTES = {
    "devsecops-eradication",
    "devops-one-change-retrospective",
}
CASCADE = "chapter-09-cascade"
SELF_KEYS = {"verified", "learned"}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _walk_self_approval(obj: object, errors: list[str], loc: str) -> None:
    if isinstance(obj, dict):
        current = str(obj.get("id") or loc)
        for key, value in obj.items():
            if key in SELF_KEYS:
                errors.append(f"record verifies itself: {current}")
            _walk_self_approval(value, errors, current)
    elif isinstance(obj, list):
        for item in obj:
            _walk_self_approval(item, errors, loc)


def evaluate(
    program: dict,
    records: dict,
    actions: dict,
    traces: dict,
    shedding: dict,
    bounds: dict,
    evidence: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    _walk_self_approval(program, errors, "program")
    _walk_self_approval(records, errors, "records")
    _walk_self_approval(actions, errors, "actions")

    forbidden = set(program.get("forbidden_actions") or [])
    if "be-more-careful" not in forbidden:
        errors.append("missing forbidden action: be-more-careful")

    substitutes = set(program.get("forbidden_substitutes") or [])
    if not REQUIRED_SUBSTITUTES.issubset(substitutes):
        errors.append("learning substitutes eradication or retrospective")

    if program.get("toil_join") != bounds.get("id"):
        errors.append("learning unbounded by toil bound")
    if not program.get("verification_independent"):
        errors.append("missing independent verification")

    incident_ids = {item.get("id") for item in traces.get("traces", [])}
    required = set(program.get("required_incidents") or []) | incident_ids
    covered = {item.get("incident") for item in records.get("records") or []}
    covered |= {item.get("incident") for item in records.get("waivers") or []}
    for incident_id in sorted(required):
        if incident_id and incident_id not in covered:
            errors.append(f"missing required record: {incident_id}")

    for waiver in records.get("waivers") or []:
        if not waiver.get("expires_at") or not waiver.get("owner"):
            errors.append(f"missing waiver expiry: {waiver.get('id', 'unknown')}")
        if not waiver.get("removal_path"):
            errors.append(f"missing waiver expiry: {waiver.get('id', 'unknown')}")

    record_ids = {item.get("id") for item in records.get("records") or []}
    shed_ids = {item.get("id") for item in shedding.get("rules") or []}
    independent_required = bool(evidence.get("independent_producer_required"))
    cascade_verified = False

    for action in actions.get("actions") or []:
        action_id = str(action.get("id", "unknown"))
        change = str(action.get("change", ""))
        if action_id in HORTATORY or change in HORTATORY:
            errors.append("hortatory action: be-more-careful")
        if not action.get("owner"):
            errors.append(f"missing action owner: {action_id}")
        if not action.get("due_at"):
            errors.append(f"missing action due date: {action_id}")
        verification = action.get("verification") or {}
        producer = verification.get("producer")
        if producer in record_ids or producer == action_id:
            errors.append("missing independent verification")
        if independent_required and not verification.get("independent_of_record"):
            errors.append("missing independent verification")
        if action.get("addresses") == CASCADE:
            if (
                producer in shed_ids
                and verification.get("independent_of_record")
                and producer not in record_ids
            ):
                cascade_verified = True

    if expectations.get("require_cascade_action") and not cascade_verified:
        errors.append("repeated cascade without verified action")

    return list(dict.fromkeys(errors))


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-11"
    return (
        load(ROOT / "learning" / "program.yaml"),
        load(ROOT / "learning" / "records.yaml"),
        load(ROOT / "learning" / "actions.yaml"),
        load(ROOT / "incidents" / "traces.yaml"),
        load(ROOT / "degradation" / "shedding.yaml"),
        load(ROOT / "toil" / "bounds.yaml"),
        load(ROOT / "inherited" / "devsecops-v1.0" / "evidence" / "interface.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
