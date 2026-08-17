from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-05"
    burns = load(checkpoint / "cases" / "unsafe-burns.yaml")
    pages = load(checkpoint / "cases" / "unsafe-pages.yaml")
    tickets = load(checkpoint / "cases" / "unsafe-tickets.yaml")
    decisions = load(ROOT / "slis" / "decisions.yaml")
    catalog_iface = load(ROOT / "inherited" / "platform-v1.0" / "catalog" / "interface.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(burns, pages, tickets, decisions, catalog_iface, expectations)
    required = {
        "missing required page: order_success_ratio/fast",
        "missing required page: order_success_ratio/slow",
        "symptom pages: cpu-utilization/storefront-oncall",
        "page emits user impact: page-cpu",
        "job-time pages: time-to-first-environment/storefront-oncall",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print(
        "chapter 05 baseline: cpu paging storefront while order burn is a panel correctly detected"
    )


if __name__ == "__main__":
    main()
