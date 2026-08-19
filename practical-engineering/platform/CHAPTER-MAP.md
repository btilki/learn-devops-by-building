# Practical Platform Engineering — Chapter Map

**Status:** Frozen  
**Freeze date:** 2026-08-16  
**Depends on:** `BOOK-PLAN.md`  
**Drafting gate:** Chapter drafting must conform to this frozen map or use an explicitly versioned plan revision.

## Cumulative state contract

Each chapter inherits the completed platform state of the previous chapter. Concept- and decision-led chapters change Northwind's reviewed platform model; implementation-led chapters change enforceable product behavior. Later implementation must consume earlier decisions rather than silently replacing them.

Each chapter must distinguish:

- **mechanism evidence:** proof that a catalog, portal, provisioner, controller, or scorecard operated;
- **decision evidence:** proof that an owner evaluated user jobs, isolation, and trade-offs;
- **outcome evidence:** proof that a team finished a production job inside the contract; and
- **recovery evidence:** proof that tenant blast radius was restored—not merely that a ticket closed.

Failure exercises use three explicit relationships to the book's main storyline:

- **Cumulative product failure:** advances shared-authority and ticket-queue harm.
- **Connected consequence:** demonstrates harm enabled by an earlier platform decision.
- **Independent control failure:** proves that the control matters even without the cumulative story.

## Chapter 1 — Define the Platform as a Product

- **Form:** Concept-led
- **Production question:** Who is the platform for, what jobs must it finish, and what does it refuse to own?
- **Start:** Storefront can deliver and secure one path. Other teams treat the platform group as a ticket queue with cluster access.
- **Pressure:** Work is selected by whoever shouts, success is "we built a portal," and no one can name the user or the non-goal.
- **Concepts:** internal product, user, job-to-be-done, promise, non-goal, service owner, platform-product indicator versus tenant workload indicator.
- **Decision/capability:** Write a product brief with users, jobs, in-scope capabilities, explicit refusals, owners, and the evidence that would prove the product works.
- **Lab artifacts:** `product/brief.yaml`, `product/users.yaml`, `product/jobs.yaml`, `product/non-goals.yaml`.
- **Evidence:** Every job names a user, a finished outcome, an owner, and a later proof; every refusal names the team that still owns the work.
- **Durable outputs:** Platform product brief; job-and-refusal register.
- **Independent control failure:** A portal launch is counted as success while time-to-first-environment and paved-road completion are unowned.
- **Correction:** Replace portal-launch evidence with job-completion evidence and assign owners.
- **Next:** Northwind knows the product but not which repeated capabilities should join it.

## Chapter 2 — Decide Which Capabilities Become Platform Products

- **Form:** Decision-led
- **Production question:** Which repeated capabilities should the platform own, which should stay with application teams, and which should be declined?
- **Start:** The product brief exists. Every painful YAML copy and every security default is proposed as "a platform thing."
- **Pressure:** Centralizing everything creates a golden cage; productizing nothing leaves every team to rebuild the path.
- **Concepts:** demand, repetition, differentiation, cognitive load, support cost, reversible extraction, thin platform versus thick platform.
- **Decision/capability:** Adopt an intake method and record productize / leave / decline decisions with review triggers.
- **Lab artifacts:** `intake/method.yaml`, `intake/candidates.yaml`, `intake/decisions.yaml`.
- **Evidence:** Each decision traces to a user job, repetition evidence, isolation impact, support cost, and an owner.
- **Durable outputs:** Capability intake method; first productization decisions.
- **Independent control failure:** Custom order-pricing logic is accepted as a platform capability because two teams asked for it.
- **Correction:** Decline it as application differentiation; keep environment provisioning and artifact promotion on the intake path.
- **Next:** Capabilities are chosen, but tenant boundaries are still labels on a shared cluster.

## Chapter 3 — Model Tenants, Teams, and Isolation Boundaries

- **Form:** Concept-led
- **Production question:** Where does one team's change, credential, or failure stop?
- **Start:** Storefront and the incoming Fulfillment team share cluster-admin patterns and a namespace-as-name convention.
- **Pressure:** A debug RoleBinding or a noisy workload can become every team's incident.
- **Concepts:** tenant, team, environment, isolation dimension (identity, network, quota, secrets, change authority), shared-nothing versus shared-control-plane, noisy neighbor.
- **Decision/capability:** Define tenant identities, isolation dimensions, allowed sharing, and the authority each role may never inherit.
- **Lab artifacts:** `tenancy/tenants.yaml`, `tenancy/isolation.yaml`, `tenancy/roles.yaml`, `tenancy/sharing.yaml`.
- **Evidence:** Every tenant has an owner, isolation dimensions, prohibited inherited roles, and a blast-radius statement.
- **Durable outputs:** Tenant-and-isolation model; role boundary map.
- **Cumulative product failure:** Fulfillment inherits cluster-admin "temporarily" to ship faster, collapsing isolation before the catalog exists.
- **Correction:** Replace inherited cluster-admin with tenant-scoped roles and record the shared-authority path as the cumulative failure to interrupt.
- **Next:** Isolation is defined, but teams cannot discover owners, dependencies, or the paved road.

