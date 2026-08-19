# Run Game Days as a Recurring Program

Chapter 12 named two regions, numeric portfolio objectives, and inherited restores as insufficient. That architecture still sits on paper. The only practiced recovery nearby is Platform’s mixed-backup isolation test. There is no cadence, no blast-radius contract, and no join to Chapter 11 learning. A single fixture becomes “we do game days.”

The production question is now:

> How does Northwind exercise reliability controls on a cadence, including failures that are not one mixed-backup fixture, without taking the portfolio down for real?

Without that program, unbounded chaos becomes an outage. A game day that cannot fail is theater. This chapter must exercise error-budget freeze, on-call page path, dependency loss, and regional-loss tabletop or simulated fail-over. It is not a rehearsal of Chapter 14 executed fail-over. It does not chaos-test a live fleet. It does not produce **Evidence of portfolio recovery**.

## 1. An unsafe annual mixed-backup

A weak record says:

```yaml
scenario: mixed-backup
cadence: annual
status: complete
```

It files Platform Chapter 14’s mixed-backup fixture as the year’s game day and marks the program complete. It never exercises a Chapter 4 freeze, a Chapter 6 page path, a Chapter 8 dependency loss, or a Chapter 12 tabletop. “We restored a backup once” may describe an isolation test. It cannot complete a reliability game-day program.

Work from the lab working tree using the How to Use This Book procedure. From the SRE lab root, run the Chapter 13 baseline:

```bash
make chapter-13-baseline
```

The command succeeds when it detects the intended unsafe design:

```text
chapter 13 baseline: single mixed-backup game day marked complete correctly detected
```

The fixture stores one `mixed-backup` result, stamps the program complete, omits cadence as a recurrence contract, records no abort, and never joins learning. A Platform isolation fixture has been treated as the SRE program. Informal heroics have been scheduled once a year.

That inversion drives the chapter.

## 2. The production model: cadence, coverage, abort, learning join

> *Theory — Recurring game-day program*
>
> This model enables Northwind to exercise freeze, page path, dependency loss, and regional-loss tabletop on a cadence, rather than by marking a single mixed-backup fixture complete.

### A game day is not chaos and not Chapter 14 fail-over

A game day is a scoped, abortable exercise of a named control. Chaos without a blast-radius contract is an outage with a calendar invite. A **DR (disaster recovery)** restore of one backup is not a portfolio game-day program. Chapter 14 will execute regional fail-over against Chapter 12 objectives. This chapter **tabletops or simulates** regional loss. If a scenario’s kind is `chapter-14-failover`, the program has skipped ahead and left freeze, paging, and dependency unexercised.

**Best Practice:** Require four kinds before anyone talks about complete: `error-budget-freeze`, `on-call-page-path`, `dependency-loss`, and `regional-loss-tabletop`.

**Production Practice:** `mixed-backup` may exist as a fixture. It is `insufficient-alone`. It cannot complete the program.

### Cadence and abort keep the blast radius declared

Cadence is a teaching value: `90d`. It is not an industry constant. Annual-once is not recurrence; it is a holiday. Abort when blast radius would exceed the contract: `blast-radius-exceeds-contract`. An unbounded-chaos attempt that would take the live portfolio down must record `disposition: abort`. A program with no abort path cannot fail safely.

The lab does not chaos-test a live fleet. Results are local fixtures, like Chapter 3’s event counts.

### Results feed Chapter 11; they do not emit recovered

Game-day results join the learning register. The dependency-loss result feeds `verify-payment-retry-shed`. That is already an owned, independently verified action. The program does not invent a hortatory “be more careful next game day.” It does not stamp `status: recovered`. A successful tabletop is mechanism and decision evidence. It is not **Evidence of portfolio recovery**.

Joins are explicit:

| Kind | Joins |
|---|---|
| error-budget-freeze | Chapter 4 `freeze-storefront-releases` |
| on-call-page-path | Chapter 6 `storefront-oncall-system` |
| dependency-loss | Chapter 8 `payment`, feeds Chapter 11 cascade action |
| regional-loss-tabletop | Chapter 12 `region-primary` → `region-standby`, mode `tabletop` |

Paging Slack, paging a catalog contact, or treating email as the dependency drill reopens earlier chapters under a game-day name.

## 3. Publish program, scenarios, and results

The completed Chapter 13 model uses three files:

```text
gamedays/program.yaml
gamedays/scenarios.yaml
gamedays/results.yaml
```

The separation is deliberate. The program names cadence, required kinds, abort rule, learning join, and that mixed-backup cannot complete it. Scenarios bind kinds to earlier artifact ids. Results record in-bounds runs, an abort, and mixed-backup as insufficient-alone. None of the files may emit `recovered`.

