import importlib.util
from copy import deepcopy
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-06/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter_06", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def codes(errors):
    return {error.split(":", 1)[0] for error in errors}


def test_approved_resolution_passes():
    assert module.evaluate(*module.inputs()) == []


def test_origin_and_ref_are_enforced():
    evidence, source, dependency, lock, ownership = module.inputs()
    evidence = deepcopy(evidence)
    evidence["source"]["origin"] = "https://example.invalid/fork.git"
    evidence["source"]["ref"] = "refs/heads/unprotected"
    result = codes(module.evaluate(evidence, source, dependency, lock, ownership))
    assert {"source-origin-untrusted", "ref-unprotected"}.issubset(result)


def test_review_must_be_independent_and_owned():
    evidence, source, dependency, lock, ownership = module.inputs()
    evidence = deepcopy(evidence)
    evidence["source"]["approvers"] = ["intern-with-no-ownership"]
    result = codes(module.evaluate(evidence, source, dependency, lock, ownership))
    assert "path-owner-approval-missing" in result
    evidence["source"]["approvers"] = [evidence["source"]["author"]]
    result = codes(module.evaluate(evidence, source, dependency, lock, ownership))
    assert {"independent-review-missing", "path-owner-approval-missing"}.issubset(result)


def test_registry_namespace_and_unknown_package_are_independent_controls():
    evidence, source, dependency, lock, ownership = module.inputs()
    evidence = deepcopy(evidence)
    item = evidence["dependencies"][0]
    item["registry"] = "registry.example.invalid"
    item["name"] = "northwind-payments"
    result = codes(module.evaluate(evidence, source, dependency, lock, ownership))
    assert {"registry-unapproved", "namespace-unapproved", "dependency-unknown"}.issubset(result)


def test_version_hash_and_registry_drift_are_distinct():
    evidence, source, dependency, lock, ownership = module.inputs()
    evidence = deepcopy(evidence)
    item = evidence["dependencies"][0]
    item["resolved"] = "3.4.2"
    item["sha256"] = "0" * 64
    item["registry"] = "pypi.org"
    result = codes(module.evaluate(evidence, source, dependency, lock, ownership))
    assert {"version-drift", "hash-mismatch", "locked-registry-mismatch"}.issubset(result)


def test_update_must_be_attributable_when_policy_requires_it():
    evidence, source, dependency, lock, ownership = module.inputs()
    evidence = deepcopy(evidence)
    evidence["source"]["claim_id"] = ""
    assert "update-unattributable" in codes(
        module.evaluate(evidence, source, dependency, lock, ownership)
    )
