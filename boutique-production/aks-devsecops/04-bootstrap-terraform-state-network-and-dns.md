# 4. Bootstrap Terraform State, Network, and DNS

Unsigned images never reach a cluster that does not exist. The first production risk on Azure is still real: local Terraform state on a laptop, a **VNet (Virtual Network)** that cannot host AKS, and a DNS zone that Let's Encrypt cannot see. This chapter covers Setup Topics **00–02** and the modules that create remote state, networking, and Azure DNS.

The production question is:

> How do you make Terraform state recoverable and DNS delegable before AKS exists, without putting secrets in Git?

## 1. Unsafe starting state

The unsafe default is `terraform apply` from `environments/dev` with local state, then “we will move the backend later.” State contains resource IDs and secret metadata. Laptop loss, a second engineer, or a partial destroy leaves an unowned estate.

The other default is to create AKS before NS records exist at the registrar. Topic 06 then spends hours on pending Challenges that are really Topic 02.

## 2. The production model: bootstrap first, foundation second

> *Theory — Split-state bootstrap*
>
> This model enables the platform stack to use versioned remote state while the bootstrap stack that *creates* that backend stays small, local, and replaceable.

Topic 00 proves tools and subscription. Topic 01 creates a dedicated resource group, storage account, and private blob container. Topic 02 applies `terraform/environments/dev/` for resource group, VNet, NSG, and Azure DNS — still **without** AKS. Logging stays out: [ADR-0012](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0012-loki-in-cluster-logging.md) forbids a Log Analytics workspace on the default path.

## 3. How this repository implements Topics 00–02

> **Practice — Confirm Topic 00 is a workstation contract**
>
> Open `docs/setup/00-prerequisites.md` and list what must be true before `terraform/bootstrap` apply.

Topic 00 installs Terraform ≥ 1.6, Azure CLI, kubectl, Helm, Git, Python, pre-commit. It requires `az login` on the intended subscription, `az vm list-skus` for `Standard_D2s_v6` / `Standard_D4s_v6` in `germanywestcentral` ([ADR-0011](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0011-aks-node-vm-sku.md)), and a **GitHub** remote. **ADO (Azure DevOps)** is named only as the future pipeline host — not as a Git remote.

> **Practice — Read the bootstrap stack**
>
> Open `terraform/bootstrap/main.tf` and `docs/setup/01-terraform-bootstrap.md`.

Bootstrap uses **local** state on purpose. Comment at the top of `main.tf`:

```hcl
# Bootstrap stack: Azure Storage for Terraform remote state.
# This stack uses local state (default). Do not configure a remote backend here.
```

It creates three resources: `azurerm_resource_group.state`, `azurerm_storage_account.state` with `min_tls_version = "TLS1_2"` and `versioning_enabled = true`, and `azurerm_storage_container.state` with `container_access_type = "private"`. Example names in the setup guide: `rg-tfstate-boutique-gwc`, `stboutiquetfgwc`, container `tfstate`. Storage account names are globally unique; collisions are expected — change `terraform.tfvars`, which is gitignored.

`terraform/environments/dev/backend.tf` then points at that container. Topic 01 is complete when `terraform init` in `environments/dev` succeeds against the blob. Platform resources are **not** created yet.

> **Practice — Read foundation modules**
>
> Open `terraform/environments/dev/main.tf` (resource-group, networking, dns), `terraform/modules/networking/main.tf`, and `terraform/modules/dns/main.tf`.

The dev root wires foundation first:

```hcl
module "resource_group" {
  source = "../../modules/resource-group"
  name     = var.resource_group_name
  location = var.location
}

module "networking" {
  source = "../../modules/networking"
  vnet_address_space  = var.vnet_address_space
  aks_subnet_prefixes = var.aks_subnet_prefixes
}

module "dns" {
  source    = "../../modules/dns"
  zone_name = var.dns_zone_name
}
```

Locked values from Topic 02: `location = germanywestcentral`, VNet `10.0.0.0/16`, AKS subnet `10.0.0.0/20`, zone `biroltilki.art`. `docs/architecture/06-network-design.md` adds service CIDR `10.1.0.0/16` and CoreDNS `10.1.0.10` — those appear when AKS is created in Topic 03; they must not overlap the node subnet.

Networking NSG allows Azure Load Balancer, VNet inbound, Internet 80/443, and outbound Internet. There is no public SSH to nodes. The AKS subnet already sets `service_endpoints = ["Microsoft.KeyVault"]` for Topic 19's optional Key Vault **ACL (Access Control List)** Deny — a scaffold consumer of a lived network choice.

DNS module is one resource: `azurerm_dns_zone`. Delegation at the registrar is the human gate. Until `dig NS biroltilki.art` shows Azure name servers, Topic 06 cannot finish.

`terraform.tfvars` stays local. `SECURITY.md` and `.gitignore` treat filled tfvars as secrets-adjacent. `make pre-commit` includes gitleaks.

`terraform/environments/dev/backend.tf` hardcodes bootstrap names:

```hcl
backend "azurerm" {
  resource_group_name  = "rg-tfstate-boutique-gwc"
  storage_account_name = "stboutiquetfgwc"
  container_name       = "tfstate"
  key                  = "dev.terraform.tfstate"
}
```

If you changed storage names in bootstrap tfvars, this file must match. Partial copy-paste is how `terraform init` talks to an empty account. `key = "dev.terraform.tfstate"` is the platform stack identity — one physical environment, named `dev` because it is the only root, not because prod Terraform lives elsewhere.

