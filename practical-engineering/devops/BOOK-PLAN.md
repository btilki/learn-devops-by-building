# Practical DevOps Engineering — Book Plan

## Promise

Build and operate a production-grade delivery path for Northwind Commerce, from source change and trusted artifact to controlled deployment and verified recovery.

## Teaching contract

- Audience: intermediate-to-advanced DevOps, platform, cloud, infrastructure, and **SRE (Site Reliability Engineering)** practitioners.
- Do not enforce a theory-to-practice percentage. Include as much theory as the reader needs to understand the mechanism, make a safe production decision, diagnose failure, and evaluate trade-offs—then use it in the implementation. Do not add theory that has no effect on the chapter's engineering decisions.
- Keep the book practical through meaningful reader actions, evidence, failure diagnosis, and recovery, not through a word-count ratio.
- Use one cumulative implementation under `books/practical-engineering/labs/devops/northwind/`.
- The chapter is the practical guide; repository files make it runnable and verifiable.
- Guided implementation counts as practice. A practical book must tell the reader what to change, why the change is necessary, how to apply it safely, and what evidence proves it worked. Do not confuse guidance with passive inspection, and do not withhold essential steps merely to make an exercise feel harder.
- On first use in each reader-facing document, write an abbreviation followed by its full form in parentheses and bold the complete expression, for example **CI (Continuous Integration)**. Use the abbreviation alone afterward. Apply this to technical abbreviations and percentile or measurement shorthand in prose and tables; do not alter literal code, commands, filenames, paths, configuration keys, image names, or version identifiers.
- Practice may include guided edits, commands, evidence interpretation, failure diagnosis, recovery, and independent extension. The reader must make or reason through meaningful system changes; they do not need to discover every implementation without help.
- At the beginning of the chapter's main conceptual section, use one blockquote box with an italic label in the form `> *Theory — Model name*`, followed by one short sentence stating the production decision the model enables. Do not add theory-completion messages or additional theory boxes later in the chapter; short just-in-time explanations may remain beside the practice that needs them.
- Mark every meaningful guided reader action with a blockquote box in the form `> **Practice — Action name**`, followed by one short sentence stating what the reader will change or prove. Use `> **Independent Practice — Action name**` for the final unguided challenge. Do not add practice-completion messages: the next heading, theory prose, or practice box closes the previous activity naturally. Do not label passive reading, trivial navigation, or every individual command as practice.
- Every chapter answers one production question and produces a falsifiable system change.
- Near `What You Learned`, name one or two durable outputs the reader should retain from the chapter. Prefer artifacts already produced by the guided implementation—such as a reviewed contract, conformance report, decision record, or mini-runbook—rather than adding ceremonial documents or another exercise.
- Revisit blast-radius control, explicit contracts, trustworthy evidence, reconciliation, and recovery.
- Every dedicated failure section must name the relevant recurring principles explicitly with a `Primary principles:` line after severity, potential blast radius, and bounding controls. Select only the principles the scenario actually exercises.
- Every final chapter audit must explicitly confirm `Primary principles: yes/no`; a dedicated failure section cannot pass review when the answer is no.

## Northwind Commerce

- `storefront-api`: public catalog, order submission, and order status.
- `order-worker`: idempotent asynchronous inventory and payment processing.
- `notification-service`: non-critical confirmation delivery.
- PostgreSQL, an at-least-once broker, and controllable payment/email simulators.

Critical outcome: a valid order is durably accepted and reaches a correct terminal state without duplicate charge, invalid inventory state, or permanent disappearance.

## Index

0. How to Use This Book
1. Build Fast Feedback You Can Trust
2. Build Once and Promote a Verifiable Artifact
3. Reconcile Infrastructure Through Reviewed Changes
4. Establish a Production Kubernetes Runtime
5. Replace Static Secrets with Workload Identity
6. Make Production Behavior Explainable
7. Release Progressively and Abort Safely
8. Change Data Without Breaking Compatibility
9. Operate Asynchronous Work Safely
10. Reconcile Environments with GitOps
11. Control Delivery Cost and Capacity
12. Recover a Failed Production Change
13. Restore Production from Durable Evidence
14. Conclusion — An Evidence-Driven Delivery Path

