from evaluate import authorize, inputs, read_events, trace_errors

s, r, t = inputs()
cases = [
    (
        "maintainer-alice",
        {"issuer": "northwind-human-idp", "audience": "northwind-source", "lifetime_seconds": 1800},
        "propose-change",
        "northwind-source",
        "repository",
        "allow",
    ),
    (
        "release-workflow",
        {"issuer": "northwind-oidc", "audience": "northwind-registry", "lifetime_seconds": 600},
        "publish-artifact",
        "northwind-registry",
        "build",
        "allow",
    ),
    (
        "deployment-controller",
        {"issuer": "northwind-oidc", "audience": "northwind-production", "lifetime_seconds": 600},
        "reconcile-deployment",
        "northwind-production",
        "production",
        "allow",
    ),
    (
        "maintainer-alice",
        {"issuer": "northwind-human-idp", "audience": "northwind-source", "lifetime_seconds": 1800},
        "reconcile-deployment",
        "northwind-production",
        "production",
        "deny",
    ),
    (
        "release-workflow",
        {
            "issuer": "northwind-oidc",
            "audience": "northwind-production",
            "lifetime_seconds": 600,
        },
        "publish-artifact",
        "northwind-registry",
        "build",
        "deny",
    ),
]
for subject, claims, action, resource, env, expected in cases:
    claims = {**claims, "claim_id": f"checkpoint-{subject}-{action}-{env}"}
    result = authorize(subject, claims, action, resource, env, s, r, t)
    if result["result"] != expected:
        raise SystemExit(result)
for event in read_events(len(cases)):
    errors = trace_errors(event)
    if errors:
        raise SystemExit({"incomplete decision trace": errors, "event": event})
print("chapter 04 checkpoint: attributable subjects, claims, and bounded authorization verified")
