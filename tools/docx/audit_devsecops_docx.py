#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

from docx import Document

docx_path = Path(sys.argv[1])
out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

chapter_titles = [
    "0. How to Use This Book",
    "1. Define What Security Must Protect",
    "2. Model Threats Across Trust Boundaries",
    "3. Turn Risk into Owned Control Decisions",
    "4. Make Human and Automation Access Attributable",
    "5. Govern Delegation and Privileged Operations",
    "6. Establish Trust in Source and Dependencies",
    "7. Enforce a Verifiable Build and Release Chain",
    "8. Prioritize Vulnerabilities by Exploitability and Harm",
    "9. Govern Secrets Through Their Complete Lifecycle",
    "10. Protect Data According to Its Use and Sensitivity",
    "11. Enforce Security Policy Without Hiding Exceptions",
    "12. Constrain Workloads and Detect Runtime Abuse",
    "13. Build Security Evidence and Actionable Detections",
    "14. Investigate and Contain a Production Compromise",
    "15. Eradicate Persistence and Restore Trust",
    "16. Turn Operational Evidence into Sustainable Governance",
    "17. Conclusion — A Defensible Production Security System",
    "Glossary and Abbreviations",
    "References",
]

core_titles = chapter_titles[1:17]
code_markers = [
    "make chapter-01-baseline",
    "make chapter-07-checkpoint",
    "make chapter-14-contain",
    "make chapter-16-baseline",
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

checks = {
    "all_chapter_titles_in_docx": present == chapter_titles,
    "heading_order_matches_contents": heading_order == chapter_titles,
    "core_chapters_present": all(title in docx_text for title in core_titles),
    "docx_external_links_present": external_links > 0,
    "code_blocks_present_in_docx": code_paragraphs > 0,
    "code_markers_present": all(marker in docx_text for marker in code_markers),
    "tables_present_in_docx": len(doc.tables) > 0,
    "book_name_not_in_header": "Practical DevSecOps Engineering" not in header_xml,
    "chapter_field_in_header": "STYLEREF" in header_xml and "Heading 1" in header_xml,
    "centered_page_field_present": "PAGE" in footer_xml and 'w:jc w:val="center"' in footer_xml,
    "letter_page_size": letter,
}

report = {
    "release": "Practical DevSecOps Engineering v1.0",
    "files": {"docx": str(docx_path)},
    "summary": {
        "docx_tables": len(doc.tables),
        "docx_code_paragraphs": code_paragraphs,
        "docx_external_links": external_links,
        "heading1_count": len(heading1),
        "titles_found": present,
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
