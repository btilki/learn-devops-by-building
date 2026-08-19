# 6. Pass the Phase 4 Gate Before Boutique Exists

A shop on an ungoverned cluster is a demo, not an SRE platform. The production question is:

> What must be true — Argo CD, secrets, admission, and network — before Online Boutique is allowed to exist?

Setup topics **09–11** are the **Phase 4 gate** (**Lived**). `PROJECT.md` session rule: do not skip Phase 4 before treating the cluster as production-ready. Production-ready here still means “safe to deploy the app,” not “browse SLO held.”

## 1. An unsafe starting state: kubectl apply the shop first

The unsafe sequence is: cluster Ready, Helm install Boutique, add Kyverno later. Images may be `:latest`. Secrets may be `kubectl create secret`. Every pod may speak to every pod. Argo CD, if present, auto-syncs. Admission then has to fight live workloads instead of denying them at the gate.

`docs/bootstrap.md` common mistakes list that sequence first: applying Boutique before Kyverno/ESO/NetworkPolicy. Topic 09’s goal statement repeats the gate. Topic 12’s prerequisites require the gate complete.

## 2. The production model: GitOps control plane, then policy, then app

> *Theory — Platform gate before workload*
>
> This model enables Boutique to land only after desired state has a reconciler, secrets have an external source, admission enforces digest and probes, and the network defaults to deny.

### Argo CD with manual sync (ADR 003)

Topic 09 installs Argo CD (Helm chart pin `7.7.16` in the guide), exposes `argocd.boutique.biroltilki.art`, registers `gitops/bootstrap/root-app.yaml`. Child Applications wait **OutOfSync** until deliberate sync.

Root Application:

```yaml
metadata:
  name: boutique-root
spec:
  source:
    repoURL: https://github.com/btilki/boutique-gke-sre
    path: gitops/apps/argocd-apps
  syncPolicy:
    # Manual sync only — see ADR 003-manual-argocd-sync
    syncOptions:
      - CreateNamespace=true
```

There is no `automated:` block. That absence is the decision.

### ESO-only secrets

Topic 10 installs **ESO (External Secrets Operator)** (guide pin `0.14.2`), binds Kubernetes SA to GCP SA via Workload Identity, and applies `gitops/bootstrap/external-secrets/cluster-secret-store.yaml`:

```yaml
spec:
  provider:
    gcpsm:
      projectID: boutique-gke
      auth:
        workloadIdentity:
          clusterLocation: europe-west1
          clusterName: boutique-gke
          serviceAccountRef:
            name: external-secrets
            namespace: external-secrets
```

Plain Secrets in Git are forbidden by Kyverno `block-plain-secrets`. Grafana admin later uses Secret Manager → ExternalSecret — same pattern.

### Kyverno plus NetworkPolicy

Topic 11 installs Kyverno (guide pin `3.3.4`) and five ClusterPolicies:

| Policy file | Rule |
| --- | --- |
| `require-digest.yaml` | Reject `:latest`; require `@sha256:` |
| `require-probes.yaml` | Liveness + readiness |
| `require-resources.yaml` | CPU/memory requests and limits |
| `require-netpol-labels.yaml` | Namespace tier label |
| `block-plain-secrets.yaml` | ESO-only Secrets |

`gitops/policies/kyverno/require-digest.yaml` sets `validationFailureAction: Enforce`. NetworkPolicies: `default-deny.yaml` deny-all in `boutique`, plus allow lists for the service graph and frontend ingress. Namespaces must carry `network-policy.biroltilki.art/tier`.

**Best Practice:** Prove the gate with a deny fixture (`examples/kyverno-policy-test/bad-latest-pod.yaml`) before Boutique.

**Production Practice:** Helm installs of platform controllers may need a documented Kyverno scale-down break-glass (`docs/security/edge-hardening.md`). That exception is bootstrap, not a standing hole for app images.

## 3. How this repository implements it

> **Practice — Walk the gate in Git without deploying Boutique**
>
> Open topics 09–11, `gitops/bootstrap/`, `gitops/policies/`, and ADR 003.

`docs/setup/README.md` marks 09 as Phase 4 **gate**. Terraform phase table: 09–16 are GitOps / Console, not new foundation modules. That split keeps IaC and cluster policy reviewable.

> **Practice — Confirm default-deny is real**
>
> Open `gitops/policies/network-policies/default-deny.yaml`.

