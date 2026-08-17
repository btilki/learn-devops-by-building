# Define What Security Must Protect

Northwind already has controls. Production artifacts are identified by digest. Workloads use bounded identities. Releases can stop when user-visible evidence degrades. Durable state can be reconstructed.

None of those mechanisms answers the first security question:

> What must Northwind protect, from which harms, and who owns the decision?

Without that answer, security work becomes a queue of tool findings and inherited defaults. A scanner reports a vulnerable package. A cloud rule reports a public endpoint. A reviewer asks for encryption. An auditor asks for evidence. Each request may be reasonable, but the team cannot compare them until it knows which business, data, identity, and operational outcomes are at risk.

This chapter establishes that foundation. You will define Northwind's critical assets, name the harms that matter, express security invariants, and assign accountable ownership. The result is not a decorative inventory. Later chapters use it to decide which threat paths deserve attention, which controls are proportionate, which evidence is meaningful, and what recovery must restore.

## 1. An unsafe security model

The inherited DevOps system protects a critical business outcome:

> A valid order is durably accepted and reaches a correct terminal state without duplicate charge, invalid inventory state, or permanent disappearance.

That statement is strong operationally. It names success in business terms rather than describing a deployment or process. Security must extend it because an attacker can violate Northwind without making the service unavailable.

Consider four examples:

- An unauthorized actor causes a valid-looking payment for an order the customer never submitted.
- A support user reads complete customer order histories without a legitimate purpose.
- A compromised maintainer admits a malicious release that still returns healthy responses.
- An attacker changes inventory state while every availability indicator remains green.

The DevOps outcome helps expose the damage, but it does not name all protected authority, data, or trust. Northwind needs an explicit security model before it chooses more controls.

Work from the lab working tree using the Chapter 0 procedure. From the DevSecOps lab root, run the Chapter 1 baseline:

```bash
make chapter-01-baseline
```

The command succeeds when it detects the intended unsafe model:

```text
chapter 01 baseline: unsafe asset classification correctly detected
```

The fixture calls a payment token a configuration value, assigns no accountable owner, and names no harm. The token may be stored in a configuration system, but storage location does not explain its security significance. It carries authority to cause an external financial effect.

That distinction drives the chapter.

## 2. The production model: assets, harms, invariants, and ownership

> *Theory — Asset-and-harm model*
>
> This model enables Northwind to select and evaluate controls according to the outcomes they protect rather than the tools that implement them.

### An asset is something whose loss or misuse can cause harm

In this book, an asset is something Northwind values because its compromise can cause a meaningful business, customer, security, or operational harm.

An asset can be tangible or intangible:

- a correct terminal order outcome;
- authority to charge a payment method;
- customer and order data;
- authority to admit a production release;
- the integrity of a dependency graph;
- an investigation record whose integrity supports a containment decision; or
- customer trust and the organization's ability to operate within its obligations.

An asset is not limited to data. Identity and authority are often more important than the credential that represents them. A credential is replaceable material. The authority it unlocks can change production, disclose data, or cause a payment.

An asset is also not necessarily a single technical object. The correct terminal state of an order depends on the storefront, queue, worker, database, payment provider, identities, and recovery evidence. Treating only the database row as the asset would miss duplicate external charges and malicious but syntactically valid state transitions.

### A resource is where an asset is represented or exercised

A resource is a system object that stores, processes, transmits, or controls access to an asset. PostgreSQL, a queue topic, a repository branch, a cloud role, a container image, and a signing key are resources.

The distinction matters because controls attach to resources while harms attach to assets.

For example:

| Resource | Asset represented or exercised | Example harm |
|---|---|---|
| PostgreSQL `orders` table | Correct order state and customer order data | Unauthorized modification or disclosure |
| Payment provider credential | Payment authority | Unauthorized charge or fraud |
| Protected production branch | Release authority and reviewed intent | Malicious or unreviewed release |
| Workload identity token | Dependency-specific workload authority | Unauthorized dependency access |
| Telemetry store | Security and operational evidence | Investigation based on altered or missing events |

If Northwind begins with the resource, it tends to copy generic controls: encrypt the database, rotate the credential, protect the branch, shorten the token, retain the logs. Those can be strong defaults. Starting with the asset and harm reveals what the control must actually accomplish and what evidence could falsify its claim.

