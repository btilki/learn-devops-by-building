# Release Checklist

Use this checklist before freezing a manuscript revision or publishing a companion-lab release.

## Book structure

- [ ] `BOOK-PLAN.md` and the reader-facing index contain the same chapter order.
- [ ] Every core chapter has one dominant production question and one falsifiable reliability change.
- [ ] Every `Next` promise matches the following chapter's opening state.
- [ ] Northwind service names, Storefront and Fulfillment journeys, and the Chapter 1 promise remain consistent.
- [ ] DevOps, DevSecOps, and Platform scope boundaries do not contradict later chapters.
- [ ] Reader guide, conclusion, glossary, and references are present.
- [ ] Mechanism, decision, outcome, and recovery evidence remain distinct.
- [ ] Regional fail-over recovery is **Evidence of portfolio recovery**, never DevSecOps restored-trust wording and never Platform isolation or platform-product recovery wording.
- [ ] Platform-product unreliability is a **job-time budget**. Reserve **error budget** for SRE portfolio governance.
- [ ] Platform-product **SLIs (Service Level Indicators)** are not portfolio **SLOs (Service Level Objectives)**.
- [ ] Catalog `*-oncall` contacts are not an on-call system.
- [ ] Chapter 4 fleet freeze references `storage-1-0-to-2-0` and does not copy the Platform upgrade freeze.

## Chapter format

- [ ] Exactly one `Theory` box establishes the chapter's main mental model.
- [ ] Meaningful guided actions use `Practice` boxes. Concept-led sections do not receive artificial exercises.
- [ ] The final unaided exercise uses one `Independent Practice` box.
- [ ] Theory is sufficient for production decisions but does not become a detached survey.
- [ ] `What changed`, `What You Learned`, `Prove It`, `Durable outputs`, and `Next` are present.
- [ ] Every chapter names one or two durable outputs already produced by its guided path.
- [ ] Dedicated failure material includes severity, plausible harm, potential blast radius, bounding controls, `Primary principles`, and the reliability questions that materially apply.
- [ ] Dedicated scenarios are classified as cumulative reliability failure, connected consequence, or independent control failure.
- [ ] Concept-led chapters use `Test the model under failure`; decision-led use `Test the decision under failure`; implementation-led and hybrid use `Test the design under failure`.
- [ ] Chapter 14 is the first chapter that produces recovery evidence, and it is bounded. Journey **SLO** outcomes are computed from independent observations; verification does not emit `slo_met` or `status: recovered`.

## Terminology and claims

- [ ] An abbreviation's first prose use in each document is bold and expanded in parentheses.
- [ ] Literal commands, paths, configuration keys, identifiers, and version strings are not altered to satisfy prose formatting.
- [ ] Illustrative SLO targets, windows, RTO, RPO, and cadence values are identified as Northwind teaching values rather than universal.
- [ ] Best Practice and Production Practice are distinguished where production validation changes the answer.
- [ ] Plane last known good `1.0` and contract last known good `tenant-storage-1.0` are not collapsed.
- [ ] Product and standards claims cite primary or authoritative sources, or state that the decision is Northwind's.
- [ ] Simulator limitations appear beside claims that depend on them.
- [ ] No chapter repeats a DevOps, DevSecOps, or Platform implementation as new SRE work.

## Companion implementation

Working-tree manuscript verification uses the lab as received. Snapshot-tag items apply at companion-lab freeze.

- [ ] Every reader-facing path and filename exists in the lab working tree.
- [ ] Every documented `make` target exists, including `matrix`.
- [ ] Every `chapter-NN-start` tag runs its baseline and proves the capability is red. *(Companion-lab freeze.)*
- [ ] Every `chapter-NN-complete` tag can reach a green checkpoint through the documented sequence. *(Companion-lab freeze.)*
- [ ] Failure state is generated from the complete snapshot in memory and is not rewritten into the working tree as a trusted complete reference.
- [ ] Checkpoints verify capabilities or behavior, not only file presence or self-emitted passing grades.
- [ ] Observations and expectations are independent where the decision could otherwise approve itself.
- [ ] Generated evidence, caches, virtual environments, and simulated state remain untracked.
- [ ] Inherited DevOps v1.1, DevSecOps v1.0, and Platform v1.0 interfaces match their checksum manifests.
- [ ] The lab does not read earlier labs' working trees at runtime.
- [ ] No fixture contains a real credential, personal data, or destructive external action.
- [ ] Simulator limitations are explicit and do not imply that a live telemetry backend, paging vendor, or multi-region fleet ran.
- [ ] `make test`, `make lint`, `make audit`, and `make matrix` pass.
- [ ] The lab working tree is clean.

## Snapshot contract

These items apply when companion-lab tags are published.

- [ ] Versioned `v1.0-chapter-NN-start` and `v1.0-chapter-NN-complete` tags exist for every core chapter.
- [ ] Reader-facing `chapter-NN-start` and `chapter-NN-complete` aliases point to those commits.
- [ ] Tag annotations describe start versus completed state.
- [ ] Readers are told that tags are curated cumulative snapshots rather than merge milestones.
- [ ] Failure state is generated from the complete snapshot and is not preserved as a trusted completed reference.
- [ ] Chapter 14 recovery verification remains bounded by inventoried regional evidence, tenant isolation, computed journey SLO outcomes, and stated **RTO (Recovery Time Objective)** limitations.

## Final release record

- [ ] Record the manuscript package identity separately from the companion-lab package identity.
- [ ] Record the companion-lab commit and tag set when that package is published.
- [ ] Record Python and tool versions used for verification.
