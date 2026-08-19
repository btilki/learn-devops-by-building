# Practical SRE Engineering — Chapter Map

**Status:** Frozen  
**Freeze date:** 2026-08-16  
**Depends on:** `BOOK-PLAN.md`  
**Drafting gate:** Chapter drafting must conform to this frozen map or use an explicitly versioned plan revision.

## Cumulative state contract

Each chapter inherits the completed reliability state of the previous chapter. Concept- and decision-led chapters change Northwind's reviewed reliability model; implementation-led chapters change enforceable portfolio behavior. Later implementation must consume earlier decisions rather than silently replacing them.

Each chapter must distinguish:

- **mechanism evidence:** proof that a dashboard, alert, pager, runbook, or fail-over controller operated;
- **decision evidence:** proof that an owner evaluated user journeys, error-budget consequences, and operational load;
- **outcome evidence:** proof that a user-visible journey kept its SLO, or that remaining error budget was accounted; and
- **recovery evidence:** **Evidence of portfolio recovery**—not merely that one service returned, one environment was reconstructed, or one control plane was restored.

Failure exercises use three explicit relationships to the book's main storyline:

- **Cumulative reliability failure:** advances availability theater and informal heroics.
- **Connected consequence:** demonstrates harm enabled by an earlier reliability decision.
- **Independent control failure:** proves that the control matters even without the cumulative story.

Inherited identities this map must not collapse:

- Platform job proofs `time-to-first-environment`, `paved-road-completion`, and `catalog-freshness` remain a **job-time budget**.
- Tenant-workload ids `order_success_ratio` and `order_latency` become Storefront user-journey candidates; they must not prove a platform job finished.
- Catalog escalations `storefront-oncall`, `fulfillment-oncall`, and `platform-oncall` are contacts, not an on-call system.
- Platform remaining owner `reliability-program` becomes the SRE program owner.
- Plane last known good `1.0` and contract `tenant-storage` `1.0` remain distinct restore identities. Neither is regional fail-over.
- Platform Chapter 14 limitations `not-regional-loss` and `not-portfolio-rto` are the gap this book closes.

## Chapter 1 — Define What Reliability Must Protect

- **Form:** Concept-led
- **Production question:** Which user journeys must stay reliable, what does Northwind refuse to count as reliability, and who owns each decision?
- **Start:** Delivery, security, and the platform product exist. Storefront has provisional indicators. Fulfillment is a second tenant. Success is still "the graphs are green."
- **Pressure:** Component uptime, kubelet Ready, and portal availability are treated as the reliability program. No one can name the journey that fails a customer.
- **Concepts:** user journey versus component, availability theater, reliability owner, protected outcome, refusal, adjacent platform job-time versus user-visible reliability.
- **Decision/capability:** Write a reliability brief with protected journeys, explicit refusals, owners, and the evidence that would prove the portfolio is reliable.
- **Lab artifacts:** `reliability/brief.yaml`, `reliability/journeys.yaml`, `reliability/refusals.yaml`, `reliability/owners.yaml`.
- **Evidence:** Every journey names a user, a failed outcome, an owner, and a later proof; every refusal names what must not count as success and who still owns that measurement.
- **Durable outputs:** Reliability brief; journey-and-refusal register.
- **Independent control failure:** Cluster and API uptime are counted as reliability success while `accept-and-complete-order` and `dispatch-fulfillment` are unowned.
- **Correction:** Replace uptime-theater evidence with journey-completion evidence and assign `reliability-program` as owner.
- **Next:** Northwind knows the journeys but not which indicators may represent them.

## Chapter 2 — Choose Indicators Users Can Feel

