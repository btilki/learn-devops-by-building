import importlib.util
from copy import deepcopy
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "checkpoints/chapter-05/evaluate.py"
s = importlib.util.spec_from_file_location("c5", p)
assert s and s.loader
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)


def test_complete():
    assert m.evaluate(*m.inputs()) == []


def test_self_approval():
    r, p = m.inputs()
    r = deepcopy(r)
    r["approver"] = r["requester"]
    assert "self-approval" in m.evaluate(r, p)


def test_expiry_and_review():
    r, p = m.inputs()
    r = deepcopy(r)
    r["expires_at"] = "2026-08-15T11:03:01Z"
    r["reviewed_at"] = "2026-08-16T10:12:01Z"
    errors = m.evaluate(r, p)
    assert "duration-excessive" in errors and "review-late" in errors


def test_policy_fields_are_executable():
    r, p = m.inputs()
    p = deepcopy(p)
    p["self_approval_allowed"] = True
    p["break_glass"]["review_due_seconds"] = 60
    r = deepcopy(r)
    r["approver"] = r["requester"]
    assert m.evaluate(r, p) == ["review-late"]


def test_lifecycle_order_and_evidence():
    r, p = m.inputs()
    r = deepcopy(r)
    r["reviewed_at"] = "2026-08-15T10:10:00Z"
    assert "lifecycle-order-invalid" in m.evaluate(r, p)
    assert [event["event"] for event in m.events()] == [
        "requested",
        "approved",
        "used",
        "revoked",
        "reviewed",
    ]


def test_after_action_review_flag_is_executable():
    r, policy = m.inputs()
    r = deepcopy(r)
    policy = deepcopy(policy)
    del r["reviewed_at"]
    policy["required_fields"] = [
        field for field in policy["required_fields"] if field != "reviewed_at"
    ]
    policy["break_glass"]["requires_after_action_review"] = False
    assert "after-action-review-missing" not in m.evaluate(r, policy)
    policy["break_glass"]["requires_after_action_review"] = True
    assert "after-action-review-missing" in m.evaluate(r, policy)
