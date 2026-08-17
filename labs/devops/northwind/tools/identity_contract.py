#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "security/workload-identity.json"
FAILURE = ROOT / "fixtures/identity/stolen-token-replay.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(failure: bool = False) -> dict[str, bool]:
    contract = read(CONTRACT)
    token = contract["token"]
    federation = contract["federation"]
    payment = contract["payment_provider"]
    authorization = contract["authorization"]
    revocation = contract["revocation"]
    break_glass = contract["break_glass"]
    evidence = contract["evidence"]
    checks = {
        "dedicated_service_account": contract["kubernetes_service_account"] == "order-worker",
        "projected_token_not_environment_secret": token["delivery"] == "projected-file",
        "token_is_audience_bound": token["audience_bound"] is True,
        "token_is_short_lived": token["short_lived"] is True,
        "token_refreshes_automatically": token["automatic_refresh"] is True,
        "supported_dependencies_federate": all(federation.values()),
        "payment_fallback_is_referenced": payment["credential_delivery"] == "brokered-file-reference",
        "payment_rotation_avoids_rebuild": payment["rotation"] == "overlapping-live-reload",
        "payment_rotation_has_overlap": payment["overlap_window"] is True,
        "authorization_is_scoped": authorization["scope"] == "dependency-specific",
        "authorization_defaults_deny": authorization["default_deny"] is True,
        "trust_can_be_revoked": revocation["trust_binding_can_be_disabled"] is True,
        "revocation_avoids_rebuild": revocation["does_not_require_application_rebuild"] is True,
        "break_glass_is_individual": break_glass["identity"] == "individual-federated-operator",
        "break_glass_is_time_bound": break_glass["time_bound"] is True,
        "break_glass_requires_approval": break_glass["approval_required"] is True,
        "identity_decisions_are_auditable": all(evidence.values()),
    }
    if failure:
        scenario = read(FAILURE)
        checks["wrong_audience_is_rejected"] = (
            scenario["issued_audience"] != scenario["attempted_audience"]
            and token["audience_bound"] is True
        )
        checks["revoked_binding_is_rejected"] = (
            scenario["trust_binding_status"] == "revoked"
            and revocation["trust_binding_can_be_disabled"] is True
        )
        checks["static_fallback_is_not_exposed"] = payment["credential_delivery"] != "literal-environment-value"
        checks["verified_workload_can_recover"] = (
            scenario["legitimate_replacement_subject"] == scenario["token_subject"]
            and token["automatic_refresh"] is True
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["stolen-token-replay"])
    args = parser.parse_args()
    checks = analyze(args.scenario == "stolen-token-replay")
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
