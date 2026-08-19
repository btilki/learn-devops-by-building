# Practical DevSecOps Engineering — Chapter Map

**Status:** Frozen  
**Freeze date:** 2026-08-15  
**Depends on:** `BOOK-PLAN.md`  
**Drafting gate:** Chapter drafting must conform to this frozen map or use an explicitly versioned plan revision.

## Cumulative state contract

Each chapter inherits the completed security state of the previous chapter. Concept- and decision-led chapters change Northwind's reviewed security model and authority contract; implementation-led chapters change enforceable behavior. Later implementation must consume earlier decisions rather than silently replacing them.

Each chapter must distinguish:

- **mechanism evidence:** proof that a configured control operated;
- **decision evidence:** proof that an owner evaluated relevant context and made a bounded decision;
- **outcome evidence:** proof that the protected business or security outcome remains healthy; and
- **recovery evidence:** proof that harmful authority, persistence, and invalid trust were removed—not merely that service returned.

Attack and failure exercises use three explicit relationships to the book's main storyline:

- **Cumulative attack:** advances the compromised-maintainer intrusion.
- **Connected consequence:** demonstrates harm enabled by that intrusion path.
- **Independent control failure:** proves that the control matters even without the cumulative attacker.

## Chapter 1 — Define What Security Must Protect

- **Form:** Concept-led
- **Production question:** What must Northwind protect, from which harms, and who owns each decision?
- **Start:** DevOps capabilities protect the order outcome, but security assets, sensitive data, privileged identities, harms, dependencies, and owners are implicit.
- **Pressure:** Teams collect findings and add controls without agreement about the outcome or asset being protected.
- **Concepts:** assets versus resources; business harm; confidentiality, integrity, and availability; safety and fraud impacts; data and identity as assets; ownership; security invariants.
- **Decision/capability:** Define Northwind's security outcome, crown-jewel assets, plausible harms, invariants, and accountable owners.
- **Lab artifacts:** `security-model/assets.yaml`, `security-model/invariants.yaml`, `security-model/ownership.yaml`, representative order/data-flow inventory.
- **Evidence:** Completeness and ownership checks; traceability from each invariant to an asset, harm, and owner.
- **Durable outputs:** Asset-and-harm register; security invariants.
- **Independent control failure:** A payment token is classified as merely an application configuration value, leaving its misuse and owner undefined.
- **Correction:** Reclassify it as sensitive authority-bearing data, assign ownership, and define prohibited and required outcomes.
- **Next:** Northwind knows what matters but not where trust is granted or how an attacker can cross those boundaries.

## Chapter 2 — Model Threats Across Trust Boundaries

- **Form:** Concept-led
- **Production question:** How can plausible actors violate Northwind's security invariants across its real trust boundaries?
- **Start:** Assets and harms are owned; system diagrams still describe connectivity rather than trust transitions.
- **Pressure:** Generic threat lists overstate unlikely attacks and miss abuse paths created by identities, automation, and third parties.
- **Concepts:** threat actor, capability, intent, precondition, attack path, abuse case, trust boundary, entry point, control assumption, residual uncertainty; limits of mnemonic threat catalogs.
- **Decision/capability:** Create a data-and-authority-flow threat model that prioritizes plausible paths to the critical assets.
- **Lab artifacts:** `threat-model/system.yaml`, `threat-model/boundaries.yaml`, `threat-model/attack-paths.yaml`, generated review report.
- **Evidence:** Every priority path names actor capability, prerequisite, boundary crossed, threatened invariant, existing controls, missing evidence, and owner.
- **Durable outputs:** Reviewed threat model; prioritized attack-path register.
- **Cumulative attack:** A compromised maintainer credential can approve a dependency change, trigger automation, and seek production authority through several implicit trust transitions.
- **Correction:** Decompose the path, expose assumptions, and identify where prevention and detection can independently interrupt it.
- **Next:** Threat paths exist, but Northwind needs a disciplined way to decide which risks merit which controls.

