from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-06"
    systems = load(checkpoint / "cases" / "unsafe-system.yaml")
    rotations = load(checkpoint / "cases" / "unsafe-rotations.yaml")
    handoffs = load(checkpoint / "cases" / "unsafe-handoffs.yaml")
    authority = load(checkpoint / "cases" / "unsafe-authority.yaml")
    pages = load(ROOT / "alerting" / "pages.yaml")
    tickets = load(ROOT / "alerting" / "tickets.yaml")
    catalog_iface = load(
        ROOT / "inherited" / "platform-v1.0" / "catalog" / "interface.yaml"
    )
    authorization = load(
        ROOT / "inherited" / "devsecops-v1.0" / "authorization" / "interface.yaml"
    )
    expectations = load(checkpoint / "expectations.yaml")
    errors = evaluate(
        systems,
        rotations,
        handoffs,
        authority,
        pages,
        tickets,
        catalog_iface,
        authorization,
        expectations,
    )
    required = {
        "catalog contact treated as system: storefront-oncall",
        "slack-as-primary: storefront-oncall/slack",
        "missing living primary: storefront-oncall",
        "missing required handoff: storefront-chat",
        "platform destination landed on storefront: storefront-oncall-system",
        "self-approval not forbidden: storefront-freeze-authority",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 06 baseline: slack-as-primary without rotation correctly detected")


if __name__ == "__main__":
    main()
