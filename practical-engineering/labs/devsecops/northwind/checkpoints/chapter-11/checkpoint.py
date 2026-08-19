from evaluate import evaluate, inputs

errors = evaluate(*inputs())
if errors:
    raise SystemExit(errors)
print("chapter 11 checkpoint: enforcement placement and bounded exceptions verified")
