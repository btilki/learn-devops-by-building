# How to Use This Book

## Who this book is for

This book is for intermediate-to-advanced DevOps, cloud, infrastructure, platform, security, and **SRE (Site Reliability Engineering)** practitioners who need to turn working delivery and security capabilities into an internal product that other teams can consume.

You should already be comfortable with Linux, Git, containers, **CI/CD (Continuous Integration and Continuous Delivery)**, cloud and Kubernetes fundamentals, infrastructure as code, networking, workload identity, observability, and the production delivery path taught in *Practical DevOps Engineering*. The book does not teach those subjects from first principles. It uses them as the surface on which platform-product decisions must operate.

You do not need to be a portal-product manager, Kubernetes operator author, public-cloud landing-zone architect, or reliability-program owner. Those disciplines contain important knowledge, but this book has a narrower promise: help you decide which capabilities belong on a platform, isolate tenants, offer a paved road with an exit, operate a shared control plane, measure finished jobs rather than vanity, run fleet lifecycle, and recover a control-plane failure without taking every tenant down.

This is not a catalog of developer-portal tools. Products change. The durable skill is being able to explain:

- who the user is and what job must finish;
- where one team's change, credential, or failure stops;
- what contract a team can rely on, and how they leave it; and
- what evidence proves the platform product is healthy—not only a tenant workload.

## Relationship to earlier books

This book continues the Northwind Commerce system from *Practical DevOps Engineering* and *Practical DevSecOps Engineering*.

The DevOps book established one team's production delivery path: fast feedback, immutable artifact identity, reconciled infrastructure, a bounded Kubernetes runtime, workload identity, observable outcomes, progressive delivery, compatible data changes, safe asynchronous processing, GitOps reconciliation, cost and capacity, incident coordination, and reconstruction from durable evidence.

The DevSecOps book made security of that same path explicit: assets and harms, threat and risk decisions, attributable identity, privileged delegation, supply-chain trust, vulnerability treatment, secrets, data protection, policy, runtime confinement, detection, investigation, eradication, bounded restored trust, and operational governance.

Those capabilities are prerequisites here. This book does not repeat their implementation and present it as new platform work. Instead, it asks the product questions that remain:

- Which repeated capabilities should other teams consume as a product?
- Where does tenant blast radius stop?
- What is a paved road, and what is a supported exit?
- How does a shared control plane avoid becoming shared root?
- Which measurements prove jobs finished, and which only prove the platform looked busy?

The published DevOps and DevSecOps v1.0 manuscripts remain unchanged. This book has a separate cumulative implementation under:

```text
books/practical-engineering/labs/platform/northwind/
```

The new lab does not read earlier labs' working trees at runtime. It carries reduced interface fixtures whose manifests record source paths, source checksums, local checksums, and consumers. `inherited/devops-v1.1/` is a lab-snapshot identifier, not the published DevOps book version.

## The Northwind system

Northwind Commerce remains deliberately small enough to understand and large enough to require real platform decisions:

```text
customer
   │
   ▼
storefront-api ───────► PostgreSQL
   │                       ▲
   │ accepted order        │ order state, identity, evidence
   ▼                       │
durable queue ───────► order-worker ───────► payment provider
                           │
                           ▼
                    notification-service ──► email provider

fulfillment-api ──► warehouse and dispatch effects
        │
        ▼
   same platform products: catalog, paved road, environments,
   abstractions, control plane, guardrails, quota, fleet
```

- `storefront-api` serves catalog reads and accepts orders.
- `order-worker` processes accepted orders asynchronously and can cause payment and inventory effects.
- `notification-service` sends non-critical confirmations.
- `fulfillment-api` is the second tenant's service. It must ship without inheriting cluster-admin or copying Storefront's unofficial path.
- PostgreSQL stores order and processing state.
- A durable queue separates acceptance from asynchronous completion.

The critical business outcome remains:

> A valid order is durably accepted and reaches a correct terminal state without duplicate charge, invalid inventory state, or permanent disappearance.

This book adds a critical platform outcome:

> Application teams can finish a production job on a reviewed paved road, inside an explicit tenant boundary, without inheriting shared cluster authority; the platform product has an owner, a contract, an exit, quota, and evidence that a control-plane failure does not take every tenant down.

A portal that launched is not that outcome. A green Storefront deployment is not that outcome. Shared cluster-admin that “unblocks” Fulfillment is the opposite of that outcome.