> **Practice — Forbid completing the program on mixed-backup alone**
>
> Keep `mixed-backup` insufficient-alone. Do not skip the four required kinds.

Open `gamedays/program.yaml`. Owner is `reliability-program`. Cadence is `90d`. `required_kinds` lists the four kinds. `abort_when` is `blast-radius-exceeds-contract`. `learning_join` is `northwind-learning-actions`. `forbidden_complete_on` is `mixed-backup`. `not_chapter_14_failover` is true. If `complete: true` appears because mixed-backup ran, the checkpoint fails.

> **Practice — Bind each required kind to an earlier control**
>
> Freeze joins a Chapter 4 action id. Page path joins a Chapter 6 system. Dependency loss is payment, not email. Regional loss is tabletop.

Open `gamedays/scenarios.yaml`. Teaching rows include freeze, page path, payment dependency loss, regional-loss tabletop, mixed-backup marked `insufficient_alone`, and an unbounded-chaos row whose only legal result is abort. The regional row `mode` is `tabletop`. If that mode is `chapter-14-failover`, the program rehearsed the next chapter.

Inspect each scenario with three questions:

1. Which earlier chapter’s artifact does this exercise—or is it only a backup job?
2. What blast radius is declared, and what abort fires if it would be exceeded?
3. Would this still be a game day if mixed-backup were deleted?

> **Practice — Record four in-bounds results, one abort, and mixed-backup as insufficient-alone**
>
> Feed the dependency result into the Chapter 11 cascade action. Do not stamp recovered.

