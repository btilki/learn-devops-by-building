# Measure and Bound Toil Without Hiding the Work

Chapter 6 gave Storefront, Fulfillment, and the platform product living primaries, handoffs, and attributable authority. Those humans still spend the week on tickets, manual silences, and copy-paste runbooks. “We will automate later” has no number. “We are busy” is not a measurement. On-call “already watches email,” so someone proposes a new critical **SLO (Service Level Objective)** for `notification-service`.

The production question is now:

> What work is toil, how is it measured, and what bound keeps reliability engineering possible?

Without that decision, unbounded toil makes SLO work theater. Pretending tickets are engineering hides the missing automation. Automating the wrong toil creates a new hero path: a bot that silences pages so nobody sees the journey burn. Chapter 3 already recorded notification as non-critical. Chapter 7 must not promote it because the rotation is drowning.

This chapter adopts a toil definition, an inventory, and a numeric bound. Remaining toil fraction is computed from inventoried hours, not emitted as “plenty of capacity.” A breach blocks adding a new critical SLO.

## 1. An unsafe toil decision

A weak record says:

```yaml
bound: we-are-busy
proposed_slo: notification-service
criticality: critical
justification: on-call-already-watches-email
```

It does not classify the week’s work, name a fraction, name an owner, or compute hours. “Already watches email” may describe last night’s inbox. It cannot complete a toil decision. It reopens a Chapter 3 non-critical system as a critical SLO so the heroics look like scope.

Work from the lab working tree using the Chapter 0 procedure. From the SRE lab root, run the Chapter 7 baseline:

```bash
make chapter-07-baseline
```

The command succeeds when it detects the intended unsafe decision:

```text
chapter 07 baseline: unmeasured toil adding notification as critical slo correctly detected
```

The fixture leaves inventory unclassified, stores the bound as `we-are-busy`, emits a comforting capacity constant, and allows `notification-service` as a new critical SLO because on-call already watches email. Toil has been treated as a mood. Scope has been treated as a reward for being overloaded.

That inversion drives the chapter.

## 2. The production model: classification, fraction, and a gate on scope

> *Theory — Toil bound*
>
> This model enables Northwind to keep reliability engineering possible by measuring interrupt work against a numeric bound, rather than by adding SLO scope because the rotation is already busy.

### Toil is classified work, not a feeling

Toil is repetitive, manual, and scales with production: silences, ticket triage, copy-paste runbooks. Engineering reduces toil or advances SLO governance: writing the Chapter 4 freeze, fixing the good-event definition, removing a class of tickets. Interrupt work arrives unplanned. Project work is planned.

“We are busy” classifies nothing. A ticket volume graph without classes is a dashboard of heroics. An automation that files more tickets than it closes is engineering that hides toil.

**Best Practice:** Give every inventoried item a class (`toil` or `engineering`) and a kind (`interrupt` or `project`), with hours per week.

**Production Practice:** Notification ticket triage is toil and non-critical. It is not a new critical journey. Chapter 3 already refused that promotion.

### The bound is a fraction computed from hours

Available hours are the reliability time the rotation can spend—not calendar myth, not Slack presence. Toil fraction is:

```text
toil fraction = (sum of toil hours per week) / available hours per week
```

The bound is a number in (0, 1], owned by `reliability-program`. Teaching values: 20 available hours, bound 0.5. If inventoried toil is 14 hours, the fraction is 0.7 and the bound is breached. The bound file must not emit `toil_fraction` or `remaining_capacity`. Those would let the inventory approve itself.

The lab cannot measure real engineer hours. The inventory hours are local teaching fixtures, like Chapter 3’s event counts.

### A breach blocks new critical SLO scope

When the fraction meets or exceeds the bound, Northwind may not add a new critical SLO. The first attempted add in this chapter is `notification-service`. It must be denied twice: it is already non-critical in the Chapter 3 catalog, and toil is over the bound.

Allowing it because “on-call already watches email” spends overload as permission. That is informal heroics applied to scope.

Automation that removes toil shrinks inventoried hours. Automation that hides toil—auto-silences that never reach a living primary—must stay classified as toil, not as engineering, until the hours actually fall.

### Load from Chapter 6 is a constraint, not the bound

`page_load_limit: 8` is how many pages a rotation can absorb. Toil hours are how much of the week is interrupt work. They are related and not the same number. Do not replace the bound with “we only got six pages.” Six pages can still consume fourteen hours of silences and runbooks.

## 3. Adopt the definition, inventory, and bound

The completed Chapter 7 model uses three files:

```text
toil/definition.yaml
toil/inventory.yaml
toil/bounds.yaml
```

The separation is deliberate. The definition names classes, kinds, and forbidden measurements. The inventory is the classified week. The bound names the fraction, available hours, owner, and denied scope proposals. Toil fraction is computed at evaluation time.

> **Practice — Forbid mood as a measurement**
>
> Name `we-are-busy` and `on-call-already-watches-email` as labels that cannot be a bound or a scope justification.

Open `toil/definition.yaml`. Allowed classes are `toil` and `engineering`. Allowed kinds are `interrupt` and `project`. Forbidden measurements include `we-are-busy` and `on-call-already-watches-email`. If those strings appear as the bound, later chapters inherit a slogan.

> **Practice — Classify the week, including notification triage**
>
> Keep notification work as non-critical toil. Do not relabel it as engineering so it can become an SLO.

Open `toil/inventory.yaml`. Teaching rows include manual alert silences, copy-paste runbooks, notification ticket triage, and error-budget policy engineering. Each row has class, kind, and `hours_per_week`. Notification triage is `toil`, `interrupt`, and `non-critical`. It is not a Chapter 1 journey.

> **Practice — Deny the notification critical SLO while the bound is breached**
>
> Compute the fraction from hours. Do not store remaining capacity. Do not allow the proposal.

Open `toil/bounds.yaml`. `bound_fraction` is 0.5. `available_hours_per_week` is 20. Owner is `reliability-program`. The scope proposal for `notification-service` as `critical` is `deny`, with reason that it is a non-critical journey and that toil exceeds the bound. If `decision: allow` appears, the checkpoint fails. If `toil_fraction` or `remaining_capacity` appears on the bound, the checkpoint fails.

