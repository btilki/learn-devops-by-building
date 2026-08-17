# Model Tenants, Teams, and Isolation Boundaries

Chapter 2 decided which capabilities the platform owns. Environment provisioning and artifact promotion are on the intake path. Custom pricing is not. Those decisions do not answer the second platform question:

> Where does one team's change, credential, or failure stop?

Without that answer, Storefront and Fulfillment share cluster-admin patterns and a namespace-as-name convention. A debug RoleBinding or a noisy workload can become every team's incident. Fulfillment can still inherit cluster-admin “temporarily” to ship `fulfillment-api`. The product brief forbids shared cluster authority. The cluster still offers it.

This chapter records tenants, isolation dimensions, allowed sharing, and the authority each role may never inherit. Later chapters provision environments, operate the control plane, allocate quota, and recover a plane failure against this model. They must not treat a namespace label as isolation.

## 1. An unsafe isolation model

A weak record says:

```yaml
id: fulfillment
namespace: fulfillment
role: cluster-admin
justification: temporary-to-ship-faster
```

It does not identify a tenant owner, isolation dimensions, prohibited inherited roles, or a blast-radius statement that stops at Fulfillment. “Temporarily” may justify a conversation. It cannot complete an isolation decision. A namespace name is a label. It is not a boundary.

Work from the lab working tree using the Chapter 0 procedure. From the Platform lab root, run the Chapter 3 baseline:

```bash
make chapter-03-baseline
```

The command succeeds when it detects the intended unsafe model:

```text
chapter 03 baseline: temporary cluster-admin inheritance correctly detected
```

The fixture grants Fulfillment cluster-admin to ship this week, leaves Storefront on the same unofficial path, treats `namespace-label` as the only isolation dimension, and does not deny cluster-admin as shared authority. Isolation has collapsed before the catalog exists. That is this book's cumulative product failure.

That collapse drives the chapter.

## 2. The production model: tenants, dimensions, and prohibited inheritance

> *Theory — Tenant isolation*
>
> This model enables Northwind to finish productized jobs inside an explicit blast-radius boundary rather than by sharing cluster-admin.

### A tenant is an isolation unit, not a namespace name

A tenant is a blast-radius boundary with an owner. Storefront is a tenant. Fulfillment is a tenant. The platform team is a user of the product, not a third application tenant. It operates the shared control plane; it does not live in `namespace: platform` as if that were isolation.

A team is the human owner of a tenant. An environment is a time-bounded instance of that tenant—non-production or production—that Chapter 6 will turn into a lease. A namespace, project, or account name may implement a tenant. It does not define one.

If isolation is “the namespace is called fulfillment,” a RoleBinding in that namespace, a credential copied from Storefront, or a debug grant on the cluster will ignore the name.

### Isolation is a set of dimensions, not a single wall

Northwind isolates on five dimensions. Each dimension names what may be shared, what may never be inherited, and where blast radius stops:

| Dimension | Stops | Must not be inherited |
|---|---|---|
| Identity | Who a credential can act as | Cross-tenant identity, cluster-admin |
| Network | Which services a workload can reach | Peer-tenant workload network |
| Quota | How much one tenant can consume | Unlimited burst into another tenant's floor |
| Secrets | Which credentials a tenant can read | Peer-tenant secret read |
| Change authority | What a tenant change can mutate | Cluster-admin, platform-operator, peer-tenant change |

A noisy neighbor is a quota and network failure: one tenant's load or chatter becomes another tenant's incident. Chapter 11 will allocate floors and ceilings. Chapter 3 must already deny unlimited burst and default-deny peer-tenant network. Otherwise later quota numbers decorate a shared cluster.

**Best Practice:** Write a blast-radius statement per tenant and per dimension. “The cluster” is not a statement. It is the failure.

**Production Practice:** A prohibited role is only real when a later binding that grants it fails. The Fulfillment cluster-admin grant is that test.

### Shared-nothing and shared-control-plane are different products

A **shared-nothing** platform gives each tenant its own cluster or account. Blast radius is cheap to explain and expensive to operate. Fleet upgrade, quota, and control-plane recovery become many planes.

A **shared-control-plane** platform lets tenants consume one plane as a product and denies them plane-admin. Blast radius depends on the dimensions above. Fleet upgrade, quota, and recovery become one plane that must not take every tenant down.

