# How to Use This Book

## Who this book is for

This book is for intermediate-to-advanced DevOps, cloud, infrastructure, platform, security, and **SRE (Site Reliability Engineering)** practitioners who need to make security enforceable across a production delivery and operating path.

You should already be comfortable with Linux, Git, containers, **CI/CD (Continuous Integration and Continuous Delivery)**, cloud and Kubernetes fundamentals, infrastructure as code, networking, workload identity, observability, and incident response basics. The book does not teach those subjects from first principles. It uses them as the production surface on which security decisions must operate.

You do not need to be a penetration tester, malware analyst, cryptographer, digital-forensics specialist, privacy lawyer, or compliance auditor. Those disciplines contain important knowledge, but this book has a narrower promise: help you decide what must be protected, model how it can be abused, select proportionate controls, enforce those controls at defensible boundaries, interpret security evidence, and restore trustworthy operation after compromise.

This is not a catalog of security tools. Products and standards change. The durable skill is being able to explain:

- which asset and harm justify a control;
- which trust and authority the control grants;
- what evidence can reveal failure or misuse;
- how an exception remains bounded and temporary; and
- what must be replaced, reconciled, and verified after trust is invalidated.

## Relationship to *Practical DevOps Engineering*

This book continues the Northwind Commerce system from *Practical DevOps Engineering*. The earlier book established a production delivery path with fast feedback, immutable artifact identity, provenance, reconciled infrastructure, a bounded Kubernetes runtime, workload identity, observable outcomes, progressive delivery, compatible data changes, safe asynchronous processing, GitOps reconciliation, cost and capacity controls, incident coordination, and reconstruction from durable evidence.

Those capabilities are prerequisites here. This book does not repeat their implementation and present it as new security work. Instead, it asks the adversarial questions that remain:

- Which source, dependency, builder, identity, and policy claims deserve trust?
- Can valid credentials exercise excessive authority?
- Does signed evidence describe an authorized process or merely a cryptographically attributable one?
- Which vulnerabilities are actually exposed, reachable, and capable of harming Northwind?
- Where do secrets and sensitive data exist beyond their intended systems?
- Which preventive failures would Northwind detect independently?
- Can recovery remove attacker capability and persistence rather than merely restore availability?

The frozen DevOps manuscript and companion lab remain unchanged. This book has a separate cumulative implementation under:

```text
books/practical-engineering/labs/devsecops/northwind/
```

The new lab does not read the DevOps lab's working tree at runtime. It carries a small set of reduced interface fixtures whose manifest records the frozen DevOps v1.1 source paths, source checksums, local checksums, and consumers. This makes the prerequisite explicit without copying the whole earlier implementation or allowing later DevOps edits to change this book silently.

## The Northwind system

Northwind Commerce remains deliberately small enough to understand and large enough to require real security decisions:

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

- `storefront-api` serves catalog reads and accepts orders.
- `order-worker` processes accepted orders asynchronously and can cause payment and inventory effects.
- `notification-service` sends non-critical confirmations.
- PostgreSQL stores order and processing state.
- A durable queue separates acceptance from asynchronous completion.
- Payment and email providers are external trust boundaries represented by controlled fixtures.
- The source, build, release, deployment, and runtime path can change what production executes and which authority it receives.

The critical business outcome remains:

> A valid order is durably accepted and reaches a correct terminal state without duplicate charge, invalid inventory state, or permanent disappearance.

This book adds a critical security outcome:

> Only authorized actors and workloads can cause or observe order-related effects; every trusted release and privileged action is attributable and policy-conformant; suspected compromise is bounded, investigated, eradicated, and followed by evidence that trustworthy operation has been restored.

Security is not separate from the business outcome. An available service that accepts attacker-controlled releases is not healthy. A restored worker that still uses compromised authority is not recovered. A policy-compliant system that exposes unnecessary customer data is not safe merely because its controls generated passing reports.

## The cumulative security path

The chapters form one dependency chain:

```text
assets, harms, invariants, and ownership
  → threat paths and trust boundaries
  → risk-owned control decisions
  → attributable identity and authorization
  → governed delegation and privilege
  → trusted source and dependencies
  → verifiable build and release admission
  → contextual vulnerability decisions
  → complete secret lifecycle
  → use-based data protection
  → enforceable policy and bounded exceptions
  → runtime confinement
  → correlated security detection
  → investigation and containment
  → eradication and restored trust
  → sustainable operational governance
```

Later chapters consume earlier decisions. The asset register determines what the threat model protects. Threat paths give risk decisions their context. Risk decisions justify identity, supply-chain, secret, data, policy, runtime, and detection controls. Those controls then produce evidence for investigation. Investigation bounds eradication, and recovery evidence becomes the strongest test of the governance claims at the end of the book.

The cumulative attack narrative begins with a compromised maintainer credential used to introduce a malicious dependency and pursue production access. It develops across identity, privilege, source, build, secret, runtime, detection, containment, and recovery chapters.

Not every security failure comes from that attacker. Exercises are labeled according to their relationship with the main narrative:

- **Cumulative attack:** advances the compromised-maintainer intrusion.
- **Connected consequence:** demonstrates harm enabled by that intrusion path.
- **Independent control failure:** proves that the control matters even without the cumulative attacker.

This distinction prevents the main attacker from becoming an unrealistic explanation for every organizational and technical failure.

## Four chapter forms

The book does not force every learning objective into the same structure.

### Concept-led chapters

A concept-led chapter develops a mental model required for later production decisions. The reader may classify assets, map authority, model trust boundaries, or distinguish forms of harm. Its durable output can be a reviewed reasoning artifact rather than executable code.

Concept-led does not mean detached theory. Every substantial conceptual section must affect a chapter decision, durable artifact, interpretation of evidence, attack diagnosis, or later implementation dependency. Material that affects none of those does not belong.

### Decision-led chapters

A decision-led chapter compares approaches under explicit threats and operational constraints. It records the recommendation, trade-offs, residual uncertainty, owner, exception behavior, and review trigger.

A risk score, scanner label, compliance result, or vendor recommendation is an input—not the decision itself.

### Implementation-led chapters

An implementation-led chapter starts from a red capability, establishes the necessary mental model, guides a system or policy change, exercises a controlled attack or failure, diagnoses the evidence, and verifies containment or recovery where required.

The chapter tells you what to change, why it matters, how to apply it safely, and what falsifiable evidence proves the claimed result. You are not expected to rediscover essential production steps merely to make the work feel difficult.

### Hybrid chapters

A hybrid chapter uses a concept or decision immediately to govern implementation. It still answers one primary production question. Hybrid is not permission to join unrelated chapters for convenience.

There is no theory-to-practice percentage. There is also no artificial exercise added to satisfy one. The practical requirement is consequential reader reasoning, meaningful system change where appropriate, trustworthy evidence, and explicit limits on what has been proved.

## Four kinds of evidence

Security mechanisms often produce impressive output while leaving the important claim unanswered. This book separates four evidence categories:

1. **Mechanism evidence** proves that a configured control operated. An admission rule rejected an artifact; an authorization engine denied an action; a detector emitted an alert.
2. **Decision evidence** proves that an owner evaluated the required context and made a bounded decision. A vulnerability treatment records exposure, exploitability, harm, uncertainty, owner, deadline, and review trigger.
3. **Outcome evidence** proves that the protected business or security outcome remains healthy. Orders still reach correct terminal states; unauthorized payment effects do not succeed; expected production behavior remains available after confinement.
4. **Recovery evidence** proves that harmful authority, persistence, and invalid trust were removed or replaced within the declared scope. Old credentials fail, compromised artifacts cannot return, trusted state is reconciled, detections remain active, and business outcomes recover.

These categories are complementary. One cannot silently substitute for another. A passing policy test does not prove the production outcome. A healthy order-success metric does not prove that no sensitive data was exposed. A restarted deployment does not prove that attacker persistence is gone.

Chapter `recover` commands produce chapter-scoped correction or recovery evidence. Only Chapter 15's `verify-recovery` command produces the book's bounded restored-trust claim. Earlier chapters should not treat a local recover target as proof that production trust was restored.

## Lab states and commands

Use Python 3.13. From the DevSecOps lab root:

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
- **Challenge:** a concept or decision scenario exposes incomplete reasoning.
- **Attack:** an inert local input exercises prevention, detection, evidence, or containment.
- **Contained:** modeled active harm and authority are bounded, but trust is not yet assumed restored.
- **Recovered:** required state is reconciled and both security and business recovery evidence pass. Except in Chapter 15, this is chapter-scoped recovery rather than production restored trust.

A successful baseline command means the evaluator correctly found the expected unsafe state. It does not mean the capability is already secure.

Chapter commands follow a stable pattern where applicable:

```text
make chapter-NN-baseline
make chapter-NN-checkpoint
make chapter-NN-challenge
make chapter-NN-attack
make chapter-NN-contain
make chapter-NN-recover
make chapter-NN-verify-recovery
```

Not every chapter uses every command. Concept-led and decision-led chapters do not manufacture an attack or recovery sequence when classification, modeling, or decision correction is the real work.

`make chapter-NN-recover` is chapter-scoped. Only `make chapter-15-verify-recovery` produces the bounded restored-trust claim.

## Chapter snapshots

Versioned start and complete tags are the exercise snapshots:

```text
v1.0-chapter-NN-start
v1.0-chapter-NN-complete
chapter-NN-start
chapter-NN-complete
```

The versioned tags are the immutable release identity. The reader-facing aliases point to the same commits in this freeze and may advance in a later release. Tags are curated exercise snapshots, not merge milestones. Do not infer the teaching contract from Git ancestry.

Attack state is generated from the complete snapshot. A malicious dependency, exposed token, permissive exception, or compromised artifact must never be preserved as if it were a trusted completed reference.

Create a working branch from the start snapshot and compare against the complete reference without merging it as a shortcut:

```bash
git switch -c my-chapter-NN chapter-NN-start
git diff chapter-NN-start chapter-NN-complete
```

### Working-tree procedure

From the DevSecOps lab root:

1. create the Python virtual environment and run `make bootstrap`, `make test`, `make lint`, and `make audit`;
2. start from `chapter-NN-start` (or work in the completed tree if you already have later chapters);
3. run the chapter baseline and confirm that it detects the documented red state;
4. follow the chapter's guided work and preserve its decision or implementation evidence;
5. run the completed checkpoint;
6. run the declared challenge or attack where applicable;
7. verify correction, containment, or recovery where the chapter requires it; and
8. retain the chapter's durable outputs.

A concept-led chapter may change only reviewed YAML or Markdown artifacts. The absence of application code does not make the decision record disposable.

Some commands mutate operational files. Those mutations persist in the working tree. Later chapters depend on earlier generated `build/` outputs and, in Chapters 12 through 16, on specific live register state. If you have already run a later chapter's containment or recovery, restore the incident-ready start with `make lab-reset` rather than assuming a start tag reset the tree.

Files that later chapters may mutate include:

- `identity/subjects.yaml`
- `runtime/contracts/order-worker.yaml`
- `runtime/policies/behavior.yaml`
- `supply-chain/deployment-evidence.yaml`
- `response/case/incident.yaml`
- `policy/enforcement-points.yaml`
- `secrets/inventory.yaml`

### Chapters 12–16 command chain

Detection through governance needs generated evidence and live incident state. When those outputs are absent, run this sequence rather than a single later baseline:

```text
make chapter-12-attack
make chapter-13-attack
make chapter-14-open
make chapter-14-baseline
make chapter-14-checkpoint
make chapter-14-contain
make chapter-14-recover
make chapter-15-baseline
# … Chapter 15 guided work …
make chapter-15-verify-recovery
make chapter-16-baseline
```

`chapter-14-open` writes incident `INC-2026-0815-01` as `investigating` and sets `compromised-session` to `active`. Complete snapshots keep that incident-ready start. After Chapter 15 verification the live case is `closed` and that session is revoked; `make lab-reset` restores the Chapter 14 start registers.

The complete tag is a reference solution and verification target. It is not a substitute for making and explaining the chapter's decisions, and it should not be merged as a shortcut.

## Safe attack simulations

The lab's attacks are deterministic, local, inert, and non-destructive:

- look-alike packages and malicious artifacts are marked text fixtures;
- credential replay uses synthetic identifiers and a modeled authorization engine;
- command-and-control traffic is represented by events and policy decisions rather than real network contact;
- exposed data is synthetic Northwind data with no personal information;
- containment and revocation modify generated lab state only; and
- no real credential, exploit payload, persistence mechanism, malware, or external attack target is included.

These constraints do not weaken the learning objective. The reader must still reason about authority, evidence, attack progression, containment, and recovery. The lab simply avoids confusing a security engineering exercise with permission to attack a real system.

## What local verification proves

The local evaluators verify structure, relationships, policy decisions, state transitions, graph reachability, expiry, mutation resistance, evidence integrity, correlation, containment, and reconciliation within the declared model.

They do not prove that a real repository host protects branches, an identity provider validates the same claims, a registry preserves trustworthy provenance, a cloud control plane enforces the modeled authorization, a Kubernetes runtime blocks the same behavior, a telemetry backend retains complete evidence, or a real attacker lacks an unmodeled persistence path.

That final limitation matters most during recovery. The book can prove that inventoried trust roots and modeled persistence paths were replaced or reconciled. It cannot universally prove that no attacker persistence exists. Production confidence depends on the completeness of the inventory, the quality and independence of collected evidence, validation against real systems, and continued heightened monitoring.

## Five principles and four security questions

The five principles established for the series remain active:

1. **Blast-radius control:** expose the smallest defensible scope to uncertain change, attack, or failure.
2. **Explicit contracts:** make identity, authority, trust, state, policy, outcomes, and failure behavior reviewable.
3. **Trustworthy evidence:** separate observations and expectations so a mechanism cannot approve itself.
4. **Reconciliation:** compare desired, recorded, external, and actual state, then make disagreement visible and owned.
5. **Recovery:** distinguish corrective action from proof that the protected outcome and required trust are healthy again.

DevSecOps work repeatedly asks four security questions:

1. What asset and harm drive this decision?
2. What trust and authority are granted?
3. What independent detection remains if prevention fails?
4. What evidence proves trust was restored?

Dedicated attacks and failures name only the principles and questions that materially apply. Repeating every label would create ceremony rather than clearer reasoning.

## Best Practice and Production Practice

The book retains two labels from the series:

- **Best Practice:** a strong default that is broadly useful.
- **Production Practice:** how that default must be validated or adapted for the actual assets, threats, identities, failure modes, dependencies, evidence quality, operating constraints, and recovery obligations.

For example, short-lived credentials are a strong default. In production, their value depends on verified subject and audience claims, bounded authorization, protected issuance, meaningful expiry, revocation behavior, attributable use, and evidence that replay outside the intended context fails.

## How to judge your work

Do not ask only whether the configured control passes. Ask:

> What asset and harm justify this decision, what trust and authority cross the boundary, what evidence could falsify the control's claim, what happens when prevention fails, and how will we prove that trustworthy operation—not merely availability—has been restored?

That question is the reading contract for the chapters ahead.
