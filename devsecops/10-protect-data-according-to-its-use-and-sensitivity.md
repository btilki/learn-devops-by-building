# Protect Data According to Its Use and Sensitivity

Chapter 9 governed authority-bearing secrets. Northwind still holds customer and operational data whose misuse may be fully authenticated and encrypted. Protection must therefore govern why data exists, who may use which fields, where copies may live, and how every copy reaches deletion.

## 1. Encryption does not prevent authorized overexposure

The notification service needs an order identifier, customer email, and total to send a confirmation. A malicious dependency requests `payment_reference` as well, then attempts to place the expanded record in telemetry and a non-production fixture. Encryption at rest would protect neither authorized retrieval nor excessive copying.

Work from the lab working tree using the Chapter 0 procedure. From the DevSecOps lab root, run:

```bash
make chapter-10-baseline
```

```text
chapter 10 baseline: permissive purpose policy admitted payment data to telemetry
```

## 2. The production model: sensitivity follows use and harm

> *Theory — Classification, purpose, minimization, and lineage*
>
> This model enables Northwind to derive controls from the harm a field can cause in a particular use.

Classification labels the protection need of a data element. Purpose explains the permitted business reason for processing it. Minimization asks whether that purpose can be achieved with fewer fields, less precision, fewer copies, or shorter retention.

| Decision | Question | Control consequence |
|---|---|---|
| Classification | What harm follows disclosure or alteration? | Access, storage, telemetry, and non-production limits |
| Purpose | Why may this subject process the data? | Field-level authorization and decision evidence |
| Store | Where may this use create state? | Encryption context, residency, retention, and deletion |
| Transformation | Can masking or tokenization preserve utility with less authority? | Reduced values and separated mapping authority |
| Retention | How long does the purpose remain valid? | Store-specific expiry and purge |
| Lineage | Which derived copies and backups inherit obligations? | Propagated classification, deletion, and restore controls |

Encryption protects data under particular key and access assumptions. Tokenization replaces a sensitive value with a reference and separates the mapping authority. Masking reduces displayed precision. None decides whether collection was necessary or whether an authenticated support user may see the field.

Deletion is a distributed state transition. Primary data, telemetry, caches, non-production copies, exports, and backups have different mechanisms. An immutable backup may expire by generation rather than support immediate record rewriting; every restore must reapply current tombstones before the data becomes usable.

## 3. Bind permitted fields to subject, purpose, and store

> **Practice — Classify data by plausible harm**
>
> Assign an owner and sensitivity to each governed field.

Open `data-security/classification.yaml`. `payment_reference` is restricted because disclosure creates payment linkage and fraud risk. `customer_email` and `order_total` are confidential; `order_id` is internal.

> **Practice — Declare minimum permitted uses**
>
> Bind each purpose to a subject, minimum field set, and allowed stores.

Open `data-security/uses.yaml` and `data-security/access-policy.yaml`. Notification may use three fields only in runtime memory. Support inquiry receives a narrower support-session view—the control that Chapter 2's `overprivileged-support-data-access` path requires for `governed-order-data`. Payment reconciliation belongs to `order-worker`, not notification or support. The access policy gives every known destination an explicit maximum class; an unknown or misspelled store is rejected rather than silently operating without a ceiling.

The field sets are reviewed claims of minimum need. The evaluator can prove that a request does not exceed a declared use, but it cannot prove that the declared use itself contains the fewest fields capable of achieving the business purpose.

> **Practice — Govern lifecycle by store**
>
> Set retention and deletion behavior for primary, telemetry, non-production, and backup copies.

`data-security/retention.yaml` makes each deletion mechanism explicit for primary, runtime memory, support sessions, telemetry, non-production, and backups. `data-security/lineage.yaml` maps derived copies from their source to destination and inherits the destination deletion contract. The checkpoint rejects any used or derived store without retention, deletion, and class policy. Run:

```bash
make audit
make chapter-10-checkpoint
```

The checkpoint proves the minimum notification use remains available and lifecycle contracts are complete. This local model cannot prove deletion from a real database or backup system; production needs authoritative access decisions, store inventories, purge reports, restore tests, and exception evidence.

## 4. Test the design under failure

### Connected consequence — Copy payment-related data into logs and non-production

> **Practice — Deny unnecessary fields and unsafe destinations**
>
> Evaluate the malicious dependency's request for `payment_reference` and telemetry storage.

