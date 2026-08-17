# Practical SRE Engineering — Book-claim → evaluator matrix

**Status:** Verified against `v1.0-chapter-14-complete`  
**Date:** 2026-08-17  
**Scope:** Chapters 1–14. Independent Practice and “explain why / distinguish evidence kinds” claims are reader-owned by design and are not lab gates.

Legend:

- **Bound** — the named evaluator fails if the claim is false.
- **Reader** — the chapter requires the reader to explain it; the lab does not grade the explanation.
- **Unaided** — Independent Practice. Catalog-browse continues; the lab does not copy the guided example.

Baseline gates load `checkpoints/chapter-NN/cases/unsafe-*.yaml`. Checkpoint gates load the working-tree artifacts. Schema audit (`make audit`) is structural only.

| Ch | Book claim | Evaluator | Status |
|---:|---|---|---|
| 1 | Cluster / API uptime is not success evidence | `chapter-01` baseline requires `brief uses theater success evidence: cluster-uptime`; evaluate rejects theater and job-time proofs on the brief and on journey `later_proof` | Bound |
| 1 | `accept-and-complete-order` has an accountable owner | Baseline requires `journey has no accountable owner: accept-and-complete-order`; checkpoint requires owners `reliability-program`, Storefront, Fulfillment, platform | Bound |
| 1 | Journeys name a known user, failed outcome, owner, and later proof | Evaluate: `journey has no known user`, `no failed outcome`, `no accountable owner`, `no later proof`; checkpoint requires `order_success_ratio` / `dispatch_success_ratio` | Bound |
| 1 | Refusals name a remaining owner | Evaluate: `refusal has no remaining owner`; checkpoint requires uptime, job-time-as-SLO, and inherited-restore refusals | Bound |
| 1 | Catalog-browse as journey or supporting signal | Independent Practice | Unaided |
| 2 | Job-time must not be classed `portfolio-slo` | Baseline requires `decision uses forbidden class: time-to-first-environment/portfolio-slo` and `job-time accepted` | Bound |
| 2 | Accept Storefront `order_success_ratio` and Fulfillment `dispatch_success_ratio` | Checkpoint requires those accepts; evaluate traces accept → Chapter 1 journey; inherited observability ids must match | Bound |
| 2 | Keep `time-to-first-environment` adjacent with Chapter 1 remaining owner | Evaluate: required adjacent, remaining-owner match to refusal `platform-job-time-as-slo` | Bound |
| 2 | Reject CPU, replica Ready, portal uptime | Required reject set; `theater accepted` is an error | Bound |
| 2 | Forbidden justifications `leadership-can-see-it`, `dashboard-already-has-it`, `copied-from-storefront` | Method must list them; accept using them fails | Bound |
| 2 | Catalog-browse ratio accept / adjacent / reject | Independent Practice | Unaided |
| 3 | A copied 99.9% from Storefront is not a portfolio | Baseline: missing `dispatch-fulfillment` SLO; evaluate: `fulfillment slo copied from storefront` | Bound |
| 3 | Every critical SLO traces to a Chapter 1 journey and Chapter 2 accepted SLI | `slo has no known journey`, `slo uses unaccepted sli`, `slo catalogs job-time`, `slo catalogs theater` | Bound |
| 3 | Remaining budget is computed from observations, not emitted | `catalog emits remaining budget`; `remaining_fraction` vs observation events | Bound |
| 3 | SLA text is not an SLO target | Baseline: `sla text used as slo target`; required out-of-scope `customer-availability-sla` | Bound |
| 3 | `notification-service` is not a critical SLO | Required non-critical; `non-critical system cataloged as slo` | Bound |
| 3 | Catalog-browse SLO without copying dispatch | Independent Practice | Unaided |
| 4 | Exhausted Storefront budget freezes releases and fleet step `storage-1-0-to-2-0` | Baseline: `unfrozen exhausted budget: storage-1-0-to-2-0`; checkpoint required freeze / slow / continue | Bound |
| 4 | Fleet freeze must not copy Platform upgrade fields or relabel `platform-upgrade-freeze` | Baseline: `fleet freeze copies platform field: freeze/rollback`; `relabels platform upgrade freeze` | Bound |
| 4 | Fulfillment stays slow, not frozen, while dispatch still has budget | Required slow target `fulfillment-releases` | Bound |
| 4 | Exceptions expire | Baseline: `exception has no expiry: exception-ship-anyway` | Bound |
| 4 | Policy does not emit remaining budget | `policy emits remaining budget`; remaining is computed | Bound |
| 4 | Catalog experiment exception vs freeze | Independent Practice | Unaided |
| 5 | CPU must not page Storefront while order burn is a panel | Baseline: `symptom pages: cpu-utilization/storefront-oncall`; missing `order_success_ratio` fast/slow pages | Bound |
| 5 | Pages bind accepted user-journey SLIs and catalog contacts | `page uses unaccepted sli`; `page is not a catalog contact` | Bound |
| 5 | Job-time tickets `platform-oncall`; symptoms do not page | Required tickets; `job-time pages: time-to-first-environment/storefront-oncall` | Bound |
| 5 | Pages must not emit `user_impact` | `page emits user impact` | Bound |
| 5 | Inherited burn window pairs are consumed, not rewritten | `inherited slow burn windows rewritten`; minimum evidence volume > 1 | Bound |
| 5 | Catalog-browse burn page vs ticket | Independent Practice | Unaided |
| 6 | Catalog contact is not an on-call system | Baseline: `catalog contact treated as system: storefront-oncall` | Bound |
| 6 | Slack is not primary; living primary required | `slack-as-primary`; `missing living primary` | Bound |
| 6 | Every Chapter 5 page binds a rotation | Required rotations for Storefront and Fulfillment systems | Bound |
| 6 | Platform destinations stay off Storefront | `platform destination landed on storefront` | Bound |
| 6 | Authority consumes inherited `self_approval_forbidden` | `self-approval not forbidden`; `inherited self_approval_forbidden ignored`; break-glass self-approval | Bound |
| 6 | Handoffs exist | Required handoff ids | Bound |
| 6 | Catalog-browse staffing vs Fulfillment paste | Independent Practice | Unaided |
| 7 | “We are busy” is not a numeric bound | Baseline: `bound is not numeric: we-are-busy` | Bound |
| 7 | Toil fraction is computed from hours, not emitted | `bound emits toil fraction rather than computing it`; `toil_fraction()` | Bound |
| 7 | Inventory items are classified | `inventory item is unclassified: tickets` | Bound |
| 7 | `notification-service` must not become a new critical SLO | `new critical slo allowed`; required deny; forbidden justification `on-call-already-watches-email` | Bound |
| 7 | Breach blocks new critical SLO scope | `new critical slo allowed while bound breached` | Bound |
| 7 | Catalog-browse toil without copying Fulfillment | Independent Practice | Unaided |
| 8 | Payment failure burns Storefront; `no_user_impact` is forbidden | Baseline: `payment failure does not burn storefront`; `dependency emits no user impact`; missing forbidden claim | Bound |
| 8 | Email / `notification-service` is not a critical page | `email paged as critical: notification-service` | Bound |
| 8 | Warehouse is attributed to Fulfillment | `warehouse not attributed to fulfillment` | Bound |
| 8 | Timeout and retry budget exist; cascade is not claimed solved | Required timeout / retry budget; no cascade-solved claim in evaluate | Bound |
| 8 | Catalog-browse provider without copying payment | Independent Practice | Unaided |
| 9 | Unbounded payment retries are not a contract | Baseline: `unbounded retries: payment`; missing required shed | Bound |
| 9 | Shed new accepts; degraded success is not success | `degraded success counted as success`; required shed `payment` | Bound |
| 9 | User-visible mode accounted as journey-burn | `missing user-visible degraded mode`; remaining budget must not be emitted | Bound |
| 9 | Must not page Fulfillment as the payment cause | `fulfillment paged as payment cause` / `must_not_page` | Bound |
| 9 | Catalog-browse shed without copying payment refuse-new | Independent Practice | Unaided |
| 10 | One-path close while dispatch fails is invalid | Baseline: `one-path close: order_success_ratio`; missing `dispatch-fulfillment` | Bound |
| 10 | Slack is not commander | `slack-as-commander` | Bound |
| 10 | Spanning incident names both tenant journeys and joins Chapter 4 freeze | Required journeys; `missing freeze join: freeze-storefront-releases` | Bound |
| 10 | Platform-product job-time does not land on Storefront | `platform-product landed on storefront` | Bound |
| 10 | Catalog contact is not the command system | `catalog contact treated as system` | Bound |
| 10 | Traces do not emit recovered | `trace emits recovered` | Bound |
| 10 | Catalog-browse incident vs spanning paste | Independent Practice | Unaided |
| 11 | Hortatory postmortem is not a control | Baseline: `hortatory action: be-more-careful`; `record verifies itself: polished-postmortem` | Bound |
| 11 | Every Chapter 10 id has a record or expiring waiver | `missing required record`; `missing waiver expiry` | Bound |
| 11 | Cascade action has owner, due date, independent producer | `missing independent verification`; `missing action owner`; `missing action due date`; `repeated cascade without verified action` | Bound |
| 11 | Records do not emit `verified` / `learned` as self-proof | Self-verification walk; independent producer required | Bound |
| 11 | Catalog-browse coverage without copying spanning record | Independent Practice | Unaided |
| 12 | Inherited restore is not regional recovery | Baseline: `inherited restore claimed as regional recovery`; insufficient restores include DevOps reconstruction and plane restore | Bound |
| 12 | Two regions, active-passive order, numeric RTO/RPO | Missing `region-standby`; `failover order is not active-passive`; `rto is not numeric: as-fast-as-possible` | Bound |
| 12 | Isolation survives fail-over; payment and warehouse are region-scoped | `missing isolation constraint`; `missing provider regionality` | Bound |
| 12 | Plane `1.0` and `tenant-storage-1.0` stay distinct insufficient identities | `collapsed restore identities` | Bound |
| 12 | Consume Platform `not-regional-loss` and `not-portfolio-rto` | `limitations_consumed` must include inherited limitations | Bound |
| 12 | Architecture does not emit recovered | `architecture emits recovered` | Bound |
| 12 | Catalog-browse data placement without copying payment | Independent Practice | Unaided |
| 13 | Mixed-backup alone cannot complete the program | Baseline: `single mixed-backup completes program`; results `insufficient-alone` | Bound |
| 13 | Four required kinds: freeze, page path, dependency, regional tabletop | Missing `error-budget-freeze`; joins freeze action, on-call system, payment/warehouse, architecture | Bound |
| 13 | Cadence is recurrence; abort exists | `cadence is not recurrence: annual`; `missing abort` | Bound |
| 13 | Not a Chapter 14 fail-over; does not emit recovered | `not_chapter_14_failover`; `game day emits recovered` | Bound |
| 13 | Results feed Chapter 11 | `missing learning join`; `results do not feed chapter 11 action` | Bound |
| 13 | Catalog-browse scenario without copying mixed-backup | Independent Practice | Unaided |
| 14 | Mixed-region newest / mixed-tenant replay is not fail-over | Baseline: `mixed-region replay applied`; `mixed-tenant replay accepted` | Bound |
| 14 | Lost region isolated; tenants continue or freeze explicitly | `lost region is not isolated`; `missing continue or freeze` | Bound |
| 14 | Numeric RTO/RPO met; commander is an on-call primary | `rto missed: 86400`; `commander is not an on-call primary` | Bound |
| 14 | Inherited restores and game days are not portfolio recovery | `inherited restore claimed as portfolio recovery`; `game day claimed as portfolio recovery` | Bound |
| 14 | Verification does not emit `status: recovered` or `slo_met` | `verification emits recovered`; `verification emits slo_met` | Bound |
| 14 | Journey SLO outcomes computed from independent observations vs Chapter 3 catalog | `journey slo not met: accept-and-complete-order/order_success_ratio`; missing observation rows | Bound |
| 14 | Consume `not-regional-loss` / `not-portfolio-rto`; plan follows Chapter 12 architecture | Plan/architecture join; inherited limitations | Bound |
| 14 | Catalog-browse fail-over without copying Storefront freeze | Independent Practice | Unaided |

