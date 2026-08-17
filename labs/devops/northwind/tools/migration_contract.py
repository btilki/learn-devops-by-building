#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/schema-change.json"
FAILURE = ROOT / "fixtures/data/old-writer-during-canary.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(failure: bool = False) -> dict[str, bool]:
    contract = read(CONTRACT)
    coexistence = contract["coexistence"]
    expand = contract["expand"]
    writes = contract["writes"]
    backfill = contract["backfill"]
    enforcement = contract["enforcement"]
    cutover = contract["cutover"]
    contraction = contract["contract"]
    checks = {
        "expand_migrate_contract_strategy": contract["strategy"] == "expand-migrate-contract",
        "additive_expand_is_nullable": expand["nullable"] is True,
        "old_writer_remains_supported": coexistence["old_writer_supported"] is True,
        "dual_write_during_coexistence": writes["mode"] == "dual-write",
        "new_reader_falls_back": coexistence["new_reader_fallback"] is True,
        "backfill_is_batched": backfill["batched"] is True,
        "backfill_is_idempotent": backfill["idempotent"] is True,
        "backfill_progress_is_checkpointed": backfill["checkpointed"] is True,
        "backfill_is_validated": backfill["validation"] == "counts-and-values",
        "enforcement_waits_for_old_version": enforcement["requires_old_version_retired"] is True,
        "enforcement_waits_for_validation": enforcement["requires_backfill_validated"] is True,
        "cutover_is_progressive": cutover["traffic_shift"] == "progressive",
        "cutover_tests_mixed_versions": cutover["compatibility_gate"] == "old-and-new-versions",
        "abort_keeps_compatible_schema": cutover["abort"]
        == "restore-old-route-keep-expanded-schema",
        "dual_run_exit_is_evidence_gated": set(cutover["exit_requires"])
        == {"zero-legacy-writes", "validated-backfill", "rollback-window-closed"},
        "destructive_cleanup_is_separate": contraction["drop_legacy_column"] == "later-reviewed-release",
        "application_rollback_preserves_reads": contraction["rollback_preserves_legacy_reads"] is True,
    }
    if failure:
        scenario = read(FAILURE)
        legacy_value = scenario["written_fields"]["total_cents"]
        checks["old_writer_is_accepted"] = (
            scenario["phase"] == "coexistence"
            and legacy_value is not None
            and coexistence["old_writer_supported"] is True
        )
        checks["new_reader_handles_legacy_row"] = (
            coexistence["new_reader_fallback"] is True and legacy_value is not None
        )
        checks["rollback_preserves_data"] = (
            scenario["rollback_requested"] is True
            and contraction["rollback_preserves_legacy_reads"] is True
            and contraction["drop_legacy_column"] == "later-reviewed-release"
        )
        checks["legacy_write_blocks_dual_run_exit"] = (
            legacy_value is not None and "zero-legacy-writes" in cutover["exit_requires"]
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["old-writer-during-canary"])
    args = parser.parse_args()
    checks = analyze(args.scenario == "old-writer-during-canary")
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
