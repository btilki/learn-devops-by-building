# 12 — Canary the Frontend on Stage and Prod

An all-or-nothing Deployment cutover makes digest promotion a binary blast. Topic 12 installs Argo Rollouts and splits **ALB (Application Load Balancer)** weight on **stage and prod** frontends. Dev stays a Deployment.

> How do you progressively expose a new frontend digest on stage and prod so a bad image can be aborted — while Git remains the lasting source of truth?

## 1. The unsafe starting state: 100% on sync

After Topic 11, a prod manual sync updates every frontend pod at once if the object is a Deployment. Kyverno still admits the digest. Users all see the new binary together. Abort is “revert and wait for a full rollout.”

FR-09 requires canary on stage **and** prod. Timed pauses without analysis still cannot auto-fail a bad digest — that auto-abort path is Topic 18 **scaffold**.

**Lived** as C4–C5: stage and prod Rollouts Progressing → Paused → Healthy. AnalysisTemplates are **scaffold**.

## 2. The production model: Rollout + ALB weights, Git for lasting recovery

> *Theory — Progressive traffic with Git as durable abort*
>
> Shift a fraction of ALB weight to a canary ReplicaSet; pause; continue or abort; encode the lasting identity change in Git so a cluster abort cannot be overwritten by the next sync of a bad digest.

`docs/architecture/05-deployment-flow.md`: abort = Git revert of the bad digest; prod canary still requires manual Application sync to *start*.

## 3. How this repository implements canary

> **Practice — Read controller, chart, and env together**
>
> Open `gitops/apps/platform-apps/applicationset.yaml` (argo-rollouts wave 25), `charts/frontend/templates/rollout.yaml`, and `gitops/envs/prod/values/frontend.yaml` canary steps.

### Controller

Topic 12 (`docs/setup/12-canary-rollouts.md`) syncs Argo Rollouts chart **2.39.5** (app **v1.8.2**) from `gitops/platform/argo-rollouts/values.yaml`. **CRDs (Custom Resource Definitions)** must exist before stage/prod charts render `kind: Rollout`. Switching Deployment → Rollout may require pruning the old Deployment once.

### Frontend Rollout template

```1:24:charts/frontend/templates/rollout.yaml
{{- if .Values.canary.enabled }}
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: {{ include "frontend.fullname" . }}
  labels:
    {{- include "frontend.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      {{- include "frontend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "frontend.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "frontend.serviceAccountName" . }}
      containers:
        - name: frontend
          image: "{{ .Values.image.repository }}@{{ .Values.image.digest }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
```

Traffic routing uses ALB Ingress, canary Service, stable Service, root Service:

```45:53:charts/frontend/templates/rollout.yaml
  strategy:
    canary:
      canaryService: {{ include "frontend.fullname" . }}-canary
      stableService: {{ include "frontend.fullname" . }}
      trafficRouting:
        alb:
          ingress: {{ include "frontend.fullname" . }}
          servicePort: {{ .Values.service.port }}
          rootService: {{ include "frontend.fullname" . }}-root
```

Analysis hook is gated on `canary.analysis.enabled` — default false. **Scaffold** when enabled via example overlays.

### Prod overlay steps

```17:33:gitops/envs/prod/values/frontend.yaml
# Topic 12 — frontend canary (ALB traffic split); starts only after manual Argo sync
# Topic 18 — analysis off by default; see frontend-analysis.example.yaml to enable
canary:
  enabled: true
  analysis:
    enabled: false
  steps:
    - setWeight: 10
    - pause:
        duration: 120
    - setWeight: 30
    - pause:
        duration: 120
    - setWeight: 50
    - pause:
        duration: 120
    - setWeight: 100
```

**Lived.** Stage overlay is the same idea. Dev `canary.enabled: false`. `gitops/platform/argo-rollouts/analysis/` templates and `frontend-analysis.example.yaml` are **scaffold** (Chapter 15).

### Abort runbook

