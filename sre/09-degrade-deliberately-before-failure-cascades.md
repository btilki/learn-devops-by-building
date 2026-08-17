# Degrade Deliberately Before Failure Cascades

Chapter 8 put payment, warehouse, and email inside the reliability contract. Payment timeout is Storefront journey-burn. Warehouse timeout is Fulfillment journey-burn. Email stays skip-and-record. Those bounds still sit on the provider row. `order-worker` can retry payment without a shed. Storefront can accept orders the worker cannot finish. Fulfillment can be pulled into Storefront’s retry storm. Graphs of “accepted orders” stay green.

The production question is now:

> How does Northwind shed load, refuse work, or run in a degraded mode before a local failure becomes every journey's outage?

Without that design, “try harder” converts a payment slowness into a portfolio outage. Silent drop without a named degraded mode hides customer harm. Chapter 8’s retry budget of `1` is not permission to retry until both **SLOs (Service Level Objectives)** are exhausted. Chapter 5 already pages `order_success_ratio` at Storefront and `dispatch_success_ratio` at Fulfillment. Chapter 9 must not page Fulfillment as the cause of Storefront payment slowness.

This chapter names degraded modes, shedding rules, and cascade denials that protect Chapter 3 journeys. Degraded success is accounted as Storefront burn, not as a good accept. Unbounded retries fail the check. The lab does not inject live overload. Tenant quota and unit-cost scaling remain Platform and DevOps; they are not this shed.

## 1. An unsafe retry storm

A weak record says:

```yaml
worker: order-worker
retry_limit: unbounded
action: accept-anyway
accounting: success
page_cause: fulfillment-oncall
```

It keeps accepting orders while payment is slow. It treats those accepts as good events. It retries until shared capacity takes Fulfillment with it. It pages `fulfillment-oncall` as if dispatch were the cause. “The accept graph is green” may describe a counter. It cannot complete a degradation design.

Work from the lab working tree using the Chapter 0 procedure. From the SRE lab root, run the Chapter 9 baseline:

```bash
make chapter-09-baseline
```

The command succeeds when it detects the intended unsafe design:

```text
chapter 09 baseline: unbounded payment retries cascading into fulfillment correctly detected
```

The fixture leaves retries unbounded, accepts work the worker cannot finish, counts those accepts as success, and pages Fulfillment as the payment cause. Availability theater continues: green accept graphs, exhausted budgets on both journeys, informal heroics on the wrong rotation.

That inversion drives the chapter.

## 2. The production model: named mode, shed, and cascade deny

> *Theory — Degradation before cascade*
>
> This model enables Northwind to refuse new accepts and bound `order-worker` retries when payment is overloaded, rather than amplifying retries until Fulfillment burns and the accept graph stays green.

### A degraded mode is user-visible and accounted as burn

Degradation is a named state with a user-visible behavior. Checkout refuses new orders, or it shows that payment cannot complete. That is honest. A `200` on accept while payment never finishes is silent drop. Silent drop is availability theater wearing a success counter.

The mode must name the Chapter 1 journey, the Chapter 2 **SLI (Service Level Indicator)**, and how remaining budget accounts the events. Teaching mode: `payment-overload-degraded` on `accept-and-complete-order` / `order_success_ratio`, user-visible `checkout-refuses-new-orders`, accounting `journey-burn`. Accepted-but-unpaid work is a bad event. It is not a good accept. The mode file must not emit `remaining_budget` or `accounting: success`. Those would let a degraded path approve itself, the same self-approval Chapter 3 refused.

**Best Practice:** Name the degraded mode, the user-visible behavior, and the journey-burn accounting before shedding a single request.

**Production Practice:** Payment overload degrades Storefront. It does not page Fulfillment as the cause, and it does not count in-flight accepts as success.

### Shedding consumes the Chapter 8 retry budget; it is not quota and not scaling

Chapter 8 already named payment `retry_budget: 1` and `fail-closed`. Shedding must consume that number. `retry_limit` on `order-worker` equals `1`. A larger limit is retry amplification. `unbounded` is not a limit.

