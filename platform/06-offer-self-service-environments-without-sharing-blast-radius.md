# Offer Self-Service Environments Without Sharing Blast Radius

Chapter 5 paved a path Fulfillment can complete or leave. That path still assumes an environment. Provisioning is a ticket. Namespaces share quota and credentials. Chapter 2 already productized environment provisioning against `obtain-bounded-environment`. Chapter 3 already named `fulfillment-nonprod` and denied `cluster-admin`. A ticket that grants “dev cluster admin” so Fulfillment can ship is the cumulative product failure continuing under a friendlier name.

The production question is now:

> How can a team obtain a bounded environment without inheriting everyone else's cluster?

Wait time returns, or self-service creates unbounded namespaces with production-like authority. This chapter records an environment product, a request, and a lease with **TTL (Time To Live)**, quota, and tenant-scoped identity. Storefront must not consume Fulfillment credentials. Fulfillment must not scale Storefront’s environment to steal quota from `cluster-capacity-pool`. Isolation is a product invariant, not a namespace label.

## 1. A shared admin that still steals quota

A weak record says:

```yaml
environment: storefront-nonprod
granted_role: dev-cluster-admin
mutated_by: fulfillment-team
```

It does not identify a Chapter 1 job, a Chapter 3 tenant environment, a request, an expiry, a quota bound, or inherited federated identity. “Dev cluster admin” may sound narrower than `cluster-admin`. It is still shared change authority. Fulfillment can scale Storefront’s environment and consume the shared pool. The paved road has somewhere to deploy, and every tenant’s blast radius is that somewhere.

Work from the lab working tree using the How to Use This Book procedure. From the Platform lab root, run the Chapter 6 baseline:

```bash
make chapter-06-baseline
```

The command succeeds when it detects the intended unsafe product:

```text
chapter 06 baseline: shared dev-cluster-admin quota steal correctly detected
```

The fixture grants `dev-cluster-admin`, lets Fulfillment mutate `storefront-nonprod`, leaves `fulfillment-nonprod` without expiry, and replaces inherited short-lived federated identity with a referenced rotatable secret. Chapter 3 removed cluster-admin from tenant roles. The unofficial environment path put it back.

That residual drives the chapter.

## 2. The production model: a lease is the environment

> *Theory — Environment as product*
>
> This model enables Fulfillment to finish `obtain-bounded-environment` inside Chapter 3’s blast-radius boundary, with a lease that expires and credentials Storefront cannot consume.

### An environment is a leased instance of a tenant, not a namespace anyone can create

Chapter 3 already listed the environment ids this product must use: `storefront-nonprod`, `storefront-prod`, `fulfillment-nonprod`, `fulfillment-prod`. The product does not invent a fifth name. A request names tenant, environment, requester, and class. A lease binds that request to expiry, quota, credentials, and isolation. If the environment is not in the tenant inventory, it is not a product. It is an unbounded namespace.

Ephemeral environments (non-production) and durable environments (production) are both leases. Durable is not infinite. Production still expires or is reviewed. The difference is TTL length, not whether isolation applies.

The shared plane is `kubernetes-control-plane`. The quota pool is `cluster-capacity-pool`. Those identifiers were declared in Chapter 3. This chapter consumes them. Chapter 11 will allocate floors and ceilings against the same pool. Do not rename the pool here to make quota look new.

### Credentials are tenant-scoped and short-lived

The inherited DevOps identity interface requires claims `subject`, `issuer`, `audience`, `expiry`, and `policy`. Its credential model is short-lived federated identity. Referenced rotatable secrets are unsupported. The environment product must not drop that model to make provisioning easier.

Audience is the shared plane, not a peer tenant. Subject must be scoped to the tenant or the environment. Storefront must not present `fulfillment-nonprod` as a credential. Fulfillment must not receive a credential that outlives the lease.

**Best Practice:** Bind each lease to a request and to a Chapter 3 environment id. An environment that cannot name its request is a ticket that skipped the product.

**Production Practice:** Isolation is computed. A lease cannot emit `status: isolated`. This chapter loads Chapter 3's `denied_inheritance` lists for network and secrets. Cross-tenant mutation, shared env-admin, expired-but-active leases, and those denied surfaces fail the invariant.

### Quota on a lease is a bound, not a FinOps program