## Back matter

- Glossary and Abbreviations
- References
- Release Checklist
- Release Manifest

## Chapter 1 state map

| Field | State |
|---|---|
| Start | `storefront-api` health behavior exists; expensive work precedes cheap checks; feedback **p95 (95th percentile)** is 31 minutes; workflow authority is too broad. |
| Pressure | Engineers receive cheap failures late and rerun noisy pipelines. |
| Implementation | Test boundaries, fail-fast order, Docker-context gate, feedback budget, minimal workflow permissions, and lightweight conformance to a reviewed workflow interface. |
| Baseline | Checkpoint reports budget, ordering, context, and authority failures. |
| Complete | Checkpoint verifies behavior, dependency ordering, critical-path budget, context rules, workflow permissions, and that the service workflow has not drifted from required template evidence and authority boundaries. |
| Failure | Runner contention raises modeled queue time from 40 to 400 seconds and pushes otherwise unchanged feedback beyond budget. |
| Recovery | Queue capacity is restored without weakening ordering, context, test, or authority controls; the complete checkpoint returns green. |
| Next | Northwind must prove the promoted artifact is the artifact **CI (Continuous Integration)** tested. |

## Chapter 2 state map

| Field | State |
|---|---|
| Start | Chapter 1 feedback controls are green; the release workflow rebuilds during promotion, uses `latest`, and carries no verifiable **SBOM (Software Bill of Materials)** or provenance. |
| Pressure | Staging and production can receive different bytes even when both runs start from the same revision. |
| Production model | Artifact identity is a digest; provenance binds that digest to source and builder; verification compares signed evidence with explicit expectations. |
| Guided implementation | Build once, create an **SPDX (Software Package Data Exchange)** SBOM, generate digest-bound provenance, define trusted source/builder/build-type expectations, attest in hosted CI, and promote by digest without rebuilding. |
| Baseline | The checkpoint reads the actual release workflow and reports mutable identity, two builds, missing evidence, and no verification expectations. |
| Complete | The local checkpoint verifies digest, SBOM, provenance subject, and expectations; the hosted workflow builds once and creates an **OIDC (OpenID Connect)**-backed attestation. |
| Failure | The artifact is modified after evidence generation while its tag-like name remains unchanged. |
| Blast radius | One release candidate; promotion is blocked before an environment consumes it. |
| Recovery | Rebuild from the reviewed revision, regenerate evidence, verify the new digest, and promote the immutable reference. |
| Next | Northwind can trust an artifact but cannot yet reproduce and reconcile the infrastructure that will run it. |

## Chapter 3 state map

| Field | State |
|---|---|
| Start | A production service exists outside declared state; state is local and unlocked; a pull-request workflow can apply directly; certificate provisioning has no renewal or expiry contract. |
| Pressure | Engineers cannot tell whether a reviewed change, stale plan, or console action produced the current infrastructure. |
| Production model | Configuration expresses intent, state binds resource addresses to remote objects, refresh observes reality, and reconciliation proposes the transition. |
| Guided implementation | Import the existing service, define desired state with Chapter 2's artifact digest, require encrypted remote state and locking, declare certificate ownership and automated renewal, verify endpoint replacement and fail-closed expiry, save a plan, separate plan/apply authority, and reconcile drift. |
| Baseline | The checkpoint reports missing desired state, binding, locking, protected apply, immutable artifact identity, and certificate lifecycle controls. |
| Complete | The checkpoint verifies desired/actual agreement, one resource binding, locked remote-state policy, read-only planning, protected apply, digest-pinned deployment, and certificate provisioning/renewal/expiry behavior. |
| Failure | A console action scales the service from two replicas to five outside the reviewed path. |
| Blast radius | One production service; the plan shows one non-destructive field correction before apply. |
| Recovery | Classify the drift, create a fresh saved plan, apply it under lock, and verify configuration, state, and actual infrastructure agree. |
| Next | Northwind has reconciled infrastructure but still needs a production Kubernetes runtime contract for its workload. |

