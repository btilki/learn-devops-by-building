# 10 — Build, Scan, and Sign — Then Open a Digest Merge Request

A pipeline that ends in `kubectl apply` is a second control plane. A pipeline that pushes `:latest` and comments “GitOps later” is a tag factory. Topic 10 is the standing contract: **CI (Continuous Integration)** may write **ECR (Elastic Container Registry)** and open a digest **MR (Merge Request)** for `dev` only.

> How do you build, Trivy-gate, cosign-sign, and propose Git changes without ever holding cluster deploy permission — including after the cluster is gone?

## 1. The unsafe starting state: CI as deployer

GitLab templates for Kubernetes often include `kubectl` or `helm upgrade`. Adding `argocd sync` “for reliability” duplicates Argo **CD (Continuous Delivery)** and forces a kubeconfig into CI variables. Static `AWS_SECRET_ACCESS_KEY` appears next.

ADR-0001 forbids that. ADR-0006 chooses Sigstore keyless signing so there is also no long-lived cosign private key. Topic 10 (`docs/setup/10-gitlab-ci-digest.md`) wires GitLab **OIDC (OpenID Connect)** to the IAM role from Topic 04.

**Lived** as digest MRs on the pilot. **Post-teardown:** pipelines are dormant unless `ENABLE_PILOT_CI=true` (needs AWS) or `ENABLE_REPO_GATES=true` (MR test-stage only). That is not a broken project; it is the cost of destroying ECR and the OIDC role.

## 2. The production model: evidence in CI, intent in Git

> *Theory — CI as proposer*
>
> The pipeline produces a scanned, signed digest and proposes it as desired state; humans merge; Argo pulls. The pipeline never becomes a cluster principal.

```21:33:docs/ci.md
## Hard rules

| Rule | Rationale |
|------|-----------|
| CI **never** runs `kubectl apply`, `helm upgrade` to the cluster, or `argocd sync` | Git is the only deploy authority |
| CI **never** stores static AWS access keys | OIDC → IAM role (ECR only) |
| Successful build opens an MR that changes **only** `image.digest` under `gitops/envs/dev/values/` | Digest-only promotion path |
| Trivy **CRITICAL** findings fail the pipeline | Supply-chain gate (pin **0.71.0**) |
| Images are signed with cosign **Sigstore keyless** | ADR-0006 |
```

Stages: `test → build → scan → sign → sbom → gitops`. The `sbom` stage is Phase 12 **scaffold** authored into the same file (Topic 15). The lived path through M3 was test/build/scan/sign/digest MR.

## 3. How this repository implements the pipeline

> **Practice — Read workflow rules as a teardown control**
>
> Open `.gitlab-ci.yml` from the top through `stages:` and `helm_lint`. Explain why `when: never` is the default after M4.

```1:21:.gitlab-ci.yml
# boutique-eks-gitops — GitLab CI
# Setup Topic 10 · Contract: docs/ci.md · Pins: docs/versions.md
#
# Stages: test → build → scan → sign → sbom → gitops (digest MR to envs/dev only)
# HARD RULES: no kubectl / no argocd CLI / no static AWS keys / no prod path writes
# Topic 15: CycloneDX SBOM + cosign attest after sign (ADR-0007)
# Topic 16: gitleaks + checkov + kyverno policy_test in test stage
#
# Post-teardown (M4): pipelines are DORMANT by default. AWS/ECR/OIDC are gone;
# auto-runs on main would fail and look like a broken project. Re-enable only
# when rebuilding: set CI/CD variable ENABLE_PILOT_CI=true (and restore AWS).
# Optional (no AWS): ENABLE_REPO_GATES=true runs MR pipelines for test-stage jobs only.

workflow:
  rules:
    - if: $ENABLE_PILOT_CI == "true" && $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $ENABLE_PILOT_CI == "true" && $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $ENABLE_PILOT_CI == "true" && $CI_COMMIT_BRANCH =~ /^ci\/.*/
    # Topic 16: security/lint gates without ECR — MR only (build/scan/sign still skipped)
    - if: $ENABLE_REPO_GATES == "true" && $CI_PIPELINE_SOURCE == "merge_request_event"
    - when: never
```

