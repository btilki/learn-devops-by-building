# Eradicate Persistence and Restore Trust

Chapter 14 stopped known attacker actions, preserved evidence, and retained business state. It did not make the environment trustworthy. The compromised artifact still identifies the contained deployment, an automation credential remains outside the first revocation scope, a payment token was read by attacker-controlled code, and a registry cache may retain material that can recreate the foothold.

## 1. Containment succeeded, but trust remains open

Northwind’s release path is frozen and `order-worker` is isolated. That prevents immediate reuse of known authority, but it does not answer which trust roots produced the affected system or which descendants must be replaced. Returning traffic because the alert is quiet would confuse inactivity with recovery.

Work from the lab working tree using the How to Use This Book procedure. From the DevSecOps lab root, run:

```bash
make chapter-14-checkpoint chapter-14-contain chapter-14-recover chapter-15-baseline
```

```text
chapter 15 baseline: harm contained but trust roots and persistence remain unresolved
```

The first three targets recreate Chapter 14 evidence custody, contained operational state, and the generated verification record; `build/` outputs and `response/evidence-manifest.yaml` are not assumed to exist in a fresh working tree. If the Chapter 13 alert or investigating case is missing, run the Chapter 14 opener sequence first. The baseline then requires `trust_restored: false`, confirms that the persistence unknown is still open, and proves that the retained artifact and automation path exist in operational state.

## 2. The production model: replace trust, reconcile state, then return traffic

> *Theory — Eradication, trust roots, and bounded recovery*
>
> Recovery replaces every affected root and reachable descendant in the modeled scope, then tests security and business outcomes over time.

Containment closes current authority. Eradication removes mechanisms that could restore that authority. A persistence path can be a credential, cache, controller, desired-state record, secret, startup mechanism, or any other route that recreates attacker capability after the visible workload is removed.

A trust root is an input accepted without being derived again inside the current decision: reviewed source intent, identity policy, builder identity, signing authority, configuration identity, or durable business data. Reusing a suspect root during recovery reproduces uncertainty even when the resulting service appears healthy.

| Element | Required recovery question | Failure mode |
|---|---|---|
| Trust inventory | Which roots and descendants can recreate authority or state? | Recovery omits a persistence path |
| Rotation scope | Which credentials, keys, and identities must be invalidated or replaced? | Old authority remains reusable |
| Clean-room rebuild | Did a trusted source, builder, key, and dependency decision produce a new artifact? | Compromised inputs reproduce the artifact |
| Cache invalidation | Can any retained layer still serve an invalidated digest? | A controller restores the foothold |
| Desired/actual agreement | Does deployed state match reviewed intent and the admitted artifact? | Recovery validates the wrong system |
| State reconciliation | Do queue, database, order, and payment outcomes agree? | Security recovery creates hidden customer harm |
| Recovery criteria | Which security and service outcomes must hold before traffic returns? | A single green sample becomes false confidence |
| Heightened monitoring | Do detections remain active across recovery windows? | Recovery hides recurrence |

Known-good state is not merely a file copied from backup. It is a chain whose roots are independently justified and whose descendants reconcile to the intended result. A clean-room rebuild therefore binds source revision, dependency resolution, builder, signing key, artifact digest, admission decision, deployment evidence, runtime contract, and desired state.

Credential rotation follows the same rule. Issuing a new credential is insufficient if the old credential remains valid, if descendants still trust its outputs, or if caches retain artifacts it published. Rotation succeeds when old authority fails and replacement authority is narrowly usable.

Restored trust is a bounded evidence claim. Northwind can prove that invalidated roots and modeled descendants were replaced, old credentials and artifacts fail, business state reconciles, and detections remain active. It cannot prove that no unmodeled persistence exists anywhere.

## 3. Build the trust-restoration contract

> **Practice — Inventory roots and reachable descendants**
>
> Open `recovery/trust-inventory.yaml`. Trace identity, automation, builder, artifact, cache, runtime, and payment trust to every modeled dependent.

The inventory marks the incident artifact invalidated, the first compromised session contained, the release automation, registry cache, and exposed payment credential suspect, and the clean rebuild roots trusted. `scope_limit` makes the epistemic boundary part of the artifact rather than a disclaimer added after the result. A descendant of an invalidated root cannot become trusted merely by changing its status: it must be invalidated, replaced, or name the trusted roots from which it was re-derived.

> **Practice — Order eradication before service restoration**
>
> Open `recovery/eradication-plan.yaml`. Evidence verification and persistence detection precede automation rotation and cache invalidation. Rebuild precedes business reconciliation, and monitored service restoration is last.

Reconciliation remains paused during persistence removal. A controller that continues converging toward stale desired state can undo eradication while responders are still rebuilding.

> **Practice — Bind the clean rebuild to inherited recovery roots**
>
> Open `recovery/rebuild-manifest.yaml` and `recovery/verification.yaml`. The manifest consumes the inherited DevOps recovery, incident, GitOps, and observability contracts.

Run:

```bash
make chapter-15-checkpoint
```

The checkpoint validates the trust graph, rejects dangling or cyclic dependencies, verifies Chapter 14 evidence custody, checks eradication order, and requires the inherited roots: reviewed intent, artifact identity, configuration identity, durable data, and identity policy.

