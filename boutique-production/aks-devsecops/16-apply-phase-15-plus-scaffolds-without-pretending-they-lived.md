# 16. Apply Phase 15+ Scaffolds Without Pretending They Lived

A YAML file in Git is not a passed milestone. This chapter covers Setup Topics **14–20** and **ADRs (Architecture Decision Records) 0013–0017**: PR CI, NetworkPolicies, Checkov, SBOM attestations, Falco, namespace hardening, and optional DAST. All are **scaffold**. Topics 00–13 lived and were torn down.

The production question is:

> How do you keep fuller DevSecOps work reviewable without claiming the lived AKS cluster ever ran it?

## 1. Unsafe starting state

The unsafe default is to mark ROADMAP rows ✅ and speak in the past tense: “we deployed Falco,” “PRs are gated,” “east-west is default-deny.” [ADR-0013](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0013-scaffold-first-phase15.md) exists because rebuilding Azure solely to author files is costly. The consequence is mandatory labeling: **Scaffold ✅ ≠ cluster-proven**.

Roadmap Phase 13 hardening was **skipped**. Phase 15+ supersedes it. Do not reopen Phase 13 as lived history.

## 2. The production model: scaffold first, apply later

> *Theory — Two-mode delivery*
>
> This model enables the repository to grow controls as files and setup topics now, and to apply them only after a Topics 00–12 rebuild — without rewriting the lived charter.

`docs/implementation/phase15-plus.md`:

| Mode | What | Azure required? |
|------|------|-----------------|
| **Scaffold** | Pipelines, policies, GitOps stubs, TF stubs, setup topics, ADRs | No |
| **Apply later** | Rebuild 00–12, then execute Topics 14–20 | Yes |

Each Topic 14–20 guide already marks **Apply later** / **Deferred validation**. This chapter does not convert those steps into a fake lab.

## 3. How this repository implements Topics 14–20

> **Practice — Inventory the scaffold packages**
>
> Open each setup topic 14–20 and the matching ADR. Write “not lived” on every validation that needs a cluster.

### Topic 14 / Phase 16 — PR CI (ADR-0013 package 2)

`docs/setup/14-pr-ci.md`: dedicated pipeline `pipelines/azure-pipelines-pr.yml` runs pre-commit, `tests/terraform/validate.sh`, Checkov, `kyverno test`. Supply-chain `azure-pipelines.yml` stays `pr: none`. **PRs (pull requests)** must not mirror/sign. Local equivalent: `make pr-validate` / `tests/ci/pr-validate.sh`. Lived pilot did not require this pipeline to be registered in ADO.

### Topic 15 / Phase 17 — NetworkPolicies

`docs/setup/15-network-policies.md` and `gitops/apps/boutique/base/networkpolicies/`:

```yaml
# 00-default-deny-ingress.yaml
spec:
  podSelector: {}
  policyTypes:
    - Ingress
```

Allow rules in `10-allow-frontend.yaml` and `20-allow-backends.yaml` match Boutique call paths. **CNI (Container Network Interface)** without `network_policy = "azure"` **does not enforce** these objects. Lived cluster used Azure CNI; NPM enable is a rebuild-time Terraform flag. Negative tests need a live cluster.

### Topic 16 / Phase 18 — Checkov

`docs/setup/16-iac-scanning.md`, `tests/terraform/checkov.sh`, `tests/terraform/.checkov.yaml`. Checkov **3.2.510**. `soft-fail: false`. Skip list is the honesty artifact: public API server, no private cluster, no Azure Policy add-on (Kyverno is **SSOT (single source of truth)**), public ACR, Key Vault Allow ACL, no purge protection. Removing a skip without fixing Terraform breaks CI; adding a skip without a comment hides risk. Runnable **locally today**; ADO job is “apply later” with Topic 14 registration.

### Topic 17 / Phase 19 — SBOM + attestations (ADR-0014)

