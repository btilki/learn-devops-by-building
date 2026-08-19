from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-02"
    method = load(checkpoint / "cases" / "unsafe-method.yaml")
    candidates = load(checkpoint / "cases" / "unsafe-candidates.yaml")
    decisions = load(checkpoint / "cases" / "unsafe-decisions.yaml")
    jobs = load(ROOT / "product" / "jobs.yaml")
    non_goals = load(ROOT / "product" / "non-goals.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(method, candidates, decisions, jobs, non_goals, expectations)
    required = {
        "non-goal productized: order-pricing-logic",
        "productize uses forbidden demand: order-pricing-logic/two-teams-asked",
        "missing required productize: environment-provisioning",
        "missing required decline: order-pricing-logic",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 02 baseline: two-teams-asked productization correctly detected")


if __name__ == "__main__":
    main()
