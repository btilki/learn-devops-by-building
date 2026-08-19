from evaluate import evaluate, inputs

errors = evaluate(*inputs())
if errors:
    raise SystemExit(errors)
print("chapter 05 checkpoint: bounded privilege, independent approval, expiry, and review verified")
