from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-04"
    policy = load(ROOT / "policy" / "error-budget.yaml")
    actions = load(checkpoint / "cases" / "unsafe-actions.yaml")
    exceptions = load(checkpoint / "cases" / "unsafe-exceptions.yaml")
    catalog = load(ROOT / "slos" / "catalog.yaml")
    observations = load(ROOT / "fixtures" / "observations" / "chapter-04.yaml")
    fleet = load(ROOT / "inherited" / "platform-v1.0" / "fleet" / "interface.yaml")
    release = load(ROOT / "inherited" / "devops-v1.1" / "release" / "interface.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        policy, actions, exceptions, catalog, observations, fleet, release, expectations
    )
    required = {
        "unfrozen exhausted budget: storage-1-0-to-2-0",
        "fleet freeze copies platform field: freeze",
        "fleet freeze copies platform field: rollback",
        "fleet freeze relabels platform upgrade freeze: platform-upgrade-freeze",
        "exception has no expiry: exception-ship-anyway",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print(
        "chapter 04 baseline: unfrozen fleet under exhausted storefront budget correctly detected"
    )


if __name__ == "__main__":
    main()
