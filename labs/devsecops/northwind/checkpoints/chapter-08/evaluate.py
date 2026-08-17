from datetime import UTC, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return yaml.safe_load(path.read_text())


def inputs():
    base = ROOT / "vulnerabilities"
    return (
        load(base / "findings/raw.yaml"),
        load(base / "findings/normalized.yaml"),
        load(base / "context.yaml"),
        load(base / "decisions.yaml"),
        load(base / "exceptions.yaml"),
        load(base / "policy.yaml"),
    )


def normalize(raw, policy):
    groups = {}
    for claim in raw["claims"]:
        if policy["active_versions"].get(claim["component"]) != claim["affected_version"]:
            continue
        key = (claim["vulnerability"], claim["component"], claim["affected_version"])
        item = groups.setdefault(key, {"sources": set(), "severities": set()})
        item["sources"].add(claim["scanner"])
        item["severities"].add(claim["severity"])
    findings = []
    for key, observed in groups.items():
        vulnerability, component, version = key
        severity = min(observed["severities"], key=policy["severity_order"].index)
        findings.append(
            {
                "id": f"{vulnerability}|{component}|{version}",
                "vulnerability": vulnerability,
                "component": component,
                "affected_version": version,
                "severity": severity,
                "sources": sorted(observed["sources"]),
                "confidence": "high" if len(observed["sources"]) > 1 else "medium",
            }
        )
    return findings


def urgent(item, policy):
    rules = policy["expedited_if"]
    return bool(
        item.get("reachable")
        and item.get("exposure") == "internet"
        and rules["reachable_and_internet"]
        or item.get("reachable")
        and set(item.get("assets", [])).intersection(policy["critical_assets"])
        and rules["reachable_and_critical_asset"]
        or item.get("known_exploitation")
        and item.get("deployed")
        and rules["known_exploitation_and_deployed"]
    )


def evaluate(raw, findings, context, decisions, exceptions, policy, now=None):
    errors = []
    if normalize(raw, policy) != findings["findings"]:
        errors.append("normalization-mismatch")
    finding_ids = {item["id"] for item in findings["findings"]}
    contexts = {item["finding"]: item for item in context["contexts"]}
    decision_map = {item["finding"]: item for item in decisions["decisions"]}
    exception_map = {item["id"]: item for item in exceptions["exceptions"]}
    priorities = [item["priority"] for item in decisions["decisions"]]
    if len(priorities) != len(set(priorities)) or sorted(priorities) != list(
        range(1, len(priorities) + 1)
    ):
        errors.append("queue-priority-invalid")
    if len(finding_ids) != len(findings["findings"]):
        errors.append("duplicate-finding")
    for finding_id in finding_ids:
        if finding_id not in contexts:
            errors.append(f"context-missing:{finding_id}")
        if finding_id not in decision_map:
            errors.append(f"decision-missing:{finding_id}")
    instant = now or datetime(2026, 8, 15, tzinfo=UTC)
    for finding_id, decision in decision_map.items():
        item = contexts.get(finding_id, {})
        required = ["deployed", "reachable", "exposure", "known_exploitation", "assets", "owner"]
        if any(field not in item for field in required):
            errors.append(f"decision-context-incomplete:{finding_id}")
        if decision["owner"] != item.get("owner"):
            errors.append(f"owner-mismatch:{finding_id}")
        if not decision.get("uncertainty"):
            errors.append(f"uncertainty-missing:{finding_id}")
        deadline = datetime.fromisoformat(decision["deadline"].replace("Z", "+00:00"))
        decided = datetime.fromisoformat(decision["decided_at"].replace("Z", "+00:00"))
        if deadline < instant:
            errors.append(f"decision-overdue:{finding_id}")
        is_urgent = urgent(item, policy)
        if is_urgent and (deadline - decided).days > policy["urgent_max_days"]:
            errors.append(f"urgent-deadline-invalid:{finding_id}")
        if is_urgent and decision["priority"] != 1:
            errors.append(f"urgent-priority-invalid:{finding_id}")
        if is_urgent and decision["treatment"] != policy["urgent_treatment"]:
            errors.append(f"urgent-treatment-invalid:{finding_id}")
        if decision["treatment"] in {"accept", "monitor"}:
            exception = exception_map.get(decision.get("exception"))
            if not exception:
                errors.append(f"exception-missing:{finding_id}")
            else:
                expiry = datetime.fromisoformat(exception["expires_at"].replace("Z", "+00:00"))
                if expiry <= instant:
                    errors.append(f"exception-expired:{finding_id}")
    return errors
