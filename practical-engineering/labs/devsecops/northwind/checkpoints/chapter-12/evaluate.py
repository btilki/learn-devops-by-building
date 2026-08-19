import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return yaml.safe_load(path.read_text())


def inputs():
    return (
        load(ROOT / "runtime/contracts/order-worker.yaml"),
        load(ROOT / "runtime/policies/behavior.yaml"),
    )


def baseline_inputs():
    return (
        load(ROOT / "checkpoints/chapter-12/cases/order-worker-contract.yaml"),
        load(ROOT / "runtime/policies/behavior.yaml"),
    )


def evaluate_behavior(observation, contract, policy):
    errors = []
    behavior_type = observation["type"]
    resource = observation["resource"]
    action = None
    if behavior_type == "process":
        action = (
            "allowed-process" if resource in contract["allowed_processes"] else "shell-execution"
        )
    elif behavior_type == "filesystem-write":
        allowed = any(resource.startswith(prefix) for prefix in contract["allowed_writes"])
        action = "allowed-filesystem-write" if allowed else "root-filesystem-write"
    elif behavior_type == "filesystem-read" and resource.startswith("/var/run/secrets"):
        action = "credential-discovery"
    elif behavior_type == "egress":
        action = "allowed-egress" if resource in contract["allowed_egress"] else "undeclared-egress"
    elif behavior_type == "privilege" and resource == "escalate":
        action = "privilege-escalation"
    else:
        action = "unmapped-behavior"
    if action.startswith("allowed-"):
        outcome = "allowed"
    else:
        mode = policy["actions"].get(action)
        if not mode:
            errors.append("action-policy-missing")
            outcome = "detected"
        else:
            outcome = "blocked" if mode == "prevent" else "detected"
    if policy["require_attribution"] and not observation.get("claim_id"):
        errors.append("attribution-missing")
    if policy["require_deployment_context"] and not observation.get("deployment"):
        errors.append("deployment-context-missing")
    if observation.get("artifact_digest") != contract["artifact_digest"]:
        errors.append("artifact-context-mismatch")
    event_times = {
        "credential-discovery": "2026-08-15T10:10:00Z",
        "shell-execution": "2026-08-15T10:11:00Z",
        "undeclared-egress": "2026-08-15T10:12:00Z",
    }
    return {
        "kind": "runtime-security-event",
        "time": event_times.get(action, "2026-08-15T10:12:00Z"),
        "source": "modeled-runtime-sensor",
        "subject": observation.get("subject"),
        "claim_id": observation.get("claim_id"),
        "action": action,
        "behavior_type": behavior_type,
        "resource": resource,
        "outcome": outcome,
        "policy_version": policy["policy_version"],
        "deployment": observation.get("deployment"),
        "artifact_digest": observation.get("artifact_digest"),
        "errors": errors,
        "correlation": "runtime-attack-12",
        "sensitivity": "security-restricted",
        "integrity": "verified",
    }


def legitimate_errors(contract):
    errors = []
    if contract["identity"] != contract["workload"]:
        errors.append("identity-mismatch")
    if contract["linux_capabilities"]:
        errors.append("capabilities-excessive")
    if contract["allow_privilege_escalation"]:
        errors.append("privilege-escalation-enabled")
    if not contract["read_only_root_filesystem"]:
        errors.append("root-filesystem-writable")
    for required in contract["required_egress"]:
        if required not in contract["allowed_egress"]:
            errors.append(f"required-egress-missing:{required}")
    return errors


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")
