from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-08"
    product = load(checkpoint / "cases" / "unsafe-product.yaml")
    subjects = load(checkpoint / "cases" / "unsafe-subjects.yaml")
    admission = load(checkpoint / "cases" / "unsafe-admission.yaml")
    reconciliation = load(checkpoint / "cases" / "unsafe-reconciliation.yaml")
    tenants = load(ROOT / "tenancy" / "tenants.yaml")
    isolation = load(ROOT / "tenancy" / "isolation.yaml")
    sharing = load(ROOT / "tenancy" / "sharing.yaml")
    roles = load(ROOT / "tenancy" / "roles.yaml")
    users = load(ROOT / "product" / "users.yaml")
    contract_versions = load(ROOT / "contracts" / "versions.yaml")
    env_product = load(ROOT / "environments" / "product.yaml")
    gitops = load(ROOT / "inherited" / "devops-v1.1" / "gitops" / "interface.yaml")
    identity = load(ROOT / "inherited" / "devops-v1.1" / "identity" / "interface.yaml")
    release = load(ROOT / "inherited" / "devops-v1.1" / "release" / "interface.yaml")
    authorization = load(ROOT / "inherited" / "devsecops-v1.0" / "authorization" / "interface.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        product,
        subjects,
        admission,
        reconciliation,
        tenants,
        isolation,
        sharing,
        roles,
        users,
        contract_versions,
        env_product,
        gitops,
        identity,
        release,
        authorization,
        expectations,
    )
    required = {
        "shared plane admin: plane-reconciler/cluster-admin",
        "cross-tenant reconcile: fulfillment-nonprod/storefront",
        "plane self-approval: plane-upgrade-1-1",
        "missing last known good: plane-upgrade-1-1",
        "control plane drops inherited federated identity",
        "controller rewrites source",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 08 baseline: cluster-admin reconciler correctly detected")


if __name__ == "__main__":
    main()
