# 2. Make Setup Guides and Versions the Contract

A repository with three places that disagree about Kubernetes version, chart pins, or topic order will be implemented incorrectly under time pressure. Chat notes and README shortcuts lose. This chapter makes `docs/setup/`, `versions.yaml`, and the repository layout the only contract for rebuild.

The production question is:

> When README, a script, and a setup topic disagree, which file wins, and how do pinned versions keep a torn-down platform reproducible?

## 1. Unsafe starting state

The unsafe default is tribal knowledge: “AKS 1.29 is fine,” “use latest Helm,” “skip Topic 08 until the app is up.” After teardown, that knowledge is gone. A rebuild with floating versions produces a different admission stack, a different cosign CLI, and a Kyverno `verifyImages` path that no longer matches [ADR-0005](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0005-cosign-key-based-signing.md).

`docs/setup/README.md` states the authority rule in one line: if README, chat, or scripts conflict with this directory, **`docs/setup/` wins**.

## 2. The production model: one catalog, one pin file, one layout

> *Theory — Setup-as-contract*
>
> This model enables a rebuild to follow the same topic order and version pins the lived pilot used, without rediscovering SKUs, chart versions, or CI split from memory.

Three artifacts form the contract:

1. **Topic catalog** — `docs/setup/README.md` sequences Topics 00–20, names prerequisites, and labels lived versus scaffold.
2. **Version pins** — `versions.yaml` is the single source for region, node SKUs, charts, Trivy, cosign, Boutique tag, and CI tool versions.
3. **Layout** — `docs/architecture/09-repository-layout.md` assigns each top-level directory a domain so Terraform does not grow GitOps files and pipelines do not grow Kubernetes YAML.

Local gates (`Makefile`, `.pre-commit-config.yaml`) enforce the contract before ADO ever runs.

## 3. How this repository implements the contract

> **Practice — Walk the topic catalog**
>
> Open `docs/setup/README.md` and separate Topics 00–13 from Topics 14–20 before you read a module.

### Topic sequence (lived)

| # | Topic | Guide | Status |
|---|-------|-------|--------|
| 00 | Prerequisites | `00-prerequisites.md` | Lived |
| 01 | Terraform bootstrap | `01-terraform-bootstrap.md` | Lived |
| 02 | Azure foundation | `02-azure-foundation.md` | Lived |
| 03 | Cluster resources | `03-cluster-resources.md` | Lived |
| 04 | ADO OIDC | `04-ado-oidc.md` | Lived |
| 05 | GitOps bootstrap | `05-gitops-bootstrap.md` | Lived |
| 06 | Ingress + TLS | `06-ingress-tls.md` | Lived |
| 07 | Secrets Store CSI | `07-secrets-csi.md` | Lived |
| 08 | Admission policies | `08-admission-policies.md` | Lived |
| 09 | CI pipeline | `09-ci-pipeline.md` | Lived |
| 10 | Boutique dev | `10-boutique-dev.md` | Lived |
| 11 | Observability | `11-observability.md` | Lived |
| 12 | Promotion | `12-promotion-stage-prod.md` | Lived |
| 13 | Teardown | `13-teardown.md` | Lived |

The catalog records a dependency chain: `00 → 01 → 02 → 03 → 04 → 05 → 06 → 07` and `03 → 09 → 08 → 10 → 11 → 12 → 13`. Topic 08 can install Kyverno before signatures exist; signature verification is validated after Topic 09 produces signed digests. That footnote is part of the contract, not a skip.

Topics 14–20 are listed as **scaffold → apply later**. Their live apply depends on Topics 00–12 being live again. Teardown remains Topic 13 when destroying a rebuild.

Estimated cost in the catalog is ~€150–250/month while AKS is up. Topic 13 is the cost stop.

> **Practice — Treat versions.yaml as the pin file**
>
> Open `versions.yaml` and list the pins a rebuild must not invent.

