#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

TOOLS = Path(__file__).resolve().parent
BOOKS = TOOLS.parents[1]
BOOK = BOOKS / "devsecops"
WORK = BOOKS / "build/pdf"
PDF_OUT = BOOKS / "releases/practical-devsecops-engineering-v1.0.pdf"
COVER_OUT = WORK / "practical-devsecops-engineering-cover.png"

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

PAGE = (6 * inch, 9 * inch)
NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#1F6FEB")
CYAN = colors.HexColor("#00A6A6")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
PALE = colors.HexColor("#EAF4FF")
CODE_BG = colors.HexColor("#F3F6F9")
LINE = colors.HexColor("#BCCCDC")


def register_fonts() -> None:
    base = Path("/System/Library/Fonts/Supplemental")
    pdfmetrics.registerFont(TTFont("Georgia", base / "Georgia.ttf"))
    pdfmetrics.registerFont(TTFont("Georgia-Bold", base / "Georgia Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Georgia-Italic", base / "Georgia Italic.ttf"))
    pdfmetrics.registerFont(TTFont("Arial", base / "Arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", base / "Arial Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Italic", base / "Arial Italic.ttf"))
    pdfmetrics.registerFont(TTFont("Menlo", "/System/Library/Fonts/Menlo.ttc", subfontIndex=0))
    pdfmetrics.registerFontFamily(
        "Georgia", normal="Georgia", bold="Georgia-Bold", italic="Georgia-Italic"
    )
    pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")


def make_cover() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    width, height = 1600, 2560
    image = Image.new("RGB", (width, height), "#102A43")
    draw = ImageDraw.Draw(image)
    bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    regular = "/System/Library/Fonts/Supplemental/Arial.ttf"
    title = ImageFont.truetype(bold, 132)
    subtitle = ImageFont.truetype(regular, 54)
    edition = ImageFont.truetype(bold, 42)
    draw.rectangle((0, 0, 95, height), fill="#00A6A6")
    draw.rectangle((95, 1750, width, 1780), fill="#1F6FEB")
    y = 340
    for line in ("PRACTICAL", "DEVSECOPS", "ENGINEERING"):
        draw.text((190, y), line, font=title, fill="white")
        y += 165
    draw.multiline_text(
        (200, 1080),
        "Production security from assets\nand authority to restored trust",
        font=subtitle,
        fill="#D9EAF7",
        spacing=26,
    )
    draw.text((200, 1880), "MID-TO-ADVANCED • PRACTICE-FIRST", font=edition, fill="#7FDBFF")
    draw.text((200, 2180), "Northwind Commerce reference implementation", font=subtitle, fill="white")
    draw.text((200, 2310), "Version 1.0", font=edition, fill="#D9EAF7")
    image.save(COVER_OUT, quality=95)


