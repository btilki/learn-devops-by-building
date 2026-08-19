import yaml
from evaluate import ROOT, authorize, inputs, load

_, policy, _ = inputs()
inventory = load(ROOT / "checkpoints/chapter-09/cases/pre-rotation-inventory.yaml")
exposure = load(ROOT / "checkpoints/chapter-09/cases/exposure.yaml")
result, errors = authorize(
    exposure["secret"],
    exposure["version"],
    exposure["subject"],
    exposure["claim_id"],
    inventory,
    policy,
    {},
)
if result != "allow" or errors:
    raise SystemExit(errors)
path = ROOT / "build/chapter-09-exposure.yaml"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(yaml.safe_dump(exposure, sort_keys=False))
provider = load(ROOT / "secrets/provider-state.yaml")
provider["observed_effects"].append("payment-order-9001-authorized")
provider["accepted_versions"] = ["payment-v1", "payment-v2"]
provider["service_health"] = "degraded-security"
provider_path = ROOT / "build/chapter-09-provider-compromised.yaml"
provider_path.write_text(yaml.safe_dump(provider, sort_keys=False))
print(f"chapter 09 attack: replay created unauthorized provider effect; evidence={path}")