## 4. Test the design under failure

### Cumulative attack — Retained automation and cache persistence

> **Practice — Attempt recovery through a path containment missed**
>
> Model a still-active release automation credential and a registry cache that can serve the invalidated artifact digest.

**Severity:** critical; premature reconciliation can recreate the production foothold after responders believe the incident is contained.  
**Plausible harm:** renewed malicious execution, repeated order or payment effects, loss of recovery confidence, and a second service interruption.  
**Potential blast radius:** release automation, registry cache, deployment controller, production workload, in-flight orders, and payment reconciliation.  
**Bounded by:** frozen deployment, paused reconciliation, preserved evidence, deterministic local fixtures, and no external execution.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence, reconciliation, and recovery.

#### Security questions

- **Asset and harm:** Trusted release authority, production state, order outcomes, and recovery evidence are at risk.
- **Trust and authority:** The old automation credential and every artifact reachable through the suspect cache remain untrusted.
- **Detection after prevention fails:** Cache selection and authorization decisions expose the persistence replay while Chapter 13 detection remains active.
- **Evidence of restored trust:** Old automation is denied, the invalidated digest is not servable, a new source-to-runtime chain agrees, terminal business outcomes reconcile, and two consecutive monitored windows pass.

#### Diagnosis

Run:

```bash
make chapter-15-attack
```

The controlled replay finds the invalidated digest still servable through the retained cache while `release-workflow` remains active. Reconciliation stays paused, so the lab proves capability without redeploying the artifact.

#### Containment

Run:

```bash
make chapter-15-contain
```

The evaluator re-verifies Chapter 14 custody, revokes the missed automation subject, authorizes its narrow replacement, rotates exposed `payment-v2` to `payment-v3` through Chapter 9’s authorization mechanism, purges the invalidated cache entry, and confirms the deployment path remains frozen. The resulting eradication record still states `trust_restored: false`.

#### Recovery

Run:

```bash
make chapter-15-recover
make chapter-15-verify-recovery
```

Recovery admits a new artifact produced by the trusted builder and signing key, binds that digest through deployment and runtime state, changes credential discovery from detection-only to prevention, and reconciles terminal order and payment outcomes. Verification rejects an unhealthy window, then requires two cadence-adjacent healthy windows. It proves that old automation and payment authority fail, the old digest is unavailable, known intrusion detection still fires, and every trusted descendant is re-derived from trusted or replaced roots. `trust_restored` is computed from those criteria; only then does verification reactivate the runtime contract, unfreeze deployment, and close the incident.

## 5. Production reality

**Best Practice:** rebuild from independently justified roots, invalidate every modeled path to the compromised descendants, and make old-authority failure as important as new-authority success.

**Production Practice:** use dedicated recovery identities and environments, hardware-backed key rotation, immutable provenance, registry and node cache purge controls, GitOps pause and resume gates, durable queue snapshots, provider reconciliation, synchronized evidence windows, and heightened monitoring. Require named owners to accept residual scope limits before traffic return.

A real recovery window should span enough time and workload diversity to expose recurrence. Two modeled windows teach the gate; production duration must follow service behavior, queue depth, scheduled automation, credential lifetimes, and the attacker’s plausible re-entry timing.

## 6. What changed

| Before | After |
|---|---|
| Known attacker actions were contained. | **Modeled mechanisms that could restore authority are invalidated.** |
| Trust roots had mixed and implicit status. | **Roots, descendants, owners, and scope limits are explicit.** |
| The compromised digest remained in the operational chain. | **A new digest binds trusted source, build, admission, deployment, and runtime state.** |
| Automation rotation meant issuing a replacement. | **The old subject is denied and the replacement is narrowly authorized.** |
| Business state was preserved but not fully recovered. | **Terminal order and payment outcomes reconcile across recovery windows.** |
| Trust restoration was deliberately false. | **Trust is restored within the declared inventory and evidence limits.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Eradication and rebuild contract | `recovery/eradication-plan.yaml`, `recovery/rebuild-manifest.yaml` | They preserve invalidation order, trusted roots, rotation scope, and the rebuilt chain. |
| Verified recovery report | `build/chapter-15-recovery-verification.json` | It separates mechanism, decision, outcome, and recovery evidence while retaining explicit limitations. Regenerate it from `make chapter-15-verify-recovery`; it is not a substitute for the committed eradication and rebuild contract. |

## What You Learned

Recovery is not the reversal of containment. It is a new trust decision supported by replaced roots, rejected old authority, reconciled business state, active detection, and sustained evidence. The durable outputs are the eradication/rebuild contract and the bounded recovery-verification report.

### Prove It

> **Independent Practice — Recover from a compromised deployment controller**
>
> Design a trust inventory and recovery sequence when the controller credential and desired-state store are both suspect but the production database remains authoritative.

Specify the roots to replace, descendants to reconcile, cache and controller invalidation, clean rebuild chain, business-state gates, consecutive evidence windows, and limitations on the restored-trust claim.

## Next

Northwind can now restore trustworthy operation after one modeled compromise. Chapter 16 turns the incident’s control, exception, detection, containment, eradication, and recovery evidence into sustainable governance without replacing risk reasoning with compliance ceremony.
