from evaluate import ROOT, evaluate_assurance, load

report = load(ROOT / "governance/assurance-report.yaml")
catalog = load(ROOT / "governance/control-catalog.yaml")
evidence_map = load(ROOT / "governance/evidence-map.yaml")
calendar = load(ROOT / "governance/review-calendar.yaml")
telemetry = load(ROOT / "checkpoints/chapter-16/cases/complete-telemetry-window.yaml")
findings = evaluate_assurance(
    report,
    catalog,
    evidence_map,
    calendar,
    telemetry,
    {"changes": []},
)
if findings:
    raise SystemExit(findings)
print("chapter 16 checkpoint: owned controls, live evidence, and review triggers verified")
