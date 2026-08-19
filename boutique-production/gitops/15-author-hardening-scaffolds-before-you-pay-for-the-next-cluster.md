# 15 — Author Hardening Scaffolds Before You Pay for the Next Cluster

A YAML file in Git is not a passed milestone. Phase 12 exists so the next rebuild does not start from a blank security backlog. Topics 15–19 and **ADRs (Architecture Decision Records)** 0007–0010 are **scaffold**: authored, not live-validated on this pilot. **AWS (Amazon Web Services)** was already destroyed.

> How do you encode signature admission, **CI (Continuous Integration)** repo gates, Argo **CD (Continuous Delivery)** AppProjects, canary analysis, **WAF (Web Application Firewall)**, and Falco in Git without pretending they protected the lived cluster?

## 1. The unsafe starting state: either skip hardening or claim it ran

Two failure modes: (1) close the pilot and lose the design; (2) tick “signed images verified at admission” because `verify-image-signatures.yaml` exists. ROADMAP Phase 12 is explicit: **Scaffold authored**; live enable after rebuild.

`ROADMAP.md` slices 15–19 are all 🚧. This chapter walks every slice. None of it is **lived** production proof.

## 2. The production model: Audit-first files, off-by-default cost

> *Theory — Scaffold-before-spend*
>
> Record the next cluster’s controls in Git with fail-open or disabled defaults so rebuilds can enable them after digest signing is proven — and so readers can see the gap between file and evidence.

Enable order after a future Topic 04–12 rebuild: 15 (admit) after signed digests exist; 16 (gates) can run without AWS via `ENABLE_REPO_GATES`; 17 (AppProjects) before Applications that reference them; 18 (analysis) on stage first; 19 (WAF/Falco) only when you accept cost and noise.

## 3. How this repository implements Phase 12

> **Practice — Prove scaffolds exist without AWS**
>
> Run the file tests from Topics 15–19 Step 1 (or `make docs-check`). Every path below must exist. None requires `terraform apply`.

### Topic 15 / ADR-0007 — signature + SBOM (scaffold)

Signing in CI was **lived** (ADR-0006). Admission verify was not enforced on the pilot.

