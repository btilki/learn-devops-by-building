# 4. Put DNS, TLS, and Ingress on a Recoverable Edge

A private cluster with no stable public name cannot serve browse or checkout, and a name that outlives teardown becomes a lie. The production question is:

> How do **DNS (Domain Name System)**, **TLS (Transport Layer Security)**, and Ingress become a recoverable edge — and how do you label that edge **inactive** after destroy?

Setup topics **05–06** (**Lived**) plus `docs/dns.md` and Terraform modules `dns` and `ingress-edge` answer it. Google-managed certificates and static IPs are mechanism. They are not SLO success.

## 1. An unsafe starting state: registrar A records and ephemeral IPs

If A records live at the registrar while Cloud DNS is also authoritative, two sources fight. If the load balancer IP is ephemeral, every Ingress reconcile can strand DNS. If TLS secrets are hand-made in the cluster, rotation and GitOps both fail.

Topic 05 exists because Google-managed certificates in topic 06 provision only after names resolve to the load balancer. Topic 06 exists because public traffic reaches GKE through an external HTTP(S) load balancer that needs a **global static IP** and a ManagedCertificate in the same namespace as the Ingress.

Post-teardown, the unsafe story is to leave the README URLs looking live. `docs/dns.md` records the honest table: both hostnames **Inactive** — no public A record after 2026-07-04.

## 2. The production model: one authority, stable address, managed certs

> *Theory — Recoverable HTTPS edge*
>
> This model enables storefront and Argo CD names to be created, delegated, certified, and deleted from Terraform plus registrar NS, so teardown does not leave a customer-looking hostname on a dead IP.

### One DNS authority

`docs/dns.md` architecture:

```text
Registrar (biroltilki.art NS) → Cloud DNS managed zone
  ├── boutique.biroltilki.art  → A → global static IP
  └── argocd.boutique.biroltilki.art → A → same IP (host-based routing on GCE Ingress)
```

Lived smoke validation later used **two** static IPs (`boutique-ingress-ip` and `argocd-ingress-ip`). The dns.md diagram describes the original shared-IP pattern; `docs/setup/16-smoke-validation.md` is the operational check: each hostname must match its reserved address. Read both. Do not flatten them into one IP if Terraform reserved two.

`terraform/modules/dns/main.tf` creates managed zone `biroltilki-art` and A records for `var.boutique_hostname` and `var.argocd_hostname` pointing at `var.static_ip_address` from the ingress-edge module.

Registrar NS delegation is the step Terraform cannot do. Topic 05: paste four `ns-cloud-*.googledomains.com` servers. Common mistake: creating A records at the registrar **and** using Cloud DNS NS.

### Static IP then certificate

`terraform/modules/ingress-edge/main.tf` reserves:

```hcl
resource "google_compute_global_address" "ingress" {
  name         = var.address_name
  address_type = "EXTERNAL"
  ip_version   = "IPV4"
}
```

Topic 06 GKE ManagedCertificate pattern (Argo CD namespace):

```yaml
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: boutique-managed-cert
  namespace: argocd
spec:
  domains:
    - boutique.biroltilki.art
    - argocd.boutique.biroltilki.art
```

HTTPS will not work end-to-end until topic 09 syncs Argo CD Ingress and the certificate reaches Active (often 15–60 minutes after DNS is correct). Boutique gets a matching cert in namespace `boutique` during topic 12.

Topic 05 registrar steps: custom nameservers, four `ns-cloud-*.googledomains.com` values, save, wait minutes to 48 hours. Troubleshooting: empty `dig` → NS; wrong IP → stale A record; TLS Provisioning → DNS not at LB; cert Active but 404 → Ingress rules.

**Best Practice:** Keep DNS in Terraform for reproducible teardown.

**Production Practice:** Delete records before releasing static IPs. An orphan global address bills monthly with no journey attached (Chapter 15).

## 3. How this repository implements it

> **Practice — Read dns.md status before any curl example**
>
> Expected while offline: `dig +short` returns empty for both names.

Open `docs/dns.md`. Current status table lists storefront and Argo CD as inactive. Re-create A records only during Phase 2 rebuild (`docs/setup/05-cloud-dns.md`).

Topic 05 apply:

```bash
terraform apply -target=module.ingress_edge -target=module.dns
terraform output ingress_static_ip
terraform output dns_name_servers
```

Then `gcloud dns record-sets list --zone=biroltilki-art --filter='type=A'`.

Topic 06 Ingress annotations (from the setup guide): `kubernetes.io/ingress.class: gce`, `kubernetes.io/ingress.global-static-ip-name` bound to the Terraform address name, `networking.gke.io/managed-certificates` bound to the CR name. Files: `gitops/bootstrap/argocd/ingress.yaml`, `gitops/bootstrap/argocd/managed-certificate.yaml`.

