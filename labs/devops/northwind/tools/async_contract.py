#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "messaging/order-worker.json"
FAILURE = ROOT / "fixtures/messaging/payment-succeeded-ack-lost.json"
CUTOVER = ROOT / "fixtures/messaging/dual-run-cutover.json"


def read(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def analyze(failure: bool = False) -> dict[str, bool]:
    contract = read(CONTRACT)
    processing = contract["processing"]
    publication = contract["publication"]
    acknowledgement = contract["acknowledgement"]
    lease = contract["lease"]
    retry = contract["retry"]
    quarantine = contract["quarantine"]
    cutover = contract["legacy_cutover"]
    evidence = contract["evidence"]
    cutover_scenario = read(CUTOVER)
    shadow_is_safe = (
        cutover["new_worker_mode"] == "shadow-without-external-effects"
        and cutover_scenario["shadow_external_effects"] == 0
    )
    exit_allowed = (
        shadow_is_safe
        and cutover_scenario["shadowed_operations"] > 0
        and cutover_scenario["terminal_outcome_mismatches"] == 0
        and cutover_scenario["legacy_backlog"] == 0
        and cutover_scenario["rollback_window_closed"] is True
        and cutover_scenario["identity_preserved_across_routes"] is True
    )
    checks = {
        "delivery_semantics_are_explicit": contract["delivery"] == "at-least-once",
        "identity_survives_redelivery": contract["message_identity"] == "stable-business-operation-id",
        "per_order_transitions_are_serialized": contract["ordering_scope"] == "per-order",
        "durable_inbox_records_duplicates": processing["deduplication_store"] == "transactional-inbox",
        "deduplication_is_unique": processing["deduplication_unique"] is True,
        "state_transition_is_atomic": processing["state_transition_atomic"] is True,
        "payment_uses_same_idempotency_key": processing["payment_idempotency_key"] == "message-id",
        "publication_uses_outbox": publication["transactional_outbox"] is True,
        "outbox_is_committed_with_state": publication["order_event"] == "same-transaction-outbox",
        "ack_follows_durable_outcome": acknowledgement["timing"] == "after-durable-outcome",
        "lease_covers_processing": lease["exceeds_processing_timeout"] is True,
        "lease_can_be_renewed": lease["renewal_supported"] is True,
        "retries_are_classified": retry["classification"] == "transient-only",
        "retries_are_bounded": retry["maximum_attempts"] > 0,
        "retry_storm_is_dispersed": retry["backoff"] == "exponential" and retry["jitter"] is True,
        "poison_messages_are_quarantined": quarantine["enabled"] is True,
        "replay_preserves_identity": quarantine["preserve_message_identity"] is True,
        "replay_is_reviewed": quarantine["reviewed_replay"] is True,
        "dual_run_has_one_effect_owner": cutover["initial_effect_owner"] == "legacy-worker"
        and shadow_is_safe,
        "ownership_changes_once_under_review": cutover["ownership_transition"]
        == "single-reviewed-switch",
        "cutover_abort_preserves_identity": cutover["abort"]
        == "restore-legacy-owner-preserve-identities",
        "legacy_exit_uses_reconciled_evidence": set(cutover["exit_requires"])
        == {
            "zero-legacy-backlog",
            "reconciled-terminal-outcomes",
            "rollback-window-closed",
        }
        and exit_allowed is cutover_scenario["expected"]["cutover_allowed"],
        "legacy_path_retires_only_after_exit": exit_allowed
        is cutover_scenario["expected"]["legacy_path_can_retire"],
        "duplicate_evidence_exists": evidence["duplicate_count"] is True,
        "backlog_age_is_measured": evidence["oldest_message_age"] is True,
        "terminal_outcome_is_measured": evidence["terminal_outcome"] is True,
    }
    if failure:
        scenario = read(FAILURE)
        same_identity = scenario["second_delivery"]["same_message_id"] is True
        first_committed = scenario["first_delivery"]["state_committed"] is True
        checks["redelivery_is_detected"] = (
            scenario["deliveries"] > 1 and same_identity and processing["deduplication_unique"] is True
        )
        checks["completed_inbox_skips_effect"] = (
            first_committed
            and processing["deduplication_store"] == "transactional-inbox"
            and processing["deduplication_unique"] is True
        )
        checks["second_charge_is_suppressed"] = (
            scenario["second_delivery"]["unprotected_handler_would_request_payment"] is True
            and processing["payment_idempotency_key"] == "message-id"
            and same_identity
        )
        checks["committed_outcome_survives_ack_loss"] = (
            first_committed and acknowledgement["timing"] == "after-durable-outcome"
        )
        checks["redelivery_can_be_acknowledged"] = (
            first_committed
            and processing["deduplication_store"] == "transactional-inbox"
            and processing["state_transition_atomic"] is True
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["payment-succeeded-ack-lost"])
    args = parser.parse_args()
    checks = analyze(args.scenario == "payment-succeeded-ack-lost")
    ok = all(checks.values())
    print(json.dumps({"checks": checks, "ok": ok}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
