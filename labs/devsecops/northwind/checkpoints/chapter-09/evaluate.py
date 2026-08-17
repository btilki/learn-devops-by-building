import json
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return yaml.safe_load(path.read_text())


def inputs():
    base = ROOT / "secrets"
    return load(base / "inventory.yaml"), load(base / "policy.yaml"), load(base / "references.yaml")


def baseline_inputs():
    cases = ROOT / "checkpoints/chapter-09/cases"
    return (
        load(cases / "recovered-inventory.yaml"),
        load(ROOT / "secrets/policy.yaml"),
        load(cases / "recovered-references.yaml"),
    )


def revocations():
    path = ROOT / "build/chapter-09-revocations.json"
    return load(path) if path.exists() else {"versions": []}


def evaluate(inventory, policy, references):
    errors = []
    records = {item["id"]: item for item in inventory["secrets"]}
    for secret in inventory["secrets"]:
        if policy["require_owner"] and not secret.get("owner"):
            errors.append(f"owner-missing:{secret['id']}")
        if secret["storage"] not in policy["approved_storage"]:
            errors.append(f"storage-unapproved:{secret['id']}")
        if len([version for version in secret["versions"] if version["status"] == "active"]) != 1:
            errors.append(f"active-version-invalid:{secret['id']}")
        if secret.get("exception") not in [None, *policy["allowed_exceptions"]]:
            errors.append(f"exception-unapproved:{secret['id']}")
    for reference in references["references"]:
        secret_id = reference["secret"]
        if secret_id not in records:
            errors.append(f"secret-unknown:{secret_id}")
            continue
        value = reference.get("value")
        if value in policy["plaintext_markers"]:
            errors.append(f"known-plaintext-marker:{secret_id}")
        if policy["require_reference_only"] and (value or not reference.get("reference")):
            errors.append(f"plaintext-reference:{secret_id}")
        versions = {item["id"]: item for item in records[secret_id]["versions"]}
        selected = versions.get(reference["version"])
        if not selected:
            errors.append(f"version-unknown:{reference['version']}")
        elif selected["status"] != "active":
            errors.append(f"version-{selected['status']}:{reference['version']}")
    return errors


def emit_event(secret_id, version, subject, claim_id, result, errors):
    path = ROOT / "build/chapter-09-access-events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "event": "secret-use",
        "secret": secret_id,
        "version": version,
        "subject": subject,
        "claim_id": claim_id,
        "purpose": "authorize-payment-provider-api",
        "result": result,
        "reasons": errors,
        "at": "2026-08-15T10:25:00Z",
    }
    with path.open("a") as stream:
        stream.write(json.dumps(event) + "\n")


def authorize(
    secret_id,
    version,
    subject,
    claim_id,
    inventory,
    policy,
    revocation_state=None,
    emit=False,
):
    record = next((item for item in inventory["secrets"] if item["id"] == secret_id), None)
    errors = []
    if not record:
        errors.append("secret-unknown")
    else:
        item = next((entry for entry in record["versions"] if entry["id"] == version), None)
        effective = revocations() if revocation_state is None else revocation_state
        if not item:
            errors.append("version-unknown")
        elif version in effective.get("versions", []):
            errors.append("version-revoked")
        elif item["status"] != "active":
            errors.append(f"version-{item['status']}")
        if subject not in record["consumers"]:
            errors.append("consumer-unapproved")
    if policy["require_attributable_use"] and not claim_id:
        errors.append("use-unattributable")
    result = "deny" if errors else "allow"
    if emit:
        emit_event(secret_id, version, subject, claim_id, result, errors)
    return result, errors


def events():
    path = ROOT / "build/chapter-09-access-events.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def overlaps(secret):
    versions = sorted(secret["versions"], key=lambda item: item["issued_at"])
    values = []
    for old, new in zip(versions, versions[1:]):
        if not old.get("retired_at"):
            continue
        retired = datetime.fromisoformat(old["retired_at"].replace("Z", "+00:00"))
        issued = datetime.fromisoformat(new["issued_at"].replace("Z", "+00:00"))
        values.append(max(0, int((retired - issued).total_seconds())))
    return values
