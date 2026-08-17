# Decide Which Capabilities Become Platform Products

Chapter 1 named the users, jobs, promise, and refusals. That brief does not decide which painful YAML copy, security default, or dashboard widget becomes a platform product.

The production question is now:

> Which repeated capabilities should the platform own, which should stay with application teams, and which should be declined?

Without an intake method, every request looks like platform work. Fulfillment waits for an environment. Storefront asks the platform to host custom order-pricing rules because another team asked too. A portal backlog fills with service-specific widgets. Centralizing everything creates a golden cage. Productizing nothing leaves every team to rebuild the path.

This chapter records productize, leave, and decline decisions against the Chapter 1 jobs. Later chapters implement the accepted capabilities; they must not reopen the pricing refusal because two teams asked again.

## 1. An unsafe intake decision

A weak record says:

```yaml
candidate: order-pricing-logic
treatment: productize
demand: two-teams-asked
```

It does not identify a user job from the product brief, repetition beyond ticket count, isolation impact, support cost, remaining owner, or review trigger. “Two teams asked” may justify a conversation. It cannot complete a productization decision.

Work from the lab working tree using the Chapter 0 procedure. From the Platform lab root, run the Chapter 2 baseline:

```bash
make chapter-02-baseline
```

The command succeeds when it detects the intended unsafe intake:

```text
chapter 02 baseline: two-teams-asked productization correctly detected
```

The fixture productizes custom order-pricing logic because two teams asked, leaves environment provisioning as a Storefront tribal path, and still claims artifact promotion is a product. Demand has been treated as a vote. A Chapter 1 non-goal has been absorbed. Fulfillment still waits.

That inversion drives the chapter.

## 2. The production model: demand, differentiation, and support cost

> *Theory — Capability intake*
>
> This model enables Northwind to select platform work according to repeated user jobs and support cost rather than according to whoever asked twice.

### Demand is unfinished work that repeats, not a vote

Demand exists when more than one team must finish the same production job and currently cannot do so without a ticket, a copy, or inherited cluster authority. Fulfillment waiting for an environment is demand. Storefront and Fulfillment each rebuilding digest promotion is demand.

Two tickets for custom pricing are not that signal. They are two application teams asking the platform to host differentiating commercial logic. Ticket volume, the loudest requester, and “the portal needs it” are forbidden justifications. Chapter 10 will refuse those labels as metrics. Chapter 2 must not encode them as intake.

### Differentiation stays with the team that owns the commercial decision

A capability is differentiating when changing it changes how a team competes, prices, or presents its own product. Order-pricing rules are Storefront’s commercial decision. Application dashboard widgets that only Storefront understands are Storefront’s presentation decision.

A capability is a candidate for the platform when the user job is the same across teams and the variation is configuration, not a new product. Environment leases, digest-pinned promotion, and an owned software catalog are that kind of work. They do not make Storefront’s prices better. They make Fulfillment able to ship without becoming a second unofficial platform.

### Support cost and cognitive load decide thickness

Every productized capability becomes a support surface. If the platform hosts pricing, every commercial change is a platform ticket. If it themes every service dashboard, every widget is a platform ticket. Cognitive load moves from application teams to a queue that cannot finish `obtain-bounded-environment`.

A **thin platform** productizes the smallest set of capabilities that finish the named jobs. A **thick platform** absorbs adjacent requests until the product is a cage: teams cannot leave, and the platform team cannot change the path because every exception is unique.

Thickness is not a moral failing. Some organizations need a thicker paved road later. The intake record must say why, who pays the support cost, and what trigger would reverse the extraction. Reversible extraction is the default: start with the job, not with a portal catalog of everything Northwind might one day want.

### Treatment is productize, leave, or decline

Northwind can:

- **Productize** a repeated capability that finishes a named user job, with an owner and a review trigger;
- **Leave** a capability with the application team that uniquely needs it, with a remaining owner and a trigger that would reopen extraction; or
- **Decline** work the product brief already refused, or work that would make the platform own differentiating logic, naming the remaining owner from the non-goal register.

“Backlog,” “maybe later,” and “the portal could do it” are not treatments.

