# Set SLOs and Error Budgets Across the Portfolio

Chapter 2 accepted the measurements users can feel. Storefront has `order_success_ratio` and `order_latency`. Fulfillment has `dispatch_success_ratio`. Job-time stays adjacent. Component uptime is rejected.

Those decisions do not answer the next production question:

> What **SLO (Service Level Objective)** target, window, and error budget does each protected journey get, and how is the portfolio cataloged?

Without that catalog, Northwind still has a dashboard of nines. Storefront carries a provisional single-service objective from DevOps Chapter 6. Fulfillment has none. Leadership pastes 99.9 percent onto both services. Legal quotes a customer **SLA (Service Level Agreement)** as if it could freeze a release. `notification-service` looks like a third critical journey because email is visible. A number that was never computed cannot later stop change.

This chapter publishes windows, targets, and remaining unreliability for the Chapter 1 journeys. Chapter 4 will freeze change against those remaining budgets. It must not inherit a copied Storefront tile, an SLA sentence, or a catalog that emitted its own remaining budget.

## 1. An unsafe SLO catalog

A weak record says:

```yaml
id: portfolio-nines
journey: accept-and-complete-order
sli: order_success_ratio
window: rolling-30d
target: 0.999
remaining_budget: 1.0
sla: "99.9 percent availability per customer contract"
```

It does not give `dispatch-fulfillment` a window. It treats an SLA sentence as a target. It emits remaining budget instead of computing it from observations. 99.9 percent on Storefront is not a portfolio.

Work from the lab working tree using the Chapter 0 procedure. From the SRE lab root, run the Chapter 3 baseline:

```bash
make chapter-03-baseline
```

The command succeeds when it detects the intended unsafe catalog:

```text
chapter 03 baseline: portfolio 99.9 from storefront alone correctly detected
```

The fixture publishes 99.9 percent on the Storefront order path, stores remaining budget as a constant, quotes the customer SLA, and never gives dispatch a window or a computed budget. One service's nines have been treated as the portfolio. A legal sentence has been treated as an SLO. Remaining unreliability has been declared rather than observed.

That inversion drives the chapter.

## 2. The production model: targets, windows, and remaining unreliability

> *Theory — Portfolio SLO catalog*
>
> This model enables Northwind to publish a reviewable internal contract per journey rather than a copied nine, a customer SLA, or a dashboard that approves itself.

### An SLO is an internal contract, not an SLA and not an SLI

An **SLI (Service Level Indicator)** is the measurement Chapter 2 accepted. An SLO is the target that measurement must meet in a named window. An SLA is a customer or legal promise. Error budget is the remaining unreliability the SLO permits. Those four words are not synonyms.

DevOps Chapter 6 already recorded a provisional 99.5 percent order-success objective over 30 days for Storefront. That is an input. It is not a portfolio catalog. It does not cover dispatch. It cannot freeze Fulfillment. It is not an SLA.

If the catalog's `target` field is a sentence, later chapters inherit a brochure. If the catalog copies Storefront's target and window onto Fulfillment, later freeze policy will stop the wrong service for the wrong reason.

### A window is a compliance period, not a graph zoom

A rolling 30-day window and a rolling 28-day window are different contracts. Copying `rolling-30d` onto dispatch because Storefront already had it is the same failure as copying 99.9 percent. The window must be named, owned, and referenced by identifier. “Last month on the dashboard” is not a window.

Northwind's Storefront success SLO keeps the inherited 30-day period and the provisional 99.5 percent target, now as a portfolio record rather than a single-service comment. Fulfillment gets its own 28-day window and a 99.0 percent target. Those numbers are teaching values. They are not industry constants. They exist so later chapters can compute remaining budget without a copied signature.

### Error budget is remaining unreliability, computed from observations

If the target is 99.5 percent, the error budget is 0.5 percent of valid events in the window. Remaining budget is:

```text
remaining = 1 - (observed bad events / allowed bad events)
```

Allowed bad events are `valid events × (1 − target)`. Observed bad events are `valid events − good events`. The catalog must not emit `remaining_budget`. The budget register must not store a constant remaining. Both would let a dashboard approve itself.

This book's **error budget** is SRE portfolio governance. It is not Platform job-time. `time-to-first-environment` still has no row in this catalog.

