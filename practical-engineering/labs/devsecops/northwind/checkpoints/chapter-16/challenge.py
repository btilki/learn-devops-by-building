from evaluate import (
    ROOT,
    evaluate_assurance,
    improvement_items,
    load,
    reopened_risk_record,
    write,
)

catalog = load(ROOT / "governance/control-catalog.yaml")
evidence_map = load(ROOT / "governance/evidence-map.yaml")
calendar = load(ROOT / "governance/review-calendar.yaml")
telemetry = load(ROOT / "checkpoints/chapter-16/cases/missing-telemetry-window.yaml")
changes = load(ROOT / "checkpoints/chapter-16/cases/changed-attack-path.yaml")
theater = load(ROOT / "checkpoints/chapter-16/cases/green-theater-report.yaml")
findings = evaluate_assurance(
    theater, catalog, evidence_map, calendar, telemetry, changes
)
required = {
    "assurance-theater:pass-with-failures",
    "exception-claim-expired:exception-dependency-mirror-2026-08",
    "telemetry-gap:artifact_digest,deployment",
    "attack-path-uncovered:registry-node-cache-redeploy",
    "material-change-review-pending:registry-node-cache-redeploy",
    "owner-mismatch:assurance-report",
}
if not required.issubset(findings):
    raise SystemExit({"required": sorted(required), "observed": findings})
failure = {
    "schema_version": 1,
    "kind": "assurance-failure",
    "report": theater["id"],
    "status": "fail",
    "findings": findings,
    "decision": "reopen-risk-and-redesign-controls",
}
write(ROOT / "build/chapter-16-assurance-failure.json", failure)
write(ROOT / "build/chapter-16-reopened-risk.json", reopened_risk_record(changes, findings))
backlog = {
    "schema_version": 1,
    "kind": "security-improvement-backlog",
    "items": improvement_items(findings),
}
if not backlog["items"]:
    raise SystemExit("improvement backlog was not derived from findings")
write(ROOT / "build/chapter-16-improvement-backlog.json", backlog)
corrected = load(ROOT / "checkpoints/chapter-16/cases/corrected-assurance-report.yaml")
corrected["evidence"]["mechanism_evidence"] = [
    "build/chapter-16-assurance-failure.json#findings"
]
corrected["evidence"]["decision_evidence"] = ["build/chapter-16-reopened-risk.json#status"]
corrected["improvement_refs"] = ["build/chapter-16-improvement-backlog.json#items"]
corrected_findings = evaluate_assurance(
    corrected, catalog, evidence_map, calendar, telemetry, changes
)
reporting_failures = [
    finding
    for finding in corrected_findings
    if finding.startswith(("assurance-theater", "assurance-criterion-stale", "owner-mismatch"))
]
if reporting_failures:
    raise SystemExit(reporting_failures)
write(ROOT / "build/chapter-16-corrected-assurance.json", corrected)
print("chapter 16 challenge: false-green assurance failed; risk and improvement work reopened")
