import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return yaml.safe_load(path.read_text())


def inputs():
    root = ROOT / "supply-chain"
    return (
        load(root / "provenance.yaml"),
        load(root / "build-policy.yaml"),
        load(root / "admission-policy.yaml"),
        load(root / "resolution-evidence.yaml"),
    )


def current_revocations():
    path = ROOT / "build/chapter-07-revocations.json"
    return load(path) if path.exists() else {}


def evaluate(provenance, build_policy, admission_policy, resolution, revocations=None):
    errors = []
    effective_revocations = current_revocations() if revocations is None else revocations
    revoked_builders = set(effective_revocations.get("builders", []))
    revoked_keys = set(effective_revocations.get("signing_keys", []))
    builder = provenance["builder"]
    if builder["id"] not in build_policy["trusted_builders"] or builder["id"] in revoked_builders:
        errors.append(f"builder-untrusted:{builder['id']}")
    if build_policy["require_isolation"] and not builder["isolated"]:
        errors.append(f"builder-not-isolated:{builder['id']}")
    if build_policy["require_hermetic"] and not builder["hermetic"]:
        errors.append(f"build-not-hermetic:{builder['id']}")
    for name, value in provenance["parameters"].items():
        if name not in build_policy["allowed_parameters"]:
            errors.append(f"parameter-unapproved:{name}")
        elif value not in build_policy["allowed_parameters"][name]:
            errors.append(f"parameter-value-unapproved:{name}")
    signature = provenance["signature"]
    if not signature["valid"]:
        errors.append("signature-invalid:artifact")
    if (
        signature["key_id"] not in build_policy["trusted_signing_keys"]
        or signature["key_id"] in revoked_keys
    ):
        errors.append(f"signing-key-untrusted:{signature['key_id']}")
    revision = resolution["source"]["revision"]
    if provenance["source"]["revision"] != revision:
        errors.append("source-decision-mismatch:revision")
    if provenance["dependency_resolution"] != resolution["resolution_id"]:
        errors.append("dependency-decision-mismatch:resolution-id")
    if admission_policy["require_sbom"] and not provenance.get("sbom_digest"):
        errors.append("sbom-missing:artifact")
    if admission_policy["require_transparency"] and not provenance.get("transparency_entry"):
        errors.append("transparency-missing:artifact")
    release = provenance["release"]
    if release["target"] not in admission_policy["allowed_targets"]:
        errors.append(f"target-unapproved:{release['target']}")
    independent = {x for x in release["approvers"] if x != release["requester"]}
    if len(independent) < admission_policy["minimum_independent_approvals"]:
        errors.append("release-approval-missing:artifact")
    return errors


def decision(provenance, policy, errors):
    return {
        "schema_version": 1,
        "kind": "release-admission-decision",
        "artifact_digest": provenance["artifact"]["digest"],
        "source_revision": provenance["source"]["revision"],
        "builder": provenance["builder"]["id"],
        "signing_key": provenance["signature"]["key_id"],
        "target": provenance["release"]["target"],
        "policy_version": policy["policy_version"],
        "result": "deny" if errors else "allow",
        "reasons": errors,
    }


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")
