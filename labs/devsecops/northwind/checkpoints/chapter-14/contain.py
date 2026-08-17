import importlib.util

from evaluate import ROOT, containment_errors, load, verify_manifest, write


def chapter_04_authorize():
    path = ROOT / "checkpoints/chapter-04/evaluate.py"
    spec = importlib.util.spec_from_file_location("chapter_04_authorization", path)
    if not spec or not spec.loader:
        raise SystemExit("chapter 4 authorization evaluator unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.authorize

manifest = load(ROOT / "response/evidence-manifest.yaml")
plan = load(ROOT / "response/containment-plan.yaml")
manifest_findings = verify_manifest(manifest)
plan_findings = containment_errors(plan)
if manifest_findings or plan_findings:
    raise SystemExit({"evidence": manifest_findings, "plan": plan_findings})

subjects_path = ROOT / "identity/subjects.yaml"
subjects = load(subjects_path)
session = next(item for item in subjects["subjects"] if item["id"] == "compromised-session")
session["status"] = "revoked"
write(subjects_path, subjects)

points_path = ROOT / "policy/enforcement-points.yaml"
points = load(points_path)
production_deploy = next(item for item in points["points"] if item["id"] == "production-deploy")
production_deploy["status"] = "frozen"
write(points_path, points)

contract_path = ROOT / "runtime/contracts/order-worker.yaml"
contract = load(contract_path)
contract["status"] = "isolated"
contract["allowed_processes"] = []
contract["allowed_egress"] = []
contract["required_egress"] = []
write(contract_path, contract)

subjects = load(subjects_path)
roles = load(ROOT / "identity/roles.yaml")
trust = load(ROOT / "identity/trust-policy.yaml")
authorize = chapter_04_authorize()
revoked = authorize(
    "compromised-session",
    {
        "claim_id": "containment-revoked-session",
        "issuer": "northwind-human-idp",
        "audience": "northwind-source",
        "lifetime_seconds": 600,
    },
    "propose-change",
    "northwind-source",
    "repository",
    subjects,
    roles,
    trust,
    record=False,
)
legitimate = authorize(
    "maintainer-alice",
    {
        "claim_id": "containment-legitimate-maintainer",
        "issuer": "northwind-human-idp",
        "audience": "northwind-source",
        "lifetime_seconds": 600,
    },
    "propose-change",
    "northwind-source",
    "repository",
    subjects,
    roles,
    trust,
    record=False,
)
if revoked["result"] != "deny" or "revoked-subject" not in revoked["reasons"]:
    raise SystemExit({"revoked-session": revoked})
if legitimate["result"] != "allow":
    raise SystemExit({"legitimate-maintainer": legitimate})
if load(points_path)["points"][1]["status"] != "frozen":
    raise SystemExit("production release path was not frozen")
if load(contract_path)["status"] != "isolated":
    raise SystemExit("order-worker was not isolated")
record = {
    "kind": "containment-decision",
    "case_id": plan["case_id"],
    "authority": {
        "compromised-session": "revoked",
        "production-release-path": "frozen",
        "order-worker": "isolated",
    },
    "business_state": {
        "queue": "preserved",
        "database": "preserved",
        "service_mode": plan["service_mode"],
    },
    "new_attacker_actions": "denied",
    "evidence_verified_before_mutation": True,
    "authorization_checks": {
        "compromised-session": revoked,
        "maintainer-alice": legitimate,
    },
}
write(ROOT / "build/chapter-14-containment.json", record)
print("chapter 14 containment: authority closed, evidence preserved, and order state retained")
