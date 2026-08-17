import json
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(p):
    return yaml.safe_load(p.read_text())


def dt(v):
    return datetime.fromisoformat(v.replace("Z", "+00:00"))


def evaluate(r, p):
    e = []
    if any(not r.get(field) for field in p["required_fields"]):
        e.append("required-field-missing")
    if not p["self_approval_allowed"] and r.get("requester") == r.get("approver"):
        e.append("self-approval")
    times = [
        r.get(x) for x in ["requested_at", "approved_at", "issued_at", "ended_at", "reviewed_at"]
    ]
    if not all(times) or not all(dt(a) < dt(b) for a, b in zip(times, times[1:])):
        e.append("lifecycle-order-invalid")
    if (
        r.get("issued_at")
        and r.get("expires_at")
        and (dt(r["expires_at"]) - dt(r["issued_at"])).total_seconds() > p["max_duration_seconds"]
    ):
        e.append("duration-excessive")
    if r.get("action") not in p["break_glass"]["allowed_actions"]:
        e.append("action-out-of-scope")
    if p["break_glass"].get("requires_after_action_review") and not r.get("reviewed_at"):
        e.append("after-action-review-missing")
    if (
        r.get("reviewed_at")
        and r.get("ended_at")
        and (dt(r["reviewed_at"]) - dt(r["ended_at"])).total_seconds()
        > p["break_glass"]["review_due_seconds"]
    ):
        e.append("review-late")
    return e


def events():
    return [json.loads(x) for x in (ROOT / "privilege/sessions.jsonl").read_text().splitlines()]


def inputs():
    return load(ROOT / "privilege/requests/approved.yaml"), load(ROOT / "privilege/policy.yaml")
