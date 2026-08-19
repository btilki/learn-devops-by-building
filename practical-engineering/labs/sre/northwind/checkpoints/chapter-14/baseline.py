from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-14"
    errors = evaluate(
        load(checkpoint / "cases" / "unsafe-plan.yaml"),
        load(checkpoint / "cases" / "unsafe-trace.yaml"),
        load(checkpoint / "cases" / "unsafe-isolation.yaml"),
        load(checkpoint / "cases" / "unsafe-verification.yaml"),
        load(ROOT / "regions" / "architecture.yaml"),
        load(ROOT / "regions" / "objectives.yaml"),
        load(ROOT / "regions" / "constraints.yaml"),
        load(ROOT / "policy" / "actions.yaml"),
        load(ROOT / "oncall" / "rotations.yaml"),
        load(ROOT / "reliability" / "journeys.yaml"),
        load(ROOT / "slos" / "catalog.yaml"),
        load(checkpoint / "cases" / "unsafe-observations.yaml"),
        load(ROOT / "inherited" / "platform-v1.0" / "recovery" / "interface.yaml"),
        load(ROOT / "inherited" / "platform-v1.0" / "tenancy" / "interface.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
    required = {
        "mixed-region replay applied",
        "mixed-tenant replay accepted",
        "verification emits recovered",
        "inherited restore claimed as portfolio recovery",
        "rto missed: 86400",
        "journey slo not met: accept-and-complete-order/order_success_ratio",
        "verification emits slo_met",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print(
        "chapter 14 baseline: mixed-region replay declared recovered "
        "correctly detected"
    )


if __name__ == "__main__":
    main()
