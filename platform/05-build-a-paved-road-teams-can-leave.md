# Build a Paved Road Teams Can Leave

Chapter 4 published owners and dependencies. Teams can find `fulfillment-api`. They still cannot ship it on a shared path. Storefront’s working path is tribal knowledge. Fulfillment copies YAML. Chapter 2 already productized artifact promotion against `ship-on-paved-road`. A catalog without a path leaves that job unfinished.

The production question is now:

> What supported path gets a team to production, and how do they leave it without becoming unsupported?

A mandatory golden path becomes a cage. An undocumented escape becomes shadow infrastructure. This chapter records a versioned paved-road contract, a scaffold that implements it, computed conformance, and a supported exit. The inherited DevOps release interface already requires promotion by `artifact_digest`. The unofficial fork that skips a slow template and promotes `latest` is not an exit. It is the connected consequence of offering a path without a way to leave it.

## 1. An unofficial fork of a tribal path

A weak record says:

```yaml
system: fulfillment-api
path: unofficial
defaults_present: [latest-tag]
```

It does not identify the Chapter 1 job, the inherited digest-promotion default, workload-identity claims, a scaffold that implements the path, or a registered exit. “We skipped the slow template” may justify a conversation. It cannot complete `ship-on-paved-road`. Identity and artifact defaults are gone. Support has nothing left to support.

Work from the lab working tree using the Chapter 0 procedure. From the Platform lab root, run the Chapter 5 baseline:

```bash
make chapter-05-baseline
```

The command succeeds when it detects the intended unsafe path:

```text
chapter 05 baseline: unofficial fork of the paved road correctly detected
```

The fixture drops inherited artifact-digest promotion from the contract, leaves the scaffold covering only a catalog entry, grants Fulfillment an unofficial `latest-tag` fork, and registers no exit. Storefront’s tribal YAML has become Fulfillment’s shadow path. That is a connected consequence of productizing a road without paving it, and of paving it without an exit.

That fork drives the chapter.

## 2. The production model: a contract you can complete and leave

> *Theory — Paved road and supported exit*
>
> This model enables Northwind to finish `ship-on-paved-road` with inherited identity and artifact defaults intact, and to leave the scaffold without becoming unofficial.

### A paved road is a product contract, not a mandate

A paved road is the default supported path to production. It names steps, defaults, a version, an owner, and a support level. It is not a golden cage. Every golden path needs a supported exit, an owner, and a review trigger.

The Northwind path is the job `ship-on-paved-road`. Its steps are:

1. a catalog entry from Chapter 4;
2. a digest-pinned artifact from the inherited DevOps release interface;
3. workload identity with the inherited required claims;
4. reviewed promotion of that digest.

Its defaults are `artifact-digest`, `workload-identity-claims`, and `no-cluster-admin`. Those defaults are not taste. `artifact-digest` is the inherited `promotion_identity`. Workload identity is the inherited short-lived federated model. `no-cluster-admin` is Chapter 3’s prohibited inheritance. A path that promotes `latest` has left the inherited delivery contract.

A scaffold implements the steps so a new service can complete the path. The lab does not generate a live repository. Completeness is whether the recorded path kept the defaults, not whether a template ran.

### An unofficial fork is not an exit

An exit is a reviewed, owned departure from the scaffold that still names lost defaults and remaining guardrails. An unofficial fork is an unreviewed departure that loses defaults and still asks the platform to debug the result.

| Treatment | What the team gets | What must remain |
|---|---|---|
| Paved | Scaffold, defaults, full path support | All contract defaults |
| Exited | Support without the lost scaffold defaults | Remaining guardrails |
| Unofficial | No product support | Nothing the platform can honestly promise |

You may leave the slow golden template. You may not leave digest promotion, workload identity, or the cluster-admin prohibition. Those remain guardrails on every path, including exits. Chapter 9 will bind them as defaults and exceptions. Chapter 5 must already refuse to treat them as optional template chrome.

**Best Practice:** Version the path. A team must be able to say which contract they completed or exited.

