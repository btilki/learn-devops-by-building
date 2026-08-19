# 5. Provision AKS, ACR, Key Vault, and Workload Identity

GitOps, signing, and admission assume a cluster, a private registry, a secret store, and identities that do not use long-lived passwords. This chapter is Setup Topic **03**: `terraform/modules/aks`, `acr`, `key-vault`, and `identities`.

The production question is:

> How do you create the Azure control plane so kubelet can pull, workloads can read Key Vault, and pipelines can later federate — without Log Analytics and without calling the result production-ready?

## 1. Unsafe starting state

The unsafe default is a public **ACR (Azure Container Registry)** with admin user enabled, a cluster without **WI (Workload Identity)**, and Container Insights “because Azure recommended it.” Admin keys become CI secrets. Workload Identity cannot be added cheaply later. Log Analytics then costs more than the nodes ([ADR-0012](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0012-loki-in-cluster-logging.md)).

The other default is to treat Topic 03 as “the production cluster.” It is the only cluster. Namespaces come later. Blast radius is already the whole node pool.

## 2. The production model: one cluster, three identities, no OMS by default

> *Theory — Identity-first cluster*
>
> This model enables every later secret and registry operation to use short-lived Azure identities instead of static keys.

Topic 03 must produce:

- **AKS (Azure Kubernetes Service)** with OIDC issuer and WI enabled, Entra **RBAC (role-based access control)**, Azure CNI, system + user pools.
- ACR with `admin_enabled = false`.
- Key Vault with RBAC authorization, short soft-delete, purge protection off for cheap teardown.
- Platform **UAMI (user-assigned managed identity)** with AcrPull on kubelet, Key Vault Secrets User, DNS Zone Contributor for cert-manager.

Pipeline identity waits for Topic 04. Do not create a service principal secret “to test docker push.”

## 3. How this repository implements Topic 03

> **Practice — Read the AKS module against ADR-0011**
>
> Open `docs/setup/03-cluster-resources.md` and `terraform/modules/aks/main.tf`.

The cluster resource sets the identity and network profile the rest of the book needs:

```hcl
oidc_issuer_enabled       = true
workload_identity_enabled = true

network_profile {
  network_plugin    = "azure"
  network_policy    = var.network_policy
  load_balancer_sku = "standard"
  outbound_type     = "loadBalancer"
}
```

System pool uses `only_critical_addons_enabled = true` so Boutique does not land on the small system node. User pool autoscales 1–3 × `Standard_D4s_v6`. `oms_agent` is a dynamic block that only renders when `log_analytics_workspace_id != null`. The lived `environments/dev/main.tf` passes `null` into ACR, Key Vault, and AKS diagnostic arguments.

`lifecycle.ignore_changes` includes `microsoft_defender` so subscription-level Defender does not fight Terraform — Topic 18 documents Defender as opt-in, not default.

Lived SKU evidence is in [ADR-0011](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0011-aks-node-vm-sku.md): DSv5 family quota was 0 in this subscription; Dsv6 quota was 10. `versions.yaml` and the module defaults follow that apply, not the original Dsv5 sketch.

> **Practice — Read ACR, Key Vault, and identities**
>
> Open `terraform/modules/acr/main.tf`, `terraform/modules/key-vault/main.tf`, and `terraform/modules/identities/main.tf`.

ACR:

```hcl
resource "azurerm_container_registry" "this" {
  sku           = var.sku
  admin_enabled = false
}
```

Diagnostic settings on ACR and Key Vault are `count = var.log_analytics_workspace_id == null ? 0 : 1`. Default test path: no workspace, no diagnostic sink.

Key Vault uses `enable_rbac_authorization = true`, `soft_delete_retention_days = 7`, `purge_protection_enabled = var.purge_protection_enabled` (false on the pilot teardown path). `network_acls` default Allow keeps CSI and ADO working; Topic 19 may flip Deny plus subnet allow-list using the Key Vault service endpoint already on the AKS subnet.

Identities module:

- `azurerm_user_assigned_identity.platform` (`uami-boutique-platform` in examples)
- kubelet `AcrPull` on ACR
- platform `Key Vault Secrets User`
- platform `DNS Zone Contributor` on `biroltilki.art` for DNS-01

Example names from Topic 03: cluster `aks-boutique-dev-gwc`, ACR `acrboutiquedevgwc`, vault `kv-boutique-dev-gwc`. ACR and Key Vault names are globally unique; the setup guide includes `az acr check-name` and a soft-delete purge check.

`terraform/environments/dev/main.tf` comments the topic split: Topic 02 modules, then Topic 03, then Topic 04 federation. That file is the physical platform. There is no `environments/prod`.

`terraform/environments/dev/main.tf` continues after Key Vault with `module.aks` (subnet from networking, kubernetes_version from variables aligned with `versions.yaml`), `module.identities`, and later `module.ado_federation`. `oms_agent` stays off. `network_policy` defaults allow Topic 15 to set `"azure"` on rebuild without rewriting the module.

`terraform/modules/aks/variables.tf` and `DEFENDER-OPT-IN.md` document Defender as subscription/portal work, not default TF. Lived Topic 03 did not turn it on.

Get credentials after apply (`az aks get-credentials`) is a human operator step. Pipeline UAMI still must not get cluster admin. Entra AAD RBAC on the cluster means your user object is the kubectl identity, not a downloaded admin cert as the long-term model.

