# Turn Risk into Owned Control Decisions

Northwind has explicit assets, harms, invariants, trust boundaries, and attack paths. It can explain how a compromised maintainer might introduce a malicious dependency and progress toward production payment authority. It also models a valid support session accessing data beyond its purpose.

Those paths do not decide what Northwind should do first. A threat model describes plausible routes to harm. Risk work compares their context, uncertainty, impact, and urgency, then assigns an accountable treatment. Without that step, severity labels and tool queues quietly become decision makers.

## 1. A critical label without a risk decision

A weak record says:

```yaml
id: scanner-critical
severity: critical
treatment: fix-now
```

It does not identify a deployed asset, attack path, exposure, reachability, business harm, uncertainty, owner, residual risk, or review trigger. “Critical” may justify immediate investigation. It cannot complete the decision.

Work from the lab working tree using the Chapter 0 procedure. From the DevSecOps lab root, run:

```bash
make chapter-03-baseline
```

The baseline succeeds when the evaluator rejects the score-only record:

```text
chapter 03 baseline: score-only risk decision correctly rejected
```

## 2. The production model: risk is owned uncertainty about harm

> *Theory — Contextual risk and control portfolios*
>
> This model enables Northwind to select proportionate treatment without mistaking numeric precision, severity, or compliance status for a production decision.

### Likelihood and impact are judgments supported by evidence

Risk concerns uncertainty about whether a threat will cause harm and how serious that harm would be. Northwind uses qualitative labels—low, medium, high, and critical—because the available evidence does not support precise probabilities or universal financial values.

| Dimension | Question | Relevant evidence |
|---|---|---|
| Exposure | How can the actor reach the prerequisite or boundary? | Network path, identity access, deployment state, feature use |
| Likelihood | How plausible is progression under current conditions? | Known exploitation, control strength, frequency, attacker capability |
| Impact | Which asset and harm can be affected, and how far can it spread? | Payment scope, data sensitivity, business outcome, reversibility |
| Uncertainty | What important fact is missing, stale, or assumed? | Incomplete telemetry, unknown reachability, untested provider behavior |

A qualitative label must not hide reasoning. Two teams can assign “medium” for different reasons. The record must preserve those reasons so later evidence can challenge them.

### Inherent and residual risk answer different questions

Inherent risk considers the path before the selected control portfolio. Residual risk describes what remains after existing and planned controls operate as expected.

Residual risk is never automatically zero. Independent approval can reduce the chance of one compromised maintainer approving a sensitive change. It does not eliminate collusion, reviewer error, identity compromise, build misuse, or runtime behavior that prevention did not anticipate.

### Treatment is a decision, not a status

Northwind can:

- **Mitigate** by reducing likelihood or impact;
- **Avoid** by removing the risky activity or authority;
- **Transfer** defined consequences through another party or contract without transferring accountability for every harm;
- **Accept** residual risk through an authorized, evidenced, time-aware decision; or
- **Monitor** uncertainty while preserving triggers that force reassessment.

“Open,” “in progress,” and “backlog” are workflow states, not treatments.

### Controls should cover failure, not merely prevention

A priority path needs a portfolio when no single mechanism can make its assumptions true:

| Control role | Purpose on the maintainer path |
|---|---|
| Prevent | Require independent approval and admit dependencies only from governed origins. |
| Detect | Correlate unusual source, identity, admission, and runtime behavior. |
| Respond | Revoke affected authority and isolate the path before harm expands. |
| Recover | Rebuild affected artifacts and workloads from trusted roots and reconcile outcomes. |

Defense in depth is not the number of tools. Controls are complementary when their failure modes and evidence are sufficiently independent.

## 3. Make the risk and control decisions

> **Practice — Record contextual risk**
>
> Tie each treatment to a real attack path, affected assets, exposure, likelihood, impact, uncertainty, owner, and review trigger.

Open `risk/risk-register.yaml`. The cumulative path is recorded as externally exposed, medium likelihood, and critical impact. More important than those labels are the preserved uncertainties:

```yaml
uncertainty:
  - maintainer-session-compromise-rate
  - dependency-review-effectiveness
  - runtime-detection-coverage
treatment: mitigate
residual_risk: >-
  A valid session may still influence reviewed source; independent admission
  and runtime detection must bound progression.
```

The record does not convert unknowns into invented decimals. It makes them reviewable and gives later identity, supply-chain, and detection chapters a reason to produce better evidence.

> **Practice — Select complementary controls**
>
> Choose controls according to where they interrupt, reveal, contain, or recover the attack path.

Open `risk/control-decisions.yaml`. The maintainer decision includes prevention, detection, response, and recovery. Its rationale states why one identity or source control is insufficient. It also names expected evidence, an owner, a due date, and a material-change trigger.

