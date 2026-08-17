import importlib.util
from copy import deepcopy
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-14/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter_14", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_manifest_verifies_current_evidence():
    value = module.manifest(module.evidence_sources())
    assert module.verify_manifest(value) == []


def test_manifest_detects_changed_digest():
    value = module.manifest(module.evidence_sources())
    value["items"][0]["sha256"] = "sha256:tampered"
    assert module.verify_manifest(value) == [
        {"path": value["items"][0]["path"], "finding": "digest-mismatch"}
    ]


def test_manifest_distinguishes_missing_evidence():
    value = module.manifest(module.evidence_sources())
    value["items"][0]["path"] = "build/does-not-exist"
    assert module.verify_manifest(value) == [
        {"path": "build/does-not-exist", "finding": "missing"}
    ]


def test_timeline_orders_observations():
    value = module.timeline([{"time": "2026-08-15T10:02:00Z"}, {"time": "2026-08-15T10:01:00Z"}])
    assert [item["time"] for item in value] == ["2026-08-15T10:01:00Z", "2026-08-15T10:02:00Z"]


def test_preservation_must_precede_mutation():
    plan = module.load(module.ROOT / "response/containment-plan.yaml")
    changed = deepcopy(plan)
    changed["actions"][0]["order"] = 9
    assert "mutation-before-preservation" in module.containment_errors(changed)


def test_all_containment_dimensions_are_required():
    plan = module.load(module.ROOT / "response/containment-plan.yaml")
    changed = deepcopy(plan)
    changed["actions"] = [item for item in changed["actions"] if item["id"] != "freeze-release"]
    assert "containment-incomplete" in module.containment_errors(changed)


def test_business_continuity_is_bounded():
    plan = module.load(module.ROOT / "response/containment-plan.yaml")
    changed = deepcopy(plan)
    changed["service_mode"] = "normal"
    assert "business-continuity-unbounded" in module.containment_errors(changed)


def test_business_state_is_preserved_before_workload_isolation():
    plan = module.load(module.ROOT / "response/containment-plan.yaml")
    changed = deepcopy(plan)
    preserve = next(item for item in changed["actions"] if item["id"] == "preserve-business-state")
    preserve["order"] = 9
    assert "business-state-preserved-after-isolation" in module.containment_errors(changed)