**Production Practice:** Completeness is computed. Conformance entries cannot emit a passing grade. `path: unofficial` always fails.

### The connected consequence is enabled by the earlier product

Fulfillment can now find the path in the catalog. Chapter 2 told them artifact promotion is a platform product. When the template is slow and there is no exit, they fork unofficially to ship `fulfillment-api`. That fork is not an independent accident. It is what a productized road without an exit produces: shadow infrastructure that drops the defaults the inherited delivery path required.

## 3. Pave the road and register an exit

The completed Chapter 5 model uses four files:

```text
paved-road/contract.yaml
paved-road/scaffold.yaml
paved-road/conformance.yaml
paved-road/exits.yaml
```

The separation is deliberate. The contract names the job, steps, and defaults. The scaffold names which steps it implements. Conformance records how each catalog system took the path. Exits name how a system left the scaffold without going unofficial.

> **Practice — Bind the path to the job and the inherited defaults**
>
> Make `ship-on-paved-road` consume digest promotion and workload identity rather than inventing a new identity for the same claims.

Open `paved-road/contract.yaml`:

```yaml
job: ship-on-paved-road
version: "1.0"
support_level: paved
steps:
  - id: catalog-entry
  - id: digest-pinned-artifact
  - id: workload-identity
  - id: reviewed-promotion
defaults:
  - artifact-digest
  - workload-identity-claims
  - no-cluster-admin
```

The evaluator loads `inherited/devops-v1.1/release/interface.yaml` and fails the contract if `artifact-digest` is missing while inherited promotion is by digest. It loads the identity interface and fails if workload-identity claims are missing. Do not rename those defaults when later chapters bind guardrails.

The path does not pretend environments are already a lease product. Chapter 6 owns that. A paved road that required a self-service environment this chapter does not have would fake outcome evidence.

> **Practice — Implement the steps, then compute conformance**
>
> Cover every contract step in the scaffold, and record whether each runnable system is paved, exited, or unofficial.

Open `paved-road/scaffold.yaml` and `paved-road/conformance.yaml`. The scaffold’s `implements` list must include every contract step. `fulfillment-api` completes the paved path with all three defaults present. There is no `reported_status`. Unofficial is a failure, not a third success mode.

> **Practice — Register an exit that keeps remaining guardrails**
>
> Name owner, lost defaults, remaining guardrails, and a review date. Do not put digest promotion in `lost_defaults`.

Open `paved-road/exits.yaml`. `notification-service` leaves the slow template:

```yaml
- id: notification-skip-slow-template
  system: notification-service
  owner: storefront-team
  lost_defaults: [golden-template-scaffold]
  remaining_guardrails: [artifact-digest, workload-identity-claims, no-cluster-admin]
  review_at: "2026-11-16T00:00:00Z"
```

