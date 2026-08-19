# 17 — Interview Questions From This Repository

These questions are for a design review or a job interview. Answer from `boutique-eks-gitops`, not from a generic GitOps slide. The cluster is gone. The files are not.

Each answer names paths. If the clone disagrees, the clone wins. If the clone is newer than this manuscript, start at `CHANGELOG.md`.

## 1. Why should CI not deploy directly to Kubernetes?

Because a pipeline that can `kubectl apply` or `argocd sync` is a second control plane with a kubeconfig. ADR-0001 forbids that. GitLab **CI (Continuous Integration)** may push to **ECR (Elastic Container Registry)** and open a digest **MR (Merge Request)** under `gitops/envs/dev/` only. The contract is `docs/ci.md` and `.gitlab-ci.yml`. After teardown, pipelines are dormant unless `ENABLE_PILOT_CI` is set. That is not a broken project; it is the same rule with the cluster deleted.

## 2. Why use Argo CD?

Argo **CD (Continuous Delivery)** is the only deployer. It pulls desired state from Git (app-of-apps + ApplicationSets) and reconciles. Prod has no `syncPolicy.automated`. That is promotion discipline on one cluster, not missing automation. Walk `gitops/bootstrap/`, `gitops/apps/`, `docs/setup/06-argocd-bootstrap.md`, and `docs/architecture/05-deployment-flow.md`.

## 3. Why use image digests instead of tags?

A tag moves. A digest does not. Charts use `image.repository` + `image.digest`. Kyverno denies `:latest` and non-digest refs and allowlists ECR. Promotion copies the same `@sha256` from `gitops/envs/dev` to `stage` to `prod`. See ADR-0001, `docs/promotion.md`, and `gitops/platform/kyverno/policies/`.

## 4. How do you promote an image from dev to production?

Humans copy digest fields. CI does not promote. Topic 11: `docs/setup/11-promotion.md`, `docs/promotion.md`. Prod path is `CODEOWNERS` `@btilki` on `gitops/envs/prod/**` plus a manual Argo sync. Do not skip stage on the happy path.

## 5. How do you roll back?

`git revert` of the digest MR. Argo reconciles the previous desired state. Do not `kubectl rollout undo` as the system of record. `docs/rollback.md` is the contract. Lasting abort of a canary is also Git, not a paused Rollout left as unmanaged state.

## 6. What happens if Argo CD is unavailable?

Existing Pods keep serving. New desired state does not apply. That is an availability gap for *change*, not for the storefront process that is already running. Recovery is restore Argo from Git (`gitops/bootstrap/`) and sync. This pilot is not multi-cluster GitOps; do not invent a second cluster during the outage. See `docs/runbooks/argo-sync.md` and `docs/architecture/08-resilience-and-dr.md` (rebuild **RTO (Recovery Time Objective)** is hours).

## 7. What happens if Git is unavailable?

Argo cannot pull a new revision. The last successfully synced revision remains the cluster's memory of intent. You cannot promote, revert, or prove a new digest. Protect Git the way you protect the control plane. Emergency `kubectl` is a bounded exception that must be reconciled back into Git or it becomes drift. ADR-0001 still holds.

## 8. How do you protect secrets?

Nothing secret in Git. **ESO (External Secrets Operator)** reads AWS Secrets Manager / SSM. SMTP for Alertmanager is an ExternalSecret. IRSA for controllers; GitLab **OIDC (OpenID Connect)** role is ECR-only. `gitops/platform/external-secrets/`, `examples/externalsecret-sample.yaml`, `docs/architecture/07-security-architecture.md`.

## 9. Why use Kyverno?

Admission is the last gate for identity the pipeline never saw: a laptop `kubectl run`, a bad overlay, a floating tag. Lived policies: digest-only, deny `:latest`, ECR allowlist. Signature/SBOM verify is Topic 15 **scaffold** (Audit first). `docs/setup/07-security-baseline.md`, `gitops/platform/kyverno/policies/`.

## 10. How would you implement multi-cluster GitOps?

This repository refused it. One **EKS (Elastic Kubernetes Service)** cluster, three namespaces, cost over blast-radius isolation (ADR-0002). A later design would need a new ADR, a second cluster generator, separate prod blast radius, and a new cost model. Do not answer “ApplicationSet cluster generator” as if this pilot already did it. `docs/ARCHITECTURE.md` tradeoffs table is the honest starting point.

## How to use this appendix

Pick three questions. Open the paths. Speak the lived vs scaffold labels. Say production *pilot*, not production-ready **HA (High Availability)**. That is the interview. The playbook shorts (E1 digest-only, E2 canary, E3 cost) are further reading, not a substitute for the files.
