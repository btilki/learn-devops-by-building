from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-13"
    program = load(checkpoint / "cases" / "unsafe-program.yaml")
    scenarios = load(checkpoint / "cases" / "unsafe-scenarios.yaml")
    results = load(checkpoint / "cases" / "unsafe-results.yaml")
    policy_actions = load(ROOT / "policy" / "actions.yaml")
    oncall = load(ROOT / "oncall" / "system.yaml")
    learning_actions = load(ROOT / "learning" / "actions.yaml")
    architecture = load(ROOT / "regions" / "architecture.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        program,
        scenarios,
        results,
        policy_actions,
        oncall,
        learning_actions,
        architecture,
        expectations,
    )
    required = {
        "single mixed-backup completes program",
        "cadence is not recurrence: annual",
        "missing abort",
        "missing required scenario: error-budget-freeze",
        "missing learning join",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print(
        "chapter 13 baseline: single mixed-backup game day marked "
        "complete correctly detected"
    )


if __name__ == "__main__":
    main()
