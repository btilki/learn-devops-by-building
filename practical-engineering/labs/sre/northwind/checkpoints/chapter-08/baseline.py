from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-08"
    catalog = load(checkpoint / "cases" / "unsafe-catalog.yaml")
    criticality = load(checkpoint / "cases" / "unsafe-criticality.yaml")
    contracts = load(checkpoint / "cases" / "unsafe-contracts.yaml")
    journeys = load(ROOT / "reliability" / "journeys.yaml")
    slo_catalog = load(ROOT / "slos" / "catalog.yaml")
    decisions = load(ROOT / "slis" / "decisions.yaml")
    pages = load(ROOT / "alerting" / "pages.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        catalog,
        criticality,
        contracts,
        journeys,
        slo_catalog,
        decisions,
        pages,
        expectations,
    )
    required = {
        "payment failure does not burn storefront: payment",
        "email paged as critical: notification-service",
        "dependency emits no user impact: payment",
        "warehouse not attributed to fulfillment",
        "missing forbidden claim: no-user-impact",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print(
        "chapter 08 baseline: payment no-impact while email pages "
        "storefront correctly detected"
    )


if __name__ == "__main__":
    main()