## Chapter 4 — Publish a Software Catalog and Ownership Map

- **Form:** Implementation-led
- **Production question:** How do teams find the service, owner, dependencies, and support path without asking the platform group?
- **Start:** Tenants exist on paper. Ownership lives in chat history and stale READMEs.
- **Pressure:** An incident or dependency change cannot find an owner; orphan services accumulate.
- **Concepts:** software catalog, system of record, owner, lifecycle status, dependency, stale metadata, catalog as contract not wiki.
- **Decision/capability:** Publish catalog entries for storefront, fulfillment, and platform products with owners, dependencies, and freshness checks.
- **Lab artifacts:** `catalog/systems.yaml`, `catalog/ownership.yaml`, `catalog/dependencies.yaml`, catalog evaluator.
- **Evidence:** Every runnable system has a living owner, on-call or escalation contact, dependency list, and a failed check when metadata is stale.
- **Durable outputs:** Catalog ownership map; stale-entry failure contract.
- **Independent control failure:** A renamed team leaves `fulfillment-api` owned by a deleted group while the catalog still reports green.
- **Correction:** Fail freshness and ownership checks; require a living owner before the entry can be complete.
- **Next:** Teams can find systems, but each still copies a private path to production.

## Chapter 5 — Build a Paved Road Teams Can Leave

- **Form:** Hybrid
- **Production question:** What supported path gets a team to production, and how do they leave it without becoming unsupported?
- **Start:** Catalog ownership exists. Storefront's working path is still tribal knowledge; Fulfillment copies YAML.
- **Pressure:** A mandatory golden path becomes a cage; an undocumented escape becomes shadow infrastructure.
- **Concepts:** paved road, golden path, scaffolding, conformance, supported exit, versioned path, deprecation of unofficial paths.
- **Decision/capability:** Define the default path, conformance evidence, a reviewed exit, and the support difference between paved and exited.
- **Lab artifacts:** `paved-road/contract.yaml`, `paved-road/scaffold.yaml`, `paved-road/conformance.yaml`, `paved-road/exits.yaml`.
- **Evidence:** A new service can complete the path; an exit names owner, lost defaults, remaining guardrails, and review date.
- **Durable outputs:** Paved-road contract; supported-exit record.
- **Connected consequence:** Fulfillment forks the path unofficially to skip a slow template, losing identity and artifact defaults.
- **Correction:** Register an explicit exit or return to the paved road; unofficial forks fail conformance.
- **Next:** The path exists, but environments are still tickets against a shared cluster.

## Chapter 6 — Offer Self-Service Environments Without Sharing Blast Radius

- **Form:** Implementation-led
- **Production question:** How can a team obtain a bounded environment without inheriting everyone else's cluster?
- **Start:** The paved road assumes an environment. Provisioning is a ticket; namespaces share quota and credentials.
- **Pressure:** Wait time returns, or self-service creates unbounded namespaces with production-like authority.
- **Concepts:** environment as product, request, TTL, quota, network isolation, credential scoping, ephemeral versus durable environments.
- **Decision/capability:** Offer a requestable environment product with tenant isolation, expiry, and evidence that storefront cannot consume fulfillment credentials.
- **Lab artifacts:** `environments/product.yaml`, `environments/requests.yaml`, `environments/leases.yaml`, environment evaluator.
- **Evidence:** A request creates a tenant-scoped environment; expiry reclaims it; cross-tenant secret or network use fails.
- **Durable outputs:** Environment product contract; lease and isolation evidence.
- **Cumulative product failure:** A shared "dev cluster admin" still lets Fulfillment scale Storefront's environment to steal quota.
- **Correction:** Enforce tenant quota and deny cross-tenant mutation; record isolation as a product invariant.
- **Next:** Environments exist, but teams still own raw modules instead of versioned contracts.

## Chapter 7 — Abstract Infrastructure Behind Reviewable Contracts

