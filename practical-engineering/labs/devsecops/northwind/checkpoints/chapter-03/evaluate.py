from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return yaml.safe_load(path.read_text())


def evaluate(risks, decisions, paths, assets, expectations):
    errors = []
    risk_by_id = {x["id"]: x for x in risks.get("risks", [])}
    path_ids = {x["id"] for x in paths.get("attack_paths", [])}
    asset_ids = {x["id"] for x in assets.get("assets", [])}
    decision_by_risk = {x["risk"]: x for x in decisions.get("decisions", [])}
    for risk_id in expectations.get("required_risks", []):
        if risk_id not in risk_by_id:
            errors.append(f"missing required risk: {risk_id}")
    for risk_id, risk in risk_by_id.items():
        if risk.get("attack_path") not in path_ids:
            errors.append(f"unknown attack path: {risk_id}")
        for field in ("exposure", "likelihood", "impact", "owner", "review_trigger"):
            if not risk.get(field):
                errors.append(f"missing {field}: {risk_id}")
        if not risk.get("uncertainty"):
            errors.append(f"missing uncertainty: {risk_id}")
        if not risk.get("residual_risk"):
            errors.append(f"missing residual risk: {risk_id}")
        for asset in risk.get("assets", []):
            if asset not in asset_ids:
                errors.append(f"unknown asset: {risk_id}/{asset}")
        if risk.get("treatment") == "mitigate" and risk_id not in decision_by_risk:
            errors.append(f"mitigated risk has no control decision: {risk_id}")
    for risk_id, decision in decision_by_risk.items():
        if risk_id not in risk_by_id:
            errors.append(f"control decision references unknown risk: {risk_id}")
        types = {x["type"] for x in decision.get("controls", [])}
        if risk_id == "maintainer-supply-chain-payment-risk":
            for required in expectations.get("required_control_types", []):
                if required not in types:
                    errors.append(f"priority risk missing {required} control")
    return errors


def completed_inputs():
    cp = ROOT / "checkpoints/chapter-03"
    return (
        load(ROOT / "risk/risk-register.yaml"),
        load(ROOT / "risk/control-decisions.yaml"),
        load(ROOT / "threat-model/attack-paths.yaml"),
        load(ROOT / "security-model/assets.yaml"),
        load(cp / "expectations.yaml"),
    )
