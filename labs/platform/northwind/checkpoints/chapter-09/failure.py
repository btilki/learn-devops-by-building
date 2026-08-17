from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

EVALUATE_PATH = Path(__file__).resolve().parent / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_09_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def injected_inputs() -> tuple:
    (
        defaults,
        scorecards,
        bindings,
        contract,
        exits,
        tenants,
        catalog,
        users,
        inherited_exceptions,
        exception_shape,
        controls,
        evidence,
        release,
        identity,
        expectations,
    ) = (copy.deepcopy(item) for item in MODULE.completed_inputs())
    for card in scorecards["scorecards"]:
        if card["system"] == "fulfillment-api":
            card["defaults_present"] = ["workload-identity-claims", "no-cluster-admin"]
            card["exception"] = "exception-dependency-mirror-2026-08"
            card["reported_status"] = "green"
    bindings["bindings"].append(
        {
            "exception": "exception-dependency-mirror-2026-08",
            "tenant": "fulfillment",
            "system": "fulfillment-api",
            "path": "paved",
            "remaining_isolation": ["workload-identity-claims", "no-cluster-admin"],
            "scorecard_effect": "waive-artifact-digest",
        }
    )
    return (
        defaults,
        scorecards,
        bindings,
        contract,
        exits,
        tenants,
        catalog,
        users,
        inherited_exceptions,
        exception_shape,
        controls,
        evidence,
        release,
        identity,
        expectations,
    )


def main() -> None:
    errors = MODULE.evaluate(*injected_inputs())
    required = {
        "scorecard reports green without conformance: fulfillment-api",
        "expired inherited exception: exception-dependency-mirror-2026-08",
        "guardrail missing: fulfillment-api/artifact-digest",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"failure did not reject expired exception scorecard: {errors}")
    print("chapter 09 failure: expired exception and disabled digest correctly rejected")


if __name__ == "__main__":
    main()
