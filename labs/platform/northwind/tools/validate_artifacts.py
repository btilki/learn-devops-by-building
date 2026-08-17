from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

ARTIFACTS = {
    ROOT / "product" / "brief.yaml": ROOT / "schemas" / "product-brief.schema.json",
    ROOT / "product" / "users.yaml": ROOT / "schemas" / "owner.schema.json",
    ROOT / "product" / "jobs.yaml": ROOT / "schemas" / "user-job.schema.json",
    ROOT / "product" / "non-goals.yaml": ROOT / "schemas" / "non-goal.schema.json",
    ROOT / "intake" / "method.yaml": ROOT / "schemas" / "intake-method.schema.json",
    ROOT / "intake" / "candidates.yaml": ROOT / "schemas" / "intake-candidates.schema.json",
    ROOT / "intake" / "decisions.yaml": ROOT / "schemas" / "intake-decision.schema.json",
    ROOT / "tenancy" / "tenants.yaml": ROOT / "schemas" / "tenant.schema.json",
    ROOT / "tenancy" / "isolation.yaml": ROOT / "schemas" / "isolation-boundary.schema.json",
    ROOT / "tenancy" / "roles.yaml": ROOT / "schemas" / "tenancy-roles.schema.json",
    ROOT / "tenancy" / "sharing.yaml": ROOT / "schemas" / "tenancy-sharing.schema.json",
    ROOT / "catalog" / "systems.yaml": ROOT / "schemas" / "catalog-system.schema.json",
    ROOT / "catalog" / "ownership.yaml": ROOT / "schemas" / "catalog-ownership.schema.json",
    ROOT / "catalog" / "dependencies.yaml": ROOT / "schemas" / "catalog-dependencies.schema.json",
    ROOT / "paved-road" / "contract.yaml": ROOT / "schemas" / "paved-road-contract.schema.json",
    ROOT / "paved-road" / "scaffold.yaml": ROOT / "schemas" / "paved-road-scaffold.schema.json",
    ROOT
    / "paved-road"
    / "conformance.yaml": ROOT / "schemas" / "paved-road-conformance.schema.json",
    ROOT / "paved-road" / "exits.yaml": ROOT / "schemas" / "supported-exit.schema.json",
    ROOT / "environments" / "product.yaml": ROOT / "schemas" / "environment-product.schema.json",
    ROOT / "environments" / "requests.yaml": ROOT / "schemas" / "environment-request.schema.json",
    ROOT / "environments" / "leases.yaml": ROOT / "schemas" / "environment-lease.schema.json",
    ROOT / "contracts" / "catalog.yaml": ROOT / "schemas" / "infrastructure-catalog.schema.json",
    ROOT / "contracts" / "versions.yaml": ROOT / "schemas" / "infrastructure-contract.schema.json",
    ROOT
    / "contracts"
    / "compatibility.yaml": ROOT / "schemas" / "contract-compatibility.schema.json",
    ROOT
    / "control-plane"
    / "product.yaml": ROOT / "schemas" / "control-plane-product.schema.json",
    ROOT
    / "control-plane"
    / "subjects.yaml": ROOT / "schemas" / "control-plane-subject.schema.json",
    ROOT
    / "control-plane"
    / "admission.yaml": ROOT / "schemas" / "control-plane-admission.schema.json",
    ROOT
    / "control-plane"
    / "reconciliation.yaml": ROOT / "schemas" / "reconciliation-result.schema.json",
    ROOT / "guardrails" / "defaults.yaml": ROOT / "schemas" / "guardrail-default.schema.json",
    ROOT / "guardrails" / "scorecards.yaml": ROOT / "schemas" / "guardrail-scorecard.schema.json",
    ROOT / "guardrails" / "exceptions.yaml": ROOT / "schemas" / "exception-binding.schema.json",
    ROOT / "devex" / "contract.yaml": ROOT / "schemas" / "devex-contract.schema.json",
    ROOT / "devex" / "indicators.yaml": ROOT / "schemas" / "devex-indicator.schema.json",
    ROOT / "devex" / "non-metrics.yaml": ROOT / "schemas" / "devex-non-metrics.schema.json",
    ROOT / "devex" / "samples.yaml": ROOT / "schemas" / "devex-samples.schema.json",
    ROOT / "quota" / "tenants.yaml": ROOT / "schemas" / "quota-policy.schema.json",
    ROOT / "quota" / "units.yaml": ROOT / "schemas" / "quota-units.schema.json",
    ROOT / "quota" / "showback.yaml": ROOT / "schemas" / "quota-showback.schema.json",
    ROOT / "fleet" / "onboarding.yaml": ROOT / "schemas" / "fleet-onboarding.schema.json",
    ROOT / "fleet" / "upgrades.yaml": ROOT / "schemas" / "fleet-upgrades.schema.json",
    ROOT / "fleet" / "deprecations.yaml": ROOT / "schemas" / "fleet-deprecations.schema.json",
    ROOT / "fleet" / "migrations.yaml": ROOT / "schemas" / "fleet-migrations.schema.json",
    ROOT / "support" / "model.yaml": ROOT / "schemas" / "support-model.schema.json",
    ROOT / "support" / "escalation.yaml": ROOT / "schemas" / "support-escalation.schema.json",
    ROOT / "support" / "changes.yaml": ROOT / "schemas" / "support-changes.schema.json",
    ROOT / "support" / "incidents.yaml": ROOT / "schemas" / "support-incident.schema.json",
    ROOT
    / "recovery"
    / "plane-evidence.yaml": ROOT / "schemas" / "plane-recovery-evidence.schema.json",
    ROOT / "recovery" / "isolation.yaml": ROOT / "schemas" / "recovery-isolation.schema.json",
    ROOT / "recovery" / "restore-trace.yaml": ROOT / "schemas" / "restore-trace.schema.json",
    ROOT
    / "recovery"
    / "verification.yaml": ROOT / "schemas" / "recovery-verification.schema.json",
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
