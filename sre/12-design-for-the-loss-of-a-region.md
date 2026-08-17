# Design for the Loss of a Region

Chapter 11 can turn a commanded incident into owned, verified change. The architecture still assumes one region. Platform Chapter 14 restored a control plane inside one region and recorded `not-regional-loss` and `not-portfolio-rto`. DevOps Chapter 13 reconstructed one environment. “We have backups” is treated as multi-region. **RTO (Recovery Time Objective)** is “as fast as possible.” Payment and warehouse regionality are hopes.

The production question is now:

> What happens when a region is lost, what portfolio RTO and **RPO (Recovery Point Objective)** are defensible, and which data cannot silently move?

Without that model, fail-over and restore collapse. Reconstructing one environment is filed as regional recovery. Restoring plane last known good `1.0` is filed as the same thing as contract last known good `tenant-storage-1.0`. Storefront and Fulfillment isolation does not survive the story. This chapter writes the architecture. It does not run a game day. It does not execute fail-over. It does not produce **Evidence of portfolio recovery**.

## 1. An unsafe regional claim

A weak record says:

```yaml
rto: as-fast-as-possible
recovery:
  - devops-reconstruction
  - platform-plane-restore
```

It points at inherited restores and calls them regional recovery. It has no second region, no fail-over order, no numeric objectives, and no isolation constraint. “We have backups” may describe one environment’s durable data. It cannot complete a regional-loss architecture.

Work from the lab working tree using the Chapter 0 procedure. From the SRE lab root, run the Chapter 12 baseline:

```bash
make chapter-12-baseline
```

The command succeeds when it detects the intended unsafe model:

```text
chapter 12 baseline: inherited restore claimed as regional recovery correctly detected
```

The fixture stores RTO as `as-fast-as-possible`, claims regional recovery from DevOps reconstruction and Platform plane restore, omits tenant isolation, omits payment and warehouse regionality, and collapses plane last known good with the storage contract identity. One-region restore has been treated as a portfolio region plan. Unmeasured speed has been treated as an objective.

That inversion drives the chapter.

## 2. The production model: regions, numeric objectives, and named insufficiency

> *Theory — Regional-loss architecture*
>
> This model enables Northwind to describe what happens when a region is lost, with numeric portfolio objectives and constraints, rather than by pointing at one-environment reconstruction or a control-plane restore.

### Fail-over is not restore

Restore rebuilds something in place: one environment from DevOps Chapter 13 roots, or a control plane to last known good `1.0` inside the same region. Fail-over moves serving to another region under a reviewed order. Those are different production questions. Platform already recorded `not-regional-loss` and `not-portfolio-rto`. This chapter **consumes** those limitations. It does not rewrite Platform recovery, and it does not pretend they were never written.

Plane last known good `1.0` and contract last known good `tenant-storage-1.0` stay distinct identities. Neither is a region. Listing them as one restore id collapses two inherited recoveries into a slogan.

**Best Practice:** Name at least two regions, a fail-over order, and the inherited restores that are insufficient.

**Production Practice:** Teaching topology is active-passive: `region-primary` serves, `region-standby` is the fail-over target. Active-active without an order is a hope. This chapter does not execute the shift.

### Portfolio RTO and RPO are numeric and owned

RTO is how long the portfolio may take to serve the Chapter 1 journeys from the surviving region. RPO is how much journey state may be lost. Both are numbers with an owner. Teaching values: RTO `14400` seconds (four hours), RPO `900` seconds (fifteen minutes), owner `reliability-program`. Those are local fixtures, not industry constants.

`as-fast-as-possible` is not a number. Unmeasured RTO cannot later prove a miss. The objectives file must not emit `status: recovered`. Architecture is not **Evidence of portfolio recovery**.

### Isolation and provider regionality are constraints, not hopes

Storefront and Fulfillment are inherited tenants. Isolation must survive fail-over. A mixed-tenant shift is a later Chapter 14 rejection, but Chapter 12 must already name the constraint or Chapter 14 inherits “put them in the same restore.”

Payment is a critical Storefront dependency. Warehouse is a critical Fulfillment dependency. Chapter 8 already placed them inside journey **SLOs (Service Level Objectives)**. Their regionality is a constraint: they do not silently follow Northwind’s traffic. Email remains non-critical; it is not a third region story.

Data that cannot silently cross regions includes tenant order state and warehouse dispatch state. The lab cannot discover unknown real data gravity. Named constraints are the architecture. Missing gravity stays missing; it is not filled with a backup slogan.

## 3. Publish architecture, objectives, and constraints

The completed Chapter 12 model uses three files:

```text
regions/architecture.yaml
regions/objectives.yaml
regions/constraints.yaml
```

The separation is deliberate. Architecture names regions, mode, and fail-over order. Objectives name numeric RTO and RPO with owner. Constraints name isolation, provider regionality, data that cannot silently move, and insufficient inherited restores. None of the files may claim the portfolio recovered.

