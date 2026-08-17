from evaluate import ROOT, evaluate, load

case = load(ROOT / "checkpoints/chapter-03/cases/score-only.yaml")
errors = evaluate(case, {"decisions": []}, {"attack_paths": []}, {"assets": []}, {})
if not any("unknown attack path" in x for x in errors):
    raise SystemExit(f"unsafe baseline missed: {errors}")
print("chapter 03 baseline: score-only risk decision correctly rejected")
