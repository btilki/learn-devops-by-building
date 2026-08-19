import importlib.util
from copy import deepcopy
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-07/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter_07", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def codes(errors):
    return {error.split(":", 1)[0] for error in errors}


def test_complete_chain_passes():
    assert module.evaluate(*module.inputs()) == []


def test_builder_isolation_and_hermeticity_are_enforced():
    provenance, build, admission, resolution = module.inputs()
    provenance = deepcopy(provenance)
    provenance["builder"] = {"id": "rogue", "isolated": False, "hermetic": False}
    result = codes(module.evaluate(provenance, build, admission, resolution))
    assert {"builder-untrusted", "builder-not-isolated", "build-not-hermetic"}.issubset(result)


def test_signature_validity_and_key_trust_are_distinct():
    provenance, build, admission, resolution = module.inputs()
    provenance = deepcopy(provenance)
    provenance["signature"] = {"valid": False, "key_id": "unknown-key"}
    result = codes(module.evaluate(provenance, build, admission, resolution))
    assert {"signature-invalid", "signing-key-untrusted"}.issubset(result)


def test_source_dependency_and_parameters_must_match():
    provenance, build, admission, resolution = module.inputs()
    provenance = deepcopy(provenance)
    provenance["source"]["revision"] = "wrong"
    provenance["dependency_resolution"] = "wrong"
    provenance["parameters"] = {"release": False}
    result = codes(module.evaluate(provenance, build, admission, resolution))
    expected = {
        "source-decision-mismatch",
        "dependency-decision-mismatch",
        "parameter-value-unapproved",
    }
    assert expected.issubset(result)


def test_evidence_target_and_approval_are_enforced():
    provenance, build, admission, resolution = module.inputs()
    provenance = deepcopy(provenance)
    provenance["sbom_digest"] = ""
    provenance["transparency_entry"] = ""
    provenance["release"]["target"] = "unknown"
    provenance["release"]["approvers"] = [provenance["release"]["requester"]]
    result = codes(module.evaluate(provenance, build, admission, resolution))
    expected = {
        "sbom-missing",
        "transparency-missing",
        "target-unapproved",
        "release-approval-missing",
    }
    assert expected.issubset(result)


def test_revoked_trust_is_rejected():
    provenance, build, admission, resolution = module.inputs()
    revocations = {
        "builders": [provenance["builder"]["id"]],
        "signing_keys": [provenance["signature"]["key_id"]],
    }
    result = codes(module.evaluate(provenance, build, admission, resolution, revocations))
    assert {"builder-untrusted", "signing-key-untrusted"}.issubset(result)


def test_default_admission_path_loads_revocations(monkeypatch, tmp_path):
    provenance, build, admission, resolution = module.inputs()
    (tmp_path / "build").mkdir()
    (tmp_path / "build/chapter-07-revocations.json").write_text(
        '{"builders": [], "signing_keys": ["release-key-v3"]}\n'
    )
    monkeypatch.setattr(module, "ROOT", tmp_path)
    result = codes(module.evaluate(provenance, build, admission, resolution))
    assert "signing-key-untrusted" in result


def test_fewer_allowed_parameters_do_not_fail():
    provenance, build, admission, resolution = module.inputs()
    provenance = deepcopy(provenance)
    provenance["parameters"] = {}
    assert "parameter-unapproved" not in codes(
        module.evaluate(provenance, build, admission, resolution, {})
    )
