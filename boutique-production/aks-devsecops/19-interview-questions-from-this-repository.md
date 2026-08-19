# 19 — Interview Questions From This Repository

Answer from `boutique-aks-devsecops`. Topics **00–13** lived and were torn down. Topics **14–20** are **scaffold**. `prod` is a namespace on one cluster. If the clone is newer than this manuscript, start at `CHANGELOG.md`.

## 1. Why is GitHub the source of truth and Azure DevOps the pipeline runner?

Separation of duties: Git, **PRs (Pull Requests)**, and Argo **CD (Continuous Delivery)** sync live on GitHub. Jobs live in `pipelines/` on **ADO (Azure DevOps)** with **OIDC (OpenID Connect)** to Azure. There is no `.github/workflows` on purpose. `pipelines/README.md`, `docs/setup/04-ado-oidc.md`, `CONTRIBUTING.md`. Playbook **A1**.

## 2. Why must unsigned or `:latest` images not reach the cluster?

A green pipeline is a report. Admission is the control. Kyverno ClusterPolicies `00`–`04`: ACR allowlist, deny `:latest`, `verifyImages`, pod security baseline, no privileged host access. Someone can still `kubectl run`. Policy must deny. `policies/kyverno/cluster/`, `docs/setup/08-admission-policies.md`, ADR-0003. Playbook **A2**.

## 3. Why key-based cosign with `--tlog-upload=false` instead of Sigstore keyless?

ADR-0005. This pilot did not send Rekor. Kyverno uses `ignoreTlog` / `ignoreSCT`. The sister EKS repo chose keyless Fulcio. Copying Fulcio settings into this policy makes CI and admission describe different signatures. Private key in Key Vault; public PEM may live in the Kyverno policy.

## 4. Why mirror upstream Boutique instead of building from source?

ADR-0009. Pin **v0.10.5**. The security program is the platform, not a fork of eleven microservices. Mirror → Trivy CRITICAL → cosign sign by digest → ACR. `pipelines/templates/build-scan-sign.yml`, `docs/security/supply-chain.md`.

## 5. How do you promote the same digest to prod?

Same `@sha256` in stage and prod overlays. ADO environment approval for prod (ADR-0008). Manual Argo sync for stage/prod. `pipelines/azure-pipelines-promote.yml`, `docs/setup/12-promotion-stage-prod.md`, `tests/integration/promotion-smoke.sh`. Do not rebuild per environment.

## 6. How do secrets leave Git?

They never enter Git. Key Vault + Secrets Store **CSI (Container Storage Interface)** + Workload Identity. Topic 07 test pod is the proof path. `docs/security/secrets-management.md`, `gitops/platform/secrets-store-csi/`, `examples/csi-secret-test/`. Cosign private material in Key Vault.

## 7. What happens if someone bypasses the pipeline?

Kyverno still sees the Pod spec. Non-ACR registry, `:latest`, or unsigned digest is denied. That is the difference between “we scan” and DevSecOps. Troubleshooting: `docs/troubleshooting/kyverno-admission.md`, `docs/troubleshooting/image-signature.md`.

## 8. Why destroy ACR on teardown?

ADR-0010. Leftover registries are leftover admission surfaces and leftover cost. Rebuild requires full re-mirror and re-sign. `docs/setup/13-teardown.md`, `scripts/operations/teardown.sh` (confirm phrase `destroy-boutique-platform`). Playbook **A3**. Bootstrap state is kept by default.

## 9. What have Topics 14–20 not proven?

PR CI, NetworkPolicies, Checkov, SBOM attestations, Falco, namespace/KV hardening, optional ZAP **DAST (Dynamic Application Security Testing)**. Files exist. ADR-0013 is literally scaffold-first. Do not say they ran on this pilot. Chapter 16 exists so you can say that out loud.

## 10. Is this production-ready?

No. The README forbids that sentence. One **AKS (Azure Kubernetes Service)** cluster, three namespaces, rebuild **DR (Disaster Recovery)** in hours, no WAF/Front Door/HSM, no 24×7 on-call. Call it a **production pilot**. Honesty is part of the security program (`CONTRIBUTING.md` public-share hygiene).

## How to use this appendix

Draw the chain: GitHub → ADO OIDC → Trivy → cosign → ACR → Git digest pin → Kyverno → Argo → AKS → destroy ACR. Name the sister EKS keyless choice as a different ADR, not a bug. Keep unsigned-must-not-land as the last sentence.
