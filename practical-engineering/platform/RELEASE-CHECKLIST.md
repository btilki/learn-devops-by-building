# Release Checklist

Use this checklist before freezing a manuscript revision or publishing a companion-lab release.

## Book structure

- [ ] `BOOK-PLAN.md` and the reader-facing index contain the same chapter order.
- [ ] Every core chapter has one dominant production question and one falsifiable product change.
- [ ] Every `Next` promise matches the following chapter's opening state.
- [ ] Northwind service names, Storefront and Fulfillment tenants, and the Chapter 1 promise remain consistent.
- [ ] DevOps, DevSecOps, and **SRE (Site Reliability Engineering)** scope boundaries do not contradict later chapters.
- [ ] Reader guide, conclusion, glossary, and references are present.
- [ ] Mechanism, decision, outcome, and recovery evidence remain distinct.
- [ ] Tenant isolation recovery is **Evidence of restored isolation**, never DevSecOps restored-trust wording.
- [ ] Chapter 14 recovery evidence is **Evidence of bounded platform-product recovery**, not a live-cluster or enterprise DR claim.
- [ ] Platform-product unreliability is a **job-time budget**. Reserve **error budget** for SRE portfolio governance.
- [ ] Platform-product **SLIs (Service Level Indicators)** are not portfolio **SLOs (Service Level Objectives)**.
- [ ] Chapter 9 exception rows reference inherited DevSecOps exception IDs and do not copy owner, scope, compensation, or expiry.

## Chapter format

- [ ] Exactly one `Theory` box establishes the chapter's main mental model.
- [ ] Meaningful guided actions use `Practice` boxes. Concept-led sections do not receive artificial exercises.
- [ ] The final unaided exercise uses one `Independent Practice` box.
- [ ] Theory is sufficient for production decisions but does not become a detached survey.
- [ ] `What changed`, `What You Learned`, `Prove It`, `Durable outputs`, and `Next` are present.
- [ ] Every chapter names one or two durable outputs already produced by its guided path.
- [ ] Dedicated failure material includes severity, plausible harm, potential blast radius, bounding controls, `Primary principles`, and the platform questions that materially apply.
- [ ] Dedicated scenarios are classified as cumulative product failure, connected consequence, or independent control failure.
- [ ] Concept-led chapters use `Test the model under failure`; decision-led use `Test the decision under failure`; implementation-led and hybrid use `Test the design under failure`.
- [ ] A denied contract check is not described as restored isolation. Chapter 14 is the first chapter that produces recovery evidence, and it is bounded.

## Terminology and claims

- [ ] An abbreviation's first prose use in each document is bold and expanded in parentheses.
- [ ] Literal commands, paths, configuration keys, identifiers, and version strings are not altered to satisfy prose formatting.
- [ ] Illustrative floors, ceilings, freeze windows, and dates are identified as Northwind cadence rather than universal.
- [ ] Best Practice and Production Practice are distinguished where production validation changes the answer.
- [ ] Self-approval is a plane-identity check, not `subject == approved_by`.
- [ ] Plane last known good and contract last known good are not collapsed because both say `1.0`.
- [ ] Product and standards claims cite primary or authoritative sources, or state that the decision is Northwind's.
- [ ] Simulator limitations appear beside claims that depend on them.
- [ ] No chapter repeats a DevOps or DevSecOps implementation as new platform work.

## Companion implementation

Working-tree manuscript verification uses the lab as received. Snapshot-tag items apply at companion-lab freeze.

- [ ] Every reader-facing path and filename exists in the lab working tree.
- [ ] Every documented `make` target exists.
- [ ] Every `chapter-NN-start` tag runs its baseline and proves the capability is red. *(Companion-lab freeze.)*
- [ ] Every `chapter-NN-complete` tag can reach a green checkpoint through the documented sequence. *(Companion-lab freeze.)*
- [ ] Every dedicated failure target runs from the completed implementation with documented prerequisites.
- [ ] Failure commands inject onto the completed snapshot in memory and do not rewrite the working tree.
- [ ] Checkpoints verify capabilities or behavior, not only file presence or self-emitted passing grades.
- [ ] Observations and expectations are independent where the decision could otherwise approve itself.
- [ ] Generated evidence, caches, virtual environments, and simulated state remain untracked.
- [ ] Inherited DevOps v1.1 and DevSecOps v1.0 interfaces match their checksum manifests.
- [ ] The lab does not read earlier labs' working trees at runtime.
- [ ] No fixture contains a real credential, personal data, or destructive external action.
- [ ] Simulator limitations are explicit and do not imply that a live portal, cluster, billing system, or ticketing system ran.
- [ ] `make test`, `make lint`, and `make audit` pass.
- [ ] The lab working tree is clean.

## Snapshot contract

These items apply when companion-lab tags are published.

- [ ] Versioned `v1.0-chapter-NN-start` and `v1.0-chapter-NN-complete` tags exist for every core chapter.
- [ ] Reader-facing `chapter-NN-start` and `chapter-NN-complete` aliases point to those commits.
- [ ] Tag annotations describe start versus completed state.
- [ ] Readers are told that tags are curated cumulative snapshots rather than merge milestones.
- [ ] Failure state is generated from the complete snapshot and is not preserved as a trusted completed reference.
- [ ] Chapter 14 recovery verification remains bounded by inventoried plane evidence, tenant isolation, and stated **RTO (Recovery Time Objective)** limitations.

## Final release record

- [ ] Record the manuscript package identity separately from the companion-lab package identity.
- [ ] Record the companion-lab commit and tag set when that package is published.
- [ ] Record Python and tool versions used for verification.
- [ ] Record the date of source-link and version-sensitive claim review.
- [ ] Record known limitations, including bounded restored isolation and unpublished snapshot tags, in this book's release manifest.
