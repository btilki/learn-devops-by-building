# Practical SRE Engineering — Release Manifest

## Release identity

| Field | Value |
|---|---|
| Version | `v1.0` |
| Release date | 2026-08-17 |
| Status | Frozen manuscript and verified companion-lab snapshot |
| Manuscript path | `books/sre/` |
| Companion lab | `books/labs/sre/northwind/` |
| Companion-lab completed snapshot | `v1.0-chapter-14-complete` → `792fc3f4b4d405c80d609814677a44e8b132d751` |
| Manuscript identity | **SHA-256 (Secure Hash Algorithm 256-bit)** file inventory below |
| Published Word file | `releases/practical-sre-engineering-v1.0.docx` |

This inventory identifies two artifacts. They are not interchangeable.

**Manuscript package** — `books/sre/` plus the published Word file. Identity is the SHA-256 inventory in this manifest.

**Companion-lab package** — `books/labs/sre/northwind/`. Identity is the Git tags and dereferenced commits below. Executable gates were verified from those tags, not from the manuscript files alone.

The manuscript directory is not represented by a companion-lab Git commit. A reader who receives only the manuscript cannot independently re-run the lab. A reader who receives only the lab cannot identify the frozen manuscript checksums.

## Release scope

This release covers one **SRE (Site Reliability Engineering)** program for Northwind’s service portfolio: protected journeys, user-visible **SLIs (Service Level Indicators)** and **SLOs (Service Level Objectives)**, error-budget governance, burn-rate paging, on-call as a system, bounded toil, dependency contracts, deliberate degradation, portfolio incident command, reliability learning, regional-loss architecture, recurring game days, and regional fail-over that produces **Evidence of portfolio recovery**.

It does not claim to reteach the DevOps delivery path, the DevSecOps security path, or the Platform product path. It does not own platform-product job proofs as portfolio SLOs. It does not certify Northwind against a legal or industry framework. It does not add a fifth series book.

## Manuscript inventory

| File | SHA-256 |
|---|---|
| `00-how-to-use-this-book.md` | `97b52234d9c0d2352117e8aa27d9e21fdc9c472f1b1b70b38e6c173c38063f3a` |
| `01-define-what-reliability-must-protect.md` | `25fc7207de37fed9a81f426e209f2dd508a4d9168ca64bac540b31595ab68ebd` |
| `02-choose-indicators-users-can-feel.md` | `15fba4fc1b5f22fba24f501deb7b456a3f567bc333b3a5bc49f115f47eff0a3d` |
| `03-set-slos-and-error-budgets-across-the-portfolio.md` | `0684cdba6f3e0c48b1b3d381c38279efd12a26cd512d67c8252c25a24e4906b5` |
| `04-govern-change-with-error-budget-policy.md` | `868afbd38c74621f1c679703270c2e05441411f82d2d2ddaaea2fac28527ce0c` |
| `05-page-on-burn-rate-not-on-every-symptom.md` | `72e93527c0df29ea40e2773ca9092c22d04eaa171904d185a0caa7302f5a50eb` |
| `06-design-on-call-as-a-system.md` | `2774dd5dbaa3b9baca375d4a7c7d5d45a34d1c22c6abe5cfe0096635a82a3203` |
| `07-measure-and-bound-toil-without-hiding-the-work.md` | `257a908bd8c85b5f5e77a00132ebe366ca45d29f297cb95f38db2c3567b0b8bb` |
| `08-put-dependencies-inside-the-reliability-contract.md` | `1c0908310b59a70d85a158694801fd394b4cdbff085fe09e626521f613e00e73` |
| `09-degrade-deliberately-before-failure-cascades.md` | `8e52a84c40c1fafba4d2cac328ee3d4f77683e031aacc55f9b14606c2b8090c8` |
| `10-command-incidents-across-services-and-tenants.md` | `068db639f91d974a8d78e29b1abdce3b74edfe1139eef8430e9395d58b9a3f4b` |
| `11-turn-incidents-into-a-reliability-learning-program.md` | `3a1f635e0fcfd129d56127b889bc3e1bd6a7ec9923da466f53eb344322b93edc` |
| `12-design-for-the-loss-of-a-region.md` | `1e7fa859dd1bc037586f0ced1b416bb868881a7faad657949b4bb7edac69615b` |
| `13-run-game-days-as-a-recurring-program.md` | `4eab961af25adb17a49b0b82260ba4099f312f1a7f478bb82c4f06415dd9b869` |
| `14-fail-over-a-region-without-taking-the-portfolio-down.md` | `897e3c338e684ad719427a06ad984107647f7fb64eb0cf9044832199532631c9` |
| `15-conclusion.md` | `11a729890863cb12472882414ec440c79ff48c5f59257d836956f3692067349c` |
| `GLOSSARY.md` | `e392645d3925d75c52eaa564790844f1690fc9d925477f1a7fd61e0893d76458` |
| `REFERENCES.md` | `5ba836cb4a63d1c74b00bbbfb1e9aec9cfdd9c2117926a8b5e745bb57a00f282` |
| `RELEASE-CHECKLIST.md` | `9c01b0af63bc69c987b71c555801a40335c77125da74e79e307146c32e286ac5` |
| `BOOK-PLAN.md` | `1927992096c09dd81c88f551cb392d241ed7dcd18a10515f83b4238dff68d59f` |

