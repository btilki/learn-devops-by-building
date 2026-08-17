import json

import yaml
from evaluate import ROOT, load, write

events_path = ROOT / "runtime/events.jsonl"
events = (
    [json.loads(line) for line in events_path.read_text().splitlines()]
    if events_path.exists()
    else []
)
if len(events) != 3:
    raise SystemExit("run chapter-12-attack before containment")
subjects = load(ROOT / "identity/subjects.yaml")
workload = next((item for item in subjects["subjects"] if item["id"] == "order-worker"), None)
if not workload or workload["status"] != "active":
    raise SystemExit("registered active workload subject missing")
contained_subjects = {**subjects, "subjects": [dict(item) for item in subjects["subjects"]]}
next(item for item in contained_subjects["subjects"] if item["id"] == "order-worker")["status"] = (
    "revoked"
)
identity_path = ROOT / "build/chapter-12-contained-subjects.yaml"
identity_path.write_text(yaml.safe_dump(contained_subjects, sort_keys=False))
if (
    next(item for item in load(identity_path)["subjects"] if item["id"] == "order-worker")["status"]
    != "revoked"
):
    raise SystemExit("workload subject revocation failed")
record = {
    "kind": "runtime-containment",
    "workload": "order-worker",
    "isolated": True,
    "identity_state": str(identity_path.relative_to(ROOT)),
    "revoked_claim": events[0]["claim_id"],
    "evidence_preserved": str(events_path.relative_to(ROOT)),
    "replacement_required": True,
}
path = ROOT / "build/chapter-12-containment.json"
write(path, record)
print(f"chapter 12 containment: workload isolated; registered subject revoked; record={path}")
