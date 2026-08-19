# Operate a Shared Control Plane as a Product

Chapter 7 versioned the infrastructure API. Fulfillment can bind `tenant-storage` `1.0` without a Terraform address. A single reconciler still applies those versions with broad authority and no tenant-scoped subject. Tickets return as “just let the controller do it.” Cluster-admin returns as a token “so onboarding works.” Chapter 3 already named `kubernetes-control-plane` as shared-control-plane and denied cluster-admin. A reconciler that still holds that token is the cumulative product failure continuing under a friendlier name.

The production question is now:

> How does the shared control plane reconcile tenant intent without becoming shared root?

Control-plane convenience recreates cluster-admin. Tenants cannot tell whether the plane is a product or a privileged script. This chapter records the plane as a product: a tenant-scoped subject, admission of Chapter 7 contract versions, inherited **GitOps (Git-based operations)** state that must not rewrite source, and a failed upgrade that retains last known good. Storefront must not be mutated by a Fulfillment reconcile. The plane must not approve its own change.

## 1. A reconciler that is still cluster-admin

A weak record says:

```yaml
subject: plane-reconciler
granted_role: cluster-admin
mutated_tenants: [fulfillment, storefront]
approved_by: plane-reconciler
```

It does not identify a Chapter 3 sharing mode, a plane identity distinct from tenant identity, an admitted contract version, inherited GitOps state, or last known good after a failed upgrade. “So onboarding works” may ship `fulfillment-api` this week. Fulfillment intent can rewrite Storefront. The plane can approve its own upgrade and keep running the version that failed.

Work from the lab working tree using the How to Use This Book procedure. From the Platform lab root, run the Chapter 8 baseline:

```bash
make chapter-08-baseline
```

The command succeeds when it detects the intended unsafe plane:

```text
chapter 08 baseline: cluster-admin reconciler correctly detected
```

The fixture grants the reconciler `cluster-admin`, lets a Fulfillment reconcile mutate Storefront, lets the plane approve its own upgrade, continues onto version `1.1` after that upgrade failed, rewrites source, and replaces inherited short-lived federated identity with a referenced rotatable secret. Contracts exist. The operator is still shared root.

That residual drives the chapter.

## 2. The production model: a plane you consume, not a token you inherit

> *Theory — Shared control plane as product*
>
> This model enables Fulfillment to finish `obtain-bounded-environment` and `ship-on-paved-road` by having admitted contract versions reconciled, without inheriting cluster-admin or mutating Storefront.

### The plane is `kubernetes-control-plane`, not a new cluster

Chapter 3 already declared the shared surface: `kubernetes-control-plane`, mode `shared-control-plane`, tenants may not inherit `cluster-admin` or `platform-operator`. Chapter 6 already used that id as the environment product’s shared plane and as credential audience. This chapter does not rename it to make the reconciler look new.

A **shared-nothing** platform would give each tenant its own plane. Northwind chose shared-control-plane. The reconciler is therefore a product with an owner, forbidden roles, and a subject. Shared cluster-admin is not that product. It is the unofficial path Chapter 3 interrupted, now running continuously.

`dev-cluster-admin` is not a plane role. Chapter 6 already forbade it on leases. The plane product forbids it too.

### Reconcile applies admitted intent; rewrite is shared root

Reconcile means: take a Chapter 7 binding that admission allowed, and apply it inside one tenant. Rewrite means: change source, skip admission, or mutate another tenant so onboarding works.

The inherited GitOps interface requires `reviewed_intent`, `immutable_artifact`, `independent_configuration`, and `reconciliation_result`. The controller may not rewrite source. Promoting `latest` is not immutable artifact identity. The inherited release interface still promotes by `artifact_digest`.

The inherited DevSecOps authorization interface already forbids self-approval and requires `subject`, `action`, `resource`, `context`, `policy_identity`, `result`, and `reason`. A plane change allowed by `plane-reconciler` as both actor and approver is self-approval. A living Chapter 1 user must approve plane upgrades. The reconciler must not.

**Best Practice:** Split plane identity from tenant identity. A tenant subject applies tenant work. A plane subject applies admitted versions and cannot approve its own change.

**Production Practice:** Isolation is a plane invariant joined to Chapter 3. This chapter loads `tenancy/sharing.yaml` and change-authority `denied_inheritance`. A plane subject with `cluster-admin` fails. A reconcile whose `mutated_tenants` includes another tenant fails.

### A failed upgrade retains last known good

