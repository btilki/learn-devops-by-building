# Support, Escalate, and Change the Platform Safely

Chapter 12 can move the fleet. Storefront is on `tenant-storage` `2.0`. Fulfillment’s `1.0` `class` binding is still legal. Support is still “message the people who built it.” Platform engineers apply live fixes with plane-admin. Tenants cannot tell a product incident from an application incident. Chapter 4 already named living escalation contacts. Chapter 8 already refused cluster-admin so onboarding works. A patch in place to clear a ticket is that token wearing a pager.

The production question is now:

> Who may change the platform, how are tenant incidents escalated, and what prevents informal production edits?

This chapter records support tiers, escalation that joins the catalog, a platform-product job-time budget rather than **CSAT (Customer Satisfaction)**, and a change path whose subject is reviewed. An unofficial plane-admin edit fails. Closing Fulfillment’s wait because Storefront’s orders look green fails. The inherited incident interface already names `terminal_order_outcomes`. Those are tenant-path recovery evidence. They are not **Evidence of bounded platform-product recovery**.

## 1. A live patch to clear a ticket

A weak record says:

```yaml
id: live-plane-patch
resource: kubernetes-control-plane
subject: plane-reconciler
approved_by: plane-reconciler
granted_role: cluster-admin
last_known_good: "1.1"
unofficial: true
ticket: fulfillment-warehouse-delay
escalation: chat-history
closed_reason: csat
error_budget_indicators: [order_success_ratio]
```

It does not identify a Chapter 4 on-call, a split between platform-product and tenant-application, a living approver, or Chapter 8’s retained plane last known good `1.0`. “Just patch it” may clear the chat. The reconciler approves itself. Last known good moves to the version Chapter 8 already failed. Fulfillment’s warehouse delay is closed because a survey smiled. Storefront’s order-success stands in for the platform-product job-time budget.

Work from the lab working tree using the Chapter 0 procedure. From the Platform lab root, run the Chapter 13 baseline:

```bash
make chapter-13-baseline
```

The command succeeds when it detects the intended unsafe support model:

```text
chapter 13 baseline: unofficial plane-admin patch correctly detected
```

The fixture lets `plane-reconciler` patch `kubernetes-control-plane` with `cluster-admin`, skip review, move last known good to `1.1`, escalate Fulfillment to chat history, close the ticket for CSAT, and meter the platform on `order_success_ratio`. The fleet can move. Change is still a hero in a shared chat.

That residual drives the chapter.

## 2. The production model: a ticket has a class, a change has a subject

> *Theory — Support, escalation, and platform-change authority*
>
> This model enables Fulfillment to finish `obtain-bounded-environment` and `ship-on-paved-road` by escalating a product wait to `platform-oncall` and an application delay to `fulfillment-oncall`, without a live plane patch substituting for a reviewed change.

### A tenant ticket is not a platform incident

Chapter 4 already bound every runnable system to a living owner and an escalation contact. This chapter loads that map. `fulfillment-api` is a tenant-application: owner `fulfillment-team`, escalation `fulfillment-oncall`. `environment-provisioning` is a platform-product: owner `platform-team`, escalation `platform-oncall`. `notification-service` is still a tenant-application on a Chapter 5 exit. An exit is not unsupported. An unofficial fork is. Chat history is.

Misclassifying a platform wait as Fulfillment’s warehouse bug sends the page to the wrong rotation. Classifying a warehouse delay as a plane incident invites the live patch this chapter refuses.

**Best Practice:** Map every catalog system to exactly one support class. Platform-product systems page `platform-oncall`. Tenant-application systems page the Chapter 4 tenant contact.

**Production Practice:** The platform-product job-time budget is Chapter 10’s job proofs `time-to-first-environment` and `paved-road-completion`. It is not a portfolio **SLO (Service Level Objective)**. Portfolio error-budget policy remains a Platform Chapter 1 non-goal with remaining owner `reliability-program`. `order_success_ratio` and `order_latency` stay tenant-workload non-metrics. CSAT and ticket volume stay vanity. Closing a product incident because those numbers moved fails.