- **Form:** Decision-led
- **Production question:** Which measurements are user-visible SLIs, and which measurements must stay non-indicators for the portfolio?
- **Start:** Journeys are named. Inherited DevOps telemetry and Platform job-time indicators are all proposed as "the SLO."
- **Pressure:** Promoting platform job-time or CPU to a portfolio SLI hides user harm; measuring nothing leaves Fulfillment without a signal.
- **Concepts:** SLI, request versus event versus window, good-event definition, user-journey SLI versus platform-product SLI versus component uptime, Goodhart's law applied to nines.
- **Decision/capability:** Adopt an SLI method and record accept / adjacent / reject decisions with review triggers.
- **Lab artifacts:** `slis/method.yaml`, `slis/candidates.yaml`, `slis/decisions.yaml`.
- **Evidence:** Each accepted SLI traces to a Chapter 1 journey; `time-to-first-environment` is adjacent job-time, not a portfolio SLI; CPU, replica Ready, and portal uptime are rejected.
- **Durable outputs:** SLI selection method; first indicator decisions.
- **Independent control failure:** `time-to-first-environment` is classed `portfolio-slo` because leadership can see it, while `order_success_ratio` stays a tenant-workload non-metric.
- **Correction:** Accept Storefront `order_success_ratio` and a Fulfillment dispatch indicator as user-journey SLIs; keep platform job-time adjacent; reject component uptime.
- **Next:** Indicators are chosen, but there are no portfolio targets, windows, or error budgets.

## Chapter 3 — Set SLOs and Error Budgets Across the Portfolio

- **Form:** Implementation-led
- **Production question:** What SLO target, window, and error budget does each protected journey get, and how is the portfolio cataloged?
- **Start:** SLI decisions exist. Storefront still carries a provisional single-service objective. Fulfillment has none. An SLA sentence is used as if it were an SLO.
- **Pressure:** One copied 99.9% target cannot govern two services; a legal SLA cannot freeze change; a dashboard of nines cannot approve itself.
- **Concepts:** SLO versus SLI versus SLA, compliance window, error budget as remaining unreliability, portfolio catalog, supporting versus critical journeys, `notification-service` as non-critical.
- **Decision/capability:** Publish a portfolio SLO catalog with windows, targets, and remaining error budget for Storefront and Fulfillment. Record that an SLA is out of scope as a legal product.
- **Lab artifacts:** `slos/catalog.yaml`, `slos/windows.yaml`, `slos/budgets.yaml`, SLO evaluator.
- **Evidence:** Every Chapter 1 journey has an SLO; Fulfillment cannot inherit Storefront's target by copy; remaining budget is computed from observations, not emitted by the catalog; notification is not a critical SLO.
- **Durable outputs:** Portfolio SLO catalog; error-budget register.
- **Independent control failure:** The catalog reports a portfolio 99.9% from Storefront alone while `dispatch-fulfillment` has no window or budget.
- **Correction:** Add the Fulfillment SLO; recompute remaining budget per journey; refuse SLA text as a substitute target.
- **Next:** Budgets exist as numbers, but exhausted budget cannot stop change.

## Chapter 4 — Govern Change with Error-Budget Policy

- **Form:** Hybrid
- **Production question:** When remaining error budget is healthy, slowing, or exhausted, what change is authorized, slowed, or frozen?
- **Start:** SLO catalogs exist. Releases, platform fleet upgrades, and exceptions still proceed on calendar and ticket pressure.
- **Pressure:** A dashboard that cannot freeze work is theater. Freezing everything on first burn recreates a change freeze with no policy. Platform already knows how to freeze a fleet for an upgrade; it does not own a freeze because budget is exhausted.
- **Concepts:** error-budget policy, continue / slow / freeze, release versus fleet versus exception, budget owner, expiry of a freeze, distinction from Platform upgrade freeze.
- **Decision/capability:** Write policy that maps remaining budget to change actions, including authority to freeze a Platform fleet upgrade for a reliability reason Platform did not own.
- **Lab artifacts:** `policy/error-budget.yaml`, `policy/actions.yaml`, `policy/exceptions.yaml`, policy evaluator.
- **Evidence:** Exhausted Storefront budget freezes Storefront releases; it may freeze fleet upgrade `storage-1-0-to-2-0` while Fulfillment is still pending; a policy exception has owner, scope, expiry, and remaining journey risk; a Platform upgrade freeze is not recorded as this policy.
- **Durable outputs:** Error-budget policy; freeze-and-exception contract.
- **Cumulative reliability failure:** Storefront budget is exhausted and the fleet upgrade still proceeds because the freeze window was "for upgrades," not for reliability.
- **Correction:** Apply the error-budget freeze, halt the fleet step, and record that this freeze reason is SRE-owned.
- **Next:** Policy exists, but pages still fire on every red graph.

