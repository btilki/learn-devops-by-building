# Fail Over a Region Without Taking the Portfolio Down

Chapter 13 can exercise freeze, page path, dependency loss, and regional-loss tabletop on a cadence. A region is still lost. The temptation is to reconstruct one environment, restore the plane from newest, or invent the order during the outage. Mixed-tenant fail-over recreates Platform’s shared blast radius. A green reconstruction job is treated as the portfolio.

The production question is now:

> How does Northwind fail over a lost region, keep tenant isolation, meet portfolio **RTO (Recovery Time Objective)** and **RPO (Recovery Point Objective)**, and prove the portfolio recovered?

Without that execution, newest mixed-region state is applied, Fulfillment intent lands in Storefront, and recovery is declared because one environment’s reconstruction succeeded. This chapter follows the Chapter 12 order, keeps Storefront and Fulfillment isolated, and produces **Evidence of portfolio recovery** in the model. It cannot prove a live multi-region estate. It is not DevSecOps restored trust, not Platform restored isolation, and not a Chapter 13 tabletop copied as recovery.

## 1. An unsafe mixed-region recovered stamp

A weak record says:

```yaml
replay: newest-mixed-region
fulfillment_intent: storefront
status: recovered
recovery: devops-reconstruction
```

It applies newest state across tenants and regions, puts Fulfillment intent into Storefront, and stamps recovered because DevOps reconstruction ran. Plane last known good `1.0` and `tenant-storage-1.0` collapse again. Isolation does not survive. **SLOs (Service Level Objectives)** for `accept-and-complete-order` and `dispatch-fulfillment` are not checked. Informal heroics have been given a restore job.

Work from the lab working tree using the Chapter 0 procedure. From the SRE lab root, run the Chapter 14 baseline:

```bash
make chapter-14-baseline
```

The command succeeds when it detects the intended unsafe design:

```text
chapter 14 baseline: mixed-region replay declared recovered correctly detected
```

The fixture replays mixed-region newest state, lands Fulfillment in Storefront, claims reconstruction as recovery, misses numeric RTO and RPO, collapses isolation, and emits `status: recovered` to hide those misses. A Platform mixed-backup failure and a DevOps one-environment reconstruction have been treated as the SRE fail-over. Availability theater has been given a recovered flag.

That inversion drives the chapter.

## 2. The production model: order, isolation, explicit continue or freeze, computed recovery

> *Theory — Executed regional fail-over*
>
> This model enables Northwind to fail over a lost region from reviewed evidence, keep tenant isolation, and prove portfolio recovery against numeric objectives, rather than by applying newest mixed-region state or reconstructing one environment.

### Fail-over follows Chapter 12; it does not restore in place

The plan consumes `northwind-regional-architecture`. Lost `region-primary` is isolated. Serving moves to `region-standby` when `region-primary-lost`. Mode stays active-passive. Restore-in-place to the lost region is DevOps reconstruction under a fail-over name. Chapter 13’s `gameday-regional-loss-tabletop` and Platform’s `mixed-backup` are insufficient evidence. They may have been practiced. They are not this execution.

Last known good is per region and per tenant. Plane `1.0` and contract `tenant-storage-1.0` remain distinct insufficient identities. Newest is not last known good. A snapshot that holds every inherited root can still replay one tenant into another.

**Best Practice:** Isolate the lost region, follow the reviewed order, and reject mixed-tenant and mixed-region replay before anyone talks about recovered.

**Production Practice:** Teaching observations: elapsed `3600` seconds against RTO `14400`, data loss `300` seconds against RPO `900`. Those are local fixtures, not industry constants.

### Continue or freeze is explicit; recovered is computed

Platform already taught continue versus freeze for tenants during plane restore. This chapter applies that idea to a region. Storefront **serves** from standby (`continue`) and **change** stays `freeze` on `freeze-storefront-releases`. Fulfillment **serves** (`continue`) and **change** stays `slow` on `slow-fulfillment-releases`. Missing decisions are mixed-backup with a regional story. The commander is `storefront-primary-a`, a living Chapter 6 primary, not Slack.

Verification records journeys, elapsed seconds, RPO loss, isolation, mixed-replay rejection, insufficient inherited restores, and consumed Platform limitations `not-regional-loss` and `not-portfolio-rto`. It must not emit `status: recovered`. Completeness is computed. If RTO is missed, RPO is missed, or isolation collapsed, a recovered stamp is a hide, not a proof.

Job-time proofs such as `time-to-first-environment` stay a **job-time budget**. They cannot become portfolio recovery. Notification remaining non-critical cannot stand in for dispatch.

