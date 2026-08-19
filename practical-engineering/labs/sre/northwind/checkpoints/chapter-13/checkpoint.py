from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 13 checkpoint failed:\n- " + "\n- ".join(errors))
    print(
        "chapter 13 checkpoint: freeze, page path, dependency, "
        "and regional tabletop coverage verified"
    )


if __name__ == "__main__":
    main()
