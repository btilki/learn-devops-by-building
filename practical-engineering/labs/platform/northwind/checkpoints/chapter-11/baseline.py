from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-11"
    policy = load(checkpoint / "cases" / "unsafe-tenants.yaml")
    units = load(checkpoint / "cases" / "unsafe-units.yaml")
    showback = load(checkpoint / "cases" / "unsafe-showback.yaml")
    tenants = load(ROOT / "tenancy" / "tenants.yaml")
    isolation = load(ROOT / "tenancy" / "isolation.yaml")
    sharing = load(ROOT / "tenancy" / "sharing.yaml")
    users = load(ROOT / "product" / "users.yaml")
    leases = load(ROOT / "environments" / "leases.yaml")
    env_product = load(ROOT / "environments" / "product.yaml")
    indicators = load(ROOT / "devex" / "indicators.yaml")
    samples = load(ROOT / "devex" / "samples.yaml")
    non_metrics = load(ROOT / "devex" / "non-metrics.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
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
    required = {
        "missing tenant floor: storefront",
        "peer floor starved: storefront",
        "unlimited burst into peer quota: fulfillment",
        "showback counts starved burst as useful unit: fulfillment",
        "showback unit is tenant workload: order_success_ratio",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 11 baseline: fulfillment burst starving storefront floor correctly detected")


if __name__ == "__main__":
    main()
