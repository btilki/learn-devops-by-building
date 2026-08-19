# Practical Platform Engineering — Book Plan

**Planning status:** Frozen  
**Draft date:** 2026-08-16  
**Freeze date:** 2026-08-16  
**Drafting gate:** Chapter drafting must conform to this frozen plan or use an explicitly versioned plan revision.

## Promise

Turn Northwind's repeated delivery and security capabilities into an owned internal platform product that application teams can consume through paved roads, with explicit tenancy, shared control-plane lifecycle, and fleet operations.

The reader will learn to decide which capabilities belong on a platform, define the product and its users, isolate tenants, publish ownership through a catalog, offer a golden path with an exit, provision environments as a product, abstract infrastructure behind contracts, operate a shared control plane, enforce guardrails without a cage, measure developer experience honestly, allocate quota and cost, run fleet lifecycle, support and change the platform safely, and recover a control-plane failure without taking every tenant down.

## Audience

This book is for intermediate-to-advanced DevOps, cloud, infrastructure, platform, security, and **SRE (Site Reliability Engineering)** practitioners. Readers should already understand Linux, Git, containers, **CI/CD (Continuous Integration and Continuous Delivery)**, cloud and Kubernetes fundamentals, infrastructure as code, networking, workload identity, observability, and the production delivery path taught in *Practical DevOps Engineering*.

The book does not teach those subjects from first principles. It teaches the product, tenancy, and fleet decisions required to turn working delivery and security capabilities into something other teams can consume.

## Relationship to earlier books

*Practical DevOps Engineering* established one team's production delivery path for Northwind: fast feedback, verifiable artifacts, reconciled infrastructure, bounded runtime, workload identity, observable outcomes, progressive delivery, compatible data change, safe asynchronous processing, GitOps, cost and capacity, incident coordination, and reconstruction from durable evidence.

*Practical DevSecOps Engineering* made security of that same path explicit: assets and harms, threat and risk decisions, attributable identity, privileged delegation, supply-chain trust, vulnerability treatment, secrets, data protection, policy, runtime confinement, detection, investigation, eradication, bounded restored trust, and operational governance.

This book consumes those capabilities as prerequisites. It may briefly restate an inherited contract when a platform decision depends on it, but it must not reteach a DevOps or DevSecOps chapter or reproduce those implementations as new platform work.

The published DevOps and DevSecOps v1.0 manuscripts remain unchanged. This book uses a separate manuscript directory and a separate cumulative lab.

## Series authority

This plan depends on `SERIES-DECISIONS.md` as the series-level record, not as a book-local file.

- **Decision 001** (Accepted, 2026-08-15; applies from DevSecOps and every later book): important operational concepts may lead chapters without an artificial practice exercise. There is no theory-to-practice ratio. Conceptual material must remain in operational scope, enable a later production decision, and not become a beginner survey. Platform inherits the no-ratio rule; the DevSecOps concept list in that decision is book-local.
- **Decision 002:** shared Word publication style.
- **Decision 003:** first published edition of every book is v1.0.
- **Decision 004:** *Practical SRE Engineering* is the planned fourth book. Its lab will inherit checksum-identified interfaces from DevOps, DevSecOps, and Platform.

## Scope

This book owns the internal platform product for Northwind's application teams:

- platform-as-product definition: users, jobs, promise, non-goals, ownership, and success evidence;
- deciding which repeated capabilities become platform products and which stay with application teams;
- tenant, team, and isolation boundaries;
- software catalog, ownership, and discoverability;
- paved roads, scaffolding, conformance, and supported exits;
- self-service environments with bounded blast radius;
- infrastructure abstractions and versioned contracts;
- shared control-plane operation as a product;
- guardrails, defaults, exceptions, and scorecards without a golden cage;
- developer-experience measurement that cannot be gamed by vanity;
- tenant quota, showback, and platform unit economics;
- fleet lifecycle: onboard, upgrade, deprecate, and migrate;
- platform support, escalation, and safe change;
- control-plane failure isolation and recovery that preserves tenant data planes.

## Boundaries

### DevOps boundary

This book does not reteach pipeline performance, artifact promotion, infrastructure reconciliation for one team, Kubernetes runtime fundamentals, observability fundamentals, progressive delivery, schema evolution, messaging correctness, GitOps for a single application, FinOps of one workload path, general incident coordination, or reconstruction of one environment. It productizes those capabilities so multiple teams can consume them.

### DevSecOps boundary

This book may ship security defaults, policy interfaces, and exception UX as platform products. It does not rebuild threat modeling, risk registers, supply-chain admission, vulnerability prioritization, secret lifecycle, detection engineering, investigation, containment, eradication, or restored-trust claims. Those remain DevSecOps outcomes that the platform must expose, not replace.

### SRE boundary

This book may define platform-product service-level indicators such as time-to-environment or paved-road success rate. It does not own portfolio-wide service-level objective governance, error-budget policy across many services, on-call system design, regional-loss architecture, recurring game days, or reliability learning programs. Those remain SRE.

