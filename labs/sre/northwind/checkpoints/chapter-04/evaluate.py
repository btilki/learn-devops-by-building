from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_FLEET_FIELDS = {
    "freeze",
    "freeze_window",
    "cohorts",
    "rollback",
    "last_known_good",
    "from_version",
    "to_version",
}
FORBIDDEN_FREEZE_REASONS = {
    "platform-upgrade-freeze",
    "for-upgrades",
    "upgrade-freeze",
}


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


def band_action(remaining: float, bands: list[dict]) -> str:
    ordered = sorted(bands, key=lambda item: item["remaining_min"], reverse=True)
    for band in ordered:
        if remaining >= band["remaining_min"]:
            return band["action"]
    return "freeze"


def evaluate(
    policy: dict,
    actions: dict,
    exceptions: dict,
    catalog: dict,
    observations: dict,
    fleet: dict,
    release: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    bands = policy.get("bands", [])
    band_names = {item.get("action") for item in bands}
    for treatment in expectations.get("required_treatments", []):
        if treatment not in band_names:
            errors.append(f"missing required treatment: {treatment}")

    if "remaining_budget" in policy or "remaining" in policy:
        errors.append("policy emits remaining budget")

    slo_by_id = {item["id"]: item for item in catalog.get("slos", [])}
    action_by_target = {item["target"]: item for item in actions.get("actions", [])}
    used_actions = {item.get("action") for item in actions.get("actions", [])}
    for treatment in expectations.get("required_treatments", []):
        if treatment not in used_actions:
            errors.append(f"no decision uses treatment: {treatment}")

    observation_by_slo = {
        item["slo"]: item for item in observations.get("observations", [])
    }
    remaining_by_slo: dict[str, float] = {}
    for slo_id, observation in observation_by_slo.items():
        slo = slo_by_id.get(slo_id)
        if slo is None:
            errors.append(f"observation has no known slo: {slo_id}")
            continue
        try:
            remaining_by_slo[slo_id] = remaining_fraction(
                int(observation["good_events"]),
                int(observation["valid_events"]),
                float(slo["target"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"remaining budget cannot be computed: {slo_id}/{exc}")

    freeze_slo = expectations.get("freeze_slo")
    if freeze_slo:
        remaining = remaining_by_slo.get(freeze_slo)
        if remaining is None:
            errors.append(f"missing remaining budget: {freeze_slo}")
        elif band_action(remaining, bands) != "freeze":
            errors.append(f"storefront remaining is not in freeze band: {remaining}")

    for target in expectations.get("required_freeze_targets", []):
        action = action_by_target.get(target)
        if action is None or action.get("action") != "freeze":
            errors.append(f"unfrozen exhausted budget: {target}")

    for target in expectations.get("required_slow_targets", []):
        action = action_by_target.get(target)
        if action is None or action.get("action") != "slow":
            errors.append(f"missing required slow: {target}")

    for target in expectations.get("required_continue_targets", []):
        action = action_by_target.get(target)
        if action is None or action.get("action") != "continue":
            errors.append(f"missing required continue: {target}")

    upgrade_id = fleet.get("upgrade_id")
    promotion_identity = release.get("promotion_identity")
    for action in actions.get("actions", []):
        action_id = action.get("id", "unknown")
        if "remaining_budget" in action or "remaining" in action:
            errors.append(f"action emits remaining budget: {action_id}")
        if not action.get("owner"):
            errors.append(f"action has no owner: {action_id}")
        if not action.get("expires_at"):
            errors.append(f"action has no expiry: {action_id}")
        if not action.get("review_trigger"):
            errors.append(f"action has no review trigger: {action_id}")
        if action.get("change_kind") == "release" and action.get("action") != "continue":
            identity = action.get("promotion_identity")
            if identity != promotion_identity:
                errors.append(f"release freeze has no inherited identity: {action_id}")
        if action.get("change_kind") != "fleet":
            continue
        target = action.get("target")
        if target != upgrade_id:
            errors.append(f"fleet freeze has no inherited upgrade: {action_id}/{target}")
        for field in FORBIDDEN_FLEET_FIELDS:
            if field in action:
                errors.append(f"fleet freeze copies platform field: {field}")
        reason = action.get("freeze_reason", "")
        if reason in FORBIDDEN_FREEZE_REASONS:
            errors.append(f"fleet freeze relabels platform upgrade freeze: {reason}")
        elif action.get("action") == "freeze" and not reason:
            errors.append(f"fleet freeze has no reason: {action_id}")

    for exception in exceptions.get("exceptions", []):
        exception_id = exception.get("id", "unknown")
        if not exception.get("owner"):
            errors.append(f"exception has no owner: {exception_id}")
        if not exception.get("scope"):
            errors.append(f"exception has no scope: {exception_id}")
        if not exception.get("remaining_journey_risk"):
            errors.append(f"exception has no remaining journey risk: {exception_id}")
        if not exception.get("expires_at"):
            errors.append(f"exception has no expiry: {exception_id}")
        if not exception.get("removal_path"):
            errors.append(f"exception has no removal path: {exception_id}")

    if not exceptions.get("exceptions"):
        errors.append("missing required exception")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-04"
    return (
        load(ROOT / "policy" / "error-budget.yaml"),
        load(ROOT / "policy" / "actions.yaml"),
        load(ROOT / "policy" / "exceptions.yaml"),
        load(ROOT / "slos" / "catalog.yaml"),
        load(ROOT / "fixtures" / "observations" / "chapter-04.yaml"),
        load(ROOT / "inherited" / "platform-v1.0" / "fleet" / "interface.yaml"),
        load(ROOT / "inherited" / "devops-v1.1" / "release" / "interface.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
