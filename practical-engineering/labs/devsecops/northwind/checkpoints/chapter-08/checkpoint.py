from evaluate import evaluate, inputs

errors = evaluate(*inputs())
if errors:
    raise SystemExit(errors)
print("chapter 08 checkpoint: context-backed vulnerability decisions verified")