```29:40:docs/runbooks/canary.md
## Abort (immediate)

```bash
NS=stage   # or prod
# Preferred (install kubectl-argo-rollouts plugin):
kubectl argo rollouts abort frontend -n "$NS"
```

Then **always** fix Git (lasting recovery):

```bash
# Prefer: git revert of the digest promote MR (see docs/rollback.md)
```

**Lived** as procedure; abort was rehearsed as C7 knowledge even when the happy path completed Healthy.

Chart defaults keep canary off so `helm template` without overlays yields a Deployment. Stage overlay turns it on with slightly different pause lengths than prod (`docs/setup/12-canary-rollouts.md` records the cutover). ALB `target-type: ip` (already on frontend Ingress from Topic 09) is a prerequisite for Rollouts traffic splitting. If someone changes that to `instance`, canary weights will not do what the Rollout spec says.

`gitops/platform/argo-rollouts/README.md` and Topic 12 Step 12.5 document abort plus Git revert. AnalysisTemplates under `analysis/` are synced only when the platform-manifests AppSet includes them — Topic 18 **scaffold**. Lived prod overlay sets `analysis.enabled: false` so a rebuild does not surprise you with curl Jobs.

> **Practice — Explain why abort alone is not rollback**
>
> If Git still has the bad digest and prod auto-sync is off, abort holds until someone syncs again. If a colleague then manual-syncs without reverting Git, the canary restarts. Write that sequence as an incident note.

## 4. Test the design under failure

**Scenario:** Canary at 30% on prod; error rate spikes; operator aborts but does not revert Git; later they manual-sync “to clean Argo.”

**Severity:** aborted canary comes back.  
**Plausible harm:** users take another 10–30% of bad frontend; dual-pod confusion; false confidence from the first abort.  
**Potential blast radius:** prod frontend traffic on the shared ALB; other services unchanged (canary is frontend-only).  
**Bounded by:** Rollout abort, timed pauses (not metric abort — lived), Git revert + CODEOWNERS, manual prod sync, canary runbook.  
**Primary principles:** Git is the only deploy authority; image identity is digest, not tag; scaffold in Git is not lived proof.

### Diagnosis

`kubectl -n prod get rollout frontend` shows Degraded/Aborted while `gitops/envs/prod/values/frontend.yaml` still has the new digest. Argo OutOfSync. Analysis not running (`analysis.enabled: false`) — so the spike was human-detected, not auto-aborted.

### Recovery

Keep the abort as containment. Revert the digest MR; approve; merge; manual sync. Confirm stable Service weight 100% and HTTPS 200. Optional: enable AnalysisTemplates only after rebuild proof (scaffold). Do not `kubectl set image` on the Rollout.

Stage steps in the overlay use 20/50/100 with 60s pauses in chart defaults; prod overlay uses 10/30/50/100 with 120s pauses. That is a production-practice difference: prod soaks longer. Neither set is metric-gated until Topic 18. `docs/runbooks/canary.md` quick triage is `get/describe rollout`, optional `kubectl argo rollouts`, curl the env host.

## 5. What You Learned

Frontend canary on stage and prod is timed ALB weight steps on a digest-pinned Rollout; lasting recovery is still Git. You can now walk Topic 12, `gitops/platform/argo-rollouts/`, and `charts/frontend/templates/rollout.yaml`.

### Durable outputs

- Setup: `docs/setup/12-canary-rollouts.md`
- Controller: `gitops/platform/argo-rollouts/`
- Chart: `charts/frontend/templates/rollout.yaml`, `charts/frontend/values.yaml`
- Overlays: `gitops/envs/stage/values/frontend.yaml`, `gitops/envs/prod/values/frontend.yaml`
- Runbook: `docs/runbooks/canary.md`

> **Independent Practice — Canary a backend without ALB**
>
> `paymentservice` has no public Ingress. Design a progressive delivery that does *not* copy frontend ALB weights. Either refuse (pilot scope is frontend only) or specify meshed/traffic-less replica canary and how Git digest promotion still works. Keep Topic 18 labeled scaffold if you mention AnalysisTemplates.

## Further reading

Playbook article **E2** is the short public argument for Argo Rollouts and ALB canary without a service mesh.

https://github.com/btilki/devops-engineering-playbook/blob/main/articles/E2.md

FR-09 is frontend-only for a reason: ALB weight steps need Ingress. Inventing canary for gRPC backends without a traffic splitter is a new ADR, not a values toggle.

`gitops/platform/argo-rollouts/values.yaml` is the controller pin (chart 2.39.5 / app v1.8.2). Without that ApplicationSet element at wave 25, stage/prod charts that set `canary.enabled: true` cannot create Rollout objects.

## Next

Chapter 13 proves the whole path with `PRODUCTION_CHECKLIST.md` and the operations/runbook set — then teardown is immediate.
