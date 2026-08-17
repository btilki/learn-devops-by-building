# Choose Indicators Users Can Feel

Chapter 1 named the journeys, refusals, promise, and owners. That brief does not decide which inherited graph becomes a user-visible **SLI (Service Level Indicator)**.

The production question is now:

> Which measurements are user-visible SLIs, and which measurements must stay non-indicators for the portfolio?

Without a selection method, every green tile looks like “the SLO.” Leadership can see time-to-first-environment. Storefront already emits `order_success_ratio`. CPU is idle. Replica Ready is true. Fulfillment still has no user-visible indicator. Promoting platform job-time or component uptime hides user harm. Measuring nothing leaves dispatch unowned.

This chapter records accept, adjacent, and reject decisions against the Chapter 1 journeys. Later chapters publish targets; they must not reopen job-time as a portfolio **SLO (Service Level Objective)** because the dashboard already shows it.

## 1. An unsafe SLI decision

A weak record says:

```yaml
candidate: time-to-first-environment
treatment: accept
class: portfolio-slo
justification: leadership-can-see-it
```

It does not identify a Chapter 1 journey, a good-event definition, a remaining owner for job-time, or a review trigger. “Leadership can see it” may justify a conversation. It cannot complete an SLI decision.

Work from the lab working tree using the Chapter 0 procedure. From the SRE lab root, run the Chapter 2 baseline:

```bash
make chapter-02-baseline
```

The command succeeds when it detects the intended unsafe selection:

```text
chapter 02 baseline: job-time classed as portfolio-slo correctly detected
```

The fixture accepts `time-to-first-environment` as a portfolio SLO because leadership can see it, leaves `order_success_ratio` as a tenant-workload non-metric, and never accepts a Fulfillment dispatch indicator. Visibility has been treated as user impact. A Chapter 1 refusal has been absorbed. Dispatch still has no signal.

That inversion drives the chapter.

## 2. The production model: good events, classes, and Goodhart's nines

> *Theory — SLI selection*
>
> This model enables Northwind to choose measurements according to user-visible journeys rather than according to whichever graph leadership can already see.

### An SLI is a good-event ratio a user can feel

An SLI answers whether a named journey succeeded for a user in a window. The numerator is good events. The denominator is valid events. A request SLI counts HTTP responses that the user needed. An event SLI counts business outcomes such as a correctly completed order. A windowed SLI counts time buckets in which the journey stayed healthy.

CPU idle is not a good event. Replica Ready is not a good event. A portal page load is not a good event for `accept-and-complete-order`. `order_success_ratio` can be a good-event ratio for that journey because Chapter 1 already named it as later proof. `dispatch_success_ratio` can be a good-event ratio for `dispatch-fulfillment`. Chapter 2 decides the class. Chapter 3 will set the target.

### Class is user-journey, adjacent job-time, or rejected uptime

Northwind can:

- **Accept** a measurement as a user-journey SLI when it traces to a Chapter 1 journey and a user can feel the failed event;
- **Keep adjacent** a platform-product indicator that remains a **job-time budget**, with the remaining owner already recorded in `reliability/refusals.yaml`; or
- **Reject** component uptime, kubelet Ready, portal availability, and other theater the brief already refused.

“Backlog,” “maybe later,” and “the dashboard already has it” are not treatments. `portfolio-slo` is not a class this book may assign to a platform job proof. Platform Chapter 10 already recorded `time-to-first-environment` as `platform-product-sli`. This chapter must not promote it.

### Adjacent is not reject, and it is not accept

Job-time proofs still matter. Fulfillment still needs a bounded environment. The reliability program must not spend those proofs as evidence that orders succeeded, and must not discard them as noise. Adjacent means: reference the inherited id, keep class `platform-product-sli`, name `platform-team` as remaining owner, and leave **error budget** for Chapter 3’s user-journey SLOs.

Platform classified `order_success_ratio` as a tenant-workload non-metric so it could not prove a platform job. That classification is not a reliability reject. The same id is an inherited DevOps outcome indicator. Accepting it as a user-journey SLI does not rename the Platform fixture and does not spend it as time-to-first-environment.

### Goodhart's law applies to nines

