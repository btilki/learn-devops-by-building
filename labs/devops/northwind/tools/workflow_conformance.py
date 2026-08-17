#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "delivery/workflow-conformance.json"
WORKFLOW = ROOT / ".github/workflows/ci.yml"


def read_contract(path: Path = CONTRACT) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def job_blocks(text: str) -> dict[str, str]:
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    in_jobs = False
    for line in text.splitlines():
        if line == "jobs:":
            in_jobs = True
            continue
        if in_jobs and line and not line.startswith(" "):
            break
        match = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line) if in_jobs else None
        if match:
            current = match.group(1)
            blocks[current] = []
        elif current is not None:
            blocks[current].append(line)
    return {name: "\n".join(lines) for name, lines in blocks.items()}


def analyze(workflow: Path = WORKFLOW) -> dict[str, bool]:
    contract = read_contract()
    text = workflow.read_text(encoding="utf-8")
    blocks = job_blocks(text)
    template_marker = f"# northwind-template: {contract['template_id']}"
    required_jobs = set(contract["required_jobs"])
    checks = {
        "reviewed_template_version_is_declared": template_marker in text,
        "required_jobs_are_present": required_jobs <= set(blocks),
        "default_authority_conforms": f"permissions:\n  {contract['default_permission']}" in text,
        "forbidden_authority_is_absent": all(
            permission not in text for permission in contract["forbidden_permissions"]
        ),
        "required_edges_conform": all(
            f"needs: {dependency}" in blocks.get(job, "")
            for job, dependency in contract["required_needs"].items()
        ),
        "required_evidence_commands_remain": all(
            command in blocks.get(job, "")
            for job, command in contract["required_commands"].items()
        ),
    }
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", type=Path, default=WORKFLOW)
    parser.add_argument("--expect", choices=["pass", "fail"], default="pass")
    args = parser.parse_args()
    checks = analyze(args.workflow)
    conforms = all(checks.values())
    expectation_met = conforms if args.expect == "pass" else not conforms
    print(
        json.dumps(
            {
                "workflow": str(args.workflow),
                "checks": checks,
                "conforms": conforms,
                "expectation_met": expectation_met,
            },
            indent=2,
        )
    )
    return 0 if expectation_met else 1


if __name__ == "__main__":
    raise SystemExit(main())