## Chapter 3 — Turn Risk into Owned Control Decisions

- **Form:** Decision-led
- **Production question:** Which threat paths require treatment now, and what constitutes a proportionate control?
- **Start:** Threats are modeled, but severity, urgency, uncertainty, cost, and ownership are not reconciled into decisions.
- **Pressure:** Numeric precision and scanner severity create false confidence while business impact and exposure remain unstated.
- **Concepts:** likelihood, impact, exposure, uncertainty, inherent and residual risk, prevention/detection/recovery portfolios, treatment choices, risk acceptance, review triggers.
- **Decision/capability:** Adopt a qualitative, evidence-backed risk method and select complementary controls for priority paths.
- **Lab artifacts:** `risk/risk-register.yaml`, `risk/control-decisions.yaml`, `risk/method.md`, decision evaluator.
- **Evidence:** Each decision traces to threats and invariants, records uncertainty, owner, treatment, rationale, due date, residual risk, and review trigger.
- **Durable outputs:** Risk method; owned control decision record.
- **Independent control failure:** A critical label forces emergency remediation despite no production reachability, while an exposed high-impact authorization path waits.
- **Correction:** Re-evaluate both using exposure, exploitability, harm, and uncertainty; preserve the reasoning.
- **Next:** The highest-priority attack paths begin with ambiguous human and automation authority.

## Chapter 4 — Make Human and Automation Access Attributable

- **Form:** Implementation-led
- **Production question:** How does Northwind ensure every security-relevant action has a verified subject and bounded authorization?
- **Start:** Shared accounts, long-lived automation tokens, inconsistent federation, and role accumulation obscure who or what acted.
- **Pressure:** Authentication success is mistaken for authorization, and attribution disappears behind shared automation.
- **Concepts:** authentication, authorization, subject, principal, claim, session, federation, service identity, role and attribute policy, least authority, separation of duties.
- **Decision/capability:** Establish individual human identities, workload/automation federation, bounded roles, protected production authorization, and attributable audit events.
- **Lab artifacts:** `identity/subjects.yaml`, `identity/roles.yaml`, `identity/trust-policy.yaml`, `identity/access-events.jsonl`, authorization evaluator.
- **Evidence:** Allowed and denied decision traces bind subject, action, resource, context, issuer, audience, expiry, policy version, and result.
- **Durable outputs:** Identity inventory; authorization matrix.
- **Cumulative attack:** The compromised maintainer credential attempts to use a reusable CI token and an inherited production role.
- **Containment/recovery:** Reject the wrong audience and excess privilege, revoke the session and binding, remove inherited access, issue bounded identity, and prove legitimate automation still works.
- **Next:** Normal identities are attributable, but exceptional delegation and emergency privilege remain dangerous.

## Chapter 5 — Govern Delegation and Privileged Operations

- **Form:** Decision-led
- **Production question:** How should Northwind grant temporary elevated authority without creating an unowned bypass?
- **Start:** Roles are bounded, but support access, approval delegation, emergency access, and machine impersonation lack a coherent contract.
- **Pressure:** Permanent privilege is convenient; emergency procedures are either unusable or unaudited.
- **Concepts:** delegation chain, impersonation, just-in-time access, just-enough administration, dual control, break glass, time and scope bounds, revocation, session evidence.
- **Decision/capability:** Define privileged workflows with explicit requester, approver, subject, purpose, scope, duration, evidence, revocation, and after-action review.
- **Lab artifacts:** `privilege/policy.yaml`, `privilege/requests/`, `privilege/sessions.jsonl`, `privilege/break-glass-runbook.md`.
- **Evidence:** Evaluator rejects self-approval, unbounded duration, missing reason, excessive scope, and absent post-use review.
- **Durable outputs:** Privileged-access decision record; break-glass mini-runbook.
- **Cumulative attack:** The compromised maintainer attempts self-approved production elevation under an invented emergency.
- **Containment/recovery:** Deny elevation, alert on the attempt, revoke the initiating session, preserve evidence, and verify a legitimate emergency path remains available.
- **Next:** Identity paths are bounded; source and dependency inputs can still introduce attacker-controlled code.

