# Practical DevSecOps Engineering — Release Manifest

## Release identity

| Field | Value |
|---|---|
| Version | `v1.0` |
| Release date | 2026-08-16 |
| Status | Frozen manuscript and verified companion-lab snapshot |
| Manuscript path | `books/devsecops/` |
| Companion lab | `books/labs/devsecops/northwind/` |
| Companion-lab completed snapshot | `v1.0-chapter-16-complete` → `0e5d786c2b652c79fe32249f92411d128cdaa872` |
| Manuscript identity | **SHA-256 (Secure Hash Algorithm 256-bit)** file inventory below |
| Published Word file | `releases/practical-devsecops-engineering-v1.0.docx` |

This inventory identifies two artifacts. They are not interchangeable.

**Manuscript package** — `books/devsecops/` plus the published Word file. Identity is the SHA-256 inventory in this manifest.

**Companion-lab package** — `books/labs/devsecops/northwind/`. Identity is the Git tags and dereferenced commits below. Executable gates were verified from those tags, not from the manuscript files alone.

The manuscript directory is not represented by a companion-lab Git commit. A reader who receives only the manuscript cannot independently re-run the lab. A reader who receives only the lab cannot identify the frozen manuscript checksums.

## Release scope

This release covers one production security path for the Northwind environment: assets and harms, threat paths, owned risk decisions, attributable identity, privileged delegation, source and dependency trust, verifiable build and release, contextual vulnerability treatment, secret lifecycle, data-use protection, policy enforcement, runtime confinement, detection, investigation and containment, eradication and bounded restored trust, and operational governance.

It does not claim to implement a shared platform product, fleet lifecycle, regional-loss architecture, or **SRE (Site Reliability Engineering)** reliability program. It does not certify Northwind against a legal or industry framework.

## Manuscript inventory

| File | SHA-256 |
|---|---|
| `00-how-to-use-this-book.md` | `9c35f39ab5af0ac30c08ba9b28910826e4e8e5b8a0b9d6eb0fdb6a97137694a4` |
| `01-define-what-security-must-protect.md` | `058dcd7cec2c9cc447f5b4bba3dca70bc4230718df67040c68ee0e0d3a8cd339` |
| `02-model-threats-across-trust-boundaries.md` | `39e66fbb4ac5f58aad55d6e3794c36151839b41c3bb3032397bec88f3b86bf7e` |
| `03-turn-risk-into-owned-control-decisions.md` | `52d7c5940d15d0d4fcb2857f35b71af7fb5d47627c875bcf867cdf38dfac78ba` |
| `04-make-human-and-automation-access-attributable.md` | `cf7433765fa6aa4fd207a30aee5bfe2c9b5e63096df15ee32da4f7e7b6b9ccd7` |
| `05-govern-delegation-and-privileged-operations.md` | `1d3ee8d0c2d7b5d475edb7ceebd73acc822314b4d2fa27cb3b86d975bb5fa814` |
| `06-establish-trust-in-source-and-dependencies.md` | `dd17180bf15d963e37090512f62c8f97703f6c9faa595f2a45d326eab1c285a1` |
| `07-enforce-a-verifiable-build-and-release-chain.md` | `ace84010ee03c3fd4d407098f46afec46979ea7f34837c75c3e5f85ed3c381e7` |
| `08-prioritize-vulnerabilities-by-exploitability-and-harm.md` | `9de82d331ce53a81a8cd3ecd4739c5bd76087eec38279a1fe2ec18e2ddf2c0b6` |
| `09-govern-secrets-through-their-complete-lifecycle.md` | `194b7eeac2af73bf4b8ef2fe1e7a0f6792a88c8bb8f3aacc5213e890ffb180c9` |
| `10-protect-data-according-to-its-use-and-sensitivity.md` | `5f5bb186eb8be6cf6f5b4e37111d0db7702b44f020622f307c69e43853f5c85d` |
| `11-enforce-security-policy-without-hiding-exceptions.md` | `b01cdddef0a1bcb4f7892f1d9d73330f17aec64eaa0346e7f246a3937df179dc` |
| `12-constrain-workloads-and-detect-runtime-abuse.md` | `b7a7e6150d88b8754cbb632bc7fd118a197dcba84b258a3aac201a2ecdcb88da` |
| `13-build-security-evidence-and-actionable-detections.md` | `1b258282ff511fb998c6c3fafc602f95f8cea9bde3dbb8782a43abed880ac6ad` |
| `14-investigate-and-contain-a-production-compromise.md` | `7cf5d5aec250f749e044bd8b7dc02de83d8a46ce3dbe681e4f86f7f05292dafe` |
| `15-eradicate-persistence-and-restore-trust.md` | `18678d3d16df752f7782777c5728c53f2fa9756dee7829c76a91d68f73f79965` |
| `16-turn-operational-evidence-into-sustainable-governance.md` | `d0cfd3e111531bbb934dcb7036b9009a2bfb62b681d679690d2fad8f7a4a14ec` |
| `17-a-defensible-production-security-system.md` | `82ae2f45d983bb799a61ea425be776b4a3e55afea0007816fc4b055c2b79da07` |
| `GLOSSARY.md` | `95d6255274c07c869e57cb7c14019af44a7411f8eff10172856b90d8d45f2b07` |
| `REFERENCES.md` | `e53ee9264561ca7af50038292079b9155ce511003e8504fbb3a0306f439e55ad` |
| `RELEASE-CHECKLIST.md` | `d753cb91cc3e48a9b1412d87b79354bed3a78f033ce07c4a7a115430829d9633` |
| `BOOK-PLAN.md` | `9810e388761256445a338a2ede620fe4c20140757560746928e326933fd92e86` |

