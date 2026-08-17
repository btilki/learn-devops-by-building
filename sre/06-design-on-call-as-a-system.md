# Design On-Call as a System

Chapter 5 pages journey burn at catalog contacts. `storefront-oncall`, `fulfillment-oncall`, and `platform-oncall` are who the catalog says to call. They are not a rotation, a load limit, a handoff, or authority. On-call is still whoever answered Slack.

The production question is now:

> Who is paged, with what load, escalation, handoff, and authority, and how is that different from a catalog contact?

Without that system, a contact is a hero roster. A rotation without load, handoff, or authority is Slack with a nicer name. Platform job-time tickets land on Storefront because “they are already up.” Inherited DevSecOps `self_approval_forbidden` already forbids a responder from approving their own break-glass. An on-call label that ignores that field is informal heroics wearing a catalog id.

This chapter designs on-call systems for Storefront, Fulfillment, and the platform product. It **references** catalog escalation ids. It adds rotation, load, handoff, and authority. It binds Chapter 5 pages to a living primary. It must not treat the contact label as the system.

## 1. An unsafe on-call label

A weak record says:

```yaml
id: storefront-oncall
primary: slack
handoff: none
```

It copies the catalog contact as the system id. It pages chat history. It has no secondary, no load limit, no recorded handoff, and no authority that consumes `self_approval_forbidden`. “Someone is in Slack” may describe last night. It cannot complete an on-call system.

Work from the lab working tree using the How to Use This Book procedure. From the SRE lab root, run the Chapter 6 baseline:

```bash
make chapter-06-baseline
```

The command succeeds when it detects the intended unsafe design:

```text
chapter 06 baseline: slack-as-primary without rotation correctly detected
```

The fixture treats `storefront-oncall` as the system, sets primary to Slack, omits handoff, lets platform destinations land on Storefront, and leaves `self_approval_forbidden` false. Pages still go to chat history. This is the book’s cumulative reliability failure continuing under a friendlier name: availability theater plus informal heroics, now wearing an escalation label.

That residual drives the chapter.

## 2. The production model: contact, rotation, load, handoff, authority

> *Theory — On-call as a system*
>
> This model enables Northwind to bind Chapter 5 pages to a living primary with load, handoff, and attributable authority rather than to a catalog label or a Slack channel.

### A catalog contact is an input, not the system

The inherited Platform catalog already names `storefront-oncall`, `fulfillment-oncall`, and `platform-oncall`. This chapter must not replace those ids and must not reuse them as the system id. A system **references** the contact. If `id: storefront-oncall`, the contact has been treated as the roster.

Three systems exist because three destinations exist. Storefront pages bind to the Storefront system. Fulfillment pages bind to the Fulfillment system. Platform tickets bind to the platform system. A platform destination that lands on Storefront’s rotation is the unofficial path Chapter 5 already refused for job-time pages.

### A rotation has a living primary and a secondary

A living primary is a named responder who is current as of a recorded time. `slack`, `chat-history`, and `whoever-answered` are not living primaries. A secondary exists so the primary is not a single hero. The evaluator checks that the primary is named and that `living_primary` is true. It cannot prove that the named person is awake. That limitation is honest.

**Best Practice:** Bind every Chapter 5 page destination to exactly one system, and every system to a rotation with a living primary and a secondary.

**Production Practice:** Slack-as-primary is the heroics path this book interrupts. A rotation that lists Slack as primary fails even if the catalog contact is correctly referenced.

### Load, compensation, and training are operational constraints

Page load is a numeric limit the rotation can absorb. Compensation and training are constraints on whether that limit is survivable. They are not an HR policy chapter. If the system cannot name a load limit, later toil bounds have nothing to protect. If compensation and training are “someone else’s problem,” the rotation will be staffed by whoever feels guilty.

### Handoff is a record, not a chat message

A rotation without a handoff is a shift that never ended. The handoff names from-primary, to-primary, and when it was recorded. Missing handoff is how Slack becomes the real primary at 17:01.

### Authority consumes DevSecOps; it does not rewrite it

Break-glass remains DevSecOps-attributable. The inherited authorization interface requires `self_approval_forbidden: true`. The inherited privilege interface requires requester, independent approver, expiry, and after-action review. This chapter consumes those fields. A primary who can approve their own freeze or break-glass is the unofficial path again.

The Storefront primary may act on Chapter 4’s freeze of Storefront releases. They may not approve that action as themselves. Reliability-program or a named independent approver remains in the record.

## 3. Design the on-call systems

The completed Chapter 6 model uses four files:

```text
oncall/system.yaml
oncall/rotations.yaml
oncall/handoffs.yaml
oncall/authority.yaml
```

The separation is deliberate. Systems reference catalog contacts and name load. Rotations name living primaries. Handoffs are the shift record. Authority consumes `self_approval_forbidden` and break-glass shape. Chapter 5 pages stay `destination_kind: catalog-contact`. This chapter binds those contacts to systems.

