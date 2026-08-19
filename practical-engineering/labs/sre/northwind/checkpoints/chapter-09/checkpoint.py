from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 09 checkpoint failed:\n- " + "\n- ".join(errors))
    print(
        "chapter 09 checkpoint: shed, named burn accounting, "
        "and cascade denial verified"
    )


if __name__ == "__main__":
    main()
