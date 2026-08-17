from evaluate import evaluate, inputs

r, p = inputs()
r = {
    **r,
    "requester": "compromised-maintainer",
    "subject": "compromised-maintainer",
    "approver": "compromised-maintainer",
    "purpose": "emergency",
    "action": "reconcile-deployment",
    "expires_at": "2026-08-16T10:03:00Z",
    "reviewed_at": "2026-08-15T10:10:00Z",
}
errors = evaluate(r, p)
required = {"self-approval", "duration-excessive", "action-out-of-scope", "lifecycle-order-invalid"}
if not required.issubset(errors):
    raise SystemExit(errors)
print("chapter 05 attack: invented emergency and self-approved production elevation denied")
