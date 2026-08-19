# 7. Bootstrap Argo CD as the Cluster Reconciler

A pipeline that `kubectl apply`s Boutique makes Git a suggestion. This chapter installs Argo CD as the only ongoing reconciler ([ADR-0004](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0004-argocd-gitops.md)). Setup Topic **05** is **lived**. HTTPS for the UI waits for Topic 06.

The production question is:

> How do you make Git the cluster's desired state without letting bootstrap kubectl become a standing deploy path?

## 1. Unsafe starting state

The unsafe default is Helm-install Argo CD from memory, point it at Azure Repos, and auto-sync prod. This repo's Git remote is GitHub. Prod sync is manual. Bootstrap kubectl is a bounded exception: you need a controller before the controller can install itself.

If Topic 05 is skipped “until the app works,” Topics 06–12 have nowhere to put Ingress, Kyverno, or Boutique overlays. Click-ops in the portal then becomes the source of truth.

## 2. The production model: app-of-apps from GitHub

> *Theory — Pull reconciliation*
>
> This model enables the cluster to converge on Git while CI remains an evidence producer, not a deployer.

ADR-0004: Argo CD with app-of-apps; **dev auto-sync; stage/prod manual sync**. `versions.yaml` pins Argo CD `2.10.7`. Install path: `gitops/bootstrap/`. AppProjects live in `gitops/projects/`. Child Applications for platform and apps are `gitops/bootstrap/platform-apps.yaml`.

kubectl at bootstrap is allowed. kubectl as the day-2 Boutique deploy path is not.

## 3. How this repository implements Topic 05

> **Practice — Read the bootstrap layout**
>
> Open `docs/setup/05-gitops-bootstrap.md` and `gitops/bootstrap/README.md`.

Install order is load-bearing:

1. `kubectl kustomize gitops/bootstrap/argocd-install --enable-helm | kubectl apply -f -`
2. `kubectl apply -k gitops/projects/`
3. Configure repository URL (GitHub)
4. `kubectl apply -f gitops/bootstrap/root-app.yaml`

Helm chart 6.7.18 ships Argo CD 2.10.7 (`gitops/bootstrap/argocd-install/`). Applying Application CRs before the controller exists fails. `gitops/platform/kustomization.yaml` is empty until Topic 06 — that is expected, not broken.

> **Practice — Read the root Application**
>
> Open `gitops/bootstrap/root-app.yaml`.

