from evaluate import evaluate_behavior, inputs, legitimate_errors

contract, policy = inputs()
errors = legitimate_errors(contract)
base = {
    "subject": "order-worker",
    "claim_id": "legitimate-claim",
    "deployment": "northwind-production/order-worker",
    "artifact_digest": contract["artifact_digest"],
}
observations = [
    {"type": "process", "resource": "order-worker"},
    {"type": "filesystem-write", "resource": "/tmp/order-worker/state"},
    *({"type": "egress", "resource": target} for target in contract["required_egress"]),
]
events = [evaluate_behavior({**base, **item}, contract, policy) for item in observations]
if any(event["outcome"] != "allowed" or event["errors"] for event in events):
    errors.append("legitimate-behavior-denied")
if errors:
    raise SystemExit(errors)
print("chapter 12 checkpoint: legitimate identity, privilege, filesystem, and egress verified")
