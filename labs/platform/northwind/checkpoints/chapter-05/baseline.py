from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-05"
    contract = load(checkpoint / "cases" / "unsafe-contract.yaml")
    scaffold = load(checkpoint / "cases" / "unsafe-scaffold.yaml")
    conformance = load(checkpoint / "cases" / "unsafe-conformance.yaml")
    exits = load(checkpoint / "cases" / "unsafe-exits.yaml")
    catalog = load(ROOT / "catalog" / "systems.yaml")
    jobs = load(ROOT / "product" / "jobs.yaml")
    users = load(ROOT / "product" / "users.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    release = load(ROOT / "inherited" / "devops-v1.1" / "release" / "interface.yaml")
    identity = load(ROOT / "inherited" / "devops-v1.1" / "identity" / "interface.yaml")
    errors = evaluate(
        contract,
        scaffold,
        conformance,
        exits,
        catalog,
        jobs,
        users,
        expectations,
        release,
        identity,
    )
    required = {
        "unofficial fork: fulfillment-api",
        "missing paved default: fulfillment-api/artifact-digest",
        "missing paved default: fulfillment-api/workload-identity-claims",
        "paved road drops inherited artifact-digest promotion",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 05 baseline: unofficial fork of the paved road correctly detected")


if __name__ == "__main__":
    main()
