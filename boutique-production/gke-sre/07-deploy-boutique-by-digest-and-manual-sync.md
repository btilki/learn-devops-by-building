# 7. Deploy Boutique by Digest and Manual Sync

Phase 4 is complete. The shop still does not exist until Git pins digests and a human syncs Argo CD. The production question is:

> How does Online Boutique become live by digest identity and manual promotion — and how do you roll back without kubectl edit?

Setup topic **12** (**Lived**), `gitops/apps/boutique/`, `tests/manifest/digest-only.sh`, and `docs/operations/rollback.md` are the path. First HTTPS 200 is mechanism evidence for the storefront, not a monthly SLO.

## 1. An unsafe starting state: Helm from upstream tags, auto-sync

Pulling `gcr.io/google-samples/microservices-demo` or tag `v0.10.2` is obsolete per topic 12: those paths fail image pull. Hand-editing tags into `values.yaml` bypasses CI attestations. Auto-sync on merge would make every digest PR immediately production. `kubectl set image` would make Git a liar.

The unsafe rollback is “roll the ReplicaSet in the UI” while `main` still pins the bad digest. The next sync brings the failure back.

## 2. The production model: digest PR, manual sync, Git revert

> *Theory — Digest promotion with a human sync gate*
>
> This model enables Boutique to change only when CI has pinned `sha256` in Git and an operator has deliberately reconciled — so rollback is a Git revert plus the same gate.

### Bootstrap images once via CI

Topic 12 §0: first deploy mirrors upstream `us-central1-docker.pkg.dev/google-samples/microservices-demo/<service>:v0.10.5` and `docker.io/library/redis:7.2-alpine` into Artifact Registry. Run `build-scan-sign`. Merge the digest PR. Do not hand-edit digests.

`gitops/apps/boutique/values.yaml` holds configuration (ingress host, tracing, resources, HPA flags). `values-images.yaml` holds identity. Kyverno and `digest-only.sh` care about the latter.

### Application object without auto-sync

`gitops/apps/argocd-apps/boutique-application.yaml`:

```yaml
spec:
  source:
    path: gitops/apps/boutique
    helm:
      valueFiles:
        - values.yaml
        - values-images.yaml
  destination:
    namespace: boutique
  syncPolicy:
    managedNamespaceMetadata:
      labels:
        network-policy.biroltilki.art/tier: application
    syncOptions:
      - CreateNamespace=true
```

Again: no `automated` sync. Namespace tier label is set on create so Kyverno `require-netpol-labels` passes.

### Rollback is Git

`docs/operations/rollback.md`:

```text
1. Revert bad commit on main (or restore previous digest in values-images.yaml)
2. Merge revert PR
3. Manual Argo CD sync
```

Helm/Argo history rollback is allowed only when Git revert is slower; Git remains source of truth. Runbook: `docs/sre/runbooks/bad-deploy-rollback.md`.

**Best Practice:** Run `./tests/manifest/digest-only.sh` before sync.

**Production Practice:** Game day 01 is the scheduled proof of this rollback. It is **Deferred** until rebuild. Do not claim it executed.

## 3. How this repository implements it

> **Practice — Read the digest-only test as a contract**
>
> Open `tests/manifest/digest-only.sh`.

The script fails if `values-images.yaml` contains `:latest` or a `tag:` field (comments ignored), and fails if it finds fewer than one `digest: sha256:` pin. CI runs this. Operators can run it locally. It does not deploy.

> **Practice — Follow topic 12 validation without treating DNS as live**
>
> When the cluster existed: `argocd app sync boutique`, wait health, `curl -I https://boutique.biroltilki.art`. Screenshot `assets/diagrams/boutique-storefront-https.png` is **Inactive**.

`gitops/apps/boutique/README.md` documents the chart. Templates include Deployments, Services, Ingress, Redis, and (Phase 9-B **scaffold** until rebuild) `hpa.yaml` and `pdb.yaml`. Replica defaults in `values.yaml` for most services start at 1; HPA for frontend and checkout is the apply-on-rebuild HA story (Chapter 14). Lived topic 12 did not require game day 02’s PDB credibility.

Tracing in `values.yaml`:

```yaml
  tracing:
    enabled: true
    collectorServiceAddr: otel-collector.observability.svc:4317
```

Chapter 8 syncs the collector. Boutique may start before traces flow; SLIs must not wait on a pretty trace graph.

