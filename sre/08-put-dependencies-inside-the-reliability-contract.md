# Put Dependencies Inside the Reliability Contract

Chapter 7 classified toil, computed a fraction, and denied a new critical **SLO (Service Level Objective)** for `notification-service`. Engineering time is gated. Payment, warehouse, and email can still fail while Northwind’s own graphs stay green, or every provider page is treated as a Storefront page.

The production question is now:

> Which dependencies are inside a journey's SLO, which are degraded or non-critical, and what evidence does each provider owe?

Without that contract, absorbing a provider’s unbounded failure makes the SLO dishonest. Ignoring a critical provider makes the SLO theater. Chapter 3 already recorded notification as non-critical. Chapter 5 already pages `order_success_ratio` at `storefront-oncall` and `dispatch_success_ratio` at `fulfillment-oncall`. Chapter 8 must not reopen email as a critical Storefront page, and it must not let a payment timeout stamp “no user impact.”

This chapter publishes dependency contracts that join Chapter 3 journeys to providers. Payment failure burns `accept-and-complete-order`. Warehouse failure burns `dispatch-fulfillment`. Email failure is recorded, not paged as a critical SLO. A dependency row cannot emit its own “no user impact.” Timeout and retry budget are named here. How Northwind sheds load when those bounds are crossed is Chapter 9.

## 1. An unsafe dependency map

A weak record says:

```yaml
- id: payment
  no_user_impact: true
- id: notification-service
  criticality: critical
  destination: storefront-oncall
```

It treats a payment timeout as someone else’s graph. It pages confirmation email as if it were the order journey. Warehouse may be missing, or copied onto Storefront so Fulfillment never burns. “The provider status page is green” may describe a vendor dashboard. It cannot complete a Northwind contract.

Work from the lab working tree using the Chapter 0 procedure. From the SRE lab root, run the Chapter 8 baseline:

```bash
make chapter-08-baseline
```

The command succeeds when it detects the intended unsafe mapping:

```text
chapter 08 baseline: payment no-impact while email pages storefront correctly detected
```

The fixture stamps `no_user_impact` on payment, pages `notification-service` at `storefront-oncall` as critical, and attributes warehouse to Storefront. Payment timeouts can exhaust the order **SLI (Service Level Indicator)** while the dependency file claims nobody was harmed. Email pages the Storefront rotation for a journey Chapter 3 refused. The wrong budget and the wrong humans absorb the failure.

That inversion drives the chapter.

## 2. The production model: criticality, attribution, and named bounds

> *Theory — Dependency contract*
>
> This model enables Northwind to put payment, warehouse, and email inside journey SLOs, rather than treating every provider page as Storefront or claiming a timeout has no user impact.

### A provider SLO is not a Northwind SLO

Payment may advertise 99.95 percent availability. That number is the provider’s product. It is not `accept-and-complete-order`. If a payment timeout prevents a valid order from reaching a correct terminal state, Storefront remaining budget burns. A green vendor status page is mechanism evidence. It is not remaining error budget.

Warehouse is the same join on the other journey. A warehouse outage that blocks dispatch is `dispatch-fulfillment` burn, not a Storefront tile and not a copied Storefront target.

Email is not a third critical journey. Chapter 3 already recorded `notification-service` as non-critical. Chapter 7 already denied promoting it because on-call watched the inbox. A confirmation that never sends can annoy a customer. That is not permission to page Storefront as if the order had failed, and it is not permission to write `no_user_impact: true`.

**Best Practice:** Name each provider, the journey it can burn or must not burn, a timeout, a retry budget, and a fallback.

**Production Practice:** Payment is fail-closed on `accept-and-complete-order`. Warehouse is fail-closed on `dispatch-fulfillment`. Email is skip-and-record. None of those rows may emit user impact or its absence.

### Critical versus non-critical is attribution, not a feeling

| Provider | Consumer | Journey | Failure effect |
|---|---|---|---|
| `payment` | Storefront | `accept-and-complete-order` | journey-burn on `order_success_ratio` |
| `warehouse` | Fulfillment | `dispatch-fulfillment` | journey-burn on `dispatch_success_ratio` |
| `notification-service` | Storefront | none; Chapter 3 non-critical | record; do not page as a critical SLO |

