import importlib.util
import json
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CATEGORIES = {
    "mechanism_evidence",
    "decision_evidence",
    "outcome_evidence",
    "recovery_evidence",
}
IMPROVEMENT_MAP = [
    (
        "exception-claim-expired",
        {
            "id": "improve-exception-live-validation",
            "owner": "platform-security",
            "action": "bind assurance exception claims to current expiry state",
            "evidence_to_restore": ["policy/exceptions.yaml", "build/chapter-11-recovery.json"],
            "due_at": "2026-08-20T00:00:00Z",
            "status": "open",
        },
    ),
    (
        "telemetry-gap",
        {
            "id": "improve-telemetry-completeness-gate",
            "owner": "security-response",
            "action": "require complete post-change telemetry before assurance passes",
            "evidence_to_restore": ["detection/event-contract.yaml", "runtime/events.jsonl"],
            "due_at": "2026-08-22T00:00:00Z",
            "status": "open",
        },
    ),
    (
        "attack-path-uncovered",
        {
            "id": "improve-node-cache-persistence-coverage",
            "owner": "security-response",
            "action": "add node-cache invalidation as a distinct control from registry-cache",
            "evidence_to_restore": ["detection/hypotheses.yaml", "governance/evidence-map.yaml"],
            "due_at": "2026-08-22T00:00:00Z",
            "status": "open",
        },
    ),
    (
        "material-change-review-pending",
        {
            "id": "improve-material-change-review-scope",
            "owner": "delivery-security",
            "action": "reopen only the objectives invalidated by the changed attack path",
            "evidence_to_restore": [
                "governance/review-calendar.yaml",
                "threat-model/attack-paths.yaml",
            ],
            "due_at": "2026-08-21T00:00:00Z",
            "status": "open",
        },
    ),
]