**Lived** pins: Trivy `0.71.0`, cosign `2.4.3`, Boutique source `v0.10.6`. Default `BOUTIQUE_BUILD_MODE: ecr-bootstrap` retags Topic 09 images rather than rebuilding from GitHub every time.

### Keyless signing

```7:16:docs/adr/0006-cosign-signing-mode.md
## Context

Container images pushed to ECR must be signed for supply-chain integrity. Long-lived cosign private keys in CI variables create theft risk and rotation burden. GitLab can issue OIDC identity tokens consumable by Sigstore Fulcio for **keyless** signatures.

## Decision

- Use **cosign 2.4.x** with **Sigstore keyless** signing.
- Obtain identity via GitLab CI `id_tokens` → `SIGSTORE_ID_TOKEN` (audience `sigstore`).
- Do **not** store cosign private keys in GitLab CI variables for routine signing.
```

**Lived.** Admission verify of those signatures is **scaffold** (ADR-0007). Signing without admit is still a real CI control; it is not a closed loop at the webhook.

### Digest MR shape

`docs/ci.md` shows the only allowed diff:

```diff
# gitops/envs/dev/values/frontend.yaml
-  digest: "sha256:old…"
+  digest: "sha256:new…"
```

No prod path writes. Forbidden job content includes `kubectl`, `argocd`, and `AWS_SECRET_ACCESS_KEY`. Variables `AWS_ROLE_ARN` and flags live in GitLab settings, not in Git.

The gitops job encodes the forbid list in the runner, not only in a comment:

```407:410:.gitlab-ci.yml
      bash <<'EOS'
      set -euo pipefail
      command -v kubectl >/dev/null 2>&1 && { echo "FORBIDDEN: kubectl present"; exit 1; }
      command -v argocd >/dev/null 2>&1 && { echo "FORBIDDEN: argocd present"; exit 1; }
```

**Lived.** Job name `gitops_digest_mr` needs the `sbom` matrix artifacts, then opens a branch `ci/digests-${CI_PIPELINE_ID}` that patches only `gitops/envs/dev/values`. Topic 10’s remaining Setup steps are GitLab variable `AWS_ROLE_ARN`, matching OIDC subject, and proving Trivy CRITICAL fails the pipeline. Node services apply `ci/docker/patch-protobufjs.Dockerfile` to bump `protobufjs` to **7.5.5** (CVE-2026-41242) before scan — a supply-chain fix that still does not deploy.

After M4, turning `ENABLE_PILOT_CI=true` without ECR produces Failed pipelines. `docs/ci.md` “Post-teardown status” is the operational truth: dormant is correct.

`docs/ci.md` forbids `kubectl`/`argocd`/kubeconfig deploys, writing digests straight to `main` without an MR, and patching `gitops/envs/prod/**` from CI. Optional operator verify is `cosign verify` with GitLab Fulcio identity regexp against an ECR digest — not a cluster apply. Admission verify remains **scaffold**. Do not paste kubeconfigs into GitLab variables to “make verify easier.”

> **Practice — Trace OIDC from Terraform to the job**
>
> Open `terraform/modules/iam_gitlab_oidc/main.tf` (Chapter 4) and Topic 10 Step 10.1. Confirm `gitlab_project_path` must match `path_with_namespace`. State what happens if you set `ENABLE_PILOT_CI=true` today without ECR.

Gitleaks, Checkov, and `policy_test` jobs exist in the same `.gitlab-ci.yml`. They are Topic 16 **scaffold** as *enabled gates*; files are real. Checkov is `soft_fail` until baselined.

## 4. Test the design under failure

**Scenario:** gitops job “helpfully” patches `gitops/envs/prod` so humans skip promotion.

**Severity:** CI becomes a prod deployer via Git.  
**Plausible harm:** unsigned-in-practice promotion; CODEOWNERS raced or bypassed; stage never saw the digest.  
**Potential blast radius:** all prod Boutique overlays, then the cluster after manual (or accidental auto) sync.  
**Bounded by:** gitops job path guards, `docs/ci.md` hard rules, CODEOWNERS, prod manual sync.  
**Primary principles:** Git is the only deploy authority; CI has ECR and Git permission, not cluster deploy permission; image identity is digest, not tag.

