# Define the Platform as a Product

Northwind already has a delivery path and a security path. Storefront can promote a digest, bind workload identity, and stop a bad release. Those mechanisms do not answer the first platform question:

> Who is the platform for, what jobs must it finish, and what does it refuse to own?

Without that answer, platform work becomes a queue of tickets and a portal launch. A team asks for cluster access. Another team copies YAML. Leadership asks when the developer portal will be ready. Each request may be reasonable, but the group cannot compare them until it knows which users, finished jobs, and refusals define the product.

This chapter establishes that foundation. You will name the users, the jobs they must finish, the promise the platform makes, the work it refuses, and the evidence that would prove the product works. The result is not a slide. Later chapters use it to decide which capabilities to productize, where tenants are isolated, what a paved road may contain, and which measurements are allowed to count as success.

## 1. An unsafe product definition

The inherited DevOps and DevSecOps systems protect a critical business outcome:

> A valid order is durably accepted and reaches a correct terminal state without duplicate charge, invalid inventory state, or permanent disappearance.

That statement is strong for one team operating one path. It does not describe a product other teams can consume.

Consider four examples:

- Fulfillment files a ticket for an environment and waits while Storefront already has one.
- A portal ships with a catalog homepage, and leadership counts the launch as success.
- A platform engineer grants cluster-admin “temporarily” so Fulfillment can ship this week.
- Time-to-first-environment and paved-road completion have no owner.

The Storefront order outcome can remain green through all four. Northwind still does not have a platform product.

Work from the lab working tree using the How to Use This Book procedure. From the Platform lab root, run the Chapter 1 baseline:

```bash
make chapter-01-baseline
```

The command succeeds when it detects the intended unsafe definition:

```text
chapter 01 baseline: portal-launch success correctly detected
```

The fixture treats a portal launch as success, leaves `obtain-bounded-environment` without an accountable owner, and uses `portal-launch` as the later proof that a service shipped. A homepage can exist while no team can finish a production job.

That distinction drives the chapter.

## 2. The production model: users, jobs, promise, and refusals

> *Theory — Internal product model*
>
> This model enables Northwind to select platform work according to finished user jobs rather than according to tickets, portals, or whoever shouts.

### A platform user is someone who must finish a job

In this book, a platform user is a team or role that needs a finished production outcome from the platform. Storefront and Fulfillment are application-team users. The platform team is also a user of its own product: it must publish a path other teams can find.

A user is not “everyone with a laptop.” A user is not “the company.” Naming a user without a job produces a portal for nobody in particular.

### A job is a finished outcome, not a request type

A job is complete when a stated production outcome exists. “Open a ticket” is not a job. “Browse the catalog” is not a job. “Obtain a tenant-scoped environment with a lease and no shared cluster-admin” is a job.

The job must name:

- who needs it;
- what finished looks like;
- who owns the product side of it; and
- what later proof would show it keeps working.

If the later proof is a portal launch, a satisfaction survey, ticket volume, or adoption percentage, the job has been replaced by vanity. Chapter 10 will make that measurement contract explicit. Chapter 1 must not encode vanity as the product’s definition of success.

### A promise is what the product commits to finish

The promise is the product’s public contract. For Northwind:

> Application teams finish production jobs on a reviewed paved road, inside an explicit tenant boundary, without inheriting shared cluster authority.

The promise is not “we will build an internal developer platform.” That sentence names a category. It does not name a finished job or a blast-radius boundary.

### A non-goal is work the platform refuses, with a remaining owner

A platform that will not refuse work becomes a ticket queue with extra YAML. Every refusal must name the team that still owns the work. Otherwise the refusal is a vacuum, and the ticket returns.

This book’s first refusals are structural, not taste:

- custom order-pricing logic stays with the application team that owns the commercial decision;
- threat modeling and restored-trust claims remain DevSecOps outcomes the platform may expose, not rebuild;
- portfolio service-level objectives and regional-loss programs remain SRE.

**Best Practice:** Write non-goals in the same register as jobs, not in a slide appendix.

**Production Practice:** A non-goal is only real when a later intake request for that work is declined with the recorded remaining owner. Chapter 2 will test that.

### Platform-product evidence is not tenant-workload evidence

Storefront’s order-success rate can be healthy while Fulfillment cannot obtain an environment. A platform-product indicator must describe a user job the platform owns: time-to-first-environment, paved-road completion, catalog freshness. It is not a portfolio **SLO (Service Level Objective)**. Those belong to SRE.

## 3. Build Northwind's product foundation

