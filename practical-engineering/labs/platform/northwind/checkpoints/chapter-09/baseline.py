from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-09"
    defaults = load(checkpoint / "cases" / "unsafe-defaults.yaml")
    scorecards = load(checkpoint / "cases" / "unsafe-scorecards.yaml")
    bindings = load(checkpoint / "cases" / "unsafe-exceptions.yaml")
    contract = load(ROOT / "paved-road" / "contract.yaml")
    exits = load(ROOT / "paved-road" / "exits.yaml")
    tenants = load(ROOT / "tenancy" / "tenants.yaml")
    catalog = load(ROOT / "catalog" / "systems.yaml")
    users = load(ROOT / "product" / "users.yaml")
    inherited_exceptions = load(
        ROOT / "inherited" / "devsecops-v1.0" / "exceptions" / "records.yaml"
    )
    exception_shape = load(
        ROOT / "inherited" / "devsecops-v1.0" / "exceptions" / "interface.yaml"
    )
    controls = load(ROOT / "inherited" / "devsecops-v1.0" / "controls" / "interface.yaml")
    evidence = load(ROOT / "inherited" / "devsecops-v1.0" / "evidence" / "interface.yaml")
    release = load(ROOT / "inherited" / "devops-v1.1" / "release" / "interface.yaml")
    identity = load(ROOT / "inherited" / "devops-v1.1" / "identity" / "interface.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        defaults,
        scorecards,
        bindings,
        contract,
        exits,
        tenants,
        catalog,
        users,
        inherited_exceptions,
        exception_shape,
        controls,
        evidence,
        release,
        identity,
        expectations,
    )
    required = {
        "guardrails form a golden cage",
        "scorecard reports green without conformance: fulfillment-api",
        "expired inherited exception: exception-dependency-mirror-2026-08",
        "guardrail missing: fulfillment-api/artifact-digest",
        "exception binding copies inherited lifecycle: owner",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 09 baseline: expired exception green scorecard correctly detected")


if __name__ == "__main__":
    main()
