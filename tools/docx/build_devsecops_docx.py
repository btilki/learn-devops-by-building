#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

TOOLS = Path(__file__).resolve().parent
BOOKS = TOOLS.parents[1]
BOOK = BOOKS / "devsecops"
WORK = BOOKS / "build/docx"
REFERENCE = WORK / "reference.docx"
MASTER = WORK / "book.md"
RAW = WORK / "practical-devsecops-engineering-v1.0.raw.docx"
OUT = BOOKS / "releases/practical-devsecops-engineering-v1.0.docx"

sys.path.insert(0, str(TOOLS))
from series_style import (
    AUTHOR,
    BOOK_VERSION,
    CODE_FILL,
    PRACTICE_BAR,
    PRACTICE_FILL,
    TABLE_BODY_STRIPE,
    TABLE_BODY_WHITE,
    TABLE_BORDER,
    TABLE_BORDER_SIZE,
    TABLE_HEADER_FILL,
    THREE_COLUMN_WEIGHTS,
    TWO_COLUMN_WEIGHTS,
    apply_heading_fonts,
    pin_theme_latin,
    set_font,
    shade_source_code_paragraphs,
)
from table_geometry import apply_table_geometry, column_widths_from_weights

FILES = [
    "00-how-to-use-this-book.md",
    "01-define-what-security-must-protect.md",
    "02-model-threats-across-trust-boundaries.md",
    "03-turn-risk-into-owned-control-decisions.md",
    "04-make-human-and-automation-access-attributable.md",
    "05-govern-delegation-and-privileged-operations.md",
    "06-establish-trust-in-source-and-dependencies.md",
    "07-enforce-a-verifiable-build-and-release-chain.md",
    "08-prioritize-vulnerabilities-by-exploitability-and-harm.md",
    "09-govern-secrets-through-their-complete-lifecycle.md",
    "10-protect-data-according-to-its-use-and-sensitivity.md",
    "11-enforce-security-policy-without-hiding-exceptions.md",
    "12-constrain-workloads-and-detect-runtime-abuse.md",
    "13-build-security-evidence-and-actionable-detections.md",
    "14-investigate-and-contain-a-production-compromise.md",
    "15-eradicate-persistence-and-restore-trust.md",
    "16-turn-operational-evidence-into-sustainable-governance.md",
    "17-a-defensible-production-security-system.md",
    "GLOSSARY.md",
    "REFERENCES.md",
]

# Display numbers used in the DOCX heading and running header. None keeps
# back-matter titles unnumbered. Manuscript sources stay unnumbered.
CHAPTER_NUMBERS: dict[str, int | None] = {
    "00-how-to-use-this-book.md": 0,
    "01-define-what-security-must-protect.md": 1,
    "02-model-threats-across-trust-boundaries.md": 2,
    "03-turn-risk-into-owned-control-decisions.md": 3,
    "04-make-human-and-automation-access-attributable.md": 4,
    "05-govern-delegation-and-privileged-operations.md": 5,
    "06-establish-trust-in-source-and-dependencies.md": 6,
    "07-enforce-a-verifiable-build-and-release-chain.md": 7,
    "08-prioritize-vulnerabilities-by-exploitability-and-harm.md": 8,
    "09-govern-secrets-through-their-complete-lifecycle.md": 9,
    "10-protect-data-according-to-its-use-and-sensitivity.md": 10,
    "11-enforce-security-policy-without-hiding-exceptions.md": 11,
    "12-constrain-workloads-and-detect-runtime-abuse.md": 12,
    "13-build-security-evidence-and-actionable-detections.md": 13,
    "14-investigate-and-contain-a-production-compromise.md": 14,
    "15-eradicate-persistence-and-restore-trust.md": 15,
    "16-turn-operational-evidence-into-sustainable-governance.md": 16,
    "17-a-defensible-production-security-system.md": 17,
    "GLOSSARY.md": None,
    "REFERENCES.md": None,
}

NAVY = RGBColor(0x10, 0x2A, 0x43)
BLUE = RGBColor(0x2E, 0x74, 0xB5)
CYAN = RGBColor(0x00, 0x8B, 0x8B)
INK = RGBColor(0x24, 0x3B, 0x53)
MUTED = RGBColor(0x62, 0x7D, 0x98)


def set_spacing(style, before: float, after: float, line: float) -> None:
    pf = style.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line


