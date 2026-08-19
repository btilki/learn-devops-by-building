# 13. Govern Error Budget, Capacity, and Toil

Pages and runbooks still cannot stop a digest PR if remaining budget is a screenshot. The production question is:

> When remaining error budget is healthy, cautious, or exhausted, what change is authorized — and what cadence keeps capacity and orphans from becoming silent toil?

Setup topic **20** is **repo-ready** (cadence anytime; richer when live). `docs/sre/error-budget-policy.md`, `docs/sre/error-budget/*`, `docs/sre/capacity/baseline.md`, and `docs/operations/orphan-scan-cadence.md` are the ritual. They did not freeze a live fleet after teardown. Practice them from Git.

## 1. An unsafe starting state: calendar deploys, infinite HPA experiments

Releases ship because it is Tuesday. Node pool max is raised during a checkout burn “to help.” Orphan global IPs accumulate because nobody owns the scan. Freeze is declared in chat and forgotten. Topic 20’s why: policies without rituals drift.

## 2. The production model: bands, freeze log, capacity when-to-scale, report-only orphans

> *Theory — Error-budget policy as change control*
>
> This model enables remaining unreliability to continue, slow, or freeze GitOps promotions and risky infra — rather than a calendar, a ticket, or “the cluster looks fine.”

### Bands

`docs/sre/error-budget-policy.md`:

| Remaining budget | Engineering response |
| --- | --- |
| **&gt; 50%** | Normal velocity — PR + manual Argo sync |
| **25–50%** | Cautious — reduce risky changes; extra infra reviewer |
| **&lt; 25%** | **Freeze** non-critical deploys; reliability work prioritized |
| **0%** | **SEV2** — halt feature releases; reliability sprint |

On-call declares the band during incidents. Platform lead approves freeze exceptions. Emergency security patches may bypass with documented exception. Resume only after budget recovers above 25% with lead sign-off.

Weekly ritual: fill `docs/sre/error-budget/weekly-review.md` (including “N/A — cluster down” while offline). If &lt; 25%, open `.github/ISSUE_TEMPLATE/error_budget_freeze.md` and append `docs/sre/error-budget/freeze-log.md` (append-only; exit is a new row).

**Best Practice:** Bind freeze to named SLOs (browse/checkout availability and latency), not to “the platform.”

**Production Practice:** 99.9% browse ≈ 43.2 min/month; 99.95% checkout ≈ 21.6 min. Freeze reduces change risk; it does not auto-remediate — runbooks still required.

### Capacity is not a freeze substitute

`docs/sre/capacity/baseline.md`: frontend and checkout HPA 2–6 at 70% CPU; cartservice 2; **redis-cart replicas 1** (do not split cart state); PDBs `minAvailable: 1` on critical paths; node pool `e2-standard-4` autoscaling 1–3 **per zone**.

When error budget &lt; 25%, **do not** expand risky capacity experiments — freeze log instead. When HPA is at max and latency burns, then GitOps/Terraform scale. `scripts/load/smoke-browse.sh` is a stub, not a soak test.

HPA/PDB templates exist in Git (`gitops/apps/boutique/templates/hpa.yaml`, `pdb.yaml`). Topic 18 must sync them on rebuild before game day 02 is credible.

### Orphan scan is reliability toil

`docs/operations/orphan-scan-cadence.md`: weekly if live; pre-destroy; post-destroy +24h; after failed apply. `scripts/teardown/orphan-resource-scan.sh` is **report only** — never pipe to delete. Cost spikes belong in the weekly review if they correlate with leftovers.

## 3. How this repository implements it

> **Practice — Walk the freeze path in Git**
>
> Open policy, weekly-review, freeze-log, and the GitHub issue template.

Freeze issue captures worst SLO, remaining %, window, on-call, exit criteria. Freeze-log example row uses Freeze ID `EB-YYYYMMDD-N`. Chat without those two artifacts is not a freeze.

> **Practice — Read capacity “when not to scale”**
>
> Do not scale to “fix” burn without a hypothesis. Do not scale Redis replicas. Do not scale during freeze without lead exception.

Topic 20 commands: `kubectl get hpa,pdb,deploy -n boutique` when live; `make runbook-lint` always; `./scripts/teardown/orphan-resource-scan.sh` with `PROJECT_ID=boutique-gke`. ROADMAP optional follow-ups (Slack budget bot, scheduled orphan GHA) are **not** implemented — checklist + local scan exist today.

`docs/sre/error-budget/README.md` indexes the living artifacts and points at topic 20.

Checkout HPA excerpt from `gitops/apps/boutique/values.yaml` (apply on rebuild with topic 18):