`RELEASE-MANIFEST.md` does not include its own checksum because changing that value would change the file being identified.

## Companion-lab tags

Tags are curated cumulative exercise snapshots, not merge milestones. The commit recorded for each tag is the dereferenced commit.

The reader-facing aliases `chapter-NN-start` and `chapter-NN-complete` point to the corresponding verified `v1.0-` commits below. The versioned tags remain the immutable release identity; the generic aliases may advance in a later release.

| Chapter | Start | Complete |
|---:|---|---|
| 1 | `5ed9b59eb77bc24024a2a2bbe960ca21b9e1c9f9` | `91d63fddfdd6968ee1ad49220d392ee56f57de4b` |
| 2 | `af994ceb1fb21d17ad4b464c44f21f54c0cb4641` | `be17247efd2dd607a1b519c6899d46a73cddec02` |
| 3 | `eea3a2e883a29115c173a901cabd54d937af091b` | `3db7e39083c0038bdc0f1097dbd2d84ad6786269` |
| 4 | `9cc9aa0cf48a75519bf73cb8c8360942f1017f4b` | `fbe0d98a7cc43964dea9ea94d4ed8920ca591ca2` |
| 5 | `feac1e028baf211cb272c25d0b9168eb53e38dd3` | `c5184a1732cfabdbd97b8f3bdbe55f47d23ce7cf` |
| 6 | `2012de33548339167684b69801e502c58cc731f0` | `0313e333f0a94decaa227bf193ce7af6dfab17fe` |
| 7 | `e5ba20a440fb7905fd56b0193c476b5d137b42db` | `d5c1ee4c3001b51ad44b8992c5fcd6001526724d` |
| 8 | `c65f65bcd992402fede19a23ba49df5949377156` | `f2d65f53d04ad1f63a007e8c985b06a41f02c583` |
| 9 | `8869d67bc718d483b159d03a0aba27168db4f72c` | `5cfafd5f8e11fb2f43fbf97144eddd4aa1b943f6` |
| 10 | `3797de04cbfc9ca35c751efa6d39697dafc519f9` | `3992c4064bacd7f40b6bfd7baa6e896acfe19a75` |
| 11 | `5f255e9758011bdd186575afafe1c47c76dac775` | `7c8c7da7d2f575fff66d3621c8464414aab99d05` |
| 12 | `aabe305d6a24a58d4cf98a36c9c6fd6fabdebe80` | `83823e9e49823a2af1bc4d6c64767666ffb492b1` |
| 13 | `4453a5b5cf8e32f31d08072a630b92c5c9547164` | `d3b09fdafbc7f4cfdf54c6b7463a42bfd45361da` |
| 14 | `4955cf23b40cb928e41e02ed63ecc23903c5f55f` | `2665b53c4dab48a804a2f5a3912a99737e0e1720` |
| 15 | `96e8a42c3c31343b25f326e27ec80c78064aeaea` | `dd08f2f4231bec4c22037a225f71e6c16c5f185e` |
| 16 | `5b2020069ee5d2303de3a3c98894ecad5ed5e346` | `0e5d786c2b652c79fe32249f92411d128cdaa872` |

## Verification environment

| Tool | Version |
|---|---|
| Python, tests, lint, and audit | 3.13.7 |
| pytest | 9.1.1 |
| Ruff | 0.16.0 |
| PyYAML | 6.0.3 |
| jsonschema | 4.26.0 |
| Git | 2.55.0 |

Python 3.13.7 executed the start/complete/failure snapshot matrix and the working-tree test, lint, and audit suite using the pinned tools declared by the companion lab.

