# 11 — Promote by Copying Digests, Not by Redeploying

Redeploying prod from **CI (Continuous Integration)** “with the same Dockerfile” does not give you the same bytes. Rebuilding for each environment is how tags sneak back in. Topic 11 is human promotion: copy `image.digest` `dev → stage → prod`.

> How do you move a proven digest to production with CODEOWNERS and manual Argo **CD (Continuous Delivery)** sync — and roll back with `git revert` instead of `kubectl rollout undo`?

## 1. The unsafe starting state: each env is a new build

“Promote” in many pipelines means “run the prod job.” That job rebuilds, retags `:prod`, and applies. Stage and prod then diverge by cache, base-image race, and who pressed the button. Rollback becomes “run the old job” if the old job still exists.

This repository’s promotion is a Git diff of digest strings. Argo reconciles. **CI** is not in the promote path.

**Lived.** Checklist C1–C3 and C6 record real MRs (`promote/stage-20260719`, prod `!11`, rollback `!12`).

## 2. The production model: copy identity, gate prod, revert identity

> *Theory — Digest copy as promotion*
>
> The artifact does not change at an environment boundary; Git copies its digest, review gates the prod path, and rollback restores the previous digest in Git.

```11:20:docs/promotion.md
## Rules (non-negotiable)

| Rule | Detail |
|------|--------|
| Digest-only | Promotion MRs change **only** `image.digest` under `gitops/envs/<env>/values/*.yaml` |
| No chart edits | Do not change templates, ports, or replica counts in a promote MR |
| No CI promote | GitLab CI writes **dev** only ([docs/ci.md](ci.md)) |
| Stage first | Never skip stage for the pilot happy path |
| Prod ownership | `gitops/envs/prod/**` requires `@btilki` CODEOWNERS approval |
| Prod sync | After merge, **manual** Argo sync for `*-prod` apps (no auto-sync) |
```

`docs/architecture/05-deployment-flow.md` is the same flowchart in architecture language.

## 3. How this repository implements promotion and rollback

> **Practice — Walk the copy loop on the clone**
>
> Read `docs/promotion.md` procedures for stage and prod. Open `CODEOWNERS`. Confirm GitLab must enable code-owner approval or the file is documentation-only (Chapter 3).

### Copy, do not rebuild

```30:47:docs/promotion.md
## Procedure — promote `dev` → `stage`

```bash
git fetch origin
git checkout -b promote/stage-$(date +%Y%m%d) origin/main

# Copy digests service-by-service (example: all boutique services)
for svc in frontend productcatalogservice cartservice checkoutservice \
           currencyservice paymentservice shippingservice redis; do
  dig=$(yq '.image.digest' "gitops/envs/dev/values/${svc}.yaml")
  yq -i ".image.digest = \"${dig}\"" "gitops/envs/stage/values/${svc}.yaml"
done

git add gitops/envs/stage/values/*.yaml
git status  # must show ONLY stage values files
git commit -m "promote: copy digests dev → stage"
```

Prod procedure is identical except the destination path, CODEOWNERS, and **manual** Argo sync after merge. Hostnames: `dev-boutique` / `stage-boutique` / `boutique` under `biroltilki.art` (**inactive** after teardown).

Topic 11 (`docs/setup/11-promotion.md`) operationalizes GitLab settings: protected `main`, code-owner approval, and rehearsal of one promote MR.

### Rollback is revert

```7:17:docs/rollback.md
## Principle

Desired state lives in Git. Rollback = return previous digests via **`git revert`** (or a new MR that restores known-good digests). Argo reconciles. Do **not** `kubectl set image` or force-sync an unreproducible state.

## When to rollback

| Signal | Action |
|--------|--------|
| Stage unhealthy after promote | Revert stage digest MR; fix forward in dev |
| Prod unhealthy after manual sync | Revert prod digest MR; manual Argo sync again |
| Canary abort (Topic 12) | Revert digest MR and/or abort Rollout — prefer Git as source of truth |
```

Anti-patterns listed: `kubectl rollout undo` only (next sync undoes you), delete pods hoping for old image, force-push `main`, CI hot-patch prod.

> **Practice — Name the two prod levers**
>
> After a prod digest MR merges, list the two remaining human actions: CODEOWNERS already fired; Argo manual sync still required. Explain what happens if you merge and walk away (nothing on the cluster, if auto-sync stays off).

`docs/operations/03-rollback.md` and `02-deployment.md` are day-2 restatements of the same contract for on-call.

Operations deployment is explicit about what not to do:

```10:16:docs/operations/02-deployment.md
## Purpose

Promote **digest-only** releases via Git so Argo reconciles the desired state.

## When to use / When not to use

**Use** after CI merged digests to `gitops/envs/dev/**` and stage validation passed.  
**Do not** `kubectl set image` or edit live Rollouts as the release mechanism.
```

**Lived** as handbook. Step 2 of that document is Argo sync: wait for `*-stage` auto-sync; for prod, press Sync yourself. Validation is HTTPS on the env host when the cluster exists. After teardown, validation is “Git still has the digest pins; DNS is inactive.”

Topic 11 also requires enabling GitLab code-owner approval — the CODEOWNERS file comment you read in Chapter 3. Checklist C2 recorded that the protected branch setting was on for the pilot MRs (`ccd3f8f`, `108f0bf` / `!11`).

## 4. Test the design under failure

**Scenario:** Operator `kubectl rollout undo` in `prod` after a bad frontend digest, and leaves Git pointing at the bad digest.

**Severity:** Git and cluster diverge; next Argo sync re-breaks prod.  
**Plausible harm:** brief recovery, then the same outage on self-heal or the next manual sync; audit trail shows Git “green.”  
**Potential blast radius:** `prod` frontend (and any other undone workloads); shared cluster still at risk if the digest is also bad in stage.  
**Bounded by:** rollback.md anti-patterns, prod manual sync, CODEOWNERS on the revert MR, canary abort (Chapter 12) as temporary containment.  
**Primary principles:** Git is the only deploy authority; image identity is digest, not tag; one cluster and three namespaces are a cost decision, not isolation.

### Diagnosis

`kubectl -n prod get rollout frontend -o yaml` image digest ≠ `gitops/envs/prod/values/frontend.yaml`. Argo OutOfSync or about to self-heal if someone enabled auto-sync. Git log still has the bad promote commit without revert.

### Recovery

Abort canary if needed (containment). Open a revert MR of the promote commit; get `@btilki` approval; merge; **manual** sync prod. Verify `https://boutique.biroltilki.art` when live. Keep the revert URL as checklist evidence (C6 / E6). Do not force-push.

Reviewer checklist in `docs/promotion.md`: diff is digest lines only; source env matches what was tested; stage precedes prod; prod MR has `@btilki`. Mixing replica or Ingress changes into a promote MR is how you lose the ability to revert a digest without reverting a hostname. Split those MRs.

`docs/rollback.md` alternative — pin known-good digests from `git show <GOOD_SHA>:gitops/envs/prod/values/frontend.yaml` — is for messy revert graphs. It is still a digest-only MR. Evidence for Topic 13 is the revert URL plus post-sync curl when live.

## 5. What You Learned

Promotion is copying digests under review; rollback is reverting Git. You can now walk Topic 11, `docs/promotion.md`, `docs/rollback.md`, and prod CODEOWNERS as one gate.

### Durable outputs

- Promotion: `docs/promotion.md`, `docs/setup/11-promotion.md`
- Rollback: `docs/rollback.md`
- Owners: `CODEOWNERS`

> **Independent Practice — Skip-stage request**
>
> Leadership wants an emergency prod-only digest from a laptop build. Using promotion rules and ADR-0001, write the refuse-or-exception note. If you allow an exception, bound it: still a Git digest, still CODEOWNERS, still manual sync, still a follow-up to realign stage, still teardown if this was a one-off cluster.

CODEOWNERS without GitLab enforcement is the failure you already classified. Topic 11 Setup Step 11.2 is enabling that setting; 11.3 is rehearsing one stage promote; 11.4 is prod with manual sync. The lived SHAs in the checklist are the rehearsal record.

```64:75:docs/rollback.md
## What not to do

| Anti-pattern | Why |
|--------------|-----|
| `kubectl rollout undo` only | Drift from Git; next sync undoes you |
| Delete pods hoping for old image | Digests in Git still point at bad image |
| Force-push rewrite of `main` | Breaks audit trail; forbidden unless disaster recovery with explicit approval |
| CI hot-patch prod digests | Violates CI contract |

## Evidence

Keep the revert MR URL and post-sync curl output for Topic 13 / PRODUCTION_CHECKLIST.
```

Paste that table into an incident channel when someone suggests `kubectl rollout undo`.

Stage and prod value paths, hostnames, and sync modes are the promotion.md table you already opened. Skipping stage on the happy path is forbidden even if prod CODEOWNERS would still fire. The lived path used `promote/stage-20260719` then `!11` to prod.

## Next

Chapter 12 adds frontend canary on stage and prod so a copied digest is not an all-or-nothing cutover.
