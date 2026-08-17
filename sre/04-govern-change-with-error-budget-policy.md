# Govern Change with Error-Budget Policy

Chapter 3 published windows, numeric targets, and remaining unreliability. Storefront and Fulfillment now have **SLOs (Service Level Objectives)**. Remaining budget is computed from observations. Those numbers still cannot stop a digest promotion, a fleet step, or an exception that never expires.

The production question is now:

> When remaining **error budget** is healthy, slowing, or exhausted, what change is authorized, slowed, or frozen?

Without that policy, the catalog is theater. Releases ship on the calendar. Platform already knows how to freeze fleet upgrade `storage-1-0-to-2-0` for an upgrade. Fulfillment’s cohort is still pending. Storefront’s order-success budget can sit at zero while that step proceeds because “the freeze window was for upgrades.” Freezing everything on first burn is the opposite failure: a change freeze with no bands, no owner, and no expiry.

This chapter maps remaining budget to continue, slow, and freeze. It may halt the same fleet step Platform knows how to freeze, for a reliability reason Platform did not own. It must not copy freeze window, cohort, or rollback, and must not relabel a Platform upgrade freeze as this policy.

## 1. An unsafe policy: exhausted budget, fleet still proceeds

A weak record says:

```yaml
target: storage-1-0-to-2-0
action: continue
freeze_reason: platform-upgrade-freeze
freeze:
  start: 2026-08-16T00:00:00Z
  end: 2026-08-23T00:00:00Z
rollback: "1.0"
```

It notices Storefront is red. It still lets the fleet step run because the inherited freeze was scheduled for the contract bump. Copying `freeze`, `cohorts`, and `rollback` onto this policy pretends Platform already answered the reliability question. Platform answered a different one.

Work from the lab working tree using the How to Use This Book procedure. From the SRE lab root, run the Chapter 4 baseline:

```bash
make chapter-04-baseline
```

The command succeeds when it detects the intended unsafe policy:

```text
chapter 04 baseline: unfrozen fleet under exhausted storefront budget correctly detected
```

The fixture computes Storefront remaining at zero, may freeze Storefront releases, and still continues `storage-1-0-to-2-0` with reason `platform-upgrade-freeze` and copied upgrade fields. Exhausted budget has been treated as a dashboard. A Platform upgrade freeze has been treated as an error-budget freeze. This is the book’s cumulative reliability failure: availability theater plus informal heroics, now wearing a fleet calendar.

That residual drives the chapter.

## 2. The production model: bands, freeze by reference, exceptions that expire

> *Theory — Error-budget policy*
>
> This model enables Northwind to continue, slow, or freeze change from remaining unreliability rather than from a calendar, a ticket, or a Platform upgrade window.

### Remaining budget selects an action; it does not emit one

Chapter 3 already defined remaining as `1 − (observed bad / allowed bad)`. Policy does not store remaining as a constant. It names bands:

| Remaining | Action | Meaning |
|---|---|---|
| ≥ 0.5 | continue | Ordinary change proceeds |
| ≥ 0.1 and < 0.5 | slow | Change proceeds with extra review and reduced rate |
| < 0.1 | freeze | Named change stops until budget recovers or an exception expires |

Those thresholds are teaching values. They are not industry constants. Remaining below zero is still freeze. A band of “freeze everything” with no target is not a policy. A band of “continue until someone pages” is not a policy.

**Best Practice:** Bind every action to a Chapter 3 SLO or to an explicit non-critical exception. A freeze that cannot name the journey is a holiday freeze.

### Release freeze and fleet freeze are different change kinds

Exhausted Storefront order-success budget freezes Storefront releases. The inherited DevOps promotion identity is `artifact_digest`. This chapter references that identity. It does not redesign digest promotion.

The same exhausted budget may freeze fleet upgrade `storage-1-0-to-2-0` while Fulfillment’s cohort is still pending. Storefront and Fulfillment share the storage contract. A fleet step that proceeds under zero Storefront budget spends reliability the catalog already refused. Fulfillment still having remaining budget does not authorize that step. Slow Fulfillment releases. Freeze the shared fleet change.

This freeze **references** the inherited upgrade id. It adds freeze reason, remaining-budget source, owner, and expiry. It must not copy Platform freeze window, cohort list, rollback, last known good, or from/to versions. Those fields already live on the Platform record. Copying them here collapses two freeze reasons into one YAML document.

