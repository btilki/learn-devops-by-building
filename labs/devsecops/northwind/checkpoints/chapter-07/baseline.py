from evaluate import ROOT, evaluate, inputs, load

attack = load(ROOT / "checkpoints/chapter-07/cases/untrusted-builder.yaml")
_, _, admission, resolution = inputs()
permissive = load(ROOT / "checkpoints/chapter-07/cases/permissive-build-policy.yaml")
errors = evaluate(attack, permissive, admission, resolution, {})
if errors:
    raise SystemExit(errors)
print("chapter 07 baseline: signature-only policy admitted an untrusted non-isolated builder")
