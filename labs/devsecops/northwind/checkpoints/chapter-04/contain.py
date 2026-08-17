from copy import deepcopy
from pathlib import Path

import yaml
from evaluate import authorize, inputs

ROOT = Path(__file__).resolve().parents[2]
subjects, roles, trust = inputs()
contained = deepcopy(subjects)
subject = next(item for item in contained["subjects"] if item["id"] == "compromised-session")
if subject["status"] != "active":
    raise SystemExit("containment precondition failed")
subject["status"] = "revoked"
decision = authorize(
    "compromised-session",
    {
        "claim_id": "contained-claim-002",
        "issuer": "northwind-human-idp",
        "audience": "northwind-source",
        "lifetime_seconds": 600,
    },
    "propose-change",
    "northwind-source",
    "repository",
    contained,
    roles,
    trust,
)
if "revoked-subject" not in decision["reasons"]:
    raise SystemExit(decision)
output = ROOT / "build" / "chapter-04-contained.yaml"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(yaml.safe_dump(contained, sort_keys=False), encoding="utf-8")
print("chapter 04 containment: active compromised subject revoked and denied")