**Production Practice:** A Platform upgrade freeze is not an error-budget freeze. An error-budget freeze may halt that same fleet step for a reason Platform did not own. `freeze_reason: platform-upgrade-freeze` is the collapse. `freeze_reason: exhausted-storefront-error-budget` with `owner: reliability-program` is this book’s act.

### Exceptions expire and name remaining journey risk

A freeze without exceptions recreates a change freeze. An exception without owner, scope, expiry, and remaining journey risk recreates a ticket. The exception is not a second SLO. It is a time-bounded permission to change a named scope while the freeze remains in force elsewhere.

If the scope is `storage-1-0-to-2-0`, the remaining journey risk must be explicit: which Chapter 1 journey still burns if the step proceeds. If the exception has no `expires_at`, it is a permanent unfreeze. If it has no `removal_path`, nobody knows how it ends.

`notification-service` is still non-critical. Confirmation templates may continue under a Storefront freeze. That continue is a policy decision, not proof that orders succeeded.

### Expiry is part of the freeze

A freeze that never expires becomes folklore. Record `expires_at` on freeze actions. Review when remaining budget recovers or the window elapses. Chapter 5 will page on burn. Chapter 4 must already stop the digest and the fleet step without waiting for a page.

## 3. Write the policy

The completed Chapter 4 model uses three files, plus Chapter 4 observations the evaluator consumes:

```text
policy/error-budget.yaml
policy/actions.yaml
policy/exceptions.yaml
fixtures/observations/chapter-04.yaml
```

The separation is deliberate. The policy names bands. Actions bind continue, slow, and freeze to change kinds. Exceptions are the only legal unfreeze. Remaining budget is computed from Chapter 4 observations against the Chapter 3 catalog. The policy files must not emit remaining as a constant.

> **Practice — Name bands that cannot freeze everything or freeze nothing**
>
> Require continue, slow, and freeze, each with a remaining threshold.

Open `policy/error-budget.yaml`. Continue starts at remaining 0.5. Slow starts at 0.1. Freeze is everything below that, including zero and negative remaining. If freeze is missing, exhausted budget cannot stop change. If continue is missing, every blip is a freeze.

> **Practice — Freeze Storefront releases and the shared fleet step by reference**
>
> Halt digest promotion and `storage-1-0-to-2-0` for exhausted Storefront budget without copying Platform upgrade fields.

Open `policy/actions.yaml`. The required freeze rows are:

```yaml
- id: freeze-storefront-releases
  slo: slo-accept-and-complete-order
  action: freeze
  change_kind: release
  target: storefront-releases
  promotion_identity: artifact_digest
  owner: reliability-program
  expires_at: 2026-08-23T00:00:00Z
  review_trigger: remaining-budget-recovers-or-window-elapses
- id: freeze-fleet-storage-upgrade
  slo: slo-accept-and-complete-order
  action: freeze
  change_kind: fleet
  target: storage-1-0-to-2-0
  freeze_reason: exhausted-storefront-error-budget
  owner: reliability-program
  expires_at: 2026-08-23T00:00:00Z
  review_trigger: remaining-budget-recovers-or-fulfillment-cohort-replanned
```

Inspect the fleet row with three questions:

1. Is `target` the inherited upgrade id, or a renamed local copy?
2. Does the row contain `freeze`, `cohorts`, `rollback`, or `last_known_good`? If it does, this policy has absorbed Platform Chapter 12.
3. Is `freeze_reason` an SRE-owned remaining-budget reason, or `platform-upgrade-freeze`?

Fulfillment releases are slowed, not frozen: dispatch remaining is still 0.3. Notification templates continue: they are not a critical journey. Order-latency remaining is still healthy; it does not unfreeze Storefront releases. Exhausted order success is enough.

> **Practice — Record an exception that expires**
>
> Name owner, scope, remaining journey risk, expiry, and removal path. Do not unfreeze the fleet step.

