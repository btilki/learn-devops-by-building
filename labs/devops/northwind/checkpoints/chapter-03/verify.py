#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.reconcile_infra import (  # noqa: E402
    ACTUAL,
    DESIRED,
    POLICY,
    STATE,
    changes,
    read,
)
from tools.certificate_lifecycle import analyze as analyze_certificate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect", choices=["red", "green"], required=True)
    args = parser.parse_args()
    policy = read(POLICY)
    workflow = (ROOT / ".github/workflows/infrastructure.yml").read_text(encoding="utf-8")
    desired = read(DESIRED) if DESIRED.exists() else {}
    actual = read(ACTUAL)
    checks = {
        "desired_state_exists": bool(desired),
        "remote_encrypted_state": policy.get("backend") == "remote"
        and policy.get("encryption") is True,
        "locking_required": policy.get("locking") is True,
        "plan_is_read_only": "plan:\n" in workflow and "contents: read" in workflow,
        "apply_is_protected": "environment: production-infrastructure" in workflow,
        "pull_requests_do_not_apply": "pull_request" in workflow and "apply --auto-plan" not in workflow,
        "separate_authority": policy.get("plan_role") != policy.get("apply_role"),
        "state_binding_exists": STATE.exists(),
        "actual_matches_desired": bool(desired) and not changes(desired, actual),
        "artifact_is_digest_pinned": "@sha256:" in str(desired.get("artifact", "")),
    }
    checks.update(analyze_certificate())
    ok = all(checks.values())
    report = {
        "expected": args.expect,
        "checks": checks,
        "capability_ok": ok,
        "expectation_met": ok if args.expect == "green" else not ok,
    }
    output = ROOT / "evidence" / f"chapter-03-{args.expect}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["expectation_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
