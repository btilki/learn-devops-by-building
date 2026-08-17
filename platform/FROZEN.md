# Practical Platform Engineering — Frozen Planning Set

**Status:** Frozen  
**Freeze date:** 2026-08-16  
**Planning version:** 1.0

The scope, teaching contract, chapter index, cumulative platform narrative, chapter map, companion-lab architecture, schema inventory, editorial conventions, and pre-freeze audit for *Practical Platform Engineering* are approved and frozen.

## Frozen identity

| File | SHA-256 |
|---|---|
| `SERIES-DECISIONS.md` | `5e19c4d0e4e835c13e098309f516f20d8023a2fed73268d28eef366ae8ea974e` |
| `platform/BOOK-PLAN.md` | `92b8f7572bc47c0fbb70d403a926f7977ebb3445a33a22d1bf0f92236844099a` |
| `platform/CHAPTER-MAP.md` | `ea332361c87e3a78fb4ee6aaa682c234560a2a8bc4066ba86377870a0c15aff8` |
| `platform/LAB-PLAN.md` | `3b4f058f334ce8c882ecd2394cd04af5a2376dce483c594f16573db92a3a1a4b` |
| `platform/SCHEMA-INVENTORY.md` | `666d09a25d4ecf5655b0139489cebd26920e82cac3639f45e2cd772c2cb02b5c` |
| `platform/EDITORIAL-CONVENTIONS.md` | `449eb6301f37a85736ad9ab44c18a8955793af965b0fa5ecad813fe18621bd67` |
| `platform/PRE-FREEZE-AUDIT.md` | `41b9d785905ce164de279e9dcbe2cb2044929a16caebc69ea6ac98d349acf532` |

`platform/FROZEN.md` does not include its own checksum because changing that value would change the file being identified.

## Frozen decisions

- The book contains 14 core chapters, plus the reader guide and conclusion.
- Concept-led, decision-led, implementation-led, and hybrid chapters are permitted.
- Important operational concepts do not require artificial exercises (Decision 001).
- Every substantial conceptual section must affect a decision, durable reasoning artifact, evidence interpretation, failure diagnosis, or later implementation dependency.
- Northwind Commerce and its critical order outcome continue from the published DevOps and DevSecOps books.
- A second tenant, Fulfillment / `fulfillment-api`, makes tenancy real. Shared authority is the cumulative product failure.
- The five series principles remain in force; four recurring platform questions guide product- and isolation-specific reasoning.
- Mechanism, decision, outcome, and recovery evidence remain distinct.
- Tenant isolation recovery is **Evidence of restored isolation**, never DevSecOps restored-trust wording.
- Chapter 14 recovery evidence is **Evidence of bounded platform-product recovery**, not a live-cluster recovery test.
- Platform-product unreliability is a **job-time budget**. Reserve **error budget** for SRE portfolio governance.
- Platform-product indicators are not SRE portfolio SLOs.
- Chapter 9 exception rows reference inherited DevSecOps exception IDs and do not copy owner, scope, compensation, or expiry.
- Lab states are `start / baseline / complete / challenge / failure / contained / recovered`. Correction is inside the challenge write-up.
- The Platform lab is separate from earlier labs and inherits only minimal checksum-identified DevOps and DevSecOps interfaces.
- The lab supports Python 3.13 and uses PyYAML plus `jsonschema` at runtime; exact dependency versions and hashes are pinned during scaffolding.
- Local failures are inert, deterministic, synthetic, non-destructive simulations with explicit evidentiary limits.
- Control-plane recovery is bounded tenant isolation, not a regional-loss or portfolio RTO program.
- *Practical SRE Engineering* is the planned fourth book (Decision 004). First edition is v1.0 (Decision 003).

## Drafting and implementation policy

Chapter and lab work may now begin. It must preserve the frozen promise, boundaries, sequence, chapter outcomes, evidence semantics, product-failure continuity, and lab safety contract.

Implementation details may be refined when scaffolding reveals a safe technical necessity, provided the refinement does not change a chapter's primary production question, platform outcome, form, dependency handoff, or durable outputs.

A change to the promise, scope boundary, chapter count or order, cumulative product narrative, evidence taxonomy, inherited-baseline strategy, or safety contract requires:

1. an explicit planning revision;
2. an updated cross-document audit;
3. new checksums;
4. a new planning version; and
5. author approval before affected drafting continues.

The published DevOps and DevSecOps v1.0 books remain unchanged.

## Next authorized phase

Manuscript edition `v1.0` and companion-lab snapshot tags are frozen. See `RELEASE-MANIFEST.md`. Future corrections must use a new version.
