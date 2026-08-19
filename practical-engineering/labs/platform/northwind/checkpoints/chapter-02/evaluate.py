from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_DEMAND = {"two-teams-asked", "loudest-ticket", "portal-needed"}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    method: dict,
    candidates: dict,
    decisions: dict,
    jobs: dict,
    non_goals: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    candidate_ids = {item["id"] for item in candidates.get("candidates", [])}
    job_ids = {item["id"] for item in jobs.get("jobs", [])}
    non_goal_by_id = {item["id"]: item for item in non_goals.get("non_goals", [])}
    decision_by_candidate = {
        item["candidate"]: item for item in decisions.get("decisions", [])
    }

    treatments = set(method.get("treatments", []))
    for treatment in expectations.get("required_treatments", []):
        if treatment not in treatments:
            errors.append(f"missing required treatment: {treatment}")

    used_treatments = {item.get("treatment") for item in decisions.get("decisions", [])}
    for treatment in expectations.get("required_treatments", []):
        if treatment not in used_treatments:
            errors.append(f"no decision uses treatment: {treatment}")

    for candidate_id in expectations.get("required_productize", []):
        decision = decision_by_candidate.get(candidate_id)
        if decision is None or decision.get("treatment") != "productize":
            errors.append(f"missing required productize: {candidate_id}")

    for candidate_id in expectations.get("required_decline", []):
        decision = decision_by_candidate.get(candidate_id)
        if decision is None or decision.get("treatment") != "decline":
            errors.append(f"missing required decline: {candidate_id}")

    for decision in decisions.get("decisions", []):
        decision_id = decision.get("id", "unknown")
        candidate_id = decision.get("candidate")
        treatment = decision.get("treatment")
        demand = decision.get("demand", "")

        if candidate_id not in candidate_ids:
            errors.append(f"decision has no known candidate: {decision_id}")

        if not decision.get("repetition"):
            errors.append(f"decision has no repetition: {decision_id}")
        if not decision.get("isolation_impact"):
            errors.append(f"decision has no isolation impact: {decision_id}")
        if not decision.get("support_cost"):
            errors.append(f"decision has no support cost: {decision_id}")
        if not decision.get("owner"):
            errors.append(f"decision has no owner: {decision_id}")
        if not decision.get("review_trigger"):
            errors.append(f"decision has no review trigger: {decision_id}")

        if treatment == "productize":
            user_job = decision.get("user_job")
            if not user_job:
                errors.append(f"productize has no user job: {candidate_id}")
            elif user_job not in job_ids:
                errors.append(f"productize has no known user job: {candidate_id}/{user_job}")
            if demand in FORBIDDEN_DEMAND:
                errors.append(f"productize uses forbidden demand: {candidate_id}/{demand}")
            if candidate_id in non_goal_by_id:
                errors.append(f"non-goal productized: {candidate_id}")

        if treatment in {"leave", "decline"} and not decision.get("remaining_owner"):
            errors.append(f"{treatment} has no remaining owner: {candidate_id}")

        if treatment == "decline" and candidate_id in non_goal_by_id:
            expected_owner = non_goal_by_id[candidate_id].get("remaining_owner")
            if decision.get("remaining_owner") != expected_owner:
                errors.append(f"non-goal remaining owner mismatch: {candidate_id}")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-02"
    return (
        load(ROOT / "intake" / "method.yaml"),
        load(ROOT / "intake" / "candidates.yaml"),
        load(ROOT / "intake" / "decisions.yaml"),
        load(ROOT / "product" / "jobs.yaml"),
        load(ROOT / "product" / "non-goals.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