```yaml
azure:
  region: germanywestcentral

aks:
  kubernetes_version: "1.34"
  node_pools:
    system:
      vm_size: Standard_D2s_v6
    user:
      vm_size: Standard_D4s_v6

supply_chain:
  trivy: "0.72.0"
  cosign: "2.2.4"
  cosign_sign_args:
    - "--tlog-upload=false"

applications:
  online_boutique:
    version: "v0.10.5"
```

GitOps pins in the same file include Argo CD `2.10.7`, NGINX Ingress chart `4.10.1`, cert-manager `1.14.5`, Kyverno `1.12.6`, CSI driver `1.4.0`, kube-prometheus-stack `58.2.2`, Loki `6.23.0`. **CI (Continuous Integration)** pins include Terraform `1.9.8`, Kyverno CLI `1.12.6`, Checkov `3.2.510`. Hostnames under `dns.zone_name: biroltilki.art` match the README table.

`environments.argocd_sync` records automatic for dev and manual for stage/prod, with `prod_promotion_gate: ado_environment_approval`. That is the promotion contract Chapter 14 will enforce; it is already pinned here.

### Repository layout

`docs/architecture/09-repository-layout.md` assigns domains:

| Directory | Domain |
|-----------|--------|
| `terraform/` | Cloud provisioning (Azure) |
| `gitops/` | Declarative cluster state (Argo CD) |
| `policies/` | Admission enforcement (Kyverno) |
| `pipelines/` | **CI/CD (Continuous Integration and Continuous Delivery)** (Azure DevOps) |
| `docs/` | Architecture, setup, security, operations |
| `scripts/` | Guarded operational helpers |
| `tests/` | Validation and smoke tests |
| `examples/` | Isolated demos |

Promotion is three different mechanisms: Terraform has a single physical root `terraform/environments/dev/`; Kubernetes has Kustomize overlays `gitops/apps/boutique/overlays/{dev,stage,prod}`; images are digest-promoted via `pipelines/` into Git. Mixing those three is how people “promote” by rebuilding.

Timing tags (`SETUP_REQUIRED`, `FEATURE_REQUIRED`, `RELEASE_REQUIRED`) tell authors when a file must exist relative to a setup topic. They are not chapter numbers.

> **Practice — Run the local contract**
>
> Open `Makefile` and `.pre-commit-config.yaml` and state what they prove without Azure.

`Makefile` exposes `pre-commit`, `checkov`, `pr-validate`, and `dast-help`. The first three can run on a laptop. `dast-help` prints a live-URL reminder; **DAST (Dynamic Application Security Testing)** is scaffold (Topic 20).

`.pre-commit-config.yaml` runs trailing-whitespace, YAML checks (excluding the huge Boutique `manifests.yaml` and vendored Argo charts), Terraform `fmt` and `validate` on `terraform/(bootstrap|environments)/`, yamllint on `gitops|policies|pipelines`, and gitleaks. That is the local substitute for “GitHub Actions lint.” `tests/README.md` repeats: there is **no GitHub Actions** CI.

Topic 00 (`docs/setup/00-prerequisites.md`) is the workstation half of the contract: Azure CLI login, SKU availability for Dsv6 in `germanywestcentral`, GitHub as the sole Git remote, ADO for pipelines only. Re-run its validation after a laptop change; do not use it as a day-2 runbook.

Troubleshooting indexes in `docs/setup/README.md` §4 point at `docs/troubleshooting/` for OIDC, Argo CD, DNS-01, signatures, Kyverno, pipelines, promotion, and monitoring. Those guides are authored with the topics; they are not a second setup path. Placeholder legend in §3 is the other half of the contract: `<ADO_ORG>` is not a Git remote.

`docs/implementation/plan.md` is the long implementation plan. Setup topics are the operator-facing slice. If they conflict, setup still wins for commands; the plan wins for phase intent — and that tension is why ADRs exist (Chapter 3).

