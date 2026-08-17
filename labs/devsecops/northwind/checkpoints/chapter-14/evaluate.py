import hashlib
import json
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return yaml.safe_load(path.read_text())


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_sources():
    return [
        ROOT / "build/chapter-13-alert.json",
        ROOT / "runtime/events.jsonl",
        ROOT / "identity/subjects.yaml",
        ROOT / "supply-chain/deployment-evidence.yaml",
        ROOT / "data-security/payment-reconciliation.yaml",
    ]


def collect_evidence(paths):
    collected = []
    evidence_root = ROOT / "response/evidence"
    if evidence_root.exists():
        shutil.rmtree(evidence_root)
    for source in paths:
        destination = evidence_root / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        collected.append(destination)
    return collected


def provenance(path):
    evidence_root = ROOT / "response/evidence"
    try:
        return str(path.relative_to(evidence_root))
    except ValueError:
        return str(path.relative_to(ROOT))


def manifest(paths):
    return {
        "schema_version": 1,
        "kind": "evidence-manifest",
        "case_id": "INC-2026-0815-01",
        "custodian": "security-response",
        "items": [
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": digest(path),
                "collected_at": "2026-08-15T10:20:00Z",
                "provenance": provenance(path),
            }
            for path in paths
        ],
    }


def verify_manifest(value):
    errors = []
    for item in value["items"]:
        path = ROOT / item["path"]
        if not path.exists():
            errors.append({"path": item["path"], "finding": "missing"})
        elif digest(path) != item["sha256"]:
            errors.append({"path": item["path"], "finding": "digest-mismatch"})
    return errors


def timeline(events):
    return sorted(events, key=lambda event: event["time"])


def containment_errors(plan):
    actions = sorted(plan["actions"], key=lambda action: action["order"])
    errors = []
    if actions[0]["id"] != "preserve-evidence":
        errors.append("mutation-before-preservation")
    required = {"revoke-session", "freeze-release", "isolate-workload", "preserve-business-state"}
    if not required.issubset({action["id"] for action in actions}):
        errors.append("containment-incomplete")
    order = {action["id"]: action["order"] for action in actions}
    if required.issubset(order) and order["preserve-business-state"] > order["isolate-workload"]:
        errors.append("business-state-preserved-after-isolation")
    if plan["service_mode"] != "bounded-intake":
        errors.append("business-continuity-unbounded")
    return errors


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".yaml":
        path.write_text(yaml.safe_dump(value, sort_keys=False))
    elif path.suffix == ".jsonl":
        path.write_text("".join(json.dumps(item) + "\n" for item in value))
    else:
        path.write_text(json.dumps(value, indent=2) + "\n")