## Chapter 4 state map

| Field | State |
|---|---|
| Start | The verified image is deployed with no resource requests, distinct health semantics, configuration contract, disruption protection, network boundary, or workload-specific service account. |
| Pressure | Kubernetes can schedule and restart the Pod, but Northwind cannot tell whether it is safe to receive traffic or survive routine node maintenance. |
| Production model | Scheduling uses requests; limits bound consumption; startup, readiness, and liveness answer different questions; flags, environment, and mounted files have distinct change behavior; disruption and network controls constrain separate failure paths. |
| Guided implementation | Pin the Chapter 2 digest, add measured requests and limits, separate probes, choose explicit configuration interfaces, validate startup and reload candidates, retain last known good configuration, restrict the container, spread replicas, use a dedicated service account, define rollout and termination behavior, add a PodDisruptionBudget and NetworkPolicy, and verify selectors as contracts. |
| Baseline | The checkpoint reports missing runtime, health, configuration, identity, disruption, and traffic boundaries. |
| Complete | Checks verify immutable artifact and configuration identity, schedulability, traffic readiness, bounded restart behavior, schema and reload safety, writable paths, restricted execution, topology spread, graceful termination, voluntary-disruption tolerance, and default-deny ingress. |
| Failure | A dependency-sensitive liveness probe restarts healthy processes during a temporary dependency outage. |
| Blast radius | One rollout of `storefront-api`; readiness removes affected Pods from service before restart amplification spreads. |
| Recovery | Move dependency health to readiness, keep liveness process-local, add startup protection, and verify traffic withdrawal without restart looping. |
| Next | Northwind's workload has a runtime identity but still needs scoped, short-lived access to production dependencies. |

## Chapter 5 state map

| Field | State |
|---|---|
| Start | `order-worker` inherits a broad default service account and receives long-lived cloud, broker, database, and payment credentials through static environment secrets. |
| Pressure | A leaked Pod credential has unclear subject, broad authority, manual rotation, and no reliable revocation boundary. |
| Production model | Workload identity binds runtime subject, audience, issuer, expiry, and policy; federation exchanges that proof for short-lived dependency-specific access without distributing a reusable secret. |
| Guided implementation | Bind a dedicated service account, project a bounded token, federate supported dependencies, broker unavoidable provider secrets, scope policy, define rotation and revocation, protect break-glass access, and record identity evidence. |
| Baseline | The checkpoint reports default identity, reusable credentials, wildcard scope, missing audience/expiry, manual rotation, unsafe revocation, shared break-glass access, and absent audit evidence. |
| Complete | Each workload receives short-lived audience-bound access for its dependency; unsupported federation uses a referenced and rotatable provider secret rather than embedding it in the workload. |
| Failure | A stolen `order-worker` token is replayed against a different audience after its trust binding is revoked. |
| Blast radius | The compromised workload identity and its explicitly scoped dependencies; audience and policy prevent lateral use. |
| Recovery | Revoke the binding, quarantine the workload, rotate any brokered provider secret exposed through it, issue fresh identity to a verified workload, and confirm rejected replay plus restored legitimate access. |
| Next | Northwind has attributable dependency access and must make production behavior explainable without leaking credential material into telemetry. |

## Chapter 6 state map

