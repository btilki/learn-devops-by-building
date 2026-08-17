from evaluate import completed_inputs, evaluate

errors = evaluate(*completed_inputs())
if errors:
    raise SystemExit("chapter 03 checkpoint failed:\n- " + "\n- ".join(errors))
print("chapter 03 checkpoint: risk context, ownership, treatment, and control portfolio verified")
