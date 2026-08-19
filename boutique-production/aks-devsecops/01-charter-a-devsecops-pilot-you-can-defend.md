# 1. Charter a DevSecOps Pilot You Can Defend

A platform that cannot name its limits will be treated as production by the next person who clones it. Badges, “enterprise-ready” language, and empty **CI (Continuous Integration)** trees create that confusion. This chapter charters the **AKS (Azure Kubernetes Service)** pilot from the files that already constrain it: `README.md`, `ROADMAP.md`, `ARCHITECTURE.md`, and `CONTRIBUTING.md`.

The production question is:

> What does this repository prove, what does it refuse to claim, and who is accountable for that honesty after teardown?

## 1. Unsafe starting state

The unsafe default for a public Azure reference is to look finished. A README with a shields.io wall, a `.github/workflows` folder that does nothing, and the phrase “production-ready” on a single-cluster namespace layout will be copied into a real subscription as if isolation were already solved.

This repository forbids that posture. The lived test is **torn down**. Topics **14–20** are **scaffold**. Hostnames in the README are **inactive** until a rebuild. Calling `boutique-prod` “production” without the limitations table is the first security failure: it misstates blast radius before any pod runs.

## 2. The production model: a defendable charter

> *Theory — Production-pilot charter*
>
> This model enables the team to publish a real DevSecOps path without implying multi-cluster isolation, 24×7 operations, or a live estate that no longer exists.

A charter is not marketing. It is a set of falsifiable claims:

- **What ran.** Setup Topics 00–13 lived on Azure in `germanywestcentral` and were destroyed.
- **What did not run.** Topics 14–20 exist as files. They are not passed milestones.
- **What isolation is.** Three namespaces on one cluster (`boutique-dev`, `boutique-stage`, `boutique-prod`).
- **What CI is.** GitHub holds Git; **ADO (Azure DevOps)** runs pipelines; GitHub Actions is absent.
- **What teardown does.** **ACR (Azure Container Registry)** is destroyed with the cluster ([ADR-0010](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0010-destroy-acr-on-teardown.md)).

The README states the limitation in the voice this book will keep:

```text
Do not call this production-ready. Environments named prod are logical
namespaces on one cluster, not a multi-cluster production estate.
```

That sentence is the charter. Later chapters implement it; they do not relax it.

## 3. How this repository implements the charter

> **Practice — Read the public contract**
>
> Open `README.md` and extract the CI story, limitations table, and hostname disclaimer before you open Terraform.

### CI story

The 30-second table in `README.md` is the delivery contract:

| | |
|-|-|
| **What** | DevSecOps on Azure AKS — signed digests, Kyverno admission, GitOps promotion |
| **CI model** | **GitHub** = source of truth · **Azure DevOps** = pipelines (**OIDC (OpenID Connect)**) · no GitHub Actions |
| **Hard rule** | Unsigned / floating tags should not reach the cluster |
| **Proven** | Setup Topics 00–13 lived and **torn down**; Topics 14–20 scaffold-only until rebuild |

The ASCII flow that follows is the rest of the book in eight lines: GitHub checkout into ADO, digest push, Argo CD reconcile, AKS plus ACR. CI does not `kubectl apply` Boutique. Git does.

### What the architecture actually claims

`ARCHITECTURE.md` repeats the same maturity line: **production pilot (single cluster)**. Functional requirements FR-01 through FR-04 map to `terraform/`, `gitops/`, `policies/`, and `pipelines/`. Non-functional cost is explicit: one cluster; teardown destroys ACR.

Environments are logical:

| Env | Namespace | Hostname | Argo sync | Prod gate |
|-----|-----------|----------|-----------|-----------|
| dev | `boutique-dev` | `dev-boutique.biroltilki.art` | Auto | — |
| stage | `boutique-stage` | `stage-boutique.biroltilki.art` | Manual | — |
| prod | `boutique-prod` | `boutique.biroltilki.art` | Manual | **ADO environment approval** |

Those **FQDNs (fully qualified domain names)** are inactive after teardown. Visual proof lives under `assets/images/setup/` and is catalogued in `assets/images/README.md`. Use screenshots when public URLs are offline. Do not invent a live demo from a clone.

### Roadmap honesty

`ROADMAP.md` separates two clocks. Setup **Topic 13** is teardown. Roadmap **Phase 13** (hardening) was skipped and superseded by Phase 15+. Setup Topics **14–20** are those fuller packages. Status ✅ on a scaffold row means files exist, not that Falco ran on the lived cluster.

Milestone M7 is teardown validated with no billable AKS/ACR. Milestone M8 rows are scaffold-complete. Confusing those rows is how a reader “enables runtime security” in a talk while the DaemonSet never started.

> **Practice — Trace one claim to a file**
>
> Pick one cell in the README limitations table and name the architecture or ADR file that makes it true.

Example: “No 24×7 on-call, Tempo/Jaeger, **SOC (Security Operations Center)** **SIEM (Security Information and Event Management)**” traces to `ARCHITECTURE.md` observability, [ADR-0012](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0012-loki-in-cluster-logging.md) (in-cluster Loki, not Log Analytics), and Chapter 13. “WAF, DDoS, HSM-backed keys” traces to the out-of-scope list in `ROADMAP.md`.

### Public-share hygiene

`CONTRIBUTING.md` treats honesty as a merge gate:

| Avoid | Why / Do instead |
|-------|------------------|
| Empty `.github/workflows` (even “with README later”) | CI is ADO only — never create this tree |
| Claiming **production-ready** / enterprise-ready | Say **production pilot**; link Limitations |
| Shields.io / badge grids on README | Status tables and prose only — no badge walls |

