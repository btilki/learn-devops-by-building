from __future__ import annotations

from evaluate import ROOT, evaluate, load


def main() -> None:
    checkpoint = ROOT / "checkpoints" / "chapter-01"
    brief = load(checkpoint / "cases" / "unsafe-brief.yaml")
    users = load(checkpoint / "cases" / "unsafe-users.yaml")
    jobs = load(checkpoint / "cases" / "unsafe-jobs.yaml")
    non_goals = {"non_goals": []}
    expectations = {"required_users": [], "required_jobs": [], "required_non_goals": []}
    errors = evaluate(brief, users, jobs, non_goals, expectations)
    required = {
        "brief uses vanity success evidence: portal-launch",
        "job has no accountable owner: obtain-bounded-environment",
        "job uses vanity later proof: ship-on-paved-road/portal-launch",
    }
    if not required.issubset(set(errors)):
        raise SystemExit(f"baseline did not detect expected weaknesses: {errors}")
    print("chapter 01 baseline: portal-launch success correctly detected")


if __name__ == "__main__":
    main()
