# Glossary and Abbreviations

## Abbreviations

| Abbreviation and full form | Use in this book |
|---|---|
| **AI (Artificial Intelligence)** | A drafting aid whose output remains untrusted source until reviewed and verified by the delivery controls. |
| **API (Application Programming Interface)** | A service or provider boundary invoked by software. |
| **CD (Continuous Delivery)** | Keeping a change deployable through an automated, controlled path. |
| **CI (Continuous Integration)** | Producing fast, trustworthy evidence about proposed source changes. |
| **CIDR (Classless Inter-Domain Routing)** | Expressing an IP address range used by network configuration. |
| **DAG (Directed Acyclic Graph)** | Modeling pipeline jobs and dependencies to calculate the critical path. |
| **DNS (Domain Name System)** | Resolving service names and participating in recovery traffic transitions. |
| **HPA (Horizontal Pod Autoscaler)** | Adjusting Kubernetes replicas from observed metrics within declared bounds. |
| **HTTP (Hypertext Transfer Protocol)** | Carrying requests and trace context across service boundaries. |
| **IAM (Identity and Access Management)** | Defining which subjects can perform which actions. |
| **OIDC (OpenID Connect)** | Providing verifiable identity claims used by hosted builds or workload federation. |
| **PDB (PodDisruptionBudget)** | Constraining voluntary Kubernetes Pod evictions. |
| **PITR (Point-in-Time Recovery)** | Restoring a database to a selected point by replaying archived changes. |
| **RPO (Recovery Point Objective)** | Maximum acceptable gap between an incident and the latest recoverable state. |
| **RTO (Recovery Time Objective)** | Maximum acceptable elapsed time to restore the required outcome. |
| **S3 (Simple Storage Service)** | The Amazon object-storage service used in the Terraform backend example. |
| **SBOM (Software Bill of Materials)** | A structured inventory of components associated with an artifact. |
| **SEV-1 (Severity 1)** | Northwind's local classification for its highest-severity incident exercise. |
| **SHA-256 (Secure Hash Algorithm 256-bit)** | The digest algorithm used to detect changed fixture bytes. |
| **SLI (Service-Level Indicator)** | A measurement of a user-visible service outcome. |
| **SLO (Service-Level Objective)** | The acceptable target for an SLI over a defined window. |
| **SLSA (Supply-chain Levels for Software Artifacts)** | A framework for reasoning about build provenance and platform assurance. |
| **SPDX (Software Package Data Exchange)** | The SBOM document format used by the artifact exercise. |
| **SQS (Simple Queue Service)** | The Amazon queue service cited for at-least-once delivery behavior. |
| **SRE (Site Reliability Engineering)** | Reliability engineering through service objectives, operations, and learning. |
| **WAL (Write-Ahead Log)** | PostgreSQL change records replayed after a base backup. |
| **W3C (World Wide Web Consortium)** | The standards organization responsible for Trace Context. |

## Production terms

**Actual state**  
The observed state of a running system or external dependency, which may disagree with declared or recorded state.

**Artifact digest**  
A content-derived immutable identifier. A tag may move; a digest identifies specific bytes.

**Attestation**  
Authenticated evidence containing claims about an artifact or process. A valid signature authenticates the signer but does not automatically make the signer trusted for the claimed action.

**Blast radius**  
The users, workloads, data, environments, or authority exposed to a change or failure.

**Break-glass access**  
Exceptional emergency authority that should be attributable, time-bound, audited, and removed after reconciliation.

**Burn rate**  
The rate at which current failures consume the unreliability permitted by a service-level objective.

**Canary**  
A bounded production cohort exposed to a candidate release before wider progression.

**Change failure**  
A production change that degrades an intended outcome and requires mitigation, rollback, roll-forward, or another corrective transition.

**Critical path**  
The longest dependent sequence in a pipeline; it determines total execution time when independent work can run concurrently.

**Desired state**  
Reviewed intent describing what the system should become.

**Drift**  
Disagreement between declared, recorded, and observed infrastructure or workload state.

**Error budget**  
The amount of unreliability permitted by a service-level objective over its window.

**Idempotency**  
The property that repeated attempts for the same business intent converge on one intended effect.

**Inbox pattern**  
A durable consumer-side record that identifies processed operations and participates in the business transaction.

**Immutable artifact**  
A release subject promoted by content identity rather than rebuilt or selected through a mutable name.

**Mitigation**  
An action that reduces current harm. Mitigation is not equivalent to verified recovery.

**Outbox pattern**  
A durable event-publication intent committed in the same transaction as local business state and relayed afterward.

**Provenance**  
Evidence binding an artifact subject to build facts such as source, revision, builder, and build type.

**Reconciliation**  
Observing disagreement and applying or proposing a controlled transition toward selected intent.

**Recovery**  
The verified restoration of the critical production outcome, not merely completion of a corrective action.

**Recovery capacity**  
Capacity retained or obtainable to process accumulated work after disruption without overloading dependencies.

**Red capability**  
A runnable checkpoint result proving that a production capability is absent or unsafe.

**Stable artifact**  
The immutable release identity currently trusted to serve normal production traffic.

**Terminal state**  
A business state in which accepted work has completed successfully or reached an explicitly handled final failure without disappearing.

**Trust expectation**  
Independent policy describing which subject, source, builder, issuer, audience, or outcome is acceptable.

**Unit economics**  
Cost normalized by a useful, quality-gated production outcome rather than by raw requests or infrastructure quantity alone.

**Workload identity**  
An attributable runtime subject exchanged for short-lived, audience-bound dependency access without distributing a reusable credential where federation is supported.
