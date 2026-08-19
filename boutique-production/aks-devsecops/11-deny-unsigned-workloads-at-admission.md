# 11. Deny Unsigned Workloads at Admission

A green pipeline that nobody enforces at the API server is a report, not a control. This chapter is Setup Topic **08**: Kyverno ClusterPolicies `00`–`04` and `policies/tests`. [ADR-0003](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0003-kyverno-admission.md) chooses Kyverno over Azure Policy for Kubernetes.

The production question is:

> What happens when someone `kubectl run`s an unsigned or `:latest` image after CI has done its job?

## 1. Unsafe starting state

The unsafe default is to “enable Kyverno later” once Boutique is up, or to run policies in Audit forever. Unsigned nginx from Docker Hub then becomes the debug pod of record. Platform namespaces must be excluded carefully: a global ACR allowlist without exclusions will brick Argo CD.

Topic 08 can install Kyverno before Topic 09 signatures exist. Signature **validation** waits for signed digests. The setup catalog's dagger footnote is the lived order.

## 2. The production model: admission is the last gate

> *Theory — Independent admission*
>
> This model enables the cluster to reject artifacts the pipeline never saw — kubectl, a compromised laptop, a bad Git overlay — using policy that does not trust CI to have been the only writer.

ADR-0003: ClusterPolicy `verifyImages` plus validation rules; no Azure Policy add-on in v1. `versions.yaml` pins Kyverno `1.12.6` / chart `3.2.7`. Policies live in `policies/kyverno/cluster/` and are synced as GitOps, not pasted into the API.

Lived enforce set:

| File | Control |
|------|---------|
| `00-registry-allowlist.yaml` | Only platform ACR |
| `01-deny-latest-tag.yaml` | No `:latest` |
| `02-verify-image-signatures.yaml` | cosign key, `ignoreTlog` / `ignoreSCT` |
| `03-require-pod-security-baseline.yaml` | No privileged; `runAsNonRoot` |
| `04-block-privileged-host-access.yaml` | No hostNetwork/PID/IPC/hostPath |

`05-verify-sbom-attestation.yaml` is Topic 17 **scaffold** (Audit first). Do not cite it as a lived deny.

## 3. How this repository implements Topic 08

> **Practice — Read the four lived supply-chain policies**
>
> Open `docs/setup/08-admission-policies.md` and `policies/kyverno/cluster/00-registry-allowlist.yaml` through `04-block-privileged-host-access.yaml`.

Allowlist (excerpt):

```yaml
validationFailureAction: Enforce
exclude:
  namespaces:
    - kube-system
    - kyverno
    - argocd
    - ingress-nginx
    - cert-manager
    - csi-test
    - monitoring
validate:
  message: "Only images from acrboutiquedevgwc.azurecr.io are allowed."
  pattern:
    spec:
      containers:
        - image: "acrboutiquedevgwc.azurecr.io/*"
```

Replace `acrboutiquedevgwc` with Terraform `acr_name`. Wrong name denies Boutique and looks like “Kyverno is broken.”

Deny latest:

```yaml
containers:
  - image: "!*:latest"
```

Upstream Boutique ships `busybox:latest` and `redis:alpine`. DR-02 and Topic 10 pin ACR copies. Policy is correct; overlays must comply.

Signature policy matches ADR-0005:

```yaml
verifyImages:
  - imageReferences:
      - "acrboutiquedevgwc.azurecr.io/*"
    mutateDigest: true
    required: true
    verifyDigest: true
    attestors:
      - entries:
          - keys:
              publicKeys: |-
                -----BEGIN PUBLIC KEY-----
                ...
              rekor:
                ignoreTlog: true
              ctlog:
                ignoreSCT: true
```

The PEM in Git is the lived public key (also in Key Vault). Rotating keys means this file plus re-sign.

> **Practice — Run the unit tests that do not need a cluster**
>
> Open `policies/tests/README.md` and `policies/tests/kyverno-test.yaml`.

```bash
cd policies/tests
kyverno test kyverno-test.yaml
```

Fixtures: `allow-compliant-workload.yaml`, `deny-non-acr-image.yaml`, `deny-latest-tag.yaml`, `deny-privileged.yaml`. Signature verification is **manual after Topic 09** — CLI tests do not substitute for `verifyImages` against real signatures. That limitation is documented; do not greenwash it.

`tests/README.md` TEST-006 is this command. GitHub Actions is still absent.

Policy `03` and `04` apply Pod Security baseline without waiting for Topic 19 PSA labels. Both can exist; ADR-0016 says PSA enforce=baseline *aligns* with Kyverno. Lived Topic 08 already denied privileged and hostPath. Topic 19’s ResourceQuota is the missing lived piece.

`policies/kyverno/kustomization.yaml` lists cluster policies for GitOps app `kyverno-policies`. Controller Helm is `gitops/platform/kyverno/`. Two Applications: engine then policies. Installing policies before the controller fails. `failurePolicy` / `validationFailureAction: Enforce` is the lived setting for 00–04.

