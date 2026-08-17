# Practical Engineering Series — Publication Style

**Status:** Active  
**Effective date:** 2026-08-16  
**Applies to:** Every book in the Practical Engineering series  
**Implementation:** `tools/docx/series_style.py`

The rendered DOCX is the publication reference. PDF, when produced, must match these colors. Markdown previews are not the acceptance artifact.

## Author

- Writer name: **Birol Tilki**
- Place the name on the title page under the subtitle, before the version line.
- Set the Word document author property to the same name.

## Version

- The first published edition of every Practical Engineering book is **v1.0**.
- Title line: `Version 1.0 — <publication date>`.
- Filenames: `practical-<book>-engineering-v1.0.docx` and `practical-<book>-engineering-v1.0.pdf`.
- Do not label a first edition `v1.1`. Later reprints or corrected editions may increment only after an explicit series revision.
- Companion-lab snapshot tags may keep historical names independently of the published book version.

## Contents

- Omit **How to Use This Book** from Contents. Keep the chapter in the book.
- Contents list numbers must match chapter numbers: `1.` opens chapter 01/1, `2.` opens chapter 02/2.
- Put the number inside the hyperlink text. Do not rely on Word automatic list numbering.
- Wrap each target heading's text with the bookmark. Do not use an empty point bookmark before the title.
- Conclusion, glossary, and references may follow without chapter numbers.

## Running header

- Show the numbered chapter title only, for example `1. Define What Security Must Protect`.
- Do not put the book name in the header.

## Table style

### Visual treatment

- Header cells: `#D9D9D9`, bold, dark text, centered.
- Body rows: alternate `#FFFFFF` and `#E8E8E8`. Do not use blue-gray row fills.
- Borders: `#4B5563` on every cell edge.
- Two-column tables use equal widths. Three-column tables use 2-1-1 weights.
- Repeat the header row on the next page.
- Keep cell padding readable. Do not clip text or run past the page margin.

### Semantic treatment

- Use columns that fit the information.
- Use `Before` / `After` only for real state changes. Bold only the After column in those tables.
- Keep code, paths, and identifiers in the inline-code style inside cells.

## Practice boxes

- Fill: `#EAF4FF`
- Left bar: `#2E74B5`

## Code blocks

- Apply to `Source Code` paragraphs (monospace / Consolas / Menlo).
- Fill: `#F2F2F2` (Word Gray-5%).
- Do not use the practice-box blue for code.

## Existing and future books

- *Practical DevOps Engineering* v1.0 and *Practical DevSecOps Engineering* v1.0 Word files already follow this revision.
- Future SRE, Platform Engineering, and other series books publish their first edition as v1.0, import `tools/docx/series_style.py`, and apply the same treatment.
- Do not replace these values unless a series-level publication revision is explicitly approved.
