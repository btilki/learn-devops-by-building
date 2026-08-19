# 08 — Change Data Without Breaking Compatibility

> **Outcome:** Change an order schema while stable and candidate versions coexist, migrate existing rows safely, and preserve application rollback.

**Current Northwind state:** Chapter 7 limits candidate traffic, but stable and candidate replicas can still access the same persistent data during rollout and abort.  
**Prerequisites:** Chapters 1–7, relational database transactions, and basic migration tooling.  
**Implementation:** `books/practical-engineering/labs/devops/northwind/`  
**Guided time:** approximately 90–120 minutes.

## 1. A safe binary rollout meets an unsafe schema

Northwind wants to rename `orders.total_cents` to `orders.order_total_cents`. The first migration adds the replacement as required, the candidate writes only the replacement, and the same release drops the legacy column. During the 5% canary, stable replicas still read and write the legacy field. An abort restores the old binary—but not the column it needs.

> How can Northwind evolve persistent data while old and new versions overlap, background migration is incomplete, and application rollback remains possible?

> **Practice — Establish the incompatible baseline**
>
> Check out the unsafe schema change and prove that coexistence, migration, validation, enforcement, cleanup, and rollback contracts are red.

```bash
cd books/practical-engineering/labs/devops/northwind
git switch -c my-chapter-08 chapter-08-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-08-baseline
```

## 2. The production model: expand, migrate, contract

> *Theory — Compatibility across independently timed phases*
>
> Decide which schema and application changes may run concurrently without making deployment or rollback depend on one perfectly timed event.

A schema change and an application rollout are separate distributed transitions. Connections remain open, replicas update at different times, a backfill may take hours, and rollback may reintroduce the old binary. A production-safe change therefore preserves compatibility across three phases:

```text
expand                  migrate                         contract
add compatible shape → move reads/writes and data → remove legacy shape later
       old + new run          retries are safe              old is absent
```

**Expand** adds an optional structure without invalidating existing readers or writers. **Migrate** changes application behavior and existing data while both representations remain valid. **Contract** enforces the final invariant and removes the legacy structure only after evidence proves no supported version depends on it.

This pattern buys rollback time at the cost of temporary schema and application complexity. It is not a command sequence to run without observation: each transition has an entry condition, evidence, and a separate recovery decision.

## 3. Expand without invalidating stable

> **Practice — Add a compatible representation**
>
> Replace the direct rename with a nullable additive field and explicitly preserve the old writer during version coexistence.

Edit `data/schema-change.json`. Set `strategy` to `expand-migrate-contract`, keep `total_cents`, add `order_total_cents` as nullable, and set `coexistence.old_writer_supported` to true.

