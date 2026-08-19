# Practical Engineering Series — Decisions

This file lives under `books/practical-engineering/`. The Boutique Production Series is a separate tree: `../boutique-production/`.

This file preserves decisions that apply across books and conversational sessions. Book-specific plans may refine these rules but must not silently contradict them.

## Decision 001 — Concept-led teaching is allowed when operational reasoning requires it

- **Status:** Accepted
- **Date:** 2026-08-15
- **Applies from:** *Practical DevSecOps Engineering* and every later series book

### Context

*Practical DevOps Engineering* is a compact, implementation-driven book. The next book must retain the series' production focus without treating that page count, chapter pattern, or implementation density as a fixed template.

DevSecOps decisions can be unsafe when readers lack complete mental models for risk, trust, identity, policy, evidence, and compromise. Some of these concepts are necessary for later production decisions even when their explanation does not immediately produce a file, command, or runnable exercise.

### Decision

Important concepts may receive dedicated explanation without an immediate practice exercise when they are necessary for reasoning about later production decisions.

Conceptual material must:

- remain relevant to the book's operational scope;
- enable a concrete security decision, interpretation, or later implementation;
- explain consequences and trade-offs rather than becoming a beginner survey; and
- avoid detached academic theory.

There is no theory-to-practice ratio and no artificial exercise added merely to satisfy one. Practice remains central wherever implementation is the appropriate proof of capability.

### Priority concept areas for *Practical DevSecOps Engineering*

- Threat modeling and trust boundaries
- Risk, likelihood, impact, and control selection
- Authentication, authorization, identity, and delegation
- Data classification and security ownership
- Software supply-chain trust
- Vulnerability severity, exploitability, and prioritization
- Policy, enforcement points, exceptions, and evidence
- Detection versus prevention
- Security incidents, containment, eradication, and recovery
- Governance, compliance, and audit evidence

This list guides planning; it is not a frozen chapter index.

### Permitted chapter forms

**Concept-led chapter:** production problem → complete mental model → decision examples → consequences → later implementation connection

**Implementation-led chapter:** production problem → necessary concepts → guided implementation → attack or failure → diagnosis → recovery

**Decision-led chapter:** competing approaches → threat and operational trade-offs → production recommendation → documented decision

The final book plan may combine these forms when a chapter's learning objective requires it.

### Consequences

- *Practical DevSecOps Engineering* is not constrained to the first book's 111-page length.
- Not every important concept requires an immediate command, file, or exercise.
- Every concept still needs an operational reason for inclusion and a connection to production decisions.
- Book planning must distinguish concept outcomes, implementation outcomes, evidence, and durable outputs rather than forcing every chapter into one template.
- The published *Practical DevOps Engineering* files remain unchanged except by an explicit new edition.
- Later books inherit the no-ratio rule. Domain-specific concept lists stay book-local; the prohibition on artificial practice is series-wide.

## Decision 002 — Word publication style is shared across the series

- **Status:** Accepted
- **Date:** 2026-08-16
- **Applies from:** *Practical DevOps Engineering* and *Practical DevSecOps Engineering*, and every later series book

### Context

The accepted Word treatment was iterated on the published DevOps and DevSecOps DOCX files: author line, Contents numbering, running header, table fills and borders, practice-box color, and code-block Gray-5% fill. Those choices must not be reinvented per book.

### Decision

Every Practical Engineering Word file uses the same publication style.

- Canonical colors and helpers live in `tools/docx/series_style.py`.
- The human-readable contract is `SERIES-PUBLICATION-STYLE.md`.
- Cursor enforcement is `.cursor/rules/series-docx-publication.mdc`.
- New book DOCX builders must import `series_style` and apply that treatment. Do not invent a new palette.

### Required treatment

- Author is **Birol Tilki** on the title page and in document properties.
- Contents omits How to Use This Book. List numbers match chapter numbers. Put the number inside the hyperlink text. Wrap heading text with the bookmark.
- Running header is the numbered chapter title only. Do not put the book name in the header.
- Table header cells: `#D9D9D9`. Body rows: `#FFFFFF` / `#E8E8E8`. Borders: `#4B5563`.
- Two-column tables are equal width. Bold the After column only in Before/After tables.
- Practice boxes: `#EAF4FF` with a `#2E74B5` left bar.
- Source Code paragraphs: `#F2F2F2` (Gray-5%).

### Consequences

- SRE, Platform Engineering, and later series Word files start from this style.
- Changing these values requires an explicit series-level publication revision.

## Decision 003 — First published edition of every book is v1.0

- **Status:** Accepted
- **Date:** 2026-08-16
- **Applies from:** *Practical DevOps Engineering*, *Practical DevSecOps Engineering*, and every later series book

### Context

The published Word and PDF files for DevOps and DevSecOps are labeled v1.0. The series should not treat DevOps as v1.1 in reader-facing files, and later books should not start at a different first-edition number.

### Decision

The first published edition of every Practical Engineering book is **v1.0**.

- Title page: `Version 1.0 — <publication date>`.
- Release files: `practical-<book>-engineering-v1.0.docx` and `.pdf`.
- SRE, Platform Engineering, and later books also publish their first edition as v1.0.
- Do not label a first edition `v1.1`.

