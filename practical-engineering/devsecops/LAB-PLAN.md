# Practical DevSecOps Engineering — Companion Lab Plan

**Status:** Frozen  
**Freeze date:** 2026-08-15  
**Lab root:** `books/practical-engineering/labs/devsecops/northwind/`  
**Depends on:** `BOOK-PLAN.md` and `CHAPTER-MAP.md`

## Lab promise

The companion lab makes Northwind's security decisions, policies, evidence, controlled attacks, containment, and restored trust inspectable and falsifiable without requiring access to a real source host, identity provider, registry, cloud account, Kubernetes cluster, security data lake, or external payment system.

It proves the behavior of the book's declared local models. It does not claim that a production vendor or environment enforces the same behavior.

## Inherited DevOps baseline decision

Use a **minimal, checksum-identified interface baseline**, not a full copy of the frozen DevOps lab and not a runtime dependency on its working tree.

The DevSecOps lab will contain `inherited/devops-v1.1/` with only the contracts and representative evidence needed by later security decisions. A manifest will record:

- source release: *Practical DevOps Engineering* v1.1;
- frozen companion-lab commit: `4c6dc1ff486d101c12e6dbee1480a49ec9eca485`;
- source path and source checksum for every inherited file;
- local interface-fixture checksum;
- whether the fixture is copied verbatim or reduced to a documented stable interface; and
- which DevSecOps chapters consume it.

The baseline will include minimal interfaces for:

- artifact identity, **SBOM (Software Bill of Materials)**, provenance, and release expectations;
- workload identity subject, issuer, audience, expiry, and policy decisions;
- structured telemetry, correlation context, deployment identity, and user-outcome evidence;
- GitOps desired identity and reconciliation result;
- incident evidence and business recovery outcomes; and
- durable reconstruction identity where Chapter 15 requires a known-good root.

Reduced fixtures must be generated deliberately and reviewed. They must not be described as exact copies. No test may read from `books/practical-engineering/labs/devops/northwind/` at runtime.

## Repository layout

```text
books/practical-engineering/labs/devsecops/northwind/
├── Makefile
├── README.md
├── pyproject.toml
├── inherited/
│   └── devops-v1.1/
│       ├── MANIFEST.yaml
│       ├── release/
│       ├── identity/
│       ├── observability/
│       ├── gitops/
│       ├── incident/
│       └── recovery/
├── schemas/                 shared artifact and evidence schemas
├── security-model/          assets, harms, invariants, ownership
├── threat-model/            boundaries, flows, abuse paths
├── risk/                    risk method and control decisions
├── identity/                subjects, trust, roles, decisions
├── privilege/               elevation, delegation, break glass
├── supply-chain/            source, dependency, build, release policy
├── vulnerabilities/         normalized findings, context, decisions
├── secrets/                 inventory, policy, exposure and rotation
├── data-security/           classification, use, access, lifecycle
├── policy/                  bundle, enforcement points, exceptions
├── runtime/                 workload contracts and security events
├── detection/               event contract, hypotheses, rules, coverage
├── response/                evidence, timeline, scope, containment
├── recovery/                eradication, trust rebuild, verification
├── governance/              controls, evidence map, assurance
├── fixtures/
│   ├── observations/        mechanism-produced or simulated facts
│   ├── attacks/             inert controlled attack inputs
│   └── expected/            independent expectations
├── checkpoints/
│   └── chapter-NN/
├── tools/                   deterministic evaluators and simulators
└── tests/                   evaluator tests and mutation tests
```

Generated reports and temporary attack state will live under ignored `build/` and `evidence/` directories. Committed fixtures must never make a generated checkpoint appear complete without running the relevant mechanism.

## Common artifact model

All governed YAML or JSON artifacts will use a shared envelope where appropriate:

```yaml
schema_version: 1
kind: control-decision
id: decision-example
owner: team-or-role
status: active
effective_at: 2026-08-15T00:00:00Z
review:
  trigger: material-change
  due_at: 2026-11-15T00:00:00Z
references: []
```

Schemas must validate syntax and required relationships. They must not pretend to validate whether a human judgment is wise. Judgment is tested through explicit scenario constraints, missing evidence, contradiction, expiry, mutation, and downstream consequences.

## Evidence contract

Every checkpoint report must keep these categories separate:

```yaml
mechanism_evidence: []
decision_evidence: []
outcome_evidence: []
recovery_evidence: []
limitations: []
```

An evaluator must not:

- accept an expected value emitted by the mechanism under test;
- treat absence of an event as proof of safety unless telemetry completeness is independently proven;
- treat schema validity as a correct risk or security decision;
- treat a blocked attack as evidence that detection worked;
- treat a restored process or deployment as restored trust; or
- silently substitute fixture truth for evidence a real system would need to produce.

## Chapter state model

Each chapter supports the states appropriate to its form:

| State | Meaning |
|---|---|
| `start` | Cumulative prerequisites exist; the chapter capability is intentionally incomplete. |
| `baseline` | The evaluator runs successfully and proves the declared weakness is present. |
| `complete` | The chapter decision or implementation satisfies independent expectations. |
| `challenge` | A concept/decision scenario exposes incomplete reasoning or unsafe treatment. |
| `attack` | An inert controlled input exercises prevention, detection, evidence, or containment. |
| `contained` | Active modeled harm and authority are bounded; trust is not yet assumed restored. |
| `recovered` | Required state is reconciled and business plus security recovery evidence passes. |

Concept-led chapters normally use `start → baseline → complete → challenge → corrected`. Implementation-led attack chapters normally use `start → baseline → complete → attack → contained/recovered`. A chapter must not manufacture states that do not support its learning objective.

## Standard command contract

Repository-wide commands:

```text
make bootstrap
make test
make lint
make audit
make matrix
```

Chapter commands use stable two-digit numbers:

```text
make chapter-NN-baseline
make chapter-NN-checkpoint
make chapter-NN-challenge       # concept/decision chapters where applicable
make chapter-NN-attack          # implementation chapters where applicable
make chapter-NN-contain         # only where containment is distinct
make chapter-NN-recover         # only where recovery is a chapter outcome
make chapter-NN-verify-recovery
```

Commands must state whether a successful exit means “unsafe baseline correctly detected,” “capability verified,” “attack injected,” “containment verified,” or “recovery verified.” A generic success message is insufficient.

## Snapshot convention

Each core chapter receives immutable versioned tags after verification:

```text
v1.0-chapter-NN-start
v1.0-chapter-NN-complete
```

Reader-facing aliases may point to the current release:

```text
chapter-NN-start
chapter-NN-complete
```

Start and complete tags are curated exercise snapshots, not promised merge milestones or linear ancestry. Attack state is generated from the complete snapshot so malicious or compromised fixtures cannot be mistaken for a trusted reference state. Contained and recovered reports are generated evidence unless a chapter genuinely requires a separate curated snapshot. The v1.0 snapshot set is published in `books/practical-engineering/labs/devsecops/northwind/`; see `RELEASE-MANIFEST.md`.

## Attack-simulation safety contract

- Simulations operate only on local inert fixtures and generated state.
- No real credentials, exploit payloads, persistence mechanisms, command-and-control endpoints, or destructive external actions are included.
- Look-alike packages and malicious artifacts are text fixtures carrying unmistakable simulation markers.
- Network behavior is represented by events and policy decisions, not real outbound contact.
- Credential replay uses non-secret identifiers and a deterministic authorization model.
- Data exposure uses synthetic Northwind records with no personal information.
- Containment and revocation mutate only generated lab state.
- Each attack command prints its scope and evidence paths before reporting success.

## Per-chapter feasibility and verification design

| Ch. | Local mechanism | What can be meaningfully verified | Required limitation |
|---:|---|---|---|
| 1 | Schema and relationship evaluator | Assets, harms, invariants, and owners are complete and cross-referenced for declared scope | Cannot prove the chosen asset set is complete for a real organization |
| 2 | Flow/path graph evaluator | Attack paths cross declared boundaries and terminate at threatened invariants with owners and assumptions | Cannot discover unknown real architecture or attacker behavior |
| 3 | Scenario decision evaluator | Risk treatments include context, uncertainty, ownership, residual risk, and review triggers without score-only decisions | Cannot assign objectively correct likelihood |
| 4 | Deterministic authorization engine | Subject/action/resource/context decisions, attribution, audience, expiry, denial, and revocation behavior | Does not exercise a real identity provider |
| 5 | Privilege workflow state machine | Independent approval, bounded scope/time, revocation, break-glass evidence, and after-action review | Does not grant real production privilege |
| 6 | Source/dependency resolver model | Approved origins, protected changes, lock/hash integrity, review independence, and confusion rejection | Does not query or secure a live repository or registry |
| 7 | Attestation/admission evaluator | Claims bind admitted source, dependencies, builder, artifact, approval, and environment; invalid trust is rejected | Uses fixture attestations rather than a hosted builder or transparency service |
| 8 | Finding correlation and decision engine | Deduplication, deployed context, reachability, exposure, harm, ownership, deadlines, and exceptions affect treatment | Does not prove exploitability against a live workload |
| 9 | Secret lifecycle state machine | Inventory completeness, reference-only use, attributable access, overlap rotation, revocation, and replay rejection | Uses synthetic tokens and a modeled provider |
| 10 | Data use/access/lifecycle evaluator | Classification drives permitted fields, purpose, store, retention, deletion, and sanitized non-production copies | Does not prove deletion from a real database or backup system |
| 11 | Policy engine and mutation suite | Enforcement-point consistency, unsafe mutation rejection, bounded exceptions, compensation, and expiry | Does not deploy a real admission controller or repository rule set |
| 12 | Runtime contract evaluator | Modeled privilege, process, filesystem, identity, and egress behavior is allowed, denied, or detected as declared | Does not exercise a kernel sensor, container runtime, or cluster network |
| 13 | Event normalizer, correlation engine, and simulations | Inherited trace/deployment context is preserved; hypotheses fire with required context; telemetry gaps are visible | Does not benchmark a production telemetry pipeline or real attacker evasion |
| 14 | Investigation and containment state machine | Evidence integrity, fact/inference separation, scope, revoked authority, isolation, and business-impact monitoring | Is not a forensic acquisition or legal chain-of-custody system |
| 15 | Trust graph and recovery reconciler | Invalid roots and descendants are replaced; old authority fails; rebuilt chain, business state, and security monitoring pass | Cannot prove absence of persistence beyond the modeled inventory and evidence |
| 16 | Control/evidence graph and assurance evaluator | Objectives map to owners, implementations, independent evidence, limits, exceptions, review triggers, and improvements | Does not certify compliance with a legal or industry framework |

