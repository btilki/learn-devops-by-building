from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATE_PATH = ROOT / "checkpoints" / "chapter-02" / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_02_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_completed_threat_model_passes() -> None:
    assert MODULE.evaluate(*MODULE.completed_inputs()) == []


def test_unknown_flow_fails() -> None:
    inputs = list(MODULE.completed_inputs())
    paths = deepcopy(inputs[2])
    paths["attack_paths"][0]["steps"][0]["flow"] = "unknown-flow"
    inputs[2] = paths
    errors = MODULE.evaluate(*inputs)
    assert any("attack step references unknown flow" in error for error in errors)


def test_boundary_disagreement_fails() -> None:
    inputs = list(MODULE.completed_inputs())
    paths = deepcopy(inputs[2])
    paths["attack_paths"][0]["steps"][0]["boundary"] = "source-to-build"
    inputs[2] = paths
    errors = MODULE.evaluate(*inputs)
    assert any("attack step boundary disagrees with flow" in error for error in errors)


def test_missing_priority_invariant_coverage_fails() -> None:
    inputs = list(MODULE.completed_inputs())
    paths = deepcopy(inputs[2])
    for path in paths["attack_paths"]:
        path["threatens"] = [item for item in path["threatens"] if item != "governed-order-data"]
    inputs[2] = paths
    errors = MODULE.evaluate(*inputs)
    assert "priority invariant has no modeled attack path: governed-order-data" in errors
