# 6. Split GitHub Truth From Azure DevOps Execution

A GitHub Action that deploys to AKS with a stored **SP (service principal)** secret is the usual Azure tutorial. This repository forbids that pattern. GitHub is the Git remote. **ADO (Azure DevOps)** is the only pipeline runner. Federation is **OIDC (OpenID Connect)**. There is no `.github/workflows` tree.

The production question is:

> How do you give CI permission to push images and read signing keys without putting a cloud password in either GitHub or Azure DevOps?

## 1. Unsafe starting state

The unsafe default is a client secret in ADO variable groups, a PAT in GitHub Actions, or “temporary” Azure Repos because the pipeline UI offered it. Secrets outlive the engineer. GitHub Actions then becomes a second CI with no Trivy gate.

`CONTRIBUTING.md` is explicit: **GitHub Actions — Not used — do not add empty `.github/workflows`**. `pipelines/README.md` repeats the CI story. A search of the lived repo for `.github/workflows` returns nothing. That absence is the teaching point.

## 2. The production model: two platforms, one federated identity

> *Theory — Split control planes*
>
> This model enables Git to remain the deploy authority while CI authenticates to Azure with a short-lived token bound to a named service connection.

Roles:

| Concern | System |
|---------|--------|
| Desired state, PRs, Argo CD `repoURL` | GitHub |
| Mirror, scan, sign, promote jobs | Azure DevOps `pipelines/` |
| Azure authentication | Federated credential on pipeline **UAMI (user-assigned managed identity)** |

CI never `kubectl apply` Boutique. It may commit digest pins to GitHub; Argo CD pulls. That is [ADR-0004](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0004-argocd-gitops.md) plus this chapter's identity.

## 3. How this repository implements Topic 04

> **Practice — Read the federation module**
>
> Open `docs/setup/04-ado-oidc.md` and `terraform/modules/ado-federation/main.tf`.

The module creates `azurerm_user_assigned_identity.pipeline` and `azurerm_federated_identity_credential.ado`:

```hcl
issuer = "https://login.microsoftonline.com/${local.tenant_id}/v2.0"
subject = coalesce(
  var.federation_subject,
  "sc://${var.ado_organization_name}/${var.ado_project_name}/${var.service_connection_name}"
)
audience = ["api://AzureADTokenExchange"]
```

Comments in the module record the 2025+ Entra issuer. Legacy `https://vstoken.dev.azure.com/{org-id}` is deprecated (retired 2027). `docs/troubleshooting/ado-oidc.md` maps `AADSTS700211` to issuer mismatch and `AADSTS700213` to subject mismatch.

RBAC on that UAMI is narrow:

- `AcrPush` on ACR
- `Key Vault Secrets User` on the vault (cosign private key in Topic 09)

It does not get Contributor on the subscription. It does not get AKS admin. That is how CI is prevented from becoming the cluster's second control plane.

> **Practice — Verify without guessing the subject**
>
> Open `scripts/verify-oidc-trust.sh` and `pipelines/README.md`.

The verify script reads Terraform outputs (`ado_pipeline_identity_client_id`, `ado_oidc_issuer`, `ado_oidc_subject`, `ado_service_connection_name`), lists the federated credential, and greps role assignments for AcrPush and Key Vault Secrets User. It then tells the operator to run a test ADO job with `az account show`. Mechanism evidence is Azure-side; outcome evidence is a green job that can see the subscription **without** a stored secret.

`scripts/register-ado-sc-federation.sh` helps the GUI service-connection step. Topic 04 still requires the ADO ARM service connection named to match Terraform — default `azure-boutique-oidc`. A typo here is the entire outage mode.

`pipelines/README.md` lists YAML that Topic 04 does not yet run: `azure-pipelines.yml` (Topic 09), promote (Topic 12), PR validate (Topic 14 scaffold), DAST (Topic 20 scaffold). Registering the wrong YAML as the OIDC test will try to mirror images before keys exist.

`pipelines/templates/variables.yml` already names the connection:

```yaml
azureServiceConnection: azure-boutique-oidc
azureRegion: germanywestcentral
acrName: acrboutiquedevgwc
```

Those strings must match Terraform outputs and the ADO GUI. Topic 04’s job is identity, not yet mirroring. A test pipeline that only runs `az account show` is enough mechanism evidence.

`tests/README.md` is blunt: **There is no GitHub Actions CI for this repo.** Local P0 is pre-commit, terraform validate, checkov, kyverno test. ADO is TEST-007 for supply chain on `main`. Do not add an Actions workflow to satisfy a GitHub branch-protection checkbox; use ADO status checks or accept GitHub-side protection without Actions.

ADO still needs a GitHub service connection or PAT with **push** for Topic 12 digest commits. That PAT is GitHub-scoped, not Azure. Prefer app installation / fine-grained push over a classic PAT in a wiki. Never put it in the Git repo.

## Lived operator commands (Topic 04)

```bash
cd terraform/environments/dev
terraform output -raw ado_oidc_issuer
terraform output -raw ado_oidc_subject
./scripts/verify-oidc-trust.sh
```

