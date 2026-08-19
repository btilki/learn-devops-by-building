# 16 — Conclusion — Git Remains the Deploy Authority

You can now defend this repository as a production *pilot*, not as a demo cluster and not as multi-account **HA (High Availability)**. The lived path is digest-only GitOps on one Amazon **EKS (Elastic Kubernetes Service)** cluster: Terraform foundation, ACM-on-ALB edge, Argo **CD (Continuous Delivery)** as the only deployer, Kyverno/ESO/NetworkPolicy baseline, on-cluster signals, Helm digest overlays, **CI (Continuous Integration)** that opens digest **MRs (Merge Requests)** and never deploys, human promotion, frontend canary, a filled checklist, and ordered teardown. **M3 (Milestone 3)** and **M4 (Milestone 4)** PASS; **AWS (Amazon Web Services)** is gone. Phase 12 is **scaffold**.

## What you can defend in a design review

The sentence that must survive is still ADR-0001: Git is the only deploy authority. A pipeline that can `kubectl apply` is a design failure. A digest merge request becomes cluster state only after review and (in prod) a human sync. CODEOWNERS and manual prod sync are gates, not decoration. Image identity is digest, not tag. Namespaces on one cluster are a cost decision. Teardown is a milestone. A YAML file is not a passed test.

You can point at files, not slogans:

- Desired state: `gitops/` and `charts/`
- Foundation contract: `terraform/modules/{network,eks,ecr,dns,iam_gitlab_oidc,irsa}`
- CI contract: `.gitlab-ci.yml`, `docs/ci.md`, ADR-0006
- Promotion and rollback: `docs/promotion.md`, `docs/rollback.md`, `CODEOWNERS`
- Evidence: `docs/PRODUCTION_CHECKLIST.md` (M3) and Appendix T (M4)
- Honest remainder: Topics 15–19 labeled scaffold

You can also say what the pilot proved on 2026-07-19/20: HTTPS storefronts, digest MRs, stage and prod canary, a revert MR, Alertmanager email, then a clean destroy. You cannot say those hostnames still answer.

By chapter, that defense looks like this:

| Chapter | You can now say |
|---------|-----------------|
| 1 | This is a closed-loop pilot with a cost bound and M4 destroy. |
| 2 | ADRs 0001–0005 bind apply; CI deploy is a recorded reversal. |
| 3 | Pins, CODEOWNERS, and Makefile checks exist before AWS. |
| 4 | CI OIDC cannot call EKS; state was remote, then deleted. |
| 5 | Edge is ACM+ALB; CI never owned Ingress. |
| 6 | Argo is the only deployer; prod automated is absent. |
| 7 | Digest/ECR Enforce, ESO, default-deny — not multi-account. |
| 8 | Signals are on-cluster email, with a placeholder shop rule. |
| 9 | Overlays pin `@sha256:`; bootstrap was a one-time exception. |
| 10 | CI proposes `dev` digests; pipelines are dormant after M4. |
| 11 | Promotion copies digests; rollback is `git revert`. |
| 12 | Frontend canary is timed ALB weights; lasting abort is Git. |
| 13 | M3 is a filled checklist, not a green UI. |
| 14 | Teardown is ordered and evidenced in Appendix T. |
| 15 | Phase 12 is complete **scaffold**, not lived proof. |

## What this book refused

It refused a service mesh. It refused multi-region **DR (Disaster Recovery)**. It refused **CI** as deployer. It refused CloudWatch, PagerDuty, and OpenTelemetry in v1. It refused to call three namespaces “production isolation.” It refused to leave the cluster up after proof. It refused to upgrade Topics 15–19 into lived claims.

Those refusals are the product. They keep the blast radius and the bill inside a two-day story you can actually finish. `docs/ARCHITECTURE.md` §16 still lists second-cluster split, remaining Boutique services, and **OTel (OpenTelemetry)** as deferred — not as missing homework this title failed to invent.

Mesh would have answered east-west mTLS. This pilot answered digest promotion and pull reconciliation. Multi-region would have answered zonal loss of `eu-central-1`. This pilot answered “can we destroy on purpose.” **CI** deploy would have answered “make the merge faster.” This pilot answered “make the merge the only write to desired state.” Different questions; do not smuggle them back in during a rebuild without new ADRs.

## Sister books

*Practical SRE on Google Kubernetes Engine* (`gke-sre/`, repository `boutique-gke-sre`) asks a reliability question on a sister Online Boutique platform. *Practical DevSecOps on Azure Kubernetes Service* (`aks-devsecops/`, repository `boutique-aks-devsecops`) asks a security-program question on Azure. The three share digest discipline and GitOps. They do not share cloud, **CI** system, or the production question each title is built to answer. Cross-read when a sister platform made a different honest choice; do not merge their claims into this EKS pilot.

This title is not a fifth Northwind book. Northwind taught the vocabulary on a companion lab. This series applies that vocabulary to a lived repository and then tells you the cluster was deleted.

If you already read the Northwind GitOps chapter, you will recognize pull reconciliation, digest identity, and “review does not equal safe.” This book’s difference is the system: real Argo ApplicationSets, real CODEOWNERS, real Appendix T, real teardown. There is no `chapter-NN-start` tag and no local reconciler simulator.

## What you should do with the clone

Keep using the files. Optional rebuild follows `docs/setup/` 01–14 and costs money (~$35–45 for two days with teardown, per the cost model). If you rebuild, Appendix T starts empty again, and Phase 12 stays scaffold until you enable it on purpose. If you do not rebuild, you still have a complete control plane in Git — which is the point of making the repository the system.

Walk the clone once more against the six principles: Git authority, digest identity, CI without deploy, namespaces-are-not-accounts, teardown required, scaffold labeled. If you can open a path for each, the book did its job.

The public GitHub mirror is https://github.com/btilki/boutique-eks-gitops. GitLab was the CI remote. Sister public mirrors: https://github.com/btilki/boutique-gke-sre and https://github.com/btilki/boutique-aks-devsecops. Do not copy their cloud-specific controls into this EKS tree without an ADR.

What this book will not claim on your behalf: that signature admission ran in Enforce, that WAF or Falco protected users, that AnalysisTemplates aborted a bad canary, that Dex replaced the admin password, or that AWS is still up. Those sentences are false for this pilot.

You finish able to explain, from this repository, why a pipeline that can `kubectl apply` is a design failure, how a digest merge request becomes cluster state, what CODEOWNERS and manual prod sync actually gate, and what the pilot refuses to claim. That was the plan’s promise. The files are still there. The cluster is not.

The glossary and references are back matter, not optional. If you reuse an abbreviation in a fork of this manuscript, keep the first-use form. If you cite a product, start from `REFERENCES.md` and the repo’s own `docs/`.

Reading order versus the sisters is optional. GitOps does not require the GKE SRE book first. DevSecOps on AKS does not replace ADR-0001. Cross-references are for honest comparison, not for copying a mesh or a multi-region story this title refused.

Practice in every core chapter was file-backed: open a path, interpret a decision, state evidence. Rebuild remains optional and costs money. That is the teaching contract, and it still holds after the last page.

Git remains the deploy authority. The cluster does not have to.

Rehearse the defense with [17-interview-questions-from-this-repository.md](17-interview-questions-from-this-repository.md). Ten questions; answers cite these files. Keep saying production *pilot*.
