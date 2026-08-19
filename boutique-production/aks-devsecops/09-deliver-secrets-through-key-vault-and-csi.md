# 9. Deliver Secrets Through Key Vault and CSI

A secret in Git, in a Docker env file, or in an ADO variable group “because CSI looked hard” is the usual leak. This chapter is Setup Topic **07**: Secrets Store **CSI (Container Storage Interface)** plus Azure Key Vault provider, proven with an isolated test pod. The inventory lives in `docs/security/secrets-management.md`.

The production question is:

> How do workloads and pipelines get secrets without those secrets becoming Git history or node-wide environment variables?

## 1. Unsafe starting state

The unsafe default is Kubernetes Secrets created by kubectl from a laptop, committed “sealed” YAML nobody can rotate, or Grafana admin password in Helm values on `main`. Topic 09's cosign private key would then sit next to the public overlays.

Boutique demo payments are mock. That is not permission to store real card data. `docs/security/secrets-management.md` says so.

## 2. The production model: Key Vault as system of record

> *Theory — Secret delivery paths*
>
> This model enables each consumer to read Key Vault through an attributable identity — ADO OIDC for ephemeral jobs, CSI plus Workload Identity for pods — while Git holds only public material.

Principles from `docs/security/secrets-management.md`:

1. Never commit private keys, passwords, or filled `terraform.tfvars`.
2. Azure Key Vault is the system of record.
3. Delivery is WI + CSI, or ADO OIDC for pipeline-only reads.
4. Least privilege: pipeline UAMI = Secrets User + AcrPush; platform UAMI = Secrets User (+ DNS).
5. Cosign **public** key may live in Git for Kyverno; private key must not.

Two paths:

| Path | When |
|------|------|
| ADO OIDC → Key Vault | Topic 09 sign job needs `cosign-private-key` for minutes |
| CSI + platform UAMI | Long-running pods mount `/mnt/secrets` or sync a Kubernetes Secret |

## 3. How this repository implements Topic 07

> **Practice — Read the CSI GitOps and the example**
>
> Open `docs/setup/07-secrets-csi.md`, `gitops/platform/secrets-store-csi/values.yaml`, and `examples/csi-secret-test/README.md`.

Topic 07 installs CSI driver **1.4.0** and Azure provider **1.5.0** (`versions.yaml`) into `kube-system` via Argo CD. It does not yet store the cosign key. It proves the mount path with secret `csi-test-secret` and namespace `csi-test`.

Placeholders in `secretproviderclass-example.yaml` and `test-serviceaccount.yaml`:

| Placeholder | Source |
|-------------|--------|
| `<KEY_VAULT_NAME>` | `terraform output -raw key_vault_name` |
| `<TENANT_ID>` | `az account show` |
| `<PLATFORM_IDENTITY_CLIENT_ID>` | platform UAMI |

A federated credential must exist for `system:serviceaccount:csi-test:csi-test-sa`. Missing federation looks like an empty volume.

Validation from the example README:

```bash
kubectl exec -n csi-test csi-test-pod -- cat /mnt/secrets/csi-test-secret
```

Cleanup matters: the test pod may use a non-ACR image. Topic 08's registry allowlist **excludes** `csi-test`. After the proof, delete the pod so you are not running an unsigned exception as a pet.

> **Practice — Read the inventory you will operate**
>
> Open the secret table in `docs/security/secrets-management.md`.

| Secret | Store | Consumers |
|--------|-------|-----------|
| Cosign private key | Key Vault `cosign-private-key` | ADO sign job |
| Cosign public key | Key Vault + Git Kyverno policy | Pipeline verify + admission |
| Grafana admin | Key Vault → K8s Secret | Topic 11 |
| CSI smoke | `csi-test-secret` | Disposable |
| TLS certs | cert-manager → K8s Secrets | NGINX |
| Terraform state | Bootstrap blob | Operators with storage RBAC |
| ADO auth | OIDC federation | Service connection — not a PAT in Git |

`make pre-commit` includes gitleaks. `SECURITY.md` restates the never-commit list.

CSI driver Helm values live in `gitops/platform/secrets-store-csi/values.yaml`. Sync is via Argo Application like other platform components. The SecretProviderClass is Azure-specific: `usePodIdentity: false`, Workload Identity objects, `objects` listing `csi-test-secret`.

Topic 09 will **not** mount the cosign private key into a long-lived pod. Agents are Microsoft-hosted VMs. Fetch-at-job-time via `az keyvault secret show` is the correct path for signing. CSI is for cluster workloads (Grafana, future app secrets). Using CSI for the pipeline would mean a pod with the signing key — a larger blast radius.

Rotation triggers in the inventory: compromise, annual test rotation for cosign; password leak for Grafana; disposable for CSI test. `docs/operations/15-secret-rotation.md` is the day-2 expansion. After teardown the private key is gone with the vault; the public PEM in Git is an orphan until Topic 09 runs again.

