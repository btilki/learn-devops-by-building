import json

from evaluate import ROOT, authorize, inputs, load

revocation_path = ROOT / "build/chapter-09-revocations.json"
provider_path = ROOT / "build/chapter-09-provider-compromised.yaml"
if not revocation_path.exists() or not provider_path.exists():
    raise SystemExit("run chapter-09-attack and chapter-09-contain before recovery")
revocation = load(revocation_path)
if not revocation["historical_access_inspected"] or not revocation["derived_credentials_replaced"]:
    raise SystemExit("containment scope is incomplete")
inventory, policy, _ = inputs()
pre_rotation = load(ROOT / "checkpoints/chapter-09/cases/pre-rotation-inventory.yaml")
old_result, old_errors = authorize(
    "payment-provider-credential", "payment-v1", "order-worker", "old-claim", pre_rotation, policy
)
new_result, errors = authorize(
    "payment-provider-credential", "payment-v2", "order-worker", "new-claim", inventory, policy
)
if old_result != "deny" or "version-revoked" not in old_errors or new_result != "allow" or errors:
    raise SystemExit("credential recovery authorization failed")
compromised = load(provider_path)
unauthorized = set(compromised["observed_effects"]) - set(compromised["expected_effects"])
if unauthorized != {"payment-order-9001-authorized"}:
    raise SystemExit("provider divergence was not detected")
provider = load(ROOT / "secrets/provider-state.yaml")
if (
    "payment-v1" in provider["accepted_versions"]
    or "payment-v2" not in provider["accepted_versions"]
):
    raise SystemExit("provider acceptance was not rotated")
if provider["service_health"] != "healthy":
    raise SystemExit("replacement credential did not preserve service health")
record = {
    "kind": "secret-recovery-evidence",
    "old_version_result": old_result,
    "old_version_reason": "version-revoked",
    "new_version_result": new_result,
    "unauthorized_effects": sorted(unauthorized),
    "corrective_effects": ["payment-order-9001-reversed"],
    "final_effects": provider["observed_effects"],
    "payment_effects_reconciled": provider["expected_effects"] == provider["observed_effects"],
    "service_health": provider["service_health"],
}
if not record["payment_effects_reconciled"]:
    raise SystemExit("payment effects are not reconciled")
output = ROOT / "build/chapter-09-recovery.json"
output.write_text(json.dumps(record, indent=2) + "\n")
print(f"chapter 09 recovery: replay denied; provider and health reconciled; record={output}")