When the budget is exhausted, Storefront refuses new accepts. That is backpressure at the edge so the worker pile cannot grow. It is not Platform tenant quota. Quota decides how much environment a tenant may consume. It is not DevOps unit-cost scaling. Adding workers so everyone can retry harder is cost policy, not cascade control. The shed record must name those two distinctions so later chapters cannot replace the rule with a quota ticket or a scale-out.

Warehouse keeps its own Chapter 8 contract. Copying the Storefront payment shed onto dispatch is the same class of copy Chapter 3 forbade for SLO targets. This chapter’s teaching storm is payment. Do not invent a second identical shed to look complete.

### Cascade deny: payment slowness is not a Fulfillment page

A retry storm that also calls warehouse, or that saturates shared capacity, can burn `dispatch-fulfillment` as a side effect. That side effect is still not “Fulfillment caused payment slowness.” Chapter 5 pages Fulfillment for `dispatch_success_ratio` burn. It must not gain a new page that says payment slowness is a dispatch incident.

The cascade contract denies three moves:

- amplifying retries past the Chapter 8 payment budget;
- paging `fulfillment-oncall` as the cause of payment overload;
- treating dispatch burn from that storm as a reason to keep accepting Storefront orders.

Email stays out of this storm. Chapter 8 already skip-and-records it. Shedding payment does not promote `notification-service` onto the critical path.

The lab does not inject live overload. Retry limits and denials are local fixtures, like Chapter 3’s event counts.

## 3. Publish modes, shedding, and cascade denials

The completed Chapter 9 model uses three files:

```text
degradation/modes.yaml
degradation/shedding.yaml
degradation/cascade.yaml
```

The separation is deliberate. Modes name user-visible degraded states and burn accounting. Shedding binds `order-worker` to the Chapter 8 retry budget and refuses new accepts. Cascade denials keep Fulfillment from being paged as the payment cause. None of the files may store remaining budget or stamp degraded work as success.

> **Practice — Name the degraded mode and account it as Storefront burn**
>
> Refuse silent drop. Do not emit remaining budget. Do not count accepted-but-unpaid as success.

Open `degradation/modes.yaml`. The teaching mode is `payment-overload-degraded`. Journey is `accept-and-complete-order`. **SLI** is `order_success_ratio`. Trigger is `payment-retry-budget-exhausted`. User-visible behavior is `checkout-refuses-new-orders`. Accounting is `journey-burn`. Worker is `order-worker`. Owner is `reliability-program`. If `accounting: success` or `remaining_budget` appears, the checkpoint fails.

> **Practice — Bound order-worker retries to the Chapter 8 payment budget and shed new accepts**
>
> Do not replace the shed with tenant quota or unit-cost scaling.

Open `degradation/shedding.yaml`. The rule `shed-storefront-payment-overload` consumes provider `payment`, worker `order-worker`, journey `accept-and-complete-order`, action `refuse-new-accepts`, and `retry_limit: 1`. That limit must equal the Chapter 8 payment `retry_budget`. `distinct_from` lists `platform-tenant-quota` and `devops-unit-cost-scaling`. If `retry_limit` is `unbounded` or the action is `accept-anyway`, the checkpoint fails.

Inspect each shed with three questions:

1. Does the retry limit match the Chapter 8 contract, or did “try harder” rewrite it?
2. What does the user see when the shed fires—and is that counted as burn?
3. Would Fulfillment still be paged as the cause if this payment row were deleted?

> **Practice — Deny paging Fulfillment as the payment cause**
>
> Dispatch pages remain for dispatch burn. They must not become the payment incident.

