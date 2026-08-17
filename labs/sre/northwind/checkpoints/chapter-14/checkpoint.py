from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 14 checkpoint failed:\n- " + "\n- ".join(errors))
    print(
        "chapter 14 checkpoint: isolation, rto rpo, and evidence of "
        "portfolio recovery verified"
    )


if __name__ == "__main__":
    main()
