import importlib.util
import json
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
COMPROMISED_DIGEST = (
    "sha256:9f4e7b3e0ac870d986f228f4d3869f46a7c506f77d5f4eaa59a24a1867d65f09"
)


def load(path):
    return yaml.safe_load(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix in {".yaml", ".yml"}:
        path.write_text(yaml.safe_dump(value, sort_keys=False))
    else:
        path.write_text(json.dumps(value, indent=2) + "\n")


def load_module(chapter, name):
    path = ROOT / f"checkpoints/{chapter}/{name}.py"
    spec = importlib.util.spec_from_file_location(f"{chapter}_{name}", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inherited_interfaces():
    base = ROOT / "inherited/devops-v1.1"
    return {
        "recovery": load(base / "recovery/interface.yaml"),
        "incident": load(base / "incident/interface.yaml"),
        "gitops": load(base / "gitops/interface.yaml"),
        "observability": load(base / "observability/interface.yaml"),
    }


def inventory_errors(inventory):
    roots = inventory["roots"]
    ids = [root["id"] for root in roots]
    known = set(ids)
    errors = []
    if len(ids) != len(known):
        errors.append("trust-root-duplicate")
    for root in roots:
        for dependent in root["dependents"]:
            if dependent not in known:
                errors.append(f"trust-dependent-unknown:{root['id']}:{dependent}")
        for source in root.get("derived_from", []):
            if source not in known:
                errors.append(f"trust-derivation-unknown:{root['id']}:{source}")
        if root["status"] in {"invalidated", "replaced"} and not root.get(
            "invalidation_reason"
        ):
            errors.append(f"invalidation-reason-missing:{root['id']}")
    compromised = next(
        (root for root in roots if root["material"] == COMPROMISED_DIGEST),
        None,
    )
    if not compromised or compromised["status"] != "invalidated":
        errors.append("compromised-artifact-not-invalidated")
    if graph_has_cycle(roots):
        errors.append("trust-graph-cycle")
    errors.extend(descendant_reconciliation_errors(inventory))
    return errors


def graph_has_cycle(roots):
    graph = {root["id"]: root["dependents"] for root in roots}
    visiting, visited = set(), set()

    def visit(node):
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(child) for child in graph.get(node, [])):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def descendants(inventory, root_id):
    graph = {root["id"]: root["dependents"] for root in inventory["roots"]}
    found, pending = set(), list(graph.get(root_id, []))
    while pending:
        node = pending.pop()
        if node not in found:
            found.add(node)
            pending.extend(graph.get(node, []))
    return found


def descendant_reconciliation_errors(inventory):
    roots = {root["id"]: root for root in inventory["roots"]}
    errors = []
    for invalidated in (
        root for root in roots.values() if root["status"] == "invalidated"
    ):
        for dependent_id in descendants(inventory, invalidated["id"]):
            dependent = roots[dependent_id]
            if dependent["status"] in {"invalidated", "replaced", "contained", "suspect"}:
                continue
            derivations = dependent.get("derived_from", [])
            if not derivations or any(
                roots[source]["status"] not in {"trusted", "replaced"}
                for source in derivations
                if source in roots
            ):
                errors.append(
                    f"invalidated-descendant-not-rederived:{invalidated['id']}:{dependent_id}"
                )
    return errors


def eradication_errors(plan):
    required = [
        "verify-evidence-custody",
        "detect-persistence",
        "rotate-missed-automation",
        "invalidate-caches",
        "rebuild-from-trusted-roots",
        "reconcile-business-state",
        "restore-monitored-service",
    ]
    actions = {action["id"]: action["order"] for action in plan["actions"]}
    errors = []
    missing = [action for action in required if action not in actions]
    if missing:
        errors.extend(f"eradication-action-missing:{action}" for action in missing)
        return errors
    if plan["reconciliation"] != "paused":
        errors.append("reconciliation-not-paused")
    if [actions[action] for action in required] != sorted(actions[action] for action in required):
        errors.append("eradication-order-invalid")
    if plan["monitoring"] != "heightened-through-recovery":
        errors.append("heightened-monitoring-missing")
    return errors


def invalidated_digests(inventory):
    return {
        root["material"]
        for root in inventory["roots"]
        if root["status"] == "invalidated" and root["material"].startswith("sha256:")
    }


def cache_findings(cache, invalidated):
    return [
        {
            "cache": cache["id"],
            "digest": entry["digest"],
            "finding": "invalidated-artifact-still-servable",
        }
        for entry in cache["entries"]
        if entry["servable"] and entry["digest"] in invalidated
    ]


def invalidate_cache(cache, invalidated):
    changed = json.loads(json.dumps(cache))
    for entry in changed["entries"]:
        if entry["digest"] in invalidated:
            entry["servable"] = False
            entry["status"] = "purged"
    changed["state"] = "invalidated"
    return changed


def rebuild_errors(manifest, provenance, deployment, contract, interfaces):
    errors = []
    digest = manifest["rebuilt_artifact_digest"]
    if digest in manifest["invalidated_digests"]:
        errors.append("rebuilt-artifact-still-invalidated")
    if set(interfaces["recovery"]["required_roots"]) != set(manifest["required_roots"]):
        errors.append("recovery-roots-incomplete")
    if provenance["artifact"]["digest"] != digest:
        errors.append("provenance-digest-mismatch")
    if provenance["builder"]["id"] != manifest["trusted_builder"]:
        errors.append("builder-mismatch")
    if provenance["signature"]["key_id"] != manifest["trusted_signing_key"]:
        errors.append("signing-key-mismatch")
    if deployment["artifact_digest"] != digest:
        errors.append("deployment-digest-mismatch")
    if contract["artifact_digest"] != digest:
        errors.append("runtime-digest-mismatch")
    if manifest["gitops"]["desired_digest"] != digest:
        errors.append("desired-state-digest-mismatch")
    return errors


def window_time(window):
    return datetime.fromisoformat(window["observed_at"].replace("Z", "+00:00"))


def window_healthy(window, thresholds):
    return (
        window["desired_actual_agreement"] is True
        and window["terminal_order_outcomes"] is True
        and window["detection_active"] is True
        and window["new_persistence_alerts"] == 0
        and window["duplicate_payment_effects"] == 0
        and window["order_success_ratio"] >= thresholds["minimum_order_success_ratio"]
        and window["order_latency_ms"] <= thresholds["maximum_order_latency_ms"]
    )


def qualifying_windows(value, minimum):
    windows = sorted(value["windows"], key=window_time)
    cadence = value["cadence_seconds"]
    current, best = [], []
    previous = None
    for window in windows:
        adjacent = (
            previous is not None
            and int((window_time(window) - window_time(previous)).total_seconds()) == cadence
        )
        if not window_healthy(window, value["thresholds"]):
            current = []
        elif current and adjacent:
            current.append(window)
        else:
            current = [window]
        if len(current) > len(best):
            best = list(current)
        previous = window
    return [window["id"] for window in best] if len(best) >= minimum else []


def business_window_errors(value, minimum):
    errors = []
    times = [window_time(window) for window in value["windows"]]
    if len(times) != len(set(times)):
        errors.append("recovery-window-time-duplicate")
    if not qualifying_windows(value, minimum):
        errors.append("healthy-consecutive-window-count-insufficient")
    return errors


def verification_errors(specification, actual):
    errors = []
    for criterion, required in specification["criteria"].items():
        if required and actual.get("criteria", {}).get(criterion) is not True:
            errors.append(f"recovery-criterion-failed:{criterion}")
    if not actual.get("limitations"):
        errors.append("recovery-limitations-missing")
    if actual.get("trust_restored") is not True:
        errors.append("trust-not-restored")
    return errors
