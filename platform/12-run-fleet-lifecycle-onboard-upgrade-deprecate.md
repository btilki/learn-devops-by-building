# Run Fleet Lifecycle: Onboard, Upgrade, Deprecate

Chapter 11 reserved Storefront’s floor. Capacity is allocated. Two tenants already consume the platform. Contract `1.0` must be retired. A new version is ready: `tenant-storage` `2.0` renames `class` to `sku` with a migration note. That is the Chapter 7 bump done as a bump. It is not yet a fleet. Forced upgrades break tenants. Eternal `1.0` support becomes a second unofficial platform.

The production question is now:

> How do tenants join, absorb a platform upgrade, and leave an old contract without an outage lottery?

This chapter records onboarding without cluster-admin, a freeze window, progressive cohorts, rollback to last known good contract `1.0`, and a deprecation window that cannot close while Fulfillment still legally sends `class`. Storefront can move first. Fulfillment’s `1.0` binding stays legal until migration evidence exists. Applying `2.0` to every tenant at once is the cumulative product failure continuing under a friendlier name.

## 1. Version 2 for everyone, while v1 was still legal

A weak record says:

```yaml
granted_role: cluster-admin
cohorts:
  - tenants: [storefront, fulfillment]
    status: complete
applied_version: "2.0"   # fulfillment
evidence: pending
window_ends_at: "2026-08-15T12:00:00Z"
remaining_tenants: [fulfillment]
```

It does not identify a freeze, a Storefront-then-Fulfillment cohort, rollback to `1.0`, or an open deprecation window. “Just cut over” may ship `sku` this week. Fulfillment still sends `class`. Chapter 7 already refused that rename on a single version. Doing it to the whole fleet in one step is the same break, now with a schedule. Cluster-admin so onboarding works is Chapter 8’s residual wearing a lifecycle coat.

Work from the lab working tree using the Chapter 0 procedure. From the Platform lab root, run the Chapter 12 baseline:

```bash
make chapter-12-baseline
```

The command succeeds when it detects the intended unsafe fleet:

```text
chapter 12 baseline: all-at-once v2 apply breaking fulfillment v1 correctly detected
```

The fixture onboards Fulfillment with `cluster-admin`, applies `tenant-storage` `2.0` to both tenants in one cohort, skips freeze and rollback, rewrites source, bills the apply without migration evidence, and closes `1.0` while Fulfillment remains. Quota exists. The cutover is still an outage lottery.

That residual drives the chapter.

## 2. The production model: a bump is not a blast radius

> *Theory — Fleet lifecycle*
>
> This model enables Fulfillment to finish `ship-on-paved-road` on a still-legal `1.0` binding while Storefront absorbs `2.0`, without inheriting cluster-admin or treating a forced cutover as a version bump.

### Onboarding is a tenant-operator join, not a plane token

Fulfillment is already a Chapter 3 tenant with a Chapter 4 catalog entry, a Chapter 6 lease, and a Chapter 11 floor. Fleet onboarding records that join as complete: `fulfillment-api` on `fulfillment-nonprod`, paved road `northwind-production-path`, `granted_role: tenant-operator`, `quota_floor_respected: true`. Cluster-admin is not onboarding. Chapter 8 already refused it so onboarding works. This chapter loads that refusal. A fleet that grants `cluster-admin` to finish the join fails.

Do not burst through Storefront’s floor to make room for the new tenant. Chapter 11 already failed that burst.

### A fleet upgrade consumes a Chapter 7 bump; it does not replace it

`tenant-storage` `2.0` exists in Chapter 7 with `sku` and `size-gb`, and compatibility records `class` → `sku` against version `2.0` with note `class-becomes-sku`. That is the leaving act Chapter 7 named: a contract version bump. The fleet act is how that bump reaches tenants: freeze, cohort, rollback, migration evidence.

They are not the same act:

| Act | Chapter | What it is |
|---|---|---|
| Supported exit | 5 | Leave the scaffold; remaining guardrails stay |
| Contract version bump | 7 | Leave a tenant-visible API version with a migration note |
| Guardrail exception | 9 | Temporary deviation; expiry lives on the inherited DevSecOps record |
| Non-metric demotion | 10 | Vanity leaves the indicator set |
| Fleet upgrade | 12 | Roll a Chapter 7 bump across tenants with freeze, cohort, and rollback |

