# Turn Incidents into a Reliability Learning Program

Chapter 10 can command a spanning incident without closing because Storefront looks green. Command is not learning. Postmortems are optional. Action items have no owner. The same Chapter 9 payment retry cascade can return. A polished write-up that says “be more careful” is blameless theater.

The production question is now:

> What learning program turns incidents into owned, verified change, rather than into blameless theater?

Without that decision, a template without verification is a blog post. Blame without a system produces silence. Action volume without a bound recreates Chapter 7 toil. Inherited DevSecOps already requires that verification be produced independently of the record that claims it. A learning file that stamps `verified: true` on itself is the same self-approval Chapter 3 refused for remaining budget. This chapter is not eradication, and it is not a second DevOps one-change retrospective.

This chapter adopts a learning-program contract: which Chapter 10 incidents require a record, how actions are owned and dated, what independent verification looks like, and when the program itself is failing. The lab cannot prove that an organization actually learned.

## 1. An unsafe learning write-up

A weak record says:

```yaml
incident: spanning-payment-and-dispatch
actions:
  - be-more-careful
verified: true
```

It has a polished postmortem. It names no owner, no due date, and no verification independent of the write-up. The Chapter 9 cascade has no owned change. The platform-product trace has neither a record nor an expiring waiver. “We talked about it” may describe last week’s meeting. It cannot complete a learning program.

Work from the lab working tree using the Chapter 0 procedure. From the SRE lab root, run the Chapter 11 baseline:

```bash
make chapter-11-baseline
```

The command succeeds when it detects the intended unsafe decision:

```text
chapter 11 baseline: hortatory postmortem without verified action correctly detected
```

The fixture stores a hortatory action, lets the record verify itself, omits owner and due date, leaves the Chapter 9 cascade without a verified action, and leaves `platform-product-job-time` uncovered. A document has been treated as a control. Informal heroics have been treated as follow-through.

That inversion drives the chapter.

## 2. The production model: record or waiver, owned action, independent verification

> *Theory — Learning as a control*
>
> This model enables Northwind to turn commanded incidents into owned, dated, independently verified change, rather than into a blameless blog post that cannot stop a repeated cascade.

### Every commanded incident is covered, or explicitly waived

Chapter 10 produced two traces: `spanning-payment-and-dispatch` and `platform-product-job-time`. Both are commanded incidents. Silence is not coverage. Each id needs a record or a waiver. A waiver is not a missing file. It names owner, `expires_at`, and a removal path, the same shape Chapter 4 already required for error-budget exceptions.

Teaching coverage: the spanning tenant-application incident gets a record with contributing factors. The platform-product job-time incident gets a waiver with expiry. That waiver is a reviewable choice, not “job-time does not count.” Copying the spanning record onto job-time would pretend checkout-plus-dispatch contributing factors apply to `time-to-first-environment`.

The record is blameless contributing-factor analysis, not a named human as the cause. A dashboard, alert, page, or postmortem is still only mechanism evidence. It is not proof that a journey kept its **SLO (Service Level Objective)**.

**Best Practice:** Require a record or an expiring waiver for every Chapter 10 incident id before calling the program complete.

**Production Practice:** The spanning cascade incident cannot be waived away while Chapter 9 shedding is the change that must be verified.

### Actions have owner, due date, and verification the record cannot emit

“Be more careful” is hortatory. It is forbidden as an action id and as a change. An action names an owner, a quoted RFC 3339 `due_at`, and a verification producer that is not the record. Inherited DevSecOps `independent_producer_required: true` is consumed here. If `verification.producer` is the record id, the write-up has approved itself.

The teaching action `verify-payment-retry-shed` addresses `chapter-09-cascade`. Its producer is the Chapter 9 shed rule `shed-storefront-payment-overload`. That is independent of `record-spanning-payment-and-dispatch`. The action file must not stamp `verified: true`. Outcome evidence is that the producer exists and is distinct, not a boolean the action stores.

A repeated Chapter 9 cascade with no such verified action means the learning program has failed, even if the postmortem is excellent.

### Learning is bounded by toil, and is not eradication

Unbounded action lists recreate Chapter 7 homework. The program **joins** `northwind-toil-bound`. It does not invent a second hour inventory. If the join is missing, later game days will attach infinite follow-up to every fixture.

This program is not DevSecOps eradication and not **Evidence of restored trust**. It is not a rewrite of DevOps Chapter 12’s one-change retrospective. Those remain inherited. Substituting them for verified reliability change leaves the cascade free to return.

The lab cannot prove that an organization actually learned. Records, waivers, and action joins are local fixtures.

## 3. Adopt the program, records, and actions

The completed Chapter 11 model uses three files:

```text
learning/program.yaml
learning/records.yaml
learning/actions.yaml
```

The separation is deliberate. The program names required incidents, forbidden hortatory labels, independent verification, the toil join, and when the program fails. Records and waivers cover Chapter 10 ids. Actions carry owner, due date, and a producer that is not the record. None of the files may emit `verified: true` or `learned: true`.

> **Practice — Forbid hortatory actions and self-verification**
>
> Keep `be-more-careful` off the action list. Do not let a record verify itself.

Open `learning/program.yaml`. Owner is `reliability-program`. `required_incidents` lists both Chapter 10 trace ids. `forbidden_actions` includes `be-more-careful`. `verification_independent` is true. `toil_join` is `northwind-toil-bound`. `program_fails_when` is `repeated-cascade-without-verified-action`. Forbidden substitutes include `devsecops-eradication` and `devops-one-change-retrospective`.

> **Practice — Cover every Chapter 10 incident with a record or an expiring waiver**
>
> Do not copy the spanning record onto job-time.

Open `learning/records.yaml`. `record-spanning-payment-and-dispatch` is a record for the spanning incident, with contributing factors that include the retry cascade and one-path command. `waiver-platform-product-job-time` is a waiver for the platform-product trace, owner `reliability-program`, quoted `expires_at`, and a removal path to write a record or a verified action. If the waiver has no expiry, it is silence with nicer YAML.

> **Practice — Own the cascade change and verify it from Chapter 9 shedding, not from the write-up**
>
> A missing cascade action fails the program even when the postmortem exists.

Open `learning/actions.yaml`. `verify-payment-retry-shed` names incident `spanning-payment-and-dispatch`, owner `reliability-program`, quoted `due_at`, change `consume-chapter-09-payment-shed`, `addresses: chapter-09-cascade`, and verification producer `shed-storefront-payment-overload` with `independent_of_record: true`. If `due_at` is missing, the action is a slogan. If the producer is the record id, the slogan has a checkbox.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-11-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 11 checkpoint: records or waivers, owned actions, and independent verification verified
```

The audit validates the three Chapter 11 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- both Chapter 10 incident ids have a record or an expiring waiver;
- waivers name owner, expiry, and removal path;
- hortatory `be-more-careful` cannot be an action;
- every action has owner and `due_at`;
- verification is independent of the record, consuming DevSecOps `independent_producer_required`;
- a Chapter 9 cascade action exists and is independently verified;
- the program joins the Chapter 7 toil bound;
- `verified: true` and `learned: true` are not stored on the files; and
- eradication and one-change retrospective are not substitutes.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint cannot prove that an organization actually learned. It does not prove that 30 days is the right commercial review cadence. Those are judgment claims. The review trigger exists so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 11 evidence |
|---|---|
| Mechanism evidence | Schemas and the learning evaluator operated successfully. |
| Decision evidence | Program contract, coverage of Chapter 10 ids, forbidden hortatory labels, and toil join are explicit. |
| Outcome evidence | Cascade follow-through is joined to an independent Chapter 9 producer, not emitted as `verified: true`. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 11 creates decision evidence about how incidents become change. Pretending that the local checkpoint proved a culture learned would weaken later game days and fail-over.

## 4. Test the decision under failure

### Independent control failure — Polished postmortem with hortatory actions

> **Practice — Replace hortatory actions with owned, dated, independently verified change**
>
> Cover the platform-product incident. Verify the cascade from the shed, not from the write-up.

The baseline fixture contains this model:

```yaml
incident: spanning-payment-and-dispatch
actions:
  - be-more-careful