**Best Practice:** Require the same fields on every treatment: demand, repetition, isolation impact, support cost, owner, and review trigger.

**Production Practice:** A decline is only real when it cites the remaining owner already recorded in `product/non-goals.yaml`. Chapter 1’s pricing refusal is tested here.

### Isolation and contracts are not yet the product

Intake does not create tenant isolation. It decides which capabilities would expand or contain blast radius if left as tickets. Shared cluster-admin as the unofficial environment path is an isolation *impact*, not a tenancy model. Chapter 3 owns that model.

Intake is also not yet a paved-road contract. Teams cannot rely on or leave a path that has not been productized. Chapter 5 owns that contract. The decision record is the first reviewable promise about what the platform will and will not own.

## 3. Make the intake decisions

The completed Chapter 2 model uses three files:

```text
intake/method.yaml
intake/candidates.yaml
intake/decisions.yaml
```

The separation is deliberate. The method names allowed treatments and forbidden demand labels. Candidates are proposed capabilities, not decisions. Decisions bind treatment to a user job or remaining owner.

> **Practice — Adopt a method that cannot treat a vote as demand**
>
> Name the three treatments and the justifications that must never productize a capability.

Open `intake/method.yaml`. The method forbids `two-teams-asked`, `loudest-ticket`, and `portal-needed`. It requires repetition, isolation impact, support cost, owner, and review trigger on every row. If those fields are missing, later chapters inherit a slogan instead of a decision.

> **Practice — Productize the jobs Fulfillment cannot finish**
>
> Keep environment provisioning and artifact promotion on the intake path, and bind each to a Chapter 1 job.

Open `intake/decisions.yaml`. The required productization decisions are:

```yaml
- id: decide-environment-provisioning
  candidate: environment-provisioning
  treatment: productize
  user_job: obtain-bounded-environment
  demand: both-tenants-wait-on-tickets
  repetition: storefront-and-fulfillment-copy-environment-manifests
  isolation_impact: shared-cluster-admin-if-left-as-a-ticket
  support_cost: one-ticket-per-environment-with-no-lease
  owner: platform-team
  review_trigger: new-tenant-or-environment-class
- id: decide-artifact-promotion
  candidate: artifact-promotion
  treatment: productize
  user_job: ship-on-paved-road
  demand: fulfillment-cannot-reuse-storefront-promotion
  repetition: each-team-rebuilds-digest-promotion
  isolation_impact: unofficial-latest-tags-if-left-tribal
  support_cost: platform-debugs-every-team-pipeline
  owner: platform-team
  review_trigger: new-artifact-type-or-registry
```

Inspect each productize row with three questions:

1. Does the user job exist in `product/jobs.yaml`, or was a new job invented to justify the request?
2. Would the capability still matter if Northwind replaced the portal product?
3. Is the named owner authorized to change the path that finishes the job?

The catalog decision productizes `publish-owned-path` for the same reason: owners currently live in chat. Chapter 4 will implement the catalog. Chapter 2 only decides that ownership discovery is platform work, not a wiki someone might update.

> **Practice — Decline differentiating logic and leave one-team presentation**
>
> Refuse work the brief already refused, and leave capabilities that only one team understands.

The pricing row must decline, not defer:

```yaml
- id: decide-order-pricing-logic
  candidate: order-pricing-logic
  treatment: decline
  remaining_owner: storefront-team
  demand: two-application-teams-requested-hosting
  repetition: commercial-rules-differ-per-team
  isolation_impact: platform-would-own-differentiating-business-logic
  support_cost: perpetual-pricing-change-tickets
  owner: platform-team
  review_trigger: pricing-becomes-a-shared-regulated-capability
```

`remaining_owner: storefront-team` must match the Chapter 1 non-goal. “Two application teams requested hosting” is recorded as the request that was refused, not as demand that productizes the capability. The forbidden label is `two-teams-asked` used as a productize justification.

