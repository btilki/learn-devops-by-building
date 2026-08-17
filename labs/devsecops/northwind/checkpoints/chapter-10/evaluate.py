import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ORDER = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}


def load(path):
    return yaml.safe_load(path.read_text())


def inputs():
    base = ROOT / "data-security"
    return (
        load(base / "classification.yaml"),
        load(base / "uses.yaml"),
        load(base / "access-policy.yaml"),
        load(base / "retention.yaml"),
        load(base / "lineage.yaml"),
    )


def decide(request, classification, uses, policy):
    errors = []
    fields = {item["id"]: item for item in classification["fields"]}
    match = next(
        (
            item
            for item in uses["uses"]
            if item["subject"] == request.get("subject")
            and item["purpose"] == request.get("purpose")
        ),
        None,
    )
    if policy["require_subject"] and not request.get("subject"):
        errors.append("subject-missing")
    if policy["require_purpose"] and not request.get("purpose"):
        errors.append("purpose-missing")
    if not match:
        errors.append("use-undeclared")
    for field in request["fields"]:
        if field not in fields:
            errors.append(f"field-unknown:{field}")
        elif policy["deny_undeclared_fields"] and (not match or field not in match["fields"]):
            errors.append(f"field-not-permitted:{field}")
        limit = policy["store_class_limits"].get(request["store"])
        if not limit:
            errors.append(f"store-policy-missing:{request['store']}")
        if limit and field in fields and ORDER[fields[field]["class"]] > ORDER[limit]:
            errors.append(f"store-class-exceeded:{field}")
    if match and request["store"] not in match["stores"]:
        errors.append(f"store-not-permitted:{request['store']}")
    decision = {
        "kind": "data-access-decision",
        "subject": request.get("subject"),
        "purpose": request.get("purpose"),
        "fields": request["fields"],
        "store": request["store"],
        "classes": {
            field: fields[field]["class"] for field in request["fields"] if field in fields
        },
        "result": "deny" if errors else "allow",
        "reasons": errors,
    }
    return decision


def lifecycle_errors(classification, uses, policy, retention, lineage):
    errors = []
    fields = {item["id"] for item in classification["fields"]}
    stores = retention["stores"]
    for use in uses["uses"]:
        for store in use["stores"]:
            if store not in stores:
                errors.append(f"retention-missing:{store}")
            if store not in policy["store_class_limits"]:
                errors.append(f"store-policy-missing:{store}")
    for store, contract in stores.items():
        if not contract.get("deletion"):
            errors.append(f"deletion-missing:{store}")
        if store not in policy["store_class_limits"]:
            errors.append(f"store-policy-missing:{store}")
    for copy in lineage["copies"]:
        if copy["source"] not in stores or copy["target"] not in stores:
            errors.append(f"lineage-store-unknown:{copy['id']}")
        if copy["deletion_inherits"] != copy["target"]:
            errors.append(f"lineage-deletion-invalid:{copy['id']}")
        for field in copy["fields"]:
            if field not in fields:
                errors.append(f"lineage-field-unknown:{field}")
    return errors


def fixture_errors(fixture, classification, policy, exposed_values):
    errors = []
    fields = {item["id"]: item for item in classification["fields"]}
    limit = policy["store_class_limits"]["nonproduction"]
    for record in fixture["records"]:
        for field, value in record.items():
            if field not in fields:
                errors.append(f"fixture-field-unknown:{field}")
            elif ORDER[fields[field]["class"]] > ORDER[limit]:
                errors.append(f"fixture-class-exceeded:{field}")
            if value in exposed_values:
                errors.append(f"production-value-retained:{field}")
    return errors


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")
