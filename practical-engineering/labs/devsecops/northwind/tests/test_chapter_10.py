import importlib.util
from copy import deepcopy
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-10/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter_10", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def codes(decision):
    reasons = decision if isinstance(decision, list) else decision["reasons"]
    return {reason.split(":", 1)[0] for reason in reasons}


def test_minimum_declared_use_passes():
    classification, uses, policy, _, _ = module.inputs()
    request = {
        "subject": "notification-service",
        "purpose": "send-order-confirmation",
        "fields": ["order_id", "customer_email", "order_total"],
        "store": "runtime-memory",
    }
    assert module.decide(request, classification, uses, policy)["result"] == "allow"


def test_field_purpose_and_store_are_independent_controls():
    classification, uses, policy, _, _ = module.inputs()
    request = {
        "subject": "notification-service",
        "purpose": "send-order-confirmation",
        "fields": ["payment_reference"],
        "store": "telemetry",
    }
    result = codes(module.decide(request, classification, uses, policy))
    assert {"field-not-permitted", "store-class-exceeded", "store-not-permitted"}.issubset(result)


def test_missing_identity_and_unknown_field_fail():
    classification, uses, policy, _, _ = module.inputs()
    request = {"subject": "", "purpose": "", "fields": ["unknown"], "store": "primary"}
    result = codes(module.decide(request, classification, uses, policy))
    assert {"subject-missing", "purpose-missing", "use-undeclared", "field-unknown"}.issubset(
        result
    )


def test_nonproduction_class_limit_is_enforced():
    classification, uses, policy, _, _ = module.inputs()
    uses = deepcopy(uses)
    uses["uses"][2]["stores"].append("nonproduction")
    request = {
        "subject": "order-worker",
        "purpose": "payment-reconciliation",
        "fields": ["payment_reference"],
        "store": "nonproduction",
    }
    assert "store-class-exceeded" in codes(module.decide(request, classification, uses, policy))


def test_unknown_store_has_no_silent_class_bypass():
    classification, uses, policy, _, _ = module.inputs()
    uses = deepcopy(uses)
    uses["uses"][2]["stores"].append("analytics")
    request = {
        "subject": "order-worker",
        "purpose": "payment-reconciliation",
        "fields": ["payment_reference"],
        "store": "analytics",
    }
    assert "store-policy-missing" in codes(module.decide(request, classification, uses, policy))


def test_every_used_and_derived_store_has_lifecycle_policy():
    classification, uses, policy, retention, lineage = module.inputs()
    assert module.lifecycle_errors(classification, uses, policy, retention, lineage) == []


def test_sanitized_fixture_rejects_unknown_sensitive_and_exposed_values():
    classification, _, policy, _, _ = module.inputs()
    fixture = {"records": [{"unknown": "x", "payment_reference": "synthetic-payment-ref"}]}
    result = codes(
        module.fixture_errors(fixture, classification, policy, {"synthetic-payment-ref"})
    )
    expected = {"fixture-field-unknown", "fixture-class-exceeded", "production-value-retained"}
    assert expected.issubset(result)
