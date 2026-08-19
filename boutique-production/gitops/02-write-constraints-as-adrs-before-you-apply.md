# 2 — Write Constraints as ADRs Before You Apply

An unwritten constraint dies at the first outage. Someone will add `:latest` “just for bootstrap,” widen the GitLab role “so the pipeline can sync,” or turn on prod auto-sync “because it is faster.” **ADRs (Architecture Decision Records)** exist so those moves require a recorded reversal, not a hallway agreement.

> How do you freeze digest-only GitOps, single-cluster namespaces, ACM-on-ALB TLS, locked hostnames, and on-cluster observability *before* Terraform creates a billable cluster?

## 1. The unsafe starting state: architecture as a slide

`docs/architecture/` can describe a beautiful system and still leave apply-time freedom. If the only artifact is a diagram, the implementer will solve the first IAM error by granting `eks:*` to **CI (Continuous Integration)**. If hostnames are “whatever works,” **ACM (AWS Certificate Manager)** **SANs (Subject Alternative Names)** and Ingress annotations will drift. If observability is “we will add CloudWatch later,” the cost model is already false.

Topic 02 (`docs/setup/02-repo-foundation.md`) therefore authors ADRs 0001–0005 while **AWS (Amazon Web Services)** spend is still zero. That order is the production control.

## 2. The production model: decisions that bind later topics

> *Theory — Constraint-first ADRs*
>
> Record the deploy authority, isolation claim, edge TLS, DNS scheme, and observability boundary as accepted decisions before any apply, so later topics implement constraints instead of rediscovering them.

The architecture index lists the first five as the lived decision set:

```20:26:docs/architecture/README.md
## Architecture Decision Records

| ADR | Decision |
|-----|----------|
| [ADR-0001](../adr/0001-digest-only-gitops.md) | Digest-only GitOps; CI never deploys to cluster |
| [ADR-0002](../adr/0002-single-cluster-namespaces.md) | Single cluster; namespace environments |
| [ADR-0003](../adr/0003-tls-acm-alb.md) | Public TLS via ACM + ALB |
| [ADR-0004](../adr/0004-dns-hostname-scheme.md) | Locked boutique hostnames |
| [ADR-0005](../adr/0005-observability-on-cluster.md) | Prom/Loki/Grafana/AM email; no CW/PD/OTel |
```

**Lived.** ADRs 0006–0010 exist; 0006 is lived with Topic 10. 0007–0010 are **scaffold** (Chapter 15).

Requirements in `docs/architecture/01-requirements.md` are the FR table those ADRs serve: Terraform foundation (FR-01), ingress/DNS/TLS (FR-02), Argo GitOps with manual prod (FR-03), Kyverno/ESO/NetworkPolicy (FR-04), on-cluster observability (FR-05), Boutique+CI+promote+canary (FR-06–09), checklist and teardown (FR-10–11).

## 3. How this repository implements the constraints

> **Practice — Read ADRs 0001–0005 as apply blockers**
>
> Open `docs/adr/0001-digest-only-gitops.md` through `0005-observability-on-cluster.md`. For each, write the sentence a reviewer would use to reject a conflicting **MR (Merge Request)**.

### ADR-0001 — Git is the only deploy authority

```7:16:docs/adr/0001-digest-only-gitops.md
## Context

We need immutable, auditable releases for Online Boutique on EKS. Tag-based deploys (`:latest`, moving tags) and CI `kubectl apply` / `argocd sync` create drift, weaken audit trails, and couple pipeline credentials to the cluster API.

## Decision

- **Git is the only deploy authority.** Desired state lives in this repo under `gitops/`.
- Workload images are referenced by **digest only** (`image.digest`); never `:latest`.
- GitLab CI may build, scan, sign, and open MRs that patch digests — it must **not** deploy to the cluster.
- Argo CD reconciles Git → cluster (app-of-apps + ApplicationSet). Prod sync is **manual**.
```