Open `policy/exceptions.yaml`. A valid exception can cover a non-critical confirmation template. It cannot omit `expires_at`. It cannot take `storage-1-0-to-2-0` as scope without stating which journey still burns.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-04-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 04 checkpoint: continue, slow, and freeze policy including SRE-owned fleet freeze verified
```

The audit validates the three Chapter 4 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- remaining budget is computed from Chapter 4 observations, not emitted by the policy;
- Storefront order-success remaining is at or below the freeze band;
- Storefront releases are frozen against inherited `artifact_digest`;
- fleet upgrade `storage-1-0-to-2-0` is frozen with an SRE-owned reason;
- the fleet freeze does not copy Platform freeze window, cohort, or rollback fields;
- `freeze_reason` is not `platform-upgrade-freeze`;
- Fulfillment releases are slowed while dispatch still has remaining budget;
- continue, slow, and freeze are all used; and
- every exception names owner, scope, remaining journey risk, expiry, and removal path.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not halt a live release or a live fleet. It does not prove that 0.5 / 0.1 are the right commercial bands. Those are judgment claims. The review triggers exist so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 4 evidence |
|---|---|
| Mechanism evidence | Schemas and the policy evaluator operated successfully. |
| Decision evidence | Bands, freeze targets, SRE-owned fleet reason, and expiring exceptions are explicit. |
| Outcome evidence | Remaining budget computed from observations selects freeze rather than continue for Storefront and the shared fleet step. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 4 creates decision evidence and uses Chapter 3’s computation as outcome input. Pretending that the local checkpoint froze a production cluster would weaken every later page, incident, and fail-over.

## 4. Test the design under failure

### Cumulative reliability failure — Storefront budget exhausted, fleet upgrade still proceeds

> **Practice — Apply the error-budget freeze and halt the fleet step**
>
> Keep Storefront releases frozen, freeze `storage-1-0-to-2-0` by reference, and drop copied Platform upgrade fields.

The baseline fixture contains this model:

```yaml
- id: proceed-fleet-storage-upgrade
  slo: slo-accept-and-complete-order
  action: continue
  change_kind: fleet
  target: storage-1-0-to-2-0
  freeze_reason: platform-upgrade-freeze
  freeze:
    start: 2026-08-16T00:00:00Z
    end: 2026-08-23T00:00:00Z
  rollback: "1.0"
