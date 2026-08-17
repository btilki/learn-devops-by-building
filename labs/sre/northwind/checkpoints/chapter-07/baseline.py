from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-07"
    definition = load(checkpoint / "cases" / "unsafe-definition.yaml")
    inventory = load(checkpoint / "cases" / "unsafe-inventory.yaml")
    bounds = load(checkpoint / "cases" / "unsafe-bounds.yaml")
    catalog = load(ROOT / "slos" / "catalog.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(definition, inventory, bounds, catalog, expectations)
    required = {
        "bound is not numeric: we-are-busy",
        "bound emits toil fraction rather than computing it",
        "new critical slo allowed: notification-service",
        "inventory item is unclassified: tickets",
        "missing required deny: notification-service",
        "scope uses forbidden justification: "
        "propose-notification-critical-slo/on-call-already-watches-email",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print(
        "chapter 07 baseline: unmeasured toil adding notification "
        "as critical slo correctly detected"
    )


if __name__ == "__main__":
    main()
