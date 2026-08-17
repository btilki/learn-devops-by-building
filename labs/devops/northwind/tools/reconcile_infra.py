#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".northwind-infra"
ACTUAL = RUNTIME / "cloud-production.json"
STATE = RUNTIME / "state-production.json"
PLAN = RUNTIME / "production.plan.json"
LOCK = RUNTIME / "production.lock"
SEED = ROOT / "fixtures/cloud/production.seed.json"
DESIRED = ROOT / "infra/environments/production/desired.json"
POLICY = ROOT / "infra/backend-policy.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def reset() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SEED, ACTUAL)
    for path in (STATE, PLAN, LOCK):
        path.unlink(missing_ok=True)


def import_existing() -> None:
    actual = read(ACTUAL)
    write(STATE, {"serial": 1, "binding": {"northwind_service.storefront": actual["id"]}, "observed": actual})


def changes(desired: dict[str, object], actual: dict[str, object]) -> list[dict[str, object]]:
    return [
        {"field": key, "before": actual.get(key), "after": value}
        for key, value in desired.items()
        if key != "id" and actual.get(key) != value
    ]


def create_plan() -> dict[str, object]:
    desired, actual = read(DESIRED), read(ACTUAL)
    state = read(STATE)
    plan = {
        "resource": "northwind_service.storefront",
        "state_serial": state["serial"],
        "configuration_digest": digest(desired),
        "observed_digest": digest(actual),
        "changes": changes(desired, actual),
        "destructive_changes": 0,
    }
    write(PLAN, plan)
    return plan


def apply_plan(auto_plan: bool = False) -> None:
    if auto_plan:
        create_plan()
    plan, desired, actual, state, policy = read(PLAN), read(DESIRED), read(ACTUAL), read(STATE), read(POLICY)
    if not policy.get("locking"):
        raise SystemExit("apply blocked: backend locking is required")
    if plan["configuration_digest"] != digest(desired) or plan["observed_digest"] != digest(actual):
        raise SystemExit("apply blocked: saved plan is stale")
    try:
        descriptor = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise SystemExit("apply blocked: state lock is held") from error
    try:
        os.close(descriptor)
        applied = {**actual, **desired, "id": actual["id"]}
        write(ACTUAL, applied)
        write(STATE, {"serial": int(state["serial"]) + 1, "binding": state["binding"], "observed": applied})
    finally:
        LOCK.unlink(missing_ok=True)


def drift(replicas: int) -> None:
    actual = read(ACTUAL)
    actual["replicas"] = replicas
    write(ACTUAL, actual)


def status() -> dict[str, object]:
    actual = read(ACTUAL)
    desired = read(DESIRED) if DESIRED.exists() else {}
    return {"actual": actual, "desired": desired, "changes": changes(desired, actual)}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("reset")
    sub.add_parser("import-existing")
    sub.add_parser("plan")
    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument("--auto-plan", action="store_true")
    drift_parser = sub.add_parser("drift")
    drift_parser.add_argument("--replicas", type=int, required=True)
    sub.add_parser("status")
    args = parser.parse_args()
    if args.command == "reset":
        reset()
    elif args.command == "import-existing":
        import_existing()
    elif args.command == "plan":
        print(json.dumps(create_plan(), indent=2))
    elif args.command == "apply":
        apply_plan(args.auto_plan)
    elif args.command == "drift":
        drift(args.replicas)
    else:
        print(json.dumps(status(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
