from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-01"
    brief = load(checkpoint / "cases" / "unsafe-brief.yaml")
    owners = load(checkpoint / "cases" / "unsafe-owners.yaml")
    journeys = load(checkpoint / "cases" / "unsafe-journeys.yaml")
    refusals = {"refusals": []}
    expectations = {
        "required_owners": [],
        "required_journeys": [],
        "required_refusals": [],
        "required_later_proofs": {},
    }
    errors = evaluate(brief, owners, journeys, refusals, expectations)
    required = {
        "brief uses theater success evidence: cluster-uptime",
        "journey has no accountable owner: accept-and-complete-order",
        "journey uses theater later proof: accept-and-complete-order/cluster-uptime",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 01 baseline: uptime-theater success correctly detected")


if __name__ == "__main__":
    main()
