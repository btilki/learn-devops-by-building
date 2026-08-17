# Practical Platform Engineering — Release Manifest

## Release identity

| Field | Value |
|---|---|
| Version | `v1.0` |
| Release date | 2026-08-16 |
| Status | Frozen manuscript and verified companion-lab snapshot |
| Manuscript path | `books/platform/` |
| Companion lab | `books/labs/platform/northwind/` |
| Companion-lab completed snapshot | `v1.0-chapter-14-complete` → `5b30e655039d75019f24a3a04fd34206572b1a9f` |
| Manuscript identity | **SHA-256 (Secure Hash Algorithm 256-bit)** file inventory below |
| Published Word file | `releases/practical-platform-engineering-v1.0.docx` |

This inventory identifies two artifacts. They are not interchangeable.

**Manuscript package** — `books/platform/` plus the published Word file. Identity is the SHA-256 inventory in this manifest.

**Companion-lab package** — `books/labs/platform/northwind/`. Identity is the Git tags and dereferenced commits below. Executable gates were verified from those tags, not from the manuscript files alone.

The manuscript directory is not represented by a companion-lab Git commit. A reader who receives only the manuscript cannot independently re-run the lab. A reader who receives only the lab cannot identify the frozen manuscript checksums.

## Release scope

This release covers one owned internal platform product for Northwind: users and jobs, capability intake, tenancy, catalog ownership, a paved road with a supported exit, self-service environments, infrastructure contracts, a shared control plane, guardrails, developer-experience measurement, quota, fleet lifecycle, support and change authority, and control-plane recovery that keeps tenant isolation.

It does not claim to reteach the DevOps delivery path or the DevSecOps security path. It does not own portfolio **SLO (Service Level Objective)** programs, error-budget governance, on-call system design, regional-loss architecture, recurring game days, or **SRE (Site Reliability Engineering)** reliability learning. It does not certify Northwind against a legal or industry framework.

## Manuscript inventory

| File | SHA-256 |
|---|---|
| `00-how-to-use-this-book.md` | `aa763cb7325eb8b820cfc0b51e23cfefe0670edc0edb50dd06e5640bb046c90d` |
| `01-define-the-platform-as-a-product.md` | `293a0c3b15ec0552122c5edce46023346f20e0274073e9618a3509f44bf35a8b` |
| `02-decide-which-capabilities-become-platform-products.md` | `e537639a2a834844d8e73f1950540d805f3446e4035627375372b15f3f004c52` |
| `03-model-tenants-teams-and-isolation-boundaries.md` | `b2dff207c443f17bccd1d27b1f9135b8d97bdba14fc69138bd96b6227487626c` |
| `04-publish-a-software-catalog-and-ownership-map.md` | `65f6df3b0106bddcf6d86112886fb478ee22c98f99b29f8d5d634c7040aa506d` |
| `05-build-a-paved-road-teams-can-leave.md` | `cbf230180dbffe78078a549bef9ed81afb092a4e719fc826c1e4688593b98a3e` |
| `06-offer-self-service-environments-without-sharing-blast-radius.md` | `fd46c626bf15379aba16ff38af438b954d7536c9774044f0bd47a45da67647e1` |
| `07-abstract-infrastructure-behind-reviewable-contracts.md` | `bcd6b72cd0fd930ee0157ade55df28b3f4b6d8a7a8d3c1675127be9fdea3ae8a` |
| `08-operate-a-shared-control-plane-as-a-product.md` | `e85508779839506ee96d98d1ac0b6f665c0614e4dbbb5cca08a40de1a522e68a` |
| `09-enforce-guardrails-without-a-golden-cage.md` | `5e63fac10d8ab9e0b4a971aae685e59207adb4aae349ae4e4f43f1303558fd3a` |
| `10-measure-developer-experience-without-vanity-metrics.md` | `d23dbcc7495e6d39993849d929c4c94017db75ecb2d7f98cdfb71af5fba0aed3` |
| `11-allocate-quota-cost-and-capacity-across-tenants.md` | `79fa71faa5e1b3e30f03289dbf2721d3ea691c6ce9ede44a5cc4b83840cc8fd3` |
| `12-run-fleet-lifecycle-onboard-upgrade-deprecate.md` | `f2b9624a486ec8eb2af97d6890eeaaa65732e2f5ed5a3317c6d7ebbb76865f49` |
| `13-support-escalate-and-change-the-platform-safely.md` | `59089b2259f7a5a26f248dbbe6547b2d672daa7df56bbcb1e57024f555977325` |
| `14-recover-a-control-plane-failure-without-taking-tenants-with-it.md` | `00f08d6f9272cb85aa830a2f6d87ff5ddc93e6d27ee23087fcdb03ac4104484c` |
| `15-conclusion.md` | `24d8d299254e129099e53f5e7678ddaeb010b923b530845fa06cf9671f129cd4` |
| `GLOSSARY.md` | `af4da431ec2cae0fbbd31bbc31dd716da1b6d500aed1fa14ca74ce1ebd84f72f` |
| `REFERENCES.md` | `b0dc03f6bbd1feeb9f77daac8dc66a3b0db5d1983f5bfb7a20038f424202e2d3` |
| `RELEASE-CHECKLIST.md` | `666828ad87c0052ed887a1acaaec0cea533275fb119fb23350302ffb587bc1d7` |
| `BOOK-PLAN.md` | `92b8f7572bc47c0fbb70d403a926f7977ebb3445a33a22d1bf0f92236844099a` |