**Severity:** high; the request expands restricted payment-linked data beyond its declared purpose.  
**Plausible harm:** customer disclosure, payment linkage, fraud enablement, and uncontrolled secondary copies.  
**Potential blast radius:** telemetry consumers, retained log stores, and non-production users receiving the copied record.  
**Bounded by:** field-purpose authorization, store class limits, minimization, quarantine, purge, retention, and secret rotation where authority was exposed.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence, reconciliation, and recovery.

#### Security questions

- **Asset and harm:** Customer order data, payment authority, and correct order outcomes drive the boundary.
- **Trust and authority:** Notification authority grants no payment-reconciliation or telemetry-copy authority.
- **Detection after prevention fails:** The decision retains subject, purpose, fields, classes, store, result, and named denials; lifecycle evidence identifies copied stores.
- **Evidence of restored trust:** Not yet applicable. Chapter-local recovery: governed copies are purged, exposed authority is rotated where relevant, sanitized replacements contain no production values, and backup expiry constraints remain explicit.

#### Diagnosis

Run `make chapter-10-attack`. The decision independently rejects the undeclared payment field, every confidential or restricted field that exceeds telemetry's class ceiling, and the undeclared telemetry store. It writes the decision plus `build/chapter-10-exposed-copies.json`, which materializes the synthetic telemetry and non-production copies used by containment.

#### Containment

Run `make chapter-10-contain`. It requires the denial and exposed-copy state, derives quarantine and purge scope from those copy IDs, and records an empty remaining-copy set. It also reads `build/chapter-09-revocations.json` and requires the exposed payment version to be revoked instead of accepting a descriptive cross-chapter label. If that file is absent, run `make chapter-09-attack chapter-09-contain` first.

#### Recovery

Run `make chapter-10-recover`. Recovery reconciles every exposed copy ID against the purge transition, then validates each sanitized-fixture field through `classification.yaml` and the non-production class ceiling. It independently compares fixture values with the exposed synthetic values, permitting any classified public or internal fields without relying on a self-declared class list. The recovery record distinguishes immediate governed-store purge from backup expiry and restore-time tombstone reapplication.

## 5. Production reality

**Best Practice:** authorize the smallest field set for one declared purpose and propagate its lifecycle obligations to every derived store.

**Production Practice:** enforce access near authoritative data, preserve application context in decision logs, tokenize payment-linked values, prevent restricted classes from entering telemetry, generate synthetic non-production fixtures, and reconcile deletion across indexes, caches, exports, analytics, and backups. Test restored backups against current tombstones before releasing them.

Classification must change when purpose, harm, regulation, topology, or transformations change. Labels copied once into a catalog and never reconciled with actual stores become misleading evidence.

## 6. What changed

| Before | After |
|---|---|
| Encryption represented complete protection. | **Purpose, field, subject, and store govern authorized use.** |
| Services received broad order objects. | **Minimum declared fields bound each use.** |
| Telemetry inherited application data accidentally. | **Store class limits reject sensitive copies.** |
| Non-production reused production-shaped values. | **Sanitized synthetic fixtures preserve utility without production data.** |
| Deletion referred only to the primary database. | **Every store has retention, purge, backup, and restore obligations.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Data classification and use register | `data-security/classification.yaml` and `data-security/uses.yaml` | They preserve harm, ownership, purpose, subject, minimum fields, and stores. |
| Retention and deletion contract | `data-security/access-policy.yaml`, `data-security/retention.yaml`, and `data-security/lineage.yaml` | They bind store ceilings, derived copies, deletion behavior, and backup limitations. |

## What You Learned

Data protection is governance of permitted use, not encryption alone. Classification, purpose, minimization, transformations, store boundaries, retention, deletion, and lineage must agree. Recovery removes unsafe copies, replaces them with validated sanitized data, and documents where immutable backup expiry delays physical deletion.

### Prove It

> **Independent Practice — Design a support investigation view**
>
> Let support diagnose a failed order without granting general customer-history or payment-data access.

Specify subject, purpose, fields, masking, session store, retention, evidence, approval, exception behavior, deletion, and the observation that would reveal over-collection.

## Next

Identity, supply chain, vulnerabilities, secrets, and data now have domain policies. Chapter 11 places those policies at explicit enforcement points and governs exceptions without hiding them.
