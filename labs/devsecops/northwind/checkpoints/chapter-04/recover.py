from pathlib import Path

import yaml
from evaluate import authorize, inputs

root = Path(__file__).resolve().parents[2]
subjects, roles, trust = inputs()
contained_path = root / "build" / "chapter-04-contained.yaml"
if not contained_path.is_file():
    raise SystemExit("run chapter-04-contain before recovery verification")
contained = yaml.safe_load(contained_path.read_text(encoding="utf-8"))
old = authorize(
    "compromised-session",
    {
        "claim_id": "recovery-old-003",
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
good = authorize(
    "release-workflow",
    {
        "claim_id": "recovery-good-004",
        "issuer": "northwind-oidc",
        "audience": "northwind-registry",
        "lifetime_seconds": 600,
    },
    "publish-artifact",
    "northwind-registry",
    "build",
    subjects,
    roles,
    trust,
)
if "revoked-subject" not in old["reasons"] or good["result"] != "allow":
    raise SystemExit({"old": old, "good": good})
print("chapter 04 recovery: revoked session fails while legitimate automation remains authorized")
