# Investigate and Contain a Production Compromise

Chapter 13 connected four observations into an actionable alert. An alert is not an incident history, proof of scope, or permission to destroy the suspected systems. Northwind must stop ongoing harm while preserving enough trustworthy evidence to learn what happened.

## 1. An alert exists, but the incident remains open

The compromised maintainer session is still active, the release path may still accept attacker-controlled work, the admitted artifact remains associated with `order-worker`, and orders are in flight. Immediate deletion could erase volatile evidence and business state. Investigation without containment would leave authority open.

Work from the lab working tree using the Chapter 0 procedure. From the DevSecOps lab root, run:

```bash
make chapter-12-attack chapter-13-attack chapter-14-open chapter-14-baseline
```

```text
chapter 14 baseline: correlated alert exists, but attacker authority and incident scope remain open
```

The baseline needs `runtime/events.jsonl` from Chapter 12, `build/chapter-13-alert.json` from Chapter 13, incident `INC-2026-0815-01` in `investigating`, and `compromised-session` still `active`. After Chapter 15 the committed case is `closed` and that session is revoked; `chapter-14-open` restores the investigation start state.

## 2. The production model: preserve, reason, then constrain

> *Theory — Incident hypotheses, evidence custody, scope, and staged containment*
>
> This model lets Northwind act quickly without turning assumptions into facts or erasing the evidence required for recovery.

An incident hypothesis is a testable explanation of observed harm. Facts are directly supported observations. Inferences connect facts but remain revisable. Unknowns define the investigation’s current limits. Keeping those categories separate prevents urgency from creating false certainty.

| Element | Required question | Failure mode |
|---|---|---|
| Hypothesis | What explanation is being tested? | Investigation becomes an unbounded search |
| Timeline | In what attributable order did events occur? | Correlation is mistaken for causation |
| Scope | Which identities, artifacts, workloads, data, and business effects may be affected? | Containment is too narrow or needlessly broad |
| Provenance | Where did each evidence item originate? | Claims cannot be reproduced |
| Integrity | Has evidence changed since collection? | Altered material supports false conclusions |
| Volatility | Which evidence disappears first? | Destructive action erases the best lead |
| Containment | Which authority must close now? | Investigation leaves active attacker capability |
| Continuity | Which business state must be preserved? | Security action creates additional customer harm |

Containment is not eradication. It closes identified access and execution paths while keeping recovery choices open. Attacker access is current authority; persistence is a mechanism that may restore authority later. Chapter 14 closes known access. Chapter 15 searches for and removes persistence before declaring trust restored. Current **NIST (National Institute of Standards and Technology)** incident guidance treats detection, response, and recovery as part of cybersecurity risk management rather than a closed four-phase procedure. Northwind still separates containment from eradication because they are different trust decisions. [NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final).

Communication follows evidence and impact. Internal responders and service owners need early operational facts. Legal, privacy, payment, or customer-notification escalation follows the organization’s defined thresholds; responders should preserve relevant evidence without inventing legal conclusions.

## 3. Build the investigation record and staged containment plan

> **Practice — Separate fact, inference, and unknown**
>
> Record one testable incident hypothesis without presenting suspected persistence or business harm as established fact.

Open `response/case/incident.yaml`. Case `INC-2026-0815-01` initially states the correlated observations as facts, builder control and payment divergence as inference or unknown, and assigns an owner. The checkpoint then collects a scoped order/payment reconciliation record. That evidence resolves the sampled payment-divergence unknown into a fact while leaving broader persistence unknown.

> **Practice — Preserve attributable evidence before mutation**
>
> Hash each collected artifact, record its provenance and custodian, and order the timeline by event time.

Run `make chapter-14-checkpoint`. It copies the Chapter 13 alert, Chapter 12 runtime events, identity register, deployment evidence, and payment reconciliation into `response/evidence/`, then creates `response/evidence-manifest.yaml` over those preserved snapshots. It also writes `response/timeline.jsonl`. Later response steps recalculate the snapshot hashes before trusting the evidence or mutating operational state.

> **Practice — Stage containment across every identified authority**
>
> Preserve evidence first; then revoke the session, freeze release, retain queue and database state, and isolate the workload.

Open `response/containment-plan.yaml`. Its explicit order prevents mutation before evidence preservation and retains in-flight business state before workload isolation. `bounded-intake` preserves defensible service without allowing the compromised worker or release path to resume normal authority.

