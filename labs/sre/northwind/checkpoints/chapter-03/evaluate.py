from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
JOB_TIME_PROOFS = {
    "time-to-first-environment",
    "paved-road-completion",
    "catalog-freshness",
}
THEATER_INDICATORS = {
    "cpu-utilization",
    "replica-ready",
    "portal-availability",
    "cluster-uptime",
    "api-uptime",
}
SLA_FIELDS = ("sla", "sla_text", "customer_sla")


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def remaining_fraction(good_events: int, valid_events: int, target: float) -> float:
    if valid_events <= 0:
        raise ValueError("valid_events must be positive")
    if good_events < 0 or good_events > valid_events:
        raise ValueError("good_events out of range")
    target_q = Fraction(target).limit_denominator(10000)
    if not 0 < target_q < 1:
        raise ValueError("target must be between 0 and 1")
    allowed_bad = Fraction(valid_events) * (1 - target_q)
    observed_bad = Fraction(valid_events - good_events)
    if allowed_bad == 0:
        raise ValueError("allowed bad events is zero")
    return float(1 - observed_bad / allowed_bad)


def evaluate(
    catalog: dict,
    windows: dict,
    budgets: dict,
    observations: dict,
    journeys: dict,
    decisions: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    journey_ids = {item["id"] for item in journeys.get("journeys", [])}
    window_ids = {item["id"] for item in windows.get("windows", [])}
    slo_by_id = {item["id"]: item for item in catalog.get("slos", [])}
    budget_by_slo = {item["slo"]: item for item in budgets.get("budgets", [])}
    observation_by_id = {item["id"]: item for item in observations.get("observations", [])}
    accepted_slis = {
        item["candidate"]
        for item in decisions.get("decisions", [])
        if item.get("treatment") == "accept"
    }
    non_critical_ids = {item["id"] for item in catalog.get("non_critical", [])}
    legal_by_id = {item["id"]: item for item in catalog.get("legal_products", [])}

    for journey_id in expectations.get("required_journeys", []):
        matching = [item for item in catalog.get("slos", []) if item.get("journey") == journey_id]
        if not matching:
            errors.append(f"missing required journey slo: {journey_id}")

    for slo_id in expectations.get("required_slos", []):
        if slo_id not in slo_by_id:
            errors.append(f"missing required slo: {slo_id}")

    for system_id in expectations.get("required_non_critical", []):
        if system_id not in non_critical_ids:
            errors.append(f"missing required non-critical: {system_id}")

    for legal_id in expectations.get("required_legal_out_of_scope", []):
        legal = legal_by_id.get(legal_id)
        if legal is None or legal.get("status") != "out-of-scope":
            errors.append(f"missing sla out-of-scope record: {legal_id}")

    storefront = slo_by_id.get(expectations.get("storefront_order_slo", ""))
    fulfillment = slo_by_id.get(expectations.get("fulfillment_slo", ""))
    if storefront and fulfillment:
        if (storefront.get("target"), storefront.get("window")) == (
            fulfillment.get("target"),
            fulfillment.get("window"),
        ):
            errors.append("fulfillment slo copied from storefront")

    for slo in catalog.get("slos", []):
        slo_id = slo.get("id", "unknown")
        journey = slo.get("journey")
        sli = slo.get("sli")
        window = slo.get("window")
        target = slo.get("target")
        criticality = slo.get("criticality")

        if journey not in journey_ids:
            errors.append(f"slo has no known journey: {slo_id}/{journey}")
        if window not in window_ids:
            errors.append(f"slo has no known window: {slo_id}/{window}")
        if sli not in accepted_slis:
            errors.append(f"slo uses unaccepted sli: {slo_id}/{sli}")
        if sli in JOB_TIME_PROOFS:
            errors.append(f"slo catalogs job-time: {slo_id}/{sli}")
        if sli in THEATER_INDICATORS:
            errors.append(f"slo catalogs theater: {slo_id}/{sli}")
        forbidden = set(expectations.get("forbidden_critical_systems", []))
        if slo_id in forbidden or sli in forbidden or journey in forbidden:
            errors.append(f"non-critical system cataloged as slo: {slo_id}")
        if not isinstance(target, int | float) or isinstance(target, bool):
            errors.append(f"slo target is not numeric: {slo_id}")
        elif not 0 < float(target) < 1:
            errors.append(f"slo target is out of range: {slo_id}")
        for field in SLA_FIELDS:
            if field in slo:
                errors.append(f"sla text used as slo target: {slo_id}")
        if "remaining_budget" in slo:
            errors.append(f"catalog emits remaining budget: {slo_id}")
        if criticality == "critical" and slo_id not in budget_by_slo:
            errors.append(f"missing required budget: {slo_id}")

    for journey_id, required_sli in expectations.get("required_sli", {}).items():
        matching = [
            item
            for item in catalog.get("slos", [])
            if item.get("journey") == journey_id and item.get("sli") == required_sli
        ]
        if not matching:
            errors.append(f"missing required sli for journey: {journey_id}/{required_sli}")

    if "notification-service" in slo_by_id:
        errors.append("non-critical system cataloged as slo: notification-service")
    for item in catalog.get("slos", []):
        if item.get("sli") == "notification-service":
            errors.append(f"non-critical system cataloged as slo: {item.get('id')}")
        elif item.get("journey") == "notification-service":
            errors.append(f"non-critical system cataloged as slo: {item.get('id')}")

    for budget in budgets.get("budgets", []):
        budget_id = budget.get("id", "unknown")
        slo_id = budget.get("slo")
        observation_id = budget.get("observation")
        if "remaining" in budget or "remaining_budget" in budget:
            errors.append(f"budget remaining emitted rather than computed: {budget_id}")
        if slo_id not in slo_by_id:
            errors.append(f"budget has no known slo: {budget_id}/{slo_id}")
        observation = observation_by_id.get(observation_id)
        if observation is None:
            errors.append(f"budget has no known observation: {budget_id}/{observation_id}")
            continue
        slo = slo_by_id.get(slo_id)
        if slo is None:
            continue
        try:
            remaining_fraction(
                int(observation["good_events"]),
                int(observation["valid_events"]),
                float(slo["target"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"remaining budget cannot be computed: {budget_id}/{exc}")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-03"
    return (
        load(ROOT / "slos" / "catalog.yaml"),
        load(ROOT / "slos" / "windows.yaml"),
        load(ROOT / "slos" / "budgets.yaml"),
        load(ROOT / "fixtures" / "observations" / "chapter-03.yaml"),
        load(ROOT / "reliability" / "journeys.yaml"),
        load(ROOT / "slis" / "decisions.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