Last known good is the plane version still running after an upgrade fails. It is not a backup of tenant data. Chapter 14 will recover the plane against this retention. This chapter must already refuse to treat a failed upgrade as a successful move to `1.1`. Completeness is computed. The plane cannot emit `status: healthy` to hide a missing last known good.

Do not build quota floors here. Do not bind guardrail exceptions here. Do not restore from mixed backups here.

## 3. Operate the plane as a product

The completed Chapter 8 model uses four files:

```text
control-plane/product.yaml
control-plane/subjects.yaml
control-plane/admission.yaml
control-plane/reconciliation.yaml
```

The separation is deliberate. The product names the plane id, jobs, federated identity, forbidden roles, and the GitOps rewrite prohibition. Subjects split plane identity from tenant identity. Admission names Chapter 7 versions and authorization decisions. Reconciliation records tenant applies and plane upgrades. The evaluator joins them to Chapter 3 tenants, isolation, sharing, and roles, Chapter 6’s environment product, Chapter 7 versions, and the inherited GitOps, identity, release, and authorization interfaces.

> **Practice — Bind the plane to the Chapter 3 sharing id and inherited identity**
>
> Consume `kubernetes-control-plane` and short-lived federated identity rather than inventing a controller token.

Open `control-plane/product.yaml`:

```yaml
owner: platform-team
plane: kubernetes-control-plane
jobs: [obtain-bounded-environment, ship-on-paved-road]
credential_model: short-lived-federated
forbidden_roles: [cluster-admin, dev-cluster-admin]
controller_may_rewrite_source: false
sharing_mode: shared-control-plane
```

The evaluator loads `inherited/devops-v1.1/identity/interface.yaml` and fails the product if federated identity is replaced by a referenced rotatable secret. It loads the GitOps interface and fails if the controller may rewrite source. It fails if the plane id is renamed.

> **Practice — Give the reconciler platform-operator, never cluster-admin**
>
> Tenants still must not inherit `platform-operator`. That is the plane role, not a tenant grant.

Open `control-plane/subjects.yaml`. The plane subject is `plane-reconciler` with `granted_role: platform-operator` and `may_approve_plane_change: false`. Storefront and Fulfillment keep `tenant-operator`. Audience is `kubernetes-control-plane`. Policy on the plane is `plane-scoped`, not `cluster-admin`.

> **Practice — Admit Chapter 7 versions and deny plane self-approval**
>
> A reconcile of an unknown version is not a product. A plane that allows its own upgrade is not reviewed.

Open `control-plane/admission.yaml` and `control-plane/reconciliation.yaml`. Admitted versions are the Chapter 7 `1.0` contracts. Fulfillment’s storage reconcile mutates `[fulfillment]` only. The failed upgrade from `1.0` to `1.1` is requested by the reconciler, approved by `platform-team`, and retains `last_known_good: "1.0"` as `current_version`.

