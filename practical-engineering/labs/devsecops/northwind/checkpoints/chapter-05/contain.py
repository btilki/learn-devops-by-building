from evaluate import ROOT, evaluate, events, inputs, load

_, policy = inputs()
r = load(ROOT / "checkpoints/chapter-05/cases/unsafe-request.yaml")
errors = evaluate(r, policy)

if not {"self-approval", "duration-excessive", "action-out-of-scope"}.issubset(errors):
    raise SystemExit(errors)
if any(event["request_id"] == r["id"] for event in events()):
    raise SystemExit("denied privilege appeared in the issued-session evidence")
print("chapter 05 containment: unsafe privilege remained unissued and absent from session evidence")
