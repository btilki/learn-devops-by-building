from evaluate import ROOT, decision, evaluate, inputs, load, write_json

unsafe = load(ROOT / "checkpoints/chapter-06/cases/unsafe-resolution.yaml")
_, source_policy, dependency_policy, lock, ownership = inputs()
errors = evaluate(unsafe, source_policy, dependency_policy, lock, ownership)
codes = {error.split(":", 1)[0] for error in errors}
required = {
    "independent-review-missing",
    "path-owner-approval-missing",
    "namespace-unapproved",
    "dependency-unknown",
}
if not required.issubset(codes):
    raise SystemExit(errors)
path = ROOT / "build/chapter-06-attack-decision.json"
write_json(path, decision(unsafe, errors))
print(f"chapter 06 attack: look-alike payment dependency denied; decision={path}")
