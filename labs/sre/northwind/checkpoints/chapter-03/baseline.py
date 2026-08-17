from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-03"
    catalog = load(checkpoint / "cases" / "unsafe-catalog.yaml")
    windows = load(checkpoint / "cases" / "unsafe-windows.yaml")
    budgets = load(checkpoint / "cases" / "unsafe-budgets.yaml")
    observations = load(checkpoint / "cases" / "unsafe-observations.yaml")
    journeys = load(ROOT / "reliability" / "journeys.yaml")
    decisions = load(ROOT / "slis" / "decisions.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        catalog, windows, budgets, observations, journeys, decisions, expectations
    )
    required = {
        "missing required journey slo: dispatch-fulfillment",
        "catalog emits remaining budget: slo-accept-and-complete-order",
        "sla text used as slo target: slo-accept-and-complete-order",
        "missing sla out-of-scope record: customer-availability-sla",
        "missing required non-critical: notification-service",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 03 baseline: portfolio 99.9 from storefront alone correctly detected")


if __name__ == "__main__":
    main()
