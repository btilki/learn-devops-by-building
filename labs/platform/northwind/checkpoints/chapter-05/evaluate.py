from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_DEFAULTS = {"latest-tag", "cluster-admin", "portal-launch"}
INHERITED_RELEASE = ROOT / "inherited" / "devops-v1.1" / "release" / "interface.yaml"
INHERITED_IDENTITY = ROOT / "inherited" / "devops-v1.1" / "identity" / "interface.yaml"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    contract: dict,
    scaffold: dict,
    conformance: dict,
    exits: dict,
    catalog: dict,
    jobs: dict,
    users: dict,
    expectations: dict,
    release: dict,
    identity: dict,
) -> list[str]:
    errors: list[str] = []
    user_ids = {item["id"] for item in users.get("users", [])}
    job_ids = {item["id"] for item in jobs.get("jobs", [])}
    catalog_ids = {item["id"] for item in catalog.get("systems", [])}
    contract_defaults = set(contract.get("defaults", []))
    contract_steps = {item["id"] for item in contract.get("steps", [])}
    exit_by_id = {item["id"]: item for item in exits.get("exits", [])}
    conformance_by_system = {item["system"]: item for item in conformance.get("entries", [])}
    required_defaults = expectations.get("required_defaults", [])
    remaining = expectations.get("required_remaining_guardrails", [])

    if contract.get("job") not in job_ids:
        errors.append(f"contract has no known job: {contract.get('job')}")
    if contract.get("job") != expectations.get("required_job"):
        errors.append(f"contract job is not {expectations.get('required_job')}")
    if contract.get("owner") not in user_ids:
        errors.append(f"contract has no known owner: {contract.get('owner')}")

    for default in required_defaults:
        if default not in contract_defaults:
            errors.append(f"paved road drops required default: {default}")

    digest_promotion = release.get("promotion_identity") == "artifact_digest"
    if digest_promotion and "artifact-digest" not in contract_defaults:
        errors.append("paved road drops inherited artifact-digest promotion")
    if identity.get("required_claims") and "workload-identity-claims" not in contract_defaults:
        errors.append("paved road drops inherited workload identity")

    if scaffold.get("contract") != contract.get("id"):
        errors.append("scaffold does not implement the paved-road contract")
    for step_id in contract_steps:
        if step_id not in set(scaffold.get("implements", [])):
            errors.append(f"scaffold missing contract step: {step_id}")

    if not exit_by_id:
        errors.append("missing supported exit")

    for exit_id, exit_row in exit_by_id.items():
        if exit_row.get("owner") not in user_ids:
            errors.append(f"exit has no known owner: {exit_id}")
        if not exit_row.get("review_at"):
            errors.append(f"exit has no review date: {exit_id}")
        lost = set(exit_row.get("lost_defaults", []))
        kept = set(exit_row.get("remaining_guardrails", []))
        for guardrail in remaining:
            if guardrail not in kept:
                errors.append(f"exit drops remaining guardrail: {exit_id}/{guardrail}")
            if guardrail in lost:
                errors.append(f"exit treats guardrail as lost default: {exit_id}/{guardrail}")

    for system_id in expectations.get("required_systems", []):
        if system_id not in catalog_ids:
            errors.append(f"missing required catalog system: {system_id}")
        if system_id not in conformance_by_system:
            errors.append(f"missing conformance: {system_id}")

    for system_id, entry in conformance_by_system.items():
        if system_id not in catalog_ids:
            errors.append(f"conformance has no known system: {system_id}")
        present = set(entry.get("defaults_present", []))
        path = entry.get("path")
        for forbidden in present & FORBIDDEN_DEFAULTS:
            errors.append(f"forbidden default: {system_id}/{forbidden}")
        if path == "unofficial":
            errors.append(f"unofficial fork: {system_id}")
            for default in required_defaults:
                if default not in present:
                    errors.append(f"missing paved default: {system_id}/{default}")
            continue
        if path == "paved":
            for default in required_defaults:
                if default not in present:
                    errors.append(f"missing paved default: {system_id}/{default}")
        elif path == "exited":
            exit_id = entry.get("exit")
            if not exit_id:
                errors.append(f"exited path has no exit record: {system_id}")
            elif exit_id not in exit_by_id:
                errors.append(f"unknown exit: {system_id}/{exit_id}")
            else:
                exit_row = exit_by_id[exit_id]
                if exit_row.get("system") != system_id:
                    errors.append(f"exit system mismatch: {exit_id}")
                for guardrail in remaining:
                    if guardrail not in present:
                        errors.append(f"exit missing remaining guardrail: {system_id}/{guardrail}")

    return errors


def completed_inputs() -> tuple:
    checkpoint = ROOT / "checkpoints" / "chapter-05"
    return (
        load(ROOT / "paved-road" / "contract.yaml"),
        load(ROOT / "paved-road" / "scaffold.yaml"),
        load(ROOT / "paved-road" / "conformance.yaml"),
        load(ROOT / "paved-road" / "exits.yaml"),
        load(ROOT / "catalog" / "systems.yaml"),
        load(ROOT / "product" / "jobs.yaml"),
        load(ROOT / "product" / "users.yaml"),
        load(checkpoint / "expectations.yaml"),
        load(INHERITED_RELEASE),
        load(INHERITED_IDENTITY),
    )