- **Form:** Implementation-led
- **Production question:** What contract can a team rely on without owning the underlying infrastructure modules?
- **Start:** Isolated environments still require each team to compose storage, identity, and networking primitives.
- **Pressure:** Abstractions that hide too much become magic; abstractions that hide too little recreate the ticket queue.
- **Concepts:** infrastructure API, composition, versioned contract, compatibility, leaky abstraction, platform-owned module versus tenant parameters.
- **Decision/capability:** Publish versioned contracts for the capabilities tenants may request, with compatibility and change rules.
- **Lab artifacts:** `contracts/catalog.yaml`, `contracts/versions.yaml`, `contracts/compatibility.yaml`, contract evaluator.
- **Evidence:** A tenant request binds to a contract version; a breaking change is rejected or migrated; hidden module internals are not tenant API.
- **Durable outputs:** Infrastructure contract catalog; compatibility policy.
- **Independent control failure:** A module refactor changes a tenant-visible field without a contract version, breaking fulfillment silently.
- **Correction:** Fail compatibility; require a versioned contract change and a migration note.
- **Next:** Contracts exist, but the shared reconciler that applies them is still an unofficial cluster operator.

## Chapter 8 — Operate a Shared Control Plane as a Product

- **Form:** Implementation-led
- **Production question:** How does the shared control plane reconcile tenant intent without becoming shared root?
- **Start:** Contracts are versioned. A single reconciler still runs with broad authority and no tenant-scoped subject.
- **Pressure:** Control-plane convenience recreates cluster-admin; tenants cannot tell whether the plane is a product or a privileged script.
- **Concepts:** control plane, tenant-scoped subject, admission, reconcile versus rewrite, plane upgrade, last-known-good plane.
- **Decision/capability:** Operate the reconciler as a product: tenant-scoped authority, admission of contract versions, separate plane identity, and upgrade evidence.
- **Lab artifacts:** `control-plane/product.yaml`, `control-plane/subjects.yaml`, `control-plane/admission.yaml`, `control-plane/reconciliation.yaml`.
- **Evidence:** The plane cannot approve its own change; it cannot mutate another tenant; a failed plane upgrade retains last known good.
- **Durable outputs:** Control-plane product contract; tenant-scoped authority map.
- **Cumulative product failure:** The reconciler uses a cluster-admin token "so onboarding works," allowing one tenant intent to mutate another.
- **Correction:** Split plane identity from tenant identity; deny cross-tenant reconcile; require reviewed plane upgrades.
- **Next:** The plane is a product, but defaults either trap teams or can be switched off quietly.

## Chapter 9 — Enforce Guardrails Without a Golden Cage

- **Form:** Hybrid
- **Production question:** Which defaults must the platform enforce, and how do exceptions stay temporary without trapping teams?
- **Start:** Control-plane authority is scoped. Security and delivery defaults from earlier books are either mandatory with no exit or optional with no owner.
- **Pressure:** A cage drives unofficial exits; missing defaults recreate the insecure copy-paste path.
- **Concepts:** guardrail, default, scorecard, exception, expiry, compensation, cage versus road, inherited DevSecOps policy as product interface.
- **Decision/capability:** Ship paved-road defaults, allow reviewed exceptions with expiry, and score conformance without blocking every legitimate exit.
- **Lab artifacts:** `guardrails/defaults.yaml`, `guardrails/scorecards.yaml`, `guardrails/exceptions.yaml` (bindings only), exception-binding evaluator.
- **Evidence:** Defaults apply to the paved road. Each `guardrails/exceptions.yaml` row references an inherited DevSecOps exception ID and must not copy owner, scope, compensation, or expiry. The platform adds tenant, remaining isolation, and scorecard effect. A scorecard cannot pass on an expired inherited exception.
- **Durable outputs:** Guardrail catalog; exception-binding contract.
- **Independent control failure:** A scorecard stays green after an exception expires and a tenant disables artifact digest pinning.
- **Correction:** Fail the scorecard, restore the default or renew the exception, and keep the exit path explicit.
- **Next:** Guardrails exist, but success is still counted in portal clicks and survey smiles.

## Chapter 10 — Measure Developer Experience Without Vanity Metrics

