from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

EVALUATE_PATH = Path(__file__).resolve().parent / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_12_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def injected_inputs() -> tuple:
    (
        onboarding,
        upgrades,
        deprecations,
        migrations,
        tenants,
        users,
        systems,
        paved_road,
        subjects,
        catalog,
        versions,
        leases,
        quota,
        exceptions,
        gitops,
        expectations,
    ) = (copy.deepcopy(item) for item in MODULE.completed_inputs())
    for upgrade in upgrades["upgrades"]:
        upgrade["freeze"] = {}
        upgrade["result"] = "complete"
        for cohort in upgrade["cohorts"]:
            cohort["status"] = "complete"
    for item in migrations["migrations"]:
        if item["tenant"] == "fulfillment":
            item["applied_version"] = "2.0"
            item["evidence"] = "pending"
    return (
        onboarding,
        upgrades,
        deprecations,
        migrations,
        tenants,
        users,
        systems,
        paved_road,
        subjects,
        catalog,
        versions,
        leases,
        quota,
        exceptions,
        gitops,
        expectations,
    )


def main() -> None:
    errors = MODULE.evaluate(*injected_inputs())
    required = {
        "fleet applied all tenants at once: storage-1-0-to-2-0",
        "fleet upgrade skipped freeze: storage-1-0-to-2-0",
        "tenant contract broken without migration: fulfillment",
        "missing fleet rollback: storage-1-0-to-2-0",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"failure did not reject all-at-once v2 apply: {errors}")
    print("chapter 12 failure: all-at-once v2 apply breaking fulfillment v1 correctly rejected")


if __name__ == "__main__":
    main()