A fleet upgrade is not a Chapter 5 exit. Teams do not leave the paved road by absorbing `2.0`. A freeze is not a Chapter 9 exception. Rollback is not a burst through a floor. Eternal `1.0` after the window, with no exception, is a second unofficial platform.

**Best Practice:** Split plane version from contract version. Chapter 8’s last known good is plane `1.0` after a failed plane upgrade to `1.1`. This chapter’s last known good is contract `tenant-storage` `1.0`. Do not collapse them because both say `1.0`.

**Production Practice:** Isolation is a fleet invariant joined to Chapter 3 and Chapter 8. A cohort apply mutates one tenant. **GitOps (Git-based operations)** still forbids source rewrite. Clearing `controller_may_rewrite_source` stops the rewrite error. The all-at-once check still runs. They are not the same check.

### Freeze, cohort, then deprecate

Storefront moves first. Fulfillment stays on `1.0` and keeps sending `class`. The freeze is `2026-08-16T00:00:00Z` to `2026-08-23T00:00:00Z`. `as_of` is inside that window. Deprecation of `1.0` stays open until `2026-11-16T00:00:00Z` with `remaining_tenants: [fulfillment]`. Closing the window without an inherited exception binding fails. Applying `2.0` to Fulfillment with `evidence: pending` fails: still-legal `v1` broke.

**Production Practice:** Those dates are Northwind’s standing cadence, not a one-off. Seven days is Chapter 6’s `ttl_hours: 168`. `2026-11-16T00:00:00Z` is the same quarterly review already used for the Chapter 5 exit `review_at` and the Chapter 6 production-lease `expires_at`. A freeze is one TTL. A deprecation window is one quarter.

Rollback `last_known_good: "1.0"` must remain allowed. A complete result that already moved every tenant without evidence has no rollback. Completeness is computed. A fleet file cannot emit `status: healthy` to hide a missing freeze.

Do not invent support tickets here. Chapter 13 will change the platform through a reviewed subject. This chapter must already refuse an all-at-once apply.

## 3. Run the fleet as a product

The completed Chapter 12 model uses four files:

```text
fleet/onboarding.yaml
fleet/upgrades.yaml
fleet/deprecations.yaml
fleet/migrations.yaml
```

The separation is deliberate. Onboarding records the join. Upgrades name freeze, cohorts, and rollback. Deprecations name the window and who remains. Migrations are evidence. The evaluator joins them to Chapter 3 tenants, Chapter 4 systems, Chapter 5 paved road, Chapter 6 leases, Chapter 7 versions and catalog bindings, Chapter 8 subjects, Chapter 9 exception bindings, Chapter 11 quota, and the inherited GitOps interface.

> **Practice — Onboard Fulfillment without cluster-admin**
>
> Consume `tenant-operator`, the paved road, the lease, and the Chapter 11 floor rather than a plane token.

Open `fleet/onboarding.yaml`. Storefront and Fulfillment are `complete` with `granted_role: tenant-operator` and `quota_floor_respected: true`. The evaluator loads Chapter 8 subjects and fails `cluster-admin`. It loads Chapter 4 and fails an unknown system. It loads Chapter 11 and fails a join that does not respect the floor.

> **Practice — Freeze, then move one cohort**
>
> Storefront can complete `2.0`. Fulfillment’s cohort stays pending while `class` is still legal.

Open `fleet/upgrades.yaml`:

```yaml
capability: tenant-storage
from_version: "1.0"
to_version: "2.0"
freeze:
  starts_at: "2026-08-16T00:00:00Z"
  ends_at: "2026-08-23T00:00:00Z"
cohorts:
  - id: storefront-cohort
    tenants: [storefront]
    status: complete
  - id: fulfillment-cohort
    tenants: [fulfillment]
    status: pending
rollback:
  last_known_good: "1.0"
  allowed: true
result: in-progress
source_rewritten: false
```

