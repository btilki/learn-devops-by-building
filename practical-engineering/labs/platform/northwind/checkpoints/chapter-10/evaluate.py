from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
INHERITED_OBSERVABILITY = (
    ROOT / "inherited" / "devops-v1.1" / "observability" / "interface.yaml"
)
VANITY = {"portal-launch", "csat", "ticket-volume", "adoption-percentage"}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    contract: dict,
    indicators: dict,
    non_metrics: dict,
    samples: dict,
    brief: dict,
    jobs: dict,
    non_goals: dict,
    users: dict,
    observability: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    job_by_id = {item["id"]: item for item in jobs.get("jobs", [])}
    indicator_by_id = {item["id"]: item for item in indicators.get("indicators", [])}
    non_metric_ids = {item["id"] for item in non_metrics.get("non_metrics", [])}
    sampled = {item.get("indicator") for item in samples.get("samples", [])}
    vanity = set(expectations.get("vanity", [])) | VANITY
    tenant_outcomes = set(observability.get("outcome_indicators", []))
    non_goal_ids = {item["id"] for item in non_goals.get("non_goals", [])}
    required = set(brief.get("success_evidence", []))
    for job in jobs.get("jobs", []):
        proof = job.get("later_proof")
        if proof:
            required.add(proof)

    if contract.get("owner") not in user_ids:
        errors.append(f"contract has no known owner: {contract.get('owner')}")
    for indicator_id in contract.get("indicators", []):
        if indicator_id not in indicator_by_id:
            errors.append(f"contract lists unknown indicator: {indicator_id}")
        if indicator_id in vanity:
            errors.append(f"vanity indicator: {indicator_id}")
        if indicator_id in tenant_outcomes:
            errors.append(f"tenant workload used as platform indicator: {indicator_id}")
    for indicator_id in required:
        if indicator_id not in indicator_by_id:
            errors.append(f"missing required indicator: {indicator_id}")
        if indicator_id not in contract.get("indicators", []):
            errors.append(f"contract drops required indicator: {indicator_id}")
        if indicator_id not in sampled:
            errors.append(f"missing sample: {indicator_id}")
        if indicator_id in non_metric_ids:
            errors.append(f"job proof recorded as non-metric: {indicator_id}")
    for vanity_id in vanity:
        if vanity_id not in non_metric_ids:
            errors.append(f"missing non-metric: {vanity_id}")
        if vanity_id in indicator_by_id:
            errors.append(f"vanity indicator: {vanity_id}")
    for outcome in tenant_outcomes:
        if outcome not in non_metric_ids:
            errors.append(f"missing non-metric: {outcome}")
        if outcome in indicator_by_id:
            errors.append(f"tenant workload used as platform indicator: {outcome}")
    for item in non_metrics.get("non_metrics", []):
        item_id = item.get("id")
        category = item.get("category")
        expected = None
        if item_id in vanity:
            expected = "vanity"
        elif item_id in tenant_outcomes:
            expected = "tenant-workload"
        if expected is not None and category != expected:
            errors.append(f"non-metric category mismatch: {item_id}")
        if expected is None and category in {"vanity", "tenant-workload"}:
            errors.append(f"non-metric category mismatch: {item_id}")

    for item in indicators.get("indicators", []):
        indicator_id = item.get("id")
        job_id = item.get("job")
        job = job_by_id.get(job_id, {})
        if item.get("owner") not in user_ids:
            errors.append(f"indicator has no known owner: {indicator_id}")
        if job_id not in job_by_id:
            errors.append(f"indicator has no known job: {indicator_id}")
        if item.get("class") == "portfolio-slo":
            errors.append(f"platform indicator treated as portfolio slo: {indicator_id}")
        if indicator_id in non_goal_ids:
            errors.append(f"non-goal used as indicator: {indicator_id}")

    for job_id, job in job_by_id.items():
        proof = job.get("later_proof")
        mapped = indicator_by_id.get(proof, {})
        if mapped and mapped.get("job") != job_id:
            errors.append(f"indicator job mismatch: {proof}")

    adoption_hides = False
    ttf_worse = False
    for sample in samples.get("samples", []):
        indicator_id = sample.get("indicator")
        if indicator_id not in indicator_by_id and indicator_id not in vanity:
            errors.append(f"sample has no known indicator: {indicator_id}")
        if (
            indicator_id == "adoption-percentage"
            and sample.get("value") == 100
            and sample.get("unofficial_paths_deleted")
        ):
            adoption_hides = True
        if indicator_id == "time-to-first-environment":
            prior = sample.get("prior_value")
            if prior is not None and sample.get("value", prior) > prior:
                ttf_worse = True
    if adoption_hides and ttf_worse:
        errors.append("adoption hides worse job time")

    return errors


def completed_inputs() -> tuple:
    checkpoint = ROOT / "checkpoints" / "chapter-10"
    return (
        load(ROOT / "devex" / "contract.yaml"),
        load(ROOT / "devex" / "indicators.yaml"),
        load(ROOT / "devex" / "non-metrics.yaml"),
        load(ROOT / "devex" / "samples.yaml"),
        load(ROOT / "product" / "brief.yaml"),
        load(ROOT / "product" / "jobs.yaml"),
        load(ROOT / "product" / "non-goals.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(INHERITED_OBSERVABILITY),
        load(checkpoint / "expectations.yaml"),
    )
