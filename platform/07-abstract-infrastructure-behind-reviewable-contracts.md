# Abstract Infrastructure Behind Reviewable Contracts

Chapter 6 leased `fulfillment-nonprod`. Fulfillment can obtain a bounded environment. That environment still asks the team to compose storage, identity, and networking primitives. Tickets return as module reviews. Copy-paste returns as Terraform addresses in the tenant request. Chapter 2 already productized environment provisioning and artifact promotion. A lease that still exposes the module is the same ticket queue with nicer YAML.

The production question is now:

> What contract can a team rely on without owning the underlying infrastructure modules?

Abstractions that hide too much become magic. Abstractions that hide too little recreate the ticket queue. This chapter records an infrastructure **API (Application Programming Interface)**: versioned capabilities, tenant parameters, hidden module internals, and a compatibility policy. Storefront and Fulfillment bind to a version. They do not name a Terraform resource. A module refactor that changes a tenant-visible field without a version bump is not an internal cleanup. It is an independent control failure that breaks Fulfillment silently.

## 1. A module that became the tenant API

A weak record says:

```yaml
capability: tenant-storage
version: "1.0"
tenant_parameters: [sku, size-gb]
parameters:
  class: small
  terraform-resource-address: google_storage_bucket.storefront
```

It does not identify a tenant-visible field list Fulfillment can keep sending, a hidden-module boundary, a compatibility rule for rename, or inherited federated identity. “We refactored the module” may be true in the platform repo. Fulfillment still sends `class`. The request now includes a Terraform address. The network request can name `peer-tenant-workload-network`. Compatibility does not call parameter rename breaking.

Work from the lab working tree using the Chapter 0 procedure. From the Platform lab root, run the Chapter 7 baseline:

```bash
make chapter-07-baseline
```

The command succeeds when it detects the intended unsafe contracts:

```text
chapter 07 baseline: leaked module internals and silent field rename correctly detected
```

The fixture lets Storefront bind `terraform-resource-address`, silently renames storage `class` to `sku` while Fulfillment still sends `class`, replaces inherited short-lived federated identity with a referenced rotatable secret, lets Fulfillment bind Chapter 3’s denied `peer-tenant-workload-network`, and names no breaking parameter changes. Isolated environments exist. The primitives are still the product.

That substitution drives the chapter.

## 2. The production model: a versioned contract, not a module checkout

> *Theory — Infrastructure API*
>
> This model enables Fulfillment to request storage, identity, network, and promotion inside a Chapter 6 lease by binding a contract version, without owning the module that implements it.

### A contract is the tenant API; the module is not

An infrastructure contract names a capability, a version, the parameters a tenant may set, and the module fields the tenant must not set. Platform-owned modules implement the version. Tenant parameters are the supported request. Hidden internals—Terraform resource addresses, provider projects, **CNI (Container Network Interface)** plugin config, **IAM (Identity and Access Management)** role ARNs, **OIDC (OpenID Connect)** thumbprints, registry credentials—are how the platform keeps the promise. They are not a second API.

The Northwind catalog productizes four capabilities tenants already need to finish jobs:

| Capability | Tenant parameters | Hidden on purpose |
|---|---|---|
| `tenant-storage` | `class`, `size-gb` | Terraform address, provider project |
| `workload-identity` | `subject` | OIDC thumbprint, IAM role ARN |
| `tenant-network` | `isolation` | CNI config, security-group id |
| `artifact-promotion` | `artifact-digest` | registry credentials, Helm release name |

Those are not new jobs. Storage and network sit inside `obtain-bounded-environment`. Identity and promotion already exist as inherited DevOps interfaces. The contract is how a team relies on them without composing the modules.

Hiding every field creates magic: Fulfillment cannot tell what they requested, and support cannot tell what broke. Publishing every field recreates the ticket queue: every module refactor becomes a tenant outage or a review of internals. The supported surface is the versioned parameter list. Leaving a contract is a new version plus a migration note, not a paved-road exit and not an exception to digest identity.

### Compatibility is a policy, not a changelog comment

Adding, removing, or renaming a tenant parameter is breaking. A hidden-module refactor is not. Breaking changes require a new version and a migration note. Recording a rename against the only live version, with no note, is how Fulfillment keeps sending `class` after the module now expects `sku`.

