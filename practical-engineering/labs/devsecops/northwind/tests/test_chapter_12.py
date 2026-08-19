import importlib.util
from copy import deepcopy
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-12/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter_12", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_legitimate_contract_passes():
    contract, _ = module.baseline_inputs()
    assert module.legitimate_errors(contract) == []


def test_privilege_filesystem_and_egress_mutations_fail():
    contract, _ = module.baseline_inputs()
    contract = deepcopy(contract)
    contract["linux_capabilities"] = ["SYS_ADMIN"]
    contract["allow_privilege_escalation"] = True
    contract["read_only_root_filesystem"] = False
    contract["allowed_egress"].remove("payment-provider")
    result = {error.split(":", 1)[0] for error in module.legitimate_errors(contract)}
    expected = {
        "capabilities-excessive",
        "privilege-escalation-enabled",
        "root-filesystem-writable",
        "required-egress-missing",
    }
    assert expected.issubset(result)


def test_prevention_detection_and_context_are_distinct():
    contract, policy = module.baseline_inputs()
    base = {
        "subject": "order-worker",
        "claim_id": "",
        "deployment": "",
        "artifact_digest": "wrong",
        "type": "process",
        "resource": "/bin/sh",
    }
    event = module.evaluate_behavior(base, contract, policy)
    assert event["outcome"] == "blocked"
    assert set(event["errors"]) == {
        "attribution-missing",
        "deployment-context-missing",
        "artifact-context-mismatch",
    }


def test_unmapped_action_is_visible():
    contract, policy = module.baseline_inputs()
    event = module.evaluate_behavior(
        {
            "subject": "order-worker",
            "claim_id": "c",
            "deployment": "d",
            "artifact_digest": contract["artifact_digest"],
            "type": "unknown-type",
            "resource": "x",
        },
        contract,
        policy,
    )
    assert "action-policy-missing" in event["errors"]


def test_contract_derives_allowed_and_prohibited_behavior():
    contract, policy = module.baseline_inputs()
    base = {
        "subject": "order-worker",
        "claim_id": "c",
        "deployment": "d",
        "artifact_digest": contract["artifact_digest"],
    }
    cases = [
        ({"type": "process", "resource": "order-worker"}, "allowed"),
        ({"type": "process", "resource": "/bin/sh"}, "blocked"),
        ({"type": "filesystem-write", "resource": "/tmp/order-worker/x"}, "allowed"),
        ({"type": "filesystem-write", "resource": "/etc/cron.d/x"}, "blocked"),
        ({"type": "egress", "resource": "postgresql"}, "allowed"),
        ({"type": "egress", "resource": "c2.invalid"}, "blocked"),
    ]
    assert [
        module.evaluate_behavior({**base, **value}, contract, policy)["outcome"]
        for value, _ in cases
    ] == [expected for _, expected in cases]


def test_all_declared_required_dependencies_are_enforced():
    contract, _ = module.baseline_inputs()
    contract = deepcopy(contract)
    contract["allowed_egress"].remove("email-provider")
    assert "required-egress-missing:email-provider" in module.legitimate_errors(contract)


def test_attack_progression_has_attributable_event_order():
    contract, policy = module.baseline_inputs()
    attack = module.load(module.ROOT / "checkpoints/chapter-12/cases/attack-behaviors.yaml")
    events = [
        module.evaluate_behavior({**attack, **behavior}, contract, policy)
        for behavior in attack["behaviors"]
    ]
    assert [event["time"] for event in events] == [
        "2026-08-15T10:10:00Z",
        "2026-08-15T10:11:00Z",
        "2026-08-15T10:12:00Z",
    ]
