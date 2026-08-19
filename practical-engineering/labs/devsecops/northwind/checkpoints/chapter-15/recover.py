from evaluate import (
    ROOT,
    business_window_errors,
    inherited_interfaces,
    load,
    load_module,
    qualifying_windows,
    rebuild_errors,
    write,
)

eradication = load(ROOT / "build/chapter-15-eradication.json")
if (
    eradication["cache_state"] != "invalidated"
    or eradication["old_automation"]["result"] != "deny"
):
    raise SystemExit("eradication must complete before trusted rebuild")

manifest = load(ROOT / "recovery/rebuild-manifest.yaml")
provenance = load(
    ROOT / "checkpoints/chapter-15/cases/trusted-rebuild-provenance.yaml"
)
chapter_07 = load_module("chapter-07", "evaluate")
_, build_policy, admission_policy, resolution = chapter_07.inputs()
admission_errors = chapter_07.evaluate(
    provenance,
    build_policy,
    admission_policy,
    resolution,
    chapter_07.current_revocations(),
)
if admission_errors:
    raise SystemExit({"trusted-rebuild-admission": admission_errors})

deployment = load(ROOT / "supply-chain/deployment-evidence.yaml")
deployment["artifact_digest"] = manifest["rebuilt_artifact_digest"]
deployment["admission_result"] = "allow"
deployment["policy_version"] = admission_policy["policy_version"]

contract = load(ROOT / "checkpoints/chapter-12/cases/order-worker-contract.yaml")
contract["status"] = "recovery-validation"
contract["artifact_digest"] = manifest["rebuilt_artifact_digest"]

interfaces = inherited_interfaces()
chain_errors = rebuild_errors(
    manifest,
    provenance,
    deployment,
    contract,
    interfaces,
)
windows = load(ROOT / "checkpoints/chapter-15/cases/business-outcome-windows.yaml")
minimum_windows = load(ROOT / "recovery/verification.yaml")["evidence_windows"][
    "minimum_consecutive"
]
window_errors = business_window_errors(
    windows,
    minimum_windows,
)
if chain_errors or window_errors:
    raise SystemExit({"rebuild": chain_errors, "business": window_errors})

write(ROOT / "supply-chain/provenance.yaml", provenance)
write(ROOT / "supply-chain/deployment-evidence.yaml", deployment)
write(ROOT / "runtime/contracts/order-worker.yaml", contract)
runtime_policy_path = ROOT / "runtime/policies/behavior.yaml"
runtime_policy = load(runtime_policy_path)
runtime_policy["policy_version"] = "runtime-v2-recovery"
runtime_policy["actions"]["credential-discovery"] = "prevent"
write(runtime_policy_path, runtime_policy)
payment_path = ROOT / "data-security/payment-reconciliation.yaml"
payment = load(payment_path)
payment["recovery_reconciliation"] = {
    "terminal_order_outcomes": True,
    "duplicate_payment_effects": 0,
    "windows": qualifying_windows(windows, minimum_windows),
}
write(payment_path, payment)
record = {
    "schema_version": 1,
    "kind": "trusted-rebuild",
    "case_id": manifest["case_id"],
    "artifact_digest": manifest["rebuilt_artifact_digest"],
    "admission": chapter_07.decision(provenance, admission_policy, admission_errors),
    "required_roots": manifest["required_roots"],
    "desired_actual_agreement": True,
    "business_window_ids": qualifying_windows(windows, minimum_windows),
    "runtime_policy_version": runtime_policy["policy_version"],
    "service_state": "recovery-validation",
    "trust_restored": False,
}
write(ROOT / "build/chapter-15-rebuild.json", record)
write(
    ROOT / "build/chapter-15-business-reconciliation.json",
    payment["recovery_reconciliation"],
)
print("chapter 15 recovery: trusted rebuild admitted and business state reconciled")