```yaml
  checkoutservice:
    replicas: 2
    autoscaling:
      enabled: true
      minReplicas: 2
      maxReplicas: 6
      targetCPUUtilizationPercentage: 70
    pdb:
      enabled: true
      minAvailable: 1
```

`hpa.yaml` / `pdb.yaml` templates range over `.Values.services` and emit objects only when enabled. Redis has a separate PDB block and must stay at one replica. Weekly review table includes all four SLOs (browse/checkout × availability/latency) even when latency objects are not live — fill N/A rather than copying availability %.

Comms when entering freeze (from the policy):

```text
Subject: [boutique-gke] Error budget — freeze
Browse/checkout SLO budget at <X>% remaining (<30d window).
Action: freeze per error-budget-policy.md
```

That template is useless without the freeze-log row.

## 4. Test the design under failure

### Cumulative reliability failure — Budget exhausted, digest PR still synced

> **Practice — Diagnose calendar promotion under zero checkout budget**
>
> Remaining checkout availability 0%. A frontend cosmetic digest merges and is manually synced because “it is not checkout.” Frontend 5xx from a bad pin still burns browse and may take checkout with it.

**Severity:** high; policy is ornamental.  
**Plausible harm:** reliability sprint never starts; GD03-style injects continue during freeze.  
**Potential blast radius:** all Boutique images in the same values file; shared cluster.  
**Bounded by:** freeze issue + log; ADR 003 still requires a human — that human must refuse the sync.  
**Primary principles:** Git is the deploy authority; Lived evidence beats scaffold; Teardown is a production control (orphans steal budget via cost/toil).

#### Diagnosis

Manual sync is not a freeze. It is a gate that can still say yes. Policy without issue + log + lead is a mood. Common mistake in the policy doc: ignoring budget because the environment is “non-production” — this repository practices prod discipline on a reference cluster.

#### Correction

Declare freeze, open the issue, append the log, stop non-reliability syncs, page SEV2 at 0%. Capacity changes via PR aligned with baseline. Orphans scanned, not auto-deleted.

That correction changes later decisions:

- Chapter 14 must not run extra game days during freeze without lead approval.
- Chapter 15 teardown still runs orphan scan even when budget is N/A offline.
- Sister GitOps book’s promotion mechanics still obey this freeze when the cluster is rebuilt.

## 5. Production reality

### Common errors

#### Freeze in chat without freeze-log + issue

Policy common mistake. Without `EB-YYYYMMDD-N` and a GitHub issue, the freeze has no exit criteria and no audit.

#### Scaling `redis-cart` to 2 under latency burn

Capacity baseline: ClusterIP would split cart state. Use restore/runbook, not replica count.

#### Load tests during freeze without lead approval

`scripts/load/smoke-browse.sh` is a curl stub. Even that belongs in an agreed window. Game days during freeze need the same approval.

#### Filling weekly-review remaining % with invented numbers while torn down

Topic 20 allows “N/A — cluster down.” Invented 87% remaining is a false SLO.

#### Auto-deleting orphan scan output

Cadence is report-only. A scripted delete will remove a static IP Terraform still expects and break the next apply.

## 6. What changed

| Before | After |
| --- | --- |
| Ship on Tuesday. | Bands from remaining budget. |
| Freeze is a feeling. | Issue template + append-only log. |
| Scale everything when red. | When-to-scale table; freeze forbids risky experiments. |
| Leftover IPs as “GCP being messy.” | Weekly/pre/post orphan scan. |

## 7. What You Learned

Error-budget policy maps remaining unreliability to continue / cautious / freeze / SEV2. Rituals (weekly review, freeze log, issue template) make it real. Capacity baseline says when to scale and when not to. Orphan scan is scheduled toil with no auto-delete. Topic 20 is practice-from-Git until rebuild makes percentages live. Cluster Ready never selects a band.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Policy | `docs/sre/error-budget-policy.md` | Bands and comms |
| Ritual | `docs/sre/error-budget/` | Weekly review + freeze log |
| Issue | `.github/ISSUE_TEMPLATE/error_budget_freeze.md` | Tracked freeze |
| Capacity | `docs/sre/capacity/baseline.md` | HPA/PDB/node defaults |
| Orphans | `docs/operations/orphan-scan-cadence.md` | Cadence |
| Setup 20 | `docs/setup/20-sre-practices-capacity-toil.md` | How to run the rhythm |

> **Independent Practice — Fill a weekly review while the project is torn down**
>
> Topic 20 allows “N/A — cluster down.”

1. What is the strictest band you can honestly declare?
2. Which look-ahead changes are still risky in Git (BA, Kyverno, digest flood) even offline?
3. Should you freeze digest PRs to `main` while down? Why or why not?
4. What evidence would reopen freeze after rebuild (first week of SLI data)?

Do not invent remaining percentages to make the table look used.
