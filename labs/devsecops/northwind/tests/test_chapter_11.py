import importlib.util
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-11/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter_11", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def codes(errors):
    return {error.split(":", 1)[0] for error in errors}


def test_complete_policy_passes():
    assert module.evaluate(*module.inputs()) == []


def test_deny_rules_require_blocking_placement_and_logging():
    rules, points, exceptions, governance = module.inputs()
    points = deepcopy(points)
    for point in points["points"]:
        point["failure_mode"] = "detect-only"
    points["points"][0]["decision_log"] = "optional"
    result = codes(module.evaluate(rules, points, exceptions, governance))
    assert {"blocking-placement-missing", "decision-log-missing"}.issubset(result)


def test_placebo_long_duration_and_broad_scope_fail():
    rules, points, _, governance = module.inputs()
    bypass = module.load(module.ROOT / "checkpoints/chapter-11/cases/broad-bypass.yaml")
    bypass = {
        **bypass,
        "rule": "dependency-admission",
        "scope": "release",
        "compensating_controls": ["none"],
        "compensation_enforcement_points": ["source-merge"],
        "evidence": ["none"],
        "expires_at": "2099-01-01T00:00:00Z",
        "removal_path": "manual",
    }
    result = set(module.exception_errors(bypass, rules, points, governance))
    assert {"exception-scope-broad", "exception-duration-excessive"}.issubset(result)
    assert "exception-compensation-not-independent" in result


def test_production_admission_is_non_exceptable():
    rules, points, exceptions, governance = module.inputs()
    value = deepcopy(exceptions["exceptions"][0])
    value["rule"] = "release-admission"
    value["enforcement_points"] = ["production-deploy"]
    assert "exception-rule-non-exceptable" in module.exception_errors(
        value, rules, points, governance
    )


def test_expired_exception_fails():
    values = module.inputs()
    now = datetime(2026, 8, 15, 12, 1, tzinfo=UTC)
    assert "exception-expired" in codes(module.evaluate(*values, now=now))


def test_decision_contains_requester_context():
    value = module.decision(
        "source-merge", "dependency-admission", "v1", {"subject": "alice"}, "deny", []
    )
    assert value["requester_context"]["subject"] == "alice"


def test_rule_owner_is_required():
    rules, points, exceptions, governance = module.inputs()
    rules = deepcopy(rules)
    rules["rules"][0]["owner"] = ""
    assert "rule-owner-missing:dependency-admission" in module.evaluate(
        rules, points, exceptions, governance
    )