> **Practice — Separate edge mechanism from journey SLO**
>
> `curl -I https://boutique.biroltilki.art` returning 200 (when live) proves TLS and routing. Browse availability SLO is still Chapter 9.

Troubleshooting in dns.md: empty `dig` means NS not delegated; TLS stuck Provisioning means DNS not pointing at the LB IP; cert Active but 404 means Ingress rules (topic 06 / 12).

`docs/bootstrap.md` validation after full bootstrap still shows `dig` and `curl` against both names. After 2026-07-04 those commands are teardown checks: empty lists, inactive names — not a regression of the book.

## 4. Test the design under failure

### Independent control failure — Certificate provisioning with no delegated zone

> **Practice — Diagnose TLS that never becomes Active**
>
> Operators applied Ingress and ManagedCertificate, skipped registrar NS, and waited on “Provisioning.”

**Severity:** medium-high; no user journey can start; teams may disable TLS to “unblock demo.”  
**Plausible harm:** HTTP-only shop; browser warnings; later Cloud Armor and uptime checks never attach to HTTPS.  
**Potential blast radius:** both public hostnames; every later smoke in topic 16.  
**Bounded by:** topic 05 validation `dig +short`; dns.md registrar steps; teardown deleting records before IP release.  
**Primary principles:** Git is the deploy authority (DNS zone in Terraform); Teardown is a production control; Lived evidence beats scaffold (screenshots of HTTPS are inactive).

#### Diagnosis

Managed certificates are not a GitOps substitute for public DNS. The control plane can show Ingress created while the internet still resolves nothing. Calling that “edge complete” is theater.

#### Correction

Delegate NS, wait for both names to match reserved IPs, then wait for ManagedCertificate Active. On teardown, follow `docs/teardown.md` so names go inactive on purpose.

That correction changes later decisions:

- Chapter 6’s Argo CD UI hostname is this edge, not a second DNS product.
- Chapter 8’s uptime checks probe these URLs.
- Chapter 15 must treat leftover forwarding rules and global IPs as reliability toil.

## 5. Production reality

### Common errors

#### Dual DNS authority

A records at the registrar plus Cloud DNS NS produce intermittent `dig` results and certificates stuck in Provisioning. Pick one authority.

#### Sharing one IP in docs while Terraform reserved two

Lived smoke (`docs/setup/16-smoke-validation.md`) compares `boutique.biroltilki.art` to `boutique-ingress-ip` and Argo to `argocd-ingress-ip`. `docs/dns.md` still describes host-based routing on one IP. On rebuild, believe Terraform outputs, then update the narrative if the module still emits a single address.

#### Hand-made TLS Secrets in the `boutique` namespace

Kyverno and ESO exist to stop that. ManagedCertificate CRs renew. Literal `tls.crt` in Git is a secret leak and a rotation failure.

#### Treating inactive `dig` as an incident after teardown

`docs/dns.md` current status table is the expected offline state. Chapter 10’s uptime runbook says the same. Empty `dig` is a passing Phase 8 check.

## 6. What changed

| Before | After |
| --- | --- |
| Ephemeral LB IPs. | `ingress-edge` global addresses. |
| Registrar-only records. | Cloud DNS zone in Terraform plus NS delegation. |
| Manual cert files. | GKE ManagedCertificate + Ingress annotations. |
| URLs implied the shop was up. | Inactive DNS is documented and required after destroy. |

## 7. What You Learned

Topics 05–06 put Cloud DNS, static IPs, GCE Ingress, and Google-managed TLS on a recoverable edge. Registrar delegation is operator work Terraform cannot perform. After destroy, inactive DNS is a passing teardown check. HTTPS 200 is not browse SLO success.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| DNS reference | `docs/dns.md` | Inactive status; delegation; validation |
| Setup 05–06 | `docs/setup/05-cloud-dns.md`, `06-ingress-tls.md` | Lived commands |
| Modules | `terraform/modules/dns`, `ingress-edge` | Zone, A records, global address |
| Ingress CRs | `gitops/bootstrap/argocd/ingress.yaml`, `managed-certificate.yaml` | Edge manifests |

> **Independent Practice — Choose apex vs subdomain delegation**
>
> `docs/dns.md` notes subdomain-only delegation versus apex. The lived zone was `biroltilki.art`.

1. What blast radius does apex NS change have for unrelated records on the domain?
2. What evidence would justify a `boutique.biroltilki.art` delegated subdomain instead?
3. After teardown, which `dig` result is success?
4. How would a leftover A record at the registrar violate one-authority?

Do not curl inactive names and call the platform down as an incident. The platform is supposed to be down.
