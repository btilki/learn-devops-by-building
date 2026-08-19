# 3. Lock Design With ADRs Before Credentials Exist

Credentials make bad architecture expensive to unwind. This chapter locks the lived **ADRs (Architecture Decision Records)** 0001–0012 and the architecture series 01–08 *before* Topic 03 creates a cluster identity. Scaffold ADRs 0013–0017 appear here only as a map; Chapter 16 treats them as unproven.

The production question is:

> Which decisions must be written while the subscription is still empty, and which later “hardening” files must not rewrite those decisions in silence?

## 1. Unsafe starting state

The unsafe default is to apply Terraform with defaults, then write ADRs that describe whatever Azure returned. That produces a keyless-looking supply chain on a key-based verifier, a “prod cluster” that is a namespace, and a logging bill from Container Insights nobody asked for.

This repo writes ADRs as accepted records with Context → Decision → Consequences. Architecture docs 01–08 supply requirements, context, components, flows, network, security, and **DR (disaster recovery)** honesty. Together they are the design lock.

## 2. The production model: decisions as blast-radius contracts

> *Theory — ADR-before-credentials*
>
> This model enables identity, registry, and pipeline work to inherit isolation, signing, and teardown choices instead of inventing them under a live control plane.

An ADR is not a blog post. It is a constraint later topics must obey. If Topic 09 signed keylessly while ADR-0005 requires `--tlog-upload=false`, the admission policy would be theatre.

The architecture index (`docs/architecture/README.md`) states maturity: **production pilot** on a **single** AKS cluster. It does not claim multi-region HA.

## 3. How this repository implements the lock

> **Practice — Summarize each lived ADR in one teaching sentence**
>
> Open `docs/adr/README.md` and `docs/adr/0001-azure-cloud-provider.md` through `0012-loki-in-cluster-logging.md`. For each, keep one sentence you could defend in a change review.

### Lived ADRs 0001–0012

| ADR | Decision | Teaching sentence |
|-----|----------|-------------------|
| 0001 | Azure only | Native Workload Identity, Key Vault **CSI (Container Storage Interface)**, and ADO federation are the point of the pilot — not multi-cloud portability. |
| 0002 | One AKS cluster, three namespaces | `boutique-prod` shares blast radius with dev; it is not a production estate. |
| 0003 | Kyverno admission, not Azure Policy for Kubernetes | Registry allowlist, deny `:latest`, `verifyImages`, and Pod Security baseline are cluster-native and unit-testable. |
| 0004 | Argo CD GitOps, app-of-apps | Dev auto-sync; stage/prod manual sync; Git remains desired state. |
| 0005 | Cosign 2.2.4 **key-based**, `--tlog-upload=false` | Kyverno sets `ignoreTlog` / `ignoreSCT`. This is **not** the EKS sister’s keyless Fulcio path. |
| 0006 | Kustomize for Boutique | Digest pins and env ingress without forking Helm charts; upstream refresh is manual. |
| 0007 | No service mesh in v1 | Supply chain and GitOps depth beat mTLS theatre on a solo cluster. |
| 0008 | ADO environment approval for prod | Human gate without CODEOWNERS; stage is manual Argo only. |
| 0009 | Mirror upstream v0.10.5 | Images come from Google Artifact Registry; this repo does not build Boutique from source. |
| 0010 | Destroy ACR on teardown | Cost stop and secret-image stop; rebuild must re-mirror. |
| 0011 | Region `germanywestcentral`, Dsv6 SKUs | Lived apply hit DSv5 quota 0; Dsv6 was the tested fallback — pins follow evidence. |
| 0012 | In-cluster Loki, no Log Analytics on the default path | Ingestion cost would dominate the stack; `diagnostics` module exists but is not wired. |

ADR-0005 is the supply-chain hinge. Quote the decision:

```text
Sign with cosign 2.2.4 using a key pair stored in Key Vault.
Pipeline uses --tlog-upload=false. Kyverno sets ignoreTlog: true
and ignoreSCT: true.
```

The EKS sister signs keylessly against a transparency log. Copying that command into this pipeline would make Kyverno deny every image unless someone also flipped `ignoreTlog`. Honest teaching states the difference instead of “use cosign.”

