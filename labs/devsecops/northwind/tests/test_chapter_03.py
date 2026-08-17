import importlib.util
from copy import deepcopy
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-03/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter03", path)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_complete():
    assert m.evaluate(*m.completed_inputs()) == []


def test_missing_uncertainty_fails():
    inputs = list(m.completed_inputs())
    risks = deepcopy(inputs[0])
    risks["risks"][0]["uncertainty"] = []
    inputs[0] = risks
    assert any("missing uncertainty" in x for x in m.evaluate(*inputs))


def test_missing_detection_fails():
    inputs = list(m.completed_inputs())
    decisions = deepcopy(inputs[1])
    decisions["decisions"][0]["controls"] = [
        x for x in decisions["decisions"][0]["controls"] if x["type"] != "detect"
    ]
    inputs[1] = decisions
    assert "priority risk missing detect control" in m.evaluate(*inputs)


def test_missing_risk_context_fails():
    inputs = list(m.completed_inputs())
    risks = deepcopy(inputs[0])
    risks["risks"][0]["owner"] = ""
    risks["risks"][0]["exposure"] = ""
    risks["risks"][0]["review_trigger"] = ""
    inputs[0] = risks
    errors = m.evaluate(*inputs)
    assert any("missing owner" in item for item in errors)
    assert any("missing exposure" in item for item in errors)
    assert any("missing review_trigger" in item for item in errors)
