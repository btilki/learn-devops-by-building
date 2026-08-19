# References

All primary evidence is the repository. Prefer the path in the clone over a remembered blog post.

## System under study

- Repository: https://github.com/btilki/boutique-aks-devsecops
- Online Boutique v0.10.5: https://github.com/GoogleCloudPlatform/microservices-demo/releases/tag/v0.10.5
- Upstream images: `us-central1-docker.pkg.dev/google-samples/microservices-demo`

## Sister platforms and series

- Boutique Production Series: `../BOUTIQUE-SERIES.md`
- Editorial conventions: `../BOUTIQUE-EDITORIAL-CONVENTIONS.md`
- *Practical GitOps on Amazon EKS* — https://github.com/btilki/boutique-eks-gitops (keyless cosign, GitLab CI)
- *Practical SRE on Google Kubernetes Engine* — https://github.com/btilki/boutique-gke-sre (SLOs, PagerDuty)
- Playbook hub: https://github.com/btilki/devops-engineering-playbook
- Featured brief: https://github.com/btilki/devops-engineering-playbook/blob/main/featured-projects/boutique-aks-devsecops.md
- Article A1 — GitHub + Azure DevOps on AKS: https://github.com/btilki/devops-engineering-playbook/blob/main/articles/A1.md
- Article A2 — Kyverno + Cosign unsigned deny: https://github.com/btilki/devops-engineering-playbook/blob/main/articles/A2.md
- Article A3 — Destroy ACR on teardown: https://github.com/btilki/devops-engineering-playbook/blob/main/articles/A3.md

## Companion books (reference, not replacements)

- Adkins, Beyer, Blankinship, Oprea, Lewandowski, Stubblefield, *Building Secure and Reliable Systems* — lifecycle security and reliability as background.
- Do not replace this repository’s ADRs, Kyverno policies, or ACR-destroy decision with a textbook chapter.

## Repository documents cited across chapters

### Charter and contract

- `README.md` — limitations, CI story, hostnames
- `ROADMAP.md` — lived 00–13 vs scaffold 14–20
- `ARCHITECTURE.md` — executive architecture
- `CONTRIBUTING.md` — public-share hygiene, no GitHub Actions
- `SECURITY.md` — secrets and supply-chain policy
- `CHANGELOG.md` — notable changes
- `versions.yaml` — pins
- `docs/setup/README.md` — topic catalog (authority)
- `docs/architecture/09-repository-layout.md`
- `Makefile`, `.pre-commit-config.yaml`
- `docs/setup/00-prerequisites.md`

### ADRs 0001–0017

- `docs/adr/README.md`
- `docs/adr/0001-azure-cloud-provider.md`
- `docs/adr/0002-single-cluster-multi-namespace.md`
- `docs/adr/0003-kyverno-admission.md`
- `docs/adr/0004-argocd-gitops.md`
- `docs/adr/0005-cosign-key-based-signing.md`
- `docs/adr/0006-kustomize-boutique.md`
- `docs/adr/0007-no-service-mesh.md`
- `docs/adr/0008-ado-prod-approval-gate.md`
- `docs/adr/0009-mirror-upstream-images.md`
- `docs/adr/0010-destroy-acr-on-teardown.md`
- `docs/adr/0011-aks-node-vm-sku.md`
- `docs/adr/0012-loki-in-cluster-logging.md`
- `docs/adr/0013-scaffold-first-phase15.md`
- `docs/adr/0014-sbom-cosign-attestations.md`
- `docs/adr/0015-falco-runtime-detection.md`
- `docs/adr/0016-namespace-kv-hardening.md`
- `docs/adr/0017-optional-zap-dast.md`

### Architecture 01–11

- `docs/architecture/README.md`
- `docs/architecture/01-requirements.md`
- `docs/architecture/02-system-context.md`
- `docs/architecture/03-component-design.md`
- `docs/architecture/04-data-flows.md`
- `docs/architecture/05-deployment-flow.md`
- `docs/architecture/06-network-design.md`
- `docs/architecture/07-security-architecture.md`
- `docs/architecture/08-resilience-and-dr.md`
- `docs/architecture/10-observability.md`
- `docs/architecture/11-cost-model.md`

### Setup Topics 00–20

- `docs/setup/00-prerequisites.md` through `docs/setup/20-dast.md`
- `docs/implementation/plan.md`
- `docs/implementation/phase15-plus.md`

### Terraform

- `terraform/README.md`
- `terraform/bootstrap/`
- `terraform/environments/dev/`
- `terraform/modules/resource-group/`, `networking/`, `dns/`, `aks/`, `acr/`, `key-vault/`, `identities/`, `ado-federation/`, `diagnostics/` (unwired)

### GitOps, policies, pipelines

- `gitops/bootstrap/`, `gitops/projects/`, `gitops/platform/`, `gitops/apps/boutique/`
- `policies/kyverno/cluster/00`–`05`, `policies/tests/`
- `pipelines/README.md`, `azure-pipelines.yml`, `azure-pipelines-promote.yml`, `azure-pipelines-pr.yml`, `azure-pipelines-dast.yml`
- `pipelines/templates/build-scan-sign.yml`, `promote-digest.yml`, `pr-validate.yml`, `dast-zap.yml`

### Security, operations, tests, scripts

- `docs/security/threat-model.md`
- `docs/security/secrets-management.md`
- `docs/security/supply-chain.md`
- `docs/slo/boutique-availability.md`
- `docs/operations/README.md` and sections 01–20
- `docs/runbooks/teardown.md`, `promotion-rollback.md`, `incident-response.md`
- `docs/troubleshooting/` (ADO OIDC, Argo CD, DNS-01, Kyverno, pipelines, promotion, monitoring)
- `scripts/verify-oidc-trust.sh`, `scripts/operations/teardown.sh`, `scripts/register-ado-sc-federation.sh`, `scripts/bootstrap-tf-backend.sh`
- `tests/README.md`, `tests/ci/`, `tests/terraform/`, `tests/integration/`
- `examples/csi-secret-test/README.md`
- `assets/images/README.md` and `assets/images/setup/`

## External specifications (tools as used)

- Sigstore Cosign: https://docs.sigstore.dev/cosign/overview/
- Kyverno `verifyImages`: https://kyverno.io/docs/writing-policies/verify-images/
- Trivy: https://trivy.dev/
- Argo CD app-of-apps: https://argo-cd.readthedocs.io/
- Azure Workload Identity federation for ADO: https://learn.microsoft.com/azure/devops/pipelines/library/connect-to-azure
- Let's Encrypt ACME DNS-01: https://letsencrypt.org/docs/challenge-types/
- Checkov: https://www.checkov.io/
- SPDX: https://spdx.dev/
- Falco: https://falco.org/
- OWASP ZAP: https://www.zaproxy.org/
