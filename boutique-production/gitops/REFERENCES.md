# References

## Principles and products

- [OpenGitOps principles](https://opengitops.dev/) — declarative, versioned, pulled, continuously reconciled desired state.
- [Argo CD documentation](https://argo-cd.readthedocs.io/) — pull reconciler, ApplicationSets, sync waves, manual sync.
- [Argo Rollouts](https://argo-rollouts.readthedocs.io/) — canary, ALB traffic splitting, AnalysisTemplates.
- [Kyverno](https://kyverno.io/) — admission policies, `verifyImages`, Audit vs Enforce.
- [Sigstore / cosign](https://docs.sigstore.dev/) — keyless signing, Fulcio, Rekor.
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/) — ALB Ingress, ACM annotations, target-type IP.
- [External Secrets Operator](https://external-secrets.io/) — Secrets Manager / SSM to Kubernetes Secrets.
- [external-dns](https://github.com/kubernetes-sigs/external-dns) — Ingress to Route53.
- [cert-manager](https://cert-manager.io/) — installed, not primary public TLS in this pilot (ADR-0003).
- [Terraform](https://www.terraform.io/) — AWS foundation and remote state.
- [Amazon EKS](https://aws.amazon.com/eks/) — managed Kubernetes 1.31 pin.
- [Trivy](https://trivy.dev/) — CRITICAL gate pin 0.71.0.
- [Checkov](https://www.checkov.io/) — Terraform IaC scan (Topic 16 scaffold).
- [Gitleaks](https://github.com/gitleaks/gitleaks) — secret scan.
- [Falco](https://falco.org/) — runtime detection (Topic 19 scaffold).
- [AWS WAFv2](https://docs.aws.amazon.com/waf/) — optional regional Web ACL (Topic 19 scaffold).
- [Google Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) — upstream application inspiration (v0.10.6).

## Source repository (system under study)

Public clone: [https://github.com/btilki/boutique-eks-gitops](https://github.com/btilki/boutique-eks-gitops)

Primary docs cited in this book:

- `README.md` — charter, honesty labels, teardown status
- `ROADMAP.md` — phases, M1–M4, Phase 12 scaffold
- `docs/ARCHITECTURE.md` — executive design
- `docs/architecture/01-requirements.md` … `10-cost-model.md`
- `docs/adr/0001-digest-only-gitops.md` … `0010-edge-waf-and-falco.md`
- `docs/setup/01-prerequisites.md` … `19-edge-runtime-waf-falco.md`
- `docs/ci.md`, `docs/promotion.md`, `docs/rollback.md`, `docs/versions.md`
- `docs/PRODUCTION_CHECKLIST.md` — M3 evidence, Appendix T (M4)
- `docs/runbooks/` — alerting, ingress, argo-sync, kyverno, canary, teardown
- `docs/operations/01-overview.md` … `20-automation-opportunities.md`
- `SECURITY.md`
- `CHANGELOG.md` — rebuild and post-pilot delta
- `gitops/README.md`

## Playbook (further reading, not a second source of truth)

- Hub: [devops-engineering-playbook](https://github.com/btilki/devops-engineering-playbook)
- Featured brief: [featured-projects/boutique-eks-gitops.md](https://github.com/btilki/devops-engineering-playbook/blob/main/featured-projects/boutique-eks-gitops.md)
- [E1 — Digest-only GitOps](https://github.com/btilki/devops-engineering-playbook/blob/main/articles/E1.md)
- [E2 — Argo Rollouts canary](https://github.com/btilki/devops-engineering-playbook/blob/main/articles/E2.md)
- [E3 — Cost-honest EKS](https://github.com/btilki/devops-engineering-playbook/blob/main/articles/E3.md)

## Companion books (reference, not replacements)

- OpenGitOps principles — already listed above.
- Burns, Villalba, Welliver, et al., *Kubernetes Best Practices*, 2nd ed. — RBAC, networking, GitOps, governance as background.
- Barrett, Chen, et al., *Cloud Native DevOps with Kubernetes* — cluster operations as background.
- Do not replace this repository’s ADRs with a textbook chapter.

## Lived screenshots (inactive)

- `assets/images/setup/06-argocd-applications-dashboard.png`
- `assets/images/setup/08-grafana-dashboards.png`
- `assets/images/setup/09-boutique-dev-homepage.png`
- `assets/images/setup/10-gitlab-ci-pipeline-passed.png`
- `assets/images/setup/11-boutique-stage-homepage.png`
- `assets/images/setup/13-boutique-prod-homepage.png`

## Series

- Boutique Production Series: `../BOUTIQUE-SERIES.md`
- Editorial conventions: `../BOUTIQUE-EDITORIAL-CONVENTIONS.md`
- Sister manuscripts: `../gke-sre/`, `../aks-devsecops/`
- Sister repositories: [boutique-gke-sre](https://github.com/btilki/boutique-gke-sre), [boutique-aks-devsecops](https://github.com/btilki/boutique-aks-devsecops)
