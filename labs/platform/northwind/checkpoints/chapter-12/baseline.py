from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-12"
    gitops = load(ROOT / "inherited" / "devops-v1.1" / "gitops" / "interface.yaml")
    errors = evaluate(
        load(checkpoint / "cases" / "unsafe-onboarding.yaml"),
        load(checkpoint / "cases" / "unsafe-upgrades.yaml"),
        load(checkpoint / "cases" / "unsafe-deprecations.yaml"),
        load(checkpoint / "cases" / "unsafe-migrations.yaml"),
        load(ROOT / "tenancy" / "tenants.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(ROOT / "catalog" / "systems.yaml"),
        load(ROOT / "paved-road" / "contract.yaml"),
        load(ROOT / "control-plane" / "subjects.yaml"),
        load(ROOT / "contracts" / "catalog.yaml"),
        load(ROOT / "contracts" / "versions.yaml"),
        load(ROOT / "environments" / "leases.yaml"),
        load(ROOT / "quota" / "tenants.yaml"),
        load(ROOT / "guardrails" / "exceptions.yaml"),
        gitops,
        load(checkpoint / "expectations.yaml"),
    )
    required = {
        "onboarding grants cluster-admin: fulfillment",
        "fleet applied all tenants at once: storage-1-0-to-2-0",
        "fleet upgrade skipped freeze: storage-1-0-to-2-0",
        "tenant contract broken without migration: fulfillment",
        "deprecation window closed with remaining tenant: fulfillment",
        "missing fleet rollback: storage-1-0-to-2-0",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 12 baseline: all-at-once v2 apply breaking fulfillment v1 correctly detected")


if __name__ == "__main__":
    main()
