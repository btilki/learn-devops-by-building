# How to Use This Book

## Who this book is for

This book is for intermediate-to-advanced DevOps, cloud, infrastructure, platform, security, and **SRE (Site Reliability Engineering)** practitioners who need to govern reliability across a service portfolio that already has a delivery path, a security path, and an owned internal platform.

You should already be comfortable with Linux, Git, containers, **CI/CD (Continuous Integration and Continuous Delivery)**, cloud and Kubernetes fundamentals, infrastructure as code, networking, workload identity, observability, incident coordination for a single failed change, reconstruction of one environment, and the platform-product, tenancy, and fleet contracts taught in *Practical Platform Engineering*. The book does not teach those subjects from first principles. It uses them as the surface on which portfolio reliability decisions must operate.

You do not need to be an observability-stack author, chaos-engineering product specialist, public-cloud multi-region architect, or incident-command handbook author. Those disciplines contain important knowledge, but this book has a narrower promise: help you decide which user journeys reliability must protect, choose indicators users can feel, set portfolio **SLOs (Service Level Objectives)** and error budgets, write policy that can freeze change, page on burn rather than on every symptom, design on-call as a system, bound toil, put dependencies inside the contract, degrade before failure cascades, command multi-service incidents, turn incidents into learning, design for regional loss, run game days, and fail over a region without taking the portfolio down.

This is not a catalog of monitoring or paging tools. Products change. The durable skill is being able to explain:

- what user-visible journey is at risk, and for which services;
- what error budget remains, and what change it authorizes or freezes;
- what human system absorbs the failure without informal heroics; and
- what evidence proves the portfolio recovered—not only one service, one environment, or one control plane.

## Relationship to earlier books

This book continues the Northwind Commerce system from *Practical DevOps Engineering*, *Practical DevSecOps Engineering*, and *Practical Platform Engineering*.

The DevOps book established one team's production delivery path: fast feedback, immutable artifact identity, reconciled infrastructure, a bounded Kubernetes runtime, workload identity, observable outcomes, progressive delivery, compatible data changes, safe asynchronous processing, **GitOps (Git-based operations)** reconciliation, cost and capacity, incident coordination, and reconstruction from durable evidence. Chapter 6 defined provisional **SLIs (Service Level Indicators)** and a burn policy for Storefront. Chapter 12 coordinated one failed production change. Chapter 13 reconstructed one environment. Those remain single-path capabilities.

The DevSecOps book made security of that same path explicit: assets and harms, threat and risk decisions, attributable identity, privileged delegation, supply-chain trust, vulnerability treatment, secrets, data protection, policy, runtime confinement, detection, investigation, eradication, bounded restored trust, and operational governance.

The Platform book turned repeated delivery and security capabilities into an owned internal product: users, jobs, tenancy, catalog, paved road, environments, contracts, shared control plane, guardrails, developer-experience measurement, quota, fleet lifecycle, support and escalation, and control-plane recovery that keeps tenant data planes bounded. Platform-product indicators such as time-to-first-environment remain a **job-time budget**. Catalog escalations `storefront-oncall`, `fulfillment-oncall`, and `platform-oncall` are contacts, not an on-call system. Chapter 14 restored a plane without taking tenants with it, and recorded `not-regional-loss` and `not-portfolio-rto`. Remaining owner `reliability-program` holds portfolio SLO governance.

Those capabilities are prerequisites here. This book does not repeat their implementation and present it as new SRE work. Instead, it asks the reliability questions that remain:

- Which user journeys must stay reliable, and what must not count as success?
- Which measurements are user-visible SLIs, and which are platform job-time or component uptime?
- What SLO and error budget govern Storefront and Fulfillment together?
- When remaining budget is exhausted, what change freezes—including a fleet step Platform already knew how to freeze for upgrades?
- Who is on-call, with what rotation, load, handoff, and authority?
- What happens when a region is lost, and what evidence proves the portfolio recovered?

The published DevOps, DevSecOps, and Platform v1.0 manuscripts remain unchanged. This book has a separate cumulative implementation under:

```text
books/labs/sre/northwind/
```

The new lab does not read earlier labs' working trees at runtime. It carries reduced interface fixtures whose manifests record source paths, source checksums, local checksums, and consumers:

```text
inherited/devops-v1.1/
inherited/devsecops-v1.0/
inherited/platform-v1.0/
```

`inherited/devops-v1.1/` is a lab-snapshot identifier, not the published DevOps book version.

## The Northwind system

Northwind Commerce remains deliberately small enough to understand and large enough to require real reliability decisions:

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

reliability program (this book):
   user journeys → SLOs → error budgets → on-call →
   learning → game days → regional loss
```

- `storefront-api` serves catalog reads and accepts orders.
- `order-worker` processes accepted orders asynchronously and can cause payment and inventory effects.
- `notification-service` sends non-critical confirmations. It is not a critical user journey.
- `fulfillment-api` is the second tenant's user-facing service. A Storefront SLO cannot stand in for dispatch.
- PostgreSQL stores order and processing state.
- A durable queue separates acceptance from asynchronous completion.
- Payment and warehouse providers are critical dependencies. Email is not.

The critical business outcome remains:

> A valid order is durably accepted and reaches a correct terminal state without duplicate charge, invalid inventory state, or permanent disappearance.

This book adds a critical reliability outcome:

> Storefront and Fulfillment keep user-visible SLOs; exhausted error budget can freeze change, including fleet change; on-call and learning are systems rather than heroics; a region can be lost and the portfolio recovered from a reviewed plan, with evidence that this is not reconstruction of one environment or restore of one control plane.

A green cluster is not that outcome. A launched dashboard of nines is not that outcome. A Platform upgrade freeze is not an error-budget freeze. Slack as the page destination is the opposite of an on-call system. Reconstructing one environment, or restoring a control plane, is not **Evidence of portfolio recovery**.

## The cumulative reliability path

The chapters form one dependency chain:

```text
protected journeys, refusals, and owners
  → SLI selection (accept / adjacent / reject)
  → portfolio SLOs, windows, and error budgets
  → error-budget policy that can freeze change
  → burn-rate paging versus symptom noise
  → on-call as a system
  → toil measurement and bounds
  → dependency contracts inside the journey
  → degradation and cascade control
  → multi-service incident command
  → learning with verified follow-through
  → regional-loss architecture
  → recurring game days
  → regional fail-over and portfolio recovery
