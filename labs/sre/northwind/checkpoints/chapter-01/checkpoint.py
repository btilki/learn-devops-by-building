from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 01 checkpoint failed:\n- " + "\n- ".join(errors))
    print(
        "chapter 01 checkpoint: reliability owners, journeys, refusals, "
        "and journey-completion evidence verified"
    )


if __name__ == "__main__":
    main()
