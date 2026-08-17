# Practical SRE Engineering — Companion Lab Plan

**Status:** Frozen  
**Freeze date:** 2026-08-16  
**Lab root:** `books/labs/sre/northwind/`  
**Depends on:** `BOOK-PLAN.md` and `CHAPTER-MAP.md`

## Lab promise

The companion lab makes Northwind's portfolio reliability decisions, SLOs, error-budget policy, on-call, toil bounds, dependency contracts, degradation, multi-service incidents, learning, game days, and regional fail-over inspectable and falsifiable without requiring a real telemetry backend, paging vendor, identity provider, multi-region fleet, or incident-management product.

It proves the behavior of the book's declared local models. It does not claim that a production vendor or environment enforces the same behavior.

## Inherited baseline decision

Use **minimal, checksum-identified interface baselines**, not full copies of earlier labs and not runtime dependencies on their working trees.

The SRE lab will contain:

```text
inherited/devops-v1.1/
inherited/devsecops-v1.0/
inherited/platform-v1.0/
```

`devops-v1.1` is the existing lab-snapshot identifier, not the published DevOps book version. Manifests will record source release, source path, source checksum, local fixture checksum, reduction notes, and consuming SRE chapters.

### DevOps baseline

Include only interfaces later reliability decisions consume:

- user-outcome telemetry: `order_success_ratio`, `order_latency`, and deployment identity;
- provisional single-service burn as a candidate input, not a finished portfolio alert;
- incident-role and one-path recovery-evidence shape (`desired_actual_agreement`, `healthy_consecutive_samples`, `terminal_order_outcomes`);
- reconstruction identity and traffic-return pair (`reconciled_business_state`, `verified_service_outcome`);
- release identity where error-budget policy must freeze a digest promotion.

### DevSecOps baseline

Include only interfaces later on-call authority and learning consume:

- authorization decision shape, including `self_approval_forbidden`;
- break-glass session shape: requester, independent approver, bounded action, expiry, after-action review;
- evidence-map shape where learning verification must remain independent of the record that claims it.

Do not inherit restored-trust claims, detection rules, or exception-owner fields as SRE recovery language.

### Platform baseline

Include only interfaces later portfolio governance consumes:

- product jobs `obtain-bounded-environment`, `ship-on-paved-road`, `publish-owned-path`;
- non-goal `portfolio-slo-governance` with remaining owner `reliability-program`;
- tenant identities `storefront` and `fulfillment` plus isolation invariants;
- catalog systems, living owners, and escalation contacts `storefront-oncall`, `fulfillment-oncall`, `platform-oncall`;
- platform-product SLIs `time-to-first-environment`, `paved-road-completion`, `catalog-freshness` and non-metrics including tenant-workload `order_success_ratio`;
- fleet upgrade `storage-1-0-to-2-0` freeze window, cohorts, and last known good `1.0`;
- support kinds `platform-product` versus `tenant-application`;
- plane last known good `1.0`, contract `tenant-storage` `1.0`, and recovery limitations `not-regional-loss`, `not-portfolio-rto`.

Reduced fixtures must be generated deliberately and reviewed. No test may read from `books/labs/devops/northwind/`, `books/labs/devsecops/northwind/`, or `books/labs/platform/northwind/` at runtime.

### Reference rules that prevent collapsed identities

- **Chapter 2 SLI decisions** reference inherited indicator IDs. They must not redefine `time-to-first-environment` as a portfolio SLI or leave `order_success_ratio` as a tenant-workload non-metric for the reliability program.
- **Chapter 4 error-budget freezes** of fleet change reference inherited upgrade ID `storage-1-0-to-2-0`. They add freeze reason, remaining budget, and owner. They must not copy freeze window, cohort, or rollback fields the Platform record already carries, and must not relabel a Platform upgrade freeze as an error-budget freeze.
- **Chapter 6 on-call systems** reference catalog escalation IDs. They add rotation, load, handoff, and authority. They must not treat the contact label as the system.
- **Chapter 10 incident traces** consume the inherited DevOps incident-evidence shape and Platform support kinds. Closing on `terminal_order_outcomes` or `order_success_ratio` alone cannot complete a portfolio incident.
- **Chapter 14 verification** references inherited traffic-return evidence and Platform limitations. It must record one-environment reconstruction and plane restore as insufficient. Verification cannot emit `status: recovered` to hide a missed portfolio RTO, missed RPO, or collapsed tenant isolation.

