from evaluate import ROOT, load, write_json

decision_path = ROOT / "build/chapter-06-attack-decision.json"
if not decision_path.exists():
    raise SystemExit("run chapter-06-attack before containment")
attack_decision = load(decision_path)
if attack_decision["result"] != "deny":
    raise SystemExit("unsafe revision was not denied")
record = {
    "kind": "source-quarantine",
    "revision": attack_decision["revision"],
    "status": "quarantined",
    "admission_decision": str(decision_path.relative_to(ROOT)),
}
path = ROOT / "build/chapter-06-quarantine.json"
write_json(path, record)
print(f"chapter 06 containment: unsafe revision quarantined; record={path}")
