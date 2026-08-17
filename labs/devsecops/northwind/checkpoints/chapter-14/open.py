from evaluate import ROOT, load, write

case = load(ROOT / "checkpoints/chapter-14/cases/open-incident.yaml")
write(ROOT / "response/case/incident.yaml", case)
subjects_path = ROOT / "identity/subjects.yaml"
subjects = load(subjects_path)
session = next(item for item in subjects["subjects"] if item["id"] == "compromised-session")
session["status"] = "active"
write(subjects_path, subjects)
print(
    "chapter 14 open: incident INC-2026-0815-01 investigating; "
    "compromised-session active"
)