## Chapter 5 — Page on Burn Rate, Not on Every Symptom

- **Form:** Implementation-led
- **Production question:** Which burn rates page a human, which create tickets, and which symptoms must not wake anyone?
- **Start:** Error-budget policy exists. Inherited DevOps Chapter 6 burn alerts are still a single-service provisional rule. CPU, replica restarts, and portal errors all page.
- **Pressure:** Symptom pages train people to ignore journeys. Missing burn pages leave exhausted budget silent until a customer complains.
- **Concepts:** multi-window burn, page versus ticket versus record, symptom versus SLO burn, minimum evidence volume, inherited single-service burn as interface not rewrite.
- **Decision/capability:** Define burn alerts that page on user-journey burn and ticket the rest, without reteaching logs, metrics, or traces.
- **Lab artifacts:** `alerting/burns.yaml`, `alerting/pages.yaml`, `alerting/tickets.yaml`, alerting evaluator.
- **Evidence:** Fast and slow burns of `order_success_ratio` page; CPU and replica Ready do not; platform job-time burn tickets `platform-oncall` and does not page Storefront; a page cannot emit its own "user impact."
- **Durable outputs:** Burn-alert contract; page-versus-ticket map.
- **Independent control failure:** CPU pages `storefront-oncall` while order-success burn is only a dashboard panel.
- **Correction:** Invert the mapping: journey burn pages; component symptoms ticket or record.
- **Next:** Pages have a destination in the catalog, but on-call is still whoever answered Slack.

## Chapter 6 — Design On-Call as a System

- **Form:** Hybrid
- **Production question:** Who is paged, with what load, escalation, handoff, and authority, and how is that different from a catalog contact?
- **Start:** Burn pages exist. Catalog escalations `storefront-oncall`, `fulfillment-oncall`, and `platform-oncall` are treated as the on-call system.
- **Pressure:** A contact without a rotation is a hero roster. A rotation without load limits, handoff, or authority recreates Slack with a nicer name.
- **Concepts:** on-call system versus escalation contact, rotation, page load, handoff, secondary, authority including break-glass that remains DevSecOps-attributable, compensation and training as operational constraints not HR policy.
- **Decision/capability:** Design on-call systems for Storefront, Fulfillment, and the platform product that consume catalog contacts rather than replacing them, and that bind Chapter 5 pages to a living rotation.
- **Lab artifacts:** `oncall/system.yaml`, `oncall/rotations.yaml`, `oncall/handoffs.yaml`, `oncall/authority.yaml`.
- **Evidence:** Every page target is a rotation with a living primary; catalog contacts are referenced, not copied as the system; handoff records exist; unofficial Slack-as-primary fails; platform pages do not land on Storefront's rotation.
- **Durable outputs:** On-call system contract; rotation-and-handoff record.
- **Cumulative reliability failure:** Pages still go to chat history; `storefront-oncall` is a label with no rotation, load, or handoff.
- **Correction:** Bind pages to rotations, require handoff, and record Slack-as-primary as the heroics path to interrupt.
- **Next:** Humans can be paged, but most of their time is unmeasured toil.

## Chapter 7 — Measure and Bound Toil Without Hiding the Work

- **Form:** Decision-led
- **Production question:** What work is toil, how is it measured, and what bound keeps reliability engineering possible?
- **Start:** On-call exists. The rotation spends the week on tickets, manual silences, and copy-paste runbooks. "We will automate later" has no bound.
- **Pressure:** Unbounded toil makes SLO work theater. Pretending tickets are engineering hides the missing automation. Automating the wrong toil creates a new hero path.
- **Concepts:** toil versus engineering, interrupt versus project, measurement of toil fraction, bound, automation that removes toil versus automation that hides it, review trigger when the bound is breached.
- **Decision/capability:** Adopt a toil definition, inventory, and bound. Record which work must shrink before new SLO scope is added.
- **Lab artifacts:** `toil/definition.yaml`, `toil/inventory.yaml`, `toil/bounds.yaml`.
- **Evidence:** Every inventoried item is classified; the bound is numeric and owned; a breach blocks adding a new critical SLO; "we are busy" is not a measurement.
- **Durable outputs:** Toil definition and bound; toil inventory.
- **Independent control failure:** Toil is unmeasured; a new critical SLO for notification is added because on-call "already watches email."
- **Correction:** Classify notification work as non-critical toil or drop it; enforce the bound before scope grows.
- **Next:** Engineering time is protected, but third parties can still burn the budget with no contract.