All chapters have a meaningful local proof target. The strongest epistemic limitation belongs to Chapter 15: absence of modeled persistence must never be phrased as universal proof that no attacker persistence exists.

## Chapter checkpoint ownership

Each `checkpoints/chapter-NN/` directory will contain:

- `README.md`: exact claim, inputs, outputs, limitations, and success meaning;
- `baseline.py`: verifies the expected red capability without treating red as command failure;
- `checkpoint.py`: verifies completed policy, evidence, and outcome relationships;
- `expectations.yaml`: independent expectations not emitted by the mechanism under test;
- `cases/`: safe positive, negative, boundary, expiry, and mutation cases; and
- chapter-specific attack, containment, correction, or recovery drivers only when required.

Shared evaluators belong in `tools/`; chapter checkpoints compose them and add chapter-specific assertions. A chapter must not own a duplicate evaluator merely to appear self-contained.

## Test strategy

### Unit tests

Test parsers, time/expiry handling, graph traversal, authorization, evidence classification, hashing, normalization, and reconciliation.

### Policy mutation tests

Automatically widen scope, remove ownership, extend expiry, change issuer/audience, replace trusted origin, remove required evidence, suppress telemetry, or swap expected artifact identity. At least one independent test must reject every material control family.

### Cumulative matrix

For each clean `start` tag:

1. baseline proves the intended weakness;
2. checkpoint does not incorrectly pass;
3. required inputs exist and generated evidence does not.

For each clean `complete` tag:

1. checkpoint passes;
2. chapter challenge or attack produces the expected unsafe or contained state;
3. recovery/correction passes when required; and
4. earlier cumulative checkpoints still pass unless the chapter explicitly and safely versions an earlier contract.

### Adversarial evaluator tests

Tests must ensure a mechanism cannot approve itself by editing observations, expected values, timestamps, owners, or policy versions together. Missing evidence, stale evidence, contradictory evidence, and evidence produced after the claimed decision must fail where relevant.

## Editorial and executable freeze gates

### Planning gates

- Book promise, boundaries, narrative, index, forms, chapter map, and lab plan agree.
- Every priority concept appears in the coverage audit.
- Every chapter has one primary question and an explicit dependency handoff.
- Every substantial concept maps to a decision, durable output, evidence interpretation, attack diagnosis, or later implementation dependency.
- Cumulative attacks, connected consequences, and independent failures are explicitly labeled.

### Artifact gates

- All governed artifacts validate against pinned schemas.
- All references resolve to existing identifiers and owners.
- Exceptions are bounded, owned, evidenced, and expiring.
- Inherited interfaces match their checksum manifest.
- No real secrets, personal data, active malware, or external attack targets exist.

### Executable gates

- All start baselines prove red from clean snapshots.
- No start snapshot incorrectly passes its completion checkpoint.
- All complete checkpoints pass from clean snapshots.
- All declared challenges and attacks produce their expected state.
- All containment/recovery chapters prove the distinct required outcome.
- The cumulative matrix passes on the supported Python version.
- Unit, mutation, adversarial, lint, and formatting checks pass.
- The lab working tree is clean after verification except documented ignored evidence.

### Editorial gates

- First-use abbreviation formatting follows the series rule.
- Attack/failure sections name applicable series principles and answer applicable security questions.
- Mechanism, decision, outcome, and recovery evidence are not conflated.
- Simulator limitations appear beside claims that depend on them.
- Each chapter retains one or two durable outputs already earned through its work.
- No chapter repeats a DevOps implementation as new DevSecOps content.

## Work required before plan freeze

1. Reconcile terminology and file paths across `BOOK-PLAN.md`, `CHAPTER-MAP.md`, and this file.
2. Define the shared schema inventory and ownership without implementing all schemas.
3. Specify the exact inherited DevOps interface files and generate their checksum manifest during lab scaffolding.
4. Decide the supported Python version and minimal dependencies.
5. Add the planning freeze record only after these decisions pass review.
