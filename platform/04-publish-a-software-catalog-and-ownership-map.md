# Publish a Software Catalog and Ownership Map

Chapter 3 defined tenants and prohibited cluster-admin. Isolation exists on paper. It does not answer the production question:

> How do teams find the service, owner, dependencies, and support path without asking the platform group?

Ownership still lives in chat history and stale READMEs. An incident or a dependency change cannot find an owner. Orphan services accumulate. Chapter 2 already productized `software-catalog` against `publish-owned-path`, with review trigger `team-rename-or-new-system`. A wiki that still reports green after a rename is not that product.

This chapter publishes catalog entries for Storefront, Fulfillment, and the platform products those teams consume. The catalog is a contract: every runnable system has a living owner, an escalation contact, a dependency list, and a failed check when metadata is stale. Later chapters will pave a path and lease environments against these owners. They must not treat a homepage as the map.

## 1. A green catalog with a deleted owner

A weak record says:

```yaml
system: fulfillment-api
owner: fulfillment-legacy-group
escalation: chat-history
last_reviewed_at: "2025-12-01T00:00:00Z"
reported_status: green
```

It does not identify a living Chapter 1 user, a Chapter 3 tenant, an escalation path that can be paged, or a review timestamp inside the freshness window. “Green” may describe a portal page. It cannot complete an ownership decision. A renamed team that leaves a deleted group in the catalog is an orphan with a badge.

Work from the lab working tree using the Chapter 0 procedure. From the Platform lab root, run the Chapter 4 baseline:

```bash
make chapter-04-baseline
```

The command succeeds when it detects the intended unsafe catalog:

```text
chapter 04 baseline: deleted-group green catalog correctly detected
```

The fixture keeps Storefront owned and current, leaves `fulfillment-api` owned by `fulfillment-legacy-group`, stamps that ownership in the previous year, and still reports green. The catalog has operated. The job has not.

That substitution drives the chapter.

## 2. The production model: catalog as contract, not wiki

> *Theory — Software catalog*
>
> This model enables Northwind to find a living owner and a dependency path without opening an orientation ticket, and to fail the catalog when those facts go stale.

### A catalog is a system of record, not a page that launched

A software catalog is the contract for who owns a runnable system, how to escalate, what it depends on, and whether that metadata is still true. It is not a developer-portal homepage. Chapter 1 already refused `portal-launch` as success evidence. `publish-owned-path` names `catalog-freshness` as later proof. A published page without freshness is the same vanity in a different coat.

Mechanism evidence is that an entry exists. Decision evidence is that a living owner, tenant, and review timestamp were assigned. Outcome evidence would be that a team finished a job using that map. This chapter produces the first two. It does not prove a real portal search or HR directory.

### An owner is living, or the entry is incomplete

A living owner is a Chapter 1 user who still exists. `fulfillment-team` is living. `fulfillment-legacy-group` is not. Escalation is a contact that can be reached when the owner is not at the keyboard. Lifecycle status (`active` or `deprecated`) is not a substitute for ownership. A deprecated system still needs someone who can answer.

The catalog must not emit its own passing grade. Completeness is computed from living ownership, escalation, dependencies, tenant binding, and `last_reviewed_at` against an independent `stale_before` expectation. `reported_status: green` is a claim. If the owner is dead or the timestamp is stale, that claim fails.

**Best Practice:** Bind each runnable system to a Chapter 3 tenant whose owner matches the catalog owner.

**Production Practice:** A rename is a catalog event. Chapter 2’s review trigger `team-rename-or-new-system` is tested here: the old group must fail, not remain green.

### Dependencies are how blast radius is discovered

An incident that cannot name dependencies cannot name who else to call. `storefront-api` depends on `order-worker` and PostgreSQL. `fulfillment-api` depends on warehouse dispatch. Platform products may have an empty list when they do not ride a tenant data path; they still need the field. `environment-provisioning` depends on `kubernetes-control-plane`, the shared surface Chapter 3 already named. Do not invent a second identifier for the same plane.