## Chapter 8 — Put Dependencies Inside the Reliability Contract

- **Form:** Implementation-led
- **Production question:** Which dependencies are inside a journey's SLO, which are degraded or non-critical, and what evidence does each provider owe?
- **Start:** Toil is bounded. Payment, warehouse, and email can fail while Northwind's own graphs stay green, or every provider page is treated as a Storefront page.
- **Pressure:** Absorbing a provider's unbounded failure makes the SLO dishonest. Ignoring a critical provider makes the SLO theater.
- **Concepts:** critical versus non-critical dependency, timeout and retry budget, fallback, provider SLO versus Northwind SLO, `notification-service` / email as non-critical, payment and warehouse as critical.
- **Decision/capability:** Publish dependency contracts that join Chapter 3 journeys to providers, with criticality, timeout, fallback, and the evidence that a provider failure is a Northwind burn or a bounded degradation.
- **Lab artifacts:** `dependencies/catalog.yaml`, `dependencies/criticality.yaml`, `dependencies/contracts.yaml`, dependency evaluator.
- **Evidence:** Payment failure burns `accept-and-complete-order`; warehouse failure burns `dispatch-fulfillment`; email failure does not page Storefront as a critical SLO; a dependency row cannot emit its own "no user impact."
- **Durable outputs:** Dependency reliability catalog; criticality-and-fallback contract.
- **Connected consequence:** Payment timeouts burn Storefront while email is paged as equally critical, exhausting the wrong budget and the wrong rotation.
- **Correction:** Reclassify email as non-critical; attribute payment burn to the Storefront journey; keep warehouse on Fulfillment.
- **Next:** Dependencies are named, but Northwind's own services still retry until the portfolio cascades.

## Chapter 9 — Degrade Deliberately Before Failure Cascades

- **Form:** Implementation-led
- **Production question:** How does Northwind shed load, refuse work, or run in a degraded mode before a local failure becomes every journey's outage?
- **Start:** Dependency contracts exist. `order-worker` retries without a shed; Storefront accepts orders the worker cannot finish; Fulfillment is pulled into Storefront's retry storm.
- **Pressure:** "Try harder" converts a payment slowness into a portfolio outage. Silent drop without a degraded-mode contract hides customer harm.
- **Concepts:** load shedding, overload, degraded mode, retry amplification, backpressure, cascade, distinct from Platform tenant quota and DevOps unit-cost scaling.
- **Decision/capability:** Define degradation modes and shedding rules that protect Chapter 3 journeys, with explicit user-visible behavior and a bound on retries.
- **Lab artifacts:** `degradation/modes.yaml`, `degradation/shedding.yaml`, `degradation/cascade.yaml`, degradation evaluator.
- **Evidence:** A payment slowness sheds or degrades Storefront without paging Fulfillment as the cause; unbounded retries fail the check; degraded mode is named in the SLO remaining-budget accounting, not hidden as success.
- **Durable outputs:** Degradation-and-shedding policy; cascade-failure contract.
- **Cumulative reliability failure:** Unbounded payment retries cascade into Fulfillment and exhaust both budgets while graphs of "accepted orders" stay green.
- **Correction:** Shed, name the degraded mode, stop retry amplification, and account the burn on the Storefront journey.
- **Next:** Cascade is bounded in the model, but a multi-service incident is still commanded as one failed change on one path.

## Chapter 10 — Command Incidents Across Services and Tenants

