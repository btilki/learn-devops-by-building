#!/usr/bin/env python3
from __future__ import annotations

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
BOOK = BOOKS / "platform"
WORK = BOOKS / "build/docx"
REFERENCE = WORK / "reference.docx"
MASTER = WORK / "book.md"
RAW = WORK / "practical-platform-engineering-v1.0.raw.docx"
OUT = BOOKS / "releases/practical-platform-engineering-v1.0.docx"

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
    "01-define-the-platform-as-a-product.md",
    "02-decide-which-capabilities-become-platform-products.md",
    "03-model-tenants-teams-and-isolation-boundaries.md",
    "04-publish-a-software-catalog-and-ownership-map.md",
    "05-build-a-paved-road-teams-can-leave.md",
    "06-offer-self-service-environments-without-sharing-blast-radius.md",
    "07-abstract-infrastructure-behind-reviewable-contracts.md",
    "08-operate-a-shared-control-plane-as-a-product.md",
    "09-enforce-guardrails-without-a-golden-cage.md",
    "10-measure-developer-experience-without-vanity-metrics.md",
    "11-allocate-quota-cost-and-capacity-across-tenants.md",
    "12-run-fleet-lifecycle-onboard-upgrade-deprecate.md",
    "13-support-escalate-and-change-the-platform-safely.md",
    "14-recover-a-control-plane-failure-without-taking-tenants-with-it.md",
    "15-conclusion.md",
    "GLOSSARY.md",
    "REFERENCES.md",
]

CHAPTER_NUMBERS: dict[str, int | None] = {
    "00-how-to-use-this-book.md": 0,
    "01-define-the-platform-as-a-product.md": 1,
    "02-decide-which-capabilities-become-platform-products.md": 2,
    "03-model-tenants-teams-and-isolation-boundaries.md": 3,
    "04-publish-a-software-catalog-and-ownership-map.md": 4,
    "05-build-a-paved-road-teams-can-leave.md": 5,
    "06-offer-self-service-environments-without-sharing-blast-radius.md": 6,
    "07-abstract-infrastructure-behind-reviewable-contracts.md": 7,
    "08-operate-a-shared-control-plane-as-a-product.md": 8,
    "09-enforce-guardrails-without-a-golden-cage.md": 9,
    "10-measure-developer-experience-without-vanity-metrics.md": 10,
    "11-allocate-quota-cost-and-capacity-across-tenants.md": 11,
    "12-run-fleet-lifecycle-onboard-upgrade-deprecate.md": 12,
    "13-support-escalate-and-change-the-platform-safely.md": 13,
    "14-recover-a-control-plane-failure-without-taking-tenants-with-it.md": 14,
    "15-conclusion.md": 15,
    "GLOSSARY.md": None,
    "REFERENCES.md": None,
}

BOOKMARKS: dict[str, str] = {
    "00-how-to-use-this-book.md": "ch-00",
    "01-define-the-platform-as-a-product.md": "ch-01",
    "02-decide-which-capabilities-become-platform-products.md": "ch-02",
    "03-model-tenants-teams-and-isolation-boundaries.md": "ch-03",
    "04-publish-a-software-catalog-and-ownership-map.md": "ch-04",
    "05-build-a-paved-road-teams-can-leave.md": "ch-05",
    "06-offer-self-service-environments-without-sharing-blast-radius.md": "ch-06",
    "07-abstract-infrastructure-behind-reviewable-contracts.md": "ch-07",
    "08-operate-a-shared-control-plane-as-a-product.md": "ch-08",
    "09-enforce-guardrails-without-a-golden-cage.md": "ch-09",
    "10-measure-developer-experience-without-vanity-metrics.md": "ch-10",
    "11-allocate-quota-cost-and-capacity-across-tenants.md": "ch-11",
    "12-run-fleet-lifecycle-onboard-upgrade-deprecate.md": "ch-12",
    "13-support-escalate-and-change-the-platform-safely.md": "ch-13",
    "14-recover-a-control-plane-failure-without-taking-tenants-with-it.md": "ch-14",
    "15-conclusion.md": "ch-15",
    "GLOSSARY.md": "glossary",
    "REFERENCES.md": "references",
}

