from evaluate import ROOT, fixture_errors, inputs, load, write

containment_path = ROOT / "build/chapter-10-containment.json"
copies_path = ROOT / "build/chapter-10-exposed-copies.json"
if not containment_path.exists() or not copies_path.exists():
    raise SystemExit("run chapter-10-contain before recovery")
containment = load(containment_path)
copy_ids = {copy["id"] for copy in load(copies_path)["copies"]}
if set(containment["purged_copy_ids"]) != copy_ids or containment["remaining_copies"]:
    raise SystemExit("modeled exposed copies remain after purge")
fixture = load(ROOT / "data-security/sanitized-fixture.yaml")
exposure = load(ROOT / "checkpoints/chapter-10/cases/exposed-fixture.yaml")
classification, _, policy, _, _ = inputs()
errors = fixture_errors(fixture, classification, policy, set(exposure["values"]))
if errors:
    raise SystemExit(errors)
record = {
    "kind": "data-recovery-evidence",
    "sanitized_replacement": "data-security/sanitized-fixture.yaml",
    "classified_fields": sorted(fixture["records"][0]),
    "exposed_values_absent": True,
    "purged_copy_ids": sorted(copy_ids),
    "backup_expiry_constraint_documented": True,
}
path = ROOT / "build/chapter-10-recovery.json"
write(path, record)
print(f"chapter 10 recovery: classified sanitized data and copy purge verified; record={path}")
