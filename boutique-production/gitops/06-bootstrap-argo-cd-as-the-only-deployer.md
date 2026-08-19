# 6 — Bootstrap Argo CD as the Only Deployer

If Argo **CD (Continuous Delivery)** auto-syncs production, Git still “owns” desired state while a merge becomes an immediate cluster mutation. If **CI (Continuous Integration)** can `argocd sync`, Git is a suggestion. This chapter is Topic 06: install Argo, wire app-of-apps, and keep prod manual.

> How do you make Argo CD the only cluster deployer so platform and workloads reconcile from this repository — without turning a merge to `main` into an unattended prod apply?

## 1. The unsafe starting state: two deployers, or one unrestricted one

After M1, Helm already installed edge controllers. The unsafe continuations are: keep using Helm forever (drift from Git), let CI sync “to be sure,” or enable `syncPolicy.automated` on prod because lower environments used it.

ADR-0001 requires pull reconciliation and **manual prod sync**. `docs/architecture/05-deployment-flow.md` is the sequence: digest **MR (Merge Request)** → merge → Argo syncs dev → human promote → stage → CODEOWNERS + manual sync prod.

**Lived.** Argo UI was at `argocd.boutique.biroltilki.art` (**inactive** now). Bootstrap values remain in Git.

## 2. The production model: app-of-apps, waves, prod automated absent

> *Theory — Pull reconciler with environment-scoped sync*
>
> One root Application automates discovery of ApplicationSets; platform apps auto-sync in waves; workload prod Applications omit automated sync so a human still pulls the lever.

```21:37:docs/architecture/05-deployment-flow.md
## GitOps sync model

| Layer | Mechanism | Sync |
|-------|-----------|------|
| Root | App-of-apps | Automated |
| Platform | Applications / ApplicationSet | Automated + **sync waves** |
| Workloads | ApplicationSet per env | dev/stage automated; **prod manual** |

**Sync waves (conceptual):**

| Wave | Content |
|------|---------|
| 0 | CRDs / Kyverno / ESO operators |
| 1 | Policies, ClusterSecretStores, NetworkPolicies |
| 2 | Ingress stack, monitoring |
| 3 | Boutique workloads |
```

`gitops/README.md` locks the same table: prod automated sync is **No**.

## 3. How this repository implements bootstrap

> **Practice — Open the three GitOps control files**
>
> Read `gitops/bootstrap/root/application.yaml`, `gitops/apps/platform-apps/applicationset.yaml`, and `gitops/apps/workload-apps/boutique-applicationset.yaml`. Write where `automated` is present and where it is absent.

### Root app-of-apps

```6:31:gitops/bootstrap/root/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
  labels:
    app.kubernetes.io/name: root
spec:
  project: default
  source:
    repoURL: https://gitlab.com/btilki/boutique-eks-gitops.git
    targetRevision: main
    path: gitops/apps
    directory:
      recurse: true
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

**Lived.** The root automates *Applications*, not prod workloads. `project: default` is the pilot choice; named AppProjects are **scaffold** (Topic 17 / ADR-0008, Chapter 15). Bootstrap install itself is Helm (`gitops/bootstrap/argocd/values.yaml`, chart 7.8.14, app v2.14.x) — the one-time exception Topic 06 documents. After that, Git is the authority.

### Platform ApplicationSet — automated, waved

The list generator installs LB controller, external-dns, cert-manager (wave 10), Kyverno and External Secrets (wave 20), kube-prometheus-stack and Loki (wave 30), Argo Rollouts (wave 25). Template `syncPolicy.automated` is on. `project: boutique-platform` is already in the file for Topic 17; on the lived pilot the default project was enough until scaffolds landed.

### Workload ApplicationSet — prod autoSync false

```20:29:gitops/apps/workload-apps/boutique-applicationset.yaml
    - matrix:
        generators:
          - list:
              elements:
                - env: dev
                  autoSync: true
                - env: stage
                  autoSync: true
                - env: prod
                  autoSync: false
```

`templatePatch` adds automated prune/selfHeal **only** when `autoSync` is true:

```70:80:gitops/apps/workload-apps/boutique-applicationset.yaml
  templatePatch: |
    {{- if .autoSync }}
    spec:
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
          - ServerSideApply=true
    {{- end }}
