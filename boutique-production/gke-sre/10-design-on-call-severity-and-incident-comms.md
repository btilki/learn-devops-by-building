# 10. Design On-Call, Severity, and Incident Comms

Burn alerts that email a shared inbox are not an on-call system. The production question is:

> Who is paged, how is **SEV (severity)** declared, and what gets said — so a checkout outage is not informal Slack heroics?

Setup topic **14** (**Lived**), `docs/sre/oncall/*`, `docs/sre/incident-response/severity.md`, and `comms.md` define the human system. Game day 04 would prove the path end-to-end; it is **Deferred**. Topic 14 did validate a test incident when the project was live.

## 1. An unsafe starting state: Slack as the pager

A Cloud Monitoring policy with an email channel, no escalation, no ack SLA, and no severity taxonomy trains people to ignore mail. Catalog labels like “platform-oncall” without a rotation are contacts, not a system. Acknowledging a PagerDuty incident without opening a runbook is theater with a louder bell.

Topic 14 exists because SLO burn is useless if nobody is paged. It completes:

```text
SLI → SLO → burn-rate alert policy → notification channel → PagerDuty → on-call engineer → runbook
```

Without a tested integration, the first real outage is the first time the key is wrong.

## 2. The production model: rotation, SEV, comms, tested channel

> *Theory — On-call as a system*
>
> This model enables a named primary to acknowledge, classify, mitigate from a runbook, communicate, and escalate on a clock — rather than hoping the right person saw a tile.

### PagerDuty service and secret

Topic 14: service `boutique-gke-production`, Events API **V2** (not v1 — Cloud Monitoring requires V2). Integration key stored in Secret Manager `pagerduty-integration-key`, not Git. Screenshot `assets/diagrams/pagerduty-service-events-api-v2.png` is **Inactive** mechanism evidence.

Consumer Gmail may be blocked on PagerDuty trial signup; the guide records using a domain mailbox. That is operational grit, not architecture.

### Severity taxonomy

`docs/sre/incident-response/severity.md`:

| Severity | Definition | Response | Examples |
| --- | --- | --- | --- |
| **SEV1** | Complete outage or data loss risk | Immediate page; war room | Storefront down; checkout 100% failing |
| **SEV2** | Major degradation or error budget exhausted | Page; stakeholder comms | Checkout fast burn; budget at 0% |
| **SEV3** | Partial; workaround exists | Ticket; business hours | Elevated 5xx on one service |
| **SEV4** | Minor; no user impact | Backlog | Dashboard gap; test alert |

Error budget at 0% → **SEV2** minimum per error-budget policy. That linkage prevents “we’re out of budget but still SEV4 because the cluster is Ready.”

### Playbook and escalation

`docs/sre/oncall/playbook.md`: acknowledge within 5 minutes → assess SEV → open runbook → triage user impact with `curl` and checkout test → check Argo/Git changes → mitigate → comms if SEV2+ → resolve → postmortem for SEV1–SEV2.

`docs/sre/oncall/escalation.md`: SEV1 checkout down → secondary + platform lead immediate; SEV2 browse degraded &gt; 15 min → secondary; SEV4 no page escalation.

`docs/sre/incident-response/comms.md` template:

```text
Incident: [title]
Severity: SEV[1-4]
Status: Investigating | Mitigating | Resolved
Impact: [user-facing effect]
Current actions: [what on-call is doing]
Next update: [time UTC]
```

Impact must be user-facing. “Nodes NotReady” is not an impact statement.

**Best Practice:** Shift checklist in `docs/sre/oncall/README.md` — PD app, kubectl, gcloud, open incidents, SLO burn review, handoff notes.

**Production Practice:** `docs/sre/oncall/test-alerts.md` is the channel proof. Game day 04 is the scheduled full routing exercise (**Deferred**). Do not mark routing lived beyond the topic 14 test incident.

## 3. How this repository implements it

> **Practice — Read on-call as files, not folklore**
>
> Open `docs/sre/oncall/README.md`, `playbook.md`, `escalation.md`, `test-alerts.md`.

DNS currently **inactive**: the on-call README already says bookmarks may not resolve. After teardown, on-call for this environment is idle. The documents remain the contract for rebuild.

> **Practice — Trace a test page**
>
> `test-alerts.md`: create a test policy, label `runbook_url` to this file, trigger, confirm push, ack, delete test policy. Screenshot `pagerduty-test-incident.png` is inactive.

Topic 14 also attaches the notification channel to burn and uptime policies (scripts such as `scripts/attach-pagerduty-channel.sh`). Integration key never lands in `terraform.tfvars` committed to Git; topic 19 allows `TF_VAR_pagerduty_service_key` when monitoring IaC is enabled on rebuild.

`docs/sre/README.md` indexes on-call as Phase 7. Phase 9-B adds Argo uptime to the same human path — still apply on rebuild.

Escalation matrix (from `escalation.md`):

