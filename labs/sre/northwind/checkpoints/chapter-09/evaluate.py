from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PAYMENT = "payment"
SILENT_DROP = {"silent-drop", "none"}
QUOTA_OR_SCALING = {"platform-tenant-quota", "devops-unit-cost-scaling"}
FORBIDDEN_ACCOUNTING = {"success", "good", "accepted"}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    modes: dict,
    shedding: dict,
    cascade: dict,
    contracts: dict,
    journeys: dict,
    pages: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    journey_ids = {item.get("id") for item in journeys.get("journeys", [])}
    payment_budget = None
    for item in contracts.get("contracts", []):
        if item.get("provider") == PAYMENT:
            payment_budget = item.get("retry_budget")
            break

    required_mode = expectations.get("required_mode", {})
    matching_modes = [
        item
        for item in modes.get("modes", [])
        if item.get("id") == required_mode.get("id")
    ]
    if not matching_modes:
        errors.append("missing required degraded mode: payment")
    for mode in modes.get("modes", []):
        if "remaining_budget" in mode:
            errors.append("degraded mode emits remaining budget")
        accounting = mode.get("accounting")
        if accounting in FORBIDDEN_ACCOUNTING or accounting != "journey-burn":
            errors.append("degraded success counted as success")
        if mode.get("user_visible") in SILENT_DROP or not mode.get("user_visible"):
            errors.append("missing user-visible degraded mode")
        journey = mode.get("journey")
        if journey not in journey_ids:
            errors.append(f"mode has no known journey: {mode.get('id')}/{journey}")
        if (
            mode.get("id") == required_mode.get("id")
            and mode.get("sli") != required_mode.get("sli")
        ):
            errors.append("missing required degraded mode: payment")

    required_shed = expectations.get("required_shed", {})
    payment_rules = [
        item
        for item in shedding.get("rules", [])
        if item.get("provider") == PAYMENT
    ]
    if not payment_rules:
        errors.append("missing required shed: payment")
    for rule in payment_rules:
        if rule.get("action") != required_shed.get("action"):
            errors.append("missing required shed: payment")
        if rule.get("worker") != required_shed.get("worker"):
            errors.append("missing required shed: payment")
        retry_limit = rule.get("retry_limit")
        if (
            retry_limit == "unbounded"
            or isinstance(retry_limit, bool)
            or not isinstance(retry_limit, int)
        ):
            errors.append("unbounded retries: payment")
        elif (
            isinstance(payment_budget, int)
            and not isinstance(payment_budget, bool)
            and retry_limit > payment_budget
        ):
            errors.append("retry amplification: payment")
        elif retry_limit != payment_budget:
            errors.append("retry amplification: payment")
        distinct = set(rule.get("distinct_from") or [])
        if not QUOTA_OR_SCALING.issubset(distinct):
            errors.append("shed replaced by quota or scaling")

    required_denial = expectations.get("required_denial", {})
    payment_denials = [
        item
        for item in cascade.get("denials", [])
        if item.get("source_provider") == PAYMENT
    ]
    if not payment_denials:
        errors.append("fulfillment paged as payment cause")
    for denial in payment_denials:
        if denial.get("must_not_page") != required_denial.get("must_not_page"):
            errors.append("fulfillment paged as payment cause")
        if denial.get("must_not_burn") != required_denial.get("must_not_burn"):
            errors.append("fulfillment paged as payment cause")
        if denial.get("page_cause") == required_denial.get("must_not_page"):
            errors.append("fulfillment paged as payment cause")
    if cascade.get("page_cause") == required_denial.get("must_not_page"):
        errors.append("fulfillment paged as payment cause")

    for page in pages.get("pages", []):
        if page.get("cause") == PAYMENT and page.get("destination") == (
            required_denial.get("must_not_page")
        ):
            errors.append("fulfillment paged as payment cause")

    return list(dict.fromkeys(errors))


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-09"
    return (
        load(ROOT / "degradation" / "modes.yaml"),
        load(ROOT / "degradation" / "shedding.yaml"),
        load(ROOT / "degradation" / "cascade.yaml"),
        load(ROOT / "dependencies" / "contracts.yaml"),
        load(ROOT / "reliability" / "journeys.yaml"),
        load(ROOT / "alerting" / "pages.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