**Production Practice:** Some organizations treat additive optional parameters as non-breaking. Northwind's policy is stricter because tenant requests must fully describe the accepted surface for a given version.

The evaluator does not trust a comment in the module. Completeness is computed: bindings must use declared tenant parameters; hidden keys must not appear in the request; a breaking change on a single version fails.

**Best Practice:** Bind each tenant request to a capability version. A request that cannot name its version is still composing primitives.

**Production Practice:** Isolation is a contract constraint, not a new tenancy model. Chapter 3 already denied `peer-tenant-workload-network`. This chapter loads that `denied_inheritance` list. A tenant-network binding may not reintroduce it.

### Inherited interfaces stay tenant-visible

The inherited DevOps release interface promotes by `artifact_digest`. The inherited identity interface is short-lived federated identity. `artifact-digest` belongs in tenant parameters, not in `hidden_module`. Workload identity must keep the federated credential model. Dropping either to make the module “simpler” is the unofficial path from Chapter 5 wearing an infrastructure coat.

Chapter 8 will reconcile these versions. This chapter must not invent a cluster operator so the contract looks applied. Chapter 11 will meter `cluster-capacity-pool`. This chapter must not invent a second pool so storage `class` looks like quota.

## 3. Publish the contract catalog

The completed Chapter 7 model uses three files:

```text
contracts/catalog.yaml
contracts/versions.yaml
contracts/compatibility.yaml
```

The separation is deliberate. The catalog names capabilities, owners, and tenant bindings. Versions name the tenant-visible fields and the hidden module. Compatibility names what is breaking and records changes. The evaluator joins them to Chapter 3 tenants, Chapter 3 isolation, and the inherited release and identity interfaces.

> **Practice — Bind tenants to versions, not to modules**
>
> Consume Chapter 3 environment ids and keep Terraform addresses out of the request.

Open `contracts/catalog.yaml`. Storefront and Fulfillment bind `storefront-nonprod` and `fulfillment-nonprod` to `tenant-storage` `1.0` with `class` and `size-gb`. They do not name `terraform-resource-address`.

> **Practice — Keep inherited identity and artifact-digest on the tenant surface**
>
> A contract that hides digest promotion or replaces federated identity has left the inherited delivery path.

Open `contracts/versions.yaml`. Workload identity stays `short-lived-federated` with tenant parameter `subject`. Artifact promotion keeps `artifact-digest` as a tenant parameter. Storage hides the Terraform address. Network hides CNI config.

> **Practice — Treat parameter rename as breaking**
>
> Hidden-module refactors may stay on the same version. Tenant-visible add, remove, and rename may not.

Open `contracts/compatibility.yaml`. Breaking kinds are `tenant-parameter-add`, `tenant-parameter-remove`, and `tenant-parameter-rename`. `hidden-module-refactor` may proceed without a bump. The completed catalog has no in-place breaking change to record.

The lab does not apply a real Terraform or Helm module. Completeness is whether Fulfillment can bind a version whose tenant fields remain stable, and whether a silent rename fails.

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
chapter 07 checkpoint: versioned infrastructure contracts and compatibility verified
```

The audit validates the three Chapter 7 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- required capabilities exist and have living Chapter 1 owners;
- bindings use Chapter 3 tenants and inventoried environment ids;
- binding parameters are declared tenant parameters, not hidden module keys;
- workload identity keeps inherited federated identity;
- artifact promotion keeps inherited `artifact-digest` on the tenant surface;
- tenant-network values are not in Chapter 3 network `denied_inheritance`;
- compatibility names parameter add, remove, and rename as breaking; and
- a breaking change on a single version, or without a migration note, fails.

The expected capabilities, environments, and breaking kinds live in a separate checkpoint file. A contract under test does not emit its own passing grade.

The checkpoint does not prove that a real module created a bucket, that a real identity provider issued a federated subject, or that a real CNI enforced default-deny. Those remain claims a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 7 evidence |
|---|---|
| Mechanism evidence | Schemas and the contract-compatibility evaluator operated successfully. |
| Decision evidence | Capabilities, tenant parameters, hidden internals, and breaking kinds are explicit. |
| Outcome evidence | Fulfillment has a computed binding to `tenant-storage` `1.0` without a Terraform address. That is not proof a bucket exists. |
| Recovery evidence | Not produced. A denied silent rename is a compatibility-contract failure, not restored tenant isolation after a live module outage. |

Chapter 7 produces mechanism, decision, and limited outcome evidence for an infrastructure API inside existing leases. Pretending the local checkpoint proves Terraform apply in a real cloud would weaken Chapter 8’s reconciler.

## 4. Test the design under failure

### Independent control failure — A module refactor changes a tenant-visible field without a contract version, breaking fulfillment silently

> **Practice — Fail compatibility before Fulfillment discovers the rename in production**
>
> Inject a `class` → `sku` rename onto the completed storage contract and refuse the in-place break.

The completed contracts are healthy. The failure command does not rewrite them. It injects the silent-refactor case against that snapshot:

```bash
make chapter-07-failure
```

Expected output:

```text
chapter 07 failure: silent tenant-parameter rename correctly rejected
```

The injected record is:

```yaml
capability: tenant-storage
version: "1.0"
tenant_parameters: [sku, size-gb]
changes:
  - capability: tenant-storage
    version: "1.0"
    kind: tenant-parameter-rename
    from_field: class
    to_field: sku