**Lived.** Every later chapter is an implementation of this page. Bootstrap still needs a one-time **ECR (Elastic Container Registry)** digest push (Topic 09) before the **CI** loop; that exception is recorded here, not hidden in a script.

### ADR-0002 — One cluster, three namespaces

```7:24:docs/adr/0002-single-cluster-namespaces.md
## Context

`dev`, `stage`, and `prod` need isolation sufficient for a production **pilot**, under a cost-sensitive short test window (single NAT, one EKS).

## Decision

Run **one** EKS cluster in `eu-central-1`. Environments are **namespaces** plus separate Git paths `gitops/envs/{dev,stage,prod}/`, differentiated by:

- Hostname scheme (ADR-0004)
- Sync policy (prod manual)
- CODEOWNERS on prod digests
- NetworkPolicy baseline

## Consequences

- **Positive:** Lower cost; simpler Terraform; faster pilot teardown.
- **Negative:** Shared blast radius (node/control-plane failure affects all envs); not multi-account isolation.
```

**Lived.** `docs/architecture/02-system-context.md` restates the environment table: dev auto-sync, stage auto/controlled with canary, prod manual + CODEOWNERS `@btilki`. Say “namespaces on one cluster” whenever you say “environments.”

### ADR-0003 and ADR-0004 — Edge is ACM + locked DNS

Public **TLS (Transport Layer Security)** is **ACM** on **ALB (Application Load Balancer)**. cert-manager is installed for platform readiness, not as the primary issuer for boutique hostnames. That choice removes DNS-01 races at the cost of AWS coupling.

ADR-0004 locks the names under Route53 zone `biroltilki.art`: `argocd.boutique.biroltilki.art`, `grafana.boutique.biroltilki.art`, `dev-boutique.biroltilki.art`, `stage-boutique.biroltilki.art`, and prod storefront `boutique.biroltilki.art`. Platform hosts use `*.boutique.biroltilki.art`; env storefronts use `{env}-boutique` except prod.

**Lived** during the pilot; **inactive** after teardown. Renames are treated as out of scope because ACM SANs, Ingress, and docs would all churn. `docs/dns-and-tls.md` later maps those names to ACM SANs: primary `boutique.biroltilki.art`, plus `*.boutique.biroltilki.art`, `dev-boutique.biroltilki.art`, and `stage-boutique.biroltilki.art`. That mapping is why ADR-0004 says treat the set as locked.

### ADR-0005 — Signals stay on the cluster

```13:16:docs/adr/0005-observability-on-cluster.md
- **Metrics / UI / alerts:** kube-prometheus-stack (Prometheus, Grafana, Alertmanager)
- **Logs:** Grafana Loki
- **Alert routing:** Alertmanager → **email** (SMTP credentials via ESO)
- **Out of v1:** CloudWatch, PagerDuty, OpenTelemetry / Tempo traces
```

**Lived.** The cost model and FR-05 are the same decision. Self-operated retention on `m6i.large` is the accepted operational burden.

### Architecture docs 01–10 bind the rest

You do not need to re-read every deep doc before apply, but you must know they exist as the expansion of these ADRs:

| Doc | Binds |
|-----|--------|
| `01-requirements.md` | FR/NFR/constraints/assumptions |
| `02-system-context.md` | Actors, env table, platform vs app |
| `03-component-design.md` | Inventory: VPC, EKS, ECR, controllers, Boutique |
| `04-data-flows.md` | Request, GitOps+CI, Terraform, secrets |
| `05-deployment-flow.md` | Digest MR → promote → manual prod → revert |
| `06-network-design.md` | Single NAT, private nodes, no mesh |
| `07-security-architecture.md` | Trust zones; CI has no `eks:*` |
| `08-resilience-and-dr.md` | Hours RTO; NAT SPOF; no multi-region |
| `09-observability.md` | Email critical path; no traces |
| `10-cost-model.md` | Teardown mandatory |

