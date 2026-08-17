#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config/runtime-contract.json"
EXPECTATIONS = ROOT / "config/runtime-expectations.json"
SCENARIO = ROOT / "fixtures/config/invalid-reload.json"
MANIFEST = ROOT / "k8s/base/runtime.yaml"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(values: dict[str, object], expectations: dict[str, object]) -> list[str]:
    errors: list[str] = []
    allowed = set(expectations["allowed_keys"])
    unknown = set(values) - allowed
    if unknown:
        errors.append(f"unknown keys: {sorted(unknown)}")
    if values.get("order_mode") not in expectations["order_mode_values"]:
        errors.append("order_mode is not allowed")
    timeout = values.get("dependency_timeout_ms")
    timeout_policy = expectations["dependency_timeout_ms"]
    if not isinstance(timeout, int) or isinstance(timeout, bool):
        errors.append("dependency_timeout_ms is not an integer")
    elif not timeout_policy["minimum"] <= timeout <= timeout_policy["maximum"]:
        errors.append("dependency_timeout_ms is outside the accepted range")
    return errors


def analyze(invalid_reload: bool = False) -> dict[str, bool]:
    contract = read(CONTRACT)
    expectations = read(EXPECTATIONS)
    scenario = read(SCENARIO)
    manifest = MANIFEST.read_text(encoding="utf-8")
    interfaces = contract["interfaces"]
    validation = contract["validation"]
    reload_policy = contract["reload"]
    evidence = contract["evidence"]

    active_errors = validate(scenario["active"]["values"], expectations)
    candidate_errors = validate(scenario["candidate"]["values"], expectations)
    candidate_accepted = not candidate_errors
    active_version_after = (
        scenario["candidate"]["version"]
        if candidate_accepted
        else scenario["active"]["version"]
    )
    checks = {
        "flags_are_for_startup_contract": interfaces["flags"]["change_behavior"]
        == "restart-required"
        and "--config=/etc/northwind/runtime.yaml" in manifest
        and "--listen=:8080" in manifest,
        "environment_keys_are_explicit": interfaces["environment"]["explicit_keys_only"]
        is True
        and "configMapKeyRef:" in manifest
        and "envFrom:" not in manifest,
        "structured_config_is_read_only_file": interfaces["mounted_file"]["read_only"] is True
        and interfaces["mounted_file"]["reloadable"] is True
        and "mountPath: /etc/northwind" in manifest
        and "readOnly: true" in manifest,
        "schema_is_versioned": validation["schema_version"] == expectations["schema_version"],
        "required_keys_are_declared": set(validation["required_keys"])
        == set(expectations["allowed_keys"]),
        "validation_rejects_bad_types_and_unknown_keys": validation["type_check"] is True
        and validation["reject_unknown_keys"] is True
        and len(candidate_errors) == 2,
        "startup_validation_precedes_readiness": validation["validate_before_ready"] is True,
        "reload_is_atomic": reload_policy["atomic"] is True,
        "invalid_reload_keeps_last_known_good": reload_policy["invalid_candidate"]
        == "reject-and-keep-last-known-good"
        and candidate_accepted is False
        and active_version_after == scenario["expected"]["active_version_after_reload"],
        "valid_active_config_passes": not active_errors
        and scenario["active"]["version"] == expectations["required_active_version"],
        "configuration_identity_is_observable": evidence["config_version_in_telemetry"] is True
        and evidence["source_revision_required"] is True
        and "northwind.io/config-version: config-v1" in manifest,
    }
    if invalid_reload:
        checks["candidate_is_rejected"] = candidate_accepted is scenario["expected"][
            "candidate_accepted"
        ]
        checks["service_keeps_verified_configuration"] = active_version_after == "config-v1"
        checks["readiness_is_preserved_on_safe_rejection"] = (
            scenario["expected"]["readiness_after_reload"] is True
        )
        checks["validation_result_is_emitted"] = (
            reload_policy["emit_result"] is True
            and scenario["expected"]["validation_event_required"] is True
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["invalid-reload"])
    args = parser.parse_args()
    checks = analyze(args.scenario == "invalid-reload")
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
