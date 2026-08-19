# 11 — Control Delivery Cost and Capacity

> **Outcome:** Reduce cost per successful order through measured capacity changes that preserve latency, backlog, dependency, and recovery contracts.

**Current Northwind state:** Chapter 10 reconciles production intent, but resource and delivery costs are not connected to service ownership, useful outcomes, or recovery capacity.  
**Prerequisites:** Chapters 1–10, resource requests and limits, autoscaling fundamentals, and service-level evidence.  
**Implementation:** `books/practical-engineering/labs/devops/northwind/`  
**Guided time:** approximately 90–120 minutes.

## 1. A cheaper system that cannot finish orders

Northwind halves `order-worker` capacity. Monthly compute cost falls 34%, and cost per successful order appears 8% lower. Order acceptance still succeeds 99.8% of the time, so the change looks efficient. Yet **p95 (95th percentile)** completion reaches 13 minutes, the oldest message is 31 minutes old, and the backlog does not drain.

> How can Northwind optimize spend without treating delayed work, reduced recovery capacity, or shifted shared cost as savings?

> **Practice — Establish the ungoverned baseline**
>
> Check out the cost-only design and prove allocation, unit economics, capacity, forecasting, optimization, and governance contracts are red.

```bash
cd books/practical-engineering/labs/devops/northwind
git switch -c my-chapter-11 chapter-11-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-11-baseline
```

## 2. The production model: cost per useful outcome

> *Theory — Unit economics constrained by reliability*
>
> Decide whether a cost change improves the economics of a successful production outcome rather than merely reducing a billing total.

Total spend answers an accounting question, not an engineering outcome. Northwind needs three connected views:

```text
allocated spend        useful outcomes          operating constraints
owner/service/env  ÷  successful orders   +   latency, backlog, recovery
         └──────────── cost per useful outcome ─────────────┘
```

Allocation makes cost attributable. Unit economics normalizes it against a business outcome. Reliability and capacity constraints prevent the denominator from hiding degraded service. If failed or permanently delayed orders disappear from the denominator, unit cost can improve because the system did less useful work.

