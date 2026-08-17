# Recover a Control-Plane Failure Without Taking Tenants With It

Chapter 13 named a support class and a reviewed plane change. Last known good is still plane `1.0`. Storefront is still on `tenant-storage` `2.0`. Fulfillment’s `1.0` `class` binding is still legal. Backup of the plane is a job-success metric. Tenant isolation during restore is undefined. Restoring from a mixed backup can replay Fulfillment’s intent into Storefront, or freeze every application path because the shared plane was down. Chapter 8 already retained last known good after a failed move to `1.1`. A newest snapshot of that failed version is that residual wearing a restore coat.

The production question is now:

> How does Northwind restore the platform product after control-plane loss without reconstructing every tenant as one blast radius?

This chapter records independently verified plane evidence, an isolated restore to last known good, and a per-tenant continue or freeze that is explicit. Mixed-tenant replay fails. Storefront’s order path continues or freezes by decision, not by accident. Fulfillment isolation holds. Regional-loss architecture and portfolio **RTO (Recovery Time Objective)** programs remain SRE.

## 1. The newest backup, with both tenants inside it

A weak record says:

```yaml
snapshot: plane-newest-corrupt
restored_version: "1.1"
last_known_good: "1.1"
mixed_backup: true
subject: plane-reconciler
replayed_from: fulfillment   # storefront row
decision: freeze
source: accident
recovered_indicators: [order_success_ratio]
```

It does not identify Chapter 8’s retained plane `1.0`, a snapshot that is not mixed, an explicit tenant decision, or a restore subject that is not the reconciler. “Just restore newest” may bring the API back. Storefront receives Fulfillment’s `1.0` `class` intent. Both tenants freeze because the plane was down. Order-success stands in for platform recovery. The unofficial `1.1` patch Chapter 13 refused becomes last known good.

Work from the lab working tree using the How to Use This Book procedure. From the Platform lab root, run the Chapter 14 baseline:

```bash
make chapter-14-baseline
```

The command succeeds when it detects the intended unsafe restore:

```text
chapter 14 baseline: mixed-backup restore replaying fulfillment into storefront correctly detected
```

The fixture applies the corrupted newest snapshot, lets `plane-reconciler` approve itself with `cluster-admin`, moves last known good to `1.1`, replays Fulfillment into Storefront, freezes Storefront by accident, and meters recovery on `order_success_ratio`. Support exists. Restore is still shared authority.

That residual drives the chapter.

## 2. The production model: restore the plane, not the blast radius

> *Theory — Isolated control-plane restore*
>
> This model enables Fulfillment to finish `obtain-bounded-environment` and `ship-on-paved-road` after plane loss by restoring independently verified last known good, without inheriting Storefront’s `2.0` intent or freezing every tenant because one plane was down.

### Plane evidence is not tenant data-plane evidence

Chapter 8’s last known good is the plane version still running after the failed upgrade to `1.1`: `1.0`. That is not a backup of Storefront orders. It is not Chapter 12’s contract last known good on `tenant-storage` `1.0`. Do not collapse them because both say `1.0`. This chapter restores the plane against Chapter 8’s retention. Tenant storage versions stay where fleet left them: Storefront `2.0`, Fulfillment `1.0`.

The inherited restore contract requires five roots: `reviewed_intent`, `artifact_identity`, `configuration_identity`, `durable_data`, and `identity_policy`. Completeness of those roots is not isolation. The newest snapshot in this lab carries all five and is still mixed, corrupt, and unverified. Applying it fails.

**Best Practice:** Inventory last known good and newest separately. Restore the independently verified isolated snapshot. Keep the mixed newest record so a later debugger can see what was refused.

**Production Practice:** Newest is not last known good. A snapshot can hold every inherited root and still replay one tenant into another. Clearing `mixed_tenants` stops the mixed-backup error. The newest-is-not-LKG check still runs. They are not the same check.

### Continue and freeze are tenant decisions, not restore defaults

A shared-plane outage tempts two mistakes: return every tenant’s traffic because the API answered, or freeze every tenant because the plane was down. Both treat tenants as one blast radius.

Storefront may **continue**. Storefront may **freeze**. Fulfillment likewise. The source must be `explicit-tenant-decision`. Accident fails. An explicit freeze is not an accidental freeze. A frozen tenant must not return traffic. A continuing tenant must present the inherited traffic-return evidence: `reconciled_business_state` and `verified_service_outcome`. Those gates are not Storefront `order_success_ratio`. That id remains tenant-workload. It cannot prove bounded platform-product recovery.

