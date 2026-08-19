# 3 — Make the Repository the Control Plane

A Git repo full of docs is not a control plane until versions are pinned, prod paths have owners, and local checks refuse secrets and format drift. The unsafe default is to apply Terraform from a laptop copy that has no CODEOWNERS, no pin matrix, and a Makefile that “bootstraps the cluster.”

> How do you make `boutique-eks-gitops` the operational control plane *before* remote state exists, so later topics write into a stable tree instead of inventing paths under pressure?

## 1. The unsafe starting state: apply from an unpublished tree

Topic 01 (`docs/setup/01-prerequisites.md`) exists because **OIDC (OpenID Connect)**, **DNS (Domain Name System)**, and **SMTP (Simple Mail Transfer Protocol)** failures surface late and waste paid cluster time. Topic 02 (`docs/setup/02-repo-foundation.md`) exists because Terraform modules and GitOps manifests need an agreed tree and **ADRs (Architecture Decision Records)** before the first apply.

Skipping foundation looks like speed. It produces missing `gitops/envs/prod`, no CODEOWNERS, and CLIs that drift off `docs/versions.md`. Then Kyverno, Helm, and **CI (Continuous Integration)** disagree about what “1.31” means.

Neither topic creates **AWS (Amazon Web Services)** billables. That is deliberate.

## 2. The production model: the repo is desired state plus gates

> *Theory — Repository as control plane*
>
> Treat layout, version pins, ownership, and local policy as production controls that exist even when the cluster does not, so apply cannot start from an unpublished or unowned tree.

The control plane is not Argo **CD (Continuous Delivery)** yet. It is this repository: `terraform/`, `gitops/`, `charts/`, `docs/`, `tests/`, and the root meta files that prevent silent drift.

Topic 02’s first check is the directory spine:

```43:55:docs/setup/02-repo-foundation.md
for d in \
  terraform/modules terraform/envs/prod \
  gitops/bootstrap gitops/apps gitops/platform \
  gitops/envs/dev gitops/envs/stage gitops/envs/prod \
  charts examples \
  docs/adr docs/runbooks docs/setup \
  tests/helm tests/policy tests/smoke
 do
  test -d "$d" && echo "OK  $d" || echo "MISSING  $d"
done
```

**Lived** as authoring and verification. No cluster required then or now.

## 3. How this repository implements the spine

> **Practice — Verify the control-plane spine on the clone**
>
> From the clone root, run the Topic 02 directory loop and `make docs-check`. Confirm `docs/versions.md`, `CODEOWNERS`, `Makefile`, and `.pre-commit-config.yaml` exist. Do not apply Terraform.

### Pins before CLIs

`docs/versions.md` is the pin matrix. Region, **EKS (Elastic Kubernetes Service)** minor, node size, Terraform floor, Helm, Trivy, and cosign are not tribal knowledge:

```12:33:docs/versions.md
## Cloud & region

| Item | Pin | Notes |
|------|-----|--------|
| AWS region | `eu-central-1` | Locked |
| DNS zone | `biroltilki.art` | Route53 |
| EKS version | **1.31** | Control plane + kubectl minor match |
| Node instance | `m6i.large` ×3 (ASG 2–5) | On-Demand; fallback `m7i.large` if capacity fails (document in setup) |

## Local CLI (Topic 01 verify)

| Tool | Required version | Why |
|------|------------------|-----|
| AWS CLI | v2.x (latest stable 2.x) | IAM, EKS kubeconfig, ECR |
| Terraform | **≥ 1.9** | Backend + module features used in foundation |
| kubectl | **1.31.x** | Within one minor of EKS 1.31 |
| Helm | **3.16.x** | Platform chart installs |
```

**Lived** as the matrix the pilot ran. After teardown, the pins remain the rebuild contract. Topic 01’s job is to install these versions and prove AWS/Route53/GitLab/SMTP *access* without creating VPC or **NAT (Network Address Translation)**.

### CODEOWNERS is the prod human gate in Git

```1:11:CODEOWNERS
# CODEOWNERS — boutique-eks-gitops
# Prod digest and env overlays require explicit ownership (@btilki).
# Setup Topic 11: enable “Code owner approval” on the protected default branch in GitLab.
# Without that GitLab setting, this file is documentation-only.

# Default reviewers for control-plane changes
* @btilki

# Production environment — digest promotion path (locked)
/gitops/envs/prod/ @btilki
/gitops/envs/prod/** @btilki
```

**Lived** once GitLab “Code owner approval” was enabled (Topic 11). The file alone is not enforcement. The comment says so. A control plane that forgets the GitLab setting has a documented owner and no actual gate.