```yaml
spec:
  project: platform
  source:
    repoURL: https://github.com/btilki/boutique-aks-devsecops
    targetRevision: main
    path: gitops/bootstrap
    directory:
      include: platform-apps.yaml
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

The root app is allowed to auto-sync **its children Applications**, not Boutique prod. Placeholders `<GITHUB_ORG>` / `<REPO_NAME>` must match the GitHub remote from Topic 00. If Argo CD points at a fork while you push to origin, the cluster will never see digest commits.

AppProjects `platform`, `applications`, and `monitoring` bound which namespaces and repos each child may touch. That is admission for GitOps itself.

Until Topic 06, the UI is port-forward only. Lived proof that Applications went Healthy/Synced is `assets/images/setup/05-argocd-applications-healthy.png`. After teardown the URL `argocd-boutique.biroltilki.art` is inactive; the screenshot is the evidence.

`gitops/bootstrap/argocd-install/values.yaml` pins the Helm install for the controller itself. Platform Applications later use multi-source Helm (chart repo + `$values` from GitHub), as with ingress-nginx. Bootstrap kubectl kustomize `--enable-helm` is the one time you render charts locally onto the API server.

Initial admin secret is a Kubernetes Secret in `argocd`. Rotate it; do not commit it. Topic 06 will put the UI on HTTPS; until then, port-forward is the lived path. Do not expose Argo CD with `--insecure` on a public LB as a shortcut.

`gitops/bootstrap/platform-apps.yaml` is what the root Application includes. After Topic 05 it may only spawn empty or placeholder children until Topics 06–11 add resources to `gitops/platform/kustomization.yaml`. An Application that is Synced and Healthy with zero workloads is still a successful bootstrap.

Repo credentials: Argo CD needs read access to GitHub. Deploy keys or GitHub App are preferred over a PAT in a Secret named `argocd` that someone dumps in Slack. ADO’s GitHub connection is a different credential for pipeline checkout/push.

## Lived operator commands (Topic 05)

```bash
kubectl kustomize gitops/bootstrap/argocd-install --enable-helm | kubectl apply -f -
kubectl rollout status deployment/argocd-server -n argocd --timeout=300s
kubectl apply -k gitops/projects/
kubectl apply -f gitops/bootstrap/root-app.yaml
kubectl get applications -n argocd
```

Port-forward until Topic 06: `kubectl port-forward svc/argocd-server -n argocd 8080:443`. Retrieve the initial admin secret from the cluster Secret; rotate it. Screenshot `05-argocd-applications-healthy.png` is what remains after teardown.

If Helm is missing `--enable-helm`, kustomize will not render the chart. Topic 00 installed Helm 3.14+. Chart 6.7.18 / Argo CD 2.10.7 must match `versions.yaml gitops.argocd`.

## Limits of this chapter

Topic 05 does not prove Boutique, TLS, or Kyverno. An empty `platform-root` that is Synced is success. Do not skip to Topic 10 because Argo CD is up. Repo credentials that can **push** are not required for Argo CD — read is enough; push is an ADO/GitHub concern for Topic 12.

The lived screenshot shows Application cards. It does not show `argocd-boutique.biroltilki.art` over public HTTPS; that is Topic 06.

## 4. Test the design under failure

### Independent control failure — Argo CD tracks the wrong Git host

> **Practice — Diagnose a silent second remote**
>
> Root `repoURL` still says GitHub, but an engineer registered an Azure Repos mirror “for ADO convenience” and pushed digest pins only there.

**Severity:** high; cluster diverges from the public source of truth.  
**Plausible harm:** Argo CD never deploys signed digests; someone kubectl-applies to “fix” it; unsigned images sneak in.  
**Potential blast radius:** all namespaces the Applications manage, including future `boutique-prod`.  
**Bounded by:** Topic 00 GitHub-only remote, root-app `repoURL`, CONTRIBUTING CI story.  
**Primary principles:** Git is the deploy authority, CI never deploys the cluster, explicit contracts, reconciliation.

#### Diagnosis

ADO checkout can use GitHub. Argo CD must use the same GitHub URL. Azure Repos is not in the architecture context diagram (`docs/architecture/02-system-context.md`). A green ADO pipeline that pushes to the wrong remote is not a successful supply chain.

#### Correction

Point every Application `repoURL` at GitHub. Push digest commits there. Delete the Azure Repos mirror or make it read-only documentation. Do not kubectl-apply Boutique overlays to catch up — fix Git, then sync.

A second failure: auto-sync enabled on prod “to be like GitOps.” That bypasses [ADR-0008](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0008-ado-prod-approval-gate.md) and Chapter 14. Correction: prod Application stays manual.

## Production reality

**Best Practice:** app-of-apps from the same GitHub remote CI will later push digest pins to.

**Production Practice:** selfHeal on the root Application is for child Application CRs, not a license to auto-heal prod Boutique. Sync waves (ingress 10, Boutique 30, monitoring 40) exist so CRDs and controllers precede consumers. Ignore waves and cert-manager will race Ingress.

Lived screenshot `05-argocd-applications-healthy.png` is the completion evidence. After teardown, `argocd app list` will fail; that does not invalidate Topic 05.

### Common errors

- Installing Argo CD with the upstream quickstart YAML at a different version than `2.10.7`.
- Pointing `repoURL` at `dev.azure.com` because the pipeline lives there.
- Applying `root-app.yaml` before AppProjects exist.

## 5. What You Learned

Topic 05 installs Argo CD from `gitops/bootstrap/`, registers AppProjects, and applies a GitHub-backed root app-of-apps. kubectl is a bootstrap exception. Day-2 desired state is Git. Dev will auto-sync; stage/prod will not. Screenshots replace the live UI after teardown.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Topic 05 guide | `docs/setup/05-gitops-bootstrap.md` | Install order and validation |
| Bootstrap tree | `gitops/bootstrap/` | Helm install, root, children |
| AppProjects | `gitops/projects/` | GitOps RBAC boundaries |
| ADR-0004 | `docs/adr/0004-argocd-gitops.md` | Auto vs manual sync |
| Lived screenshot | `assets/images/setup/05-argocd-applications-healthy.png` | Evidence while DNS is offline |

## What changed

| Before | After |
|--------|--------|
| kubectl apply as deploy. | **Argo CD reconciles GitHub.** |
| Auto-sync everywhere. | **Dev auto; stage/prod manual (ADR-0004).** |
| Unknown Git remote. | **Root Application `repoURL` is GitHub.** |

`gitops/README.md` and `gitops/projects/` document AppProject destinations. Platform project must allow `ingress-nginx`, `cert-manager`, `kyverno`, `monitoring`, and later `falco` (scaffold). Applications project allows `boutique-*`. Crossing those projects is how a Boutique overlay takes over the ingress namespace.

> **Independent Practice — Classify three kubectl commands**
>
> For each command, say whether it is bootstrap exception, emergency, or a design failure: (1) apply `argocd-install`; (2) `kubectl set image` on `frontend` in `boutique-prod`; (3) `argocd app sync boutique-stage` after a Git digest commit. Explain using ADR-0004.

**Figure 7.1 — Inactive.** Argo CD Applications cards Healthy/Synced.

![Argo CD applications healthy](https://raw.githubusercontent.com/btilki/boutique-aks-devsecops/main/assets/images/setup/05-argocd-applications-healthy.png)

Source: `assets/images/setup/05-argocd-applications-healthy.png`. DNS is inactive.