Copying Storefront’s payment row onto warehouse does not protect dispatch. Copying warehouse onto Storefront exhausts the order budget for a warehouse the Storefront rotation does not own. Treating every provider as equally critical pages email with payment.

Chapter 5 already pages those two journey **SLIs**. This chapter does not add a third critical page for email. It says which provider failures *are* those burns.

### Timeout and retry budget are named; cascade is not yet the chapter

A contract without a timeout absorbs the provider until the worker pile grows. Teaching values: payment `2s` with retry budget `1`, warehouse `5s` with retry budget `1`, email `10s` with retry budget `0`. Those numbers are local fixtures, not industry constants.

Retry budget `1` is not permission to retry until Fulfillment is pulled into Storefront’s storm. Chapter 9 owns shedding and cascade denial. Chapter 8 must already name the bound, or Chapter 9 inherits “try harder” as the contract.

Fallback `fail-closed` means the journey is not counted good when the provider fails. Fallback `skip-and-record` means the supporting step is skipped and the protected journey is not automatically burned. Skip is not “no user impact.” It is an explicit, reviewable choice that confirmation email is outside the protected outcome.

### A row cannot approve its own harmlessness

`no_user_impact: true` is the same self-approval Chapter 3 refused when remaining budget was emitted, Chapter 5 refused when a page stamped `user_impact`, and Chapter 7 refused when the bound emitted `toil_fraction`. Outcome evidence is computed from the journey, not stored on the provider row.

The lab does not query a real provider status page. Attribution is a local contract.

## 3. Publish the catalog, criticality, and contracts

The completed Chapter 8 model uses three files:

```text
dependencies/catalog.yaml
dependencies/criticality.yaml
dependencies/contracts.yaml
```

The separation is deliberate. The catalog names providers, consumers, and forbidden claims. Criticality joins each provider to a journey, **SLI**, and failure effect. Contracts name timeout, retry budget, fallback, and the evidence token that says whether failure is Northwind burn. None of the files may carry `user_impact` or `no_user_impact`.

> **Practice — Forbid “no user impact” as a self-claim**
>
> Keep `no-user-impact` on the forbidden-claim list. Do not store harmlessness on the provider.

Open `dependencies/catalog.yaml`. Providers are `payment` (Storefront), `warehouse` (Fulfillment), and `notification-service` (Storefront, supporting). Forbidden claims include `no-user-impact`. If that string is missing, later chapters inherit a slogan. Owner is `reliability-program`.

> **Practice — Attribute payment to Storefront burn and warehouse to Fulfillment burn**
>
> Do not copy the Storefront payment row onto warehouse. Do not put warehouse on `accept-and-complete-order`.

Open `dependencies/criticality.yaml`. Payment is `critical`, journey `accept-and-complete-order`, **SLI** `order_success_ratio`, failure effect `journey-burn`. Warehouse is `critical`, journey `dispatch-fulfillment`, **SLI** `dispatch_success_ratio`, failure effect `journey-burn`. Notification is `non-critical`, failure effect `record`, remaining owner `storefront-team` from Chapter 3. If `destination: storefront-oncall` appears on email as a critical page, the checkpoint fails.

Inspect each assignment with three questions:

1. If this provider times out, which Chapter 1 journey fails—or which Chapter 3 non-critical row already refused that promotion?
2. Would this still be true if the provider’s own status page stayed green?
3. Is the consumer the team that owns that journey, or whoever got the first ticket?

> **Practice — Name timeout, retry budget, and fallback without pretending cascade is solved**
>
> Payment and warehouse fail-closed. Email skip-and-record. Do not emit remaining budget or user impact.

