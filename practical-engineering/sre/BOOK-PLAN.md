# Practical SRE Engineering — Book Plan

**Planning status:** Frozen  
**Draft date:** 2026-08-16  
**Freeze date:** 2026-08-16  
**Drafting gate:** Chapter drafting must conform to this frozen plan or use an explicitly versioned plan revision.

## Promise

Govern reliability across Northwind's service portfolio: user-visible **SLOs (Service Level Objectives)** for Storefront and Fulfillment, error-budget policy that can freeze change, an on-call system rather than a hero roster, recurring game days, and recovery from regional loss without inventing the plan during the outage.

The reader will learn to decide which user journeys reliability must protect, choose **SLIs (Service Level Indicators)** users can feel, set portfolio SLOs and error budgets, write policy that can stop change when budget is exhausted, page on burn rather than on every symptom, design on-call as a system, bound toil, put dependencies inside the reliability contract, degrade before failure cascades, command multi-service incidents, turn incidents into a learning program, design for the loss of a region, run game days as a recurring program, and fail over a region without taking the portfolio down.

## Audience

This book is for intermediate-to-advanced DevOps, cloud, infrastructure, platform, security, and **SRE (Site Reliability Engineering)** practitioners. Readers should already understand Linux, Git, containers, **CI/CD (Continuous Integration and Continuous Delivery)**, cloud and Kubernetes fundamentals, infrastructure as code, networking, workload identity, observability, incident coordination for a single failed change, reconstruction of one environment, and the platform-product, tenancy, and fleet contracts taught in *Practical Platform Engineering*.

The book does not teach those subjects from first principles. It teaches the portfolio reliability decisions required to govern SLOs, error budgets, on-call, game days, and regional loss across services that already have a delivery path, a security path, and an owned internal platform.

## Relationship to earlier books

*Practical DevOps Engineering* established one team's production delivery path for Northwind: fast feedback, verifiable artifacts, reconciled infrastructure, bounded runtime, workload identity, observable outcomes, progressive delivery, compatible data change, safe asynchronous processing, GitOps, cost and capacity, incident coordination, and reconstruction from durable evidence. Chapter 6 defined provisional service-level indicators and a burn policy for Storefront. Chapter 12 coordinated one failed production change. Chapter 13 reconstructed one environment. Those remain single-path capabilities.

*Practical DevSecOps Engineering* made security of that same path explicit: assets and harms, threat and risk decisions, attributable identity, privileged delegation, supply-chain trust, vulnerability treatment, secrets, data protection, policy, runtime confinement, detection, investigation, eradication, bounded restored trust, and operational governance.

*Practical Platform Engineering* turned repeated delivery and security capabilities into an owned internal platform product: users, jobs, tenancy, catalog, paved road, environments, contracts, shared control plane, guardrails, developer-experience measurement, quota, fleet lifecycle, support and escalation, and control-plane recovery that keeps tenant data planes bounded. Platform-product indicators such as time-to-first-environment remain a **job-time budget**. Escalation contacts exist; they are not an on-call system. Chapter 14 explicitly refused regional-loss architecture and a portfolio **RTO (Recovery Time Objective)**. Remaining owner `reliability-program` holds portfolio SLO governance.

This book consumes those capabilities as prerequisites. It may briefly restate an inherited contract when a reliability decision depends on it, but it must not reteach a DevOps, DevSecOps, or Platform chapter or reproduce those implementations as new SRE work.

The published DevOps, DevSecOps, and Platform v1.0 manuscripts remain unchanged. This book uses a separate manuscript directory and a separate cumulative lab.

## Series authority

This plan depends on `SERIES-DECISIONS.md` as the series-level record, not as a book-local file.

- **Decision 001** (Accepted, 2026-08-15; applies from DevSecOps and every later book): important operational concepts may lead chapters without an artificial practice exercise. There is no theory-to-practice ratio. Conceptual material must remain in operational scope, enable a later production decision, and not become a beginner survey. SRE inherits the no-ratio rule; domain-specific concept lists stay book-local.
- **Decision 002:** shared Word publication style.
- **Decision 003:** first published edition of every book is v1.0.
- **Decision 004:** *Practical SRE Engineering* is the planned fourth book. Its lab inherits checksum-identified interfaces from DevOps, DevSecOps, and Platform.

## Scope

This book owns reliability across Northwind's service portfolio:

