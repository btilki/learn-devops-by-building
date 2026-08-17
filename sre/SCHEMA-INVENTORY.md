# Practical SRE Engineering — Shared Schema Inventory

**Status:** Frozen  
**Freeze date:** 2026-08-16  
**Schema location:** `books/labs/sre/northwind/schemas/`

## Runtime and dependency decision

- Supported interpreter: Python 3.13.
- Runtime libraries: PyYAML for YAML parsing and `jsonschema` for JSON Schema validation.
- Development tools: pytest and Ruff.
- Application frameworks, cloud SDKs, Kubernetes clients, telemetry backends, paging vendors, and incident-management APIs are excluded from the common dependency set.
- Exact package versions and hashes will be pinned when the lab is scaffolded.

## Schema design rules

- Use JSON Schema Draft 2020-12 for both YAML and JSON artifacts.
- Give every governed artifact `schema_version`, `kind`, and `id` fields unless it is an append-only event.
- Use stable identifiers for references; never join governed records by display name.
- Express timestamps as timezone-qualified RFC 3339 values.
- Express SLO windows and toil bounds in an explicitly documented format and test expiry and threshold boundaries.
- Require owners on decisions, exceptions, journeys, SLOs, rotations, incidents, learning actions, and fail-over plans.
- Keep observations, expectations, and decisions in separate artifacts.
- Schema validity proves structure only. Cross-reference, budget, freeze, page-path, isolation, and outcome evaluators own semantic claims.
- Version incompatible schema changes and provide an explicit migration or compatibility rule.
- Inherited identities are referenced, not copied: indicator IDs, catalog escalation contacts, fleet upgrade `storage-1-0-to-2-0`, DevOps incident-evidence fields, and Platform recovery limitations.

## Shared schemas

| Schema | First owner | Purpose | Primary consumers |
|---|---:|---|---|
| `artifact-envelope.schema.json` | 1 | Common identity, version, ownership, status, references, and review metadata | 1–14 |
| `owner.schema.json` | 1 | Stable team/role identity; `reliability-program` is the program owner | 1–14 |
| `reliability-brief.schema.json` | 1 | Protected journeys, promise, refusals, owners, and later proofs | 1–3, 8, 14 |
| `user-journey.schema.json` | 1 | User, failed outcome, owner, later proof; not a component or platform job | 1–5, 8–10, 14 |
| `reliability-refusal.schema.json` | 1 | Uptime theater and other measurements that must not count as success, with remaining owner | 1–3 |
| `sli-decision.schema.json` | 2 | Candidate indicator, treatment accept/adjacent/reject, journey, class, review | 2–5 |
| `slo.schema.json` | 3 | Journey, accepted SLI, window, target; SLA text is not a target field | 3–5, 8–10, 14 |
| `error-budget.schema.json` | 3 | Remaining unreliability computed from observations, not emitted by the catalog | 3–5, 9–10, 14 |
| `error-budget-policy.schema.json` | 4 | Continue/slow/freeze actions; fleet freeze **references** inherited upgrade ID and must not copy Platform freeze window, cohort, or rollback | 4–5, 10, 13 |
| `error-budget-exception.schema.json` | 4 | Owner, scope, remaining journey risk, expiry, removal path | 4, 10 |
| `burn-alert.schema.json` | 5 | Multi-window burn, page versus ticket versus record, minimum evidence volume | 5–6, 10 |
| `oncall-system.schema.json` | 6 | Rotation, load, handoff, authority; **references** catalog escalation ID and must not treat the contact as the system | 6, 10, 13 |
| `toil-bound.schema.json` | 7 | Definition, inventory classification, numeric bound, breach that blocks new critical SLO scope | 7, 11 |
| `dependency-contract.schema.json` | 8 | Provider, journey, criticality, timeout, fallback; a row cannot claim “no user impact” | 8–10, 13 |
| `degradation-policy.schema.json` | 9 | Shed/degrade mode, retry bound, cascade deny, burn accounting for degraded success | 9–10, 13 |
| `portfolio-incident.schema.json` | 10 | Commander, affected journeys, on-call systems, support kind, freeze join; one-path close is invalid | 10–11, 14 |
| `learning-action.schema.json` | 11 | Record or expiring waiver; action owner, due date, independent verification | 11, 13–14 |
| `regional-architecture.schema.json` | 12 | Regions, fail-over order, numeric portfolio RTO/RPO, data-gravity and isolation constraints; inherited restores listed as insufficient | 12–14 |
| `gameday-program.schema.json` | 13 | Cadence, abort, scenario coverage; a single mixed-backup result cannot complete the program | 13–14 |
| `portfolio-failover.schema.json` | 14 | Plan, trace, isolation, verification; mixed replay reject; **Evidence of portfolio recovery**; inherited restores insufficient | 14 |

## Non-schema semantic evaluators

These claims require code in addition to structural validation:

- reference resolution and ownership completeness;
- journey completeness against the reliability brief;
- SLI class enforcement: user-journey versus adjacent job-time versus rejected component uptime;
- remaining error budget computed from observations, not catalog self-emission;
- Fulfillment SLO not copied from Storefront;
- SLA text rejected as an SLO target;
- error-budget freeze of fleet change by inherited upgrade ID, distinct from a Platform upgrade freeze;
- journey burn pages versus symptom tickets;
- on-call rotation living-primary checks; Slack-as-primary denial;
- toil-bound breach blocking new critical SLO scope;
- dependency criticality: payment → Storefront, warehouse → Fulfillment, email non-critical;
- retry-amplification and cascade denial; degraded mode accounted as burn;
- portfolio incident close denied when only one journey is green;
- learning actions that cannot verify themselves;
- inherited restore identities listed as insufficient for regional loss;
- game-day coverage beyond one mixed-backup fixture; and
- mixed-tenant or mixed-region fail-over rejection, explicit continue/freeze, and verification that cannot emit `status: recovered` to hide missed RTO, missed RPO, or collapsed isolation.

## Versioning policy

Before the first lab release, schemas use version `1` and may change with the frozen plan. After release, an incompatible schema change requires a new schema version, migration instructions, updated fixtures, and a new lab release manifest.
