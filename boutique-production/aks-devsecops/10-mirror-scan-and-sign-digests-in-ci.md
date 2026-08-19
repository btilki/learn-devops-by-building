# 10. Mirror, Scan, and Sign Digests in CI

Admission cannot verify a signature that was never created. This chapter is Setup Topic **09**: the **ADO (Azure DevOps)** pipeline that mirrors Online Boutique **v0.10.5**, fails on Trivy **CRITICAL**, and signs each **digest** with **cosign 2.2.4** using `--tlog-upload=false`. It implements [ADR-0005](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0005-cosign-key-based-signing.md) and [ADR-0009](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0009-mirror-upstream-images.md).

The production question is:

> How do you turn Google-published images into ACR-resident, scanned, key-signed digests without rebuilding Boutique and without Rekor?

## 1. Unsafe starting state

The unsafe default is `image: frontend:latest` from Docker Hub, or “we scan in a spreadsheet.” A valid-looking storefront can still be an unscanned, unsigned, public image. The other default is keyless cosign copied from `boutique-eks-gitops`. This cluster's Kyverno expects a PEM and `ignoreTlog: true`.

This repo **mirrors**; it does not compile Boutique. FR-04 is scan/sign/push, not SAST on Go/Node source.

## 2. The production model: scan the digest you sign

> *Theory — Mirror-scan-sign by digest*
>
> This model enables Kyverno to admit only ACR images whose exact digest was Trivy-gated and signed by the Key Vault key — not a floating tag and not a transparency-log identity this pilot does not operate.

`docs/security/supply-chain.md` states the layers: pinned v0.10.5, private ACR, Trivy CRITICAL, cosign 2.2.4 key-based, Kyverno verify. SBOM attestation is Topic 17 **scaffold** (`enableSbomAttest` in templates) — do not treat SPDX as lived for the 00–13 pilot.

Order rule from `docs/architecture/04-data-flows.md`: scan before sign; sign the scanned digest.

Unlike the EKS sister (keyless / Fulcio), this pipeline does:

```bash
cosign sign --key cosign.key --tlog-upload=false -y <acr>.azurecr.io/<service>@sha256:<digest>
```

Verify in the job uses `--insecure-ignore-tlog`. That flag is honesty, not a skip of signatures.

## 3. How this repository implements Topic 09

> **Practice — Read the pipeline contract**
>
> Open `docs/setup/09-ci-pipeline.md`, `pipelines/azure-pipelines.yml`, and `pipelines/templates/build-scan-sign.yml`.

Main pipeline:

```yaml
trigger:
  branches:
    include:
      - main
pr: none
```

**PRs (pull requests)** do not mirror. That is intentional: ACR and signing are `main`-only. Topic 14 adds a separate PR pipeline without OIDC.

`azure-pipelines.yml` validates required variables, then includes `templates/build-scan-sign.yml`. The job uses `AzureCLI@2` with `azureSubscription: $(azureServiceConnection)` — the Topic 04 OIDC connection.

Lived loop (excerpt):

```bash
docker pull "${SRC_IMAGE}"
docker push "${DEST_VERSION_TAG}"
# resolve digest from ACR
trivy image --scanners vuln --severity CRITICAL --ignore-status fixed --exit-code 1 "${DEST_DIGEST_REF}"
cosign sign --key "${COSIGN_KEY}" --tlog-upload=false -y "${DEST_DIGEST_REF}"
cosign verify --key "${PUB_KEY}" --insecure-ignore-tlog "${DEST_DIGEST_REF}"
```

Keys are fetched from Key Vault each run (`cosign-private-key`, `cosign-public-key`), chmod 600, not cached as pipeline artifacts. `COSIGN_PASSWORD=""` matches how Topic 09 generates the key pair.

Eleven services from `versions.yaml`: frontend, cartservice, checkoutservice, currencyservice, emailservice, paymentservice, productcatalogservice, recommendationservice, shippingservice, adservice, loadgenerator. Upstream: `us-central1-docker.pkg.dev/google-samples/microservices-demo/<service>:v0.10.5`.