verified: true
```

The problem is not merely a missing field. A blameless document exists. The Chapter 9 cascade can repeat. The platform-product incident has no waiver. The record is the verifier. That is availability theater applied to learning: the slide is green, the control did not change production.

**Severity:** high; the same retry storm returns, and Chapter 10 command becomes a meeting that produces prose.  
**Plausible harm:** payment overload cascades again; freeze is re-joined in Slack; job-time incidents vanish without expiry.  
**Potential blast radius:** every polished template; every “be more careful” backlog.  
**Bounded by:** later game-day join to these actions. None repairs a program that cannot fail.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** The spanning record is about `accept-and-complete-order` and `dispatch-fulfillment`. Hortatory text does not change those journeys.
- **Error budget:** Not a new freeze. Chapter-local implication: unverified cascade follow-through leaves Chapter 4 freeze as a recurring surprise.
- **Human system:** Applicable as load. Unbounded actions recreate Chapter 7 toil on the Chapter 6 rotations.
- **Portfolio recovery:** Not yet produced. A postmortem cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling the write-up complete encourages three controls: skip owners because the prose is good, skip dates because “we all know,” and tick verified because the record exists. Those moves may be sincere. They do not answer which Chapter 9 producer changed, which Chapter 10 id is uncovered, or what would falsify the program.

Self-verification makes outcome evidence a constant. Silence on `platform-product-job-time` makes Chapter 10’s second trace ornamental. Hortatory actions make blamelessness a tone rather than a system.

#### Correction

The completed model does not keep `be-more-careful`. It covers both Chapter 10 ids, owns a cascade action dated and verified from the Chapter 9 shed, joins the Chapter 7 toil bound, forbids the record as verifier, and treats a repeated cascade without that action as program failure.

That correction changes later decisions:

- Chapter 13 must feed game-day results into these actions, not into a new hortatory list.
- Chapter 14 must not treat a completed postmortem as **Evidence of portfolio recovery**.
- Regional architecture in Chapter 12 still has to be written; learning does not invent a second region.

The decision is practical because it changes the production contract across the rest of the book. Adding an arbitrary retrospective workshop would not make it more practical.

## 5. Production reality

### Common learning errors

#### Hortatory actions

“Be more careful” cannot be verified. A shed rule can.

#### Letting the record verify itself

Independent producer is the inherited evidence-map rule. A checkbox on the write-up is self-approval.

#### Optional postmortems

Silence on a Chapter 10 id is not a waiver. A waiver expires.

#### Copying one record onto every incident

Job-time is not checkout-plus-dispatch. Coverage is per id.

#### Unbounded action volume

Without the Chapter 7 join, learning becomes the next toil inventory.

#### Substituting eradication or a one-change retrospective

Those are inherited programs with different promises. They do not verify a portfolio cascade action.

#### Storing `learned: true`

The program can fail. A stored success flag cannot.

## 6. What changed

| Before | After |
|---|---|
| The action was `be-more-careful`. | **The cascade action is owned, dated, and forbidden to be hortatory.** |
| The record stamped `verified: true`. | **Verification producer is the Chapter 9 shed, independent of the record.** |
| Platform-product had no coverage. | **It has an expiring waiver with owner and removal path.** |
| The spanning incident had prose only. | **It has a contributing-factor record plus a verified cascade action.** |
| Action volume was unbounded. | **The program joins `northwind-toil-bound`.** |
| A valid schema could appear to prove learning. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a reviewable learning control that later game days and fail-over can join without treating a blog post as follow-through.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Learning-program contract | `learning/program.yaml` | It retains required incidents, forbidden hortatory labels, independent verification, toil join, and program-failure conditions later chapters must not replace with a template. |
| Action-verification register | `learning/records.yaml` and `learning/actions.yaml` | They retain coverage of Chapter 10 ids and the cascade action whose producer is not the record. |

These artifacts should change when Northwind's incident ids, cascade controls, or toil bound materially change—not whenever a new retrospective template is adopted.

## What You Learned

Learning is a reliability control: record or expiring waiver per commanded incident, owned dated actions, and verification independent of the write-up. Hortatory actions fail. A repeated Chapter 9 cascade without a verified action fails the program. The program joins the toil bound and does not substitute eradication or a one-change retrospective. Schema checks can prove structural completeness within declared scope. They cannot prove an organization actually learned. A decision earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Cover a catalog-browse incident without copying the spanning record**
>
> A storefront engineer wants a one-line action “be more careful about search” and to mark the spanning payment record as covering browse “because it is the same postmortem.”

Extend the Chapter 11 model without adding regional architecture yet:

1. Decide whether catalog-browse needs its own record, a waiver, or is out of scope given Chapters 1–3 and 10.
2. If you add an action, give it owner and `due_at`; do not use `be-more-careful`.
3. Name a verification producer that is not the spanning payment record.
4. Do not emit `verified: true` or `learned: true`.
5. Identify one observation that would falsify coverage—for example the Chapter 9 cascade repeating with no shed-joined action.
6. Explain which material change would trigger review of the program, not just the template.

Do not copy the spanning record and rename it. Catalog reads have different contributing factors and freeze consequences from checkout plus dispatch. Your durable output is the coverage decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 11 capability when you can explain why a polished postmortem is not a control, cover every Chapter 10 id with a record or expiring waiver, own a cascade action with independent verification, refuse hortatory text, join the toil bound, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Learning can change the portfolio. The architecture still assumes one region. Platform Chapter 14 restored a control plane inside one region and recorded `not-regional-loss` and `not-portfolio-rto`. DevOps Chapter 13 reconstructed one environment. “We have backups” is not multi-region.

Chapter 12 writes a regional-loss architecture with numeric portfolio **RTO (Recovery Time Objective)** and **RPO (Recovery Point Objective)**, and lists those inherited restores as insufficient.