A measurement that becomes the SLO will be optimized. If the SLO is cluster Ready, teams will keep Ready green while orders fail. If the SLO is time-to-first-environment, teams will provision faster while dispatch disappears. If the SLO is a copied Storefront 99.9 percent, Fulfillment will inherit a number with no journey.

**Best Practice:** Require the same fields on every treatment: class, journey or remaining owner, owner, and review trigger.

**Production Practice:** An adjacent decision is only real when it cites the remaining owner already recorded on `platform-job-time-as-slo`. A reject is only real when it cites the remaining owner on `cluster-api-uptime`. Chapter 1’s refusals are tested here.

### Targets are not yet the SLI

Selection does not publish a window or an error budget. It decides which measurements may later be targeted. A customer **SLA (Service Level Agreement)** sentence is not an SLI and not an SLO. Chapter 3 owns targets. The decision record is the first reviewable promise about what the portfolio will and will not count.

## 3. Make the SLI decisions

The completed Chapter 2 model uses three files:

```text
slis/method.yaml
slis/candidates.yaml
slis/decisions.yaml
```

The separation is deliberate. The method names allowed treatments, allowed classes, and forbidden justifications. Candidates are proposed measurements, not decisions. Decisions bind treatment to a Chapter 1 journey or remaining owner.

> **Practice — Adopt a method that cannot treat visibility as user impact**
>
> Name the three treatments and the justifications that must never accept a measurement.

Open `slis/method.yaml`. The method forbids `leadership-can-see-it`, `dashboard-already-has-it`, and `copied-from-storefront`. It requires class, journey or remaining owner, owner, and review trigger on every row. Allowed classes are `user-journey-sli`, `platform-product-sli`, and `component-uptime`. If `portfolio-slo` appears as a class, later chapters inherit a slogan instead of a decision.

> **Practice — Accept the journey proofs Chapter 1 already named**
>
> Keep `order_success_ratio` and `dispatch_success_ratio` on the accept path, and bind each to a Chapter 1 journey.

Open `slis/decisions.yaml`. The required accept decisions are:

```yaml
- id: decide-order-success-ratio
  candidate: order_success_ratio
  treatment: accept
  class: user-journey-sli
  journey: accept-and-complete-order
  justification: inherited-outcome-matches-named-journey
  owner: reliability-program
  review_trigger: order-path-changes-good-event-definition
- id: decide-dispatch-success-ratio
  candidate: dispatch_success_ratio
  treatment: accept
  class: user-journey-sli
  journey: dispatch-fulfillment
  justification: chapter-1-later-proof-for-dispatch
  owner: reliability-program
  review_trigger: warehouse-contract-changes-good-event-definition
```

Inspect each accept row with three questions:

1. Does the journey exist in `reliability/journeys.yaml`, or was a new journey invented to justify the graph?
2. Would the measurement still matter if Northwind replaced the dashboard product?
3. Is the named owner authorized to change how the journey is measured?

`order_latency` is accepted for the same Storefront journey. It is an inherited DevOps outcome indicator, not a Platform job proof. Chapter 3 may give it a different window from success ratio. Chapter 2 only decides that users can feel latency on `accept-and-complete-order`.

> **Practice — Keep job-time adjacent and reject component uptime**
>
> Do not promote Platform job proofs, and do not accept CPU or replica Ready as user-journey SLIs.

The environment job-time row must be adjacent, not accepted:

```yaml
- id: decide-time-to-first-environment
  candidate: time-to-first-environment
  treatment: adjacent
  class: platform-product-sli
  remaining_owner: platform-team
  justification: inherited-platform-job-proof
  owner: reliability-program
  review_trigger: platform-product-jobs-change
```

`remaining_owner: platform-team` must match the Chapter 1 refusal `platform-job-time-as-slo`. `paved-road-completion` and `catalog-freshness` stay adjacent for the same reason. The forbidden label is `leadership-can-see-it` used as an accept justification, and the forbidden class is `portfolio-slo` on a job-time id.

