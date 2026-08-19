# 1. Define the Reliability Platform, Not a Green Cluster

A private **GKE (Google Kubernetes Engine)** cluster can be Ready, Argo CD can show Synced, and `boutique.biroltilki.art` can return 200, while checkout still has no owner, no **SLO (Service Level Objective)**, and no freeze when remaining budget is gone. The production question of this chapter is:

> What is this repository for, what does it refuse to count as reliability success, and who owns the journeys?

Without that answer, later chapters optimize graphs. `PROJECT.md` already names the bar. This chapter makes it the reliability contract.

## 1. An unsafe reliability definition

The repository opens with a decommissioned platform, not a green demo:

```text
Infrastructure: Decommissioned 2026-07-04. Documentation and screenshots remain;
public DNS names are inactive (no A records until rebuild).
```

That sentence in `README.md` is operational honesty. The unsafe definition is the opposite: treat “cluster exists” as the program.

`PROJECT.md` scopes a **single GCP (Google Cloud Platform)** project, one cluster, and a production bar that includes HTTPS (when live), Kyverno, digest-only images, SLOs with burn alerts and runbook links, and a game day that actually ran. Out of scope: multi-project isolation, multi-region active-active, a service mesh default, custom app code, and a status-page product.

The unsafe reading of that charter is: “we built GKE, therefore we have SRE.” A regional private cluster is a runtime. Reliability is whether browse and checkout journeys hold under loss.

`docs/bootstrap.md` walks empty project to production-style URLs. It also states the gate:

> Do not skip topics 09–11 (Argo CD, ESO, Kyverno) before treating the cluster as production-ready.

That gate is necessary and still insufficient. Passing Phase 4 means Boutique must not land on an ungoverned cluster. It does not mean SLOs already protect users. Topic 12 deploys the shop. Topic 13 attaches availability SLOs. Topics 17–20 remain **repo-ready / apply on rebuild**.

`ROADMAP.md` records Phases 1–8 complete and infrastructure torn down. Phases 9-A–9-D are “Repo ready (apply on rebuild).” Calling those phases lived would be availability theater in a different costume.

## 2. The production model: journeys, refusals, and a lived bar

> *Theory — User-journey reliability model*
>
> This model enables the platform to select reliability work from browse and checkout outcomes rather than from cluster Ready, portal uptime, or whoever owns the loudest dashboard.

### A journey is a user-visible outcome that can fail

Online Boutique’s customer path is browse then checkout. Architecture overview §13 and `docs/sre/slos/catalog.md` name those two services:

| Journey | What failure looks like | Later proof |
| --- | --- | --- |
| Browse | Home, product, or cart view does not succeed | Browse availability 99.9% and p95 &lt; 500ms |
| Checkout | Place order via `checkoutservice` does not succeed | Checkout availability 99.95% and p95 &lt; 1000ms |

A journey is not “the `frontend` Deployment.” It is not “Kubernetes.” Naming a component without a failed user outcome produces theater.

### A refusal is a measurement that must not count as success

This book’s first refusals are structural:

- cluster, kubelet, and API Ready must not count as reliability success;
- Argo CD UI uptime is an operability signal (topic 18, apply on rebuild), not a user-journey SLO;
- time-to-first-environment and other platform job proofs are not this program’s error budget;
- reconstructing the cluster from Terraform is recovery of a runtime, not proof that checkout held.

**Best Practice:** Write refusals next to the production bar, not in a slide appendix.

**Production Practice:** A refusal is only real when a later SLI candidate for that measurement is rejected or kept adjacent. Chapter 9 pages on burn of browse and checkout, not on every Ready probe.

### A promise is what the program commits to protect

From `PROJECT.md` and the architecture non-functionals:

> Browse and checkout keep user-visible SLOs; exhausted error budget can freeze change; component uptime is not success.

The promise is not “we will run SRE.” That sentence names a category.

## 3. How this repository implements the contract

> **Practice — Read the charter before the dashboards**
>
> Open the four files that define what this platform is allowed to claim.

Open `README.md`, `PROJECT.md`, `ROADMAP.md`, and `docs/bootstrap.md`.

`README.md` states the lens: reliability after deploy — observability, PagerDuty, incident paths — on a private GKE cluster. GitOps and supply-chain controls are included; they are not the reliability question.

`PROJECT.md` production bar (abridged):

```text
- HTTPS on boutique.biroltilki.art and argocd.boutique.biroltilki.art (when live)
- Kyverno enforced; digest-only images; ESO-only secrets
- SLOs + burn alerts with runbook links; PagerDuty test incident validated
- Latency SLO artifacts + Grafana dashboards in repo (topic 17 — apply on rebuild)
- HA GitOps, Argo uptime, game-day STATUS/TEMPLATE, GD03 postmortem (topic 18)
- Terraform monitoring + GKE Backup modules (topic 19 — enable_*_iac on rebuild)
- Error-budget ritual, capacity baseline, toil cadence (topic 20)
- Game-day scenario executed (2026-07-04); infrastructure decommissioned 2026-07-04
```

Notice the honesty labels already in the charter. Topic 17 is not claimed as lived SLO latency in Cloud Monitoring after teardown. Topic 18 does not claim game days 01, 02, and 04 ran. Topic 19 flags default off.

`ROADMAP.md` maps setup topics to phases. Topics **01–16** are the original bootstrap. Topics **17–20** are Phase 9 expansions. The dependency graph forbids treating Boutique as production-ready before Phase 4.

`docs/bootstrap.md` is the executive path, not a second architecture. It lists stages, points at `docs/setup/README.md`, and warns against applying Boutique before Kyverno, **ESO (External Secrets Operator)**, and NetworkPolicy.