- **Form:** Implementation-led
- **Production question:** How is an incident that spans Storefront, Fulfillment, and the platform commanded, and what evidence is portfolio evidence rather than one-path recovery?
- **Start:** Degradation exists. Inherited DevOps Chapter 12 can coordinate one failed production change. A payment and dispatch failure still gets one informal commander in Slack.
- **Pressure:** Single-path incident command mis-assigns owner, freeze, and recovery proof. Closing because Storefront orders look green leaves Fulfillment down. Treating a platform-product incident as a tenant-application incident pages the wrong rotation.
- **Concepts:** incident command, portfolio versus one-path, platform-product versus tenant-application (inherited from Platform support), commander versus operator, communication cadence, freeze that joins Chapter 4 policy, inherited incident-role interface consumed not rewritten.
- **Decision/capability:** Define multi-service command, distinct roles, and an executed trace that a Slack-only response fails. Consume DevOps incident roles and Platform escalation kinds; do not reteach them.
- **Lab artifacts:** `incidents/command.yaml`, `incidents/roles.yaml`, `incidents/traces.yaml`, incident evaluator.
- **Evidence:** A spanning incident names commander, affected journeys, on-call systems, and whether Chapter 4 freeze applies; Storefront green cannot close Fulfillment; a platform-product incident routes to the platform rotation; unofficial single-hero command fails.
- **Durable outputs:** Portfolio incident-command model; executed multi-service trace.
- **Connected consequence:** DevOps one-change command is reused; the incident closes on `order_success_ratio` while `dispatch-fulfillment` is still failing and `platform-oncall` was never paged.
- **Correction:** Re-open under portfolio command, page the right rotations, apply freeze if budget requires it, and split tenant-application from platform-product.
- **Next:** Incidents can be commanded, but learning is still a document with no verified follow-through.

## Chapter 11 — Turn Incidents into a Reliability Learning Program

- **Form:** Decision-led
- **Production question:** What learning program turns incidents into owned, verified change, rather than into blameless theater?
- **Start:** Portfolio command exists. Postmortems are optional, action items have no owner, and the same payment retry cascade returns.
- **Pressure:** A template without verification is a blog post. Blame without a system produces silence. Action volume without a bound recreates toil.
- **Concepts:** blameless learning, contributing-factor analysis, action owner, verification evidence, review cadence, learning as a control, distinction from DevSecOps eradication and from a single DevOps incident retrospective.
- **Decision/capability:** Adopt a learning-program contract: which incidents require a record, how actions are owned and verified, and when the program itself is failing.
- **Lab artifacts:** `learning/program.yaml`, `learning/records.yaml`, `learning/actions.yaml`.
- **Evidence:** Every Chapter 10 complete incident has a record or an explicit waiver with expiry; every action has owner, due date, and verification that is not the record approving itself; a repeated Chapter 9 cascade without a verified action fails the program.
- **Durable outputs:** Learning-program contract; action-verification register.
- **Independent control failure:** A polished postmortem exists; actions are "be more careful" with no owner, due date, or verification.
- **Correction:** Replace hortatory actions with owned changes; fail the program until verification exists.
- **Next:** Learning can change the portfolio, but the architecture still assumes one region.

## Chapter 12 — Design for the Loss of a Region

- **Form:** Concept-led
- **Production question:** What happens when a region is lost, what portfolio RTO and RPO are defensible, and which data cannot silently move?
- **Start:** Learning exists. Platform Chapter 14 restored a control plane inside one region and recorded `not-regional-loss` and `not-portfolio-rto`. DevOps Chapter 13 reconstructed one environment.
- **Pressure:** "We have backups" is treated as multi-region. RTO is "as fast as possible." Data gravity, tenant isolation, and payment-provider regionality are ignored.
- **Concepts:** region, fail-over versus restore, portfolio RTO and RPO, data gravity, active-passive versus active-active, tenant isolation during fail-over, distinction from one-environment reconstruction and from plane restore.
- **Decision/capability:** Write a regional-loss architecture: regions, fail-over order, portfolio objectives, data that cannot cross regions silently, and what remains out of scope.
- **Lab artifacts:** `regions/architecture.yaml`, `regions/objectives.yaml`, `regions/constraints.yaml`.
- **Evidence:** Portfolio RTO and RPO are numeric and owned; Storefront and Fulfillment isolation constraints survive fail-over; plane last known good and contract last known good are listed as insufficient; payment and warehouse regionality are constraints, not hopes.
- **Durable outputs:** Regional-loss architecture; portfolio RTO/RPO decision record.
- **Independent control failure:** Architecture claims regional recovery by pointing at DevOps reconstruction and Platform plane restore; RTO is unmeasured.
- **Correction:** Separate fail-over from restore; assign portfolio objectives; record inherited recoveries as insufficient.
- **Next:** The architecture exists on paper, but it has not been exercised as a program.