```1:21:docs/adr/0007-admission-verify-and-sbom.md
# ADR-0007: Admission signature verify + CycloneDX SBOM attestations

- **Status:** Accepted (scaffold)  
- **Date:** 2026-07-25  
- **Setup:** Topic 15  

## Context

ADR-0006 established **Sigstore keyless** cosign signing in GitLab CI. Signing alone does not stop an unsigned or foreign image from being admitted if Kyverno only checks digest/ECR. Operators also need a durable software bill of materials (**SBOM**) for vulnerability and license review.

## Decision

1. **Admission:** Kyverno `verifyImages` ClusterPolicies require Sigstore keyless signatures (and optionally CycloneDX attestations) for `*.dkr.ecr.eu-central-1.amazonaws.com/boutique-eks-gitops/*` in `dev` / `stage` / `prod`.
2. **Default mode:** Policies ship as **`validationFailureAction: Audit`** so Topic 09 bootstrap digests and first rebuild are not blocked. Switch to **Enforce** only after CI-signed (and attested) digests are proven.
```

```19:36:gitops/platform/kyverno/policies/verify-image-signatures.yaml
spec:
  # Audit until rebuild + signed digests exist — see Topic 15 Step 15.4
  validationFailureAction: Audit
  background: false
  failurePolicy: Fail
  webhookTimeoutSeconds: 30
  rules:
    - name: verify-sigstore-keyless
      match:
        any:
          - resources:
              kinds:
                - Pod
              namespaces:
                - dev
                - stage
                - prod
      verifyImages:
```

**Scaffold.** Sister file `verify-sbom-attestation.yaml` is also Audit. `.gitlab-ci.yml` `sbom` stage and `docs/setup/15-supply-chain-verify-sbom.md` complete the loop on paper. Enforce before signed digests exist will block Boutique.

### Topic 16 — Gitleaks, Checkov, policy unit tests (scaffold as CI gates)

```1:18:.checkov.yaml
# Checkov config — Topic 16 / docs/setup/16-ci-security-gates.md
# Soft-fail keeps the scaffold green until findings are baselined after rebuild.
# Flip soft_fail to false once suppressions below are reviewed.

compact: true
framework:
  - terraform
directory:
  - terraform
soft_fail: true
download-external-modules: false

# Pilot-known trade-offs (single cluster / cost). Revisit before Enforce-style CI.
skip-check:
  # Single NAT Gateway for cost (architecture cost model)
  - CKV_AWS_130
```

**Scaffold.** `.gitleaks.toml`, `tests/policy/unit/kyverno-test.yaml` (plus digest/deny fixtures), and CI jobs `gitleaks` / `checkov` / `policy_test` are in Git. `ENABLE_REPO_GATES=true` runs them on **MRs (Merge Requests)** without **ECR (Elastic Container Registry)**. Pre-commit already runs Gitleaks locally (Chapter 3). Soft-fail Checkov is not a passed IaC gate.

### Topic 17 / ADR-0008 — AppProjects; SSO examples (scaffold)

Lived Argo used `project: default` and local admin. **Scaffold** files:

```1:18:gitops/bootstrap/argocd/hardening/projects/boutique-platform.yaml
# Platform AppProject — controllers, policy, monitoring (not Boutique workloads)
# Setup Topic 17 · ADR-0008
# Synced early (wave 5) via platform-manifests; child apps reference this project.
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: boutique-platform
  namespace: argocd
  annotations:
    argocd.argoproj.io/sync-wave: "5"
spec:
  description: Platform add-ons (ingress, policy, secrets, observability, rollouts)
  sourceRepos:
    - https://gitlab.com/btilki/boutique-eks-gitops.git
```

`gitops/bootstrap/argocd/hardening/projects/boutique-workloads.yaml` allowlists namespace kinds for `dev`/`stage`/`prod` only (`clusterResourceWhitelist: []`). ApplicationSets already reference `boutique-platform` / `boutique-workloads` — **critical ordering**: sync AppProjects first on rebuild or child apps fail. Dex/SSO and notifications: `hardening/rbac/argocd-rbac-cm.example.yaml` and `hardening/notifications/configmap.example.yaml` — examples only; `values.yaml` keeps them **disabled**. ADR-0008 status: Accepted (scaffold).

### Topic 18 / ADR-0009 — AnalysisTemplates (scaffold)

Lived canary was timed pauses. **Scaffold** ClusterAnalysisTemplates `frontend-http-smoke` and `frontend-pod-ready` at wave 26:

```1:18:gitops/platform/argo-rollouts/analysis/frontend-http-smoke.yaml
# ClusterAnalysisTemplate — HTTP smoke against canary Service (Topic 18)
# Args: url (e.g. http://frontend-canary.stage.svc:8080/)
apiVersion: argoproj.io/v1alpha1
kind: ClusterAnalysisTemplate
metadata:
  name: frontend-http-smoke
  annotations:
    argocd.argoproj.io/sync-wave: "26"
spec:
  args:
    - name: url
  metrics:
    - name: http-smoke
      count: 3
      interval: 15s
      failureLimit: 1
```

Stage/prod keep `canary.analysis.enabled: false`. Operators copy `gitops/envs/*/values/frontend-analysis.example.yaml` after rebuild proof. Chart `rollout.yaml` already has the hook (Chapter 12). Enabling analysis on prod without stage proof is how you page yourself with curl Jobs.

### Topic 19 / ADR-0010 — WAF + Falco (scaffold, off)

```1:28:terraform/modules/waf/main.tf
# Optional WAFv2 Web ACL for ALB (Topic 19 / ADR-0010)
# Default: disabled (count = 0) — enable after rebuild via enable_waf = true