Fourteen toil hours in a twenty-hour week is remaining engineering time of six hours, not permission to add email as a critical SLO.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-07-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 07 checkpoint: classified inventory, numeric bound, and blocked notification SLO verified
```

The audit validates the three Chapter 7 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- every inventory item has class and kind;
- the bound is a number, not `we-are-busy`;
- toil fraction is computed from hours and available hours;
- the fraction meets or exceeds the bound in the teaching fixture;
- `notification-service` cannot be allowed as a new critical SLO;
- the proposal is denied against the Chapter 3 non-critical record; and
- forbidden justifications are not used as allow reasons.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not measure real engineer hours. It does not prove that 0.5 is the right commercial bound. Those are judgment claims. The review trigger exists so the bound can be reopened without pretending it was never set.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 7 evidence |
|---|---|
| Mechanism evidence | Schemas and the toil evaluator operated successfully. |
| Decision evidence | Definition, classified inventory, numeric bound, and denied notification scope are explicit. |
| Outcome evidence | Toil fraction is computed from inventoried hours, not emitted as capacity. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 7 creates decision evidence and a computed fraction. Pretending that the local checkpoint proved a real week’s hours would weaken later learning and game days.

## 4. Test the decision under failure

### Independent control failure — Unmeasured toil adds notification as a critical SLO

> **Practice — Classify notification as non-critical toil and enforce the bound**
>
> Replace `we-are-busy` with a fraction. Deny the critical SLO.

The baseline fixture contains this model:

```yaml
bound: we-are-busy
proposed_slo: notification-service
criticality: critical
justification: on-call-already-watches-email
toil_fraction: 0.1
```

The problem is not merely missing hours. The model treats overload as permission and a Chapter 3 non-critical system as the next SLO. A constant `toil_fraction: 0.1` is the same self-approval Chapter 3 refused when remaining budget was emitted.

**Severity:** high; the humans Chapter 6 just designed will spend the next SLO on email while order and dispatch toil stay unbounded.  
**Plausible harm:** notification becomes a critical page; order silences stay manual; engineering time disappears; a silence bot hides journey burn.  
**Potential blast radius:** every inbox someone “already watches”; every busy rotation rewarded with more scope.  
**Bounded by:** later dependency contracts (email stays non-critical) and learning-program action bounds. None repairs a bound that is a mood.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** `notification-service` is not `accept-and-complete-order` or `dispatch-fulfillment`. Adding it as critical spends the wrong human system on the wrong outcome.
- **Error budget:** Not a freeze decision. Chapter-local implication: a new critical SLO would consume Chapter 4 freeze attention and Chapter 5 pages the rotation cannot absorb.
- **Human system:** Applicable as load on the Chapter 6 rotations. Unmeasured toil makes `page_load_limit` ornamental.
- **Portfolio recovery:** Not yet produced. A quieter inbox cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling the bound “we are busy” encourages scope controls: add the SLO that matches the inbox, stamp a low fraction so the slide is green, skip classification because tickets “feel like engineering.” Those moves may be sincere. They do not answer which hours are toil, whether notification is a protected journey, or what would have to shrink before scope grows.

The missing classes make automation that hides toil look like progress. The allow on notification makes Chapter 3’s non-critical row ornamental. The emitted fraction makes outcome evidence a constant.

#### Correction

The completed model does not allow the notification SLO. It classifies silences, runbooks, and notification triage as toil, classifies freeze-policy work as engineering, computes a fraction above 0.5 from 14 / 20 hours, denies the proposal, and forbids mood labels as the bound.

That correction changes later decisions:

- Chapter 8 must keep email non-critical in the dependency contract, not promote it because toil was high.
- Chapter 10 must not page Storefront as if notification were a critical journey.
- Chapter 11 must bound learning actions so they do not recreate this inventory as homework.
- Chapter 13 must not treat “we were busy” as a skipped game day.

The decision is practical because it changes the production contract across the rest of the book. Adding an arbitrary command would not make it more practical.

## 5. Production reality

### Common toil errors

#### Using mood as the bound

“We are busy” cannot gate scope. A fraction can.

#### Rewarding overload with a new SLO

The inbox that already consumes the week is usually the thing that should shrink, not the thing that should become critical.

#### Calling tickets engineering

Classification is the decision. Volume is not.

#### Automating silence instead of removing the class of work

A bot that hides pages is toil with a nicer name until inventoried hours fall.

#### Emitting remaining capacity on the bound file

Computed fraction is outcome evidence. A stored 0.1 is a slide.

#### Ignoring Chapter 3 non-critical rows

`notification-service` was already refused as a protected journey. Toil does not reverse that.

## 6. What changed

| Before | After |
|---|---|
| The bound was `we-are-busy`. | **The bound is 0.5 of 20 available hours, owned by `reliability-program`.** |
| Inventory was unclassified tickets. | **Each item has class, kind, and hours per week.** |
| Notification became a proposed critical SLO. | **The proposal is denied; triage stays non-critical toil.** |
| Capacity was a stored 0.1. | **Toil fraction is computed from 14 / 20 hours.** |
| “Already watches email” justified scope. | **Forbidden justifications cannot allow a new critical SLO.** |
| A valid schema could appear to prove a bound. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a reviewable work-allocation contract that later dependencies, incidents, and learning cannot expand by rewarding overload.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Toil definition and bound | `toil/definition.yaml` and `toil/bounds.yaml` | They retain the classes, forbidden measurements, fraction, and scope gate later chapters must not replace with mood. |
| Toil inventory | `toil/inventory.yaml` | It retains classified hours the fraction is computed from. |

These artifacts should change when Northwind's rotations, interrupt classes, or SLO scope materially change—not whenever the ticket tool is renamed.

## What You Learned

Toil is classified, measured as a fraction of available hours, and bounded. A breach blocks new critical SLO scope. `notification-service` stays non-critical. “We are busy” is not a measurement. Automation that hides toil is still toil. Schema checks can prove structural completeness within declared scope. They cannot measure real engineer hours. A decision earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Bound catalog-browse toil without copying the notification row**
>
> A storefront engineer wants a critical catalog-browse SLO “because on-call already answers those tickets.”

Extend the Chapter 7 model without adding dependency policy yet:

1. Classify catalog-browse tickets as toil or engineering, interrupt or project.
2. Decide whether they are in-scope for a new critical SLO given Chapters 1–3.
3. Recompute toil fraction with one teaching hour count; do not emit `toil_fraction`.
4. Allow or deny the proposal against the numeric bound.
5. Identify one observation that would falsify the classification—for example hours falling after a real removal of the ticket class.
6. Explain which material change would trigger review of the bound, not just the ticket queue.

Do not copy the notification deny and rename it. Catalog reads have different criticality and freeze consequences from confirmation email. Your durable output is the classification and gate, not the number of YAML lines changed.

You can demonstrate the Chapter 7 capability when you can explain why “we are busy” is not a bound, classify every inventoried item, compute toil fraction from hours, deny `notification-service` as a new critical SLO, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Engineering time is protected by a numeric gate. Third parties can still burn the budget with no contract. Payment, warehouse, and email can fail while Northwind’s own graphs stay green, or every provider page is treated as a Storefront page.

Chapter 8 puts dependencies inside the reliability contract so payment burns Storefront, warehouse burns Fulfillment, and email stays non-critical.