### Makefile does not deploy

```1:21:Makefile
# Makefile — validation helpers only.
# Does NOT install CLIs, apply Terraform, or deploy to the cluster.
# Setup authority remains docs/setup/.

.PHONY: help lint docs-check

help:
	@echo "Targets:"
	@echo "  make lint       - terraform fmt -check (when modules exist) + basic file checks"
	@echo "  make docs-check - verify Setup Guide index and versions matrix exist"

lint:
	@echo "==> docs/versions.md"
	@test -f docs/versions.md
	@echo "==> terraform fmt (if .tf files present)"
	@if find terraform -name '*.tf' 2>/dev/null | grep -q .; then \
		terraform fmt -check -recursive terraform; \
	else \
		echo "No .tf files — skip fmt"; \
	fi
	@echo "lint: OK"
```

`docs-check` then asserts the Setup Guide topics 01–19, ADRs through 0010, Kyverno verify policies, WAF/Falco stubs, and teardown runbook. That is how Phase 12 scaffolds stay first-class in Git without being lived.

### Pre-commit is local policy, not cloud apply

```1:24:.pre-commit-config.yaml
# Pre-commit hooks — lint/format only (no cloud apply).
# Install: pip install pre-commit && pre-commit install
# Run: pre-commit run --all-files
# TODO(setup:2.5): adjust rev pins if org mirror differs.
# Topic 16: gitleaks hook added alongside detect-private-key.

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
        args: [--allow-multiple-documents]
      - id: check-added-large-files
        args: [--maxkb=500]
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
        args: ["--config", ".gitleaks.toml"]
```

**Lived** for format and private-key detection during the pilot. The Gitleaks hook is the same pin as Topic 16’s CI job. Topic 16’s Checkov and Kyverno CLI unit tests are **scaffold** as *CI gates after teardown* (pipelines dormant); the files are in Git.

> **Practice — Prove the Makefile cannot apply**
>
> Read the entire `Makefile`. Confirm there is no `terraform apply`, `helm upgrade`, or `kubectl` target. Contrast that with `docs/setup/README.md`, which is the bootstrap authority.

`docs/setup/README.md` states the rule: if README, chat, or scripts conflict with `docs/setup/`, the Setup Guide wins. The topic table 01–19 is the walking order for the rest of this book.

## 4. Test the design under failure

**Scenario:** Prod digest MR merged without code-owner approval because CODEOWNERS was never enabled in GitLab.

**Severity:** human prod gate is documentation-only.  
**Plausible harm:** any Maintainer can land `gitops/envs/prod/**` digest changes; manual Argo sync then applies unowned intent.  
**Potential blast radius:** all Boutique workloads in the `prod` namespace on the shared cluster.  
**Bounded by:** CODEOWNERS file, GitLab protected-branch setting (Topic 11), Argo prod manual sync (still a second gate), digest-only MR shape.  
**Primary principles:** Git is the only deploy authority; one cluster and three namespaces are a cost decision, not isolation; CI has ECR and Git permission, not cluster deploy permission.

### Diagnosis

`CODEOWNERS` comments say the GitLab setting is required. If an MR to `gitops/envs/prod/values/frontend.yaml` merged with only a non-owner approval, the setting is off. `git log` on that path will not show `@btilki` as a required reviewer.

### Recovery

Enable code-owner approval on the default branch. Do not rewrite `main`. If a bad digest already merged, follow `docs/rollback.md` (Chapter 11): `git revert`, then manual Argo sync for prod. Treat the missing GitLab setting as an incident, not as a docs typo.

## 5. What You Learned

The repository is the control plane when pins, tree, ownership, and local checks exist *before* AWS. You can now walk Topics 01–02 as lived foundation: prerequisites and repo spine, with `make docs-check` as the cheap verifier.

### Durable outputs

- Prerequisites and access checks: `docs/setup/01-prerequisites.md`
- Repo foundation: `docs/setup/02-repo-foundation.md`
- Pin matrix: `docs/versions.md`
- Prod path owners: `CODEOWNERS`
- Local verify only: `Makefile`, `.pre-commit-config.yaml`

> **Independent Practice — Add a twelfth service without breaking the spine**
>
> Product wants `recommendationservice` in the same GitOps model. List every path Topic 02 already created that you would have to extend (charts, env overlays, ECR list, ApplicationSet, CODEOWNERS if prod). State which files you must *not* change in the first MR (Terraform apply, Kyverno weaken, Makefile deploy target). Keep namespaces-on-one-cluster explicit.

## Next

Chapter 4 is the first high-cost step: remote state, then VPC, EKS, ECR, and identities that still cannot deploy from CI.
