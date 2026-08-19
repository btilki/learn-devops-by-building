from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-04"
    systems = load(checkpoint / "cases" / "unsafe-systems.yaml")
    ownership = load(checkpoint / "cases" / "unsafe-ownership.yaml")
    dependencies = load(checkpoint / "cases" / "unsafe-dependencies.yaml")
    tenants = load(ROOT / "tenancy" / "tenants.yaml")
    users = load(ROOT / "product" / "users.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(systems, ownership, dependencies, tenants, users, expectations)
    required = {
        "owner is not living: fulfillment-api/fulfillment-legacy-group",
        "catalog reports green without a living owner: fulfillment-api",
        "stale ownership: fulfillment-api",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 04 baseline: deleted-group green catalog correctly detected")


if __name__ == "__main__":
    main()
