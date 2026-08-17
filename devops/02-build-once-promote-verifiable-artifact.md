# 02 — Build Once and Promote a Verifiable Artifact

> **Outcome:** Build one release candidate, bind evidence to its immutable digest, verify who built it from which source, and carry that same identity into promotion.

**Current Northwind state:** pull requests receive fast, bounded feedback. The release workflow still builds once for staging and again for production, publishes mutable names, and produces no verifiable supply-chain evidence.  
**Prerequisites:** Chapter 1's completed state, GitHub Actions familiarity, container-image fundamentals, and Python 3.12.  
**Implementation:** `books/labs/devops/northwind/`  
**Guided time:** approximately 105–135 minutes.

## 1. The source revision is the same; the artifact is not

Northwind approves `storefront-api` in staging, then the production job executes the container build again. Both jobs use the same Git revision, but they run at different times against external package repositories and different builder state.

During the last release review, staging recorded this image identity:

```text
ghcr.io/northwind-commerce/storefront-api@sha256:7f93...d22a
```

Production recorded:

```text
ghcr.io/northwind-commerce/storefront-api@sha256:b451...901e
```

The release ticket says that staging approved version `latest`. That proves only that the tag resolved to something at the time; it does not identify the bytes that were tested. Nobody can answer whether the digest changed because of a legitimate rebuild, an unpinned dependency, changed builder input, or interference after the build.

> How can Northwind prove that the artifact promoted later is exactly the artifact **CI (Continuous Integration)** built and evaluated?

> **Practice — Establish the untrusted release baseline**
>
> Check out the two-build release path and prove that artifact identity and supply-chain evidence are absent.

Start from the deliberately unsafe release path:

```bash
cd books/labs/devops/northwind
git switch -c my-chapter-02 chapter-02-start
python3.12 -m venv .venv
source .venv/bin/activate
make bootstrap
make chapter-02-baseline
```

The baseline command succeeds because red is expected, but its report must show why: two builds, a floating `latest` reference, no **SBOM (Software Bill of Materials)**, no provenance, no attestation, and no digest passed to promotion. This is an observation of the checked-out workflow—not a prearranged answer hidden in the checkpoint.

## 2. The production model: identity, evidence, and expectations

> *Theory — Artifact identity and chain of custody*
>
> Build the mental model needed to distinguish a source revision, build execution, artifact digest, tag, and trusted evidence.

A tag is a movable name. A digest is an identity derived from content. If one byte changes, the digest changes. Promotion should therefore carry an image reference of the form `name@sha256:digest`, even when human-friendly tags also exist.

Four identities are often incorrectly treated as one:

| Identity | What it identifies | What it does not prove |
|---|---|---|
| Source revision | A state in version control | Which dependencies or builder inputs produced the artifact |
| Build invocation | One execution of a build definition | That its output is the artifact later deployed |
| Artifact digest | Exact artifact content | Who built it or whether the source was approved |
| Tag | A registry reference that can move | Stable content identity |

The release contract must connect these identities. A reviewed revision enters an expected builder; that invocation produces a digest; authenticated provenance binds the digest to the build facts; policy decides whether those facts are acceptable; promotion carries that digest without another build.

Evidence has different jobs:

- An SBOM describes components associated with an artifact. It helps answer what is inside, but does not by itself prove who produced the artifact.
- **Provenance** binds an artifact subject and digest to build facts such as source, build type, and builder identity.
- An **attestation** is an authenticated statement about a subject. Its value depends on the issuer, signing mechanism, verification policy, and protection of the build system.
- **Expectations** state what Northwind accepts: the artifact name, source repository, revision, builder identity, build type, and evidence type. Validly formatted evidence is not sufficient if it describes an untrusted builder or the wrong source.

```text
reviewed source ──> trusted build ──> artifact digest
                         │                  │
                         └── provenance ────┘
                                  │
policy expectations ── verify ────┴──> promotable digest
```

The governing promotion invariant is short:

```text
build once → identify by digest → verify evidence → promote the same digest
```

## 3. Define what Northwind is willing to trust

> **Practice — Write independent trust expectations**
>
> Define the artifact, source, revision, builder, and build type Northwind will accept before inspecting generated evidence.

Create `release/expectations.json`:

