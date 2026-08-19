from evaluate import ROOT, evidence_sources, load

alert = ROOT / "build/chapter-13-alert.json"
case = load(ROOT / "response/case/incident.yaml")
if not alert.exists() or case["status"] != "investigating":
    raise SystemExit("chapter 14 baseline prerequisites missing")
if not any(
    subject["id"] == "compromised-session" and subject["status"] == "active"
    for subject in load(evidence_sources()[2])["subjects"]
):
    raise SystemExit("active attacker authority was not reproduced")
print(
    "chapter 14 baseline: correlated alert exists, but attacker authority "
    "and incident scope remain open"
)