Application dashboard layout is left with Storefront. One team today is not repetition. The review trigger is explicit: three or more teams sharing the same widget contract would reopen extraction. That is reversible, not a permanent exile.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-02-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 02 checkpoint: productize, leave, and decline decisions verified
```

The audit validates the three Chapter 2 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- the method names productize, leave, and decline;
- environment provisioning and artifact promotion are productized against known jobs;
- order-pricing logic is declined with the non-goal’s remaining owner;
- productize rows do not use forbidden demand labels;
- every decision names repetition, isolation impact, support cost, owner, and review trigger; and
- leave and decline rows name a remaining owner.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not prove that these five candidates are the right set for a real company. It does not prove that Northwind should remain a thin platform, or that pricing will never become a regulated shared capability. Those are judgment claims. The review triggers exist so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 2 evidence |
|---|---|
| Mechanism evidence | Schemas and the intake evaluator operated successfully. |
| Decision evidence | Productize, leave, and decline records trace to jobs, refusals, repetition, isolation impact, support cost, owners, and review triggers. |
| Outcome evidence | Later paved-road, environment, and catalog chapters can be evaluated against these accepted capabilities. |
| Recovery evidence | Not yet produced; later chapters must prove tenant isolation and bounded platform-product recovery in the model. |

Chapter 2 primarily creates decision evidence. Pretending that the local checkpoint proves teams can already obtain environments or promote artifacts would weaken every later chapter.

## 4. Test the decision under failure

### Independent control failure — Custom order-pricing logic is accepted as a platform capability because two teams asked

> **Practice — Decline differentiating logic that arrived as a vote**
>
> Reverse a two-teams-asked productization and keep environment provisioning and artifact promotion on the intake path.

The baseline fixture contains this model:

```yaml
- id: decide-order-pricing-logic
  candidate: order-pricing-logic
  treatment: productize
  user_job: ship-on-paved-road
  demand: two-teams-asked
- id: decide-environment-provisioning
  candidate: environment-provisioning
  treatment: leave
  remaining_owner: storefront-team