| Field | State |
|---|---|
| Start | Runtime health is enforceable, but requests, dependency calls, and order outcomes cannot be correlated; alerts describe component symptoms rather than user impact. |
| Pressure | Operators see elevated errors but cannot determine which release, route, dependency, or order path is responsible. |
| Production model | Metrics expose bounded aggregate behavior, logs preserve event context, traces connect causality, and service-level indicators measure user-visible outcomes. |
| Guided implementation | Define provisional service-level indicators and an objective/window, propagate correlation context, emit structured logs and bounded-cardinality metrics, model traces across the request path, record deployment identity, and evaluate alerts against an error-budget burn policy. |
| Baseline | The checkpoint reports missing correlation, unbounded labels, absent deployment identity, no user-visible indicator, and symptom-only alerting. |
| Complete | One synthetic order can be followed across logs, metrics, and trace spans; indicators and burn alerts are computed from production-shaped evidence. |
| Failure | A payment dependency slows and fails only for one route while process health and aggregate processor utilization remain normal. |
| Blast radius | Order submission; catalog reads remain healthy and alerts identify the affected user journey. |
| Recovery | Isolate the dependency and release dimensions, repair the request path, verify latency/error indicators recover, and retain evidence that the burn has stopped. |
| Next | Northwind can explain production behavior and can use that evidence to control a progressive release. |

## Chapter 7 state map

| Field | State |
|---|---|
| Start | Northwind deploys all replicas at once; Chapter 6 signals exist but do not control rollout progression or rollback. |
| Pressure | A release can remain technically Ready while burning the order-success budget, and operators must correlate and reverse it manually. |
| Production model | Progressive delivery is a feedback controller: expose a bounded cohort, evaluate trustworthy outcome evidence, then advance, pause, or abort. |
| Guided implementation | Define reviewed digest handoffs, canary steps, immutable stable/candidate identities, minimum evidence volume, success and latency gates, pause/abort behavior, rollback verification, and protected promotion authority. |
| Baseline | The checkpoint reports all-at-once exposure, no analysis gate, no minimum sample, no automatic abort, and mutable rollback identity. |
| Complete | A rollout advances only when both user-visible indicators and evidence-volume requirements pass; failure returns traffic to the prior digest and verifies recovery. |
| Failure | The candidate remains ready but payment errors consume the order error budget in its initial traffic cohort. |
| Blast radius | The configured canary cohort; stable replicas continue serving the remaining traffic. |
| Recovery | Abort progression, restore stable traffic, verify order indicators recover, and retain candidate-specific evidence for diagnosis. |
| Next | Northwind can control stateless release risk but must change persistent data without breaking old and new versions. |

## Chapter 8 state map

| Field | State |
|---|---|
| Start | A single release replaces `orders.total_cents`, requires the new field immediately, and drops the legacy field while stable replicas may still run. |
| Pressure | Mixed application versions, long-running backfill, and rollback require incompatible schema states at the same time. |
| Production model | Expand adds compatible structure, migrate moves behavior and data with retry-safe evidence, and contract removes legacy structure only after dependencies retire. |
| Guided implementation | Add a nullable replacement, preserve old writers, dual-write transactionally, read with fallback, define a batched idempotent checkpointed backfill, validate coverage and values, gate enforcement, define progressive legacy cutover and abort, require exit evidence, and defer destructive cleanup. |
| Baseline | The checkpoint reports direct replacement, incompatible readers/writers, unsafe backfill, premature enforcement, same-release destruction, and lost rollback. |
| Complete | Stable and candidate coexist, migration can pause and resume, validation gates enforcement, application rollback retains compatible data, and legacy retirement waits for zero legacy writes plus a closed rollback window. |
| Failure | An old stable replica writes only the legacy field while the candidate and backfill are active. |
| Blast radius | Orders served by mixed-version replicas; the additive schema and fallback keep those rows readable. |
| Recovery | Return traffic to stable, retain the expanded schema and progress cursor, verify order correctness, and resume or repair forward without destructive reversal. |
| Next | Northwind must operate at-least-once asynchronous order work without duplicating financial or inventory effects. |

## Chapter 9 state map