Database encryption does not stop an overprivileged application from reading unnecessary fields. Credential rotation does not establish which subject used the old credential. Branch protection does not prove that an approved dependency origin was trustworthy. Log retention does not prove that required events were produced or preserved intact.

### Harm is the consequence Northwind is trying to prevent or bound

A harm is a meaningful adverse outcome. It is not the same as a technical event.

“A token appeared in a log” is an observation. The possible harms include unauthorized charge, fraudulent refund, data access, loss of attribution, or use of the credential to enter another trust boundary.

“A container opened a shell” is behavior. The possible harms depend on the workload's authority, accessible data, network reach, deployment context, and the attacker's ability to persist or move laterally.

Naming harm forces useful precision:

- Who or what is affected?
- Which outcome becomes incorrect, unavailable, disclosed, or untrustworthy?
- Can the harm propagate outside the originating resource?
- Can Northwind reverse the effect, or only compensate for it?
- Which evidence would show that the harm occurred?

The familiar confidentiality, integrity, and availability model remains useful:

- **Confidentiality:** information or authority is not disclosed to an unauthorized subject.
- **Integrity:** state, decisions, code, evidence, or effects are not created or changed without authorization.
- **Availability:** required capability and information remain accessible to authorized users at the necessary time.

Northwind also needs business-specific harms such as fraud, duplicate financial effects, loss of attribution, prohibited data use, and inability to establish trustworthy recovery. These are not replacements for confidentiality, integrity, and availability. They make those properties operationally meaningful.

### A security invariant states what must remain true

A security invariant is a required or prohibited outcome that should remain true across normal operation, change, attack, failure, containment, and recovery.

Good invariants describe the protected result without prescribing the tool:

- Only an authorized attributable workload may cause a payment effect for an accepted order.
- Order data is disclosed or modified only for an authorized purpose by an attributable subject.
- Every production release is attributable, reviewed, policy-conformant, and bound to trusted evidence.
- A valid order reaches one correct terminal state without duplicate charge or invalid inventory.

Weak statements describe mechanisms or aspirations:

- Use a secrets manager.
- Enable multifactor authentication.
- Scan every image.
- Follow least privilege.
- Keep customer data secure.

The first four may become controls. The last is too vague to evaluate. None states what must remain true when the mechanism fails, is bypassed, produces incomplete evidence, or applies to the wrong resource.

An invariant should be falsifiable. Northwind should be able to identify observations that would contradict it. A payment effect with no accepted order, no authorized workload subject, or no stable operation identity falsifies the payment invariant. A production digest admitted from an unauthorized builder falsifies the release invariant even if its signature is cryptographically valid.

### Ownership means decision accountability

Ownership in this chapter does not mean that one team performs every control or responds alone. It means one role or team is accountable for maintaining the asset definition, accepting or escalating relevant risk, reviewing material changes, and ensuring that unclear responsibility does not silently become accepted exposure.

Several groups may participate:

- service owners understand business behavior and application changes;
- security engineers understand threats, control failure, and investigation evidence;
- platform or cloud teams operate shared enforcement mechanisms;
- data owners determine permitted uses and lifecycle obligations;
- incident responders coordinate containment and recovery; and
- executives or risk owners may accept consequences that engineering teams cannot authorize.

Shared work is normal. Shared accountability without a decision owner is dangerous.

An owner must be able to answer:

- Which asset and harm are in scope?
- Which changes require review?
- Who may accept residual risk?
- Where is escalation routed when evidence is missing or contradictory?
- What event triggers reassessment?

An email address alone does not create ownership. A useful ownership record binds a stable role or team identifier to explicit assets and an escalation path.

## 3. Build Northwind's security foundation

The completed Chapter 1 model uses three files:

```text
security-model/assets.yaml
security-model/invariants.yaml
security-model/ownership.yaml
```

The separation is deliberate. Assets describe what is valuable and how its compromise causes harm. Invariants state what must remain true. Ownership identifies who is accountable. Keeping them distinct makes contradictions and missing relationships visible.

> **Practice — Classify assets by harm**
>
> Define what Northwind values before assigning controls to the resources that represent it.

Open `security-model/assets.yaml`. The register begins with four assets:

```yaml
schema_version: 1
kind: asset-register
assets:
  - id: order-outcome
    name: Correct terminal order outcome
    owner: commerce-operations
    harms: [duplicate-charge, invalid-inventory, permanent-order-loss]
  - id: payment-authority
    name: Authority to cause payment effects
    owner: payments-security
    harms: [unauthorized-charge, payment-fraud]
  - id: customer-order-data
    name: Customer and order data
    owner: data-governance
    harms: [unauthorized-disclosure, unauthorized-modification]
  - id: release-authority
    name: Authority to admit production releases
    owner: delivery-security
    harms: [malicious-release, unreviewed-production-change]
```

Notice what is absent. PostgreSQL is not listed as the customer-data asset. A token is not listed as payment authority. Git is not listed as release authority. Those resources will appear in later data, identity, and trust-boundary models. Here, the register remains stable even if Northwind changes database, identity, or repository products.

Inspect each entry and test it with three questions:

1. If this asset were disclosed, modified, unavailable, or misused, could you name a meaningful harm?
2. Would the asset remain important if Northwind replaced the current implementation technology?
3. Is the named owner authorized to maintain the definition and escalate its risk?

Do not expand the inventory into a list of every file, table, queue, and credential. Later chapters need a reviewable set of assets tied to consequential harm, not a configuration-management database disguised as a security model.

**Production Practice:** Real organizations usually need multiple levels of asset inventory. A high-level harm-oriented register guides threat and risk decisions. More detailed resource inventories support exposure analysis, vulnerability correlation, data lineage, secret rotation, and incident scope. They should reference one another without pretending to serve the same purpose.

> **Practice — State falsifiable security invariants**
>
> Express the outcomes that controls and recovery evidence must preserve.

Open `security-model/invariants.yaml`. The register names four required outcomes:

```yaml
- id: correct-order-terminal-state
  statement: A valid order reaches one correct terminal state without duplicate charge or invalid inventory.
  assets: [order-outcome, payment-authority]
  harms: [duplicate-charge, invalid-inventory, permanent-order-loss]
  owner: commerce-operations
- id: attributable-payment-effects
  statement: Only an authorized attributable workload may cause a payment effect for an accepted order.
  assets: [payment-authority, order-outcome]
  harms: [unauthorized-charge, payment-fraud]
  owner: payments-security
- id: governed-order-data
  statement: Order data is disclosed or modified only for an authorized purpose by an attributable subject.
  assets: [customer-order-data]
  harms: [unauthorized-disclosure, unauthorized-modification]
  owner: data-governance
- id: governed-production-release
  statement: Every production release is attributable, reviewed, policy-conformant, and bound to trusted evidence.
  assets: [release-authority]
  harms: [malicious-release, unreviewed-production-change]
  owner: delivery-security
```

Each field affects later work:

- `statement` defines the claim.
- `assets` links the claim to protected value.
- `harms` identifies why violation matters.
- `owner` identifies who must resolve ambiguity and review material change.

The invariant intentionally requires both authorization and attribution. A shared credential might successfully authorize a payment while failing to show which workload or operation used it. A perfectly attributable request from an unauthorized subject is still unsafe. Chapter 4 will make this distinction enforceable.

The phrase “for an accepted order” binds authority to business context. Payment access alone is insufficient. Later asynchronous-processing and investigation evidence must connect the external effect to the stable order operation.

Review each invariant. For each one, write down one observation that would falsify it. If you cannot describe contradictory evidence, the statement is probably too vague.

> **Practice — Make ownership reciprocal**
>
> Verify that assets name real owners and that owners explicitly acknowledge accountability for those assets.

Open `security-model/ownership.yaml`:

```yaml
owners:
  - id: payments-security
    accountable_for: [payment-authority]
    escalation: security-incident-commander
```

The asset register points to `payments-security`, and the ownership register points back to `payment-authority`. The checkpoint verifies both directions. This prevents a document from assigning responsibility to a team whose own declared scope does not include the asset.

The `escalation` field is a stable role, not a person's name. The lab verifies that the field exists. A real organization must additionally verify that the role is staffed, reachable, authorized, and rehearsed.

