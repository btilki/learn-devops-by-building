# Release Checklist

Use this checklist before freezing a manuscript revision or publishing a companion-lab release.

## Book structure

- [ ] `BOOK-PLAN.md` and the reader-facing index contain the same chapter order.
- [ ] Every chapter has one dominant production question and one falsifiable system change.
- [ ] Every `Next` promise matches the following chapter's opening state.
- [ ] Northwind service names, transaction flow, and critical outcome remain consistent.
- [ ] DevOps, DevSecOps, Platform Engineering, and **SRE (Site Reliability Engineering)** scope boundaries do not contradict later chapters.
- [ ] Introduction, architecture guide, conclusion, glossary, and references are present.

## Chapter format

- [ ] Exactly one `Theory` box establishes the chapter's main mental model.
- [ ] Meaningful guided actions use `Practice` boxes.
- [ ] The final unaided exercise uses one `Independent Practice` box.
- [ ] Theory is sufficient for production decisions but does not become a detached survey.
- [ ] `What changed`, `What You Learned`, `Prove It`, and `Next` are present.
- [ ] Every implementation chapter names one or two durable outputs already produced by its guided path.
- [ ] Dedicated failure material includes severity, potential blast radius, bounding controls, and `Primary principles`.
- [ ] A corrective action is not described as recovery without outcome evidence.

## Terminology and claims

- [ ] An abbreviation's first prose use in each document is bold and expanded in parentheses.
- [ ] Literal commands, paths, configuration keys, image names, and version identifiers are not altered to satisfy prose formatting.
- [ ] Illustrative thresholds, resource values, cohorts, and objectives are identified as contextual rather than universal.
- [ ] Best Practice and Production Practice are distinguished where workload validation changes the answer.
- [ ] Product and standards claims cite primary or authoritative sources.
- [ ] Version-sensitive claims and links have been rechecked near publication time.

## Companion implementation

- [ ] Every reader-facing path and filename exists in the tagged exercise snapshot.
- [ ] Every documented `make` target exists.
- [ ] Every `chapter-NN-start` tag runs its baseline and proves the capability is red.
- [ ] Every `chapter-NN-complete` tag can reach a green checkpoint through the documented sequence.
- [ ] Every dedicated failure target runs from the completed implementation with documented prerequisites.
- [ ] Checkpoints verify capabilities or behavior, not only file presence or configured booleans.
- [ ] Observations and expectations are independent where the decision could otherwise approve itself.
- [ ] Generated evidence, caches, virtual environments, simulated cloud state, and backup artifacts remain untracked.
- [ ] Simulator limitations are explicit and do not imply that a live production mechanism ran.
- [ ] `make test`, `make lint`, and `git diff --check` pass.
- [ ] The lab working tree is clean.

## Snapshot contract

- [ ] Start and complete tags exist for every chapter.
- [ ] Tag annotations describe start versus completed state.
- [ ] Readers are told that tags are curated cumulative snapshots rather than merge milestones.
- [ ] Verifier corrections applied after drafting are reflected in both relevant snapshots.
- [ ] Chapter 2 documents local artifact/evidence generation before tamper checks.
- [ ] Chapter 3 documents simulated cloud/state generation before its completed checkpoint.

## Final release record

- [ ] Record the manuscript revision or archive checksum.
- [ ] Record the companion-lab commit and tag set.
- [ ] Record Python and tool versions used for verification.
- [ ] Record the date of source-link and version-sensitive claim review.
- [ ] Record known limitations and deferred work in the appropriate companion book.
