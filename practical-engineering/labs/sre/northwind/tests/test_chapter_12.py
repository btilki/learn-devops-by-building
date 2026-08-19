from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-12" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_12_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_regional_architecture_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_unmeasured_rto_and_inherited_restore_fail() -> None:
    (
        architecture,
        objectives,
        constraints,
        platform_recovery,
        tenancy,
        expectations,
    ) = MODULE.completed_inputs()
    objectives["rto"] = "as-fast-as-possible"
    del objectives["rto_seconds"]
    constraints["claims"] = "regional-recovery"
    constraints["insufficient_restores"] = []
    errors = MODULE.evaluate(
        architecture,
        objectives,
        constraints,
        platform_recovery,
        tenancy,
        expectations,
    )
    assert "rto is not numeric: as-fast-as-possible" in errors
    assert "inherited restore claimed as regional recovery" in errors


def test_missing_isolation_and_collapsed_identities_fail() -> None:
    (
        architecture,
        objectives,
        constraints,
        platform_recovery,
        tenancy,
        expectations,
    ) = MODULE.completed_inputs()
    constraints["isolation"]["survives_failover"] = False
    constraints["insufficient_identities"] = ["1.0"]
    constraints["provider_regionality"] = []
    errors = MODULE.evaluate(
        architecture,
        objectives,
        constraints,
        platform_recovery,
        tenancy,
        expectations,
    )
    assert "missing isolation constraint" in errors
    assert "collapsed restore identities" in errors
    assert "missing provider regionality: payment" in errors