Adding a nullable column is the model, not a universal claim that every database executes the change without blocking. Before production, inspect the database engine and version, table size, lock mode, rewrite behavior, replication lag, and transaction timeout. PostgreSQL, for example, documents that `ALTER TABLE` subcommands require different lock levels and that some forms rewrite the table and indexes. A logically compatible statement can still cause an operational outage. [PostgreSQL `ALTER TABLE`](https://www.postgresql.org/docs/current/sql-altertable.html).

## 4. Move behavior while both versions run

> **Practice — Make writes and reads coexist**
>
> Dual-write both fields and let the candidate read the new value with a legacy fallback.

Set `writes.mode` to `dual-write` and `coexistence.new_reader_fallback` to true. During the overlap:

```text
write: total_cents = value, order_total_cents = value
read:  order_total_cents if present, otherwise total_cents
```

The application should update both values in one database transaction. Dual writing through two independent requests creates a new partial-failure problem. If multiple services write the table, inventory every writer—including jobs, administrative tools, and old consumers—before declaring coexistence safe.

The fallback is intentionally temporary. Instrument how often it is used. A falling count proves migration progress; a persistent count reveals an undiscovered writer or failed backfill.

## 5. Backfill as resumable production work

> **Practice — Define a bounded, retry-safe backfill**
>
> Require batches, idempotent updates, durable progress checkpoints, and validation of both row coverage and values.

Set `backfill.batched`, `backfill.idempotent`, and `backfill.checkpointed` to true. Set validation to `counts-and-values`.

A safe worker updates only missing replacements, commits bounded batches, records its cursor, and can repeat a batch without changing a correct row. Batch size is a measured control, not a constant: tune it against lock duration, replica lag, transaction logs, foreground latency, and available capacity. Throttle or pause when those signals cross Northwind's tested limits.

Counting non-null rows detects missing coverage but not incorrect values. Compare values or invariants as well—for this change, every migrated row must satisfy `order_total_cents = total_cents`. Sample-based validation may supplement, but not silently replace, a complete invariant when the consequence is financial corruption.

## 6. Delay enforcement and destruction

> **Practice — Put evidence before contraction**
>
> Require retirement of the old version and validated backfill before enforcement, then move destructive cleanup to a later reviewed release.

Set both enforcement prerequisites to true. Set `contract.drop_legacy_column` to `later-reviewed-release` and `rollback_preserves_legacy_reads` to true.

For a legacy cutover, also complete `cutover`: shift traffic progressively, test old and new versions together, and define abort as restoring the old route while keeping the expanded schema. Require zero observed legacy writes, validated backfill, and closure of the agreed rollback window before exiting dual-run. These are separate facts: a complete backfill does not prove that an undiscovered legacy writer has stopped.

“Candidate reached 100%” is not enough. Confirm no old replica, worker, scheduled job, rollback target, or externally maintained client still uses the legacy field. Then enforce the new invariant. Drop the old column only after the agreed rollback window closes and telemetry shows zero legacy reads and writes.

Application rollback and schema rollback are not symmetric. Rolling back application traffic is often fast; reversing a destructive data migration may require restoring data. Northwind therefore rolls back the binary while keeping the expanded schema, then repairs forward unless evidence requires a separately rehearsed data recovery.

Treat dual-run as a temporary transition with an owner and deadline, not a permanent compatibility layer. Record which path is authoritative, compare old and new outcomes, and stop the cutover when correctness, latency, or capacity evidence crosses its abort boundary. Retire the legacy path only through a reviewed decision backed by the exit evidence; do not infer retirement from low traffic alone.

> **Practice — Verify the compatibility contract**
>
> Check expansion, coexistence, backfill safety, validation gates, delayed enforcement, separate cleanup, and application rollback together.

```bash
make chapter-08-checkpoint
```

The checkpoint verifies the declared migration protocol. Production must additionally rehearse engine-specific locking, cancellation, replication behavior, backup restoration, connection-pool pressure, and the effect of a partially completed backfill.

## 7. Keep an old writer safe during canary

**Severity:** order-write incompatibility during a mixed-version release.  
**Potential blast radius:** orders handled by stable replicas while the candidate and backfill coexist.  
**Bounded by:** additive schema, transactional dual writes, reader fallback, delayed enforcement, and separate destructive cleanup.  
**Primary principles:** explicit contracts, blast-radius control, trustworthy evidence, and recovery.

> **Practice — Exercise mixed-version compatibility**
>
> Let an old stable replica write only the legacy field, then prove the candidate can read the row and application rollback preserves the data.

```bash
make chapter-08-break
```

The scenario must report `old_writer_is_accepted`, `new_reader_handles_legacy_row`, `rollback_preserves_data`, and `legacy_write_blocks_dual_run_exit` as true. A passing check does not mean migration is complete; it proves the deliberately mixed state remains serviceable and correctly prevents premature retirement.

Recovery is not merely stopping the candidate. Return traffic to the verified stable digest, leave the compatible expansion in place, stop or pause the backfill safely, verify new orders remain correct, and retain progress so the migration can resume without duplicating effects.

## 8. Production reality

**Best Practice:** use expand–migrate–contract, keep transitions backward compatible, make backfills bounded and idempotent, validate before enforcement, and separate destructive cleanup.

**Production Practice:** test the exact database engine and dataset; account for locks, replicas, long transactions, caches, change-data-capture consumers, old jobs, and rollback windows. Some changes require shadow tables, online schema-change tooling, or application-level translation rather than a direct alteration. The safe mechanism follows observed workload and failure behavior.

## 9. What changed

| Before | After |
|---|---|
| One release renamed and removed a live field. | Expansion, migration, enforcement, and cleanup are independently gated. |
| Stable and candidate required incompatible schemas. | Old writers and new readers coexist. |
| The backfill was an unbounded one-time action. | Batches are retry-safe, checkpointed, throttleable, and validated. |
| Candidate completion authorized destruction. | Old-version retirement and migration evidence authorize later contraction. |
| Application abort depended on restoring removed data. | Rollback keeps the compatible expanded schema and preserves legacy reads. |
| Legacy retirement followed assumed completion. | Measured legacy writes, validated data, and the rollback window gate dual-run exit. |

## Durable outputs

- Schema evolution and cutover contract: `data/schema-change.json`.
- Mixed-version failure evidence: `fixtures/data/old-writer-during-canary.json` and the Chapter 8 checkpoint report.

## What You Learned

Persistent data makes release phases overlap even when deployment tooling appears sequential. You can now design a compatibility window, move reads and writes without a flag day, run a resumable backfill, distinguish validation from completion, abort a legacy cutover without reversing compatible data, and retire the old path only after its exit evidence is complete.

### Prove It

> **Independent Practice — Evolve an order state safely**
>
> Replace a free-text `orders.status` field with a constrained state model while an external reporting consumer updates only once per day.

Define the expansion, old/new read and write behavior, invalid-value handling, backfill cursor and throttle signals, validation queries, consumer evidence, enforcement gate, rollback window, cleanup authority, and response to a backfill stopped at 63%. Justify which step is reversible and which requires restore evidence.

## Next

Northwind can now change synchronous application data safely. Chapter 9 applies the same compatibility and evidence discipline to at-least-once asynchronous work, where retries can duplicate external effects.