Non-critical confirmations do not need the full template. They still promote a digest, still bind workload identity, and still must not inherit cluster-admin. That is a supported exit. Fulfillment skipping the template *and* promoting `latest` is not.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-05-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 05 checkpoint: paved-road completion and supported exit verified
```

The audit validates the four Chapter 5 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- the contract names `ship-on-paved-road` and a known owner;
- required defaults include inherited digest promotion, workload identity, and no cluster-admin;
- the scaffold implements every contract step;
- `storefront-api` and `fulfillment-api` have conformance records;
- paved systems keep required defaults;
- at least one supported exit exists;
- exits keep remaining guardrails and do not list them as lost; and
- unofficial forks fail.

The expected identifiers live in a separate checkpoint file. Conformance under test does not emit its own passing expectations.

The checkpoint does not prove that a live repository was scaffolded, that a real registry denied `latest`, or that a real identity provider issued the claims. Those remain claims a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 5 evidence |
|---|---|
| Mechanism evidence | Schemas and the conformance evaluator operated successfully. |
| Decision evidence | The path, defaults, support difference, and exit trade-offs are explicit and reviewed. |
| Outcome evidence | `fulfillment-api` has a computed paved completion with identity and artifact defaults intact. That is not proof a production cluster admitted the digest. |
| Recovery evidence | Not produced. A failed unofficial fork is a path-contract failure, not restored tenant isolation. |

Chapter 5 produces mechanism, decision, and limited outcome evidence for `ship-on-paved-road`. Pretending the local checkpoint proves a live pipeline would weaken Chapters 6 and 9.

## 4. Test the design under failure

### Connected consequence — Fulfillment forks the path unofficially to skip a slow template, losing identity and artifact defaults

> **Practice — Reject the unofficial fork or register an exit**
>
> Inject a `latest-tag` fork onto the completed `fulfillment-api` path and refuse conformance.

The completed road is healthy. The failure command does not rewrite it. It injects the connected fork against that snapshot:

```bash
make chapter-05-failure
```

Expected output:

```text
chapter 05 failure: unofficial fork correctly rejected
```

The injected record is:

```yaml
system: fulfillment-api
path: unofficial
defaults_present: [latest-tag]
```

The contract, scaffold, and `notification-service` exit stay in place. Fulfillment could have returned to the paved road or registered an exit that kept remaining guardrails. They did neither. They skipped the template and lost the inherited defaults. The evaluator rejects the fork, the missing digest, the missing identity claims, and `latest-tag` as a forbidden default.

**Severity:** high; every later environment, guardrail, and support conversation will debug a shadow path that the product does not own.  
**Plausible harm:** `latest` replaces digest identity; workload identity is dropped; cluster-admin returns as the unofficial way to ship.  
**Potential blast radius:** Fulfillment workloads and any Storefront consumer that trusts the same unofficial pipeline pattern.  
**Bounded by:** inherited release and identity interfaces, Chapter 3 prohibited roles, and the registered exit contract. None of those repair a path that treats unofficial as success.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Platform questions

- **User and job:** Fulfillment must finish `ship-on-paved-road` with identity and artifact defaults intact. Skipping a slow template by promoting `latest` is not that job.
- **Isolation:** Not yet applicable as an environment lease. Chapter-local implication: dropping workload-identity claims and `no-cluster-admin` reopens the shared-authority path Chapter 3 interrupted.
- **Contract and exit:** The contract is `northwind-production-path` version 1.0. Teams leave it through a registered exit that names owner, lost defaults, remaining guardrails, and `review_at`. An unofficial fork is not an exit.
- **Platform-product evidence:** A running template is not proof the product works. Required proof is computed `paved-road-completion` with inherited defaults present. This is not a portfolio **SLO (Service Level Objective)**.

#### Diagnosis

Calling the template mandatory without an exit encourages two failures at once. Teams who comply wait. Teams who ship fork unofficially and drop the defaults the inherited delivery path required. The catalog made the path discoverable, so Fulfillment knew what to skip. Productizing artifact promotion without conformance made `latest` look like a shortcut rather than a broken contract.

The missing supported exit makes the road a cage. The missing inherited digest default makes promotion tribal again. The unofficial path makes Chapter 13’s support model impossible: there is no product to support.

#### Correction

The completed model does not accept Fulfillment’s unofficial fork. `fulfillment-api` returns to the paved road with digest, identity, and no cluster-admin intact. `notification-service` shows the other legal move: a registered exit that loses only the golden template and keeps remaining guardrails. Unofficial forks fail conformance either way.

This failure is a path-contract failure. It is not a runtime isolation event that needs containment and plane recovery. Do not call the rejected fork **Evidence of restored isolation**. Nothing tenant-runtime was restored. The path stopped treating shadow infrastructure as completion.

That correction changes later decisions:

- Chapter 6 must lease environments that this path can assume, not tickets that recreate unofficial YAML.
- Chapter 9 must bind remaining guardrails on paved and exited paths alike; an exit is not an exception to digest identity.
- Chapter 12 must version and deprecate unofficial paths rather than bless them as “whatever shipped.”
- Chapter 13 must support paved and exited systems as products, and refuse unofficial forks as unsupported.

The design is practical because the failed check is the product. Adding an arbitrary repository-scaffold command would not make it more practical.

## 5. Production reality

### Common paved-road errors

#### Making the template mandatory and calling that a product

A cage produces unofficial forks. If the only way off the path is shadow infrastructure, the path is not supported.

#### Treating `latest` as a default

Inherited promotion is by digest. `latest` is a forbidden default, not a convenience.

#### Putting remaining guardrails in `lost_defaults`

An exit that loses workload identity is an unofficial fork with paperwork.

#### Emitting conformance success from the system under test

A path that scores itself cannot fail a fork. Keep observations (`path`, `defaults_present`) separate from expectations.

#### Paving Storefront and leaving Fulfillment unofficial “until the template is faster”

The second tenant is why the path exists. If only Storefront is paved, Northwind still has tribal YAML.

#### Using a green pipeline UI as paved-road completion

A template run is mechanism evidence. `paved-road-completion` requires inherited defaults intact.

## 6. What changed

| Before | After |
|---|---|
| Fulfillment forked unofficially to skip a slow template. | **Unofficial forks fail; Fulfillment completes the paved path or registers an exit.** |
| Promotion used `latest`. | **The path consumes inherited `artifact-digest` promotion.** |
| Identity defaults were tribal YAML. | **Workload-identity claims are a required default and a remaining guardrail.** |
| The golden path had no exit. | **`notification-service` leaves the template, keeps guardrails, and has a review date.** |
| Support meant debugging whatever shipped. | **Paved and exited are supported; unofficial is not.** |
| A valid schema could appear to prove a path. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely four YAML files. Northwind now has a versioned path contract that later chapters can lease, guard, and support without treating a golden cage or a shadow fork as shipping.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Paved-road contract | `paved-road/contract.yaml` | It retains the job, version, steps, and inherited defaults later guardrails must not rename. |
| Supported-exit record | `paved-road/exits.yaml` | It retains how a team leaves the scaffold without becoming unofficial, including remaining guardrails and a review date. |

These artifacts should change when Northwind’s delivery defaults, inherited interfaces, or support model materially change—not whenever a template is restyled.

## What You Learned

A paved road is a versioned product contract with steps, defaults, and support. A supported exit names owner, lost defaults, remaining guardrails, and a review date. An unofficial fork that skips a slow template and drops inherited identity and artifact defaults fails conformance. Schema checks can prove structural completeness within declared scope. They cannot prove a live repository was scaffolded. A design earns its place when leaving the path is a reviewed contract rather than shadow infrastructure.

### Prove It

> **Independent Practice — Decide a Storefront exit without copying the Fulfillment fork**
>
> Storefront wants to skip the golden template because it injects a dashboard widget they already declined in Chapter 2.

Extend the Chapter 5 model without adding environment policy yet:

1. Decide whether Storefront should stay paved, register an exit, or whether an unofficial fork would fail and why.
2. Name lost defaults that are not `artifact-digest` or `workload-identity-claims`.
3. State remaining guardrails that Chapter 9 must still bind.
4. Choose an owner and a `review_at` that is not “when the template is faster.”
5. Identify one observation that would falsify the exit—for example `storefront-api` promoting `latest` while claiming the exit.
6. Explain whether `order-worker` must follow the same treatment or can remain paved independently.

Do not copy the Fulfillment unofficial-fork row and relabel it an exit. Storefront already ships; the dashboard widget is Chapter 2’s left capability, not a missing digest. Your durable output is the exit decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 5 capability when you can explain why unofficial is not an exit, trace the path to `ship-on-paved-road` and inherited digest promotion, describe evidence that would falsify conformance, distinguish structural validation from decision and outcome evidence, and explain what the baseline, checkpoint, and failure command do and do not prove.

## Next

The path exists, but environments are still tickets against a shared cluster. The paved road assumes an environment. Provisioning is still a wait, or a namespace that shares quota and credentials.

Chapter 6 offers self-service environments without sharing blast radius, so finishing the path does not require cluster-admin or an unbounded namespace.
