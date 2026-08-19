# Practical DevSecOps on Azure Kubernetes Service — Book Plan

**Planning status:** Active draft  
**Draft date:** 2026-08-18  
**Source repository:** `boutique-aks-devsecops`  
**Series:** [Boutique Production Series](../BOUTIQUE-SERIES.md)

## Promise

Run a defensible Azure DevSecOps path for Online Boutique on one **AKS (Azure Kubernetes Service)** cluster: GitHub as source of truth, Azure DevOps as the only pipeline runner, **OIDC (OpenID Connect)** to Azure, mirror-scan-sign by digest, Kyverno as the last admission gate, Key Vault plus CSI for secrets, GitOps promotion with prod approval, teardown that destroys **ACR (Azure Container Registry)**, and Phase 15+ scaffolds that stay labeled scaffold.

The reader will be able to explain, from this repository, why unsigned or `:latest` images must not reach the cluster, why GitHub Actions is absent on purpose, why destroying ACR is a security and cost control, and what Topics 14–20 have not yet proven live.

## Audience

Intermediate-to-advanced DevSecOps, platform, and Azure practitioners. The book does not teach Azure, Kubernetes, or YAML from first principles.

## System under study

```text
https://github.com/btilki/boutique-aks-devsecops
```

Local path: `/Users/biroltilki/Documents/Cursor/boutique-aks-devsecops`.

Setup Topics 00–13 lived and were torn down. Topics 14–20 are scaffold-complete. Region when rebuilt: `germanywestcentral`. Do not call the platform production-ready.

## Coverage rule

Every setup topic (00–20), architecture document, ADR (0001–0017), Terraform module, GitOps tree, `pipelines/` YAML, `policies/` tree, security doc, test, teardown script, and operations/runbook area must appear in at least one chapter.

## Index

0. How to Use This Book
1. Charter a DevSecOps Pilot You Can Defend
2. Make Setup Guides and Versions the Contract
3. Lock Design With ADRs Before Credentials Exist
4. Bootstrap Terraform State, Network, and DNS
5. Provision AKS, ACR, Key Vault, and Workload Identity
6. Split GitHub Truth From Azure DevOps Execution
7. Bootstrap Argo CD as the Cluster Reconciler
8. Terminate TLS With Ingress and DNS-01
9. Deliver Secrets Through Key Vault and CSI
10. Mirror, Scan, and Sign Digests in CI
11. Deny Unsigned Workloads at Admission
12. Deploy Boutique With Kustomize Overlays
13. Observe Without Buying a SIEM First
14. Promote the Same Digest Through Approval
15. Destroy ACR When You Tear Down
16. Apply Phase 15+ Scaffolds Without Pretending They Lived
17. Threat-Model the Pilot and Operate Day-2 Honestly
18. Conclusion — Unsigned Must Not Land
19. Interview Questions From This Repository

## Back matter

- Glossary and Abbreviations
- References

## Topic map

| Chapter | Setup / ADR / area |
|---|---|
| 1 | README, ROADMAP, ARCHITECTURE, limitations, CONTRIBUTING hygiene |
| 2 | setup README, versions.yaml, repository layout, Makefile, pre-commit |
| 3 | ADRs 0001–0012, architecture 01–08 |
| 4 | setup 00–02, terraform bootstrap/networking/dns |
| 5 | setup 03, aks/acr/key-vault/identities modules |
| 6 | setup 04, ado-federation, pipelines/README, no GitHub Actions |
| 7 | setup 05, gitops/bootstrap, ADR-0004 |
| 8 | setup 06, ingress-nginx, cert-manager, DNS-01 |
| 9 | setup 07, CSI, secrets-management.md, examples/csi-secret-test |
| 10 | setup 09, build-scan-sign, ADRs 0005/0009, supply-chain.md |
| 11 | setup 08, policies/kyverno/cluster 00–04, ADR-0003 |
| 12 | setup 10, gitops/apps/boutique, ADR-0006 |
| 13 | setup 11, monitoring, ADR-0012, SLO doc |
| 14 | setup 12, promote pipeline, ADR-0008, rollback tests |
| 15 | setup 13, ADR-0010, teardown script, cost model |
| 16 | setup 14–20, ADRs 0013–0017, Falco, SBOM, Checkov, NetPol, DAST |
| 17 | threat-model, security architecture, operations, incident-response |

## Recurring principles

1. GitHub holds Git; Azure DevOps runs pipelines; neither gets a long-lived cloud secret.
2. Unsigned and floating tags must not reach AKS.
3. The same digest is promoted; CI does not rebuild per environment.
4. `prod` is a namespace on one cluster, not a separate production estate.
5. Destroying ACR on teardown is intentional.
6. Scaffold-complete is not live-validated.