The completed Chapter 1 model uses four files:

```text
product/brief.yaml
product/users.yaml
product/jobs.yaml
product/non-goals.yaml
```

The separation is deliberate. Users describe who must finish work. Jobs describe finished outcomes and later proof. The brief binds promise, owner, and success evidence. Non-goals name refused work and remaining owners.

> **Practice — Name the users who must finish jobs**
>
> Identify who the platform is for before choosing capabilities or tools.

Open `product/users.yaml`. The register begins with three users:

```yaml
users:
  - id: storefront-team
    role: application-team
    jobs: [obtain-bounded-environment, ship-on-paved-road]
  - id: fulfillment-team
    role: application-team
    jobs: [obtain-bounded-environment, ship-on-paved-road]
  - id: platform-team
    role: platform-product-owner
    jobs: [publish-owned-path]
```

Storefront already has an unofficial path. Fulfillment does not. If the product names only Storefront, Fulfillment will inherit cluster-admin to catch up. If it names “all engineers,” no job has an owner.

> **Practice — State falsifiable jobs**
>
> Express finished outcomes the platform can later prove without counting a portal launch.

Open `product/jobs.yaml`:

```yaml
- id: obtain-bounded-environment
  user: fulfillment-team
  finished_outcome: A tenant-scoped environment exists with a lease and no shared cluster-admin.
  owner: platform-team
  later_proof: time-to-first-environment
```

Inspect each job with three questions:

1. Can you tell when the job is finished without looking at a homepage?
2. Would the job remain important if Northwind replaced the portal product?
3. Is the named owner authorized to change the path that finishes the job?

Do not expand the register into every possible ticket type. Later chapters need a reviewable set of jobs, not a service-catalog dump.

> **Practice — Bind promise, owner, and job-completion evidence**
>
> Make success evidence match the jobs, and make ownership reciprocal.

Open `product/brief.yaml` and `product/non-goals.yaml`. The brief’s `success_evidence` values must be job proofs, not `portal-launch`. Each non-goal names a `remaining_owner`. The checkpoint verifies that users exist, jobs have owners, vanity proofs are rejected, and required refusals are present.

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
chapter 01 checkpoint: product users, jobs, refusals, and job-completion evidence verified
```

The audit validates the four Chapter 1 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- all independently required users, jobs, and non-goals exist;
- the brief names an accountable owner;
- success evidence and later proofs are not vanity labels;
- every job names a known user, owner, finished outcome, and later proof; and
- every non-goal names a remaining owner.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not prove that three jobs are sufficient for a real company. It does not prove that the platform team has organizational authority, or that Fulfillment’s warehouse effects are the right second tenant. Those are judgment claims.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 1 evidence |
|---|---|
| Mechanism evidence | Schemas and the relationship evaluator operated successfully. |
| Decision evidence | Users, jobs, promise, refusals, owners, and later proofs are explicit and reviewed. |
| Outcome evidence | Later environment, paved-road, and measurement chapters can be evaluated against these jobs. |
| Recovery evidence | Not yet produced; later chapters must prove tenant isolation and bounded platform-product recovery in the model. |

Chapter 1 primarily creates decision evidence. Pretending that the local checkpoint proves teams can already finish jobs would weaken every later chapter.

## 4. Test the model under failure

### Independent control failure — Portal launch counted as success

> **Practice — Diagnose vanity success**
>
> Replace portal-launch evidence with owned job-completion evidence.

The baseline fixture contains this model:

```yaml
promise: Ship a developer portal.
owner: unassigned
success_evidence:
  - portal-launch
