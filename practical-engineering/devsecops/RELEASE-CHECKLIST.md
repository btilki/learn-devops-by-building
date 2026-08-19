# Release Checklist

Use this checklist before freezing a manuscript revision or publishing a companion-lab release.

## Book structure

- [ ] `BOOK-PLAN.md` and the reader-facing index contain the same chapter order.
- [ ] Every chapter has one dominant production question and one falsifiable system change.
- [ ] Every `Next` promise matches the following chapter's opening state.
- [ ] Northwind service names, transaction flow, critical business outcome, and critical security outcome remain consistent.
- [ ] DevOps, Platform Engineering, and **SRE (Site Reliability Engineering)** scope boundaries do not contradict later chapters.
- [ ] Reader guide, conclusion, glossary, and references are present.
- [ ] Mechanism, decision, outcome, and recovery evidence remain distinct.
- [ ] Restored trust is stated as a bounded claim, never as universal absence of persistence.
- [ ] The support-data path remains in the threat, risk, and governance registers; the incident arc's payment-only scope is explicit.

## Chapter format

- [ ] Exactly one `Theory` box establishes the chapter's main mental model.
- [ ] Meaningful guided actions use `Practice` boxes. Concept-led sections do not receive artificial exercises.
- [ ] The final unaided exercise uses one `Independent Practice` box.
- [ ] Theory is sufficient for production decisions but does not become a detached survey.
- [ ] `What changed`, `What You Learned`, `Prove It`, `Durable outputs`, and `Next` are present.
- [ ] Every chapter names one or two durable outputs already produced by its guided path.
- [ ] Dedicated failure material includes severity, plausible harm, potential blast radius, bounding controls, `Primary principles`, and the security questions that materially apply.
- [ ] Dedicated scenarios are classified as cumulative attack, connected consequence, or independent control failure.
- [ ] Containment and recovery remain separate when active harm can be bounded before trust is restored.
- [ ] A corrective action is not described as recovery without outcome and recovery evidence.

## Terminology and claims

- [ ] An abbreviation's first prose use in each document is bold and expanded in parentheses.
- [ ] Literal commands, paths, configuration keys, image names, and version identifiers are not altered to satisfy prose formatting.
- [ ] Illustrative thresholds, exception windows, overlap periods, and objectives are identified as contextual rather than universal.
- [ ] Best Practice and Production Practice are distinguished where production validation changes the answer.
- [ ] Product and standards claims cite primary or authoritative sources.
- [ ] Version-sensitive claims and links have been rechecked near publication time.
- [ ] Simulator limitations appear beside claims that depend on them.
- [ ] No chapter repeats a DevOps implementation as new DevSecOps content.

## Companion implementation

Working-tree manuscript verification uses the lab as received. Snapshot-tag items apply at companion-lab freeze.

- [x] Every reader-facing path and filename exists in the lab working tree.
- [x] Every documented `make` target exists.
- [x] Every `chapter-NN-start` tag runs its baseline and proves the capability is red. *(Chapter 8 baseline is a complete-tree displacement check; the start overlay keeps the checkpoint red.)*
- [x] Every `chapter-NN-complete` tag can reach a green checkpoint through the documented sequence.
- [x] Every dedicated failure, challenge, containment, and recovery target runs from the completed implementation with documented prerequisites.
- [x] Checkpoints verify capabilities or behavior, not only file presence or configured booleans.
- [x] Observations and expectations are independent where the decision could otherwise approve itself.
- [x] Generated attack, containment, and recovery artifacts remain untracked except the Chapter 16 assurance evidence files cited by the complete snapshot.
- [x] Inherited DevOps v1.1 interfaces match their checksum manifest.
- [x] No fixture contains a real credential, personal data, active malware, or external attack target.
- [x] Simulator limitations are explicit and do not imply that a live production mechanism ran.
- [x] `make test`, `make lint`, and `make audit` pass.
- [x] The lab working tree is clean.

## Snapshot contract

These items apply when companion-lab tags are published.

- [x] Versioned `v1.0-chapter-NN-start` and `v1.0-chapter-NN-complete` tags exist for every core chapter.
- [x] Reader-facing `chapter-NN-start` and `chapter-NN-complete` aliases point to those commits.
- [x] Tag annotations describe start versus completed state.
- [x] Readers are told that tags are curated cumulative snapshots rather than merge milestones.
- [x] Attack state is generated from the complete snapshot and is not preserved as a trusted completed reference.
- [x] Verifier corrections applied after drafting are reflected in both relevant snapshots.
- [x] Chapter 15 recovery verification remains bounded by inventoried roots, modeled descendants, and stated evidence limits.

## Final release record

- [x] Record the manuscript revision or archive checksum.
- [x] Record the companion-lab commit and tag set.
- [x] Record Python and tool versions used for verification.
- [x] Record the date of source-link and version-sensitive claim review.
- [x] Record known limitations, including bounded restored trust and the payment-only incident arc, in this book's release manifest.