ADR-0011 is the other honesty check. Original design preferred Dsv5. Lived `terraform apply` returned `ErrCode_InsufficientVCPUQuota` for DSv5 while Dsv6 quota was 10. The ADR was **amended**. Versions and Terraform follow the amendment, not the first sketch.

> **Practice — Map architecture 01–08 to those ADRs**
>
> Open `docs/architecture/01-requirements.md` through `08-resilience-and-dr.md` and name which ADR each document depends on.

**01 Requirements.** FR-01–FR-04 demand Terraform foundation, AKS + identities, GitOps platform, and ADO mirror/scan/sign. Derived requirements DR-01–DR-05 force ACR mirror, busybox/redis pin (deny `:latest`), DNS delegation before TLS, ADO prod approval, digest pins. Boutique is 11 services plus redis-cart and loadgenerator from `us-central1-docker.pkg.dev/google-samples/microservices-demo`.

**02 System context.** Actors are platform engineer, developer, demo user, Let's Encrypt, Google Artifact Registry. Users never pull Google images at runtime — only ACR after mirror/sign.

**03 Component design.** NGINX is the single north-south entry. Kyverno admits Boutique namespaces. Terraform modules listed: resource-group, networking, dns, diagnostics (unwired), aks, acr, key-vault, identities, ado-federation. Ceiling: full Boutique × 3 namespaces; the lived test often ran a slim storefront for pod capacity.

**04 Data flows.** Request flow terminates TLS at NGINX. Supply-chain sequence: pull GAR → push ACR → Trivy @digest → cosign @digest → Git overlay → Argo → Kyverno → pull @digest. Order rule: scan before sign; sign the scanned digest.

**05 Deployment flow.** Same digest promoted; prod requires ADO approval plus manual Argo sync. Rollback is Git revert of digest pins. After Phase 14 destroys ACR, rollback to an old digest requires the image still exist or a re-mirror.

**06 Network design.** VNet `10.0.0.0/16`, AKS subnet `10.0.0.0/20`, service CIDR `10.1.0.0/16`, Azure CNI, one Standard Load Balancer, five hostnames on one ingress IP.

**07 Security architecture.** Trust zones from Internet → edge TLS → workloads → control plane → ACR/Key Vault. Kyverno must match `--tlog-upload=false`. Blast radius table: a Boutique pod can still reach cluster network until Topic 15 NetworkPolicies (scaffold) enforce.

**08 Resilience and DR.** **RTO (Recovery Time Objective)** 4–8 hours rebuild-from-Git. **RPO (Recovery Point Objective)** 0 for Terraform state with blob versioning; Redis cart is ephemeral. Multi-region is out of scope. Rebuild order ends with CI mirror because ACR is gone.

Scaffold ADRs **0013–0017** (scaffold-first Phase 15+, SPDX attestations, Falco, namespace/KV hardening, optional ZAP) must not be presented as lived. They inherit 0001–0012; they do not replace them.

ADR-0007 (no mesh) and the ROADMAP out-of-scope list are the same refusal: WAF, Front Door, DDoS, private AKS, HSM-backed keys, Azure Policy duplicate of Kyverno. An ADR that is missing is sometimes the decision. Do not “complete” the architecture by adding Istio in a PR without a new ADR that accepts the ops cost.

`ARCHITECTURE.md` §15 tradeoffs table is the executive version of 0002, 0003, 0005, 0009, and 0010. If a PR changes signing to keyless, that table and ADR-0005 and Kyverno `02` must move together.

Component → repo → setup map at the end of `ARCHITECTURE.md` is the routing table for the rest of this book: bootstrap state is Topic 01, VNet/DNS Topic 02, AKS/ACR/KV Topic 03, and so on through teardown Topic 13. Chapter numbers in the manuscript are not those topic numbers; the map prevents the mix-up.

## Architecture files this chapter requires

Keep these open together; they are the lock:

- `docs/architecture/01-requirements.md` — FR-01–FR-04, DR-01–DR-05, Boutique inventory
- `docs/architecture/02-system-context.md` — GitHub, ADO, GAR, Let's Encrypt, no Azure Repos
- `docs/architecture/03-component-design.md` — NGINX north-south, module list
- `docs/architecture/04-data-flows.md` — scan before sign
- `docs/architecture/05-deployment-flow.md` — ADO approval on prod
- `docs/architecture/06-network-design.md` — CIDRs and five FQDNs
- `docs/architecture/07-security-architecture.md` — `ignoreTlog` must match signing
- `docs/architecture/08-resilience-and-dr.md` — rebuild includes Topic 09 because ACR dies

