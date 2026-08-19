from evaluate import ROOT, exception_errors, inputs, load

rules, points, _, governance = inputs()
bypass = load(ROOT / "checkpoints/chapter-11/cases/broad-bypass.yaml")
placebo = {
    **bypass,
    "rule": "dependency-admission",
    "scope": "release",
    "expires_at": "2099-01-01T00:00:00Z",
    "compensating_controls": ["none"],
    "compensation_enforcement_points": ["source-merge"],
    "evidence": ["none"],
    "removal_path": "manual",
}
permissive = {
    **governance,
    "maximum_duration_seconds": 3_000_000_000,
    "forbidden_scopes": ["*"],
    "placeholder_values": [],
    "minimum_evidence_items": 1,
    "require_independent_compensation_point": False,
}
if exception_errors(placebo, rules, points, permissive):
    raise SystemExit("permissive exception baseline did not reproduce")
if not exception_errors(placebo, rules, points, governance):
    raise SystemExit("completed governance accepted the placebo exception")
print("chapter 11 baseline: permissive exception policy admitted a placebo release waiver")