### Governance boundary

This book explains how platform contracts, scorecards, and exceptions produce evidence useful to governance. It does not certify Northwind against a legal or industry framework, or reduce platform engineering to a compliance portal.

### Specialist boundaries

The book does not replace a complete Kubernetes operator textbook, service-mesh reference, developer-portal product manual, public-cloud landing-zone guide, or AI-platform survey. It includes only the depth needed for the production decisions in scope. A dedicated AI-native platform chapter is out of scope; optional assist features may appear only as a paved-road interface with fail-closed authority.

## Northwind platform narrative

The same Northwind Commerce system continues as the production context:

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

The critical business outcome remains:

> A valid order is durably accepted and reaches a correct terminal state without duplicate charge, invalid inventory state, or permanent disappearance.

The critical platform outcome is:

> Application teams can finish a production job on a reviewed paved road, inside an explicit tenant boundary, without inheriting shared cluster authority; the platform product has an owner, a contract, an exit, quota, and evidence that a control-plane failure does not take every tenant down.

## Cumulative platform story

Northwind begins with a working delivery path and a working security path for one team. Every new team still copies manifests, files tickets for environments, and shares cluster-admin authority. A Fulfillment team must ship `fulfillment-api` without becoming a second unofficial platform.

Across the book, the reader will:

1. define the platform as a product with users, jobs, promise, and non-goals;
2. decide which capabilities to productize and which to leave with application teams;
3. model tenants, teams, and isolation boundaries;
4. publish a catalog and ownership map other teams can trust;
5. build a paved road with conformance evidence and a supported exit;
6. offer self-service environments that do not share blast radius;
7. abstract infrastructure behind versioned, reviewable contracts;
8. operate the shared control plane as a product with tenant-scoped authority;
9. enforce guardrails and exceptions without trapping teams;
10. measure developer experience with evidence that vanity cannot satisfy;
11. allocate quota, cost, and capacity across tenants;
12. onboard, upgrade, deprecate, and migrate the fleet;
13. support, escalate, and change the platform without informal heroics;
14. recover a control-plane failure while tenant data planes remain bounded.

The cumulative product failure is shared authority: a platform that is really a ticket queue plus a cluster everyone can break. Early chapters make the product and tenancy explicit. Middle chapters make the paved road, environments, and control plane consumable. Later chapters prove fleet change, support, and control-plane recovery.

The second tenant is a teaching thread, not a claim that two teams represent every organization.

## Teaching contract

- Preserve the series' production focus: every chapter must enable a consequential platform decision, produce an operational capability, or establish a mental model required by later production work.
- Do not enforce a theory-to-practice percentage.
- Do not add an exercise merely to make a concept appear practical.
- **Decision 001** in `SERIES-DECISIONS.md` (Accepted, 2026-08-15) applies: important operational concepts may lead chapters without artificial practice. There is no theory-to-practice ratio.
- Concept-led chapters may produce a product brief, tenancy model, decision record, or measurement contract rather than executable code.
- Every substantial conceptual section must be traceable to a chapter decision, durable reasoning artifact, interpretation of evidence, failure diagnosis, or later implementation dependency.
- Implementation-led chapters must tell the reader what to change, why it matters, how to apply it safely, how it can fail, and what evidence proves the result.
- Decision-led chapters must compare defensible alternatives against explicit user jobs, isolation constraints, failure modes, and recovery consequences.
- Each chapter answers one primary production platform question.
- Chapters must distinguish mechanism evidence from outcome evidence. A portal, catalog, scorecard, or provisioner must not be treated as proof that teams can finish jobs.
- A paved road is a product contract, not a mandate. Every golden path needs a supported exit, an owner, and a review trigger.
- Tenancy is an isolation and authority boundary, not a naming convention in a YAML label.
- Platform-product indicators are not SRE portfolio objectives. Call unreliability against those indicators a **job-time budget**. Reserve **error budget** for SRE portfolio governance. Do not smuggle error-budget governance or regional-loss design into this book.
- Near `What You Learned`, identify one or two durable outputs worth retaining.
- On first use in each reader-facing document, write an abbreviation followed by its full form and bold the complete expression. Do not alter literal code, commands, filenames, paths, keys, image names, or version identifiers.
- Use one cumulative implementation under `books/practical-engineering/labs/platform/northwind/`.
- The manuscript is the guide; repository artifacts make product contracts, tenancy, paved roads, environments, control-plane operations, and recovery runnable or inspectable where that adds learning value.
- Local deterministic exercises must state what they simulate and what would require validation against a real portal, identity provider, cluster fleet, cost system, or ticketing system.

## Recurring principles and platform questions

The five series-wide principles remain active:

1. **Blast-radius control:** expose the smallest defensible scope to uncertain change, attack, or failure.
2. **Explicit contracts:** make identity, authority, trust, state, policy, outcomes, and failure behavior reviewable.
3. **Trustworthy evidence:** separate observations and expectations so a mechanism cannot approve itself.
4. **Reconciliation:** compare desired, recorded, external, and actual state, then make disagreement visible and owned.
5. **Recovery:** distinguish corrective action from proof that the protected outcome and required trust are healthy again.