### A platform change has a reviewed subject, not a pager token

Chapter 8’s plane subject is `plane-reconciler` with `may_approve_plane_change: false`. Last known good after the failed plane upgrade to `1.1` is still `1.0`. That is plane last known good. It is not Chapter 12’s contract last known good on `tenant-storage` `1.0`. Do not collapse them because both say `1.0`.

A reviewed change names `platform-team` as subject and approver, keeps `last_known_good: "1.0"`, and does not rewrite source. An unofficial change that grants `cluster-admin`, lets `plane-reconciler` approve itself, or moves last known good to `1.1` fails. The inherited evidence map requires an independent producer. A change file cannot emit `result: allow` to hide an unofficial patch.

**Production Practice:** Self-approval is not `subject == approved_by`. An allowed change fails when its `subject` or `approved_by` is a Chapter 8 plane identity (`kind: plane`). That identity is `plane-reconciler`, already flagged `may_approve_plane_change: false`. `platform-team` may appear in both fields because it is a living Chapter 1 user, not that plane subject. A governing team recorded as requester and approver inside its own domain is not an automation identity certifying itself.

They are not the same act:

| Act | Chapter | What it is |
|---|---|---|
| Supported exit | 5 | Leave the scaffold; remaining guardrails stay |
| Contract version bump | 7 | Leave a tenant-visible API version with a migration note |
| Guardrail exception | 9 | Temporary deviation; expiry lives on the inherited record |
| Non-metric demotion | 10 | Vanity leaves the indicator set |
| Fleet upgrade | 12 | Roll a Chapter 7 bump with freeze, cohort, and rollback |
| Platform change | 13 | Reviewed subject on the plane; unofficial plane-admin fails |

A live patch is not a fleet upgrade. It is not a Chapter 9 exception. It is not a Chapter 5 exit. Communication cadence is Chapter 12’s freeze window: seven days, the same TTL. Heroes in chat are not that cadence.

The inherited DevOps incident interface still requires `desired_actual_agreement`, `healthy_consecutive_samples`, and `terminal_order_outcomes` when an order path recovers. A platform-product incident may not list those as its recovery evidence. They prove Storefront’s workload, not that `obtain-bounded-environment` finished.

Do not restore mixed backups here. Chapter 14 will recover the plane against last known good and tenant isolation. This chapter must already refuse the unofficial patch that would become that mixed backup.

## 3. Support the product as a product

The completed Chapter 13 model uses four files:

```text
support/model.yaml
support/escalation.yaml
support/changes.yaml
support/incidents.yaml
```

The separation is deliberate. The model names tiers, unsupported paths, freeze cadence, and the job-time budget. Escalation binds every catalog system. Changes are the plane-authority record. Incidents are observations. The evaluator joins them to Chapter 1 users and brief, Chapter 4 systems and ownership, Chapter 8 subjects, plane product, and last known good, Chapter 10 indicators and non-metrics, and the inherited observability, incident, and evidence-map interfaces.

> **Practice — Split platform-product from tenant-application**
>
> Page `platform-oncall` for environment waits. Page `fulfillment-oncall` for warehouse delays. Do not close either for CSAT.

Open `support/model.yaml` and `support/escalation.yaml`. Tiers are `platform-product` and `tenant-application`. Unsupported paths are `unofficial-fork` and `chat-history`. Job-time budget indicators are `time-to-first-environment` and `paved-road-completion`. Every Chapter 4 system has a route whose owner and escalation match the catalog. `notification-service` stays on `storefront-oncall`. It left the scaffold. It did not leave support.

> **Practice — Keep Chapter 8 last known good on a reviewed plane change**
>
> `platform-team` may update admission. `plane-reconciler` may not approve that change. Last known good stays plane `1.0`.

Open `support/changes.yaml`:

```yaml
id: reviewed-admission-note
resource: kubernetes-control-plane
subject: platform-team
approved_by: platform-team
action: update-admission
last_known_good: "1.0"
current_version: "1.0"
unofficial: false
source_rewritten: false
result: allow
```