**Production Practice:** Traffic return is not plane restore. Restoring the five roots does not return traffic. Meeting the inherited traffic-return pair does not choose continue for a tenant. Continue and freeze are explicit decisions joined to Chapter 3’s tenant boundary. Accidental freeze of Storefront is not that join.

Quota still binds. Restored units must match Chapter 6 lease sums. Remaining capacity after one tenant’s restored usage must still cover the peer floor. A restore that replays Fulfillment’s burst into Storefront’s floor fails `unlimited-burst-into-peer-quota` the same way Chapter 11 failed the live burst.

### A restore is not a leave, a bump, or a live patch

They are not the same act:

| Act | Chapter | What it is |
|---|---|---|
| Supported exit | 5 | Leave the scaffold; remaining guardrails stay |
| Contract version bump | 7 | Leave a tenant-visible API version with a migration note |
| Guardrail exception | 9 | Temporary deviation; expiry lives on the inherited record |
| Non-metric demotion | 10 | Vanity leaves the indicator set |
| Fleet upgrade | 12 | Roll a Chapter 7 bump with freeze, cohort, and rollback |
| Platform change | 13 | Reviewed subject on the plane; unofficial plane-admin fails |
| Isolated restore | 14 | Restore plane last known good; mixed-tenant replay fails |

A mixed backup apply is not a Chapter 8 plane upgrade. It is not a Chapter 12 fleet upgrade. It is not a Chapter 13 unofficial patch, even when it uses `plane-reconciler` and last known good `1.1`.

**Production Practice:** Self-approval on a restore is still not `subject == approved_by`. An allowed restore fails when its `subject` or `approved_by` is a Chapter 8 plane identity (`kind: plane`). That identity is `plane-reconciler`, already flagged `may_approve_plane_change: false`. `platform-team` may appear in both fields because it is a living Chapter 1 user, not that plane subject. The restore YAML repeats Chapter 13’s healthy pattern; it does not invent a symmetry check.

Do not build a regional-loss program here. Do not assign a portfolio RTO. Chapter 1 already left those with remaining owner `reliability-program`. This chapter records that limitation on the verification. A verification file cannot emit `status: recovered` to hide a mixed apply.

## 3. Recover the plane as a product

The completed Chapter 14 model uses four files:

```text
recovery/plane-evidence.yaml
recovery/isolation.yaml
recovery/restore-trace.yaml
recovery/verification.yaml
```

The separation is deliberate. Plane evidence inventories snapshots. Isolation records per-tenant continue or freeze, replay, and restored contract version. Restore-trace is the plane-authority record. Verification is the bounded claim. The evaluator joins them to Chapter 1 users, Chapter 3 tenants and isolation, Chapter 6 leases, Chapter 8 subjects, plane product, and last known good, Chapter 11 quota, Chapter 12 migrations, Chapter 13 changes and incidents, and the inherited restore contract. It does not load the **GitOps (Git-based operations)**, observability, or incident interfaces those earlier chapters already consumed.

> **Practice — Keep last known good and newest in the same inventory**
>
> Restore `plane-lkg-1-0`. Leave `plane-newest-corrupt` on file as the refused snapshot. Do not delete the mixed record to make the inventory look clean.

Open `recovery/plane-evidence.yaml`. Owner is `platform-team`. Plane is `kubernetes-control-plane`. Last known good is `1.0`. The verified snapshot is not newest, not mixed, not corrupt. The newest snapshot has the same five roots and is still mixed.

> **Practice — Restore Chapter 8 last known good with a reviewed subject**
>
> `platform-team` may restore. `plane-reconciler` may not approve that restore. Last known good stays plane `1.0`.

Open `recovery/restore-trace.yaml`:

```yaml
id: restore-plane-lkg
snapshot: plane-lkg-1-0
resource: kubernetes-control-plane
subject: platform-team
approved_by: platform-team
action: restore-last-known-good
restored_version: "1.0"
last_known_good: "1.0"
mixed_backup: false
unofficial: false
source_rewritten: false
result: allow
```

The evaluator loads Chapter 8’s failed plane upgrade and fails a restore whose last known good is not `1.0`. It fails mixed backups, newest selection, unverified snapshots, `cluster-admin`, a plane identity as subject or approver, and source rewrite. It loads Chapter 8 `forbidden_roles` live. Clearing that list does not make a mixed apply legal. `platform-team` in both fields is the reviewed path, not the self-approval the newest restore impersonates.