```yaml
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

Without `boutique-allow.yaml` and `boutique-frontend-ingress.yaml`, the shop cannot receive north-south traffic or reach dependencies. Default-deny with no allows is a locked box. Default-allow with a policy file unused is theater.

Tests: `make kyverno-test`, `tests/kyverno/`, CI jobs in `.github/workflows/ci.yml`. Mechanism evidence that policies parse. Lived evidence was the five policies in Enforce on the cluster (`assets/diagrams/kyverno-five-policies.png`, inactive screenshot).

Child apps: `gitops/apps/argocd-apps/policies-application.yaml`, `observability-application.yaml`, `boutique-application.yaml`. Boutique Application exists in Git during Phase 4; syncing it is topic 12. Registering the app object is not deploying the shop.

## 4. Test the design under failure

### Cumulative reliability failure — Boutique synced before Enforce policies

> **Practice — Diagnose a shop that cannot be admitted later**
>
> Workloads created before `require-digest` Enforce may keep running. The next recreate (scale-to-zero, node drain, BA enforce) is when the gate appears — Chapter 14’s Redis lesson in another form.

**Severity:** high; policy becomes archaeology.  
**Plausible harm:** `:latest` in production until the first restart; secrets copied from laptops; lateral movement inside the namespace.  
**Potential blast radius:** all future Deployments on the cluster; restore paths that recreate pods.  
**Bounded by:** Phase 4 session rule; topic 11 validation; digest-only tests.  
**Primary principles:** Git is the deploy authority; Identity is digest, not tag; Lived evidence beats scaffold.

#### Diagnosis

“We’ll add Kyverno after the demo” treats admission as documentation. Admission that is not Enforce at first app deploy does not protect the first app deploy.

#### Correction

Complete 09–11. Deny the bad-latest fixture. Then proceed to topic 12. Do not call the gate an SLO. Call it the precondition for a shop that SRE can honestly own.

That correction changes later decisions:

- Chapter 7 manual sync assumes policies will deny illegal manifests.
- Chapter 11 BA enforce assumes Kyverno already rejected floating tags.
- Chapter 14 restore recreates pods against current admission, not against the old Running set.

## 5. Production reality

### Common errors

#### Helm-installing Boutique in `default` to “see the shop”

That bypasses the `boutique` Application, namespace labels, NetworkPolicy, and digest values. Kyverno may still deny. If it does not, you have an untracked shop.

#### Scaling Kyverno to zero and forgetting to scale back

Edge-hardening.md documents a Helm bootstrap exception. Leaving admission at 0 replicas is standing disable of the gate.

#### Default-deny without allow policies

Boutique cannot reach Redis, checkout cannot reach payment, frontend cannot receive Ingress. The gate is not “deny YAML exists”; it is deny plus the reviewed allows.

#### Registering `boutique-root` with automated sync “to finish faster”

`gitops/bootstrap/root-app.yaml` comments manual sync. Topic 16 smoke greps for `automated:` and expects 0. Auto-sync on the root app would sync Boutique before you intend topic 12.

## 6. What changed

| Before | After |
| --- | --- |
| kubectl apply as the control plane. | Argo CD app-of-apps, manual sync. |
| Secrets in Git or random kubectl. | ClusterSecretStore + Workload Identity. |
| Any image, no probes. | Five Kyverno ClusterPolicies in Enforce. |
| Open pod network. | Default-deny plus service-graph allows. |

## 7. What You Learned

Topics 09–11 install Argo CD with manual sync, ESO with Secret Manager, Kyverno Enforce policies, and default-deny NetworkPolicy. That is the Phase 4 gate. Skipping it to get a storefront URL faster produces a cluster that later chapters cannot defend. Gate complete is not browse success.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Setup 09–11 | `docs/setup/09-argocd-bootstrap.md` … `11-kyverno-policies.md` | Gate procedure |
| ADR 003 | `docs/adr/003-manual-argocd-sync.md` | Manual sync |
| Root app | `gitops/bootstrap/root-app.yaml` | App-of-apps |
| ESO store | `gitops/bootstrap/external-secrets/cluster-secret-store.yaml` | WI to Secret Manager |
| Policies | `gitops/policies/kyverno/`, `network-policies/` | Admission and NetPol |

> **Independent Practice — Classify observability NetworkPolicies**
>
> Files include `observability-default-deny.yaml`, `observability-collector-ingress.yaml`, `observability-platform-egress.yaml`.

1. Is the observability namespace in the Phase 4 gate or a Phase 6 add-on that must still match the label policy?
2. What happens if Boutique starts before those allows exist (traces black-hole vs shop down)?
3. Should a missing collector deny checkout? Why or why not for SLIs?
4. What evidence would prove default-deny is active besides `kubectl get netpol`?

Do not deploy topic 12 until you can explain each of the five ClusterPolicies in one sentence.

**Figure 6.1 — Inactive.** Argo CD apps Synced/Healthy after the Phase 4 gate.

![Argo CD applications healthy](https://raw.githubusercontent.com/btilki/boutique-gke-sre/main/assets/diagrams/argocd-applications-healthy-synced.png)

**Figure 6.2 — Inactive.** Five Kyverno ClusterPolicies in Enforce.

![Kyverno five policies](https://raw.githubusercontent.com/btilki/boutique-gke-sre/main/assets/diagrams/kyverno-five-policies.png)

Sources: `assets/diagrams/argocd-applications-healthy-synced.png`, `assets/diagrams/kyverno-five-policies.png`.