- **Form:** Decision-led
- **Production question:** Which measurements prove teams finish jobs, and which measurements only prove the platform looked busy?
- **Start:** Scorecards exist. Leadership asks for adoption percentage, CSAT, and ticket volume as proof the platform works.
- **Pressure:** Vanity metrics reward forcing teams onto the road and hiding wait time in Slack.
- **Concepts:** developer experience, leading versus lagging evidence, time-to-job, paved-road completion, self-service rate, vanity, Goodhart's law, platform-product SLI versus SRE portfolio SLO.
- **Decision/capability:** Adopt a measurement contract: job-completion times, failure classes, and explicit non-metrics.
- **Lab artifacts:** `devex/contract.yaml`, `devex/indicators.yaml`, `devex/non-metrics.yaml`, `devex/samples.yaml`.
- **Evidence:** Each retained indicator maps to a user job; vanity candidates are recorded as non-metrics; missing samples fail the contract.
- **Durable outputs:** Developer-experience measurement contract; non-metric register.
- **Independent control failure:** Adoption hits 100% after the unofficial path is deleted, while time-to-environment gets worse.
- **Correction:** Fail the measurement contract; restore job-time evidence as the product indicator.
- **Next:** Honest measurements exist, but tenants still contend for unbounded shared capacity.

## Chapter 11 — Allocate Quota, Cost, and Capacity Across Tenants

- **Form:** Implementation-led
- **Production question:** How does the platform allocate scarce capacity so one tenant cannot starve another, and what unit cost is honest?
- **Start:** DevEx indicators exist. Environments and the control plane share an unowned pool.
- **Pressure:** A lower shared bill hides fulfillment starvation, or chargeback without quality gates rewards cheap broken environments.
- **Concepts:** quota, fair share, showback, platform unit (environment-hour, successful provision), quality gate, noisy neighbor, inherited DevOps useful-unit thinking applied to the platform product—not a reteach of order-path FinOps.
- **Decision/capability:** Define tenant quotas, a platform unit with quality gates, and evidence that bursting cannot silently consume another tenant's floor.
- **Lab artifacts:** `quota/tenants.yaml`, `quota/units.yaml`, `quota/showback.yaml`, quota evaluator.
- **Evidence:** A tenant cannot exceed quota; showback uses successful product units; starvation of the other tenant's floor fails the check.
- **Durable outputs:** Tenant quota policy; platform unit-cost model.
- **Connected consequence:** Fulfillment burst consumes Storefront's environment floor after isolation labels exist but quota does not.
- **Correction:** Enforce floors and ceilings; recompute showback on quality-gated units.
- **Next:** Capacity is allocated, but the fleet still cannot upgrade or leave old contracts.

## Chapter 12 — Run Fleet Lifecycle: Onboard, Upgrade, Deprecate

- **Form:** Implementation-led
- **Production question:** How do tenants join, absorb a platform upgrade, and leave an old contract without an outage lottery?
- **Start:** Two tenants consume the platform. Contract v1 must be retired; a new paved-road version is ready.
- **Pressure:** Forced upgrades break tenants; eternal v1 support becomes a second unofficial platform.
- **Concepts:** onboard, compatibility window, freeze, progressive fleet upgrade, deprecation, migration evidence, rollback of a platform version.
- **Decision/capability:** Onboard fulfillment completely, upgrade a contract version with a freeze window, deprecate v1 with evidence, and roll back a failed fleet step.
- **Lab artifacts:** `fleet/onboarding.yaml`, `fleet/upgrades.yaml`, `fleet/deprecations.yaml`, `fleet/migrations.yaml`.
- **Evidence:** Onboarding completes without cluster-admin; an upgrade has freeze, cohort, and rollback; deprecation fails if a tenant remains on v1 after the window with no exception.
- **Durable outputs:** Fleet lifecycle policy; upgrade-and-deprecation record.
- **Cumulative product failure:** Platform v2 is applied to all tenants at once; fulfillment's still-legal v1 contract breaks.
- **Correction:** Restore last-known-good contract version, complete migration evidence, and resume progressive upgrade.
- **Next:** The fleet can move, but platform change still happens through heroes in a shared chat.

## Chapter 13 — Support, Escalate, and Change the Platform Safely

- **Form:** Implementation-led
- **Production question:** Who may change the platform, how are tenant incidents escalated, and what prevents informal production edits?
- **Start:** Fleet upgrades exist. Support is still "message the people who built it."
- **Pressure:** Platform engineers apply live fixes with plane-admin; tenants cannot tell a product incident from an application incident.
- **Concepts:** support tier, escalation, platform incident versus tenant incident, change authority, freeze, communication cadence, job-time budget of the platform product—not the SRE portfolio error budget.
- **Decision/capability:** Define support paths, distinct platform-change authority, and an executed trace that a live unofficial edit is rejected.
- **Lab artifacts:** `support/model.yaml`, `support/escalation.yaml`, `support/changes.yaml`, `support/incidents.yaml`.
- **Evidence:** A tenant ticket maps to a product or application owner; a platform change has a reviewed subject; unofficial plane-admin edits fail.
- **Durable outputs:** Support and escalation model; platform-change authority record.
- **Independent control failure:** An engineer patches the control plane in place to clear a ticket, leaving no review and no last known good.
- **Correction:** Revert to reviewed intent, record a platform incident, and require the change path.
- **Next:** Support is explicit, but a control-plane outage can still become every tenant's outage.

