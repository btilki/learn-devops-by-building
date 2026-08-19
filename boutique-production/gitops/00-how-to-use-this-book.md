# How to Use This Book

This book teaches production **GitOps (Git as the deploy authority)** from one lived repository: Online Boutique on a single Amazon **EKS (Elastic Kubernetes Service)** cluster. The unsafe default the series refuses is a pipeline that can `kubectl apply` or `argocd sync` against the cluster. The durable claim is narrower: Git is the only deploy authority, image identity is digest, and **CI (Continuous Integration)** never deploys.

## Who this book is for

This book is for intermediate-to-advanced DevOps, platform, cloud, and GitOps practitioners who already work with Linux, Git, containers, **IaC (Infrastructure as Code)**, Kubernetes, Helm, and a cloud account. It does not teach those tools from first principles.

You should be able to read a Terraform module, an Argo **CD (Continuous Delivery)** Application, and a Helm values file without a primer. What you may not yet have is a complete, honest production-pilot path: digest-only promotion, human `dev → stage → prod`, frontend canary, a security and observability baseline, production-readiness evidence, mandatory teardown, and labeled Phase 12 scaffolds.

Sister titles in this series answer different production questions on the same storefront family: *Practical SRE on Google Kubernetes Engine* (`gke-sre/`) and *Practical DevSecOps on Azure Kubernetes Service* (`aks-devsecops/`). Reading order is optional.

## The repository is the system

There is no companion lab and no invented storefront. Clone or open:

```text
https://github.com/btilki/boutique-eks-gitops
```

Local path on the author's machine: `/Users/biroltilki/Documents/Cursor/boutique-eks-gitops`. GitHub is the public source; GitLab was the **CI** and merge remote during the pilot.

```bash
git clone https://github.com/btilki/boutique-eks-gitops.git
cd boutique-eks-gitops
```

Do not provision **AWS (Amazon Web Services)** from the README. The Setup Guide under `docs/setup/` is the bootstrap authority. This book walks that same tree as a reader: you open a path, interpret a decision, and state what evidence would prove a change. Rebuilds cost money and are optional unless a chapter is explicitly about rebuild or teardown.

The lived pilot ran in `eu-central-1`, reached **M3 (Milestone 3)** + **M4 (Milestone 4)** PASS on 2026-07-19/20, and then destroyed AWS resources. Public **DNS (Domain Name System)** names under `biroltilki.art` are **inactive** until a rebuild. Practice is file-backed. Live rebuild is optional and costs money.

## Lived, scaffold, and inactive

Every cited topic carries one honesty label:

| Label | Meaning |
|-------|---------|
| **Lived** | Ran on a real cluster before teardown. Milestones M1–M4 and Setup Topics 01–14. |
| **Scaffold** | Files in Git that were not live-validated on this pilot. Setup Topics 15–19 and **ADRs (Architecture Decision Records)** 0007–0010. |
| **Inactive** | DNS names and screenshots that remain after teardown. They describe what existed; they are not a live endpoint. |

Do not upgrade a scaffold into a proven production claim. A YAML file in Git is not the same as a passed milestone. Chapter 15 exists so you can author the next cluster's hardening *before* you pay for it — and so you can say, honestly, that signature admission, **WAF (Web Application Firewall)**, and Falco were not proven here.

The repository's own README already draws that line:

```23:24:README.md
| **Proven** | Multi-AZ pilot (M3+M4 PASS); AWS resources **torn down** after validation |
| **Stack** | Terraform · EKS 1.31 · Argo CD · Rollouts · Kyverno · Prom/Loki/Grafana |
```

**Lived.** The maturity badge is production *pilot*, not multi-account **HA (High Availability)**.

## How to walk the chapters with the clone

Open the clone beside this manuscript. Each core chapter cites repository-relative paths. When a Practice box says "open," you open that file. When it says "prove," you state the Git evidence that would make the claim true — a digest diff, a CODEOWNERS path, a `syncPolicy` absence, a teardown appendix row. You do not need a live cluster for that work.

Suggested rhythm:

1. Read Chapter 1 against `README.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, and `docs/architecture/10-cost-model.md`.
2. Read Chapters 2–3 before any Terraform file. Constraints and repository spine come first.
3. Read Chapters 4–8 as the platform path (Topics 03–08). Treat quoted `kubectl` and `helm` commands as the operator's Setup Guide, not as homework against a live account.
4. Read Chapters 9–12 as the workload path (charts, **CI**, promotion, canary).
5. Read Chapters 13–14 as evidence and teardown. Appendix T in `docs/PRODUCTION_CHECKLIST.md` is the M4 record.
6. Read Chapter 15 as scaffold. Label every path you open.

Later chapters consume earlier decisions. Digest identity from Chapter 2 becomes the Helm contract in Chapter 9 and the **CI** **MR (Merge Request)** in Chapter 10. Manual prod sync from Chapter 6 becomes the promotion gate in Chapter 11. Teardown in Chapter 14 is not an appendix; it is a production control.

The numbered chapters map onto Setup topics 01–19 without remainder:

| Chapters | Setup topics | Honesty |
|----------|--------------|---------|
| 1–2 | Charter + architecture 01–10 + ADRs 0001–0005 | **Lived** decisions |
| 3 | 01–02 | **Lived** repo spine |
| 4 | 03–04 | **Lived** Terraform; AWS objects destroyed |
| 5–8 | 05–08 | **Lived** M1–M2 platform |
| 9–12 | 09–12 | **Lived** charts, CI, promotion, canary |
| 13–14 | 13–14 | **Lived** M3 + M4 |
| 15 | 15–19 + ADRs 0007–0010 | **Scaffold** only |

If a path in the clone disagrees with a sentence here, the clone wins. This book teaches the repository; it does not replace `docs/setup/` as bootstrap authority.

If the clone is **newer** than this manuscript, start at `CHANGELOG.md`. That file is the rebuild and post-pilot delta. This book is a snapshot of the lived M3+M4 path plus labeled Phase 12 scaffold; it does not restate every later commit.

**Inactive figures.** Several chapters embed screenshots from `assets/images/setup/` (Argo CD, Grafana, GitLab CI, storefronts). DNS is inactive. The PNG is historical evidence, not a live UI. The catalog lives in the clone; if a PNG is missing, skip the figure.

**Interview appendix.** After the conclusion, [17-interview-questions-from-this-repository.md](17-interview-questions-from-this-repository.md) answers ten design-review questions from these files. Use it as a rehearsal, not as a second architecture.

**Playbook shorts.** Matching chapters end with one further-reading link into [devops-engineering-playbook](https://github.com/btilki/devops-engineering-playbook) (E1 digest-only, E2 canary, E3 cost). The article is not a second source of truth.

**Citation drift.** From `books-prompts/books/boutique-production/`, run `python3 tools/citation_drift_check.py --book gitops` after a repo or manuscript change.

## Abbreviations

On first use in each reader-facing file, write the abbreviation followed by its full form, and bold the complete expression: **CI (Continuous Integration)**. Use the abbreviation alone afterward. Do not expand inside code fences, filenames, or version identifiers. The glossary at the back lists every abbreviation this book uses.

## How to read the boxes

`Theory` establishes the mental model for the chapter's production decision. It is not a survey of GitOps literature.

`Practice` tells you which real path to open, what decision it encodes, and what evidence would prove a change. Guided work is file-backed. Commands shown are the commands the operator used in the Setup Guide, not new Makefile targets invented for this book.

`Independent Practice` is the unguided close. It changes a constraint and requires a justified design rather than copying the guided walk.

## What this book will not do

It will not teach a demo cluster that you leave running. It will not pretend namespaces on one cluster are multi-account isolation. It will not treat Phase 12 files as lived proof. It will not make **CI** the deployer. It will not add a service mesh, multi-region **DR (Disaster Recovery)**, CloudWatch, PagerDuty, or OpenTelemetry to a pilot that refused them.

The Makefile at the repo root is a documentation and format check. It does not install CLIs, apply Terraform, or deploy to the cluster. Setup authority remains `docs/setup/`.

## Recurring principles

1. Git is the only deploy authority.
2. Image identity is digest, not tag.
3. **CI** has **ECR (Elastic Container Registry)** and Git permission, not cluster deploy permission.
4. One cluster and three namespaces are a cost decision, not isolation.
5. Teardown after the pilot is required, not optional hygiene.
6. Scaffold in Git is not lived proof.

Each dedicated failure names the subset it exercises.

## Environment for optional rebuild

If you rebuild, follow `docs/setup/` in numeric order through Topic 14. Pins live in `docs/versions.md`. Budget awareness is in `docs/architecture/10-cost-model.md`: roughly **$35–45** for a two-day run with teardown, or **$350–500/mo** if left up. The original pilot's AWS resources are gone. A rebuild is a new spend, a new cluster, and a new Appendix T.

You can complete this book without spending that money. The files are the system.

When a chapter quotes `kubectl` or `helm upgrade --install`, copy it only if you are rebuilding. The quote proves what the operator ran in `docs/setup/`; it is not a hidden lab makefile. `make lint` and `make docs-check` are the only repo-root commands this book expects of every reader.

Public names `argocd.boutique.biroltilki.art`, `grafana.boutique.biroltilki.art`, `dev-boutique.biroltilki.art`, `stage-boutique.biroltilki.art`, and `boutique.biroltilki.art` are **inactive**. Screenshots in the repo, if any, are historical. Do not file a bug that “the shop is down.” M4 required that.

Editorial pointer: [`EDITORIAL-CONVENTIONS.md`](EDITORIAL-CONVENTIONS.md) in this folder and [`../BOUTIQUE-EDITORIAL-CONVENTIONS.md`](../BOUTIQUE-EDITORIAL-CONVENTIONS.md) for the series skeleton.