| Field | State |
|---|---|
| Start | `order-worker` treats each delivery as new work, acknowledges before durable outcome, publishes after commit, and retries every error without a limit. |
| Pressure | Payment can succeed while acknowledgement or local commit fails, so redelivery can repeat financial and inventory effects. |
| Production model | Delivery attempts converge on one business effect through stable identity, idempotent external calls, durable transaction boundaries, and acknowledgement after recoverable outcome. |
| Guided implementation | Preserve operation identity, serialize per order, add transactional inbox and outbox records, reuse the identity at payment, define acknowledgement and lease rules, classify and bound retries, quarantine poison messages, protect replay, measure useful progress, shadow a legacy worker without external effects, and transfer ownership once under reviewed evidence. |
| Baseline | The checkpoint reports unstable identity, no deduplication or outbox, unsafe acknowledgement, unbounded retry, no quarantine, and symptom-only evidence. |
| Complete | Repeated delivery converges on one payment, inventory transition, terminal order state, and recoverable event publication; dual-run comparison cannot create effects, and reconciled outcomes plus a drained legacy backlog gate retirement. |
| Failure | Payment and order state succeed, but acknowledgement is lost and the broker redelivers the same operation. |
| Blast radius | One order per unsafe duplicate; stable identity, per-order serialization, and bounded retries prevent amplification. |
| Recovery | Reconcile provider payment, inventory, inbox, order, and outbox evidence; acknowledge the duplicate only after the durable outcome is confirmed and backlog age recovers. |
| Next | Northwind must continuously reconcile reviewed delivery intent into environments without broadening production authority. |

## Chapter 10 state map

| Field | State |
|---|---|
| Start | Release automation writes directly to production with mutable identity; the controller has broad authority, plaintext secrets enter desired state, and drift, pruning, and unhealthy retries are uncontrolled. |
| Pressure | Northwind needs continuous convergence without allowing release automation or the controller to propose, approve, apply, and conceal the same change. |
| Production model | Declarative versioned intent is pulled by a bounded controller that observes actual state, applies approved transitions, reports evidence separately, and cannot rewrite its source. |
| Guided implementation | Protect production intent, require digests and secret references, separate proposal and merge, close candidate/stable handoffs, promote independently identified application configuration through environments, freeze failed configuration while retaining last known good, use workload identity, scope the controller, classify self-heal and prune behavior, order dependencies, bound health waits, and expire exceptions. |
| Baseline | The checkpoint reports push deployment, self-approval, broad controller authority, mutable artifacts, plaintext secrets, uncontrolled reconciliation, permanent exceptions, and unverified recovery. |
| Complete | A reviewed digest and independently versioned application configuration are pulled and reconciled by bounded authority; configuration promotion uses validation plus runtime evidence, while drift and unhealthy state produce classified actions with retained evidence. |
| Failure | A validly reviewed candidate degrades runtime and order outcomes while the controller attempts convergence. |
| Blast radius | The progressive candidate cohort and Northwind namespace; stable traffic and unrelated environments remain outside the controller's authority. |
| Recovery | Pause reconciliation, preserve failed evidence, submit a reviewed revert, reconcile it, and verify stable identity, health, user outcomes, and resource cleanup. |
| Next | Northwind must measure and control the capacity and cost consequences of its production delivery system. |

## Chapter 11 state map

| Field | State |
|---|---|
| Start | Spend lacks ownership and useful-unit context; processor utilization alone drives scaling; budgets alert after spend; rightsizing has no reliability or rollback gate. |
| Pressure | A lower bill can hide delayed orders, shifted shared cost, dependency overload, and insufficient capacity to recover from backlog. |
| Production model | Allocate spend, normalize it by a quality-gated useful outcome with explicit accounting assumptions, and constrain optimization with latency, backlog, dependency, and recovery evidence. |
| Guided implementation | Define ownership and shared allocation, make currency, window, cost basis, components, denominator, discounts, credits, and delivery-cost treatment explicit, calculate cost per correct terminal order, join reliability evidence, build a tested autoscaling envelope, forecast spend and anomalies, baseline commitments, and make optimization progressive and reversible. |
| Baseline | The checkpoint reports unallocated spend, no useful unit, missing reliability joins, unsafe scaling floors and ceilings, reactive budgets, and irreversible optimization. |
| Complete | Cost and capacity decisions use a reproducible reviewed unit model and are owned, normalized, forecast, reliability-gated, dependency-aware, and recoverable through reviewed desired state. |
| Failure | Halving worker capacity lowers spend and apparent unit cost while completion latency and oldest-message age exceed policy and backlog cannot drain. |
| Blast radius | Orders processed during the optimization window; progressive change and backlog gates limit continued exposure. |
| Recovery | Reconcile the last verified envelope, ramp below dependency limits, verify backlog age and completion recover, reconcile business outcomes, and retain recovery cost evidence. |
| Next | Northwind must coordinate response and verified recovery when a production change still escapes these controls. |

