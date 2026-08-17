import importlib.util
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-08/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter_08", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def codes(errors):
    return {error.split(":", 1)[0] for error in errors}


def test_complete_decisions_and_normalization_pass():
    assert module.evaluate(*module.inputs()) == []


def test_missing_context_owner_and_uncertainty_fail():
    raw, findings, context, decisions, exceptions, policy = module.inputs()
    context = deepcopy(context)
    context["contexts"][0].pop("reachable")
    decisions = deepcopy(decisions)
    decisions["decisions"][0]["owner"] = "nobody"
    decisions["decisions"][0]["uncertainty"] = []
    result = codes(module.evaluate(raw, findings, context, decisions, exceptions, policy))
    expected = {"decision-context-incomplete", "owner-mismatch", "uncertainty-missing"}
    assert expected.issubset(result)


def test_reachable_critical_asset_is_urgent_without_known_exploitation():
    raw, findings, context, decisions, exceptions, policy = module.inputs()
    context = deepcopy(context)
    context["contexts"][1]["known_exploitation"] = False
    decisions = deepcopy(decisions)
    urgent = decisions["decisions"][0]
    urgent["priority"] = 2
    urgent["treatment"] = "monitor"
    result = codes(module.evaluate(raw, findings, context, decisions, exceptions, policy))
    assert {"urgent-priority-invalid", "urgent-treatment-invalid", "exception-missing"}.issubset(
        result
    )


def test_deadlines_and_queue_integrity_are_enforced():
    raw, findings, context, decisions, exceptions, policy = module.inputs()
    decisions = deepcopy(decisions)
    decisions["decisions"][0]["priority"] = 2
    decisions["decisions"][0]["deadline"] = "2032-08-15T00:00:00Z"
    decisions["decisions"][1]["priority"] = 2
    result = codes(module.evaluate(raw, findings, context, decisions, exceptions, policy))
    assert {"queue-priority-invalid", "urgent-deadline-invalid"}.issubset(result)


def test_overdue_decision_and_exception_fail():
    values = module.inputs()
    now = datetime(2026, 9, 16, tzinfo=UTC)
    result = codes(module.evaluate(*values, now=now))
    assert {"decision-overdue", "exception-expired"}.issubset(result)


def test_stale_raw_claim_is_excluded_and_duplicates_are_correlated():
    raw, findings, _, _, _, policy = module.inputs()
    normalized = module.normalize(raw, policy)
    assert normalized == findings["findings"]
    assert all(item["affected_version"] != "1.7.0" for item in normalized)
    assert normalized[0]["sources"] == ["image-scanner", "sbom-scanner"]