```

The problem is not merely missing fields. The model classifies a vote as demand and a Chapter 1 non-goal as a platform job. Environment provisioning, the job Fulfillment actually cannot finish, is left as Storefront tribal knowledge.

**Severity:** high; every later paved-road, environment, and support conversation will optimize unique commercial requests instead of repeated jobs.  
**Plausible harm:** the platform owns pricing change tickets; Fulfillment still waits; unofficial cluster-admin remains the environment path.  
**Potential blast radius:** every application team asked to “put it on the platform”; Storefront’s unofficial path remains the real path.  
**Bounded by:** Chapter 1 non-goals, later paved-road contracts, and tenant isolation. None repairs an intake method that productizes whoever asked twice.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Platform questions

- **User and job:** The users are application teams that must obtain environments and ship on a paved road. Hosting order-pricing rules is not that job; it is Storefront’s commercial work, already refused.
- **Isolation:** Not yet applicable as a tenancy decision. Chapter-local implication: leaving environment provisioning as a ticket preserves shared cluster-admin as the unofficial path, and productizing pricing would expand the platform’s blast radius into business logic it cannot isolate.
- **Contract and exit:** There is no paved-road contract yet. Teams cannot rely on or leave a product that absorbs differentiating logic and declines the repeated environment job.
- **Platform-product evidence:** `two-teams-asked` is a vote, not proof the product works. Required proofs remain time-to-first-environment and paved-road completion. This is not a portfolio **SLO (Service Level Objective)**.

#### Diagnosis

Calling demand “two teams asked” encourages intake by volume: accept pricing, accept widgets, accept the next unique pipeline. Those requests may be sincere, but they do not answer which user job finishes, who pays support cost, or what isolation impact follows if the capability stays a ticket.

The missing decline makes Chapter 1’s non-goal ornamental. The leave on environment provisioning makes Chapter 6’s lease product a surprise rather than an inherited decision. Mapping pricing onto `ship-on-paved-road` invents a job the brief never named.

#### Correction

The completed model does not productize pricing. It declines it with `storefront-team` as remaining owner, productizes environment provisioning and artifact promotion against the Chapter 1 jobs, leaves one-team dashboard layout with a review trigger, and forbids vote labels as productize demand.

That correction changes later decisions:

- Chapter 3 must isolate Fulfillment so the environment product does not require cluster-admin.
- Chapter 4 may implement the catalog because ownership discovery was productized, not because a portal needed a homepage.
- Chapter 5 must pave artifact promotion as a path with an exit, not as a unique Storefront pipeline.
- Chapter 6 must make `obtain-bounded-environment` a lease product because intake already accepted that job.
- Chapter 9 must not grow a golden cage of pricing exceptions; pricing was never a platform default.
- Chapter 13 must support environment and promotion failures as product incidents, not as Storefront tribal knowledge.

The decision is practical because it changes the production contract across the rest of the book. Adding an arbitrary command would not make it more practical.

## 5. Production reality

### Common intake errors

#### Treating a second ticket as demand

Two teams can share a coincidence. Demand requires the same unfinished job, not the same complaint category.

#### Productizing to keep the peace

Accepting pricing “for now” creates a support surface that never expires. Decline with a remaining owner and a review trigger instead.

#### Leaving the painful repeated job because one team already copes

Storefront’s copied environment YAML is not a product. Fulfillment’s wait is the signal. Leave is for one-team differentiation, not for unofficial paths.

#### Inventing a user job to justify a request

If the job is not in `product/jobs.yaml`, either the brief is wrong or the request is out of scope. Do not mint `host-pricing-rules` to make a productize row schema-valid.

#### Measuring intake success as adoption percentage

A thick catalog of unused capabilities is not a thin platform. Later measurement must count finished jobs, not accepted candidates.

#### Assigning ownership without authority

The platform team cannot own environment provisioning if it cannot change tickets into leases. Record the real decision path.

## 6. What changed

| Before | After |
|---|---|
| Custom pricing was accepted because two teams asked. | **Order-pricing logic is declined with Storefront as remaining owner.** |
| Environment provisioning stayed a Storefront ticket path. | **Environment provisioning is productized against `obtain-bounded-environment`.** |
| Artifact promotion was tribal YAML. | **Artifact promotion is productized against `ship-on-paved-road`.** |
| Demand meant ticket volume. | **Demand means a repeated unfinished job; vote labels cannot productize.** |
| Leave, decline, and backlog were interchangeable. | **Leave and decline name remaining owners and review triggers.** |
| A valid schema could appear to prove a sound productization. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a reviewable intake contract that later chapters can pave, isolate, measure, and support without absorbing differentiating work.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Capability intake method | `intake/method.yaml` | It retains the treatments and forbidden demand labels later chapters must not reopen as votes. |
| First productization decisions | `intake/decisions.yaml` | They retain which capabilities the platform owns, leaves, or declines, with owners and review triggers. |

These artifacts should change when Northwind’s jobs, repetition, or organizational authority materially change—not whenever a second team files a ticket.

## What You Learned

A platform productizes repeated capabilities that finish named user jobs. It leaves one-team presentation with the team that owns it. It declines differentiating logic even when two teams ask. Demand is unfinished repeated work, not a vote. Schema checks can prove structural completeness within declared scope. They cannot prove that centralization is objectively correct. A decision earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Decide a third-party settlement calendar without copying the pricing row**
>
> A payments team asks the platform to host a settlement calendar because two other teams “might need it next quarter.”

Extend the Chapter 2 model without adding implementation policy yet:

1. Decide whether the calendar is a repeated unfinished job or a differentiating commercial schedule.
2. Choose productize, leave, or decline without using `two-teams-asked`, `loudest-ticket`, or `portal-needed` as demand.
3. Name the user job from Chapter 1 or the remaining owner if the work is refused.
4. State repetition, isolation impact, and support cost as they would exist if the platform hosted the calendar.
5. Identify one observation that would falsify your treatment.
6. Explain which material change would trigger review of your decision.

Do not copy the pricing decline and rename it. A shared regulated calendar has different isolation and review consequences from Storefront-only prices. Your durable output is the decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 2 capability when you can explain why two teams asking is not demand, trace every productize row to a known user job, decline a Chapter 1 non-goal with the recorded remaining owner, describe evidence that would falsify the treatment, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Northwind now knows which capabilities belong on the product and which do not. Tenant boundaries are still labels on a shared cluster. Fulfillment can still inherit cluster-admin “temporarily” to ship.

Chapter 3 models tenants, teams, and isolation boundaries so finishing a productized job does not require shared authority.
