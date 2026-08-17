# 06 — Make Production Behavior Explainable

> **Outcome:** Correlate user-visible failure with route, dependency, trace, and release evidence, then alert on service-level impact rather than component symptoms.

**Current Northwind state:** Kubernetes can enforce runtime health, but operators cannot explain an order failure across telemetry signals.  
**Prerequisites:** Chapters 1–5 and monitoring fundamentals.  
**Implementation:** `books/labs/devops/northwind/`  
**Guided time:** approximately 90–120 minutes.

## 1. Healthy process, failed orders

Payment requests now take more than two seconds and return `503`; catalog reads remain fast and processor utilization is 31%. Northwind's only alert fires above 80% utilization. Text logs have no request or trace identity, and request metrics use `user_id` labels.

> How can an operator prove which user journey, dependency, and release is failing without searching every log or declaring the whole service unhealthy?

> **Practice — Establish the telemetry baseline**
>
> Check out the symptom-only state and prove that correlation, cardinality, release identity, user-visible indicators, and burn alerting are red.

```bash
cd books/labs/devops/northwind
git switch -c my-chapter-06 chapter-06-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-06-baseline
```

## 2. The production model: signals answer different questions

> *Theory — Correlated signals and user-visible evidence*
>
> Choose metrics, logs, traces, and service-level indicators according to the production question each can answer.