## Chapter 6 — Establish Trust in Source and Dependencies

- **Form:** Implementation-led
- **Production question:** Which source and dependency inputs may enter Northwind's build, under whose approval and evidence?
- **Start:** Git review exists and an SBOM can be produced, but maintainer trust, branch rules, dependency origins, update authority, lock integrity, and ownership are incomplete.
- **Pressure:** A valid credential and ordinary dependency update can satisfy superficial review while introducing malicious code.
- **Concepts:** source authenticity, review independence, protected refs, dependency confusion, typosquatting, namespace and registry trust, lockfiles, vendoring, update automation, ownership and provenance.
- **Decision/capability:** Enforce trusted sources, independent approval for sensitive paths, pinned dependency resolution, approved registries, and attributable update automation.
- **Lab artifacts:** `supply-chain/source-policy.yaml`, `supply-chain/dependency-policy.yaml`, lockfiles, ownership rules, dependency resolution evidence.
- **Evidence:** Source/dependency verifier independently reconstructs origin, revision, approvers, resolved versions, hashes, registry, and policy result.
- **Durable outputs:** Source trust policy; dependency admission policy.
- **Cumulative attack:** A compromised maintainer adds a look-alike payment package from an unapproved registry.
- **Containment/recovery:** Block resolution/admission, quarantine the change, revoke the credential, verify the approved dependency graph, and retain the attempt for detection work.
- **Next:** Trusted inputs are defined, but the build and release path must preserve that trust end to end.

## Chapter 7 — Enforce a Verifiable Build and Release Chain

- **Form:** Implementation-led
- **Production question:** How can Northwind admit only artifacts built from trusted inputs by bounded builders and released under reviewed policy?
- **Start:** Artifacts have digests, SBOMs, and provenance, but admission does not evaluate complete trust policy or builder isolation.
- **Pressure:** Signed evidence can be valid yet describe an unauthorized source, vulnerable builder, unexpected dependency set, or unapproved release.
- **Concepts:** attestation semantics, root of trust, builder identity, hermeticity and isolation, provenance levels, signing versus trust, transparency, admission, trust rotation.
- **Decision/capability:** Verify source, dependencies, builder, parameters, artifact, attestations, approval, and target environment at release admission.
- **Lab artifacts:** `supply-chain/build-policy.yaml`, `supply-chain/admission-policy.yaml`, provenance/SBOM fixtures, transparency records, admission evaluator.
- **Evidence:** Independent admission decision with verified subjects, claims, policy version, missing/failed conditions, and deployment result.
- **Durable outputs:** Release trust policy; admission evidence record.
- **Cumulative attack:** A correctly signed artifact originates from an untrusted builder after build-token misuse.
- **Containment/recovery:** Reject admission, revoke builder trust, rotate affected trust material, rebuild on an approved builder, and verify the deployed digest and full chain.
- **Next:** The chain is trustworthy, but vulnerability findings still overwhelm remediation decisions.

## Chapter 8 — Prioritize Vulnerabilities by Exploitability and Harm

- **Form:** Decision-led
- **Production question:** Which vulnerabilities must Northwind remediate, mitigate, accept, or monitor first?
- **Start:** Multiple scanners produce inconsistent findings and severity labels without runtime reachability, exposure, asset harm, or ownership.
- **Pressure:** Teams chase counts and critical scores while exploitable paths and aging accepted risks receive insufficient attention.
- **Concepts:** weakness versus vulnerability; severity; exploitability; exposure; reachability; known exploitation; affected configuration; compensating control; remediation and risk-acceptance windows.
- **Decision/capability:** Correlate and deduplicate findings, add production context, assign owners, and make time-bounded treatment decisions.
- **Lab artifacts:** `vulnerabilities/findings/`, `vulnerabilities/context.yaml`, `vulnerabilities/decisions.yaml`, triage evaluator.
- **Evidence:** Decision trace records affected asset, deployed version, reachability, exposure, exploitation evidence, harm, treatment, deadline, exception, and verification.
- **Durable outputs:** Prioritized remediation queue; vulnerability exception record.
- **Independent control failure:** A critical unreachable library competes with a high-severity internet-reachable flaw on the order path.
- **Correction:** Prioritize through explicit context without declaring unreachable equal to harmless; define monitoring and review triggers.
- **Next:** Vulnerability risk is owned; reusable secrets can still collapse otherwise bounded identity and supply-chain controls.

