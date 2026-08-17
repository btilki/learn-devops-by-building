# Enforce a Verifiable Build and Release Chain

Chapter 6 established which source and dependency inputs Northwind may trust. That decision can still be lost inside the build. A signed artifact may come from an unauthorized builder, use different inputs, omit required evidence, or target an environment its approval never covered.

## 1. A valid signature on an untrusted build

The compromised maintainer obtains build-token authority and submits an artifact produced by `compromised-builder-v2`. Its signature is cryptographically valid. Its provenance also says the builder was neither isolated nor hermetic.

Work from the lab working tree using the How to Use This Book procedure. From the DevSecOps lab root, run:

```bash
make chapter-07-baseline
```

The permissive start policy trusts the compromised builder and asks only whether the signature is valid. The baseline therefore exposes the weakness without pretending a successful denial already exists:

```text
chapter 07 baseline: signature-only policy admitted an untrusted non-isolated builder
```

## 2. The production model: attestations make claims; policy grants trust

> *Theory — Provenance, roots of trust, and admission*
>
> This model enables Northwind to decide whether one artifact may cross one release boundary.

An attestation is a signed statement about a subject. Provenance describes how an artifact was produced. A signature can establish that a particular key signed those claims and that they have not changed. It cannot establish that the signer, builder, inputs, parameters, or target are authorized. The [**SLSA (Supply-chain Levels for Software Artifacts)** build requirements](https://slsa.dev/spec/v1.2/build-requirements) distinguish merely existing provenance from authentic provenance and from an isolated build platform. Apply that distinction here: a valid signature can authenticate claims without proving the builder was isolated or authorized.

| Claim | Admission question | Failure hidden by signature-only checks |
|---|---|---|
| Source revision | Does it equal the admitted Chapter 6 revision? | The builder used different source |
| Dependency decision | Does it bind the admitted resolution? | Resolution changed after review |
| Builder identity | Is this builder currently trusted? | A valid key was used by an unauthorized builder |
| Isolation and hermeticity | Could undeclared state influence the result? | Host or network inputs entered the build |
| Build parameters | Were only reviewed release parameters used? | Debug or unsafe options changed the artifact |
| Artifact digest | Which immutable output is being admitted? | Evidence refers to a different image |
| **SBOM (Software Bill of Materials)** and transparency | Are required evidence and a durable record present? | Claims disappear or dependencies cannot be inspected |
| Release approval and target | Who authorized this digest for this environment? | Staging approval is replayed for production |

The root of trust is the set of identities, keys, policy sources, and verification mechanisms whose correctness the decision depends on. Adding signatures expands the evidence graph; it does not eliminate roots. Trust rotation is therefore an operational capability: Northwind must be able to revoke a builder or key, replace it, rebuild, and prove old authority no longer admits releases.

Hermeticity means declared inputs determine the build without undeclared network or host dependencies. Isolation bounds interference between builds and limits what a compromised build can affect. These properties overlap, but neither implies the other.

## 3. Enforce the complete release chain

> **Practice — Bound builders and build parameters**
>
> Declare trusted builders, signing keys, isolation, hermeticity, and allowed release parameters.

Open `supply-chain/build-policy.yaml`. `northwind-builder-v3` is the trusted builder. Both the older and current signing keys are initially recognizable so Chapter 7 can distinguish a cryptographically valid signature from an authorized builder. The pre-rotation artifact uses `release-key-v2`; containment revokes that key, and recovery must produce a different digest with `release-key-v3`.

> **Practice — Bind provenance to the admitted inputs**
>
> Require provenance to name the Chapter 6 source revision and dependency-resolution decision.

Open `supply-chain/provenance.yaml`. Its source claim binds revision `8a19e60`, while its dependency claim binds the content-addressed Chapter 6 resolution decision. A dependency graph change therefore invalidates the binding even if someone reuses the same source revision. The artifact has an immutable digest, and the attestation names builder identity, build properties, parameters, signing key, SBOM digest, and transparency entry.

The verifier compares these observations with independent policies and Chapter 6 evidence. It does not accept a builder's statement that the builder itself is trusted. This follows the verification shape described by the [SLSA artifact verification guidance](https://slsa.dev/spec/v1.2/verifying-artifacts): validate the subject and digest, then evaluate provenance fields against trusted expectations.

> **Practice — Admit one digest to one environment**
>
> Evaluate independent release approval, evidence requirements, policy version, and target environment before deployment.

Open `supply-chain/admission-policy.yaml` and `supply-chain/deployment-evidence.yaml`, then run:

```bash
make audit
make chapter-07-checkpoint
```

The audit validates the governed artifacts. The checkpoint admits the chain only when source, dependencies, builder, parameters, signature, key, evidence, approval, artifact, and target agree. This lab uses fixture attestations; production must verify signatures, repository decisions, transparency inclusion, builder isolation, and deployed digests against their authoritative systems.

## 4. Test the design under failure

### Cumulative attack — Present a signed artifact from an untrusted builder

> **Practice — Reject cryptographic validity without policy trust**
>
> Evaluate a correctly signed artifact produced after build-token misuse by a non-isolated, non-hermetic builder.

**Severity:** critical; the artifact seeks production release authority.  
**Plausible harm:** malicious production code, falsified order effects, credential exposure, or persistence through a trusted-looking release.  
**Potential blast radius:** production workloads and business effects reached by the artifact.  
**Bounded by:** admitted inputs, trusted builder identity, isolation, hermeticity, parameter policy, release approval, transparency, and digest-bound deployment.  
**Primary principles:** blast-radius control, explicit contracts, trustworthy evidence, reconciliation, and recovery.

#### Security questions

- **Asset and harm:** Release authority, payment authority, and correct order outcomes drive admission.
- **Trust and authority:** A valid signature authenticates a claim; only policy authorizes the builder, key, artifact, and production target.
- **Detection after prevention fails:** The admission decision retains builder, signing key, source revision, artifact digest, target, policy version, result, and individual denial reasons.
- **Evidence of restored trust:** Not yet applicable. Chapter-local recovery: compromised signing trust is revoked, a trusted builder produces a new digest with the rotated key, and deployment evidence names that exact digest and policy.

#### Diagnosis

Run `make chapter-07-attack`. The artifact is denied because its builder is untrusted, non-isolated, and non-hermetic even though its signature is valid. The command writes `build/chapter-07-attack-decision.json`.

#### Containment

Run `make chapter-07-contain`. It derives the compromised builder and signing key from the denial decision, then writes them to `build/chapter-07-revocations.json`. Every ordinary admission evaluation automatically consumes active revocations; callers cannot accidentally admit an old key by omitting an optional argument. Rejection stops this deployment, but responders must still locate earlier artifacts produced with that authority.

#### Recovery

Run `make chapter-07-recover`. Recovery requires the revocation record and first proves that the legitimate pre-rotation artifact signed by `release-key-v2` is no longer admissible. It then evaluates a rebuilt artifact with a new digest from `northwind-builder-v3` using `release-key-v3`. Finally, it reconciles the digest, environment, admission result, and policy version with production deployment evidence and writes a distinct recovery decision.

Service availability alone would not prove recovery. The deployed digest, source and dependency decisions, builder identity, rotated key, policy version, and production target must form one consistent chain.

## 5. Production reality

**Best Practice:** admit an artifact only by verifying the semantics of its complete evidence chain against independently governed trust policy.

**Production Practice:** isolate ephemeral builders, minimize network access, protect signing operations from build steps, retain transparency records, version admission policy, and reconcile the deployed digest after admission. Test key rotation, builder revocation, verifier outage, log unavailability, and rollback. Decide explicitly which failures deny production admission and which require a bounded emergency process.

Higher provenance levels can improve consistency, but labels do not replace examination of the claims Northwind needs. A sophisticated attestation that omits target approval or binds the wrong dependency resolution remains insufficient.

## 6. What changed

| Before | After |
|---|---|
| A valid signature was treated as sufficient trust. | **Signature validity and policy authorization are separate checks.** |
| Builder identity was descriptive metadata. | **Only current, bounded builder identities may produce releasable artifacts.** |
| Provenance could describe inputs without binding admission. | **Source and dependency decisions must match the artifact chain.** |
| Release approval was detached from an environment. | **Approval binds one digest to one target under one policy version.** |
| Deployment success implied recovery. | **Revocation, rebuild, rotation, and deployed-digest reconciliation prove restored trust.** |

## Durable outputs

| Artifact | Location | Keep it because |
|---|---|---|
| Release trust policy | `supply-chain/build-policy.yaml` and `supply-chain/admission-policy.yaml` | It preserves builders, keys, build properties, approval, evidence, and allowed targets. |
| Admission evidence record | `supply-chain/provenance.yaml`, `supply-chain/deployment-evidence.yaml`, and generated `build/chapter-07-*.json` | Reviewed fixtures define the trusted chain; gitignored generated decisions demonstrate denial, revocation, and recovery for the exercise run. |

## What You Learned

Signing proves integrity and signer possession, not authorization or truth. Trustworthy release admission verifies source, dependencies, builder, isolation, parameters, artifact, evidence, approval, and environment as one chain. Recovery removes compromised roots, rebuilds from admitted inputs, rotates affected trust, and reconciles the exact deployed digest.

### Prove It

> **Independent Practice — Rotate a trusted builder without stopping releases**
>
> Design an overlap window in which Northwind replaces a builder and signing key without letting the retired trust remain valid indefinitely.

Specify old and new identities, admissible overlap, transparency evidence, revocation trigger, rebuild scope, rollback constraints, deployed-digest verification, and the observation that closes the migration.

## Next

Northwind can now verify its source-to-production trust chain. Chapter 8 turns vulnerability findings about that chain and its runtime components into prioritized, owned treatment decisions.
