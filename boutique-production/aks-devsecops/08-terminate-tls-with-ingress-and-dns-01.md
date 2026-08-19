# 8. Terminate TLS With Ingress and DNS-01

A storefront on HTTP, or a certificate issued with a portal-pasted secret, is not a DevSecOps edge. This chapter is Setup Topic **06**: NGINX Ingress, cert-manager, and Let's Encrypt **DNS-01** against Azure DNS using the platform **WI (Workload Identity)** from Topic 03.

The production question is:

> How do five HTTPS hostnames share one Load Balancer without storing a DNS credential in Git or in a long-lived Kubernetes Secret?

## 1. Unsafe starting state

The unsafe default is HTTP-01, a wildcard cert bought as a file, or Azure DNS keys in `cluster-issuer` YAML. HTTP-01 fails when 80 is blocked. Files in Git leak. Static DNS secrets outlive rotation.

The other default is to debug cert-manager for an hour before checking `dig NS biroltilki.art`. Topic 02 delegation is the real prerequisite. Topic 06 cannot invent nameservers.

## 2. The production model: DNS-01 with Workload Identity

> *Theory — Identity-bound certificate issuance*
>
> This model enables Let's Encrypt to prove domain control through Azure DNS using the same platform UAMI that later mounts Key Vault secrets — not a copied API key.

All platform and Boutique hostnames share one NGINX Ingress and one Azure Standard Load Balancer (`docs/architecture/06-network-design.md`). cert-manager issues per-Ingress certificates via ClusterIssuer `letsencrypt-prod`. The DNS-01 solver uses Azure DNS in resource group `rg-boutique-dev-gwc`, zone `biroltilki.art`, and federated identity `system:serviceaccount:cert-manager:cert-manager`.

`versions.yaml` pins nginx ingress chart `4.10.1` and cert-manager `1.14.5`.

## 3. How this repository implements Topic 06

> **Practice — Patch placeholders, then sync**
>
> Open `docs/setup/06-ingress-tls.md` and the cert-manager GitOps files it names.

Topic 06 requires replacing:

| Placeholder | Source |
|-------------|--------|
| `<PLATFORM_IDENTITY_CLIENT_ID>` | `terraform output -raw platform_identity_client_id` |
| `<ACME_EMAIL>` | Operator email |
| `<AZURE_SUBSCRIPTION_ID>` | `az account show` |

Those values go in `gitops/platform/cert-manager/values.yaml` (WI annotation on the service account) and `gitops/platform/cert-manager/cluster-issuer-letsencrypt.yaml` (`resourceGroupName`, `hostedZoneName`). Push to GitHub so Argo CD's `platform-root` can sync. kubectl-editing the ClusterIssuer on the cluster is drift.

NGINX is installed via `gitops/platform/ingress-nginx/`. It creates the public IP. DNS **A records** for `argocd-boutique`, later Grafana and Boutique hosts, must point at that IP. Five FQDNs, one address.

Topic goal when complete: `https://argocd-boutique.biroltilki.art` with a Ready certificate. Boutique hostnames wait for Topics 10 and 12; they reuse this Ingress class.

> **Practice — Use the DNS-01 runbook before changing YAML**
>
> Open `docs/troubleshooting/cert-manager-dns01.md`.

Lived failure classes:

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Challenge `pending` | Delegation incomplete | `dig NS biroltilki.art` must show Azure NS |
| `azureDNS` authentication error | WI / federated credential missing | Topic 06 federation step; identities module DNS Zone Contributor |
| Wrong zone | `hostedZoneName` mismatch | Must match `biroltilki.art` and the foundation RG |
| Rate limits | Repeated failed issuances | Staging issuer; wait |

Inspect:

```bash
kubectl get clusterissuer letsencrypt-prod
kubectl get certificate -A
kubectl describe challenge -A
```

Platform UAMI must have **DNS Zone Contributor** (Topic 03) and a federated credential for `system:serviceaccount:cert-manager:cert-manager`. Missing either looks like “cert-manager is broken” when identity is broken.

NGINX Application (`gitops/platform/ingress-nginx/Application.yaml`) is multi-source Helm:

```yaml
sources:
  - repoURL: https://kubernetes.github.io/ingress-nginx
    chart: ingress-nginx
    targetRevision: 4.10.1
    helm:
      valueFiles:
        - $values/gitops/platform/ingress-nginx/values.yaml
  - repoURL: https://github.com/btilki/boutique-aks-devsecops
    ref: values
```

Chart version must stay aligned with `versions.yaml`. Values stay in Git. `ServerSideApply=true` is a lived install detail for CRDs.

After the LB IP exists, create Azure DNS A records (or let a later GitOps DNS approach exist — this pilot used Azure DNS records as documented in Topic 06). Five names, one IP: `argocd-boutique`, `grafana-boutique`, `dev-boutique`, `stage-boutique`, `boutique`. Missing A records look like TLS failure.

Let's Encrypt staging versus prod issuers: troubleshooting mentions rate limits. A rebuild that issues, destroys, and re-issues the same FQDNs in a day will hit them. Plan a staging issuer for the first apply.