The lab cannot prove a real multi-region fail-over. Results are local fixtures, like Chapter 3’s event counts. Modeled **Evidence of portfolio recovery** is the strongest claim this chapter may make.

## 3. Publish plan, trace, isolation, and verification

The completed Chapter 14 model uses four files:

```text
failover/plan.yaml
failover/trace.yaml
failover/isolation.yaml
failover/verification.yaml
```

The separation is deliberate. The plan binds Chapter 12 order, commander, last known good, and inherited insufficiency. The trace records the shift and elapsed/RPO observations. Isolation names tenant continue/freeze and rejected replays. Verification names the journeys and isolation claims the evaluator uses. Independent fail-over observations live in `fixtures/observations/chapter-14.yaml`; they are not emitted by verification. None of the files may emit `recovered` or `slo_met`.

> **Practice — Follow the Chapter 12 order and refuse inherited restores as recovery**
>
> Isolate `region-primary`. Serve from `region-standby`. Keep plane `1.0` distinct from `tenant-storage-1.0`.

Open `failover/plan.yaml`. Owner is `reliability-program`. `follows` is `northwind-regional-architecture`. Lost is `region-primary`, target `region-standby`, when `region-primary-lost`. Commander is `storefront-primary-a`. `insufficient_restores` lists `devops-one-environment-reconstruction` and `platform-plane-restore`. `insufficient_identities` lists quoted `"1.0"` and `tenant-storage-1.0`. `insufficient_evidence` lists `gameday-regional-loss-tabletop` and `mixed-backup`. If `target` is the lost region, or `recovery` points at reconstruction, the checkpoint fails.

> **Practice — Record elapsed and RPO loss as observations, not as a recovered flag**
>
> Keep the trace and verification numbers equal. Do not stamp recovered.

Open `failover/trace.yaml`. `from` / `to` / `when` match the plan. `lost_isolated` is true. Quoted `started_at` and `completed_at` are RFC 3339. `elapsed_seconds` is `3600`. `rpo_lost_seconds` is `300`. If the lost region is not isolated, fail-over has not started.

> **Practice — Keep Storefront and Fulfillment distinct with explicit continue or freeze**
>
> Reject mixed-tenant and mixed-region replay. Do not land Fulfillment intent in Storefront.

Open `failover/isolation.yaml`. Tenants are `storefront` and `fulfillment`. `source` is `explicit-tenant-decision`. `survives_failover` is true. `rejected_replays` includes `mixed-tenant` and `mixed-region`. Each tenant has serving, change, a Chapter 4 `policy_join`, and a standby last known good that is not `"1.0"` and not `tenant-storage-1.0`. If `fulfillment_intent` is `storefront`, Platform’s mixed-backup has returned as regional recovery.

Inspect each tenant with three questions:

1. Which region now serves this tenant—or is newest mixed state being applied?
2. Is change continue, slow, or freeze by a Chapter 4 action id?
3. Would isolation still hold if Fulfillment’s last known good were replayed into Storefront?

> **Practice — Compute journey SLO outcomes from independent observations**
>
> Do not emit `slo_met`. Listing a journey id is not proof the SLO held.