Northwind chooses shared-control-plane. That is why Chapter 8 can operate the plane as a product and Chapter 14 can recover it without taking Storefront and Fulfillment with it. Shared cluster-admin is not shared-control-plane. It is shared-nothing's opposite: one plane, no tenants.

The control-plane API may be shared. Cluster-admin may not. Tenant secrets may not. Peer-tenant change authority may not.

### Temporary inheritance is still inheritance

Fulfillment cannot finish `obtain-bounded-environment` today. Granting cluster-admin “until the environment product exists” makes the unofficial path the real path. Every later environment lease, paved-road default, and plane subject will have to unwind that grant. The cumulative product failure starts here: shared authority used as a shipping shortcut, collapsing isolation before the catalog exists.

The inherited DevSecOps authorization interface already forbids self-approval. It does not decide tenant blast radius. Platform tenancy must not treat a valid Storefront identity as authority to change Fulfillment, or a valid Fulfillment identity as cluster-admin.

## 3. Build Northwind's isolation model

The completed Chapter 3 model uses four files:

```text
tenancy/tenants.yaml
tenancy/isolation.yaml
tenancy/roles.yaml
tenancy/sharing.yaml
```

The separation is deliberate. Tenants name owners, environments, dimensions, prohibited roles, and blast radius. Isolation dimensions name allowed sharing and denied inheritance. Roles name what a principal may never inherit. Sharing names the plane and quota pool tenants may consume, and the authority they may not.

> **Practice — Name tenants as isolation units**
>
> Bind each tenant to a Chapter 1 owner and a blast-radius statement that does not mean the cluster.

Open `tenancy/tenants.yaml`. Fulfillment is recorded as:

```yaml
- id: fulfillment
  owner: fulfillment-team
  environments: [fulfillment-nonprod, fulfillment-prod]
  isolation_dimensions: [identity, network, quota, secrets, change-authority]
  prohibited_inherited_roles: [cluster-admin, platform-operator]
  blast_radius: fulfillment-workloads-and-warehouse-effects-only
```

Inspect each tenant with three questions:

1. Would a credential stolen in this tenant be able to act as Storefront?
2. Would a debug RoleBinding here be able to change the control plane?
3. Is the named owner a Chapter 1 user, or a namespace string?

Do not add a `platform` tenant to make the platform team look symmetric. The platform team operates the shared plane. Treating it as a peer tenant invites cluster-admin “for the platform namespace.”

> **Practice — Declare dimensions and denied inheritance**
>
> Make change authority deny cluster-admin, and make quota deny a noisy neighbor's unlimited burst.

Open `tenancy/isolation.yaml`. Change authority is the dimension the baseline collapsed:

```yaml
- id: change-authority
  allowed_sharing: none
  denied_inheritance: [cluster-admin, platform-operator, peer-tenant-change]
  blast_radius: a-tenant-change-cannot-mutate-another-tenant-or-the-control-plane
```

Network may share `kubernetes-control-plane`. Quota may share `cluster-capacity-pool`. Identity, secrets, and change authority share nothing. If a dimension's `allowed_sharing` names a surface that is not in `tenancy/sharing.yaml`, the graph is incomplete.

> **Practice — Bind tenant-scoped roles and deny cluster-admin as sharing**
>
> Replace inherited cluster-admin with tenant-operator, and record cluster-admin as denied sharing.

Open `tenancy/roles.yaml` and `tenancy/sharing.yaml`. Tenant-developer and tenant-operator both list `cluster-admin` under `never_inherit`. Bindings grant Storefront and Fulfillment `tenant-operator` inside their own tenant. Sharing records the Kubernetes control plane as `shared-control-plane` and lists `cluster-admin` under `denied`.

