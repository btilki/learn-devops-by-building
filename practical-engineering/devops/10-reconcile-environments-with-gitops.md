# 10 — Reconcile Environments with GitOps

> **Outcome:** Continuously reconcile reviewed production intent through a bounded pull controller, then stop and recover when validly reviewed intent is operationally harmful.

**Current Northwind state:** Chapters 2 and 7 define verified digest handoffs, but release automation and operators still need an enforceable path from reviewed intent to actual environment state.  
**Prerequisites:** Chapters 1–9, declarative Kubernetes configuration, and repository protection fundamentals.  
**Implementation:** `books/practical-engineering/labs/devops/northwind/`  
**Guided time:** approximately 100–130 minutes.

## 1. A reviewed repository is not yet reconciliation

Northwind's release job can identify the verified candidate digest, but it writes directly to the cluster. The same identity can propose, apply, and effectively approve production changes. Manual drift remains until someone notices it, while plaintext secrets can enter the declared state.

> How can Northwind make the reviewed repository authoritative without turning either release automation or the reconciliation controller into an unrestricted production principal?

> **Practice — Establish the push-based baseline**
>
> Check out the direct-write design and prove source, handoff, controller authority, reconciliation, exception, and recovery contracts are red.

```bash
cd books/practical-engineering/labs/devops/northwind
git switch -c my-chapter-10 chapter-10-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-10-baseline
```

## 2. The production model: declared intent plus continuous feedback

> *Theory — Pull-based reconciliation authority*
>
> Decide which system may propose, approve, observe, and apply a production transition without allowing any one mechanism to approve itself.