A missing dependency list is an incomplete entry. An invented “the platform” dependency is not a list.

### Stale metadata is a failed contract, not a warning

If `last_reviewed_at` is older than the independent freshness window, the entry is stale. If the owner is not living, the entry is incomplete even when the timestamp is current. A team rename can produce exactly that: someone “reviewed” the page yesterday and left the deleted group in place. Freshness without a living owner is still an orphan.

This failure is a catalog-contract failure. It is not a runtime isolation event that needs containment and plane recovery. The control is that the entry cannot be complete. Do not call a failed check **Evidence of restored isolation**. Nothing tenant-runtime was restored. The catalog stopped lying.

## 3. Publish Northwind's catalog

The completed Chapter 4 model uses three files:

```text
catalog/systems.yaml
catalog/ownership.yaml
catalog/dependencies.yaml
```

The separation is deliberate. Systems name kind, lifecycle, and tenant. Ownership names living owner, escalation, and review time. Dependencies name what an incident must also find. The evaluator joins them. No file may declare itself green.

> **Practice — Register runnable systems against tenants**
>
> Put Storefront and Fulfillment services in the catalog with Chapter 3 tenant ids, and register the platform products Chapter 2 accepted.

Open `catalog/systems.yaml`. Fulfillment’s service is a tenant-scoped runnable system:

```yaml
- id: fulfillment-api
  kind: runnable-service
  lifecycle: active
  tenant: fulfillment
```

`software-catalog`, `environment-provisioning`, and `artifact-promotion` are `platform-product` entries. They have no tenant field. Chapter 3 refused to make the platform team a peer tenant; the catalog must not smuggle that tenant back in.

Inspect each runnable system with three questions:

1. Does its tenant exist in `tenancy/tenants.yaml`?
2. Would deleting this entry make an incident unable to find the service?
3. Is this a Northwind system, or a wiki section that names a category?

> **Practice — Assign living owners and escalation**
>
> Require a Chapter 1 user and a contact that is not chat history.

Open `catalog/ownership.yaml`:

```yaml
- system: fulfillment-api
  owner: fulfillment-team
  escalation: fulfillment-oncall
  last_reviewed_at: "2026-08-16T00:00:00Z"
```

There is no `reported_status`. The checkpoint computes whether the owner is living and whether `last_reviewed_at` is after `stale_before`. `fulfillment-team` must match the Chapter 3 owner of tenant `fulfillment`. A catalog that says Storefront owns `fulfillment-api` has drifted from isolation even if both teams are living.

> **Practice — Record dependencies the incident will need**
>
> Name what a service reaches, including the shared plane where the platform product consumes it.

