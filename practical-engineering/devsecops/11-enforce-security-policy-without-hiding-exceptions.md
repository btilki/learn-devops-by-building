# Enforce Security Policy Without Hiding Exceptions

Chapters 4 through 10 created policies for identity, privilege, source, release, vulnerabilities, secrets, and data. A policy document changes nothing unless Northwind places it at a boundary that can decide, records what happened, and prevents exceptions from becoming invisible permanent authority.

## 1. Release pressure becomes policy

A release manager proposes one broad waiver that disables dependency and production-admission checks, covers every change, has no compensating detection, and never expires. No attacker is required; organizational pressure alone can reopen the compromised-maintainer path.

Work from the lab working tree using the How to Use This Book procedure. From the DevSecOps lab root, run:

```bash
make chapter-11-baseline
```

```text
chapter 11 baseline: permissive exception policy admitted a placebo release waiver
```

## 2. The production model: intent, placement, decision, exception

> *Theory — Enforcement points and failure behavior*
>
> This model enables Northwind to turn policy intent into consistent decisions without hiding operational trade-offs.

Policy intent states the outcome. A rule makes a testable condition. An enforcement point has the context and authority to allow, deny, transform, or observe a transition. Decision evidence binds input identity, rule, policy version, result, reason, and exception.

| Choice | Appropriate use | Principal risk |
|---|---|---|
| Admission enforcement | Unsafe state must not cross a boundary | Verifier outage can block safe work |
| Runtime enforcement | Context exists only during use | Latency or availability couples to policy engine |
| Detection-only | Prevention is impossible or too risky | Harm may occur before response |
| Fail-closed | Missing decision is more dangerous than interruption | Availability loss |
| Fail-open | Continuity is more important for this bounded transition | Silent unsafe admission |

Central policy improves consistency and review but can lose local context. Local policy understands its system but can drift or be bypassed. Northwind therefore governs a versioned bundle while declaring where each rule is enforced and which context that point supplies.

An exception is a bounded policy decision, not the absence of policy. It needs an owner, rationale, narrow scope, affected enforcement points, compensating controls, evidence, effective time, expiry, and removal path.

## 3. Place rules and govern deviations

> **Practice — Map every rule to an enforcement point**
>
> Declare where source, deployment, data, and detection decisions occur.

Open `policy/bundle/rules.yaml` and `policy/enforcement-points.yaml`. Dependency policy runs at source merge, release policy at production deployment, and field policy at data query. The `runtime-observation` point is detection-only for `data-field-access`; Chapter 12 still prevents shell execution and undeclared egress. Every point requires a decision log and names its failure mode.

> **Practice — Make exceptions visible and expiring**
>
> Preserve scope, ownership, compensation, evidence, expiry, and removal.

Open `policy/exception-policy.yaml` and `policy/exceptions.yaml`. The governance policy caps exceptions at four hours, forbids wildcard and release-wide scopes, rejects placeholder compensation, requires independent compensation points and multiple evidence items, and marks production release admission non-exceptable. A registry-mirror outage permits one locked dependency at source merge for two hours. Hash verification and runtime resolution alerts compensate at a point independent of source merge.

The evaluator uses the explicit `evaluation_time` in exception policy so exercises remain deterministic. Production evaluation must use a trustworthy current clock and preserve that instant in its decision evidence.

Run:

```bash
make audit
make chapter-11-checkpoint
```

The checkpoint consumes each rule's `unsafe_result`: a deny rule must have at least one fail-closed placement, not merely a detection point. It also verifies supported failure behavior, required logging, and exceptions against the reviewable governance policy. The lab does not deploy a repository rule, admission controller, or distributed policy service; production must verify real enforcement and decision delivery under dependency failure.

## 4. Test the design under failure

### Independent control failure — Release pressure creates a permanent bypass

> **Practice — Reject organizationally created trust expansion**
>
> Evaluate a broad, non-expiring exception that disables dependency and release admission.

