"""Practical Engineering series DOCX visual constants.

Import these values from every book DOCX builder so future Word files
match the accepted DevOps and DevSecOps v1.0 treatment.
"""

from __future__ import annotations

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from lxml import etree

AUTHOR = "Birol Tilki"
BOOK_VERSION = "1.0"

NAVY = RGBColor(0x10, 0x2A, 0x43)
BLUE = RGBColor(0x2E, 0x74, 0xB5)
CYAN = RGBColor(0x00, 0x8B, 0x8B)

TABLE_HEADER_FILL = "D9D9D9"
TABLE_BODY_WHITE = "FFFFFF"
TABLE_BODY_STRIPE = "E8E8E8"
TABLE_BORDER = "4B5563"
TABLE_BORDER_SIZE = "6"

PRACTICE_FILL = "EAF4FF"
PRACTICE_BAR = "2E74B5"

CODE_FILL = "F2F2F2"

TWO_COLUMN_WEIGHTS = [1, 1]
THREE_COLUMN_WEIGHTS = [2, 1, 1]


def shade_fill(element_pr, fill: str) -> None:
    shd = element_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        element_pr.append(shd)
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)


def shade_source_code_paragraphs(doc) -> int:
    count = 0
    if "Source Code" in doc.styles:
        shade_fill(doc.styles["Source Code"].element.get_or_add_pPr(), CODE_FILL)
    for paragraph in doc.paragraphs:
        if paragraph.style.name != "Source Code":
            continue
        shade_fill(paragraph._p.get_or_add_pPr(), CODE_FILL)
        count += 1
    return count


def set_font(style, name: str, size: float, color: RGBColor, bold: bool = False, italic: bool = False) -> None:
    style.font.name = name
    style.font.size = Pt(size)
    style.font.color.rgb = color
    style.font.bold = bold
    style.font.italic = italic
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in list(rfonts.attrib):
        if attr.split("}")[-1].lower().endswith("theme"):
            del rfonts.attrib[attr]
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:eastAsia"), name)
    rfonts.set(qn("w:cs"), name)
    half_points = str(int(size * 2))
    for tag in ("w:sz", "w:szCs"):
        size_el = rpr.find(qn(tag))
        if size_el is None:
            size_el = OxmlElement(tag)
            rpr.append(size_el)
        size_el.set(qn("w:val"), half_points)


def apply_heading_fonts(doc) -> None:
    """Section titles are Arial 13; subsections are Arial 12. No theme fonts."""
    for name, size, color, before, after in (
        ("Heading 1", 16, NAVY, 18, 10),
        ("Heading 2", 13, BLUE, 14, 7),
        ("Heading 3", 12, CYAN, 10, 5),
        ("Heading 4", 11, NAVY, 8, 4),
    ):
        style = doc.styles[name]
        set_font(style, "Arial", size, color, bold=True)
        pf = style.paragraph_format
        pf.space_before = Pt(before)
        pf.space_after = Pt(after)
        pf.line_spacing = 1.1
        pf.keep_with_next = True


def pin_theme_latin(doc, name: str = "Arial") -> None:
    """Stop Word mapping heading theme fonts to Aptos Display."""
    drawingml = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    for rel in doc.part.rels.values():
        if "theme" not in rel.reltype:
            continue
        part = rel.target_part
        root = etree.fromstring(part.blob)
        for latin in root.iter(f"{drawingml}latin"):
            parent = latin.getparent()
            if parent is not None and parent.tag in {
                f"{drawingml}majorFont",
                f"{drawingml}minorFont",
            }:
                latin.set("typeface", name)
        part._blob = etree.tostring(
            root, xml_declaration=True, encoding="UTF-8", standalone=True
        )
