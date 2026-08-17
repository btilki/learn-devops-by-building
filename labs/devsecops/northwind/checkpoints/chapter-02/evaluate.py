from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(
    system: dict,
    boundaries: dict,
    paths: dict,
    invariants: dict,
    expectations: dict,
) -> list[str]:
    errors: list[str] = []
    components = {item["id"] for item in system.get("components", [])}
    flows = {item["id"]: item for item in system.get("flows", [])}
    boundary_by_id = {item["id"]: item for item in boundaries.get("boundaries", [])}
    path_by_id = {item["id"]: item for item in paths.get("attack_paths", [])}
    invariant_ids = {item["id"] for item in invariants.get("invariants", [])}

    for boundary_id in expectations.get("required_boundaries", []):
        if boundary_id not in boundary_by_id:
            errors.append(f"missing required boundary: {boundary_id}")
    for path_id in expectations.get("required_attack_paths", []):
        if path_id not in path_by_id:
            errors.append(f"missing required attack path: {path_id}")

    for flow_id, flow in flows.items():
        if flow.get("from") not in components or flow.get("to") not in components:
            errors.append(f"flow references unknown component: {flow_id}")
        boundary_id = flow.get("boundary")
        if boundary_id and boundary_id not in boundary_by_id:
            errors.append(f"flow references unknown boundary: {flow_id}/{boundary_id}")

    threatened_priority: set[str] = set()
    for path_id, path in path_by_id.items():
        if not path.get("prerequisites"):
            errors.append(f"attack path has no prerequisite: {path_id}")
        if not path.get("missing_evidence"):
            errors.append(f"attack path has no missing evidence: {path_id}")
        for invariant_id in path.get("threatens", []):
            if invariant_id not in invariant_ids:
                errors.append(f"attack path threatens unknown invariant: {path_id}/{invariant_id}")
            threatened_priority.add(invariant_id)
        for step in path.get("steps", []):
            flow_id = step.get("flow")
            boundary_id = step.get("boundary")
            if flow_id not in flows:
                errors.append(f"attack step references unknown flow: {path_id}/{flow_id}")
                continue
            if boundary_id not in boundary_by_id:
                errors.append(f"attack step references unknown boundary: {path_id}/{boundary_id}")
            if flows[flow_id].get("boundary") != boundary_id:
                errors.append(f"attack step boundary disagrees with flow: {path_id}/{flow_id}")

    for invariant_id in expectations.get("required_priority_invariants", []):
        if invariant_id not in threatened_priority:
            errors.append(f"priority invariant has no modeled attack path: {invariant_id}")
    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-02"
    return (
        load(ROOT / "threat-model" / "system.yaml"),
        load(ROOT / "threat-model" / "boundaries.yaml"),
        load(ROOT / "threat-model" / "attack-paths.yaml"),
        load(ROOT / "security-model" / "invariants.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
