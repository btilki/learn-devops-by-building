from evaluate import evaluate, inputs

errors = evaluate(*inputs())
if errors:
    raise SystemExit(errors)
print("chapter 06 checkpoint: source origin, review, registry, version, and hash verified")
