# Allocate Quota, Cost, and Capacity Across Tenants

Chapter 10 made job time the product indicator. Fulfillment’s time-to-first-environment is sampled. Adoption cannot hide a longer wait. Environments and the control plane still share an unowned pool. Chapter 3 already named `cluster-capacity-pool` and denied `unlimited-burst-into-peer-quota`. Chapter 6 already bound each lease on that pool. Isolation labels exist. Floors do not. A Fulfillment burst can still consume Storefront’s environment floor, and a cheaper shared bill can call that success.

The production question is now:

> How does the platform allocate scarce capacity so one tenant cannot starve another, and what unit cost is honest?

A lower shared bill hides Fulfillment starvation, or chargeback without quality gates rewards cheap broken environments. This chapter records tenant floors and ceilings on the same pool, platform units with quality gates, and showback that cannot count a starved burst as a useful unit. Storefront’s floor is not Fulfillment’s headroom. A cheaper bill is not a platform-product **SLI (Service Level Indicator)**.

## 1. A burst that still eats the other floor

A weak record says:

```yaml
pool: cluster-capacity-pool
capacity: 32
tenants: [storefront, fulfillment]
showback:
  - tenant: fulfillment
    unit: environment-hour
    usage: 24
    billed_units: 24
  - tenant: fulfillment
    unit: order_success_ratio
    billed_units: 1
```

It does not identify a floor, a ceiling, a quality gate, or the Chapter 6 lease commitment the floor must cover. Isolation labels may still say Storefront cannot be starved below a floor. There is no floor. Fulfillment uses 24 of 32. Storefront’s leases still commit 12. Eight remain. `32 - 24 = 8`, and `8 < 12`. Storefront’s order-success ratio can stay green through that squeeze. The inherited observability contract already tracks `order_success_ratio`. Chapter 10 already refused it as product evidence. Billing it as a platform unit is the same borrow, now in currency.

Work from the lab working tree using the How to Use This Book procedure. From the Platform lab root, run the Chapter 11 baseline:

```bash
make chapter-11-baseline
```

The command succeeds when it detects the intended unsafe allocation:

```text
chapter 11 baseline: fulfillment burst starving storefront floor correctly detected
```

The fixture lists both tenants on `cluster-capacity-pool` without floors, lets Fulfillment use 24 environment-hours, bills that burst as useful, and treats Storefront order-success as a cost unit. Leases exist. The pool is still unowned.

That residual drives the chapter.

## 2. The production model: floors on the pool you already named

> *Theory — Quota, showback, and useful platform units*
>
> This model enables Storefront and Fulfillment to finish `obtain-bounded-environment` on a shared pool without one tenant’s burst becoming the other’s incident, and without treating a cheaper bill as job completion.

### The pool is `cluster-capacity-pool`, not a new bill

Chapter 3 already declared the shared surface: `cluster-capacity-pool`, mode `shared-quota-pool`, tenants may not inherit `unlimited-burst-into-peer-quota`. Chapter 6 already used that id as the environment product’s quota pool and as each lease bound. This chapter does not rename it to make showback look like **FinOps (Financial Operations)** of the order path. Inherited DevOps useful-unit thinking applies here to the platform product: count environment-hours and successful provisions that passed a quality gate. Do not reteach Storefront’s cost of serving orders.

A **shared-nothing** platform would give each tenant its own capacity account. Northwind chose a shared pool. The pool is therefore a product with an owner, floors, ceilings, and units. Unlimited burst is not that product. It is the noisy neighbor Chapter 3 already denied, now running as a cheaper bill.

Do not invent a second pool so storage class or a control-plane slice looks like quota. The plane shares this pool. Tenants are metered on it.

### A floor is a lease commitment; a ceiling must leave the other floor

Storefront’s leases commit `4 + 8 = 12` units on `storefront-nonprod` and `storefront-prod`. Fulfillment’s leases commit the same split on `fulfillment-nonprod` and `fulfillment-prod`. Those bounds are Chapter 6’s product check against unlimited lease size. They are not yet a floor the other tenant must leave behind.

