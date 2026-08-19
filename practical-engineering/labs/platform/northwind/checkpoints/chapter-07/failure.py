from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

EVALUATE_PATH = Path(__file__).resolve().parent / "evaluate.py"
SPEC = importlib.util.spec_from_file_location("chapter_07_evaluate", EVALUATE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def injected_inputs() -> tuple:
    (
        catalog,
        versions,
        compatibility,
        tenants,
        isolation,
        users,
        release,
        identity,
        expectations,
    ) = (copy.deepcopy(item) for item in MODULE.completed_inputs())
    for version in versions["versions"]:
        if version["capability"] == "tenant-storage":
            version["tenant_parameters"] = ["sku", "size-gb"]
    compatibility["changes"].append(
        {
            "capability": "tenant-storage",
            "version": "1.0",
            "kind": "tenant-parameter-rename",
            "from_field": "class",
            "to_field": "sku",
        }
    )
    return (
        catalog,
        versions,
        compatibility,
        tenants,
        isolation,
        users,
        release,
        identity,
        expectations,
    )


def main() -> None:
    errors = MODULE.evaluate(*injected_inputs())
    required = {
        "breaking change without version: tenant-storage/1.0",
        "missing migration note: tenant-storage/1.0",
        "tenant parameter missing: fulfillment-nonprod/tenant-storage/class",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"failure did not reject silent field rename: {errors}")
    print("chapter 07 failure: silent tenant-parameter rename correctly rejected")


if __name__ == "__main__":
    main()
