from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 14 checkpoint failed:\n- " + "\n- ".join(errors))
    print("chapter 14 checkpoint: isolated plane restore and tenant continue/freeze verified")


if __name__ == "__main__":
    main()
