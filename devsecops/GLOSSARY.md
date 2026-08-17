# Glossary and Abbreviations

## Abbreviations

| Abbreviation and full form | Use in this book |
|---|---|
| **API (Application Programming Interface)** | A service or provider boundary invoked by software. |
| **CD (Continuous Delivery)** | Keeping a change deployable through an automated, controlled path. |
| **CI (Continuous Integration)** | Producing fast, trustworthy evidence about proposed source changes. |
| **CISA (Cybersecurity and Infrastructure Security Agency)** | The U.S. agency that maintains the known-exploited vulnerability catalog cited as exploitation intelligence. |
| **CVSS (Common Vulnerability Scoring System)** | A severity scoring framework; its Base score is not by itself a risk decision. |
| **GRC (Governance, Risk, and Compliance)** | Organizational processes for owned risk, control evidence, and obligations; a mapped obligation is not proof that a control works. |
| **IMDSv2 (Instance Metadata Service version 2)** | AWS instance-metadata access that requires a session-oriented request rather than an unauthenticated GET. |
| **KEV (Known Exploited Vulnerabilities)** | CISA's catalog of vulnerabilities with evidence of exploitation in the wild. |
| **NIST (National Institute of Standards and Technology)** | The U.S. standards body whose incident-response publication is cited for current risk-management framing. |
| **OIDC (OpenID Connect)** | Providing verifiable identity claims used by hosted builds or workload federation. |
| **SBOM (Software Bill of Materials)** | A structured inventory of components associated with an artifact. |
| **SLSA (Supply-chain Levels for Software Artifacts)** | A framework for reasoning about build provenance and platform assurance. |
| **SRE (Site Reliability Engineering)** | Reliability engineering through service objectives, operations, and learning. |
| **STRIDE (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege)** | A mnemonic threat catalog used as a prompt, not as proof of coverage. |

Chapter 0 writes **CI/CD (Continuous Integration and Continuous Delivery)** on first use for the combined delivery surface. Later chapters may use **CI** alone when they mean the integration system that stored or disclosed a secret.

## Production terms

**Asset**  
Something Northwind values because its compromise can cause a meaningful business, customer, security, or operational harm. Identity and authority can be assets; a credential is replaceable material that represents them.

**Assurance**  
A bounded conclusion drawn from current independent evidence that a control objective still holds. A green report is not assurance by itself.

**Attack path**  
Connected actions across real flows and trust boundaries that can progress a threat actor toward a named harm.

**Attestation**  
A signed statement about a subject. A valid signature authenticates the signer and unchanged claims; it does not automatically make the signer, builder, inputs, or target trusted.

**Blast radius**  
The identities, artifacts, data, environments, workloads, or authority exposed to a change, attack, or failure.

**Break-glass access**  
A predesigned emergency path that grants exceptional authority. It remains attributable, independently approved, time-bound, audited, and removed after review.

**Containment**  
Closing identified attacker access and execution paths while preserving evidence and required business state. Containment is not eradication or restored trust.

**Decision evidence**  
Proof that an owner evaluated required context and made a bounded decision, including uncertainty, rationale, owner, and review trigger.

**Detection hypothesis**  
A statement of which attack behavior should produce which evidence, within what window, with which context, and what response follows.

**Enforcement point**  
A boundary with the context and authority to allow, deny, transform, or observe a transition according to a named policy rule.

**Eradication**  
Removing modeled mechanisms that could restore attacker authority after containment, including credentials, caches, controllers, secrets, and other persistence paths.

**Exception**  
A bounded policy decision with owner, rationale, narrow scope, compensating controls, evidence, effective time, expiry, and removal path. It is not the absence of policy.

**Finding**  
A tool's claim that a weakness or vulnerability may exist. Findings inform risk decisions; they are not risk decisions.

**Harm**  
The adverse outcome if a security invariant is violated.

**Hermeticity**  
The property that declared inputs determine a build without undeclared network or host dependencies. Isolation bounds interference between builds; neither property implies the other.

**Inherent risk**  
The assessed risk of a path before the selected control portfolio.

**Mechanism evidence**  
Proof that a configured control or evaluator operated: a denial, admission, alert, hash, or other observation of the mechanism itself.

**Outcome evidence**  
Proof that the protected business or security outcome remains healthy, such as correct terminal order state or failed unauthorized payment effects.

**Persistence path**  
A credential, cache, controller, desired-state record, secret, startup mechanism, or other route that can recreate attacker capability after the visible workload is removed.

**Provenance**  
Evidence binding an artifact subject to build facts such as source, revision, builder, parameters, and build type.

**Reachability**  
Time-bound evidence that a particular version, configuration, and path can exercise a finding. Unreachable does not mean permanently harmless.

**Reconciliation**  
Observing disagreement among desired, recorded, external, and actual state—including order and payment effects—and applying or proposing a controlled transition.

**Recovery**  
Verified restoration of protected outcomes and required trust, not merely completion of a corrective action.

**Recovery evidence**  
Proof that harmful authority, persistence, and invalid trust were removed or replaced within the declared scope, that detections remain active, and that business outcomes recover.

**Red capability**  
A runnable checkpoint result proving that a production capability is absent or unsafe.

**Residual risk**  
What remains after existing and planned controls operate as expected. Residual risk is never automatically zero.

**Restored trust**  
A bounded evidence claim that inventoried roots and modeled descendants were replaced, old authority fails, trusted state is reconciled, detections remain active, and business outcomes recover. It is not a universal proof that no unmodeled persistence exists.

**Root of trust**  
The identities, keys, policy sources, and verification mechanisms whose correctness a trust decision depends on. Adding signatures expands the evidence graph; it does not eliminate roots.

**Secret**  
Material whose possession grants capability. An identity is an attributable subject with claims evaluated in context; possession of a secret often weakens that attribution.

**Security invariant**  
A required or prohibited outcome that should remain true across normal operation, change, attack, failure, containment, and recovery. Later controls, detections, and recovery evidence must preserve it.

**Threat**  
A circumstance or actor capability that could violate a security invariant.

**Trust boundary**  
A transition where the receiving side must decide whether to accept claims, data, identity, intent, or authority from a different trust context. It is not merely a network segment.

**Trust root**  
An input accepted without being derived again inside the current decision, such as reviewed source intent, identity policy, builder identity, signing authority, configuration identity, or durable business data.

**Vulnerability**  
A weakness that can be exercised under relevant conditions to violate a security property.

**Workload contract**  
Declared identity, artifact, process, privilege, filesystem, and network behavior expected for one workload.

**Workload identity**  
An attributable runtime subject exchanged for short-lived, audience-bound dependency access without distributing a reusable credential where federation is supported.
