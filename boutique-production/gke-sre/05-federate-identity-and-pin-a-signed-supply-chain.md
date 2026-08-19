# 5. Federate Identity and Pin a Signed Supply Chain

CI that deploys with a JSON key, or a cluster that runs `:latest`, will fail the reliability program before the first SLO exists. The production question is:

> How does **CI (Continuous Integration)** authenticate without long-lived keys, and how does identity of an image become a digest plus a signature — without CI deploying the cluster?

Setup topics **07–08** (**Lived**), ADR 002, Terraform `wif` / `artifact-registry` / `binary-authorization`, `.github/workflows/build-scan-sign.yml`, and `docs/security/supply-chain.md` implement that loop. **GitOps (Git-based operations)** still promotes. CI proposes.

## 1. An unsafe starting state: SA keys and floating tags

GitHub Actions needs GCP access for Artifact Registry push. Downloading a service account JSON into GitHub Secrets is a standing credential: leak equals project-scoped compromise, rotation is toil, audit is weak. Deploying `image: frontend:latest` makes rollback and Binary Authorization meaningless — identity is not pinned.

Architecture deployment flow already refused that path: WIF auth, Trivy, push digest, cosign sign, CI opens PR on `values-images.yaml`, human merge, operator manual sync, Binary Authorization, Kyverno. Skipping any of those reopens the unsafe state.

## 2. The production model: short-lived federation, digest promotion, admit-time verify

> *Theory — Federated CI and digest identity*
>
> This model enables CI to produce scanned, signed evidence and propose Git changes, while GKE admits only attested digests — without Actions becoming the deploy authority.

### WIF over keys (ADR 002)

ADR 002: use **WIF (Workload Identity Federation)** with GitHub **OIDC (OpenID Connect)**. Prohibit long-lived GCP service account JSON keys in GitHub Secrets.

`terraform/modules/wif/main.tf` creates CI service account, workload identity pool, and provider with issuer `https://token.actions.githubusercontent.com`. Attribute mapping includes `repository` and `ref`. Condition binds to `github_org/github_repo` (and optionally a ref). Tokens are short-lived and auditable.

Topic 07 workflows use `google-github-actions/auth@v2` with `id-token: write`. No key download steps appear in `docs/security/supply-chain.md` by design.

### Artifact Registry plus Binary Authorization

Topic 08: regional Docker repository `europe-west1-docker.pkg.dev/boutique-gke/boutique`. Binary Authorization attestor trusts cosign signatures from CI. Unsigned images are rejected at deploy time once enforce mode is on.

Supply-chain.md pipeline:

```text
CI (WIF) → Trivy → AR → cosign → PR digest → Argo sync
  → Binary Authorization → Kyverno → NetworkPolicy → workload
```

**AR (Artifact Registry)** is image storage. **BA (Binary Authorization)** is admit-time policy. Kyverno `require-digest` is a second gate against `:latest`. They are complementary, not duplicates.

### CI never deploys

`.github/workflows/build-scan-sign.yml` mirrors upstream Online Boutique `v0.10.5` (and `redis:7.2-alpine` for `redis-cart`), scans, pushes, signs. On success, `manifest-digest-pr` updates `gitops/apps/boutique/values-images.yaml`. A human merges. An operator syncs Argo CD (ADR 003). That is series principle: CI never deploys the cluster.

**Best Practice:** Fail Trivy on critical/high for images you control.

**Production Practice:** Upstream mirrors needed `.github/trivy/upstream-mirror.trivyignore` as documented accepted risk. That is a decision record, not a silent disable. Regenerating ignore without review is a supply-chain failure.

## 3. How this repository implements it

> **Practice — Trace WIF from Terraform to the workflow**
>
> Open `docs/setup/07-github-wif.md`, `terraform/modules/wif/main.tf`, and the auth step in `build-scan-sign.yml`.

Workflow header (abridged):

```yaml
name: build-scan-sign
on:
  workflow_dispatch:
    inputs:
      upstream_version:
        default: "v0.10.5"
      redis_tag:
        default: "7.2-alpine"
permissions:
  contents: read
  id-token: write
```

Matrix covers the ten Boutique services plus `redis-cart`. Secrets required: `GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_SERVICE_ACCOUNT`, `COSIGN_PRIVATE_KEY`, `COSIGN_PASSWORD`. Keys for GCP are not among them.

> **Practice — Read digest pins, not tags**
>
> Open `gitops/apps/boutique/values-images.yaml`. Every image has `digest: sha256:...` against Artifact Registry.

Example:

```yaml
  frontend:
    repository: europe-west1-docker.pkg.dev/boutique-gke/boutique/frontend
    digest: sha256:50ca57c513de1ef22a97b6ef76989a73878d4a3873f85b5314bfc207853d5475
  redis-cart:
    repository: europe-west1-docker.pkg.dev/boutique-gke/boutique/redis-cart
    digest: sha256:18e7e254e2fe1fa185f9434450649b33c1efb9a7dcda9daaf1ce0dfb133bc16b
```

