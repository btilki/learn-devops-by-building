# Practical DevSecOps Engineering — Shared Schema Inventory

**Status:** Frozen design  
**Freeze date:** 2026-08-15  
**Schema location:** `books/practical-engineering/labs/devsecops/northwind/schemas/`

## Runtime and dependency decision

- Supported interpreter: Python 3.13.
- Runtime libraries: PyYAML for YAML parsing and `jsonschema` for JSON Schema validation.
- Development tools: pytest and Ruff.
- Application frameworks, cloud SDKs, policy-engine runtimes, Kubernetes clients, cryptographic toolkits, and telemetry backends are intentionally excluded from the common dependency set.
- Exact package versions and hashes will be pinned when the lab is scaffolded and verified on the supported interpreter.

This small dependency boundary keeps evaluators inspectable. Chapter-specific code should use the standard library unless a new dependency enables a production-relevant learning objective that cannot be represented clearly otherwise.

## Schema design rules

- Use JSON Schema Draft 2020-12 for both YAML and JSON artifacts.
- Give every governed artifact `schema_version`, `kind`, and `id` fields unless it is an append-only event.
- Use stable identifiers for references; never join governed records by display name.
- Express timestamps as timezone-qualified RFC 3339 values.
- Express durations in an explicitly documented format and test expiry boundaries.
- Require owners on decisions, exceptions, risks, assets, controls, and response actions.
- Keep observations, expectations, and decisions in separate artifacts.
- Schema validity proves structure only. Cross-reference, temporal, policy, and outcome evaluators own semantic claims.
- Version incompatible schema changes and provide an explicit migration or compatibility rule.

## Shared schemas

| Schema | First owner | Purpose | Primary consumers |
|---|---:|---|---|
| `artifact-envelope.schema.json` | 1 | Common identity, version, ownership, status, references, and review metadata | 1–16 |
| `owner.schema.json` | 1 | Stable team/role identity and escalation contact contract | 1–16 |
| `asset.schema.json` | 1 | Asset, business use, sensitivity, harms, dependencies, and owner | 1–3, 8–10, 14–16 |
| `security-invariant.schema.json` | 1 | Required or prohibited outcome tied to assets and harms | 1–3, 6–16 |
| `trust-boundary.schema.json` | 2 | Boundary, entering claims/data, validator, assumptions, and owner | 2, 4–7, 9–15 |
| `attack-path.schema.json` | 2 | Actor capability, prerequisites, steps, boundaries, target invariant, controls, and uncertainty | 2–3, 6–16 |
| `risk-decision.schema.json` | 3 | Context, exposure, likelihood, impact, uncertainty, treatment, residual risk, owner, and review | 3, 8, 11, 16 |
| `control.schema.json` | 3 | Control objective, type, target threats, enforcement, evidence, owner, and limitations | 3–16 |
| `authorization-decision.schema.json` | 4 | Subject, action, resource, context, claims, policy identity, result, and reason | 4–5, 9–15 |
| `privilege-request.schema.json` | 5 | Requester, approver, purpose, scope, duration, compensation, revocation, and review | 5, 14–16 |
| `supply-chain-evidence.schema.json` | 6 | Source, dependency, builder, artifact, attestation, approval, and admission identities | 6–8, 11–15 |
| `finding.schema.json` | 8 | Normalized vulnerability identity, affected component, source evidence, and confidence | 8, 11, 16 |
| `exception.schema.json` | 8 | Bounded deviation, rationale, owner, compensation, evidence, expiry, and removal path | 8, 11, 16 |
| `secret-record.schema.json` | 9 | Secret purpose, custodian, consumers, storage, issue/rotate/revoke state, and exceptions | 9, 13–16 |
| `data-class.schema.json` | 10 | Data element, sensitivity, purpose, permitted uses, stores, retention, and deletion contract | 10, 14–16 |
| `policy-decision.schema.json` | 11 | Enforcement point, input identity, policy version, result, reason, and exception reference | 11–16 |
| `security-event.schema.json` | 12 | Time, source, subject, action, resource, outcome, correlation, deployment, evidence integrity, and sensitivity | 12–16 |
| `detection-hypothesis.schema.json` | 13 | Threat hypothesis, required events, correlation, threshold, expected context, owner, and response | 13–16 |
| `evidence-item.schema.json` | 13 | Evidence category, producer, subject, collection time, integrity, provenance, retention, and limitations | 13–16 |
| `response-action.schema.json` | 14 | Hypothesis, scope, authority, action, expected effect, business constraint, evidence, and status | 14–16 |
| `trust-root.schema.json` | 15 | Trust material, dependents, validity, invalidation reason, replacement, and verification | 15–16 |
| `recovery-verification.schema.json` | 15 | Invalid authority rejection, rebuilt chain, reconciled state, monitoring, business outcome, and limitations | 15–16 |
| `assurance-claim.schema.json` | 16 | Objective, implementation, independent evidence, exceptions, limitations, review, and improvement | 16 |

## Non-schema semantic evaluators

These claims require code in addition to structural validation:

- reference resolution and ownership completeness;
- graph reachability across assets, boundaries, attack paths, controls, and trust roots;
- issuer, audience, subject, action, resource, and context authorization;
- time windows, expiry, rotation overlap, evidence freshness, and event ordering;
- independent approval and separation of duties;
- source, dependency, builder, artifact, and deployment identity binding;
- finding correlation and treatment deadlines;
- field/purpose access and lifecycle reconciliation;
- exception scope containment and compensation;
- event normalization, correlation, and missing-telemetry detection;
- evidence hashing and fact-versus-inference separation;
- containment state and invalidated-authority rejection;
- trust-root replacement and descendant reconciliation; and
- assurance failure when evidence, ownership, review, or exception state is invalid.

## Versioning policy

Before the first lab release, schemas use version `1` and may change with the frozen plan. After release, an incompatible schema change requires a new schema version, migration instructions, updated fixtures, and a new lab release manifest. Old versioned tags remain bound to their original schemas.