### Diagnosis

MR diff touches `gitops/envs/prod` or `gitops/envs/stage`. Job script lacks the path guard. `ENABLE_PILOT_CI` pipelines running after M4 fail on ECR — that is expected, not this scenario.

### Recovery

Close the MR. Restore the job to `dev` only. If it merged, revert. Do not sync prod. Rotate the Git token the job used to open MRs if it had overly broad `write_repository` on all paths.

Topic 10 Setup remaining steps (10.2+) are workstation verification of OIDC assume-role, a first pipeline on a `ci/` branch or `main` with `ENABLE_PILOT_CI`, Trivy CRITICAL failure proof, and the digest MR merged to `dev` only. `docs/ci.md` lists forbidden strings in `.gitlab-ci.yml`. Gitleaks/Checkov/`policy_test` sit in `test` but are Phase 12 **scaffold** as *gates you rely on after teardown* unless `ENABLE_REPO_GATES` is on. The `sbom` stage is the same: authored in the lived file, not a lived admission loop.

## 5. What You Learned

CI builds, scans, signs, and proposes digest MRs for dev. It does not deploy. After teardown, dormant pipelines are a control. You can now walk Topic 10, `.gitlab-ci.yml`, `docs/ci.md`, and ADR-0006.

### Durable outputs

- Pipeline: `.gitlab-ci.yml`
- Contract: `docs/ci.md`
- Setup: `docs/setup/10-gitlab-ci-digest.md`
- Signing ADR: `docs/adr/0006-cosign-signing-mode.md`

> **Independent Practice — Design the gitops job deny list**
>
> Write the checks a gitops job must run before `git push`: path glob, forbidden strings (`kubectl`, `argocd sync`), no `prod/` files, single-line digest hunks. Explain how a compromised job still cannot call EKS if IAM stays ECR-only.

**Figure 10.1 — Inactive.** GitLab CI pipeline passed: test → build → scan → sign → sbom → gitops digest MR.

![GitLab CI pipeline passed](https://raw.githubusercontent.com/btilki/boutique-eks-gitops/main/assets/images/setup/10-gitlab-ci-pipeline-passed.png)

Source: `assets/images/setup/10-gitlab-ci-pipeline-passed.png`. Pipelines are dormant after M4 unless `ENABLE_PILOT_CI` is set.

Chapter 6 pointed at playbook **E1**. This chapter is the pipeline half of that same argument: CI proposes; Git records; Argo reconciles.

`docs/ci.md` remaining contract: re-sign of an already-signed digest is OK because ECR tags are immutable; OIDC `id_tokens` for AWS (`GITLAB_OIDC_TOKEN`) and Sigstore (`SIGSTORE_ID_TOKEN`); no `AWS_SECRET_ACCESS_KEY`. Topic 10 Setup GUI tables document GitLab CI/CD variables. After teardown those variables may still exist in GitLab — disable `ENABLE_PILOT_CI` so they cannot create Failed badges against missing ECR.

Pipeline stages in `.gitlab-ci.yml` are `test`, `build`, `scan`, `sign`, `sbom`, `gitops`. `helm_lint` lints all eight charts. `gitleaks` / `checkov` / `policy_test` are Topic 16 **scaffold** jobs in the same file. Build default is `ecr-bootstrap` retag of Topic 09 images (`BOUTIQUE_SOURCE_TAG: bootstrap`, Boutique `v0.10.6`). Scan pin Trivy `0.71.0`. Sign pin cosign `2.4.3`. The gitops job fails if `kubectl` or `argocd` binaries exist in the image — a mechanical ADR-0001 check.

Topic 10 is FR-07 in the requirements table. Without it, Topic 09 bootstrap would be the only image path and the standing loop would be a human retag. With it, humans promote; machines propose. `docs/setup/10-gitlab-ci-digest.md` estimated time is 2–3 hours on a live GitLab project — optional after teardown unless you rebuild.

## Next

Chapter 11 promotes by copying those digests through stage to prod — humans and CODEOWNERS, not a second pipeline.
