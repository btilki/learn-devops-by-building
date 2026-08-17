# Page on Burn Rate, Not on Every Symptom

Chapter 4 can freeze a digest and a fleet step when remaining budget is exhausted. Humans are still woken by every red graph. CPU pages. Replica Ready pages. Portal errors page. `order_success_ratio` burn is a dashboard panel. Inherited DevOps Chapter 6 already defined a provisional fast and slow burn for Storefront. That rule is a single-service interface. It is not a portfolio page policy.

The production question is now:

> Which burn rates page a human, which create tickets, and which symptoms must not wake anyone?

Without that map, symptom pages train people to ignore journeys. Missing burn pages leave exhausted budget silent until a customer complains. Platform job-time burn pages Storefront because leadership can see time-to-first-environment. Chapter 2 already kept that proof adjacent. Chapter 5 must not page it as if it were `accept-and-complete-order`.

This chapter defines multi-window burn alerts that page on user-journey burn and ticket the rest. It does not reteach logs, metrics, or traces. Catalog destinations `storefront-oncall`, `fulfillment-oncall`, and `platform-oncall` are contacts. Chapter 6 will turn them into an on-call system. A page that emits `user_impact: true` is not evidence that a user was harmed.

## 1. An unsafe page map

A weak record says:

```yaml
- id: page-cpu
  burn: cpu-utilization
  destination: storefront-oncall
  user_impact: true
- id: panel-order-success
  burn: order_success_ratio
  disposition: dashboard
```

It pages a component symptom at a catalog contact and treats journey burn as a tile. “The CPU is high” may justify a ticket. It cannot complete a page. `user_impact: true` written by the page is a slogan.

Work from the lab working tree using the Chapter 0 procedure. From the SRE lab root, run the Chapter 5 baseline:

```bash
make chapter-05-baseline
```

The command succeeds when it detects the intended unsafe mapping:

```text
chapter 05 baseline: cpu paging storefront while order burn is a panel correctly detected
```

The fixture pages `cpu-utilization` at `storefront-oncall`, stamps `user_impact: true`, leaves `order_success_ratio` as a dashboard panel, and may page job-time at Storefront. Symptom noise has been treated as user impact. Inherited burn windows have been ignored. Exhausted Chapter 4 budget can freeze a fleet while nobody is paged for the journey.

That inversion drives the chapter.

## 2. The production model: paired windows, page versus ticket, minimum volume

> *Theory — Burn-alert disposition*
>
> This model enables Northwind to wake a human for user-journey burn and to ticket or record the rest, without reteaching observability fundamentals.

### A burn alert is a paired window, not a red tile

DevOps Chapter 6 already recorded fast burn (`5m` and `1h`, threshold `14.4`) and slow burn (`30m` and `6h`, threshold `6`) for `order_success_ratio`. Those numbers are teaching values. This chapter **consumes** them. It does not rewrite them into a new observability stack, and it does not pretend they are industry constants.

Fast burn catches urgent consumption of error budget. Slow burn catches sustained consumption that a short spike would miss. A single CPU threshold is not a paired window. A dashboard panel is not a burn alert.

Fulfillment reuses the same inherited window pairs on `dispatch_success_ratio`. That is extending the interface to a second journey. It is not copying Storefront’s **SLO (Service Level Objective)** target. Chapter 3 already forbade that copy.

### Page, ticket, and record are different dispositions

| Disposition | When | Destination |
|---|---|---|
| page | Fast or slow burn of an accepted user-journey **SLI (Service Level Indicator)** | Catalog contact for that journey |
| ticket | Adjacent job-time burn, or a component symptom that still needs an owner | `platform-oncall` for job-time and theater |
| record | A graph that must not wake anyone and need not open a ticket | No page, no ticket |

`order_success_ratio` pages `storefront-oncall`. `dispatch_success_ratio` pages `fulfillment-oncall`. `time-to-first-environment` tickets `platform-oncall` and must not page Storefront. CPU and replica Ready do not page. Replica Ready may ticket. CPU may record.

**Best Practice:** Require a minimum evidence volume on every page. One failed request is not a burn.

