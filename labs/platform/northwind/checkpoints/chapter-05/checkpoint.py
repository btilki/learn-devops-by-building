from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 05 checkpoint failed:\n- " + "\n- ".join(errors))
    print("chapter 05 checkpoint: paved-road completion and supported exit verified")


if __name__ == "__main__":
    main()
