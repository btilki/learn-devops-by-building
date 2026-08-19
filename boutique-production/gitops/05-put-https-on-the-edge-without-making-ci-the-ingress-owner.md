# 5 — Put HTTPS on the Edge Without Making CI the Ingress Owner

A pipeline that `kubectl apply -f ingress.yaml` owns the edge. The next outage then belongs to whoever last ran the job, not to Git. This chapter is **M1 (Milestone 1)**: prove HTTPS through **ACM (AWS Certificate Manager)** on an **ALB (Application Load Balancer)** while **CI (Continuous Integration)** still has no cluster credentials.

> How do you expose boutique **DNS (Domain Name System)** over TLS so Argo, Grafana, and the storefront can exist later — without making the pipeline the Ingress controller?

## 1. The unsafe starting state: CI as the edge operator

After Topic 04, nodes are Ready (when the cluster exists). The temptation is to apply a tutorial Ingress from the laptop or from GitLab “just to see 200.” That writes Load Balancers that Terraform does not know, skips **IRSA (IAM Roles for Service Accounts)**, and teaches the team that Git is optional.

ADR-0003 already chose ACM on ALB as primary public **TLS (Transport Layer Security)**. ADR-0004 already locked hostnames. Topic 05 (`docs/setup/05-ingress-dns-tls.md`) implements those ADRs with three platform charts: AWS Load Balancer Controller, external-dns, cert-manager.

**Lived** as M1. After teardown, hostnames are **inactive**. The Git values still contain the pilot account’s role ARNs and VPC ID — evidence of what ran, not a live edge.

## 2. The production model: controllers reconcile AWS from cluster objects

> *Theory — GitOps-ready edge, Helm-first bootstrap*
>
> Install ingress, DNS, and certificate controllers with IRSA so Kubernetes objects create ALBs and Route53 records; keep cert-manager present but not the public issuer; do not let CI apply Ingress.

Topic 05 installs with Helm first. Argo **CD (Continuous Delivery)** adopts the same values paths in Topic 06. That is a bounded bootstrap exception: humans follow the Setup Guide; **CI** still never applies.

The data path is:

```text
Internet → ALB (ACM TLS terminate) → Ingress → Service → Pod
Ingress annotations → external-dns (IRSA) → Route53
```

cert-manager is installed for platform readiness. It is not the primary path for `boutique.biroltilki.art`.

## 3. How this repository implements the edge

> **Practice — Bind IRSA in the values files (read-only today)**
>
> Open `gitops/platform/aws-load-balancer-controller/values.yaml`, `gitops/platform/external-dns/values.yaml`, and `gitops/platform/cert-manager/values.yaml`. Match them to Terraform outputs named in `docs/setup/05-ingress-dns-tls.md` Step 5.1.

### AWS Load Balancer Controller

```11:25:gitops/platform/aws-load-balancer-controller/values.yaml
clusterName: "boutique-eks-gitops"
region: "eu-central-1"
vpcId: "vpc-0e62f0ba117cc7846"

serviceAccount:
  create: true
  name: aws-load-balancer-controller
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::868480224481:role/boutique-eks-gitops-aws-lb-controller"

replicaCount: 2

# Chart appVersion should resolve to 2.11.x — confirm with: helm show chart eks/aws-load-balancer-controller --version 1.11.0
image:
  tag: v2.11.0
```

**Lived.** Pins match `docs/versions.md` (controller v2.11.0, chart 1.11.0). The ApplicationSet later installs chart `1.11.0` at sync wave 10 (`gitops/apps/platform-apps/applicationset.yaml`).

### external-dns

```9:33:gitops/platform/external-dns/values.yaml
provider: aws
policy: sync
registry: txt
txtOwnerId: boutique-eks-gitops

domainFilters:
  - "biroltilki.art"

# Restrict to our hosted zone (recommended)
zoneIdFilters:
  - "Z0450359HEFSZWRHZ73V"

sources:
  - ingress
  - service

aws:
  region: eu-central-1
  zoneType: public

serviceAccount:
  create: true
  name: external-dns
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::868480224481:role/boutique-eks-gitops-external-dns"
```

**Lived.** `policy: sync` means external-dns will delete records it owns when Ingress goes away — required for teardown (Chapter 14) and dangerous if `txtOwnerId` collides with another controller.

### cert-manager is present, not primary

```1:7:gitops/platform/cert-manager/values.yaml
# cert-manager — GitOps values
# Setup Topic 05 · pin v1.16.x (docs/versions.md)
# Public TLS for Boutique/platform uses ACM on ALB (ADR-0003).
# cert-manager is installed for platform readiness / future issuers — not primary public TLS.

crds:
  enabled: true
```

**Lived** as an installed controller. No ClusterIssuer for public boutique hosts in v1. `docs/dns-and-tls.md` (created in Topic 05) maps hostname → ACM.

### Smoke Ingress then delete it

Topic 05 uses `examples/smoke-ingress.yaml` to prove M1: an HTTPS hostname under `*.boutique.biroltilki.art` via ACM+ALB. The smoke object is temporary. Leaving it creates an extra ALB hour. Boutique hostnames arrive in Topic 09 overlays, not here.