```

Fulfillment’s binding still sends `class`. Identity, network isolation, artifact-digest, and Storefront’s other bindings stay current. The baseline’s leaked Terraform address, dropped federated identity, denied network join, and missing breaking policy are not required for this failure. A module refactor can happen after the catalog already looks complete. Breaking without a version, a missing migration note, and the stale `class` parameter must all fail on their own terms.

**Severity:** high; every later reconcile, guardrail, and support conversation will apply a contract Fulfillment can no longer satisfy.  
**Plausible harm:** `fulfillment-api` cannot obtain storage; Storefront appears healthy on `sku`; the platform debugs a “tenant misconfiguration” that was a silent API change.  
**Potential blast radius:** every tenant still bound to `tenant-storage` `1.0`, plus any workload that assumed `class` remained the request.  
**Bounded by:** Chapter 3 environment ids, Chapter 6 leases, inherited federated identity, and the compatibility policy. None of those repair a version that changed its tenant fields in place.  
**Primary principles:** explicit contracts, blast-radius control, trustworthy evidence.

#### Platform questions

- **User and job:** Fulfillment must finish `obtain-bounded-environment` with storage, identity, and network it can request. Sending a Terraform address, or discovering `sku` only after a module merge, is not that job.
- **Isolation:** The boundary is still Chapter 3’s tenant plus this contract constraint: a tenant-network binding must not reintroduce `peer-tenant-workload-network`. This chapter does not invent a new tenancy model. Isolation is applicable as a denied sharing join, not as a recovered live network.
- **Contract and exit:** The contract is the versioned infrastructure API. Teams leave a version by binding a new version with a migration note, not by forking the module. A paved-road exit is a different contract; this chapter does not replace it. An exit is not an exception to digest identity.
- **Platform-product evidence:** A successful Terraform apply is not proof the product works. Required later proof is a tenant request bound to a named version whose compatibility still holds. This is not a portfolio **SLO (Service Level Objective)**.

#### Diagnosis

Calling the change an internal refactor encourages module controls: rename the field, keep version `1.0`, skip the tenant note. Fulfillment’s request still says `class`. Storefront may already speak `sku` because the platform team tested the new module. Compatibility that does not name rename as breaking cannot fail. Support sees a tenant error. The catalog still looks versioned.

The leaked Terraform address makes every module path a tenant API. The dropped federated model makes identity something teams copy again. The denied network value makes Chapter 3’s isolation ornamental. The missing bump makes the version string a label, not a contract.

#### Correction

The completed model does not rename `class` to `sku` on `1.0`. Tenant-visible rename is breaking. It requires another version and a migration note. Bindings that still send `class` fail until they move. Hidden-module refactors may stay on `1.0`. Parameter rename may not. Completeness is computed. The failure command proves the check still fails when only storage fields change and identity stays federated.

This failure is a compatibility-contract failure. It is not a runtime plane recovery. Do not call the denied rename **Evidence of restored isolation**. Nothing tenant-runtime was restored from a live module outage. The product stopped treating an in-place field change as an internal cleanup.

That correction changes later decisions:

- Chapter 8 must reconcile these versions with a tenant-scoped plane subject; it must not apply a hidden field Fulfillment never requested.
- Chapter 9 must bind remaining guardrails to inherited defaults, not to Terraform internals.
- Chapter 12 must treat a contract version bump as a fleet change, not a silent module merge.
- Chapter 13 must debug a failed binding as a product incident when the version moved under the tenant.

The design is practical because the failed compatibility check is the product. Adding an arbitrary Terraform apply would not make it more practical.

## 5. Production reality

### Common infrastructure-contract errors

#### Publishing the module as the request

`terraform-resource-address` in a tenant binding is the ticket queue. Hide the address; version `class` and `size-gb`.

#### Renaming a tenant field without a bump

`class` → `sku` on the same version is how Fulfillment breaks silently. Add a version and a migration note.

#### Treating hidden-module refactors as breaking, or tenant renames as not

The first recreates magic and endless version churn. The second recreates outages. Name both in policy.

#### Reintroducing `peer-tenant-workload-network` as an isolation parameter

Chapter 3 already denied it. Join that list. Do not hardcode a second copy and hope it stays true.

#### Dropping federated identity or hiding `artifact-digest`

Those are inherited delivery contracts. They are tenant-visible on purpose.

#### Building the reconciler in this chapter

Contracts are the API. Chapter 8 operates the plane that applies them. Do not grant cluster-admin so the YAML looks live.

## 6. What changed

| Before | After |
|---|---|
| Fulfillment sent `class` after a silent `sku` rename. | **In-place tenant-parameter rename fails compatibility.** |
| Storefront bound a Terraform address. | **Hidden module internals are not tenant API.** |
| Each team composed storage, identity, and network primitives. | **Tenants bind Chapter 3 environments to versioned capabilities.** |
| Compatibility was a module changelog. | **Add, remove, and rename of tenant parameters are breaking and need a migration note.** |
| Identity and digest could disappear into the module. | **Contracts consume inherited federated identity and `artifact-digest`.** |
| A valid schema could appear to prove Terraform applied. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has an infrastructure contract catalog that later chapters can reconcile, guard, and support without treating a module refactor as the tenant API.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Infrastructure contract catalog | `contracts/catalog.yaml` and `contracts/versions.yaml` | They retain capability versions, tenant parameters, and hidden internals later reconcilers must not promote into the tenant API. |
| Compatibility policy | `contracts/compatibility.yaml` | It retains the rule that tenant-visible add, remove, and rename require a version and a migration note. |

These artifacts should change when Northwind’s tenant-visible infrastructure API materially changes—not whenever a module is restyled behind the same version.

## What You Learned

An infrastructure contract is a versioned tenant API with hidden modules, compatibility rules, and inherited identity and artifact constraints. A silent field rename on `1.0` is a break, not a cleanup. Schema checks can prove structural completeness within declared scope. They cannot prove a real Terraform or Helm apply. A design earns its place when Fulfillment can bind `tenant-storage` `1.0` without owning the module, and when an in-place rename fails.

### Prove It

> **Independent Practice — Version a tenant-cache contract without copying the storage rename**
>
> A data-analytics path needs bounded object cache in `storefront-nonprod` and must not receive Storefront’s Terraform state or Fulfillment’s storage `class`.

Extend the Chapter 7 model without adding a control-plane reconciler yet:

1. Decide whether cache is a new capability or a parameter class of `tenant-storage`.
2. Name tenant parameters and hidden module fields so a cache refactor cannot become the request.
3. State which inherited identity and artifact fields still apply, and which Chapter 3 network value must fail if bound.
4. Choose what is breaking versus `hidden-module-refactor` when cache `tier` is later renamed to `sku`.
5. Identify one observation that would falsify the contract—for example a binding that still sends `tier` after version `1.0` only lists `sku`.
6. Explain which material change would trigger review of the compatibility policy, not just one binding.

Do not copy the storage `class` → `sku` row and rename it. Cache has different durability, eviction, and isolation consequences than block storage. Your durable output is the version-and-compatibility decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 7 capability when you can explain why a module field is not a tenant API, trace a binding to a version, Chapter 3 environment, and inherited interface, describe evidence that would falsify compatibility, distinguish structural validation from decision and outcome evidence, and explain what the baseline, checkpoint, and failure command do and do not prove.

## Next

Contracts exist, but the shared reconciler that applies them is still an unofficial cluster operator. A single controller still runs with broad authority and no tenant-scoped subject.

Chapter 8 operates a shared control plane as a product, so reconciliation cannot become shared root.
