# 14. Promote the Same Digest Through Approval

Rebuilding `:v0.10.5` for prod “to be sure” produces a different digest than stage. This chapter is Setup Topic **12**: stage and prod overlays, **ADO (Azure DevOps)** environment approval ([ADR-0008](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0008-ado-prod-approval-gate.md)), and promotion/rollback tests.

The production question is:

> How does the same signed digest move from `boutique-dev` to `boutique-prod` without CI applying to the cluster and without pretending those namespaces are separate estates?

## 1. Unsafe starting state

The unsafe default is `kubectl rollout` in prod, or a pipeline that `docker build`s per environment. Tags lie. Rebuilds surprise. Auto-sync on prod bypasses the human gate.

`prod` here is namespace `boutique-prod` on the **same** AKS cluster ([ADR-0002](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0002-single-cluster-multi-namespace.md)). Approval reduces accidental Git updates; it does not provide multi-account isolation.

## 2. The production model: copy pins, then sync

> *Theory — Digest promotion*
>
> This model enables prod to run only a digest already scanned, signed, and observed in a lower namespace — with Git as the change record and Argo CD as the applier.

`docs/architecture/05-deployment-flow.md`:

```text
Mirror → Trivy → cosign → dev overlay → Argo auto-sync
  → stage overlay (same digest) → manual Argo sync
  → ADO Environment Approval → prod overlay → manual Argo sync
```

Rule from `docs/runbooks/promotion-rollback.md`: never promote a digest to prod that was not validated in stage.

CI still does not deploy. `pipelines/templates/promote-digest.yml` **commits** overlay pins to GitHub; Argo CD pulls. Prod job uses `environment: prod` so ADO can require an approver.

## 3. How this repository implements Topic 12

> **Practice — Read the environment matrix**
>
> Open `docs/setup/12-promotion-stage-prod.md` and the stage/prod Applications.

| Env | Namespace | Hostname | Argo sync | ADO gate |
|-----|-----------|----------|-----------|----------|
| dev | `boutique-dev` | `dev-boutique.biroltilki.art` | Automatic | — |
| stage | `boutique-stage` | `stage-boutique.biroltilki.art` | **Manual** | — |
| prod | `boutique-prod` | `boutique.biroltilki.art` | **Manual** | **Approval** |

Prod overlay includes `replicas-patch.yaml` (frontend replicas: 2). That is capacity on the same user pool, not HA across zones.

> **Practice — Read the promote pipeline**
>
> Open `pipelines/azure-pipelines-promote.yml` and `pipelines/templates/promote-digest.yml`.

```yaml
trigger: none
pr: none
# MirrorScanSign then Promote_stage then Promote_prod
environment: ${{ parameters.targetEnvironment }}
```

The deploy job downloads `digest-manifest.json`, installs kustomize, rewrites `gitops/apps/boutique/overlays/${TARGET_ENV}`, and pushes to GitHub (`persistCredentials: true`). If approval is rejected, Git does not change; Argo CD has nothing new to sync.

Manual Option A in the runbook: copy the `images:` digest block from dev → stage → prod kustomization files, commit, **then** Sync in the Argo UI. First promotion is often manual so you see the pins.

Preconditions: `./tests/integration/dev-smoke.sh`, Grafana Boutique Overview, SLO budget not exhausted, Kyverno enforcing signatures.

After sync: `./tests/integration/promotion-smoke.sh stage` then `prod`. Rollback: restore prior `images:` block or `git revert`; `./tests/integration/rollback-smoke.sh <env>`. Argo history rollback is allowed in emergency but creates Git drift — reconcile Git afterward (`docs/runbooks/promotion-rollback.md`).

Lived screenshots: `12-stage-boutique-homepage.png`, `12-prod-boutique-homepage.png`. Inactive DNS: those PNGs are the prod proof.

`docs/operations/03-rollback.md` prefers Git revert over Argo History:

```bash
git log -5 --oneline -- gitops/apps/boutique/overlays/<env>/kustomization.yaml
git revert <bad-commit-sha> --no-edit
git push origin main
```

Then manual Argo sync for stage/prod; auto-sync for dev. Capture current image before revert: `kubectl get deploy -n boutique-<env> frontend -o jsonpath='{.spec.template.spec.containers[0].image}'`. If that image is a tag without digest, you are already off-contract.

Promote template pushes to **GitHub** (`persistCredentials`). ADO environment `prod` is the approval UX. There is no GitHub CODEOWNERS gate required (ADR-0008 consequence). A GitHub branch rule that blocks the pipeline’s push will stall promotion — coordinate GitHub permissions with ADO.

24h stage soak is the runbook’s ideal; the test minimum is “same session after stage validation.” Do not market the latter as a 24h soak.

## Lived operator commands (Topic 12)

```bash
./tests/integration/dev-smoke.sh
# copy images: digest pins dev → stage kustomization, git push
# Argo CD → boutique-stage → Sync
./tests/integration/promotion-smoke.sh stage
# ADO: queue azure-pipelines-promote.yml or copy pins to prod after approval
# Argo CD → boutique-prod → Sync
./tests/integration/promotion-smoke.sh prod
# rollback drill:
./tests/integration/rollback-smoke.sh stage
```

