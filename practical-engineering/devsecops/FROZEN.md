# Practical DevSecOps Engineering — Frozen Planning Set

**Status:** Frozen  
**Freeze date:** 2026-08-15  
**Planning version:** 1.0

The scope, teaching contract, chapter index, cumulative security narrative, chapter map, companion-lab architecture, schema inventory, and pre-freeze audit for *Practical DevSecOps Engineering* are approved and frozen.

## Frozen identity

| File | SHA-256 |
|---|---|
| `SERIES-DECISIONS.md` | `67187a619e0e70f63ec901363a8e22f1b27348a1d6fde8f31d78560558e85eb3` |
| `devsecops/BOOK-PLAN.md` | `9810e388761256445a338a2ede620fe4c20140757560746928e326933fd92e86` |
| `devsecops/CHAPTER-MAP.md` | `a290d854202d0857cebce534aeb8e984a1473e8648b0618b8972be57235eff97` |
| `devsecops/LAB-PLAN.md` | `1a7d9ee80aa816f49bd33fdcc6152b261639b81392061198a266c1026e9c3990` |
| `devsecops/SCHEMA-INVENTORY.md` | `a9b4f8558c10e7b2c0023628a38810c9da75dc6bdcb80744c865d56b5c20d066` |
| `devsecops/PRE-FREEZE-AUDIT.md` | `2725df74fb1cf87fe7b4aa2c81522119e81f3902de9679b41c81a69358e47114` |

`devsecops/FROZEN.md` does not include its own checksum because changing that value would change the file being identified.

## Frozen decisions

- The book contains 16 core chapters, plus the reader guide and conclusion.
- Concept-led, decision-led, implementation-led, and hybrid chapters are permitted.
- Important operational concepts do not require artificial exercises.
- Every substantial conceptual section must affect a decision, durable reasoning artifact, evidence interpretation, attack diagnosis, or later implementation dependency.
- Northwind Commerce and its critical order outcome continue from the frozen DevOps book.
- A compromised-maintainer intrusion provides the cumulative attack narrative, supplemented by explicitly labeled connected consequences and independent control failures.
- The five series principles remain in force; four recurring security questions guide threat- and compromise-specific reasoning.
- Mechanism, decision, outcome, and recovery evidence remain distinct.
- The DevSecOps lab is separate from the frozen DevOps lab and inherits only minimal checksum-identified stable interfaces.
- The lab supports Python 3.13 and uses PyYAML plus `jsonschema` at runtime; exact dependency versions and hashes are pinned during scaffolding.
- Local attacks are inert, deterministic, synthetic, non-destructive simulations with explicit evidentiary limits.
- Restored trust is a bounded claim and must never be presented as universal proof that no attacker persistence exists.

## Drafting and implementation policy

Chapter and lab work may now begin. It must preserve the frozen promise, boundaries, sequence, chapter outcomes, evidence semantics, attack continuity, and lab safety contract.

Implementation details may be refined when scaffolding reveals a safe technical necessity, provided the refinement does not change a chapter's primary production question, security outcome, form, dependency handoff, or durable outputs.

A change to the promise, scope boundary, chapter count or order, cumulative attack narrative, evidence taxonomy, inherited-baseline strategy, or safety contract requires:

1. an explicit planning revision;
2. an updated cross-document audit;
3. new checksums;
4. a new planning version; and
5. author approval before affected drafting continues.

The published DevOps v1.0 book remains frozen. Companion-lab snapshot tags remain the historical `v1.1-` set.

## Next authorized phase

Manuscript edition `v1.0` and companion-lab snapshot tags are frozen. See `RELEASE-MANIFEST.md`. Future corrections must use a new version.
