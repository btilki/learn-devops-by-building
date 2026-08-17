from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-01"
    unsafe_assets = load(checkpoint / "cases" / "unsafe-assets.yaml")
    ownership = {"owners": []}
    invariants = {"invariants": []}
    expectations = {"required_assets": [], "required_invariants": []}
    errors = evaluate(unsafe_assets, ownership, invariants, expectations)
    required = {
        "asset has no defined harm: payment-token",
        "asset has no accountable owner: payment-token",
    }
    if not required.issubset(errors):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 01 baseline: unsafe asset classification correctly detected")


if __name__ == "__main__":
    main()