A control without expected evidence cannot be evaluated. A due date without an owner is a reminder, not accountability. A mitigation without residual risk implies unjustified certainty.

> **Practice — Compare risk rather than compare labels**
>
> Explain why an exposed high-impact authorization path can outrank a critical but unreachable finding.

The support-data path has high impact and internal exposure. Its valid identity makes misuse plausible even without stolen credentials. A scanner finding labeled critical but absent from deployed code may require verification and monitoring, while the active support boundary requires treatment now.

This does not mean unreachable equals harmless. Reachability evidence can be wrong or change. Record the uncertainty and review trigger instead of deleting the finding.

### Prove the capability

Run:

```bash
make audit
make chapter-03-checkpoint
```

The checkpoint verifies known attack paths and assets, explicit uncertainty and residual risk, owned mitigation decisions, and a complete control-role portfolio for the priority cumulative path. It cannot prove that the likelihood label is objectively correct or that the selected controls will work in a real provider.

## 4. Test the decision under failure

### Independent control failure — Severity displaces exposure and harm

> **Practice — Correct a score-driven priority inversion**
>
> Reorder two findings using deployed context, exploitability, harm, uncertainty, and ownership rather than severity alone.

**Severity:** high decision risk; resources can be diverted from an exposed harmful path.  
**Plausible harm:** delayed authorization repair, unauthorized data access, unmanaged residual risk, and false confidence from shrinking critical-count dashboards.  
**Potential blast radius:** every asset governed by the distorted remediation queue.  
**Bounded by:** attack-path traceability, exposure and asset context, authorized ownership, review triggers, and independent evidence.  
**Primary principles:** explicit contracts, trustworthy evidence, reconciliation, and blast-radius control.

#### Security questions

- **Asset and harm:** Priority follows the affected asset and plausible harm, not the scanner's label alone.
- **Trust and authority:** The exposed support role already holds usable authority; the unreachable component may not execute in production.
- **Detection after prevention fails:** Accepted or deferred risks need monitoring tied to the condition that justified the decision.
- **Evidence of restored trust:** Not yet applicable; later chapters must implement and test the selected controls.

#### Diagnosis

The score-only record cannot distinguish theoretical component presence from an active authorization path. It also hides uncertainty and leaves no owner able to revise the decision.

#### Correction

Verify deployment and reachability, preserve uncertainty, prioritize the exposed path according to harm, assign both records an explicit treatment and owner, and define triggers that reopen either decision when evidence changes.

## 5. Production reality

**Best Practice:** use consistent risk criteria and require authorized ownership for treatment and acceptance.

**Production Practice:** calibrate labels against Northwind's assets, operating constraints, fraud exposure, data use, and recovery capability. Do not compare labels across teams until their definitions and evidence expectations are comparable.

Avoid multiplying likelihood and impact numbers merely to produce a ranked decimal. Arithmetic can conceal weak assumptions. Preserve decision context, contradictory evidence, due dates, exceptions, and material-change triggers.

## 6. What changed

| Before | After |
|---|---|
| Severity selected work automatically. | **Attack path, exposure, harm, and uncertainty support an owned priority decision.** |
| Unknown facts disappeared inside a score. | **Uncertainty is explicit and becomes a later evidence requirement.** |
| Mitigation meant adding one preventive tool. | **Complementary prevention, detection, response, and recovery cover different failure modes.** |
| “Backlog” acted as a treatment. | **Mitigate, avoid, transfer, accept, or monitor are explicit decisions.** |
| Passing controls implied no remaining risk. | **Residual risk and review triggers remain visible.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Owned risk register | `risk/risk-register.yaml` | It preserves attack context, assets, exposure, uncertainty, treatment, residual risk, ownership, and review triggers. |
| Control decision register | `risk/control-decisions.yaml` | It records the complementary portfolio, rationale, evidence, deadlines, and owners that later chapters must implement. |

## What You Learned

Risk is owned uncertainty about harm, not a synonym for vulnerability severity. Qualitative labels support decisions only when their context and uncertainty remain visible. Treatments must be explicit, residual risk must survive control selection, and priority paths often require complementary preventive, detective, responsive, and recovery controls.

### Prove It

> **Independent Practice — Decide under incomplete exploitability evidence**
>
> Choose a treatment without converting missing evidence into false numeric certainty.

Northwind finds a high-severity library in `notification-service`. Runtime reachability is unknown, the service has no payment authority, and exploitation could expose confirmation metadata. Compare it with the active support-data path. Record both decisions, their uncertainty, owners, evidence needs, residual risk, and review triggers.

## Next

Northwind has selected owned controls for its priority paths. The first implementation problem is identity: shared accounts, reusable automation credentials, and accumulated roles can make a valid action neither sufficiently attributable nor appropriately authorized.

Chapter 4 makes human and automation access attributable and bounded.