def add_field(paragraph, instruction: str, fallback: str, size_half_points: str = "16") -> None:
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), instruction)
    result_run = OxmlElement("w:r")
    result_props = OxmlElement("w:rPr")
    result_fonts = OxmlElement("w:rFonts")
    result_fonts.set(qn("w:ascii"), "Arial")
    result_fonts.set(qn("w:hAnsi"), "Arial")
    result_props.append(result_fonts)
    result_size = OxmlElement("w:sz")
    result_size.set(qn("w:val"), size_half_points)
    result_props.append(result_size)
    result_color = OxmlElement("w:color")
    result_color.set(qn("w:val"), "627D98")
    result_props.append(result_color)
    result_run.append(result_props)
    result_text = OxmlElement("w:t")
    result_text.text = fallback
    result_run.append(result_text)
    fld.append(result_run)
    paragraph._p.append(fld)


def shade_cell(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)


def set_cell_borders(cell, color: str = TABLE_BORDER, size: str = TABLE_BORDER_SIZE) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.find(qn("w:tcBorders"))
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = qn(f"w:{edge}")
        border = borders.find(tag)
        if border is None:
            border = OxmlElement(f"w:{edge}")
            borders.append(border)
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), size)
        border.set(qn("w:color"), color)


def set_repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def header_cells(table) -> list[str]:
    return [cell.text.strip() for cell in table.rows[0].cells]


def style_reference(path: Path) -> None:
    doc = Document(path)
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)
    section.different_first_page_header_footer = True

    normal = doc.styles["Normal"]
    set_font(normal, "Arial", 10.5, INK)
    set_spacing(normal, 0, 6, 1.2)

    title = doc.styles["Title"]
    set_font(title, "Arial", 30, NAVY, bold=True)
    set_spacing(title, 132, 8, 1.0)
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle = doc.styles["Subtitle"]
    set_font(subtitle, "Arial", 14, MUTED)
    set_spacing(subtitle, 0, 14, 1.15)
    subtitle.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    try:
        author = doc.styles["Author"]
    except KeyError:
        author = doc.styles.add_style("Author", WD_STYLE_TYPE.PARAGRAPH)
    set_font(author, "Arial", 14, NAVY, bold=True)
    set_spacing(author, 6, 10, 1.15)
    author.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    apply_heading_fonts(doc)
    pin_theme_latin(doc)
    doc.styles["Heading 1"].paragraph_format.page_break_before = True

    for name in ("List Bullet", "List Number"):
        try:
            style = doc.styles[name]
        except KeyError:
            style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        set_font(style, "Arial", 10.5, INK)
        set_spacing(style, 0, 4, 1.2)
        style.paragraph_format.left_indent = Inches(0.375)
        style.paragraph_format.first_line_indent = Inches(-0.188)

    if "Source Code" in doc.styles:
        code = doc.styles["Source Code"]
    else:
        code = doc.styles.add_style("Source Code", WD_STYLE_TYPE.PARAGRAPH)
    set_font(code, "Menlo", 8.5, INK)
    set_spacing(code, 4, 7, 1.0)
    code.paragraph_format.left_indent = Inches(0.12)
    code.paragraph_format.right_indent = Inches(0.12)
    code.paragraph_format.keep_together = True
    code_ppr = code.element.get_or_add_pPr()
    code_shd = OxmlElement("w:shd")
    code_shd.set(qn("w:val"), "clear")
    code_shd.set(qn("w:color"), "auto")
    code_shd.set(qn("w:fill"), CODE_FILL)
    code_ppr.append(code_shd)

    if "Block Text" in doc.styles:
        quote = doc.styles["Block Text"]
    else:
        quote = doc.styles.add_style("Block Text", WD_STYLE_TYPE.PARAGRAPH)
    set_font(quote, "Arial", 10, NAVY)
    set_spacing(quote, 5, 7, 1.15)
    quote.paragraph_format.left_indent = Inches(0.2)
    quote.paragraph_format.right_indent = Inches(0.1)

    header = section.header.paragraphs[0]
    header.text = ""
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_field(header, 'STYLEREF "Heading 1"', "Chapter", "12")

    footer = section.footer.paragraphs[0]
    footer.text = ""
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(footer, "PAGE", "1")
    doc.save(path)


def create_reference() -> None:
    data = subprocess.check_output(["pandoc", "--print-default-data-file", "reference.docx"])
    REFERENCE.write_bytes(data)
    style_reference(REFERENCE)


def numbered_chapter(filename: str, text: str) -> str:
    first_line, remainder = text.split("\n", 1)
    if not first_line.startswith("# "):
        raise ValueError(f"{filename} does not start with a heading")
    title = first_line[2:].strip()
    number = CHAPTER_NUMBERS[filename]
    heading = title if number is None else f"{number}. {title}"
    return f"# {heading}\n{remainder}"


