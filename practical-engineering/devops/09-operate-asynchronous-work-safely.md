# 09 — Operate Asynchronous Work Safely

> **Outcome:** Process at-least-once order messages without duplicating payment or inventory effects, then diagnose and recover from redelivery safely.

**Current Northwind state:** Chapter 8 preserves database compatibility, but `order-worker` still treats each broker delivery as new work.  
**Prerequisites:** Chapters 1–8, database transactions, queue consumers, and external service calls.  
**Implementation:** `books/practical-engineering/labs/devops/northwind/`  
**Guided time:** approximately 100–130 minutes.

## 1. Payment succeeded; acknowledgement disappeared

`order-worker` reserves inventory and the payment provider accepts the charge. The worker commits the order state, but its acknowledgement is lost before the broker records it. The broker delivers the same order again. If the worker equates delivery with intent, the retry can charge the customer twice and reserve inventory twice.

> How can Northwind make redelivery safe when a database, broker, and external payment provider cannot share one atomic transaction?

> **Practice — Establish the unsafe consumer baseline**
>
> Check out the consumer that has no durable identity, transaction boundary, bounded retry policy, quarantine path, or outcome evidence.

```bash
cd books/practical-engineering/labs/devops/northwind
git switch -c my-chapter-09 chapter-09-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-09-baseline
```

One control is already correct: delivery is explicitly at least once. The baseline is red because acknowledging that fact without engineering for duplicates is not a safe capability.

## 2. The production model: repeated delivery, one business effect

> *Theory — Idempotent effect boundaries*
>
> Decide which identity and durable records make repeated execution converge on one observable business outcome.

A broker delivery is an attempt, not a unique business intent. At-least-once systems may redeliver after consumer failure, acknowledgement loss, lease expiry, or broker recovery. Amazon **SQS (Simple Queue Service)** documents that standard queues can deliver a message more than once and advises idempotent consumers. [Amazon SQS at-least-once delivery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html).

```text
stable operation identity
          ↓
receive → recognize or claim → perform idempotent external effect
          ↓                         ↓
     commit inbox + order state + outbox
          ↓
     acknowledge delivery
```

“Exactly once” is not a property Northwind assumes across the whole path. The broker, database, and payment provider have different commit points. Northwind instead makes each effect retry-safe, stores durable evidence of the transition, and acknowledges only after the required outcome is recoverable.

## 3. Give the operation a stable identity

> **Practice — Preserve identity across attempts**
>
> Replace delivery-generated identity with one stable business-operation identifier and serialize conflicting transitions per order.

Edit `messaging/order-worker.json`. Set `message_identity` to `stable-business-operation-id` and `ordering_scope` to `per-order`.

The identifier represents the intent—such as the first payment attempt for order 1042—not the broker's receipt handle or retry count. Every redelivery carries the same identifier. A later, intentionally distinct payment attempt needs a new identifier; otherwise idempotency can suppress legitimate work.

Per-order ordering does not require globally serial processing. Northwind may partition by order, lock the order row, or use a conditional state transition. The necessary guarantee is narrower: two workers cannot concurrently advance the same order through incompatible states.

## 4. Make local effects atomic

> **Practice — Build a transactional inbox and outbox**
>
> Uniquely record consumed operations with the order transition and stage outgoing events in the same database transaction.

Set the deduplication store to `transactional-inbox`; require a unique identity and atomic state transition. Enable `transactional_outbox` and set `publication.order_event` to `same-transaction-outbox`.

The inbox unique constraint turns a race into a database decision. The order update and inbox record commit together, so a redelivery can distinguish completed work from a new operation. The outbox closes the opposite gap: the order state and the intent to publish its event commit together, while a separate relay retries broker publication.

The relay can still publish the same outbox row more than once if it crashes after send and before marking it sent. Downstream consumers therefore remain idempotent. The outbox removes lost publication between database commit and broker send; it does not remove duplicates.

## 5. Bound the external payment effect

> **Practice — Reuse identity at the payment boundary**
>
> Send the message identity as the provider idempotency key for every retry of the same payment operation.

