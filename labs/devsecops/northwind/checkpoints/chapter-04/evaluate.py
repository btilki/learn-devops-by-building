import json
from datetime import UTC, datetime
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
EVENTS = ROOT / "identity" / "access-events.jsonl"
TRACE_SCHEMA = json.loads(
    (ROOT / "schemas" / "authorization-decision.schema.json").read_text(encoding="utf-8")
)


def load(p):
    return yaml.safe_load(p.read_text())


def authorize(
    subject_id, claims, action, resource, environment, subjects, roles, trust, record=True
):
    subject = next((x for x in subjects["subjects"] if x["id"] == subject_id), None)
    reasons = []
    if not subject:
        reasons.append("unknown-subject")
    elif subject["status"] != "active":
        reasons.append("revoked-subject")
    if claims.get("issuer") != (subject or {}).get("issuer"):
        reasons.append("issuer-mismatch")
    issuer = next((x for x in trust["issuers"] if x["id"] == claims.get("issuer")), None)
    if not issuer or claims.get("audience") not in issuer["audiences"]:
        reasons.append("audience-rejected")
    elif subject and claims.get("audience") not in subject["audiences"]:
        reasons.append("audience-rejected")
    if claims.get("lifetime_seconds", 999999) > trust["max_session_seconds"]:
        reasons.append("session-too-long")
    if claims.get("reusable", False) and not trust["reusable_tokens_allowed"]:
        reasons.append("reusable-token-rejected")
    allowed = False
    if subject:
        role_map = {x["id"]: x for x in roles["roles"]}
        allowed = any(
            rule == {"action": action, "resource": resource, "environment": environment}
            for role in subject["roles"]
            for rule in role_map.get(role, {}).get("allows", [])
        )
    if not allowed:
        reasons.append("authorization-denied")
    decision = {
        "claim_id": claims.get("claim_id", "unidentified-claim"),
        "subject": subject_id,
        "action": action,
        "resource": resource,
        "environment": environment,
        "issuer": claims.get("issuer"),
        "audience": claims.get("audience"),
        "session_lifetime_seconds": claims.get("lifetime_seconds"),
        "reusable_claim": bool(claims.get("reusable", False)),
        "authorization_policy_version": roles.get("policy_version"),
        "trust_policy_version": trust.get("policy_version"),
        "result": "deny" if reasons else "allow",
        "reasons": reasons,
    }
    if record:
        append_event(decision)
    return decision


def append_event(decision):
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    event = {"recorded_at": datetime.now(UTC).isoformat(timespec="seconds"), **decision}
    with EVENTS.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event) + "\n")


def read_events(count=None):
    if not EVENTS.exists():
        return []
    events = [json.loads(line) for line in EVENTS.read_text(encoding="utf-8").splitlines() if line]
    return events if count is None else events[-count:]


def trace_errors(decision):
    validator = Draft202012Validator(TRACE_SCHEMA)
    return sorted(e.message for e in validator.iter_errors(decision))


def inputs():
    return (
        load(ROOT / "identity/subjects.yaml"),
        load(ROOT / "identity/roles.yaml"),
        load(ROOT / "identity/trust-policy.yaml"),
    )


def start_state():
    case = load(Path(__file__).resolve().parent / "cases" / "shared-identity.yaml")
    return case["subjects"], case["roles"], case["trust"]
