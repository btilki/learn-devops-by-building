from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-09"
    modes = load(checkpoint / "cases" / "unsafe-modes.yaml")
    shedding = load(checkpoint / "cases" / "unsafe-shedding.yaml")
    cascade = load(checkpoint / "cases" / "unsafe-cascade.yaml")
    contracts = load(ROOT / "dependencies" / "contracts.yaml")
    journeys = load(ROOT / "reliability" / "journeys.yaml")
    pages = load(ROOT / "alerting" / "pages.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        modes, shedding, cascade, contracts, journeys, pages, expectations
    )
    required = {
        "unbounded retries: payment",
        "missing required shed: payment",
        "degraded success counted as success",
        "fulfillment paged as payment cause",
        "missing user-visible degraded mode",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print(
        "chapter 09 baseline: unbounded payment retries cascading "
        "into fulfillment correctly detected"
    )


if __name__ == "__main__":
    main()
