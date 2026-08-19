from evaluate import decision, evaluate, inputs

provenance, build, admission, resolution = inputs()
errors = evaluate(provenance, build, admission, resolution)
if errors or decision(provenance, admission, errors)["result"] != "allow":
    raise SystemExit(errors)
print("chapter 07 checkpoint: complete source-to-target release chain admitted")