### Critical and supporting are not the same catalog row

`accept-and-complete-order` and `dispatch-fulfillment` are critical journeys. They receive SLOs. `notification-service` sends non-critical confirmations. Email can fail while an order still reaches a correct terminal state. Recording notification as a critical SLO would freeze Storefront releases for a confirmation template. Chapter 8 will put email in the dependency contract as non-critical. Chapter 3 must already refuse it as a protected journey SLO.

**Best Practice:** Give every Chapter 1 journey a window, a numeric target, an accepted SLI, and a budget whose remaining value is computed.

**Production Practice:** A copied target is only real when the evaluator can see the same target and window on Fulfillment as on Storefront. An SLA is only refused when a legal sentence cannot occupy the target field.

### A catalog that emits remaining budget is not outcome evidence

Schema validity can prove that a row has a number. Outcome evidence for this chapter is remaining unreliability computed from named observations. Pretending the catalog's `remaining_budget: 1.0` proves journeys are healthy would make Chapter 4 freeze against fiction.

## 3. Publish the portfolio catalog

The completed Chapter 3 model uses three files, plus named observations the evaluator consumes:

```text
slos/catalog.yaml
slos/windows.yaml
slos/budgets.yaml
fixtures/observations/chapter-03.yaml
```

The separation is deliberate. The catalog names journeys, accepted SLIs, windows, numeric targets, and criticality. Windows name duration. The budget register joins each SLO to an observation. Remaining budget is computed at evaluation time. Observations are not a self-approving dashboard.

> **Practice — Publish a catalog that cannot treat an SLA as a target**
>
> Give each Chapter 1 journey a numeric target and record the customer SLA as out of scope.

Open `slos/catalog.yaml`. The required critical rows are:

```yaml
- id: slo-accept-and-complete-order
  journey: accept-and-complete-order
  sli: order_success_ratio
  window: rolling-30d
  target: 0.995
  criticality: critical
  owner: reliability-program
  review_trigger: order-path-changes-good-event-definition
- id: slo-dispatch-fulfillment
  journey: dispatch-fulfillment
  sli: dispatch_success_ratio
  window: rolling-28d
  target: 0.99
  criticality: critical
  owner: reliability-program
  review_trigger: warehouse-contract-changes-good-event-definition
```

Inspect each row with three questions:

1. Is the SLI an accepted user-journey indicator from Chapter 2, or a job-time proof the method kept adjacent?
2. Would the target still be a number if the customer contract were rewritten?
3. Is Fulfillment's `(target, window)` different from Storefront's, or was 99.9 percent pasted twice?

`order_latency` receives its own Storefront SLO on the same journey, with a 99.0 percent good-event target in the 30-day window. Chapter 2 allowed that second contract. It is not a copy of dispatch. `notification-service` is listed under `non_critical`, not under `slos`. The customer availability SLA is recorded as `out-of-scope`. It is not a target.

> **Practice — Name windows so Fulfillment cannot inherit Storefront's period by copy**
>
> Keep Storefront on the inherited 30-day window and give dispatch a distinct compliance period.

Open `slos/windows.yaml`. `rolling-30d` is 30 days. `rolling-28d` is 28 days. If dispatch pointed at `rolling-30d` and also used 0.995, the evaluator would treat that as a copied Storefront SLO even though the SLI name differed.

> **Practice — Compute remaining budget from observations**
>
> Join each critical SLO to good and valid event counts. Do not store remaining as a constant.

Open `slos/budgets.yaml` and `fixtures/observations/chapter-03.yaml`. Each budget names an SLO and an observation. The observation names `good_events` and `valid_events`. The evaluator computes remaining unreliability. If `remaining_budget` appears on the catalog or the register, the checkpoint fails.