| Severity | Condition | Escalate to | Target time |
| --- | --- | --- | --- |
| SEV1 | Checkout down or data loss risk | Secondary + platform lead | Immediate |
| SEV2 | Browse degraded > 15 min | Secondary on-call | 15 min |
| SEV3 | Single service, workaround exists | Notify secondary if unresolved | 30 min |
| SEV4 | Low impact / internal | No page escalation | — |

GD03 user-visible 5xx for seven minutes is at least SEV2 in this table even though it was a scheduled exercise. “We meant to break it” does not change Impact in `comms.md`.

Tooling table in the on-call README: PagerDuty, Cloud Monitoring, Argo CD, kubectl, GitHub. Manual Argo sync only (ADR 003). Error-budget policy gates risky changes during the shift.

## 4. Test the design under failure

### Independent control failure — Ack without runbook, SEV1 without users

> **Practice — Diagnose heroics and over-classification**
>
> Primary acks in 30 seconds, debugs Grafana, never curls the storefront, labels SEV1 because “PagerDuty is loud.”

**Severity:** medium-high; fatigue plus missed user impact.  
**Plausible harm:** real checkout burn competes with dashboard gaps; secondary never joins because everything is SEV1.  
**Potential blast radius:** the rotation itself — people mute the app.  
**Bounded by:** severity table; playbook step 4 user impact; postmortem requirement SEV1–2.  
**Primary principles:** Lived evidence beats scaffold; Git is the deploy authority (runbook URLs in Git).

#### Diagnosis

Severity.md common mistakes: SEV1 without customer impact evidence; skipping postmortem on repeated SEV3s. Playbook common mistake: acknowledging without opening the runbook.

#### Correction

Classify from user journeys. Open the linked runbook. Escalate on the clock. Record timeline in PagerDuty. The 2026-07-04 Redis game day **did not** verify PD — Chapter 14 will not pretend it did.

That correction changes later decisions:

- Chapter 12 runbooks are the work instruction this system opens.
- Chapter 13 freeze at 0% is SEV2, not a chat mood.
- Chapter 14 GD04 remains deferred until a dated report exists.

## 5. Production reality

### Common errors

#### Events API v1 integration

Topic 14: Cloud Monitoring requires V2. v1 looks configured and never pages.

#### Integration key in `terraform.tfvars` committed to Git

Secret Manager (lived) or `TF_VAR_pagerduty_service_key` (topic 19) exist so the key is not in the repo. gitleaks is not a substitute for never adding it.

#### SEV1 for “Grafana is down”

Severity table: SEV1 is complete outage or data-loss risk for users. Grafana is operator triage. Classify from storefront and checkout.

#### Skipping test-alerts.md because “we will find out in game day 04”

Game day 04 is deferred. Topic 14’s test incident was the lived channel proof. After rebuild, re-run the test before chaotic injects.

#### On-call README curl against inactive DNS treated as SEV1

The file already bookmarks inactive names. After teardown, the rotation is idle. Do not page yourself for expected empty `dig`.

## 6. What changed

| Before | After |
| --- | --- |
| Email / Slack as pager. | PagerDuty Events API V2 + Secret Manager key. |
| Everything is SEV1. | SEV1–SEV4 with budget → SEV2 at 0%. |
| No ack clock. | 5-minute ack; escalation matrix. |
| Impact = “pods crashing.” | Comms Impact is user-facing. |

## 7. What You Learned

Topic 14 wires Cloud Monitoring to PagerDuty Events API V2 with the key in Secret Manager. On-call is a playbook, severity taxonomy, escalation matrix, and comms template. Test incident is mechanism evidence. Game day 04 is still not executed. Cluster Ready is not a SEV definition.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Setup 14 | `docs/setup/14-pagerduty.md` | Lived PD integration |
| On-call | `docs/sre/oncall/` | Shift, playbook, escalation, test |
| Severity | `docs/sre/incident-response/severity.md` | SEV1–SEV4 + budget link |
| Comms | `docs/sre/incident-response/comms.md` | Status template |

> **Independent Practice — Classify Redis scale-to-zero using only severity.md**
>
> Storefront returns HTTP 500; Redis replicas 0; BA later blocks restore (facts from GD03).

**Figure 10.1 — Inactive.** TEST alert created a PagerDuty incident on the lived pilot.

![PagerDuty test incident](https://raw.githubusercontent.com/btilki/boutique-gke-sre/main/assets/diagrams/pagerduty-test-incident.png)

Source: `assets/diagrams/pagerduty-test-incident.png`. Game day 03 did **not** re-verify this path.

1. SEV1 or SEV2 during the 5xx window? Quote the table.
2. Does “alert not verified” change severity of user impact?
3. Write a comms Impact line that does not mention Binary Authorization.
4. When would you escalate to platform lead under escalation.md?

Do not use “the exercise was planned” to down-classify user-visible 5xx.