> **Practice — Separate mechanism from journey success**
>
> After bootstrap, smoke validation (`docs/setup/16-smoke-validation.md`) proves HTTPS, GitOps, policy, and a test page. That is mechanism evidence. Journey success is the SLO catalog in Chapter 9.

The production bar requires a PagerDuty test incident. That proves the channel. It does not prove browse availability held for a month.

### Evidence this chapter can claim

| Evidence category | What exists |
| --- | --- |
| Mechanism | README, charter, roadmap, bootstrap path, setup 01–20 index |
| Decision | Single project, single cluster, SRE lens, Phase 4 gate, Phase 9 labeled apply-on-rebuild |
| Outcome | Not yet: SLOs are later chapters; DNS is inactive |
| Recovery | Teardown on 2026-07-04 is recorded; journey recovery is Chapter 14–15 |

## 4. Test the design under failure

### Independent control failure — Cluster Ready counted as success

> **Practice — Diagnose uptime theater**
>
> Replace Ready-as-success with owned browse and checkout proofs.

Imagine a weekly report that says: nodes Ready, Argo Synced, Grafana up, therefore reliability is green. `docs/sre/slos/catalog.md` would still be unread. Checkout could 5xx while the control plane looks healthy — exactly what game day 03 later showed when Redis scaled to zero and the storefront returned HTTP 500.

**Severity:** high; every later SLO, alert, and freeze conversation will optimize graphs instead of journeys.  
**Plausible harm:** customers cannot browse or check out while leadership cites a green cluster.  
**Potential blast radius:** every service asked to “be reliable”; platform namespaces (`argocd`, `kyverno`, `observability`) get treated as user journeys.  
**Bounded by:** SLO catalog, burn-rate pages, error-budget policy, game-day STATUS. None repairs a program that counts Ready as success.  
**Primary principles:** Lived evidence beats scaffold; Namespaces on one cluster are not multi-account isolation.

#### Diagnosis

Calling the program “keep the cluster green” encourages graph controls: scrape kubelet, count Ready replicas, publish an Argo tile. Those reduce orientation noise. They do not answer which user fails, who owns remaining budget, or what dated report would falsify success.

The missing refusals make every green tile in-scope. The missing journey names leave Chapter 9 nothing honest to page on.

#### Correction

The completed model does not elevate Ready into the program. It uses `PROJECT.md` as the bar, `ROADMAP.md` as the honesty calendar, and browse/checkout as the only user-facing success evidence later chapters may target.

That correction changes later decisions:

- Chapter 2 must record blast radius of one cluster, not pretend namespaces are accounts.
- Chapter 6 must pass the Phase 4 gate before Boutique exists — still without calling the gate an SLO.
- Chapter 9 must page on burn of browse and checkout.
- Chapter 14 must refuse to mark game days 01, 02, and 04 executed.

## 5. Production reality

### Common errors

#### Naming the dashboard as the program

If Grafana disappeared, browse and checkout should still be nameable from `docs/sre/slos/catalog.md`. If they are not, there was no reliability program.

#### Treating topic 16 smoke as monthly reliability

Smoke validation proves HTTPS, digest-only images, five Kyverno policies, and a test page. `PROJECT.md` requires that bar. It is a bootstrap gate. It is not 30 days of 99.9% browse.

#### Calling Phase 9 complete because ROADMAP shows checkmarks

ROADMAP checkmarks for 9-A–9-D say “Repo ready (apply on rebuild).” That is the opposite of “lived on the current cluster.” The current cluster does not exist.

#### Using Argo CD UI uptime as the shop SLO

Operators cannot sync when Argo is down. Shoppers do not use `argocd.boutique.biroltilki.art`. Keep the check adjacent.

## 6. What changed

| Before | After |
| --- | --- |
| Success was cluster Ready. | Success is browse and checkout journeys named in the catalog. |
| Phase 9 looked “done” in Git. | Phase 9 is labeled apply-on-rebuild. |
| DNS URLs looked like a live demo. | DNS is inactive; teardown is in the charter. |
| Bootstrap was the whole SRE story. | Bootstrap is the runtime; SLOs come later. |

## 7. What You Learned

A reliability platform is defined by protected journeys, a production bar that can freeze change, explicit refusals, and honest phase labels. GKE Ready is a runtime signal. DNS inactivity after teardown is part of the contract, not an embarrassment to hide. Schema-complete YAML for Phase 9 is scaffold until rebuild.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Charter | `PROJECT.md` | Production bar, scope, DNS inactive, Phase 4 session rule |
| Honesty calendar | `ROADMAP.md` | Lived 1–8 vs apply-on-rebuild 9-A–9-D |
| Bootstrap path | `docs/bootstrap.md` | Ordered topics; gate before Boutique |
| Reader entry | `README.md` | Decommissioned state; SRE lens |

> **Independent Practice — Refuse Argo CD uptime as the portfolio SLO**
>
> Topic 18 adds `observability/monitoring/uptime-checks/argocd-ui.yaml`. Decide whether that check is a user journey, an adjacent operability signal, or a refusal-as-success trap.

Work from Git only:

1. Name the failed user outcome if Argo CD is down. Who is harmed — a shopper or an operator?
2. If you keep the check, say why it must not replace browse/checkout SLOs.
3. Identify one observation that would falsify “Argo uptime means the shop is reliable.”
4. State which material change would trigger review (second cluster, public status page, or a real multi-team on-call).

Do not copy the browse catalog row and rename it `argocd`. Operator UI availability has different freeze consequences.

You can demonstrate this chapter when you can explain why cluster Ready is not a finished journey, trace the production bar to `PROJECT.md`, distinguish lived Phases 1–8 from Phase 9 apply-on-rebuild, and refuse DNS screenshots as proof the edge is live.
