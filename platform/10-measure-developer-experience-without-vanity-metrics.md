# Measure Developer Experience Without Vanity Metrics

Chapter 9 bound remaining guardrails. Scorecards exist. Leadership still asks for adoption percentage, **CSAT (Customer Satisfaction)**, and ticket volume as proof the platform works. A green scorecard and a smiling survey can hide Fulfillment waiting. Chapter 1 already refused `portal-launch` as success evidence and named later proofs: `time-to-first-environment`, `paved-road-completion`, and `catalog-freshness`. Chapter 6 said a created namespace is not that proof. This chapter makes the measurement contract explicit.

The production question is now:

> Which measurements prove teams finish jobs, and which measurements only prove the platform looked busy?

Vanity metrics reward forcing teams onto the road and hiding wait time in Slack. **Goodhart's law** is the pressure: when adoption becomes the target, deleting the unofficial path produces 100% adoption while time-to-first-environment gets worse. That is not developer experience. It is a busier-looking cage.

## 1. One hundred percent adoption and a longer wait

A weak record says:

```yaml
indicators: [adoption-percentage, order_success_ratio]
samples:
  - indicator: adoption-percentage
    value: 100
    unofficial_paths_deleted: true
  - indicator: time-to-first-environment
    value: 120
    prior_value: 48
    unit: hours
```

It does not identify Chapter 1 jobs, later proofs as owned indicators, samples for those proofs, or an explicit non-metric register. “Everyone is on the road” may be true after the unofficial path is deleted. Fulfillment’s wait moved from 48 hours to 120. Storefront’s order-success ratio can stay green through that wait. The inherited observability contract already tracks `order_success_ratio` and `order_latency`. Those are tenant workload outcomes. They are not platform-product **SLIs (Service Level Indicators)**, and they are not portfolio **SLOs (Service Level Objectives)**.

Work from the lab working tree using the Chapter 0 procedure. From the Platform lab root, run the Chapter 10 baseline:

```bash
make chapter-10-baseline
```

The command succeeds when it detects the intended unsafe measurement:

```text
chapter 10 baseline: adoption vanity and missing job samples correctly detected
```

The fixture treats adoption and Storefront order-success as product indicators, omits a catalog-freshness sample, leaves adoption off the non-metric register, and records 100% adoption after unofficial paths are deleted while time-to-first-environment worsens from 48 hours to 120. Guardrails exist. Success is still a portal smile.

That substitution drives the chapter.

## 2. The production model: job time is the product indicator

> *Theory — Developer-experience measurement*
>
> This model enables Northwind to treat finished user jobs as product evidence and to refuse metrics that only prove the platform looked busy.

### A platform-product SLI is a job proof, not a portfolio SLO

Chapter 1’s later proofs are the retained indicators:

| Indicator | Job | Evidence kind |
|---|---|---|
| `time-to-first-environment` | `obtain-bounded-environment` | lagging |
| `paved-road-completion` | `ship-on-paved-road` | lagging |
| `catalog-freshness` | `publish-owned-path` | lagging |

They are platform-product SLIs. They are not portfolio SLOs. Portfolio SLO governance remains a Platform Chapter 1 non-goal with remaining owner `reliability-program`. Do not put `class: portfolio-slo` on a job proof to make it look like SRE.

Lagging evidence is that the job finished, and how long it took. Leading evidence—self-service rate, request-to-lease time—can sit beside those proofs. It cannot replace them. A leading dashboard with no sample for `time-to-first-environment` is still vanity.

### Vanity is recorded, not used

Adoption percentage, CSAT, ticket volume, and portal launch are forbidden as indicators. They are required as non-metrics. Forcing every team onto the paved road by deleting unofficial paths will drive adoption to 100% and can make wait time worse. CSAT can rise while Fulfillment still files tickets in Slack. Ticket volume can fall because people stopped asking. A portal launch is Chapter 1’s already-rejected proof.

The inherited DevOps observability interface names `order_success_ratio` and `order_latency`. This chapter loads that list. Those outcomes stay Storefront’s workload evidence. They must appear in the non-metric register so nobody can “borrow” a green order path as platform health.

**Best Practice:** Map every retained indicator to a Chapter 1 job and to that job’s `later_proof`. A metric without a job is a dashboard.

