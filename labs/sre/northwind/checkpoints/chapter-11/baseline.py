from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-11"
    program = load(checkpoint / "cases" / "unsafe-program.yaml")
    records = load(checkpoint / "cases" / "unsafe-records.yaml")
    actions = load(checkpoint / "cases" / "unsafe-actions.yaml")
    traces = load(ROOT / "incidents" / "traces.yaml")
    shedding = load(ROOT / "degradation" / "shedding.yaml")
    bounds = load(ROOT / "toil" / "bounds.yaml")
    evidence = load(
        ROOT / "inherited" / "devsecops-v1.0" / "evidence" / "interface.yaml"
    )
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        program, records, actions, traces, shedding, bounds, evidence, expectations
    )
    required = {
        "hortatory action: be-more-careful",
        "missing independent verification",
        "missing required record: platform-product-job-time",
        "repeated cascade without verified action",
        "record verifies itself: polished-postmortem",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print(
        "chapter 11 baseline: hortatory postmortem without verified "
        "action correctly detected"
    )


if __name__ == "__main__":
    main()
