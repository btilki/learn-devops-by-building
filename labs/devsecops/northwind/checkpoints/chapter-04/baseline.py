from evaluate import authorize, start_state, trace_errors

s, r, t = start_state()
decision = authorize(
    "northwind-ci",
    {
        "issuer": "northwind-shared",
        "audience": "northwind-production",
        "lifetime_seconds": 86400,
        "reusable": True,
    },
    "reconcile-deployment",
    "northwind-production",
    "production",
    s,
    r,
    t,
    record=False,
)
if decision["result"] != "allow":
    raise SystemExit(f"baseline did not reproduce the unsafe start state: {decision}")
if not trace_errors(decision):
    raise SystemExit(f"baseline decision was unexpectedly attributable: {decision}")
print(
    "chapter 04 baseline: shared subject allowed unattributable production authority "
    "with a reusable day-long token"
)
