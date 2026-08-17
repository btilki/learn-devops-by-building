# 07 — Release Progressively and Abort Safely

> **Outcome:** Expose a bounded production cohort to an immutable candidate, advance only on sufficient user-impact evidence, and prove abort restored the prior stable release.

**Current Northwind state:** Chapter 6 explains production behavior, but deployment still exposes every user before evaluating that evidence.  
**Prerequisites:** Chapters 1–6 and basic rollout-controller familiarity.  
**Implementation:** `books/labs/devops/northwind/`  
**Guided time:** approximately 90–120 minutes.

## 1. Ready candidate, failed orders

Northwind deploys `storefront-api:latest` to 100% of traffic. The new Pods are Ready, but order success falls to 88% and **p95 (95th percentile)** latency rises to 2.3 seconds because payment calls fail. Stable was serving 99.8% successfully.

> How can Northwind limit exposure, make progression an evidence-based decision, and prove rollback restored the exact prior release?

> **Practice — Establish the all-at-once baseline**
>
> Check out the unsafe rollout and prove that cohort, evidence, authority, abort, and rollback contracts are red.

```bash
cd books/labs/devops/northwind
git switch -c my-chapter-07 chapter-07-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-07-baseline
```

## 2. The production model: rollout as feedback control

> *Theory — Bounded exposure and evidence-driven progression*
>
> Decide when a release controller should advance, pause, or abort without confusing runtime readiness with user success.