CPU utilization, replica Ready, and portal availability are rejected with remaining owner `platform-team`, matching `cluster-api-uptime`. They are theater. They are not Fulfillment’s missing dispatch signal.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-02-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 02 checkpoint: accept, adjacent, and reject SLI decisions verified
```

The audit validates the three Chapter 2 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- the method names accept, adjacent, and reject;
- `order_success_ratio` and `dispatch_success_ratio` are accepted against known journeys;
- `time-to-first-environment` is adjacent with the job-time remaining owner;
- CPU and replica Ready are rejected;
- accept rows do not use forbidden justifications or class `portfolio-slo`;
- every decision names class, owner, and review trigger; and
- adjacent and reject rows name a remaining owner.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not prove that these candidates are the right set for a real company. It does not prove that `order_success_ratio` is the correct good-event definition under live traffic. Those are judgment claims. The review triggers exist so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 2 evidence |
|---|---|
| Mechanism evidence | Schemas and the SLI evaluator operated successfully. |
| Decision evidence | Accept, adjacent, and reject records trace to journeys, refusals, classes, owners, and review triggers. |
| Outcome evidence | Later SLO and burn chapters can be evaluated against these accepted indicators. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 2 primarily creates decision evidence. Pretending that the local checkpoint proves journeys already keep their SLOs would weaken every later chapter.

## 4. Test the decision under failure

### Independent control failure — Time-to-first-environment is classed as a portfolio SLO because leadership can see it

> **Practice — Keep job-time adjacent and accept the named journey proofs**
>
> Reverse a visibility-based accept and restore `order_success_ratio` as a user-journey SLI.

The baseline fixture contains this model:

```yaml
- id: decide-time-to-first-environment
  candidate: time-to-first-environment
  treatment: accept
  class: portfolio-slo
  journey: accept-and-complete-order
  justification: leadership-can-see-it
- id: decide-order-success-ratio
  candidate: order_success_ratio
  treatment: reject
  class: tenant-workload
  remaining_owner: storefront-team
