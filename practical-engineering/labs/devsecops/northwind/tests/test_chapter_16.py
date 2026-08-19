import importlib.util
from copy import deepcopy
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-16/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter_16", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def inputs():
    return (
        module.load(module.ROOT / "governance/assurance-report.yaml"),
        module.load(module.ROOT / "governance/control-catalog.yaml"),
        module.load(module.ROOT / "governance/evidence-map.yaml"),
        module.load(module.ROOT / "governance/review-calendar.yaml"),
        module.load(
            module.ROOT / "checkpoints/chapter-16/cases/complete-telemetry-window.yaml"
        ),
        {"changes": []},
    )


def test_complete_assurance_recomputes_cleanly():
    assert module.evaluate_assurance(*inputs()) == []


def test_unresolved_evidence_link_fails():
    _, catalog, evidence_map, _, _, _ = inputs()
    changed = deepcopy(evidence_map)
    changed["links"][0]["ref"] = "build/missing-governance-evidence.json"
    assert "evidence-link-missing:build/missing-governance-evidence.json" in (
        module.evidence_map_errors(catalog, changed)
    )


def test_assurance_report_cannot_prove_itself():
    _, catalog, evidence_map, _, _, _ = inputs()
    changed = deepcopy(evidence_map)
    changed["links"][0]["ref"] = "governance/assurance-report.yaml#status"
    assert any(
        error.startswith("evidence-self-reference")
        for error in module.evidence_map_errors(
            catalog, changed, ("governance/assurance-report.yaml",)
        )
    )


def test_missing_control_owner_fails():
    _, catalog, _, _, _, _ = inputs()
    changed = deepcopy(catalog)
    changed["objectives"][0]["owner"] = ""
    errors = module.catalog_errors(
        changed,
        module.load(module.ROOT / "risk/risk-register.yaml"),
        module.load(module.ROOT / "threat-model/attack-paths.yaml"),
    )
    assert "objective-owner-missing:obj-supply-chain-admission" in errors


def test_registered_risk_without_objective_fails():
    _, catalog, _, _, _, _ = inputs()
    changed = deepcopy(catalog)
    changed["objectives"] = [
        objective
        for objective in changed["objectives"]
        if objective["risk"] != "support-data-purpose-risk"
    ]
    errors = module.catalog_errors(
        changed,
        module.load(module.ROOT / "risk/risk-register.yaml"),
        module.load(module.ROOT / "threat-model/attack-paths.yaml"),
    )
    assert "risk-without-objective:support-data-purpose-risk" in errors
    assert "attack-path-without-objective:overprivileged-support-data-access" in errors


def test_priority_risk_requires_all_control_types():
    _, catalog, _, _, _, _ = inputs()
    changed = deepcopy(catalog)
    for objective in changed["objectives"]:
        if objective["control_type"] == "recover":
            objective["control_type"] = "prevent"
    errors = module.catalog_errors(
        changed,
        module.load(module.ROOT / "risk/risk-register.yaml"),
        module.load(module.ROOT / "threat-model/attack-paths.yaml"),
    )
    assert "priority-risk-missing-recover-control" in errors


def test_expired_exception_claim_fails():
    report, _, _, _, _, _ = inputs()
    changed = deepcopy(report)
    changed["evaluated_at"] = "2026-08-15T12:30:00Z"
    assert (
        "exception-claim-expired:exception-dependency-mirror-2026-08"
        in module.exception_claim_errors(
            changed, module.load(module.ROOT / "policy/exceptions.yaml")
        )
    )


def test_missing_telemetry_context_fails():
    telemetry = module.load(
        module.ROOT / "checkpoints/chapter-16/cases/missing-telemetry-window.yaml"
    )
    assert module.telemetry_errors(telemetry) == [
        "telemetry-gap:artifact_digest,deployment"
    ]


def test_changed_attack_path_requires_distinct_layer_control():
    _, catalog, _, _, _, _ = inputs()
    changes = module.load(
        module.ROOT / "checkpoints/chapter-16/cases/changed-attack-path.yaml"
    )
    assert module.attack_path_coverage_errors(changes, catalog) == [
        "attack-path-uncovered:registry-node-cache-redeploy"
    ]
    assert "node-cache" in catalog["objectives"][4]["does_not_cover"]


