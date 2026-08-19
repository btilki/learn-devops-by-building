# 12. Deploy Boutique With Kustomize Overlays

Signed images still fail if GitOps points at Google's registry or at `:latest`. This chapter is Setup Topic **10**: Kustomize base plus **dev** overlay for Online Boutique v0.10.5 ([ADR-0006](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0006-kustomize-boutique.md)). Stage and prod overlays exist in the tree; their promotion gate is Chapter 14.

The production question is:

> How do you run the storefront in `boutique-dev` so every container is an ACR digest Kyverno will admit?

## 1. Unsafe starting state

The unsafe default is `kubectl apply -f kubernetes-manifests.yaml` from upstream. That file uses Google Artifact Registry and `busybox:latest`. Kyverno will deny it. The other default is a Helm fork that drifts from v0.10.5. ADR-0006 chooses Kustomize overlays so image transforms stay reviewable.

`prod` is not deployed in this topic. Auto-sync applies to **dev** only.

## 2. The production model: base plus env overlays

> *Theory — Overlay identity*
>
> This model enables one upstream-derived base to serve three namespaces while image identity remains a digest pin and ingress host remains an overlay patch.

`gitops/apps/boutique/README.md`:

- `base/` — upstream-derived manifests; ACR refs; redis/busybox pins
- `overlays/dev/` — `dev-boutique.biroltilki.art`, auto-sync
- `overlays/stage/` / `overlays/prod/` — manual sync; prod also needs ADO approval before Git update

NetworkPolicies and hardening directories under base are Topic 15/19 **scaffold** inherited by overlays. Lived Topic 10 success does not prove default-deny NetworkPolicy enforcement (needs Azure NPM on rebuild).

## 3. How this repository implements Topic 10

> **Practice — Read the image transforms**
>
> Open `docs/setup/10-boutique-dev.md` and `gitops/apps/boutique/base/kustomization.yaml`.

```yaml
images:
  - name: us-central1-docker.pkg.dev/google-samples/microservices-demo/frontend
    newName: acrboutiquedevgwc.azurecr.io/frontend
    newTag: v0.10.5
  # ... eleven services ...
  - name: redis
    newName: acrboutiquedevgwc.azurecr.io/redis
    newTag: 7.2-alpine
  - name: busybox
    newName: acrboutiquedevgwc.azurecr.io/busybox
    newTag: 1.36.1
patches:
  - path: patches/remove-frontend-external.yaml
```

`remove-frontend-external.yaml` drops the extra Load Balancer. Ingress from Topic 06 is the north-south path.

Topic 10 Step 10.2 mirrors and signs redis and busybox. Without that, deny-latest and allowlist fail the init container. That is DR-02 from `docs/architecture/01-requirements.md`.

> **Practice — Read the dev overlay**
>
> Open `gitops/apps/boutique/overlays/dev/kustomization.yaml` and `dev-application.yaml`.

```yaml
namespace: boutique-dev
resources:
  - namespace.yaml
  - ingress.yaml
  - ../../base
patches:
  - path: patches/recreate-deployment-strategy.yaml
  - path: patches/reduce-resource-requests.yaml
  - path: patches/container-run-as-non-root.yaml
  - path: patches/loadgenerator-replicas.yaml
  - path: patches/optional-services-replicas.yaml
```

Commented block shows where Topic 09 `digest-manifest.json` becomes `images: digest: sha256:...`. Tags get you to first sync; **digest pins** are the production identity. `runAsNonRoot` patches exist because policy `03` enforces it.

Argo CD Application for dev uses **automated** sync. Lived UI: `assets/images/setup/10-dev-boutique-homepage.png` and `10-dev-boutique-cart-checkout.png`. FQDN is inactive after teardown; screenshots are the storefront.

`gitops/apps/boutique/dev-application.yaml`:

```yaml
spec:
  project: applications
  source:
    path: gitops/apps/boutique/overlays/dev
  destination:
    namespace: boutique-dev
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

`CreateNamespace=true` plus overlay `namespace.yaml` is belt and braces. Sync wave 30 runs after ingress (wave 10) and Kyverno. If you sync Boutique before policies, unsigned images might land in the gap — another reason Topic 08 precedes Topic 10 in the dependency chain even though Kyverno could install earlier.

`tests/integration/dev-smoke.sh` hits HTTPS `/_healthz` and checks pods. It needs kubectl and DNS. `tests/README.md` TEST-008. After teardown, quote the screenshot instead of running it.

Optional services replica patches scale down ads/loadgenerator for the slim test. That is capacity, not a security control. Do not call a scaled-to-zero loadgenerator “attack surface removed” unless you also drop it from the image allowlist.

Slim vs full Boutique: `ARCHITECTURE.md` notes the reference test often ran a slim storefront for pod capacity. Overlay replica patches encode that. Full × 3 namespaces is the designed ceiling, not a promise of headroom.

## Lived operator commands (Topic 10)

```bash
# after Topic 09 signatures exist:
# mirror+sign redis:7.2-alpine and busybox:1.36.1 to ACR (Step 10.2)
kubectl kustomize gitops/apps/boutique/overlays/dev | head
kubectl get application -n argocd boutique-dev
./tests/integration/dev-smoke.sh
```

Replace `acrboutiquedevgwc` in `base/kustomization.yaml` with your `acr_login_server`. Push GitHub so auto-sync runs. Screenshot `10-dev-boutique-homepage.png` is the storefront after DNS dies. Slim replica patches are capacity, not a threat-model control.

Limits: digest pins may still be comments after first sync. Stage/prod Applications exist in Git but must not auto-sync. NetworkPolicies under `base/networkpolicies/` are scaffold inheritance — YAML in the overlay is not Azure NPM enforcement.

## 4. Test the design under failure

### Independent control failure — Overlay still pulls `redis:alpine` from Docker Hub

> **Practice — Trace a Kyverno deny on cart**
>
> `cartservice` is Running; `redis-cart` is ImagePullBackOff or admission-denied. Base kustomization missed the redis transform or ACR mirror for redis was skipped.

**Severity:** high; checkout/cart broken; temptation to exclude redis from policy.  
**Plausible harm:** operator adds `redis:alpine` exception; unsigned public redis runs beside signed Boutique.  
**Potential blast radius:** session data in redis; same cluster as prod namespace later.  
**Bounded by:** DR-02, deny-latest, ACR allowlist, Topic 10.2 auxiliary mirror.  
**Primary principles:** identity is digest not tag, Git is the deploy authority, blast-radius control.

#### Diagnosis

`kubectl describe` the denied pod. If message is `:latest` or non-ACR, read `base/kustomization.yaml` images list. If ImagePullBackOff for `acr.../redis`, Topic 10.2 did not push/sign.

#### Correction

Mirror redis 7.2-alpine and busybox 1.36.1 to ACR, sign, pin. Do not exclude `boutique-dev` from ClusterPolicies.

A second failure: `kubectl apply` the overlay to “go faster than Argo.” Correction: push Git, let auto-sync work; kubectl is not the deploy path.

## Production reality

**Best Practice:** Kustomize image transformers to a private registry; remove extra public LBs.

**Production Practice:** first sync may use tags `v0.10.5` that were signed; promotion quality is digest pins. Topic 12’s job is to copy those pins. If you never pin digests, `:v0.10.5` can move in ACR after a re-mirror of the same tag — Kyverno `verifyDigest` still wants the Pod spec to request a digest.

Upstream refresh: a new Boutique version is a new ADR-0009-style decision, new mirror, new base `manifests.yaml`. Do not `kustomize edit` piecemeal against `latest` upstream.

### Common errors

- Forgetting busybox/redis auxiliary sign.
- Leaving `frontend-external` Service as LoadBalancer (second public IP, extra cost, extra NSG story).
- Auto-syncing prod because the dev Application YAML was copied blindly.

## 5. What You Learned

Topic 10 deploys Boutique to `boutique-dev` through Kustomize and Argo CD auto-sync. Every image name is rewritten to ACR; redis and busybox are pinned and signed; the public Load Balancer is removed. Digest pins complete the identity story. Stage/prod wait for promotion. Screenshots replace live `dev-boutique.biroltilki.art`.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Topic 10 guide | `docs/setup/10-boutique-dev.md` | Auxiliary images and smoke |
| Base + overlays | `gitops/apps/boutique/` | ACR transforms, env patches |
| ADR-0006 | `docs/adr/0006-kustomize-boutique.md` | Why not Helm fork |
| Dev smoke | `tests/integration/dev-smoke.sh` | Lived HTTPS check |
| Screenshots | `assets/images/setup/10-dev-boutique-*.png` | Inactive DNS evidence |

## What changed

| Before | After |
|--------|--------|
| Upstream manifests applied raw. | **Kustomize ACR transforms + overlay.** |
| Extra public LB. | **Ingress only (`remove-frontend-external`).** |
| `runAsRoot` from upstream. | **Patches for policy 03.** |
| Stage/prod in the same sync. | **Dev auto-sync only in this topic.** |

`gitops/apps/boutique/overlays/dev/ingress.yaml` holds `dev-boutique.biroltilki.art`. Stage/prod ingress files change Host only. TLS secret names follow cert-manager. `base/manifests.yaml` is the upstream dump — do not edit it by hand for a one-line replica change; that is what overlays are for.

> **Independent Practice — Pin one digest by hand**
>
> Using the commented example in `overlays/dev/kustomization.yaml`, write the `images:` entry for `frontend` given a fictional `sha256:abc…`. State why Argo CD must see that commit before Kyverno sees a new Pod.
