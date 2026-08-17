from evaluate import ROOT, decision, evaluate, inputs, load, write_json

quarantine_path = ROOT / "build/chapter-06-quarantine.json"
if not quarantine_path.exists() or load(quarantine_path)["status"] != "quarantined":
    raise SystemExit("run chapter-06-contain before recovery")
evidence, source_policy, dependency_policy, lock, ownership = inputs()
errors = evaluate(evidence, source_policy, dependency_policy, lock, ownership)
if errors:
    raise SystemExit(errors)
if evidence["source"]["author"] != source_policy["automation_subject"]:
    raise SystemExit("bounded update automation is unavailable")
path = ROOT / "build/chapter-06-recovery-decision.json"
write_json(path, decision(evidence, errors))
print(f"chapter 06 recovery: trusted graph admitted after quarantine; decision={path}")
