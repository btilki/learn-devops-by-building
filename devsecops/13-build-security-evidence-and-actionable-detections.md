# Build Security Evidence and Actionable Detections

Chapter 12 produced attributable runtime events. Northwind also has identity denials, supply-chain decisions, privilege attempts, secret evidence, and data decisions. Separate alerts do not reveal whether those observations form one intrusion or unrelated operational noise.

## 1. Four signals, no shared meaning

A credential misuse denial, unusual dependency change, denied elevation, and blocked runtime egress exist in four systems. Each looks locally contained. Together they describe the compromised-maintainer path progressing from identity through source and privilege to runtime.

Work from the lab working tree using the How to Use This Book procedure. From the DevSecOps lab root, run:

```bash
make chapter-12-attack chapter-13-baseline
```

```text
chapter 13 baseline: four valid signals had no detection hypothesis and produced no alert
```

`chapter-12-attack` writes the undeclared-egress event in `runtime/events.jsonl` that the Chapter 13 evaluator joins with the modeled identity, supply-chain, and privilege observations.

## 2. The production model: detect hypotheses, not tool activity

> *Theory — Evidence, correlation, coverage, and telemetry integrity*
>
> This model enables Northwind to turn observations into an owned response decision.

A signal is an observation that may matter. Evidence is a signal interpreted with producer, subject, time, integrity, provenance, and limitations. A detection hypothesis states which attack behavior should produce which evidence, within what window, with which context, and what response follows.

| Element | Required question | Failure mode |
|---|---|---|
| Event contract | Can sources preserve common identity and deployment context? | Parallel security telemetry loses operational traces |
| Hypothesis | Which plausible path should the evidence reveal? | Rules measure generic suspiciousness |
| Correlation | Which shared fields and time window join events? | Unrelated activity becomes one incident |
| Threshold | Which distinct observations are sufficient? | Repeated noise satisfies a count |
| Integrity | Can evidence loss or alteration be detected? | Missing telemetry is interpreted as safety |
| Routing | Who acts, and what action is expected? | Alerts accumulate without reducing harm |
| Coverage | Which path steps remain unobserved? | Dashboards imply universal visibility |

False positives consume response capacity and encourage suppression. False negatives hide harmful behavior. Threshold tuning must preserve the threat hypothesis: requiring distinct actions within a bounded window is safer here than counting repeated authentication denials.

Northwind extends the inherited DevOps telemetry contract rather than building a security-only stack. Deployment identity, traces, service outcomes, and security decisions must remain correlatable.

## 3. Normalize evidence and encode response hypotheses

> **Practice — Define one security event contract**
>
> Require core event fields, then require action-specific identity, session, deployment, and artifact context.

Open `detection/event-contract.yaml`. It defines required core fields, accepted integrity state, retention, and missing-telemetry behavior. The rule adds the context required for each action. Missing or unacceptable context creates a telemetry-gap finding; incomplete events are not silently treated as evidence of absence.

> **Practice — Map the priority attack path to evidence**
>
> Declare required distinct actions, permitted join fields, time window, owner, and response.

Open `detection/hypotheses.yaml` and `detection/rules/correlate-progression.yaml`. The cumulative hypothesis requires four distinct actions within 30 minutes. The evaluator computes the join: identity, dependency, and privilege evidence share the maintainer session; the dependency evidence then bridges to Chapter 12’s emitted runtime event through the admitted artifact digest. No preassigned incident identifier manufactures the relationship. The result routes to `security-response` with the action `investigate-and-isolate-order-worker`.

Run:

```bash
make audit
make chapter-13-checkpoint
```

The checkpoint proves the controlled event set—including the event emitted by Chapter 12—normalizes, correlates, fires, and carries ownership plus response. It also reads the retention and accepted-integrity contract. It does not benchmark a production telemetry pipeline or prove resistance to attacker evasion; real deployments must validate delivery latency, cryptographic or platform-backed integrity, retention enforcement, clock behavior, source coverage, and routing.

## 4. Test the design under failure

### Cumulative attack — Correlate identity, dependency, privilege, and runtime evidence

> **Practice — Detect progression rather than count alerts**
>
> Replay inert normalized observations for the cumulative compromised-maintainer path.

