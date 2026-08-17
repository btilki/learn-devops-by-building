from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-14"
    errors = evaluate(
        load(checkpoint / "cases" / "unsafe-plane-evidence.yaml"),
        load(checkpoint / "cases" / "unsafe-isolation.yaml"),
        load(checkpoint / "cases" / "unsafe-restore-trace.yaml"),
        load(checkpoint / "cases" / "unsafe-verification.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(ROOT / "tenancy" / "tenants.yaml"),
        load(ROOT / "tenancy" / "isolation.yaml"),
        load(ROOT / "environments" / "leases.yaml"),
        load(ROOT / "control-plane" / "subjects.yaml"),
        load(ROOT / "control-plane" / "product.yaml"),
        load(ROOT / "control-plane" / "reconciliation.yaml"),
        load(ROOT / "quota" / "tenants.yaml"),
        load(ROOT / "fleet" / "upgrades.yaml"),
        load(ROOT / "fleet" / "migrations.yaml"),
        load(ROOT / "support" / "changes.yaml"),
        load(ROOT / "support" / "incidents.yaml"),
        load(ROOT / "inherited" / "devops-v1.1" / "recovery" / "interface.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
    required = {
        "mixed backup restore: restore-newest-mixed",
        "cross-tenant replay: storefront/fulfillment",
        "missing last known good: restore-newest-mixed",
        "accidental tenant freeze: storefront",
        "platform recovered uses tenant workload: order_success_ratio",
        "plane self-approval: restore-newest-mixed",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print(
        "chapter 14 baseline: mixed-backup restore replaying fulfillment "
        "into storefront correctly detected"
    )


if __name__ == "__main__":
    main()