Open `gamedays/results.yaml`. Four in-bounds results cover the required kinds. One abort records `blast-radius-exceeds-contract`. The mixed-backup result is `insufficient-alone`. The dependency result `feeds_action` is `verify-payment-retry-shed`. Quoted `as_of` values are RFC 3339. If only mixed-backup is `complete`, the program has not run.

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
chapter 13 checkpoint: freeze, page path, dependency, and regional tabletop coverage verified
```

The audit validates the three Chapter 13 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- cadence is a recurrence, not `annual` as the only event;
- four required kinds have in-bounds results;
- mixed-backup cannot complete the program;
- an abort is recorded for blast radius that would exceed the contract;
- freeze joins a Chapter 4 freeze action;
- page path joins a Chapter 6 on-call system, not Slack or a catalog contact;
- dependency loss is payment (or warehouse), not email as a critical drill;
- regional loss is tabletop, not Chapter 14 fail-over;
- results feed a Chapter 11 action; and
- `status: recovered` is not emitted.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not chaos-test a live fleet. It does not prove that 90 days is the right commercial cadence. Those are judgment claims. The review trigger exists so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 13 evidence |
|---|---|
| Mechanism evidence | Schemas and the game-day evaluator operated successfully. |
| Decision evidence | Cadence, required kinds, abort, learning join, and mixed-backup insufficiency are explicit. |
| Outcome evidence | Completeness is computed from four in-bounds kinds plus abort, not emitted from mixed-backup. |
| Recovery evidence | Not yet produced; Chapter 14 must prove **Evidence of portfolio recovery** in the model. |

Chapter 13 creates decision evidence about how controls are exercised. Pretending that the local checkpoint proved a production game day would weaken executed fail-over.

## 4. Test the design under failure

### Independent control failure — Mixed-backup filed as the annual game day and marked complete

> **Practice — Fail completeness; add freeze, page path, dependency, and regional tabletop; require recurrence**
>
> Drop `complete` on mixed-backup alone. Record an abort path.

The baseline fixture contains this model:

```yaml
scenario: mixed-backup
cadence: annual
status: complete
```

The problem is not merely a missing calendar. Platform’s isolation fixture has been treated as the SRE program. Freeze, paging, payment loss, and regional tabletop never ran. There is no abort. Learning is not joined. Chapter 12’s architecture remains unexercised. Chapter 14 is either skipped or silently rehearsed as “we already restored a backup.”

**Severity:** high; the first real region loss still invents the plan, and exhausted budget still has never been frozen in an exercise.  
**Plausible harm:** mixed-backup succeeds; freeze is unpracticed; Slack is the page path; payment loss is a surprise; regional tabletop never happened.  
**Potential blast radius:** every annual “game day” that is one fixture; every unbounded chaos drill without abort.  
**Bounded by:** later executed fail-over. None repairs a program that cannot fail.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** Freeze and payment-loss drills protect `accept-and-complete-order`. Regional tabletop protects both journeys. Mixed-backup alone protects neither as a portfolio exercise.
- **Error budget:** Applicable as the freeze scenario joining Chapter 4. Skipping it leaves freeze unpracticed.
- **Human system:** Applicable as the page-path scenario joining Chapter 6. Mixed-backup does not page a living primary.
- **Portfolio recovery:** Not yet produced. A mixed-backup complete flag cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling mixed-backup complete encourages three controls: skip the other kinds because a restore ran, skip abort because the fixture is safe, and skip learning because the slide is green. Those moves may be sincere. They do not answer whether freeze still joins, whether the page hit a Chapter 6 system, or whether regional loss was tabletopped against Chapter 12.

A `chapter-14-failover` scenario would make the same mistake in the other direction: rehearsing execution while freeze and paging stay theoretical.

#### Correction

The completed model does not mark mixed-backup complete. It requires four kinds, records in-bounds results for each, aborts unbounded blast radius, joins freeze, on-call, payment, and regional tabletop, feeds Chapter 11, and forbids treating this program as Chapter 14 fail-over.

That correction changes later decisions:

- Chapter 14 must execute fail-over against Chapter 12, not copy these tabletop results as **Evidence of portfolio recovery**.
- Mixed-backup remains an isolation fixture. It still cannot close the reliability program.

The design is practical because it changes the production contract across the rest of the book. Adding an arbitrary chaos product would not make it more practical.

## 5. Production reality

### Common game-day errors

#### Completing on one mixed-backup result

Insufficient-alone means the program is not done.

#### Rehearsing Chapter 14 as the only scenario

Tabletop regional loss. Do not skip freeze, paging, and dependency.

#### Annual-once cadence

A holiday is not a program.

#### No abort path

If blast radius cannot fail the exercise, the exercise cannot be safe.

#### Paging Slack or a catalog contact

Chapter 6 already refused that as the system.

#### Email as the dependency drill

Chapter 8 already kept notification non-critical.

#### Hortatory follow-up instead of a Chapter 11 action

Results feed owned verification, not “be more careful.”

#### Storing recovered on the result

A tabletop is not portfolio recovery.

## 6. What changed

| Before | After |
|---|---|
| Mixed-backup was marked complete. | **Mixed-backup is insufficient-alone; four kinds have in-bounds results.** |
| Cadence was annual-once. | **Cadence is `90d`.** |
| There was no abort. | **Unbounded blast radius records `abort`.** |
| Freeze, page path, and payment were unexercised. | **Each kind joins a Chapter 4, 6, or 8 artifact.** |
| Regional loss was either skipped or Chapter 14. | **Regional loss is `tabletop` against Chapter 12.** |
| Learning was not joined. | **The dependency result feeds `verify-payment-retry-shed`.** |

What changed was not merely three YAML files. Northwind now has a reviewable game-day program that later fail-over can follow without pretending a backup fixture was the reliability program.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Game-day program contract | `gamedays/program.yaml` | It retains cadence, required kinds, abort, learning join, and mixed-backup insufficiency later execution must not replace with one fixture. |
| Scenario-and-result register | `gamedays/scenarios.yaml` and `gamedays/results.yaml` | They retain the four exercised kinds, the abort, and tabletop regional loss. |

These artifacts should change when Northwind's freeze actions, on-call systems, dependencies, or regions materially change—not whenever a backup job is renamed.

## What You Learned

A game-day program recurs, declares blast radius, and can abort. Completeness requires freeze, page path, dependency loss, and regional-loss tabletop—not a single mixed-backup result, and not a rehearsal of Chapter 14. Results feed Chapter 11. Schema checks can prove structural completeness within declared scope. They cannot chaos-test a live fleet. A design earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Exercise catalog-browse without copying mixed-backup or the payment drill**
>
> A storefront engineer wants to mark the program complete “because mixed-backup already ran, and browse can reuse the payment dependency scenario.”

Extend the Chapter 13 model without adding executed fail-over yet:

1. Decide whether catalog-browse needs its own scenario kind or is out of scope given Chapters 1–3 and 8.
2. If you add a result, keep mixed-backup `insufficient-alone`.
3. Do not page Slack, and do not treat the result as Chapter 14 fail-over.
4. Join or refuse a Chapter 11 action without hortatory text.
5. Identify one observation that would falsify completeness—for example only mixed-backup marked complete.
6. Explain which material change would trigger review of the program, not just the backup fixture name.

Do not copy the payment dependency row and rename it. Catalog reads have different criticality and freeze consequences from checkout. Your durable output is the coverage decision and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 13 capability when you can explain why mixed-backup cannot complete the program, name the four required kinds, record an abort, join freeze, on-call, payment, and regional tabletop, refuse Chapter 14 rehearsal, feed Chapter 11, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

The program can exercise controls. An actual regional fail-over has not been proven. A region is lost. The temptation is to reconstruct one environment, restore the plane from newest, or invent the order during the outage.

Chapter 14 executes fail-over against Chapter 12, keeps tenant isolation, and produces **Evidence of portfolio recovery** that cannot hide a missed **RTO (Recovery Time Objective)**, a missed **RPO (Recovery Point Objective)**, or collapsed isolation.