`docs/setup/17-sbom-attestations.md`. Trivy `spdx-json`, `cosign attest --type spdxjson`, same Key Vault key, `--tlog-upload=false`. Kyverno `05-verify-sbom-attestation.yaml` starts in **Audit**. Enforce before attestations exist will block deploys. `enableSbomAttest` is already in `build-scan-sign.yml`; generating attestations still needs live ACR. Not lived on the torn-down pilot.

### Topic 18 / Phase 20 — Falco (ADR-0015)

`docs/setup/18-runtime-security.md`, `gitops/platform/falco/`, chart `9.1.0`, modern **eBPF (extended Berkeley Packet Filter)**, JSON logs → Promtail → Loki. Microsoft Defender for Containers is **opt-in** (`terraform/modules/aks/DEFENDER-OPT-IN.md`), not wired in `environments/dev`. AKS module already `ignore_changes` on `microsoft_defender`. Lived Topic 11 did not run Falco.

### Topic 19 / Phase 21 — Namespace / KV hardening (ADR-0016)

`docs/setup/19-namespace-hardening.md`. **PSA (Pod Security Admission)** `enforce=baseline`, warn/audit `restricted` on `boutique-*` namespaces (already labeled in overlay `namespace.yaml` files). LimitRange + ResourceQuota under `base/hardening/`. Optional Key Vault Deny ACL + purge protection **complicates teardown** (ADR-0010 path). Default remains Allow / purge false.

### Topic 20 / Phase 22 — Optional ZAP DAST (ADR-0017)

`docs/setup/20-dast.md`, `pipelines/azure-pipelines-dast.yml`, `tests/ci/dast-zap.sh`. **OWASP (Open Worldwide Application Security Project)** **ZAP (Zed Attack Proxy)** baseline, manual trigger, `dastFailOnWarn: false`. Scan only hostnames you operate. Needs live HTTPS. Advisory; not a merge gate. Phase 15+ is complete **without** running DAST.

Policy `05` header is the labeling standard to copy:

```yaml
# SCAFFOLD: validationFailureAction is Audit until a full mirror+attest pipeline has run.
spec:
  validationFailureAction: Audit
```

Falco values (`gitops/platform/falco/values.yaml`): `driver.kind: modern_ebpf`, `json_output: true`, HTTP output off, modest requests on D4s_v6. Metrics disabled until a ServiceMonitor exists. Privileged/eBPF on nodes is the residual ADR-0015 accepted.

Checkov skips in `tests/terraform/.checkov.yaml` name CKV_AZURE_6 (public API), 115 (private cluster), 116 (Azure Policy add-on), 139 (ACR public), and KV purge/ACL IDs. Topic 19 says remove matching skips when Deny/purge are enabled. That is how scaffold closes a lived tradeoff without rewriting history.

`tests/kubernetes/` is empty on purpose (`tests/README.md`: do not invent greenwash tests). Scaffold does not fill it with fake kubeconform success.

> **Practice — Say the apply order out loud**
>
> From `docs/setup/README.md`: Topics 00–12 live again → `14 → 15 → 16` (CI/net/IaC), `17` (SBOM), `18`–`19` (runtime + hardening), `20` optional. Teardown remains Topic 13.

## Production reality

**Best Practice:** author fuller controls as apply-later packages after a lived core.

**Production Practice:** every Topic 14–20 file that can run locally (Checkov, kyverno test, pr-validate) is still not “lived on AKS.” Local green is useful; it is not Topic 18 Falco Ready.

Goals G-07–G-13 and FR-05–FR-11 in `phase15-plus.md` are acceptance criteria **after apply**. Using them as past-tense resume bullets is the failure in §4.

### Common errors

- Flipping SBOM policy to Enforce before re-mirror.
- Applying NetworkPolicies without `network_policy=azure`.
- Running ZAP against a hostname you do not operate.
- Enabling Defender and Log Analytics together and undoing ADR-0012.

## Scaffold files to open without applying

