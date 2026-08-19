from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 02 checkpoint failed:\n- " + "\n- ".join(errors))
    print("chapter 02 checkpoint: accept, adjacent, and reject SLI decisions verified")


if __name__ == "__main__":
    main()