```

The problem is not merely missing fields. The model classifies visibility as user impact and a Chapter 1 refusal as a portfolio SLO. `order_success_ratio`, the later proof Storefront actually named, is left as a tenant-workload non-metric. Dispatch is still absent.

**Severity:** high; every later target, burn page, and freeze conversation will optimize environment wait time instead of orders and dispatch.  
**Plausible harm:** environments provision quickly while orders fail; Fulfillment has no SLI; CPU pages become “the reliability program.”  
**Potential blast radius:** every service asked to “put it on the SLO dashboard”; Storefront’s provisional indicators remain the only real signal.  
**Bounded by:** Chapter 1 refusals, later SLO catalogs, and burn-alert policy. None repairs a method that accepts whichever graph leadership can see.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** The journeys are `accept-and-complete-order` and `dispatch-fulfillment`. Time-to-first-environment is a platform job proof, not those journeys. Rejecting `order_success_ratio` removes the Storefront later proof Chapter 1 already named.
- **Error budget:** Not yet applicable as a freeze decision. Chapter-local implication: a program that targets job-time cannot later freeze Storefront releases for order burn.
- **Human system:** Not yet applicable as on-call design. Chapter-local implication: paging on job-time or CPU trains heroes to ignore dispatch.
- **Portfolio recovery:** Not yet produced. A green time-to-first-environment tile cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling justification “leadership can see it” encourages selection by dashboard: accept job-time, accept CPU, copy Storefront’s number onto Fulfillment. Those graphs may be sincere, but they do not answer which user event is good, who owns the remaining measurement, or what class the inherited Platform fixture already had.

The missing adjacent decision makes Chapter 1’s job-time refusal ornamental. The reject on `order_success_ratio` makes Chapter 3’s Storefront SLO a surprise rather than an inherited later proof. Mapping time-to-first-environment onto `accept-and-complete-order` invents a journey binding the brief never named. Class `portfolio-slo` on a platform-product SLI collapses two books’ evidence.

#### Correction

The completed model does not accept job-time as a portfolio SLO. It keeps `time-to-first-environment` adjacent with `platform-team` as remaining owner, accepts `order_success_ratio` and `dispatch_success_ratio` against the Chapter 1 journeys, rejects CPU and replica Ready, and forbids visibility labels as accept justification.

That correction changes later decisions:

- Chapter 3 must publish windows and remaining budget on accepted user-journey SLIs, not on job-time.
- Chapter 4 must freeze change against order and dispatch burn, not against time-to-first-environment.
- Chapter 5 must page on journey burn and ticket platform job-time to `platform-oncall`.
- Chapter 8 must put payment inside `order_success_ratio`, not inside cluster Ready.

The decision is practical because it changes the production contract across the rest of the book. Adding an arbitrary command would not make it more practical.

## 5. Production reality

### Common selection errors

#### Treating a visible graph as a user-journey SLI

Leadership can see many true graphs. Visibility is not a good-event definition.

#### Leaving Platform’s tenant-workload label on a user outcome

`order_success_ratio` was a non-metric *for the platform product*. It is a candidate *for the reliability program*. Do not copy the Platform exclusion into an SRE reject.

#### Accepting job-time “for now”

Promoting time-to-first-environment creates a target that never expires. Keep it adjacent with a remaining owner and a review trigger instead.

#### Copying Storefront’s indicator onto Fulfillment

Dispatch is not order success. If the journey is not in `reliability/journeys.yaml`, either the brief is wrong or the measurement is out of scope. Do not mint `accept-and-complete-order` bindings for environment wait time.

#### Measuring selection success as dashboard coverage

A thick catalog of CPU tiles is not a thin SLI set. Later measurement must count journey good events, not accepted graphs.

#### Assigning class without authority

The reliability program cannot accept `order_success_ratio` if it cannot change how that ratio is computed. Record the real decision path.

## 6. What changed

| Before | After |
|---|---|
| Time-to-first-environment was accepted as a portfolio SLO. | **Job-time proofs are adjacent with the platform team as remaining owner.** |
| `order_success_ratio` stayed a tenant-workload non-metric. | **`order_success_ratio` is accepted for `accept-and-complete-order`.** |
| Fulfillment had no user-visible indicator. | **`dispatch_success_ratio` is accepted for `dispatch-fulfillment`.** |
| Justification meant dashboard visibility. | **Justification cannot be `leadership-can-see-it`; class cannot be `portfolio-slo`.** |
| CPU and replica Ready looked like reliability. | **Component uptime is rejected with a remaining owner.** |
| A valid schema could appear to prove a sound SLI. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a reviewable SLI contract that later chapters can target, page, freeze, and recover without promoting job-time or theater.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| SLI selection method | `slis/method.yaml` | It retains the treatments, classes, and forbidden justifications later chapters must not reopen as visibility. |
| First indicator decisions | `slis/decisions.yaml` | They retain which measurements the program accepts, keeps adjacent, or rejects, with owners and review triggers. |

These artifacts should change when Northwind’s journeys or good-event definitions materially change—not whenever a new graph is added to the dashboard.

## What You Learned

A reliability program accepts measurements users can feel on named journeys. It keeps platform job-time adjacent. It rejects component uptime even when the graph is green. Visibility is not user impact. Schema checks can prove structural completeness within declared scope. They cannot prove that an indicator is objectively correct. A decision earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Decide a catalog-browse ratio without copying the dispatch row**
>
> A storefront engineer proposes `catalog_read_success_ratio` because “customers hit that page more than they order.”

Extend the Chapter 2 model without adding implementation policy yet:

1. Decide whether catalog reads are a user-visible journey event or a supporting signal of `accept-and-complete-order`.
2. Choose accept, adjacent, or reject without using `leadership-can-see-it`, `dashboard-already-has-it`, or `copied-from-storefront`.
3. Name the Chapter 1 journey or the remaining owner if the measurement is not a user-journey SLI.
4. State the good-event definition as it would exist if the ratio became an SLO.
5. Identify one observation that would falsify your treatment.
6. Explain which material change would trigger review of your decision.

Do not copy the dispatch accept and rename it. Catalog reads have different criticality, dependencies, and freeze consequences from warehouse dispatch. Your durable output is the decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 2 capability when you can explain why a visible job-time graph is not a user-journey SLI, trace every accept row to a known journey, keep a Chapter 1 job-time refusal adjacent with the recorded remaining owner, describe evidence that would falsify the treatment, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Northwind now knows which measurements may represent the journeys and which must not. There are still no portfolio targets, windows, or remaining error budgets. Fulfillment can still inherit Storefront’s 99.9 percent by copy.

Chapter 3 sets SLOs and error budgets across the portfolio so accepted SLIs become governed contracts rather than dashboard tiles.