A rolling update controls replacement rate. A canary controls exposure and evaluates the candidate against a stable control. Kubernetes availability proves Pods satisfy runtime contracts; it does not prove customers can complete orders. Google defines canarying as a partial, time-limited production deployment whose evaluation determines whether rollout proceeds. [Canarying releases](https://sre.google/workbook/canarying-releases/).

```text
immutable candidate
        ↓
bounded cohort → enough evidence? ── no ─→ pause
        │ yes
        ↓
success and latency pass? ── no ─→ abort → stable digest → verify recovery
        │ yes
        ↓
advance exposure
```

The controller needs three outcomes. **Advance** means evidence is sufficient and acceptable. **Pause** means evidence is inconclusive—often low traffic or missing telemetry. **Abort** means evidence is sufficient and unacceptable. Treating missing data as success converts telemetry failure into uncontrolled progression.

## 3. Preserve stable and candidate identity

> **Practice — Pin both sides of the comparison**
>
> Replace mutable tags with exact stable and candidate digests and make rollback target the same stable identity.

Edit `delivery/rollout.json`. Set `stable_artifact` and `candidate_artifact` to `name@sha256:digest` references. Set `rollback.target` to exactly the stable reference.

The fixture's repeated `a` candidate digest is visibly illustrative. In production, the candidate digest must come from Chapter 2's verified release path. A human-friendly tag may coexist, but comparison, promotion, and rollback use digests. Otherwise “rollback” can resolve to different bytes from those previously observed.

Close the handoff explicitly in the same contract:

```json
"handoff": {
  "candidate_source": "verified-release-digest",
  "proposal_path": "reviewed-delivery-change",
  "promotion_path": "controller-authored-reviewed-change",
  "stable_transition": "copy-candidate-after-100-percent-and-recovery-verification"
}
```

Chapter 2 produces the verified digest. A reviewed delivery change writes that digest to `candidate_artifact`; the rollout controller may observe it but cannot invent another artifact. After the 100% stage and final recovery verification pass, protected automation proposes a reviewed change copying the candidate digest to `stable_artifact`. An abort leaves stable unchanged. This closes the source-to-artifact-to-infrastructure chain introduced in Chapters 2 and 3; Chapter 10 will automate reconciliation of the reviewed delivery repository rather than redefine ownership.

## 4. Bound exposure and require evidence

> **Practice — Define progressive cohorts**
>
> Replace 100% initial exposure with monotonic 5%, 25%, 50%, and 100% stages separated by observation pauses.

```json
"steps": [
  {"traffic_percent": 5, "pause_seconds": 300},
  {"traffic_percent": 25, "pause_seconds": 600},
  {"traffic_percent": 50, "pause_seconds": 900},
  {"traffic_percent": 100, "pause_seconds": 0}
]
```

These cohort sizes and pauses are Northwind teaching values. Low traffic may require longer windows or synthetic transactions; high-risk changes may require smaller cohorts. Cohort assignment must avoid bias—for example, routing only internal users to canary can hide production behavior.

> **Practice — Gate progression on volume and outcomes**
>
> Require enough candidate requests, order success and latency limits, automatic abort, and pause on inconclusive evidence.

Configure at least 50 candidate requests, minimum success `0.995`, maximum latency p95 `750` milliseconds, and both `order_success_ratio` and `order_latency` indicators. Set `automatic_abort: true` and `inconclusive_action: pause`.

A **SLI (Service-Level Indicator)** threshold in rollout policy is not automatically the long-window **SLO (Service-Level Objective)** from Chapter 6. The release gate may be stricter and shorter, but its eligibility rules must remain compatible. Minimum sample volume prevents a candidate from advancing after one lucky request; it does not make a small sample statistically representative.

## 5. Protect promotion and verify the contract

> **Practice — Separate rollout observation from promotion authority**
>
> Require the protected production release identity to advance traffic and require post-rollback indicator verification.

Set `promotion_authority` to `production-release-approver` and `rollback.verify_indicators` to true. In a real controller, repository environment protection, deployment identity, traffic-router authority, and audit events must enforce these names.

> **Practice — Verify the controller contract**
>
> Check immutable identities, reviewed candidate/stable handoffs, bounded monotonic cohorts, evidence sufficiency, user-impact gates, pause/abort behavior, protected promotion, and rollback recovery together.

```bash
make chapter-07-checkpoint
```

The local contract models controller decisions. Production must also test routing accuracy, telemetry freshness, controller availability, concurrent rollouts, and what happens when abort cannot update the traffic provider.

## 6. Abort a Ready but harmful candidate

**Severity:** candidate order-submission failure; stable remains healthy.  
**Potential blast radius:** the configured 5% canary cohort.  
**Bounded by:** immutable identities, limited traffic, minimum evidence, and automatic abort.  
**Primary principles:** blast-radius control, trustworthy evidence, explicit contracts, and recovery.

> **Practice — Prove automatic abort and stable recovery**
>
> Evaluate the failing payment candidate and verify that readiness cannot override user-impact evidence.

```bash
make chapter-07-break
```

The fixture supplies 50 candidate requests, 88% order success, 2.3-second latency, and `ready: true`. The result must show `ready_is_not_success`, `candidate_aborts`, and `stable_remains_healthy` as true.

Abort is an action, not recovery. Production recovery requires traffic returned to the stable digest, order indicators back within policy, no continuing candidate traffic, and retained candidate-specific traces and logs. Do not erase the evidence by immediately relabelling the failed digest.

## 7. Production reality

**Best Practice:** canary immutable artifacts, expose a bounded cohort, require sufficient user-impact evidence, pause uncertainty, and automate abort.

**Production Practice:** account for low traffic, cohort bias, delayed failures, telemetry gaps, stateful compatibility, traffic-router failure, overlapping releases, and rollback that cannot undo external side effects. Kubernetes Deployment progress reports replica availability and stalled rollout mechanics; business-result analysis requires an additional controller or release system. [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).

## 8. What changed

| Before | After |
|---|---|
| Every user received the candidate immediately. | Exposure advances through bounded cohorts. |
| Tags identified stable and rollback targets. | Digests preserve exact stable and candidate identity. |
| Digest handoff and stable promotion were implicit. | Reviewed changes carry verified candidates in and promote stable only after full verification. |
| Readiness implied release success. | Order success, latency, and volume control progression. |
| Missing evidence had no defined action. | Inconclusive analysis pauses. |
| Rollback was a mutable action. | Abort restores the stable digest and requires recovery evidence. |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Progressive-delivery decision contract | `delivery/rollout.json` | It binds stable and candidate digests to cohort steps, evidence volume, advance/pause/abort decisions, promotion authority, and recovery verification. |
| Rollout conformance evidence | `evidence/chapter-07-green.json` | It preserves the verified controller policy that future threshold, routing, or authority changes must intentionally replace. |

## What You Learned

Progressive delivery is a feedback controller, not merely a slower Deployment. You can now preserve stable and candidate identity across a reviewed handoff, bound initial exposure, separate insufficient evidence from failed evidence, gate advancement on user-visible outcomes, and distinguish an abort action from verified service recovery.

### Prove It

> **Independent Practice — Design a low-traffic release policy**
>
> Adapt the rollout for a service that receives only 20 valid orders per hour but has high financial impact.

Specify cohort assignment, minimum evidence, maximum wait, synthetic evidence, pause and human-review rules, success and latency gates, rollback identity, delayed-failure monitoring, and the conditions under which the release may never advance automatically.

## Next

Northwind can now control stateless release risk. Chapter 8 changes persistent data while old and new application versions coexist.
