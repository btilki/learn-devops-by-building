#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.observability_contract import analyze  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect", choices=["red", "green"], required=True)
    args = parser.parse_args()
    checks = analyze()
    ok = all(checks.values())
    report = {"expected": args.expect, "checks": checks, "capability_ok": ok, "expectation_met": ok if args.expect == "green" else not ok}
    output = ROOT / "evidence" / f"chapter-06-{args.expect}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["expectation_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
