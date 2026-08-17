# Define What Reliability Must Protect

Northwind already has a delivery path, a security path, and an owned internal platform. Storefront can promote a digest, bind workload identity, and stop a bad release. Fulfillment can obtain a bounded environment on a paved road. Those mechanisms do not answer the first reliability question:

> Which user journeys must stay reliable, what does Northwind refuse to count as reliability, and who owns each decision?

Without that answer, reliability work becomes a dashboard of green graphs. The cluster is idle. The apiserver is Ready. The developer portal loads. Leadership asks whether Northwind has five nines. Each signal may be true, and a customer can still fail to complete an order while a warehouse dispatch never happens.

This chapter establishes that foundation. You will name the journeys reliability must protect, the measurements it refuses to count as success, the owners of those decisions, and the evidence that would prove the portfolio is reliable. The result is not a slide. Later chapters use it to choose **SLIs (Service Level Indicators)**, set **SLOs (Service Level Objectives)**, freeze change when budget is exhausted, and prove **Evidence of portfolio recovery**.

## 1. An unsafe reliability definition

The inherited DevOps, DevSecOps, and Platform systems protect a critical business outcome:

> A valid order is durably accepted and reaches a correct terminal state without duplicate charge, invalid inventory state, or permanent disappearance.

That statement is strong for one path and one platform product. It does not describe a reliability program across Storefront and Fulfillment.

Consider four examples:

- Cluster and API uptime are green while `accept-and-complete-order` has no owner.
- Time-to-first-environment is treated as the portfolio SLO because leadership can see it.
- Fulfillment dispatch is assumed covered because Storefront orders look healthy.
- Reconstructing one environment, or restoring a control plane, is filed as regional recovery.

The Storefront order path can remain operable through all four. Northwind still does not have a reliability program.

Work from the lab working tree using the How to Use This Book procedure. From the SRE lab root, run the Chapter 1 baseline:

```bash
make chapter-01-baseline
```

The command succeeds when it detects the intended unsafe definition:

```text
chapter 01 baseline: uptime-theater success correctly detected
```

The fixture treats cluster and API uptime as success, leaves `accept-and-complete-order` without an accountable owner, and uses `cluster-uptime` as the later proof that reliability works. Graphs can be green while no journey has an owner.

That distinction drives the chapter.

## 2. The production model: journeys, refusals, promise, and owners

> *Theory — User-journey reliability model*
>
> This model enables Northwind to select reliability work according to user-visible journeys rather than according to component uptime, portal availability, or whoever owns the loudest dashboard.

### A journey is a user-visible outcome that can fail

In this book, a protected journey is a customer or operator outcome that must remain reliable. `accept-and-complete-order` is a journey. `dispatch-fulfillment` is a journey. Cluster Ready is not a journey. A platform job such as `obtain-bounded-environment` is already named by Platform; it remains a **job-time budget**, not a user-facing journey.

A journey is not “the storefront-api Deployment.” A journey is not “Kubernetes.” Naming a component without a failed user outcome produces availability theater.

### A failed outcome is what the user experiences, not what the graph shows

The journey must name:

- who is harmed when it fails;
- what failed looks like in user terms;
- who owns the reliability decision; and
- what later proof would show it keeps working.

If the later proof is cluster uptime, kubelet Ready, portal availability, or five nines of an apiserver, the journey has been replaced by theater. Chapter 2 will choose SLIs. Chapter 1 must not encode theater as the program’s definition of success.

### A promise is what the reliability program commits to protect

The promise is the program’s public contract. For Northwind:

> Storefront and Fulfillment keep user-visible journeys; exhausted error budget can later freeze change; component uptime is not success.

The promise is not “we will run **SRE (Site Reliability Engineering)**.” That sentence names a category. It does not name a journey or a refusal.

### A refusal is a measurement that must not count as success, with a remaining owner

A program that will not refuse measurements becomes a dashboard with extra YAML. Every refusal must name who still owns that measurement. Otherwise the refusal is a vacuum, and the green graph returns as the SLO.

This book’s first refusals are structural, not taste:

- cluster, API, kubelet, and portal uptime must not count as reliability success;
- platform job-time proofs remain a job-time budget owned by the platform team, not a portfolio SLO;
- one-environment reconstruction and control-plane restore remain inherited recoveries; they are not **Evidence of portfolio recovery**.

**Best Practice:** Write refusals in the same register as journeys, not in a slide appendix.

**Production Practice:** A refusal is only real when a later SLI candidate for that measurement is rejected or kept adjacent. Chapter 2 will test that.

### User-journey evidence is not platform job-time and not component uptime

Time-to-first-environment can be healthy while orders fail. `order_success_ratio` can be healthy while Fulfillment cannot dispatch. Platform-product indicators describe platform jobs. User-journey later proofs describe customer outcomes. Neither is a customer **SLA (Service Level Agreement)**. An SLA is a legal or commercial promise. An SLO is the internal contract Chapter 3 will publish.