Platform chapters apply four recurring platform questions rather than a second list of principles:

1. Who is the user, and what job must finish?
2. What isolation boundary limits tenant blast radius?
3. What contract can a team rely on, and how do they leave it?
4. What evidence proves the platform product is healthy—not only a tenant workload?

Dedicated failures must name the relevant series principles and answer the platform questions that materially apply. They must not repeat labels that have no bearing on the scenario.

## Chapter forms

### Concept-led chapter

production problem → complete mental model → applied decision cases → consequences → durable reasoning artifact → connection to later implementation

### Implementation-led chapter

production problem → necessary concepts → baseline evidence → guided implementation → failure → diagnosis → containment or recovery → verified outcome

### Decision-led chapter

production problem → competing approaches → user-job and operational trade-offs → production recommendation → decision record → review trigger

### Hybrid chapter

Use only when a concept or decision must immediately govern an implementation. The chapter must still have one primary question and one coherent outcome.

## Proposed chapter index

0. How to Use This Book
1. Define the Platform as a Product
2. Decide Which Capabilities Become Platform Products
3. Model Tenants, Teams, and Isolation Boundaries
4. Publish a Software Catalog and Ownership Map
5. Build a Paved Road Teams Can Leave
6. Offer Self-Service Environments Without Sharing Blast Radius
7. Abstract Infrastructure Behind Reviewable Contracts
8. Operate a Shared Control Plane as a Product
9. Enforce Guardrails Without a Golden Cage
10. Measure Developer Experience Without Vanity Metrics
11. Allocate Quota, Cost, and Capacity Across Tenants
12. Run Fleet Lifecycle: Onboard, Upgrade, Deprecate
13. Support, Escalate, and Change the Platform Safely
14. Recover a Control-Plane Failure Without Taking Tenants With It
15. Conclusion — An Owned Internal Platform

## Initial chapter-form allocation

| Chapter | Primary form | Primary outcome |
|---:|---|---|
| 1 | Concept-led | Platform product brief: users, jobs, promise, non-goals, owners |
| 2 | Decision-led | Capability intake record: productize, leave with teams, or decline |
| 3 | Concept-led | Tenant and isolation model with authority boundaries |
| 4 | Implementation-led | Catalog entries with owners, dependencies, and stale-data failure |
| 5 | Hybrid | Paved-road contract, conformance evidence, and supported exit |
| 6 | Implementation-led | Self-service environment product with TTL, quota, and isolation |
| 7 | Implementation-led | Versioned infrastructure contracts tenants consume without owning modules |
| 8 | Implementation-led | Shared control plane with tenant-scoped authority and upgrade evidence |
| 9 | Hybrid | Guardrail defaults, exception lifecycle, and scorecards that are not cages |
| 10 | Decision-led | Developer-experience measurement contract that rejects vanity |
| 11 | Implementation-led | Tenant quota, showback, and platform unit-cost model |
| 12 | Implementation-led | Onboard, upgrade, deprecate, and migrate with freeze and rollback |
| 13 | Implementation-led | Support model, escalation, and platform-change authority |
| 14 | Implementation-led | Control-plane recovery that leaves tenant data planes bounded |

## Resolved structural decisions

- Keep Chapters 1 and 2 separate: defining the product is not the same decision as which capabilities join it.
- Keep Chapters 3 and 4 separate: tenancy is an isolation model; the catalog is the discoverable ownership surface.
- Keep Chapters 5 and 9 separate: a paved road is a supported path; guardrails are the defaults and exceptions around every path, including exits.
- Keep Chapters 6 and 7 separate: an environment product is not the same as the infrastructure contract underneath it.
- Keep Chapter 8 after environments and abstractions: the shared control plane is the product that reconciles those contracts.
- Keep Chapter 10 before quota: measurement that can be gamed must be settled before cost and capacity numbers are treated as product evidence.
- Keep Chapter 14 after support and fleet change so recovery is tested against a platform that already has tenants, upgrades, and escalation.
- Do not include a dedicated AI-platform chapter.
- Do not include a dedicated SRE reliability, game-day, or multi-region chapter.
- Inherit reduced DevOps and DevSecOps interfaces through checksum-identified fixtures. The lab never reads those working trees at runtime.
- Chapter 9 exception rows reference an inherited DevSecOps exception ID. They do not duplicate owner, scope, compensation, or expiry.
- Use deterministic local evaluators. The lab does not run a real developer portal, identity provider, cluster fleet, or billing system.

## Authorized drafting

The planning set is frozen. Draft How to Use This Book, then Chapter 1, and scaffold the companion lab according to `LAB-PLAN.md`. Do not change the promise, boundaries, chapter count or order, cumulative narrative, evidence taxonomy, inherited-baseline strategy, or safety contract without a new planning version.
