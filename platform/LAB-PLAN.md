# Practical Platform Engineering — Companion Lab Plan

**Status:** Frozen  
**Freeze date:** 2026-08-16  
**Lab root:** `books/labs/platform/northwind/`  
**Depends on:** `BOOK-PLAN.md` and `CHAPTER-MAP.md`

## Lab promise

The companion lab makes Northwind's platform-product decisions, tenancy, paved roads, environments, contracts, control-plane operations, quota, fleet change, support, and bounded control-plane recovery inspectable and falsifiable without requiring a real developer portal, identity provider, cluster fleet, billing export, or ticketing system.

It proves the behavior of the book's declared local models. It does not claim that a production vendor or environment enforces the same behavior.

## Inherited baseline decision

Use **minimal, checksum-identified interface baselines**, not full copies of earlier labs and not runtime dependencies on their working trees.

The Platform lab will contain:

```text
inherited/devops-v1.1/
inherited/devsecops-v1.0/
```

`devops-v1.1` is the existing lab-snapshot identifier, not the published DevOps book version. Manifests will record source release, source path, source checksum, local fixture checksum, reduction notes, and consuming Platform chapters.

The DevOps baseline will include only interfaces later platform products consume:

- artifact identity and promotion expectations;
- workload identity subject, issuer, audience, and expiry;
- user-outcome telemetry and deployment identity;
- GitOps desired identity and reconciliation result;
- reconstruction identity where control-plane recovery needs a known-good root.

The DevSecOps baseline will include only interfaces later guardrails consume:

- authorization decision shape;
- policy decision and exception shape;
- control and evidence-map shape.

Reduced fixtures must be generated deliberately and reviewed. No test may read from `books/labs/devops/northwind/` or `books/labs/devsecops/northwind/` at runtime.

Platform Chapter 9 guardrail exceptions must **reference** an inherited DevSecOps exception ID. `guardrails/exceptions.yaml` must not duplicate owner, scope, compensation, or expiry fields that the inherited exception already carries. The platform record may add only platform-local projection: tenant, paved-road or exit, remaining isolation, and scorecard effect. Evaluators resolve those fields from the inherited fixture.

## Repository layout

```text
books/labs/platform/northwind/
├── Makefile
├── README.md
├── pyproject.toml
├── inherited/
│   ├── devops-v1.1/
│   └── devsecops-v1.0/
├── schemas/
├── product/                 brief, users, jobs, non-goals
├── intake/                  capability candidates and decisions
├── tenancy/                 tenants, isolation, roles
├── catalog/                 systems, ownership, dependencies
├── paved-road/              contract, scaffold, conformance, exits
├── environments/            product, requests, leases
├── contracts/               infrastructure API versions and compatibility
├── control-plane/           subjects, admission, reconciliation
├── guardrails/              defaults, scorecards, exceptions
├── devex/                   measurement contract and samples
├── quota/                   tenant floors, ceilings, showback
├── fleet/                   onboard, upgrade, deprecate, migrate
├── support/                 model, escalation, changes, incidents
├── recovery/                plane evidence, isolation, restore, verification
├── fixtures/
│   ├── observations/
│   └── expected/
├── checkpoints/
│   └── chapter-NN/
├── tools/
└── tests/
```

Generated reports live under ignored `build/` and `evidence/` directories. Committed fixtures must never make a generated checkpoint appear complete without running the relevant mechanism.

## Common artifact model

All governed YAML or JSON artifacts will use a shared envelope where appropriate:

```yaml
schema_version: 1
kind: platform-decision
id: decision-example
owner: team-or-role
status: active
effective_at: 2026-08-16T00:00:00Z
review:
  trigger: material-change
  due_at: 2026-11-16T00:00:00Z
references: []
```

Schemas must validate syntax and required relationships. They must not pretend to validate whether a product judgment is wise.

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
- treat a portal page, catalog publish, or scorecard as proof a team finished a job;
- treat schema validity as a correct productization or tenancy decision;
- treat restored control-plane process as proof every tenant is healthy;
- silently substitute fixture truth for evidence a real platform would need to produce.

## Chapter state model

| State | Meaning |
|---|---|
| `start` | Cumulative prerequisites exist; the chapter capability is intentionally incomplete. |
| `baseline` | The evaluator runs successfully and proves the declared weakness is present. |
| `complete` | The chapter decision or implementation satisfies independent expectations. |
| `challenge` | A concept/decision scenario exposes incomplete reasoning or unsafe treatment. Correction is part of that write-up, not a separate lab state. |
| `failure` | An inert controlled input exercises isolation, quota, upgrade, or authority failure. |
| `contained` | Active modeled harm and authority are bounded; product health is not yet assumed restored. |
| `recovered` | Required state is reconciled and platform-product plus tenant isolation evidence passes. |

Concept-led and decision-led chapters normally use `start → baseline → complete → challenge`. Correction happens **inside** the challenge write-up; there is no `corrected` state and no `make chapter-NN-corrected` target. Implementation-led chapters normally use `start → baseline → complete → failure → contained/recovered`.