Live implementation protocol in the catalog (STATE → FILE CHECK → INSTRUCT → VALIDATE → WAIT) is how the lived pilot was executed: one step per turn, no skip-ahead, no bypass scripts. The book’s Practice boxes are the reading analogue: open the file, do not invent a Makefile target.

## 4. Test the design under failure

### Independent control failure — Pin drift between setup and pipeline

> **Practice — Diagnose a silent version fork**
>
> A rebuild hardcodes Trivy `0.51.4` in a setup checklist while `versions.yaml` and `pipelines/templates/variables.yml` pin `0.72.0`. Decide which file is wrong and what harm the mismatch causes.

**Severity:** medium; unreproducible supply-chain gate.  
**Plausible harm:** CRITICAL findings differ between laptop and ADO; Kyverno or cosign CLI flags diverge from [ADR-0005](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0005-cosign-key-based-signing.md); “it worked on my machine” after teardown.  
**Potential blast radius:** every mirrored image in a rebuild; admission policy that expects a different signature payload.  
**Bounded by:** `versions.yaml` as SSOT, setup topics that must reference it, pre-commit on composed Terraform roots.  
**Primary principles:** explicit contracts, trustworthy evidence, lived evidence beats scaffold.

#### Diagnosis

The setup catalog says topics reference `versions.yaml` and must not hardcode divergent versions. A leftover `0.51.4` in a checklist is a documentation defect, not a second pin. Pipelines consume `templates/variables.yml`; that file must stay aligned with `versions.yaml`.

#### Correction

Change the checklist. Do not change the pipeline to match a stale sentence. If you bump cosign, bump `versions.yaml`, pipeline templates, and Kyverno compatibility notes in the same change — and record whether `--tlog-upload=false` still holds.

## Production reality

**Best Practice:** one pin file referenced by pipelines, Terraform docs, and setup.

**Production Practice:** when `pipelines/templates/variables.yml` and `versions.yaml` diverge, CI is the runtime pin and the YAML file is a bug. Topic 09’s checklist once mentioned Trivy `0.51.4` while `versions.yaml` pins `0.72.0`. Believe the pin file; file a doc fix. Do not run two scanners and pick the greener one.

`environments.prod_promotion_gate: ado_environment_approval` in `versions.yaml` is a contract Chapter 14 must not replace with CODEOWNERS “for GitHub-nativeness.” GitHub does not run these pipelines.

Hostnames in `versions.yaml` match README. After teardown they are documentation, not liveness probes.

### Common errors

- Hardcoding chart versions in a Helm Application while `versions.yaml` stays stale.
- Running `terraform validate` on leaf modules only; pre-commit validates `bootstrap` and `environments` roots.
- Using Azure Cloud Shell as the long-term workstation (Topic 00 prefers a real machine with pre-commit).

## 5. What You Learned

`docs/setup/` is the implementation authority. `versions.yaml` is the pin file. Layout keeps Terraform, GitOps, policies, and pipelines from absorbing each other. Pre-commit and `make pr-validate` are the local CI the repo chose instead of GitHub Actions.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Setup catalog | `docs/setup/README.md` | Topic order, lived vs scaffold, cost |
| Version pins | `versions.yaml` | Region, SKUs, charts, Trivy, cosign, Boutique |
| Layout | `docs/architecture/09-repository-layout.md` | Domain boundaries |
| Local gates | `Makefile`, `.pre-commit-config.yaml` | Reproducible checks without Azure |
| Prerequisites | `docs/setup/00-prerequisites.md` | Workstation and GitHub-remote contract |

## What changed

| Before | After |
|--------|--------|
| Version pins lived in chat. | **`versions.yaml` is the pin file.** |
| Topic order was tribal. | **`docs/setup/` wins, including lived vs scaffold.** |
| GitHub Actions was assumed. | **Pre-commit and `make pr-validate` are local CI.** |

> **Independent Practice — Propose a version bump**
>
> You want Kyverno 1.13. List every file that must change besides `versions.yaml`. State whether ADR-0005 (key-based cosign, `ignoreTlog`) still holds. Do not apply Azure.
