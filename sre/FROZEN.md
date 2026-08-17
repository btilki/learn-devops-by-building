# Practical SRE Engineering — Frozen Planning Set

**Status:** Frozen  
**Planning freeze date:** 2026-08-16  
**Manuscript freeze date:** 2026-08-17  
**Planning version:** 1.0

The scope, teaching contract, chapter index, cumulative reliability narrative, chapter map, companion-lab architecture, schema inventory, editorial conventions, and pre-freeze audit for *Practical SRE Engineering* are approved and frozen.

## Frozen identity

| File | SHA-256 |
|---|---|
| `SERIES-DECISIONS.md` | `97e110c50f77dc62e9450afb62be2cf4f7fa5e545ac7c866e1bfcc8b5e2f31d1` |
| `sre/BOOK-PLAN.md` | `1927992096c09dd81c88f551cb392d241ed7dcd18a10515f83b4238dff68d59f` |
| `sre/CHAPTER-MAP.md` | `d3b03814c05312411cfce02dd0263672bc02de5ab742ff3682c6887010f33faa` |
| `sre/LAB-PLAN.md` | `1322afeaddd9c0b0a1867cf4de7f00fba5f9e32fbbbb0e521c1c84f450116e07` |
| `sre/SCHEMA-INVENTORY.md` | `70b33341367411e26ddc03857e042e89c2cebb90f1766d1c3168eaaaec8d5982` |
| `sre/EDITORIAL-CONVENTIONS.md` | `d108a2381d497ea9aa1b18f8eea89e2e4b70e61aead2decf4e352296e7a9f045` |
| `sre/PRE-FREEZE-AUDIT.md` | `00399f83b6583d6ee6f87d795d853388d5627196c41fd95fb61d7b21782c7da4` |

`sre/FROZEN.md` does not include its own checksum because changing that value would change the file being identified.

## Frozen decisions

- The book contains 14 core chapters, plus the reader guide and conclusion.
- Concept-led, decision-led, implementation-led, and hybrid chapters are permitted.
- Important operational concepts do not require artificial exercises (Decision 001).
- Every substantial conceptual section must affect a decision, durable reasoning artifact, evidence interpretation, failure diagnosis, or later implementation dependency.
- Northwind Commerce and its critical order outcome continue from the published DevOps, DevSecOps, and Platform books.
- A second user-facing service, Fulfillment / `fulfillment-api`, makes the portfolio real. Availability theater plus informal heroics is the cumulative reliability failure.
- The five series principles remain in force; four recurring reliability questions guide journey-, budget-, and recovery-specific reasoning.
- Mechanism, decision, outcome, and recovery evidence remain distinct.
- Regional fail-over recovery is **Evidence of portfolio recovery**, never DevSecOps restored-trust wording and never Platform isolation or platform-product recovery wording.
- Platform-product unreliability remains a **job-time budget**. Reserve **error budget** for SRE portfolio governance.
- Platform-product indicators are not SRE portfolio SLOs. Catalog `*-oncall` contacts are not an on-call system.
- Error-budget freeze of fleet upgrade `storage-1-0-to-2-0` references the inherited Platform record and does not copy or relabel that upgrade freeze.
- Inherited DevSecOps `self_approval_forbidden` is the named authorization field on-call authority consumes.
- Lab states are `start / baseline / complete / challenge / failure / contained / recovered`. Correction is inside the challenge write-up.
- The SRE lab is separate from earlier labs and inherits only minimal checksum-identified DevOps, DevSecOps, and Platform interfaces (Decision 004).
- The lab supports Python 3.13 and uses PyYAML plus `jsonschema` at runtime; exact dependency versions and hashes are pinned during scaffolding.
- Local failures are inert, deterministic, synthetic, non-destructive simulations with explicit evidentiary limits.
- Chapter 14 fail-over is modeled **Evidence of portfolio recovery**, not a live multi-region program.
- First edition is v1.0 (Decision 003).

## Drafting and implementation policy

The planning set, manuscript v1.0, and companion-lab tags are frozen. Later work must preserve the frozen promise, boundaries, sequence, chapter outcomes, evidence semantics, reliability-failure continuity, and lab safety contract.

Chapter 13 game days must continue to exercise error-budget freeze, on-call page path, dependency loss, and regional-loss tabletop or simulated fail-over. They must not be only a rehearsal of Chapter 14 fail-over.

Implementation details may be refined when scaffolding reveals a safe technical necessity, provided the refinement does not change a chapter's primary production question, reliability outcome, form, dependency handoff, or durable outputs.

A change to the promise, scope boundary, chapter count or order, cumulative reliability narrative, evidence taxonomy, inherited-baseline strategy, or safety contract requires:

1. an explicit planning revision;
2. an updated cross-document audit;
3. new checksums;
4. a new planning version; and
5. author approval before affected drafting continues.

The published DevOps, DevSecOps, and Platform v1.0 books remain unchanged.

## Next authorized phase

The four-book series is frozen. Manuscript v1.0 and companion-lab tags are recorded in `sre/RELEASE-MANIFEST.md`. Future corrections require a new version. There is no fifth series book in Decision 004.