## Repository layout

```text
books/labs/sre/northwind/
├── Makefile
├── README.md
├── pyproject.toml
├── inherited/
│   ├── devops-v1.1/
│   ├── devsecops-v1.0/
│   └── platform-v1.0/
├── schemas/
├── reliability/             brief, journeys, refusals, owners
├── slis/                    method, candidates, decisions
├── slos/                    catalog, windows, budgets
├── policy/                  error-budget actions and exceptions
├── alerting/                burns, pages, tickets
├── oncall/                  system, rotations, handoffs, authority
├── toil/                    definition, inventory, bounds
├── dependencies/            catalog, criticality, contracts
├── degradation/             modes, shedding, cascade
├── incidents/               command, roles, traces
├── learning/                program, records, actions
├── regions/                 architecture, objectives, constraints
├── gamedays/                program, scenarios, results
├── failover/                plan, trace, isolation, verification
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
kind: reliability-decision
id: decision-example
owner: team-or-role
status: active
effective_at: 2026-08-16T00:00:00Z
review:
  trigger: material-change
  due_at: 2026-11-16T00:00:00Z
references: []
```

Schemas must validate syntax and required relationships. They must not pretend to validate whether a reliability judgment is wise.

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
- treat a dashboard, alert rule, paging vendor, postmortem template, or fail-over runbook as proof a user journey kept its SLO;
- treat schema validity as a correct SLI, SLO, or freeze decision;
- treat platform job-time as a portfolio SLO, or Storefront `order_success_ratio` as proof a platform job finished;
- treat a catalog escalation contact as an on-call system;
- treat a Platform upgrade freeze as an error-budget freeze;
- treat one-environment reconstruction, plane restore, or mixed-backup isolation as **Evidence of portfolio recovery**;
- treat DevSecOps restored trust as reliability recovery;
- treat an SLA sentence as an SLO target;
- silently substitute fixture truth for evidence a real reliability program would need to produce.

Recovery evidence for Chapter 14 is **Evidence of portfolio recovery**. It is not **Evidence of restored trust** and not **Evidence of bounded platform-product recovery**.

## Chapter state model

| State | Meaning |
|---|---|
| `start` | Cumulative prerequisites exist; the chapter capability is intentionally incomplete. |
| `baseline` | The evaluator runs successfully and proves the declared weakness is present. |
| `complete` | The chapter decision or implementation satisfies independent expectations. |
| `challenge` | A concept/decision scenario exposes incomplete reasoning or unsafe treatment. Correction is part of that write-up, not a separate lab state. |
| `failure` | An inert controlled input exercises burn, cascade, page-path, freeze, or regional-loss failure. |
| `contained` | Active modeled harm and change are bounded; portfolio health is not yet assumed recovered. |
| `recovered` | Required state is reconciled and journey plus portfolio-recovery evidence passes. |

Concept-led and decision-led chapters normally use `start → baseline → complete → challenge`. Correction happens **inside** the challenge write-up; there is no `corrected` state and no `make chapter-NN-corrected` target. Implementation-led and hybrid chapters that inject failure normally use `start → baseline → complete → failure → contained/recovered`. A hybrid chapter may also use `challenge` when the primary proof is a decision under failure rather than an injected runtime failure.

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
- No real credentials, cluster mutation, paging-vendor APIs, regional traffic shifts, or destructive external actions are included.
- Cross-tenant and cross-region access uses synthetic identifiers.
- Burn, overload, and cascade cases are numeric fixtures, not live load tests.
- Game days and fail-over mutate only generated lab state.
- Each failure command prints its scope and evidence paths before reporting success.

## Per-chapter feasibility and verification design

