import json

from evaluate import (
    COMPROMISED_DIGEST,
    ROOT,
    business_window_errors,
    cache_findings,
    inherited_interfaces,
    invalidated_digests,
    inventory_errors,
    load,
    load_module,
    qualifying_windows,
    rebuild_errors,
    verification_errors,
    write,
)
from jsonschema import Draft202012Validator

specification = load(ROOT / "recovery/verification.yaml")
inventory = load(ROOT / "build/chapter-15-trust-inventory.yaml")
manifest = load(ROOT / "recovery/rebuild-manifest.yaml")
eradication = load(ROOT / "build/chapter-15-eradication.json")
rebuild = load(ROOT / "build/chapter-15-rebuild.json")
cache = load(ROOT / "build/chapter-15-registry-cache-state.json")
provenance = load(ROOT / "supply-chain/provenance.yaml")
deployment = load(ROOT / "supply-chain/deployment-evidence.yaml")
contract = load(ROOT / "runtime/contracts/order-worker.yaml")
interfaces = inherited_interfaces()
windows = load(ROOT / "checkpoints/chapter-15/cases/business-outcome-windows.yaml")

chapter_12 = load_module("chapter-12", "evaluate")
runtime_event = chapter_12.evaluate_behavior(
    {
        "subject": "order-worker",
        "claim_id": "recovery-runtime-proof",
        "deployment": "northwind-production/order-worker",
        "artifact_digest": manifest["rebuilt_artifact_digest"],
        "type": "process",
        "resource": "order-worker",
    },
    contract,
    load(ROOT / "runtime/policies/behavior.yaml"),
)
credential_discovery = chapter_12.evaluate_behavior(
    {
        "subject": "order-worker",
        "claim_id": "recovery-secret-read-proof",
        "deployment": "northwind-production/order-worker",
        "artifact_digest": manifest["rebuilt_artifact_digest"],
        "type": "filesystem-read",
        "resource": "/var/run/secrets/payment-token",
    },
    contract,
    load(ROOT / "runtime/policies/behavior.yaml"),
)
chapter_13 = load_module("chapter-13", "evaluate")
event_contract, hypotheses, rule, events = chapter_13.inputs()
normalized, gaps = chapter_13.normalize(events, event_contract, rule)
alert = chapter_13.correlate(normalized, hypotheses["hypotheses"][0], rule)

chain_errors = rebuild_errors(
    manifest,
    provenance,
    deployment,
    contract,
    interfaces,
)
window_errors = business_window_errors(
    windows,
    specification["evidence_windows"]["minimum_consecutive"],
)
old_artifact_denied = (
    COMPROMISED_DIGEST in invalidated_digests(inventory)
    and not cache_findings(cache, invalidated_digests(inventory))
)
criteria = {
    "old_credentials_fail": (
        eradication["old_automation"]["result"] == "deny"
        and eradication["old_payment_credential"]["result"] == "deny"
        and eradication["replacement_payment_credential"]["result"] == "allow"
    ),
    "old_artifact_denied": old_artifact_denied,
    "rebuilt_chain_complete": not chain_errors and rebuild["admission"]["result"] == "allow",
    "persistence_absent_within_inventory": False,
    "detection_active": not gaps and alert["result"] == "alert",
    "business_reconciled": not window_errors,
}
runtime_root = next(root for root in inventory["roots"] if root["id"] == "order-worker-runtime")
runtime_root["status"] = "trusted"
runtime_root["derived_from"] = ["rebuilt-artifact", "payment-credential"]
scope_errors = inventory_errors(inventory)
criteria["persistence_absent_within_inventory"] = (
    eradication["cache_state"] == "invalidated"
    and eradication["old_automation"]["result"] == "deny"
    and not scope_errors
)
trust_restored = all(criteria.values())
qualified_window_ids = qualifying_windows(
    windows, specification["evidence_windows"]["minimum_consecutive"]
)
report = {
    "schema_version": 1,
    "kind": "recovery-verification",
    "case_id": specification["case_id"],
    "criteria": criteria,
    "evidence_windows": specification["evidence_windows"],
    "evidence": {
        "mechanism_evidence": [
            "build/chapter-15-eradication.json#old_automation",
            "build/chapter-15-eradication.json#old_payment_credential",
            "build/chapter-15-registry-cache-state.json#entries",
            "build/chapter-15-rebuild.json#admission",
        ],
        "decision_evidence": [
            "recovery/eradication-plan.yaml#actions",
            "build/chapter-15-eradication.json#release_path",
        ],
        "outcome_evidence": [
            "build/chapter-15-business-reconciliation.json#terminal_order_outcomes",
            "build/chapter-15-business-reconciliation.json#duplicate_payment_effects",
        ],
        "recovery_evidence": [
            f"build/chapter-15-rebuild.json#artifact_digest={manifest['rebuilt_artifact_digest']}",
            "build/chapter-13-alert.json#result",
            *[
                f"checkpoints/chapter-15/cases/business-outcome-windows.yaml#{window_id}"
                for window_id in qualified_window_ids
            ],
        ],
    },
    "limitations": specification["limitations"],
    "owner": specification["owner"],
    "trust_restored": trust_restored,
}
errors = verification_errors(specification, report)
if runtime_event["outcome"] != "allowed":
    errors.append("rebuilt-runtime-not-allowed")
if credential_discovery["outcome"] != "blocked":
    errors.append("recovered-secret-read-not-blocked")
errors.extend(scope_errors)
schema = json.loads(
    (ROOT / "schemas/recovery-verification.schema.json").read_text()
)
errors.extend(
    f"schema:{error.message}"
    for error in Draft202012Validator(schema).iter_errors(report)
)
if errors:
    raise SystemExit(errors)

contract["status"] = "active"
write(ROOT / "runtime/contracts/order-worker.yaml", contract)
points_path = ROOT / "policy/enforcement-points.yaml"
points = load(points_path)
production = next(item for item in points["points"] if item["id"] == "production-deploy")
production["status"] = "active"
write(points_path, points)
case_path = ROOT / "response/case/incident.yaml"
case = load(case_path)
case["status"] = "closed"
persistence_unknown = "whether another persistence path exists"
if persistence_unknown in case["unknowns"]:
    case["unknowns"].remove(persistence_unknown)
case["facts"].append(
    "modeled cache, automation, and exposed payment authority were replaced "
    "and recovery remained healthy"
)
write(case_path, case)
write(ROOT / "build/chapter-15-trust-inventory.yaml", inventory)
write(ROOT / "build/chapter-15-recovery-verification.json", report)
print("chapter 15 verify-recovery: trust restored within stated evidence limits")