Chapter 7 already admitted `2.0` as a version and Chapter 8 admitted it for Storefront’s reconcile. Fulfillment’s catalog binding and reconcile stay `1.0` with `class`. The evaluator fails a single cohort that lists every tenant as complete, a missing freeze, source rewrite, and rollback to `2.0`.

> **Practice — Keep 1.0 legal until migration evidence exists**
>
> A pending Fulfillment row is not failure. Applying `2.0` without evidence is.

Open `fleet/migrations.yaml` and `fleet/deprecations.yaml`. Storefront’s note is `class-becomes-sku`, `applied_version: "2.0"`, `evidence: complete`. Fulfillment’s applied version is still `1.0` with evidence pending. Deprecation of `1.0` is open. The window has not closed.

The lab does not upgrade a live fleet. Completeness is whether Fulfillment joined without cluster-admin, Storefront absorbed `2.0` inside a freeze, and `1.0` remains legal until evidence exists.

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
chapter 12 checkpoint: onboard, freeze, cohort, and deprecation window verified
```

The audit validates the four Chapter 12 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- onboarding owner is a living Chapter 1 user;
- every Chapter 3 tenant is onboarded as `tenant-operator` on the paved road with a lease and a respected floor;
- `tenant-storage` `2.0` exists as a Chapter 7 version, not an in-place rename of `1.0`;
- the upgrade has a freeze that covers `as_of`, two cohorts, and rollback to `1.0`;
- GitOps still forbids source rewrite;
- Storefront migration evidence is complete and Fulfillment’s `1.0` apply is still pending;
- deprecation of `1.0` stays open while Fulfillment remains; and
- a closed window with remaining tenants and no Chapter 9 exception binding fails.

The expected capability, forbidden roles, and `as_of` live in a separate checkpoint file. A fleet under test does not emit its own passing grade.

The checkpoint does not prove that a real cluster rolled a Deployment, that a real freeze stopped merges, or that 2.0 is the right next storage API. Those remain claims a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 12 evidence |
|---|---|
| Mechanism evidence | Schemas and the fleet-lifecycle evaluator operated successfully. |
| Decision evidence | Onboarding role, freeze, cohorts, rollback, deprecation window, and migration notes are explicit. |
| Outcome evidence | Storefront has a computed `2.0` apply. Fulfillment has a computed still-legal `1.0`. That is not proof a cluster changed. |
| Recovery evidence | Not produced. A denied all-at-once apply is a fleet invariant, not restored isolation after a live cutover outage. |

Chapter 12 produces mechanism, decision, and limited outcome evidence for lifecycle on existing contracts. Pretending the local checkpoint proves a live rolling upgrade would weaken Chapter 13’s change authority and Chapter 14’s bounded recovery.

## 4. Test the design under failure

### Cumulative product failure — Platform v2 is applied to all tenants at once; fulfillment's still-legal v1 contract breaks

> **Practice — Fail the cutover that applies 2.0 before Fulfillment’s class binding has a note**
>
> Inject a skipped freeze, both cohorts complete, and Fulfillment `applied_version: "2.0"` with pending evidence, and refuse the all-at-once apply.

The completed fleet is healthy. The failure command does not rewrite it. It injects the residual all-at-once case against that snapshot:

```bash
make chapter-12-failure
```

Expected output:

```text
chapter 12 failure: all-at-once v2 apply breaking fulfillment v1 correctly rejected
```

The injected record is:

```yaml
freeze: {}
result: complete
cohorts:
  - tenants: [storefront]
    status: complete
  - tenants: [fulfillment]
    status: complete
