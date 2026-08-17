from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-10"
    command = load(checkpoint / "cases" / "unsafe-command.yaml")
    roles = load(checkpoint / "cases" / "unsafe-roles.yaml")
    traces = load(checkpoint / "cases" / "unsafe-traces.yaml")
    inherited_incident = load(
        ROOT / "inherited" / "devops-v1.1" / "incident" / "interface.yaml"
    )
    inherited_support = load(
        ROOT / "inherited" / "platform-v1.0" / "support" / "interface.yaml"
    )
    systems = load(ROOT / "oncall" / "system.yaml")
    rotations = load(ROOT / "oncall" / "rotations.yaml")
    actions = load(ROOT / "policy" / "actions.yaml")
    journeys = load(ROOT / "reliability" / "journeys.yaml")
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        command,
        roles,
        traces,
        inherited_incident,
        inherited_support,
        systems,
        rotations,
        actions,
        journeys,
        expectations,
    )
    required = {
        "slack-as-commander: spanning-payment-and-dispatch/slack",
        "one-path close: order_success_ratio",
        "missing required journey: dispatch-fulfillment",
        "platform-product landed on storefront",
        "missing freeze join: freeze-storefront-releases",
        "catalog contact treated as system: storefront-oncall",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 10 baseline: one-path close while dispatch fails correctly detected")


if __name__ == "__main__":
    main()
