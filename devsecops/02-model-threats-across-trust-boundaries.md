# Model Threats Across Trust Boundaries

Northwind now knows which outcomes, authority, and data it must protect. It has explicit harms, security invariants, and accountable owners. That foundation still does not explain how a plausible actor can violate an invariant.

A connectivity diagram shows that `order-worker` calls the payment provider. A threat model asks harder questions: what authority crosses that boundary, which claims the provider validates, which assumptions remain outside the validation, and how a compromised maintainer could arrive at the same boundary through source, build, release, and runtime transitions.

This chapter turns Northwind's asset model into explicit data and authority flows, trust boundaries, and prioritized attack paths. It does not attempt to enumerate every imaginable attack. It creates a reviewable model of how plausible capabilities can reach the harms defined in Chapter 1.

## 1. A threat list without a system model

A weak threat model often begins like this:

```yaml
actor: hacker
capability: attack-system
action: compromise-everything
threatens: [be-secure]
```

The words sound security-related, but none supports a production decision. The actor capability is undefined. The prerequisite says nothing about existing access. The action does not follow a real Northwind flow. The threatened goal is not a known invariant. No owner can determine whether the path is plausible, interrupted, detectable, or accepted.

Work from the lab working tree using the How to Use This Book procedure. From the DevSecOps lab root, run:

```bash
make chapter-02-baseline
```

The baseline succeeds when it rejects the generic path:

```text
chapter 02 baseline: generic, untraceable attack path correctly rejected
```

A list of threats can prompt discussion. It becomes an engineering model only when its claims connect to the system, trust transitions, protected invariants, controls, missing evidence, and ownership.

## 2. The production model: flows, boundaries, and attack paths

> *Theory — Trust transitions and attack paths*
>
> This model enables Northwind to identify where untrusted claims gain authority and where prevention or detection can interrupt plausible harm.

### Threats describe possible harm, not inevitable events

A threat is a circumstance or actor capability that could violate a security invariant. An attack path describes how that capability can progress through the modeled system.

Keep these terms separate:

| Term | Meaning | Northwind example |
|---|---|---|
| Threat actor | A person, group, or process capable of acting against an invariant | External attacker controlling a maintainer session |
| Capability | What the actor can presently do | Act through an authenticated maintainer session |
| Prerequisite | A condition required before a step is plausible | Dependency changes are permitted through the session |
| Action | What the actor attempts at one step | Introduce a look-alike payment dependency |
| Attack path | Connected actions across real flows and boundaries | Maintainer → source → build → registry → production → provider |
| Harm | The adverse outcome if an invariant is violated | Unauthorized charge or malicious release |

An actor label alone is rarely useful. “Nation state,” “insider,” and “hacker” may imply different motivation, patience, and resources, but Northwind still needs testable capabilities and prerequisites. A junior employee with valid production access may have more immediate authority than a sophisticated external actor with no foothold.

Threat modeling does not predict the future. It records what the current system makes plausible, which assumptions support that judgment, and what evidence could change it.

### Data flow and authority flow are different

Data-flow diagrams show what moves. Security decisions also need to show what the receiver permits the sender to cause.

The `order-payment-effect` flow carries an order identifier, payment request, and stable operation identifier. It also exercises `cause-payment` authority. The data may be syntactically valid while the effect is unauthorized.

Likewise, the source-to-build flow carries reviewed source and a dependency lock. It exercises authority to trigger a build. The build-to-registry flow carries an artifact and evidence while exercising publication authority.

| Flow question | Data view | Authority view |
|---|---|---|
| What crosses? | Source, artifact, token, order, event, or claim | Permission to build, publish, deploy, read, modify, or cause an external effect |
| What can be malformed? | Content, encoding, schema, identity value | Scope, subject, approval, context, duration, or delegated power |
| What is the consequence? | Incorrect or exposed information | Unauthorized state transition or external effect |

Modeling only data misses confused-deputy failures: a trusted workload can receive attacker-influenced input and use its own legitimate authority to cause harm.

### A trust boundary is where claims require validation

A trust boundary is not simply a network segment. It is a transition where the receiving side must decide whether to accept claims, data, identity, intent, or authority from a different trust context.

Northwind's boundaries include:

- a human session proposing and approving source;
- reviewed source entering a build execution;
- a builder publishing an artifact;
- registry evidence entering production admission;
- a deployment controller changing a runtime workload;
- a workload requesting a payment effect; and
- a support session requesting protected order data.

Each boundary record names:

- the source and destination trust zones;
- what the receiver validates;
- what the design still assumes; and
- who owns the boundary.

