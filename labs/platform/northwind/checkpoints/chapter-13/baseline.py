from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-13"
    errors = evaluate(
        load(checkpoint / "cases" / "unsafe-model.yaml"),
        load(checkpoint / "cases" / "unsafe-escalation.yaml"),
        load(checkpoint / "cases" / "unsafe-changes.yaml"),
        load(checkpoint / "cases" / "unsafe-incidents.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(ROOT / "catalog" / "systems.yaml"),
        load(ROOT / "catalog" / "ownership.yaml"),
        load(ROOT / "control-plane" / "subjects.yaml"),
        load(ROOT / "control-plane" / "product.yaml"),
        load(ROOT / "control-plane" / "reconciliation.yaml"),
        load(ROOT / "product" / "brief.yaml"),
        load(ROOT / "devex" / "indicators.yaml"),
        load(ROOT / "devex" / "non-metrics.yaml"),
        load(ROOT / "inherited" / "devops-v1.1" / "observability" / "interface.yaml"),
        load(ROOT / "inherited" / "devops-v1.1" / "incident" / "interface.yaml"),
        load(ROOT / "inherited" / "devsecops-v1.0" / "evidence" / "interface.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
    required = {
        "unofficial plane-admin change: live-plane-patch",
        "plane self-approval: live-plane-patch",
        "missing last known good: live-plane-patch",
        "escalation is chat-history: fulfillment-api",
        "incident closed for vanity: fulfillment-warehouse-delay",
        "job-time budget uses tenant workload: order_success_ratio",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 13 baseline: unofficial plane-admin patch correctly detected")


if __name__ == "__main__":
    main()
