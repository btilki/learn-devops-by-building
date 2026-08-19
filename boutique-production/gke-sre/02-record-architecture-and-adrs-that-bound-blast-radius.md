# 2. Record Architecture and ADRs That Bound Blast Radius

Chapter 1 named browse and checkout as the journeys. Architecture still has to say where those journeys run, what they share, and which failures are in-scope. The production question is:

> How does one private regional cluster bound blast radius in writing, without pretending namespaces are accounts?

Without recorded **ADRs (Architecture Decision Records)**, the next engineer will “fix” cost by adding a second cluster in conversation, or “fix” promotion by turning on auto-sync, while the blast radius of Redis, Binary Authorization, and a single project remains undesigned.

## 1. An inherited gap: diagrams without decisions

`ARCHITECTURE.md` is an executive summary. Sixteen sections live in `docs/architecture/overview.md`. Diagrams live in `assets/diagrams/`. That is enough surface to look complete. It is not enough if the three ADRs are unread.

The unsafe default is to treat the mermaid chart as the contract:

```text
Git → GitHub Actions (WIF) → Artifact Registry → Argo CD → Private GKE
  → HTTPS (Cloud Armor, TLS) → OTel → Cloud Monitoring → PagerDuty
```

The chart is true. It does not say that namespaces `boutique`, `argocd`, `monitoring`, `kyverno`, and `external-secrets` share one control plane, one node pool bill, and one Binary Authorization policy. A Kyverno misconfiguration or a BA enforce surprise (Chapter 14) hits every workload on the cluster.

## 2. The production model: one cluster, written limits

> *Theory — Recorded blast-radius architecture*
>
> This model enables operators to extend or refuse change from accepted ADRs rather than from a slide that shows boxes without isolation consequences.

### Isolation is a decision, not a namespace count

ADR 001:

```text
Use one GCP project (boutique-gke) and one regional private GKE cluster.
Isolate by Kubernetes namespaces, not by cluster or project.
```

Consequences are explicit: lower cost and simpler Terraform; **no hard blast-radius separation between “envs”**; patterns must translate explicitly to multi-env designs. Mitigation is documentation plus manual Argo sync and policies — not a second project hidden in naming.

**Best Practice:** Put the negative consequence in the ADR, not only the cost win.

**Production Practice:** Whenever this book says “production-style,” it means discipline on one cluster, not multi-account isolation. Series principle: namespaces on one cluster are not multi-account isolation.

### Promotion and identity are also blast-radius controls

ADR 002 prohibits long-lived GCP service account JSON keys in GitHub Secrets. **WIF (Workload Identity Federation)** issues short-lived tokens bound to the repository. A leaked key would have been project-wide. Federation bounds CI’s blast radius in time and attribute condition.

ADR 003 requires **manual** Argo CD sync even on a single cluster. Auto-sync would collapse “merged” and “live” into one event. Manual sync keeps Git as deploy authority with a human gate. Drift until sync is the accepted cost.

### Journeys sit inside a documented request path

Overview §6:

```text
User browser
  → DNS (boutique.biroltilki.art → static IP)
  → Cloud Armor (WAF / rate limits)
  → GCE Ingress (TLS termination, Google-managed cert)
  → frontend Service (boutique namespace)
  → frontend Pod
      → adservice, cartservice, checkoutservice, ...
      → cartservice → Redis (StatefulSet)
      → checkoutservice → paymentservice, emailservice, shippingservice
```

Redis is on the checkout path. Zone loss, bad deploy, Redis down, ingress/TLS failure, Kyverno/ESO down, Binary Auth misconfig, and WIF/CI failure are named in §10. Disaster recovery in §12 gives Redis **RPO (Recovery Point Objective)** &lt; 1h and **RTO (Recovery Time Objective)** &lt; 30m — targets, not proofs. Cluster rebuild RTO is hours.

## 3. How this repository implements it

> **Practice — Read the executive summary, then the ADRs**
>
> Confirm that isolation, WIF, and manual sync are accepted decisions, not backlog wishes.

Open `ARCHITECTURE.md`. Key decisions:

| Topic | Choice |
| --- | --- |
| Isolation | One cluster; namespaces `boutique`, `argocd`, `monitoring`, `kyverno`, `external-secrets` |
| Deploy | GitOps; manual Argo CD sync; digest-only images |
| Security | WIF, ESO, Kyverno, NetworkPolicy, Binary Authorization, Cloud Armor |
| SRE | Browse 99.9%, checkout 99.95%; burn alerts; runbooks per alert |

Open `docs/adr/001-single-cluster.md`, `docs/adr/002-wif-over-sa-keys.md`, and `docs/adr/003-manual-argocd-sync.md`. Status on all three: Accepted.

> **Practice — Bind diagrams to failure scenarios**
>
> Open `assets/diagrams/README.md` and the four Mermaid sources.

| File | What it bounds |
| --- | --- |
| `architecture.mmd` | Component and data-plane overview |
| `network-flow.mmd` | VPC, ingress, NetworkPolicy zones |
| `deployment-pipeline.mmd` | CI → GitOps → deploy gate |
| `sre-alert-flow.mmd` | SLO → burn alert → PagerDuty → runbook |