## Executable gate results

| Gate | Result |
|---|---|
| Red start checkpoints | 16/16 failed from clean start-tag snapshots |
| Red baselines | 15/16 passed from clean start-tag snapshots; Chapter 8 baseline compares completed decision order with severity order and is verified from complete tags |
| Green completion checkpoints | 16/16 passed from clean complete-tag snapshots |
| Dedicated failure targets | 13/13 passed from complete-tag snapshots; Chapters 1–3 use baseline rather than a separate attack target; Chapters 8 and 16 use challenge |
| Python 3.13 test suite | 119/119 passed |
| Python 3.13 Ruff | Passed |
| Inherited DevOps v1.1 interface checksums | Passed |
| Governed artifact schema validation | Passed |
| Companion-lab working tree | Clean |

## Editorial gate results

- All 16 core chapters have exactly one Theory box.
- Every core chapter has guided Practice boxes and one Independent Practice.
- All 16 core chapters contain `What changed`, `What You Learned`, `Prove It`, `Durable outputs`, and `Next`.
- Every dedicated failure includes severity, potential blast radius, bounding controls, `Primary principles`, and the security questions that materially apply.
- Every dedicated scenario is classified as a cumulative attack, connected consequence, or independent control failure.
- First-use abbreviation formatting was applied in chapters that introduce new abbreviations, plus the glossary, references, checklist, and this manifest.
- The manuscript contains approximately 36,668 words including the reader guide, conclusion, glossary, references, release checklist, and book plan.

## Reference validation

- Validation window: 2026-08-15
- Consolidated external references checked: 14
- Successful **HTTP (Hypertext Transfer Protocol)** 200 responses: 13
- Failed or non-200 responses: 1 — the Alex Birsan dependency-confusion disclosure on Medium returned 403 to the automated checker and remains the canonical cited source
- Fictional Northwind source, workflow, subject, and digest identifiers were excluded because they are fixture evidence rather than external references.
- The fast-moving **CVSS (Common Vulnerability Scoring System)** v4.0, **CISA (Cybersecurity and Infrastructure Security Agency)** **KEV (Known Exploited Vulnerabilities)**, **SLSA (Supply-chain Levels for Software Artifacts)** v1.2, and **NIST (National Institute of Standards and Technology)** SP 800-61r3 claims were rechecked against their primary documentation immediately before this inventory.

## Known limitations

- The lab uses deterministic local evaluators for identity, supply chain, secrets, data, policy, runtime, detection, response, recovery, and assurance. It does not run a real identity provider, registry, Kubernetes cluster, telemetry backend, secret broker, payment provider, or audit platform.
- Restored trust is bounded by inventoried roots, modeled descendants, collected evidence, and stated limitations. The lab does not prove that no unmodeled persistence exists.
- The incident arc in Chapters 12 through 15 exercises the payment path. Support-data remains in the threat, risk, and governance registers without detection, containment, eradication, or recovery evidence.
- Complete snapshots keep the Chapter 14 incident-ready operational registers. Attack, containment, and recovery reports are generated from a complete snapshot. Chapter 16 complete tracks only the assurance evidence files cited by the governance catalog and evidence map.
- The snapshot tags are not promised to form linear Git ancestry. Their contract is documented in `00-how-to-use-this-book.md`.
- The v1.0 snapshot set contains 64 annotated tags: start and complete for each of 16 chapters, plus reader-facing aliases. Tags are curated independently and are not required to share linear ancestry.
- Published format: `releases/practical-devsecops-engineering-v1.0.docx`. Rebuild with `python3 tools/docx/build_devsecops_docx.py`. A matching PDF was not produced in this inventory.
- Thresholds, exception windows, overlap periods, and detection intervals are Northwind teaching values and require workload-specific validation.
- Source links were checked at inventory time but remain externally maintained and may change.

## Companion-book boundaries

- DevOps: delivery-path evidence, progressive release, data-change compatibility, GitOps operation, and reconstruction from durable operational evidence.
- Platform Engineering: paved-road products, tenancy, shared control planes, fleet lifecycle, and platform ownership.
- SRE: portfolio service-level objectives, error-budget governance, on-call systems, regional-loss design, recurring game days, and reliability learning.

## Freeze decision

Editorial and executable release gates passed on 2026-08-16. This manifest freezes the Practical DevSecOps Engineering manuscript as published edition `v1.0` and records the companion-lab `v1.0-` snapshot tags.

Any post-freeze change to a manuscript file, companion-lab tag, verifier, fixture, or published Word file requires a new manifest and version.
