from evaluate import ROOT, decide, inputs, load

classification, uses, policy, _, _ = inputs()
unsafe = load(ROOT / "checkpoints/chapter-10/cases/unsafe-request.yaml")
permissive = {
    **policy,
    "deny_undeclared_fields": False,
    "store_class_limits": {**policy["store_class_limits"], "telemetry": "restricted"},
}
expanded = {**uses, "uses": [{**uses["uses"][0], "stores": ["runtime-memory", "telemetry"]}]}
if decide(unsafe, classification, expanded, permissive)["result"] != "allow":
    raise SystemExit("permissive data-use baseline did not reproduce")
print("chapter 10 baseline: permissive purpose policy admitted payment data to telemetry")