**Severity:** critical; correlated evidence shows progression toward production and payment-related authority.  
**Plausible harm:** malicious release, privilege escalation, secret discovery, exfiltration, and fraudulent business effects.  
**Potential blast radius:** identities, delivery systems, and runtime resources linked by the intrusion correlation.  
**Bounded by:** normalized context, distinct-action threshold, bounded window, telemetry-gap alarms, owned routing, and workload isolation.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence, reconciliation, and recovery.

#### Security questions

- **Asset and harm:** Release authority, payment authority, secrets, data, and order outcomes drive the hypothesis.
- **Trust and authority:** No individual denial proves safety; correlated attempts reveal how authority is being pursued.
- **Detection after prevention fails:** Independent identity, supply-chain, privilege, and runtime producers contribute evidence with integrity and deployment context.
- **Evidence of restored trust:** Not yet applicable. Chapter-local correction: the controlled path still alerts after context correction and noise tuning, with complete response context and explicit coverage limits.

#### Diagnosis

Run `make chapter-13-attack`. The four observations correlate into `build/chapter-13-alert.json`, carrying distinct actions, window, owner, response, and evidence count.

#### Containment

Run `make chapter-13-contain`. It persists a damaged event set with artifact context removed from the dependency event. The normalizer raises a telemetry-gap alarm, excludes the incomplete event, and the cumulative path correctly produces no alert. This demonstrates the detection loss honestly: the independent gap alarm preserves an owned signal, but it does not replace the suppressed attack-path detection.

#### Recovery

Run `make chapter-13-recover`. Recovery reads the persisted damaged event set, restores its artifact digest from `supply-chain/deployment-evidence.yaml`, writes the corrected evidence, and requires that corrected set to produce one actionable alert with all four evidence items. The record states that proof covers only modeled sources and actions; it does not claim universal attacker visibility.

## 5. Production reality

**Best Practice:** begin with a plausible threat hypothesis, require sufficient context for action, and alarm independently when required evidence disappears.

**Production Practice:** normalize into the existing telemetry path, preserve raw provenance, protect clocks and retention, monitor source delivery, test routing, measure time to actionable context, and tune with controlled simulations. Never optimize alert count by suppressing the only evidence covering a priority path. OpenTelemetry remains the inherited signal model; security events must remain correlatable with service and deployment context. [OpenTelemetry signals](https://opentelemetry.io/docs/concepts/signals/), [context propagation](https://opentelemetry.io/docs/concepts/context-propagation/).

## 6. What changed

| Before | After |
|---|---|
| Security events remained tool-specific. | **One contract preserves identity, deployment, policy, and integrity context.** |
| Alert counts represented detection maturity. | **Threat hypotheses define distinct required evidence.** |
| Missing events looked like quiet systems. | **Telemetry gaps alarm independently.** |
| Thresholds counted repeated noise. | **Distinct actions and bounded time establish progression.** |
| Alerts lacked operational consequence. | **Every hypothesis names an owner and response action.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Detection catalog | `detection/event-contract.yaml`, `detection/hypotheses.yaml`, and `detection/rules/` | They preserve event semantics, hypotheses, thresholds, ownership, and response. |
| Attack-path coverage report | Generated `build/chapter-13-recovery.json` plus the hypothesis mapping | It records controlled coverage, complete context, and explicit limitations. Regenerate it from the Chapter 13 recover command; it is not a substitute for the committed detection catalog. |

## What You Learned

Detection engineering connects plausible attack behavior to trustworthy evidence and a specific response. Correlation requires shared identity, deployment, time, integrity, and policy context. Missing telemetry is a finding, repeated noise is not progression, and controlled simulation proves only the declared coverage.

### Prove It

> **Independent Practice — Detect payment-credential misuse**
>
> Correlate secret exposure, unexpected provider use, identity context, and payment-effect divergence without alerting on every ordinary payment request.

Specify required events, correlation, window, integrity, missing-source alarm, owner, response, false-positive boundary, retention, and coverage limitation.

## Next

Northwind can now raise an evidence-rich signal. Chapter 14 investigates and contains the production compromise without destroying evidence or widening business harm.
