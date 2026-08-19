from evaluate import evaluate, events, inputs

r, p = inputs()
required = {"requested", "approved", "used", "revoked", "reviewed"}
if evaluate(r, p) or {x["event"] for x in events()} != required:
    raise SystemExit("lifecycle evidence incomplete")
print("chapter 05 recovery: legitimate emergency lifecycle and evidence remain available")