`tests/terraform/foundation-post-apply.sh` is TEST-011: AKS Ready, ACR reachable, Key Vault exists. Run it after Topic 03, not from a teardown laptop.

## Lived operator commands (Topic 03)

```bash
az acr check-name --name acrboutiquedevgwc
az keyvault list-deleted --query "[?name=='kv-boutique-dev-gwc']" -o table
az vm list-skus --location germanywestcentral --size Standard_D4s_v6 --all -o table
cd terraform/environments/dev && terraform plan && terraform apply
az aks get-credentials --resource-group rg-boutique-dev-gwc --name aks-boutique-dev-gwc
kubectl get nodes
./tests/terraform/foundation-post-apply.sh
```

Confirm `oidc_issuer_enabled` in the cluster resource. Confirm ACR `admin_enabled` is false. Confirm no Log Analytics workspace was created. Cost starts here; Topic 13 is how it stops.

Limits: one cluster, public API (Checkov skip), no private ACR. `prod` still does not exist. WI is on so later topics can federate; this topic does not yet prove CSI or ADO OIDC.

## 4. Test the design under failure

### Lived control failure — Insufficient DSv5 quota at apply

> **Practice — Reconstruct the ADR-0011 amendment**
>
> Topic 03 apply failed with `ErrCode_InsufficientVCPUQuota` for Standard DSv5 while Dsv6 remained available. Decide what a “just change the SKU in the portal” response would have broken.

**Severity:** high; blocked cluster, temptation to click-ops.  
**Plausible harm:** portal-created node pools that Terraform cannot manage; SKU drift from `versions.yaml`; later rebuilds fail again.  
**Potential blast radius:** the only cluster; every GitOps workload waiting on nodes.  
**Bounded by:** `az vm list-skus` in Topic 00/03, ADR-0011 amendment, pins in `versions.yaml`.  
**Primary principles:** explicit contracts, reconciliation, lived evidence beats scaffold.

#### Diagnosis

Quota is a subscription fact, not a Terraform syntax error. Changing SKU only in the Azure Portal leaves state and docs lying. Changing SKU only in `main.tf` without ADR and `versions.yaml` leaves setup Topic 00 teaching the old size.

#### Correction

Amend ADR-0011 (done). Pin Dsv6 in `versions.yaml` and module variables. Keep the preferred Dsv5 note for when quota exists. Re-run `az vm list-usage` on the next rebuild before apply.

A second failure: enabling ACR admin user to “unblock docker login.” That creates a password that will leak into ADO variables. Correction: kubelet AcrPull plus pipeline UAMI AcrPush (Topic 04). `admin_enabled` stays false.

## Production reality

**Best Practice:** Workload Identity and OIDC issuer enabled at cluster create.

**Production Practice:** SKU and quota are subscription-specific. Re-run `az vm list-skus` on every rebuild. Do not assume Dsv6 remains the right fallback. Key Vault names after soft-delete require purge or a new name before re-apply — Topic 03’s `az keyvault list-deleted` check exists because teardown without purge protection still soft-deletes.

ACR Basic SKU is a cost choice (`var.acr_sku`). Content trust / quarantine Checkov skips (Topic 16) document that cosign+Kyverno replace registry-native trust. Do not enable ACR admin to “see if push works.”

### Common errors

- Passing a Log Analytics ID “temporarily” and forgetting ADR-0012.
- Putting Boutique on the system pool by disabling `only_critical_addons_enabled`.
- Granting the platform UAMI Contributor so “DNS and KV just work.”

## 5. What You Learned

Topic 03 creates the only cluster, a non-admin ACR, a teardown-friendly Key Vault, and a platform identity for CSI and DNS-01. OIDC issuer and WI are on so Topic 04 and Topic 06 can federate. Log Analytics stays unwired. `prod` still does not exist as a cluster.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Topic 03 guide | `docs/setup/03-cluster-resources.md` | Apply order and name checks |
| AKS module | `terraform/modules/aks/` | WI, CNI, pools, Defender ignore |
| ACR module | `terraform/modules/acr/` | No admin user |
| Key Vault module | `terraform/modules/key-vault/` | RBAC, optional ACL/purge |
| Identities | `terraform/modules/identities/` | AcrPull, Secrets User, DNS Contributor |
| Cost model | `docs/architecture/11-cost-model.md` | Why teardown matters after this topic |

## What changed

| Before | After |
|--------|--------|
| ACR admin user for docker login. | **`admin_enabled = false`; kubelet AcrPull.** |
| Cluster without WI. | **`oidc_issuer_enabled` and `workload_identity_enabled`.** |
| OMS agent by default. | **`log_analytics_workspace_id = null`.** |
| Dsv5 assumed. | **Lived Dsv6 after quota evidence.** |

`terraform/modules/aks/README.md` and sibling module READMEs list inputs/outputs. Read them before changing SKU or `network_policy`. `environments/dev/outputs.tf` is what Topics 04–09 consume (`aks_oidc_issuer_url`, `acr_login_server`, `platform_identity_client_id`). Missing outputs become copied secrets.

> **Independent Practice — Decide private ACR**
>
> ROADMAP defers private AKS/ACR. Using ADR-0002, cost model, and the pipeline's Microsoft-hosted agent, write why private ACR would break Topic 09 unless you also change agents or peering. Do not implement it.