## Chapter 9 — Govern Secrets Through Their Complete Lifecycle

- **Form:** Implementation-led
- **Production question:** How does Northwind prevent, detect, and recover from secret exposure across creation, storage, distribution, use, rotation, and retirement?
- **Start:** Workload federation replaced some static secrets, but provider credentials, signing material, developer tokens, backups, logs, and historical repository content lack unified governance.
- **Pressure:** Secret scanning finds strings, while unknown ownership and incomplete revocation make exposure response unreliable.
- **Concepts:** secret versus identity; generation; custody; envelope encryption; distribution; dynamic credentials; rotation; revocation; version overlap; exposure evidence; secret zero.
- **Decision/capability:** Inventory unavoidable secrets, eliminate unnecessary ones, enforce approved custody/use, detect exposure, rotate safely, and verify revocation.
- **Lab artifacts:** `secrets/inventory.yaml`, `secrets/policy.yaml`, reference manifests, exposure fixtures, rotation/revocation evidence.
- **Evidence:** No plaintext in governed paths; use is attributable; rotations preserve service; revoked material fails; exception inventory is complete.
- **Durable outputs:** Secret inventory; rotation and exposure-response runbook.
- **Connected consequence:** A brokered payment credential appears in CI logs and is replayed through the compromised-maintainer path.
- **Containment/recovery:** Mask further exposure, revoke and rotate, reconcile provider and application use, inspect historical access, replace derived credentials, and prove replay rejection plus healthy payment outcomes.
- **Next:** Authority-bearing secrets are governed; customer and operational data need use-based protection and lifecycle decisions.

## Chapter 10 — Protect Data According to Its Use and Sensitivity

- **Form:** Hybrid
- **Production question:** What data may Northwind collect, expose, transform, retain, and delete, and which controls follow from those uses?
- **Start:** PostgreSQL and telemetry are recoverable, but data classification, minimization, field access, retention, deletion, non-production use, and evidence are inconsistent.
- **Pressure:** Blanket encryption is treated as complete protection while excessive collection and authorized overexposure remain.
- **Concepts:** classification, purpose, minimization, data flow, access need, encryption context, tokenization, masking, retention, deletion, backup implications, lineage.
- **Decision/capability:** Classify Northwind data, map permitted uses, minimize collection, enforce field/purpose boundaries, and reconcile retention and deletion across primary, telemetry, and backup stores.
- **Lab artifacts:** `data-security/classification.yaml`, `data-security/uses.yaml`, `data-security/access-policy.yaml`, `data-security/retention.yaml`, sanitized fixtures.
- **Evidence:** Access decisions and lifecycle reports trace data class, purpose, subject, store, retention, deletion status, and exceptions.
- **Durable outputs:** Data classification/use register; retention and deletion contract.
- **Connected consequence:** The malicious dependency causes notification-service to request unnecessary payment-related fields and emit sensitive order data into logs and a non-production fixture.
- **Containment/recovery:** Deny unnecessary access, quarantine data, purge governed copies, rotate exposed authority where relevant, validate sanitized replacements, and document backup expiry constraints.
- **Next:** Individual domains have controls, but Northwind needs consistent policy placement and governed exceptions.

## Chapter 11 — Enforce Security Policy Without Hiding Exceptions