def toc_anchor(heading: str) -> str:
    slug = heading.lower()
    slug = slug.replace("—", " ").replace("–", " ")
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    return re.sub(r"\s+", "-", slug.strip())


def create_master() -> None:
    toc_lines = []
    for filename in FILES:
        number = CHAPTER_NUMBERS[filename]
        title = (BOOK / filename).read_text(encoding="utf-8").split("\n", 1)[0][2:].strip()
        heading = title if number is None else f"{number}. {title}"
        if filename == "00-how-to-use-this-book.md" or number == 0:
            continue
        if number is None:
            toc_lines.append(f"[{title}](#{toc_anchor(heading)})")
        else:
            toc_lines.append(f"{number}. [{title}](#{toc_anchor(heading)})")

    front = f"""---
title: Practical DevSecOps Engineering
subtitle: Production security from assets and authority to restored trust
author: {AUTHOR}
date: Version {BOOK_VERSION} — 15 August 2026
lang: en-US
---

```{{=openxml}}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# Contents

{chr(10).join(toc_lines)}

"""
    parts = [front]
    for filename in FILES:
        parts.append(numbered_chapter(filename, (BOOK / filename).read_text(encoding="utf-8")))
        parts.append("\n")
    MASTER.write_text("\n".join(parts), encoding="utf-8")


def run_pandoc() -> None:
    subprocess.run(
        [
            "pandoc",
            str(MASTER),
            "--from=gfm+raw_attribute",
            "--to=docx",
            f"--reference-doc={REFERENCE}",
            f"--output={RAW}",
        ],
        check=True,
    )


def finalize() -> None:
    doc = Document(RAW)
    apply_heading_fonts(doc)
    pin_theme_latin(doc)
    for section in doc.sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)
        section.top_margin = Inches(1)
        section.right_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.header_distance = Inches(0.492)
        section.footer_distance = Inches(0.492)
        section.different_first_page_header_footer = True

    for table in doc.tables:
        columns = len(table.columns)
        headers = header_cells(table)
        before_after = headers[:2] == ["Before", "After"]
        if columns == 2:
            weights = TWO_COLUMN_WEIGHTS
        elif columns == 3:
            weights = THREE_COLUMN_WEIGHTS
        else:
            weights = [1] * columns
        widths = column_widths_from_weights(weights, 9360)
        apply_table_geometry(
            table,
            widths,
            table_width_dxa=9360,
            indent_dxa=150,
            cell_margins_dxa={"top": 130, "bottom": 130, "start": 150, "end": 150},
        )
        set_repeat_header(table.rows[0])
        for row_index, row in enumerate(table.rows):
            for column_index, cell in enumerate(row.cells):
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                if row_index == 0:
                    shade_cell(cell, TABLE_HEADER_FILL)
                elif row_index % 2 == 0:
                    shade_cell(cell, TABLE_BODY_STRIPE)
                else:
                    shade_cell(cell, TABLE_BODY_WHITE)
                set_cell_borders(cell)
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.space_before = Pt(0)
                    paragraph.paragraph_format.space_after = Pt(0)
                    paragraph.paragraph_format.line_spacing = 1.08
                    if row_index == 0:
                        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in paragraph.runs:
                        style_name = run.style.name if run.style is not None else ""
                        run.font.name = "Menlo" if "Verbatim" in style_name or "Code" in style_name else "Arial"
                        run.font.size = Pt(9.5)
                        if row_index == 0:
                            run.font.bold = True
                            run.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
                        elif before_after and column_index == 1:
                            run.font.bold = True

    shade_source_code_paragraphs(doc)

    for paragraph in doc.paragraphs:
        if paragraph.style.name == "Block Text":
            ppr = paragraph._p.get_or_add_pPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:fill"), PRACTICE_FILL)
            ppr.append(shd)
            borders = OxmlElement("w:pBdr")
            left = OxmlElement("w:left")
            left.set(qn("w:val"), "single")
            left.set(qn("w:sz"), "18")
            left.set(qn("w:space"), "8")
            left.set(qn("w:color"), PRACTICE_BAR)
            borders.append(left)
            ppr.append(borders)

    props = doc.core_properties
    props.title = "Practical DevSecOps Engineering"
    props.subject = "Production security from assets and authority to restored trust"
    props.author = AUTHOR
    props.keywords = "DevSecOps, production security, identity, supply chain, detection, recovery"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    create_reference()
    create_master()
    run_pandoc()
    finalize()
    print(OUT)


if __name__ == "__main__":
    main()