The `redis-cart` digest later appears in the 2026-07-04 postmortem: the image in AR lacked a trusted attestation when BA was already in enforce. Supply chain and SRE meet in restore, not only in happy-path CI.

Root module (`terraform/environments/boutique/main.tf`): `module.wif`, `module.artifact_registry` (CI writer + node reader IAM), `module.binary_authorization` counted on when `cosign_public_key_pem != ""`. Enforcement mode variable is applied in topic 16 / edge-hardening — not on first AR create.

WIF provider attribute mapping (from `terraform/modules/wif/main.tf`):

```hcl
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
  }
```

Condition binds `attribute.repository == "org/repo"` and optionally `attribute.ref`. That is the blast-radius control ADR 002 paid setup cost for.

`docs/security/supply-chain.md` also covers ESO, Kyverno minimum policies, and NetworkPolicy. Those are Chapter 6. This chapter stops at identity and image trust so the gate has something to enforce.

## 4. Test the design under failure

### Independent control failure — JSON key “just for the workshop”

> **Practice — Refuse the key fallback**
>
> A stuck WIF attribute condition tempts `gcloud iam service-accounts keys create` into GitHub Secrets.

**Severity:** high; standing credential equals project blast radius.  
**Plausible harm:** leaked key pushes unsigned images or reads Secret Manager; rotation forgotten.  
**Potential blast radius:** entire `boutique-gke` IAM surface the SA holds.  
**Bounded by:** ADR 002; topic 07 attribute conditions; gitleaks pre-commit.  
**Primary principles:** Identity is digest, not tag; CI never deploys; Git is the deploy authority.

#### Diagnosis

WIF setup is more YAML than a key file. That cost is the mitigation. Architecture failure scenario “WIF/CI failure → no image promotion” is accepted: fix the pool, do not fall back to keys.

#### Correction

Repair `attribute.repository` / ref conditions. Keep `id-token: write`. Promote via digest PR. If BA blocks a restore, that is Chapter 11/14 — not a reason to turn off signatures.

That correction changes later decisions:

- Chapter 7’s `digest-only.sh` test assumes this pin file.
- Chapter 11’s enforce mode assumes attestations exist for Boutique images.
- Chapter 14’s Redis restore failed when attestation did not exist for `redis-cart`.

## 5. Production reality

### Common errors

#### `id-token: write` missing on the job

WIF cannot mint a token. The failure looks like GCP auth. The fix is workflow permissions, not a JSON key.

#### Attribute condition too wide (`repository` only, any ref)

ADR 002’s point is scoped trust. Binding every branch to the prod CI SA lets a fork of `main` push to Artifact Registry. Prefer `attribute.ref` when the module variable allows it.

#### Tag immutability as a substitute for digest pins

Artifact Registry tag immutability is optional in topic 08. Helm values must still use `digest: sha256:`. Kyverno and `digest-only.sh` do not care that a tag cannot move if you never pin the digest.

#### Silent `trivyignore` growth

`.github/trivy/README.md` is the review policy. Expanding ignores during a checkout burn (Chapter 13 freeze band) is a reliability decision, not a CI convenience.

## 6. What changed

| Before | After |
| --- | --- |
| SA JSON in GitHub Secrets. | WIF pool/provider + `google-github-actions/auth@v2`. |
| `:latest` / floating tags. | `values-images.yaml` digest pins from CI PRs. |
| Unsigned images. | cosign sign/attest; BA prepared in Terraform. |
| CI Helm-installed Boutique. | CI never deploys; Argo waits for a human. |

## 7. What You Learned

Topics 07–08 federate GitHub to GCP without JSON keys, store immutable images in Artifact Registry, sign with cosign, and prepare Binary Authorization. CI opens digest PRs. It does not sync Argo CD. `:latest` is a failure of identity.

### Durable outputs

| Artifact | Location | Keep it because |
| --- | --- | --- |
| ADR 002 | `docs/adr/002-wif-over-sa-keys.md` | WIF decision |
| Setup 07–08 | `docs/setup/07-github-wif.md`, `08-artifact-registry-binary-auth.md` | Lived WIF and AR/BA |
| Modules | `terraform/modules/wif`, `artifact-registry`, `binary-authorization` | IaC |
| Pipeline | `.github/workflows/build-scan-sign.yml` | Mirror, scan, sign |
| Policy prose | `docs/security/supply-chain.md` | End-to-end trust loop |

> **Independent Practice — Decide what happens when Trivy fails on upstream Redis**
>
> The lived workflow used `upstream-mirror.trivyignore`.

1. Is accepting a CVE in `redis-cart` an SRE decision, a security decision, or both?
2. What freeze-band in Chapter 13 would forbid expanding that ignore file during a checkout burn?
3. What evidence would justify rebuilding Redis from a different base instead of ignoring?
4. How does an ignore file interact with BA (does BA see CVEs)?

Do not treat a green Actions badge as proof that checkout is reliable.

## Further reading

Playbook article **G2** is the short public argument for Workload Identity Federation instead of SA JSON keys.

https://github.com/btilki/devops-engineering-playbook/blob/main/articles/G2.md
