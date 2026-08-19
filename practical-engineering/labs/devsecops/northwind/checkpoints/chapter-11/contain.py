from evaluate import ROOT, decision, exception_errors, inputs, load, log, write

state_path = ROOT / "build/chapter-11-exception-state.json"
if not state_path.exists() or not load(state_path)["exceptions"]:
    raise SystemExit("run chapter-11-attack before containment")
rules, points, exceptions, governance = inputs()
narrow = exceptions["exceptions"][0]
errors = exception_errors(narrow, rules, points, governance)
if errors:
    raise SystemExit(errors)
write(state_path, {"kind": "exception-state", "exceptions": [narrow]})
record = decision(
    "source-merge",
    narrow["rule"],
    rules["version"],
    {"subject": narrow["owner"], "incident": "mirror-incident-441"},
    "allow-with-exception",
    [],
    narrow["id"],
)
record["compensating_controls"] = narrow["compensating_controls"]
record["expires_at"] = narrow["expires_at"]
path = ROOT / "build/chapter-11-contained-decision.json"
write(path, record)
log(record)
print(f"chapter 11 containment: bypass replaced by narrow expiring exception; decision={path}")