## Cross-cutting claims

| Book claim | Bound to | Status |
|---|---|---|
| Structural validation ≠ decision / outcome / recovery evidence | Schema audit vs checkpoint; Ch14 forbids self-emitted `recovered` / `slo_met` | Bound for recovery stamps; Reader for the taxonomy itself |
| Platform job-time is never a portfolio SLO | Ch2 adjacent, Ch3 `slo catalogs job-time`, Ch5 job-time tickets, Ch10 platform-product routing | Bound |
| Catalog `*-oncall` is a contact, not a system | Ch5 `destination_kind: catalog-contact`; Ch6 / Ch10 catalog-contact-as-system | Bound |
| Error budget is SRE-only; Platform fleet freeze is referenced, not copied | Ch4 copy/relabel detectors | Bound |
| **Evidence of portfolio recovery** is Chapter 14 only | Ch12–13 forbid `recovered`; Ch14 computes isolation, RTO/RPO, and journey SLOs | Bound |
| Lab states are start / baseline / complete (plus challenge write-up) | Snapshot tags + `make chapter-NN-baseline` / `checkpoint` | Bound |

## Gate summary

| Gate | Result |
|---|---|
| Machine-checkable guided claims | 14/14 chapters bound to baseline (red) and checkpoint (green) |
| Independent Practice (catalog-browse) | 14/14 unaided by design |
| Dedicated `chapter-NN-failure` Make targets | None (SRE uses baseline + checkpoint) |
| P0 unbound guided claim | None |

This file is an audit record. It is not a reader-facing chapter and is not part of the Word manuscript.