## Chapter 12 state map

| Field | State |
|---|---|
| Start | Evidence can identify an incompatible queue release, but one responder informally declares, operates, communicates, and chooses rollback without a shared recovery contract. |
| Pressure | The candidate producer emits `v2` while the stable consumer understands only `v1`; acceptance remains healthy while decode errors, message age, and pending work increase. |
| Production model | Incident response is a coordinated control loop: declare from impact, establish authority, test hypotheses, communicate, mitigate, and verify sustained recovery. |
| Guided implementation | Define severity and distinct roles, freeze unrelated change, preserve a shared hypothesis record, bound emergency access, choose a verified producer rollback plus reviewed consumer roll-forward, communicate on a cadence, and require terminal business outcomes. |
| Baseline | The checkpoint diagnoses the mismatch but reports missing declaration, authority, communication, mitigation, learning, and recovery controls. |
| Complete | Policy and an executed incident trace prove declaration, distinct roles, evidence-based mixed mitigation, regular updates, preserved queue state, and sustained recovery. |
| Failure | A reviewed producer emits an unsupported message schema, leaving accepted orders unable to reach a terminal state. |
| Blast radius | Orders published as `v2` during candidate exposure; progressive rollout, durable queue state, and idempotent processing bound further harm. |
| Recovery | Reconcile the verified stable producer, roll forward a reviewed dual-schema consumer, drain without purge or duplicate charge, and verify consecutive healthy samples plus desired/actual agreement. |
| Next | Northwind must restore service, data, identity, and reconciliation after durable state or control-plane loss. |

## Chapter 13 state map

| Field | State |
|---|---|
| Start | Backup jobs report success, but recovery objectives are aspirational, production identity controls recovery evidence, restore order is undefined, and traffic has no business-validation gate. |
| Pressure | The database and cluster control plane are lost; the newest backup is corrupted, an older base plus continuous **WAL (Write-Ahead Log)** reaches minute −5, and five accepted orders exist beyond that database point. |
| Production model | Recovery reconstructs from independently verified durable evidence, restores dependencies in isolation, reconciles business state, and releases traffic only after measured **RPO (Recovery Point Objective)** and **RTO (Recovery Time Objective)** pass. |
| Guided implementation | Bound objectives, isolate and protect evidence, verify manifests, select a valid base and WAL chain, restore identity/infrastructure/data/queue/workloads/controller in order, and reconcile orders, payments, inventory, duplication, and desired state. |
| Baseline | The checkpoint finds usable evidence but reports unsafe authority, unmeasured objectives, undefined ordering, missing reconciliation requirements, and no traffic gate. |
| Complete | The executed trace rejects corruption, measures a five-minute RPO and 52-minute RTO, reconstructs dependencies, reconciles 1,000 accepted orders, and then releases traffic. |
| Failure | The newest scheduled backup reports complete but fails manifest integrity after production and control-plane loss. |
| Blast radius | All Northwind order processing and state after the selected recovery point; isolated evidence and blocked traffic prevent destructive amplification. |
| Recovery | Select the older verified base, replay continuous WAL, reconcile five newer queue orders with provider and inventory evidence, restore reviewed intent, revoke emergency access, and verify objectives. |
| Next | The DevOps delivery arc closes with tested reconstruction of this Northwind environment; portfolio restore objectives, regional-loss design, and recurring recovery game days remain in the SRE book. |
