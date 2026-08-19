# How to Use This Book

## Who this book is for

This book is for intermediate-to-advanced platform, cloud, and **SRE (Site Reliability Engineering)** practitioners who already know Linux, Git, containers, **CI (Continuous Integration)**, Kubernetes, and infrastructure as code, and who need to govern reliability of a real storefront on **GKE (Google Kubernetes Engine)**.

You should already be comfortable reading Terraform, Helm, and GitHub Actions; interpreting a private cluster; and following an alert to a runbook. The book does not teach those subjects from first principles. It uses them as the surface on which reliability decisions must operate.

You do not need a live **GCP (Google Cloud Platform)** project to read this book. Infrastructure for the system under study was decommissioned on **2026-07-04**. Public **DNS (Domain Name System)** names are **inactive**. The durable evidence is Git: architecture, **ADRs (Architecture Decision Records)**, setup topics 01–20, Terraform modules, GitOps trees, SLO catalogs, runbooks, and one dated game-day report.

This is not a catalog of monitoring products. Products change. The durable skill is being able to explain:

- which user-visible journeys **SLOs (Service Level Objectives)** protect, and which measurements must not count as success;
- what remaining error budget authorizes, slows, or freezes;
- what human system absorbs a page without informal heroics; and
- what a dated game-day report proved — and what STATUS without a report still claims.

## The repository is the system

There is no companion lab and no invented storefront. The system under study is:

```text
https://github.com/btilki/boutique-gke-sre
```

Local path on the author’s machine:

```text
/Users/biroltilki/Documents/Cursor/boutique-gke-sre
```