## 4. Test the design under failure

### Cumulative attack — Retained authority and unverified evidence

> **Practice — Reject an investigation claim built on changed evidence**
>
> Compare the collected digest with the evidence manifest before using the artifact to justify scope or recovery.

**Severity:** critical; attacker authority remains active while evidence quality determines every later decision.  
**Plausible harm:** continued malicious releases, lost forensic scope, fraudulent effects, or destructive over-containment.  
**Potential blast radius:** maintainer identity, build and release authority, production workload, in-flight orders, payment effects, and incident evidence.  
**Bounded by:** preserved evidence, explicit uncertainty, staged authority closure, workload isolation, and retained business state.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence, reconciliation, and recovery.

#### Security questions

- **Asset and harm:** Release authority, payment authority, order outcomes, and trustworthy incident evidence are at risk.
- **Trust and authority:** The session, release path, artifact, and workload are treated as affected until evidence narrows scope.
- **Detection after prevention fails:** The Chapter 13 alert initiates investigation; timeline and custody records support response decisions.
- **Evidence of restored trust:** Not yet applicable. This chapter proves containment, not eradication or restored production trust.

#### Diagnosis

Run `make chapter-14-attack`. The controlled failure copies one preserved item, mutates that working copy, and verifies it against the digest recorded at collection. The resulting `digest-mismatch` rejects the investigation claim while leaving the preserved snapshot intact. A missing item would instead produce a distinct `missing` finding.

#### Containment

Run `make chapter-14-contain`. The evaluator verifies custody before revoking `compromised-session` in the identity register, freezing the production deployment enforcement point, and isolating the `order-worker` runtime contract. It re-reads those controls, calls Chapter 4 authorization to prove the revoked session is denied, and proves a legitimate maintainer remains allowed for bounded source intake.

#### Recovery

Run `make chapter-14-recover`. This re-verifies the preserved snapshots and operational identity, release, runtime, and authorization state rather than trusting the containment record alone. The output deliberately records `trust_restored: false`: containment recovery is sufficient to enter eradication, not to resume normal production.

## 5. Production reality

**Best Practice:** preserve volatile and decision-relevant evidence before mutation, label facts and inference separately, and choose the narrowest containment that closes attacker authority without hiding material business risk.

**Production Practice:** use synchronized clocks, immutable or independently protected evidence storage, documented custody, predefined incident roles, identity and release kill paths, workload isolation, safe queue handling, legal escalation criteria, and rehearsed communications. Record why service was stopped, degraded, or retained.

## 6. What changed

| Before | After |
|---|---|
| A correlated alert implied an incident. | **A testable hypothesis separates facts, inference, and unknowns.** |
| Evidence existed in mutable operational paths. | **A hashed manifest preserves provenance and detects change.** |
| Scope was an intuition. | **Identity, artifact, workload, data, and business dimensions are explicit.** |
| Fast response meant deleting systems. | **Preservation precedes staged authority closure.** |
| Availability and containment competed implicitly. | **Bounded service and preserved state make the trade-off reviewable.** |
| Containment sounded like recovery. | **The verification record keeps restored trust explicitly open.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Investigation timeline and evidence manifest | `response/timeline.jsonl`, `response/evidence-manifest.yaml` | They preserve event order, provenance, custody, and integrity checks. |
| Containment decision | `response/containment-plan.yaml`, generated `build/chapter-14-containment.json` | It preserves action order, authority closure, continuity choices, ownership, and escalation boundaries. |

## What You Learned

Incident response is disciplined uncertainty under time pressure. Evidence must remain attributable and unchanged; claims must distinguish observation from inference; and containment must close known authority while preserving business state and later recovery options.

### Prove It

> **Independent Practice — Contain suspected payment-provider misuse**
>
> Design an investigation and containment record for unexpected provider charges while legitimate payment requests remain in flight.

Specify facts, inference, unknowns, volatile evidence, integrity checks, identity and credential containment, payment continuity, reconciliation boundaries, communications, and the evidence required before eradication begins.

## Next

Northwind has stopped known attacker actions without declaring the environment trustworthy. Chapter 15 removes persistence, rebuilds from trusted roots, rotates affected authority, and reconciles business state before normal operation resumes.