The workflow also says: one phase per **PR (pull request)**; `docs/setup/` is the source of truth for implementation order; run `pre-commit run --all-files` before opening a PR. That is how the charter survives the next edit.

`SECURITY.md` restates the same supply-chain and secret rules: no keys in Git, OIDC for pipelines, Kyverno at admission, ACR destroyed on teardown. The security policy is part of the charter, not a footer.

## Files this charter rests on

Read in this order on a first pass:

1. `README.md` — limitations, CI story, inactive hostnames
2. `ROADMAP.md` — lived vs scaffold tables
3. `ARCHITECTURE.md` — FR/NFR and component map
4. `CONTRIBUTING.md` — public-share hygiene
5. `SECURITY.md` — never-commit and teardown ACR
6. `assets/images/README.md` — screenshot catalog
7. Playbook articles A1–A3 — optional retellings; repo files win

`CHANGELOG.md` is the notice board. It does not replace an ADR. `docs/implementation/plan.md` is the long plan; setup topics are the operator path.

## 4. Test the design under failure

### Independent control failure — Publish the pilot as production-ready

> **Practice — Diagnose a dishonest README**
>
> A fork adds a “production-ready AKS platform” badge and an empty `.github/workflows/ci.yml` “for later.” Decide what harm that causes before any cluster exists.

**Severity:** high; false isolation and false CI authority.  
**Plausible harm:** a team deploys unsigned images from GitHub Actions, treats `boutique-prod` as a separate estate, and leaves ACR running after a “temporary” test.  
**Potential blast radius:** the whole cluster (ADR-0002) plus any registry and identity leftovers after incomplete teardown.  
**Bounded by:** limitations table, CONTRIBUTING hygiene, absence of `.github/workflows`, ADR-0010 destroy-ACR, lived-versus-scaffold labels.  
**Primary principles:** explicit contracts (GitHub vs ADO), namespaces on one cluster are not multi-account isolation, teardown is a production control, lived evidence beats scaffold.

#### Diagnosis

The badge answers a marketing question. The empty workflow answers a tooling fashion. Neither answers the four security questions: what asset is protected, what trust is granted, what detection remains, what recovery evidence exists. A GitHub Actions file that does not sign images also trains reviewers to ignore `pipelines/`.

The lived cluster is already gone. Inflating the README after teardown is worse: readers cannot falsify the claim against Azure.

#### Correction

Restore the limitations table. Delete `.github/workflows`. Point CI to `pipelines/README.md`. Keep Topics 14–20 labeled scaffold. If you need a status line, use the README table: planning scaffold complete; implementation 00–13 complete and torn down.

## Production reality

**Best Practice:** publish limitations next to the demo, not in a wiki nobody clones.

**Production Practice:** every public sentence must remain true after teardown. If DNS is down, the README must say so and point at `assets/images/`. If Topics 14–20 are files only, ROADMAP must not use the same ✅ icon without a scaffold column.

Related portfolio links in the README (playbook, articles A1–A3, sister repos) are allowed. They are not a claim that this cluster is still running. Article A2 (unsigned deny) and A3 (destroy ACR) are the same unique claim this book makes; the manuscript cites the repo files, not the articles, as evidence.

`CHANGELOG.md` records notable changes. It is not a substitute for ADRs. If a SKU changed, ADR-0011 is the decision; the changelog is the notice.

Cost ~€150–250/month is an order of magnitude for `germanywestcentral` with two nodes. Publishing “cheap HA production” against that number is a charter failure even if every control in later chapters is perfect.

### Common errors

- Copying the repo and adding GitHub Actions “so Dependabot has a status check.”
- Renaming `boutique-prod` to `production` in slides without the namespace footnote.
- Treating M8 scaffold ✅ as “Falco lived.”
- Linking `https://dev-boutique.biroltilki.art` in a resume after Topic 13 without the screenshot.

## 5. What You Learned

A defendable DevSecOps pilot starts as a charter: one cluster, three namespaces, GitHub for Git, ADO for pipelines, unsigned images forbidden, ACR destroyed on teardown, scaffolds named as scaffolds. `README.md`, `ROADMAP.md`, `ARCHITECTURE.md`, and `CONTRIBUTING.md` are the public contract. Screenshots replace live DNS after destroy.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Limitations and CI story | `README.md` | Names what the repo proves and refuses |
| Phase tracker | `ROADMAP.md` | Separates lived Topics 00–13 from scaffold 14–20 |
| Executive architecture | `ARCHITECTURE.md` | Maps FR-01–FR-04 to repo paths |
| Public-share hygiene | `CONTRIBUTING.md` | Forbids empty Actions trees and “production-ready” copy |
| Screenshot catalog | `assets/images/README.md` | Evidence while FQDNs are inactive |

## What changed

| Before | After |
|--------|--------|
| A public AKS sample looked production-ready. | **README limitations forbid that sentence.** |
| CI might be implied by GitHub. | **GitHub holds Git; ADO runs `pipelines/`; no Actions.** |
| Topics 14–20 looked like finished work. | **ROADMAP splits lived 00–13 from scaffold 14–20.** |
| Live URLs were the demo. | **Screenshots remain after teardown.** |

> **Independent Practice — Rewrite a dishonest fork blurb**
>
> A colleague wants to list this repo on an internal catalog as “enterprise HA Boutique on AKS.” Write six sentences they may publish. Each sentence must be true after teardown. Include CI split, namespace isolation, ACR destroy, and scaffold status. Do not add a badge.

You can demonstrate Chapter 1 when you can explain why `prod` is not a production estate, why GitHub Actions is absent, why screenshots exist, and which ROADMAP rows are lived versus scaffold.
