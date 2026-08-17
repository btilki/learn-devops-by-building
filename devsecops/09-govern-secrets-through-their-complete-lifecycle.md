# Govern Secrets Through Their Complete Lifecycle

Chapter 8 made vulnerability risk explicit. A reusable secret can still collapse the identity and supply-chain boundaries Northwind has built: whoever possesses the value may exercise its authority without inheriting the identity controls that should govern its use.

## 1. A secret found is not a secret recovered

Northwind's payment-provider credential is stored as a **CI (Continuous Integration)** variable and injected as plaintext. A scanner can identify its synthetic marker, but no inventory proves its owner, consumers, custody, active version, or revocation state.

Work from the lab working tree using the Chapter 0 procedure. From the DevSecOps lab root, run:

```bash
make chapter-09-baseline
```

```text
chapter 09 baseline: plaintext synthetic credential passed permissive reference policy
```

Finding the string is only exposure evidence. Recovery requires Northwind to stop disclosure, remove old authority, replace it safely, inspect use, reconcile provider effects, and prove the exposed material no longer works.

## 2. The production model: govern authority through a lifecycle

> *Theory — Secrets, identities, custody, and rotation*
>
> This model enables Northwind to minimize unavoidable secrets and recover when their confidentiality fails.

An identity is an attributable subject with claims evaluated in context. A secret is material whose possession grants capability. A secret may authenticate a subject, decrypt data, sign artifacts, or authorize a provider call, but possession alone often weakens attribution because different holders can present the same value.

| Lifecycle stage | Required decision | Evidence |
|---|---|---|
| Create | Is a reusable secret unavoidable, and how is it generated? | Purpose, owner, custodian, creation method |
| Store | Which system protects plaintext and encryption keys? | Approved custody and reference-only manifests |
| Distribute | Which consumers may receive which version? | Workload identity, reference, delivery decision |
| Use | Which subject exercised which purpose and authority? | Secret version, subject claim, result, time |
| Rotate | How do old and new versions overlap without interruption? | Issue, overlap, consumer migration, health |
| Revoke | Which authority and derived material must stop working? | Provider rejection and access-history review |
| Retire | When is historical material no longer recoverable or usable? | Inventory state, backup and log constraints |

Envelope encryption separates a data-encryption key from the key that protects it, improving rotation and custody boundaries. It does not eliminate the initial authority needed to obtain decryption capability. That bootstrap dependency is sometimes called secret zero. Federation and workload identity can reduce it, but every remaining root must be named rather than hidden.

Rotation is not replacement alone. During bounded overlap, old and new versions may both work so consumers can move safely. The overlap increases authority and must expire. Revocation closes old authority; retirement records that it is no longer an active operational version.

## 3. Enforce custody, reference-only use, and attribution

> **Practice — Inventory unavoidable secrets**
>
> Record purpose, owner, custodian, storage, consumers, versions, rotation method, and exceptions.

Open `secrets/inventory.yaml`. Northwind retains one modeled payment-provider credential because the external provider still requires it. `payment-v1` is retired; `payment-v2` is active under the secret broker. Workload federation should replace reusable credentials wherever the dependency supports it.

> **Practice — Keep plaintext out of governed manifests**
>
> Store only a broker reference and the expected version in workload configuration.

Open `secrets/policy.yaml` and `secrets/references.yaml`. The policy requires approved custody, ownership, reference-only use, attributable access, and no more than 15 minutes of rotation overlap. The reference manifest carries no usable value.

> **Practice — Preserve lifecycle and use evidence**
>
> Bind every modeled use to secret ID, version, workload subject, claim, purpose, result, and time.

The authorization mechanism emits `build/chapter-09-access-events.jsonl` when it evaluates the allowed `payment-v2` use by `order-worker`. The checkpoint cross-checks secret, version, subject, claim, purpose, and result rather than trusting a hand-written event. Run:

```bash
make audit
make chapter-09-checkpoint
```

The checkpoint validates governed artifacts, reference-only configuration, one active version, bounded overlap, an approved consumer, and attributable use. This deterministic model does not operate a real broker, encryption service, CI system, or payment provider; production must validate custody, delivery, access logs, masking, and provider rejection against those systems.

## 4. Test the design under failure

### Connected consequence — Expose and replay a brokered payment credential

> **Practice — Treat exposure as loss of confidentiality, not proof of misuse**
>
> Exercise an inert marker representing `payment-v1` in a CI log and replay its modeled authority through the compromised-maintainer path.

