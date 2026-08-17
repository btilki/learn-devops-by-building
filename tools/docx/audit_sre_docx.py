#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

docx_path = Path(sys.argv[1])
out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

chapter_titles = [
    "0. How to Use This Book",
    "1. Define What Reliability Must Protect",
    "2. Choose Indicators Users Can Feel",
    "3. Set SLOs and Error Budgets Across the Portfolio",
    "4. Govern Change with Error-Budget Policy",
    "5. Page on Burn Rate, Not on Every Symptom",
    "6. Design On-Call as a System",
    "7. Measure and Bound Toil Without Hiding the Work",
    "8. Put Dependencies Inside the Reliability Contract",
    "9. Degrade Deliberately Before Failure Cascades",
    "10. Command Incidents Across Services and Tenants",
    "11. Turn Incidents into a Reliability Learning Program",
    "12. Design for the Loss of a Region",
    "13. Run Game Days as a Recurring Program",
    "14. Fail Over a Region Without Taking the Portfolio Down",
    "15. Conclusion — A Governed Reliability Portfolio",
    "Glossary and Abbreviations",
    "References",
]

core_titles = chapter_titles[1:16]
code_markers = [
    "make chapter-01-baseline",
    "make chapter-07-checkpoint",
    "make chapter-14-checkpoint",
]

doc = Document(docx_path)
docx_text = "\n".join(p.text for p in doc.paragraphs)
heading1 = [p.text.strip() for p in doc.paragraphs if p.style.name == "Heading 1"]

with zipfile.ZipFile(docx_path) as archive:
    header_xml = "\n".join(
        archive.read(name).decode("utf-8")
        for name in archive.namelist()
        if re.fullmatch(r"word/header\d+\.xml", name)
    )
    footer_xml = "\n".join(
        archive.read(name).decode("utf-8")
        for name in archive.namelist()
        if re.fullmatch(r"word/footer\d+\.xml", name)
    )
    styles_xml = archive.read("word/styles.xml").decode("utf-8")
    document_xml = archive.read("word/document.xml").decode("utf-8")
    core_xml = archive.read("docProps/core.xml").decode("utf-8")
    external_links = sum(
        1
        for name in archive.namelist()
        if name.endswith(".rels")
        for _ in re.findall(r'TargetMode="External"', archive.read(name).decode("utf-8"))
    )

code_paragraphs = sum(1 for p in doc.paragraphs if p.style.name == "Source Code")
section = doc.sections[0]
letter = (
    abs(section.page_width.inches - 8.5) < 0.02
    and abs(section.page_height.inches - 11) < 0.02
)

present = [title for title in chapter_titles if title in docx_text]
heading_order = [title for title in chapter_titles if title in heading1]
contents_heading_index = heading1.index("Contents") if "Contents" in heading1 else -1
how_to_heading_index = next(
    (i for i, title in enumerate(heading1) if title.endswith("How to Use This Book")),
    -1,
)
toc_texts = []
seen_contents = False
for paragraph in doc.paragraphs:
    if paragraph.style.name == "Heading 1":
        if paragraph.text.strip() == "Contents":
            seen_contents = True
            continue
        if seen_contents:
            break
    elif seen_contents:
        toc_texts.append(paragraph.text.strip())


checks = {
    "all_chapter_titles_in_docx": present == chapter_titles,
    "heading_order_matches_contents": heading_order == chapter_titles,
    "core_chapters_present": all(title in docx_text for title in core_titles),
    "how_to_use_omitted_from_contents_heading": contents_heading_index == 0
    and how_to_heading_index == 1,
    "how_to_use_omitted_from_toc_links": not any(
        "How to Use This Book" in text for text in toc_texts
    ),
    "docx_external_links_absent": external_links == 0,
    "code_blocks_present_in_docx": code_paragraphs > 0,
    "code_markers_present": all(marker in docx_text for marker in code_markers),
    "tables_present_in_docx": len(doc.tables) > 0,
    "book_name_not_in_header": "Practical SRE Engineering" not in header_xml,
    "chapter_field_in_header": "STYLEREF" in header_xml and "Heading 1" in header_xml,
    "centered_page_field_present": "PAGE" in footer_xml and 'w:jc w:val="center"' in footer_xml,
    "letter_page_size": letter,
    "author_is_birol_tilki": "Birol Tilki" in core_xml,
    "table_header_fill_d9d9d9": "D9D9D9" in document_xml,
    "table_stripe_e8e8e8": "E8E8E8" in document_xml,
    "practice_fill_eaf4ff": "EAF4FF" in document_xml,
    "practice_bar_2e74b5": "2E74B5" in document_xml,
    "code_fill_f2f2f2": "F2F2F2" in document_xml or "F2F2F2" in styles_xml,
}

report = {
    "release": "Practical SRE Engineering v1.0",
    "files": {"docx": str(docx_path)},
    "summary": {
        "docx_tables": len(doc.tables),
        "docx_code_paragraphs": code_paragraphs,
        "docx_external_links": external_links,
        "heading1_count": len(heading1),
        "titles_found": present,
        "heading1": heading1,
    },
    "checks": checks,
    "passed": all(checks.values()),
}

text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
if out_path is not None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
print(text, end="")
sys.exit(0 if report["passed"] else 1)
