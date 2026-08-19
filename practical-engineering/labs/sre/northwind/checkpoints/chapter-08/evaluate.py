from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_PROVIDERS = ("payment", "warehouse", "notification-service")
FORBIDDEN_CLAIM_LABEL = "no-user-impact"
FORBIDDEN_KEYS = {"no_user_impact", "user_impact", "no-user-impact"}
FORBIDDEN_VALUES = {"no-user-impact", "no user impact"}
REQUIRED_EVIDENCE = {
    "payment": "payment-timeout-is-storefront-burn",
    "warehouse": "warehouse-timeout-is-fulfillment-burn",
    "notification-service": "email-failure-is-not-order-burn",
}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _provider_label(obj: dict, fallback: str) -> str:
    if obj.get("id") in REQUIRED_PROVIDERS:
        return str(obj["id"])
    if obj.get("provider") in REQUIRED_PROVIDERS:
        return str(obj["provider"])
    return fallback


def _walk_forbidden(obj: object, errors: list[str], provider: str = "") -> None:
    if isinstance(obj, dict):
        current = _provider_label(obj, provider)
        for key, value in obj.items():
            label = current or key
            if key in FORBIDDEN_KEYS:
                errors.append(f"dependency emits no user impact: {label}")
            if key == "evidence" and value in FORBIDDEN_VALUES:
                errors.append(f"dependency emits no user impact: {label}")
            _walk_forbidden(value, errors, current)
    elif isinstance(obj, list):
        for item in obj:
            _walk_forbidden(item, errors, provider)


def evaluate(
    catalog: dict,
    criticality: dict,
    contracts: dict,
    journeys: dict,
    slo_catalog: dict,
    decisions: dict,
    pages: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    _walk_forbidden(catalog, errors, "catalog")
    _walk_forbidden(criticality, errors, "criticality")
    _walk_forbidden(contracts, errors, "contracts")

    forbidden = set(catalog.get("forbidden_claims") or [])
    if FORBIDDEN_CLAIM_LABEL not in forbidden:
        errors.append(f"missing forbidden claim: {FORBIDDEN_CLAIM_LABEL}")

    providers = {item.get("id"): item for item in catalog.get("providers", [])}
    for provider_id in REQUIRED_PROVIDERS:
        if provider_id not in providers:
            errors.append(f"missing required provider: {provider_id}")

    expected_consumers = expectations.get("consumers", {})
    for provider_id, consumer in expected_consumers.items():
        actual = providers.get(provider_id, {}).get("consumer")
        if actual != consumer:
            if provider_id == "warehouse":
                errors.append("warehouse not attributed to fulfillment")
            else:
                errors.append(f"provider consumer mismatch: {provider_id}/{actual}")

    journey_ids = {item.get("id") for item in journeys.get("journeys", [])}
    accepted_slis = {
        item["candidate"]
        for item in decisions.get("decisions", [])
        if item.get("treatment") == "accept"
    }
    non_critical = {item["id"] for item in slo_catalog.get("non_critical", [])}
    assignments = {
        item.get("provider"): item for item in criticality.get("assignments", [])
    }
    required_burns = expectations.get("required_burns", {})
    for provider_id, expected in required_burns.items():
        row = assignments.get(provider_id, {})
        journey = row.get("journey")
        if journey not in journey_ids and expected.get("journey"):
            errors.append(f"assignment has no known journey: {provider_id}/{journey}")
        matches = (
            row.get("journey") == expected.get("journey")
            and row.get("sli") == expected.get("sli")
            and row.get("criticality") == expected.get("criticality")
            and row.get("failure_effect") == expected.get("failure_effect")
        )
        if not matches:
            if provider_id == "payment":
                errors.append("payment failure does not burn storefront: payment")
            elif provider_id == "warehouse":
                errors.append("warehouse not attributed to fulfillment")
            else:
                errors.append(f"missing required journey-burn: {provider_id}")
        if row.get("sli") and row.get("sli") not in accepted_slis:
            errors.append(f"burn uses unaccepted sli: {provider_id}/{row.get('sli')}")

    for provider_id in expectations.get("required_non_critical", []):
        row = assignments.get(provider_id, {})
        if (
            row.get("criticality") != "non-critical"
            or row.get("failure_effect") == "page"
            or row.get("destination") == "storefront-oncall"
        ):
            errors.append(f"email paged as critical: {provider_id}")
        if provider_id in non_critical and row.get("criticality") == "critical":
            errors.append(f"email paged as critical: {provider_id}")
        if row.get("remaining_owner") != "storefront-team":
            if row.get("criticality") == "critical":
                errors.append(f"email paged as critical: {provider_id}")

    for provider_id in expectations.get("forbidden_page_providers", []):
        dest = assignments.get(provider_id, {}).get("destination")
        if dest == "storefront-oncall":
            errors.append(f"email paged as critical: {provider_id}")
    for page in pages.get("pages", []):
        page_id = str(page.get("id", ""))
        burn_id = str(page.get("burn", ""))
        if "notification" in page_id or burn_id.startswith("notification"):
            errors.append("email paged as critical: notification-service")

    contract_by_provider = {
        item.get("provider"): item for item in contracts.get("contracts", [])
    }
    required_fallbacks = expectations.get("required_fallbacks", {})
    for provider_id, fallback in required_fallbacks.items():
        contract = contract_by_provider.get(provider_id, {})
        if not contract.get("timeout"):
            errors.append(f"missing required timeout: {provider_id}")
        retry_budget = contract.get("retry_budget")
        if not isinstance(retry_budget, int) or isinstance(retry_budget, bool):
            errors.append(f"missing retry budget: {provider_id}")
        if contract.get("fallback") != fallback:
            errors.append(f"fallback mismatch: {provider_id}/{contract.get('fallback')}")
        expected_evidence = REQUIRED_EVIDENCE.get(provider_id)
        if expected_evidence and contract.get("evidence") != expected_evidence:
            errors.append(f"evidence mismatch: {provider_id}")

    return list(dict.fromkeys(errors))


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-08"
    return (
        load(ROOT / "dependencies" / "catalog.yaml"),
        load(ROOT / "dependencies" / "criticality.yaml"),
        load(ROOT / "dependencies" / "contracts.yaml"),
        load(ROOT / "reliability" / "journeys.yaml"),
        load(ROOT / "slos" / "catalog.yaml"),
        load(ROOT / "slis" / "decisions.yaml"),
        load(ROOT / "alerting" / "pages.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
