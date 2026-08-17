from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-12"
    architecture = load(checkpoint / "cases" / "unsafe-architecture.yaml")
    objectives = load(checkpoint / "cases" / "unsafe-objectives.yaml")
    constraints = load(checkpoint / "cases" / "unsafe-constraints.yaml")
    platform_recovery = load(
        ROOT / "inherited" / "platform-v1.0" / "recovery" / "interface.yaml"
    )
    tenancy = load(ROOT / "inherited" / "platform-v1.0" / "tenancy" / "interface.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        architecture,
        objectives,
        constraints,
        platform_recovery,
        tenancy,
        expectations,
    )
    required = {
        "inherited restore claimed as regional recovery",
        "rto is not numeric: as-fast-as-possible",
        "missing isolation constraint",
        "missing provider regionality: payment",
        "collapsed restore identities",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print(
        "chapter 12 baseline: inherited restore claimed as regional "
        "recovery correctly detected"
    )


if __name__ == "__main__":
    main()
