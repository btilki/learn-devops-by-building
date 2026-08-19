# Boutique Production Series

**Status:** Drafting  
**Date:** 2026-08-18  
**Author:** Birol Tilki

This series lives under `books/boutique-production/`. It is **separate** from the frozen Northwind Practical Engineering books (`../practical-engineering/devops/`, `../practical-engineering/devsecops/`, `../practical-engineering/platform/`, `../practical-engineering/sre/`). Do not mutate those manuscripts or labs. Do not treat these books as a fifth Northwind title.

## Why this series exists

The Northwind books teach production decisions on a designed companion lab. They are practical, but they do not use the author's lived GitOps, SRE, and DevSecOps repositories as the system under study.

These books do. Each title is bound to one repository. Every chapter cites files, ADRs, and setup topics from that repository. Examples must cover every topic the repository contains: lived setup, architecture, ADRs, implementation, operations, scaffolds, and honest limits.

## Books

| Book | Manuscript | Source repository |
| --- | --- | --- |
| *Practical GitOps on Amazon EKS* | [gitops/](gitops/) | `Cursor/boutique-eks-gitops` |
| *Practical SRE on Google Kubernetes Engine* | [gke-sre/](gke-sre/) | `Cursor/boutique-gke-sre` |
| *Practical DevSecOps on Azure Kubernetes Service* | [aks-devsecops/](aks-devsecops/) | `Cursor/boutique-aks-devsecops` |

The three repositories are sister platforms for [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo). They share GitOps and digest discipline. They differ in cloud, CI, and the production question each one is built to answer.

Reading order is optional. GitOps, SRE, and DevSecOps can be read independently. Cross-references are allowed when a sister platform made a different, equally honest choice.

## Teaching contract

- Audience: intermediate-to-advanced practitioners. Do not teach Linux, Git, containers, or Kubernetes from first principles.
- The repository is the system. There is no Northwind companion lab and no invented storefront.
- Practice is file-backed: the reader opens a real path, interprets a real decision, and reasons about a change, failure, or rebuild. Rebuilds cost money and are optional unless a chapter says otherwise.
- Infrastructure for all three platforms was torn down after the lived pilots. The books teach from Git, ADRs, screenshots, and reports. Do not pretend the clusters are still running.
- Scaffold topics are first-class. Label them **lived** or **scaffold**. Do not upgrade a scaffold into a proven production claim.
- On first use in each reader-facing document, write an abbreviation followed by its full form in parentheses and bold the complete expression, for example **CI (Continuous Integration)**. Use the abbreviation alone afterward. Do not alter literal code, paths, or version identifiers.
- At the start of the main conceptual section, use one theory box: `> *Theory — Model name*` plus one sentence stating the production decision the model enables.
- Mark guided reader work with `> **Practice — Action name**` plus one sentence stating what the reader will open, change, or prove. Use `> **Independent Practice — Action name**` for the unguided close.
- Every chapter answers one production question and names durable outputs (usually ADRs, policies, runbooks, or checklists already in the repo).
- Every dedicated failure section names severity, plausible harm, potential blast radius, bounding controls, and `Primary principles:`.
- Prefer quoting short, real excerpts over paraphrasing. Cite repository-relative paths.
- **Further reading** at the end of a matching chapter may point to one playbook article (`devops-engineering-playbook/articles/E1.md`, `A1.md`, `G1.md`, and siblings). Do not duplicate the article. One line plus the URL is enough.
- **Figures** are **Inactive** lived evidence: screenshots and diagrams already in the source repo (`assets/images/setup/`, `assets/diagrams/`). Caption them as historical. Do not imply DNS still answers.
- **CHANGELOG.md** is the rebuild delta. How to Use and References must point to it so a later clone is actionable, not only disclaimed.
- **Interview questions** live in a numbered appendix after the conclusion. Answers must cite repository paths. Do not invent a second architecture.
- Run `tools/citation_drift_check.py` when a source repo or manuscript changes. If a cited path is missing from the clone, the clone wins and the manuscript must change.

## Recurring principles

1. **Git is the deploy authority** unless a chapter is explicitly about a bounded exception (bootstrap, teardown, emergency).
2. **Identity is digest, not tag.** Floating tags and `:latest` are failures.
3. **CI never deploys** the cluster. It produces evidence and proposes Git changes.
4. **Namespaces on one cluster are not multi-account isolation.** Say so whenever environments appear.
5. **Teardown is a production control**, not an afterthought. Cost and leftover identity are in scope.
6. **Lived evidence beats scaffold.** A YAML file in Git is not the same as a passed milestone.

## Relationship to the Northwind series

Readers of the Northwind books already know the vocabulary: digest promotion, pull reconciliation, burn rate, threat boundaries. These books apply that vocabulary to three real platforms. They do not reteach Northwind chapters and they do not replace them.

Publication style (author line, Word colors) remains `../practical-engineering/SERIES-PUBLICATION-STYLE.md` if these titles are later rendered to Word. First edition of each title is **v1.0**.

## Source paths on this machine

```text
/Users/biroltilki/Documents/Cursor/boutique-eks-gitops
/Users/biroltilki/Documents/Cursor/boutique-gke-sre
/Users/biroltilki/Documents/Cursor/boutique-aks-devsecops
```

Public GitHub mirrors:

- https://github.com/btilki/boutique-eks-gitops
- https://github.com/btilki/boutique-gke-sre
- https://github.com/btilki/boutique-aks-devsecops