Each lease names `cluster-capacity-pool` and a unit count. That bound is what Fulfillment would steal by scaling Storefront. It is not portfolio showback. Chapter 11 owns floors, ceilings, and unit economics. Chapter 6 must already deny unlimited burst into a peer tenant’s lease. Chapter 3 already denied `unlimited-burst-into-peer-quota`. The lease makes that denial a product check.

`dev-cluster-admin` is not a new role to productize. It is `cluster-admin` wearing a non-prod badge. Forbidden roles on the environment product include both.

## 3. Offer the environment product

The completed Chapter 6 model uses three files:

```text
environments/product.yaml
environments/requests.yaml
environments/leases.yaml
```

The separation is deliberate. The product names the job, shared plane, quota pool, credential model, forbidden roles, and TTL. Requests are the intake. Leases are the granted instances. The evaluator joins them to Chapter 3 tenants and the inherited identity interface.

> **Practice — Bind the product to the job and the inherited identity**
>
> Consume `kubernetes-control-plane`, `cluster-capacity-pool`, and short-lived federated identity rather than inventing new names for the same surfaces.

Open `environments/product.yaml`:

```yaml
job: obtain-bounded-environment
shared_plane: kubernetes-control-plane
quota_pool: cluster-capacity-pool
credential_model: short-lived-federated
forbidden_roles: [cluster-admin, dev-cluster-admin, platform-operator]
ttl_hours: 168
```

The evaluator loads `inherited/devops-v1.1/identity/interface.yaml` and fails the product if federated identity is replaced by a referenced rotatable secret. It fails if the shared plane or quota pool is renamed.

> **Practice — Request a tenant environment that already exists in the inventory**
>
> Fulfillment asks for `fulfillment-nonprod`, not a new namespace string.

Open `environments/requests.yaml`. The requester must be the Chapter 3 tenant owner. A request from Fulfillment for `storefront-nonprod` is already a cross-tenant act.

> **Practice — Issue a lease with expiry, bound quota, and tenant-scoped claims**
>
> Keep Storefront’s credentials unusable as Fulfillment, and keep Fulfillment unable to mutate Storefront’s lease.

Open `environments/leases.yaml`. Fulfillment’s non-production lease is:

```yaml
- id: lease-fulfillment-nonprod
  request: request-fulfillment-nonprod
  tenant: fulfillment
  environment: fulfillment-nonprod
  granted_role: tenant-operator
  expires_at: "2026-08-23T00:00:00Z"
  quota:
    pool: cluster-capacity-pool
    units: 4
  credentials:
    subject: fulfillment-nonprod
    issuer: northwind-workload-identity
    audience: kubernetes-control-plane
    expiry: "2026-08-23T00:00:00Z"
    policy: tenant-scoped
  isolation:
    network: tenant-default-deny
    secrets: tenant-scoped
```

