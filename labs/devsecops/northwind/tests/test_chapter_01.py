from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-01" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_01_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_security_model_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_unknown_owner_and_missing_harm_fail() -> None:
    assets, ownership, invariants, expectations = MODULE.completed_inputs()
    assets["assets"][0]["owner"] = "unknown-team"
    assets["assets"][0]["harms"] = []
    errors = MODULE.evaluate(assets, ownership, invariants, expectations)
    assert "asset has no defined harm: order-outcome" in errors
    assert "asset has no accountable owner: order-outcome" in errors


def test_unknown_invariant_asset_fails() -> None:
    assets, ownership, invariants, expectations = MODULE.completed_inputs()
    invariants["invariants"][0]["assets"].append("unknown-asset")
    errors = MODULE.evaluate(assets, ownership, invariants, expectations)
    expected = "invariant references unknown asset: correct-order-terminal-state/unknown-asset"
    assert expected in errors