**Production Practice:** Missing samples fail the contract. Completeness is computed. A measurement file cannot emit `status: healthy`. The lab does not survey real developers.

**Production Practice:** The non-metric register is one list with two exclusion kinds. `category: vanity` means the signal is gameable. `category: tenant-workload` means the signal is real and belongs to a tenant path. Northwind records both so a later debugger can tell “stop treating adoption as success” from “stop borrowing Storefront’s order-success.”

### Deleting the unofficial path is not completion

The independent failure is Goodhart in one number: adoption 100, unofficial paths deleted, time-to-first-environment 120 hours after 48. The unofficial path was evidence that the product was slow. Deleting it without improving job time hides the wait. Restore job-time evidence as the product indicator. Keep adoption on the non-metric register.

Do not allocate quota here. Chapter 11 will use these indicators so a cheaper shared bill cannot replace Fulfillment’s wait.

## 3. Adopt the measurement contract

The completed Chapter 10 model uses four files:

```text
devex/contract.yaml
devex/indicators.yaml
devex/non-metrics.yaml
devex/samples.yaml
```

The separation is deliberate. The contract names retained indicators and non-metrics. Indicators bind jobs, owners, and SLI class. Non-metrics name vanity and tenant-workload outcomes the product refuses. Samples are observations. The evaluator joins them to Chapter 1’s brief, jobs, and non-goals, and to the inherited observability interface.

> **Practice — Keep Chapter 1 later proofs as the indicator set**
>
> Do not replace `time-to-first-environment` with adoption, CSAT, or Storefront order-success.

Open `devex/contract.yaml` and `devex/indicators.yaml`. The three later proofs are the indicators. Each row names a Chapter 1 job, `platform-team` as owner, class `platform-product-sli`, and evidence kind `lagging`.

> **Practice — Register vanity and tenant outcomes as non-metrics**
>
> Tag each refusal. Vanity is gameable. Inherited order outcomes are the wrong layer.

Open `devex/non-metrics.yaml`. The inherited order indicators are there on purpose. Refusing them is a decision, not an omission. The category says which failure mode a later debugger hit:

```yaml
- id: adoption-percentage
  category: vanity
  reason: forcing-teams-onto-the-road
- id: order_success_ratio
  category: tenant-workload
  reason: tenant-workload-not-platform-product
```

`reason` is the row-specific why. `category` is the kind. Tagging adoption as `tenant-workload`, or Storefront order-success as `vanity`, fails. They are not interchangeable refusals.

> **Practice — Attach a sample to every retained indicator**
>
> Fulfillment’s time-to-first-environment is 48 hours. That number is an observation. It is not proof a real cluster provisioned a namespace.

Open `devex/samples.yaml`. `paved-road-completion` records one Fulfillment completion. `catalog-freshness` records current entries. There is no adoption sample, because adoption is not an indicator.

The lab does not survey developers and does not scrape a portal. Completeness is whether job proofs have owners, samples, and a non-metric register that includes vanity and inherited tenant outcomes.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-10-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 10 checkpoint: job-completion indicators and non-metrics verified
```

The audit validates the four Chapter 10 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- contract owner is a living Chapter 1 user;
- every Chapter 1 `later_proof` and brief `success_evidence` is a retained indicator with a sample;
- each indicator maps to the job that named that proof;
- vanity ids are non-metrics with category `vanity`, not indicators;
- inherited `outcome_indicators` are non-metrics with category `tenant-workload`, not indicators;
- no indicator uses class `portfolio-slo`; and
- 100% adoption after deleting unofficial paths cannot hide a worse time-to-first-environment.

The expected vanity list lives in a separate checkpoint file. A measurement under test does not emit its own passing grade.

The checkpoint does not prove that 48 hours is the right wait for a real company, that developers are satisfied, or that a real clock measured provisioning. Those remain claims a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 10 evidence |
|---|---|
| Mechanism evidence | Schemas and the measurement-contract evaluator operated successfully. |
| Decision evidence | Retained indicators, non-metrics with exclusion category, SLI class, and job mappings are explicit. |
| Outcome evidence | Fulfillment has a computed time-to-first-environment sample. That is not proof a developer finished in 48 hours. |
| Recovery evidence | Not produced. A failed adoption target is a measurement invariant, not restored isolation. |

Chapter 10 produces mechanism, decision, and limited outcome evidence for job-completion measurement. Pretending the local checkpoint proves developer happiness would weaken Chapter 11’s quota and Chapter 13’s support.

## 4. Test the decision under failure

### Independent control failure — Adoption hits 100% after the unofficial path is deleted, while time-to-environment gets worse

> **Practice — Fail the contract when adoption hides wait**
>
> Inject 100% adoption after unofficial paths are deleted and a time-to-first-environment sample that moved from 48 hours to 120, and refuse both.

The completed contract is healthy. The failure command does not rewrite it. It injects the Goodhart case against that snapshot:

```bash
make chapter-10-failure
```

Expected output:

```text
chapter 10 failure: adoption hiding worse time-to-environment correctly rejected
```

The injected record is:

```yaml
indicators: [time-to-first-environment, paved-road-completion, catalog-freshness, adoption-percentage]
samples:
  - indicator: adoption-percentage
    value: 100
    unofficial_paths_deleted: true
  - indicator: time-to-first-environment
    value: 120
    prior_value: 48
    unit: hours
