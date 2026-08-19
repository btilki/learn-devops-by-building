# Practical DevOps Engineering — Release Manifest

## Release identity

| Field | Value |
|---|---|
| Version | `v1.0` |
| Release date | 2026-08-15 |
| Status | Frozen manuscript and verified companion-lab snapshot |
| Manuscript path | `books/practical-engineering/devops/` |
| Companion lab | `books/practical-engineering/labs/devops/northwind/` |
| Companion-lab completed snapshot | `v1.1-chapter-13-complete` → `4c6dc1ff486d101c12e6dbee1480a49ec9eca485` |
| Manuscript identity | **SHA-256 (Secure Hash Algorithm 256-bit)** file inventory below |

The manuscript directory is not represented by the companion lab's Git commit. Its frozen identity is the set of file checksums recorded in this manifest.

## Release scope

This release covers one production delivery path for the Northwind environment: source feedback, verifiable artifacts, infrastructure reconciliation, Kubernetes runtime, workload identity, observability, progressive delivery, data compatibility, asynchronous processing, GitOps, workload cost and capacity, failed-change response, and reconstruction from durable evidence.

It does not claim to implement a full DevSecOps governance program, shared platform product, fleet lifecycle, regional-loss architecture, or **SRE (Site Reliability Engineering)** reliability program.

## Manuscript inventory

| File | SHA-256 |
|---|---|
| `00-how-to-use-this-book.md` | `aead12b3eaa70cae836db059c6e9227ef6695b57ed9a01d21c4e0f2d210e117f` |
| `01-build-fast-feedback.md` | `9305a2f17fc5edf069defcf4115c67508b9313f2b1f2966fb1f49552103ce6b4` |
| `02-build-once-promote-verifiable-artifact.md` | `c50433b35d0a519b51f5a780bd94b998a8c8c9b965678d1a4affd510659c3dc5` |
| `03-reconcile-infrastructure-through-reviewed-changes.md` | `2f964f38161d1931d640946251b3173c232b2763db54221e779eedd4742a7ca3` |
| `04-establish-production-kubernetes-runtime.md` | `b2809963f22736d8dbd3362d9adfba1c5cfae7cff40f5ced63a7e6589bc55d9a` |
| `05-replace-static-secrets-with-workload-identity.md` | `505b3e6511be7436cb6b622c75ea870e56987c8f0b5457b13a2b107d722c40c3` |
| `06-make-production-behavior-explainable.md` | `6162a71d4fb23f992b25b4c5b0c02792fd3a4c17f98d75fa6b9f4719599a5f74` |
| `07-release-progressively-and-abort-safely.md` | `54382fc51f830b71009d539e76ceb222f72acc3c396742428d972fbc8f2f3fa8` |
| `08-change-data-without-breaking-compatibility.md` | `d8d3d059d8fdbfbb539df9bbe72d31fa45d50c25c27b775b8a79b2d7278610de` |
| `09-operate-asynchronous-work-safely.md` | `79595f14a8dd45837526a4722de56d1a9a12cb7b81e2d6f6763f100669681032` |
| `10-reconcile-environments-with-gitops.md` | `84fa6950caf790949f8653589f0c44982879be5eaeece3e2563d85f3853544c3` |
| `11-control-delivery-cost-and-capacity.md` | `5bf272132a99741f6602ef9777d1891c36400ccf7802eadf1f119b31601ef14e` |
| `12-recover-a-failed-production-change.md` | `5e9c1e52c729b607d55cb99494ee24ef9f974772527fcf906d50eee3d263881c` |
| `13-restore-production-from-durable-evidence.md` | `000bd3ff086498abe5d6228e289845f9f46eed5bb9387ba6249c3646d2c9b4fd` |
| `14-conclusion.md` | `7d4ca10d7003a832e53bb2503f49e3a74f57319a83199f951ef33b948eee6e70` |
| `GLOSSARY.md` | `3a57a0c70acdb9aeb15cd10715817054ad144393d33ca5c530ece93284b8f5bf` |
| `REFERENCES.md` | `afb375906ba78a5824bf9d1fda70ef11ea237befac4559e0999b1f0ec5622582` |
| `RELEASE-CHECKLIST.md` | `924a10f23cff2201bfa37ea2b05af5a7bebd389d64ee5f9239b33c72f5a8a9d7` |
| `BOOK-PLAN.md` | `c4f5c0e2a2ae32220a4ede7eaea273f0786a98b984543874e9f0783527199494` |

`RELEASE-MANIFEST.md` does not include its own checksum because changing that value would change the file being identified.

## Companion-lab tags

Tags are curated cumulative exercise snapshots, not merge milestones. The commit recorded for each tag is the dereferenced commit.

The reader-facing aliases `chapter-NN-start` and `chapter-NN-complete` point to the corresponding verified `v1.1-` commits below. The versioned tags remain the immutable release identity; the generic aliases may advance in a later release.