Set `processing.payment_idempotency_key` to `message-id`.

The idempotency key identifies the payment operation; it is not the payment credential. Chapter 5's workload identity authenticates `order-worker` to the secret broker, which supplies the referenced provider credential without placing it in this message or contract. Keep authentication material out of queue payloads, inbox rows, outbox events, and retry evidence.

The database cannot atomically commit with an external provider. If the provider accepts idempotency keys, send the same key and identical operation parameters on every retry. Stripe, for example, documents that repeated requests with the same idempotency key return the saved result instead of performing the operation twice. Provider retention windows and error semantics vary, so Northwind must test the actual contract and retain its own durable operation record. [Stripe idempotent requests](https://docs.stripe.com/api/idempotent_requests).

A safe sequence is:

1. Receive the stable operation identifier.
2. Return the stored result if the inbox already contains a terminal outcome.
3. Call payment with that identifier as its idempotency key.
4. In one database transaction, record the inbox outcome, transition the order, and append the outbox event.
5. Acknowledge only after commit.

If the worker crashes after payment but before database commit, redelivery calls payment with the same key, obtains the prior result, and completes the local transaction. This is why database deduplication alone is insufficient for an external financial effect.

## 6. Control leases, acknowledgements, and retries

> **Practice — Make retry timing an explicit contract**
>
> Acknowledge after durable outcome, cover normal processing with a renewable lease, and retry only transient failures with bounded exponential backoff and jitter.

Set acknowledgement timing to `after-durable-outcome`. Require a lease longer than the processing timeout with renewal support. Set retry classification to `transient-only`, backoff to `exponential`, enable jitter, and choose a finite maximum such as the illustrative value `8`.

The lease must exceed expected processing time but cannot replace idempotency: a paused process or network partition can outlive it. Renewal needs an upper bound so a stuck worker cannot hide a message forever.

Retry connection timeouts, rate limits, and explicitly retryable provider failures. Do not repeatedly retry invalid payloads or forbidden transitions. Exponential backoff reduces pressure; jitter prevents many workers from retrying in lockstep. Attempt count, backoff, and lease duration are workload-specific values that production evidence must tune.

## 7. Quarantine poison messages and measure progress

> **Practice — Make terminal failure recoverable**
>
> Quarantine exhausted or non-retryable messages, preserve their identity, require reviewed replay, and measure duplicates, oldest backlog age, and terminal outcomes.

Enable quarantine, identity preservation, and reviewed replay. Enable all three evidence fields.

Complete `legacy_cutover` for a transition from the legacy worker. Keep the legacy worker as the initial external-effect owner and run the new worker in `shadow-without-external-effects` mode. Both paths may parse, validate, and derive an expected terminal outcome; they must not both charge payment or reserve inventory. Transfer ownership with one reviewed switch, and preserve the original operation identity across both routes so abort does not turn old work into new financial intent.

A dead-letter queue is isolation, not resolution. Its runbook must retain payload version, operation identity, source queue, failure classification, attempt history, and relevant trace context. Replay must use the original identity; minting a new identifier converts replay into a new payment operation. Repair the cause, select the exact messages, bound replay rate, and watch both source and destination outcomes.

Queue depth alone is ambiguous because normal traffic changes it. Oldest-message age shows whether work is making timely progress. Duplicate count reveals retry pressure, while terminal order outcomes distinguish a busy worker from a useful one.

Use `fixtures/messaging/dual-run-cutover.json` as the observed cutover evidence. The new path shadows 10,000 operations without external effects, terminal outcomes reconcile with no unexplained mismatch, the legacy backlog reaches zero, identities remain stable, and the rollback window closes. The checkpoint calculates whether those observations permit retirement; setting an `enabled` flag cannot bypass the decision. If any condition fails, keep or restore the legacy owner, preserve the inbox and provider identities, and diagnose before shifting ownership again.

> **Practice — Verify the asynchronous processing contract**
>
> Check identity, concurrency, inbox/outbox atomicity, payment idempotency, acknowledgement, lease, retry, quarantine, replay, and outcome evidence together.

```bash
make chapter-09-checkpoint
```

The model verifies the declared protocol. Production must also test broker outage, provider timeout after acceptance, database failover during commit, lease-renewal failure, relay duplication, message expiry, and replay under load.

## 8. Redeliver after a successful payment

**Severity:** duplicate financial and inventory effects after acknowledgement loss.  
**Potential blast radius:** one order per unsafe duplicate; a retry storm can widen this across the active backlog.  
**Bounded by:** stable operation identity, provider idempotency, transactional inbox/outbox, per-order serialization, and bounded retries.  
**Primary principles:** explicit contracts, trustworthy evidence, reconciliation, blast-radius control, and recovery.

> **Practice — Prove acknowledgement loss is safe**
>
> Redeliver an operation whose payment and database state succeeded, then verify the second attempt converges without another charge.

```bash
make chapter-09-break
```

The scenario must report `redelivery_is_detected`, `completed_inbox_skips_effect`, `second_charge_is_suppressed`, `committed_outcome_survives_ack_loss`, and `redelivery_can_be_acknowledged` as true. The completed inbox prevents a second call in this scenario. Reusing the provider key remains a separate defense for a crash after provider acceptance but before the inbox transaction commits.

Acknowledging the duplicate is an action, not complete recovery. Verify exactly one provider-side payment for the operation key, one valid inventory transition, one correct terminal order state, no stuck outbox record, and recovered oldest-message age. Retain the duplicate and acknowledgement-loss evidence for diagnosis.

## 9. Production reality

**Best Practice:** assume redelivery, give each intent stable identity, make local state atomic, make external effects idempotent, acknowledge after durable outcome, classify and bound retries, and quarantine poison messages.

**Production Practice:** validate provider idempotency retention, broker lease and ordering semantics, database contention, partition distribution, outbox relay lag, replay authorization, privacy retention, and capacity during dependency recovery. Ordering can reduce concurrency and create hot partitions; choose the smallest ordering scope that protects the business invariant.

## 10. What changed

| Before | After |
|---|---|
| Every delivery represented new work. | A stable operation identity survives redelivery. |
| Database and broker writes could diverge. | Inbox, order state, and outbox define recoverable transaction boundaries. |
| A payment retry could repeat the charge. | The provider receives the same idempotency key for the same intent. |
| Acknowledgement and retry timing were implicit. | Durable outcome, leases, classifications, backoff, and limits govern retries. |
| Failed messages disappeared into repeated attempts. | Quarantine and reviewed replay preserve identity and evidence. |
| Queue depth implied worker health. | Age, duplicates, and terminal outcomes measure useful progress. |
| Old and new workers could both own side effects during migration. | Shadow comparison precedes one reviewed ownership switch, and reconciled evidence gates legacy retirement. |

## Durable outputs

- Asynchronous effect and legacy-cutover contract: `messaging/order-worker.json`.
- Executable dual-run evidence: `fixtures/messaging/dual-run-cutover.json` and the Chapter 9 checkpoint report.

## What You Learned

At-least-once delivery moves correctness into the consumer and its effect boundaries. You can now distinguish an attempt from an intent, combine inbox and outbox records with business state, extend idempotency to an external provider, design bounded retry and quarantine paths, and migrate worker ownership without allowing dual-run to duplicate external effects.

### Prove It

> **Independent Practice — Recover a payment-provider outage**
>
> Design the response when payment times out for 40 minutes, 60,000 orders queue, and the provider recovers with half Northwind's normal request capacity.

Define operation identity, retry classification and schedule, lease behavior, backlog admission, per-order ordering, worker concurrency, provider rate limiting, oldest-age alerting, quarantine criteria, recovery ramp, reconciliation queries, and evidence that no order was charged twice or permanently lost. Justify which controls prevent recovery from becoming a second outage.

## Next

Northwind can now process asynchronous work safely. Chapter 10 makes the reviewed delivery repository continuously reconcile environments without giving every automation path production authority.