| Ch. | Local mechanism | What can be meaningfully verified | Required limitation |
|---:|---|---|---|
| 1 | Schema and relationship evaluator | Journeys, refusals, owners, and later proofs are complete and cross-referenced | Cannot prove the chosen journeys are the right journeys for a real company |
| 2 | SLI decision evaluator | Accept / adjacent / reject records join journeys; job-time stays adjacent; component uptime is rejected | Cannot assign an objectively correct indicator for a live user population |
| 3 | SLO and budget evaluator | Every journey has window, target, and computed remaining budget; Fulfillment is not a copy of Storefront; SLA text is not a target | Does not compute burn from a real telemetry backend |
| 4 | Error-budget policy evaluator | Continue / slow / freeze actions bind remaining budget; fleet upgrade is frozen by reference; Platform upgrade freeze is distinct | Does not halt a live release or fleet |
| 5 | Burn-alert evaluator | Journey burns page; CPU and replica Ready do not; platform job-time tickets the platform rotation | Does not send a real page |
| 6 | On-call system evaluator | Pages bind to living rotations; catalog contacts are referenced; Slack-as-primary fails; platform pages do not land on Storefront | Does not operate a real paging or calendar product |
| 7 | Toil bound evaluator | Inventory is classified; bound is numeric; a breach blocks a new critical SLO | Cannot measure real engineer hours |
| 8 | Dependency-contract evaluator | Payment burns Storefront; warehouse burns Fulfillment; email is non-critical; a row cannot emit “no user impact” | Does not query a real provider status page |
| 9 | Degradation and cascade evaluator | Shedding bounds retries; degraded mode is accounted as burn not success; Fulfillment is not paged as the cause of Storefront payment slowness | Does not inject live overload |
| 10 | Portfolio incident evaluator | Commander, journeys, rotations, and freeze join; Storefront green cannot close Fulfillment; one-path command fails | Does not run a real incident-management tool |
| 11 | Learning-program evaluator | Records or expiring waivers exist; actions have owner, due date, and independent verification; hortatory actions fail | Cannot prove an organization actually learned |
| 12 | Regional-architecture evaluator | Numeric portfolio RTO/RPO; isolation constraints; inherited restores listed as insufficient | Cannot discover unknown real data gravity |
| 13 | Game-day program evaluator | Cadence, abort, and coverage of freeze, page path, dependency loss, and regional loss; a single mixed-backup result cannot complete the program | Does not chaos-test a live fleet |
| 14 | Regional fail-over reconciler | Mixed-tenant/region replay rejected; continue/freeze is explicit; inherited restores insufficient; verification cannot self-emit recovered | Cannot prove a real multi-region fail-over; modeled **Evidence of portfolio recovery** only |

All chapters have a meaningful local proof target. The strongest epistemic limitation belongs to Chapter 14: modeled regional fail-over must never be phrased as proof that a production multi-region estate failed over.

## Chapter checkpoint ownership

Each `checkpoints/chapter-NN/` directory will contain:

- `README.md`: exact claim, inputs, outputs, limitations, and success meaning;
- `baseline.py`: verifies the expected red capability without treating red as command failure;
- `checkpoint.py`: verifies completed reliability, evidence, and outcome relationships;
- `expectations.yaml`: independent expectations not emitted by the mechanism under test;
- `cases/`: safe positive, negative, boundary, expiry, and mutation cases; and
- chapter-specific failure, containment, correction, or recovery drivers only when required.

Shared evaluators belong in `tools/`.

## Test strategy

- Schema tests for every governed kind.
- Evaluator tests for missing journeys, job-time promoted to portfolio SLO, copied Fulfillment targets, SLA-as-SLO, unfrozen exhausted budget, symptom paging, Slack-as-primary, unbounded toil, misclassified dependencies, retry cascade, one-path incident close, unverified learning actions, inherited restore claimed as regional recovery, single mixed-backup game day, and mixed-tenant fail-over.
- Mutation tests that flip one required field and expect checkpoint failure.
- No test may read earlier labs' working trees.
- Ruff and pytest on Python 3.13.

## Runtime and tools

- Supported interpreter: Python 3.13.
- Runtime libraries: PyYAML and `jsonschema`.
- Development tools: pytest and Ruff.
- Exact versions and hashes are pinned during scaffolding, not invented before verification.

## Planning freeze completed

Terminology, file paths, schema inventory, editorial conventions, and author review are complete. Exact inherited interface files and checksum manifests are generated during lab scaffolding, not before.

## Release gates before a companion-lab freeze

1. Planning freeze of this file with the rest of the planning set.
2. Scaffolded lab with inherited manifests and checksums.
3. Working-tree tests, lint, and audit green.
4. Git repository, versioned start/complete tags, and a clean-worktree matrix.
5. A release manifest that records those tags.

Until those exist, the manuscript may still be drafted after planning freeze; snapshot-tag gates remain unpublished, as with DevSecOps and Platform.