`RELEASE-MANIFEST.md` does not include its own checksum because changing that value would change the file being identified.

## Companion-lab tags

Tags are curated cumulative exercise snapshots, not merge milestones. The commit recorded for each tag is the dereferenced commit.

The reader-facing aliases `chapter-NN-start` and `chapter-NN-complete` point to the corresponding verified `v1.0-` commits below. The versioned tags remain the immutable release identity; the generic aliases may advance in a later release.

| Chapter | Start | Complete |
|---:|---|---|
| 1 | `255ac1074700daa3e751774b93f43b1eb34b27d0` | `3cb5c253b68957dc09ef17142da047778149b94f` |
| 2 | `62b9e8ce340a69de437fe8f5b94e0365e191d7a4` | `afdee6e4e6c226b90a9ffda1fbb9d81f0da684b3` |
| 3 | `e13c85a22d59d9bfc47a88d89f58dca050ac00c7` | `597d8c58a5780b747bc890b374585505362225f7` |
| 4 | `5325317b3418908d82519c7481c024a75b8f5748` | `5d12cab3d36074f3e419179e365b98b5ced1009f` |
| 5 | `c398e0a851d7063c1dbb474db50c2f718eb1eaaf` | `bcfff8e4f18340d1f3994ae7b42966cacdf47dde` |
| 6 | `b63d504472f7aa812db728e8196be8b29eb930bd` | `e67b3ca617f0dc9dfc4b121e4670708855731b45` |
| 7 | `f836dfe0c0e6ad184993f3b358423719923ec3df` | `03b2746a9c1f755de31550dbe8a61d5360a5c212` |
| 8 | `52bc4fc479a61577b15625f3f2ee62c2bfc65e0e` | `d3397e32a3fffcad9cd1f4f49bca75b6814adf09` |
| 9 | `b36d5c5381518c5191887d1a29e18db89413d430` | `1cc24c56f33b30e74d1d8fced06005613bb85f3e` |
| 10 | `8d4237337ccd689ae670d369b626b7cfa26fd80c` | `b7faa2b89d789cc6809846d0c8f7d3501fab8f48` |
| 11 | `bb5b9923bb27fb8cc49d92a5d550ef7401732702` | `d63b64947b9d53ed027042a52b0b7ac5168331c4` |
| 12 | `e0c48f37d226aa2cb51ccb8078fd5f2899b58c20` | `be2040dc4cb65b89f66c114deb761165809386c5` |
| 13 | `f55e684d39a628964a06d93a33665cd43de8005a` | `c1c5d6eb025fb4de450488f677ab62a7858464a8` |
| 14 | `9920ea1674f5175a5d0bca63d3dde932bfee9d09` | `5b30e655039d75019f24a3a04fd34206572b1a9f` |

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
| Red baselines | 14/14 passed from clean start-tag snapshots |
| Green completion checkpoints | 14/14 passed from clean complete-tag snapshots |
| Dedicated failure targets | 11/11 passed from complete-tag snapshots; Chapters 1–3 use baseline and challenge rather than a separate failure target |
| Python 3.13 test suite | 87/87 passed |
| Python 3.13 Ruff | Passed |
| Inherited DevOps v1.1 interface checksums | Passed |
| Inherited DevSecOps v1.0 interface checksums | Passed |
| Governed artifact schema validation | Passed |
| Companion-lab working tree | Clean |