This chapter sets:

| Tenant | Floor | Ceiling |
|---|---:|---:|
| storefront | 12 | 20 |
| fulfillment | 12 | 20 |

Pool capacity is 32. `12 + 20 = 32`. A ceiling that cannot be used without taking the peer’s floor is not a ceiling. It is unlimited burst with extra YAML. `floor_peer + ceiling_self <= capacity` is the allocation invariant. Usage must stay at or under the ceiling. Remaining capacity after one tenant’s usage must still cover the other’s floor. Completeness is computed. A quota file cannot emit `status: healthy` to hide a missing floor.

**Best Practice:** Set each floor at least as high as that tenant’s Chapter 6 lease sum. A floor below the lease commitment makes the lease ornamental.

**Production Practice:** Ceilings may sum to more than capacity. `20 + 20 = 40`, and `40 > 32`. That is a guaranteed floor plus an oversubscribed best-effort ceiling, not a latent overflow. The runtime check—remaining capacity after one tenant’s usage still covers the peer floor—is what prevents both tenants bursting at once from starving either floor.

**Production Practice:** Isolation is a quota invariant joined to Chapter 3. This chapter loads quota `denied_inheritance`. A burst that leaves a peer below its floor—or below its lease sum when the floor is missing—fails `unlimited-burst-into-peer-quota`. Clearing that denial stops the inheritance error. The numeric starvation check still runs. They are not the same check.

### Showback counts useful units, not a cheaper shared average

Two units are retained:

| Unit | Meters | Quality gate |
|---|---|---|
| `environment-hour` | `cluster-capacity-pool` | `lease-bound-on-pool` |
| `successful-provision` | `obtain-bounded-environment` | `time-to-first-environment-sampled` |

An environment-hour that is not bound on the Chapter 6 pool is not a useful unit. A successful provision without a Chapter 10 `time-to-first-environment` sample is a namespace create, not job completion. Billing a starved burst as `quality_gate_passed: true` is Goodhart in currency: Fulfillment looks cheap and busy while Storefront’s floor is gone.

Chapter 10’s non-metric register still applies. `category: vanity` ids are not units. `category: tenant-workload` ids—including `order_success_ratio` and `order_latency`—are not units. Chapter 1 later proofs are job-time SLIs, not cost units. A cheaper bill must not replace `time-to-first-environment`.

Do not onboard a fleet here. Chapter 12 will change contracts against this allocation. This chapter must already refuse to treat a burst through Storefront’s floor as headroom.

## 3. Allocate the pool as a product

The completed Chapter 11 model uses three files:

```text
quota/tenants.yaml
quota/units.yaml
quota/showback.yaml
```

The separation is deliberate. The policy names the pool, capacity, floors, and ceilings. Units name what is metered and which gate makes a unit useful. Showback is observation. The evaluator joins them to Chapter 3 tenants, isolation, and sharing, Chapter 6 leases and environment product, and Chapter 10 indicators, samples, and non-metric categories.

> **Practice — Bind floors to the Chapter 3 pool and Chapter 6 lease sums**
>
> Consume `cluster-capacity-pool` rather than inventing a billing account name.

Open `quota/tenants.yaml`:

```yaml
owner: platform-team
pool: cluster-capacity-pool
capacity: 32
tenants:
  - tenant: storefront
    floor: 12
    ceiling: 20
  - tenant: fulfillment
    floor: 12
    ceiling: 20
```

The evaluator loads Chapter 3 sharing and Chapter 6 `quota_pool`. It fails if the pool is renamed. It fails if a floor is below that tenant’s lease sum. It fails if `floor_peer + ceiling_self` exceeds capacity.

> **Practice — Declare platform units with quality gates**
>
> Environment-hours meter the pool. Successful provisions meter `obtain-bounded-environment`. Neither meters Storefront orders.

