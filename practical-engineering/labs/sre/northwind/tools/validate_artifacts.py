from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

ARTIFACTS = {
    ROOT / "reliability" / "brief.yaml": ROOT / "schemas" / "reliability-brief.schema.json",
    ROOT / "reliability" / "owners.yaml": ROOT / "schemas" / "owner.schema.json",
    ROOT / "reliability" / "journeys.yaml": ROOT / "schemas" / "user-journey.schema.json",
    ROOT / "reliability" / "refusals.yaml": ROOT / "schemas" / "reliability-refusal.schema.json",
    ROOT / "slis" / "method.yaml": ROOT / "schemas" / "sli-method.schema.json",
    ROOT / "slis" / "candidates.yaml": ROOT / "schemas" / "sli-candidates.schema.json",
    ROOT / "slis" / "decisions.yaml": ROOT / "schemas" / "sli-decision.schema.json",
    ROOT / "slos" / "catalog.yaml": ROOT / "schemas" / "slo.schema.json",
    ROOT / "slos" / "windows.yaml": ROOT / "schemas" / "slo-windows.schema.json",
    ROOT / "slos" / "budgets.yaml": ROOT / "schemas" / "error-budget.schema.json",
    ROOT / "policy" / "error-budget.yaml": ROOT / "schemas" / "error-budget-policy.schema.json",
    ROOT / "policy" / "actions.yaml": ROOT / "schemas" / "error-budget-actions.schema.json",
    ROOT / "policy" / "exceptions.yaml": ROOT / "schemas" / "error-budget-exception.schema.json",
    ROOT / "alerting" / "burns.yaml": ROOT / "schemas" / "burn-alert.schema.json",
    ROOT / "alerting" / "pages.yaml": ROOT / "schemas" / "burn-pages.schema.json",
    ROOT / "alerting" / "tickets.yaml": ROOT / "schemas" / "burn-tickets.schema.json",
    ROOT / "oncall" / "system.yaml": ROOT / "schemas" / "oncall-system.schema.json",
    ROOT / "oncall" / "rotations.yaml": ROOT / "schemas" / "oncall-rotations.schema.json",
    ROOT / "oncall" / "handoffs.yaml": ROOT / "schemas" / "oncall-handoffs.schema.json",
    ROOT / "oncall" / "authority.yaml": ROOT / "schemas" / "oncall-authority.schema.json",
    ROOT / "toil" / "definition.yaml": ROOT / "schemas" / "toil-definition.schema.json",
    ROOT / "toil" / "inventory.yaml": ROOT / "schemas" / "toil-inventory.schema.json",
    ROOT / "toil" / "bounds.yaml": ROOT / "schemas" / "toil-bound.schema.json",
    ROOT / "dependencies" / "catalog.yaml": ROOT / "schemas" / "dependency-catalog.schema.json",
    ROOT / "dependencies" / "criticality.yaml": (
        ROOT / "schemas" / "dependency-criticality.schema.json"
    ),
    ROOT / "dependencies" / "contracts.yaml": ROOT / "schemas" / "dependency-contract.schema.json",
    ROOT / "degradation" / "modes.yaml": ROOT / "schemas" / "degradation-modes.schema.json",
    ROOT / "degradation" / "shedding.yaml": ROOT / "schemas" / "degradation-shedding.schema.json",
    ROOT / "degradation" / "cascade.yaml": ROOT / "schemas" / "degradation-policy.schema.json",
    ROOT / "incidents" / "command.yaml": ROOT / "schemas" / "incident-command.schema.json",
    ROOT / "incidents" / "roles.yaml": ROOT / "schemas" / "incident-roles.schema.json",
    ROOT / "incidents" / "traces.yaml": ROOT / "schemas" / "portfolio-incident.schema.json",
    ROOT / "learning" / "program.yaml": ROOT / "schemas" / "learning-program.schema.json",
    ROOT / "learning" / "records.yaml": ROOT / "schemas" / "learning-records.schema.json",
    ROOT / "learning" / "actions.yaml": ROOT / "schemas" / "learning-action.schema.json",
    ROOT / "regions" / "architecture.yaml": (
        ROOT / "schemas" / "regional-architecture.schema.json"
    ),
    ROOT / "regions" / "objectives.yaml": ROOT / "schemas" / "regional-objectives.schema.json",
    ROOT / "regions" / "constraints.yaml": ROOT / "schemas" / "regional-constraints.schema.json",
    ROOT / "gamedays" / "program.yaml": ROOT / "schemas" / "gameday-program.schema.json",
    ROOT / "gamedays" / "scenarios.yaml": ROOT / "schemas" / "gameday-scenarios.schema.json",
    ROOT / "gamedays" / "results.yaml": ROOT / "schemas" / "gameday-results.schema.json",
    ROOT / "failover" / "plan.yaml": ROOT / "schemas" / "portfolio-failover.schema.json",
    ROOT / "failover" / "trace.yaml": ROOT / "schemas" / "failover-trace.schema.json",
    ROOT / "failover" / "isolation.yaml": (
        ROOT / "schemas" / "failover-isolation.schema.json"
    ),
    ROOT / "failover" / "verification.yaml": (
        ROOT / "schemas" / "failover-verification.schema.json"
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