Expected issuer: `https://login.microsoftonline.com/{tenant-id}/v2.0`. Expected subject: `sc://{org}/{project}/azure-boutique-oidc` unless you overrode `federation_subject`. Then create the ADO ARM service connection (Workload Identity federation) with **the same name** and run a job whose only step is `az account show`.

Do not run `azure-pipelines.yml` as the OIDC smoke test — it will try to mirror images and fetch a cosign key that does not exist yet.

## Limits of this chapter

OIDC success is `az account show` from an ADO job using the federated connection. It is not a mirrored image. Topic 09 is the first consumer of AcrPush and Key Vault Secrets User. If you grant extra roles “to finish later,” you have already broken least privilege.

GitHub Actions remains absent. Branch protection on GitHub can require a human review; it cannot replace ADO as the runner without creating a second CI.

## 4. Test the design under failure

### Independent control failure — Service connection renamed in the GUI

> **Practice — Diagnose AADSTS700213**
>
> Someone “cleans up” the ADO service connection name to `Azure-Prod-OIDC`. Terraform still federates `sc://org/project/azure-boutique-oidc`. The first Topic 09 job fails token exchange.

**Severity:** high; CI cannot push or sign; temptation to paste a client secret “just for today.”  
**Plausible harm:** long-lived SP created to unblock; secret committed to a variable group; GitHub Actions added as a workaround.  
**Potential blast radius:** ACR write and Key Vault read if a broader identity is substituted; cluster still not directly deployed by CI unless someone also grants AKS rights.  
**Bounded by:** federated subject lock, verify script, troubleshooting guide, CONTRIBUTING ban on Actions.  
**Primary principles:** explicit contracts, CI never deploys the cluster, trustworthy evidence, recovery.

#### Diagnosis

OIDC fails closed when subject ≠ service connection. That is success. The failure is the operational response: adding a secret instead of aligning names.

#### Correction

Rename the service connection back, or set `federation_subject` / tfvars to the new `sc://` path and `terraform apply`. Re-run `scripts/verify-oidc-trust.sh`. Do not create `.github/workflows/mirror.yml`.

Issuer mismatch (`AADSTS700211`) is the other lived class: federated credential still on `vstoken.dev.azure.com` while ADO issues Entra tokens. Re-apply `module.ado_federation` per the troubleshooting table.

## Production reality

**Best Practice:** federated identity with an exact subject and a least-privilege UAMI.

**Production Practice:** Entra issuer `login.microsoftonline.com/{tenant}/v2.0` is required for new ADO connections. If you restore a 2024 screenshot that shows `vstoken.dev.azure.com`, you will debug the wrong year. RBAC propagation 1–5 minutes is called out in the verify script — retry before widening roles.

GitHub remains the Argo CD `repoURL`. ADO checkout of GitHub is not a second source of truth.

### Common errors

- Creating the ARM service connection as a secret-based SP because the OIDC checkbox was skipped.
- Binding federation to `ref:refs/heads/main` on GitHub Actions documentation and wondering why ADO subjects look like `sc://`.
- Giving the pipeline UAMI `Azure Kubernetes Service Cluster Admin` “for kubectl in CI.”

## 5. What You Learned

GitHub is source of truth. Azure DevOps executes `pipelines/`. Federation binds an Entra-issued token to a UAMI with AcrPush and Key Vault Secrets User. No GitHub Actions, no long-lived pipeline secret, no Azure Repos requirement. Topic 09 will use this connection; Topic 14's PR pipeline will deliberately **not** need it.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Topic 04 guide | `docs/setup/04-ado-oidc.md` | GUI + Terraform order |
| Federation module | `terraform/modules/ado-federation/` | Issuer, subject, RBAC |
| Verify script | `scripts/verify-oidc-trust.sh` | Independent Azure-side check |
| Pipeline index | `pipelines/README.md` | CI story and YAML map |
| OIDC troubleshooting | `docs/troubleshooting/ado-oidc.md` | AADSTS700211/700213 |
| Hygiene | `CONTRIBUTING.md` | Forbids `.github/workflows` |

## What changed

| Before | After |
|--------|--------|
| Client secret in ADO. | **Federated credential on pipeline UAMI.** |
| GitHub Actions “for CI.” | **No `.github/workflows`; YAML in `pipelines/`.** |
| Azure Repos as Git. | **GitHub `repoURL` for Argo and digest commits.** |

`docs/troubleshooting/ado-oidc.md` is required reading the first time `AADSTS700213` appears. `scripts/register-ado-sc-federation.sh` helps the GUI; it does not replace matching `ado_service_connection_name` in tfvars. Pipeline identity has AcrPush, not cluster admin — Chapter 7’s Argo CD remains the applier.

> **Independent Practice — Draw the trust triangle**
>
> On one page, draw GitHub, ADO, and Entra/UAMI. Label what each stores (Git vs job definition vs federated credential). Mark the one arrow that must never appear: GitHub Actions → `az aks get-credentials` with a stored secret.

## Further reading

Playbook article **A1** is the short public argument for GitHub as Git and Azure DevOps as CI.

https://github.com/btilki/devops-engineering-playbook/blob/main/articles/A1.md