def inline_markup(text: str) -> str:
    text = html.escape(text, quote=False)
    tokens: list[str] = []

    def hold(value: str) -> str:
        tokens.append(value)
        return f"@@TOKEN{len(tokens) - 1}@@"

    text = re.sub(
        r"`([^`]+)`",
        lambda match: hold(f'<font name="Menlo" size="7.4">{match.group(1)}</font>'),
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda match: hold(
            f'<link href="{html.escape(match.group(2), quote=True)}" color="#1F6FEB">'
            f"{match.group(1)}</link>"
        ),
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    for index, value in enumerate(tokens):
        text = text.replace(f"@@TOKEN{index}@@", value)
    return text


def styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontName="Georgia",
            fontSize=9.2,
            leading=13.2,
            textColor=INK,
            spaceAfter=5.5,
            allowWidows=0,
            allowOrphans=0,
        ),
        "h1": ParagraphStyle(
            "H1",
            fontName="Arial-Bold",
            fontSize=21,
            leading=25,
            textColor=NAVY,
            spaceAfter=12,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2",
            fontName="Arial-Bold",
            fontSize=14,
            leading=18,
            textColor=NAVY,
            spaceBefore=12,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3",
            fontName="Arial-Bold",
            fontSize=11,
            leading=14,
            textColor=CYAN,
            spaceBefore=9,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "h4": ParagraphStyle(
            "H4",
            fontName="Arial-Bold",
            fontSize=9.5,
            leading=12,
            textColor=INK,
            spaceBefore=7,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "quote": ParagraphStyle(
            "Quote",
            fontName="Arial",
            fontSize=8.8,
            leading=12.5,
            textColor=NAVY,
            leftIndent=10,
            rightIndent=8,
            borderPadding=(7, 8, 7, 11),
            backColor=PALE,
            spaceBefore=5,
            spaceAfter=7,
        ),
        "code": ParagraphStyle(
            "Code",
            fontName="Menlo",
            fontSize=6.7,
            leading=9.1,
            textColor=INK,
            leftIndent=6,
            rightIndent=6,
            borderColor=LINE,
            borderWidth=0.5,
            borderPadding=7,
            backColor=CODE_BG,
            spaceBefore=4,
            spaceAfter=7,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            fontName="Georgia",
            fontSize=9,
            leading=12.7,
            textColor=INK,
            leftIndent=3,
            spaceAfter=2,
        ),
        "table": ParagraphStyle(
            "TableCell", fontName="Arial", fontSize=6.9, leading=9.2, textColor=INK
        ),
        "table_head": ParagraphStyle(
            "TableHead", fontName="Arial-Bold", fontSize=7, leading=9.3, textColor=colors.white
        ),
        "toc": ParagraphStyle(
            "TOCHeading",
            fontName="Arial-Bold",
            fontSize=22,
            leading=26,
            textColor=NAVY,
            spaceAfter=16,
        ),
    }


def parse_table(lines: list[str], position: int, sheet: dict[str, ParagraphStyle]) -> tuple[Table, int]:
    rows: list[list[str]] = []
    while position < len(lines) and lines[position].strip().startswith("|"):
        cells = [cell.strip() for cell in lines[position].strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            rows.append(cells)
        position += 1
    width = PAGE[0] - 33 * mm
    columns = max(len(row) for row in rows)
    data = []
    for row_index, row in enumerate(rows):
        style = sheet["table_head"] if row_index == 0 else sheet["table"]
        padded = row + [""] * (columns - len(row))
        data.append([Paragraph(inline_markup(cell), style) for cell in padded])
    table = Table(data, colWidths=[width / columns] * columns, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
            ]
        )
    )
    return table, position


def markdown_story(path: Path, sheet: dict[str, ParagraphStyle]) -> list:
    lines = path.read_text(encoding="utf-8").splitlines()
    story: list = []
    paragraph: list[str] = []
    quote: list[str] = []
    in_code = False
    code: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), sheet["body"]))
            paragraph.clear()

    def flush_quote() -> None:
        if quote:
            value = "<br/>".join(inline_markup(item) for item in quote if item)
            story.append(Paragraph(value, sheet["quote"]))
            quote.clear()

    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            flush_quote()
            if in_code:
                story.append(
                    Preformatted(
                        "\n".join(code), sheet["code"], maxLineLength=88, splitChars=" /._-,:"
                    )
                )
                code.clear()
                in_code = False
            else:
                in_code = True
            index += 1
            continue
        if in_code:
            code.append(raw.replace("\t", "    "))
            index += 1
            continue
        if stripped.startswith(">"):
            flush_paragraph()
            quote.append(stripped[1:].strip())
            index += 1
            if index == len(lines) or not lines[index].strip().startswith(">"):
                flush_quote()
            continue
        flush_quote()
        if not stripped:
            flush_paragraph()
            index += 1
            continue
        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            story.append(Paragraph(inline_markup(heading.group(2)), sheet[f"h{level}"]))
            index += 1
            continue
        if stripped.startswith("|") and index + 1 < len(lines) and re.match(
            r"^\|?\s*:?-{3,}", lines[index + 1].strip()
        ):
            flush_paragraph()
            table, index = parse_table(lines, index, sheet)
            story.extend([table, Spacer(1, 6)])
            continue
        if re.match(r"^[-*]\s+", stripped):
            flush_paragraph()
            items = []
            while index < len(lines) and re.match(r"^[-*]\s+", lines[index].strip()):
                text = re.sub(r"^[-*]\s+", "", lines[index].strip())
                items.append(ListItem(Paragraph(inline_markup(text), sheet["bullet"]), leftIndent=10))
                index += 1
            story.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    start="circle",
                    leftIndent=17,
                    bulletFontName="Arial",
                    bulletFontSize=6,
                    spaceAfter=5,
                )
            )
            continue
        if re.match(r"^\d+\.\s+", stripped):
            flush_paragraph()
            items = []
            while index < len(lines) and re.match(r"^\d+\.\s+", lines[index].strip()):
                text = re.sub(r"^\d+\.\s+", "", lines[index].strip())
                items.append(ListItem(Paragraph(inline_markup(text), sheet["bullet"]), leftIndent=12))
                index += 1
            story.append(
                ListFlowable(
                    items,
                    bulletType="1",
                    leftIndent=20,
                    bulletFontName="Arial",
                    bulletFontSize=7,
                    spaceAfter=5,
                )
            )
            continue
        if stripped in {"---", "***"}:
            flush_paragraph()
            story.append(HRFlowable(width="100%", thickness=0.5, color=LINE, spaceBefore=6, spaceAfter=8))
            index += 1
            continue
        paragraph.append(stripped)
        index += 1
    flush_paragraph()
    flush_quote()
    return story


class BookDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        self.chapter_title = ""

    def afterFlowable(self, flowable) -> None:
        if isinstance(flowable, Paragraph):
            style = flowable.style.name
            if style in {"H1", "H2"}:
                level = 0 if style == "H1" else 1
                text = flowable.getPlainText()
                key = f"heading-{self.seq.nextf('heading')}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, level=level, closed=False)
                self.notify("TOCEntry", (level, text, self.page, key))
                if style == "H1":
                    self.chapter_title = text


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    page = canvas.getPageNumber()
    if page > 1:
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.4)
        canvas.line(17 * mm, PAGE[1] - 14 * mm, PAGE[0] - 17 * mm, PAGE[1] - 14 * mm)
        canvas.setFont("Arial", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(17 * mm, PAGE[1] - 11 * mm, "PRACTICAL DEVSECOPS ENGINEERING")
        if doc.chapter_title:
            canvas.drawRightString(PAGE[0] - 17 * mm, PAGE[1] - 11 * mm, doc.chapter_title[:58])
        canvas.drawCentredString(PAGE[0] / 2, 10 * mm, str(page - 1))
    canvas.restoreState()


def build_pdf() -> None:
    register_fonts()
    make_cover()
    sheet = styles()
    frame = Frame(16.5 * mm, 16 * mm, PAGE[0] - 33 * mm, PAGE[1] - 33 * mm, id="normal")
    template = PageTemplate(id="book", frames=[frame], onPage=header_footer)
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BookDocTemplate(
        str(PDF_OUT),
        pagesize=PAGE,
        leftMargin=16.5 * mm,
        rightMargin=16.5 * mm,
        topMargin=17 * mm,
        bottomMargin=16 * mm,
        title="Practical DevSecOps Engineering",
        author="Northwind Book Project",
        subject="Production security from assets and authority to restored trust",
    )
    doc.addPageTemplates([template])
    story: list = [
        Spacer(1, 28 * mm),
        Paragraph(
            "PRACTICAL",
            ParagraphStyle(
                "CoverKicker",
                fontName="Arial-Bold",
                fontSize=14,
                leading=18,
                textColor=CYAN,
                alignment=TA_LEFT,
            ),
        ),
        Spacer(1, 4 * mm),
        Paragraph(
            "DevSecOps<br/>Engineering",
            ParagraphStyle(
                "CoverTitle",
                fontName="Arial-Bold",
                fontSize=32,
                leading=36,
                textColor=NAVY,
                alignment=TA_LEFT,
            ),
        ),
        Spacer(1, 10 * mm),
        HRFlowable(width="55%", thickness=3, color=BLUE, hAlign="LEFT"),
        Spacer(1, 8 * mm),
        Paragraph(
            "Production security from assets and authority to restored trust",
            ParagraphStyle("CoverSub", fontName="Georgia", fontSize=15, leading=21, textColor=INK),
        ),
        Spacer(1, 48 * mm),
        Paragraph(
            "A mid-to-advanced, practice-first guide<br/>Northwind Commerce reference implementation<br/><br/>Version 1.0",
            ParagraphStyle("CoverMeta", fontName="Arial", fontSize=10, leading=15, textColor=MUTED),
        ),
        PageBreak(),
        Paragraph("Contents", sheet["toc"]),
    ]
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            "TOC1",
            fontName="Arial-Bold",
            fontSize=9,
            leading=13,
            textColor=NAVY,
            leftIndent=0,
            firstLineIndent=0,
            spaceBefore=3,
        ),
        ParagraphStyle(
            "TOC2",
            fontName="Arial",
            fontSize=7.5,
            leading=10,
            textColor=MUTED,
            leftIndent=14,
            firstLineIndent=0,
        ),
    ]
    story.extend([toc, PageBreak()])
    for number, filename in enumerate(FILES):
        if number:
            story.append(PageBreak())
        story.extend(markdown_story(BOOK / filename, sheet))
    doc.multiBuild(story)
    print(PDF_OUT)


if __name__ == "__main__":
    build_pdf()