```

Later chapters consume earlier decisions. The journey register determines which indicators Chapter 2 may accept. Accepted SLIs determine which SLOs Chapter 3 may publish. Remaining error budget determines which change Chapter 4 may freeze. Pages bind to the on-call system in Chapter 6, not to a catalog label. Game days in Chapter 13 must exercise error-budget freeze, on-call page path, dependency loss, and regional-loss tabletop or simulated fail-over. They are not a rehearsal of Chapter 14 fail-over.

The cumulative reliability failure is availability theater plus informal heroics: green graphs, exhausted budgets that do not freeze change, Slack-as-on-call, and a regional outage whose plan is invented during the event. It develops across SLOs, policy, paging, on-call, cascade, incidents, and fail-over.

Not every reliability failure comes from that story. Exercises are labeled according to their relationship with the main narrative:

- **Cumulative reliability failure:** advances availability theater and informal heroics.
- **Connected consequence:** demonstrates harm enabled by an earlier reliability decision.
- **Independent control failure:** proves that the control matters even without the cumulative story.

## Four chapter forms

The book does not force every learning objective into the same structure.

### Concept-led chapters

A concept-led chapter develops a mental model required for later production decisions. The reader may name protected journeys, refuse uptime theater, or design for the loss of a region. Its durable output can be a reviewed reasoning artifact rather than executable code.

Concept-led does not mean detached theory. Every substantial conceptual section must affect a chapter decision, durable artifact, interpretation of evidence, failure diagnosis, or later implementation dependency.

### Decision-led chapters

A decision-led chapter compares approaches under explicit user journeys and operational constraints. It records the recommendation, trade-offs, owner, and review trigger.

A copied 99.9 percent target, a customer **SLA (Service Level Agreement)**, a dashboard of nines, or a survey score is an input—not the decision itself. An SLA is a customer or legal promise. An SLO is the internal reliability contract that error budget governs. Do not treat them as synonyms.

### Implementation-led chapters

An implementation-led chapter starts from a red capability, establishes the necessary mental model, guides a contract or system change, exercises a controlled failure, diagnoses the evidence, and verifies containment or recovery where required.

### Hybrid chapters

A hybrid chapter uses a concept or decision immediately to govern implementation. It still answers one primary production question.

There is no theory-to-practice percentage. **Decision 001** in `SERIES-DECISIONS.md` forbids adding an exercise merely to satisfy one. The practical requirement is consequential reader reasoning, meaningful change where appropriate, trustworthy evidence, and explicit limits on what has been proved.

## Four kinds of evidence

Reliability mechanisms often produce impressive output while leaving the important claim unanswered. This book separates four evidence categories:

1. **Mechanism evidence** proves that a dashboard, alert, pager, runbook, or fail-over controller operated.
2. **Decision evidence** proves that an owner evaluated user journeys, error-budget consequences, and operational load.
3. **Outcome evidence** proves that a user-visible journey kept its SLO, or that remaining error budget was accounted.
4. **Recovery evidence** proves **Evidence of portfolio recovery**—not merely that one service returned, one environment was reconstructed, or one control plane was restored.

These categories are complementary. A published SLO catalog does not prove journeys hold. A healthy Storefront `order_success_ratio` does not prove Fulfillment dispatch succeeded, and it does not prove a platform job finished. Time-to-first-environment does not prove orders succeeded. A restored control-plane process does not prove a region failed over.

Do not call regional fail-over recovery **Evidence of restored trust**. That phrase belongs to DevSecOps compromise recovery. Do not call it **Evidence of restored isolation** or **Evidence of bounded platform-product recovery**. Those phrases belong to Platform. Use **Evidence of portfolio recovery**.

Do not call platform-product indicators portfolio SLOs. Platform job proofs `time-to-first-environment`, `paved-road-completion`, and `catalog-freshness` remain a job-time budget. Reserve **error budget** for SRE portfolio governance. A Platform fleet freeze for an upgrade is not an error-budget freeze. An error-budget freeze may halt that same fleet step for a reason Platform did not own.

## Lab states and commands

Use Python 3.13. From the SRE lab root:

```bash
python3 -m venv .venv
source .venv/bin/activate
make bootstrap
make test
make lint
make audit
make matrix
```

The lab uses these states when they support the chapter's learning objective:

- **Start:** cumulative prerequisites exist, but the chapter capability is incomplete.
- **Baseline:** the evaluator runs successfully and proves the declared weakness is present.
- **Complete:** the chapter decision or implementation satisfies independent expectations.
- **Challenge:** a concept or decision scenario exposes incomplete reasoning. Correction happens inside that write-up; there is no `corrected` lab state.
- **Failure:** an inert local input exercises burn, cascade, page-path, freeze, or regional-loss failure.
- **Contained:** modeled harm and change are bounded, but portfolio health is not yet assumed recovered.
- **Recovered:** required state is reconciled and journey plus portfolio-recovery evidence pass.

A successful baseline command means the evaluator correctly found the expected unsafe state. It does not mean the portfolio is already reliable.

This lab’s executable chapter commands are:

```text
make chapter-NN-baseline
make chapter-NN-checkpoint
```

`make matrix` runs tests, lint, audit, and every Chapter 1–14 baseline and checkpoint. Challenge, failure, contained, and recovered remain learning states. Correction lives in the chapter write-up. This lab does not ship `chapter-NN-challenge`, `chapter-NN-failure`, `chapter-NN-contain`, `chapter-NN-recover`, or `chapter-NN-verify-recovery` Make targets. Failure input is generated from the complete snapshot and is not a trusted completed reference.

## Chapter snapshots

Versioned start and complete tags are the exercise snapshots:

```text
v1.0-chapter-NN-start
v1.0-chapter-NN-complete
chapter-NN-start
chapter-NN-complete
```

The versioned tags are the immutable release identity. The reader-facing aliases point to the same commits in this freeze and may advance in a later release. Tags are curated exercise snapshots, not merge milestones. Do not infer the teaching contract from Git ancestry.

Failure state is generated from the complete snapshot. An exhausted budget that did not freeze, a Slack-as-primary page, a retry cascade, or a mixed-region fail-over must never be preserved as if it were a trusted completed reference.

Create a working branch from the start snapshot and compare against the complete reference without merging it as a shortcut:

```bash
git switch -c my-chapter-NN chapter-NN-start
git diff chapter-NN-start chapter-NN-complete
```

### Working-tree procedure

From the SRE lab root:

1. from the SRE lab root, create the Python virtual environment and run `make bootstrap`, `make test`, `make lint`, and `make audit`;
2. start from `chapter-NN-start` (or work in the completed tree if you already have later chapters);
3. run the chapter baseline and confirm that it detects the documented red state;
4. follow the chapter's guided work and preserve its decision or implementation evidence;
5. run the completed checkpoint;
6. run the declared challenge or failure where applicable;
7. verify correction, containment, or recovery where the chapter requires it; and
8. retain the chapter's durable outputs.

A concept-led chapter may change only reviewed YAML artifacts. The absence of application code does not make the reliability brief disposable.

## Safe failure simulations

The lab's failures are deterministic, local, inert, and non-destructive:

- cross-tenant and cross-region access uses synthetic identifiers;
- burn, overload, and cascade cases are numeric fixtures, not live load tests;
- game days and fail-over mutate generated lab state only; and
- no real credential, cluster mutation, paging-vendor API, regional traffic shift, or destructive external action is included.

## What local verification proves

The local evaluators verify structure, relationships, SLI class, remaining budget, freeze policy, page versus ticket, on-call rotations, toil bounds, dependency criticality, cascade denial, incident command, learning verification, game-day coverage, and bounded fail-over within the declared model.

They do not prove that a real telemetry backend, paging vendor, identity provider, multi-region fleet, or incident-management product enforces the same behavior.

Chapter 14 can prove that inventoried regional evidence was failed over and tenant isolation held in the model. It cannot prove that a production multi-region estate failed over. One-environment reconstruction and control-plane restore remain inherited recoveries. They are listed as insufficient.

## Five principles and four reliability questions

The five principles established for the series remain active:

1. **Blast-radius control:** expose the smallest defensible scope to uncertain change, attack, or failure.
2. **Explicit contracts:** make identity, authority, trust, state, policy, outcomes, and failure behavior reviewable.
3. **Trustworthy evidence:** separate observations and expectations so a mechanism cannot approve itself.
4. **Reconciliation:** compare desired, recorded, external, and actual state, then make disagreement visible and owned.
5. **Recovery:** distinguish corrective action from proof that the protected outcome and required trust are healthy again.

SRE work repeatedly asks four reliability questions:

1. What user-visible journey is at risk, and for which services?
2. What error budget remains, and what change does it authorize or freeze?
3. What human system absorbs the failure without informal heroics?
4. What evidence proves the portfolio recovered—not only one service, one environment, or one control plane?

Dedicated failures name only the principles and questions that materially apply.

## Best Practice and Production Practice

The book retains two labels from the series:

- **Best Practice:** a strong default that is broadly useful.
- **Production Practice:** how that default must be validated or adapted for the actual journeys, error budgets, on-call load, dependencies, failure modes, evidence quality, and recovery obligations.

For example, an SLO is a strong default. In production, its value depends on a user-visible SLI, a computed remaining error budget, a policy that can freeze change, an on-call system that can be paged, and evidence that recovery of the portfolio—not only one graph—has been proved.

## How to judge your work

Do not ask only whether the dashboard is green. Ask:

> What user-visible journey is at risk, what error budget remains and what change it freezes, who is on-call with authority rather than heroics, and what evidence proves the portfolio recovered—not only one service, one environment, or one control plane?

That question is the reading contract for the chapters ahead.
