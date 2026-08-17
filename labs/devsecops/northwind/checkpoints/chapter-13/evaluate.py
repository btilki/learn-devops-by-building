import json
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return yaml.safe_load(path.read_text())


def inputs():
    modeled = load(ROOT / "checkpoints/chapter-13/cases/attack-events.yaml")
    runtime_path = ROOT / "runtime/events.jsonl"
    runtime = [json.loads(line) for line in runtime_path.read_text().splitlines()]
    egress = next(event for event in runtime if event["action"] == "undeclared-egress")
    return (
        load(ROOT / "detection/event-contract.yaml"),
        load(ROOT / "detection/hypotheses.yaml"),
        load(ROOT / "detection/rules/correlate-progression.yaml"),
        {"events": [*modeled["events"], egress]},
    )


def normalize(events, contract, rule):
    normalized, gaps = [], []
    if contract["retention_days"] <= 0:
        gaps.append({"event": "contract", "invalid": "retention-days"})
    for index, event in enumerate(events["events"]):
        required = [
            *contract["required_fields"],
            *rule["required_context"].get(event.get("action"), []),
        ]
        missing = [field for field in required if not event.get(field)]
        invalid = []
        if event.get("integrity") not in contract["accepted_integrity"]:
            invalid.append("integrity")
        if missing or invalid:
            gaps.append({"event": index, "missing": sorted(set(missing)), "invalid": invalid})
        else:
            normalized.append(event)
    return normalized, gaps


def connected(events, fields):
    if not events:
        return []
    group = [events[0]]
    remaining = events[1:]
    changed = True
    while changed:
        changed = False
        values = {event.get(field) for event in group for field in fields if event.get(field)}
        for event in remaining[:]:
            if any(event.get(field) in values for field in fields if event.get(field)):
                group.append(event)
                remaining.remove(event)
                changed = True
    return group


def correlate(events, hypothesis, rule):
    matched = connected(events, rule["correlation_fields"])
    actions = {event["action"] for event in matched}
    times = sorted(
        datetime.fromisoformat(event["time"].replace("Z", "+00:00")) for event in matched
    )
    window = int((times[-1] - times[0]).total_seconds()) if times else 0
    distinct = rule["noise_boundary"] == "require-distinct-actions"
    fires = (
        set(hypothesis["required_actions"]).issubset(actions)
        and (len(actions) if distinct else len(matched)) >= hypothesis["threshold"]
        and window <= hypothesis["maximum_window_seconds"]
    )
    return {
        "kind": "security-alert",
        "hypothesis": hypothesis["id"],
        "joined_on": rule["correlation_fields"],
        "actions": sorted(actions),
        "window_seconds": window,
        "owner": hypothesis["owner"],
        "response": hypothesis["response"],
        "result": "alert" if fires else "no-alert",
        "evidence_count": len(matched),
    }


def alerts(events, hypotheses, rule):
    return [correlate(events, hypothesis, rule) for hypothesis in hypotheses["hypotheses"]]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")
