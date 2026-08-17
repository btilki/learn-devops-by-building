from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-03"
    tenants = load(checkpoint / "cases" / "unsafe-tenants.yaml")
    isolation = load(checkpoint / "cases" / "unsafe-isolation.yaml")
    roles = load(checkpoint / "cases" / "unsafe-roles.yaml")
    sharing = load(checkpoint / "cases" / "unsafe-sharing.yaml")
    users = load(ROOT / "product" / "users.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(tenants, isolation, roles, sharing, users, expectations)
    required = {
        "tenant inherits prohibited role: fulfillment/cluster-admin",
        "missing prohibited inherited role: fulfillment/cluster-admin",
        "tenant missing isolation dimension: fulfillment/change-authority",
        "sharing does not deny: cluster-admin",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 03 baseline: temporary cluster-admin inheritance correctly detected")


if __name__ == "__main__":
    main()
