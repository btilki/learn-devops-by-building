from evaluate import ROOT, decision, evaluate, inputs, load, write_json

attack = load(ROOT / "checkpoints/chapter-07/cases/untrusted-builder.yaml")
_, build, admission, resolution = inputs()
errors = evaluate(attack, build, admission, resolution)
codes = {x.split(":", 1)[0] for x in errors}
if not {"builder-untrusted", "builder-not-isolated", "build-not-hermetic"}.issubset(codes):
    raise SystemExit(errors)
path = ROOT / "build/chapter-07-attack-decision.json"
write_json(path, decision(attack, admission, errors))
print(f"chapter 07 attack: valid signature did not establish builder trust; decision={path}")