Avoid assigning every asset to “Security.” Security teams may operate controls and guide decisions, but service, business, data, payment, and delivery owners retain knowledge and authority that a centralized security group cannot manufacture.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-01-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 01 checkpoint: asset, harm, invariant, and ownership relationships verified
```

The audit validates the three Chapter 1 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- all independently required assets exist;
- all independently required invariants exist;
- every asset names at least one harm;
- every asset refers to a known accountable owner;
- each owner acknowledges the assets assigned to it;
- every invariant refers to known assets and an accountable owner; and
- every invariant names at least one threatened harm.

The expected asset and invariant identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not prove that four assets are sufficient for a real commerce company. It does not prove that the harms are complete, the owners have correct organizational authority, or the invariants express every legal and business obligation. Those are judgment claims requiring review with service, business, data, security, and operational stakeholders.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 1 evidence |
|---|---|
| Mechanism evidence | Schemas and the relationship evaluator operated successfully. |
| Decision evidence | Assets, harms, invariants, owners, and escalation paths are explicit and reviewed. |
| Outcome evidence | Later controls and production observations can be evaluated against stable security invariants. |
| Recovery evidence | Not yet produced; later chapters must prove compromised trust and business outcomes were restored. |

Chapter 1 primarily creates decision evidence. Pretending that the local checkpoint proves the security outcome would weaken every later chapter.

## 4. Test the model under failure

### Independent control failure — Payment authority hidden as configuration

> **Practice — Diagnose hidden payment authority**
>
> Reclassify an ownerless configuration value by the authority it grants, the harm it can cause, and the evidence recovery requires.

The baseline fixture contains this model:

```yaml
assets:
  - id: payment-token
    name: Payment token configuration value
    owner: unassigned
    harms: []