> **Practice — Name two regions and an order; do not call restore fail-over**
>
> Keep the topology active-passive until a later chapter executes a shift.

Open `regions/architecture.yaml`. Regions are `region-primary` and `region-standby`. Mode is `active-passive`. Fail-over order is from `region-primary` to `region-standby` when `region-primary` is lost. Owner is `reliability-program`. If only one region appears, later fail-over has nowhere to go.

> **Practice — Publish numeric owned RTO and RPO**
>
> Refuse `as-fast-as-possible`. Do not emit recovered.

Open `regions/objectives.yaml`. `rto_seconds` is `14400`. `rpo_seconds` is `900`. Owner is `reliability-program`. Review trigger is material change to journeys, regions, or provider regionality. If RTO is a slogan, the checkpoint fails.

Inspect the objectives with three questions:

1. Could a later fail-over miss this number, or is the target unfalsifiable?
2. Is the owner `reliability-program`, or whoever restored the plane last time?
3. Would this still be true if DevOps reconstruction succeeded in the lost region?

> **Practice — List inherited restores as insufficient; keep isolation and provider regionality**
>
> Consume `not-regional-loss` and `not-portfolio-rto`. Do not collapse plane `1.0` with `tenant-storage-1.0`.

Open `regions/constraints.yaml`. Isolation requires Storefront and Fulfillment to remain distinct through fail-over. Provider regionality marks `payment` and `warehouse` as `region-scoped`. `no_silent_cross_region` names tenant order state and warehouse dispatch state. `insufficient_restores` lists DevOps one-environment reconstruction and Platform plane restore. `insufficient_identities` lists plane last known good `1.0` and contract last known good `tenant-storage-1.0` as separate rows. `limitations_consumed` lists `not-regional-loss` and `not-portfolio-rto`.

If those inherited limitation ids are missing, later chapters will treat Platform recovery as the regional plan.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-12-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 12 checkpoint: numeric rto rpo, isolation, and insufficient inherited restores verified
```

The audit validates the three Chapter 12 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- two regions and an active-passive fail-over order exist;
- RTO and RPO are positive numbers owned by `reliability-program`;
- RTO is not `as-fast-as-possible`;
- Storefront and Fulfillment isolation survives fail-over;
- payment and warehouse regionality are constraints;
- DevOps reconstruction and Platform plane restore are insufficient;
- plane last known good `1.0` and `tenant-storage-1.0` stay distinct insufficient identities;
- Platform limitations `not-regional-loss` and `not-portfolio-rto` are consumed; and
- `status: recovered` is not emitted.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint cannot discover unknown real data gravity. It does not fail over a live region. It does not prove that four hours or fifteen minutes is the right commercial pair. Those are judgment claims. The review trigger exists so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 12 evidence |
|---|---|
| Mechanism evidence | Schemas and the regional-architecture evaluator operated successfully. |
| Decision evidence | Regions, fail-over order, numeric objectives, isolation, and insufficient inherited restores are explicit. |
| Outcome evidence | Not yet produced as a fail-over; objectives are falsifiable numbers, not slogans. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 12 creates decision evidence about regional loss. Pretending that the local checkpoint proved a multi-region estate would weaken game days and executed fail-over.

## 4. Test the model under failure

### Independent control failure — Inherited restore claimed as regional recovery

> **Practice — Separate fail-over from restore; assign numeric objectives; list inherited recoveries as insufficient**
>
> Drop `as-fast-as-possible`. Keep plane `1.0` distinct from `tenant-storage-1.0`.

The baseline fixture contains this model:

```yaml
rto: as-fast-as-possible
recovery:
  - devops-reconstruction
  - platform-plane-restore