> **Practice — Name continue or freeze per tenant, then keep Fulfillment’s version**
>
> Storefront continues on `tenant-storage` `2.0`. Fulfillment continues on `1.0`. Neither row may list the other tenant under `mutated_tenants`.

Open `recovery/isolation.yaml` and `recovery/verification.yaml`. Both tenants use `source: explicit-tenant-decision`. Storefront’s restored version is `2.0`, matching Chapter 8’s reconcile and Chapter 12’s completed migration. Fulfillment stays `1.0`. Quota units are the Chapter 6 lease sums, `12` and `12`. Traffic return lists the inherited pair, not `order_success_ratio`. Limitations include `not-regional-loss` and `not-portfolio-rto`. Completeness is computed.

The lab does not restore a real etcd. Completeness is whether mixed backup is rejected, whether each tenant’s restored version matches the living fleet, and whether continue or freeze is explicit.

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
chapter 14 checkpoint: isolated plane restore and tenant continue/freeze verified
```

The audit validates the four Chapter 14 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- plane evidence owner is a living Chapter 1 user and the plane is `kubernetes-control-plane`;
- last known good joins Chapter 8’s retained `1.0`, not Chapter 12’s contract `1.0`;
- an allowed restore of a mixed, newest, corrupt, or unverified snapshot fails;
- complete inherited roots do not legalize mixed tenants;
- an allowed restore whose subject or approver is `plane-reconciler` fails self-approval; `platform-team` in both fields does not;
- unofficial or `cluster-admin` restores fail;
- every Chapter 3 tenant has an explicit continue or freeze;
- Fulfillment intent replayed into Storefront fails, including a Storefront row restored to Fulfillment’s `1.0`;
- restored quota units match leases and cannot starve a peer floor;
- a continuing tenant presents inherited traffic-return evidence, and a frozen tenant does not;
- `order_success_ratio` cannot prove bounded platform-product recovery; and
- verification cannot emit `status: recovered` and must record that this is not regional-loss or portfolio RTO.

The expected plane, jobs, limitations, and forbidden indicators live in a separate checkpoint file. A restore under test does not emit its own passing grade.

The checkpoint does not prove that a real control plane was restored, that a real freeze stopped Storefront checkout, or that 60 minutes is the right RTO. Those remain claims a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 14 evidence |
|---|---|
| Mechanism evidence | Schemas and the plane-restore evaluator operated successfully. |
| Decision evidence | Last known good versus newest, explicit continue or freeze, refused mixed snapshots, and SRE limitations are explicit. |
| Outcome evidence | Storefront has a computed continue on `2.0`. Fulfillment has a computed continue on `1.0`. That is not proof etcd was restored. |
| Recovery evidence | Produced and bounded. Mixed backup is rejected. Plane last known good `1.0` is the restored version. Tenant isolation holds in the model. That is **Evidence of restored isolation** and **Evidence of bounded platform-product recovery**. It is not DevSecOps restored trust, not a live-cluster recovery test, and not a regional-loss program. |

Chapter 14 produces mechanism, decision, outcome, and bounded recovery evidence for isolated plane restore. Pretending the local checkpoint proves a multi-region disaster-recovery exercise would hand the planned SRE book a claim this lab cannot make.

## 4. Test the design under failure

### Cumulative product failure — A corrupted newest plane backup is applied and replays Fulfillment intent into Storefront

> **Practice — Fail the newest mixed restore that writes Fulfillment into Storefront**
>
> Inject `plane-newest-corrupt` as an allowed restore with last known good `1.1`, and a Storefront row replayed from Fulfillment onto `1.0`, and refuse the apply.

The completed recovery model is healthy. The failure command does not rewrite it. It injects the residual mixed-backup case against that snapshot:

```bash
make chapter-14-failure
```

Expected output:

```text
chapter 14 failure: mixed-backup restore correctly rejected
```

The injected restore is:

```yaml
id: restore-newest-mixed
snapshot: plane-newest-corrupt
subject: plane-reconciler
approved_by: plane-reconciler
granted_role: cluster-admin
restored_version: "1.1"
last_known_good: "1.1"
mixed_backup: true
unofficial: true
source_rewritten: true
result: allow
```

The injected Storefront isolation row is:

```yaml
tenant: storefront
replayed_from: fulfillment
mutated_tenants: [storefront, fulfillment]
restored_version: "1.0"
```

Fulfillment’s own row stays `replayed_from: fulfillment`, `restored_version: "1.0"`, and `decision: continue`. Plane evidence still lists last known good `1.0`. The baseline’s accidental freeze, order-success recovered indicators, and missing SRE limitation are not required for this failure. A mixed apply can appear after the inventory already looks complete. Chapter 8 already failed the move to plane `1.1`. Last known good `1.1` is that failure, now used as a restore source. Storefront’s living version is `2.0`. Restoring Fulfillment’s `1.0` onto Storefront is the replay.

**Severity:** high; every later conversation will restore an unofficial mixed plane instead of reviewed last known good and tenant isolation.  
**Plausible harm:** Storefront’s `sku` path becomes Fulfillment’s `class` intent; warehouse and checkout share one reconstructed plane; both tenants look recovered because the API answered.  
**Potential blast radius:** both application tenants, `kubernetes-control-plane`, and `cluster-capacity-pool`; Fulfillment’s blast radius no longer stops at Fulfillment.  
**Bounded by:** Chapter 3 isolation, Chapter 6 leases, Chapter 8 last known good and forbidden roles, Chapter 11 floors, Chapter 12 migrations, Chapter 13 change authority, and the inherited restore contract. None of those repair an allowed mixed apply.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence.

#### Platform questions

- **User and job:** Fulfillment must finish `obtain-bounded-environment` or `ship-on-paved-road` after the plane returns. A mixed newest restore that writes Fulfillment into Storefront is not those jobs. It is shared authority substituting for last known good.
- **Isolation:** The boundary is Chapter 3’s tenant plus this restore: Storefront’s reconstructed intent must remain Storefront. Fulfillment’s blast radius must stop at Fulfillment. This is not a new tenancy model. It is Chapter 8’s tenant-scoped reconcile applied to recovery.
- **Contract and exit:** The contract is independently verified plane last known good plus per-tenant continue or freeze. Teams do not leave it the way they leave a paved-road scaffold. A mixed apply is not a Chapter 5 exit, not a Chapter 7 version bump, not a Chapter 9 exception, not a Chapter 10 non-metric, not a Chapter 11 burst, not a Chapter 12 fleet upgrade, and not a Chapter 13 reviewed change.
- **Platform-product evidence:** A restored apiserver is not proof the product works. Required proof is last known good `1.0`, no cross-tenant replay, explicit continue or freeze, and named platform jobs. This is not a portfolio **SLO (Service Level Objective)**. Storefront `order_success_ratio` remains tenant workload.

#### Diagnosis

Calling the write “newest is the best backup” encourages the same unofficial path Chapter 8 interrupted and Chapter 13 refused: Fulfillment is blocked, someone shares plane-admin, Storefront moves with the restore, and last known good becomes the broken version. Newest looks complete because it has every inherited root. Freeze looks safe because nobody is serving. Order-success looks like recovery because Storefront’s path flickered green.

The missing LKG join makes Chapter 8’s failed upgrade a successful restore. The missing replay check makes Chapter 12’s two contract versions one reconstructed tenant. Accidental freeze makes Chapter 3’s blast-radius statement a comment. Closing on `order_success_ratio` makes Chapter 10’s non-metric a memory.

#### Correction

The completed model does not allow `restore-newest-mixed`. The reviewed restore keeps subject `platform-team`, snapshot `plane-lkg-1-0`, last known good `1.0`, and `mixed_backup: false`. Storefront continues on `2.0` from Storefront. Fulfillment continues on `1.0` from Fulfillment. Completeness is computed. The failure command proves the check still fails when only the mixed apply and the Storefront replay are injected.

The denied mixed apply is a restore-authority invariant. It is not by itself the recovery. **Evidence of restored isolation** is the completed verification: plane last known good restored, tenant replay absent, continue or freeze explicit, platform jobs named, regional-loss not claimed. Nothing in that record is DevSecOps restored trust. Nothing in it is a multi-region fail-over.

That correction changes later decisions:

- The conclusion may assemble an owned internal platform only if restore cannot reconstruct every tenant as one blast radius.
- Mixed-backup restore must not replay a hero edit or a peer contract version into another tenant.
- Support may not freeze every tenant because one warehouse ticket was noisy during restore.
- Regional-loss and portfolio RTO remain SRE. This chapter records that limitation rather than filling it.

The design is practical because the failed mixed apply is the product. Adding an arbitrary etcd snapshot tool would not make it more practical.

## 5. Production reality

### Common restore errors

#### Restoring newest because it completed most recently

Chapter 8 already failed plane `1.1`. Newest is that failure plus whatever mixed after it.

#### Treating complete restore roots as isolation

The inherited five roots prove reconstruction identity. They do not prove Storefront’s intent stayed Storefront.

#### Freezing every tenant because the plane was down

Continue and freeze are explicit. Accident fails. An explicit freeze is legal and must not return traffic.

#### Borrowing Storefront order-success as platform recovery

The inherited traffic-return pair is `reconciled_business_state` and `verified_service_outcome`. `order_success_ratio` stays tenant workload.

#### Collapsing plane 1.0 and contract 1.0

Chapter 8 retains plane last known good. Chapter 12 retains contract last known good. Restore must not move either by applying Fulfillment’s `1.0` onto Storefront’s `2.0`.

#### Claiming regional-loss or portfolio RTO in this chapter

Record the limitation. Leave those programs to SRE. Do not restore a real cluster.

## 6. What changed

| Before | After |
|---|---|
| Newest mixed `1.1` was applied as last known good. | **Mixed, newest, corrupt, and unverified snapshots fail the restore path.** |
| Fulfillment intent replayed into Storefront. | **Each tenant restores its own living contract version.** |
| Both tenants froze because the plane was down. | **Continue and freeze are explicit tenant decisions.** |
| Order-success closed recovery. | **Tenant-workload ids cannot prove bounded platform-product recovery.** |
| A valid schema could appear to prove disaster recovery. | **Structural, decision, outcome, and bounded recovery evidence remain distinct.** |

What changed was not merely four YAML files. Northwind now has a restore path the conclusion can name without treating a mixed newest backup as the product.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Control-plane recovery contract | `recovery/plane-evidence.yaml` and `recovery/restore-trace.yaml` | They retain independently verified last known good and the refused mixed newest snapshot later recovery must not promote. |
| Bounded isolation verification | `recovery/isolation.yaml` and `recovery/verification.yaml` | They retain explicit continue or freeze, per-tenant restored versions, and the SRE limitation a restored apiserver must not erase. |

These artifacts should change when Northwind’s plane last known good, living contract versions, or tenant freeze policy materially change—not whenever a backup tool is restyled.

## What You Learned

Restore is independently verified last known good plus an explicit tenant decision. A newest mixed snapshot that writes Fulfillment into Storefront is shared plane-admin, not recovery. Schema checks can prove structural completeness within declared scope. They cannot restore a real control plane. A design earns its place when `plane-lkg-1-0` is restored, `plane-newest-corrupt` is refused, Storefront continues on `2.0`, Fulfillment continues on `1.0`, and `plane-reconciler` cannot approve a restore that moves last known good to `1.1`.

### Prove It

> **Independent Practice — Restore after Storefront-only evidence loss without copying the mixed-backup row**
>
> Storefront’s nonprod plane evidence is unverified. Fulfillment asks to keep shipping warehouse effects. Someone will offer to restore newest so both tenants return together.

Extend the Chapter 14 model without claiming regional-loss:

1. Decide whether Storefront continues, freezes, or is still waiting on independently verified evidence.
2. Name which snapshot is last known good—and which newest snapshot must not be selected even if it lists every inherited root.
3. State whether Fulfillment may continue while Storefront is frozen, or whether a shared-plane restore forces both.
4. Choose a sample that would falsify “Storefront-only loss can restore newest safely”—for example Storefront `replayed_from: fulfillment` with restored version `1.0`.
5. Identify which last known good that sample must retain—plane version, contract version, or both.
6. Explain which material change would trigger review of the recovery contract, not just one restore.

Do not copy the Fulfillment-into-Storefront mixed-backup row and rename it. A Storefront-only evidence gap has different continue/freeze and last-known-good consequences than a mixed newest apply. Your durable output is the snapshot-decision-and-isolation reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 14 capability when you can explain why newest is not last known good, trace a restore to Chapter 8 last known good and a Chapter 3 tenant decision, describe evidence that would falsify mixed-tenant replay, distinguish structural validation from decision, outcome, and recovery evidence, and explain what the baseline, checkpoint, and failure command do and do not prove.

## Next

Product, tenancy, paved road, control plane, fleet, support, and bounded recovery now exist as one owned internal platform. The remaining work is to say what that platform is, what the five principles demand of it, what this book does not claim, and what the planned fourth book, *Practical SRE Engineering*, must take from here.
