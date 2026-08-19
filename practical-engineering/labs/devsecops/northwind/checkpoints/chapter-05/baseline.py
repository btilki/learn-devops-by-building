from pathlib import Path

from evaluate import ROOT, evaluate, inputs, load

_, p = inputs()
r = load(Path(ROOT / "checkpoints/chapter-05/cases/unsafe-request.yaml"))
errors = evaluate(r, p)
if not {"self-approval", "duration-excessive", "lifecycle-order-invalid"}.issubset(errors):
    raise SystemExit(errors)
print("chapter 05 baseline: self-approved unbounded privilege correctly rejected")
