from evaluate import ROOT, evaluate, inputs, load

raw, findings, context, _, exceptions, policy = inputs()
unsafe = load(ROOT / "checkpoints/chapter-08/cases/severity-only-decisions.yaml")
errors = evaluate(raw, findings, context, unsafe, exceptions, policy)
codes = {error.split(":", 1)[0] for error in errors}
if not {"urgent-priority-invalid", "urgent-treatment-invalid", "exception-missing"}.issubset(codes):
    raise SystemExit(errors)
print("chapter 08 challenge: context policy rejected the severity-ordered decision set")
