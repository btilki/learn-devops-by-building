from evaluate import ROOT, load, verify_manifest, write

containment = load(ROOT / "build/chapter-14-containment.json")
manifest = load(ROOT / "response/evidence-manifest.yaml")
subjects = load(ROOT / "identity/subjects.yaml")
session = next(item for item in subjects["subjects"] if item["id"] == "compromised-session")
points = load(ROOT / "policy/enforcement-points.yaml")
production_deploy = next(item for item in points["points"] if item["id"] == "production-deploy")
contract = load(ROOT / "runtime/contracts/order-worker.yaml")
if (
    verify_manifest(manifest)
    or session["status"] != "revoked"
    or production_deploy["status"] != "frozen"
    or contract["status"] != "isolated"
    or containment["authorization_checks"]["compromised-session"]["result"] != "deny"
    or containment["authorization_checks"]["maintainer-alice"]["result"] != "allow"
):
    raise SystemExit("containment verification failed")
record = {
    "kind": "containment-verification",
    "case_id": containment["case_id"],
    "evidence_custody": "verified",
    "attacker_authority": "closed",
    "release_path": "frozen",
    "workload": "isolated",
    "queue_and_database": "preserved",
    "service_mode": containment["business_state"]["service_mode"],
    "trust_restored": False,
    "next": "eradicate-persistence-and-restore-trust",
}
write(ROOT / "build/chapter-14-verification.json", record)
print("chapter 14 recovery: containment verified; trust restoration intentionally remains open")