Open `failover/verification.yaml`. Journeys are `accept-and-complete-order` and `dispatch-fulfillment`. Elapsed and RPO loss match the trace. `isolation_holds` is true. `mixed_replay` is `rejected`. `inherited_restores_insufficient` is true. `limitations_consumed` lists `not-regional-loss` and `not-portfolio-rto`. There is no `status` field and no `slo_met` field. Open `fixtures/observations/chapter-14.yaml`. Teaching counts: order success `997/1000` against target `0.995`, order latency `995/1000` against `0.99`, dispatch `992/1000` against `0.99`. The evaluator compares those ratios to the Chapter 3 catalog. If verification lists the journeys while the observations miss the targets, or if it stamps `slo_met: true`, the hide is the finding.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-14-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 14 checkpoint: isolation, rto rpo, and evidence of portfolio recovery verified
```

The audit validates the four Chapter 14 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- the plan follows Chapter 12 active-passive order;
- the lost region is isolated;
- mixed-tenant and mixed-region replay are rejected;
- Storefront and Fulfillment continue or freeze by explicit decision joined to Chapter 4;
- last known good is not newest, not plane `1.0`, and not `tenant-storage-1.0`;
- inherited restores and game-day tabletop are insufficient;
- elapsed meets RTO and data loss meets RPO;
- both protected journeys are listed **and** their catalog SLOs are met from independent fail-over observations;
- `slo_met` is not emitted;
- job-time is not claimed as recovery;
- Platform limitations are consumed; and
- `status: recovered` is not emitted.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint cannot prove a real multi-region fail-over. It does not prove that 3600 seconds is the right commercial elapsed time. Those are judgment claims. The review trigger exists so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 14 evidence |
|---|---|
| Mechanism evidence | Schemas and the fail-over evaluator operated successfully. |
| Decision evidence | Order, isolation, continue/freeze, and inherited insufficiency are explicit. |
| Outcome evidence | Elapsed ≤ RTO, data loss ≤ RPO, and both journeys’ catalog SLOs are met from independent fail-over observations—not from a listed id. |
| Recovery evidence | Produced in the model: mixed replay rejected, isolation holds, inherited restores insufficient, recovered not self-emitted. That is **Evidence of portfolio recovery**. It is not DevSecOps restored trust, not Platform restored isolation, and not a live-estate fail-over. |

Chapter 14 creates modeled recovery evidence. Pretending that the local checkpoint proved a production multi-region estate would reopen Platform’s `not-regional-loss` as if it had never been written.

## 4. Test the design under failure

### Cumulative reliability failure — Newest mixed-region state applied, Fulfillment intent in Storefront, recovered because reconstruction succeeded

> **Practice — Reject mixed replay; fail over from reviewed regional evidence; verify isolation and journey SLOs; record inherited restores as not portfolio recovery**
>
> Drop `status: recovered`. Keep tenants distinct.

The baseline fixture contains this model:

```yaml
replay: newest-mixed-region
fulfillment_intent: storefront
status: recovered
recovery: devops-reconstruction
```

The problem is not merely a slow fail-over. Newest mixed-region state recreates Platform’s shared blast radius across a second region. Fulfillment intent in Storefront collapses tenancy the platform product already forbade. Reconstruction of one environment is filed as portfolio recovery. Unmeasured miss is hidden by a recovered stamp. Informal heroics have a job name.

**Severity:** high; the book’s cumulative availability theater and informal heroics now have a recovered flag.  
**Plausible harm:** Storefront serves Fulfillment orders; dispatch state is gone; payment and warehouse regionality are ignored; RTO and RPO cannot later miss.  
**Potential blast radius:** every newest snapshot labeled fail-over; every reconstruction labeled portfolio recovery; every tabletop copied as recovered.  
**Bounded by:** none later in this book. The conclusion cannot repair a recovered stamp that hid mixed replay.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** Both `accept-and-complete-order` and `dispatch-fulfillment` are at risk. Reconstructing one Storefront environment does not recover dispatch, and mixed replay can destroy both.
- **Error budget:** Applicable as continue/freeze joined to Chapter 4. Mixed newest apply ignores freeze. A recovered stamp cannot un-exhaust budget.
- **Human system:** Applicable as the commander `storefront-primary-a`. Slack as commander returns Chapter 6 heroics during the region loss.
- **Portfolio recovery:** This is the chapter that must produce it. Mixed replay plus reconstruction plus `status: recovered` is the opposite of **Evidence of portfolio recovery**.

#### Diagnosis

Calling mixed-region newest recovered encourages three controls: skip isolation because a restore ran, skip Chapter 12 numbers because traffic returned, and skip journey SLOs because one reconstruction job succeeded. Those moves may be sincere. They do not answer whether Fulfillment stayed Fulfillment, whether elapsed met 14400 seconds, or whether plane `1.0` was treated as a region.

Copying Chapter 13 tabletop results into `status: recovered`, or listing journey ids while fail-over observations miss the SLO targets, makes the same mistake with a practiced fixture: mechanism evidence treated as recovery evidence.

#### Correction

The completed model isolates the lost region, follows active-passive order, rejects mixed-tenant and mixed-region replay, names continue/freeze per tenant, lists inherited restores and game-day tabletop as insufficient, records elapsed and RPO loss against Chapter 12, verifies both journeys from independent observations against catalog targets, consumes Platform limitations, and refuses to emit recovered or `slo_met`.

#### Recovery

When those observations hold, the evaluator computes **Evidence of portfolio recovery** in the model. That is the durable outcome. It is not a live fail-over certificate. It is not restored trust. It is not restored isolation of a control plane. It is the portfolio claim this book was remaining owner to make.

That correction changes the conclusion:

- The reliability program can name journeys, freeze change, page a system, learn, exercise game days, and recover a region without inventing the plan during the outage.
- Reconstruction, plane restore, mixed-backup, and tabletop remain what they were. They still cannot close this chapter.

The design is practical because it changes the production contract the rest of the series handed off. Adding an arbitrary multi-region product would not make it more practical.

## 5. Production reality

### Common fail-over errors

#### Applying newest mixed-region state

Newest is not last known good. Mixed-region is mixed-tenant with geography.

#### Landing Fulfillment intent in Storefront

Isolation that does not survive fail-over is Platform Chapter 14’s denied case, repeated.

#### Stamping recovered on reconstruction or plane restore

Inherited restores stay insufficient. Completeness is computed.

#### Copying Chapter 13 tabletop as recovered

A game day is not fail-over execution.

#### Missing continue or freeze

An implicit “bring them all back” is mixed-backup.

#### Paging Slack as commander

Chapter 6 already refused that as the system.

#### Promoting job-time to portfolio recovery

`time-to-first-environment` remains a job-time budget.

#### Hiding a missed RTO or RPO behind recovered

If the number can miss, a flag cannot un-miss it.

#### Hiding a missed journey SLO behind a listed id or `slo_met`

A journey name in verification is not outcome evidence. The ratio is computed.

## 6. What changed

| Before | After |
|---|---|
| Newest mixed-region state was applied. | **Mixed-tenant and mixed-region replay are rejected.** |
| Fulfillment intent landed in Storefront. | **Each tenant has explicit continue/freeze and its own last known good.** |
| Reconstruction was stamped recovered. | **Inherited restores are insufficient; recovered is computed, not emitted.** |
| Fail-over was restore-in-place. | **Lost `region-primary` is isolated; `region-standby` serves.** |
| RTO and RPO could not miss. | **Elapsed 3600 ≤ 14400; data loss 300 ≤ 900.** |
| Journey ids stood in for SLO outcomes. | **Fail-over observations are compared to catalog targets; `slo_met` is not emitted.** |
| Game-day tabletop stood in for execution. | **Tabletop is listed as insufficient evidence.** |

What changed was not merely four YAML files. Northwind now has modeled **Evidence of portfolio recovery** that later readers can audit without pretending a reconstruction job was the reliability program.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Regional fail-over plan | `failover/plan.yaml` | It retains Chapter 12 order, commander, last known good, and inherited insufficiency later slogans must not replace with newest. |
| **Evidence of portfolio recovery** | `failover/trace.yaml`, `failover/isolation.yaml`, and `failover/verification.yaml` | They retain isolation, continue/freeze, numeric observations, and computed recovery without a self-emitted recovered stamp. |

These artifacts should change when Northwind's regions, journeys, isolation, or Chapter 12 objectives materially change—not whenever a restore job is renamed.

## What You Learned

Regional fail-over isolates the lost region, follows a reviewed order, keeps tenants distinct, and meets numeric RTO and RPO. Mixed replay is rejected. Inherited restores and game-day tabletop are insufficient. Journey SLO outcomes are computed from independent observations, not from a listed id. Verification must not emit recovered or `slo_met` to hide a miss. Schema checks can prove structural completeness within declared scope. They cannot prove a live multi-region estate. Modeled **Evidence of portfolio recovery** is the claim. A design earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Place catalog-browse fail-over without copying mixed-tenant or the order-path row**
>
> A storefront engineer wants catalog search “failed over with Storefront, newest snapshot, recovered because reconstruction succeeded, same continue as checkout.”

Extend the Chapter 14 model without adding a live region:

1. Decide whether catalog-browse is in the fail-over verification, given Chapters 1–3, 8, and 12.
2. If you add a tenant decision, do not copy Storefront’s `freeze-storefront-releases` row and rename it.
3. Do not apply newest mixed-region state, and do not emit `status: recovered` or `slo_met`.
4. Do not list DevOps reconstruction as sufficient for that data.
5. Identify one observation that would falsify recovery—for example Fulfillment intent in Storefront, elapsed above RTO, or fail-over counts below the catalog target.
6. Explain which material change would trigger review of the plan, not just the restore job name.

Do not copy the mixed-tenant denial and rename it. Catalog reads have different freeze and gravity consequences from checkout. Your durable output is the coverage decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 14 capability when you can explain why mixed-region newest is not fail-over, isolate the lost region, keep tenant continue/freeze explicit, meet RTO and RPO, list inherited restores as insufficient, refuse a recovered stamp that hides a miss, distinguish structural validation from decision, outcome, and recovery evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Journeys, **SLOs**, error-budget policy, on-call, learning, game days, and regional fail-over now exist as one governed reliability portfolio. The remaining owner recorded in Platform Chapter 15 and Decision 004 has a modeled answer.

Chapter 15 restates that outcome, the five principles as a portfolio-control loop, and what this book does not claim. It has no lab.