```

Catalog-freshness and paved-road-completion samples stay current. The baseline’s missing catalog sample and borrowed order-success indicator are not required for this failure. Adoption can become a target after the contract already looks complete. Vanity-as-indicator and hidden wait must both fail on their own terms. 120 is greater than 48. The arithmetic is the story.

**Severity:** high; every later quota, fleet, and support conversation will optimize a 100% adoption chart instead of Fulfillment’s wait.  
**Plausible harm:** unofficial paths are deleted; wait moves to Slack; leadership funds the portal; `obtain-bounded-environment` still does not finish.  
**Potential blast radius:** every application team measured as “adopted,” plus capacity and support decisions that trust that number.  
**Bounded by:** Chapter 1 later proofs, the inherited observability outcome list, and the non-metric register. None of those repair a contract that treats adoption as success.  
**Primary principles:** trustworthy evidence, explicit contracts.

#### Platform questions

- **User and job:** Fulfillment must finish `obtain-bounded-environment`. 100% adoption after deleting unofficial paths is not that job.
- **Isolation:** Not a new tenancy model. Chapter-local implication: Storefront `order_success_ratio` must not stand in for Fulfillment’s wait. Per-tenant job time is how the product sees that Storefront being green does not isolate Fulfillment from delay.
- **Contract and exit:** The contract is the measurement set. Teams do not leave it the way they leave a paved-road scaffold. Vanity leaves the indicator set by being listed as a non-metric. That is not a Chapter 5 exit, not a Chapter 7 version bump, and not a Chapter 9 exception.
- **Platform-product evidence:** Adoption, CSAT, and ticket volume prove the platform looked busy. Required proof is sampled job time and completion. This is a platform-product SLI, not a portfolio SLO.

#### Diagnosis

Calling adoption success encourages Goodhart controls: delete unofficial YAML, count every remaining team as adopted, ignore the 48-to-120 hour wait. CSAT and ticket volume move the same way. Borrowing `order_success_ratio` from inherited observability makes Storefront’s orders the platform’s health. Missing samples make the later proofs ornamental.

The missing non-metric register makes Chapter 1’s vanity refusal a memory. The missing job mapping makes Chapter 6’s lease a namespace again. 100% is a target that consumed the unofficial path as evidence.

#### Correction

The completed model does not retain adoption as an indicator. Time-to-first-environment stays a sampled lagging SLI mapped to `obtain-bounded-environment`. Unofficial-path deletion cannot improve the grade. Inherited order metrics stay non-metrics. Completeness is computed. The failure command proves the check still fails when only adoption and the 48-to-120 hour change are injected.

This failure is a measurement-contract failure. It is not a runtime plane recovery. Do not call the failed adoption target **Evidence of restored isolation**. Nothing tenant-runtime was restored. The product stopped treating a 100% chart as job completion.

That correction changes later decisions:

- Chapter 11 must not treat a lower shared bill as product health if time-to-first-environment worsened.
- Chapter 12 must not call a fleet complete because adoption is 100%.
- Chapter 13 must not close a support ticket because CSAT moved.
- Quota and fleet change may not replace job-time samples with portal clicks.

The decision is practical because the failed vanity check is the product. Adding an arbitrary survey command would not make it more practical.

## 5. Production reality

### Common measurement errors

#### Counting adoption after deleting unofficial paths

That is Goodhart. Measure job time. Leave adoption on the non-metric register.

#### Using CSAT or ticket volume as completion

Smiles and silence are not `ship-on-paved-road`.

#### Borrowing Storefront order-success as platform health

The inherited observability contract already owns those outcomes. They are tenant workload indicators. Record them with `category: tenant-workload`, not `vanity`.

#### Calling a job proof a portfolio SLO

Platform Chapter 1 refused portfolio SLO governance. Keep class `platform-product-sli`.

#### Shipping indicators without samples

A named proof with no observation is a slogan. Missing samples fail.

#### Building quota or surveys in this chapter

Adopt the contract. Leave floors to Chapter 11. Do not survey real developers.

## 6. What changed

| Before | After |
|---|---|
| Adoption hit 100% after unofficial paths were deleted while wait grew from 48 hours to 120. | **Vanity adoption and hidden worse job time fail the contract.** |
| CSAT, tickets, and portal launch counted as success. | **Those labels are required non-metrics.** |
| Storefront order-success stood in for platform health. | **Inherited tenant outcomes are refused as product indicators.** |
| Chapter 1 later proofs had no samples. | **Each later proof is an owned SLI with an observation.** |
| A valid schema could appear to prove developers were happy. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely four YAML files. Northwind now has a measurement contract later quota, fleet, and support chapters can use without treating a 100% adoption chart as Fulfillment’s finished job.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Developer-experience measurement contract | `devex/contract.yaml` and `devex/indicators.yaml` | They retain Chapter 1 later proofs as platform-product SLIs later quota and support must not replace with vanity. |
| Non-metric register | `devex/non-metrics.yaml` | It retains the refusal of adoption, CSAT, ticket volume, and portal launch as vanity, and of inherited tenant-outcome metrics as the wrong layer. |

These artifacts should change when Northwind’s jobs or inherited observability outcomes materially change—not whenever a dashboard theme is restyled.

## What You Learned

Developer experience is sampled job completion, not adoption, CSAT, or a green order path. Deleting unofficial paths to hit 100% adoption while wait grows is Goodhart, not success. Schema checks can prove structural completeness within declared scope. They cannot survey real developers. A decision earns its place when Fulfillment’s time-to-first-environment has a sample, and when 100% adoption cannot hide that sample getting worse.

### Prove It

> **Independent Practice — Measure a read-only analytics path without copying the adoption row**
>
> A data-analytics team needs bounded read access. Leadership will ask for “analytics adoption %.”

Extend the Chapter 10 model without adding quota floors yet:

1. Decide which Chapter 1 job, if any, analytics finishes—or whether this is still not a platform job.
2. Name one platform-product SLI and one non-metric you must refuse if asked for adoption percentage, and which exclusion category that non-metric uses.
3. State whether Storefront `order_latency` may be reused as analytics health, given the inherited observability list.
4. Choose a sample that would falsify “analytics can self-serve”—for example time-to-first-environment moving from 48 hours to 120 with unofficial paths deleted.
5. Identify whether that sample is leading or lagging, and which owner remains accountable.
6. Explain which material change would trigger review of the measurement contract, not just one dashboard tile.

Do not copy the Fulfillment 100% adoption row and rename it. Analytics has different wait, isolation, and job-proof consequences than `obtain-bounded-environment` for `fulfillment-api`. Your durable output is the indicator-and-non-metric decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 10 capability when you can explain why 100% adoption is not job completion, trace each retained indicator to a Chapter 1 later proof and sample, describe evidence that would falsify the contract, distinguish structural validation from decision and outcome evidence, and explain what the baseline, checkpoint, and failure command do and do not prove.

## Next

Honest measurements exist, but tenants still contend for unbounded shared capacity. Environments and the control plane share an unowned pool. A lower shared bill can hide Fulfillment starvation.

Chapter 11 allocates quota, cost, and capacity across tenants, so bursting cannot silently consume another tenant’s floor.