## Standard command contract

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
make chapter-NN-challenge
make chapter-NN-failure
make chapter-NN-contain
make chapter-NN-recover
make chapter-NN-verify-recovery
```

Commands must state whether a successful exit means “unsafe baseline correctly detected,” “capability verified,” “failure injected,” or “recovery verified.”

## Snapshot convention

```text
v1.0-chapter-NN-start
v1.0-chapter-NN-complete
```

Reader-facing aliases may point to the current release:

```text
chapter-NN-start
chapter-NN-complete
```

Tags are curated exercise snapshots, not promised merge milestones or linear ancestry. Failure state is generated from the complete snapshot so broken fixtures cannot be mistaken for a trusted reference state. Contained and recovered reports are generated evidence unless a chapter genuinely requires a separate curated snapshot.

## Failure-simulation safety contract

- Simulations operate only on local inert fixtures and generated state.
- No real credentials, cluster mutation, billing APIs, or destructive external actions are included.
- Cross-tenant access uses synthetic identifiers.
- Quota and noisy-neighbor cases are numeric fixtures, not live load tests.
- Control-plane restore mutates only generated lab state.
- Each failure command prints its scope and evidence paths before reporting success.

## Per-chapter feasibility and verification design

| Ch. | Local mechanism | What can be meaningfully verified | Required limitation |
|---:|---|---|---|
| 1 | Schema and relationship evaluator | Users, jobs, owners, and refusals are complete and cross-referenced | Cannot prove the chosen jobs are the right jobs for a real company |
| 2 | Intake decision evaluator | Productize/leave/decline records include demand, isolation impact, support cost, and review | Cannot assign objectively correct centralization |
| 3 | Isolation graph evaluator | Tenants, roles, and prohibited inherited authority are consistent | Cannot discover unknown real cluster sharing |
| 4 | Catalog freshness evaluator | Living owners, dependencies, and stale-entry failure | Does not run a real portal search or HR system |
| 5 | Conformance and exit evaluator | Path completion, unofficial-fork failure, supported-exit fields | Does not scaffold a live repository |
| 6 | Environment lease state machine | Request, TTL reclaim, cross-tenant deny, isolation invariants | Does not provision a real namespace or VPC |
| 7 | Contract compatibility evaluator | Version binding, breaking-change rejection, migration notes | Does not apply real Terraform/Helm modules |
| 8 | Admission and reconcile evaluator | Tenant-scoped subjects, self-approval deny, last-known-good plane | Does not run a real Kubernetes control plane |
| 9 | Guardrail binding evaluator | Defaults apply; each exception row references a DevSecOps exception ID; scorecard fails on inherited expiry without local field copies | Does not deploy real admission webhooks |
| 10 | Measurement-contract evaluator | Job indicators present; vanity listed as non-metrics; missing samples fail | Does not survey real developers |
| 11 | Quota and showback evaluator | Floors, ceilings, quality-gated units, starvation failure | Does not read a real cloud bill |
| 12 | Fleet state machine | Onboard, freeze, cohort upgrade, deprecation, rollback | Does not upgrade a live fleet |
| 13 | Support and change evaluator | Escalation mapping, unofficial plane-admin reject, reviewed change | Does not operate a real ticketing system |
| 14 | Plane restore reconciler | Mixed-backup reject, cross-tenant replay deny, bounded tenant continue/freeze | Cannot prove regional-loss or portfolio RTO; that remains SRE |

All chapters have a meaningful local proof target. The strongest epistemic limitation belongs to Chapter 14: isolated plane restore must never be phrased as an enterprise disaster-recovery or multi-region program.

## Chapter checkpoint ownership

Each `checkpoints/chapter-NN/` directory will contain:

- `README.md`: exact claim, inputs, outputs, limitations, and success meaning;
- `baseline.py`: verifies the expected red capability without treating red as command failure;
- `checkpoint.py`: verifies completed product, evidence, and outcome relationships;
- `expectations.yaml`: independent expectations not emitted by the mechanism under test;
- `cases/`: safe positive, negative, boundary, expiry, and mutation cases; and
- chapter-specific failure, containment, correction, or recovery drivers only when required.

Shared evaluators belong in `tools/`.

## Test strategy

- Schema tests for every governed kind.
- Evaluator tests for missing evidence, stale ownership, cross-tenant access, expired exceptions, vanity metrics, quota starvation, and mixed-backup restore.
- Mutation tests that flip one required field and expect checkpoint failure.
- No test may read earlier labs' working trees.
- Ruff and pytest on Python 3.13.

## Runtime and tools

- Supported interpreter: Python 3.13.
- Runtime libraries: PyYAML and `jsonschema`.
- Development tools: pytest and Ruff.
- Exact versions and hashes are pinned during scaffolding, not invented before verification.

## Release gates before a companion-lab freeze

1. Planning freeze of this file with the rest of the planning set.
2. Scaffolded lab with inherited manifests and checksums.
3. Working-tree tests, lint, and audit green.
4. Git repository, versioned start/complete tags, and a clean-worktree matrix.
5. A release manifest that records those tags.

Until those exist, the manuscript may still be drafted after planning freeze; snapshot-tag gates remain unpublished, as with DevSecOps.