```

The problem is not merely missing fields. The model classifies the resource and hides the asset.

**Severity:** high; unauthorized external financial effects and lost attribution.  
**Plausible harm:** unauthorized charges, payment fraud, incorrect order state, dispute and compensation cost, and inability to determine which subject caused an effect.  
**Potential blast radius:** every payment operation permitted by the token's provider-side scope and validity window; a reusable credential may extend beyond one workload or order.  
**Bounded by:** provider-side scope, short validity, per-operation idempotency, transaction limits, workload-specific distribution, anomaly detection, rapid revocation, and reconciliation between accepted orders and provider effects. None repairs the missing asset decision by itself.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control, reconciliation, and recovery.

#### Security questions

- **Asset and harm:** The asset is authority to cause payment effects; the harms include unauthorized charge and fraud.
- **Trust and authority:** Possession of the token may grant reusable provider authority without a sufficiently attributable workload and order context.
- **Detection after prevention fails:** Northwind needs independently correlated provider, workload, order, and identity evidence capable of revealing effects without valid accepted operations.
- **Evidence of restored trust:** Not yet applicable. Chapter-local correction: the exposed authority must fail, replacement authority must be bounded and attributable, provider effects must reconcile with accepted orders, and legitimate payment outcomes must recover.

#### Diagnosis

Calling the token “configuration” encourages configuration controls: encrypt it at rest, keep it outside Git, and inject it at runtime. Those may reduce exposure, but they do not answer who can use the authority, for which operations, for how long, with what attribution, or how Northwind detects and recovers from misuse.

The missing harm makes prioritization impossible. The missing owner makes treatment and acceptance ambiguous. The missing invariant leaves no stable claim for later identity, secret, detection, and recovery chapters to enforce.

#### Correction

The completed model does not elevate the token itself into a crown-jewel asset. It defines `payment-authority` and states the invariant that only an authorized attributable workload may cause a payment effect for an accepted order.

That correction changes later decisions:

- Chapter 4 must bind authorization to an attributable workload subject.
- Chapter 5 must prevent self-approved elevation into payment or production authority.
- Chapter 9 must govern unavoidable payment credentials through issue, use, rotation, exposure, and revocation.
- Chapter 13 must correlate identity, order, provider, and runtime events.
- Chapters 14 and 15 must reconcile payment effects and invalidate compromised authority before declaring restored trust.

The concept is practical because it changes the production contract across the rest of the book. Adding an arbitrary command would not make it more practical.

## 5. Production reality

### Common modeling errors

#### Listing every resource as an asset

An exhaustive resource list becomes stale quickly and obscures the few outcomes that should drive risk decisions. Maintain detailed inventories where exposure, lifecycle, and response require them, but connect them to stable harm-oriented assets.

#### Naming controls as invariants

“All secrets use Vault” binds the security claim to one product and says nothing about authorized use, exposure, revocation, or recovery. State the required outcome first; select the mechanism later.

#### Assigning ownership without authority

A team cannot own a risk decision if it lacks authority to change the system, fund treatment, accept residual impact, or escalate to someone who can. Record the real decision path.

#### Treating confidentiality as the only security property

For Northwind, malicious but valid-looking changes to order, release, identity, and payment state can be more damaging than disclosure. Integrity, attribution, purpose, and recoverability deserve explicit treatment.

#### Using high-level assets without downstream traceability

“Customer trust” may be valuable, but it is too broad to govern an authorization rule by itself. Connect it to specific data, authority, service, and evidence outcomes that later controls can evaluate.

#### Assuming absence of evidence means absence of harm

If Northwind cannot correlate a payment effect with an accepted operation and attributable subject, it has missing evidence—not proof that the effect was authorized. Chapter 13 will make telemetry completeness an explicit detection concern.

## 6. What changed

| Before | After |
|---|---|
| Northwind listed technical resources without naming the protected outcome. | **Assets describe stable business, data, identity, and operational value.** |
| A payment token looked like ordinary configuration. | **Payment authority is modeled through unauthorized-charge and fraud harms.** |
| Security goals described tools or broad aspirations. | **Falsifiable invariants state what must remain true across operation, attack, and recovery.** |
| Asset ownership was implied by system operation. | **Assets and owners acknowledge accountability in both directions and name escalation paths.** |
| A valid schema could appear to prove a sound decision. | **Structural, decision, outcome, and recovery evidence remain explicitly distinct.** |
| Findings and controls had no stable business reference. | **Later threats, risks, controls, detections, and recovery decisions inherit the same asset-and-harm model.** |

What changed was not merely three YAML files. Northwind now has a falsifiable security contract that later chapters can threaten, enforce, observe, and restore.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Asset-and-harm and ownership registers | `security-model/assets.yaml` and `security-model/ownership.yaml` | They retain the stable protected outcomes, plausible harms, accountable owners, and escalation paths that later risk decisions reference. |
| Security invariant register | `security-model/invariants.yaml` | It retains the falsifiable claims that later controls, attacks, evidence, and recovery must preserve or restore. |

These artifacts should change when Northwind's business use, authority, data, dependencies, or plausible harms materially change—not whenever a tool produces a new finding.

## What You Learned

Assets are valued outcomes, data, or authority whose compromise can cause harm. Resources store, transmit, represent, or exercise those assets but are not automatically the assets themselves. Technical events become security-relevant through their plausible consequences. Security invariants state falsifiable required or prohibited outcomes without prescribing tools, while accountable owners provide real decision and escalation paths.

Schema and relationship checks can prove structural completeness within declared scope. They cannot prove that human judgment is correct. A concept earns its place when it changes later production decisions, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Model refund authority**
>
> Decide how Northwind protects refund authority without copying the payment-authority model mechanically.

Northwind plans to add customer-service refunds. A refund changes an external financial state, but its actor, business context, limits, approval path, and harm differ from an order-worker payment.

Extend the Chapter 1 model without adding implementation policy yet:

1. Decide whether refund authority is a new asset or a bounded use of `payment-authority`.
2. Name at least two plausible harms, including one that does not require stolen credentials.
3. Write a falsifiable invariant connecting subject, authorization, order context, amount or scope, and attribution.
4. Assign an accountable owner and escalation role.
5. Identify one observation that would falsify the invariant.
6. Explain which material change would trigger review of your decision.

Do not copy the payment entry and rename it. A support user's refund authority has different delegation, fraud, approval, evidence, and recovery consequences. Your durable output is the decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 1 capability when you can explain why payment authority matters more than the token that represents it, trace every invariant to known assets and harms, describe evidence that would falsify each invariant, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Northwind now knows what it must protect and who owns the definitions. It still does not know where trust is granted, which actors can cross those boundaries, or how a compromised maintainer can progress from source authority toward production and payment harm.

Chapter 2 turns the asset and invariant registers into a threat model with explicit data and authority flows, trust boundaries, attack prerequisites, control assumptions, and prioritized abuse paths.
