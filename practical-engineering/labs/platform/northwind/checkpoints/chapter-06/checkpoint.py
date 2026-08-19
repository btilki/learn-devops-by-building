from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 06 checkpoint failed:\n- " + "\n- ".join(errors))
    print("chapter 06 checkpoint: tenant-scoped leases and isolation invariants verified")


if __name__ == "__main__":
    main()