- **Form:** Hybrid
- **Production question:** Where should Northwind enforce security decisions, and how can exceptions remain bounded and visible?
- **Start:** Identity, supply-chain, vulnerability, secret, and data policies exist in separate formats with inconsistent enforcement and waiver behavior.
- **Pressure:** Central policy becomes detached from system context; local policy can be bypassed; permanent exceptions normalize drift.
- **Concepts:** policy intent, rule, enforcement point, admission versus detection, fail-open/fail-closed, policy versioning, decision logging, exception lifecycle, compensating control, policy ownership.
- **Decision/capability:** Place enforcement at explicit boundaries, test policy behavior, and govern exceptions with scope, owner, rationale, compensation, evidence, expiry, and review.
- **Lab artifacts:** `policy/bundle/`, `policy/tests/`, `policy/exceptions.yaml`, `policy/enforcement-points.yaml`, conformance evaluator.
- **Evidence:** Consistent decisions across declared enforcement points; mutation tests prove unsafe cases fail; expired or widened exceptions are rejected.
- **Durable outputs:** Enforcement-point map; exception register.
- **Independent control failure:** Release pressure produces a broad, non-expiring bypass that disables dependency and admission checks, demonstrating how organizational behavior can reopen the attack path without direct attacker action.
- **Containment/recovery:** Reject or narrowly reissue the exception, apply compensating detection, expire it automatically, remove bypass state, and verify normal enforcement resumes.
- **Next:** Policy governs expected transitions; a workload that reaches runtime can still abuse kernel, network, identity, or application behavior.

## Chapter 12 — Constrain Workloads and Detect Runtime Abuse

- **Form:** Implementation-led
- **Production question:** How can Northwind bound a compromised workload and observe behavior that violates its runtime contract?
- **Start:** Kubernetes security contexts and network boundaries exist, but threat-driven runtime confinement, egress control, sensitive system-call policy, identity-use expectations, and response evidence are incomplete.
- **Pressure:** A healthy, policy-admitted container can still execute malicious behavior after startup.
- **Concepts:** defense in depth, workload attack surface, sandbox boundary, capability, syscall, filesystem and process behavior, egress, runtime baseline, behavioral detection, evasion and false positives.
- **Decision/capability:** Define and enforce workload-specific runtime contracts, then detect meaningful violations independently.
- **Lab artifacts:** `runtime/contracts/`, `runtime/policies/`, `runtime/events.jsonl`, attack simulator, behavior evaluator.
- **Evidence:** Expected application behavior remains functional; prohibited privilege, filesystem, process, identity, and egress actions are blocked or detected with attributable context.
- **Durable outputs:** Runtime security contract; containment mini-runbook.
- **Cumulative attack:** The malicious dependency attempts credential discovery, shell execution, and outbound command-and-control traffic.
- **Containment/recovery:** Bound execution and egress, isolate the workload, preserve evidence, revoke its identity, replace the artifact, and verify no related behavior persists.
- **Next:** Runtime events exist; Northwind must turn cross-system security evidence into actionable detections.

## Chapter 13 — Build Security Evidence and Actionable Detections

- **Form:** Implementation-led
- **Production question:** Which evidence can reveal priority attack paths early enough for a specific response?
- **Start:** The DevOps observability contract already provides structured events, trace correlation, and deployment identity. Audit, admission, secret, data, and runtime security events exist, but their coverage, integrity, normalization, retention, hypotheses, thresholds, and response ownership are fragmented.
- **Pressure:** Alert volume measures tool activity, not detection of meaningful misuse; missing telemetry is silently interpreted as safety.
- **Concepts:** detection hypothesis, signal and evidence, attack-path coverage, telemetry integrity, normalization, correlation, baseline, threshold, false positive/negative, alert routing, evidence retention.
- **Decision/capability:** Extend the inherited DevOps telemetry contract with security event semantics, build detections from threat hypotheses, validate them with controlled simulations, and route them to owned response actions. Do not create a parallel security-only telemetry stack.
- **Lab artifacts:** inherited `observability/contract.json` interface fixture, `detection/event-contract.yaml`, `detection/hypotheses.yaml`, `detection/rules/`, normalized event fixtures, simulation cases, coverage report.
- **Evidence:** Each priority path maps to prevention and/or detection; simulations measure expected alerts, context, timing, owner, and response action; missing telemetry alarms independently.
- **Durable outputs:** Detection catalog; attack-path coverage report.
- **Cumulative attack:** Credential misuse, unusual dependency change, denied elevation, and runtime egress form one correlated intrusion path.
- **Containment/recovery:** Validate the alert chain, correct missing/ambiguous context, bound noisy rules without suppressing the path, and prove the controlled attack is detected.
- **Next:** Northwind can raise an evidence-rich signal; responders must investigate and contain without destroying evidence or widening harm.

