import importlib.util
from copy import deepcopy
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-09/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter_09", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def codes(errors):
    return {error.split(":", 1)[0] for error in errors}


def test_governed_secret_state_passes():
    assert module.evaluate(*module.baseline_inputs()) == []


def test_owner_storage_and_plaintext_are_enforced():
    inventory, policy, references = module.baseline_inputs()
    inventory = deepcopy(inventory)
    inventory["secrets"][0]["owner"] = ""
    inventory["secrets"][0]["storage"] = "repository"
    references = deepcopy(references)
    references["references"][0]["value"] = "SYNTHETIC_SECRET_DO_NOT_USE"
    result = codes(module.evaluate(inventory, policy, references))
    expected = {
        "owner-missing",
        "storage-unapproved",
        "plaintext-reference",
        "known-plaintext-marker",
    }
    assert expected.issubset(result)


def test_revoked_wrong_consumer_and_unattributable_use_fail():
    inventory, policy, _ = module.baseline_inputs()
    result, errors = module.authorize(
        "payment-provider-credential",
        "payment-v2",
        "compromised-maintainer",
        "",
        inventory,
        policy,
        {"versions": ["payment-v2"]},
    )
    assert result == "deny"
    assert {"version-revoked", "consumer-unapproved", "use-unattributable"}.issubset(set(errors))


def test_rotation_overlap_is_bounded():
    inventory, policy, _ = module.baseline_inputs()
    assert max(module.overlaps(inventory["secrets"][0])) <= policy["maximum_overlap_seconds"]


def test_overlap_survives_reordered_and_accumulated_versions():
    inventory, _, _ = module.baseline_inputs()
    secret = deepcopy(inventory["secrets"][0])
    secret["versions"].append(
        {
            "id": "payment-v3",
            "status": "planned",
            "issued_at": "2026-09-14T23:55:00Z",
        }
    )
    secret["versions"].reverse()
    assert module.overlaps(secret) == [600]


def test_unknown_retired_and_revoked_versions_are_distinct():
    inventory, policy, _ = module.baseline_inputs()
    unknown = module.authorize(
        "payment-provider-credential", "missing", "order-worker", "c", inventory, policy, {}
    )
    retired = module.authorize(
        "payment-provider-credential", "payment-v1", "order-worker", "c", inventory, policy, {}
    )
    active = deepcopy(inventory)
    active["secrets"][0]["versions"][0]["status"] = "active"
    active["secrets"][0]["versions"][1]["status"] = "retired"
    revoked = module.authorize(
        "payment-provider-credential",
        "payment-v1",
        "order-worker",
        "c",
        active,
        policy,
        {"versions": ["payment-v1"]},
    )
    assert unknown[1] == ["version-unknown"]
    assert retired[1] == ["version-retired"]
    assert revoked[1] == ["version-revoked"]


def test_authorize_emits_matching_use_event(monkeypatch, tmp_path):
    inventory, policy, _ = module.baseline_inputs()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    result, errors = module.authorize(
        "payment-provider-credential",
        "payment-v2",
        "order-worker",
        "claim-test",
        inventory,
        policy,
        {},
        True,
    )
    assert result == "allow" and errors == []
    event = module.events()[0]
    assert (event["version"], event["subject"], event["claim_id"], event["result"]) == (
        "payment-v2",
        "order-worker",
        "claim-test",
        "allow",
    )


def test_unapproved_exception_fails():
    inventory, policy, references = module.baseline_inputs()
    inventory = deepcopy(inventory)
    inventory["secrets"][0]["exception"] = "permanent-bypass"
    assert "exception-unapproved" in codes(module.evaluate(inventory, policy, references))
