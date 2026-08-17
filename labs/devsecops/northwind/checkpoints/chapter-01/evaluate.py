from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate(assets: dict, ownership: dict, invariants: dict, expectations: dict) -> list[str]:
    errors: list[str] = []
    asset_by_id = {item["id"]: item for item in assets.get("assets", [])}
    owner_by_id = {item["id"]: item for item in ownership.get("owners", [])}
    invariant_by_id = {item["id"]: item for item in invariants.get("invariants", [])}

    for asset_id in expectations.get("required_assets", []):
        if asset_id not in asset_by_id:
            errors.append(f"missing required asset: {asset_id}")

    for invariant_id in expectations.get("required_invariants", []):
        if invariant_id not in invariant_by_id:
            errors.append(f"missing required invariant: {invariant_id}")

    for asset_id, asset in asset_by_id.items():
        owner = asset.get("owner")
        harms = asset.get("harms", [])
        if not harms:
            errors.append(f"asset has no defined harm: {asset_id}")
        if owner not in owner_by_id:
            errors.append(f"asset has no accountable owner: {asset_id}")
        elif asset_id not in owner_by_id[owner].get("accountable_for", []):
            errors.append(f"owner does not acknowledge asset: {owner}/{asset_id}")

    for invariant_id, invariant in invariant_by_id.items():
        for asset_id in invariant.get("assets", []):
            if asset_id not in asset_by_id:
                errors.append(f"invariant references unknown asset: {invariant_id}/{asset_id}")
        if invariant.get("owner") not in owner_by_id:
            errors.append(f"invariant has no accountable owner: {invariant_id}")
        if not invariant.get("harms"):
            errors.append(f"invariant has no threatened harm: {invariant_id}")

    return errors


def completed_inputs() -> tuple[dict, dict, dict, dict]:
    checkpoint = ROOT / "checkpoints" / "chapter-01"
    return (
        load(ROOT / "security-model" / "assets.yaml"),
        load(ROOT / "security-model" / "ownership.yaml"),
        load(ROOT / "security-model" / "invariants.yaml"),
        load(checkpoint / "expectations.yaml"),
    )
