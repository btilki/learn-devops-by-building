# Command Incidents Across Services and Tenants

Chapter 9 can shed Storefront when payment is overloaded and refuse to page Fulfillment as the cause. A payment slowness that also harmed dispatch still gets one informal commander in Slack. Inherited DevOps Chapter 12 can coordinate one failed production change. That is a single-path capability. It is not portfolio command.

The production question is now:

> How is an incident that spans Storefront, Fulfillment, and the platform commanded, and what evidence is portfolio evidence rather than one-path recovery?

Without that design, single-path command mis-assigns owner, freeze, and recovery proof. Closing because Storefront `order_success_ratio` looks green leaves `dispatch-fulfillment` down. Treating a **platform-product** incident as a **tenant-application** incident pages Storefront for job-time. Chapter 4 already froze Storefront releases and fleet step `storage-1-0-to-2-0`. An incident that ignores those actions makes freeze ornamental. Chapter 6 already designed living primaries. Slack-as-commander is Slack-as-primary under a louder name.

This chapter defines multi-service command, distinct roles, and executed traces. It **consumes** the inherited DevOps recovery-evidence shape and Platform support kinds. It does not reteach one-change coordination or platform support. A trace cannot emit `status: recovered`. That language belongs to later **Evidence of portfolio recovery**, not to closing a ticket.

## 1. An unsafe one-path close

A weak record says:

```yaml
commander: slack
close_on: order_success_ratio
status: closed
affected: [accept-and-complete-order]
```

It reuses DevOps one-change command. It closes on a Storefront **SLI (Service Level Indicator)** while dispatch is still failing. It never pages `platform-oncall` for a platform-product issue. “Orders look green” may describe one path. It cannot complete a portfolio incident.

Work from the lab working tree using the How to Use This Book procedure. From the SRE lab root, run the Chapter 10 baseline:

```bash
make chapter-10-baseline
```

The command succeeds when it detects the intended unsafe command:

```text
chapter 10 baseline: one-path close while dispatch fails correctly detected
```

The fixture sets commander to Slack, closes on `order_success_ratio` and `terminal_order_outcomes`, omits `dispatch-fulfillment`, skips Chapter 4 freeze join, treats catalog contact `storefront-oncall` as the system, and routes a platform-product incident onto Storefront. One green graph has been treated as the portfolio. Informal heroics have been treated as command.

That inversion drives the chapter.

## 2. The production model: commander, scope, freeze join, support kind

> *Theory — Portfolio incident command*
>
> This model enables Northwind to command a spanning incident with named roles, both journeys, the right on-call systems, and Chapter 4 freeze, rather than closing a Slack thread because Storefront looks green.

### One-path recovery evidence cannot close the portfolio

DevOps Chapter 12 already named recovery evidence for one failed change: `desired_actual_agreement`, `healthy_consecutive_samples`, and `terminal_order_outcomes`. This chapter **consumes** those fields. It does not rewrite them into a new incident-management product. They remain insufficient to close a portfolio incident. So is `order_success_ratio` alone.

If dispatch is failing, Storefront green is availability theater. If only Storefront was listed, Fulfillment was never in the incident. Closing then is a one-path close.

**Best Practice:** Name every affected Chapter 1 journey and every Chapter 6 on-call system before anyone talks about close.

**Production Practice:** A spanning tenant-application incident lists `accept-and-complete-order` and `dispatch-fulfillment`, pages `storefront-oncall-system` and `fulfillment-oncall-system`, and stays `open` while dispatch is failing.

### Commander is a role, not whoever answered Slack

Commander and operator are distinct. Commander owns the incident clock and whether close is even discussable. Operator executes. `slack`, `chat-history`, and `whoever-answered` cannot be commander. Those are the same forbidden primaries Chapter 6 already refused.

The commander for a tenant-application spanning incident is a living primary from Chapter 6, not a catalog contact. `storefront-oncall` is who the catalog says to call. `storefront-oncall-system` is the system. Treating the contact as the system reopens Chapter 6.

