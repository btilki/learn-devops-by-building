from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-02"
    method = load(checkpoint / "cases" / "unsafe-method.yaml")
    candidates = load(checkpoint / "cases" / "unsafe-candidates.yaml")
    decisions = load(checkpoint / "cases" / "unsafe-decisions.yaml")
    journeys = load(ROOT / "reliability" / "journeys.yaml")
    refusals = load(ROOT / "reliability" / "refusals.yaml")
    devex = load(ROOT / "inherited" / "platform-v1.0" / "devex" / "interface.yaml")
    observability = load(
        ROOT / "inherited" / "devops-v1.1" / "observability" / "interface.yaml"
    )
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        method,
        candidates,
        decisions,
        journeys,
        refusals,
        devex,
        observability,
        expectations,
    )
    required = {
        "missing required accept: order_success_ratio",
        "missing required accept: dispatch_success_ratio",
        "missing required adjacent: time-to-first-environment",
        "accept uses forbidden justification: time-to-first-environment/leadership-can-see-it",
        "decision uses forbidden class: time-to-first-environment/portfolio-slo",
        "job-time accepted: time-to-first-environment",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 02 baseline: job-time classed as portfolio-slo correctly detected")


if __name__ == "__main__":
    main()