## Chapter 14 — Investigate and Contain a Production Compromise

- **Form:** Implementation-led
- **Production question:** How does Northwind establish what happened and stop ongoing harm while preserving trustworthy evidence?
- **Start:** A correlated detection identifies the compromised maintainer path, but scope, evidence custody, identity containment, workload isolation, and business continuity choices are unresolved.
- **Pressure:** Fast destructive action can erase evidence; slow investigation leaves attacker authority active.
- **Concepts:** incident hypothesis, timeline, scope, evidence provenance and integrity, volatile evidence, containment strategy, attacker access versus persistence, communication and legal escalation boundaries.
- **Decision/capability:** Preserve an attributable evidence set, test hypotheses, bound the affected identities/artifacts/workloads/data, and execute staged containment.
- **Lab artifacts:** `response/case/`, `response/timeline.jsonl`, `response/evidence-manifest.yaml`, `response/containment-plan.yaml`, investigation evaluator.
- **Evidence:** Hashes and provenance protect collected evidence; claims separate facts from inference; containment closes identified authority while the critical business outcome is monitored.
- **Durable outputs:** Investigation timeline; containment decision record.
- **Cumulative attack:** The attacker retains a maintainer session, compromised builder path, malicious artifact, and workload foothold while some orders remain in flight.
- **Containment/recovery:** Revoke active authority, freeze affected release paths, isolate compromised workloads, preserve queue/database state, maintain bounded service where defensible, and verify no new attacker action succeeds.
- **Next:** Active harm is contained, but compromised trust roots and persistence must be removed before normal operation resumes.

## Chapter 15 — Eradicate Persistence and Restore Trust

- **Form:** Implementation-led
- **Production question:** How can Northwind prove that attacker capability and persistence are gone and production is trustworthy again?
- **Start:** The intrusion is contained; identities, build infrastructure, artifacts, secrets, workloads, and evidence have varying levels of trust.
- **Pressure:** Restoring availability from possibly compromised state can reintroduce the attacker and invalidate all later evidence.
- **Concepts:** eradication, persistence, trust root, credential and key hierarchy, clean-room rebuild, known-good state, scope of rotation, state reconciliation, recovery criteria, heightened monitoring.
- **Decision/capability:** Establish trusted recovery roots, replace invalidated identity and secret material, rebuild affected artifacts and workloads, reconcile durable state, and validate security plus business outcomes.
- **Lab artifacts:** `recovery/trust-inventory.yaml`, `recovery/eradication-plan.yaml`, `recovery/rebuild-manifest.yaml`, `recovery/verification.yaml`, controlled recovery evaluator.
- **Evidence:** Old credentials and artifacts fail; trusted source-to-runtime chain is rebuilt; unauthorized persistence is absent within stated evidence limits; orders reconcile; detections remain active through recovery.
- **Durable outputs:** Eradication and trust-restoration plan; verified recovery report.
- **Cumulative attack:** A forgotten automation credential or unreviewed image cache attempts to restore the malicious artifact after service return.
- **Containment/recovery:** Keep reconciliation paused, revoke the missed path, invalidate caches, rebuild again from trusted inputs, then prove sustained security and business health across consecutive evidence windows.
- **Next:** Northwind can restore trust after one compromise; its operational evidence must now support durable governance and improvement.

