from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-06"
    product = load(checkpoint / "cases" / "unsafe-product.yaml")
    requests = load(checkpoint / "cases" / "unsafe-requests.yaml")
    leases = load(checkpoint / "cases" / "unsafe-leases.yaml")
    tenants = load(ROOT / "tenancy" / "tenants.yaml")
    isolation_model = load(ROOT / "tenancy" / "isolation.yaml")
    users = load(ROOT / "product" / "users.yaml")
    jobs = load(ROOT / "product" / "jobs.yaml")
    identity = load(ROOT / "inherited" / "devops-v1.1" / "identity" / "interface.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
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
    required = {
        "cross-tenant mutation: storefront-nonprod/fulfillment-team",
        "shared env admin: storefront-nonprod/dev-cluster-admin",
        "missing lease expiry: fulfillment-nonprod",
        "environment product drops inherited federated identity",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 06 baseline: shared dev-cluster-admin quota steal correctly detected")


if __name__ == "__main__":
    main()