TITLE = "Practical Platform Engineering"
SUBTITLE = "From product and tenancy to paved roads, fleet, and isolated recovery"
DATE_LINE = f"Version {BOOK_VERSION} — 16 August 2026"

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
    bookmark = BOOKMARKS[filename]
    return f"# {heading} {{#{bookmark}}}\n{remainder}"


def create_master() -> None:
    toc_lines = []
    for filename in FILES:
        number = CHAPTER_NUMBERS[filename]
        if filename == "00-how-to-use-this-book.md" or number == 0:
            continue
        title = (BOOK / filename).read_text(encoding="utf-8").split("\n", 1)[0][2:].strip()
        bookmark = BOOKMARKS[filename]
        if number is None:
            toc_lines.append(f"[{title}](#{bookmark})")
        else:
            toc_lines.append(f"[{number}. {title}](#{bookmark})")

    front = f"""---
title: {TITLE}
subtitle: {SUBTITLE}
author: {AUTHOR}
date: {DATE_LINE}
lang: en-US
---

```{{=openxml}}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# Contents

{chr(10).join(f"{line}{chr(10)}" for line in toc_lines)}

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
            "--from=markdown+raw_attribute+header_attributes",
            "--to=docx",
            f"--reference-doc={REFERENCE}",
            f"--output={RAW}",
        ],
        check=True,
    )


def wrap_heading_bookmarks(doc) -> None:
    """Wrap Heading 1 text with its bookmark instead of an empty point before the title."""
    wanted = set(BOOKMARKS.values())
    body = doc.element.body
    children = list(body)
    heading_indexes = []
    for index, child in enumerate(children):
        if child.tag != qn("w:p"):
            continue
        p_style = child.find(qn("w:pPr"))
        if p_style is None:
            continue
        style = p_style.find(qn("w:pStyle"))
        if style is not None and style.get(qn("w:val")) in {"Heading1", "1"}:
            heading_indexes.append(index)

    for heading_index in heading_indexes:
        paragraph = children[heading_index]
        starts: list = []
        scan = heading_index - 1
        while scan >= 0:
            sibling = children[scan]
            if sibling.tag == qn("w:bookmarkStart"):
                name = sibling.get(qn("w:name"), "")
                if name in wanted or name.startswith("_Toc") or name.startswith("ch-"):
                    starts.insert(0, sibling)
                    scan -= 1
                    continue
            break
        if not starts:
            existing = [
                child
                for child in paragraph
                if child.tag == qn("w:bookmarkStart") and child.get(qn("w:name"), "") in wanted
            ]
            if existing:
                _move_bookmarks_around_runs(paragraph, existing)
            continue
        ids = [item.get(qn("w:id")) for item in starts]
        ends = []
        for sibling in children[heading_index + 1 :]:
            if sibling.tag == qn("w:bookmarkEnd") and sibling.get(qn("w:id")) in ids:
                ends.append(sibling)
            elif sibling.tag == qn("w:p"):
                break
        for item in starts + ends:
            parent = item.getparent()
            if parent is not None:
                parent.remove(item)
        _insert_bookmarks_around_runs(paragraph, starts, ids)


def _move_bookmarks_around_runs(paragraph, starts: list) -> None:
    ids = [item.get(qn("w:id")) for item in starts]
    ends = [
        child
        for child in list(paragraph)
        if child.tag == qn("w:bookmarkEnd") and child.get(qn("w:id")) in ids
    ]
    for item in starts + ends:
        paragraph.remove(item)
    _insert_bookmarks_around_runs(paragraph, starts, ids)


def _insert_bookmarks_around_runs(paragraph, starts: list, ids: list) -> None:
    p_pr = paragraph.find(qn("w:pPr"))
    insert_at = 1 if p_pr is not None else 0
    for offset, start in enumerate(starts):
        paragraph.insert(insert_at + offset, start)
    for bookmark_id in ids:
        end = OxmlElement("w:bookmarkEnd")
        end.set(qn("w:id"), bookmark_id)
        paragraph.append(end)


def finalize() -> None:
    doc = Document(RAW)
    wrap_heading_bookmarks(doc)
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
    props.title = TITLE
    props.subject = SUBTITLE
    props.author = AUTHOR
    props.keywords = "Platform Engineering, paved road, tenancy, control plane, fleet, recovery"
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