## Chapter 14 — Recover a Control-Plane Failure Without Taking Tenants With It

- **Form:** Implementation-led
- **Production question:** How does Northwind restore the platform product after control-plane loss without reconstructing every tenant as one blast radius?
- **Start:** Support and change authority exist. Backup of the plane is a job-success metric; tenant isolation during restore is undefined.
- **Pressure:** Restoring the plane from a mixed backup can replay one tenant's intent into another, or freeze all application traffic unnecessarily.
- **Concepts:** control-plane evidence versus tenant data-plane evidence, isolated restore, last known good, tenant freeze versus tenant continue, bounded recovery claim. Regional-loss architecture and portfolio RTO programs remain SRE.
- **Decision/capability:** Restore the plane from independently verified evidence, keep tenant data planes bounded, reject mixed-tenant replay, and prove bounded modeled platform-product recovery.
- **Lab artifacts:** `recovery/plane-evidence.yaml`, `recovery/isolation.yaml`, `recovery/restore-trace.yaml`, `recovery/verification.yaml`.
- **Evidence:** Mixed backup is rejected; plane restore does not grant cross-tenant authority; storefront order outcome can continue or is frozen by explicit tenant decision, not by accident; fulfillment isolation holds.
- **Durable outputs:** Control-plane recovery contract; bounded isolation verification.
- **Cumulative product failure:** A corrupted newest plane backup is applied and replays Fulfillment intent into Storefront.
- **Correction:** Reject the corrupt backup, restore last known good plane, verify tenant isolation and product jobs, and record the limitation that this is not a regional-loss program.
- **Next:** The conclusion assembles product, tenancy, paved road, control plane, fleet, support, and bounded recovery into one owned internal platform.

## Chapter 15 — Conclusion — An Owned Internal Platform

The conclusion is not a lab chapter. It restates the platform outcome, the five principles as a product-control loop, what the book does not claim, and the handoff to the planned fourth book, *Practical SRE Engineering* (Decision 004).

## Cross-chapter coverage audit

| Required platform area | Primary chapters | Later proof |
|---|---|---|
| Platform as product, users, jobs, non-goals | 1 | 2, 10, 13 |
| Capability intake and productization decisions | 2 | 5–7, 12 |
| Tenancy, isolation, noisy neighbor | 3 | 6, 8, 11, 14 |
| Catalog and ownership | 4 | 12–13 |
| Paved road, conformance, supported exit | 5 | 9, 12 |
| Self-service environments | 6 | 11–12, 14 |
| Infrastructure contracts and compatibility | 7 | 8, 12 |
| Shared control plane as product | 8 | 12–14 |
| Guardrails, exceptions, scorecards | 9 | 12–13 |
| Developer-experience measurement | 10 | 11, 13 |
| Quota, showback, platform unit cost | 11 | 12, 14 |
| Fleet onboard, upgrade, deprecate | 12 | 13–14 |
| Support, escalation, safe platform change | 13 | 14 |
| Control-plane recovery with tenant isolation | 14 | Conclusion |

## Companion-lab design constraints

- The lab root will be `books/practical-engineering/labs/platform/northwind/`; it must not mutate DevOps or DevSecOps labs.
- Inherited DevOps and DevSecOps capabilities enter through documented checksum-identified fixtures, never through those working trees at runtime.
- Every evaluator must separate observations from expectations and must fail when required evidence is absent.
- Concept-led artifacts require schema and cross-reference validation, not a fake command that claims to validate judgment itself.
- Failure simulations must be deterministic, local, non-destructive, and clearly labeled as simulations.
- A successful simulation proves the modeled product logic only; it does not claim that a real portal, cluster fleet, identity provider, or billing system was tested.

## Pre-freeze resolutions

1. Shared schemas and first-use ownership are defined in `SCHEMA-INVENTORY.md`.
2. Tool responsibilities, Make targets, and snapshot conventions are defined in `LAB-PLAN.md`.
3. Inherited artifacts enter through minimal stable interface fixtures.
4. Every proposed chapter implementation has a local verification target and an explicit real-system limitation in `LAB-PLAN.md`.
