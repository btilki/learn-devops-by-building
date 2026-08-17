from evaluate import ROOT, load, write

decision_path = ROOT / "build/chapter-10-attack-decision.json"
copies_path = ROOT / "build/chapter-10-exposed-copies.json"
secret_revocation = ROOT / "build/chapter-09-revocations.json"
if (
    not decision_path.exists()
    or load(decision_path)["result"] != "deny"
    or not copies_path.exists()
):
    raise SystemExit("run chapter-10-attack before containment")
if not secret_revocation.exists() or "payment-v1" not in load(secret_revocation)["versions"]:
    raise SystemExit("Chapter 9 payment-authority revocation evidence missing")
copies = load(copies_path)["copies"]
record = {
    "kind": "data-containment",
    "quarantined_copy_ids": [copy["id"] for copy in copies],
    "purged_copy_ids": [copy["id"] for copy in copies],
    "remaining_copies": [],
    "payment_authority_revocation": str(secret_revocation.relative_to(ROOT)),
    "backup_constraint": "expire-by-generation-and-reapply-tombstones-on-restore",
}
path = ROOT / "build/chapter-10-containment.json"
write(path, record)
print(f"chapter 10 containment: modeled exposed copies transitioned to purged; record={path}")