## The cumulative platform path

The chapters form one dependency chain:

```text
product users, jobs, promise, and refusals
  → capability intake decisions
  → tenant isolation and role boundaries
  → catalog and ownership
  → paved road with a supported exit
  → self-service environments
  → versioned infrastructure contracts
  → shared control plane as a product
  → guardrails and exception bindings
  → honest developer-experience measurement
  → tenant quota and platform unit cost
  → fleet onboard, upgrade, and deprecation
  → support and safe platform change
  → bounded control-plane recovery
```

Later chapters consume earlier decisions. The product brief determines which jobs intake may accept. Tenancy determines what an environment product may share. The paved road determines which defaults guardrails may bind. Quota and fleet change are meaningless until those contracts exist.

The cumulative product failure is shared authority: a platform that is really a ticket queue plus a cluster everyone can break. It develops across tenancy, environments, the control plane, fleet upgrades, and recovery.

Not every platform failure comes from that story. Exercises are labeled according to their relationship with the main narrative:

- **Cumulative product failure:** advances shared-authority and ticket-queue harm.
- **Connected consequence:** demonstrates harm enabled by an earlier platform decision.
- **Independent control failure:** proves that the control matters even without the cumulative story.

## Four chapter forms

The book does not force every learning objective into the same structure.

### Concept-led chapters

A concept-led chapter develops a mental model required for later production decisions. The reader may define users and jobs, model tenancy, or reject vanity measurement. Its durable output can be a reviewed reasoning artifact rather than executable code.

Concept-led does not mean detached theory. Every substantial conceptual section must affect a chapter decision, durable artifact, interpretation of evidence, failure diagnosis, or later implementation dependency.

### Decision-led chapters

A decision-led chapter compares approaches under explicit user jobs and operational constraints. It records the recommendation, trade-offs, owner, and review trigger.

Adoption percentage, survey scores, and ticket volume are inputs—not the decision itself.

### Implementation-led chapters

An implementation-led chapter starts from a red capability, establishes the necessary mental model, guides a contract or system change, exercises a controlled failure, diagnoses the evidence, and verifies containment or recovery where required.

### Hybrid chapters

A hybrid chapter uses a concept or decision immediately to govern implementation. It still answers one primary production question.

There is no theory-to-practice percentage. **Decision 001** in `SERIES-DECISIONS.md` forbids adding an exercise merely to satisfy one. The practical requirement is consequential reader reasoning, meaningful change where appropriate, trustworthy evidence, and explicit limits on what has been proved.

## Four kinds of evidence

Platform mechanisms often produce impressive output while leaving the important claim unanswered. This book separates four evidence categories:

1. **Mechanism evidence** proves that a catalog, portal, provisioner, controller, or scorecard operated.
2. **Decision evidence** proves that an owner evaluated user jobs, isolation, and trade-offs.
3. **Outcome evidence** proves that a team finished a production job inside the contract.
4. **Recovery evidence** proves that tenant blast radius was restored—not merely that a ticket closed.

These categories are complementary. A published portal does not prove jobs finish. A healthy Storefront order metric does not prove Fulfillment is isolated. A restored control-plane process does not prove every tenant is healthy.

Do not call tenant isolation recovery **Evidence of restored trust**. That phrase belongs to DevSecOps compromise recovery. Use **Evidence of restored isolation** or **Evidence of bounded platform-product recovery**.

Do not call platform-product indicators portfolio **SLOs (Service Level Objectives)**. Those belong to SRE. This book may use platform-product **SLIs (Service Level Indicators)** such as time-to-first-environment. Call unreliability against those indicators a **job-time budget**. Reserve **error budget** for SRE portfolio governance.

## Lab states and commands

Use Python 3.13. From the Platform lab root:

```bash
python3 -m venv .venv
source .venv/bin/activate
make bootstrap
make test
make lint
make audit
```

The lab uses these states when they support the chapter's learning objective:

- **Start:** cumulative prerequisites exist, but the chapter capability is incomplete.
- **Baseline:** the evaluator runs successfully and proves the declared weakness is present.
- **Complete:** the chapter decision or implementation satisfies independent expectations.
- **Challenge:** a concept or decision scenario exposes incomplete reasoning. Correction happens inside that write-up; there is no `corrected` lab state.
- **Failure:** an inert local input exercises isolation, quota, upgrade, or authority failure.
- **Contained:** modeled harm and authority are bounded, but product health is not yet assumed restored.
- **Recovered:** required state is reconciled and platform-product plus tenant isolation evidence pass.