Validation and assumption must not be conflated. The payment provider can validate workload subject, audience, operation identity, and order context while still assuming its idempotency behavior is correct and its evidence remains available. Later verification must either test those assumptions or keep the uncertainty visible.

### Controls interrupt paths; evidence tests the interruption

A control can prevent one step, reduce its impact, expose it to detection, or help recover afterward. It does not erase the attack path from the model.

Northwind already promotes artifacts by digest and uses workload identity. Those controls narrow ambiguity and authority. They do not prove that a dependency origin was approved, a valid maintainer session was uncompromised, or an admitted workload behaved as intended at runtime.

Keep paths that remain plausible under control failure. Record both existing controls and missing evidence. Later chapters will turn those gaps into owned risk and control decisions.

Mnemonic catalogs such as **STRIDE (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege)** can help teams remember those categories. They are prompts, not proof of coverage. [STRIDE threat categories](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats). A long catalog with no connection to Northwind's flows and invariants is weaker than a smaller set of explicit paths with real prerequisites and owners.

## 3. Build Northwind's threat model

The Chapter 2 model uses three files:

```text
threat-model/system.yaml
threat-model/boundaries.yaml
threat-model/attack-paths.yaml
```

> **Practice — Map data and authority flows**
>
> Describe what crosses each production connection and what the receiver allows the sender to cause.

Open `threat-model/system.yaml`. One flow is:

```yaml
- id: order-payment-effect
  from: order-worker
  to: payment-provider
  carries: [order-id, payment-request, operation-id]
  authority: [cause-payment]
  boundary: workload-to-provider
```

The stable component and flow identifiers matter. Attack paths reference them rather than copying prose that can drift independently.

Inspect every flow and ask:

1. What data or claim crosses?
2. Which authority is exercised?
3. Which security invariant can be affected?
4. Does the flow cross a decision boundary?
5. Which observations would later show accepted and rejected use?

Do not infer trust from location. Two processes in one cluster can have different identities and authority. A managed external service can enforce stronger claims than an internal shared account. The boundary follows the decision, not the network drawing.

> **Practice — Separate validation from assumption**
>
> Record what each receiver verifies and what remains an explicit uncertainty owned by the system.

Open `threat-model/boundaries.yaml` and inspect production admission:

```yaml
- id: registry-to-production
  from_zone: artifact-storage
  to_zone: deployment-control
  validates: [artifact-digest, source-identity, builder-identity, admission-policy]
  assumptions: [attestation-verifier-independent, policy-source-protected]
  owner: delivery-security
```

The boundary does not say “the registry is trusted.” It states which claims admission validates and which properties it assumes. Chapter 7 will make the validation enforceable. Chapter 13 will preserve evidence capable of revealing failures that prevention misses.

Review assumptions as future work, not hidden truth. An assumption can be accepted temporarily, converted into a verified control, monitored through detection, or rejected by redesigning the boundary.

> **Practice — Trace the cumulative attack path**
>
> Connect the compromised maintainer's capability to real flows, boundaries, threatened invariants, controls, and missing evidence.

Open `threat-model/attack-paths.yaml`. The cumulative path begins with control of an active maintainer session and progresses through six named steps. Its final step attempts a payment effect outside valid order context.

The path threatens three Chapter 1 invariants:

- `governed-production-release`;
- `attributable-payment-effects`; and
- `correct-order-terminal-state`.

It records existing controls—reviewed source, digest promotion, workload identity, and provider idempotency—without declaring the path impossible. It also records missing evidence about session assurance, dependency origin, and correlated runtime behavior.

The second path, `overprivileged-support-data-access`, models a valid support session with excessive field access. It threatens `governed-order-data`. This is not part of the cumulative attacker story. It proves that authorized subjects can violate purpose and data boundaries without stolen credentials.

### Prove the capability

Run the audit and Chapter 2 checkpoint:

```bash
make audit
make chapter-02-checkpoint
```

Expected output includes:

```text
artifact validation: passed
chapter 02 checkpoint: flows, boundaries, attack paths, and invariants verified
```

The checkpoint proves within the declared model that:

- flows reference known components and boundaries;
- all independently required boundaries exist;
- attack steps reference real flows and agree with their boundaries;
- paths state prerequisites and missing evidence;
- threatened invariants exist in Chapter 1; and
- every independently required priority invariant has a modeled attack path.

It cannot discover undocumented architecture, prove assumptions true, establish objective likelihood, or predict a real attacker's behavior.

## 4. Test the model under failure

The cumulative compromised-maintainer path is the completed model in section 3. This dedicated failure is independent: it proves the model rejects untraceable stories even when no Northwind attacker is present.

### Independent control failure — A generic attacker bypasses every real boundary