Open `dependencies/contracts.yaml`. Payment timeout `2s`, retry budget `1`, fallback `fail-closed`, evidence `payment-timeout-is-storefront-burn`. Warehouse timeout `5s`, retry budget `1`, fallback `fail-closed`, evidence `warehouse-timeout-is-fulfillment-burn`. Email timeout `10s`, retry budget `0`, fallback `skip-and-record`, evidence `email-failure-is-not-order-burn`. If payment fallback is `skip-and-record`, orders can look successful without payment. If email fallback is `fail-closed`, confirmation has been promoted onto the critical path.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-08-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 08 checkpoint: attributed burns and non-critical email verified
```

The audit validates the three Chapter 8 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- `payment`, `warehouse`, and `notification-service` are cataloged;
- payment is critical journey-burn on `accept-and-complete-order` / `order_success_ratio`;
- warehouse is critical journey-burn on `dispatch-fulfillment` / `dispatch_success_ratio`;
- email is non-critical, recorded, and not paged as a Storefront critical SLO;
- the Chapter 3 non-critical row is consumed, not reversed;
- payment fallback is fail-closed and email fallback is skip-and-record;
- timeout and retry budget are present and numeric;
- `no-user-impact` is forbidden; and
- no row emits `user_impact` or `no_user_impact`.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not query a real provider status page. It does not prove that 2 seconds or one retry is the right commercial bound. Those are judgment claims. The review triggers exist so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 8 evidence |
|---|---|
| Mechanism evidence | Schemas and the dependency evaluator operated successfully. |
| Decision evidence | Catalog, criticality, timeout, fallback, and forbidden claims are explicit. |
| Outcome evidence | Payment and warehouse burns are attributed to journeys; harmlessness is not stored on the row. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 8 creates decision evidence about which provider failures are whose burn. Pretending that the local checkpoint proved a vendor outage would weaken every later degradation, incident, and game day.

## 4. Test the design under failure

### Connected consequence — Payment timeouts burn Storefront while email is paged as equally critical

> **Practice — Reclassify email; attribute payment to Storefront; keep warehouse on Fulfillment**
>
> Drop `no_user_impact`. Stop paging confirmation as the order journey.

The baseline fixture contains this model:

```yaml
payment:
  no_user_impact: true
  failure_effect: none
notification-service:
  criticality: critical
  destination: storefront-oncall
warehouse:
  journey: accept-and-complete-order