```

The problem is not merely a missing freeze row. The model treats a Platform upgrade calendar as the reliability decision. Storefront remaining is zero. Fulfillment’s cohort is still pending. The shared storage step proceeds. Copied freeze fields make the two reasons look like one record.

**Severity:** high; exhausted journey budget cannot stop the change that still couples Storefront and Fulfillment.  
**Plausible harm:** Storefront releases pause while the fleet step still moves storage; Fulfillment absorbs `2.0` under a Storefront outage; heroes ship around the dashboard.  
**Potential blast radius:** every tenant on `tenant-storage`; Storefront order path and the pending Fulfillment cohort.  
**Bounded by:** later burn pages, on-call, and incident freeze joins. None repairs a policy that continues fleet change because the upgrade freeze was “already on the calendar.”  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** `accept-and-complete-order` is at remaining zero. `dispatch-fulfillment` still has remaining budget. The fleet step is shared; it is not a Fulfillment-only change.
- **Error budget:** Applicable as a freeze decision. Remaining Storefront unreliability is exhausted. Continuing `storage-1-0-to-2-0` spends that budget. A Platform upgrade freeze does not compute remaining.
- **Human system:** Not yet applicable as on-call design. Chapter-local implication: an unfrozen fleet step under a red Storefront tile trains heroes to “just finish the upgrade.”
- **Portfolio recovery:** Not yet produced. Completing a fleet cohort cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling the continue “the freeze window is for upgrades” encourages calendar controls: keep Platform’s dates, copy rollback to `1.0`, mark the reliability program aligned. Those fields are true for Platform Chapter 12. They do not answer whether Storefront may still change, who owns a reliability freeze, or when that freeze expires.

The missing SRE freeze reason makes Chapter 3’s remaining budget ornamental. The copied upgrade fields make Chapter 12’s freeze look like this policy. An exception without expiry would finish the collapse: a permanent unfreeze by ticket.

#### Correction

The completed model does not continue the fleet step. It freezes Storefront releases against `artifact_digest`, freezes `storage-1-0-to-2-0` with reason `exhausted-storefront-error-budget` and owner `reliability-program`, slows Fulfillment releases, lets non-critical notification continue, and records an exception that expires. Platform freeze window, cohort, and rollback stay on the inherited record.

That correction changes later decisions:

- Chapter 5 must page on journey burn that this policy already froze, not on CPU that cannot freeze a fleet.
- Chapter 6 must page a rotation that can act on this freeze, not a catalog label.
- Chapter 10 must join incident close to whether this freeze still applies.
- Chapter 13 must exercise an error-budget freeze, not only a Platform upgrade freeze.

The design is practical because it changes the production contract across the rest of the book. Adding an arbitrary command would not make it more practical.

## 5. Production reality

### Common policy errors

#### Relabeling a Platform upgrade freeze as error-budget policy

The same upgrade id can be frozen twice for two reasons. Copying the reason collapses them.

#### Freezing Storefront releases but letting the shared fleet step run

Fulfillment’s remaining budget does not authorize a storage bump Storefront cannot currently survive.

#### Copying freeze window, cohort, or rollback into this policy

Those fields are Platform’s. Reference the upgrade id. Add reason, owner, and expiry.

#### Freezing everything on first burn

Without a slow band, every dip is a holiday freeze. Heroes will file exceptions that never expire.

#### Exceptions without expiry

A freeze with a permanent ticket is not a freeze. Record `expires_at` and `removal_path`.

#### Emitting remaining budget on the policy

Chapter 3 already refused catalog self-approval. Policy self-approval is the same failure.

## 6. What changed

| Before | After |
|---|---|
| Storefront remaining was zero and the fleet step still proceeded. | **`storage-1-0-to-2-0` is frozen for exhausted Storefront error budget.** |
| The freeze reason was `platform-upgrade-freeze`. | **The freeze reason is SRE-owned remaining-budget exhaustion.** |
| Platform freeze window, cohort, and rollback were copied here. | **The policy references the upgrade id and leaves those fields on the inherited record.** |
| Bands were “ship unless someone yells.” | **Continue, slow, and freeze bind remaining unreliability to named change kinds.** |
| Exceptions were tickets. | **Exceptions name owner, scope, remaining journey risk, expiry, and removal path.** |
| A valid schema could appear to prove a freeze. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a reviewable change-control contract that later chapters can page, command, and exercise without relabeling a Platform upgrade freeze.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Error-budget policy | `policy/error-budget.yaml` | It retains the continue / slow / freeze bands later pages and incidents must not replace with a calendar. |
| Freeze-and-exception contract | `policy/actions.yaml` and `policy/exceptions.yaml` | They retain which releases and which fleet step freeze, by reference, with expiry. |

These artifacts should change when Northwind's journeys, remaining-budget bands, or fleet upgrade identity materially change—not whenever a change-calendar theme is restyled.

## What You Learned

Error-budget policy maps remaining unreliability to continue, slow, or freeze. Exhausted Storefront budget freezes Storefront releases and may freeze a shared fleet step Platform already knows how to freeze for upgrades. That freeze references the inherited upgrade id. It does not copy Platform freeze window, cohort, or rollback, and it does not relabel an upgrade freeze as this policy. Schema checks can prove structural completeness within declared scope. They cannot halt a live fleet. A design earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Exception a catalog experiment without copying the fleet freeze**
>
> A storefront engineer wants to ship a catalog-browse experiment while order-success remaining is zero “because Fulfillment’s cohort is pending anyway.”

Extend the Chapter 4 model without adding paging policy yet:

1. Decide whether the experiment is a Storefront release (frozen), a non-critical continue, or an exception.
2. If you grant an exception, name remaining journey risk that is not “the fleet freeze window is still open.”
3. Choose a scope that is not a paste of `storage-1-0-to-2-0` unless the experiment actually mutates that upgrade.
4. Set `expires_at` and a `removal_path`.
5. Identify one observation that would falsify the exception—for example remaining still zero and catalog reads now in the order path.
6. Explain which material change would trigger review of the exception, not just the experiment ticket.

Do not copy the fleet freeze row and rename it. Catalog reads have different freeze consequences from a shared storage upgrade. Your durable output is the policy decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 4 capability when you can explain why a Platform upgrade freeze is not an error-budget freeze, freeze Storefront releases and `storage-1-0-to-2-0` from computed remaining budget, refuse copied upgrade fields, keep Fulfillment slowed rather than frozen while dispatch still has budget, require exceptions to expire, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Northwind can now stop a digest and a fleet step when remaining budget is exhausted. Humans are still woken by every red graph. CPU pages. Replica Ready pages. Order-success burn is a dashboard panel.

Chapter 5 pages on burn rate rather than on every symptom, so this policy has a signal that matches the journey rather than a hero roster chasing tiles.