Topic 09 also generates the key pair locally, stores it in Key Vault, and pastes the **public** PEM into `policies/kyverno/cluster/02-verify-image-signatures.yaml`. That Git commit is what admission will trust.

`--ignore-status fixed` on Trivy is a **test** concession for pinned upstream CVEs on v0.10.5. It is documented in the template comment. Do not silently generalize it to “ignore CRITICAL.”

Lived evidence: `assets/images/setup/09-ado-pipeline-supply-chain-success.png` and `09-acr-repositories-frontend.png`. After ACR destroy, those screenshots are the registry.

`pipelines/templates/variables.yml` is the runtime twin of `versions.yaml`:

```yaml
trivyVersion: 0.72.0
cosignVersion: 2.2.4
cosignSignArgs: --tlog-upload=false
enableSbomAttest: "true"
boutiqueVersion: v0.10.5
```

`enableSbomAttest: "true"` means a **rebuild** that runs current YAML will generate SPDX attestations. The lived 00–13 pilot did not treat SBOM as a passed milestone; ADR-0014 is scaffold. If you rebuild today, Topic 17’s pipeline steps may execute inside Topic 09’s template. Do not back-date that as lived 2026-07 evidence. Set `false` only as the template comment allows: emergency rebuild.

Artifact `digest-manifest.json` is what Topic 12 consumes. Without it, promote jobs fail closed. PublishPipelineArtifact is the handoff; it is not admission.

`docs/troubleshooting/pipeline-failures.md` and `image-signature.md` cover Trivy exit 1, ACR login, and cosign verify mismatch. A CRITICAL finding on a pinned upstream image is an ADR-0009 moment: you do not patch Boutique source in this repo; you pin, ignore-fixed as documented, or wait for a new upstream tag with a new ADR.

## Lived operator commands (Topic 09)

```bash
cosign generate-key-pair
az keyvault secret set --vault-name <KV> --name cosign-private-key --file cosign.key
az keyvault secret set --vault-name <KV> --name cosign-public-key --file cosign.pub
# paste public PEM into policies/kyverno/cluster/02-verify-image-signatures.yaml
# register pipelines/azure-pipelines.yml on main (pr: none)
az acr repository show --name <ACR> --image frontend:v0.10.5
```

Delete local `cosign.key` after vault upload. `COSIGN_PASSWORD` empty matches the pipeline. Screenshot `09-ado-pipeline-supply-chain-success.png` and `09-acr-repositories-frontend.png` remain after ACR destroy. Auxiliary redis/busybox wait for Topic 10.2 but must be signed the same way.

Limits: SBOM attest in the current template may run on a *future* rebuild; it was not a lived 00–13 milestone. `enableSbomAttest: "true"` in Git is not proof Topic 17 lived. Trivy `--ignore-status fixed` is a documented upstream concession, not a general CRITICAL ignore.

## 4. Test the design under failure

### Independent control failure — Sign a tag, admit a different digest

> **Practice — Reject tag identity**
>
> CI signs `:v0.10.5` without resolving digest. Someone retags `:v0.10.5` on ACR to a different manifest. Kyverno `verifyDigest: true` is the last chance.

**Severity:** critical; substitution at the registry.  
**Plausible harm:** unsigned or different content runs under a familiar tag.  
**Potential blast radius:** every Boutique namespace pulling that name.  
**Bounded by:** digest resolution before Trivy, sign `@sha256`, Kyverno `mutateDigest` / `verifyDigest`, overlay digest pins in later topics.  
**Primary principles:** identity is digest not tag, trustworthy evidence, CI never deploys the cluster, Git is the deploy authority.

#### Diagnosis

Tags move. Digests do not. The pipeline's `az acr repository show-manifests` query exists to freeze identity before scan. Signing only the tag would authenticate a moving pointer.

#### Correction

