# Practical DevSecOps on Azure Kubernetes Service

**Series:** Boutique Production Series  
**Edition:** v1.0  
**Source repository:** [boutique-aks-devsecops](https://github.com/btilki/boutique-aks-devsecops)

Run a defensible Azure **DevSecOps (Development, Security, and Operations)** path for Online Boutique on one **AKS (Azure Kubernetes Service)** cluster: GitHub as source of truth, **ADO (Azure DevOps)** as the only pipeline runner, **OIDC (OpenID Connect)** to Azure, mirror-scan-sign by digest, Kyverno as the last admission gate, Key Vault plus **CSI (Container Storage Interface)** for secrets, GitOps promotion with prod approval, teardown that destroys **ACR (Azure Container Registry)**, and Phase 15+ scaffolds that stay labeled scaffold.

Do not call the platform production-ready. `prod` is a namespace on one cluster.

## Manuscript

| # | File | Lived / scaffold |
|---|------|------------------|
| 0 | [00-how-to-use-this-book.md](00-how-to-use-this-book.md) | — |
| 1 | [01-charter-a-devsecops-pilot-you-can-defend.md](01-charter-a-devsecops-pilot-you-can-defend.md) | Lived charter |
| 2 | [02-make-setup-guides-and-versions-the-contract.md](02-make-setup-guides-and-versions-the-contract.md) | Lived |
| 3 | [03-lock-design-with-adrs-before-credentials-exist.md](03-lock-design-with-adrs-before-credentials-exist.md) | ADRs 0001–0012 lived; 0013–0017 scaffold |
| 4 | [04-bootstrap-terraform-state-network-and-dns.md](04-bootstrap-terraform-state-network-and-dns.md) | Lived Topics 00–02 |
| 5 | [05-provision-aks-acr-key-vault-and-workload-identity.md](05-provision-aks-acr-key-vault-and-workload-identity.md) | Lived Topic 03 |
| 6 | [06-split-github-truth-from-azure-devops-execution.md](06-split-github-truth-from-azure-devops-execution.md) | Lived Topic 04 |
| 7 | [07-bootstrap-argo-cd-as-the-cluster-reconciler.md](07-bootstrap-argo-cd-as-the-cluster-reconciler.md) | Lived Topic 05 |
| 8 | [08-terminate-tls-with-ingress-and-dns-01.md](08-terminate-tls-with-ingress-and-dns-01.md) | Lived Topic 06 |
| 9 | [09-deliver-secrets-through-key-vault-and-csi.md](09-deliver-secrets-through-key-vault-and-csi.md) | Lived Topic 07 |
| 10 | [10-mirror-scan-and-sign-digests-in-ci.md](10-mirror-scan-and-sign-digests-in-ci.md) | Lived Topic 09 |
| 11 | [11-deny-unsigned-workloads-at-admission.md](11-deny-unsigned-workloads-at-admission.md) | Lived Topic 08 |
| 12 | [12-deploy-boutique-with-kustomize-overlays.md](12-deploy-boutique-with-kustomize-overlays.md) | Lived Topic 10 |
| 13 | [13-observe-without-buying-a-siem-first.md](13-observe-without-buying-a-siem-first.md) | Lived Topic 11 |
| 14 | [14-promote-the-same-digest-through-approval.md](14-promote-the-same-digest-through-approval.md) | Lived Topic 12 |
| 15 | [15-destroy-acr-when-you-tear-down.md](15-destroy-acr-when-you-tear-down.md) | Lived Topic 13 |
| 16 | [16-apply-phase-15-plus-scaffolds-without-pretending-they-lived.md](16-apply-phase-15-plus-scaffolds-without-pretending-they-lived.md) | Scaffold Topics 14–20 |
| 17 | [17-threat-model-the-pilot-and-operate-day-2-honestly.md](17-threat-model-the-pilot-and-operate-day-2-honestly.md) | Lived model; day-2 docs |
| 18 | [18-conclusion.md](18-conclusion.md) | — |
| 19 | [19-interview-questions-from-this-repository.md](19-interview-questions-from-this-repository.md) | Rehearsal from files |

## Back matter

- [GLOSSARY.md](GLOSSARY.md)
- [REFERENCES.md](REFERENCES.md)
- [EDITORIAL-CONVENTIONS.md](EDITORIAL-CONVENTIONS.md)
- [BOOK-PLAN.md](BOOK-PLAN.md) — planning document; not a chapter

## Promise

The reader will be able to explain, from this repository, why unsigned or `:latest` images must not reach the cluster, why GitHub Actions is absent on purpose, why destroying ACR is a security and cost control, and what Topics 14–20 have not yet proven live.

## Sister titles

| Book | Unique claim |
|------|----------------|
| *Practical GitOps on Amazon EKS* | Git as deploy authority; keyless cosign; GitLab CI |
| *Practical SRE on Google Kubernetes Engine* | User-visible **SLOs (Service Level Objectives)** and PagerDuty |
| *This book* | Admission + signed digest + ACR destroy on AKS |