**Production Practice:** A page is only real when it names a Chapter 2 accepted user-journey SLI, a paired window, a catalog contact, and a volume floor. A page that emits `user_impact` has forged outcome evidence.

### Inherited burn is an interface, not a rewrite

Do not replace `5m` / `1h` / `14.4` with a vendor-specific “anomaly score” and call it maturity. Do not drop slow burn because fast burn already pages. Do not point Storefront’s inherited windows at `time-to-first-environment` and call that portfolio coverage.

Job-time proofs remain a **job-time budget**. Their alerts are tickets to the platform contact. They are not pages on the order path.

### A catalog contact is not yet an on-call system

`storefront-oncall` is who the catalog says to call. It is not a rotation, a load limit, a handoff, or authority. Chapter 6 will bind these pages to living primaries. Chapter 5 must already refuse to page CPU at that contact. Otherwise Chapter 6 inherits a hero roster whose first job is silencing symptoms.

## 3. Define the page-versus-ticket map

The completed Chapter 5 model uses three files:

```text
alerting/burns.yaml
alerting/pages.yaml
alerting/tickets.yaml
```

The separation is deliberate. Burns name SLI, window pair, class, volume floor, and disposition. Pages bind journey burns to catalog contacts. Tickets bind job-time and remaining symptoms. Pages must not carry a `user_impact` field.

> **Practice — Consume the inherited fast and slow windows**
>
> Keep `5m`/`1h`/`14.4` and `30m`/`6h`/`6` on user-journey burns. Do not rewrite them.

Open `alerting/burns.yaml`. The method records those pairs once and applies them to `order_success_ratio` and `dispatch_success_ratio`. `minimum_evidence_volume` is 50 valid events. That number is a teaching floor. It exists so a single error cannot page.

User-journey burns have `disposition: page`. Job-time has `disposition: ticket`. CPU has `disposition: record`. Replica Ready has `disposition: ticket`.

> **Practice — Page journey burn at the matching catalog contact**
>
> Fast and slow `order_success_ratio` page `storefront-oncall`. Fast and slow `dispatch_success_ratio` page `fulfillment-oncall`.

Open `alerting/pages.yaml`. Each page names a burn id, a destination contact from the inherited catalog, and `destination_kind: catalog-contact`. If `destination_kind` is `on-call-system`, Chapter 6 has been skipped. If `user_impact` appears, the page has approved itself.

Inspect each page with three questions:

1. Is the SLI an accepted user-journey indicator from Chapter 2?
2. Would this still page if the CPU graph were deleted?
3. Is the destination a catalog contact for that journey, or whoever answered last time?

> **Practice — Ticket job-time and symptoms; do not page Storefront for them**
>
> `time-to-first-environment` tickets `platform-oncall`. CPU does not page. Replica Ready does not page.

Open `alerting/tickets.yaml`. The job-time ticket destination is `platform-oncall`. A row that pages Storefront for environment wait time reopens Chapter 2. Replica Ready may open a platform ticket. CPU is recorded, not paged.

### Prove the capability

Run the artifact audit and completed checkpoint:

```bash
make audit
make chapter-05-checkpoint
```

Expected output includes:

```text
inherited interface verification: passed
artifact validation: passed
chapter 05 checkpoint: journey burn pages and symptom tickets verified
```

The audit validates the three Chapter 5 files against pinned structural schemas. The checkpoint then applies semantic checks that schema validation alone cannot provide:

- fast and slow burns of `order_success_ratio` page `storefront-oncall`;
- fast and slow burns of `dispatch_success_ratio` page `fulfillment-oncall`;
- inherited window pairs are consumed, not rewritten;
- CPU and replica Ready do not page;
- `time-to-first-environment` tickets `platform-oncall` and does not page Storefront;
- every page names `destination_kind: catalog-contact` and has no `user_impact` field;
- minimum evidence volume is greater than one; and
- page targets are accepted user-journey SLIs.

The expected identifiers live in a separate checkpoint file. The model under test does not emit its own passing expectations.

The checkpoint does not send a real page. It does not prove that 14.4 or 50 events are the right commercial thresholds. Those are judgment claims. The review triggers exist so the judgments can be reopened without pretending they were never made.