There is no `mutated_by` from another tenant. There is no `dev-cluster-admin`. Network is not `peer-tenant-workload-network`; the evaluator joins that denial from `tenancy/isolation.yaml` rather than copying the id. Secrets are not `peer-tenant-secret-read`. The lab does not provision a real namespace or **VPC (Virtual Private Cloud)**. Completeness is whether the lease keeps those invariants.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-06-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 06 checkpoint: tenant-scoped leases and isolation invariants verified
```

The audit validates the three Chapter 6 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- the product names `obtain-bounded-environment` and inherited federated identity;
- shared plane and quota pool reuse Chapter 3 identifiers;
- required leases exist for `storefront-nonprod` and `fulfillment-nonprod`;
- each lease binds a request, a known tenant, and an inventoried environment;
- granted roles are not `cluster-admin` or `dev-cluster-admin`;
- `mutated_by` cannot be another tenant’s owner;
- expiry is present and unreclaimed leases are not past `as_of`;
- quota is bound on `cluster-capacity-pool`;
- credentials carry inherited claims, tenant-scoped subjects, and plane audience; and
- network and secrets are not in Chapter 3 `denied_inheritance`.

The expected identifiers and `as_of` live in a separate checkpoint file. A lease under test does not emit its own passing isolation status.

The checkpoint does not prove that a real cluster created a namespace, that a real identity provider issued the claims, or that a real network policy blocked traffic. Those remain claims a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 6 evidence |
|---|---|
| Mechanism evidence | Schemas and the lease-state evaluator operated successfully. |
| Decision evidence | Job, plane, pool, TTL, forbidden roles, and isolation invariants are explicit. |
| Outcome evidence | Fulfillment has a computed lease for `fulfillment-nonprod` with no shared env-admin. That is not proof a production namespace exists. |
| Recovery evidence | Not produced. A denied cross-tenant scale is an isolation invariant, not restored tenant isolation after a live steal. |

Chapter 6 produces mechanism, decision, and limited outcome evidence for `obtain-bounded-environment`. Pretending the local checkpoint proves `time-to-first-environment` in a real cluster would weaken Chapters 10 and 11.

## 4. Test the design under failure

### Cumulative product failure — A shared "dev cluster admin" still lets Fulfillment scale Storefront's environment to steal quota

> **Practice — Deny cross-tenant mutation and shared env-admin**
>
> Inject a Fulfillment scale onto the completed Storefront lease and refuse the invariant.

The completed product is healthy. The failure command does not rewrite it. It injects the residual shared-admin case against that snapshot:

```bash
make chapter-06-failure
```

Expected output:

```text
chapter 06 failure: cross-tenant environment scale correctly rejected
```

The injected record is:

```yaml
environment: storefront-nonprod
granted_role: dev-cluster-admin
mutated_by: fulfillment-team
```

TTL, federated identity, and Fulfillment’s own lease stay current. The baseline’s missing expiry and secret-model drop are not required for this failure. Shared env-admin can appear after the product already looks complete. Cross-tenant mutation and `dev-cluster-admin` must both fail on their own terms.

**Severity:** high; every later quota, control-plane, and recovery conversation will optimize a shared environment instead of a tenant lease.  
**Plausible harm:** Fulfillment starves Storefront’s order path by scaling `storefront-nonprod`; Storefront credentials leak into Fulfillment; cluster-admin returns as “just non-prod.”  
**Potential blast radius:** both application tenants and the shared `cluster-capacity-pool`; Storefront’s order path is no longer a separate failure domain.  
**Bounded by:** Chapter 3 tenant inventory and prohibited roles, inherited federated identity, and lease TTL. None of those repair a product that still grants `dev-cluster-admin`.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence.

#### Platform questions

- **User and job:** Fulfillment must finish `obtain-bounded-environment`. Scaling Storefront’s namespace with `dev-cluster-admin` is not that job; it is shared authority substituting for a lease.
- **Isolation:** The boundary is the Chapter 3 tenant plus this lease: environment id, tenant-scoped credentials, quota bound on `cluster-capacity-pool`, default-deny network, tenant-scoped secrets, and no cross-tenant `mutated_by`. Fulfillment’s blast radius must stop at Fulfillment.
- **Contract and exit:** The contract is the environment product and the lease. Teams leave an environment when the lease expires and is reclaimed, not by holding `dev-cluster-admin`. A paved-road exit is a different contract; this chapter does not replace it.
- **Platform-product evidence:** A created namespace is not proof the product works. Required later proof is `time-to-first-environment` inside this lease. This is not a portfolio **SLO (Service Level Objective)**.

#### Diagnosis

Calling the grant “dev cluster admin” encourages the same unofficial path Chapter 3 interrupted: Fulfillment is blocked, someone shares environment authority, Storefront’s quota moves, and the order path becomes a noisy neighbor. The paved road then deploys into a shared blast radius. Self-service without a lease produces unbounded namespaces. Tickets without isolation produce the same sharing, only slower.

The missing TTL makes every environment durable by accident. The missing federated identity makes credentials something Storefront and Fulfillment can copy. The missing quota bound makes `cluster-capacity-pool` a slogan. Shared env-admin makes Chapter 3’s prohibited inheritance ornamental.

#### Correction

The completed model does not grant `dev-cluster-admin`. Fulfillment receives `fulfillment-nonprod` through a request and a tenant-operator lease with expiry, bound quota, federated claims, and default-deny isolation. Storefront’s lease cannot be mutated by `fulfillment-team`. Isolation is recorded as a product invariant. Unreclaimed expiry fails. Cross-tenant secret and network sharing fail.

This failure is a lease-isolation invariant. It is not a runtime plane recovery. Do not call the denied scale **Evidence of restored isolation**. Nothing tenant-runtime was restored from a live steal. The product stopped treating shared env-admin as provisioning.

That correction changes later decisions:

- Chapter 7 must offer infrastructure contracts inside these leases, not modules that recreate shared namespaces.
- Chapter 8 must bind plane subjects that tenants still may not inherit; `dev-cluster-admin` is not a plane role.
- Chapter 11 must allocate floors and ceilings against `cluster-capacity-pool` without renaming it.
- Chapter 14 must recover the shared plane without replaying one tenant’s lease into another.

The design is practical because the denied mutation is the product. Adding an arbitrary cluster-provision command would not make it more practical.

## 5. Production reality

### Common environment-product errors

#### Renaming cluster-admin to dev-cluster-admin

Non-prod is not a different blast-radius physics. Forbidden is forbidden.

#### Creating namespaces that are not in the tenant inventory

A new string is how unbounded environments start. Use Chapter 3’s environment ids.

#### Issuing credentials that outlive the lease

A dead lease with a live secret is a stolen identity waiting for a user.

#### Treating TTL as optional on production

Durable is a longer lease, not an immortal namespace.

#### Using Storefront’s order metrics as environment health

Green orders can hide Fulfillment waiting on a ticket, or Fulfillment scaling Storefront. Platform-product evidence is a tenant-scoped lease.

#### Building a quota program in this chapter

Bound the lease. Leave floors, showback, and unit economics to Chapter 11. Do not invent a second pool name.

## 6. What changed

| Before | After |
|---|---|
| Fulfillment scaled Storefront with `dev-cluster-admin`. | **Cross-tenant mutation and shared env-admin fail the lease invariant.** |
| Environments were tickets or unbounded namespaces. | **A request creates a tenant-scoped lease with TTL.** |
| Credentials were copyable secrets. | **Leases consume inherited federated identity with tenant-scoped claims.** |
| Quota was the shared cluster. | **Each lease is bound on `cluster-capacity-pool`.** |
| Isolation was a namespace label. | **Network default-deny and tenant-scoped secrets are lease fields.** |
| A valid schema could appear to prove a provisioner. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has an environment product that later chapters can contract, reconcile, meter, and recover without treating shared env-admin as self-service.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Environment product contract | `environments/product.yaml` | It retains the job, shared plane, quota pool, federated identity, forbidden roles, and TTL later quota and plane chapters must not rename. |
| Lease and isolation evidence | `environments/leases.yaml` | It retains tenant-scoped expiry, quota bounds, credentials, and the invariant that Fulfillment cannot mutate Storefront. |

These artifacts should change when Northwind’s tenants, environment classes, or inherited identity model materially change—not whenever a namespace prefix is restyled.

## What You Learned

An environment is a leased instance of a tenant with expiry, bound quota, and tenant-scoped identity. `dev-cluster-admin` is shared authority. Schema checks can prove structural completeness within declared scope. They cannot prove a real cluster provisioned a namespace. A design earns its place when Fulfillment can obtain `fulfillment-nonprod` without scaling Storefront.

### Prove It

> **Independent Practice — Lease a read-only analytics environment without copying Fulfillment**
>
> A data-analytics team needs a bounded read environment for order events and must not consume Storefront credentials or inherit `dev-cluster-admin`.

Extend the Chapter 6 model without adding infrastructure-contract policy yet:

1. Decide whether analytics uses a new Chapter 3 tenant and environment id, or a bounded class of Storefront.
2. Name TTL and quota so a forgotten analytics namespace cannot starve `cluster-capacity-pool`.
3. State which inherited identity claims still apply, and which Storefront credential must fail if presented.
4. Deny the network and secret sharing that would let analytics restart `storefront-api`.
5. Identify one observation that would falsify the lease—for example `mutated_by: analytics-team` on `storefront-prod`.
6. Explain which material change would trigger review of the environment product, not just one lease.

Do not copy the Fulfillment non-prod lease and rename it. Read-only analytics has different durability, secret, and change-authority consequences. Your durable output is the isolation decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 6 capability when you can explain why `dev-cluster-admin` is still shared authority, trace a lease to a request, a Chapter 3 environment, and inherited identity claims, describe evidence that would falsify isolation, distinguish structural validation from decision and outcome evidence, and explain what the baseline, checkpoint, and failure command do and do not prove.

## Next

Environments exist, but teams still own raw modules instead of versioned contracts. Isolated namespaces still require each team to compose storage, identity, and networking primitives.

Chapter 7 abstracts infrastructure behind reviewable contracts, so a tenant request binds to a version rather than to a hidden module.
