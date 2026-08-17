#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "infra/certificate-lifecycle.json"
EXPECTATIONS = ROOT / "infra/certificate-expectations.json"
SCENARIO = ROOT / "fixtures/certificates/renewal.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(expiry_scenario: bool = False) -> dict[str, bool]:
    contract = read(CONTRACT)
    expectations = read(EXPECTATIONS)
    scenario = read(SCENARIO)
    ownership = contract["ownership"]
    key_material = contract["key_material"]
    renewal_policy = contract["renewal"]
    validation = contract["validation"]
    expiry_policy = contract["expiry"]
    current = scenario["current_certificate"]
    renewal = scenario["renewal"]
    replacement = scenario["replacement_certificate"]
    endpoint = scenario["endpoint_after_switch"]

    renewal_lead_days = current["not_after_day"] - renewal["requested_day"]
    overlap_valid = (
        replacement["not_before_day"]
        <= renewal["endpoint_switched_day"]
        <= current["not_after_day"]
    )
    replacement_validity_days = replacement["not_after_day"] - replacement["not_before_day"]
    endpoint_valid = (
        endpoint["served_serial"] == replacement["serial"]
        and expectations["hostname"] in replacement["hostnames"]
        and replacement["chain_valid"] is True
        and endpoint["tls_available"] is True
    )
    checks = {
        "certificate_has_owner": bool(ownership["service_owner"]),
        "certificate_is_declarative": ownership["provisioning"] == "declarative",
        "hostname_matches_expectation": ownership["hostname"] == expectations["hostname"],
        "key_is_referenced_not_embedded": key_material["source"] == "managed-reference"
        and key_material["embedded_in_state"] is False,
        "renewal_is_automatic": renewal_policy["automated"] is True,
        "renewal_policy_has_required_lead": renewal_policy["renew_before_expiry_days"]
        >= expectations["minimum_renewal_lead_days"],
        "late_renewal_alert_is_bounded": renewal_policy["alert_when_remaining_days"]
        <= expectations["maximum_unalerted_remaining_days"],
        "observed_renewal_meets_declared_lead": renewal_lead_days
        >= renewal_policy["renew_before_expiry_days"],
        "old_and_new_certificates_overlap": renewal_policy["overlap_required"] is True
        and overlap_valid,
        "replacement_validity_is_sufficient": replacement_validity_days
        >= expectations["minimum_replacement_validity_days"],
        "endpoint_serves_verified_replacement": all(validation.values()) and endpoint_valid,
        "plaintext_fallback_is_forbidden": expiry_policy["plaintext_fallback"] is False
        and endpoint["plaintext_fallback"] is False,
        "traffic_requires_valid_certificate": expiry_policy[
            "traffic_release_requires_valid_certificate"
        ]
        is True,
    }
    if expiry_scenario:
        expired = scenario["expired_without_replacement"]
        checks["expired_certificate_fails_closed"] = (
            expired["observation_day"] > current["not_after_day"]
            and expiry_policy["behavior"] == "tls-unavailable"
            and expired["tls_available"] is False
            and expired["plaintext_fallback"] is False
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["expiry-without-replacement"])
    args = parser.parse_args()
    checks = analyze(args.scenario == "expiry-without-replacement")
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
