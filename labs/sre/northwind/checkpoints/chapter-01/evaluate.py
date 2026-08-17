from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
THEATER_PROOFS = {
    "cluster-uptime",
    "api-uptime",
    "kubelet-ready",
    "portal-availability",
    "five-nines",
}
JOB_TIME_PROOFS = {
    "time-to-first-environment",
    "paved-road-completion",
    "catalog-freshness",
}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    brief: dict, owners: dict, journeys: dict, refusals: dict, expectations: dict
) -> list[str]:
    errors: list[str] = []
    owner_by_id = {item["id"]: item for item in owners.get("owners", [])}
    journey_by_id = {item["id"]: item for item in journeys.get("journeys", [])}
    refusal_by_id = {item["id"]: item for item in refusals.get("refusals", [])}

    for owner_id in expectations.get("required_owners", []):
        if owner_id not in owner_by_id:
            errors.append(f"missing required owner: {owner_id}")

    for journey_id in expectations.get("required_journeys", []):
        if journey_id not in journey_by_id:
            errors.append(f"missing required journey: {journey_id}")

    for refusal_id in expectations.get("required_refusals", []):
        if refusal_id not in refusal_by_id:
            errors.append(f"missing required refusal: {refusal_id}")

    expected_brief_owner = expectations.get("brief_owner")
    owner = brief.get("owner")
    if expected_brief_owner and owner != expected_brief_owner:
        errors.append(f"brief has no accountable owner: {owner}")
    elif owner not in owner_by_id:
        errors.append(f"brief has no accountable owner: {owner}")

    for proof in brief.get("success_evidence", []):
        if proof in THEATER_PROOFS:
            errors.append(f"brief uses theater success evidence: {proof}")
        elif proof in JOB_TIME_PROOFS:
            errors.append(f"brief uses job-time success evidence: {proof}")

    required_later_proofs = expectations.get("required_later_proofs", {})
    for journey_id, journey in journey_by_id.items():
        if journey.get("user") not in owner_by_id:
            errors.append(f"journey has no known user: {journey_id}")
        if journey.get("owner") not in owner_by_id:
            errors.append(f"journey has no accountable owner: {journey_id}")
        if not journey.get("failed_outcome"):
            errors.append(f"journey has no failed outcome: {journey_id}")
        proof = journey.get("later_proof", "")
        if not proof:
            errors.append(f"journey has no later proof: {journey_id}")
        elif proof in THEATER_PROOFS:
            errors.append(f"journey uses theater later proof: {journey_id}/{proof}")
        elif proof in JOB_TIME_PROOFS:
            errors.append(f"journey uses job-time later proof: {journey_id}/{proof}")
        expected_proof = required_later_proofs.get(journey_id)
        if expected_proof and proof != expected_proof:
            errors.append(
                f"journey later proof is not the required proof: {journey_id}/{proof}"
            )

    for refusal_id, refusal in refusal_by_id.items():
        if not refusal.get("remaining_owner"):
            errors.append(f"refusal has no remaining owner: {refusal_id}")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-01"
    return (
        load(ROOT / "reliability" / "brief.yaml"),
        load(ROOT / "reliability" / "owners.yaml"),
        load(ROOT / "reliability" / "journeys.yaml"),
        load(ROOT / "reliability" / "refusals.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