`terraform/modules/resource-group/` is a thin wrapper: name, location, tags. Topic 02’s platform RG (example `rg-boutique-dev-gwc`) is distinct from the bootstrap RG. Destroying the wrong one is a teardown incident; creating both in one apply is a bootstrap incident.

Foundation apply is billable even without AKS: VNet is cheap; the mistake is enabling diagnostics to Log Analytics “while we are here.” `environments/dev/main.tf` comments: Loki later; no workspace. `module.diagnostics` exists in the repo and stays unwired.

## Lived operator commands (Topics 00–02)

```bash
terraform version   # >= 1.6
az account show
az vm list-skus --location germanywestcentral --size Standard_D2s_v6 --all -o table
pre-commit run --all-files
cd terraform/bootstrap && terraform apply
cd terraform/environments/dev && terraform init && terraform apply
dig NS biroltilki.art +short
```

Topic 00 Step 4 connects the GitHub remote. Without it, Argo CD later has nothing to pull. Bootstrap tfvars stay gitignored. If `stboutiquetfgwc` is taken, change the name in bootstrap **and** `environments/dev/backend.tf` together.

Limits: Topic 02 without registrar NS is an incomplete DNS zone. Do not debug cert-manager yet. Do not create AKS in the same apply “to save time” — Topic 03 is a separate plan review.

## 4. Test the design under failure

### Independent control failure — Lost local bootstrap state

> **Practice — Diagnose an orphaned state account**
>
> An engineer deletes `terraform/bootstrap/terraform.tfstate` after Topic 02 is live. `environments/dev` still has a remote backend. They re-run bootstrap apply with a new storage name.

**Severity:** high; split brain for Terraform and possible orphan billing.  
**Plausible harm:** two state accounts; inability to destroy the platform cleanly; leaked resource IDs in the abandoned blob.  
**Potential blast radius:** every resource in `environments/dev` plus the original bootstrap RG.  
**Bounded by:** blob versioning, private container, documented split (bootstrap local / platform remote), teardown script that destroys env first.  
**Primary principles:** explicit contracts, reconciliation, teardown is a production control, recovery.

#### Diagnosis

Bootstrap state is the map to the map. Losing it does not delete the storage account. Re-applying with a new name creates a second backend that `environments/dev` does not use. The platform stack still points at the old blob until `backend.tf` is rewritten — which is a migration, not a bootstrap.

#### Correction

Recover bootstrap state from backup or import existing RG/storage/container into a new local state. Do not create a second account “to be safe.” Topic 13 retains bootstrap by default for this reason: destroy AKS/ACR first; keep the versioned blob until you explicitly pass `--destroy-bootstrap`.

A second failure mode is DNS: Azure zone created but registrar NS not updated. Detection is `dig NS`; recovery is registrar change and wait. Do not debug cert-manager until that check passes.

## Production reality

**Best Practice:** remote state with versioning and a private container before any cluster.

**Production Practice:** bootstrap remains local-state on purpose so a backend chicken-and-egg does not appear. Protect `terraform/bootstrap/terraform.tfstate` like a secret map. Topic 13 keeps the blob so destroy/re-init does not require archaeology.

DNS: Azure can host the zone while the registrar still points at the old NS. `dig NS` is the only completion test that matters for Topic 02. cert-manager errors in Topic 06 are not a Terraform bug.

### Common errors

- Committing `terraform.tfvars` with subscription IDs “because the example has them.”
- Overlapping `service_cidr` with `10.0.0.0/16` when someone “simplifies” addressing.
- Creating the DNS zone in a different RG than cert-manager’s `resourceGroupName`.

## 5. What You Learned

Topic 00 proves the workstation and GitHub remote. Topic 01 creates versioned, private remote state without putting the bootstrap stack on that backend. Topic 02 lays VNet, NSG, and a DNS zone that can be delegated — still no cluster. Logs stay in-cluster later; they are not an Azure Monitor workspace here.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Prerequisites | `docs/setup/00-prerequisites.md` | Tool and SKU contract |
| Bootstrap guide | `docs/setup/01-terraform-bootstrap.md` | Remote state procedure |
| Foundation guide | `docs/setup/02-azure-foundation.md` | VNet/DNS apply and delegation |
| Bootstrap stack | `terraform/bootstrap/` | State RG, storage, private container |
| Modules | `terraform/modules/resource-group/`, `networking/`, `dns/` | Reviewable CIDR and zone |
| Network design | `docs/architecture/06-network-design.md` | Addressing and ingress path |

## What changed

| Before | After |
|--------|--------|
| State could live on a laptop. | **Bootstrap blob, versioned, private; platform remote.** |
| AKS might be created before DNS. | **Topic 02 zone + registrar NS before Topic 06.** |
| Log Analytics “while we are here.” | **Not wired; Loki later.** |

`scripts/bootstrap-tf-backend.sh` may wrap Topic 01. `docs/setup/01-terraform-bootstrap.md` remains the checklist. Networking README under `terraform/modules/networking/README.md` documents purpose, inputs, outputs — module docs are part of the contract, not optional comments.

> **Independent Practice — Plan a zone rename**
>
> You do not own `biroltilki.art`. List every file that embeds that zone or its hostnames (`versions.yaml`, GitOps ingress, setup placeholders). State the Topic 02 order: create zone, delegate NS, only then Topic 06. Do not apply Azure unless you are rebuilding.
