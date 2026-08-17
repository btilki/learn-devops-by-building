import importlib.util
from copy import deepcopy
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-15/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter_15", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_complete_trust_inventory_validates():
    inventory = module.load(module.ROOT / "recovery/trust-inventory.yaml")
    assert module.inventory_errors(inventory) == []
    assert "order-worker-runtime" in module.descendants(inventory, "compromised-artifact")


def test_unknown_trust_graph_dependent_fails():
    inventory = deepcopy(module.load(module.ROOT / "recovery/trust-inventory.yaml"))
    inventory["roots"][0]["dependents"].append("unknown-root")
    assert any(
        error.startswith("trust-dependent-unknown")
        for error in module.inventory_errors(inventory)
    )


def test_trust_graph_cycle_fails():
    inventory = deepcopy(module.load(module.ROOT / "recovery/trust-inventory.yaml"))
    runtime = next(root for root in inventory["roots"] if root["id"] == "order-worker-runtime")
    runtime["dependents"] = ["compromised-artifact"]
    assert "trust-graph-cycle" in module.inventory_errors(inventory)


def test_invalidated_descendant_must_be_rederived_from_trusted_roots():
    inventory = deepcopy(module.load(module.ROOT / "recovery/trust-inventory.yaml"))
    runtime = next(root for root in inventory["roots"] if root["id"] == "order-worker-runtime")
    runtime["status"] = "trusted"
    errors = module.inventory_errors(inventory)
    assert any(error.startswith("invalidated-descendant-not-rederived") for error in errors)
    runtime["derived_from"] = ["rebuilt-artifact"]
    assert module.inventory_errors(inventory) == []


def test_eradication_requires_pause_and_order():
    plan = deepcopy(module.load(module.ROOT / "recovery/eradication-plan.yaml"))
    plan["reconciliation"] = "running"
    next(action for action in plan["actions"] if action["id"] == "invalidate-caches")[
        "order"
    ] = 9
    errors = module.eradication_errors(plan)
    assert "reconciliation-not-paused" in errors
    assert "eradication-order-invalid" in errors


def test_cache_invalidation_removes_invalidated_digest():
    inventory = module.load(module.ROOT / "recovery/trust-inventory.yaml")
    cache = module.load(
        module.ROOT / "checkpoints/chapter-15/cases/persistence-cache-redeploy.yaml"
    )
    invalidated = module.invalidated_digests(inventory)
    assert module.cache_findings(cache, invalidated)
    assert module.cache_findings(module.invalidate_cache(cache, invalidated), invalidated) == []


def test_rebuilt_chain_binds_source_to_runtime():
    manifest = module.load(module.ROOT / "recovery/rebuild-manifest.yaml")
    provenance = module.load(
        module.ROOT / "checkpoints/chapter-15/cases/trusted-rebuild-provenance.yaml"
    )
    deployment = deepcopy(module.load(module.ROOT / "supply-chain/deployment-evidence.yaml"))
    deployment["artifact_digest"] = manifest["rebuilt_artifact_digest"]
    contract = module.load(
        module.ROOT / "checkpoints/chapter-12/cases/order-worker-contract.yaml"
    )
    contract["artifact_digest"] = manifest["rebuilt_artifact_digest"]
    assert (
        module.rebuild_errors(
            manifest,
            provenance,
            deployment,
            contract,
            module.inherited_interfaces(),
        )
        == []
    )


def test_single_recovery_window_is_insufficient():
    windows = deepcopy(
        module.load(
            module.ROOT / "checkpoints/chapter-15/cases/business-outcome-windows.yaml"
        )
    )
    windows["windows"] = windows["windows"][1:2]
    assert "healthy-consecutive-window-count-insufficient" in module.business_window_errors(
        windows, 2
    )


def test_two_consecutive_recovery_windows_pass():
    windows = module.load(
        module.ROOT / "checkpoints/chapter-15/cases/business-outcome-windows.yaml"
    )
    assert module.business_window_errors(windows, 2) == []
    assert module.qualifying_windows(windows, 2) == [
        "recovery-window-1",
        "recovery-window-2",
    ]


def test_nonadjacent_healthy_windows_do_not_pass():
    windows = deepcopy(
        module.load(
            module.ROOT / "checkpoints/chapter-15/cases/business-outcome-windows.yaml"
        )
    )
    windows["windows"] = windows["windows"][1:]
    windows["windows"][1]["observed_at"] = "2026-08-15T11:10:00Z"
    assert "healthy-consecutive-window-count-insufficient" in module.business_window_errors(
        windows, 2
    )


def test_verification_requires_explicit_limitations():
    specification = module.load(module.ROOT / "recovery/verification.yaml")
    actual = {
        "criteria": deepcopy(specification["criteria"]),
        "limitations": [],
        "trust_restored": True,
    }
    assert "recovery-limitations-missing" in module.verification_errors(
        specification, actual
    )


def test_old_automation_denied_while_replacement_allowed():
    chapter_04 = module.load_module("chapter-04", "evaluate")
    subjects, roles, trust = (deepcopy(value) for value in chapter_04.inputs())
    rotation = module.load(
        module.ROOT
        / "checkpoints/chapter-15/cases/missed-release-workflow-credential.yaml"
    )
    old = next(item for item in subjects["subjects"] if item["id"] == "release-workflow")
    old["status"] = "revoked"
    subjects["subjects"] = [
        item
        for item in subjects["subjects"]
        if item["id"] != rotation["replacement_subject"]["id"]
    ]
    subjects["subjects"].append(rotation["replacement_subject"])
    decisions = [
        chapter_04.authorize(
            subject,
            claims,
            "publish-artifact",
            "northwind-registry",
            "build",
            subjects,
            roles,
            trust,
            record=False,
        )["result"]
        for subject, claims in [
            (rotation["old_subject"], rotation["claims"]["old"]),
            (rotation["replacement_subject"]["id"], rotation["claims"]["replacement"]),
        ]
    ]
    assert decisions == ["deny", "allow"]
