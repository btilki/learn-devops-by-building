from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

EVALUATE_PATH = Path(__file__).resolve().parent / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_05_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def injected_inputs() -> tuple:
    (
        contract,
        scaffold,
        conformance,
        exits,
        catalog,
        jobs,
        users,
        expectations,
        release,
        identity,
    ) = (copy.deepcopy(item) for item in MODULE.completed_inputs())
    for entry in conformance["entries"]:
        if entry["system"] == "fulfillment-api":
            entry["path"] = "unofficial"
            entry["defaults_present"] = ["latest-tag"]
            entry.pop("exit", None)
    return (
        contract,
        scaffold,
        conformance,
        exits,
        catalog,
        jobs,
        users,
        expectations,
        release,
        identity,
    )


def main() -> None:
    errors = MODULE.evaluate(*injected_inputs())
    required = {
        "unofficial fork: fulfillment-api",
        "missing paved default: fulfillment-api/artifact-digest",
        "missing paved default: fulfillment-api/workload-identity-claims",
        "forbidden default: fulfillment-api/latest-tag",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"failure did not reject unofficial fork: {errors}")
    print("chapter 05 failure: unofficial fork correctly rejected")


if __name__ == "__main__":
    main()
