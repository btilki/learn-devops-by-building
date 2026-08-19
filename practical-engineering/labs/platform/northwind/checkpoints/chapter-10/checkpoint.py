from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 10 checkpoint failed:\n- " + "\n- ".join(errors))
    print("chapter 10 checkpoint: job-completion indicators and non-metrics verified")


if __name__ == "__main__":
    main()