Storefront's teaching observation is 19,940 good events in 20,000 valid events against a 99.5 percent target: 60 bad events of 100 allowed, remaining 0.4. Fulfillment's teaching observation is 9,930 good events in 10,000 valid events against a 99.0 percent target: 70 bad events of 100 allowed, remaining 0.3. Those fixtures are local. They do not prove a production telemetry backend.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-03-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 03 checkpoint: portfolio SLOs, windows, and computed remaining budgets verified
```

The audit validates the three Chapter 3 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- every Chapter 1 journey has a critical SLO;
- each SLO uses an accepted user-journey SLI, a named window, and a numeric target in (0, 1);
- Fulfillment's target and window are not a copy of Storefront's order-success SLO;
- job-time proofs and theater indicators are not cataloged as SLOs;
- `notification-service` is not a critical SLO;
- SLA text is not a target;
- remaining budget is computed from observations, not emitted by the catalog or the register; and
- every critical SLO has a budget row.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not prove that 99.5 percent or 99.0 percent is the right commercial target. It does not prove that 20,000 events represent live traffic. Those are judgment claims. The review triggers exist so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 3 evidence |
|---|---|
| Mechanism evidence | Schemas and the SLO evaluator operated successfully. |
| Decision evidence | Windows, numeric targets, criticality, and the SLA-out-of-scope record are explicit. |
| Outcome evidence | Remaining error budget is computed from named observations for each critical journey. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 3 creates decision evidence and the first computed outcome evidence. Pretending that the local checkpoint proves journeys already keep their SLOs in production would weaken every later freeze, page, and fail-over.

## 4. Test the design under failure

### Independent control failure — Portfolio 99.9 percent from Storefront alone

> **Practice — Add the Fulfillment SLO and recompute remaining budget**
>
> Remove the SLA sentence, stop emitting remaining budget, and give dispatch its own window and target.

The baseline fixture contains this model:

```yaml
- id: slo-accept-and-complete-order
  journey: accept-and-complete-order
  sli: order_success_ratio
  window: rolling-30d
  target: 0.999
  remaining_budget: 1.0
  sla: "99.9 percent availability per customer contract"