Queue-time: `trigger: none` on the promote pipeline. Confirm ADO Environments `stage` (no approval) and `prod` (approval). Grafana Boutique Overview is a precondition, not a nice-to-have. Screenshots `12-stage-boutique-homepage.png` and `12-prod-boutique-homepage.png` are inactive-DNS evidence.

Limits: approval is not multi-account isolation. Same-session stage validation is not a 24h soak. After ACR destroy, these smokes cannot run and old digests cannot be rolled back without Topic 09.

## 4. Test the design under failure

### Independent control failure — Prod overlay rebuilt from `:v0.10.5` tag

> **Practice — Catch a silent rebuild**
>
> A pipeline job `docker pull`s upstream again for “prod freshness” and writes a new digest to `overlays/prod` that stage never ran.

**Severity:** high; unvalidated artifact in the prod namespace.  
**Plausible harm:** regression or malicious substitution not observed in stage; SLO burn; Kyverno may still admit it if signed.  
**Potential blast radius:** `boutique-prod` plus shared node/ingress with dev and stage.  
**Bounded by:** ADR-0008, promote template using existing digest-manifest, runbook “same digest” rule, manual Argo sync.  
**Primary principles:** identity is digest not tag, CI never deploys the cluster, namespaces on one cluster are not multi-account isolation, Git is the deploy authority.

#### Diagnosis

Compare `images:` sha256 in stage vs prod kustomization. If they differ, promotion failed the contract even if both are signed. ADO approval of a bad commit is still a bad commit — approval is not cryptographic equality.

#### Correction

Copy stage pins to prod. Revert the rebuild commit. Do not kubectl set image. After ACR teardown, you cannot roll back to a destroyed digest; re-mirror first (Chapter 15).

A second failure: auto-sync enabled on `boutique-prod`. Correction: restore manual sync per ADR-0004/0008.

## Production reality

**Best Practice:** promote the digest-manifest, not a new build, with a human gate on prod Git writes.

**Production Practice:** namespaces are not accounts. A bad digest in prod still shares nodes, ingress IP, and Kyverno with dev. Approval reduces fat-finger Git; it does not contain a cluster-admin kubeconfig.

After ACR destroy (Chapter 15), rollback to yesterday’s digest is impossible unless you re-mirror. Promotion runbooks that assume registry retention contradict ADR-0010.

### Common errors

- `targetEnvironment: prod` queued without stage pins matching.
- Enabling auto-sync on `boutique-prod` Application.
- Using Argo rollback and leaving Git on the bad digest (next selfHeal on a mis-copied spec fights you).

## 5. What You Learned

Topic 12 promotes one signed digest through Git to stage then prod. ADO approval gates the Git write for prod; Argo CD manual sync gates the cluster. Tests cover promotion and rollback. `prod` remains a namespace. Screenshots remain after DNS dies.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Topic 12 guide | `docs/setup/12-promotion-stage-prod.md` | Overlay and ADO env setup |
| Promote pipeline | `pipelines/azure-pipelines-promote.yml` | Manual trigger, stage then prod |
| Promote template | `pipelines/templates/promote-digest.yml` | Digest → Git |
| ADR-0008 | `docs/adr/0008-ado-prod-approval-gate.md` | Human gate choice |
| Runbook | `docs/runbooks/promotion-rollback.md` | Same-digest rule |
| Tests | `tests/integration/promotion-smoke.sh`, `rollback-smoke.sh` | Lived checks |
| Screenshots | `assets/images/setup/12-*-boutique-homepage.png` | Inactive FQDNs |

## What changed

| Before | After |
|--------|--------|
| Rebuild per environment. | **Same digest in three overlays.** |
| kubectl in prod. | **Git pin + manual Argo sync.** |
| No human gate. | **ADO environment approval (ADR-0008).** |
| Argo history as source of truth. | **Git revert preferred (`03-rollback.md`).** |

`gitops/apps/boutique/stage-application.yaml` and `prod-application.yaml` must not set `automated` sync. Prod overlay `replicas-patch.yaml` is two frontend pods on the same cluster — say that when someone hears “prod replicas.” Tests TEST-009 and TEST-012 in `tests/README.md` are the lived promotion/rollback commands.

> **Independent Practice — Write the approval ticket**
>
> List the evidence an approver must see before clicking Approve: digest equality with stage, smoke output, Grafana screenshot or dashboard name, Kyverno not in deny-loop, SLO freeze status. Keep it to one screen.

**Figure 14.1 — Inactive.** Production storefront `boutique.biroltilki.art` after digest promotion.

![Prod boutique homepage](https://raw.githubusercontent.com/btilki/boutique-aks-devsecops/main/assets/images/setup/12-prod-boutique-homepage.png)

Source: `assets/images/setup/12-prod-boutique-homepage.png`. The hostname is inactive; this is historical evidence of the same digest on the `prod` namespace.
