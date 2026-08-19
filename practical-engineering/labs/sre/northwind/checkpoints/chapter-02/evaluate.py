from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_JUSTIFICATIONS = {
    "leadership-can-see-it",
    "dashboard-already-has-it",
    "copied-from-storefront",
}
FORBIDDEN_CLASS = "portfolio-slo"
ALLOWED_CLASSES = {
    "user-journey-sli",
    "platform-product-sli",
    "component-uptime",
}
JOB_TIME_PROOFS = {
    "time-to-first-environment",
    "paved-road-completion",
    "catalog-freshness",
}
STOREFRONT_INHERITED = {"order_success_ratio", "order_latency"}
THEATER_CANDIDATES = {"cpu-utilization", "replica-ready", "portal-availability"}
TREATMENT_CLASSES = {
    "accept": "user-journey-sli",
    "adjacent": "platform-product-sli",
    "reject": "component-uptime",
}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    method: dict,
    candidates: dict,
    decisions: dict,
    journeys: dict,
    refusals: dict,
    devex: dict,
    observability: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    candidate_ids = {item["id"] for item in candidates.get("candidates", [])}
    journey_ids = {item["id"] for item in journeys.get("journeys", [])}
    refusal_by_id = {item["id"]: item for item in refusals.get("refusals", [])}
    decision_by_candidate = {
        item["candidate"]: item for item in decisions.get("decisions", [])
    }
    platform_product_slis = set(devex.get("platform_product_slis", []))
    outcome_indicators = set(observability.get("outcome_indicators", []))

    treatments = set(method.get("treatments", []))
    for treatment in expectations.get("required_treatments", []):
        if treatment not in treatments:
            errors.append(f"missing required treatment: {treatment}")

    used_treatments = {item.get("treatment") for item in decisions.get("decisions", [])}
    for treatment in expectations.get("required_treatments", []):
        if treatment not in used_treatments:
            errors.append(f"no decision uses treatment: {treatment}")

    method_forbidden = set(method.get("forbidden_justifications", []))
    for label in FORBIDDEN_JUSTIFICATIONS:
        if label not in method_forbidden:
            errors.append(f"missing forbidden justification: {label}")

    for candidate_id in expectations.get("required_accept", []):
        decision = decision_by_candidate.get(candidate_id)
        if decision is None or decision.get("treatment") != "accept":
            errors.append(f"missing required accept: {candidate_id}")

    for candidate_id in expectations.get("required_adjacent", []):
        decision = decision_by_candidate.get(candidate_id)
        if decision is None or decision.get("treatment") != "adjacent":
            errors.append(f"missing required adjacent: {candidate_id}")

    for candidate_id in expectations.get("required_reject", []):
        decision = decision_by_candidate.get(candidate_id)
        if decision is None or decision.get("treatment") != "reject":
            errors.append(f"missing required reject: {candidate_id}")

    job_time_owner = refusal_by_id.get("platform-job-time-as-slo", {}).get(
        "remaining_owner"
    )
    uptime_owner = refusal_by_id.get("cluster-api-uptime", {}).get("remaining_owner")
    accept_journeys = expectations.get("required_accept_journeys", {})

    for decision in decisions.get("decisions", []):
        decision_id = decision.get("id", "unknown")
        candidate_id = decision.get("candidate")
        treatment = decision.get("treatment")
        class_name = decision.get("class", "")
        justification = decision.get("justification", "")

        if candidate_id not in candidate_ids:
            errors.append(f"decision has no known candidate: {decision_id}")

        if not class_name:
            errors.append(f"decision has no class: {decision_id}")
        if not decision.get("owner"):
            errors.append(f"decision has no owner: {decision_id}")
        if not decision.get("review_trigger"):
            errors.append(f"decision has no review trigger: {decision_id}")

        if class_name == FORBIDDEN_CLASS:
            errors.append(f"decision uses forbidden class: {candidate_id}/{class_name}")
        elif class_name and class_name not in ALLOWED_CLASSES:
            errors.append(f"decision has unknown class: {candidate_id}/{class_name}")
        elif treatment in TREATMENT_CLASSES and class_name != TREATMENT_CLASSES[treatment]:
            errors.append(f"{treatment} has wrong class: {candidate_id}/{class_name}")

        if candidate_id in JOB_TIME_PROOFS and candidate_id not in platform_product_slis:
            errors.append(f"job-time candidate is not inherited: {candidate_id}")
        if candidate_id in STOREFRONT_INHERITED and candidate_id not in outcome_indicators:
            errors.append(f"storefront candidate is not inherited: {candidate_id}")

        if treatment == "accept":
            journey = decision.get("journey")
            if not journey:
                errors.append(f"accept has no journey: {candidate_id}")
            elif journey not in journey_ids:
                errors.append(f"accept has no known journey: {candidate_id}/{journey}")
            expected_journey = accept_journeys.get(candidate_id)
            if expected_journey and journey != expected_journey:
                errors.append(f"accept journey mismatch: {candidate_id}/{journey}")
            if justification in FORBIDDEN_JUSTIFICATIONS:
                errors.append(
                    f"accept uses forbidden justification: {candidate_id}/{justification}"
                )
            if candidate_id in JOB_TIME_PROOFS:
                errors.append(f"job-time accepted: {candidate_id}")
            if candidate_id in THEATER_CANDIDATES:
                errors.append(f"theater accepted: {candidate_id}")

        if treatment in {"adjacent", "reject"} and not decision.get("remaining_owner"):
            errors.append(f"{treatment} has no remaining owner: {candidate_id}")

        if treatment == "adjacent" and candidate_id in JOB_TIME_PROOFS:
            if decision.get("remaining_owner") != job_time_owner:
                errors.append(f"adjacent remaining owner mismatch: {candidate_id}")

        if treatment == "reject" and candidate_id in THEATER_CANDIDATES:
            if decision.get("remaining_owner") != uptime_owner:
                errors.append(f"reject remaining owner mismatch: {candidate_id}")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-02"
    return (
        load(ROOT / "slis" / "method.yaml"),
        load(ROOT / "slis" / "candidates.yaml"),
        load(ROOT / "slis" / "decisions.yaml"),
        load(ROOT / "reliability" / "journeys.yaml"),
        load(ROOT / "reliability" / "refusals.yaml"),
        load(ROOT / "inherited" / "platform-v1.0" / "devex" / "interface.yaml"),
        load(ROOT / "inherited" / "devops-v1.1" / "observability" / "interface.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
