from __future__ import annotations

from evaluate import completed_inputs, evaluate


def main() -> None:
    errors = evaluate(*completed_inputs())
    if errors:
        raise SystemExit("chapter 01 checkpoint failed:\n- " + "\n- ".join(errors))
    print(
        "chapter 01 checkpoint: product users, jobs, refusals, "
        "and job-completion evidence verified"
    )


if __name__ == "__main__":
    main()
