#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "gitops/sync-storm-contract.json"
SCENARIO = ROOT / "fixtures/gitops/sync-storm.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def simulate(contract: dict[str, object], scenario: dict[str, object]) -> dict[str, object]:
    coordination = contract["coordination"]
    wave_policy = contract["waves"]
    degraded_policy = contract["degraded_control_plane"]
    requested = sum(item["requested_parallel_applies"] for item in scenario["controllers"])
    peak = min(requested, coordination["global_parallel_apply_limit"])
    events: list[dict[str, object]] = []
    applied = 0
    last_wave: str | None = None

    for wave in scenario["waves"]:
        batches = math.ceil(wave["resources"] / peak)
        applied += wave["resources"]
        last_wave = wave["name"]
        events.append(
            {
                "event": "wave_applied",
                "wave": wave["name"],
                "resources": wave["resources"],
                "batches": batches,
                "healthy": wave["healthy_after_apply"],
            }
        )
        if wave["healthy_after_apply"] is False and wave_policy["stop_after_unhealthy_wave"]:
            events.append({"event": "later_waves_suspended", "after": wave["name"]})
            break

    pruned = scenario["prune_requests"]
    if (
        scenario["control_plane"]["degraded"] is True
        and degraded_policy["prune_action"] == "suspend"
    ):
        pruned = 0
    source_after = scenario["source_revision"]
    if degraded_policy["source_mutation"] != "forbidden":
        source_after = "controller-rewritten-source"

    return {
        "events": events,
        "peak_concurrent_applies": peak,
        "applied_resources": applied,
        "last_applied_wave": last_wave,
        "pruned_resources": pruned,
        "source_revision_after": source_after,
    }


def analyze() -> dict[str, bool]:
    contract = read(CONTRACT)
    scenario = read(SCENARIO)
    result = simulate(contract, scenario)
    expected = scenario["expected"]
    retry_offsets = [item["retry_offset_seconds"] for item in scenario["controllers"]]
    return {
        "global_limit_binds_all_controllers": result["peak_concurrent_applies"]
        == expected["peak_concurrent_applies"]
        and result["peak_concurrent_applies"]
        <= scenario["control_plane"]["maximum_concurrent_applies"],
        "retries_are_staggered": contract["coordination"]["retry_jitter_required"] is True
        and len(set(retry_offsets)) == len(retry_offsets),
        "dependency_failure_stops_later_wave": result["last_applied_wave"]
        == expected["last_applied_wave"]
        and result["applied_resources"] == expected["applied_resources"]
        and any(event["event"] == "later_waves_suspended" for event in result["events"]),
        "degraded_control_plane_suspends_prune": result["pruned_resources"]
        == expected["pruned_resources"],
        "controller_preserves_reviewed_source": result["source_revision_after"]
        == expected["source_revision_after"],
    }


def main() -> int:
    contract = read(CONTRACT)
    scenario = read(SCENARIO)
    checks = analyze()
    report = {"trace": simulate(contract, scenario), "checks": checks, "ok": all(checks.values())}
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
