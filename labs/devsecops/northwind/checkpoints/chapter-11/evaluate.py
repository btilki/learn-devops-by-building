import json
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return yaml.safe_load(path.read_text())


def inputs():
    base = ROOT / "policy"
    return (
        load(base / "bundle/rules.yaml"),
        load(base / "enforcement-points.yaml"),
        load(base / "exceptions.yaml"),
        load(base / "exception-policy.yaml"),
    )


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def exception_errors(exception, rules, points, governance, now=None):
    errors = []
    rule_ids = {item["id"] for item in rules["rules"]}
    point_ids = {item["id"] for item in points["points"]}
    if exception["rule"] not in rule_ids:
        errors.append("exception-rule-invalid")
    if exception["rule"] in governance["non_exceptable_rules"]:
        errors.append("exception-rule-non-exceptable")
    if not set(exception["enforcement_points"]).issubset(point_ids):
        errors.append("exception-point-invalid")
    if exception["scope"] in governance["forbidden_scopes"]:
        errors.append("exception-scope-broad")
    required = [
        "owner",
        "rationale",
        "compensating_controls",
        "compensation_enforcement_points",
        "evidence",
        "expires_at",
        "removal_path",
    ]
    for field in required:
        value = exception.get(field)
        if not value:
            errors.append(f"exception-{field.replace('_', '-')}-missing")
        values = value if isinstance(value, list) else [value]
        if any(item in governance["placeholder_values"] for item in values):
            errors.append(f"exception-{field.replace('_', '-')}-placeholder")
    if len(exception.get("evidence", [])) < governance["minimum_evidence_items"]:
        errors.append("exception-evidence-insufficient")
    compensation_points = set(exception.get("compensation_enforcement_points", []))
    if governance["require_independent_compensation_point"] and (
        not compensation_points or compensation_points.intersection(exception["enforcement_points"])
    ):
        errors.append("exception-compensation-not-independent")
    if exception.get("expires_at"):
        start = instant(exception["effective_at"])
        expiry = instant(exception["expires_at"])
        current = now or instant(governance["evaluation_time"])
        if expiry <= current:
            errors.append("exception-expired")
        if (expiry - start).total_seconds() > governance["maximum_duration_seconds"]:
            errors.append("exception-duration-excessive")
    return errors


def evaluate(rules, points, exceptions, governance, now=None):
    errors = []
    for rule in rules["rules"]:
        if not rule.get("owner"):
            errors.append(f"rule-owner-missing:{rule['id']}")
        placements = [point for point in points["points"] if rule["id"] in point["rules"]]
        if not placements:
            errors.append(f"rule-unplaced:{rule['id']}")
        if rule["unsafe_result"] == "deny" and not any(
            point["failure_mode"] == "fail-closed" for point in placements
        ):
            errors.append(f"blocking-placement-missing:{rule['id']}")
    for point in points["points"]:
        if point["failure_mode"] not in {"fail-closed", "detect-only"}:
            errors.append(f"failure-mode-invalid:{point['id']}")
        if point["decision_log"] != "required":
            errors.append(f"decision-log-missing:{point['id']}")
    for exception in exceptions["exceptions"]:
        errors.extend(
            f"{error}:{exception['id']}"
            for error in exception_errors(exception, rules, points, governance, now)
        )
    return errors


def decision(point, rule, policy_version, requester, result, reasons, exception=None):
    return {
        "kind": "policy-decision",
        "requester_context": requester,
        "enforcement_point": point,
        "rule": rule,
        "policy_version": policy_version,
        "result": result,
        "reasons": reasons,
        "exception": exception,
    }


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def log(value):
    path = ROOT / "build/chapter-11-decisions.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        stream.write(json.dumps(value) + "\n")