```

**Lived.** `frontend-prod` having empty `syncPolicy.automated` was PRODUCTION_CHECKLIST A7. Services include redis through frontend; each Helm chart path is `charts/{{.service}}` with values from `gitops/envs/{{.env}}/values/{{.service}}.yaml`.

> **Practice — Confirm CI cannot sync**
>
> Grep `.gitlab-ci.yml` and `docs/ci.md` for `argocd` and `kubectl apply`. Topic 10 forbids both. Bootstrap commands in `docs/setup/06-argocd-bootstrap.md` are operator CLI/Helm, not pipeline jobs.

`gitops/apps/README.md` and `docs/setup/06-argocd-bootstrap.md` walk repo credentials (read-only deploy token), UI Ingress on the locked hostname, and “changing prod to automated is not allowed.”

Helm bootstrap values put Argo behind the same ACM+ALB pattern as everything else:

```9:38:gitops/bootstrap/argocd/values.yaml
global:
  domain: argocd.boutique.biroltilki.art

configs:
  params:
    server.insecure: true
  cm:
    # Restrictive defaults; widen only if needed
    timeout.reconciliation: 180s
    application.instanceLabelKey: argocd.argoproj.io/instance

server:
  replicas: 2
  ingress:
    enabled: true
    ingressClassName: alb
    annotations:
      alb.ingress.kubernetes.io/scheme: internet-facing
      alb.ingress.kubernetes.io/target-type: ip
      alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
      alb.ingress.kubernetes.io/certificate-arn: "<ACM_CERTIFICATE_ARN>"
      alb.ingress.kubernetes.io/ssl-redirect: "443"
      alb.ingress.kubernetes.io/backend-protocol: HTTP
      external-dns.alpha.kubernetes.io/hostname: argocd.boutique.biroltilki.art
    hosts:
      - argocd.boutique.biroltilki.art
    tls: false # TLS at ALB, not Ingress secret
```

**Lived.** `server.insecure: true` is correct behind ACM termination, not “TLS off.” Dex stays disabled until Topic 17 examples exist. `gitops/apps/README.md` later records actual waves 5–40 including Topic 17 AppProjects at wave 5 (**scaffold** on rebuild ordering).

## 4. Test the design under failure

**Scenario:** Prod ApplicationSet element flipped to `autoSync: true`.

**Severity:** every merge to `gitops/envs/prod/**` becomes a live apply.  
**Plausible harm:** a mistaken digest copy reaches users before CODEOWNERS ritual and before a human watches the canary; rollback requires winning a race with auto-heal.  
**Potential blast radius:** all `*-prod` Boutique apps on the shared cluster.  
**Bounded by:** ApplicationSet `autoSync: false` for prod, CODEOWNERS `@btilki`, checklist A7, Setup 06 “not allowed.”  
**Primary principles:** Git is the only deploy authority; one cluster and three namespaces are a cost decision, not isolation; image identity is digest, not tag.

### Diagnosis

`kubectl -n argocd get app frontend-prod -o yaml` shows `spec.syncPolicy.automated`. Git blame on `boutique-applicationset.yaml` shows `autoSync: true` for prod. Argo UI “AUTO-SYNC” enabled on `*-prod`.

### Recovery

Revert the ApplicationSet in Git. Disable auto-sync on live apps if they already flipped. If a bad digest landed, `git revert` and *then* sync (Chapter 11). Do not “pause” forever; a forgotten pause is unmanaged state with GitOps branding.

## 5. What You Learned

Argo CD is the only deployer; prod still requires a human sync. You can now walk Topic 06, `gitops/bootstrap/`, `gitops/apps/`, and the deployment-flow doc as one sync model.

### Durable outputs

- Setup: `docs/setup/06-argocd-bootstrap.md`
- Layout and sync table: `gitops/README.md`
- Root, platform AppSet, boutique AppSet: `gitops/bootstrap/root/application.yaml`, `gitops/apps/platform-apps/applicationset.yaml`, `gitops/apps/workload-apps/boutique-applicationset.yaml`
- Flow: `docs/architecture/05-deployment-flow.md`

> **Independent Practice — Split platform and workload credentials**
>
> After rebuild you want the repo-server to clone with a token that cannot write Git, and you want a *second* token never created. Using ADR-0001 and `gitops/bootstrap/`, specify token scopes, where the Secret lives (not Git), and what a compromised Argo would still be able to do on the cluster. Do not add CI sync as a “backup.”

**Figure 6.1 — Inactive.** Argo CD Applications, Healthy/Synced on the lived pilot.

![Argo CD Applications dashboard](https://raw.githubusercontent.com/btilki/boutique-eks-gitops/main/assets/images/setup/06-argocd-applications-dashboard.png)

Source: `assets/images/setup/06-argocd-applications-dashboard.png` in the clone. Public DNS is inactive; this is historical evidence.

## Further reading

Playbook article **E1** is the short public argument for digest-only GitOps and “CI never deploys.” It is not a second source of truth.

https://github.com/btilki/devops-engineering-playbook/blob/main/articles/E1.md

## Next

Chapter 7 enforces digest, secrets, and NetworkPolicy so unsigned tags and plaintext SMTP cannot enter the namespaces Argo now owns.