```

The problem is not merely a missing Fulfillment row. The model treats Storefront's nines as the portfolio, a legal sentence as a target, and a constant as remaining unreliability. Dispatch still has no window. Notification could be added next as another 99.9 percent tile.

**Severity:** high; every later freeze, page, and fail-over conversation will optimize a copied Storefront number instead of dispatch.  
**Plausible harm:** Storefront looks healthy at 99.9 percent while warehouse dispatch has no budget; an SLA dispute is mistaken for remaining unreliability; a dashboard reports remaining 1.0 while events are uncounted.  
**Potential blast radius:** every service asked to “take the portfolio SLO”; Fulfillment inherits Storefront's target by paste.  
**Bounded by:** later error-budget policy, burn alerts, and dependency contracts. None repairs a catalog that has only one journey and an SLA sentence.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** `accept-and-complete-order` has a row. `dispatch-fulfillment` does not. A portfolio 99.9 percent is not a journey.
- **Error budget:** Applicable as remaining unreliability, not yet as a freeze decision. Chapter-local implication: remaining cannot be 1.0 because the catalog said so; Fulfillment has no remaining value to freeze against.
- **Human system:** Not yet applicable as on-call design. Chapter-local implication: paging on a copied nine trains heroes to ignore dispatch.
- **Portfolio recovery:** Not yet produced. A green Storefront tile cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling the catalog “99.9 percent portfolio availability” encourages copy controls: paste Storefront's target onto Fulfillment, quote the customer contract, set remaining to 1.0 so the slide is green. Those moves may be sincere, but they do not answer which events are valid, how many are allowed to fail, or whether dispatch has a contract at all.

The missing Fulfillment window makes Chapter 4's freeze ornamental for warehouse change. The SLA field makes a legal product look like an internal target. The emitted remaining budget makes outcome evidence a constant. Mapping notification into the same 99.9 percent would freeze the order path for email.

#### Correction

The completed model does not publish a portfolio nine. It gives Storefront a 99.5 percent / 30-day success SLO and a separate latency SLO, gives Fulfillment a 99.0 percent / 28-day dispatch SLO, records `notification-service` as non-critical, records the customer SLA as out of scope, and computes remaining budget from observations.

That correction changes later decisions:

- Chapter 4 must freeze change against remaining journey budget, not against an SLA sentence or a copied 99.9 percent.
- Chapter 5 must page on burn of these windows, not on a single Storefront tile.
- Chapter 8 must put payment inside the Storefront success SLO and warehouse inside dispatch, not inside notification.
- Chapter 9 must account degraded success as burn against these remaining budgets.

The design is practical because it changes the production contract across the rest of the book. Adding an arbitrary command would not make it more practical.

## 5. Production reality

### Common catalog errors

#### Copying Storefront's target onto Fulfillment

Two services can share a percentage by coincidence. They cannot share a `(target, window)` signature because someone pasted the row. Dispatch is not order success.

#### Treating an SLA sentence as an SLO target

A customer contract can motivate a conversation. It cannot occupy the `target` field. Error budget cannot freeze a legal clause.

#### Emitting remaining budget from the catalog

A constant remaining of 1.0 is a slide. Remaining unreliability is `1 − (observed bad / allowed bad)` from named events.

#### Cataloging job-time as a portfolio SLO

Chapter 2 already kept `time-to-first-environment` adjacent. Chapter 3 must not reopen it as a target.

#### Making `notification-service` critical because email is visible

Visibility is the Chapter 2 failure again. Confirmation mail is not `accept-and-complete-order`.

#### Measuring catalog success as coverage of every graph

A thick catalog of CPU SLOs is not a thin portfolio. Later freeze policy will stop the wrong change.

## 6. What changed

| Before | After |
|---|---|
| The portfolio was Storefront's 99.9 percent. | **Each Chapter 1 journey has its own window, numeric target, and computed remaining budget.** |
| Fulfillment had no SLO. | **`dispatch-fulfillment` has a 99.0 percent target over 28 days, not a copied Storefront signature.** |
| An SLA sentence sat in the target field. | **The customer SLA is out of scope; targets are numbers in (0, 1).** |
| Remaining budget was a constant. | **Remaining unreliability is computed from good and valid events.** |
| Notification looked like a third critical journey. | **`notification-service` is recorded as non-critical.** |
| A valid schema could appear to prove a sound SLO. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a reviewable portfolio contract that later chapters can freeze, page, and recover without a copied nine or a legal sentence.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Portfolio SLO catalog | `slos/catalog.yaml` | It retains journey, accepted SLI, window, numeric target, and criticality later policy must not replace with an SLA or a copied nine. |
| Error-budget register | `slos/budgets.yaml` | It retains the join from SLO to observation so remaining unreliability stays computed. |

These artifacts should change when Northwind's journeys, good-event definitions, or commercial risk materially change—not whenever a dashboard theme is redesigned.

## What You Learned

A portfolio SLO catalog gives each protected journey a numeric target, a named window, and remaining unreliability computed from observations. An SLA is not that catalog. A copied Storefront nine is not a Fulfillment SLO. `notification-service` is not a critical journey. Schema checks can prove structural completeness within declared scope. They cannot prove that 99.5 percent is the right commercial target. A design earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Set a catalog-browse SLO without copying the dispatch row**
>
> A storefront engineer proposes a 99.0 percent / 28-day SLO for `catalog_read_success_ratio` “so it matches Fulfillment.”

Extend the Chapter 3 model without adding freeze policy yet:

1. Decide whether catalog reads are a critical journey SLO, a supporting SLO of `accept-and-complete-order`, or out of scope.
2. If you publish a target, choose a window that is not a paste of `rolling-28d` plus 0.99 unless you can defend that signature on its own facts.
3. State the good and valid event definition as it would exist in an observation file.
4. Compute remaining budget from one teaching observation; do not emit `remaining_budget`.
5. Identify one observation that would falsify your target or criticality.
6. Explain which material change would trigger review of your SLO.

Do not copy the dispatch row and rename it. Catalog reads have different criticality, dependencies, and freeze consequences from warehouse dispatch. Your durable output is the contract and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 3 capability when you can explain why a copied 99.9 percent is not a portfolio, trace every critical SLO to a Chapter 1 journey and a Chapter 2 accepted SLI, compute remaining budget from observations rather than from a catalog constant, refuse an SLA sentence as a target, keep `notification-service` non-critical, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Northwind now has windows, targets, and remaining error budgets for Storefront and Fulfillment. Those numbers still cannot stop a release, a fleet upgrade, or an exception. Exhausted budget is still a report.

Chapter 4 governs change with error-budget policy so remaining unreliability can continue, slow, or freeze work—including fleet change—without relabeling a Platform upgrade freeze.
