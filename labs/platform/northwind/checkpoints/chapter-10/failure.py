from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

EVALUATE_PATH = Path(__file__).resolve().parent / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_10_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def injected_inputs() -> tuple:
    (
        contract,
        indicators,
        non_metrics,
        samples,
        brief,
        jobs,
        non_goals,
        users,
        observability,
        expectations,
    ) = (copy.deepcopy(item) for item in MODULE.completed_inputs())
    contract["indicators"].append("adoption-percentage")
    indicators["indicators"].append(
        {
            "id": "adoption-percentage",
            "job": "obtain-bounded-environment",
            "owner": "platform-team",
            "class": "platform-product-sli",
            "evidence_kind": "lagging",
        }
    )
    for sample in samples["samples"]:
        if sample["indicator"] == "time-to-first-environment":
            sample["prior_value"] = 48
            sample["value"] = 120
    samples["samples"].append(
        {
            "indicator": "adoption-percentage",
            "observed_at": "2026-08-16T12:00:00Z",
            "value": 100,
            "unit": "percent",
            "unofficial_paths_deleted": True,
        }
    )
    return (
        contract,
        indicators,
        non_metrics,
        samples,
        brief,
        jobs,
        non_goals,
        users,
        observability,
        expectations,
    )


def main() -> None:
    errors = MODULE.evaluate(*injected_inputs())
    required = {
        "vanity indicator: adoption-percentage",
        "adoption hides worse job time",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"failure did not reject adoption vanity: {errors}")
    print("chapter 10 failure: adoption hiding worse time-to-environment correctly rejected")


if __name__ == "__main__":
    main()
