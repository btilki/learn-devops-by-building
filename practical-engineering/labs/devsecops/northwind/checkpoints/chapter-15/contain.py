from evaluate import (
    ROOT,
    cache_findings,
    invalidate_cache,
    invalidated_digests,
    load,
    load_module,
    write,
)

inventory = load(ROOT / "recovery/trust-inventory.yaml")
plan = load(ROOT / "recovery/eradication-plan.yaml")
attack = load(ROOT / "build/chapter-15-persistence-attempt.json")
chapter_14 = load_module("chapter-14", "evaluate")
if chapter_14.verify_manifest(load(ROOT / "response/evidence-manifest.yaml")):
    raise SystemExit("preserved Chapter 14 evidence failed custody verification")
if plan["reconciliation"] != "paused" or not attack["findings"]:
    raise SystemExit("persistence containment prerequisites missing")

rotation = load(
    ROOT / "checkpoints/chapter-15/cases/missed-release-workflow-credential.yaml"
)
subjects_path = ROOT / "identity/subjects.yaml"
subjects = load(subjects_path)
old = next(item for item in subjects["subjects"] if item["id"] == rotation["old_subject"])
old["status"] = "revoked"
subjects["subjects"] = [
    item
    for item in subjects["subjects"]
    if item["id"] != rotation["replacement_subject"]["id"]
]
subjects["subjects"].append(rotation["replacement_subject"])
write(subjects_path, subjects)

cache = load(ROOT / "checkpoints/chapter-15/cases/persistence-cache-redeploy.yaml")
invalidated = invalidated_digests(inventory)
contained_cache = invalidate_cache(cache, invalidated)
if cache_findings(contained_cache, invalidated):
    raise SystemExit("invalidated cache remained servable")
write(ROOT / "build/chapter-15-registry-cache-state.json", contained_cache)
release_root = next(root for root in inventory["roots"] if root["id"] == "release-automation")
release_root["status"] = "replaced"
release_root["invalidation_reason"] = "missed-automation-persistence-path"
release_root["replacement"] = rotation["replacement_subject"]["id"]
cache_root = next(root for root in inventory["roots"] if root["id"] == "registry-cache")
cache_root["status"] = "invalidated"
cache_root["invalidation_reason"] = "retained-compromised-artifact"

chapter_09 = load_module("chapter-09", "evaluate")
secret_inventory_path = ROOT / "secrets/inventory.yaml"
secret_inventory = load(secret_inventory_path)
payment = next(
    secret
    for secret in secret_inventory["secrets"]
    if secret["id"] == "payment-provider-credential"
)
payment_v2 = next(version for version in payment["versions"] if version["id"] == "payment-v2")
payment_v2["status"] = "retired"
payment_v2["retired_at"] = "2026-08-15T10:40:00Z"
payment["versions"] = [
    version for version in payment["versions"] if version["id"] != "payment-v3"
]
payment["versions"].append(
    {
        "id": "payment-v3",
        "status": "active",
        "issued_at": "2026-08-15T10:35:00Z",
        "retire_by": "2026-09-15T00:00:00Z",
    }
)
payment_policy = load(ROOT / "secrets/policy.yaml")
payment_revocations = {"versions": ["payment-v2"]}
old_payment_result, old_payment_errors = chapter_09.authorize(
    "payment-provider-credential",
    "payment-v2",
    "order-worker",
    "recovery-old-payment",
    secret_inventory,
    payment_policy,
    payment_revocations,
)
new_payment_result, new_payment_errors = chapter_09.authorize(
    "payment-provider-credential",
    "payment-v3",
    "order-worker",
    "recovery-new-payment",
    secret_inventory,
    payment_policy,
    payment_revocations,
)
if (
    old_payment_result != "deny"
    or "version-revoked" not in old_payment_errors
    or new_payment_result != "allow"
    or new_payment_errors
):
    raise SystemExit(
        {
            "old-payment": [old_payment_result, old_payment_errors],
            "new-payment": [new_payment_result, new_payment_errors],
        }
    )
write(secret_inventory_path, secret_inventory)
references_path = ROOT / "secrets/references.yaml"
references = load(references_path)
payment_reference = next(
    reference
    for reference in references["references"]
    if reference["secret"] == "payment-provider-credential"
)
payment_reference["version"] = "payment-v3"
payment_reference["reference"] = "secret://payments/payment-provider-credential/payment-v3"
write(references_path, references)
provider_path = ROOT / "secrets/provider-state.yaml"
provider = load(provider_path)
provider["accepted_versions"] = ["payment-v3"]
write(provider_path, provider)
payment_root = next(root for root in inventory["roots"] if root["id"] == "payment-credential")
payment_root["status"] = "replaced"
payment_root["invalidation_reason"] = "runtime-credential-discovery-observed"
payment_root["replacement"] = "payment-v3"
write(ROOT / "build/chapter-15-trust-inventory.yaml", inventory)

chapter_04 = load_module("chapter-04", "evaluate")
subjects = load(subjects_path)
roles = load(ROOT / "identity/roles.yaml")
trust = load(ROOT / "identity/trust-policy.yaml")
old_decision = chapter_04.authorize(
    rotation["old_subject"],
    rotation["claims"]["old"],
    "publish-artifact",
    "northwind-registry",
    "build",
    subjects,
    roles,
    trust,
    record=False,
)
replacement_decision = chapter_04.authorize(
    rotation["replacement_subject"]["id"],
    rotation["claims"]["replacement"],
    "publish-artifact",
    "northwind-registry",
    "build",
    subjects,
    roles,
    trust,
    record=False,
)
points = load(ROOT / "policy/enforcement-points.yaml")
production = next(item for item in points["points"] if item["id"] == "production-deploy")
if (
    old_decision["result"] != "deny"
    or replacement_decision["result"] != "allow"
    or production["status"] != "frozen"
):
    raise SystemExit(
        {
            "old": old_decision,
            "replacement": replacement_decision,
            "production": production,
        }
    )
record = {
    "schema_version": 1,
    "kind": "persistence-eradication",
    "case_id": inventory["case_id"],
    "reconciliation": "paused",
    "old_automation": old_decision,
    "replacement_automation": replacement_decision,
    "cache_state": contained_cache["state"],
    "old_payment_credential": {
        "version": "payment-v2",
        "result": old_payment_result,
        "reasons": old_payment_errors,
    },
    "replacement_payment_credential": {
        "version": "payment-v3",
        "result": new_payment_result,
        "reasons": new_payment_errors,
    },
    "release_path": "frozen",
    "trust_restored": False,
}
write(ROOT / "build/chapter-15-eradication.json", record)
print("chapter 15 containment: missed automation revoked and invalidated cache purged")
