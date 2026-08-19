# 1 — Charter a Production Pilot, Not a Demo Cluster

A demo cluster is provisioned to show that Kubernetes works. A production pilot is chartered to prove a deploy authority, then destroyed so the bill and the attack surface stop. The unsafe default is to leave **EKS (Elastic Kubernetes Service)** running after the screenshot, call three namespaces “environments,” and treat a README feature table as a production claim.

> How do you charter Online Boutique on one Amazon EKS cluster so Git is the only deploy authority, cost is bounded, and teardown is a milestone rather than leftover hygiene?

## 1. The unsafe starting state: a cluster that exists to exist

The usual AWS workshop path creates a cluster, applies a Helm chart from a laptop, and stops when a browser shows the storefront. That path has no digest identity, no promotion gate, no admission policy, and no ordered destroy. **CI (Continuous Integration)** often holds a kubeconfig. Environments are either one namespace with a comment or three unpaid clusters.

This repository refuses that charter. The README states the system and the honesty labels in the first screen:

```16:35:README.md
### At a glance (30 seconds)

| | |
|-|-|
| **What** | Digest-only GitOps on Amazon EKS for a scoped Online Boutique workload |
| **Hard rule** | **CI never deploys** — pipelines open digest MRs; Argo CD reconciles from Git |
| **Proven** | Multi-AZ pilot (M3+M4 PASS); AWS resources **torn down** after validation |
| **Stack** | Terraform · EKS 1.31 · Argo CD · Rollouts · Kyverno · Prom/Loki/Grafana |
| **Start reading** | Diagram below → [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) → [`docs/adr/0001-digest-only-gitops.md`](docs/adr/0001-digest-only-gitops.md) |
```

**Lived.** The public clone is the control-plane documentation and desired state. The cluster is gone.

## 2. The production model: a pilot with a closed loop

> *Theory — Production-pilot charter*
>
> Decide the workload, the deploy authority, the isolation you will not claim, the cost bound, and the destroy milestone before the first `terraform apply`.

The architecture executive summary is the charter in one paragraph:

```11:15:docs/ARCHITECTURE.md
This repository is the **operational control plane** for Online Boutique on Amazon **EKS (Elastic Kubernetes Service)**. **Git is the only authority** for what runs on the cluster. GitLab **CI (Continuous Integration)** builds, scans (Trivy), signs (cosign), and opens **MRs (Merge Requests)** that change **only image digests**. Argo CD reconciles desired state; it never receives deploy commands from CI.

Three application environments (`dev`, `stage`, `prod`) share one cluster as namespaces, isolated by NetworkPolicy, sync policy, CODEOWNERS, and manual prod sync. Public HTTPS uses **ACM (AWS Certificate Manager)** on **ALB (Application Load Balancer)**. Observability is entirely on-cluster (**Prometheus, Loki, Grafana, Alertmanager → email**). Short pilots end with **Phase 11 ordered teardown immediately after all tests** (no keep-alive). **This pilot’s AWS resources were destroyed 2026-07-19/20** (Appendix T); the live cluster is gone.
```

That is not marketing. It names what is in, what is out, and what is already destroyed. The roadmap turns the charter into milestones:

```32:41:ROADMAP.md
## Milestones

| Milestone | After phase | Definition of done |
|-----------|-------------|--------------------|
| **M1 — Cluster reachable** | 3 | EKS Ready; ACM+ALB smoke hostname under `*.boutique.biroltilki.art` |
| **M2 — Platform complete** | 6 | Argo + Kyverno/ESO/NP + Prometheus/Loki/Grafana/Alertmanager (email) live |
| **M3 — Production path proven** | 10 | Digest MR → promote → prod manual sync + canary; checklist green |
| **M4 — Clean teardown** | 11 | Workloads removed; `terraform destroy` complete; no orphan billable resources |
```

**Lived.** M1 through M4 passed. Phase 12 is scaffold authored in Git, not a fifth milestone.

## 3. How this repository implements the charter