```json
{
  "artifactName": "ghcr.io/northwind-commerce/storefront-api",
  "builderId": "https://github.com/northwind-commerce/storefront/.github/workflows/release.yml@refs/heads/main",
  "buildType": "https://northwind.example/build-types/storefront-container/v1",
  "sourceRepository": "https://github.com/northwind-commerce/storefront",
  "sourceRevision": "chapter-02-complete"
}
```

These are lab expectations, not universal values. In a real verifier, the expected revision comes from the approved release record, the builder identifier must match the identity emitted by the hosted builder, and repository renames or reusable-workflow boundaries require an intentional policy change.

The important ordering is that expectations exist before verification. Deriving the accepted builder or source from the attestation being checked would allow evidence to approve itself.

> **Production callout —** **AI (Artificial Intelligence)** drafts; humans verify
>
> Treat changes drafted with AI assistance as untrusted source input, not as review evidence. The same protected review, tests, workflow-conformance checks, dependency controls, build isolation, and artifact verification apply regardless of who or what produced the first draft.
>
> Generated Dockerfiles, workflow edits, manifests, and dependency updates can be plausible while changing authority, omitting a failure boundary, inventing a package version, or exposing build data. Keep the proposed diff narrow enough to inspect; do not place production secrets or restricted source into an unapproved model context; run the repository's executable checks; and require an accountable reviewer to explain the operational effect before merge. Record material generation constraints when organizational policy requires traceability.
>
> Provenance later proves which reviewed source and builder produced the artifact. It does not prove that generated source is correct, that a reviewer understood it, or that the model's suggestion was safe. Human approval is therefore not a substitute for verification either: people own the decision, while independent controls produce the evidence.

> **Practice — Build one digest-bound evidence set**
>
> Generate the deterministic candidate, manifest, SBOM, and provenance, then identify which claims each file contributes.

Build the local release candidate and its evidence:

```bash
make chapter-02-evidence
```

The command creates a deterministic teaching artifact at `dist/storefront-api.tar` and writes three evidence files under `evidence/chapter-02/`:

- `manifest.json` carries the immutable artifact reference;
- `sbom.spdx.json` records direct Python dependencies in **SPDX (Software Package Data Exchange)** 2.3 form;
- `provenance.json` binds the digest to the expected source, revision, builder, and build type.

The two direct application dependencies in `requirements.txt` use exact versions, so their declared versions become controlled build inputs and appear in the teaching SBOM. Exact direct pins are not a complete dependency lock: production should resolve and review transitive dependencies, retain the lock artifact, and use hashes or an equivalent integrity mechanism supported by the package workflow. Rebuilding later still remains a separate act from promoting the artifact already evaluated.

### Verify the claim, not merely the document

