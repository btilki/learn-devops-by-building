# 13 — Prove Readiness With Checklists and Runbooks

A green Argo **CD (Continuous Delivery)** UI is not production readiness. A README that says “canary works” is not evidence. Topic 13 is **M3 (Milestone 3)**: walk a checklist with pasted proof, then proceed immediately to teardown.

> How do you prove digest → promote → prod manual sync + canary with artifacts an outsider can audit — without claiming enterprise **HA (High Availability)** or a live cluster that no longer exists?

## 1. The unsafe starting state: “it worked on my kubeconfig”

Operators remember a 200 OK and call the program done. Six weeks later nobody knows whether CODEOWNERS was enabled, whether Alertmanager email was proven, or whether prod auto-sync was off. The cluster is still billing.

FR-10 requires operability artifacts. Topic 13 (`docs/setup/13-production-readiness.md`) owns `docs/PRODUCTION_CHECKLIST.md`, the runbook set, and the ROADMAP sign-off. Cost still burns until Topic 14.

**Lived.** Filled 2026-07-19. M3 PASS. AWS is gone; the checklist is the evidence.

## 2. The production model: evidence rows, not vibes

> *Theory — Readiness as auditable evidence*
>
> A production path is proven only when each Must check has a recorded observation (command output, MR SHA, timestamp) and explicit non-goals stay unlabeled as PASS.

The checklist maps to FRs in `docs/architecture/01-requirements.md`. Sections A–D are platform, supply chain, promotion/canary, docs. Section E is one end-to-end pass. Appendix T is teardown (Chapter 14).

## 3. How this repository implements proof

> **Practice — Read the sign-off before the ticks**
>
> Open `docs/PRODUCTION_CHECKLIST.md` from the header through section E. Treat HTTPS 200s as **inactive** historical evidence.

```10:17:docs/PRODUCTION_CHECKLIST.md
**Sign-off**

| Field | Value |
|-------|--------|
| Operator | Birol Tilki (`@btilki`) |
| Date (UTC) | 2026-07-19 |
| M3 result | ✅ **PASS** · ⬜ FAIL |
| Notes | Path proven end-to-end. Stage realigned via !13 (`365c59d`); stage=prod `563ebf12…`; canary Healthy; HTTPS 200. C6=!12. Ignore red CI on digest MRs. |
```

**Lived.** “Ignore red CI on digest MRs” is an honesty note, not a pass for broken pipelines. Post-teardown red CI is a different story (dormant rules, Chapter 10).

### Sections A–E (sampled)

| Area | Example Must | Evidence style |
|------|----------------|----------------|
| A foundation | EKS 1.31 Ready; prod sync manual | node version; `frontend-prod` automated empty |
| B workloads | 7 services + Redis `@sha256:`; CI no cluster API | pod images; `.gitlab-ci.yml` guards |
| C promote/canary | CODEOWNERS; stage+prod canary; revert | MR SHAs `d1a4ad3`, `108f0bf`, `!12` |
| D artifacts | ADRs 0001–0006; five runbooks | paths exist |
| E path | E1–E6 one pass | digest MR → dev → stage canary → prod manual → revert |

**Lived.** ADRs 0007–0010 are not required for M3; they are Phase 12 **scaffold**.

### Runbooks (symptom playbooks)

`docs/runbooks/README.md` indexes alerting, ingress, argo-sync, kyverno, canary, teardown. Topic 13 requires them *usable*, not merely present. You already walked alerting (Chapter 8) and canary (Chapter 12). Ingress and Argo-sync are the shop-down and OutOfSync paths. Kyverno is the deny-storm path.

### Operations handbook 01–20

`docs/operations/README.md` is day-2. Bootstrap remains `docs/setup/`. On-call quick links send shop-down to `17-common-incidents.md` and `runbooks/ingress.md`.