Open `quota/units.yaml`. `environment-hour` meters `cluster-capacity-pool` with gate `lease-bound-on-pool`. `successful-provision` meters `obtain-bounded-environment` with gate `time-to-first-environment-sampled`. The evaluator joins Chapter 10 samples and non-metrics. Tagging `order_success_ratio` as a unit fails as tenant workload, not as vanity.

> **Practice — Bill only units that passed the gate**
>
> A starved burst is not a successful environment-hour. A provision without a job-time sample is not a successful provision.

Open `quota/showback.yaml`. Storefront and Fulfillment each show 12 environment-hours, matching the lease sum, billed 12, gate passed. Fulfillment shows one successful provision because Chapter 10 sampled Fulfillment’s time-to-first-environment. There is no Storefront successful-provision row, because that sample does not exist. There is no adoption row, because adoption is not a unit.

The lab does not read a real cloud bill or scheduler. Completeness is whether floors cover lease commitments, ceilings leave the other floor, and showback cannot count a starved burst or a borrowed order metric as a useful unit.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-11-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 11 checkpoint: tenant floors, ceilings, and quality-gated showback verified
```

The audit validates the three Chapter 11 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- policy owner is a living Chapter 1 user;
- the pool is Chapter 3 `cluster-capacity-pool` and matches the Chapter 6 environment product;
- every Chapter 3 tenant has a floor and a ceiling;
- each floor covers that tenant’s Chapter 6 lease sum;
- a ceiling cannot be used without leaving the peer floor;
- required units are `environment-hour` and `successful-provision` with the declared gates;
- vanity, tenant-workload, and job-proof ids are not units;
- showback bills only gated usage; and
- remaining capacity after one tenant’s usage still covers the other’s floor.

The expected pool, units, and denied burst id live in a separate checkpoint file. An allocation under test does not emit its own passing grade.

The checkpoint does not prove that a real cluster throttled Fulfillment, that a real bill charged environment-hours, or that 32 is the right pool size for a real company. Those remain claims a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 11 evidence |
|---|---|
| Mechanism evidence | Schemas and the quota-showback evaluator operated successfully. |
| Decision evidence | Pool, floors, ceilings, units, quality gates, and non-unit refusals are explicit. |
| Outcome evidence | Fulfillment and Storefront have computed usage at the lease sum. That is not proof a scheduler reserved those units. |
| Recovery evidence | Not produced. A denied burst is a quota invariant, not restored isolation after a live noisy-neighbor outage. |

Chapter 11 produces mechanism, decision, and limited outcome evidence for allocation on an existing pool. Pretending the local checkpoint proves a cloud bill would weaken Chapter 12’s fleet change and Chapter 14’s bounded recovery.

## 4. Test the design under failure

### Connected consequence — Fulfillment burst consumes Storefront's environment floor after isolation labels exist but quota does not

> **Practice — Fail the burst that bills Storefront’s floor as Fulfillment headroom**
>
> Inject Fulfillment environment-hour usage of 24 onto the completed showback and refuse the ceiling overflow, the starved floor, and the useful-unit bill.

The completed allocation is healthy. The failure command does not rewrite it. It injects the burst against that snapshot:

```bash
make chapter-11-failure
```

Expected output:

```text
chapter 11 failure: fulfillment burst consuming storefront floor correctly rejected
```

The injected record is:

```yaml
- tenant: fulfillment
  unit: environment-hour
  usage: 24
  billed_units: 24
  quality_gate_passed: true