This distinction is the chapter's evidence model:

| Evidence category | Chapter 5 evidence |
|---|---|
| Mechanism evidence | Schemas and the alerting evaluator operated successfully. |
| Decision evidence | Page versus ticket versus record, catalog contacts, and inherited windows are explicit. |
| Outcome evidence | Not yet produced as live user impact; a page must not emit `user_impact`. |
| Recovery evidence | Not yet produced; later chapters must prove **Evidence of portfolio recovery** in the model. |

Chapter 5 creates decision evidence about who is woken. Pretending that the local checkpoint proved a customer felt the burn would weaken every later on-call, incident, and fail-over.

## 4. Test the design under failure

### Independent control failure — CPU pages Storefront while order burn is a panel

> **Practice — Invert the mapping**
>
> Page journey burn; ticket or record component symptoms; drop forged `user_impact`.

The baseline fixture contains this model:

```yaml
pages:
  - id: page-cpu
    burn: cpu-utilization
    destination: storefront-oncall
    user_impact: true
burns:
  - id: panel-order-success
    sli: order_success_ratio
    disposition: dashboard
```

The problem is not merely a missing dispatch page. The model treats a symptom as the reason to wake Storefront and treats the Chapter 2 accepted SLI as decoration. Forged `user_impact` makes the page look like outcome evidence. Job-time can follow the same path next.

**Severity:** high; the humans who must act on Chapter 4’s freeze are woken by CPU and sleep through order burn.  
**Plausible harm:** Storefront silences CPU while orders fail; Fulfillment is never paged; platform wait time pages the wrong contact.  
**Potential blast radius:** every catalog contact asked to “just add the graph”; inherited burn windows unused.  
**Bounded by:** later on-call systems, incident command, and dependency contracts. None repairs a map that pages symptoms and panels journeys.  
**Primary principles:** explicit contracts, trustworthy evidence, blast-radius control.

#### Reliability questions

- **Journey:** `accept-and-complete-order` is the journey CPU does not measure. `dispatch-fulfillment` is still silent if only Storefront CPU pages.
- **Error budget:** Applicable as the thing burn consumes. Chapter-local implication: a CPU page cannot freeze Storefront releases; an unpaged `order_success_ratio` burn can sit at the Chapter 4 freeze band with no human.
- **Human system:** Not yet applicable as rotation design. Chapter-local implication: paging CPU at `storefront-oncall` trains whoever answers that contact to hunt nodes instead of orders.
- **Portfolio recovery:** Not yet produced. A silenced CPU page cannot become **Evidence of portfolio recovery**.

#### Diagnosis

Calling the page “CPU is user-visible” encourages symptom controls: scrape kubelet, count Restarts, stamp `user_impact: true` so the ticket looks serious. Those graphs may be true. They do not name a good-event ratio, a paired window, or a minimum volume. Leaving `order_success_ratio` on a panel makes Chapter 3’s SLO and Chapter 4’s freeze ornamental at 2 a.m.

Paging `time-to-first-environment` at Storefront would finish the collapse: Chapter 2’s adjacent decision undone by the loudest tile.

#### Correction

The completed model does not page CPU. It pages fast and slow burns of `order_success_ratio` and `dispatch_success_ratio` at the matching catalog contacts, tickets job-time to `platform-oncall`, tickets replica Ready, records CPU, consumes inherited window pairs, requires a volume floor, and forbids `user_impact` on the page.

That correction changes later decisions:

- Chapter 6 must bind these pages to rotations, not to a new CPU roster.
- Chapter 8 must page payment burn as Storefront journey burn, not as a provider tile equal to email.
- Chapter 9 must not page Fulfillment for Storefront payment slowness.
- Chapter 10 must not close an incident because CPU recovered.

The design is practical because it changes the production contract across the rest of the book. Adding an arbitrary command would not make it more practical.

## 5. Production reality

### Common alerting errors

#### Paging the loudest graph

CPU, replica Ready, and portal errors are easy to scrape. They are not user-journey burn.

#### Leaving inherited burn on a dashboard

