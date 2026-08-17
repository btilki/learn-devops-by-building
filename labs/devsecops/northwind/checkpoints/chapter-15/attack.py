from evaluate import ROOT, cache_findings, invalidated_digests, load, write

inventory = load(ROOT / "recovery/trust-inventory.yaml")
cache = load(ROOT / "checkpoints/chapter-15/cases/persistence-cache-redeploy.yaml")
subjects = load(ROOT / "identity/subjects.yaml")
release = next(item for item in subjects["subjects"] if item["id"] == "release-workflow")
findings = cache_findings(cache, invalidated_digests(inventory))
if release["status"] != "active" or not findings:
    raise SystemExit("modeled persistence replay did not reproduce")
record = {
    "schema_version": 1,
    "kind": "persistence-replay",
    "case_id": inventory["case_id"],
    "attempt": cache["attempt"],
    "automation_status": release["status"],
    "findings": findings,
    "reconciliation_resumed": False,
    "trust_restored": False,
}
write(ROOT / "build/chapter-15-persistence-attempt.json", record)
print("chapter 15 attack: retained cache and automation could restore the invalidated artifact")