## 3. Build Northwind's reliability foundation

The completed Chapter 1 model uses four files:

```text
reliability/brief.yaml
reliability/journeys.yaml
reliability/refusals.yaml
reliability/owners.yaml
```

The separation is deliberate. Owners describe who may be accountable. Journeys describe failed user outcomes and later proof. The brief binds promise, owner, and success evidence. Refusals name measurements that must not count as success and remaining owners.

> **Practice — Name the owners of the reliability program**
>
> Identify who owns the program before choosing indicators or tools.

Open `reliability/owners.yaml`. The register begins with four owners:

```yaml
owners:
  - id: reliability-program
    role: reliability-program-owner
    journeys: [accept-and-complete-order, dispatch-fulfillment]
  - id: storefront-team
    role: application-team
    journeys: [accept-and-complete-order]
  - id: fulfillment-team
    role: application-team
    journeys: [dispatch-fulfillment]
  - id: platform-team
    role: platform-product-owner
    journeys: []
```

`reliability-program` is the remaining owner Platform already recorded on non-goal `portfolio-slo-governance`. If the program names only Storefront, Fulfillment’s dispatch will be assumed covered. If it names “operations,” no journey has an owner. The platform team remains owner of job-time proofs; it is not the owner of user-facing journeys. An empty `journeys` list on `platform-team` is therefore required, not an omission.

> **Practice — State falsifiable journeys**
>
> Express failed user outcomes the program can later prove without counting cluster uptime.

Open `reliability/journeys.yaml`:

```yaml
- id: accept-and-complete-order
  user: storefront-team
  failed_outcome: A valid order is not durably accepted or does not reach a correct terminal state.
  owner: reliability-program
  later_proof: order_success_ratio
```

Inspect each journey with three questions:

1. Can you tell when the journey has failed without looking at cluster Ready?
2. Would the journey remain important if Northwind replaced the dashboard product?
3. Is the named owner authorized to change how the journey is protected?

`order_success_ratio` is an inherited DevOps outcome indicator. Chapter 1 names it as later proof. Chapter 2 decides whether it is an accepted user-journey SLI. Do not put `time-to-first-environment` on a user journey.

Do not expand the register into every component. Later chapters need a reviewable set of journeys, not an inventory of Deployments. `notification-service` is non-critical; it is not a third protected journey.

> **Practice — Bind promise, owner, and journey-completion evidence**
>
> Make success evidence match the journeys, and make ownership reciprocal.

Open `reliability/brief.yaml` and `reliability/refusals.yaml`. The brief’s `success_evidence` values must be journey proofs, not `cluster-uptime`. Each refusal names a `remaining_owner`. The checkpoint verifies that owners exist, journeys have owners, theater proofs are rejected, job-time proofs are not used as journey success, and required refusals are present.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-01-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 01 checkpoint: reliability owners, journeys, refusals, and journey-completion evidence verified
```

The audit validates the four Chapter 1 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- all independently required owners, journeys, and refusals exist;
- the brief names `reliability-program` as owner;
- success evidence and later proofs are not theater labels and not platform job-time ids;
- every journey names a known user, owner, failed outcome, and later proof; and
- every refusal names a remaining owner.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not prove that two journeys are sufficient for a real company. It does not prove that `reliability-program` has organizational authority, or that warehouse dispatch is the right second journey. Those are judgment claims.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 1 evidence |
|---|---|
| Mechanism evidence | Schemas and the relationship evaluator operated successfully. |
| Decision evidence | Owners, journeys, promise, refusals, and later proofs are explicit and reviewed. |
| Outcome evidence | Later SLI, SLO, and recovery chapters can be evaluated against these journeys. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 1 primarily creates decision evidence. Pretending that the local checkpoint proves journeys already keep their SLOs would weaken every later chapter.

## 4. Test the model under failure

### Independent control failure — Cluster and API uptime counted as success

> **Practice — Diagnose uptime theater**
>
> Replace cluster-uptime evidence with owned journey-completion evidence.

The baseline fixture contains this model:

```yaml
promise: Keep the graphs green.
owner: unassigned
success_evidence:
  - cluster-uptime
  - api-uptime