The evaluator loads Chapter 8’s failed plane upgrade and fails a change whose last known good is not `1.0`. It fails `cluster-admin`, a plane identity as subject or approver, and source rewrite. It loads Chapter 8 `forbidden_roles` live. Clearing that list does not make an `unofficial: true` patch legal. `platform-team` in both fields is the reviewed path, not the self-approval the live patch impersonates.

> **Practice — Record the ticket against the route, not against a smile**
>
> Fulfillment’s warehouse delay stays a tenant-application incident. Environment wait stays a platform-product incident with `time-to-first-environment`.

Open `support/incidents.yaml`. Neither row reports green. Neither closes for CSAT or `order_success_ratio`. The platform row does not list `terminal_order_outcomes`. Completeness is computed.

The lab does not operate a real ticketing system. Completeness is whether every catalog system has a living route, whether unofficial plane-admin fails, and whether the job-time budget is still Chapter 10’s job proofs.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-13-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 13 checkpoint: escalation routes and reviewed plane change verified
```

The audit validates the four Chapter 13 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- model owner is a living Chapter 1 user and the plane is `kubernetes-control-plane`;
- communication cadence is Chapter 12’s freeze window;
- job-time budget contains Chapter 1 brief success evidence and no vanity or tenant-workload ids;
- every Chapter 4 system has a route whose class, owner, and escalation match the catalog;
- chat history and unofficial forks are unsupported;
- an allowed change whose subject or approver is `plane-reconciler` fails self-approval; `platform-team` in both fields does not;
- unofficial or `cluster-admin` changes fail;
- plane last known good joins Chapter 8’s retained `1.0`;
- incidents match their routes and cannot close for CSAT or order-success; and
- a platform incident cannot borrow inherited tenant recovery evidence.

The expected plane, cadence, budget, and forbidden roles live in a separate checkpoint file. A support model under test does not emit its own passing grade.

The checkpoint does not prove that a real pager fired, that a real freeze stopped a merge, or that 48 hours is the right wait. Those remain claims a local lab cannot make.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 13 evidence |
|---|---|
| Mechanism evidence | Schemas and the support-and-change evaluator operated successfully. |
| Decision evidence | Tiers, routes, job-time budget indicators, reviewed subjects, and unsupported paths are explicit. |
| Outcome evidence | Fulfillment has a computed tenant-application incident. Environment wait has a computed platform-product incident. That is not proof an on-call engineer was paged. |
| Recovery evidence | Not produced. A denied live patch is a change-authority invariant, not restored isolation after a live plane edit. |

Chapter 13 produces mechanism, decision, and limited outcome evidence for support on an existing plane. Pretending the local checkpoint proves a ticketing vendor would weaken Chapter 14’s bounded recovery.

## 4. Test the design under failure

### Independent control failure — An engineer patches the control plane in place to clear a ticket, leaving no review and no last known good

> **Practice — Fail the live patch that clears Fulfillment’s ticket with plane-admin**
>
> Inject `plane-reconciler` as subject and approver, `cluster-admin`, last known good `1.1`, and `unofficial: true`, and refuse the change.

The completed support model is healthy. The failure command does not rewrite it. It injects the residual live-patch case against that snapshot:

```bash
make chapter-13-failure
```

Expected output:

```text
chapter 13 failure: unofficial plane-admin patch correctly rejected
```

The injected record is:

```yaml
id: live-plane-patch
resource: kubernetes-control-plane
subject: plane-reconciler
approved_by: plane-reconciler
action: patch-in-place
granted_role: cluster-admin
ticket: fulfillment-warehouse-delay
last_known_good: "1.1"
current_version: "1.1"
unofficial: true
source_rewritten: true
result: allow
```

Escalation routes stay on Chapter 4 contacts. Fulfillment’s incident stays tenant-application. The reviewed admission note stays `1.0`. The baseline’s chat-history route, CSAT close, and order-success as the job-time budget are not required for this failure. An unofficial patch can appear after the model already looks complete. Chapter 8 already failed the move to plane `1.1`. Last known good `1.1` is that failure, now used as a ticket-clearing write.

**Severity:** high; every later recovery conversation will restore an unofficial plane instead of reviewed last known good.  
**Plausible harm:** Fulfillment’s warehouse ticket closes; the reconciler holds cluster-admin; Storefront’s `2.0` and Fulfillment’s `1.0` share one patched plane; Chapter 14 then has a mixed backup.  
**Potential blast radius:** both application tenants and `kubernetes-control-plane`; a tenant ticket is no longer a separate support domain.  
**Bounded by:** Chapter 4 escalation, Chapter 8 last known good and forbidden roles, Chapter 10 non-metrics, and inherited incident and evidence-map interfaces. None of those repair an allowed unofficial patch.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence.

#### Platform questions

- **User and job:** Fulfillment must finish `ship-on-paved-road` or `obtain-bounded-environment`. A live plane patch to clear a warehouse ticket is not those jobs. It is shared authority substituting for a reviewed subject.
- **Isolation:** The boundary is Chapter 3’s tenant plus this classification: a tenant-application incident must not mutate the plane. Fulfillment’s blast radius must stop at Fulfillment. This is not a new tenancy model. It is change authority joined to Chapter 8’s plane subject.
- **Contract and exit:** The contract is the support model, the catalog route, and the reviewed change path. Teams do not leave it the way they leave a paved-road scaffold. A live patch is not a Chapter 5 exit, not a Chapter 7 version bump, not a Chapter 9 exception, not a Chapter 10 non-metric, and not a Chapter 12 fleet upgrade.
- **Platform-product evidence:** A closed ticket is not proof the product works. Required proof is a classified incident plus a reviewed plane change that still holds last known good `1.0`. This is a platform-product job-time budget, not a portfolio SLO. Storefront `order_success_ratio` remains tenant workload.

#### Diagnosis

Calling the write “so the ticket closes” encourages the same unofficial path Chapter 8 interrupted: Fulfillment is blocked, someone shares plane-admin, Storefront moves with the patch, and last known good becomes the broken version. Chat history becomes escalation. CSAT becomes closure. Order-success becomes the platform’s health. Inherited `terminal_order_outcomes` then look like recovery.

The missing class split makes Chapter 4’s contacts a directory. The missing review makes Chapter 8’s `may_approve_plane_change: false` ornamental. Last known good `1.1` makes Chapter 8’s failed upgrade a successful move. Closing for CSAT makes Chapter 10’s vanity refusal a memory.

#### Correction

The completed model does not allow `live-plane-patch`. The reviewed change keeps subject `platform-team`, last known good `1.0`, and `unofficial: false`. Fulfillment’s warehouse delay stays a tenant-application incident on `fulfillment-oncall`. Environment wait stays a platform-product incident on `time-to-first-environment`. Completeness is computed. The failure command proves the check still fails when only the unofficial patch is injected.

This failure is a change-authority invariant. It is not a runtime plane recovery. Do not call the denied patch **Evidence of restored isolation**. Nothing tenant-runtime was restored from a live edit. The product stopped treating a closed ticket as a plane change.

That correction changes later decisions:

- Chapter 14 must restore `kubernetes-control-plane` from reviewed last known good `1.0`, not from an unofficial `1.1` patch taken to clear a ticket.
- Mixed-backup restore must not replay a hero edit into another tenant.
- Support may not freeze every tenant because one warehouse ticket was noisy.
- Regional-loss and portfolio RTO remain SRE. This chapter does not claim them.

The design is practical because the failed unofficial patch is the product. Adding an arbitrary ticket vendor would not make it more practical.

## 5. Production reality

### Common support errors

#### Messaging the people who built it

Chapter 4 already named `fulfillment-oncall` and `platform-oncall`. Chat history is an unsupported path.

#### Patching the plane in place to clear a tenant ticket

Tenant-application incidents do not grant plane-admin. Chapter 8 already refused that bargain for onboarding.

#### Closing because CSAT or ticket volume moved

Those are Chapter 10 vanity non-metrics. Job time is the product indicator.

#### Borrowing Storefront order-success as the job-time budget

The inherited observability contract already owns those outcomes. They are tenant workload.

#### Collapsing plane 1.0 and contract 1.0

Chapter 8 retains plane last known good. Chapter 12 retains contract last known good. A live patch must not move either by accident.

#### Building mixed-backup restore in this chapter

Refuse unofficial plane-admin. Leave isolated restore to Chapter 14. Do not operate a real ticketing system.

## 6. What changed

| Before | After |
|---|---|
| `plane-reconciler` patched the plane with cluster-admin to clear a ticket. | **Unofficial plane-admin, self-approval, and missing last known good fail the change path.** |
| Fulfillment escalated to chat history. | **Every catalog system routes to its Chapter 4 contact.** |
| A product wait and a warehouse delay used the same queue. | **Platform-product and tenant-application are distinct classes.** |
| CSAT and order-success closed the incident. | **Vanity and tenant-workload ids cannot close a ticket or fill the job-time budget.** |
| A valid schema could appear to prove a pager fired. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely four YAML files. Northwind now has a support and change path Chapter 14 can recover against without treating a hero edit as last known good.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Support and escalation model | `support/model.yaml` and `support/escalation.yaml` | They retain the product/application split, freeze cadence, job-time budget, and Chapter 4 contacts later recovery must not replace with chat. |
| Platform-change authority record | `support/changes.yaml` | It retains the reviewed subject and Chapter 8 plane last known good an unofficial patch must not move. |

These artifacts should change when Northwind’s catalog systems, plane last known good, or Chapter 10 job proofs materially change—not whenever a chat tool is restyled.

## What You Learned

Support is a classified ticket plus a reviewed plane change. A live patch to clear Fulfillment’s warehouse delay is shared plane-admin, not a support path. Schema checks can prove structural completeness within declared scope. They cannot page a real on-call. A design earns its place when `environment-provisioning` pages `platform-oncall`, `fulfillment-api` pages `fulfillment-oncall`, and `plane-reconciler` cannot approve a patch that moves last known good to `1.1`.

### Prove It

> **Independent Practice — Route a read-only analytics outage without copying the live-patch row**
>
> A data-analytics path in `storefront-nonprod` pages at 02:00. Someone will offer to patch the plane so the ticket closes.

Extend the Chapter 13 model without adding mixed-backup restore yet:

1. Decide whether analytics is a tenant-application, a platform-product, or still not a platform job.
2. Name the Chapter 4 owner and escalation contact if it is a catalog system—or which unsupported path it is if it is an unofficial fork.
3. State whether the outage may close because CSAT moved, or because Storefront `order_latency` recovered.
4. Choose a sample that would falsify “analytics can be patched safely”—for example `plane-reconciler` as approver with last known good `1.1`.
5. Identify which last known good that sample must retain—plane version, contract version, or both.
6. Explain which material change would trigger review of the support model, not just one ticket.

Do not copy the Fulfillment live-patch row and rename it. Analytics has different class, escalation, and last-known-good consequences than a warehouse delay cleared with cluster-admin. Your durable output is the class-route-and-change decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 13 capability when you can explain why a live plane patch is not support, trace a ticket to a Chapter 4 contact and a Chapter 8 last known good, describe evidence that would falsify unofficial plane-admin, distinguish structural validation from decision and outcome evidence, and explain what the baseline, checkpoint, and failure command do and do not prove.

## Next

Support is explicit, but a control-plane outage can still become every tenant's outage. Backup of the plane is a job-success metric. Tenant isolation during restore is undefined. Restoring from a mixed backup can replay one tenant’s intent into another, or freeze all application traffic unnecessarily.

Chapter 14 recovers a control-plane failure without taking tenants with it, so mixed-tenant replay is rejected and Storefront can continue or freeze by explicit decision, not by accident.