## Lived operator commands (Topic 06)

```bash
dig NS biroltilki.art +short
cd terraform/environments/dev
terraform output -raw platform_identity_client_id
kubectl get clusterissuer letsencrypt-prod
kubectl get certificate -A
kubectl describe challenge -A
az identity federated-credential list \
  --identity-name uami-boutique-platform \
  --resource-group rg-boutique-dev-gwc -o table
```

NS must show Azure nameservers before Challenges can succeed. Patch Git placeholders, push, let Argo sync — do not kubectl-edit ClusterIssuer. Ingress IP from `ingress-nginx-controller` is the A-record target for all five names.

Limits: HTTP-01 was not chosen. Staging issuer is for rebuilds that would hit rate limits. Topic 06 success is Argo CD HTTPS, not Boutique. Five FQDNs share fate with one LB.

## 4. Test the design under failure

### Lived control failure — Certificate stuck Issuing after a placeholder miss

> **Practice — Separate DNS, identity, and ACME**
>
> A Challenge stays pending. Three hypotheses: NS not delegated, WI client ID still `<PLATFORM_IDENTITY_CLIENT_ID>`, or Let's Encrypt rate limit. Order the checks.

**Severity:** high for platform UI and later Boutique HTTPS; medium if only Argo CD is blocked and kubectl still works.  
**Plausible harm:** operators fall back to HTTP, skip TLS, or paste a personal access token into the ClusterIssuer.  
**Potential blast radius:** every hostname on the shared Ingress; Boutique cannot complete Topic 10.  
**Bounded by:** Topic 02 delegation, platform UAMI DNS RBAC, GitOps placeholders, DNS-01 runbook.  
**Primary principles:** explicit contracts, Git is the deploy authority, trustworthy evidence, recovery.

#### Diagnosis

`dig NS` first. If NS is wrong, cert-manager logs are noise. If NS is right, compare ClusterIssuer subscription, RG, zone, and client ID to Terraform outputs. If those match, read Challenge events for ACME errors versus Azure 403.

#### Correction

Fix Git, not the live CR, then Argo sync. For rate limits, use the staging ClusterIssuer documented in the troubleshooting guide. Do not copy a Let's Encrypt account key into the repo.

A second failure: creating five public Load Balancers (one per Service `type: LoadBalancer`). Boutique base patches **remove** `frontend-external` for this reason (`gitops/apps/boutique/base/patches/remove-frontend-external.yaml`). Correction: Ingress only.

## Production reality

**Best Practice:** DNS-01 with Workload Identity so no DNS shared key lives in Git.

**Production Practice:** federation subject for cert-manager is a Kubernetes service account, not the ADO `sc://` subject. Mixing those federated credentials is a common 403. Identities module already granted DNS Zone Contributor to the **platform** UAMI — cert-manager must use that client ID.

HTTP-01 is simpler until it is not. This design chose DNS-01 because all hostnames share an Ingress and the zone is already in Azure.

### Common errors

- Leaving `<ACME_EMAIL>` in the ClusterIssuer and wondering why ACME registration fails.
- Pointing `hostedZoneName` at a subdomain that was never delegated.
- Opening NSG to the world on 80/443 twice (NSG already allows 80/443 in Topic 02).

## 5. What You Learned

Topic 06 puts TLS termination on NGINX and proves domain control with DNS-01 via Workload Identity. One LB, five hostnames, no DNS secret in Git. Delegation is a Topic 02 leftover; identity is a Topic 03 leftover. Screenshots and Git record success after DNS goes offline.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Topic 06 guide | `docs/setup/06-ingress-tls.md` | Placeholder map and validation |
| Ingress GitOps | `gitops/platform/ingress-nginx/` | Shared controller |
| cert-manager GitOps | `gitops/platform/cert-manager/` | ClusterIssuer + WI |
| Network design | `docs/architecture/06-network-design.md` | Hostname table |
| DNS-01 runbook | `docs/troubleshooting/cert-manager-dns01.md` | Challenge diagnosis |

## What changed

| Before | After |
|--------|--------|
| HTTP or a cert file in Git. | **Let's Encrypt DNS-01 via platform WI.** |
| One LoadBalancer per service. | **One NGINX LB; Boutique frontend-external removed.** |
| HTTP-01 behind a firewall. | **Azure DNS proof; A records for five FQDNs.** |

`docs/architecture/06-network-design.md` DNS flow: registrar NS → Azure DNS → A record → LB → NGINX → Service → Pod. Ports 80/443 only at the NSG Internet rule. Node SSH is not in the design. If you need to debug TLS, `kubectl describe challenge` beats opening 80 to the world.

Lived completion is a Ready Certificate for Argo CD. Boutique hostnames reuse the same issuer in Topics 10 and 12. After teardown, `dig` fails; screenshots from 10/12 still show padlock-era pages.

> **Independent Practice — Design a staging issuer**
>
> Write the GitOps change you would make to issue from Let's Encrypt staging during a rebuild, and the promotion step to production issuer. Name the rate-limit harm you are avoiding. Do not apply unless you are in a live rebuild.
