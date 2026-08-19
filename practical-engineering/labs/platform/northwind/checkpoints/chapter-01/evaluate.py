from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
VANITY_PROOFS = {"portal-launch", "csat", "ticket-volume", "adoption-percentage"}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    brief: dict, users: dict, jobs: dict, non_goals: dict, expectations: dict
) -> list[str]:
    errors: list[str] = []
    user_by_id = {item["id"]: item for item in users.get("users", [])}
    job_by_id = {item["id"]: item for item in jobs.get("jobs", [])}
    non_goal_by_id = {item["id"]: item for item in non_goals.get("non_goals", [])}

    for user_id in expectations.get("required_users", []):
        if user_id not in user_by_id:
            errors.append(f"missing required user: {user_id}")

    for job_id in expectations.get("required_jobs", []):
        if job_id not in job_by_id:
            errors.append(f"missing required job: {job_id}")

    for non_goal_id in expectations.get("required_non_goals", []):
        if non_goal_id not in non_goal_by_id:
            errors.append(f"missing required non-goal: {non_goal_id}")

    owner = brief.get("owner")
    if owner not in user_by_id:
        errors.append(f"brief has no accountable owner: {owner}")

    for proof in brief.get("success_evidence", []):
        if proof in VANITY_PROOFS:
            errors.append(f"brief uses vanity success evidence: {proof}")

    for job_id, job in job_by_id.items():
        if job.get("user") not in user_by_id:
            errors.append(f"job has no known user: {job_id}")
        if job.get("owner") not in user_by_id:
            errors.append(f"job has no accountable owner: {job_id}")
        if not job.get("finished_outcome"):
            errors.append(f"job has no finished outcome: {job_id}")
        proof = job.get("later_proof", "")
        if not proof:
            errors.append(f"job has no later proof: {job_id}")
        elif proof in VANITY_PROOFS:
            errors.append(f"job uses vanity later proof: {job_id}/{proof}")

    for non_goal_id, non_goal in non_goal_by_id.items():
        if not non_goal.get("remaining_owner"):
            errors.append(f"non-goal has no remaining owner: {non_goal_id}")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-01"
    return (
        load(ROOT / "product" / "brief.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(ROOT / "product" / "jobs.yaml"),
        load(ROOT / "product" / "non-goals.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