> **Practice — Reference the catalog contact; do not become it**
>
> Give Storefront, Fulfillment, and the platform product distinct system ids that point at the inherited escalation ids.

Open `oncall/system.yaml`. Storefront is recorded as:

```yaml
- id: storefront-oncall-system
  catalog_contact: storefront-oncall
  owner: storefront-team
  journeys: [accept-and-complete-order]
  page_load_limit: 8
  compensation: operational-constraint
  training: operational-constraint
```

Inspect each system with three questions:

1. Is `id` different from `catalog_contact`, or was the label copied as the roster?
2. Do Chapter 5 pages to that contact bind here, or to Slack?
3. Would a platform ticket still land on Storefront if this row were deleted?

`page_load_limit: 8` is a teaching value: eight pages per week before the rotation is overloaded. It is not an industry constant. Compensation and training are marked operational constraints so Chapter 7 can measure toil against a staffed rotation, not against unpaid heroics.

> **Practice — Name a living primary and record a handoff**
>
> Slack is not a primary. A shift without a handoff record is still Slack.

Open `oncall/rotations.yaml` and `oncall/handoffs.yaml`. Each system has a primary and a secondary. `living_primary` is true. `as_of` is `2026-08-16T00:00:00Z`. Each rotation has a handoff from one named primary to the next. If `primary: slack`, the checkpoint fails. If handoffs are empty, the checkpoint fails.

> **Practice — Bind authority to `self_approval_forbidden`**
>
> A responder may act on a freeze. They may not approve that action as themselves.

Open `oncall/authority.yaml`. Storefront freeze authority sets `self_approval_forbidden: true` to match the inherited authorization field. Break-glass names requester, independent approver, expiry, and `after_action_review: true`. If the approver equals the requester, the unofficial path is back.

Chapter 5 pages to `storefront-oncall` now resolve to `storefront-oncall-system` and its living primary. Pages to `fulfillment-oncall` resolve to Fulfillment. Tickets to `platform-oncall` resolve to the platform system. They must not resolve to Storefront.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-06-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 06 checkpoint: living rotations, handoffs, and attributable authority verified
```

The audit validates the four Chapter 6 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- every Chapter 5 page and platform ticket destination binds to a system whose `catalog_contact` matches;
- no system id equals its catalog contact;
- every system has a rotation with a living primary and a secondary;
- `slack`, `chat-history`, and `whoever-answered` are not primaries;
- every rotation has a handoff record;
- platform destinations do not land on Storefront’s rotation;
- `self_approval_forbidden` remains true; and
- break-glass names an independent approver, expiry, and after-action review.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not operate a real paging or calendar product. It does not prove that the named primary is trained or compensated. Those are judgment claims. The operational-constraint fields exist so later toil measurement cannot pretend staffing was free.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 6 evidence |
|---|---|
| Mechanism evidence | Schemas and the on-call evaluator operated successfully. |
| Decision evidence | Systems, rotations, handoffs, load limits, and attributable authority are explicit. |
| Outcome evidence | Not yet produced as a survived night; a living-primary flag is not proof someone woke. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 6 creates decision evidence about the human system. Pretending that the local checkpoint proved a real responder answered would weaken every later incident, game day, and fail-over.

## 4. Test the design under failure

### Cumulative reliability failure — Pages still go to chat history

> **Practice — Bind pages to rotations and interrupt Slack-as-primary**
>
> Give each catalog contact a system, a living primary, a handoff, and authority that cannot self-approve.

The baseline fixture contains this model:

```yaml
- id: storefront-oncall
  catalog_contact: storefront-oncall
  primary: slack
  handoff: none
  self_approval_forbidden: false
