import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return yaml.safe_load(path.read_text())


def inputs():
    base = ROOT / "supply-chain"
    return (
        load(base / "resolution-evidence.yaml"),
        load(base / "source-policy.yaml"),
        load(base / "dependency-policy.yaml"),
        load(base / "lock.yaml"),
        load(base / "ownership.yaml"),
    )


def add(errors, code, subject="source"):
    errors.append(f"{code}:{subject}")


def evaluate(evidence, source_policy, dependency_policy, lock, ownership):
    errors = []
    if evidence.get("resolution_id") != resolution_id(evidence):
        add(errors, "resolution-id-mismatch")
    source = evidence["source"]
    if source["origin"] not in source_policy["trusted_origins"]:
        add(errors, "source-origin-untrusted")
    if source["ref"] not in source_policy["protected_refs"]:
        add(errors, "ref-unprotected")
    if dependency_policy["require_attributable_update"] and (
        not source.get("author") or not source.get("claim_id")
    ):
        add(errors, "update-unattributable")

    for path in source["changed_paths"]:
        matching = [
            prefix for prefix in source_policy["sensitive_paths"] if path.startswith(prefix)
        ]
        if not matching:
            continue
        independent = {x for x in source["approvers"] if x != source["author"]}
        if len(independent) < source_policy["minimum_independent_approvals"]:
            add(errors, "independent-review-missing", path)
        path_owners = {
            owner
            for prefix, owners in ownership["paths"].items()
            if path.startswith(prefix)
            for owner in owners
        }
        if not independent.intersection(path_owners):
            add(errors, "path-owner-approval-missing", path)

    locked_by_name = {item["name"]: item for item in lock["dependencies"]}
    registries = dependency_policy["registries"]
    for dependency in evidence["dependencies"]:
        name = dependency["name"]
        registry = dependency["registry"]
        if registry not in registries:
            add(errors, "registry-unapproved", name)
            add(errors, "namespace-unapproved", name)
        else:
            prefixes = registries[registry]["allowed_namespaces"]
            if not any(name.startswith(prefix) for prefix in prefixes):
                add(errors, "namespace-unapproved", name)

        expected = locked_by_name.get(name)
        if not expected:
            add(errors, "dependency-unknown", name)
            continue
        if dependency["resolved"] != expected["version"]:
            add(errors, "version-drift", name)
        if dependency_policy["require_lock_hash"] and dependency["sha256"] != expected["sha256"]:
            add(errors, "hash-mismatch", name)
        if registry != expected["registry"]:
            add(errors, "locked-registry-mismatch", name)
    return errors


def decision(evidence, errors):
    return {
        "schema_version": 1,
        "kind": "supply-chain-admission-decision",
        "revision": evidence["source"]["revision"],
        "resolution_id": resolution_id(evidence),
        "author": evidence["source"].get("author"),
        "claim_id": evidence["source"].get("claim_id"),
        "approvers": evidence["source"]["approvers"],
        "dependencies": evidence["dependencies"],
        "result": "deny" if errors else "allow",
        "reasons": errors,
    }


def resolution_id(evidence):
    material = {
        "source": evidence["source"],
        "dependencies": evidence["dependencies"],
    }
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")