> **Practice — Reject an untraceable threat story**
>
> Diagnose why dramatic attacker language cannot support a control or evidence decision without system traceability.

**Severity:** decision failure; a generic model can hide high-impact paths while creating false confidence.  
**Plausible harm:** misdirected controls, missed release or payment abuse, unowned evidence gaps, and delayed containment.  
**Potential blast radius:** every asset whose protection relies on the incomplete threat model.  
**Bounded by:** independently required invariants, stable system identifiers, boundary ownership, cross-reference checks, and periodic review after material change.  
**Primary principles:** explicit contracts, trustworthy evidence, reconciliation, and blast-radius control.

#### Security questions

- **Asset and harm:** The model must terminate at known assets and invariants rather than “security” in general.
- **Trust and authority:** Every step must identify the real boundary and authority being crossed.
- **Detection after prevention fails:** Missing evidence must be explicit enough to become a detection hypothesis later.
- **Evidence of restored trust:** Not yet applicable; this chapter establishes the path that later containment and recovery must close.

#### Diagnosis

The unsafe fixture refers to an unknown flow, a fictional `trusted-network` boundary, and an undefined `be-secure` invariant. The checkpoint rejects it because no reviewer can determine where the actor entered, which validator failed, which owner acts, or what observation could falsify the story.

#### Correction

Correct the model by selecting a real actor capability, stating prerequisites, tracing named flows and boundaries, linking Chapter 1 invariants, recording existing controls without assuming perfection, naming missing evidence, and assigning an owner.

## 5. Production reality

**Best Practice:** threat-model material changes to assets, identities, trust boundaries, dependencies, and authority before release.

**Production Practice:** choose a review cadence and participation model that match Northwind's change rate and harm. The service owner, delivery owner, data owner, payment owner, and security practitioner see different parts of the same path.

Avoid these common failures:

- treating a network diagram as a threat model;
- listing attacker types without capabilities or prerequisites;
- trusting authenticated input without checking authorization and purpose;
- deleting paths because one preventive control exists;
- modeling every imaginable attack at equal depth;
- hiding uncertainty inside words such as “trusted,” “internal,” or “secure”; and
- allowing the document to drift after identities, dependencies, providers, or release authority change.

A useful model is incomplete but explicit. Its limitations and assumptions are review inputs. An exhaustive-looking model with stale or implicit boundaries is harder to challenge and therefore more dangerous.

## 6. What changed

| Before | After |
|---|---|
| The architecture showed connectivity. | **Flows state both transferred data and exercised authority.** |
| “Internal” and “trusted” hid validation decisions. | **Boundaries name validated claims, assumptions, and owners.** |
| Threats were generic attacker labels. | **Paths state capabilities, prerequisites, actions, and real transitions.** |
| Controls made paths disappear from discussion. | **Existing controls and missing evidence remain visible on the path.** |
| Security goals were detached from Chapter 1. | **Every priority path terminates at known invariants and harms.** |
| Review completeness was an opinion. | **Independent expectations and semantic checks reject missing coverage and broken references.** |

Northwind now has an attack model that later risk decisions can prioritize and later controls can interrupt, observe, and recover from.

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| System and trust-boundary model | `threat-model/system.yaml` and `threat-model/boundaries.yaml` | They record data, authority, validation, assumptions, and ownership at every modeled transition. |
| Prioritized attack-path register | `threat-model/attack-paths.yaml` | It connects actor capabilities to real flows, controls, missing evidence, and Chapter 1 invariants. |

## What You Learned

A threat model is a decision model, not a catalog of frightening possibilities. Data flows show what crosses a connection; authority flows show what the receiver allows the sender to cause. Trust boundaries identify where claims require validation and where assumptions remain. Attack paths connect plausible capabilities and prerequisites to real transitions, protected invariants, existing controls, missing evidence, and owners.

### Prove It

> **Independent Practice — Model compromised support access**
>
> Extend the support-data path without treating a valid identity as proof of authorized purpose.

Assume an attacker controls an active support session but cannot change source or production workloads. Model a path toward unauthorized customer-order disclosure. State the capability, prerequisites, flow, boundary, validated claims, remaining assumptions, threatened invariant, existing controls, missing evidence, and owner. Then explain which prevention and detection decisions Chapter 3 should evaluate.

## Next

Northwind now knows what it protects and how plausible capabilities can cross trust boundaries toward harm. It still cannot decide which paths require immediate treatment, which uncertainty is acceptable, or how to select complementary controls without turning severity labels into automatic decisions.

Chapter 3 turns the threat model into owned, evidence-backed risk and control decisions with explicit residual uncertainty and review triggers.