A successful baseline command means the evaluator correctly found the expected unsafe state. It does not mean the product is already healthy.

Chapter commands follow a stable pattern where applicable:

```text
make chapter-NN-baseline
make chapter-NN-checkpoint
make chapter-NN-challenge
make chapter-NN-failure
make chapter-NN-contain
make chapter-NN-recover
make chapter-NN-verify-recovery
```

Not every chapter uses every command. Concept-led and decision-led chapters do not manufacture a failure or recovery sequence when classification, modeling, or decision correction is the real work.

## Chapter snapshots

Versioned start and complete tags are the exercise snapshots:

```text
v1.0-chapter-NN-start
v1.0-chapter-NN-complete
chapter-NN-start
chapter-NN-complete
```

The versioned tags are the immutable release identity. The reader-facing aliases point to the same commits in this freeze and may advance in a later release. Tags are curated exercise snapshots, not merge milestones. Do not infer the teaching contract from Git ancestry.

Failure state is generated from the complete snapshot. An unofficial plane patch, mixed backup, or starved quota must never be preserved as if it were a trusted completed reference.

Create a working branch from the start snapshot and compare against the complete reference without merging it as a shortcut:

```bash
git switch -c my-chapter-NN chapter-NN-start
git diff chapter-NN-start chapter-NN-complete
```

### Working-tree procedure

From the Platform lab root:

1. from the Platform lab root, create the Python virtual environment and run `make bootstrap`, `make test`, `make lint`, and `make audit`;
2. start from `chapter-NN-start` (or work in the completed tree if you already have later chapters);
3. run the chapter baseline and confirm that it detects the documented red state;
4. follow the chapter's guided work and preserve its decision or implementation evidence;
5. run the completed checkpoint;
6. run the declared challenge or failure where applicable;
7. verify correction, containment, or recovery where the chapter requires it; and
8. retain the chapter's durable outputs.

A concept-led chapter may change only reviewed YAML artifacts. The absence of application code does not make the product brief disposable.

## Safe failure simulations

The lab's failures are deterministic, local, inert, and non-destructive:

- cross-tenant access uses synthetic identifiers;
- quota and noisy-neighbor cases are numeric fixtures, not live load tests;
- control-plane restore mutates generated lab state only; and
- no real credential, cluster mutation, billing API, or destructive external action is included.

## What local verification proves

The local evaluators verify structure, relationships, isolation, compatibility, expiry, vanity rejection, quota, fleet windows, and bounded restore within the declared model.

They do not prove that a real portal, identity provider, cluster fleet, cost system, or ticketing system enforces the same behavior.

Chapter 14 can prove that inventoried plane evidence was restored and tenant isolation held in the model. It cannot prove regional loss or a portfolio recovery-time program. Those remain SRE.

## Five principles and four platform questions

The five principles established for the series remain active:

1. **Blast-radius control:** expose the smallest defensible scope to uncertain change, attack, or failure.
2. **Explicit contracts:** make identity, authority, trust, state, policy, outcomes, and failure behavior reviewable.
3. **Trustworthy evidence:** separate observations and expectations so a mechanism cannot approve itself.
4. **Reconciliation:** compare desired, recorded, external, and actual state, then make disagreement visible and owned.
5. **Recovery:** distinguish corrective action from proof that the protected outcome and required trust are healthy again.

Platform work repeatedly asks four platform questions:

1. Who is the user, and what job must finish?
2. What isolation boundary limits tenant blast radius?
3. What contract can a team rely on, and how do they leave it?
4. What evidence proves the platform product is healthy—not only a tenant workload?

Dedicated failures name only the principles and questions that materially apply.

## Best Practice and Production Practice

The book retains two labels from the series:

- **Best Practice:** a strong default that is broadly useful.
- **Production Practice:** how that default must be validated or adapted for the actual users, jobs, isolation, failure modes, evidence quality, and recovery obligations.

For example, a paved road is a strong default. In production, its value depends on a finished job, remaining guardrails on exit, an owner, and evidence that unofficial forks fail conformance.

## How to judge your work

Do not ask only whether the portal shipped. Ask:

> Who is the user, what job must finish, where does tenant blast radius stop, what contract can they rely on and leave, and what evidence proves the platform product—not only one workload—is healthy?

That question is the reading contract for the chapters ahead.
