#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.artifact_evidence import verify  # noqa: E402


def workflow_checks(path: Path) -> dict[str, bool]:
    text = path.read_text(encoding="utf-8")
    promote = text.split("\n  promote:\n", maxsplit=1)[-1]
    return {
        "builds_once": text.count("docker/build-push-action@v6") == 1,
        "floating_latest_absent": ":latest" not in text,
        "sbom_enabled": "sbom: true" in text,
        "max_provenance_enabled": "provenance: mode=max" in text,
        "attestation_generated": "actions/attest@v4" in text,
        "attestation_uses_build_digest": "subject-digest: ${{ steps.build.outputs.digest }}" in text,
        "oidc_permission_scoped": "id-token: write" in text,
        "attestation_permission_scoped": "attestations: write" in text,
        "promotion_uses_prior_digest": "needs.build.outputs.digest" in promote,
        "promotion_does_not_build": "docker/build-push-action" not in promote,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect", choices=["red", "green"], required=True)
    args = parser.parse_args()
    workflow = workflow_checks(ROOT / ".github/workflows/release.yml")
    policy_path = ROOT / "release/expectations.json"
    evidence_ok = False
    evidence_checks: dict[str, bool] = {}
    if policy_path.exists() and (ROOT / "dist/storefront-api.tar").exists():
        try:
            evidence_ok, evidence_checks = verify(policy_path)
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            evidence_ok = False
    capability_ok = all(workflow.values()) and evidence_ok
    report = {
        "expected": args.expect,
        "workflow": workflow,
        "evidence": evidence_checks,
        "capability_ok": capability_ok,
        "expectation_met": capability_ok if args.expect == "green" else not capability_ok,
    }
    output = ROOT / "evidence" / f"chapter-02-{args.expect}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["expectation_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

