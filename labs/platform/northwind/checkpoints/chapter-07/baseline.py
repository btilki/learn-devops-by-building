from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-07"
    catalog = load(checkpoint / "cases" / "unsafe-catalog.yaml")
    versions = load(checkpoint / "cases" / "unsafe-versions.yaml")
    compatibility = load(checkpoint / "cases" / "unsafe-compatibility.yaml")
    tenants = load(ROOT / "tenancy" / "tenants.yaml")
    isolation = load(ROOT / "tenancy" / "isolation.yaml")
    users = load(ROOT / "product" / "users.yaml")
    release = load(ROOT / "inherited" / "devops-v1.1" / "release" / "interface.yaml")
    identity = load(ROOT / "inherited" / "devops-v1.1" / "identity" / "interface.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
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
    required = {
        "hidden module used as tenant API: storefront-nonprod/terraform-resource-address",
        "identity contract drops inherited federated identity",
        "contract violates isolation: fulfillment-nonprod/peer-tenant-workload-network",
        "missing compatibility policy",
        "tenant parameter missing: fulfillment-nonprod/tenant-storage/class",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 07 baseline: leaked module internals and silent field rename correctly detected")


if __name__ == "__main__":
    main()