Also in topic 12: `tests/manifest/kubeconform.sh` and `tests/manifest/boutique-kyverno.sh`. Manifests that cannot pass Kyverno dry-run should not be synced.

Topic 12 smoke when live included screenshot `github-actions-build-scan-sign-success.png` and the Trivy failure screenshot before `upstream-mirror.trivyignore`. Those are **Inactive** CI evidence. `digest-only.sh` still runs in CI on every PR to `main` even while the cluster is gone — identity discipline does not require a live shop.

Ingress in `values.yaml` binds the storefront to the edge from Chapter 4:

```yaml
ingress:
  enabled: true
  host: boutique.biroltilki.art
  staticIpName: boutique-ingress-ip
  managedCertName: boutique-managed-cert
```

A 200 on that host is topic 12/16 mechanism. Browse SLO remains Chapter 9.

## 4. Test the design under failure

### Connected consequence — Floating tag sneaks past review

> **Practice — Diagnose identity failure at admit time**
>
> A PR changes `digest:` to `tag: latest`. `digest-only.sh` should fail in CI. If CI is skipped and someone syncs, Kyverno `require-digest` must deny.

**Severity:** high; rollback identity disappears.  
**Plausible harm:** every node pull races a moving tag; BA attestation cannot bind.  
**Potential blast radius:** all Boutique services sharing `values-images.yaml`.  
**Bounded by:** `digest-only.sh`, Kyverno Enforce, BA (once enforce).  
**Primary principles:** Identity is digest, not tag; CI never deploys; Git is the deploy authority.

#### Diagnosis

Tags are convenient for humans. They are not production identity. Topic 12’s obsolete GCR warning is the same class of failure: convenience path that does not exist.

#### Correction

Keep pins. Revert via Git. Manual sync. If BA denies a recreate, fix attestations — do not `kubectl edit` a tag onto the live Deployment.

That correction changes later decisions:

- Chapter 9 burn on checkout after a bad digest is a page, not a Helm rollback party.
- Chapter 12 runbook `bad-deploy-rollback` must match this procedure.
- Chapter 14 game day 01, when executed, must use a documented non-fatal misconfig — not a random unsigned image.

## 5. Production reality

### Common errors

#### Mirroring from obsolete `gcr.io/google-samples/microservices-demo` tag `v0.10.2`

Topic 12 table is explicit: use `us-central1-docker.pkg.dev/google-samples/microservices-demo` at `v0.10.5`. Old coordinates fail pulls.

#### Putting digests in `values.yaml`

CI writes `values-images.yaml`. Mixing identity into config values hides the digest-only test’s file path and invites floating tags next to resource requests.

#### Argo History rollback while `main` still pins the bad digest

The next manual sync restores the failure. `docs/operations/rollback.md` prefers Git revert.

#### Claiming HPA/PDB “validated” after topic 12

Templates exist. Topic 18 must sync them on rebuild. Game day 02 is deferred until then. `values.yaml` already sets `checkoutservice` replicas 2 and autoscaling min 2 — still scaffold relative to the torn-down cluster.

## 6. What changed

| Before | After |
| --- | --- |
| Upstream tags on the cluster. | AR digests in `values-images.yaml`. |
| Auto-deploy on merge. | `boutique-application.yaml` without `automated`. |
| kubectl rollback. | Git revert + manual sync. |
| HTTPS 200 as SLO. | HTTPS 200 as topic 12/16 mechanism. |

## 7. What You Learned

Topic 12 deploys Online Boutique from Helm values plus digest pins, via Argo CD manual sync, after CI mirror/sign. Rollback restores a previous digest in Git. Storefront HTTPS is necessary mechanism. It is not the browse SLO. HPA/PDB GitOps files are real; their HA claim is apply-on-rebuild until topic 18 is lived again.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| Setup 12 | `docs/setup/12-boutique-deploy.md` | Lived deploy path |
| Chart | `gitops/apps/boutique/` | App + image pins |
| Digest test | `tests/manifest/digest-only.sh` | CI contract |
| Rollback | `docs/operations/rollback.md` | Git revert + sync |

> **Independent Practice — Write the rollback evidence you would keep**
>
> A bad `checkoutservice` digest merged and was synced.

1. Which Git artifact is the last known good identity?
2. What user-visible check is not `kubectl get pods`?
3. If Argo shows Synced but checkout still 5xx, which chapter’s telemetry do you need?
4. Would you use Argo History rollback if `main` still has the bad digest? Why or why not?

Do not call a green Application Healthy “checkout reliable.” Healthy means probes passed.