## Chapter 13 — Run Game Days as a Recurring Program

- **Form:** Implementation-led
- **Production question:** How does Northwind exercise reliability controls on a cadence, including failures that are not one mixed-backup fixture, without taking the portfolio down for real?
- **Start:** Regional architecture exists. The only practiced recovery is Platform's mixed-backup isolation test. There is no cadence, blast-radius contract, or learning join.
- **Pressure:** A single fixture becomes "we do game days." Unbounded chaos becomes an outage. A game day that cannot fail the program is theater.
- **Concepts:** game day versus chaos versus DR test, recurrence, scoped blast radius, fail-safe abort, scenario coverage, join to Chapters 4, 6, 8, 10, 11, and 12.
- **Decision/capability:** Publish a game-day program with cadence, allowed scenarios, abort rules, and evidence that more than one fixture is exercised.
- **Lab artifacts:** `gamedays/program.yaml`, `gamedays/scenarios.yaml`, `gamedays/results.yaml`, game-day evaluator.
- **Evidence:** The program includes at least error-budget freeze, on-call page path, dependency loss, and regional-loss tabletop or simulated fail-over; a single `mixed-backup` result cannot complete the program; an abort is recorded when blast radius would exceed the contract; results feed Chapter 11 actions.
- **Durable outputs:** Game-day program contract; scenario-and-result register.
- **Independent control failure:** Platform Chapter 14's mixed-backup fixture is filed as the annual game day and marked complete.
- **Correction:** Fail completeness; add freeze, page-path, dependency, and regional scenarios; require recurrence.
- **Next:** The program can exercise controls, but an actual regional fail-over has not been proven.

## Chapter 14 — Fail Over a Region Without Taking the Portfolio Down

- **Form:** Implementation-led
- **Production question:** How does Northwind fail over a lost region, keep tenant isolation, meet portfolio RTO and RPO, and prove the portfolio recovered?
- **Start:** Game days exist. A region is lost. The temptation is to reconstruct one environment, restore the plane from newest, or invent the order of operations during the outage.
- **Pressure:** Mixed-tenant fail-over recreates Platform's shared blast radius. Treating DevOps reconstruction as regional recovery misses the other region and the other tenant. Traffic returns before journey SLOs and isolation hold.
- **Concepts:** fail-over execution, region isolation, traffic shift, tenant continue versus freeze (inherited idea, now regional), last known good per region, **Evidence of portfolio recovery**, explicit non-claims.
- **Decision/capability:** Execute a reviewed fail-over from independently verified evidence, keep Storefront and Fulfillment isolated, reject mixed-region or mixed-tenant replay, and prove portfolio recovery against Chapter 12 objectives.
- **Lab artifacts:** `failover/plan.yaml`, `failover/trace.yaml`, `failover/isolation.yaml`, `failover/verification.yaml`.
- **Evidence:** Lost region is isolated; fail-over follows the Chapter 12 order; mixed-tenant replay fails; plane restore and one-environment reconstruction are recorded as insufficient; Storefront and Fulfillment continue or freeze by explicit decision; verification cannot emit `status: recovered` to hide a missed RTO, a missed RPO, or a collapsed isolation boundary.
- **Durable outputs:** Regional fail-over plan; **Evidence of portfolio recovery**.
- **Cumulative reliability failure:** Newest mixed-region state is applied, Fulfillment intent lands in Storefront, and recovery is declared because one environment's reconstruction job succeeded.
- **Correction:** Reject mixed replay, fail over from reviewed regional evidence, verify isolation and journey SLOs, and record inherited restores as not portfolio recovery.
- **Next:** The conclusion assembles journeys, SLOs, error-budget policy, on-call, learning, game days, and regional fail-over into one governed reliability portfolio.

