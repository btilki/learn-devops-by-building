from evaluate import decide, inputs, lifecycle_errors

classification, uses, policy, retention, lineage = inputs()
request = {
    "subject": "notification-service",
    "purpose": "send-order-confirmation",
    "fields": ["order_id", "customer_email", "order_total"],
    "store": "runtime-memory",
}
if decide(request, classification, uses, policy)["result"] != "allow":
    raise SystemExit("minimum notification use was denied")
errors = lifecycle_errors(classification, uses, policy, retention, lineage)
if errors or not retention["backup_constraint"]:
    raise SystemExit(errors or "backup deletion constraint missing")
print("chapter 10 checkpoint: use, store, lineage, and lifecycle contracts verified")
