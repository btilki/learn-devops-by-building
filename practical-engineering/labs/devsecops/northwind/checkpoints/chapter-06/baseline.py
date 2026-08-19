from evaluate import ROOT, evaluate, load

cases = ROOT / "checkpoints/chapter-06/cases"
unsafe = load(cases / "unsafe-resolution.yaml")
errors = evaluate(
    unsafe,
    load(cases / "permissive-source-policy.yaml"),
    load(cases / "permissive-dependency-policy.yaml"),
    load(cases / "permissive-lock.yaml"),
    load(cases / "permissive-ownership.yaml"),
)
if errors:
    raise SystemExit(f"permissive start state unexpectedly denied the unsafe input: {errors}")
print("chapter 06 baseline: permissive source and dependency policy admitted unsafe input")
