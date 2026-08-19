# 18. Conclusion — Unsigned Must Not Land

This book followed one repository through a lived Azure **DevSecOps (Development, Security, and Operations)** path and an honest teardown. The system was never a companion lab. It was `boutique-aks-devsecops`: GitHub for Git, **ADO (Azure DevOps)** for pipelines, **OIDC (OpenID Connect)** to Azure, digest identity, Kyverno as the last gate, Key Vault plus **CSI (Container Storage Interface)**, GitOps promotion with a prod approval, and **ACR (Azure Container Registry)** destroyed on the way out.

The unsafe default at the start of the book was a public cluster with `:latest`, a stored cloud password in CI, and a README that said production-ready. The lived default at the end is: no cluster, no registry, Git still true, screenshots still true, scaffolds still labeled scaffold.

## What this title uniquely claims

Unsigned images and `:latest` must not reach **AKS (Azure Kubernetes Service)**. That claim is not a scanner report. It is admission policy `00`–`04` plus a pipeline that signs the same digest Trivy scanned, with **cosign key-based** `--tlog-upload=false` ([ADR-0005](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0005-cosign-key-based-signing.md)). Destroying ACR ([ADR-0010](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0010-destroy-acr-on-teardown.md)) is the matching cost and trust control: leftover registries are leftover admission surfaces.

`prod` was a namespace on one cluster. The platform was not production-ready. Topics 14–20 remain scaffold.

The unique claim is the conjunction, not any single tool:

| Control | Without the others |
|---------|--------------------|
| Trivy CRITICAL | A scanned unsigned image can still be `kubectl apply`'d |
| Cosign key-based | A signature CI never verifies at the API is a report |
| Kyverno Enforce | A pipeline can be bypassed |
| Destroy ACR | Yesterday’s signed malware remains pullable |

GitHub versus ADO is the other conjunction: two platforms so that Git remains the deploy authority and CI never holds a long-lived Azure password. That split is as much the book as Kyverno.

## Sisters, different honest choices

*Practical GitOps on Amazon EKS* (`boutique-eks-gitops`) asks whether Git is the only deploy authority. Its CI is GitLab. Its cosign path is **keyless**. That is a different root of trust, not a missing feature of this book. If you copy Fulcio settings into this Kyverno policy, admission and CI stop describing the same signature.

*Practical SRE on Google Kubernetes Engine* (`boutique-gke-sre`) asks whether user-visible **SLOs (Service Level Objectives)** and PagerDuty change engineering behavior. This AKS pilot wrote a 99.5% frontend SLO and a freeze rule without a pager. That is proportionate, not incomplete SRE. Grafana plus a written freeze is what Topic 12 required; a roster was not.

The three platforms share Online Boutique, GitOps, and digest discipline. They disagree on cloud, CI host, and signing. Teaching the disagreement is the series.

## Recurring principles, restated

1. GitHub holds Git; Azure DevOps runs pipelines; neither stores a long-lived Azure secret.
2. Identity is digest, not tag. Kyverno deny-latest and `verifyDigest` are the same idea at admission.
3. CI never deploys the cluster. Promote jobs write Git; Argo CD reconciles; kubectl at bootstrap is the exception.
4. Three namespaces share one blast radius. Approval is not isolation.
5. Teardown that leaves ACR is incomplete. Destroy the images you signed.
6. Scaffold-complete is not live-validated. Falco YAML is not a DaemonSet that ran in 2026.

## What you should be able to explain

- Why `.github/workflows` is absent and why adding one would split the control plane.
- Why Kyverno `ignoreTlog` must match `--tlog-upload=false`.
- Why the same digest is copied through overlays instead of rebuilt per environment.
- Why teardown that leaves ACR is an incomplete control.
- Why Phase 15+ YAML is not evidence Falco ran.
- Why `docs/setup/` wins over README shortcuts, and why `versions.yaml` wins over a remembered CLI version.
- Why screenshots in `assets/images/setup/` are storefront evidence while `biroltilki.art` is inactive.

## What the lived path proved

Topics 00–13 proved, on a real `germanywestcentral` cluster that was then destroyed:

- Remote Terraform state, VNet, DNS, AKS, ACR, Key Vault, and Workload Identity
- ADO OIDC without a long-lived cloud secret
- Argo CD from GitHub, TLS via DNS-01, CSI mount proof
- Mirror → Trivy CRITICAL → key-based cosign → Kyverno deny of unsigned / `:latest`
- Boutique on `boutique-dev`, then the same digest to stage/prod with ADO approval
- Loki/Grafana without Log Analytics, then teardown that included ACR

Topics 14–20 proved only that the files exist. That is still worth teaching. It is not a second lived milestone.

## How to continue

If you rebuild, start at `docs/setup/00-prerequisites.md` and stop at Topic 12 before you apply any scaffold. Expect the cost model’s monthly band while nodes are up. Run Topic 09 before Boutique, or Kyverno will deny you. When you are finished, Topic 13 destroys AKS and ACR; keep Git and the public PEM.

If you only read, keep the clone and the screenshot catalog. Practice boxes asked you to open paths, not to spend money.

If you write about this platform, use **production pilot**, **lived / scaffold / inactive**, and never “enterprise HA.”

The next sentence of the series is optional: GitOps on EKS for deploy authority, or SRE on GKE for error budgets. This book’s sentence is already complete: **unsigned must not land, and ACR must not outlive the cluster.**

Durable outputs of the whole manuscript are the repository itself: ADRs 0001–0017, setup Topics 00–20, `pipelines/`, `policies/`, `gitops/`, `terraform/`, operations, runbooks, tests, and screenshots. The book does not add a lab. It teaches you to read that tree without inflating it.

Unsigned must not land. `:latest` must not land. ACR must not outlive the cluster. GitHub Actions must not appear. `prod` is a namespace. Scaffold is scaffold. That is the whole claim.

Rehearse it with [19-interview-questions-from-this-repository.md](19-interview-questions-from-this-repository.md). Ten questions; answers cite these files. Keep public-share hygiene.
