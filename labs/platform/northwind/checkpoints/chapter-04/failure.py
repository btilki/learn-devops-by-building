from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

EVALUATE_PATH = Path(__file__).resolve().parent / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_04_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def injected_inputs() -> tuple[dict, dict, dict, dict, dict, dict]:
    systems, ownership, dependencies, tenants, users, expectations = (
        copy.deepcopy(item) for item in MODULE.completed_inputs()
    )
    for entry in ownership["ownership"]:
        if entry["system"] == "fulfillment-api":
            entry["owner"] = "fulfillment-legacy-group"
            entry["reported_status"] = "green"
    return systems, ownership, dependencies, tenants, users, expectations


def main() -> None:
    errors = MODULE.evaluate(*injected_inputs())
    required = {
        "owner is not living: fulfillment-api/fulfillment-legacy-group",
        "catalog reports green without a living owner: fulfillment-api",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"failure did not reject deleted-group owner: {errors}")
    print("chapter 04 failure: catalog correctly rejected a deleted-group owner")


if __name__ == "__main__":
    main()