```10:23:docs/operations/README.md
## On-call quick links

| Situation | Runbook | First command |
|-----------|---------|---------------|
| Shop / HTTPS down | [17](17-common-incidents.md) · [ingress](../runbooks/ingress.md) | `curl -sI -o /dev/null -w '%{http_code}\n' https://boutique.biroltilki.art` |
| Bad digest / failed promote | [03](03-rollback.md) · [rollback](../rollback.md) | `git log --oneline -- gitops/envs/prod/values \| head` |
| Failed / stuck deploy | [02](02-deployment.md) · [argo-sync](../runbooks/argo-sync.md) | `kubectl -n argocd get app \| grep -E 'prod\|stage\|frontend'` |
| Canary stuck / abort | [canary](../runbooks/canary.md) | `kubectl -n prod get rollout frontend -o wide` |
| Kyverno deny | [kyverno](../runbooks/kyverno.md) | `kubectl get clusterpolicy` |
| No alert email | [alerting](../runbooks/alerting.md) | `kubectl -n monitoring get secret alertmanager-smtp` |
| End pilot / stop cost | [teardown](../runbooks/teardown.md) | Follow Topic 14 **immediately** |
```

**Lived** as authored procedures. Escalation is solo: L1–L3 are the same person (`docs/operations/01-overview.md`). **SLO (Service Level Objective)** is best-effort; **RTO (Recovery Time Objective)** is hours (`docs/operations/05-disaster-recovery.md` — rebuild from Git + Terraform, no multi-region).

Sample the rest of the handbook by purpose, not by rereading every page in this chapter:

| Doc | Role |
|-----|------|
| `01-overview.md` | Operational model, env table, honest SLOs |
| `02-deployment.md` / `03-rollback.md` | Day-2 restatement of Topics 11–12 |
| `04-scaling.md` | ASG 2–5; do not scale by console-only |
| `05-disaster-recovery.md` / `06-backup-and-restore.md` | Rebuild vs ephemeral Redis |
| `07-incident-response.md` / `17-common-incidents.md` / `19-postmortem-checklist.md` | SEV, CrashLoop playbook, write-up |
| `08-health-checks.md` / `09-monitoring.md` / `10-alerting.md` / `11-logging.md` | Signal ownership; placeholder shop alert |
| `12-maintenance.md` / `13-upgrades.md` / `14-certificate-rotation.md` / `15-secret-rotation.md` | Planned change via Git |
| `16-troubleshooting.md` / `18-recovery-procedures.md` | Ordered debug; restore from Git |
| `20-automation-opportunities.md` | What not to automate (CI deploy) |

Topic 13 Step 13.1’s evidence collectors are the commands the operator actually ran (nodes, applications, clusterpolicies, monitoring pods, three storefront curls, grep for `:latest`). After teardown those commands fail against a missing cluster; the pasted outputs in the checklist remain the M3 record. Do not re-tick the boxes from memory on a rebuild.

`docs/operations/07-incident-response.md` is the SEV path; `17-common-incidents.md` Playbook A (CrashLoop) sends you to rollback or the Kyverno runbook, not to `terraform destroy` unless SEV-1 unrecoverable. `19-postmortem-checklist.md` is how M3-style evidence becomes a write-up. `18-recovery-procedures.md` repeats Git revert and Terraform rebuild. `06-backup-and-restore.md` is honest about Redis: ephemeral carts, no customer DB.

`docs/runbooks/ingress.md`, `argo-sync.md`, and `kyverno.md` are the three symptom books not fully quoted earlier. Ingress: ACM/ALB/target health. Argo-sync: OutOfSync vs Unhealthy vs missing auto-sync on prod (prod *should* be missing auto-sync). Kyverno: policy reports and the deny-latest fixture.

> **Practice — Pick one incident playbook and one ops chapter**
>
> Open `docs/operations/17-common-incidents.md` Playbook A and `docs/operations/05-disaster-recovery.md` Step 1. State when teardown is the correct DR move (pilot over) versus rebuild.

## 4. Test the design under failure

**Scenario:** Checklist ticked green without MR URLs; prod auto-sync actually on.

**Severity:** false M3; unattended prod applies.  
**Plausible harm:** auditors (or future you) believe CODEOWNERS and manual sync; the next digest merge ships immediately.  
**Potential blast radius:** all `*-prod` apps.  
**Bounded by:** checklist Evidence column, A7 explicit empty automated policy, Topic 13 “do not mark PASS without evidence.”  
**Primary principles:** Git is the only deploy authority; scaffold in Git is not lived proof; teardown after the pilot is required.

### Diagnosis

Empty Evidence cells with ticked Done. `frontend-prod` YAML shows automated sync. ROADMAP Phase 10 ✅ anyway.

### Recovery

Untick. Capture real `kubectl`/`argocd` output and MR SHAs. Fix ApplicationSet if auto-sync leaked. Do not proceed to marketing. Proceed to Topic 14 only after a real PASS or an explicit abort of the pilot.

Incident classification lives in `docs/operations/07-incident-response.md`: email-based, no PagerDuty, SEV table, do not use the incident doc for planned promotes. `docs/runbooks/ingress.md` orders triage: curl, dig, Ingress ADDRESS, ACM listener, target health, pods, LB controller, external-dns logs. `docs/runbooks/kyverno.md` lists the five ClusterPolicies and labels verify-* as Topic 15 Audit. After teardown, those commands are rebuild procedures; the 2026-07-19 checklist rows are the proof this pilot already ran them.

## 5. What You Learned

M3 is a filled checklist plus usable runbooks and an operations handbook, with DNS evidence now inactive. You can now walk Topic 13, `PRODUCTION_CHECKLIST.md`, `docs/runbooks/*`, and sampled `docs/operations/01`–`20`.

### Durable outputs

- Checklist: `docs/PRODUCTION_CHECKLIST.md`
- Setup: `docs/setup/13-production-readiness.md`
- Runbooks: `docs/runbooks/`
- Handbook: `docs/operations/`

> **Independent Practice — Write tomorrow’s M3 row**
>
> On a rebuild, you will not have SHAs `108f0bf` or `!12`. Draft the empty Evidence column for C1–C6 as “what I must paste,” including how you prove prod automated is still absent. Do not copy 2026-07-19 numbers as if they were live.

### Operations 01–20 as a set

You do not need to memorize twenty files. You need to know they exist and that none of them authorizes **CI (Continuous Integration)** deploy:

- Change path: `02-deployment.md`, `03-rollback.md`, `04-scaling.md`, `12-maintenance.md`, `13-upgrades.md`
- Identity/secrets/certs: `14-certificate-rotation.md`, `15-secret-rotation.md`
- Signals: `08-health-checks.md`, `09-monitoring.md`, `10-alerting.md`, `11-logging.md`
- Failure: `07-incident-response.md`, `16-troubleshooting.md`, `17-common-incidents.md`, `18-recovery-procedures.md`, `19-postmortem-checklist.md`
- Limits: `01-overview.md` (best-effort SLO), `05-disaster-recovery.md` (hours, not multi-region), `06-backup-and-restore.md` (Redis ephemeral), `20-automation-opportunities.md` (do not automate cluster apply)

That is FR-10’s handbook. Topic 13’s job was to prove it is linked and usable, then stop the bill.

Section E of the checklist is the required path proof: CI digest MR to `gitops/envs/dev/**` (E1), Argo syncs dev (E2), promote to stage with canary (E3), promote to prod with `@btilki` and **manual** sync (E4), prod canary to stable and HTTPS 200 (E5), optional revert (E6 — **!12**). Path owner Birol Tilki, 2026-07-19. **Inactive** hosts now; the SHAs remain.

Runbook files Topic 13 requires present: `alerting.md`, `ingress.md`, `argo-sync.md`, `kyverno.md`, `canary.md`, plus teardown stub then filled in Topic 14.

Checklist section D required architecture Accepted, ADRs 0001–0006, those runbooks, promotion/rollback linked from README, versions matching live, and the checklist itself filled. Section F records teardown as FR-11 (done in Appendix T) and restates out-of-scope CloudWatch/PagerDuty/OTel and mesh. Topic 13 Setup says proceed **immediately** to Topic 14 — no keep-alive after PASS.

`docs/operations/04-scaling.md` and `08-health-checks.md` complete the handbook sample: scale via Git/ASG, not console-only; health is curl plus Argo plus Prometheus, not a vendor SLO.

Topic 13 is FR-10. M3 PASS is dated 2026-07-19 with operator `@btilki`. The notes say ignore red CI on digest MRs from that day — a different problem from post-M4 dormant pipelines. Do not conflate them.

## Next

Chapter 14 tears the platform down as a production control, not as leftover hygiene.