- reliability outcomes as user-visible journeys rather than component uptime or availability theater;
- SLI selection for Storefront, Fulfillment, and other user-facing services, distinct from platform-product job-time indicators;
- portfolio SLO targets, windows, and error budgets;
- error-budget policy that can continue, slow, or freeze change—including fleet change Platform already knows how to freeze for upgrades;
- burn-rate alerting that pages people, not every red graph;
- on-call as a designed system: rotation, load, escalation, handoff, and authority;
- toil measurement and bounds so reliability engineering remains possible;
- dependency reliability: payment, warehouse, email, and other providers inside the contract;
- deliberate degradation, load shedding, and protection against cascading failure;
- incident command across services and tenants, not only one failed change on one path;
- blameless learning as a reliability control with owned, verified follow-through;
- regional-loss architecture, portfolio RTO and **RPO (Recovery Point Objective)**, and fail-over evidence;
- recurring game days that can fail safely and that exercise more than one mixed-backup fixture.

## Boundaries

### DevOps boundary

This book does not reteach pipeline performance, artifact promotion, infrastructure reconciliation for one team, Kubernetes runtime fundamentals, observability fundamentals, progressive delivery, schema evolution, messaging correctness, GitOps for a single application, FinOps of one workload path, general incident coordination of one failed change, or reconstruction of one environment. It consumes those capabilities so a portfolio can be governed. Provisional Storefront SLIs and burn alerts from DevOps Chapter 6 are an inherited interface, not a chapter to rewrite.

### DevSecOps boundary

This book may use security evidence to bound reliability changes and to keep break-glass on-call authority attributable. It does not rebuild threat modeling, risk registers, supply-chain admission, vulnerability prioritization, secret lifecycle, detection engineering, investigation, containment, eradication, or restored-trust claims. Those remain DevSecOps outcomes. Reliability recovery is not **Evidence of restored trust**.

### Platform Engineering boundary

This book inherits the platform product rather than rediscovering it. Jobs `obtain-bounded-environment`, `ship-on-paved-road`, and `publish-owned-path` are already named. Tenancy, catalog ownership, paved roads, environments, contracts, control-plane operation, guardrails, developer-experience measurement, quota, fleet lifecycle, support, and bounded control-plane recovery remain Platform. Platform-product unreliability stays a job-time budget. This book may freeze a fleet because an error budget is exhausted; it does not redesign fleet upgrade, deprecation, or tenant isolation. Escalation contacts from the catalog are inputs to on-call design, not a substitute for it. Plane last known good `1.0` and contract `tenant-storage` `1.0` must not collapse into one restore identity, and neither is regional fail-over.

### Governance boundary

This book explains how SLO reports, error-budget decisions, incident records, and game-day evidence produce material useful to governance. It does not certify Northwind against a legal or industry framework, write customer **SLAs (Service Level Agreements)** as a legal product, or reduce SRE to a dashboard of nines.

### Specialist boundaries

The book does not replace a complete observability-stack textbook, chaos-engineering product manual, public-cloud multi-region reference, queueing-theory course, or incident-command handbook. It includes only the depth needed for the production decisions in scope. A dedicated AI-ops or AI-SRE chapter is out of scope.

## Northwind reliability narrative

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

reliability program (this book):
   user journeys → SLOs → error budgets → on-call →
   learning → game days → regional loss
