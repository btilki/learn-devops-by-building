from evaluate import ROOT, decision, exception_errors, inputs, load, log, write

rules, points, _, governance = inputs()
bypass = load(ROOT / "checkpoints/chapter-11/cases/broad-bypass.yaml")
errors = exception_errors(bypass, rules, points, governance)
required = {
    "exception-rule-invalid",
    "exception-scope-broad",
    "exception-compensating-controls-missing",
    "exception-evidence-missing",
    "exception-expires-at-missing",
    "exception-removal-path-missing",
}
if not required.issubset(errors):
    raise SystemExit(errors)
record = decision(
    "production-deploy",
    "release-admission",
    rules["version"],
    {"subject": "release-manager", "reason": "release-pressure"},
    "deny",
    errors,
    bypass["id"],
)
state = {"kind": "exception-state", "exceptions": [bypass]}
write(ROOT / "build/chapter-11-exception-state.json", state)
path = ROOT / "build/chapter-11-attack-decision.json"
write(path, record)
log(record)
print(f"chapter 11 attack: broad non-expiring bypass denied; decision={path}")