Keep `@digest` through Trivy, cosign, artifact `digest-manifest.json`, and GitOps overlays (Chapter 14). Rotate keys if a private key leaked (`docs/security/supply-chain.md` rotation). Re-mirror after ACR teardown — old signatures do not survive [ADR-0010](https://github.com/btilki/boutique-aks-devsecops/blob/main/docs/adr/0010-destroy-acr-on-teardown.md).

A second failure: enabling GitHub Actions to “also sign.” Two signers, one Kyverno key, unclear provenance. Correction: one ADO pipeline; no `.github/workflows`.

## Production reality

**Best Practice:** sign the digest you scanned; store the private key in Key Vault; verify in the same job.

**Production Practice:** keyless signing would require Rekor availability and Kyverno tlog settings this pilot explicitly disabled. The EKS sister made that bet. This AKS book’s unique operational duty is key rotation (`docs/security/supply-chain.md`). After ACR destroy, signatures are gone; the PEM in Git is not a registry.

Microsoft-hosted `ubuntu-22.04` agents install Trivy and cosign every run. That is slower and more reproducible than a snowflake VM with leftover keys.

### Common errors

- Signing `:v0.10.5` only and hoping tags are immutable.
- Uploading to Rekor while Kyverno `ignoreTlog: true` — extra public log without a verifier.
- Enabling `pr:` on `azure-pipelines.yml` so every PR mirrors 11 images.

## 5. What You Learned

Topic 09 mirrors v0.10.5 to ACR, gates CRITICAL (with a documented upstream ignore), and key-signs digests with `--tlog-upload=false`. That is a different honest choice from the EKS sister's keyless path. CI writes evidence and Git (later); it does not apply to the cluster. Unsigned images still must not be schedulable — that is Chapter 11.

### Durable outputs

| Artifact | Location | Keep it because |
|----------|----------|-----------------|
| Topic 09 guide | `docs/setup/09-ci-pipeline.md` | Keygen, ADO, Kyverno PEM |
| Main pipeline | `pipelines/azure-pipelines.yml` | `pr: none`, Validate + mirror |
| Supply-chain template | `pipelines/templates/build-scan-sign.yml` | Mirror, Trivy, cosign |
| ADRs | `docs/adr/0005-*.md`, `0009-*.md` | Key-based sign; mirror not build |
| Narrative | `docs/security/supply-chain.md` | Inventory and rotation |
| Screenshots | `assets/images/setup/09-*.png` | Lived pipeline and ACR |

## What changed

| Before | After |
|--------|--------|
| Pull Google images at runtime. | **Mirror to ACR, then pull ACR only.** |
| Tag identity. | **Digest from ACR manifests before Trivy.** |
| Keyless copy-paste. | **`--tlog-upload=false` + Key Vault key.** |
| PR builds of 11 images. | **`pr: none` on the supply-chain pipeline.** |

`docs/security/supply-chain.md` key rotation: generate new pair, store in KV, update Kyverno PEM, re-sign, verify old signatures fail. That procedure is lived documentation even when the vault is gone. Article A2 in the playbook retells unsigned deny; this chapter’s files are the primary source.

**Figure 10.1 — Inactive.** Azure DevOps supply-chain pipeline green (mirror / Trivy / cosign).

![ADO pipeline supply chain success](https://raw.githubusercontent.com/btilki/boutique-aks-devsecops/main/assets/images/setup/09-ado-pipeline-supply-chain-success.png)

**Figure 10.2 — Inactive.** ACR `frontend` `v0.10.5` with digest tags.

![ACR frontend repositories](https://raw.githubusercontent.com/btilki/boutique-aks-devsecops/main/assets/images/setup/09-acr-repositories-frontend.png)

Sources: `assets/images/setup/09-ado-pipeline-supply-chain-success.png`, `assets/images/setup/09-acr-repositories-frontend.png`. ACR was destroyed on teardown (ADR-0010); these images are historical.

> **Independent Practice — Compare keyless vs key-based**
>
> In one paragraph, explain what Rekor would add and what operational duty this pilot accepted instead (key storage, rotation, `ignoreTlog`). Name the Kyverno fields that must change if you ever switch. Do not switch.