## Editorial gate results

- All 14 core chapters have exactly one Theory box.
- Every core chapter has guided Practice boxes and one Independent Practice.
- All 14 core chapters contain `What changed`, `What You Learned`, `Prove It`, `Durable outputs`, and `Next`.
- Every dedicated failure includes severity, plausible harm, potential blast radius, bounding controls, `Primary principles`, and the platform questions that materially apply.
- Every dedicated scenario is classified as a cumulative product failure, connected consequence, or independent control failure.
- First-use abbreviation formatting was applied in chapters that introduce new abbreviations, plus the glossary, references, checklist, and this manifest.
- The manuscript contains approximately 50,833 words including the reader guide, conclusion, glossary, references, release checklist, and book plan.

## Reference validation

- Validation window: 2026-08-16
- Consolidated external **HTTP (Hypertext Transfer Protocol)** product or standards URLs: 0
- This book's production decisions are Northwind's. Inherited delivery and security contracts come from *Practical DevOps Engineering* v1.0 and *Practical DevSecOps Engineering* v1.0 rather than from a portal-product manual or landing-zone guide.
- Fictional Northwind identifiers were excluded because they are fixture evidence rather than external references.

## Known limitations

- The lab uses deterministic local evaluators for product, tenancy, catalog, paved road, environments, contracts, control plane, guardrails, measurement, quota, fleet, support, and bounded restore. It does not run a real developer portal, identity provider, Kubernetes cluster, billing export, or ticketing system.
- **Evidence of restored isolation** and **Evidence of bounded platform-product recovery** are bounded by inventoried plane evidence, per-tenant continue or freeze, and stated limitations. Chapter 14 does not prove a live-cluster recovery test, regional loss, or a portfolio **RTO (Recovery Time Objective)**.
- The snapshot tags are not promised to form linear Git ancestry. Their contract is documented in `00-how-to-use-this-book.md`.
- The v1.0 snapshot set contains 56 annotated tags: start and complete for each of 14 chapters, plus reader-facing aliases. Tags are curated independently and are not required to share linear ancestry.
- Published format: `releases/practical-platform-engineering-v1.0.docx`. Rebuild with `python3 tools/docx/build_platform_docx.py`. A matching PDF was not produced in this inventory.
- Floors, ceilings, freeze windows, and review dates are Northwind teaching values and require tenant-specific validation.
- Source links, where later added, remain externally maintained and may change.

## Companion-book boundaries

- DevOps: delivery-path evidence, progressive release, data-change compatibility, **GitOps (Git-based operations)** operation, and reconstruction from durable operational evidence.
- DevSecOps: threat and risk, attributable identity, supply chain, secrets, policy, detection, containment, eradication, and bounded restored trust.
- SRE: portfolio service-level objectives, error-budget governance, on-call systems, regional-loss design, recurring game days, and reliability learning.

## Freeze decision

Editorial and executable release gates passed on 2026-08-16. This manifest freezes the Practical Platform Engineering manuscript as published edition `v1.0` and records the companion-lab `v1.0-` snapshot tags.

Any post-freeze change to a manuscript file, companion-lab tag, verifier, fixture, or published Word file requires a new manifest and version.