Online Boutique is the upstream application ([GoogleCloudPlatform/microservices-demo](https://github.com/GoogleCloudPlatform/microservices-demo)). This repository is the production-style platform around it: one private regional GKE cluster in project `boutique-gke`, **GitOps (Git-based operations)** with manual Argo CD sync, digest-only images, SLOs on browse and checkout, burn-rate pages to PagerDuty, and teardown that must leave no orphans.

The README states the current operational fact in the first line:

```text
Infrastructure: Decommissioned 2026-07-04. Documentation and screenshots remain;
public DNS names are inactive (no A records until rebuild).
```

Do not treat screenshots of `boutique.biroltilki.art` as proof that the edge is live. They are **Inactive** evidence of a lived pilot. Do not treat cluster Ready, kubelet Ready, or Argo CD UI uptime as reliability success. SLOs protect browse and checkout journeys.

If the clone is **newer** than this manuscript, start at `ROADMAP.md` and `docs/release/`. This repository has no `CHANGELOG.md`; those two trees are the delta. Several chapters embed **Inactive** PNGs from `assets/diagrams/` (Argo CD, Grafana, SLO dashboard, PagerDuty, Kyverno, Armor, Binary Authorization, runbook-lint). If a PNG is missing from the clone, skip the figure.

After the conclusion, [17-interview-questions-from-this-repository.md](17-interview-questions-from-this-repository.md) answers ten design-review questions from these files. Matching chapters point at playbook articles **G1** (burn), **G2** (WIF), **G3** (BinAuth + Armor). From `books-prompts/books/boutique-production/`, run `python3 tools/citation_drift_check.py --book gke-sre` after a repo or manuscript change.

## Lived, scaffold, and apply-on-rebuild

`ROADMAP.md` and `docs/setup/README.md` split the work honestly:

| Label | Meaning in this book |
| --- | --- |
| **Lived** | Phases 1–8 and setup topics **01–16** ran on the real cluster before teardown. |
| **Repo-ready / apply on rebuild** | Phases **9-A–9-D**, setup topics **17–20**. Files exist in Git. They were not re-applied after 2026-07-04. |
| **Executed game day** | Game day **03** (Redis / cart down) on **2026-07-04**, with a dated report and a postmortem. |
| **Deferred game days** | Game days **01**, **02**, and **04**. Guides exist. STATUS.md does not mark them executed. |
| **Inactive** | `boutique.biroltilki.art` and `argocd.boutique.biroltilki.art` have no public A records. |

Topic 20 (error-budget ritual, capacity baseline, toil) can be practiced from Git while the project is offline. Topics 17–19 require a rebuilt cluster to become lived again.

A YAML file in Git is not a passed milestone. `docs/sre/game-days/reports/STATUS.md` is the honesty gate: a scenario without a dated report is **Deferred**, not done.

## How to read a chapter

Each chapter answers one production question and cites repository-relative paths. Guided work uses Practice boxes: you open a real file, interpret a real decision, and state what evidence would prove a change. You are not required to spend cloud money unless the chapter is explicitly about rebuild or teardown.

At the start of the main conceptual section, a theory box names the model. Independent Practice at the end is unguided. Dedicated failure sections classify severity, plausible harm, potential blast radius, bounding controls, and `Primary principles:` drawn from the series contract.

On first use in each reader-facing file, abbreviations are written as **SLO (Service Level Objective)** (or the equivalent for that term). The abbreviation is used alone afterward. Literal code, paths, and version identifiers are not expanded.

## What this book will not do

- It will not reteach GitOps mechanics as the point of the book. Manual Argo CD sync is promotion discipline (ADR 003); the GitOps sister title owns that question more deeply.
- It will not reteach Azure supply-chain threat modeling as the point of the book. The DevSecOps sister title owns that question more deeply.
- It will not invent a second cluster, a status-page product, or a multi-region fail-over that the repository refused.
- It will not call Phase 9 complete because the files exist.

## Relationship to the sister titles

This book is one title in the Boutique Production Series. It does not mutate the frozen Northwind manuscripts. It does not reteach Linux or Kubernetes.

- *Practical GitOps on Amazon EKS* teaches pull reconciliation and promotion on `boutique-eks-gitops`. This book assumes you can read an Argo CD Application and a digest pin. Manual sync is a reliability gate here (ADR 003), not a GitOps tutorial.
- *Practical DevSecOps on Azure Kubernetes Service* teaches threat boundaries on `boutique-aks-devsecops`. This book assumes you can read WIF, Kyverno, and Binary Authorization as controls that SRE depends on. Chapter 14 is the place those controls collided with restore.

Reading order across the three titles is optional. Cross-references appear when a sister platform made a different honest choice. They do not require you to finish another book first.

## Chapter dependency

Later chapters consume earlier decisions:

```text
journeys and refusals (Ch 1)
  → recorded blast radius and ADRs (Ch 2)
  → private foundation (Ch 3)
  → recoverable edge (Ch 4)
  → WIF and signed digests (Ch 5)
  → Phase 4 gate (Ch 6)
  → Boutique by digest (Ch 7)
  → telemetry pipeline (Ch 8)
  → SLO burn pages (Ch 9)
  → on-call and SEV (Ch 10)
  → Armor and BA enforce (Ch 11)
  → runbooks as product (Ch 12)
  → error-budget freeze (Ch 13)
  → honest game days (Ch 14)
  → teardown and rebuild (Ch 15)
```

You can skip a chapter only if you already accept its durable outputs (the ADRs, catalogs, and STATUS table already in Git). You cannot skip Chapter 1’s refusals and then call cluster Ready an SLO in Chapter 9.

## Four kinds of evidence

1. **Mechanism evidence** proves that a dashboard, alert, pager, runbook, or Terraform module exists and is wired.
2. **Decision evidence** proves that an owner evaluated journeys, blast radius, and freeze behavior.
3. **Outcome evidence** proves that a user-visible journey held, or that remaining error budget was accounted.
4. **Recovery evidence** proves the journey recovered after a named failure — not that nodes returned to Ready.

The 2026-07-04 Redis game day produced mechanism and partial recovery evidence. It did **not** verify PagerDuty. Binary Authorization blocked restore until a temporary DRYRUN window. Chapter 14 treats that as the teaching event, not as a passed production drill.

## What opening a file proves

Opening `docs/sre/slos/catalog.md` proves the journeys were named. It does not prove Cloud Monitoring still has SLO objects. Opening `STATUS.md` proves the honesty rule. It does not prove game days 01, 02, or 04 ran. `terraform plan` on a rebuilt project proves drift against Git. It does not prove browse availability.

When a chapter shows a command, it is the command from the setup guide the operator used — not a new Makefile target invented for this book. Rebuilds cost money. They are optional unless you are in Chapter 15 or explicitly practicing apply-on-rebuild for topics 17–20.

## How to judge your work

Do not ask only whether the cluster was Ready or whether Grafana loaded. Ask:

> Which browse or checkout journey is at risk, what error budget remains and what change it freezes, which runbook the page opens, and what dated report would prove the failure was actually exercised?

That question is the reading contract for the chapters ahead.