| Chapter | Start | Complete |
|---:|---|---|
| 1 | `4be2416003fbb2fc512dc9352f9695cb98c6bc79` | `c50248b47bcba54505c34b9b0f80d4820c4acfda` |
| 2 | `1947ce973d0e610ffcc5c98c1e2acfa3f31a0ede` | `6bacf65d819fc8ba36db709ec0e8cddded13b021` |
| 3 | `88c5ca5f8e75adcecdb7a412a492534c09af7b2b` | `92d1ac0fabbe61136d6f1409b83b1835d38c8824` |
| 4 | `cb5a13d9390fb58b6398a787767980e6b40d177e` | `ccef15b196d9457c00f6da2de6a189373e229daa` |
| 5 | `58c97a611a7f256ee59d9eea56c56545c6c9dbc0` | `1ce0f965b6ea109d4e8d53c8c4a8e68a382f36b5` |
| 6 | `4cdda97445fd3c3fc8525b77b8efe33088d498ae` | `fde818dc3db82893bfed215845e436b85f1bd45e` |
| 7 | `a9c51827db79d2aa9c98891d68989c233f224231` | `a5aafc1846efc69a6cab11860db81cd0c09e1b8c` |
| 8 | `374b7851212625665be0ef79d43349e1f6f5ceae` | `fddc28ce9229fbdbcc2ab692be62026b7b4268c5` |
| 9 | `47fcd9a11210560bd28568e4045f6e1bdd3c2f21` | `a6f8990dca03105a7c6d0580674ebee06ac8e555` |
| 10 | `4a3a1e95be34804b2b233d6af46c827cb0807e1e` | `cc6be4c5bfed68edbc2cef52b6612c54c804221d` |
| 11 | `59f6d6261cccc2cb526f7e0ad67a1bc7a31eac77` | `9a91750f073cad69e0bb0a72237117f76f162349` |
| 12 | `60e2d985718417274436452a063a9fbe81410122` | `a0dde16e25c9609d72b2516658ae6728a34cb96e` |
| 13 | `7cb23fe810a2ec5983a904280b8436f6b559f44b` | `4c6dc1ff486d101c12e6dbee1480a49ec9eca485` |

## Verification environment

| Tool | Version |
|---|---|
| Python, clean-worktree matrix runner and tests | 3.13.7 |
| pytest | 8.3.4 |
| Ruff | 0.8.4 |
| Git | 2.55.0 |

Python 3.13.7 executed the full start/complete/failure worktree matrix using the pinned test tools declared by the companion lab.

## Executable gate results

| Gate | Result |
|---|---|
| Red baselines | 13/13 passed from clean start-tag worktrees |
| Green completion checkpoints | 13/13 passed from clean complete-tag worktrees |
| Dedicated failure targets | 12/12 passed; Chapter 1 uses its guided queue-regression checkpoint rather than a separate `break` target |
| Chapter 2 generated evidence prerequisite | Passed before checkpoint and tamper exercise |
| Chapter 3 reset/import/plan/apply prerequisite | Passed before completed checkpoint and drift exercise |
| Workflow-template conformance and drift rejection | Passed |
| Certificate provisioning, renewal, and expiry rejection | Passed |
| Application-configuration validation and reviewed promotion/revert | Passed |
| Legacy dual-run exit gating | Passed |
| GitOps synchronization-storm game day | Passed |
| Explicit unit-cost assumption evaluation | Passed |
| Python 3.13 test suite | 5/5 passed |
| Python 3.13 Ruff | Passed |
| `git diff --check` | Passed |
| Companion-lab working tree | Clean |

## Editorial gate results

- All 13 core chapters have exactly one Theory box.
- Every core chapter has guided Practice boxes and one Independent Practice.
- All 13 core chapters contain `What You Learned`, `Prove It`, and `Next`.
- Every dedicated failure includes severity, potential blast radius, bounding controls, and `Primary principles`.
- Chapter-to-chapter `Next` promises match the next opening state after the Chapter 4/5 continuity correction.
- First-use abbreviation formatting was audited across chapters and back matter.
- The manuscript contains approximately 33,771 words including the reader guide, conclusion, glossary, references, release checklist, and book plan.

## Reference validation

- Validation window: 2026-08-14 through 2026-08-15
- Consolidated external references checked: 38
- Successful **HTTP (Hypertext Transfer Protocol)** responses: 38
- Failed or redirected-to-error responses: 0
- Fictional Northwind source, workflow, and build-type identifiers were excluded because they are fixture evidence rather than external references.
- The fast-moving Terraform S3-locking and AWS Certificate Manager lifecycle claims were rechecked against their primary vendor documentation immediately before publication.

## Known limitations

- The lab uses deterministic local evaluators for several production control systems. It does not run a real cloud account, registry, Kubernetes cluster, identity provider, GitOps controller, billing export, incident channel, PostgreSQL data directory, **WAL (Write-Ahead Log)** archive, or external payment system.
- Chapters 2 and 3 intentionally generate ignored evidence and simulated infrastructure state before their completed checkpoints.
- The snapshot tags are not promised to form linear Git ancestry. Their contract is documented in `00-how-to-use-this-book.md`.
- The v1.1 snapshot set contains 26 annotated tags. Tags are curated independently and are not required to share linear ancestry.
- Thresholds, resource values, rollout cohorts, recovery objectives, and capacity ceilings are Northwind teaching values and require workload-specific validation.
- Source links were reachable at release time but remain externally maintained and may change.

## Companion-book boundaries

- DevSecOps: supply-chain policy, vulnerability management, secret governance, detection, and compromise response.
- Platform Engineering: paved-road products, tenancy, shared control planes, fleet lifecycle, and platform ownership.
- SRE: portfolio service-level objectives, error-budget governance, on-call systems, regional-loss design, recurring game days, and reliability learning.

## Freeze decision

All required editorial and executable release gates passed on 2026-08-15. This manifest freezes the Practical DevOps Engineering manuscript as published edition `v1.0`. Companion-lab snapshot tags remain the historical `v1.1-` set.

Any post-freeze change to a manuscript file, companion-lab tag, verifier, fixture, or cited version-sensitive claim requires a new manifest and version.