Screenshots in the same directory are **Inactive** validation from the lived pilot: storefront HTTPS, Argo apps, `build-scan-sign` success, Trivy failure before `trivyignore`, PagerDuty Events API V2, SLO dashboard, `make runbook-lint`, Kyverno five policies, Cloud Armor, Grafana, Cloud Trace checkout. They prove mechanisms existed. They do not prove the cluster is up today.

Overview constraints that later chapters must not silently reverse:

- Single GCP project `boutique-gke` — no dev/stage/prod project split
- Single regional GKE — isolation via namespaces only
- GCP-only — no multi-cloud abstraction
- No service mesh as default
- No custom app code — upstream Online Boutique images only
- Manual Argo CD sync
- WIF-only CI auth
- Operator-executed provisioning — Terraform and setup guides; no opaque automation scripts

Non-functionals NF1–NF4 are the SLO numbers Chapter 9 will operationalize. NF5–NF7 are digest, supply chain, and Kyverno. NF8 is private nodes and Cloud NAT. NF9 is SEV1–SEV4. NF10 is Redis/cart recoverability.

## 4. Test the design under failure

### Connected consequence — Treating namespaces as environment isolation

> **Practice — State what a BA or Kyverno failure shares**
>
> A Binary Authorization enforce surprise during Redis restore (lived, 2026-07-04) did not stay inside a “cart env.” It blocked recreation of `redis-cart` on the only cluster.

**Severity:** high; one admission policy gates every new pod.  
**Plausible harm:** checkout 5xx while restore is denied; operators soften BA for the whole project to recover one Deployment.  
**Potential blast radius:** all namespaces on `boutique-gke`; every future digest promotion.  
**Bounded by:** ADR 001’s explicit negative; platform image whitelist; break-glass DRYRUN documented in `docs/security/edge-hardening.md`.  
**Primary principles:** Namespaces on one cluster are not multi-account isolation; Git is the deploy authority; Lived evidence beats scaffold.

#### Diagnosis

Calling `boutique` vs `argocd` “prod vs tools” encourages false comfort: “only the shop is exposed.” They share nodes, BA, and often the same operator identity. ADR 001 already recorded the cost/simplicity trade. Ignoring the negative consequence is the failure.

#### Correction

Keep one cluster. Write the blast radius. Use manual sync (ADR 003) and policies as production discipline. Do not add a fake second environment in naming. Extension path is a second GCP project — listed under future enhancements, not implemented.

That correction changes later decisions:

- Chapter 3 must build private nodes knowing NAT and the VPC are shared blast radius for egress.
- Chapter 6 must install Kyverno cluster-wide before Boutique.
- Chapter 11 must whitelist platform images without exempting Boutique app images.
- Chapter 14 must treat BA-blocked restore as an architecture lesson, not a Redis-only incident.

## 5. Production reality

### Common errors

#### Treating ADR 001’s cost win as the whole decision

The negative consequence — no hard env isolation — is the reliability-relevant half. Dropping it in conversation recreates a fake multi-env estate.

#### Enabling Argo auto-sync “just on policies”

Policies are cluster-wide. Auto-syncing Kyverno is still a production change. ADR 003 does not contain a policies exception.

#### Drawing a second region on a whiteboard and calling it in-scope

Overview §16 lists multi-region as future. NF architecture is single region `europe-west1` with three zones. Zone loss is in §10; regional loss is not this book’s fail-over chapter.

#### Using architecture screenshots as live topology

`assets/diagrams/` PNGs are setup-validation captures. Mermaid `.mmd` files are the canonical diagrams. Inactive screenshots do not update when you change Terraform.

## 6. What changed

| Before | After |
| --- | --- |
| Isolation was implied by namespace names. | ADR 001 records namespace-only isolation and its cost. |
| CI keys were a bootstrap shortcut. | ADR 002 forbids JSON keys. |
| Merge meant live. | ADR 003 keeps manual sync. |
| Failures were “Kubernetes will fix it.” | Overview §10 names Redis, BA, WIF, ingress, and zone loss. |

## 7. What You Learned

Architecture is the recorded bound on blast radius: one project, one regional private cluster, three accepted ADRs, named failure scenarios, and diagrams that match Git. Namespace isolation is operational convenience. It is not multi-account tenancy. Screenshots are inactive evidence of a lived pilot.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Executive architecture | `ARCHITECTURE.md` | Stack flow and key decisions |
| Canonical design | `docs/architecture/overview.md` | 16 sections: requirements through tradeoffs |
| ADRs 001–003 | `docs/adr/` | Isolation, WIF, manual sync |
| Diagrams | `assets/diagrams/` | Mermaid sources plus lived screenshots |

> **Independent Practice — Propose a second project without rewriting ADR 001 in chat**
>
> Leadership wants “dev” on the same cluster with auto-sync “because it is not prod.”

1. Quote ADR 001’s negative consequence in your answer.
2. Decide whether auto-sync on a second Application violates ADR 003’s intent even if the first Application stays manual.
3. Name one shared control (BA, Kyverno, node pool, or Cloud Armor) that would still couple “dev” to checkout.
4. Identify what evidence would justify opening a new ADR rather than a Slack exception.

Do not invent a mesh or a second region. The repository refused both as defaults.