**Severity:** critical; the exposed credential can authorize payment-provider effects.  
**Plausible harm:** unauthorized charges, fraudulent reconciliation, concealed payment divergence, and customer harm.  
**Potential blast radius:** provider operations authorized by the exposed credential until revocation.  
**Bounded by:** masking, consumer policy, versioned rotation, provider revocation, attributable access, effect reconciliation, and replay tests.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence, reconciliation, and recovery.

#### Security questions

- **Asset and harm:** Payment authority and attributable payment effects drive the response.
- **Trust and authority:** Possession of the old value must not grant continuing authority after revocation.
- **Detection after prevention fails:** Exposure location, version, subject claim, access history, provider operations, and masking status remain reviewable.
- **Evidence of restored trust:** Not yet applicable. Chapter-local recovery: old replay is denied, the new version works only for the approved workload, provider effects reconcile, and only the replacement remains accepted.

#### Diagnosis

Run `make chapter-09-attack`. The pre-rotation model demonstrates that the compromised maintainer can replay the exposed synthetic `payment-v1` authority and writes `build/chapter-09-exposure.yaml`. The modeled provider then records an unauthorized `payment-order-9001-authorized` effect, accepts both versions during the transition, reports degraded security health, and writes `build/chapter-09-provider-compromised.yaml` for recovery. No real credential or external provider is used.

#### Containment

Run `make chapter-09-contain`. It requires `build/chapter-09-exposure.yaml` from the attack, derives the affected version, records revocation in `build/chapter-09-revocations.json`, marks further CI-log disclosure as masked, confirms historical-access inspection, and records replacement of the derived provider session. Containment stops new modeled use; it does not prove that earlier provider effects are legitimate. Chapter 10 containment reads that revocation file.

#### Recovery

Run `make chapter-09-recover`. Recovery evaluates `payment-v1` against the pre-rotation inventory where it is still active, so denial depends on the containment revocation rather than its later retired label. It distinguishes unknown, retired, and revoked versions in its evidence. Recovery then proves `payment-v2` works for `order-worker`, verifies v1 is absent from provider acceptance after the bounded overlap, identifies the unauthorized provider effect, records its reversal, reconciles final effects, and requires healthy service. It writes `build/chapter-09-recovery.json`.

Historical repository content, logs, caches, backups, derived session tokens, and copied local files remain investigation scope even after provider revocation. Rotation without that scope assessment restores a credential but may leave other authority active.

## 5. Production reality

**Best Practice:** eliminate reusable secrets where federation is available; govern every unavoidable secret from creation through verified retirement.

**Production Practice:** separate secret custody from application configuration, use short-lived delivery, bind access to workload identity, test masking and broker outage, rotate under observed service health, and verify revocation at the authoritative provider. Maintain emergency procedures for broker or identity-provider failure without creating permanent plaintext fallbacks.

Secret scanning should cover current files, history, logs, artifacts, tickets, and generated output, but scanner results remain exposure indicators. High-entropy detection can miss structured credentials and produce false positives. Ownership and provider-side verification determine the response.

## 6. What changed

| Before | After |
|---|---|
| A CI variable represented the payment credential. | **An inventory defines purpose, owner, custody, consumers, and versions.** |
| Workloads received plaintext configuration. | **Governed manifests contain broker references only.** |
| Rotation meant writing a new value. | **Issue, bounded overlap, migration, revocation, and retirement form one lifecycle.** |
| Exposure detection implied incident closure. | **Replay rejection and access-history scope prove authority was removed.** |
| Service success implied recovery. | **Replacement use and reconciled payment effects prove business and security recovery.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Secret inventory | `secrets/inventory.yaml`, `secrets/policy.yaml`, and `secrets/references.yaml` | They preserve ownership, custody, consumers, lifecycle, and reference-only use. |
| Rotation and exposure-response runbook | `secrets/exposure-response-runbook.md` | It preserves containment, rotation, revocation, historical inspection, derived-credential replacement, reconciliation, and recovery obligations. |

## What You Learned

A secret is authority-bearing material, not merely a sensitive string. Safe governance spans necessity, generation, custody, distribution, use, rotation, revocation, retirement, and evidence. Exposure response is complete only when old authority fails, replacement use remains healthy and attributable, and external effects reconcile.

### Prove It

> **Independent Practice — Rotate signing material after suspected exposure**
>
> Design the response without treating a newly generated key as proof that old release authority disappeared.

Specify custodian, affected signatures and derived trust, overlap policy, revocation distribution, transparency evidence, rebuild scope, old-key rejection, new-key use, historical inspection, and the observation that proves the trust migration closed.

## Next

Authority-bearing secrets are now governed. Chapter 10 protects customer and operational data according to purpose, sensitivity, retention, deletion, and permitted use.
