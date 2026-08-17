from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

EVALUATE_PATH = Path(__file__).resolve().parent / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_08_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def injected_inputs() -> tuple:
    (
        product,
        subjects,
        admission,
        reconciliation,
        tenants,
        isolation,
        sharing,
        roles,
        users,
        contract_versions,
        env_product,
        gitops,
        identity,
        release,
        authorization,
        expectations,
    ) = (copy.deepcopy(item) for item in MODULE.completed_inputs())
    for subject in subjects["subjects"]:
        if subject["id"] == "plane-reconciler":
            subject["granted_role"] = "cluster-admin"
    for result in reconciliation["results"]:
        if result["environment"] == "fulfillment-nonprod":
            result["mutated_tenants"] = ["fulfillment", "storefront"]
    return (
        product,
        subjects,
        admission,
        reconciliation,
        tenants,
        isolation,
        sharing,
        roles,
        users,
        contract_versions,
        env_product,
        gitops,
        identity,
        release,
        authorization,
        expectations,
    )


def main() -> None:
    errors = MODULE.evaluate(*injected_inputs())
    required = {
        "shared plane admin: plane-reconciler/cluster-admin",
        "cross-tenant reconcile: fulfillment-nonprod/storefront",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"failure did not reject cluster-admin reconcile: {errors}")
    print("chapter 08 failure: cluster-admin cross-tenant reconcile correctly rejected")


if __name__ == "__main__":
    main()