The **FinOps (Financial Operations)** Framework treats allocation, forecasting, budgeting, anomaly management, and unit economics as connected practices rather than a one-time cost-cutting exercise. [FinOps Framework](https://www.finops.org/framework/).

## 3. Make spend attributable

> **Practice — Define attributable unit economics**
>
> Allocate direct and shared spend, then normalize it by a quality-gated successful order while measuring delivery cost separately.

Edit `finops/capacity-contract.json`. Enable the four allocation fields and set shared-cost policy to `documented-allocation`.

Use provider billing dimensions, Kubernetes labels, account or project boundaries, and workload metadata that survive into cost exports. Validate coverage and cardinality; a label standard that only 70% of spend follows does not produce trustworthy service economics.

Shared cost is not free. Allocate cluster control, observability, networking, artifact storage, and shared runners through a declared method such as measured consumption, reserved capacity, or an agreed proportional rule. Show both direct and allocated values so a changed formula cannot masquerade as engineering savings.

## 4. Measure useful production and delivery units

Set the economic unit to `cost-per-successful-order`, enable the denominator quality gate, and enable delivery-cost measurement.

Create the calculation contract in `finops/unit-cost-assumptions.json`. The chapter fixture uses these explicit, illustrative assumptions:

| Assumption | Northwind fixture decision | Why it must be visible |
|---|---|---|
| Currency | United States dollar | Mixed currencies make totals incomparable without an exchange-rate policy. |
| Observation window | One-hour accepted-order cohort | Numerator and denominator must describe the same population and time boundary. |
| Cost basis | Amortized | Commitments and discounts must not appear entirely in the purchase period. |
| Workload numerator | Direct worker cost plus allocated shared-runtime cost | A lower direct bill must not hide cost shifted into the shared platform. |
| Delivery cost | Reported separately | Pipeline economics remain visible without silently changing the workload unit. |
| Denominator | Quality-qualified terminal orders | Accepted, failed, duplicated, invalid, or permanently delayed work is not successful production. |
| Shared allocation | Documented fixed-capacity share for this fixture | Changing the allocation method is a model change, not an engineering saving. |
| One-time credits | Excluded and reported separately | A credit must not look like a repeatable efficiency improvement. |

The fixture's baseline workload numerator is `75 + 25 = 100` dollars for 1,000 qualified orders, or `0.10` dollars per order. The candidate is `41 + 25 = 66` dollars for approximately 717.39 qualified orders, or `0.092` dollars per order. Those inputs produce the stated 34% spend reduction and 8% apparent unit-cost reduction. The values teach the calculation; they are not Northwind production prices or a universal allocation method.

A successful order is not merely accepted by the **API (Application Programming Interface)**. It must reach the valid terminal state defined by Northwind's critical outcome without duplicate charge, invalid inventory, or permanent disappearance. Report delayed and failed work separately instead of silently removing them from the cohort.

Delivery cost includes runners, artifact storage and transfer, scanners, preview environments, and repeated failed pipelines. Chapter 1 already measures queue and execution time; attach provider cost and retained evidence to the same workflow identity. Do not reduce cost by deleting the test or provenance evidence that prevents change failure.

## 5. Join capacity with user and queue evidence

> **Practice — Join reliability to a tested capacity envelope**
>
> Require user, queue, and recovery evidence, then connect measured requests, autoscaling, headroom, and dependency ceilings.

Enable every reliability-evidence field.

`storefront-api` can remain fast while `order-worker` falls hours behind. Chapter 6's request indicators and Chapter 9's oldest-message age therefore describe different parts of the same user journey. Recovery capacity asks a third question: after dependency or worker failure, can Northwind drain accumulated work without violating the payment provider's rate limit?

Define the observation window before evaluating the change. It must include normal peak, low traffic, scale transitions, and a recovery-shaped backlog. A seven-day average can conceal the exact hour where capacity is inadequate.

## 6. Build a tested capacity envelope

Enable measured requests. Add `oldest-message-age` beside processor utilization, set minimum capacity to `tested-recovery-floor`, verify maximum capacity, define failure-and-growth-tested headroom, bind scaling to the provider rate limit, and enable downscale stabilization.

Kubernetes **HPA (Horizontal Pod Autoscaler)** can evaluate multiple metrics and chooses the largest replica recommendation. Resource-based utilization also depends on resource requests being present. [Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/).

Processor utilization alone can stay low while workers wait on payment or the database. Oldest-message age captures delayed useful work. Conversely, scaling aggressively on backlog can overload the provider and increase failure. Bound maximum concurrency by tested downstream capacity and use per-order correctness from Chapter 9.

Minimum replicas are not sacred. They are the smallest capacity that survives routine disruption and meets measured recovery requirements. Maximum replicas are not aspirational: confirm scheduling headroom, startup time, database connections, broker partitions, payment rate limits, and cost at that scale.

## 7. Forecast before the invoice

> **Practice — Add predictive financial controls**
>
> Forecast expected spend, alert on forecast and anomalies, assign a service owner, and buy commitments only after measuring a stable baseline.

Enable forecasting, set budget alerts to `forecast-and-anomaly`, assign anomalies to `service-owner`, and require a baseline before commitments.

A budget threshold that fires after money is spent is historical reporting. Forecasts should explain volume, unit price, allocation coverage, planned releases, seasonal demand, and commitment assumptions. Anomaly detection finds unexpected shape; an owner decides whether it represents demand, leakage, attack, failed cleanup, price change, or allocation error.

Commitments can lower unit price while reducing flexibility. Base them on durable baseline demand, not peak autoscaling or temporary migration capacity. Keep uncertain growth and failure headroom outside the commitment unless the financial and availability trade-off is explicit.

## 8. Treat optimization as a production change

> **Practice — Gate, evaluate, and verify the optimization**
>
> Make rightsizing reviewed and reversible, compute the story's economics and gates, exercise recovery capacity, and verify the full contract.

Enable every optimization-change control. Set rollback capacity to `last-verified-envelope` and evidence window to `peak-and-recovery`.

Also enable expiring governance exceptions, team-scoped showback, and the prohibition on individual ranking. These controls keep temporary financial exceptions owned and stop noisy shared-cost estimates from becoming personal performance measures.

Change requests, limits, replicas, autoscaling targets, instance types, commitment coverage, or spot placement through Chapter 10's reviewed reconciliation path. Expose the change progressively where the platform supports it. Compare cost and useful outcomes against the prior envelope, and retain enough capacity to reverse before backlog or dependency pressure becomes irreversible.

Interruptible capacity is appropriate only where interruption is tested: idempotent workers with bounded leases and safe redelivery may use it, but the minimum recovery floor and stateful database need a different decision. A discount does not remove correlated interruption or replacement-delay risk.

Run the local decision engine, then the acceptance checkpoint:

```bash
make chapter-11-evaluate
make chapter-11-checkpoint
```

The evaluator sums only the declared workload components, keeps delivery cost separate, divides by quality-qualified terminal orders from the same cohort, and derives both percentages; the fixture does not label them. It independently evaluates the success, completion, and oldest-message-age gates. The same run restores the verified processing profile and simulates 30 minutes of backlog recovery, proving the queue drains without crossing the provider limit.

This is a deterministic decision-system and capacity-recovery simulation, not a live bill, cluster resize, or autoscaler. The checkpoint requires its calculated results in addition to the policy contract. Production must also validate billing-export delay, missing allocation, discounts and credits, currency and amortization rules, telemetry gaps, autoscaler failure, node shortage, provider throttling, and cost during incident recovery.

## 9. Reject a cheap but slow worker fleet

**Severity:** delayed asynchronous order completion and lost recovery margin after aggressive rightsizing.  
**Potential blast radius:** orders entering the worker backlog during the optimization window.  
**Bounded by:** progressive capacity change, oldest-age and completion gates, dependency-aware maximums, and a retained last verified envelope.  
**Primary principles:** trustworthy evidence, blast-radius control, explicit contracts, reconciliation, and recovery.

> **Practice — Diagnose false savings**
>
> Evaluate the lower-cost worker fleet and prove that spend reduction cannot approve degraded backlog and recovery behavior.

```bash
make chapter-11-break
```

The report must show `spend_reduction_is_real`, `unit_cost_does_not_prove_health`, `backlog_harm_is_detected`, `optimization_is_rejected`, and `recovery_restores_verified_capacity` as true. Spend reduction is accepted as a fact; retention of the change is rejected because the computed 780-second completion and 1,900-second oldest age exceed independent expectations. Recovery passes only when the simulated backlog reaches zero within the provider ceiling.

Restoring replicas is an action, not recovery. Reconcile the last verified envelope, cap the recovery ramp below provider and database limits, verify oldest-message age falls continuously, confirm order completion and success recover, reconcile payment and inventory outcomes, and measure the temporary recovery cost. Do not declare success while the backlog is merely smaller.

## 10. Production reality

**Best Practice:** allocate spend, measure cost per useful outcome, join cost with reliability, derive capacity from workload evidence, forecast before thresholds, and treat optimization as a reversible production change.

**Production Practice:** qualify billing data delay, allocation gaps, shared-cost formulas, discounts, commitments, telemetry failure, seasonality, dependency ceilings, recovery demand, interruptible capacity, and organizational ownership. Cost targets are constraints for teams and systems; do not convert noisy infrastructure allocation into individual-engineer rankings.

## 11. What changed

| Before | After |
|---|---|
| Total spend lacked operational ownership. | Direct and shared cost have explicit service and organizational dimensions. |
| Cheap successful requests defined efficiency. | Cost is normalized by correct terminal orders and constrained by delay and recovery. |
| Currency, window, allocation, discounts, and denominator were implicit. | A reviewed assumption contract makes the unit reproducible and exposes model changes. |
| Processor utilization controlled worker scale. | Work age, requests, headroom, and dependency capacity define an envelope. |
| Budgets reported overspend after occurrence. | Forecast and anomalies create owned, earlier decisions. |
| Rightsizing changed production immediately. | Optimization is reviewed, progressive, evidence-gated, and reversible. |
| Cost reports could rank individuals. | Team showback informs system decisions and exceptions expire. |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Unit-cost assumption contract | `finops/unit-cost-assumptions.json` | It makes currency, cohort, numerator, denominator, allocation, and accounting treatments reviewable. |
| Cost-and-capacity decision evidence | `evidence/chapter-11-green.json` | It retains the calculated economics, reliability decision, and verified recovery result together. |

## What You Learned

Cost efficiency is a production outcome, not a lower invoice in isolation. You can now state and reproduce a unit-cost model, allocate spend, define a quality-gated economic unit, join economics to synchronous and asynchronous reliability, construct a tested capacity envelope, forecast anomalies, and reject savings that remove recovery margin.

### Prove It

> **Independent Practice — Place interruptible worker capacity safely**
>
> Move 60% of `order-worker` capacity to instances that may disappear with two minutes' notice during Northwind's busiest hour.

Define the non-interruptible floor, termination and lease behavior, per-order idempotency dependency, autoscaling signals, replacement-time assumption, provider limit, backlog and completion gates, cost baseline, interruption experiment, rollback trigger, recovery ramp, and evidence needed before expanding beyond 60%. Explain how correlated loss differs from ordinary Pod disruption.

## Next

Northwind can now optimize cost without silently spending reliability or recovery margin. Chapter 12 coordinates diagnosis, rollback or roll-forward, communication, and verified recovery when a production change still fails.
