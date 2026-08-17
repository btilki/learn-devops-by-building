from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 07 checkpoint failed:\n- " + "\n- ".join(errors))
    print(
        "chapter 07 checkpoint: classified inventory, numeric bound, "
        "and blocked notification SLO verified"
    )


if __name__ == "__main__":
    main()