```

The problem is not merely missing fields. The model classifies component uptime as the program.

**Severity:** high; every later SLO, alert, and freeze conversation will optimize graphs instead of journeys.  
**Plausible harm:** orders fail while Ready stays green; Fulfillment dispatch is unowned; a region can be lost with no named journey to recover.  
**Potential blast radius:** every service asked to “be reliable”; Storefront’s provisional indicators remain the only real signal.  
**Bounded by:** later SLI decisions, error-budget policy, and regional architecture. None repairs a program definition that counts uptime theater.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** The journeys are `accept-and-complete-order` and `dispatch-fulfillment`; cluster and API uptime are not those journeys.
- **Error budget:** Not yet applicable as a freeze decision. Chapter-local implication: a program with no journey cannot later compute remaining budget.
- **Human system:** Not yet applicable as on-call design. Chapter-local implication: an unowned program invites Slack-as-primary when graphs turn red.
- **Portfolio recovery:** Not yet produced. Cluster uptime cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling the program “keep the graphs green” encourages graph controls: scrape kubelet, count Ready replicas, publish an uptime tile. Those may reduce orientation noise, but they do not answer which user fails, who owns the wait, or what evidence would falsify success.

The missing owner makes SLI selection and on-call ambiguous. The missing refusals make every green tile in-scope. The missing journey proof leaves Chapter 3 nothing honest to target.

#### Correction

The completed model does not elevate uptime into the program. It defines owners, journeys, a promise about user-visible outcomes, and success evidence that later chapters can collect without a cluster graph.

That correction changes later decisions:

- Chapter 2 must accept `order_success_ratio` as a user-journey candidate and keep `time-to-first-environment` adjacent.
- Chapter 3 must give Fulfillment its own SLO; Storefront cannot cover dispatch by copy.
- Chapter 4 must freeze change against journey budget, not against cluster Ready.
- Chapter 12 must list one-environment reconstruction and plane restore as insufficient for regional loss.

The concept is practical because it changes the production contract across the rest of the book. Adding an arbitrary command would not make it more practical.

## 5. Production reality

### Common modeling errors

#### Naming the dashboard as the program

A dashboard is a distribution surface. If it disappeared, the journeys should still be nameable. If they are not, there was no reliability program.

#### Treating Storefront’s provisional indicators as the portfolio

One team’s DevOps Chapter 6 burn policy is not a portfolio. Fulfillment’s missing journey is the demand signal.

#### Refusing nothing

A program that accepts cluster uptime, platform job-time, and inherited restores as success will not have time to protect orders. Record remaining owners.

#### Using platform job-time as user-journey success

Healthy time-to-first-environment can hide failed orders. Journey evidence must describe user outcomes.

#### Assigning ownership without authority

A reliability program cannot own `order_success_ratio` if it cannot change how that journey is measured or frozen. Record the real decision path. Inherited `self_approval_forbidden` will bind on-call authority in Chapter 6; it does not replace an owner here.

## 6. What changed

| Before | After |
|---|---|
| Success was cluster and API uptime. | **Success evidence is `order_success_ratio` and `dispatch_success_ratio`.** |
| Owners were “operations.” | **`reliability-program`, Storefront, Fulfillment, and the platform team are named, with journeys.** |
| Journeys were component names. | **Journeys are failed user outcomes with owners and later proofs.** |
| Refusals lived in conversation. | **Refusals name remaining owners for uptime theater, job-time-as-SLO, and inherited restores.** |
| A valid schema could appear to prove a sound program. | **Structural, decision, outcome, and recovery evidence remain distinct.** |
| Later chapters had no stable journey reference. | **SLI selection, SLOs, freeze policy, and fail-over inherit this brief.** |

What changed was not merely four YAML files. Northwind now has a falsifiable reliability contract that later chapters can measure, freeze, page, and recover.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Reliability brief | `reliability/brief.yaml` | It retains the promise, owner, and journey-completion evidence later SLOs must not replace with theater. |
| Journey-and-refusal register | `reliability/journeys.yaml` and `reliability/refusals.yaml` | They retain the failed outcomes and the measurements the program will not count as success. |

These artifacts should change when Northwind’s journeys or organizational authority materially change—not whenever a dashboard theme is redesigned.

## What You Learned

A reliability program is defined by protected journeys, a promise, explicit refusals, and accountable owners. A dashboard, cluster, or portal is a resource that may serve those journeys. Theater evidence cannot prove the program. Schema checks can prove structural completeness within declared scope. They cannot prove that human judgment is correct. A concept earns its place when it changes later production decisions, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Model catalog browse without copying Fulfillment**
>
> Decide whether Northwind should protect customer catalog reads as a journey or refuse them as a supporting measurement.

Extend the Chapter 1 model without adding implementation policy yet:

1. Decide whether catalog browse is a new journey or a supporting signal of `accept-and-complete-order`.
2. If it is a journey, name a failed outcome that is not “the Deployment is not Ready.”
3. Choose later proof that is not `cluster-uptime`, `api-uptime`, `time-to-first-environment`, or `csat`.
4. Assign an accountable owner and a refusal if the team asks to count kubelet Ready as success.
5. Identify one observation that would falsify the decision.
6. Explain which material change would trigger review of your decision.

Do not copy the Fulfillment entry and rename it. Catalog reads have different criticality, dependencies, and freeze consequences. Your durable output is the decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 1 capability when you can explain why cluster uptime is not a finished journey, trace every journey to a known user and owner, describe evidence that would falsify the promise, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Northwind now knows which journeys reliability must protect and what it refuses to count as success. It still does not know which measurements may represent those journeys, which inherited indicators stay adjacent as platform job-time, and which component graphs must be rejected.

Chapter 2 turns the reliability brief into an SLI method with accept, adjacent, and reject decisions.