`RELEASE-MANIFEST.md` does not include its own checksum because changing that value would change the file being identified.

## Companion-lab tags

Tags are curated cumulative exercise snapshots, not merge milestones. The commit recorded for each tag is the dereferenced commit.

The reader-facing aliases `chapter-NN-start` and `chapter-NN-complete` point to the corresponding verified `v1.0-` commits below. The versioned tags remain the immutable release identity; the generic aliases may advance in a later release.

This freeze records a linear history from `chapter-01-start` through `chapter-14-complete`. Readers are not required to treat later tags as Git merge milestones.

| Chapter | Start | Complete |
|---:|---|---|
| 1 | `6b96c59ec64722225c97fa3126c07e2c221e9a10` | `b1a26fbb256b37a2b19e58a44888ca335d9be8e4` |
| 2 | `a1679170f01502f07d66ad1d06d0cefb06228da0` | `8e0bff49aa6b490e3e05ebff7192c55fea84f105` |
| 3 | `52f08a078f31dcc095dfd3cb850057eda261cd29` | `3b7df7774fdb49a4234f145958fa016fe8476f92` |
| 4 | `d4c94db606864c82cdd284b48f3ef17a9162b68c` | `e69d3ba71bf983746a980f254354fa8e976c5c41` |
| 5 | `1986c48cd729df608c6ac7f7f4d78b7f676eaeb4` | `bff2df5dc961bc500b05641920679b9403c59c55` |
| 6 | `3c1720f972495efffca4f9a44469d6e4899bd0b9` | `93982f6a58e654daf8e97194a3fed506691259d7` |
| 7 | `2a6875a818c7d4bf15275984934836a9be87b20b` | `2d06db7c9eec84434457cfcc78642c248cd3abbd` |
| 8 | `00f8b6ad2cfc1600b5987e460ba9ea3fed7e65a4` | `c13a404d87eb351a9c07b6fd2065333b5ba68358` |
| 9 | `91fbad5125dc45d64d34189cfb3993ce35211ba6` | `fb12d61669d49d486c12b1650ce101d53850a5a3` |
| 10 | `738cd4392d55142384a22fa8895b53d1c7dcaeba` | `5570a0921125c08eaac6176dfc3702978fc2a5ab` |
| 11 | `f58fab54b9837bf0ab30fd5c2557cebaddfd1299` | `97d644f8e65c2a13171b07de17eacda39989cd08` |
| 12 | `d3a8ba59eb5d0f58cf31257e0f022079039e0465` | `5dc9af2420e6a7292f4bfca1b5268a44ad37c27a` |
| 13 | `542564b808d2f5c9e2bd1616d7e1296cb44ce226` | `1200051f2219766f7ec9a237d9656ba01f04d16b` |
| 14 | `947fa7f43461683afeb7a10c6b355728bb4efdeb` | `792fc3f4b4d405c80d609814677a44e8b132d751` |

## Verification environment

| Tool | Version |
|---|---|
| Python, tests, lint, and audit | 3.13.7 |
| pytest | 9.1.1 |
| Ruff | 0.16.0 |
| PyYAML | 6.0.3 |
| jsonschema | 4.26.0 |
| Git | 2.55.0 |

Python 3.13.7 executed the start/complete snapshot matrix and the working-tree test, lint, and audit suite using the pinned tools declared by the companion lab.

## Executable gate results