Cadence is a teaching value: `30m`. It is not an industry constant. It exists so later learning and game days inherit a reviewable clock rather than “we were in Slack.”

### Freeze joins Chapter 4; it is not invented in the war room

Storefront remaining budget is already exhausted. Chapter 4 already recorded `freeze-storefront-releases` and `freeze-fleet-storage-upgrade`. A spanning incident that includes `accept-and-complete-order` must **join** those action ids. It must not copy Platform freeze window, cohort, or rollback onto the trace. It must not invent `platform-upgrade-freeze` as the reason.

If freeze_join is empty while those actions exist, exhausted budget cannot stop change during the incident. Chapter 4 becomes a file nobody opened.

### Platform-product and tenant-application are different incidents

Inherited Platform support kinds are `platform-product` and `tenant-application`. Consume them. Do not invent a third kind called “whatever is on fire.”

A platform-product incident about `time-to-first-environment` routes to `platform-oncall-system`. It is a **job-time budget** issue, not a portfolio **SLO (Service Level Objective)** close. It must not land on Storefront because “they are already up.” A tenant-application spanning incident must not be labeled platform-product to dodge freeze join.

The lab does not run a real incident-management tool. Traces are local fixtures.

## 3. Publish command, roles, and traces

The completed Chapter 10 model uses three files:

```text
incidents/command.yaml
incidents/roles.yaml
incidents/traces.yaml
```

The separation is deliberate. Command names forbidden commanders, cadence, and which evidence cannot close the portfolio. Roles keep commander distinct from operator. Traces are executed incidents: spanning tenant-application and platform-product. None of the files may emit `status: recovered`.

> **Practice — Consume inherited one-path evidence as insufficient**
>
> Keep `desired_actual_agreement`, `healthy_consecutive_samples`, `terminal_order_outcomes`, and `order_success_ratio` off the close path.

Open `incidents/command.yaml`. Owner is `reliability-program`. Forbidden commanders include `slack`, `chat-history`, and `whoever-answered`. Cadence is `30m`. `insufficient_close_evidence` lists the inherited DevOps recovery fields and `order_success_ratio`. If those inherited ids are missing, later traces will close on one-path evidence and call it portfolio recovery.

> **Practice — Keep commander distinct from operator; Slack cannot command**
>
> A single hero role is unofficial command.

Open `incidents/roles.yaml`. Role `commander` may discuss close. Role `operator` may not. If the only role is `whoever-answered`, the checkpoint fails.

> **Practice — Trace both journeys, both on-call systems, and Chapter 4 freeze**
>
> Storefront green cannot close Fulfillment. Platform-product cannot land on Storefront.

Open `incidents/traces.yaml`. Teaching traces:

1. `spanning-payment-and-dispatch` — `support_kind: tenant-application`, commander `storefront-primary-a`, journeys `accept-and-complete-order` and `dispatch-fulfillment`, systems `storefront-oncall-system` and `fulfillment-oncall-system`, freeze join `freeze-storefront-releases` and `freeze-fleet-storage-upgrade`, dispatch state `failing`, status `open`, `as_of` quoted as RFC 3339.
2. `platform-product-job-time` — `support_kind: platform-product`, commander `platform-primary-a`, job-time `time-to-first-environment`, system `platform-oncall-system`, status `open`.

Inspect each trace with three questions:

1. If Storefront’s accept graph were deleted, would this incident still exist?
2. Which Chapter 6 system is paged—and is it a catalog contact wearing a system id?
3. Does Chapter 4 freeze still apply, or was freeze left in the policy file?

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
chapter 10 checkpoint: portfolio command, freeze join, and split support kinds verified
```

The audit validates the three Chapter 10 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- inherited one-path recovery evidence is listed as insufficient to close;
- `order_success_ratio` alone cannot close;
- Slack cannot be commander;
- commander and operator are distinct roles;
- the spanning trace names both Chapter 1 journeys and both tenant on-call systems;
- dispatch failing keeps status `open`;
- Chapter 4 freeze actions are joined by id;
- catalog contacts are not treated as on-call systems;
- platform-product routes to `platform-oncall-system`; and
- `status: recovered` is refused.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not run a real incident-management tool. It does not prove that 30 minutes is the right commercial cadence. Those are judgment claims. The review trigger exists so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 10 evidence |
|---|---|
| Mechanism evidence | Schemas and the incident evaluator operated successfully. |
| Decision evidence | Command model, roles, support kinds, freeze join, and insufficient close evidence are explicit. |
| Outcome evidence | A spanning trace cannot close while dispatch fails; one-path **SLI** close is denied. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 10 creates decision evidence about how a spanning failure is commanded. Pretending that the local checkpoint proved a real war room would weaken later learning, game days, and fail-over.

## 4. Test the design under failure

### Connected consequence — One-path close on order success while dispatch fails

> **Practice — Re-open under portfolio command**
>
> Page both tenant systems, join freeze, route platform-product to the platform rotation, and drop Slack as commander.

The baseline fixture contains this model:

```yaml
commander: slack
close_on: [order_success_ratio, terminal_order_outcomes]
status: closed
affected: [accept-and-complete-order]
oncall: storefront-oncall
platform_incident_on: storefront-oncall-system
```

The problem is not merely a missing field. DevOps one-change evidence has been treated as portfolio close. Chapter 9’s cascade can still harm dispatch while the ticket says done. Chapter 4 freeze was never joined. A platform-product wait-time incident pages Storefront. Informal heroics continue under an inherited recovery field.

**Severity:** high; Fulfillment stays down, freeze does not apply, and the wrong rotation debugs job-time.  
**Plausible harm:** leadership sees “incident closed”; warehouse dispatch remains failing; Storefront is woken for environment wait time.  
**Potential blast radius:** every one-path green graph used as a close; every Slack thread treated as command.  
**Bounded by:** later learning-program verification. None repairs a close that ignored a journey.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** Both `accept-and-complete-order` and `dispatch-fulfillment` are at risk. Closing on the first does not restore the second.
- **Error budget:** Chapter 4 freeze still applies to Storefront releases and `storage-1-0-to-2-0`. The trace must join those actions.
- **Human system:** Applicable as Chapter 6 rotations. Slack-as-commander is informal heroics.
- **Portfolio recovery:** Not yet produced. `terminal_order_outcomes` on one path cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling Slack the commander encourages three controls: close when the first graph recovers, skip the journey that is still failing, and send platform-product work to whoever is already in the channel. Those moves may be sincere. They do not answer which journeys are still failed, which freeze still applies, or which on-call system Chapter 6 designed.

Closing on `order_success_ratio` makes outcome evidence a single **SLI**. Omitting freeze join makes Chapter 4 a brochure. Routing platform-product to Storefront reopens Chapter 2’s job-time confusion as an incident path.

#### Correction

The completed model does not close the spanning incident. It names a living primary as commander, lists both journeys and both tenant on-call systems, joins the Chapter 4 freeze actions, keeps status `open` while dispatch is failing, routes platform-product to `platform-oncall-system`, and treats inherited one-path evidence as insufficient to close.

That correction changes later decisions:

- Chapter 11 must require a learning record or expiring waiver for this complete command, not a blog post that says “be more careful.”
- Chapter 13 must exercise the on-call page path as these systems, not as a Slack channel discovered during the game day.
- Chapter 14 must not treat one-path `terminal_order_outcomes` as **Evidence of portfolio recovery**.

The design is practical because it changes the production contract across the rest of the book. Adding an arbitrary chat-ops bot would not make it more practical.

## 5. Production reality

### Common incident-command errors

#### Reusing DevOps one-change close as portfolio close

`terminal_order_outcomes` is inherited one-path evidence. It is not a portfolio close.

#### Closing because Storefront is green

Dispatch is a second journey. Green on one **SLI** is theater if the other is failing.

#### Slack as commander

A channel is not a role. Chapter 6 already refused it as primary.

#### Treating a catalog contact as the on-call system

`storefront-oncall` is a label. `storefront-oncall-system` is the system.

#### Skipping freeze join

If Chapter 4 already froze the digest and the fleet, the incident does not get to unfreeze by omission.

#### Routing platform-product to Storefront

Job-time is a **job-time budget**. It pages the platform rotation.

#### Emitting `status: recovered` on the trace

That forges later recovery evidence. This chapter may keep an incident `open` or `contained`. It may not declare the portfolio recovered.

#### Copying the spanning payment-and-dispatch trace onto every ticket

A platform-product incident is a different support kind. Copying journeys onto it recreates tenant-application coverage for job-time.

## 6. What changed

| Before | After |
|---|---|
| Commander was Slack. | **Commander is a living Chapter 6 primary; Slack is forbidden.** |
| Close used `order_success_ratio` and `terminal_order_outcomes`. | **Inherited one-path evidence is insufficient to close.** |
| Only Storefront was listed. | **The spanning trace names both journeys and both tenant on-call systems.** |
| Dispatch was still failing and the ticket was closed. | **Status stays `open` while dispatch is failing.** |
| Freeze stayed in the policy file. | **The trace joins `freeze-storefront-releases` and `freeze-fleet-storage-upgrade`.** |
| Platform-product landed on Storefront. | **Platform-product pages `platform-oncall-system`.** |

What changed was not merely three YAML files. Northwind now has a reviewable command contract that later learning, game days, and fail-over can consume without closing a Slack thread because one graph recovered.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Portfolio incident-command model | `incidents/command.yaml` and `incidents/roles.yaml` | They retain forbidden commanders, distinct roles, cadence, and insufficient close evidence later chapters must not replace with Slack. |
| Executed multi-service trace | `incidents/traces.yaml` | It retains spanning tenant-application command, freeze join, and a split platform-product trace. |

These artifacts should change when Northwind's journeys, on-call systems, freeze actions, or support kinds materially change—not whenever a new chat channel is created.

## What You Learned

A spanning incident is commanded as a portfolio, not as one failed change on one path. Inherited DevOps recovery evidence cannot close it. Storefront green cannot close Fulfillment. Chapter 4 freeze joins by id. Commander is a living primary, not Slack. Catalog contacts are not on-call systems. Platform-product pages the platform rotation. Schema checks can prove structural completeness within declared scope. They cannot run a real incident-management tool. A design earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Command a catalog-browse incident without copying the spanning trace**
>
> A storefront engineer wants to close the payment-and-dispatch incident “because catalog browse recovered, and that is what customers see,” and to page Storefront for a `catalog-freshness` stall “because they are already on.”

Extend the Chapter 10 model without adding a learning program yet:

1. Decide whether catalog-browse is in the spanning tenant-application incident, a separate tenant-application incident, or out of scope given Chapters 1–3.
2. Decide whether `catalog-freshness` is platform-product job-time and which Chapter 6 system it pages.
3. Name commander and operator without using Slack or copying `storefront-primary-a` from the payment trace as if browse were checkout.
4. State what would make close invalid—for example dispatch still failing.
5. Identify one observation that would falsify the command—for example freeze join omitted while Storefront budget is exhausted.
6. Explain which material change would trigger review of the command model, not just the chat channel.

Do not copy the payment-and-dispatch trace and rename it. Catalog reads have different criticality, support kind, and freeze consequences from checkout plus dispatch. Your durable output is the command decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 10 capability when you can explain why one-path close is invalid, name commander and both tenant journeys for a spanning incident, join Chapter 4 freeze, route platform-product to the platform rotation, refuse Slack as commander, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Incidents can be commanded. Learning is still a document with no verified follow-through. Postmortems are optional. Action items have no owner. The same payment retry cascade can return.

Chapter 11 adopts a learning-program contract so every complete Chapter 10 incident has a record or an expiring waiver, and so actions have owner, due date, and verification that is not the record approving itself.
