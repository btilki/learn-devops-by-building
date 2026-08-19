from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

ARTIFACTS = {
    ROOT / "security-model" / "assets.yaml": ROOT / "schemas" / "asset.schema.json",
    ROOT / "security-model" / "ownership.yaml": ROOT / "schemas" / "ownership.schema.json",
    ROOT / "security-model" / "invariants.yaml": (
        ROOT / "schemas" / "security-invariant.schema.json"
    ),
    ROOT / "threat-model" / "system.yaml": ROOT / "schemas" / "system-flow.schema.json",
    ROOT / "threat-model" / "boundaries.yaml": (ROOT / "schemas" / "trust-boundary.schema.json"),
    ROOT / "threat-model" / "attack-paths.yaml": (ROOT / "schemas" / "attack-path.schema.json"),
    ROOT / "risk" / "risk-register.yaml": ROOT / "schemas" / "risk-decision.schema.json",
    ROOT / "risk" / "control-decisions.yaml": ROOT / "schemas" / "control.schema.json",
    ROOT / "identity" / "subjects.yaml": ROOT / "schemas" / "identity-subject.schema.json",
    ROOT / "identity" / "roles.yaml": ROOT / "schemas" / "authorization-policy.schema.json",
    ROOT / "identity" / "trust-policy.yaml": ROOT / "schemas" / "identity-trust.schema.json",
    ROOT / "privilege" / "requests" / "approved.yaml": (
        ROOT / "schemas" / "privilege-request.schema.json"
    ),
    ROOT / "privilege" / "policy.yaml": (
        ROOT / "schemas" / "privileged-access-policy.schema.json"
    ),
    ROOT / "supply-chain" / "source-policy.yaml": (ROOT / "schemas" / "source-policy.schema.json"),
    ROOT / "supply-chain" / "dependency-policy.yaml": (
        ROOT / "schemas" / "dependency-policy.schema.json"
    ),
    ROOT / "supply-chain" / "ownership.yaml": (ROOT / "schemas" / "source-ownership.schema.json"),
    ROOT / "supply-chain" / "lock.yaml": ROOT / "schemas" / "dependency-lock.schema.json",
    ROOT / "supply-chain" / "resolution-evidence.yaml": (
        ROOT / "schemas" / "dependency-resolution.schema.json"
    ),
    ROOT / "supply-chain" / "build-policy.yaml": ROOT / "schemas" / "build-policy.schema.json",
    ROOT / "supply-chain" / "admission-policy.yaml": (
        ROOT / "schemas" / "admission-policy.schema.json"
    ),
    ROOT / "supply-chain" / "provenance.yaml": ROOT / "schemas" / "provenance.schema.json",
    ROOT / "supply-chain" / "deployment-evidence.yaml": (
        ROOT / "schemas" / "deployment-evidence.schema.json"
    ),
    ROOT / "vulnerabilities" / "findings" / "normalized.yaml": (
        ROOT / "schemas" / "finding.schema.json"
    ),
    ROOT / "vulnerabilities" / "findings" / "raw.yaml": (
        ROOT / "schemas" / "raw-finding.schema.json"
    ),
    ROOT / "vulnerabilities" / "policy.yaml": (
        ROOT / "schemas" / "vulnerability-policy.schema.json"
    ),
    ROOT / "vulnerabilities" / "decisions.yaml": (
        ROOT / "schemas" / "vulnerability-decision.schema.json"
    ),
    ROOT / "vulnerabilities" / "exceptions.yaml": (ROOT / "schemas" / "exception.schema.json"),
    ROOT / "secrets" / "inventory.yaml": ROOT / "schemas" / "secret-record.schema.json",
    ROOT / "secrets" / "policy.yaml": ROOT / "schemas" / "secret-policy.schema.json",
    ROOT / "secrets" / "references.yaml": ROOT / "schemas" / "secret-reference.schema.json",
    ROOT / "data-security" / "classification.yaml": ROOT / "schemas" / "data-class.schema.json",
    ROOT / "data-security" / "uses.yaml": ROOT / "schemas" / "data-use.schema.json",
    ROOT / "data-security" / "access-policy.yaml": ROOT / "schemas" / "data-access.schema.json",
    ROOT / "data-security" / "retention.yaml": ROOT / "schemas" / "data-retention.schema.json",
    ROOT / "data-security" / "lineage.yaml": ROOT / "schemas" / "data-lineage.schema.json",
    ROOT / "policy" / "bundle" / "rules.yaml": ROOT / "schemas" / "policy-bundle.schema.json",
    ROOT / "policy" / "enforcement-points.yaml": ROOT / "schemas" / "enforcement-point.schema.json",
    ROOT / "policy" / "exceptions.yaml": ROOT / "schemas" / "policy-exception.schema.json",
    ROOT / "policy" / "exception-policy.yaml": (
        ROOT / "schemas" / "exception-governance.schema.json"
    ),
    ROOT / "runtime" / "contracts" / "order-worker.yaml": (
        ROOT / "schemas" / "runtime-contract.schema.json"
    ),
    ROOT / "runtime" / "policies" / "behavior.yaml": (
        ROOT / "schemas" / "runtime-policy.schema.json"
    ),
    ROOT / "detection" / "event-contract.yaml": ROOT / "schemas" / "security-event.schema.json",
    ROOT / "detection" / "hypotheses.yaml": (ROOT / "schemas" / "detection-hypothesis.schema.json"),
    ROOT / "detection" / "rules" / "correlate-progression.yaml": (
        ROOT / "schemas" / "detection-rule.schema.json"
    ),
    ROOT / "response" / "case" / "incident.yaml": ROOT / "schemas" / "incident-case.schema.json",
    ROOT / "response" / "containment-plan.yaml": ROOT / "schemas" / "containment-plan.schema.json",
    ROOT / "recovery" / "trust-inventory.yaml": ROOT / "schemas" / "trust-inventory.schema.json",
    ROOT / "recovery" / "eradication-plan.yaml": ROOT / "schemas" / "eradication-plan.schema.json",
    ROOT / "recovery" / "rebuild-manifest.yaml": ROOT / "schemas" / "rebuild-manifest.schema.json",
    ROOT / "recovery" / "verification.yaml": (
        ROOT / "schemas" / "recovery-verification.schema.json"
    ),
    ROOT / "governance" / "control-catalog.yaml": (
        ROOT / "schemas" / "control-catalog.schema.json"
    ),
    ROOT / "governance" / "evidence-map.yaml": ROOT / "schemas" / "evidence-map.schema.json",
    ROOT / "governance" / "review-calendar.yaml": (
        ROOT / "schemas" / "review-calendar.schema.json"
    ),
    ROOT / "governance" / "assurance-report.yaml": (
        ROOT / "schemas" / "assurance-claim.schema.json"
    ),
}


def load_yaml(path: Path) -> object:
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def validate() -> None:
    for artifact_path, schema_path in ARTIFACTS.items():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(load_yaml(artifact_path))


if __name__ == "__main__":
    validate()
    print("artifact validation: passed")