```bash
ls pipelines/azure-pipelines-pr.yml tests/ci/pr-validate.sh
ls gitops/apps/boutique/base/networkpolicies/
ls tests/terraform/.checkov.yaml tests/terraform/checkov.sh
ls policies/kyverno/cluster/05-verify-sbom-attestation.yaml
ls gitops/platform/falco/
ls gitops/apps/boutique/base/hardening/
ls pipelines/azure-pipelines-dast.yml tests/ci/dast-zap.sh
```

Local: `make checkov`, `make pr-validate`, `kyverno test policies/tests`. These can pass on a laptop with no Azure. That is **not** Topic 18 applied. Falco `values.yaml` `driver.kind: modern_ebpf` still needs a kernel and a rebuilt cluster. ZAP needs a live URL you operate.

Limits: ROADMAP scaffold ✅ is files. Live checklists inside Topics 14–20 were not ticked on the torn-down pilot. Checkov can pass locally because skips encode lived tradeoffs — that is honesty, not a hardened subscription.

## 4. Test the design under failure

### Independent control failure — Demo script claims “Falco is in production”

> **Practice — Correct a slide**
>
> A talk says the AKS platform “includes Falco, Checkov on every PR, and default-deny NetworkPolicy.” The cluster is torn down; Topic 18 was never applied.

**Severity:** medium–high; false residual-risk picture.  
**Plausible harm:** leadership skips funding real runtime detection; a rebuild ships without NPM and believes NetworkPolicy YAML is enforcement.  
**Potential blast radius:** next lived environment plus every reader of the talk.  
**Bounded by:** ADR-0013, honesty labels, ROADMAP scaffold vs live columns.  
**Primary principles:** lived evidence beats scaffold, explicit contracts, namespaces on one cluster are not multi-account isolation.

#### Diagnosis

ROADMAP “Scaffold ✅” means files exist. Live apply checklists inside Topics 14–20 are empty of timestamps from the 00–13 pilot. `gitops/platform/falco/` in Git is not `kubectl get pods -n falco`.

#### Correction

Speak in two sentences: lived path was Topics 00–13 with Kyverno + signed digests; Phase 15+ is authored for apply-after-rebuild. If you apply, tick the topic's live validation — then you may change the tense.

## 5. What You Learned

Topics 14–20 and ADRs 0013–0017 are first-class and unproven on this pilot. PR CI must not trigger mirror. NetworkPolicy YAML needs Azure NPM. Checkov skips document pilot tradeoffs. SBOM attestations reuse key-based cosign. Falco is the runtime detector; Defender is opt-in. PSA/quotas and KV ACL are reversible. DAST is optional and advisory. None of that is a lived green cluster.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| ADR-0013 | `docs/adr/0013-scaffold-first-phase15.md` | Two-mode rule |
| Phase plan | `docs/implementation/phase15-plus.md` | Packages 1–8 |
| Topics 14–20 | `docs/setup/14-pr-ci.md` … `20-dast.md` | Apply-later checklists |
| ADRs 0014–0017 | `docs/adr/0014-` … `0017-` | SBOM, Falco, PSA/KV, ZAP |
| PR/Checkov/DAST files | `pipelines/azure-pipelines-pr.yml`, `tests/terraform/.checkov.yaml`, `azure-pipelines-dast.yml` | Scaffold implementation |

## What changed

| Before | After |
|--------|--------|
| Phase 13 skipped, story ended. | **Phase 15+ packages 1–8 in Git (ADR-0013).** |
| No PR gates in ADO. | **`azure-pipelines-pr.yml` authored, not necessarily registered.** |
| East-west open. | **NetworkPolicy YAML present; NPM not lived.** |
| Signatures without SBOM. | **ADR-0014 Audit policy; Enforce later.** |
| No runtime detector. | **Falco GitOps; Defender opt-in docs.** |

`docs/implementation/plan.md` still describes the lived 00–13 path. `phase15-plus.md` is the scaffold plan. Keep both; do not merge them into one past-tense timeline.

> **Independent Practice — Write a rebuild ticket for one package**
>
> Pick Topic 15 or 18. Write acceptance criteria that distinguish “manifests in Git” from “enforced on AKS.” Include the Terraform or kernel prerequisite. Do not mark the ticket done from Git alone.
