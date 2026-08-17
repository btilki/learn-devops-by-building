from evaluate import ROOT, authorize, evaluate, events, inputs, overlaps

inventory, policy, references = inputs()
errors = evaluate(inventory, policy, references)
secret = inventory["secrets"][0]
event_path = ROOT / "build/chapter-09-access-events.jsonl"
if event_path.exists():
    event_path.unlink()
result, use_errors = authorize(
    secret["id"], "payment-v2", "order-worker", "claim-920", inventory, policy, emit=True
)
if (
    errors
    or use_errors
    or result != "allow"
    or max(overlaps(secret), default=0) > policy["maximum_overlap_seconds"]
):
    raise SystemExit(errors or use_errors or "rotation overlap invalid")
event = events()[-1] if events() else {}
expected = (secret["id"], "payment-v2", "order-worker", "claim-920", "allow")
actual = tuple(event.get(key) for key in ["secret", "version", "subject", "claim_id", "result"])
if actual != expected:
    raise SystemExit("attributable use evidence does not match authorization")
print("chapter 09 checkpoint: reference-only use, bounded rotation, and attribution verified")
