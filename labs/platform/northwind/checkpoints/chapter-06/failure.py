from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

EVALUATE_PATH = Path(__file__).resolve().parent / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_06_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def injected_inputs() -> tuple:
    (
        product,
        requests,
        leases,
        tenants,
        isolation_model,
        users,
        jobs,
        identity,
        expectations,
    ) = (copy.deepcopy(item) for item in MODULE.completed_inputs())
    for lease in leases["leases"]:
        if lease["environment"] == "storefront-nonprod":
            lease["mutated_by"] = "fulfillment-team"
            lease["granted_role"] = "dev-cluster-admin"
    return (
        product,
        requests,
        leases,
        tenants,
        isolation_model,
        users,
        jobs,
        identity,
        expectations,
    )


def main() -> None:
    errors = MODULE.evaluate(*injected_inputs())
    required = {
        "cross-tenant mutation: storefront-nonprod/fulfillment-team",
        "shared env admin: storefront-nonprod/dev-cluster-admin",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"failure did not reject cross-tenant scale: {errors}")
    print("chapter 06 failure: cross-tenant environment scale correctly rejected")


if __name__ == "__main__":
    main()