| Gate | Result |
|---|---|
| Red baselines | 14/14 passed from clean start-tag snapshots |
| Green completion checkpoints | 14/14 passed from clean complete-tag snapshots |
| Dedicated failure Make targets | none; SRE uses baseline (red) and checkpoint (green) rather than a separate `chapter-NN-failure` target |
| Python 3.13 test suite | 46/46 passed |
| Python 3.13 Ruff | Passed |
| Inherited DevOps v1.1 interface checksums | Passed |
| Inherited DevSecOps v1.0 interface checksums | Passed |
| Inherited Platform v1.0 interface checksums | Passed |
| Governed artifact schema validation | Passed |
| Companion-lab working tree | Clean |
| `MATRIX_REQUIRE_CLEAN=1 make matrix` | Passed from `v1.0-chapter-14-complete` |

Start-tag checkpoints were verified red: each `chapter-NN-checkpoint` failed on the corresponding `v1.0-chapter-NN-start` snapshot.

## Editorial gate results

- All 14 core chapters have exactly one Theory box.
- Every core chapter has guided Practice boxes and one Independent Practice.
- All 14 core chapters contain `What changed`, `What You Learned`, `Prove It`, `Durable outputs`, and `Next`.
- Every dedicated failure includes severity, plausible harm, potential blast radius, bounding controls, `Primary principles`, and the reliability questions that materially apply.
- Every dedicated scenario is classified as a cumulative reliability failure, connected consequence, or independent control failure.
- First-use abbreviation formatting was applied in chapters that introduce new abbreviations, plus the glossary, references, checklist, and this manifest.
- The manuscript contains approximately 47,846 words including the reader guide, conclusion, glossary, references, release checklist, and book plan.

## Reference validation

- Validation window: 2026-08-17
- Consolidated external **HTTP (Hypertext Transfer Protocol)** product or standards URLs: 0
- This book’s production decisions are Northwind’s. Inherited delivery, security, and platform-product contracts come from *Practical DevOps Engineering* v1.0, *Practical DevSecOps Engineering* v1.0, and *Practical Platform Engineering* v1.0 rather than from an SRE textbook, paging vendor, or public-cloud multi-region guide.
- Fictional Northwind identifiers were excluded because they are fixture evidence rather than external references.

## Known limitations

- The lab uses deterministic local evaluators for journeys, SLIs, SLOs, error-budget policy, burn paging, on-call, toil, dependencies, degradation, incidents, learning, regions, game days, and fail-over. It does not run a live telemetry backend, paging vendor, ticketing system, or multi-region fleet.
- **Evidence of portfolio recovery** is bounded by inventoried regional evidence, tenant isolation, numeric **RTO (Recovery Time Objective)** and **RPO (Recovery Point Objective)**, and independent journey observations. Chapter 14 does not prove a live multi-region fail-over.
- Chapter 13 game days exercise freeze, page path, dependency loss, and regional-loss tabletop. They do not emit recovered and are not a miniature of Chapter 14.
- The snapshot tags are curated cumulative snapshots. Their contract is documented in `00-how-to-use-this-book.md`.
- The v1.0 snapshot set contains 56 annotated tags: start and complete for each of 14 chapters, plus reader-facing aliases.
- Published format: `releases/practical-sre-engineering-v1.0.docx`. Rebuild with `python3 tools/docx/build_sre_docx.py`. A matching PDF was not produced in this inventory.
- Windows, burn multiples, RTO, RPO, and cadence values are Northwind teaching values and require service-specific validation.
- Source links, where later added, remain externally maintained and may change.

## Companion-book boundaries

- DevOps: delivery-path evidence, progressive release, data-change compatibility, **GitOps (Git-based operations)** operation, and reconstruction from durable operational evidence.
- DevSecOps: threat and risk, attributable identity, supply chain, secrets, policy, detection, containment, eradication, and bounded restored trust.
- Platform: owned internal platform product, job-time budgets, catalog contacts, fleet upgrade freeze `storage-1-0-to-2-0`, plane last known good `1.0`, contract last known good `tenant-storage-1.0`, and remaining owner `reliability-program`.
- No fifth series book is in scope (Decision 004).

## Freeze decision

Editorial and executable release gates passed on 2026-08-17. This manifest freezes the Practical SRE Engineering manuscript as first edition `v1.0` and records the companion-lab `v1.0-` snapshot tags.

Any post-freeze change to a manuscript file, companion-lab tag, verifier, fixture, or later published Word file requires a new manifest and version.