```

The problem is not merely missing YAML. The model treats the catalog label as the roster and Slack as the primary. Platform tickets can follow Storefront because that is who is in the channel. A freeze can be self-approved because authority was never designed.

**Severity:** high; Chapter 5’s journey pages have no human system, so Chapter 4’s freeze is a file nobody is obligated to enact.  
**Plausible harm:** order-success burn pages Slack; the named engineer is not on shift; platform wait time wakes Storefront; a self-approved break-glass has no after-action review.  
**Potential blast radius:** every catalog contact used as a chat mention; Fulfillment and platform inherit Storefront’s channel.  
**Bounded by:** later toil bounds, incident command, and game-day page-path exercises. None repairs a roster that is a Slack channel.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** `accept-and-complete-order` pages a contact with no living primary. `dispatch-fulfillment` is in the same channel if only one label exists.
- **Error budget:** Applicable as the freeze the primary must be able to enact. Chapter-local implication: Slack cannot freeze `storage-1-0-to-2-0` with attributable authority.
- **Human system:** Applicable as the chapter’s subject. Slack-as-primary is informal heroics. Load, handoff, and independent approval are the system.
- **Portfolio recovery:** Not yet produced. A Slack mention cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling the roster `storefront-oncall` encourages label controls: paste the catalog id, mention the channel, skip handoff because “we all saw the message.” Those moves may find a human once. They do not answer who is primary as of now, who is secondary, what load is allowed, or who can approve break-glass without self-approval.

The missing rotation makes Chapter 5’s page map a destination without a person. The missing handoff makes the last shift the permanent primary. `self_approval_forbidden: false` makes DevSecOps ornamental. Routing platform destinations to Storefront finishes the collapse: job-time again wakes the order path.

#### Correction

The completed model does not page Slack. It references each catalog contact from a distinct system, names living primaries and secondaries, records handoffs, limits page load, keeps compensation and training as operational constraints, consumes `self_approval_forbidden`, and keeps platform destinations on the platform rotation.

That correction changes later decisions:

- Chapter 7 must measure toil against these rotations, not against “we were in Slack.”
- Chapter 10 must page these systems, not a one-path hero.
- Chapter 13 must exercise the on-call page path, not a catalog mention.
- Chapter 14 must not invent a commander from chat history.

The design is practical because it changes the production contract across the rest of the book. Adding an arbitrary command would not make it more practical.

## 5. Production reality

### Common on-call errors

#### Treating the catalog contact as the system

The contact is how the catalog points at a team. The system is rotation, load, handoff, and authority.

#### Slack-as-primary

A channel is a distribution surface. It is not a living primary.

#### Skipping handoff because the same person stays on

A record is how the next primary exists. Chat is how the last primary never ends.

#### Landing platform pages on Storefront

Job-time and plane issues belong on the platform rotation. Storefront cannot absorb them as courtesy.

#### Self-approved break-glass

Inherited `self_approval_forbidden` is the named field. Do not invert it to ship faster.

#### Calling compensation and training “HR”

If the rotation cannot be staffed, later **SLOs (Service Level Objectives)** are theater. Name the constraints here; do not write the payroll policy.

## 6. What changed

| Before | After |
|---|---|
| `storefront-oncall` was the system. | **Each system references a catalog contact and has a different id.** |
| Primary was Slack. | **Each rotation has a living primary and a secondary.** |
| Handoff was a chat message. | **Each rotation has a recorded handoff.** |
| Platform tickets woke Storefront. | **Platform destinations bind to the platform system.** |
| Break-glass could self-approve. | **`self_approval_forbidden` remains true; approver is independent.** |
| Load, compensation, and training were implied. | **Load is numeric; compensation and training are operational constraints.** |
| A valid schema could appear to prove a roster. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely four YAML files. Northwind now has a reviewable human system that later toil, incidents, and game days can page without treating Slack as the roster.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| On-call system contract | `oncall/system.yaml` | It retains the reference from catalog contact to system, load, and operational constraints later chapters must not replace with a channel name. |
| Rotation-and-handoff record | `oncall/rotations.yaml` and `oncall/handoffs.yaml` | They retain living primaries and the shift record a page actually binds to. |

These artifacts should change when Northwind's catalog contacts, staffing, or authority model materially change—not whenever a chat tool is renamed.

## What You Learned

An on-call system references a catalog contact and adds rotation, load, handoff, and authority. The contact label is not the system. Slack is not a living primary. Platform destinations must not land on Storefront. Break-glass remains DevSecOps-attributable through `self_approval_forbidden`. Schema checks can prove structural completeness within declared scope. They cannot operate a real paging calendar. A design earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Staff catalog-browse pages without copying the Fulfillment rotation**
>
> A storefront engineer wants catalog-browse burn to page `storefront-oncall` “because Fulfillment already has a rotation we can paste.”

Extend the Chapter 6 model without adding toil policy yet:

1. Decide whether catalog-browse pages share the Storefront system or need a distinct rotation.
2. If they share Storefront, show how page load stays inside the numeric limit.
3. Name a living primary that is not Slack and not a pasted Fulfillment id.
4. Record a handoff; keep `self_approval_forbidden` true.
5. Identify one observation that would falsify the design—for example platform tickets landing on this rotation.
6. Explain which material change would trigger review of the system, not just the chat mention.

Do not copy the Fulfillment rotation and rename it. Catalog reads have different load and freeze consequences from warehouse dispatch. Your durable output is the system decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 6 capability when you can explain why a catalog contact is not an on-call system, bind every Chapter 5 page to a living primary, refuse Slack-as-primary, keep platform destinations off Storefront, consume `self_approval_forbidden`, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Humans can be paged with a rotation, a handoff, and attributable authority. Most of their week is still unmeasured tickets, silences, and copy-paste runbooks. “We will automate later” has no bound.

Chapter 7 measures and bounds toil so reliability engineering remains possible, and so a new critical SLO cannot be added because on-call “already watches email.”