**Severity:** critical; the bypass removes independent supply-chain enforcement.  
**Plausible harm:** untrusted dependency or artifact admission, production compromise, and concealed release authority.  
**Potential blast radius:** every source change and production deployment covered by the wildcard.  
**Bounded by:** rule-specific scope, named enforcement points, compensation, evidence, expiry, logging, and automatic removal.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence, reconciliation, and recovery.

#### Security questions

- **Asset and harm:** Release authority and correct production outcomes drive rejection.
- **Trust and authority:** Delivery urgency grants no authority to erase dependency and admission policy.
- **Detection after prevention fails:** Generated decision logs identify requester context, point, rule, policy version, denial reasons, and exception reference.
- **Evidence of restored trust:** Not yet applicable. Chapter-local correction: the broad bypass is absent, any narrow exception expires, and ordinary enforcement produces consistent decisions again.

#### Diagnosis

Run `make chapter-11-attack`. The evaluator independently rejects the wildcard scope, unknown all-rules target, missing compensation, missing evidence, absent expiry, and absent removal path. It writes the attempted bypass into generated exception state, emits `build/chapter-11-attack-decision.json`, and appends the requester-bound decision to `build/chapter-11-decisions.jsonl`.

#### Containment

Run `make chapter-11-contain`. It replaces the bypass in generated state with the reviewed mirror exception: one rule, one point, one dependency, independent compensating detection, evidence, and two-hour expiry. The generated decision preserves requester context, policy version, and exception reference.

#### Recovery

Run `make chapter-11-recover`. Recovery advances beyond the exception deadline, proves it is rejected as expired, transitions generated exception state to an empty list, verifies both the broad bypass and narrow exception IDs are absent, and evaluates the bundle with no exceptions to prove blocking enforcement resumes.

## 5. Production reality

**Best Practice:** place policy at the boundary with sufficient context and authority, then make every deviation narrower and shorter than the rule it relaxes.

**Production Practice:** version bundles, test decisions before rollout, retain allow and deny evidence, define verifier-outage behavior per point, measure exception age, alert before expiry, and reconcile configured points with actual infrastructure. Emergency policy must remain usable during the failure it addresses without becoming a general fail-open switch. Kubernetes admission controllers illustrate one production enforcement point: they can deny objects before persistence, and their failure mode is a cluster-level availability decision. [Admission controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/).

## 6. What changed

| Before | After |
|---|---|
| Policies existed as disconnected files. | **Every rule maps to a named enforcement point.** |
| Failure behavior was accidental. | **Fail-closed and detection-only choices are explicit.** |
| Decisions lacked a stable interpretation. | **Policy version, point, result, reason, and exception are retained.** |
| Waivers disabled broad control families. | **Exceptions are narrow, owned, compensated, evidenced, and expiring.** |
| Removing a ticket implied recovery. | **Normal enforcement is re-evaluated without bypass state.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Enforcement-point map | `policy/bundle/rules.yaml` and `policy/enforcement-points.yaml` | They preserve rule ownership, placement, failure behavior, and evidence obligations. |
| Exception register | `policy/exceptions.yaml` | It keeps deviations scoped, owned, compensated, evidenced, expiring, and removable. |

## What You Learned

Policy becomes security only at a real decision boundary. Central intent and local context must meet in versioned, reviewable decisions. Exceptions are temporary governed decisions whose scope, compensation, evidence, expiry, and removal are as important as their rationale.

### Prove It

> **Independent Practice — Design an identity-provider outage exception**
>
> Preserve one legitimate containment action without converting an authentication outage into general fail-open production access.

Specify point, rule, subject, action, resource, duration, evidence, compensation, approver, logging, expiry, removal, and the check that proves ordinary identity enforcement resumed.

## Next

Policy now governs expected transitions and visible exceptions. Chapter 12 constrains workloads that reach runtime and detects behavior outside their process, filesystem, identity, privilege, and network contracts.
