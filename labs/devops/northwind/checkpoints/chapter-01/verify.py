#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.context_gate import measure  # noqa: E402
from tools.pipeline_feedback import analyze  # noqa: E402
from tools.workflow_conformance import analyze as analyze_workflow_conformance  # noqa: E402


def workflow_checks(path: Path) -> dict[str, bool]:
    text = path.read_text(encoding="utf-8")
    return {
        "workflow_read_only_by_default": "permissions:\n  contents: read" in text,
        "pull_request_has_no_write_permission": "packages: write" not in text,
        "floating_latest_absent": ":latest" not in text,
        "context_gate_present": "tools/context_gate.py" in text,
        "lint_before_test": "needs: lint" in text,
        "test_before_build": "needs: test" in text,
    }


def run_application_tests() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "services/storefront-api/tests", "-q"],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect", choices=["red", "green"], required=True)
    args = parser.parse_args()
    pipeline = ROOT / "delivery/pipeline.json"
    pipeline_report = analyze(pipeline, budget_seconds=600)
    context_bytes, _ = measure(ROOT)
    context_ok = context_bytes <= 209_715_200
    checks: dict[str, object] = {
        "expected": args.expect,
        "pipeline": pipeline_report,
        "context_bytes": context_bytes,
        "context_ok": context_ok,
    }
    authority = workflow_checks(ROOT / ".github/workflows/ci.yml")
    checks["workflow"] = authority
    checks["template_conformance"] = analyze_workflow_conformance()
    checks["application_tests_ok"] = run_application_tests()
    capability_ok = bool(
        pipeline_report["ok"]
        and context_ok
        and all(authority.values())
        and all(checks["template_conformance"].values())
        and checks["application_tests_ok"]
    )
    checks["capability_ok"] = capability_ok
    checks["expectation_met"] = capability_ok if args.expect == "green" else not capability_ok
    output = ROOT / "evidence" / f"chapter-01-{args.expect}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks, indent=2))
    print(f"evidence={output.relative_to(ROOT)}")
    return 0 if checks["expectation_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