## Lived operator commands (Topic 07)

```bash
cd terraform/environments/dev
terraform output -raw key_vault_name
terraform output -raw platform_identity_client_id
terraform output -raw aks_oidc_issuer_url
az keyvault secret set --vault-name <KV> --name csi-test-secret --value "csi-ok"
kubectl exec -n csi-test csi-test-pod -- cat /mnt/secrets/csi-test-secret
```

Create the federated credential for `system:serviceaccount:csi-test:csi-test-sa` before expecting the mount. After the cat succeeds, delete the test pod so Topic 08’s allowlist exclusion is not a standing unsigned workload. Topic 09 will use `az keyvault secret show` from ADO, not this mount, for `cosign-private-key`.

## Limits of this chapter

CSI proof is one secret in `csi-test`. It does not rotate cosign keys, does not lock Key Vault networking, and does not store Boutique payment data (there is none). Topic 19’s ACL Deny is scaffold. Calling Topic 07 “vault hardened” is a Chapter 16 error.

## 4. Test the design under failure

### Independent control failure — Cosign private key committed “for Kyverno”

> **Practice — Classify public vs private material**
>
> A PR adds `cosign.key` next to `02-verify-image-signatures.yaml` “so the cluster can sign.” Gitleaks may catch it; a `.gitignore` miss may not.

**Severity:** critical; signing authority stolen.  
**Plausible harm:** attacker signs arbitrary ACR tags; Kyverno admits malware that looks like Boutique.  
**Potential blast radius:** all namespaces that pull ACR images; residual trust until key rotation and re-sign.  
**Bounded by:** gitignore, gitleaks, Key Vault RBAC, public-key-only Git policy, rotation section in secrets-management and supply-chain docs.  
**Primary principles:** explicit contracts, identity is digest not tag, recovery, blast-radius control.

#### Diagnosis

Kyverno needs the **public** PEM. Signing is a pipeline identity concern. Putting the private key in Git confuses verifier and signer.

#### Correction

Purge from Git history if it landed. Rotate the key pair in Key Vault (Topic 09 procedure). Update Kyverno public key. Re-sign digests. Treat old signatures as untrusted. The CSI test secret is disposable; the cosign key is not.

A second failure: CSI mount works in `csi-test` but Grafana later uses a hardcoded Helm password. Correction: reuse the Topic 07 pattern in Topic 11, not a parallel secret channel.

## Production reality

**Best Practice:** one system of record (Key Vault) and two delivery paths (OIDC vs CSI) chosen by consumer lifetime.

**Production Practice:** public Key Vault + no purge protection are documented residuals (Checkov skips, ADR-0016). Closing them in Topic 19 can break CSI and complicate destroy. Do not flip Deny ACL on a Friday without the Key Vault service endpoint already on the subnet (Topic 02 already added `Microsoft.KeyVault`).

gitleaks in pre-commit is mechanism evidence for Git. It is not evidence nobody pasted a key into ADO library variables. Topic 04’s OIDC design exists to make that paste unnecessary.

### Common errors

- Syncing every Key Vault object into a Kubernetes Secret (duplicates the store; RBAC becomes two problems).
- Checking in `cosign.pub` with the wrong key after rotation and leaving Kyverno trusting the old one — actually that is required during overlap; the error is leaving the private key in Git.
- Using `csi-test` as a junk drawer namespace after Topic 08 Enforce.

## 5. What You Learned

Topic 07 proves Key Vault → CSI → pod using platform Workload Identity. Git holds public keys and placeholders. Pipelines will read the private signing key through OIDC, not through CSI, because agents are ephemeral. The test namespace is an exception to be removed, not a third environment.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Topic 07 guide | `docs/setup/07-secrets-csi.md` | Install and placeholder map |
| CSI GitOps | `gitops/platform/secrets-store-csi/` | Driver, provider, test SPC |
| Example | `examples/csi-secret-test/README.md` | Mount validation commands |
| Inventory | `docs/security/secrets-management.md` | Rotation triggers and paths |
| Policy | `SECURITY.md` | Never-commit rules |

## What changed

| Before | After |
|--------|--------|
| Secrets in Helm values on `main`. | **Key Vault as system of record.** |
| Pipeline passwords. | **OIDC GET for cosign; CSI for pods.** |
| Public key confused with private. | **PEM in Kyverno; key in vault.** |

`gitops/platform/secrets-store-csi/secretproviderclass-example.yaml` is the lived SPC pattern. Copy it for Grafana in Topic 11 rather than inventing `envFrom` from a kubectl-created Secret. `examples/README.md` points at the CSI test as the isolated demo — that is the book’s “lab,” not a Northwind tree.

> **Independent Practice — Design Grafana delivery**
>
> Using only the inventory table, write the Topic 11 secret path: Key Vault object name, CSI vs synced Secret, who can read, and the rotation trigger. Do not put the password in Git.