## Chapter 15 — Conclusion — A Governed Reliability Portfolio

The conclusion is not a lab chapter. It restates the reliability outcome, the five principles as a portfolio-control loop, what the book does not claim, and that this fourth book closes the SRE handoff recorded in Platform Chapter 15 and Decision 004.

## Cross-chapter coverage audit

| Required SRE area | Primary chapters | Later proof |
|---|---|---|
| Protected journeys, refusals, reliability owner | 1 | 2–3, 8, 14 |
| User-visible SLI selection; job-time kept adjacent | 2 | 3, 5 |
| Portfolio SLOs, windows, error budgets; SLA ≠ SLO | 3 | 4–5, 8–9, 14 |
| Error-budget policy that can freeze change, including fleet | 4 | 5, 10, 13 |
| Burn-rate paging versus symptom noise | 5 | 6, 10 |
| On-call system versus catalog escalation contact | 6 | 10, 13 |
| Toil definition, measurement, and bound | 7 | 11 |
| Dependency criticality inside the journey contract | 8 | 9–10, 13 |
| Degradation, shedding, cascade control | 9 | 10, 13 |
| Multi-service / multi-tenant incident command | 10 | 11, 14 |
| Learning program with verified actions | 11 | 13–14 |
| Regional-loss architecture; portfolio RTO/RPO | 12 | 13–14 |
| Recurring game days beyond one mixed-backup fixture | 13 | 14 |
| Regional fail-over with Evidence of portfolio recovery | 14 | Conclusion |

### Overlap explicitly refused

| Topic | Stays in | SRE consumes as |
|---|---|---|
| Observability fundamentals, logs/metrics/traces | DevOps 6 | Inherited telemetry interface |
| Provisional single-service SLI and burn | DevOps 6 | Candidate input to Chapters 2 and 5 |
| One failed-change incident coordination | DevOps 12 | Role interface for Chapter 10 |
| Reconstruction of one environment | DevOps 13 | Insufficient for Chapter 12–14 |
| Restored trust after compromise | DevSecOps 15 | Not reliability recovery language |
| Platform product, jobs, tenancy, paved road | Platform 1–7 | Inherited product context |
| Platform job-time budget and non-metrics | Platform 10 | Adjacent evidence, never portfolio SLO |
| Fleet upgrade freeze | Platform 12 | Distinct from Chapter 4 error-budget freeze |
| Support tiers and catalog escalation contacts | Platform 13 | Inputs to Chapter 6 |
| Control-plane restore with tenant isolation | Platform 14 | Insufficient for regional loss; isolation invariant to preserve |

## Companion-lab design constraints

- The lab root will be `books/practical-engineering/labs/sre/northwind/`; it must not mutate DevOps, DevSecOps, or Platform labs.
- Inherited capabilities enter through documented checksum-identified fixtures:

  ```text
  inherited/devops-v1.1/
  inherited/devsecops-v1.0/
  inherited/platform-v1.0/
  ```

  No test may read those working trees at runtime.
- Every evaluator must separate observations from expectations and must fail when required evidence is absent.
- Concept-led artifacts require schema and cross-reference validation, not a fake command that claims to validate judgment itself.
- Failure simulations must be deterministic, local, non-destructive, and clearly labeled as simulations.
- A successful simulation proves the modeled reliability logic only; it does not claim that a real telemetry backend, paging vendor, multi-region fleet, or incident-management product was tested.
- Verification must not treat platform job-time, one-environment reconstruction, or plane restore as **Evidence of portfolio recovery**.

## Pre-freeze resolutions

1. Shared schemas and first-use ownership are defined in `SCHEMA-INVENTORY.md`.
2. Tool responsibilities, Make targets, and snapshot conventions are defined in `LAB-PLAN.md`.
3. Inherited artifacts enter through minimal stable interface fixtures from all three predecessors (Decision 004).
4. Every proposed chapter implementation has a local verification target and an explicit real-system limitation in `LAB-PLAN.md`.
5. Chapter 13 game days must exercise Chapters 4–10 mechanisms plus regional-loss tabletop or simulated fail-over, not only a miniature of Chapter 14.