TEST-006b (`pr-validate.sh`) will run these unit tests on PRs once Topic 14 is registered. Until then, laptops and discipline. The lived cluster still enforced them — unit tests are not a substitute for `kubectl apply` deny, but they catch YAML mistakes before sync.

`docs/troubleshooting/image-signature.md` is the signature-specific cousin: wrong PEM, `ignoreTlog` missing, digest not signed, platform image in Boutique namespace. Platform exclusions exist because Argo CD and ingress images are not in ACR. Putting Boutique in `kube-system` to skip policy is a threat-model fail.

## 4. Test the design under failure

### Lived control failure — Unsigned image presented at the API

> **Practice — Prove deny independently of CI**
>
> After policies Enforce, apply a Pod with `nginx:latest` in `boutique-dev`. Expect admission deny. If it lands, the control did not exist.

**Severity:** critical; runtime execution of untrusted content.  
**Plausible harm:** attacker-controlled process in a Boutique namespace; credential theft from mounted secrets; lateral movement on the shared cluster.  
**Potential blast radius:** all namespaces on the single cluster (ADR-0002); NetworkPolicy isolation is still scaffold (Topic 15).  
**Bounded by:** ClusterPolicies 00–02 Enforce, namespace exclusions only for platform, PSS 03–04.  
**Primary principles:** identity is digest not tag, blast-radius control, trustworthy evidence, namespaces on one cluster are not multi-account isolation.

#### Diagnosis

If the Pod is Created, check: policy `validationFailureAction`, matching kind `Pod`, exclusions accidentally including `boutique-dev`, Kyverno replicas, or `kubectl --dry-run=server` skipped. PolicyReports and `kubectl describe` events are mechanism evidence.

If deny works for `:latest` but not for an unsigned ACR digest, Topic 09 public key and `ignoreTlog` alignment are the suspects.

#### Correction

Do not set Audit to “unblock a demo.” Fix the image: mirror, scan, sign, pin digest. Temporary Audit is an exception that must be time-bounded and recorded — this pilot's lived path used Enforce for 00–04.

## Production reality

**Best Practice:** Enforce at admission for registry, tags, signatures, and host isolation.

**Production Practice:** exclusions are the real policy. Review them when adding namespaces. `csi-test` is listed on allowlist and verifyImages so the Topic 07 pod could exist; remove it after the proof. `monitoring` is excluded from deny-latest because the stack pulls many upstream tags — that is a residual. Topic 16 Checkov skips are the Terraform analogue: named residuals beat silent holes.

Kyverno 1.12.x was chosen to match key-based `verifyImages` (ADR-0005). Bumping Kyverno without testing signatures is how Enforce becomes a weekend outage.

### Common errors

- `validationFailureAction: Audit` left on 00–02 after “debugging.”
- Public key PEM indentation broken in YAML (`|-` block).
- Applying policies with `kubectl` and never GitOps-syncing — next Argo prune removes them.

## 5. What You Learned

Kyverno is the last gate: ACR only, no `:latest`, signatures required, baseline PSS, no host namespaces. CI can be bypassed; admission must not. Unit tests cover validation fixtures; signature verify is lived against Topic 09 keys. Policy `05` is scaffold.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Topic 08 guide | `docs/setup/08-admission-policies.md` | Install, placeholders, test |
| Cluster policies | `policies/kyverno/cluster/00`–`04` | Lived Enforce set |
| Tests | `policies/tests/` | `kyverno test` fixtures |
| ADR-0003 | `docs/adr/0003-kyverno-admission.md` | Why not Azure Policy |
| Troubleshooting | `docs/troubleshooting/kyverno-admission.md` | Deny-loop recovery |

## What changed

| Before | After |
|--------|--------|
| Pipeline as the only gate. | **Kyverno Enforce at the API.** |
| Docker Hub debug pods. | **ACR allowlist (with named exclusions).** |
| `:latest` from upstream busybox. | **Deny latest + Topic 10 pins.** |
| Signature-optional Audit. | **`verifyImages` required, `ignoreTlog: true`.** |

`policies/tests/resources/deny-non-acr-image.yaml` and `allow-compliant-workload.yaml` are the fixtures to read before changing exclusions. If a new platform namespace appears (Falco `falco`), add it to exclusions **and** to the threat-model residual list in the same PR.

> **Independent Practice — Propose an exclusion**
>
> Someone wants `kube-system` style exclusion for `boutique-prod` “so we can debug.” Write the blast-radius paragraph that refuses it, then an alternative (signed debug image in ACR). Do not add the exclusion.

## Further reading

Playbook article **A2** is the short public argument for Kyverno plus cosign deny of unsigned and `:latest` images.

https://github.com/btilki/devops-engineering-playbook/blob/main/articles/A2.md
