import importlib.util
from copy import deepcopy
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "checkpoints/chapter-13/evaluate.py"
spec = importlib.util.spec_from_file_location("chapter_13", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def prepared():
    contract, hypotheses, rule, events = module.inputs()
    normalized, gaps = module.normalize(events, contract, rule)
    return contract, hypotheses, rule, events, normalized, gaps


def test_complete_path_alerts():
    _, hypotheses, rule, _, normalized, gaps = prepared()
    assert gaps == []
    assert module.correlate(normalized, hypotheses["hypotheses"][0], rule)["result"] == "alert"


def test_runtime_signal_is_ingested_from_chapter_12():
    *_, events, _, _ = prepared()
    runtime = events["events"][-1]
    assert runtime["source"] == "modeled-runtime-sensor"
    assert runtime["action"] == "undeclared-egress"


def test_missing_context_is_a_gap_and_suppresses_path_alert():
    contract, hypotheses, rule, events, _, _ = prepared()
    events = deepcopy(events)
    events["events"][1].pop("artifact_digest")
    normalized, gaps = module.normalize(events, contract, rule)
    assert gaps
    assert module.correlate(normalized, hypotheses["hypotheses"][0], rule)["result"] == "no-alert"


def test_unverified_integrity_is_rejected():
    contract, _, rule, events, _, _ = prepared()
    events = deepcopy(events)
    events["events"][0]["integrity"] = "unverified"
    normalized, gaps = module.normalize(events, contract, rule)
    assert len(normalized) == 3
    assert gaps[0]["invalid"] == ["integrity"]


def test_invalid_retention_contract_is_a_gap():
    contract, _, rule, events, _, _ = prepared()
    contract = deepcopy(contract)
    contract["retention_days"] = 0
    _, gaps = module.normalize(events, contract, rule)
    assert {"event": "contract", "invalid": "retention-days"} in gaps


def test_missing_action_and_late_window_do_not_alert():
    _, hypotheses, rule, _, normalized, _ = prepared()
    assert (
        module.correlate(normalized[:-1], hypotheses["hypotheses"][0], rule)["result"] == "no-alert"
    )
    normalized = deepcopy(normalized)
    normalized[-1]["time"] = "2026-08-15T12:00:00Z"
    assert module.correlate(normalized, hypotheses["hypotheses"][0], rule)["result"] == "no-alert"


def test_duplicate_noise_does_not_replace_distinct_actions():
    _, hypotheses, rule, events, _, _ = prepared()
    repeated = [events["events"][0]] * 10
    assert module.correlate(repeated, hypotheses["hypotheses"][0], rule)["result"] == "no-alert"


def test_unrelated_activity_does_not_join():
    _, hypotheses, rule, _, normalized, _ = prepared()
    normalized = deepcopy(normalized)
    normalized[-1]["artifact_digest"] = "sha256:unrelated"
    assert module.correlate(normalized, hypotheses["hypotheses"][0], rule)["result"] == "no-alert"


def test_rule_controls_the_join():
    _, hypotheses, rule, _, normalized, _ = prepared()
    rule = deepcopy(rule)
    rule["correlation_fields"] = ["subject"]
    assert module.correlate(normalized, hypotheses["hypotheses"][0], rule)["result"] == "no-alert"
