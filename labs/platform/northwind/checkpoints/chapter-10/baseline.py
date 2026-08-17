from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-10"
    contract = load(checkpoint / "cases" / "unsafe-contract.yaml")
    indicators = load(checkpoint / "cases" / "unsafe-indicators.yaml")
    non_metrics = load(checkpoint / "cases" / "unsafe-non-metrics.yaml")
    samples = load(checkpoint / "cases" / "unsafe-samples.yaml")
    brief = load(ROOT / "product" / "brief.yaml")
    jobs = load(ROOT / "product" / "jobs.yaml")
    non_goals = load(ROOT / "product" / "non-goals.yaml")
    users = load(ROOT / "product" / "users.yaml")
    observability = load(ROOT / "inherited" / "devops-v1.1" / "observability" / "interface.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        contract,
        indicators,
        non_metrics,
        samples,
        brief,
        jobs,
        non_goals,
        users,
        observability,
        expectations,
    )
    required = {
        "vanity indicator: adoption-percentage",
        "missing sample: catalog-freshness",
        "missing non-metric: adoption-percentage",
        "tenant workload used as platform indicator: order_success_ratio",
        "platform indicator treated as portfolio slo: order_success_ratio",
        "adoption hides worse job time",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 10 baseline: adoption vanity and missing job samples correctly detected")


if __name__ == "__main__":
    main()
