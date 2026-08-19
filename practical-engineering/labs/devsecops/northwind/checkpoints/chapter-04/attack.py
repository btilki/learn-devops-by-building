from evaluate import authorize, inputs, read_events, trace_errors

s, r, t = inputs()
result = authorize(
    "compromised-session",
    {
        "claim_id": "attack-claim-001",
        "issuer": "northwind-human-idp",
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
)
required = {
    "audience-rejected",
    "session-too-long",
    "reusable-token-rejected",
    "authorization-denied",
}
if result["result"] != "deny" or not required.issubset(result["reasons"]):
    raise SystemExit(result)
event = read_events(1)[0]
errors = trace_errors(event)
if errors or event["subject"] != "compromised-session":
    raise SystemExit({"unattributable denial": errors, "event": event})
print("chapter 04 attack: compromised reusable session denied and attributed")