The [**SLSA (Supply-chain Levels for Software Artifacts)** build requirements](https://slsa.dev/spec/v1.2/build-requirements) distinguish merely existing provenance from authentic provenance and from a hardened build platform. Apply that distinction to the files you just created. A verifier must answer:

1. Does the subject name and digest match the candidate artifact?
2. Is the statement type understood, and are required fields present?
3. Is the attestation authentic under a trusted issuer or key?
4. Is the builder one Northwind permits?
5. Do source, revision, build type, and external parameters match the approved release?
6. Is the signing identity still acceptable under current policy?

The local verifier exercises subject, format, builder, source, revision, and build-type expectations. It cannot establish authenticity because its local evidence files are unsigned. That limitation is why the hosted workflow later creates an **OIDC (OpenID Connect)**-backed attestation.

> **Practice — Verify subject binding and policy**
>
> Compare the actual artifact digest with its manifest and provenance, then evaluate the evidence against Northwind's independent expectations.

Inspect the binding rather than just checking that files exist:

```bash
shasum -a 256 dist/storefront-api.tar
python -m json.tool evidence/chapter-02/manifest.json
python -m json.tool evidence/chapter-02/provenance.json
python tools/artifact_evidence.py verify
```

The same digest must appear in the calculated hash, manifest, and provenance subject. The verifier also compares the statement with `release/expectations.json`. This follows the verification shape described by the [SLSA artifact verification guidance](https://slsa.dev/spec/v1.2/verifying-artifacts): validate the subject and digest, then evaluate provenance fields against trusted expectations.

The local evidence generator is intentionally small enough to inspect. It teaches the contract and detects accidental mutation, but an attacker able to replace the artifact could also replace the unsigned evidence files. Authenticity comes from the hosted attestation path implemented next.

## 4. Build once in the guarded release workflow

Open `.github/workflows/release.yml`. The starting workflow publishes `latest`, then the `promote` job runs `docker/build-push-action` again.

Build once and reproducible builds solve different problems. Build once prevents promotion from changing the candidate. Reproducibility asks whether an independent build of the same declared inputs produces equivalent output and helps expose hidden inputs. It does not justify rebuilding for each environment: dependency availability, timestamps, builder state, or compromise can still change the result. Promotion carries the evaluated digest; reproducibility independently evaluates the build process.

> **Practice — Replace environmental rebuilds with one candidate**
>
> Give one guarded job publication authority, build once, and export its immutable digest for downstream promotion.

Now replace the two-build topology with one build job whose digest becomes an explicit job output:

```yaml
permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write
      attestations: write
    outputs:
      digest: ${{ steps.build.outputs.digest }}
```

The workflow default remains read-only. Only the build job receives package publication and attestation authority. `id-token: write` allows the job to request an OIDC identity token; it does not grant every workflow a long-lived signing key.

Configure the single image build:

```yaml
- name: Build and publish the release candidate once
  id: build
  uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/northwind-commerce/storefront-api:sha-${{ github.sha }}
    sbom: true
    provenance: mode=max
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

BuildKit attaches SBOM and provenance records to the pushed image. Docker documents the available forms and storage behavior in [Build attestations](https://docs.docker.com/build/metadata/attestations/). `mode=max` exposes more build metadata than the default minimal mode; review the resulting statement because build arguments, source locations, and other metadata can disclose information that should never have been passed as secrets.

The `sha-...` tag helps humans search the registry, but it is not the promoted identity. The build step's digest is.

## 5. Add authenticated evidence, then promote the digest

> **Practice — Attest and promote the build output**
>
> Bind hosted identity to the published digest and pass that same digest into a promotion job that cannot rebuild it.

Immediately after publication, attest the exact build output:

```yaml
- name: Attest the published digest
  uses: actions/attest@v4
  with:
    subject-name: ghcr.io/northwind-commerce/storefront-api
    subject-digest: ${{ steps.build.outputs.digest }}
    push-to-registry: true
```

The subject digest comes from the publishing step; it is not recalculated from a tag. GitHub's current [artifact attestation documentation](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations) describes the required `id-token`, `attestations`, and package permissions and the container-image subject fields.

Now remove all build and push actions from `promote`. Carry the previous job's output instead:

```yaml
promote:
  needs: build
  runs-on: ubuntu-latest
  environment: production
  permissions:
    contents: read
  steps:
    - name: Record the immutable production candidate
      env:
        CANDIDATE: ghcr.io/northwind-commerce/storefront-api@${{ needs.build.outputs.digest }}
      run: |
        echo "candidate=${CANDIDATE}" | tee -a "$GITHUB_STEP_SUMMARY"
```

The production environment can add approval and deployment protection rules without receiving build authority. In Chapter 3, this step will submit the verified digest to a reviewed deployment repository. For now it records the handoff and proves that promotion does not rebuild.

> **Practice — Verify the release chain of custody**
>
> Prove that the workflow builds once, produces evidence with scoped authority, and promotes the prior build's digest.

```bash
make chapter-02-checkpoint
```

Green means more than valid workflow syntax. The checkpoint verifies that the workflow builds once, avoids `latest`, requests scoped authority, enables SBOM and maximum provenance, attests the build output, and passes the prior digest into a non-building promotion job. It also rebuilds the local fixture and verifies every digest and policy expectation.

## 6. Break the artifact after evidence generation

**Severity:** blocked release; no production outage.  
**Potential blast radius:** one release candidate.  
**Bounded by:** verification before promotion and an immutable subject digest.  
**Primary principles:** explicit contracts, trustworthy evidence, and recovery.

> **Practice — Detect tampering and rebuild safely**
>
> Mutate the candidate after evidence generation, explain the failed checks, and recover with a new coherent artifact-and-evidence set.

Simulate registry-side mutation or a corrupted transfer by appending bytes after evidence has been generated:

```bash
make chapter-02-break
make chapter-02-verify-tamper
```

The second command succeeds only when verification rejects the candidate. Its report should show failures for the manifest digest, provenance subject digest, and promotable reference while the expected builder and source remain true. That distinction matters: the evidence has the right shape and claims the right producer, but it no longer describes the available bytes.

Do not repair this by updating the old provenance with the new digest. Evidence belongs to the build execution that produced its subject. Rebuild from the reviewed source and regenerate the evidence:

```bash
make chapter-02-checkpoint
```

Recovery requires a newly coherent artifact-and-evidence set and a green policy evaluation. A command completing or an image tag existing is not proof of recovery.

## 7. Production reality

**Best Practice:** build a release candidate once, refer to it by digest, generate SBOM and provenance during that build, and verify authenticated evidence against explicit expectations before promotion.

**Production Practice:** secure the system that issues the evidence. A perfect signature from an overprivileged or attacker-controlled workflow faithfully authenticates the wrong process.

### SLSA level is not a checkbox

Locally produced provenance demonstrates the structure associated with SLSA Build L1. Authentic provenance from a recognized hosted issuer can support Build L2 when the platform and verification satisfy the specification. Build L3 additionally requires a hardened build platform with isolation properties. Adding `provenance: mode=max` does not by itself make an arbitrary pipeline L3.

### Verification policy needs ownership

Define who may change trusted builders, source repositories, reusable release workflows, and admission policy. Protect workflow files with code-owner review and branch rules. Pin third-party actions according to organizational policy; tags improve maintainability, while immutable commit references reduce movement risk. Record any exception and its expiry.

### Multi-platform images have more than one digest

A multi-platform image index has its own digest and refers to platform-specific manifests with their own digests. Decide whether promotion and verification target the index, each platform manifest, or both. Do not compare unlike subjects and conclude that a valid release was altered.

### SBOM existence is not SBOM quality

The local fixture lists only direct Python requirements. A production SBOM should account for operating-system packages, language dependencies, generated or vendored components, and the final image filesystem. Completeness, vulnerability policy, exceptions, and remediation belong to the DevSecOps book; this chapter establishes evidence identity and delivery integration.

### Registry lifecycle can break recovery

Retain promoted digests and their attached attestations for at least the deployment and rollback horizon. Garbage collection based only on convenient tags can delete an artifact that production still references. Test retrieval and rollback, not just publication.

## 8. What changed

| Before | After |
|---|---|
| Staging and production rebuilt the same revision. | One build produces the candidate promoted between environments. |
| `latest` named whichever image it currently referenced. | The digest identifies the exact promoted content. |
| Evidence files were absent. | SBOM, provenance, and hosted attestation are bound to the build output. |
| Valid-looking metadata could define its own trust. | Independent expectations constrain source, revision, builder, build type, and subject. |
| Mutation could remain hidden behind a familiar name. | Digest verification blocks the changed candidate before promotion. |

Northwind did not merely add signing syntax. It created a chain of custody: reviewed source enters a constrained builder, the builder publishes one immutable subject, evidence describes that subject, policy verifies it, and promotion carries the same identity forward.

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Artifact trust expectations | `release/expectations.json` | They independently define the subject, source, revision, builder, and build type that verification may accept. |
| Digest-bound release evidence | `evidence/chapter-02/manifest.json`, `evidence/chapter-02/sbom.spdx.json`, and `evidence/chapter-02/provenance.json` | Together they identify the candidate, describe its declared contents, and bind it to build facts for verification and later diagnosis. |

## What You Learned

Source identity does not prove artifact identity. You can now build one candidate, identify it by digest, bind an SBOM and provenance to that subject, evaluate authenticated evidence against independent trust expectations, promote without rebuilding, detect post-build tampering, and recover by producing a new artifact and evidence set rather than rewriting history.

### Prove It

> **Independent Practice — Design a partner artifact contract**
>
> Define the acceptance and recovery policy for a multi-platform artifact built outside Northwind's trust boundary.

Northwind acquires a service built in a partner repository. The partner supplies a signed image, SBOM, and provenance, but uses a builder Northwind does not operate. Production runs both `linux/amd64` and `linux/arm64`, and the registry removes untagged manifests after 30 days.

Design the acceptance and promotion contract. Specify the trusted issuer and builder expectations, source and revision constraints, multi-platform subjects, vulnerability-policy ownership, exception path, registry retention rule, and evidence required before rollback. Explain which controls prevent a compromised partner workflow from approving itself and which risks remain even after cryptographic verification succeeds.

## Next

Northwind can now identify and verify the exact artifact entering promotion. It still creates runtime infrastructure through mutable console actions and cannot prove that declared state matches deployed state. Chapter 3 moves infrastructure changes into a reviewed reconciliation path and makes drift observable.