> **Practice — Read the charter artifacts**
>
> Open `README.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md`, and `docs/architecture/10-cost-model.md`. Write one sentence for scope, one for deploy authority, one for isolation you will not claim, and one for the destroy condition.

### Scope is a storefront path, not the whole Boutique catalog

The implementation plan lists seven services plus Redis. Ads, recommendation, and email are deferred. Mesh is out. The architecture mapping table is the component inventory you will walk for the rest of this book:

```176:191:docs/ARCHITECTURE.md
## Mapping (component → repo → setup)

| Component | Repo path | Setup topic |
|-----------|-----------|-------------|
| Versions / ADRs | `docs/versions.md`, `docs/adr/` | 01, 02 |
| Remote state | `terraform/envs/prod/backend*` | 03 |
| VPC / EKS / ECR / OIDC | `terraform/modules/*` | 04 |
| Ingress / DNS / TLS | `gitops/platform/{aws-load-balancer-controller,external-dns,cert-manager}/` | 05 |
| Argo CD | `gitops/bootstrap/`, `gitops/apps/` | 06 |
| Kyverno / ESO / NP | `gitops/platform/{kyverno,external-secrets,network-policies}/` | 07 |
| Observability | `gitops/platform/monitoring/` | 08 |
| Boutique | `charts/`, `gitops/envs/` | 09 |
| GitLab CI | `.gitlab-ci.yml` | 10 |
| Promotion / canary | `docs/promotion.md`, `gitops/platform/argo-rollouts/` | 11, 12 |
| Checklist | `docs/PRODUCTION_CHECKLIST.md` | 13 |
| Teardown | `docs/runbooks/teardown.md` | 14 |
```

**Lived** for Topics 01–14. Topics 15–19 appear later in `ROADMAP.md` as Phase 12 scaffold.

### Cost is a design input, not a retrospective

The cost model is not a finance appendix. It is why there is one **NAT (Network Address Translation)** gateway, why nodes are `m6i.large`, and why teardown is mandatory:

```21:39:docs/architecture/10-cost-model.md
### 2-day pilot (48h) with teardown

| Band | Est. |
|------|------|
| Typical | **~$35–45** |
| Lean | ~$28–35 |
| Heavy pulls / extras | ~$50–70 |

## Guardrails

| Guardrail | Setting |
|-----------|---------|
| Node type | `m6i.large` (not larger unless proven need) |
| ASG max | 5 |
| NAT count | 1 |
| Log/metric retention | ≤15 days Prom; ≤7 days Loki |
| No CloudWatch Logs ingestion | On-cluster only |
| ECR endpoints | Enabled to cut NAT GB |
| Always run Phase 11 **immediately after all tests** | Mandatory — no keep-alive |
```

Leaving the stack up is the **$350–500/mo** band. The charter treats that as failure, not as “we might need it next week.”

### Honest limits are part of the charter

`docs/ARCHITECTURE.md` §15 names rejected alternatives: **CI** `kubectl` push, three clusters, cert-manager **DNS-01** as primary **TLS (Transport Layer Security)**, CloudWatch/PagerDuty/**OTel (OpenTelemetry)**, and floating tags. Each rejected option has a cost of the choice. Namespace isolation on one cluster is not multi-account isolation. **DR (Disaster Recovery)** is rebuild-from-Git in hours, not multi-region minutes.

The README feature table already splits ✅ Implemented from 🚧 Scaffold. That split is the charter’s honesty mechanism. You will use it in every later chapter.

The implementation plan (`docs/implementation/plan.md`) is the build-time companion: FR-01 through FR-11 mapped to phases, with G-01 through G-11 success indicators. You do not re-execute that plan in this book. You use it to see that teardown (G-11) was a goal from the start, not a cleanup ticket added after the bill arrived. Risks in §7.9 still matter after M4: GitLab OIDC misconfig, Kyverno breaking Rollouts, NAT/ECR cost, prod auto-sync left enabled, hostname/TLS mismatch. Those are the failure stories later chapters classify.

`docs/architecture/08-resilience-and-dr.md` separates **DR (Disaster Recovery)** (restore while intending to keep running) from teardown (intentional destroy for cost). The charter chooses teardown for short tests. Rebuild order, if you ever intend to keep running again, is remote state → Terraform apply → ingress → Argo bootstrap → platform waves → envs → verify DNS/TLS. Primary recovery is Git + Terraform, not AMI bakefiles. Redis cart state is ephemeral; there is no customer database in scope.

> **Practice — Name what the pilot refuses**
>
> From `docs/ARCHITECTURE.md` §16 and the README “Out of scope” legend, list mesh, multi-region, CloudWatch, PagerDuty, and **CI** deploy. For each, state the production question it would answer and why this pilot deferred it.

## 4. Test the design under failure

**Scenario:** Keep-alive after M3.

**Severity:** cost and identity leftover after the production path is already proven.  
**Plausible harm:** hourly EKS, NAT, and **ALB (Application Load Balancer)** charges continue; **IAM (Identity and Access Management)** roles, **ECR (Elastic Container Registry)** images, and public hostnames remain reachable; the next engineer treats an unattended cluster as production.  
**Potential blast radius:** the entire pilot account’s boutique resources (VPC, cluster, ALBs, ECR, **ACM (AWS Certificate Manager)**, Route53 records).  
**Bounded by:** Phase 11 / Topic 14 ordered teardown, cost-model guardrail “no keep-alive,” Appendix T in `docs/PRODUCTION_CHECKLIST.md`.  
**Primary principles:** teardown after the pilot is required; one cluster and three namespaces are a cost decision, not isolation; scaffold in Git is not lived proof.

### Diagnosis

If `ROADMAP.md` still says M3 PASS and Phase 11 is not ✅, the charter is incomplete. If `docs/architecture/10-cost-model.md` is unread, the operator has no bound. If DNS still resolves to an ALB after the pilot, teardown did not finish.

### Recovery

Run Topic 14 immediately. Do not “leave it for demos.” Record Appendix T. After 2026-07-19/20 that recovery already happened: AWS cloud deleted. A reader cloning today diagnoses *absence* of billables as success, not as a missing cluster.

The plan’s scope section (`docs/implementation/plan.md` §7.8) is the charter’s in/out list in table form: modules, platform, seven services, digest CI, canary, docs, teardown in; multi-region, remaining Boutique services, mesh, CloudWatch/PagerDuty/OTel, custom operators, second EKS out unless single-cluster limits hurt. Chapter 1 is that table taught as a production question.

## 5. What You Learned

A production pilot is a closed loop: declared scope, digest-only GitOps, named isolation limits, a dollar bound, four milestones, and destroy. You can now read this repository’s README, roadmap, architecture, and cost model as one charter rather than as marketing pages.

### Durable outputs

- Charter and honesty labels: `README.md`
- Milestones M1–M4 and Phase 12 scaffold status: `ROADMAP.md`
- System design summary: `docs/ARCHITECTURE.md`
- Cost guardrails and teardown order: `docs/architecture/10-cost-model.md`

> **Independent Practice — Charter a second region without pretending you have it**
>
> Your organization asks for “prod in `us-east-1` as well.” Using only this repository’s charter artifacts, write the smallest ADR-shaped note that either (a) refuses the request with the single-cluster and cost constraints, or (b) lists the new blast radius, NAT count, ApplicationSet cluster generator, and teardown obligation a second cluster would create. Do not invent Terraform. Name which README claims would become false.

README § maturity still says production **pilot**, not enterprise HA. If a slide deck upgrades that word, the charter failed even if Git did not change.

Cost-model continuous monthly band (~$350–500) is the keep-alive failure mode: EKS control plane ~$73, 3× `m6i.large` ~$250, NAT ~$35+, ALB ~$20–40. The charter’s 2-day band only exists if Chapter 14 runs.

## Next

Chapter 2 records the constraints as **ADRs (Architecture Decision Records)** 0001–0005 so the first apply cannot quietly reopen CI deploy, three clusters, or tag-based images.