DevOps Chapter 6 already named the windows. A panel is not a page.

#### Paging Storefront for job-time

Time-to-first-environment is adjacent. Ticket `platform-oncall`.

#### Forging user impact on the page

Outcome evidence is computed remaining budget and later recovery. A boolean on the alert is not that evidence.

#### Paging on one event

Minimum volume exists so a single error cannot wake the contact. Choose a floor and review it.

#### Treating the catalog contact as the on-call system

Chapter 5 may destination a contact. Chapter 6 must still add rotation, load, and handoff. Do not skip that by naming the contact `on-call-system` here.

## 6. What changed

| Before | After |
|---|---|
| CPU paged `storefront-oncall`. | **CPU is recorded; it does not page.** |
| `order_success_ratio` burn was a dashboard panel. | **Fast and slow order-success burns page `storefront-oncall`.** |
| Dispatch had no page. | **Fast and slow dispatch burns page `fulfillment-oncall`.** |
| Job-time could page Storefront. | **`time-to-first-environment` tickets `platform-oncall`.** |
| Pages stamped `user_impact: true`. | **Pages cannot emit user impact.** |
| Inherited windows were ignored or rewritten. | **`5m`/`1h`/`14.4` and `30m`/`6h`/`6` are consumed as interface.** |
| A valid schema could appear to prove a sound page. | **Structural, decision, outcome, and recovery evidence remain distinct.** |

What changed was not merely three YAML files. Northwind now has a reviewable page-versus-ticket contract that later on-call, incidents, and game days can bind without waking people for theater.

## Durable outputs

Retain these reviewed outputs:

| Artifact | Location | Keep it because |
|---|---|---|
| Burn-alert contract | `alerting/burns.yaml` | It retains paired windows, dispositions, and the volume floor later pages must not replace with a symptom threshold. |
| Page-versus-ticket map | `alerting/pages.yaml` and `alerting/tickets.yaml` | They retain which burns wake a catalog contact and which must not. |

These artifacts should change when Northwind's journeys, accepted SLIs, or inherited window policy materially change—not whenever a new graph is added to the dashboard.

## What You Learned

A reliability program pages on user-journey burn and tickets or records the rest. Inherited DevOps burn windows are an interface, not a rewrite. CPU and replica Ready must not page. Job-time tickets the platform contact. A page cannot emit user impact. Catalog contacts are destinations, not yet an on-call system. Schema checks can prove structural completeness within declared scope. They cannot send a real page. A design earns its place when it changes later production implementation, evidence, diagnosis, or recovery.

### Prove It

> **Independent Practice — Alert catalog-browse burn without copying the dispatch page**
>
> A storefront engineer wants a fast-burn page for `catalog_read_success_ratio` at `storefront-oncall` “because customers hit that page more than they order.”

Extend the Chapter 5 model without adding rotation policy yet:

1. Decide whether catalog-browse burn pages, tickets, or records, given Chapter 2 and Chapter 3 treatments of catalog reads.
2. If you page, consume the inherited window pairs rather than inventing a one-window CPU-style threshold.
3. Name the catalog contact and keep `destination_kind: catalog-contact`.
4. Set a minimum evidence volume that is not 1.
5. Identify one observation that would falsify the disposition—for example CPU still pages while this burn is a panel.
6. Explain which material change would trigger review of the alert, not just the dashboard widget.

Do not copy the dispatch page and rename it. Catalog reads have different criticality and freeze consequences from warehouse dispatch. Your durable output is the disposition and its reasoning, not the number of YAML lines changed.

You can demonstrate the Chapter 5 capability when you can explain why a CPU page is not journey burn, trace every page to an accepted user-journey SLI and a catalog contact, ticket job-time to `platform-oncall`, refuse `user_impact` on the page, consume inherited window pairs, distinguish structural validation from decision and outcome evidence, and explain what the baseline and completed checkpoint do and do not prove.

## Next

Pages now have a destination in the catalog. On-call is still whoever answered Slack. `storefront-oncall` is a label. It has no rotation, load, handoff, or authority.

Chapter 6 designs on-call as a system so these pages bind to a living primary rather than to a contact treated as the roster.