Open `catalog/dependencies.yaml`. Runnable systems have a non-empty `depends_on` list. The environment product names `kubernetes-control-plane` rather than a new string for the same shared surface.

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
chapter 04 checkpoint: living owners, dependencies, and freshness verified
```

The audit validates the three Chapter 4 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- required systems `storefront-api`, `fulfillment-api`, and `software-catalog` exist;
- every system has ownership, escalation, and a dependency list;
- owners are living Chapter 1 users;
- runnable systems bind a known tenant whose owner matches;
- `last_reviewed_at` is not before the independent freshness window; and
- a green claim cannot survive a dead owner or a stale timestamp.

The expected identifiers and `stale_before` live in a separate checkpoint file. The catalog under test does not emit its own passing expectations.

The checkpoint does not prove that a real developer portal, identity provider, or HR system would return these owners. It cannot discover services that were never registered. Those remain later mechanism claims, and some of them a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 4 evidence |
|---|---|
| Mechanism evidence | Schemas and the catalog freshness evaluator operated successfully. |
| Decision evidence | Living owners, tenant bindings, escalation, dependencies, and review timestamps are explicit. |
| Outcome evidence | Later paved-road, support, and fleet chapters can be evaluated against these owners. Finding an entry is not yet proof a team finished `ship-on-paved-road`. |
| Recovery evidence | Not produced. A failed freshness check is a contract failure, not restored tenant isolation. |

Chapter 4 primarily creates mechanism and decision evidence for `publish-owned-path`. Pretending that the local checkpoint proves portal search, on-call routing, or job completion would weaken Chapters 5 and 13.

## 4. Test the design under failure

### Independent control failure — A renamed team leaves fulfillment-api owned by a deleted group while the catalog still reports green

> **Practice — Fail freshness and ownership before the entry can be complete**
>
> Inject a deleted-group owner onto a current catalog and refuse the green claim.

The completed catalog is healthy. The failure command does not rewrite it. It injects the renamed-team case against that snapshot:

```bash
make chapter-04-failure
```

Expected output:

```text
chapter 04 failure: catalog correctly rejected a deleted-group owner
```

The injected record is:

```yaml
system: fulfillment-api
owner: fulfillment-legacy-group
escalation: fulfillment-oncall
last_reviewed_at: "2026-08-16T00:00:00Z"
reported_status: green
```

The review timestamp is current. The baseline’s stale date is not required for this failure. A rename can happen on a page someone touched today. Living owner and green claim are independent checks. Both must fail here.

**Severity:** high; every later incident, paved-road, and support conversation will page a group that does not exist.  
**Plausible harm:** `fulfillment-api` becomes an orphan; Storefront cannot find a dependency owner; the platform remains the phone book.  
**Potential blast radius:** every consumer of `fulfillment-api` and every platform product that trusts this catalog as a system of record.  
**Bounded by:** Chapter 1 living users, Chapter 3 tenant owners, and the independent freshness window. None of those repair a catalog that is allowed to stay green.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Platform questions

- **User and job:** The user is the platform team finishing `publish-owned-path`, and the application teams who must find an owner without a ticket. A green page owned by `fulfillment-legacy-group` is not that job.
- **Isolation:** Catalog metadata is not a network policy. Chapter-local implication: `fulfillment-api` is a Fulfillment tenant system; its owner must be the living tenant owner. A deleted group cannot be the blast-radius owner Chapter 3 recorded.
- **Contract and exit:** The catalog contract is a living owner, escalation, dependencies, and computed freshness. A paved-road exit is not yet applicable. Teams cannot leave a path that has not been paved; they also cannot rely on a catalog that remains green after a rename.
- **Platform-product evidence:** `reported_status: green` is a self-emitted claim. Required proof is `catalog-freshness` computed against living owners. This is not a portfolio **SLO (Service Level Objective)**.

#### Diagnosis

Calling the catalog green because the portal rendered encourages wiki controls: update markdown, keep the badge, skip the identity of the owner. After a rename, `fulfillment-legacy-group` still looks complete. Chat history becomes the real escalation path. Chapter 2’s review trigger never fires because the page did not fail.

The missing living-owner check makes Chapter 1’s user register ornamental. The missing tenant match makes Chapter 3’s isolation owner a second, disagreeing record. The self-emitted green status makes the evaluator a display function.

#### Correction

The completed model does not let `fulfillment-api` report green under a deleted group. It requires a living Chapter 1 owner, a matching Chapter 3 tenant owner, escalation, dependencies, and a review timestamp inside the freshness window. Completeness is computed. The failure command proves the check still fails when only the owner is swapped and the timestamp stays current.

That correction changes later decisions:

- Chapter 5 must pave a path that names these system ids, not unofficial YAML copies with no owner.
- Chapter 12 must treat a team rename as a catalog freshness failure, not a fleet footnote.
- Chapter 13 must escalate to the living contact, not to chat history.
- Support and fleet change may not treat a green badge as proof the product is healthy.

The design is practical because the failed check is the product. Adding an arbitrary portal command would not make it more practical.

## 5. Production reality

### Common catalog errors

#### Treating the portal as the catalog

If the homepage disappeared, owners and dependencies should still be nameable. If they are not, there was no catalog.

#### Allowing the entry to emit green

A system of record that scores itself cannot be failed by a rename. Keep observations (`last_reviewed_at`, owner id) separate from expectations (`stale_before`, living users).

#### Copying Storefront ownership onto Fulfillment

A living owner on the wrong tenant is still an isolation error. Match `tenancy/tenants.yaml`.

#### Leaving platform products out because they are not services

`publish-owned-path` is a platform job. If the catalog product has no owner, the platform is again a ticket queue.

#### Using Storefront’s order metrics as catalog health

Green orders can hide an orphan `fulfillment-api`. Platform-product evidence is freshness and living ownership.

#### Skipping dependencies because “everyone knows”

The first incident is when everyone does not know. Record the list before it is needed.

## 6. What changed

| Before | After |
|---|---|
| `fulfillment-api` was owned by a deleted group and still green. | **Ownership requires a living Chapter 1 user; a green claim fails without one.** |
| Ownership lived in chat and stale READMEs. | **Owners, escalation, and review timestamps are catalog records.** |
| A namespace list stood in for a catalog. | **Runnable systems bind Chapter 3 tenants; platform products do not fake a platform tenant.** |
| Dependencies were tribal knowledge. | **Each runnable system names what an incident must also find.** |
| Freshness was a badge the page displayed. | **Freshness is computed against an independent `stale_before` expectation.** |
| A valid schema could appear to prove a living map. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a catalog contract that later chapters can pave, support, and rename against without treating a green homepage as ownership.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Catalog ownership map | `catalog/systems.yaml` and `catalog/ownership.yaml` | They retain living owners, tenant bindings, and escalation later support and fleet rename must not replace with a wiki. |
| Stale-entry failure contract | `catalog/ownership.yaml` plus the Chapter 4 evaluator | They retain the rule that a deleted group or a stale timestamp cannot remain complete. |

These artifacts should change when Northwind’s systems, owners, or team names materially change—not whenever a portal theme is redesigned.

## What You Learned

A software catalog is a contract for living owners, escalation, dependencies, and computed freshness. A green page owned by a deleted group is an orphan. Schema checks can prove structural completeness within declared scope. They cannot prove a real portal or HR system. A design earns its place when a rename fails the catalog instead of leaving it green.

### Prove It

> **Independent Practice — Handle a Storefront team rename without copying the Fulfillment row**
>
> `storefront-team` is renamed to `storefront-commerce`. The portal still shows green.

Extend the Chapter 4 model without adding a paved-road policy yet:

1. Decide which catalog fields must change besides the owner string.
2. State whether `storefront-api`, `order-worker`, and `notification-service` fail together or can drift independently.
3. Name the Chapter 1 and Chapter 3 records that must move with the rename.
4. Identify one observation that would falsify “the rename is complete”—for example a remaining `storefront-team` owner on `order-worker`.
5. Choose whether `reported_status: green` may exist at all during the rename.
6. Explain which material change would trigger review of the catalog contract itself.

Do not copy the Fulfillment deleted-group row and rename it. Storefront owns three runnable systems on one tenant; a partial rename is a different failure than one orphan service. Your durable output is the freshness decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 4 capability when you can explain why a green catalog is not a living owner, trace every required system to a known user and tenant, describe evidence that would falsify freshness, distinguish structural validation from decision and outcome evidence, and explain what the baseline, checkpoint, and failure command do and do not prove.

## Next

Teams can find systems, owners, and dependencies. Each still copies a private path to production. Storefront’s working path is tribal knowledge; Fulfillment copies YAML.

Chapter 5 builds a paved road teams can leave, so shipping does not require an unofficial fork or a golden cage.