```

The critical business outcome remains:

> A valid order is durably accepted and reaches a correct terminal state without duplicate charge, invalid inventory state, or permanent disappearance.

The critical reliability outcome is:

> Storefront and Fulfillment keep user-visible SLOs; exhausted error budget can freeze change, including fleet change; on-call and learning are systems rather than heroics; a region can be lost and the portfolio recovered from a reviewed plan, with evidence that this is not reconstruction of one environment or restore of one control plane.

## Cumulative reliability story

Northwind begins with a working delivery path, a working security path, and an owned platform product. Storefront has provisional indicators. Fulfillment is a second tenant with catalog owners and escalation contacts. Each service can look "up" while a user journey fails. Error budget does not stop change. On-call is whoever answered Slack. Platform Chapter 14 can restore a plane without taking tenants with it, and still cannot fail over a region.

Across the book, the reader will:

1. define which user journeys reliability must protect, and refuse availability theater;
2. choose SLIs users can feel, without promoting platform job-time or component uptime to portfolio SLOs;
3. set SLO targets, windows, and error budgets across Storefront, Fulfillment, and named supporting journeys;
4. write error-budget policy that can continue, slow, or freeze change;
5. page on burn rate rather than on every symptom;
6. design on-call as a rotation with load, escalation, handoff, and authority;
7. measure and bound toil so reliability engineering remains possible;
8. put payment, warehouse, email, and other dependencies inside the reliability contract;
9. degrade and shed load before failure cascades;
10. command incidents that span services and tenants;
11. turn incidents into a learning program with owned, verified follow-through;
12. design for the loss of a region, including portfolio RTO and RPO;
13. run game days as a recurring program that can fail safely;
14. fail over a region without taking the portfolio down, and prove recovery with evidence.

The cumulative reliability failure is availability theater plus informal heroics: green graphs, exhausted budgets that do not freeze change, Slack-as-on-call, and a regional outage whose plan is invented during the event. Early chapters make journeys, SLIs, SLOs, and policy explicit. Middle chapters make alerting, on-call, toil, dependencies, and degradation operable. Later chapters prove portfolio incident command, learning, game days, and regional fail-over.

The second user-facing service is a teaching thread, not a claim that two services represent every organization.

## Teaching contract

- Preserve the series' production focus: every chapter must enable a consequential reliability decision, produce an operational capability, or establish a mental model required by later production work.
- Do not enforce a theory-to-practice percentage.
- Do not add an exercise merely to make a concept appear practical.
- **Decision 001** in `SERIES-DECISIONS.md` (Accepted, 2026-08-15) applies: important operational concepts may lead chapters without artificial practice. There is no theory-to-practice ratio.
- Concept-led chapters may produce a reliability brief, SLI/SLO decision record, on-call model, or learning-program contract rather than executable code.
- Every substantial conceptual section must be traceable to a chapter decision, durable reasoning artifact, interpretation of evidence, failure diagnosis, or later implementation dependency.
- Implementation-led chapters must tell the reader what to change, why it matters, how to apply it safely, how it can fail, and what evidence proves the result.
- Decision-led chapters must compare defensible alternatives against explicit user journeys, error-budget consequences, operational load, and recovery consequences.
- Each chapter answers one primary production reliability question.
- Chapters must distinguish mechanism evidence from outcome evidence. A dashboard, alert rule, paging vendor, postmortem template, or fail-over runbook must not be treated as proof that users kept their SLO or that a region recovered.
- Platform-product indicators remain a job-time budget. Do not rename them portfolio SLOs. Do not spend Storefront `order_success_ratio` as proof that a platform job finished, and do not spend time-to-first-environment as proof that orders succeeded.
- Reserve **error budget** for SRE portfolio governance. A Platform fleet freeze for an upgrade is not an error-budget freeze. An error-budget freeze may halt fleet change for a reason Platform did not own.
- **SLA** is a customer or legal promise. **SLO** is the internal reliability contract that error budget governs. Do not treat them as synonyms.
- Reliability recovery after regional loss is **Evidence of portfolio recovery**. It is not DevSecOps restored trust, not DevOps reconstruction of one environment, and not Platform **Evidence of bounded platform-product recovery**.
- Near `What You Learned`, identify one or two durable outputs worth retaining.
- On first use in each reader-facing document, write an abbreviation followed by its full form and bold the complete expression. Do not alter literal code, commands, filenames, paths, keys, image names, or version identifiers.
- Use one cumulative implementation under `books/practical-engineering/labs/sre/northwind/`.
- The manuscript is the guide; repository artifacts make SLO contracts, error-budget policy, on-call, incidents, game days, and regional recovery runnable or inspectable where that adds learning value.
- Local deterministic exercises must state what they simulate and what would require validation against a real telemetry backend, paging system, identity provider, multi-region fleet, or incident tool.

## Recurring principles and reliability questions

The five series-wide principles remain active:

1. **Blast-radius control:** expose the smallest defensible scope to uncertain change, attack, or failure.
2. **Explicit contracts:** make identity, authority, trust, state, policy, outcomes, and failure behavior reviewable.
3. **Trustworthy evidence:** separate observations and expectations so a mechanism cannot approve itself.
4. **Reconciliation:** compare desired, recorded, external, and actual state, then make disagreement visible and owned.
5. **Recovery:** distinguish corrective action from proof that the protected outcome and required trust are healthy again.

SRE chapters apply four recurring reliability questions rather than a second list of principles:

1. What user-visible journey is at risk, and for which services?
2. What error budget remains, and what change does it authorize or freeze?
3. What human system absorbs the failure without informal heroics?
4. What evidence proves the portfolio recovered—not only one service, one environment, or one control plane?

Dedicated failures must name the relevant series principles and answer the reliability questions that materially apply. They must not repeat labels that have no bearing on the scenario.

## Chapter forms

### Concept-led chapter

production problem → complete mental model → applied decision cases → consequences → durable reasoning artifact → connection to later implementation

### Implementation-led chapter

production problem → necessary concepts → baseline evidence → guided implementation → failure → diagnosis → containment or recovery → verified outcome

### Decision-led chapter

production problem → competing approaches → user-journey and operational trade-offs → production recommendation → decision record → review trigger

### Hybrid chapter

Use only when a concept or decision must immediately govern an implementation. The chapter must still have one primary question and one coherent outcome.

## Proposed chapter index

0. How to Use This Book
1. Define What Reliability Must Protect
2. Choose Indicators Users Can Feel
3. Set SLOs and Error Budgets Across the Portfolio
4. Govern Change with Error-Budget Policy
5. Page on Burn Rate, Not on Every Symptom
6. Design On-Call as a System
7. Measure and Bound Toil Without Hiding the Work
8. Put Dependencies Inside the Reliability Contract
9. Degrade Deliberately Before Failure Cascades
10. Command Incidents Across Services and Tenants
11. Turn Incidents into a Reliability Learning Program
12. Design for the Loss of a Region
13. Run Game Days as a Recurring Program
14. Fail Over a Region Without Taking the Portfolio Down
15. Conclusion — A Governed Reliability Portfolio

## Initial chapter-form allocation

| Chapter | Primary form | Primary outcome |
|---:|---|---|
| 1 | Concept-led | Reliability brief: protected journeys, refused uptime theater, remaining owners |
| 2 | Decision-led | SLI selection record that rejects component uptime and platform job-time as portfolio SLIs |
| 3 | Implementation-led | Portfolio SLO catalog with windows, targets, and error budgets for Storefront and Fulfillment |
| 4 | Hybrid | Error-budget policy that can continue, slow, or freeze change, including fleet change |
| 5 | Implementation-led | Multi-window burn alerts that page on user-journey burn and ticket the rest |
| 6 | Hybrid | On-call system: rotation, load, escalation from catalog contacts, handoff, authority |
| 7 | Decision-led | Toil definition, measurement contract, and bound that protects engineering time |
| 8 | Implementation-led | Dependency reliability contract for payment, warehouse, and non-critical email |
| 9 | Implementation-led | Degradation and load-shedding policy that prevents cascade |
| 10 | Implementation-led | Multi-service incident command with distinct roles and portfolio evidence |
| 11 | Decision-led | Learning-program contract: blameless records, owned actions, verification, review cadence |
| 12 | Concept-led | Regional-loss architecture with portfolio RTO, RPO, and data-gravity constraints |
| 13 | Implementation-led | Recurring game-day program that can fail safely and that exercises more than one fixture |
| 14 | Implementation-led | Regional fail-over that preserves tenant isolation and proves portfolio recovery |

## Resolved structural decisions

- Keep Chapters 1 and 2 separate: naming the protected journey is not the same decision as choosing the indicator.
- Keep Chapters 3 and 4 separate: publishing targets and budgets is not the policy that can freeze a fleet when budget is exhausted.
- Keep Chapter 5 after policy: burn alerting implements the budget; it is not the budget.
- Keep Chapter 6 after alerting: Northwind pages a designed on-call system, not a Slack channel discovered at page time.
- Keep Chapter 7 as decision-led: toil is a work-allocation decision, not a new observability stack.
- Keep Chapters 8 and 9 separate: a dependency contract is not the same as how Northwind's own services shed load.
- Keep Chapters 10 and 11 separate: commanding an incident is not the learning program that must follow it.
- Keep Chapters 12, 13, and 14 separate: regional architecture, the recurring proof program, and executed fail-over are three production questions. Game days must be able to exercise error-budget freeze, on-call, dependency loss, and regional loss—not only one mixed-backup fixture.
- Do not include a dedicated AI-SRE, observability-vendor, or chaos-product chapter.
- Do not reteach DevOps Chapter 6 telemetry, Chapter 12 one-change incident coordination, or Chapter 13 one-environment reconstruction.
- Do not collapse platform job-time budget into portfolio error budget. Consume Platform job proofs as adjacent evidence.
- Inherit reduced DevOps, DevSecOps, and Platform interfaces through checksum-identified fixtures. The lab never reads those working trees at runtime.
- Use deterministic local evaluators. The lab does not run a real telemetry backend, paging vendor, multi-region fleet, or incident-management product.

## Authorized drafting

The planning set is frozen. Draft How to Use This Book, then Chapter 1, and scaffold the companion lab according to `LAB-PLAN.md`. Do not change the promise, boundaries, chapter count or order, cumulative narrative, evidence taxonomy, inherited-baseline strategy, or safety contract without a new planning version.

When drafting Chapter 13, game days must exercise error-budget freeze, on-call page path, dependency loss, and regional-loss tabletop or simulated fail-over. They must not be only a rehearsal of Chapter 14 fail-over.
