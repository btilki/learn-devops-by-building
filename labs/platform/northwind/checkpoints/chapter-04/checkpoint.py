from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 04 checkpoint failed:\n- " + "\n- ".join(errors))
    print("chapter 04 checkpoint: living owners, dependencies, and freshness verified")


if __name__ == "__main__":
    main()
