# Practical Platform Engineering — Shared Schema Inventory

**Status:** Frozen  
**Freeze date:** 2026-08-16  
**Schema location:** `books/labs/platform/northwind/schemas/`

## Runtime and dependency decision

- Supported interpreter: Python 3.13.
- Runtime libraries: PyYAML for YAML parsing and `jsonschema` for JSON Schema validation.
- Development tools: pytest and Ruff.
- Application frameworks, cloud SDKs, Kubernetes clients, portal products, and billing APIs are excluded from the common dependency set.
- Exact package versions and hashes will be pinned when the lab is scaffolded.

## Schema design rules

- Use JSON Schema Draft 2020-12 for both YAML and JSON artifacts.
- Give every governed artifact `schema_version`, `kind`, and `id` fields unless it is an append-only event.
- Use stable identifiers for references; never join governed records by display name.
- Express timestamps as timezone-qualified RFC 3339 values.
- Require owners on decisions, exceptions, tenants, catalog entries, contracts, and changes.
- Keep observations, expectations, and decisions in separate artifacts.
- Schema validity proves structure only. Cross-reference, temporal, isolation, and outcome evaluators own semantic claims.
- Version incompatible schema changes and provide an explicit migration or compatibility rule.

## Shared schemas

| Schema | First owner | Purpose | Primary consumers |
|---|---:|---|---|
| `artifact-envelope.schema.json` | 1 | Common identity, version, ownership, status, references, and review metadata | 1–14 |
| `owner.schema.json` | 1 | Stable team/role identity and escalation contact contract | 1–14 |
| `product-brief.schema.json` | 1 | Users, jobs, promise, non-goals, owners, and product evidence | 1–2, 10, 13 |
| `user-job.schema.json` | 1 | User, finished outcome, owner, and later proof | 1, 5, 10 |
| `intake-decision.schema.json` | 2 | Candidate, demand, isolation impact, productize/leave/decline, review | 2, 5–7, 12 |
| `tenant.schema.json` | 3 | Tenant identity, owner, isolation dimensions, prohibited roles | 3, 6, 8, 11, 14 |
| `isolation-boundary.schema.json` | 3 | Dimension, allowed sharing, denied inheritance, blast-radius statement | 3, 6, 8, 11, 14 |
| `catalog-system.schema.json` | 4 | System, owner, lifecycle, dependencies, freshness | 4, 12–13 |
| `paved-road-contract.schema.json` | 5 | Path steps, defaults, conformance, support level | 5, 9, 12 |
| `supported-exit.schema.json` | 5 | Owner, lost defaults, remaining guardrails, review date | 5, 9, 12 |
| `environment-lease.schema.json` | 6 | Tenant, request, TTL, quota, isolation evidence | 6, 11–12, 14 |
| `infrastructure-contract.schema.json` | 7 | Capability, version, tenant parameters, compatibility | 7–8, 12 |
| `control-plane-subject.schema.json` | 8 | Plane identity, tenant scope, prohibited cluster-admin, upgrade | 8, 12–14 |
| `reconciliation-result.schema.json` | 8 | Desired, actual, admission, tenant, last known good | 8, 12, 14 |
| `guardrail-default.schema.json` | 9 | Default, enforcement point, inherited policy reference, owner | 9, 12–13 |
| `exception-binding.schema.json` | 9 | Tenant, paved-road or exit, remaining isolation, scorecard effect, and **reference** to an inherited DevSecOps exception ID — not a copy of owner, scope, compensation, or expiry | 9, 12–13 |
| `devex-indicator.schema.json` | 10 | Job mapping, sample, non-metric flag, owner | 10–11, 13 |
| `quota-policy.schema.json` | 11 | Tenant floors, ceilings, unit, quality gate | 11–12, 14 |
| `fleet-change.schema.json` | 12 | Onboard, upgrade cohort, freeze, deprecation, rollback | 12–14 |
| `support-incident.schema.json` | 13 | Product versus tenant incident, escalation, change authority | 13–14 |
| `plane-recovery.schema.json` | 14 | Evidence identity, mixed-backup reject, tenant isolation, limitations | 14 |

## Non-schema semantic evaluators

These claims require code in addition to structural validation:

- reference resolution and ownership completeness;
- tenant isolation and prohibited role inheritance;
- catalog freshness and living-owner checks;
- paved-road conformance versus unofficial forks;
- environment TTL reclaim and cross-tenant deny;
- contract compatibility and breaking-change detection;
- control-plane self-approval denial and last-known-good retention;
- exception-binding resolution to an inherited DevSecOps exception ID, with scorecard failure on inherited expiry and no local copies of owner, scope, compensation, or expiry;
- vanity-metric rejection and missing-sample failure;
- quota floor/ceiling and starvation;
- fleet freeze, cohort, and deprecation windows;
- unofficial plane-admin change rejection; and
- mixed-backup restore rejection and bounded tenant continue/freeze.

## Versioning policy

Before the first lab release, schemas use version `1` and may change with the frozen plan. After release, an incompatible schema change requires a new schema version, migration instructions, updated fixtures, and a new lab release manifest.
