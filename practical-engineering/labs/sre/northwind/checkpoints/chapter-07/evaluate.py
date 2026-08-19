from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_MEASUREMENTS = {"we-are-busy", "on-call-already-watches-email"}
FORBIDDEN_BOUND_VALUES = FORBIDDEN_MEASUREMENTS


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def toil_fraction(toil_hours: float, available_hours: float) -> float:
    if available_hours <= 0:
        raise ValueError("available_hours must be positive")
    if toil_hours < 0:
        raise ValueError("toil_hours out of range")
    return float(
        (Fraction(toil_hours) / Fraction(available_hours)).limit_denominator(10000)
    )


def evaluate(
    definition: dict,
    inventory: dict,
    bounds: dict,
    catalog: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    forbidden = set(definition.get("forbidden_measurements", []))
    for label in FORBIDDEN_MEASUREMENTS:
        if label not in forbidden:
            errors.append(f"missing forbidden measurement: {label}")

    for item in inventory.get("items", []):
        item_id = item.get("id", "unknown")
        if item.get("class") not in {"toil", "engineering"}:
            errors.append(f"inventory item is unclassified: {item_id}")
        if item.get("kind") not in {"interrupt", "project"}:
            errors.append(f"inventory item has no kind: {item_id}")
        if not item.get("hours_per_week"):
            errors.append(f"inventory item has no hours: {item_id}")

    bound_value = bounds.get("bound_fraction", bounds.get("bound"))
    if bound_value in FORBIDDEN_BOUND_VALUES:
        errors.append(f"bound is not numeric: {bound_value}")
    elif not isinstance(bound_value, int | float) or isinstance(bound_value, bool):
        errors.append(f"bound is not numeric: {bound_value}")
    elif not 0 < float(bound_value) <= 1:
        errors.append("bound fraction is out of range")

    if "toil_fraction" in bounds or "remaining_capacity" in bounds:
        errors.append("bound emits toil fraction rather than computing it")

    toil_hours = sum(
        float(item.get("hours_per_week", 0))
        for item in inventory.get("items", [])
        if item.get("class") == "toil"
    )
    available = bounds.get("available_hours_per_week")
    fraction: float | None = None
    if isinstance(available, int | float) and not isinstance(available, bool) and available > 0:
        fraction = toil_fraction(toil_hours, float(available))
        if isinstance(bound_value, int | float) and not isinstance(bound_value, bool):
            if fraction >= float(bound_value) and expectations.get("require_breach"):
                pass
            elif expectations.get("require_breach") and fraction < float(bound_value):
                errors.append(f"toil bound is not breached: {fraction}")
    else:
        errors.append("missing available hours")

    non_critical = {item["id"] for item in catalog.get("non_critical", [])}
    for proposal in bounds.get("scope_proposals", []):
        proposal_id = proposal.get("id", "unknown")
        slo = proposal.get("slo")
        decision = proposal.get("decision")
        reason = proposal.get("reason", "")
        if slo in non_critical and proposal.get("criticality") == "critical":
            if decision != "deny":
                errors.append(f"new critical slo allowed: {slo}")
        if decision == "allow" and slo in expectations.get("forbidden_critical_slos", []):
            errors.append(f"new critical slo allowed: {slo}")
        justification = str(proposal.get("justification", ""))
        if reason in FORBIDDEN_MEASUREMENTS or justification in FORBIDDEN_MEASUREMENTS:
            errors.append(
                f"scope uses forbidden justification: {proposal_id}/{justification or reason}"
            )
        if fraction is not None and isinstance(bound_value, int | float):
            if fraction >= float(bound_value) and decision == "allow":
                errors.append(f"new critical slo allowed while bound breached: {slo}")

    if not bounds.get("scope_proposals"):
        errors.append("missing required scope proposal")
    for slo in expectations.get("forbidden_critical_slos", []):
        matching = [
            item
            for item in bounds.get("scope_proposals", [])
            if item.get("slo") == slo and item.get("decision") == "deny"
        ]
        if not matching:
            errors.append(f"missing required deny: {slo}")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-07"
    return (
        load(ROOT / "toil" / "definition.yaml"),
        load(ROOT / "toil" / "inventory.yaml"),
        load(ROOT / "toil" / "bounds.yaml"),
        load(ROOT / "slos" / "catalog.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
