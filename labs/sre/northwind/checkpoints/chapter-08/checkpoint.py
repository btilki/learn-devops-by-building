from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 08 checkpoint failed:\n- " + "\n- ".join(errors))
    print("chapter 08 checkpoint: attributed burns and non-critical email verified")


if __name__ == "__main__":
    main()