ADR-0007 (no mesh) is as important as ADR-0003 (Kyverno). A PR that adds Istio “for mTLS” without a new ADR is an unlock of the lock.

Limits: ADRs 0013–0017 are indexed here so you do not miss them; they are not lived. Architecture 09–11 (layout, observability, cost) are taught in Chapters 2, 13, and 15. This chapter’s job is 01–08 plus 0001–0012.

## 4. Test the design under failure

### Independent control failure — Import keyless signing from the sister repo

> **Practice — Reject a copied Fulcio pipeline**
>
> A well-meaning PR replaces `cosign sign --key ... --tlog-upload=false` with keyless signing “like boutique-eks-gitops.” Kyverno still has `ignoreTlog: true` and a public key block.

**Severity:** high; admission and CI no longer verify the same claim.  
**Plausible harm:** unsigned-looking or differently attested images reach AKS, or every deploy fails, prompting someone to disable `verifyImages`.  
**Potential blast radius:** all Boutique namespaces on the shared cluster.  
**Bounded by:** ADR-0005, Kyverno `02-verify-image-signatures.yaml`, `versions.yaml` `cosign_sign_args`.  
**Primary principles:** explicit contracts, identity is digest not tag, Git is the deploy authority, lived evidence beats scaffold.

#### Diagnosis

Keyless signing authenticates a different root (Fulcio/Rekor). This platform’s verifier is a PEM in Git plus `ignoreTlog`. Mixing roots is not “more secure.” It is an unverified chain.

#### Correction

Keep key-based signing until a new ADR changes both the pipeline *and* Kyverno *and* key-rotation runbooks together. Cross-reference the EKS book as a different honest choice, not a drop-in.

## Production reality

**Best Practice:** write ADRs before the first secret exists.

**Production Practice:** amend ADRs when Azure returns a different fact (quota, issuer format). ADR-0011’s Dsv6 amendment and ado-federation’s Entra issuer comments are lived corrections. A frozen wrong ADR is worse than no ADR.

Architecture 08’s rebuild order is an ADR-0010 consequence: you cannot restore a digest that died with ACR. DR planning that assumes registry retention contradicts a signed decision.

### Common errors

- Treating ADR status “Accepted (scaffold)” as “Accepted (lived).”
- Adding Azure Policy “for compliance” while ADR-0003 forbids the duplicate in v1.
- Copying EKS keyless settings into Kyverno because a sister README said cosign.

## 5. What You Learned

ADRs 0001–0012 lock cloud, isolation, admission, GitOps, key-based cosign, Kustomize, no mesh, ADO prod gate, mirror-not-build, destroy ACR, SKU evidence, and Loki-not-Log-Analytics. Architecture 01–08 make those decisions operational. Scaffold ADRs wait for Chapter 16.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| ADR index | `docs/adr/README.md` | 0001–0017 status |
| Lived decisions | `docs/adr/0001-*.md` … `0012-*.md` | Constraints before credentials |
| Architecture series | `docs/architecture/01-` … `08-` | Requirements through DR |
| Executive summary | `ARCHITECTURE.md` | Component → repo → setup map |

## What changed

| Before | After |
|--------|--------|
| Cloud and isolation were implicit. | **ADR-0001 Azure-only; ADR-0002 one cluster.** |
| Cosign meant “whatever the sister repo did.” | **ADR-0005 key-based `--tlog-upload=false`.** |
| Logging defaulted to Azure Monitor. | **ADR-0012 Loki; diagnostics unwired.** |
| SKUs were a first sketch. | **ADR-0011 records the Dsv6 quota amendment.** |

> **Independent Practice — Write the missing sentence for ADR-0002**
>
> A stakeholder asks for “prod on its own cluster for the same budget.” Using ADR-0002 and architecture 08, write the consequence paragraph you would add if you *accepted* multi-cluster. Then write why this pilot *rejected* it. Do not apply Azure.