A justification of `temporary-to-ship-faster` does not change the graph. The evaluator rejects the grant, not the adverb.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-03-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 03 checkpoint: tenant isolation and prohibited inheritance verified
```

The audit validates the four Chapter 3 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- Storefront and Fulfillment exist with Chapter 1 owners;
- each tenant names the five isolation dimensions and prohibits cluster-admin;
- blast-radius statements are not aliases for the shared cluster;
- tenant-scoped roles may not inherit cluster-admin;
- no tenant binding grants cluster-admin;
- change authority denies cluster-admin;
- the control plane is shared as a product, not as cluster-admin; and
- sharing denies cluster-admin.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not prove that a real cluster, identity provider, or network policy enforces these boundaries. It cannot discover unknown sharing outside the declared model. Those are later mechanism claims, and some of them remain claims a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 3 evidence |
|---|---|
| Mechanism evidence | Schemas and the isolation-graph evaluator operated successfully. |
| Decision evidence | Tenants, dimensions, prohibited roles, bindings, and denied sharing are explicit and reviewed. |
| Outcome evidence | Later environment, control-plane, quota, and recovery chapters can be evaluated against these boundaries. |
| Recovery evidence | Not yet produced; later chapters must prove tenant isolation held after a real modeled failure. |

Chapter 3 primarily creates decision evidence. Pretending that the local checkpoint proves NetworkPolicies, quotas, or plane recovery already work would weaken every later chapter. Do not call this correction **Evidence of restored isolation**. Nothing runtime was restored. The model no longer grants the shared authority this book interrupts.

## 4. Test the model under failure

### Cumulative product failure — Fulfillment inherits cluster-admin "temporarily" to ship faster, collapsing isolation before the catalog exists

> **Practice — Replace inherited cluster-admin with tenant-scoped roles**
>
> Interrupt shared authority at the binding, not after Fulfillment has shipped on the unofficial path.

The baseline fixture contains this model:

```yaml
- id: fulfillment
  owner: fulfillment-team
  isolation_dimensions: [namespace-label]
  prohibited_inherited_roles: []
  blast_radius: the-cluster
bindings:
  - principal: fulfillment-team
    tenant: fulfillment
    role: cluster-admin
    justification: temporary-to-ship-faster