```

Storefront stays at 12. Fulfillment’s successful-provision sample stays at 1. Floors stay 12. Ceilings stay 20. The baseline’s missing floors and borrowed order-success unit are not required for this failure. Burst can appear after the policy already looks complete. `24 > 20`. `32 - 24 = 8`. `8 < 12`. The arithmetic is the story.

**Severity:** high; every later fleet, support, and recovery conversation will optimize a cheaper shared bill instead of Storefront’s reserved floor.  
**Plausible harm:** Fulfillment scales; Storefront’s environments cannot hold their lease; wait returns as “the cluster is busy”; leadership funds the lower unit cost.  
**Potential blast radius:** both application tenants and `cluster-capacity-pool`; Storefront’s order path is no longer a separate capacity domain.  
**Bounded by:** Chapter 3 quota denial, Chapter 6 lease sums, Chapter 10 job-time samples, and the non-metric register. None of those repair a showback file that still bills 24.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence.

#### Platform questions

- **User and job:** Storefront and Fulfillment must finish `obtain-bounded-environment`. A Fulfillment burst to 24 is not that job for Storefront. It is a noisy neighbor substituting for a floor.
- **Isolation:** The boundary is Chapter 3’s quota dimension plus this policy: `cluster-capacity-pool` as shared-quota-pool, floor 12, ceiling 20, and no `unlimited-burst-into-peer-quota`. Fulfillment’s blast radius must stop before Storefront’s floor. This is not a new tenancy model. It is the quota check Chapter 3 deferred and Chapter 6 could only bound per lease.
- **Contract and exit:** The contract is the quota policy and the unit catalog. Teams do not leave it the way they leave a paved-road scaffold. A burst is not a Chapter 5 exit, not a Chapter 7 version bump, not a Chapter 9 exception, and not a Chapter 10 non-metric demotion. A ceiling is not an exception to a floor.
- **Platform-product evidence:** A lower shared bill is not proof the product works. Required proof is usage at or under ceiling that still leaves the peer floor, billed only when the quality gate passed. This is a platform-product SLI input, not a portfolio **SLO (Service Level Objective)**.

#### Diagnosis

Calling 24 environment-hours “headroom” encourages the same unofficial path Chapter 3 interrupted: Fulfillment is blocked, someone shares the pool, Storefront’s reserved units move, and the order path becomes a noisy neighbor. Isolation labels stay green. The lease still says 12. Remaining capacity is 8. Showback then bills the burst as a useful unit, so the cheaper average looks like efficiency.

The missing floor makes Chapter 3’s starvation blast-radius statement ornamental. The missing ceiling makes Chapter 6’s lease bound a per-namespace cap with no peer. Billing `order_success_ratio` makes Chapter 10’s tenant-workload refusal a memory. Billing a starved burst makes useful-unit thinking a slogan.

#### Correction

The completed model does not let Fulfillment use 24. Usage stays at the lease sum until a ceiling that still leaves Storefront’s 12 is granted and observed. Showback does not count a starved burst as a useful environment-hour. Inherited order metrics stay non-metrics, not units. Completeness is computed. The failure command proves the check still fails when only Fulfillment’s environment-hour row moves from 12 to 24.

This failure is a quota-invariant failure. It is not a runtime plane recovery. Do not call the denied burst **Evidence of restored isolation**. Nothing tenant-runtime was restored from a live noisy-neighbor outage. The product stopped treating Storefront’s floor as Fulfillment headroom.

That correction changes later decisions:

- Chapter 12 must not onboard or upgrade a tenant by bursting through another tenant’s floor.
- Chapter 13 must not close a capacity ticket because the shared unit cost moved down.
- Chapter 14 must recover `cluster-capacity-pool` without replaying one tenant’s burst into another’s floor.
- Fleet change may not replace floors with a cheaper bill or with Chapter 10 adoption.

The design is practical because the failed burst check is the product. Adding an arbitrary cloud-bill import would not make it more practical.

## 5. Production reality

### Common quota errors

#### Sharing a pool with labels and no floors

Chapter 3 already denied unlimited burst. Labels without numbers are still a shared cluster.

#### Setting a ceiling that cannot leave the peer floor

`floor_peer + ceiling_self > capacity` is unlimited burst with a friendlier name. Summing both ceilings above capacity is the opposite case: oversubscription is allowed. Do not “fix” `20 + 20 > 32` by shrinking both ceilings until they statically reserve the whole pool. That removes burst. The runtime check is what keeps both bursts from happening at once.

#### Billing failed or starved usage as a useful unit

Inherited useful-unit thinking does not mean “count every hour.” It means count hours that did not take another tenant’s job.

#### Borrowing Storefront order-success as platform cost

Chapter 10 already refused those outcomes as product indicators. They are tenant workload, not showback.

#### Replacing time-to-first-environment with a cheaper bill

Chapter 10’s later proof remains the job SLI. Showback is not allowed to demote it.

#### Building fleet onboarding in this chapter

Allocate the pool. Leave cohorts, freezes, and deprecation to Chapter 12. Do not read a real cloud bill.

## 6. What changed

| Before | After |
|---|---|
| Fulfillment used 24 of 32 and left Storefront 8 against a 12-unit lease. | **Ceiling overflow and peer-floor starvation fail the quota invariant.** |
| Isolation labels existed and floors did not. | **Each Chapter 3 tenant has a floor covering its Chapter 6 lease sum.** |
| A cheaper shared bill counted the burst as useful. | **Starved burst cannot pass the environment-hour quality gate as billed usage.** |
| Storefront order-success stood in for platform cost. | **Tenant-workload ids are refused as units.** |
| A valid schema could appear to prove a cloud bill. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has an allocation later fleet, support, and recovery chapters can use without treating a cheaper shared bill as Storefront’s reserved floor.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Tenant quota policy | `quota/tenants.yaml` | It retains `cluster-capacity-pool`, floors, and ceilings later fleet and recovery chapters must not rename or burst through. |
| Platform unit-cost model | `quota/units.yaml` and `quota/showback.yaml` | They retain quality-gated environment-hours and successful provisions, and the refusal to bill vanity, tenant workload, or starved burst as useful units. |

These artifacts should change when Northwind’s tenant set, lease commitments, or Chapter 10 job proofs materially change—not whenever a billing dashboard theme is restyled.

## What You Learned

Quota is floors and ceilings on the pool Chapter 3 already named, not a new account and not a cheaper average. A Fulfillment burst to 24 that leaves Storefront 8 against a 12-unit floor is a noisy neighbor, not headroom. Schema checks can prove structural completeness within declared scope. They cannot read a real cloud bill. A design earns its place when Storefront’s floor still has 12 after Fulfillment runs, and when 24 billed environment-hours cannot hide that `8 < 12`.

### Prove It

> **Independent Practice — Meter a read-only analytics path without copying the 24-unit burst**
>
> A data-analytics team needs bounded read environments on the same pool. Leadership will ask for a lower analytics unit cost after “bursting into unused Storefront capacity.”

Extend the Chapter 11 model without adding fleet onboarding yet:

1. Decide whether analytics is a new Chapter 3 tenant—or still not a platform tenant—and which job, if any, it finishes.
2. Name a floor that covers its lease commitment, and a ceiling that still leaves Storefront’s 12.
3. State whether `order_latency` or `time-to-first-environment` may be reused as an analytics cost unit, given Chapter 10’s register.
4. Choose a sample that would falsify “analytics can burst safely”—for example analytics environment-hours moving to a number that leaves Storefront remaining capacity below 12.
5. Identify which quality gate that sample must fail, and which owner remains accountable.
6. Explain which material change would trigger review of the quota policy, not just one showback tile.

Do not copy the Fulfillment 24 / Storefront 8 row and rename it. Analytics has different wait, isolation, and job-proof consequences than `obtain-bounded-environment` for `fulfillment-api`. Your durable output is the floor-ceiling-and-unit decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 11 capability when you can explain why a cheaper shared bill is not Storefront’s floor, trace each tenant to a Chapter 6 lease sum and a Chapter 3 pool id, describe evidence that would falsify the allocation, distinguish structural validation from decision and outcome evidence, and explain what the baseline, checkpoint, and failure command do and do not prove.

## Next

Capacity is allocated, but the fleet still cannot upgrade or leave old contracts. Two tenants consume the platform. Contract v1 must be retired. A new paved-road version is ready. Forced upgrades break tenants. Eternal v1 support becomes a second unofficial platform.

Chapter 12 runs fleet lifecycle: onboard, upgrade, and deprecate, so Fulfillment can join and leave a contract version without an outage lottery.