def test_unrelated_review_does_not_clear_affected_change():
    report, catalog, _, calendar, _, _ = inputs()
    report = deepcopy(report)
    report["evaluated_at"] = "2026-08-15T12:30:00Z"
    changes = module.load(
        module.ROOT / "checkpoints/chapter-16/cases/changed-attack-path.yaml"
    )
    assert module.material_change_errors(calendar, changes, report, catalog) == [
        "material-change-review-pending:registry-node-cache-redeploy"
    ]


def test_review_cadence_and_evidence_freshness_are_enforced():
    report, _, evidence_map, calendar, _, _ = inputs()
    stale_calendar = deepcopy(calendar)
    stale_calendar["last_reviewed_at"] = "2026-01-01T00:00:00Z"
    assert "review-cadence-exceeded" in module.calendar_errors(
        stale_calendar, report, evidence_map
    )
    stale_map = deepcopy(evidence_map)
    stale_map["links"][0]["collected_at"] = "2026-06-01T00:00:00Z"
    assert any(
        error.startswith("evidence-stale:")
        for error in module.calendar_errors(calendar, report, stale_map)
    )


def test_permissive_checklist_grades_the_report_booleans():
    report, catalog, evidence_map, calendar, telemetry, changes = inputs()
    assert (
        module.evaluate_assurance(
            report, catalog, evidence_map, calendar, telemetry, changes, permissive=True
        )
        == []
    )
    false_report = deepcopy(report)
    false_report["criteria"]["exceptions_bounded"] = False
    assert module.evaluate_assurance(
        false_report,
        catalog,
        evidence_map,
        calendar,
        telemetry,
        changes,
        permissive=True,
    ) == ["checklist-criterion-false:exceptions_bounded"]


def test_report_declared_evidence_must_resolve():
    report, _, _, _, _, _ = inputs()
    changed = deepcopy(report)
    changed["evidence"]["mechanism_evidence"] = ["build/missing-report-evidence.json"]
    assert "evidence-link-missing:build/missing-report-evidence.json" in (
        module.report_evidence_errors(changed)
    )


def test_false_green_report_is_rejected():
    _, catalog, evidence_map, calendar, _, _ = inputs()
    report = module.load(
        module.ROOT / "checkpoints/chapter-16/cases/green-theater-report.yaml"
    )
    telemetry = module.load(
        module.ROOT / "checkpoints/chapter-16/cases/missing-telemetry-window.yaml"
    )
    changes = module.load(
        module.ROOT / "checkpoints/chapter-16/cases/changed-attack-path.yaml"
    )
    findings = module.evaluate_assurance(
        report, catalog, evidence_map, calendar, telemetry, changes
    )
    assert "assurance-theater:pass-with-failures" in findings
    assert "owner-mismatch:assurance-report" in findings


def test_corrected_report_is_honest_about_open_work():
    _, catalog, evidence_map, calendar, _, _ = inputs()
    report = module.load(
        module.ROOT / "checkpoints/chapter-16/cases/corrected-assurance-report.yaml"
    )
    telemetry = module.load(
        module.ROOT / "checkpoints/chapter-16/cases/missing-telemetry-window.yaml"
    )
    changes = module.load(
        module.ROOT / "checkpoints/chapter-16/cases/changed-attack-path.yaml"
    )
    findings = module.evaluate_assurance(
        report, catalog, evidence_map, calendar, telemetry, changes
    )
    assert not any(
        finding.startswith(
            ("assurance-theater", "assurance-criterion-stale", "owner-mismatch")
        )
        for finding in findings
    )
    assert "attack-path-uncovered:registry-node-cache-redeploy" in findings
    items = module.improvement_items(findings)
    assert {item["id"] for item in items} >= {
        "improve-node-cache-persistence-coverage",
        "improve-telemetry-completeness-gate",
        "improve-material-change-review-scope",
    }