The lab does not run a real Kubernetes control plane. Completeness is whether the reconciler stays a product: tenant-scoped apply, admitted versions, no source rewrite, no self-approval, last known good after failure.

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
chapter 08 checkpoint: tenant-scoped plane subjects and last known good verified
```

The audit validates the four Chapter 8 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- the product names `kubernetes-control-plane` and inherited federated identity;
- sharing mode is `shared-control-plane` from Chapter 3;
- required jobs remain `obtain-bounded-environment` and `ship-on-paved-road`;
- the plane subject exists, is not tenant-scoped, and is not `cluster-admin` or `dev-cluster-admin`;
- tenant subjects do not inherit change-authority denials from Chapter 3;
- admitted versions exist in Chapter 7;
- authorization decisions carry inherited fields and the plane cannot allow its own upgrade;
- reconciles bind Chapter 3 environment ids and mutate only their tenant;
- GitOps required state is present and source is not rewritten;
- immutable artifact is not `latest` when promotion identity is digest; and
- a failed upgrade retains last known good as the current version.

The expected plane id, jobs, and forbidden roles live in a separate checkpoint file. A plane under test does not emit its own passing health.

The checkpoint does not prove that a real apiserver admitted a contract, that a real controller applied an object, or that a real upgrade rolled back. Those remain claims a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 8 evidence |
|---|---|
| Mechanism evidence | Schemas and the admission-and-reconcile evaluator operated successfully. |
| Decision evidence | Plane id, subjects, forbidden roles, admitted versions, and last known good are explicit. |
| Outcome evidence | Fulfillment has a computed reconcile for `fulfillment-nonprod` that does not mutate Storefront. That is not proof a live object exists. |
| Recovery evidence | Not produced. A denied cluster-admin reconcile is a plane-authority invariant, not restored tenant isolation after a live rewrite. Last known good is retained version evidence, not Chapter 14 restore. |

Chapter 8 produces mechanism, decision, and limited outcome evidence for a shared plane product. Pretending the local checkpoint proves kube-apiserver behavior would weaken Chapter 12’s fleet upgrades and Chapter 14’s bounded recovery.

## 4. Test the design under failure

### Cumulative product failure — The reconciler uses a cluster-admin token "so onboarding works," allowing one tenant intent to mutate another

> **Practice — Deny shared plane-admin and cross-tenant reconcile**
>
> Inject cluster-admin onto the completed plane subject and refuse a Fulfillment apply that mutates Storefront.

The completed plane is healthy. The failure command does not rewrite it. It injects the residual cluster-admin case against that snapshot:

```bash
make chapter-08-failure
```

Expected output:

```text
chapter 08 failure: cluster-admin cross-tenant reconcile correctly rejected
```

The injected record is:

```yaml
id: plane-reconciler
granted_role: cluster-admin
# fulfillment-nonprod-storage
mutated_tenants: [fulfillment, storefront]
```

Federated identity, GitOps rewrite prohibition, admitted Chapter 7 versions, self-approval denial, and last known good stay current. The baseline’s missing last known good, source rewrite, and secret-model drop are not required for this failure. Shared plane-admin can appear after the product already looks complete. Cluster-admin on the reconciler and cross-tenant mutate must both fail on their own terms.

**Severity:** high; every later guardrail, fleet, support, and recovery conversation will optimize a shared-root controller instead of a plane product.  
**Plausible harm:** Fulfillment onboarding rewrites Storefront storage; the order path moves with a warehouse change; the plane then upgrades itself.  
**Potential blast radius:** both application tenants and `kubernetes-control-plane`; Storefront’s order path is no longer a separate failure domain.  
**Bounded by:** Chapter 3 sharing and change-authority denials, Chapter 6 leases, Chapter 7 admitted versions, and inherited GitOps and authorization. None of those repair a reconciler that still holds `cluster-admin`.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence.

#### Platform questions

- **User and job:** Fulfillment must finish `obtain-bounded-environment` and `ship-on-paved-road`. A cluster-admin token so onboarding works is not those jobs; it is shared authority substituting for a plane subject.
- **Isolation:** The boundary is Chapter 3’s tenant plus this plane subject: `kubernetes-control-plane` as shared-control-plane, `platform-operator` that tenants may not inherit, no `cluster-admin`, and a reconcile that cannot list another tenant in `mutated_tenants`. Fulfillment’s blast radius must stop at Fulfillment.
- **Contract and exit:** The contract is the plane product, admitted Chapter 7 versions, and last known good. Teams do not leave the plane the way they leave a paved-road scaffold. They consume it without inheriting it. A plane upgrade is a reviewed change, not a tenant exit and not an exception to digest identity.
- **Platform-product evidence:** A running controller is not proof the product works. Required later proof is tenant-scoped reconcile plus retained last known good. This is not a portfolio **SLO (Service Level Objective)**.

#### Diagnosis

Calling the token “so onboarding works” encourages the same unofficial path Chapter 3 interrupted and Chapter 6 renamed `dev-cluster-admin`: Fulfillment is blocked, someone shares change authority, Storefront moves, and the order path becomes a noisy neighbor. Versioned contracts then apply through shared root. Self-approval makes the upgrade path ornamental. Missing last known good makes failure a successful move. Source rewrite makes GitOps a label on a privileged script.

The missing plane/tenant identity split makes Chapter 3’s `platform-operator` a second cluster-admin. The missing admission join makes Chapter 7’s versions documentation. Shared plane-admin makes shared-control-plane a slogan.

#### Correction

The completed model does not grant the reconciler `cluster-admin`. The plane subject is `platform-operator` with federated, plane-scoped claims. Fulfillment’s reconcile mutates Fulfillment. Storefront is not in `mutated_tenants`. Plane upgrades are approved by `platform-team`, not by `plane-reconciler`. A failed upgrade keeps version `1.0` as last known good. Source is not rewritten. Isolation is recorded as a plane invariant.

This failure is a plane-authority invariant. It is not a runtime plane recovery. Do not call the denied reconcile **Evidence of restored isolation**. Nothing tenant-runtime was restored from a live rewrite. The product stopped treating cluster-admin as onboarding.

That correction changes later decisions:

- Chapter 9 must enforce defaults on this plane without granting the reconciler cluster-admin to “make the webhook stick.”
- Chapter 12 must upgrade the plane in cohorts against last known good, not by patching shared root in place.
- Chapter 13 must reject unofficial plane-admin the same way this chapter rejects the onboarding token.
- Chapter 14 must recover `kubernetes-control-plane` from last known good without replaying one tenant’s reconcile into another.

The design is practical because the denied cross-tenant apply is the product. Adding an arbitrary kubectl command would not make it more practical.

## 5. Production reality

### Common control-plane errors

#### Granting cluster-admin so onboarding works

Onboarding is a tenant job. Cluster-admin is shared root. They are not a bargain.

#### Letting the plane approve its own change

Inherited authorization already forbids self-approval. A living owner must admit plane upgrades.

#### Treating a failed upgrade as the new current version

Last known good is the version still running. `to_version` is intent, not fact.

#### Rewriting Git source from the controller

The inherited GitOps interface forbids it. Reconcile applies reviewed intent. It does not edit the request.

#### Using a tenant subject as the plane, or a plane subject as a tenant

Split identity. Audience stays `kubernetes-control-plane`. Policy does not.

#### Building quota, guardrails, or restore in this chapter

Admit versions and retain last known good. Leave floors to Chapter 11, exceptions to Chapter 9, and mixed-backup restore to Chapter 14.

## 6. What changed

| Before | After |
|---|---|
| The reconciler used `cluster-admin` so onboarding worked. | **Shared plane-admin and cross-tenant reconcile fail the plane invariant.** |
| One controller mutated whichever tenant was convenient. | **Each reconcile mutates only its Chapter 3 tenant.** |
| Plane and tenant identity were the same token. | **Plane subject is `platform-operator`; tenants remain `tenant-operator`.** |
| Contract versions were documentation. | **Admission joins Chapter 7; unknown versions cannot apply.** |
| The plane approved its own upgrade and kept the failed version. | **A living owner approves; failed upgrades retain last known good.** |
| A valid schema could appear to prove kube-apiserver. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely four YAML files. Northwind now has a control-plane product that later chapters can guard, upgrade, support, and recover without treating cluster-admin as reconciliation.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Control-plane product contract | `control-plane/product.yaml` | It retains the plane id, jobs, federated identity, forbidden roles, and GitOps rewrite prohibition later fleet and recovery chapters must not rename. |
| Tenant-scoped authority map | `control-plane/subjects.yaml` | It retains the split between plane-operator and tenant-operator, and the rule that the plane cannot approve its own change. |

These artifacts should change when Northwind’s shared plane, tenant set, or inherited GitOps model materially change—not whenever a controller image tag is restyled.

## What You Learned

A shared control plane is a product with a tenant-scoped subject, admitted contract versions, and last known good. A cluster-admin token so onboarding works is shared root. Schema checks can prove structural completeness within declared scope. They cannot prove a real Kubernetes control plane. A design earns its place when Fulfillment’s reconcile cannot mutate Storefront, and when a failed plane upgrade still runs the last known good version.

### Prove It

> **Independent Practice — Scope a read-only analytics reconciler without copying cluster-admin**
>
> A data-analytics path needs the plane to apply a read contract in `storefront-nonprod` and must not mutate Fulfillment or approve plane upgrades.

Extend the Chapter 8 model without adding guardrail exceptions yet:

1. Decide whether analytics uses the existing `plane-reconciler` with a narrower admit list, or a second plane subject that still is not `cluster-admin`.
2. Name which Chapter 7 versions that subject may reconcile, and which tenant must be absent from `mutated_tenants`.
3. State which inherited GitOps fields still apply, and which authorization action must deny if the subject is the approver.
4. Choose last known good if this subject’s apply fails—plane version, tenant binding, or both.
5. Identify one observation that would falsify isolation—for example `mutated_tenants: [storefront, fulfillment]` on an analytics reconcile.
6. Explain which material change would trigger review of the plane product, not just one reconcile.

Do not copy the Fulfillment cluster-admin row and rename it. Read-only analytics has different admission, mutate, and upgrade consequences than a shipping reconciler. Your durable output is the subject-and-admission decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 8 capability when you can explain why a cluster-admin reconciler is still shared root, trace a reconcile to a Chapter 3 tenant, a Chapter 7 version, and inherited GitOps state, describe evidence that would falsify last known good, distinguish structural validation from decision and outcome evidence, and explain what the baseline, checkpoint, and failure command do and do not prove.

## Next

The plane is a product, but defaults either trap teams or can be switched off quietly. Security and delivery defaults from earlier books are either mandatory with no exit or optional with no owner.

Chapter 9 enforces guardrails without a golden cage, so remaining defaults stay owned and exceptions stay temporary.