Metrics aggregate bounded dimensions efficiently: *which route is failing and how often?* Logs retain event context: *what did this request decide?* Traces connect causal work: *where did time and failure propagate?* Resource attributes identify the emitting service, release, and environment. OpenTelemetry treats metrics, logs, and traces as separate signals connected through context propagation. [OpenTelemetry signals](https://opentelemetry.io/docs/concepts/signals/), [instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/).

Do not place `user_id`, `order_id`, or `request_id` in metric labels. Their unbounded value sets multiply time series and operational cost. Preserve those identities in controlled logs or traces where access, retention, and privacy policy can be enforced.

A **SLI (Service-Level Indicator)** measures an outcome such as successful valid order submissions or order latency. A **SLO (Service-Level Objective)** states the acceptable target over a window. Error-budget burn expresses how quickly failures consume the permitted unreliability. Component utilization may help diagnosis, but it is not evidence that customers can place orders.

## 3. Define the telemetry contract

> **Practice — Structure logs and bound metric dimensions**
>
> Replace free text and user-labelled metrics with correlated event fields and bounded route, status, method, and dependency dimensions.

Edit `observability/contract.json`. Set log format to `json` and include `timestamp`, `level`, `message`, `service`, `route`, `status`, `dependency`, `trace_id`, and `request_id`. Remove `user_id` from request-counter labels.

Route values must be templates such as `/orders/{id}`, not raw paths containing identifiers. Dependency names must come from a controlled set. Structured logging is not permission to emit credentials, payment data, or arbitrary request bodies.

> **Practice — Propagate causality and deployment identity**
>
> Carry trace context across **HTTP (Hypertext Transfer Protocol)**, payment, and queue boundaries and identify which release emitted every signal.

Configure `traceparent` and `tracestate` propagation and require `http.server`, `payment.client`, and `queue.publish` spans. Record `service.name`, `service.version`, and `deployment.environment.name` as resource attributes. The older `deployment.environment` key is deprecated. OpenTelemetry's default propagation uses **W3C (World Wide Web Consortium)** Trace Context, while `service.version` identifies the artifact version associated with telemetry. [Context propagation](https://opentelemetry.io/docs/concepts/context-propagation/), [deployment attributes](https://opentelemetry.io/docs/specs/semconv/registry/attributes/deployment/).

Correlation context crosses trust boundaries. Validate incoming headers, avoid sensitive baggage, and create a new trusted boundary where policy requires it.

## 4. Measure the order journey

> **Practice — Define user-visible indicators**
>
> Measure valid order success and latency separately from catalog and process health.

Add `order_success_ratio` and `order_latency` to `service_level_indicators`. Define a provisional 99.5% order-success objective over 30 days in `service_level_objectives`; this Northwind value must be validated against user expectations and business risk. Burn rate is meaningless without a target and window. Define eligible events precisely: malformed or unauthorized requests may be excluded when they do not represent service failure; dependency failures after accepting valid work normally count. Record the policy so numerator and denominator cannot drift between dashboard and alert.

Latency needs a distribution, not an average. Choose thresholds and percentiles from user expectations and workload evidence. The fixture names the indicator contract; production instrumentation must emit histogram boundaries suitable for those decisions.

> **Practice — Alert on fast and slow error-budget burn**
>
> Replace processor-only alerting with paired windows that detect urgent and sustained user impact.

Add fast burn (`5m` and `1h`, threshold `14.4`) and slow burn (`30m` and `6h`, threshold `6`) alerts for `order_success_ratio`. These are illustrative Northwind policy values. Validate evaluation intervals, minimum traffic, missing-data behavior, and paging ownership. Multi-window alerts reduce sensitivity to brief noise while preserving response to sustained burn.

## 5. Verify correlated evidence

> **Practice — Verify the observability contract**
>
> Check log structure, bounded labels, context propagation, release identity, user-visible indicators, and burn alerting together.

```bash
make chapter-06-checkpoint
```

Green proves the declared contract, not backend ingestion, retention, query correctness, or dashboard usability. Production needs end-to-end telemetry tests from application emission through collection and query.

## 6. Diagnose payment degradation

**Severity:** order-submission outage; catalog remains available.  
**Potential blast radius:** the `/orders` journey and payment dependency.  
**Bounded by:** route-specific indicators and causal trace context.  
**Primary principles:** trustworthy evidence, blast-radius control, and recovery.

> **Practice — Isolate user impact without a false global outage**
>
> Evaluate the production-shaped fixture and prove that order failure maps to payment while catalog remains healthy.

```bash
make chapter-06-break
```

The report must detect order failure, isolate `payment-provider`, and keep catalog healthy. Recovery requires repaired payment behavior plus recovered success and latency indicators over the chosen windows; a quiet processor graph or one successful request is insufficient.

## 7. Production reality

**Best Practice:** correlate bounded metrics, structured logs, and traces with stable service and release identity; alert on user-visible outcomes.

**Production Practice:** control telemetry cost, privacy, sampling, retention, collector failure, clock skew, and missing data. Tail sampling can preserve errors but requires infrastructure; head sampling may discard the trace needed during a rare incident. Metrics should remain useful when tracing is sampled. Telemetry pipelines require capacity limits and monitoring so observability failure does not overload the application it observes.

## 8. What changed

| Before | After |
|---|---|
| Text events could not be correlated. | Structured logs carry request and trace context. |
| User IDs created unbounded metric series. | Metrics use bounded operational dimensions. |
| Failures lacked causal and release identity. | Trace propagation and resource attributes connect both. |
| Processor utilization drove alerting. | Order SLIs and burn windows represent user impact. |
| Payment failure looked service-wide. | Evidence isolates orders and preserves catalog health. |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Production telemetry and service-level contract | `observability/contract.json` | It keeps correlation fields, bounded metric dimensions, release identity, indicator eligibility, objective, and burn-window policy reviewable together. |
| Observability conformance evidence | `evidence/chapter-06-green.json` | It records the last accepted contract checks for comparison when instrumentation, alerts, or telemetry backends change. |

## What You Learned

Production observability must explain user-visible behavior without creating uncontrolled cost or cardinality. You can now correlate logs, metrics, and traces across a request path, bind evidence to a release, define service-level indicators and burn alerts, distinguish an affected journey from a global outage, and recognize when missing or misleading telemetry cannot support a safe operational decision.

### Prove It

> **Independent Practice — Design asynchronous order evidence**
>
> Extend correlation and service-level measurement from accepted order through queue redelivery, payment, and terminal state.

Define identifiers for logs and traces, bounded metric labels, producer/consumer spans, duplicate-delivery evidence, success and latency eligibility, sampling behavior, and an alert that detects permanently stuck orders without paging on normal queue delay.

## Next

Northwind can now explain production behavior. Chapter 7 uses those service-level signals to advance, pause, or abort a progressive release.