variable "enabled" {
  type        = bool
  description = "When false, no WAF resources are created"
  default     = false
}
...
resource "aws_wafv2_web_acl" "this" {
  count = var.enabled ? 1 : 0
```

Root `module "waf"` uses `var.enable_waf` (default false). Association is Ingress annotation (`examples/waf-ingress-annotation.example.yaml`), not a hard-coded ALB ARN.

```1:16:gitops/platform/falco/values.yaml
# Falco Helm values — Topic 19 / ADR-0010 scaffold
# Pin: Falco chart **4.19.3** (falcosecurity) — confirm with helm show chart before enable
# NOT synced by default — add ApplicationSet element from falco-applicationset-snippet.yaml.example

# Driver: modern-bpf preferred on EKS 1.31 (no DKMS on nodes)
driver:
  enabled: true
  kind: modern-bpf
```

**Scaffold.** Falco is not in the live `platform-apps` list. DaemonSet cost/noise is why. ADR-0010: Accepted (scaffold).

> **Practice — Label a PR description**
>
> Write one paragraph for a rebuild MR that enables *one* of: Enforce signatures, Checkov hard-fail, Dex, analysis, or `enable_waf`. Include the lived prerequisite and the blast radius if you enable it too early.

`tests/README.md` and `tests/policy/unit/` are the offline Kyverno fixtures. They do not prove a webhook on a cluster that does not exist.

## 4. Test the design under failure

**Scenario:** Flip `verify-image-signatures` to Enforce on a rebuild that still uses Topic 09 unsigned bootstrap digests.

**Severity:** total Boutique admission deny.  
**Plausible harm:** empty storefront, Argo Degraded, operators disable *all* Kyverno (including lived digest/ECR policies).  
**Potential blast radius:** Pods in `dev` / `stage` / `prod`.  
**Bounded by:** Audit default, Topic 15 warnings, ADR-0007 “Enforce after signed digests.”  
**Primary principles:** scaffold in Git is not lived proof; image identity is digest, not tag; Git is the only deploy authority.

### Diagnosis

ClusterPolicy `validationFailureAction: Enforce` while `cosign verify` fails on `:bootstrap` images. Kyverno reports signature errors. Apps OutOfSync.

### Recovery

Return to Audit in Git and sync. Finish CI-signed digests; promote those; then Enforce. Do not delete ClusterPolicies to “get the shop up.” Do not claim the pilot verified admission — it did not.

## 5. What You Learned

Phase 12 is a complete scaffold set: Topics 15–19, ADRs 0007–0010, verify policies, Checkov/Gitleaks/policy tests, AppProjects, AnalysisTemplates, WAF module, Falco values. None of it is lived proof. You can now author the next cluster’s hardening before you pay for nodes.

### Durable outputs (all scaffold)

- 15: `docs/setup/15-supply-chain-verify-sbom.md`, ADR-0007, `gitops/platform/kyverno/policies/verify-*.yaml`
- 16: `docs/setup/16-ci-security-gates.md`, `.checkov.yaml`, `.gitleaks.toml`, `tests/policy/unit/`
- 17: `docs/setup/17-argocd-hardening.md`, ADR-0008, `gitops/bootstrap/argocd/hardening/`
- 18: `docs/setup/18-canary-analysis.md`, ADR-0009, `gitops/platform/argo-rollouts/analysis/`
- 19: `docs/setup/19-edge-runtime-waf-falco.md`, ADR-0010, `terraform/modules/waf/`, `gitops/platform/falco/`

> **Independent Practice — Rank enablement for a 48-hour rebuild**
>
> You have two days and the same cost model. Rank Topics 15–19 by “enable live” vs “leave scaffold.” Justify with blast radius and dollar cost. Keep at least two items off. Do not enable Falco and WAF together “because security.”

## Next

Chapter 16 states what you can defend, what sister books cover, and what this title refused.
