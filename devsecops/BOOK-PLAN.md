# Practical DevSecOps Engineering — Book Plan

**Planning status:** Frozen  
**Draft date:** 2026-08-15  
**Freeze date:** 2026-08-15  
**Drafting gate:** Chapter drafting must conform to this frozen plan or use an explicitly versioned plan revision.

## Promise

Protect Northwind Commerce's production delivery and order-processing path by making security risk, trust, authority, policy, evidence, detection, and compromise recovery explicit and operationally enforceable.

The reader will learn to decide what must be protected, model how it can be abused, select proportionate controls, enforce those controls at defensible boundaries, investigate violations, and restore trustworthy operation after compromise.

## Audience

This book is for intermediate-to-advanced DevOps, cloud, infrastructure, platform, security, and **SRE (Site Reliability Engineering)** practitioners. Readers should already understand Linux, Git, containers, **CI/CD (Continuous Integration and Continuous Delivery)**, cloud and Kubernetes fundamentals, infrastructure as code, networking, workload identity, observability, and incident response basics.

The book does not teach security tools or foundational computing from first principles. It teaches the mental models and production decisions required to use security mechanisms responsibly.

## Relationship to *Practical DevOps Engineering*

The DevOps book established a trustworthy production delivery path for Northwind: fast feedback, verifiable artifacts, reconciled infrastructure, bounded runtime behavior, workload identity, observable outcomes, progressive delivery, compatible data change, safe asynchronous processing, GitOps, cost and capacity controls, incident coordination, and reconstruction from durable evidence.

This book consumes those capabilities as prerequisites. It may briefly restate an inherited contract when a security decision depends on it, but it must not reteach the DevOps chapter or reproduce its implementation as new work.

The DevOps v1.1 manuscript and companion-lab snapshots remain frozen and unchanged. The DevSecOps book uses a separate manuscript directory and a separate cumulative lab.

## Scope

This book owns the security of Northwind's software and production path:

- security ownership, assets, harm, threat actors, abuse cases, and trust boundaries;
- qualitative risk reasoning and proportionate control selection;
- human, workload, service, and automation identity, including delegation and privileged access;
- source, dependency, build, artifact, deployment, and runtime supply-chain trust;
- vulnerability discovery, reachability, exploitability, prioritization, remediation, and accepted risk;
- secret governance across creation, distribution, use, rotation, revocation, and evidence;
- data classification, minimization, protection, retention, deletion, and access evidence;
- policy design, enforcement points, exceptions, expiry, and independently reviewable evidence;
- preventive, detective, and responsive controls across application, cloud, Kubernetes, and delivery boundaries;
- security telemetry, detection engineering, investigation, containment, eradication, recovery, and restored trust;
- control evidence that can support governance, compliance, and audit without substituting compliance for security.

## Boundaries

### DevOps boundary

This book does not reteach pipeline performance, general artifact promotion, infrastructure reconciliation, Kubernetes runtime fundamentals, observability fundamentals, progressive delivery, schema evolution, messaging correctness, GitOps operation, FinOps, general incident coordination, or disaster recovery. It extends those mechanisms with adversarial models, security policy, security evidence, and compromise recovery.

### Platform Engineering boundary

This book may define requirements for secure defaults and enforcement interfaces, but it does not design an internal platform product, developer portal, paved-road experience, tenant model, shared control-plane lifecycle, or fleet-wide platform operating model.

### SRE boundary

This book may use service-level evidence to bound security changes and prove recovery, but it does not own portfolio-wide service-level objective governance, on-call design, regional-loss architecture, recurring resilience programs, or reliability learning across many services.

### Governance boundary

This book explains how operational controls produce evidence useful to governance, risk, compliance, and audit. It does not provide jurisdiction-specific legal advice, certify Northwind against a framework, or reduce security to checklist compliance.

### Specialist security boundaries

The book does not attempt to replace a complete secure-coding textbook, penetration-testing manual, cryptography text, malware-analysis course, digital-forensics handbook, privacy-law guide, or enterprise security architecture reference. It includes only the depth needed for the production decisions in scope.

## Northwind security narrative

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

source → review → build → artifact → deployment → runtime
   │        │        │         │          │          │
 identity, policy, trust evidence, detection, and response