> **Practice — Reject a conflicting change with an ADR citation**
>
> Take this proposed MR title: “CI: argocd sync prod after digest merge.” Cite ADR-0001 and `docs/architecture/05-deployment-flow.md`. State what the pipeline is allowed to do instead.

`docs/architecture/03-component-design.md` inventories why each box exists: single NAT for cost-controlled egress, ECR for immutable digests and scan-on-push, GitLab OIDC for keyless CI, LB controller for ALB+ACM, Argo for pull sync, Kyverno for admission. `docs/architecture/04-data-flows.md` adds the four sequences you will reuse: user request, GitOps+CI, Terraform state, secrets. If an MR proposes a fifth sequence (CI → kubectl), it contradicts both the ADR and the data-flow document.

`docs/architecture/08-resilience-and-dr.md` is the failure table that later chapters specialize: node loss, NAT AZ failure, GitOps desync, bad digest, state lock, observability down, ACM issue, Kyverno deny storm. Reading it before apply means you already know single-NAT is an accepted SPOF.

## 4. Test the design under failure

**Scenario:** Unsigned constraint — CI granted cluster deploy to “unblock M3.”

**Severity:** deploy-authority collapse.  
**Plausible harm:** a pipeline token becomes a second production principal; Git history no longer explains cluster state; a failed job can still have applied a partial sync.  
**Potential blast radius:** all namespaces the Argo / kubeconfig identity can write, including prod.  
**Bounded by:** ADR-0001, GitLab OIDC role scoped to ECR (Chapter 4), `.gitlab-ci.yml` hard rules (Chapter 10), CODEOWNERS and manual prod sync (Chapters 6 and 11).  
**Primary principles:** Git is the only deploy authority; CI has ECR and Git permission, not cluster deploy permission; image identity is digest, not tag.

### Diagnosis

Search `.gitlab-ci.yml` for `kubectl`, `helm upgrade`, and `argocd sync`. Search the GitLab OIDC IAM policy for `eks:*`. If either exists, ADR-0001 is already violated regardless of README claims.

### Recovery

Remove cluster credentials from CI. Revert any direct-apply commits. Restore desired state from Git and let Argo reconcile. Record the incident against ADR-0001 rather than “fixing the pipeline.” Do not treat a successful `kubectl apply` as a recovery signal.

`docs/architecture/06-network-design.md` and `07-security-architecture.md` are the expansion of ADRs 0002–0003 into trust zones and VPC layout. Read them as ADR commentary, not as a second decision set. If they disagree with an ADR, the ADR wins until you write a new one.

## 5. What You Learned

Constraints that are not ADRs will be bargained away under time pressure. You can now map FRs in `docs/architecture/01-requirements.md` to ADRs 0001–0005 and use those records as merge blockers before any apply.

### Durable outputs

- ADRs 0001–0005: `docs/adr/0001-digest-only-gitops.md` … `0005-observability-on-cluster.md`
- Requirements and constraints: `docs/architecture/01-requirements.md`
- Context, components, flows, network, security, resilience, observability, cost: `docs/architecture/02`–`10`

> **Independent Practice — Write the rejection for a three-cluster proposal**
>
> A reviewer wants `dev`, `stage`, and `prod` as three EKS clusters “because namespaces are not isolation.” Using ADR-0002, `02-system-context.md`, and `10-cost-model.md`, write the accept/reject note. If you would accept, list the ADRs you must amend and the teardown obligation that triples. If you reject, name the residual blast radius you are still required to say out loud.

ADR-0006 is lived with Topic 10 but was not required before first apply. ADRs 0007–0010 are **scaffold** and must not be cited as lived constraints in an apply-time review of this pilot.

`docs/architecture/05-deployment-flow.md` is the ADR-0001 sequence diagram in architecture form. If a proposed pipeline stage is not on that flowchart, it is not this pilot.

## Next

Chapter 3 turns those ADRs into a repository spine: versions, CODEOWNERS, Makefile, and pre-commit — still with no AWS resources.