## Chapter 16 — Turn Operational Evidence into Sustainable Governance

- **Form:** Decision-led
- **Production question:** How can Northwind govern controls over time without replacing risk reasoning with compliance ceremony?
- **Start:** Security controls and evidence work for the cumulative scenario, but ownership cadence, obligation mapping, evidence retention, drift review, exception aging, and improvement are not systematic.
- **Pressure:** Point-in-time audits reward screenshots and passing controls while threats, systems, owners, and exceptions change.
- **Concepts:** governance, obligation, control objective, control implementation, evidence, assurance, auditability, continuous monitoring, ownership, review cadence, control effectiveness, material change.
- **Decision/capability:** Map operational controls and evidence to owned objectives, define review triggers and retention, test effectiveness, and feed incidents and exceptions back into threat and risk decisions.
- **Lab artifacts:** `governance/control-catalog.yaml`, `governance/evidence-map.yaml`, `governance/review-calendar.yaml`, `governance/assurance-report.yaml`.
- **Evidence:** Every claimed objective maps to a real owner, implementation, independent evidence, limitation, review trigger, exception state, and improvement action.
- **Durable outputs:** Control-and-evidence catalog; security improvement backlog.
- **Independent control failure:** A compliance report remains green despite an expired exception, missing detection telemetry, and a changed attack path.
- **Correction:** Fail assurance, reopen the affected risk decisions, restore evidence, and record control redesign rather than editing the report alone.
- **Next:** The conclusion assembles assets, threats, authority, trust, policy, detection, response, recovery, and governance into one defensible production security system.

## Cross-chapter coverage audit

| Required concept area | Primary chapters | Later proof |
|---|---|---|
| Threat modeling and trust boundaries | 1–2 | 6–7, 12–15 |
| Risk, likelihood, impact, control selection | 3 | 8, 11, 16 |
| Authentication, authorization, identity, delegation | 4–5 | 9, 14–15 |
| Data classification and ownership | 1, 10 | 14–16 |
| Software supply-chain trust | 6–7 | 12–15 |
| Vulnerability prioritization | 8 | 11, 16 |
| Secret governance and exposure recovery | 9 | 13–16 |
| Policy, enforcement, exceptions, evidence | 11 | 12–16 |
| Runtime confinement and abuse prevention | 12 | 14–15 |
| Detection versus prevention | 2–3, 12–13 | 14–15 |
| Containment, eradication, recovery | 14–15 | 16 |
| Governance, compliance, audit evidence | 16 | Conclusion |

## Companion-lab design constraints

- The lab root will be `books/practical-engineering/labs/devsecops/northwind/`; it must not mutate `books/practical-engineering/labs/devops/northwind/`.
- Inherited DevOps capabilities must enter through documented fixture contracts or a deliberate copied baseline, never through an implicit dependency on a mutable working tree.
- Every evaluator must separate observations from expectations and must fail when required evidence is absent.
- Concept-led artifacts require schema and cross-reference validation, not a fake command that claims to validate judgment itself.
- Attack simulations must be deterministic, local, non-destructive, and clearly labeled as simulations.
- A successful simulation proves the modeled decision logic only; it does not claim that a real repository, identity provider, registry, cloud, cluster, endpoint, or adversary was tested.
- Attack fixtures must not contain functioning malware, real credentials, or instructions whose value depends on harming an external system.
- Chapter snapshots should preserve red baseline, green capability, attack or decision challenge, and corrected/recovered evidence where the chapter form supports those states.

## Pre-freeze resolutions

1. Shared schemas and first-use ownership are defined in `SCHEMA-INVENTORY.md`; tool responsibilities, Make targets, snapshot conventions, and audit gates are defined in `LAB-PLAN.md`.
2. Inherited DevOps artifacts enter through minimal, checksum-identified stable interface fixtures. The lab never reads the frozen DevOps working tree at runtime.
3. Every proposed chapter implementation has a meaningful local verification target and an explicit real-system limitation in `LAB-PLAN.md`.
