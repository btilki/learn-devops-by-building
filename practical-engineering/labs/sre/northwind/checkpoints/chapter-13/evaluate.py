from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_KINDS = {
    "error-budget-freeze",
    "on-call-page-path",
    "dependency-loss",
    "regional-loss-tabletop",
}
ALLOWED_DEPENDENCIES = {"payment", "warehouse"}
FORBIDDEN_DEPENDENCIES = {"notification-service", "email"}
FORBIDDEN_PAGES = {"slack", "storefront-oncall", "fulfillment-oncall", "platform-oncall"}
CHAPTER_14_KINDS = {"chapter-14-failover", "portfolio-failover"}
RECOVERED_KEYS = {"recovered"}
COMPLETE_DISPOSITIONS = {"complete", "in-bounds"}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _walk_recovered(obj: object, errors: list[str], loc: str) -> None:
    if isinstance(obj, dict):
        current = str(obj.get("id") or loc)
        for key, value in obj.items():
            if key in RECOVERED_KEYS or value == "recovered":
                errors.append("game day emits recovered")
            if key == "status" and value == "recovered":
                errors.append("game day emits recovered")
            _walk_recovered(value, errors, current)
    elif isinstance(obj, list):
        for item in obj:
            _walk_recovered(item, errors, loc)


def evaluate(
    program: dict,
    scenarios: dict,
    results: dict,
    policy_actions: dict,
    oncall: dict,
    learning_actions: dict,
    architecture: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    _walk_recovered(program, errors, "program")
    _walk_recovered(scenarios, errors, "scenarios")
    _walk_recovered(results, errors, "results")

    cadence = program.get("cadence")
    expected_cadence = expectations.get("cadence", "90d")
    if cadence != expected_cadence:
        errors.append(f"cadence is not recurrence: {cadence}")

    if program.get("abort_when") != "blast-radius-exceeds-contract":
        errors.append("missing abort")
    if program.get("learning_join") != learning_actions.get("id"):
        errors.append("missing learning join")
    if program.get("forbidden_complete_on") != "mixed-backup":
        errors.append("single mixed-backup completes program")
    if not program.get("not_chapter_14_failover"):
        errors.append("regional scenario rehearses chapter 14")

    declared = set(program.get("required_kinds") or [])
    if not REQUIRED_KINDS.issubset(declared):
        for kind in sorted(REQUIRED_KINDS - declared):
            errors.append(f"missing required scenario: {kind}")

    rows = scenarios.get("scenarios") or []
    by_id = {item.get("id"): item for item in rows}
    kinds = {item.get("kind") for item in rows}
    for kind in CHAPTER_14_KINDS:
        if kind in kinds:
            errors.append("regional scenario rehearses chapter 14")

    freeze_ids = {
        item.get("id")
        for item in policy_actions.get("actions") or []
        if item.get("action") == "freeze"
    }
    system_ids = {item.get("id") for item in oncall.get("systems") or []}
    region_ids = {item.get("id") for item in architecture.get("regions") or []}
    action_ids = {item.get("id") for item in learning_actions.get("actions") or []}
    expected_action = expectations.get("learning_action", "verify-payment-retry-shed")

    freeze_ok = False
    page_ok = False
    dependency_ok = False
    regional_ok = False
    mixed_insufficient = False
    for item in rows:
        kind = item.get("kind")
        joins = item.get("joins")
        if kind == "error-budget-freeze":
            freeze_ok = joins in freeze_ids
        elif kind == "on-call-page-path":
            page_ok = joins in system_ids and joins not in FORBIDDEN_PAGES
            if joins in FORBIDDEN_PAGES:
                errors.append("page path does not join on-call system")
        elif kind == "dependency-loss":
            dependency_ok = joins in ALLOWED_DEPENDENCIES
            if joins in FORBIDDEN_DEPENDENCIES:
                errors.append("dependency drill is not payment or warehouse")
        elif kind == "regional-loss-tabletop":
            mode = item.get("mode")
            regional_ok = joins in region_ids and mode in {"tabletop", "simulated"}
            if mode in CHAPTER_14_KINDS or mode == "executed":
                errors.append("regional scenario rehearses chapter 14")
        elif kind == "mixed-backup":
            mixed_insufficient = bool(item.get("insufficient_alone"))

    if "error-budget-freeze" in kinds and not freeze_ok:
        errors.append("freeze does not join error-budget action")
    if "on-call-page-path" in kinds and not page_ok:
        errors.append("page path does not join on-call system")
    if "dependency-loss" in kinds and not dependency_ok:
        errors.append("dependency drill is not payment or warehouse")
    if "regional-loss-tabletop" in kinds and not regional_ok:
        errors.append("regional tabletop does not join architecture")

    in_bounds: set[str] = set()
    mixed_claims_complete = False
    abort_recorded = False
    fed_learning = False
    for result in results.get("results") or []:
        scenario = by_id.get(result.get("scenario"), {})
        kind = scenario.get("kind")
        disposition = result.get("disposition")
        if disposition == "in-bounds" and kind in REQUIRED_KINDS:
            in_bounds.add(kind)
        if kind == "mixed-backup" and disposition in COMPLETE_DISPOSITIONS:
            if not mixed_insufficient:
                mixed_claims_complete = True
        if (
            disposition == "abort"
            and result.get("abort_reason") == "blast-radius-exceeds-contract"
        ):
            abort_recorded = True
        feeds = result.get("feeds_action") or scenario.get("feeds_action")
        if feeds == expected_action and feeds in action_ids:
            fed_learning = True
        elif feeds and feeds not in action_ids:
            errors.append("results do not feed chapter 11 action")

    for kind in sorted(REQUIRED_KINDS - in_bounds):
        errors.append(f"missing required scenario: {kind}")
    if not abort_recorded:
        errors.append("missing abort")
    if not fed_learning:
        errors.append("results do not feed chapter 11 action")

    claimed_complete = program.get("status") == "complete" or program.get("complete") is True
    if claimed_complete and not REQUIRED_KINDS.issubset(in_bounds):
        errors.append("single mixed-backup completes program")
    if mixed_claims_complete and not REQUIRED_KINDS.issubset(in_bounds):
        errors.append("single mixed-backup completes program")
    if not mixed_insufficient and "mixed-backup" in kinds:
        if claimed_complete or mixed_claims_complete:
            errors.append("single mixed-backup completes program")

    return list(dict.fromkeys(errors))


def completed_inputs() -> tuple[dict, dict, dict, dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-13"
    return (
        load(ROOT / "gamedays" / "program.yaml"),
        load(ROOT / "gamedays" / "scenarios.yaml"),
        load(ROOT / "gamedays" / "results.yaml"),
        load(ROOT / "policy" / "actions.yaml"),
        load(ROOT / "oncall" / "system.yaml"),
        load(ROOT / "learning" / "actions.yaml"),
        load(ROOT / "regions" / "architecture.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