# fulfillment-storage-2-0
applied_version: "2.0"
evidence: pending
```

Onboarding stays `tenant-operator`. Deprecation stays open. Storefront’s completed migration stays `2.0` with evidence. The baseline’s cluster-admin join, source rewrite, and closed window are not required for this failure. An all-at-once apply can appear after the policy already looks complete. Fulfillment still had a legal `1.0` `class` binding. `2.0` expects `sku`. Pending evidence means the note was not executed. Last known good was not restored.

**Severity:** high; every later support and recovery conversation will optimize a fleet-wide cutover instead of a still-legal tenant contract.  
**Plausible harm:** Fulfillment keep-alive traffic sends `class`; storage `2.0` rejects it; warehouse effects stop while Storefront’s `sku` path looks healthy.  
**Potential blast radius:** both application tenants and `tenant-storage`; Fulfillment’s still-legal `1.0` is no longer a separate compatibility domain.  
**Bounded by:** Chapter 7 version `2.0` and migration note, Chapter 8 admission and last known good, Chapter 9 exception bindings, and inherited GitOps. None of those repair a complete result that already moved every tenant.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence.

#### Platform questions

- **User and job:** Fulfillment must finish `ship-on-paved-road` on a contract it can still send. An all-at-once `2.0` apply is not that job. It is a cutover substituting for a cohort.
- **Isolation:** The boundary is Chapter 3’s tenant plus this cohort: Storefront can complete `2.0` without Fulfillment absorbing `sku` in the same step. Fulfillment’s blast radius must stop at Fulfillment. This is not a new tenancy model. It is the compatibility window Chapter 7 deferred to fleet.
- **Contract and exit:** The contract is Chapter 7 `tenant-storage` versions plus this freeze and deprecation window. Teams do not leave it the way they leave a paved-road scaffold. Absorbing `2.0` is a Chapter 7 bump rolled by the fleet, not a Chapter 5 exit, not a Chapter 9 exception, not a Chapter 10 non-metric, and not a Chapter 11 burst.
- **Platform-product evidence:** A finished cohort dashboard is not proof the product works. Required proof is freeze, pending Fulfillment `1.0`, complete Storefront evidence, and rollback still allowed. This is not a portfolio **SLO (Service Level Objective)**. Adoption at 100% after deleting unofficial paths is still Chapter 10 vanity.

#### Diagnosis

Calling the cutover “v2 is ready” encourages the same unofficial path Chapter 7 interrupted in-place and Chapter 8 renamed cluster-admin: Fulfillment is blocked, someone shares the change, Storefront’s `sku` and Fulfillment’s `class` collide, and the warehouse path becomes the outage. Freeze labels stay in the runbook. Both cohorts show complete. Evidence stays pending. Last known good stays a field that was not used.

The missing freeze makes Chapter 7’s migration note a comment. The missing cohort makes Chapter 8’s tenant-scoped reconcile a slogan. Closing `1.0` while Fulfillment remains makes deprecation a second unofficial platform. Cluster-admin onboarding makes the join shared root again.

#### Correction

The completed model does not mark Fulfillment’s cohort complete. Freeze stays in force. Fulfillment’s applied version stays `1.0` with pending evidence. Storefront stays on `2.0` with complete evidence. Rollback to `1.0` stays allowed. Onboarding stays `tenant-operator`. Completeness is computed. The failure command proves the check still fails when only freeze, both cohort statuses, Fulfillment’s applied version, and result are injected.

This failure is a fleet-invariant failure. It is not a runtime plane recovery. Do not call the denied cutover **Evidence of restored isolation**. Nothing tenant-runtime was restored from a live apply. The product stopped treating every tenant as one compatibility domain.

That correction changes later decisions:

- Chapter 13 must not patch the plane in place to “finish the cutover.”
- Chapter 14 must recover `kubernetes-control-plane` without replaying Storefront’s `2.0` reconcile into Fulfillment’s `1.0`.
- Support may not close a ticket because the fleet dashboard shows 100% on `2.0`.
- A deprecation window may not replace migration evidence.

The design is practical because the failed all-at-once apply is the product. Adding an arbitrary kubectl rollout would not make it more practical.

## 5. Production reality

### Common fleet errors

#### Granting cluster-admin so onboarding works

Onboarding is a tenant join. Cluster-admin is shared root. Chapter 8 already refused the bargain.

#### Applying the new version to every tenant in one step

That is Chapter 7’s silent rename at fleet scale. Freeze, then one cohort.

#### Closing v1 while a tenant still legally sends it

Eternal v1 without a window is an unofficial platform. A closed window without an exception is an outage.

#### Collapsing plane 1.0 and contract 1.0

Chapter 8 retains plane last known good. This chapter retains contract last known good. Same string, different products.

#### Rewriting source so the cutover sticks

Inherited GitOps already forbids it. A fleet upgrade is reviewed intent, not a controller edit.

#### Building support-on-call in this chapter

Run freeze, cohort, and deprecation. Leave unofficial plane-admin edits to Chapter 13. Do not upgrade a live fleet.

## 6. What changed

| Before | After |
|---|---|
| `2.0` was applied to Storefront and Fulfillment in one step while Fulfillment still sent `class`. | **All-at-once apply and broken v1 without migration evidence fail the fleet invariant.** |
| Fulfillment onboarded with cluster-admin. | **Onboarding is `tenant-operator` on the paved road.** |
| There was no freeze and no rollback to contract `1.0`. | **Freeze covers `as_of`; last known good stays `1.0` and allowed.** |
| `1.0` closed while Fulfillment remained. | **Deprecation stays open until evidence exists or an exception binds.** |
| A valid schema could appear to prove a live rollout. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely four YAML files. Northwind now has a fleet lifecycle later support and recovery chapters can use without treating a finished dashboard as Fulfillment’s still-legal contract.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Fleet lifecycle policy | `fleet/onboarding.yaml` and `fleet/upgrades.yaml` | They retain the no-cluster-admin join, freeze, cohorts, and contract last known good later change and recovery chapters must not skip. |
| Upgrade-and-deprecation record | `fleet/deprecations.yaml` and `fleet/migrations.yaml` | They retain the open `1.0` window, Storefront’s completed `class-becomes-sku` evidence, and Fulfillment’s still-legal pending row. |

These artifacts should change when Northwind’s contract versions, tenant set, or freeze calendar materially change—not whenever a rollout dashboard theme is restyled.

## What You Learned

A fleet upgrade is how a Chapter 7 version bump reaches tenants: freeze, cohort, rollback, and migration evidence. Applying `2.0` to everyone while Fulfillment’s `1.0` `class` binding is still legal is an outage lottery, not a cutover. Schema checks can prove structural completeness within declared scope. They cannot upgrade a live fleet. A design earns its place when Storefront can be on `sku` while Fulfillment still sends `class`, and when both cohorts complete without evidence cannot hide that break.

### Prove It

> **Independent Practice — Onboard a read-only analytics tenant without copying the all-at-once 2.0 row**
>
> A data-analytics path needs to join `storefront-nonprod` for reads and must absorb a later contract bump without taking Fulfillment’s `1.0` window with it.

Extend the Chapter 12 model without adding support-on-call yet:

1. Decide whether analytics is a new Chapter 3 tenant—or still not a platform tenant—and which job, if any, it finishes.
2. Name the granted role that is not `cluster-admin`, and whether its join may burst Storefront’s floor.
3. State which Chapter 7 version it binds first, and which cohort it must not share with Fulfillment’s pending `1.0` row.
4. Choose a sample that would falsify “analytics can cut over safely”—for example both analytics and Fulfillment marked complete on `2.0` with analytics evidence pending.
5. Identify last known good if that apply fails—contract version, plane version, or both.
6. Explain which material change would trigger review of the fleet policy, not just one cohort tile.

Do not copy the Fulfillment all-at-once `2.0` row and rename it. Analytics has different admission, freeze, and remaining-window consequences than `tenant-storage` for `fulfillment-api`. Your durable output is the onboard-cohort-and-window decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 12 capability when you can explain why an all-at-once `2.0` apply is still a silent rename at fleet scale, trace a tenant to a Chapter 7 version, a freeze, and inherited GitOps state, describe evidence that would falsify rollback, distinguish structural validation from decision and outcome evidence, and explain what the baseline, checkpoint, and failure command do and do not prove.

## Next

The fleet can move, but platform change still happens through heroes in a shared chat. Support is still “message the people who built it.” Platform engineers apply live fixes with plane-admin. Tenants cannot tell a product incident from an application incident.

Chapter 13 supports, escalates, and changes the platform safely, so a live unofficial edit is rejected and a tenant ticket maps to a product or application owner.
