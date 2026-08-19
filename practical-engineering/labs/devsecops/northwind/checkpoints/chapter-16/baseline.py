from evaluate import ROOT, evaluate_assurance, load

recovery = load(ROOT / "build/chapter-15-recovery-verification.json")
if recovery["trust_restored"] is not True:
    raise SystemExit("Chapter 15 recovery verification is required")
report = load(ROOT / "checkpoints/chapter-16/cases/green-theater-report.yaml")
catalog = load(ROOT / "governance/control-catalog.yaml")
evidence_map = load(ROOT / "governance/evidence-map.yaml")
calendar = load(ROOT / "governance/review-calendar.yaml")
telemetry = load(ROOT / "checkpoints/chapter-16/cases/missing-telemetry-window.yaml")
changes = load(ROOT / "checkpoints/chapter-16/cases/changed-attack-path.yaml")
if evaluate_assurance(
    report,
    catalog,
    evidence_map,
    calendar,
    telemetry,
    changes,
    permissive=True,
):
    raise SystemExit("permissive checklist unexpectedly rejected the green report")
if not evaluate_assurance(
    report, catalog, evidence_map, calendar, telemetry, changes
):
    raise SystemExit("live assurance failed to expose the governance gap")
print("chapter 16 baseline: checklist governance accepted a false-green assurance report")