> **Practice — Explain why CI is not in this chapter’s command list**
>
> Read Topic 05’s Helm install commands in `docs/setup/05-ingress-dns-tls.md`. They run on the operator workstation. List what would break ADR-0001 if those commands moved into `.gitlab-ci.yml`.

Platform ApplicationSet wave 10 will own these charts after Topic 06. Until then, Helm is the bootstrap. Either way, Git holds the values; CI does not hold kubeconfig.

`docs/dns-and-tls.md` is the operator map Topic 05 creates:

```7:16:docs/dns-and-tls.md
## Locked hostnames

| Hostname | Purpose | TLS |
|----------|---------|-----|
| `argocd.boutique.biroltilki.art` | Argo CD UI | ACM on ALB |
| `grafana.boutique.biroltilki.art` | Grafana | ACM on ALB |
| `dev-boutique.biroltilki.art` | Boutique storefront (dev) | ACM on ALB |
| `stage-boutique.biroltilki.art` | Boutique storefront (stage) | ACM on ALB |
| `boutique.biroltilki.art` | Boutique storefront (prod) | ACM on ALB |
| `smoke.boutique.biroltilki.art` | Temporary M1 smoke (Topic 05) | ACM on ALB |
```

**Lived** as the M1 contract; **inactive** now. Smoke is listed so you remember to delete it. Leaving `smoke.boutique.biroltilki.art` is an extra ALB and a DNS name that is not in ADR-0004’s locked production set — it is a test fixture.

`docs/architecture/06-network-design.md` restates the ingress path as Internet → ALB (ACM TLS terminate) → Ingress → Service → Pod, with east-west ClusterIP and no mesh. After teardown you cannot curl those hosts; you can still reject an MR that adds a fourth public hostname without an ADR.

## 4. Test the design under failure

**Scenario:** ACM certificate is ISSUED but Ingress annotations omit `certificate-arn` and `listen-ports HTTPS`.

**Severity:** users hit HTTP or a default cert; M1 is false.  
**Plausible harm:** browser warnings; traffic on 80; storefront appears “up” on an unencrypted listener.  
**Potential blast radius:** every hostname sharing that ALB (smoke, later Argo/Grafana/Boutique).  
**Bounded by:** ADR-0003, locked DNS (ADR-0004), Setup 05 validation (`curl -I https://…`), later Kyverno does *not* check Ingress TLS — operators must.  
**Primary principles:** Git is the only deploy authority; teardown after the pilot is required; one cluster and three namespaces are a cost decision, not isolation.

### Diagnosis

`kubectl get ingress -A` shows ADDRESS but `curl -I https://host` fails TLS or redirects wrongly. ALB listener is 80 only. ACM ARN in annotations does not match `terraform output acm_certificate_arn`. After teardown, diagnosis is historical: Appendix T and the values files.

### Recovery

Patch Ingress annotations in Git (or the smoke example during M1), wait for the controller to attach the ACM listener, re-curl. Do not “fix” TLS by pointing CI at `kubectl apply`. If the certificate SAN set is wrong, that is an ADR-0004 / `module.dns` change, not an Ingress comment.

`docs/runbooks/ingress.md` is the day-2 form of M1: curl, dig, Ingress ADDRESS, ACM on listener, target health, pods, LB controller, external-dns logs. After teardown, `dig` for those names should *not* point at an ALB you still own. If it does, M4 is incomplete.

## 5. What You Learned

The edge is ACM+ALB+external-dns, with cert-manager installed and unused for public boutique TLS. You can now walk Topic 05 and the three `gitops/platform/` charts as M1, and you can say CI was never the Ingress owner.

### Durable outputs

- Setup: `docs/setup/05-ingress-dns-tls.md`
- ADRs: `docs/adr/0003-tls-acm-alb.md`, `docs/adr/0004-dns-hostname-scheme.md`
- Values: `gitops/platform/aws-load-balancer-controller/`, `external-dns/`, `cert-manager/`
- Mapping: `docs/dns-and-tls.md`, `examples/smoke-ingress.yaml`

> **Independent Practice — Choose DNS-01 without breaking ADR-0003**
>
> A colleague wants Let’s Encrypt via cert-manager DNS-01 for `boutique.biroltilki.art`. Write the change list (ClusterIssuer, Ingress tls block, ACM annotation removal, external-dns race). Then either refuse with ADR-0003 or define a *new* ADR that replaces 0003 and names the failure modes Topic 05 avoided. Do not implement it in this exercise.

Topic 05 M1 validation is HTTPS to the smoke host, then delete smoke. Controllers remain. Argo/Grafana/Boutique Ingresses come later and reuse the same ACM ARN annotation pattern.

`examples/smoke-ingress.yaml` is the M1 fixture. It is not a Boutique overlay. Leaving it after M1 is extra ALB spend and a hostname outside the locked production set except the documented smoke name.

## Next

Chapter 6 bootstraps Argo CD as the only deployer, with prod manual sync as the operational expression of ADR-0001.
