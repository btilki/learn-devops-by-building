from evaluate import ROOT, evaluate_behavior, inputs, legitimate_errors, load, write

containment = ROOT / "build/chapter-12-containment.json"
if not containment.exists() or not load(containment)["isolated"]:
    raise SystemExit("run chapter-12-contain before recovery")
contract, policy = inputs()
deployment = load(ROOT / "supply-chain/deployment-evidence.yaml")
if contract["artifact_digest"] != deployment["artifact_digest"]:
    raise SystemExit("replacement artifact does not match admitted deployment")
if legitimate_errors(contract):
    raise SystemExit("legitimate replacement contract is unhealthy")
base = {
    "subject": contract["identity"],
    "claim_id": "replacement-claim-121",
    "deployment": "northwind-production/order-worker",
    "artifact_digest": contract["artifact_digest"],
}
observations = [
    {"type": "process", "resource": "order-worker"},
    {"type": "filesystem-write", "resource": "/tmp/order-worker/recovered-state"},
    *({"type": "egress", "resource": target} for target in contract["required_egress"]),
]
events = [evaluate_behavior({**base, **item}, contract, policy) for item in observations]
behavior_ok = all(event["outcome"] == "allowed" and not event["errors"] for event in events)
if not behavior_ok:
    raise SystemExit("post-replacement behavior violated the runtime contract")
record = {
    "kind": "runtime-recovery-evidence",
    "replacement_digest": contract["artifact_digest"],
    "identity": contract["identity"],
    "post_replacement_observations": events,
    "violation_count": sum(event["outcome"] != "allowed" for event in events),
    "legitimate_order_processing": "verified" if behavior_ok else "unverified",
    "monitoring": "active",
    "coverage_limit": "declared process, write, and required-egress observations only",
}
path = ROOT / "build/chapter-12-recovery.json"
write(path, record)
print(
    f"chapter 12 recovery: replacement observations allowed under active monitoring; record={path}"
)