def load(path):
    if path.suffix == ".json":
        return json.loads(path.read_text())
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text().splitlines() if line]
    return yaml.safe_load(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix in {".yaml", ".yml"}:
        path.write_text(yaml.safe_dump(value, sort_keys=False))
    else:
        path.write_text(json.dumps(value, indent=2) + "\n")


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def expectations():
    return load(ROOT / "checkpoints/chapter-16/expectations.yaml")


def forbidden_prefixes():
    return tuple(expectations()["forbidden_evidence_prefixes"])


def load_module(chapter, name="evaluate"):
    path = ROOT / f"checkpoints/{chapter}/{name}.py"
    spec = importlib.util.spec_from_file_location(f"{chapter}_{name}", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_id(value, identifier):
    if isinstance(value, dict):
        if value.get("id") == identifier:
            return value
        for child in value.values():
            found = find_id(child, identifier)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_id(child, identifier)
            if found is not None:
                return found
    return None


def fragment_value(value, fragment):
    current = value
    for part in fragment.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            found = find_id(current, part)
            if found is None:
                raise KeyError(part)
            current = found
    return current


def resolve_evidence_link(ref, forbidden=()):
    if any(ref.startswith(prefix) for prefix in forbidden):
        return None, [f"evidence-self-reference:{ref}"]
    path_part, _, fragment = ref.partition("#")
    path = ROOT / path_part
    if not path.exists():
        return None, [f"evidence-link-missing:{ref}"]
    value = load(path)
    if not fragment:
        return value, []
    expected = None
    if "=" in fragment:
        fragment, expected = fragment.split("=", 1)
    try:
        selected = fragment_value(value, fragment)
    except KeyError:
        return None, [f"evidence-fragment-missing:{ref}"]
    if expected is not None and str(selected).lower() != expected.lower():
        return selected, [f"evidence-link-value-mismatch:{ref}"]
    return selected, []


def catalog_errors(catalog, risks, attack_paths, expected=None):
    expected = expected or expectations()
    errors = []
    objectives = catalog["objectives"]
    ids = [objective["id"] for objective in objectives]
    if len(ids) != len(set(ids)):
        errors.append("objective-duplicate")
    known_risks = {risk["id"] for risk in risks["risks"]}
    known_paths = {path["id"] for path in attack_paths["attack_paths"]}
    covered_risks = {objective["risk"] for objective in objectives}
    covered_paths = {path for objective in objectives for path in objective["attack_paths"]}
    for risk_id in sorted(known_risks - covered_risks):
        errors.append(f"risk-without-objective:{risk_id}")
    for path_id in sorted(known_paths - covered_paths):
        errors.append(f"attack-path-without-objective:{path_id}")
    for required in expected["required_objectives"]:
        if required not in ids:
            errors.append(f"required-objective-missing:{required}")
    types = {
        objective["control_type"]
        for objective in objectives
        if objective["risk"] == expected["priority_risk"]
    }
    for required in expected["required_control_types_for_priority_risk"]:
        if required not in types:
            errors.append(f"priority-risk-missing-{required}-control")
    for objective in objectives:
        if not objective["owner"]:
            errors.append(f"objective-owner-missing:{objective['id']}")
        if objective["risk"] not in known_risks:
            errors.append(f"objective-risk-unknown:{objective['id']}")
        if not set(objective["attack_paths"]).issubset(known_paths):
            errors.append(f"objective-attack-path-unknown:{objective['id']}")
        for implementation in objective["implementation"]:
            _, link_errors = resolve_evidence_link(implementation)
            errors.extend(
                error.replace("evidence-", "implementation-", 1) for error in link_errors
            )
        if not objective["limitations"]:
            errors.append(f"objective-limitations-missing:{objective['id']}")
    return errors


def evidence_map_errors(catalog, evidence_map, forbidden=None):
    forbidden = forbidden if forbidden is not None else forbidden_prefixes()
    expected = expectations()
    errors = []
    objectives = {objective["id"] for objective in catalog["objectives"]}
    linked = {link["objective"] for link in evidence_map["links"]}
    for objective in sorted(objectives - linked):
        errors.append(f"objective-evidence-missing:{objective}")
    counts = {objective: 0 for objective in objectives}
    categories = set()
    for link in evidence_map["links"]:
        categories.add(link["category"])
        counts[link["objective"]] = counts.get(link["objective"], 0) + 1
        if link["objective"] not in objectives:
            errors.append(f"evidence-objective-unknown:{link['objective']}")
        if not link["independent"]:
            errors.append(f"evidence-not-independent:{link['ref']}")
        _, link_errors = resolve_evidence_link(link["ref"], forbidden)
        errors.extend(link_errors)
    for category in sorted(set(expected["required_evidence_categories"]) - categories):
        errors.append(f"evidence-category-missing:{category}")
    for objective, count in counts.items():
        if count < expected["minimum_links_per_objective"]:
            errors.append(f"objective-evidence-missing:{objective}")
    return errors


def report_evidence_errors(report, forbidden=None):
    forbidden = forbidden if forbidden is not None else forbidden_prefixes()
    errors = []
    for refs in report.get("evidence", {}).values():
        for ref in refs:
            _, link_errors = resolve_evidence_link(ref, forbidden)
            errors.extend(link_errors)
    return errors


def exception_claim_errors(report, exceptions):
    errors = []
    now = instant(report["evaluated_at"])
    records = {item["id"]: item for item in exceptions["exceptions"]}
    for exception_id in report["active_exceptions"]:
        exception = records.get(exception_id)
        if not exception:
            errors.append(f"exception-claim-stale:{exception_id}")
            continue
        if exception["status"] != "active" or instant(exception["expires_at"]) <= now:
            errors.append(f"exception-claim-expired:{exception_id}")
        if not exception.get("owner"):
            errors.append(f"exception-claim-unowned:{exception_id}")
    return errors


def telemetry_errors(events):
    chapter_13 = load_module("chapter-13")
    contract = load(ROOT / "detection/event-contract.yaml")
    rule = load(ROOT / "detection/rules/correlate-progression.yaml")
    _, gaps = chapter_13.normalize({"events": events["events"]}, contract, rule)
    return [
        f"telemetry-gap:{','.join([*gap.get('missing', []), *gap.get('invalid', [])])}"
        for gap in gaps
    ]


def attack_path_coverage_errors(changes, catalog):
    covered_layers = {
        layer
        for objective in catalog["objectives"]
        for layer in objective.get("covers", [])
    }
    excluded_layers = {
        layer
        for objective in catalog["objectives"]
        for layer in objective.get("does_not_cover", [])
    }
    controls = {objective["control"] for objective in catalog["objectives"]}
    errors = []
    for change in changes.get("changes", []):
        layer = change.get("layer")
        required = change["required_control"]
        distinct = change.get("distinct_from")
        uncovered = required not in controls
        if layer and (layer in excluded_layers or layer not in covered_layers):
            uncovered = True
        if distinct and distinct in controls and required != distinct:
            uncovered = True
        if uncovered:
            errors.append(f"attack-path-uncovered:{change['id']}")
    return errors


def affected_objectives(catalog, attack_path):
    return {
        objective["id"]
        for objective in catalog["objectives"]
        if attack_path in objective["attack_paths"]
    }


def material_change_errors(calendar, changes, report, catalog):
    errors = []
    evaluation = instant(report["evaluated_at"])
    for change in changes.get("changes", []):
        changed_at = instant(change["changed_at"])
        if changed_at > evaluation:
            continue
        affected = affected_objectives(catalog, change["attack_path"])
        matching = [
            trigger
            for trigger in calendar["material_change_triggers"]
            if set(trigger["requires_review"]) & affected
        ]
        if not any(instant(trigger["completed_at"]) >= changed_at for trigger in matching):
            errors.append(f"material-change-review-pending:{change['id']}")
    return errors


def calendar_errors(calendar, report, evidence_map):
    errors = []
    claim_time = instant(report["evaluated_at"])
    scheduled = instant(calendar["evaluation_time"])
    last_reviewed = instant(calendar["last_reviewed_at"])
    horizon = max(claim_time, scheduled)
    if (horizon - last_reviewed).days > calendar["cadence_days"]:
        errors.append("review-cadence-exceeded")
    freshness = calendar["evidence_freshness_days"]
    for link in evidence_map["links"]:
        age = (claim_time - instant(link["collected_at"])).days
        if age > freshness:
            errors.append(f"evidence-stale:{link['ref']}")
    for obligation in calendar["obligations"]:
        if instant(obligation["due_at"]) <= claim_time:
            errors.append(f"obligation-overdue:{obligation['id']}")
    return errors


def detection_errors():
    chapter_13 = load_module("chapter-13")
    contract, hypotheses, rule, events = chapter_13.inputs()
    normalized, gaps = chapter_13.normalize(events, contract, rule)
    alert = chapter_13.correlate(normalized, hypotheses["hypotheses"][0], rule)
    return gaps or ([] if alert["result"] == "alert" else ["priority-path-not-detected"])


def custody_errors():
    chapter_14 = load_module("chapter-14")
    manifest = load(ROOT / "response/evidence-manifest.yaml")
    return chapter_14.verify_manifest(manifest)


def recovery_errors():
    chapter_15 = load_module("chapter-15")
    specification = load(ROOT / "recovery/verification.yaml")
    report = load(ROOT / "build/chapter-15-recovery-verification.json")
    return chapter_15.verification_errors(specification, report)


def checklist_errors(report):
    return [
        f"checklist-criterion-false:{name}"
        for name, value in report["criteria"].items()
        if value is not True
    ]


def improvement_items(findings):
    items = []
    seen = set()
    for prefix, item in IMPROVEMENT_MAP:
        if any(str(finding).startswith(prefix) for finding in findings) and item["id"] not in seen:
            items.append(item)
            seen.add(item["id"])
    return items


def reopened_risk_record(changes, findings):
    risks = load(ROOT / "risk/risk-register.yaml")
    decisions = load(ROOT / "risk/control-decisions.yaml")
    path = changes["changes"][0]["attack_path"] if changes.get("changes") else None
    risk = next((item for item in risks["risks"] if item["attack_path"] == path), risks["risks"][0])
    decision = next(item for item in decisions["decisions"] if item["risk"] == risk["id"])
    return {
        "schema_version": 1,
        "kind": "risk-review-decision",
        "risk": risk["id"],
        "control_decision": decision["id"],
        "status": "reopened",
        "reopened_at": "2026-08-15T12:30:00Z",
        "reason": "post-incident-assurance-failure",
        "source": "build/chapter-16-assurance-failure.json",
        "findings": findings,
    }


def flatten(values):
    items = []
    for value in values:
        if isinstance(value, str):
            items.append(value)
        else:
            items.append(json.dumps(value, sort_keys=True))
    return items


def recompute_criteria(report, catalog, calendar, telemetry, changes):
    checks = {
        "exceptions_bounded": exception_claim_errors(
            report, load(ROOT / "policy/exceptions.yaml")
        ),
        "detection_covers_priority_paths": detection_errors(),
        "telemetry_complete_for_claimed_window": telemetry_errors(telemetry),
        "incident_evidence_custody_valid": custody_errors(),
        "recovery_claim_within_limits": recovery_errors(),
        "attack_path_register_current": attack_path_coverage_errors(changes, catalog),
        "material_change_review_complete": material_change_errors(
            calendar, changes, report, catalog
        ),
    }
    return {criterion: not findings for criterion, findings in checks.items()}, checks


def evaluate_assurance(
    report,
    catalog,
    evidence_map,
    calendar,
    telemetry,
    changes,
    *,
    permissive=False,
):
    if permissive:
        return checklist_errors(report)
    findings = []
    findings.extend(
        catalog_errors(
            catalog,
            load(ROOT / "risk/risk-register.yaml"),
            load(ROOT / "threat-model/attack-paths.yaml"),
        )
    )
    findings.extend(evidence_map_errors(catalog, evidence_map))
    findings.extend(report_evidence_errors(report))
    findings.extend(calendar_errors(calendar, report, evidence_map))
    criteria, checks = recompute_criteria(report, catalog, calendar, telemetry, changes)
    for values in checks.values():
        findings.extend(flatten(values))
    for criterion, actual in criteria.items():
        if report["criteria"].get(criterion) is not actual:
            findings.append(f"assurance-criterion-stale:{criterion}")
    if report["owner"] != catalog["owner"]:
        findings.append("owner-mismatch:assurance-report")
    if not report["limitations"]:
        findings.append("assurance-limitations-missing")
    if report["status"] == "pass" and findings:
        findings.insert(0, "assurance-theater:pass-with-failures")
    return findings