```

The problem is not merely a missing timeout. Payment can take the order **SLI** while the contract claims nobody was harmed. Email exhausts Storefront pages and Chapter 4 freeze attention for a system Chapter 3 called non-critical. Warehouse copied onto Storefront leaves dispatch without a provider contract and spends the wrong remaining budget.

**Severity:** high; exhausted Storefront budget and a Storefront rotation now absorb email, while payment harm is denied in the file that should have attributed it.  
**Plausible harm:** orders fail at payment while graphs stay green; confirmation pages wake the order primary; Fulfillment dispatch has no warehouse burn.  
**Potential blast radius:** every vendor treated as equal to payment; every supporting tool promoted because it already has a ticket queue.  
**Bounded by:** later degradation (retry amplification) and incident command. None repairs a contract that denies payment harm and pages email.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** Payment is inside `accept-and-complete-order`. Warehouse is inside `dispatch-fulfillment`. `notification-service` is not a protected journey.
- **Error budget:** Payment timeouts consume Storefront remaining budget. Email pages would spend freeze attention on the wrong SLO. Not yet a new freeze rule.
- **Human system:** Applicable as load on Chapter 6 rotations. Email as a critical Storefront page reopens Slack-as-heroics under a provider name.
- **Portfolio recovery:** Not yet produced. A green payment status page cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling payment harmless encourages two controls: keep Storefront graphs green by excluding the timeout, and page whatever already has an inbox so someone is “covering dependencies.” Those moves may be sincere. They do not answer which journey the customer lost, which remaining budget burns, or which rotation Chapter 6 designed for that page.

The `no_user_impact` stamp makes outcome evidence a constant. The email page makes Chapter 3’s non-critical row and Chapter 7’s deny ornamental. Warehouse on Storefront copies the wrong consumer, the same class of copy Chapter 3 forbade for SLO targets.

#### Correction

The completed model does not let payment approve its own harmlessness. It attributes payment timeout as Storefront journey-burn, warehouse timeout as Fulfillment journey-burn, and email as non-critical record with skip-and-record. It forbids `no-user-impact` as a claim. It names timeouts and retry budgets without pretending cascade is solved.

That correction changes later decisions:

- Chapter 9 must shed and bound retries against these contracts, not invent a new payment path that is “always success.”
- Chapter 10 must not close a portfolio incident because email was paged and Storefront graphs were green.
- Chapter 13 must exercise dependency loss as payment or warehouse, not as a mixed email drill that stands in for both journeys.
- Chapter 14 must not treat a restored notification template as **Evidence of portfolio recovery**.

The design is practical because it changes the production contract across the rest of the book. Adding an arbitrary vendor API call would not make it more practical.

## 5. Production reality

### Common dependency errors

#### Storing “no user impact” on the provider row

Harmlessness is not a field the dependency gets to emit. Attribution is.

#### Paging every provider as Storefront

Email is not payment. A contact that already exists is not a criticality decision.

#### Copying Storefront’s payment contract onto warehouse

Fulfillment has a different journey, **SLI**, window, and rotation. Copying the consumer copies the lie.

#### Treating a provider status page as remaining budget

Mechanism evidence is not outcome evidence.

#### Skipping timeout so the worker can “wait it out”

An unnamed bound is not a bound. Chapter 9 cannot deny a cascade that Chapter 8 never limited.

#### Fail-closing email, or skip-recording payment

Fallback is criticality in operational form. Mixing them reverses Chapters 3 and 1.

## 6. What changed

| Before | After |
|---|---|
| Payment stamped `no_user_impact`. | **Payment timeout is Storefront journey-burn on `order_success_ratio`.** |
| Email paged `storefront-oncall` as critical. | **Email is non-critical, recorded, skip-and-record.** |
| Warehouse sat on the order journey. | **Warehouse burns `dispatch-fulfillment` on Fulfillment.** |
| Provider status was treated as the SLO. | **Provider availability is not the Northwind journey SLO.** |
| Timeout and retry were “try harder.” | **Timeouts and retry budgets are named; cascade remains Chapter 9.** |
| A valid schema could appear to prove harmlessness. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a reviewable provider contract that later degradation, incidents, and game days can consume without paging email as the order path or hiding payment timeouts behind a slogan.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Dependency reliability catalog | `dependencies/catalog.yaml` | It retains providers, consumers, and the forbidden harmlessness claim later chapters must not restore. |
| Criticality-and-fallback contract | `dependencies/criticality.yaml` and `dependencies/contracts.yaml` | They retain which provider burns which journey, with timeout, retry budget, and fallback. |

These artifacts should change when Northwind's providers, protected journeys, or fallback policy materially change—not whenever a vendor renames a status page.

## What You Learned

Dependencies sit inside journey SLOs or they are explicitly non-critical. Payment burns Storefront. Warehouse burns Fulfillment. Email stays non-critical. A provider’s advertised availability is not Northwind’s SLO. A row cannot emit “no user impact.” Timeout and retry budget are named here; cascade control is the next chapter. Schema checks can prove structural completeness within declared scope. They cannot query a real provider. A design earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Contract catalog-browse search without copying the payment row**
>
> A storefront engineer wants the catalog search index marked critical “because browse already has tickets, and users see search more than they pay.”

Extend the Chapter 8 model without adding shedding policy yet:

1. Decide whether catalog-search is critical journey-burn, non-critical record, or out of scope, given Chapters 1–3 treatments of catalog reads.
2. Name a consumer, timeout, retry budget, and fallback that are not a renamed payment `fail-closed`.
3. Join or refuse a Chapter 1 journey; do not invent `accept-and-complete-order` coverage for search.
4. Do not emit `no_user_impact`, even if you skip search.
5. Identify one observation that would falsify the criticality—for example payment timeouts remaining “no impact” while search pages Storefront.
6. Explain which material change would trigger review of the contract, not just the vendor’s status tile.

Do not copy the warehouse row and rename it. Catalog reads have different criticality, consumers, and freeze consequences from dispatch. Your durable output is the attribution and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 8 capability when you can explain why a provider status page is not a Northwind SLO, attribute payment to Storefront and warehouse to Fulfillment, keep email non-critical, refuse `no_user_impact`, name timeout and retry budget without claiming cascade is solved, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Dependencies are named and attributed. Northwind’s own services can still retry until the portfolio cascades. `order-worker` can retry payment without a shed. Storefront can accept work the worker cannot finish. Fulfillment can be pulled into Storefront’s retry storm.

Chapter 9 defines degradation and shedding so a payment slowness does not become every journey’s outage, and so degraded success is accounted as burn rather than hidden as a green graph.
