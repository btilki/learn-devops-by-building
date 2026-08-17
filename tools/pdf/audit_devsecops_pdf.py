#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from pypdf import PdfReader

pdf_path = Path(sys.argv[1])
out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

titles = [
    "How to Use This Book",
    "Define What Security Must Protect",
    "Model Threats Across Trust Boundaries",
    "Turn Risk into Owned Control Decisions",
    "Make Human and Automation Access Attributable",
    "Govern Delegation and Privileged Operations",
    "Establish Trust in Source and Dependencies",
    "Enforce a Verifiable Build and Release Chain",
    "Prioritize Vulnerabilities by Exploitability and Harm",
    "Govern Secrets Through Their Complete Lifecycle",
    "Protect Data According to Its Use and Sensitivity",
    "Enforce Security Policy Without Hiding Exceptions",
    "Constrain Workloads and Detect Runtime Abuse",
    "Build Security Evidence and Actionable Detections",
    "Investigate and Contain a Production Compromise",
    "Eradicate Persistence and Restore Trust",
    "Turn Operational Evidence into Sustainable Governance",
    "A Defensible Production Security System",
    "Glossary and Abbreviations",
    "References",
]
markers = [
    "make chapter-01-baseline",
    "make chapter-07-checkpoint",
    "make chapter-14-contain",
    "make chapter-16-baseline",
]

reader = PdfReader(pdf_path)
page_count = len(reader.pages)
text = "\n".join(page.extract_text() or "" for page in reader.pages)
meta = reader.metadata
page = reader.pages[0]
width = float(page.mediabox.width)
height = float(page.mediabox.height)

checks = {
    "pdf_magic": pdf_path.read_bytes()[:5] == b"%PDF-",
    "title_metadata": bool(meta and meta.title == "Practical DevSecOps Engineering"),
    "page_count_at_least_100": page_count >= 100,
    "six_by_nine_page": abs(width - 432) < 2 and abs(height - 648) < 2,
    "chapter_titles_present": all(title in text for title in titles),
    "code_markers_present": all(marker in text for marker in markers),
}

report = {
    "release": "Practical DevSecOps Engineering v1.0",
    "files": {"pdf": str(pdf_path)},
    "summary": {"pdf_pages": page_count, "page_size": [width, height]},
    "checks": checks,
    "passed": all(checks.values()),
}
payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
if out_path is not None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(payload, encoding="utf-8")
print(payload, end="")
sys.exit(0 if report["passed"] else 1)