claims: regional-recovery
```

The problem is not merely a missing second region. The model treats one-environment reconstruction and in-region plane restore as the regional architecture. Unmeasured RTO cannot later miss. Isolation and provider regionality are absent, so a mixed-tenant hope is the plan.

**Severity:** high; a real region loss will invent the plan during the event, the book’s cumulative informal heroics.  
**Plausible harm:** Storefront is restored in the lost region; Fulfillment isolation collapses; payment does not exist in the “standby”; RTO is whatever someone typed in chat.  
**Potential blast radius:** every backup labeled multi-region; every plane restore labeled portfolio RTO.  
**Bounded by:** later game days and executed fail-over. None repairs an architecture that is two inherited runbooks.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** Both `accept-and-complete-order` and `dispatch-fulfillment` are at risk when a region is lost. Reconstructing one Storefront environment does not recover dispatch.
- **Error budget:** Not a new freeze rule. Chapter-local implication: unmeasured RTO cannot later authorize continue or freeze during fail-over.
- **Human system:** Applicable as later game-day and fail-over load on Chapter 6 rotations. An unmeasured objective makes the commander guess.
- **Portfolio recovery:** Not yet produced. Pointing at plane last known good cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling inherited restore “regional recovery” encourages three controls: skip a second region because backups exist, skip numbers because speed is obvious, and skip isolation because tenants already share a platform. Those moves may be sincere. They do not answer where traffic goes, how much state may be lost, or which provider will not follow.

Collapsing plane `1.0` with `tenant-storage-1.0` makes two Platform identities one restore. Omitting `not-regional-loss` makes Platform’s own limitation ornamental. `as-fast-as-possible` makes outcome evidence a mood.

#### Correction

The completed model does not claim inherited restore is regional fail-over. It names two regions and an active-passive order, publishes numeric owned RTO and RPO, keeps tenant isolation, marks payment and warehouse as region-scoped, lists DevOps reconstruction and plane restore as insufficient, keeps the two last-known-good identities distinct, and consumes Platform’s regional limitations.

That correction changes later decisions:

- Chapter 13 must tabletop or simulate this regional loss as one scenario among others, not as a mixed-backup fixture that stands in for fail-over.
- Chapter 14 must execute fail-over against these numbers and constraints, and must not treat reconstruction or plane restore as **Evidence of portfolio recovery**.

The model is practical because it changes the production contract across the rest of the book. Adding an arbitrary cloud-region diagram would not make it more practical.

## 5. Production reality

### Common regional-architecture errors

#### Treating backups as a second region

Durable data in one region is restore. Fail-over needs another region.

#### Unmeasured RTO

“As fast as possible” cannot miss. A second count can.

#### Collapsing plane last known good with the storage contract

They are distinct inherited identities. Neither is a region.

#### Ignoring tenant isolation

Storefront and Fulfillment must remain distinct through the story, or Chapter 14 inherits mixed-tenant fail-over.

#### Hoping payment and warehouse follow traffic

Chapter 8 already made them critical. Regionality is a constraint.

#### Emitting recovered on the architecture file

Architecture is not **Evidence of portfolio recovery**.

#### Copying Storefront’s region row onto Fulfillment as if dispatch were checkout

Different journey, dependency, and data gravity.

## 6. What changed

| Before | After |
|---|---|
| RTO was `as-fast-as-possible`. | **RTO is 14400 seconds, RPO is 900 seconds, owned by `reliability-program`.** |
| Recovery pointed at DevOps reconstruction and plane restore. | **Those inherited restores are listed as insufficient.** |
| Plane `1.0` and `tenant-storage-1.0` were one identity. | **They remain distinct insufficient identities.** |
| Isolation was assumed. | **Storefront and Fulfillment isolation survives fail-over.** |
| Payment and warehouse would “just work.” | **Both are region-scoped constraints.** |
| A valid schema could appear to prove multi-region. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a reviewable regional-loss architecture that later game days and fail-over can consume without inventing the plan during the outage.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Regional-loss architecture | `regions/architecture.yaml` | It retains regions, active-passive mode, and fail-over order later execution must not replace with a single restore. |
| Portfolio RTO/RPO decision record | `regions/objectives.yaml` and `regions/constraints.yaml` | They retain numeric objectives, isolation, provider regionality, and insufficient inherited restores. |

These artifacts should change when Northwind's regions, journeys, or provider regionality materially change—not whenever a backup product is renamed.

## What You Learned

Regional loss needs two regions, a fail-over order, and numeric owned RTO and RPO. Fail-over is not restore. DevOps one-environment reconstruction and Platform plane restore are insufficient. Plane last known good and contract last known good stay distinct. Tenant isolation and payment/warehouse regionality are constraints. Schema checks can prove structural completeness within declared scope. They cannot discover unknown real data gravity or fail over a live estate. A model earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Place catalog-browse data without copying the payment region row**
>
> A storefront engineer wants catalog search “in both regions because backups already exist, RTO as fast as possible, same as payment.”

Extend the Chapter 12 model without adding a game-day program yet:

1. Decide whether catalog-browse state may silently cross regions, given Chapters 1–3 and 8.
2. Give it a constraint that is not a renamed payment `region-scoped` row, or record it out of scope.
3. Do not use `as-fast-as-possible` as its objective.
4. Do not list DevOps reconstruction as sufficient for that data.
5. Identify one observation that would falsify the architecture—for example plane restore still claimed as regional recovery.
6. Explain which material change would trigger review of the objectives, not just the backup job name.

Do not copy the warehouse constraint and rename it. Catalog reads have different gravity and freeze consequences from dispatch. Your durable output is the constraint and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 12 capability when you can explain why inherited restore is not fail-over, name two regions and numeric RTO/RPO, keep isolation and provider regionality, list plane `1.0` and `tenant-storage-1.0` as distinct insufficient identities, consume `not-regional-loss` and `not-portfolio-rto`, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

The architecture exists on paper. It has not been exercised as a program. The only practiced recovery nearby is Platform’s mixed-backup isolation test. There is no cadence, blast-radius contract, or learning join.

Chapter 13 publishes a game-day program so freeze, on-call page path, dependency loss, and regional-loss tabletop or simulated fail-over are exercised on a cadence—not as a rehearsal of Chapter 14 fail-over, and not as a single mixed-backup fixture.