GitOps is not “configuration stored in Git.” The OpenGitOps principles require desired state to be declarative, versioned and immutable, pulled automatically, and continuously reconciled. [OpenGitOps principles](https://opengitops.dev/).

```text
verified artifact → proposed repository change → protected review
                                                   ↓
actual cluster ← bounded reconciler pulls ← versioned desired state
       │                                           ↑
       └──── health + drift evidence ──────────────┘
```

Repository history proves what intent was accepted. The controller observes actual state and attempts convergence. Neither mechanism proves the intent is safe: review can approve a harmful value, health can be misleading, and a powerful controller can amplify error quickly. Production GitOps therefore combines separation of authority, bounded application, health feedback, and an explicit recovery path.

## 3. Make production intent reviewable and safe to store

> **Practice — Protect source and promotion handoff**
>
> Require safe production intent, then separate candidate proposal, review, and evidence-backed stable promotion.

Edit `gitops/reconciliation.json`. Set the source to declarative and versioned, protect the production path, require `verified-digest`, and set secrets to `references-only`.

The repository stores the Chapter 2 digest and Chapter 7 rollout contract, not a mutable image tag. It stores references understood by Chapter 5's credential delivery path, not payment keys, database passwords, or projected tokens. Repository encryption can reduce accidental disclosure but does not make broad decryption authority safe; identity and audit boundaries still apply.

Protect changes by path and environment. Require review from owners who understand the affected production boundary, prevent self-approval, retain the evaluated revision, and rerun policy when the branch changes. A review accepted against an older revision is not evidence for newly pushed content.

Application configuration follows the same authority path, but it has a different identity from the binary. Edit `gitops/config-delivery.json`: reference Chapter 4's runtime contract, require protected review, promote configuration through development, staging, and production, and keep `artifact_and_config_separate` true. A timeout change should not require rebuilding the image, and deploying a new image must not silently change the accepted configuration. Record both identities in deployment evidence.

Set application of a candidate to `validate-then-atomic`, retain the last-known-good configuration when runtime evidence fails, and report the active configuration version. Schema validation proves shape and type; it does not prove production behavior. The promotion gate must therefore combine Chapter 4 validation with Chapter 6 rollout evidence.

## 4. Close the candidate and stable handoff

Set `release_automation` to `propose-change`, `merge_authority` to `protected-review`, and the candidate field to `candidate_artifact`. Set the stable transition to `reviewed-after-rollout-verification`.

This completes the contract promised in Chapters 2 and 7:

1. The build produces and verifies a digest.
2. Release automation proposes that digest as the candidate; it cannot merge or reach the cluster.
3. The reconciler observes the merged candidate intent and supplies it to the rollout controller.
4. The rollout controller advances, pauses, or aborts using Chapter 7 evidence.
5. After 100% exposure and recovery verification, protected automation proposes copying the candidate digest to stable.
6. Review accepts or rejects that transition; the reconciler applies accepted intent.

An abort leaves stable unchanged and retains the failed candidate revision. Do not silently edit Git history or relabel a digest to make the repository appear green.

## 5. Bound the reconciliation controller

> **Practice — Give the controller only the authority it needs**
>
> Switch to pull reconciliation, make repository access read-only, scope cluster writes to Northwind's namespace, and use Chapter 5 workload identity.

Set controller mode to `pull`, repository access to `read`, cluster scope to `northwind-namespace`, workload identity to true, and `can_write_source` to false.

Pull removes production cluster credentials from **CI (Continuous Integration)** and release jobs. It does not justify cluster-admin for the controller. Separate controllers or service accounts by environment and trust boundary; restrict resource kinds, namespaces, and privileged fields; and prevent one tenant's desired state from creating identities that escape its boundary.

The controller can report status outside the desired-state repository through deployment events or an evidence channel. It cannot merge a revert, change approval rules, or rewrite the declaration it consumes. Otherwise a compromised reconciler can manufacture both intent and evidence.

## 6. Classify drift, pruning, and dependency order

> **Practice — Define continuous but bounded convergence**
>
> Detect drift continuously, self-heal only classified safe differences, guard deletion, order dependencies, and stop unhealthy synchronization after a finite wait.

Enable continuous reconciliation and drift detection. Set self-heal to `safe-drift-only`, pruning to `allowlisted-with-confirmation`, dependency ordering to true, use the illustrative 900-second health timeout, and set failed health action to `pause-and-alert`.

Not every difference should be overwritten automatically. Replica drift inside an owned Deployment may be safe to reconcile; an emergency scale-up, changed persistent-volume claim, or unknown cluster resource needs classification. Chapter 3's rule still holds: drift is a difference before it is a defect.

Pruning is more dangerous than applying an additive field. Allowlist resources the controller owns, preview deletions, protect stateful objects, and define orphan handling. Dependency order prevents an application from racing its namespace, identity binding, policy, migration, or custom-resource definition. Argo **CD (Continuous Delivery)**, for example, applies sync waves in order and waits for earlier out-of-sync or unhealthy waves before progressing. [Argo CD sync waves](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/).

A timeout stops indefinite automation; it does not prove rollback. Values depend on startup, migration, and controller behavior and must be tuned with observed evidence.

## 7. Make emergency divergence temporary

> **Practice — Bound exceptions and run the reconciler trace**
>
> Require temporary, audited divergence, then execute proposal, denial, pull, pause, reviewed revert, and recovery transitions.

Enable all exception controls.

An operator may need to suspend reconciliation before an emergency change. Record who suspended it, why, affected scope, current and expected state, expiry, and recovery owner. Apply the same rule to an emergency application-configuration override: bind it to an individual identity, cap its lifetime, audit it, and automatically remove it at expiry. Before expiry, either encode the emergency state in a reviewed change or deliberately reconcile it away. A forgotten suspension or override creates unmanaged state while dashboards still advertise GitOps.

Run the deterministic local reconciler before the acceptance checkpoint:

```bash
make chapter-10-trace
make chapter-10-config
make chapter-10-checkpoint
```

The trace executes state transitions rather than accepting enum values as behavior. It attempts a direct cluster write from release automation, proposes and merges a harmful candidate, pulls it, reaches the health timeout, pauses while preserving the source revision and stable artifact, denies a controller source rewrite, merges a distinct reviewed recovery revision, and reconciles back to healthy state. Inspect the ordered events and final state; the checkpoint independently requires those transitions.

The configuration trace proposes reviewed `config-v2`, promotes it through development and staging, and then observes a 0.91 production order-success ratio against the illustrative 0.995 gate. It must freeze the candidate, keep `config-v1` active, leave the artifact digest unchanged, and recover through a reviewed configuration revert. It also advances beyond an emergency override's expiry and proves that the override is removed and represented by a backport revision. These transitions distinguish review, validation, runtime acceptance, active state, and recovery instead of treating a changed file as successful configuration delivery.

This remains a deterministic local control-plane simulator, not a running Git server, Kubernetes cluster, or Argo CD installation. It proves the authority and state-machine contract without requiring external infrastructure. Production must additionally test repository outage, controller restart, webhook loss, polling delay, identity expiry, policy-engine failure, partial sync, cluster unreachability, deletion protection, and multiple controllers claiming the same object.

## 8. Stop faithfully applying harmful intent

**Severity:** reviewed candidate degrades order processing while reconciliation repeatedly attempts convergence.  
**Potential blast radius:** the candidate cohort and resources owned by the Northwind production controller.  
**Bounded by:** immutable candidate identity, progressive traffic, health timeout, paused retry, namespace scope, protected stable intent, and reviewed recovery.  
**Primary principles:** reconciliation, trustworthy evidence, explicit contracts, blast-radius control, and recovery.

> **Practice — Exercise a harmful reviewed revision**
>
> Apply a validly reviewed candidate whose runtime and order evidence degrades, then prove the controller pauses without rewriting source or disturbing stable traffic.

```bash
make chapter-10-break
```

The report must show `review_does_not_equal_safe`, `controller_stops_amplification`, `stable_traffic_is_preserved`, `controller_does_not_rewrite_intent`, and `recovery_requires_health_evidence` as true. These results come from the executed trace: the failure fixture supplies observations, while the state machine decides whether each actor may transition source or cluster state.

Pause is containment, not recovery. Retain the failed revision, digest, controller events, and rollout evidence. Create a reviewed revert removing the candidate or restoring the last accepted declaration. Reconciliation applies the new revision; then verify stable digest, runtime health, order success and latency, absence of continuing candidate traffic, and no orphaned resources.

### Optional Game Day — Contain a synchronization storm

> **Game Day — Reconcile without overwhelming the control plane**
>
> Start three controllers against the same reviewed revision, degrade the control plane, and prove global coordination bounds application, unhealthy dependencies stop later waves, pruning is suspended, retries are staggered, and source remains unchanged.

Run the deterministic exercise:

```bash
make chapter-10-game-day
```

The fixture gives each of three controllers demand for eight concurrent applies, while the shared contract permits ten and the degraded control plane can tolerate twelve. The simulator must therefore report a peak of ten—not eight per controller and not twenty-four in aggregate. It applies the six-resource foundation wave, then the twenty-four-resource workload wave. Unhealthy workload evidence prevents the optional twenty-resource wave, seven requested prunes become zero, and the reviewed source revision remains `7f21storm`.

These values are illustrative. In production, derive concurrency from measured control-plane latency and throttling, controller count, object size, admission cost, and recovery demand. Inject the event in a non-production environment first; define abort conditions, observers, evidence retention, and restoration ownership before starting. A green local trace proves the decision model, not a running controller or Kubernetes control plane.

## 9. Production reality

**Best Practice:** keep desired state declarative and versioned, pull it through a continuously reconciling controller, separate proposal from approval, use immutable artifacts and secret references, bound controller authority, and recover through reviewed intent.

**Production Practice:** classify self-heal and prune behavior per resource, test repository and controller failure, model propagation time, coordinate concurrency across controllers, isolate environments, constrain custom resources, protect stateful deletion, validate health semantics, control emergency suspension, and retain a non-Git recovery path for loss of the repository or controller. Chapter 13 will exercise restoration of those control-plane dependencies.

## 10. What changed

| Before | After |
|---|---|
| Release automation wrote directly to production. | It proposes a verified digest for protected review. |
| The controller could change its own source. | It reads desired state and reports evidence through a separate path. |
| Tags and plaintext secrets entered declarations. | Digests and identity-backed secret references are required. |
| Drift and deletion behavior were implicit. | Detection, classified self-heal, guarded pruning, and ownership are explicit. |
| Synchronization retried unhealthy state forever. | Health timeout pauses amplification and retains stable traffic. |
| Emergency suspension could become permanent. | Exceptions expire, remain audited, and require backport or reconciliation. |
| Binary and application configuration changed as one implicit release. | Independently identified configuration is reviewed, promoted, reconciled, and recovered against the Chapter 4 runtime contract. |

## Durable outputs

- Reconciliation authority contract: `gitops/reconciliation.json`.
- Application configuration delivery contract and executable promotion trace: `gitops/config-delivery.json` and `tools/config_delivery.py`.

## What You Learned

GitOps makes reconciliation continuous; it does not make declared intent correct. You can now connect verified artifact and application-configuration promotion to a protected repository, bound a pull controller with workload identity, classify drift and pruning, stop unhealthy convergence, manage emergency divergence, and recover through a reviewed revision without allowing automation to approve itself.

### Prove It

> **Independent Practice — Reconcile two production clusters safely**
>
> Extend Northwind to a second cluster that must trail the first by at least 30 minutes and may run a different secret-provider integration.

Define repository layout, promotion order, digest identity, controller subjects and scopes, health evidence, minimum soak, environment-specific references, drift ownership, partial-promotion recovery, emergency suspension, and the reviewed condition that advances or reverts the second cluster. Explain how correlated bad intent is bounded when both controllers trust the same repository.

## Next

Northwind now continuously reconciles reviewed production intent. Chapter 11 measures and controls the capacity and cost consequences of that delivery system without trading away reliability evidence.
