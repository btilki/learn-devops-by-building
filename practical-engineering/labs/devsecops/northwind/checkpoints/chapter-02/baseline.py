from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-02"
    system = load(ROOT / "threat-model" / "system.yaml")
    boundaries = load(ROOT / "threat-model" / "boundaries.yaml")
    invariants = load(ROOT / "security-model" / "invariants.yaml")
    unsafe_paths = load(checkpoint / "cases" / "unsafe-paths.yaml")
    errors = evaluate(system, boundaries, unsafe_paths, invariants, {})
    required_fragments = ["unknown invariant", "unknown flow"]
    if not all(any(fragment in error for error in errors) for fragment in required_fragments):
        raise SystemExit(f"baseline did not detect generic threat-model defects: {errors}")
    print("chapter 02 baseline: generic, untraceable attack path correctly rejected")


if __name__ == "__main__":
    main()
