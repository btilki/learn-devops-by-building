# 16. Conclusion — Reliability Is Behavior Under Loss

This repository is a private regional **GKE (Google Kubernetes Engine)** platform for Online Boutique. Reliability was never “the cluster came up.” It was whether browse and checkout journeys held, whether remaining error budget could freeze change, whether a page opened a runbook, and whether a game day wrote what actually happened.

On **2026-07-04** those questions met Redis. Scaling `redis-cart` to zero produced storefront HTTP 500 — user-visible loss. Restore was not a `kubectl scale` fairy tale: **BA (Binary Authorization)** denied the recreate until a time-boxed DRYRUN. PagerDuty was not verified. The cluster was then torn down. DNS names went **inactive**. Git kept the evidence. That is an honest SRE ending.

## What the chapters established

Chapters 1–2 refused Ready-as-success and recorded one-cluster blast radius in ADRs 001–003. Chapters 3–4 built private foundation and a recoverable HTTPS edge that teardown must leave **inactive**. Chapters 5–7 federated CI, pinned digests, passed the Phase 4 gate, and promoted Boutique by manual sync. Chapters 8–10 made journeys observable, paged on burn, and put a human on PagerDuty with SEV and comms. Chapters 11–13 hardened Armor/BA, treated runbooks as a linted product, and mapped remaining budget to freeze. Chapters 14–15 wrote the only executed game day honestly and made teardown-with-orphan-scan part of the contract.

Latency SLOs, Grafana JSON, HPA/PDB HA claims, Argo uptime, monitoring/backup Terraform flags, and the weekly budget ritual are **repo-ready**. They apply on rebuild. They are not lived after 2026-07-04.

## What this title uniquely owns

Sister books in the Boutique Production Series share digest identity, Git as deploy authority, and Online Boutique. They do not share this reliability contract.

*Practical GitOps on Amazon EKS* (`boutique-eks-gitops`) owns pull reconciliation and promotion mechanics on Amazon as the primary question. This book **consumes** **GitOps (Git-based operations)**: ADR 003 manual Argo CD sync is promotion discipline here, not the thesis.

*Practical DevSecOps on Azure Kubernetes Service* (`boutique-aks-devsecops`) owns threat boundaries and Azure control mapping as the primary question. This book **consumes** supply-chain controls: **WIF (Workload Identity Federation)**, cosign, Kyverno, Armor, BA. It cares when those controls extend an outage (unsigned Redis) or bound one (CRS at the edge).

What SRE uniquely owns on `boutique-gke-sre`:

- User-journey **SLOs (Service Level Objectives)** on browse (99.9%, p95 &lt; 500ms) and checkout (99.95%, p95 &lt; 1000ms), not cluster Ready or Argo UI uptime.
- Multi-window burn pages with runbook URLs, not symptom paging as the program.
- Error-budget bands that can freeze digest syncs and risky infra, with weekly review and append-only freeze log.
- On-call as PagerDuty + SEV1–SEV4 + comms, not Slack as the pager.
- Game-day STATUS that refuses execution without a dated report — and one lived report that kept its gaps.
- Teardown with orphan scan as part of the reliability contract.

Setup topics **01–16** lived. Setup **17–20** are Phase 9-A–9-D: apply on rebuild (topic 20 cadence can be practiced offline). Game days **01, 02, 04** remain Deferred. Only **GD03** has `reports/2026-07-04-redis-cart-down.md` plus a postmortem.

Phases **9-A–9-D** (setup **17–20**) remain **repo-ready / apply on rebuild**: latency SLOs and Grafana JSON, HA HPA/PDB plus Argo uptime and deferred game days, Terraform monitoring/backup flags, and the error-budget/capacity/toil cadence. Do not upgrade that YAML into lived proof.

## How to judge the work after the last chapter

Ask the same four questions the How to Use chapter started with:

1. Which browse or checkout journey is at risk?
2. What error budget remains, and what change does it freeze?
3. Who is on-call with a runbook, not a hero narrative?
4. What dated report would prove the failure was exercised — and what did 2026-07-04 already refuse to claim?

A rebuilt cluster that is Ready is a foundation. Evidence of reliability is still a user journey under loss, a freeze that can say no, and STATUS that can say Deferred.

## What not to take away

- Do not treat `assets/diagrams/*.png` as a live portal.
- Do not treat Argo CD Synced/Healthy as checkout success.
- Do not treat topic 16 smoke as a monthly SLO.
- Do not treat Phase 9 YAML as executed game days 01, 02, or 04.
- Do not treat temporary BA DRYRUN as a standing configuration.
- Do not treat this book as a license to rebuild without reading `docs/teardown.md` first — rebuilds cost money.

Sister GitOps work still applies here: Git is the deploy authority. Sister DevSecOps work still applies: identity and admission are real. SRE’s extra obligation is to say what failed for a user, what budget remains, who was paged, and what the dated report actually contains.

The Northwind SRE title taught the same vocabulary on a companion lab. This title applies it to `boutique-gke-sre` without that lab. Do not merge the two manuscripts. Do not pretend this cluster is still running.

## Rebuild, if you choose it

Optional, costly, and not required to finish this book. If you rebuild:

1. Topics 01–16 in order; do not skip the Phase 4 gate.
2. Sign and attest `redis-cart` before BA enforce and before the next GD03.
3. Apply topics 17–20 as labeled — latency SLOs, HA sync, monitoring/backup flags, weekly ritual.
4. Run game day 04 before chaotic injects; write dated reports; leave STATUS Deferred until then.
5. Tear down with orphan scan when the learning window ends.

The unique SRE residue is not a running cluster. It is a catalog of journeys, a freeze that can say no, runbooks CI can lint, and a 2026-07-04 report that kept its gaps.

Setup **01–20** are all in this book: foundation (01–04), edge (05–06), identity (07–08), Phase 4 gate (09–11), Boutique (12), observability and SLOs (13, 17), PagerDuty (14), Armor and smoke (15–16), game-day operability (18), backup IaC (19), budget/capacity/toil (20). Lived versus apply-on-rebuild is the only honest split.

Public evidence remains at https://github.com/btilki/boutique-gke-sre. DNS names `boutique.biroltilki.art` and `argocd.boutique.biroltilki.art` stay inactive until someone pays to rebuild.

BOOK-PLAN.md in this directory is the planning artifact. It was not rewritten as a chapter.

## Next

Read the sister titles if you need GitOps or DevSecOps depth. Stay in this repository if you need to govern SLOs, burn, freeze, on-call, and honest game days on GKE. When you rebuild, apply 17–20, sign `redis-cart`, and write a new report. Do not edit 2026-07-04 into a cleaner story than it was.

Reliability is behavior under loss. This platform lost Redis for seven minutes, lost restore to BA for six of them, lost PagerDuty verification entirely, then lost the cluster on purpose. The book’s job was to keep those facts in Git and refuse to call Ready a success.

Rehearse that story with [17-interview-questions-from-this-repository.md](17-interview-questions-from-this-repository.md). Ten questions; answers cite these files. Do not upgrade game days 01, 02, or 04 into executed reports.