```

The critical business outcome remains:

> A valid order is durably accepted and reaches a correct terminal state without duplicate charge, invalid inventory state, or permanent disappearance.

The critical security outcome is:

> Only authorized actors and workloads can cause or observe order-related effects; every trusted release and privileged action is attributable and policy-conformant; suspected compromise is bounded, investigated, eradicated, and followed by evidence that trustworthy operation has been restored.

## Cumulative security story

Northwind begins with working DevOps controls but an incomplete security model. Assets and ownership are implicit. Trust boundaries are undocumented. Human and automation privileges accumulate. Supply-chain evidence exists but is not governed by risk-based policy. Vulnerabilities generate noise rather than decisions. Secrets and sensitive data lack complete lifecycle controls. Preventive controls are fragmented. Detection is symptom-driven. Incident recovery can restore availability without proving that attacker persistence or compromised trust has been removed.

Across the book, the reader will:

1. define security outcomes, assets, ownership, harm, and trust boundaries;
2. model plausible threats and prioritize risk rather than enumerate everything;
3. design attributable identity, authorization, delegation, and privileged access;
4. establish policy for trusted source, dependency, build, artifact, and deployment transitions;
5. turn vulnerability findings into risk-owned remediation decisions;
6. govern secrets and sensitive data through their full lifecycles;
7. place preventive and detective controls at explicit enforcement boundaries;
8. create security evidence that supports investigation and governance;
9. detect and investigate an intrusion across identities, delivery, and runtime;
10. contain, eradicate, recover, and re-establish trust after compromise.

The cumulative attack narrative is a compromised maintainer credential used to introduce a malicious dependency and pursue production access. Early chapters model and constrain the attack path. Middle chapters enforce supply-chain, identity, secret, data, and runtime controls. Later chapters detect a controlled compromise attempt, investigate its evidence, contain its authority and exposure, eradicate persistence, rebuild from trusted roots, and prove both business and security recovery.

The attack is a teaching thread, not a claim that one scenario represents every threat actor or organization.

## Teaching contract

- Preserve the series' production focus: every chapter must enable a consequential security decision, produce an operational capability, or establish a mental model required by later production work.
- Do not enforce a theory-to-practice percentage.
- Do not add an exercise merely to make a concept appear practical.
- Concept-led chapters may produce a threat model, classification, decision record, policy rationale, risk register entry, or evidence specification rather than executable code.
- Every substantial conceptual section must be traceable to a chapter decision, durable reasoning artifact, interpretation of evidence, attack diagnosis, or later implementation dependency. Remove conceptual material that affects none of these.
- Implementation-led chapters must tell the reader what to change, why it matters, how to apply it safely, how it can fail or be attacked, and what evidence proves the result.
- Decision-led chapters must compare defensible alternatives against explicit threats, operational constraints, failure modes, and recovery consequences.
- Each chapter answers one primary production security question.
- Chapters must distinguish mechanism evidence from outcome evidence. A scanner, policy engine, identity provider, or detection rule must not be treated as proof of its own effectiveness.
- Findings are inputs to decisions, not risk decisions by themselves. Severity labels, compliance status, and tool output must not replace context, exploitability, ownership, or business impact.
- Prevention, detection, response, and recovery must be treated as complementary controls rather than maturity stages where one makes the others unnecessary.
- Every exception must have an owner, rationale, bounded scope, compensating controls where necessary, evidence, expiry, and a review or removal path.
- Every dedicated attack or failure must name severity, plausible harm, blast radius, bounding controls, evidence, containment, eradication, recovery, and proof that trust was restored.
- Near `What You Learned`, identify one or two durable outputs worth retaining.
- On first use in each reader-facing document, write an abbreviation followed by its full form and bold the complete expression. Do not alter literal code, commands, filenames, paths, keys, image names, or version identifiers.
- Use one cumulative implementation under `books/labs/devsecops/northwind/`.
- The manuscript is the guide; repository artifacts make decisions, policies, attacks, evidence, and recovery runnable or inspectable where that adds learning value.
- Local deterministic exercises must state what they simulate and what would require validation against real identity providers, registries, repositories, cloud controls, Kubernetes systems, security telemetry, ticketing systems, and external dependencies.

## Recurring principles and security questions

The five series-wide principles remain active:

1. **Blast-radius control:** expose the smallest defensible scope to uncertain change, attack, or failure.
2. **Explicit contracts:** make identity, authority, trust, state, policy, outcomes, and failure behavior reviewable.
3. **Trustworthy evidence:** separate observations and expectations so a mechanism cannot approve itself.
4. **Reconciliation:** compare desired, recorded, external, and actual state, then make disagreement visible and owned.
5. **Recovery:** distinguish corrective action from proof that the protected outcome and required trust are healthy again.

DevSecOps chapters apply four recurring security questions rather than maintaining a second list of principles:

1. What asset and harm drive this decision?
2. What trust and authority are granted?
3. What independent detection remains if prevention fails?
4. What evidence proves trust was restored?

Dedicated attacks and failures must name the relevant series principles and answer the security questions that materially apply. They must not repeat labels that have no bearing on the scenario.

## Chapter forms

### Concept-led chapter

Use when the primary outcome is a mental model necessary for later decisions:

production problem → complete mental model → applied decision cases → consequences → durable reasoning artifact → connection to later implementation

The chapter does not require an artificial lab mutation. It must still make the reader decide, classify, model, or evaluate something consequential.

### Implementation-led chapter

Use when a mechanism must be built or changed to prove the capability:

production problem → necessary concepts → baseline evidence → guided implementation → attack or failure → diagnosis → containment or recovery → verified outcome

### Decision-led chapter

Use when multiple approaches can be correct under different threats and constraints:

production problem → competing approaches → threat and operational trade-offs → production recommendation → decision record → review trigger

### Hybrid chapter

Use only when a concept or decision must immediately govern an implementation. The chapter must still have one primary question and one coherent outcome; it must not become two chapters joined for convenience.

## Proposed chapter index

0. How to Use This Book
1. Define What Security Must Protect
2. Model Threats Across Trust Boundaries
3. Turn Risk into Owned Control Decisions
4. Make Human and Automation Access Attributable
5. Govern Delegation and Privileged Operations
6. Establish Trust in Source and Dependencies
7. Enforce a Verifiable Build and Release Chain
8. Prioritize Vulnerabilities by Exploitability and Harm
9. Govern Secrets Through Their Complete Lifecycle
10. Protect Data According to Its Use and Sensitivity
11. Enforce Security Policy Without Hiding Exceptions
12. Constrain Workloads and Detect Runtime Abuse
13. Build Security Evidence and Actionable Detections
14. Investigate and Contain a Production Compromise
15. Eradicate Persistence and Restore Trust
16. Turn Operational Evidence into Sustainable Governance
17. Conclusion — A Defensible Production Security System

## Initial chapter-form allocation

| Chapter | Primary form | Primary outcome |
|---:|---|---|
| 1 | Concept-led | Security outcome, asset inventory, harm model, and ownership map |
| 2 | Concept-led | Threat model with explicit trust boundaries and prioritized abuse paths |
| 3 | Decision-led | Owned risk and control-selection record with review triggers |
| 4 | Implementation-led | Attributable human and automation identities with bounded authorization |
| 5 | Decision-led | Delegation and privileged-access model with break-glass controls |
| 6 | Implementation-led | Governed source and dependency trust with reviewable provenance |
| 7 | Implementation-led | Policy-enforced build and release chain from trusted inputs to deployment |
| 8 | Decision-led | Vulnerability prioritization and remediation decisions tied to exposure and harm |
| 9 | Implementation-led | Secret inventory, distribution, rotation, revocation, and use evidence |
| 10 | Hybrid | Data classification decisions enforced through access and lifecycle controls |
| 11 | Hybrid | Policy enforcement, exception lifecycle, and independent conformance evidence |
| 12 | Implementation-led | Workload confinement plus evidence of attempted runtime abuse |
| 13 | Implementation-led | Security telemetry and detections tied to hypotheses and response actions |
| 14 | Implementation-led | Evidence-preserving investigation and bounded containment |
| 15 | Implementation-led | Eradication, trust replacement, state reconciliation, and verified recovery |
| 16 | Decision-led | Control evidence mapped to owners, obligations, review cadence, and improvement |

## Final pre-freeze decisions

- The shared schemas and their first-use owners are defined in `SCHEMA-INVENTORY.md`.
- The lab supports Python 3.13, with PyYAML and `jsonschema` as runtime libraries and pytest and Ruff as development tools. Exact versions and hashes are pinned during scaffolding after compatibility verification.
- The cross-document terminology and path audit passed; results and accepted limitations are recorded in `PRE-FREEZE-AUDIT.md`.

## Resolved structural decisions

- Keep Chapters 4 and 5 separate: baseline identity and authorization differ from temporary delegation, privileged access, and break-glass operation.
- Keep Chapters 6 and 7 separate: admitting a source or dependency is a different claim from proving that an authorized builder produced and released an artifact from admitted inputs.
- Keep Chapter 10 combined unless implementation design proves it too dense: classification, permitted use, access, retention, and deletion form one data lifecycle.
- Keep Chapter 16 after compromise recovery so governance evaluates control evidence that the cumulative incident has tested.
- Retain the five series principles and use four recurring security questions instead of introducing five additional principles.
- Use a minimal, checksum-identified DevOps v1.1 interface baseline rather than copying the entire frozen lab or depending on its working tree at runtime.
- Use deterministic local evaluators, state machines, graph checks, policy mutation, and inert simulations according to the feasibility design in `LAB-PLAN.md`.
- Treat restored trust as a bounded evidence claim: invalidated roots and descendants are replaced, old authority fails, trusted state is reconciled, detections remain active, and business outcomes recover; the lab must not claim universal absence of attacker persistence.

## Required work before drafting

1. Review and revise the promise, boundaries, narrative, teaching contract, principles, and index.
2. Build a full chapter map covering start state, pressure, concepts, production decision, capability, files, evidence, durable outputs, attack or failure, containment, recovery, and next dependency.
3. Audit topic coverage and remove overlap, gaps, and topics that belong to another book.
4. Define the companion-lab architecture and verifier contract.
5. Freeze the reviewed plan with a dated decision record.
6. Only then draft Chapter 0 and Chapter 1.
