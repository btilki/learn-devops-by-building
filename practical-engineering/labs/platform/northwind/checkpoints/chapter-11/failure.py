from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

EVALUATE_PATH = Path(__file__).resolve().parent / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_11_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def injected_inputs() -> tuple:
    (
        policy,
        units,
        showback,
        tenants,
        isolation,
        sharing,
        users,
        leases,
        env_product,
        indicators,
        samples,
        non_metrics,
        expectations,
    ) = (copy.deepcopy(item) for item in MODULE.completed_inputs())
    for entry in showback["entries"]:
        if entry["tenant"] == "fulfillment" and entry["unit"] == "environment-hour":
            entry["usage"] = 24
            entry["billed_units"] = 24
    return (
        policy,
        units,
        showback,
        tenants,
        isolation,
        sharing,
        users,
        leases,
        env_product,
        indicators,
        samples,
        non_metrics,
        expectations,
    )


def main() -> None:
    errors = MODULE.evaluate(*injected_inputs())
    required = {
        "tenant exceeds ceiling: fulfillment",
        "peer floor starved: storefront",
        "unlimited burst into peer quota: fulfillment",
        "showback counts starved burst as useful unit: fulfillment",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"failure did not reject fulfillment burst: {errors}")
    print("chapter 11 failure: fulfillment burst consuming storefront floor correctly rejected")


if __name__ == "__main__":
    main()