```

The problem is not merely missing fields. The model classifies a namespace label as isolation and a temporary grant as a shipping strategy. Storefront remains on the same unofficial path. Catalog, environments, and the control plane have nothing left to isolate.

**Severity:** high; every later environment, paved-road, quota, and recovery conversation will optimize a shared cluster instead of a tenant boundary.  
**Plausible harm:** a Fulfillment debug RoleBinding changes Storefront; a noisy workload becomes every team's incident; cluster-admin spreads as the way to finish `obtain-bounded-environment`.  
**Potential blast radius:** both application tenants and the shared control plane; Storefront's order path is no longer a separate failure domain.  
**Bounded by:** later environment leases, plane subjects, quota floors, and control-plane recovery. None repairs a tenancy model that already granted cluster-admin.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence.

#### Platform questions

- **User and job:** Fulfillment must obtain a bounded environment and ship on a paved road. Cluster-admin is not that job; it is shared authority substituting for the environment product Chapter 2 already accepted.
- **Isolation:** The boundary is the five dimensions and the prohibited inheritance of cluster-admin. A namespace label and a temporary grant are not that boundary. Fulfillment's blast radius must stop at Fulfillment workloads and warehouse effects.
- **Contract and exit:** Not yet applicable as a paved-road contract. Chapter-local implication: the isolation model is the authority contract a team can rely on. Teams cannot leave a path that has not been paved; they also cannot rely on a tenant product that still offers cluster-admin.
- **Platform-product evidence:** A successful grant is not proof the platform works. Required later proofs remain time-to-first-environment and paved-road completion inside this boundary. This is not a portfolio **SLO (Service Level Objective)**.

#### Diagnosis

Calling isolation a namespace name encourages namespace controls: create `fulfillment`, copy Storefront's RoleBindings, grant cluster-admin so the team is not blocked. Those steps can ship `fulfillment-api` this week. They make Storefront, Fulfillment, and the control plane one failure domain.

The missing prohibited role makes Chapter 1's promise ornamental. The missing change-authority dimension makes Chapter 6's lease a label on the same cluster. The missing denial of cluster-admin in sharing makes Chapter 8's plane subjects inherit the unofficial path. Shared authority is no longer a risk on a slide. It is the recorded way Fulfillment ships.

#### Correction

The completed model does not grant Fulfillment cluster-admin. It defines Storefront and Fulfillment as tenants with Chapter 1 owners, five isolation dimensions, prohibited inheritance of cluster-admin and platform-operator, tenant-scoped role bindings, shared-control-plane consumption without plane-admin, and a blast-radius statement that is not the cluster.

Record this grant-and-reversal as the cumulative product failure the rest of the book interrupts. Later chapters inherit the corrected boundary. They must not reintroduce cluster-admin as a shipping shortcut.

That correction changes later decisions:

- Chapter 4 may publish catalog owners because tenants now exist as isolation units, not because a namespace list looked like a catalog.
- Chapter 6 must lease environments inside these tenants; a lease that implies cluster-admin has left the model.
- Chapter 8 must bind plane subjects that tenants may not inherit.
- Chapter 11 must allocate quota against the noisy-neighbor denial already recorded here.
- Chapter 14 must recover the shared plane without replaying one tenant's authority into another.

The concept is practical because it changes the production contract across the rest of the book. Adding an arbitrary command would not make it more practical.

## 5. Production reality

### Common isolation errors

#### Treating the namespace as the tenant

A name is how humans find an object. Isolation is what a stolen credential, a RoleBinding, or a noisy process cannot cross.

#### Granting cluster-admin to unblock a second team

The second tenant is the teaching thread that makes tenancy real. If Fulfillment ships by inheriting Storefront's unofficial path, Northwind still has one tenant.

#### Making the platform team a peer tenant

Plane operators need plane-scoped authority in Chapter 8. They do not need a `platform` namespace that inherits cluster-admin “because it is the platform.”

#### Isolating network and ignoring change authority

Default-deny east-west traffic does not stop a RoleBinding. Change authority is the dimension this chapter's failure actually collapsed.

#### Declaring shared-control-plane while sharing cluster-admin

If tenants can administer the plane, you have a shared cluster, not a plane product.

#### Using Storefront's order metrics as isolation evidence

A green order path can hide Fulfillment cluster-admin. Platform-product evidence must describe tenant boundaries and later job completion inside them.

## 6. What changed

| Before | After |
|---|---|
| Fulfillment inherited cluster-admin to ship faster. | **Fulfillment is bound to tenant-operator; cluster-admin is prohibited and denied.** |
| Isolation was a namespace label. | **Isolation is identity, network, quota, secrets, and change authority.** |
| Blast radius was the cluster. | **Each tenant's blast radius stops at its workloads and effects.** |
| The plane was a shared cluster-admin path. | **The plane is a shared-control-plane product tenants may not administer.** |
| Temporary grants were a shipping strategy. | **Temporary inheritance is still inheritance and fails the graph.** |
| A valid schema could appear to prove isolation. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely four YAML files. Northwind now has a reviewable isolation contract that later chapters can lease, pave, measure, and recover without treating shared authority as the path.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Tenant-and-isolation model | `tenancy/tenants.yaml` and `tenancy/isolation.yaml` | They retain owners, dimensions, prohibited roles, and blast-radius statements later environments and recovery must not replace with namespace labels. |
| Role boundary map | `tenancy/roles.yaml` and `tenancy/sharing.yaml` | They retain tenant-scoped bindings and the denial of cluster-admin as shared authority. |

These artifacts should change when Northwind's tenants, isolation dimensions, or organizational authority materially change—not whenever a namespace is renamed.

## What You Learned

A tenant is an isolation unit with an owner, dimensions, prohibited inheritance, and a blast-radius statement. A namespace name is not that unit. Shared-control-plane is a product tenants consume without inheriting cluster-admin. Temporary cluster-admin is the cumulative product failure this book interrupts. Schema checks can prove structural completeness within declared scope. They cannot discover unknown real cluster sharing. A concept earns its place when it changes later production decisions, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Model a read-only analytics tenant without copying Fulfillment**
>
> A data-analytics team needs a bounded read environment for order events and must not ship on the order paved road.

Extend the Chapter 3 model without adding implementation policy yet:

1. Decide whether analytics is a new tenant or a bounded use of Storefront.
2. Name isolation dimensions that are not a copy of Fulfillment's warehouse-effects blast radius.
3. State what read sharing is allowed, and deny change authority on Storefront and cluster-admin.
4. Assign an owner from Chapter 1 or justify a new Chapter 1 user first.
5. Identify one observation that would falsify the boundary—for example a RoleBinding that can restart `storefront-api`.
6. Explain which material change would trigger review of your tenant record.

Do not copy the Fulfillment entry and rename it. Read-only analytics has different network, secret, and change-authority consequences. Your durable output is the isolation decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 3 capability when you can explain why a namespace label is not a tenant, trace every tenant to a known owner and prohibited cluster-admin inheritance, describe evidence that would falsify the blast-radius statement, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Isolation is defined. Teams still cannot discover owners, dependencies, or the paved road without asking the platform group. Ownership lives in chat history and stale READMEs.

Chapter 4 publishes a software catalog and ownership map so a tenant can find the path without inheriting a ticket queue.