Companion-lab snapshot tags and inherited fixture paths may keep historical names, including `v1.1-chapter-*` and `inherited/devops-v1.1/`. Those are lab identifiers, not the published book version.

### Consequences

- DevOps and DevSecOps ship as v1.0.
- Future first editions start at v1.0.
- A later corrected reprint uses a new version only after an explicit series revision.

## Decision 004 — Practical SRE is the planned fourth book and inherits three lab baselines

- **Status:** Accepted
- **Date:** 2026-08-16
- **Applies from:** *Practical SRE Engineering*, after *Practical Platform Engineering* is published

### Context

DevOps, DevSecOps, and Platform all carve out portfolio SLOs, error-budget governance, on-call systems, regional-loss architecture, recurring game days, and reliability learning as SRE territory. Platform Chapter 15 hands off to that book. Extending the checksum-fixture pattern is cheap before Platform freezes and expensive after.

### Decision

*Practical SRE Engineering* is the planned fourth book in the series. It is not defensive scoping with no sequel.

When that book is planned, its companion lab inherits **minimal, checksum-identified interfaces** from all three predecessors:

```text
inherited/devops-v1.1/
inherited/devsecops-v1.0/
inherited/platform-v1.0/
```

It does not copy those working trees or read them at runtime. It does not reteach DevOps delivery, DevSecOps compromise recovery, or Platform product/tenancy/fleet work.

### Consequences

- Platform planning may say "handoff to SRE" as a real sequel, not a hedge.
- SRE first edition is v1.0 (Decision 003).
- The drafting gate passed: Platform's plan was frozen, SRE had a reviewed planning set, and *Practical SRE Engineering* v1.0 is now frozen. Do not start a fifth book from this decision.

## Next-book planning sequence

The four-book series recorded in Decisions 003 and 004 is frozen:

| Book | Edition | Status |
|---|---|---|
| *Practical DevOps Engineering* | v1.0 | Frozen manuscript and companion-lab tags |
| *Practical DevSecOps Engineering* | v1.0 | Frozen manuscript and companion-lab tags |
| *Practical Platform Engineering* | v1.0 | Frozen manuscript and companion-lab tags |
| *Practical SRE Engineering* | v1.0 | Frozen manuscript and companion-lab tags |

See each book's `RELEASE-MANIFEST.md` for SHA-256 inventory and lab tag identity.

There is no fifth series book in Decision 004. A later book would need a new series decision, its own planning set, and checksum-identified inheritance from the books it consumes.

## Decision 005 — Boutique Production Series is a separate series, not a fifth Northwind book

- **Status:** Accepted
- **Date:** 2026-08-18
- **Applies to:** `boutique-production/gitops/`, `boutique-production/gke-sre/`, `boutique-production/aks-devsecops/`

### Context

The Northwind Practical Engineering books are frozen (Decisions 003–004). The author's GitOps, SRE, and DevSecOps repositories were not the system those books teach. Readers need practical titles whose examples come from those repositories and cover every topic they contain.

### Decision

A **Boutique Production Series** exists beside the Northwind series. It does not inherit Northwind labs, does not reteach Northwind chapters as new work, and does not mutate frozen manuscripts.

Authority: `boutique-production/BOUTIQUE-SERIES.md` and `boutique-production/BOUTIQUE-EDITORIAL-CONVENTIONS.md`.

| Book | Manuscript | Source repository |
| --- | --- | --- |
| *Practical GitOps on Amazon EKS* | `boutique-production/gitops/` | `boutique-eks-gitops` |
| *Practical SRE on Google Kubernetes Engine* | `boutique-production/gke-sre/` | `boutique-gke-sre` |
| *Practical DevSecOps on Azure Kubernetes Service* | `boutique-production/aks-devsecops/` | `boutique-aks-devsecops` |

The system under study is the named repository. Practice is file-backed. Lived pilots were torn down; scaffolds stay labeled scaffold. First edition of each title is v1.0 (Decision 003). Word style remains Decision 002 if later rendered.

### Consequences

- Decision 004 still forbids a fifth Northwind book from that decision.
- These three titles are not Northwind sequels.
- IaC multi-environment AWS/Azure repositories are out of this decision. A later IaC book needs its own plan.

## New-chat bootstrap

Use this instruction when continuing *Practical SRE Engineering* from `books/practical-engineering/`:

> Continue *Practical SRE Engineering*. Manuscript v1.0 and companion-lab tags are frozen. See `sre/FROZEN.md` and `sre/RELEASE-MANIFEST.md`. Read `SERIES-DECISIONS.md`, `SERIES-PUBLICATION-STYLE.md`, `sre/FROZEN.md`, `sre/BOOK-PLAN.md`, `sre/CHAPTER-MAP.md`, `sre/LAB-PLAN.md`, and `sre/EDITORIAL-CONVENTIONS.md` first. Preserve series conventions. Apply Decision 001 (concept-led teaching), Decision 002 (shared Word style), Decision 003 (first edition is v1.0), and Decision 004 (three inherited lab baselines). Do not mutate the published DevOps, DevSecOps, or Platform v1.0 manuscripts or labs. Do not retag the SRE companion lab or change frozen promise, boundaries, chapter order, or inherited-baseline strategy without a new version. Future corrections require a new manuscript or lab version.