```

The problem is not merely missing fields. The model classifies a launch as the product.

**Severity:** high; every later measurement, intake, and support conversation will optimize the homepage instead of finished jobs.  
**Plausible harm:** Fulfillment still waits for environments; unofficial cluster-admin spreads; the platform cannot tell whether it works.  
**Potential blast radius:** every team asked to “adopt the platform”; Storefront’s unofficial path remains the real path.  
**Bounded by:** later measurement contracts, intake refusals, and tenant isolation. None repairs a product definition that counts launches.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Platform questions

- **User and job:** The users are application teams that must obtain environments and ship on a paved road; a portal launch is not that job.
- **Isolation:** Not yet applicable as a tenancy decision. Chapter-local implication: an unowned product invites shared cluster-admin as the unofficial path.
- **Contract and exit:** There is no contract yet, only a homepage. Teams cannot rely on or leave a product that has not named a job.
- **Platform-product evidence:** `portal-launch` is vanity. Required proofs are time-to-first-environment and paved-road completion.

#### Diagnosis

Calling the product “a portal” encourages portal controls: pick a catalog UI, publish markdown, count unique visitors. Those may reduce orientation tickets, but they do not answer who finishes which job, who owns the wait, or what evidence would falsify success.

The missing owner makes intake and support ambiguous. The missing non-goals make every request in-scope. The missing job proof leaves Chapter 10 nothing honest to measure.

#### Correction

The completed model does not elevate the portal into the product. It defines users, jobs, a promise about tenant-bounded paved-road work, and success evidence that later chapters can collect without a homepage.

That correction changes later decisions:

- Chapter 2 must intake capabilities against these jobs, not against whoever asked twice.
- Chapter 3 must isolate Fulfillment so finishing a job does not require cluster-admin.
- Chapter 5 must make `ship-on-paved-road` a path with an exit, not a cage.
- Chapter 6 must make `obtain-bounded-environment` a product with a lease.
- Chapter 10 must treat time-to-first-environment as product evidence and portal-launch as a non-metric.

The concept is practical because it changes the production contract across the rest of the book. Adding an arbitrary command would not make it more practical.

## 5. Production reality

### Common modeling errors

#### Naming the portal as the product

A portal is a distribution surface. If it disappeared, the jobs should still be nameable. If they are not, there was no product.

#### Treating Storefront’s working path as the platform

One team’s tribal YAML is not a product. Fulfillment’s inability to reuse it is the demand signal.

#### Refusing nothing

A platform that accepts custom pricing, threat-model rebuilds, and portfolio SLO programs will not have time to offer environments. Record remaining owners.

#### Using tenant-workload health as platform success

Green order metrics can hide a ticket queue. Platform-product evidence must describe platform jobs.

#### Assigning ownership without authority

A platform team cannot own time-to-first-environment if it cannot change provisioning. Record the real decision path.

## 6. What changed

| Before | After |
|---|---|
| Success was a portal launch. | **Success evidence is time-to-first-environment and paved-road completion.** |
| Users were “engineers.” | **Storefront, Fulfillment, and the platform team are named users with jobs.** |
| Jobs were ticket types. | **Jobs are finished outcomes with owners and later proofs.** |
| Refusals lived in conversation. | **Non-goals name remaining owners for pricing, DevSecOps rebuilds, and SRE programs.** |
| A valid schema could appear to prove a sound product. | **Structural, decision, outcome, and recovery evidence remain distinct.** |
| Later chapters had no stable user-job reference. | **Intake, tenancy, paved road, environments, and measurement inherit this brief.** |

What changed was not merely four YAML files. Northwind now has a falsifiable product contract that later chapters can intake, isolate, pave, measure, and recover.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Platform product brief | `product/brief.yaml` | It retains the promise, owner, and job-completion evidence later measurement must not replace with vanity. |
| Job-and-refusal register | `product/jobs.yaml` and `product/non-goals.yaml` | They retain the finished outcomes and the work the platform will not absorb. |

These artifacts should change when Northwind’s users, jobs, or organizational authority materially change—not whenever a portal theme is redesigned.

## What You Learned

A platform product is defined by users, finished jobs, a promise, and explicit refusals. A portal, catalog, or cluster is a resource that may serve those jobs. Vanity evidence cannot prove the product. Schema checks can prove structural completeness within declared scope. They cannot prove that human judgment is correct. A concept earns its place when it changes later production decisions, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Model a third user without copying Fulfillment**
>
> Decide how Northwind would admit a data-analytics team that needs a bounded read environment but must not ship on the order paved road.

Extend the Chapter 1 model without adding implementation policy yet:

1. Decide whether the analytics team is a new user or a bounded use of an existing user.
2. Name one job that is not `ship-on-paved-road`, including a finished outcome that is not a dashboard screenshot.
3. Choose later proof that is not `portal-launch`, `csat`, or `adoption-percentage`.
4. Assign an accountable owner and a non-goal if the team asks for production write access.
5. Identify one observation that would falsify the job.
6. Explain which material change would trigger review of your decision.

Do not copy the Fulfillment entry and rename it. Read-only analytics has different isolation, support, and exit consequences. Your durable output is the decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 1 capability when you can explain why a portal launch is not a finished job, trace every job to a known user and owner, describe evidence that would falsify the promise, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Northwind now knows who the platform is for and what it refuses. It still does not know which repeated capabilities should become products, which should stay with application teams, and which should be declined even when two teams ask.

Chapter 2 turns the product brief into an intake method with productize, leave, and decline decisions.