Open `degradation/cascade.yaml`. Denial `deny-payment-retry-into-fulfillment` names source provider `payment`, source journey `accept-and-complete-order`, `must_not_page: fulfillment-oncall`, and `must_not_burn: dispatch-fulfillment` as a reason to keep accepting. If `page_cause: fulfillment-oncall` appears, the storm has been blamed on the wrong rotation.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-09-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 09 checkpoint: shed, named burn accounting, and cascade denial verified
```

The audit validates the three Chapter 9 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- a named degraded mode exists for payment overload on `accept-and-complete-order`;
- user-visible behavior is not silent drop;
- accounting is `journey-burn`, not success, and remaining budget is not emitted;
- `order-worker` retry limit equals Chapter 8 payment `retry_budget`;
- new accepts are refused when that budget is exhausted;
- the shed is distinct from Platform tenant quota and DevOps unit-cost scaling;
- Fulfillment is not paged as the cause of payment slowness; and
- unbounded retries and `accept-anyway` fail.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not inject live overload. It does not prove that one retry or refuse-new-accepts is the right commercial shed. Those are judgment claims. The review triggers exist so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 9 evidence |
|---|---|
| Mechanism evidence | Schemas and the degradation evaluator operated successfully. |
| Decision evidence | Named mode, shed action, retry limit, and cascade denials are explicit. |
| Outcome evidence | Degraded accepts are accounted as Storefront journey-burn, not as success. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 9 creates decision evidence about how Northwind fails small. Pretending that the local checkpoint proved a production retry storm would weaken every later incident and game day.

## 4. Test the design under failure

### Cumulative reliability failure — Unbounded payment retries cascade into Fulfillment

> **Practice — Shed, name the mode, stop amplification, account Storefront burn**
>
> Drop `unbounded`. Stop paging Fulfillment as the cause. Stop counting accepts as success.

The baseline fixture contains this model:

```yaml
worker: order-worker
retry_limit: unbounded
action: accept-anyway
accounting: success
page_cause: fulfillment-oncall
```

The problem is not merely a missing timeout. Chapter 8 already named `2s` and retry budget `1`. The worker ignores that budget, Storefront keeps accepting, the accept graph stays green, and Fulfillment is paged for a payment slowness it did not cause. Both remaining budgets can exhaust while leadership sees “orders accepted.” That is the book’s cumulative reliability failure: availability theater plus informal heroics, now as a retry loop.

**Severity:** high; one slow payment becomes two journey outages and a mis-paged rotation.  
**Plausible harm:** checkout appears to work; payment never finishes; dispatch fails under shared load; Fulfillment on-call debugs the wrong cause.  
**Potential blast radius:** every worker taught to retry harder; every green accept counter treated as an SLO.  
**Bounded by:** later portfolio incident command. None repairs a shed that is “accept anyway.”  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** `accept-and-complete-order` is at risk on Storefront. `dispatch-fulfillment` may be harmed as a cascade, not as the cause.
- **Error budget:** Degraded accepts consume Storefront remaining budget. Hiding them as success forges outcome evidence. Not yet a new freeze rule.
- **Human system:** Applicable as load on Chapter 6 rotations. Paging Fulfillment for payment slowness is informal heroics under a provider name.
- **Portfolio recovery:** Not yet produced. A green accept graph cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling retries unbounded encourages three controls: keep accepting so the storefront looks live, count those accepts as good so the **SLI** stays green, and page whoever is downstream when shared capacity fails. Those moves may be sincere. They do not answer which journey the customer lost, which remaining budget burns, or which rotation Chapter 6 designed for payment.

Silent drop makes mechanism evidence (accept count) look like outcome evidence. `page_cause: fulfillment-oncall` makes Chapter 5’s dispatch pages ornamental as a blame label. `accept-anyway` makes Chapter 8’s fail-closed payment contract ornamental.

#### Correction

The completed model does not leave retries unbounded. It names `payment-overload-degraded`, shows checkout refusing new orders, accounts those events as Storefront journey-burn, sets `order-worker` retry limit to the Chapter 8 payment budget, refuses new accepts, and denies paging Fulfillment as the payment cause.

That correction changes later decisions:

- Chapter 10 must command a spanning incident without closing because accepts looked green, and without treating Fulfillment as the payment owner.
- Chapter 13 must exercise dependency loss with this shed in place, not with an unbounded retry drill that stands in for cascade control.
- Chapter 14 must not treat restored accept volume as **Evidence of portfolio recovery** if payment still cannot complete.

The design is practical because it changes the production contract across the rest of the book. Adding an arbitrary load-generator command would not make it more practical.

## 5. Production reality

### Common cascade errors

#### Retrying past the named budget

Chapter 8’s `retry_budget: 1` is the limit. A larger number is amplification.

#### Accepting work the worker cannot finish

A green accept counter is not a completed order.

#### Counting degraded success as a good event

Accounting is `journey-burn`. A stored success flag is a slide.

#### Paging Fulfillment for Storefront payment slowness

Cause and cascade are different. Chapter 5 already split those pages.

#### Replacing the shed with tenant quota or scale-out

Quota and unit cost are inherited jobs. They do not refuse a retry storm.

#### Silent drop without a named mode

If the user cannot see the degradation, remaining budget cannot either.

#### Copying the payment shed onto warehouse to look complete

Dispatch has its own contract. This chapter’s teaching failure is payment amplification.

## 6. What changed

| Before | After |
|---|---|
| `order-worker` retries were unbounded. | **Retry limit equals Chapter 8 payment `retry_budget: 1`.** |
| Storefront accepted work it could not finish. | **New accepts are refused when the budget is exhausted.** |
| Accepted-but-unpaid counted as success. | **The degraded mode accounts those events as Storefront journey-burn.** |
| Fulfillment was paged as the payment cause. | **Cascade denial forbids `fulfillment-oncall` as the payment page.** |
| Quota or scale-out stood in for a shed. | **The shed is distinct from tenant quota and unit-cost scaling.** |
| A valid schema could appear to prove cascade control. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a reviewable degradation contract that later incidents and game days can consume without retrying payment into a portfolio outage or hiding harm behind a green accept graph.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Degradation-and-shedding policy | `degradation/modes.yaml` and `degradation/shedding.yaml` | They retain the named mode, user-visible behavior, burn accounting, and retry limit later incidents must not replace with “try harder.” |
| Cascade-failure contract | `degradation/cascade.yaml` | It retains the denial that payment slowness is not a Fulfillment page and not a reason to keep accepting. |

These artifacts should change when Northwind's workers, payment retry budget, or user-visible degraded behavior materially change—not whenever a dashboard adds an accept counter.

## What You Learned

Northwind sheds and degrades before a local payment slowness becomes every journey’s outage. `order-worker` retries are bounded by the Chapter 8 contract. New accepts are refused. Degraded work is user-visible and accounted as Storefront burn, not as success. Fulfillment is not paged as the payment cause. Tenant quota and unit-cost scaling are not the shed. Schema checks can prove structural completeness within declared scope. They cannot inject live overload. A design earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Degrade catalog-browse without copying the payment shed**
>
> A storefront engineer wants catalog search to retry unbounded “because browse already has tickets, and if search is slow we should try harder until Fulfillment is fine.”

Extend the Chapter 9 model without adding incident command yet:

1. Decide whether catalog-browse may retry unbounded, given Chapters 1–3 and the Chapter 8 search-contract practice.
2. Name a user-visible degraded behavior that is not a renamed `checkout-refuses-new-orders`.
3. Account any degraded browse events without emitting `remaining_budget` or `accounting: success`.
4. Do not page `fulfillment-oncall` as the cause of a Storefront search slowness.
5. Identify one observation that would falsify the shed—for example accepts still counted as success while retries are unbounded.
6. Explain which material change would trigger review of the mode, not just the worker replica count.

Do not copy the payment refuse-new-accepts row and rename it. Catalog reads have different criticality, workers, and freeze consequences from checkout. Your durable output is the mode and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 9 capability when you can explain why unbounded retries are not a contract, shed new accepts against the Chapter 8 payment budget, name a user-visible mode accounted as journey-burn, refuse to page Fulfillment as the payment cause, distinguish quota and scaling from shedding, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Cascade is bounded in the model. A multi-service incident is still commanded as one failed change on one path. Inherited DevOps Chapter 12 can coordinate one production change. A payment slowness that also harmed dispatch still gets one informal commander in Slack.

Chapter 10 defines portfolio incident command so Storefront green cannot close Fulfillment, and so the right rotations and Chapter 4 freeze join the trace.
