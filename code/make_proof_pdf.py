# -*- coding: utf-8 -*-
"""Build a single proofreading PDF for the IJS submission package.
Order: Cover letter -> Manuscript -> Tables -> Figures 1-4 -> Fig S1 -> Suppl Tables -> STROBE.
"""
import html, os
from docx import Document
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph as DocxPara
from docx.oxml.ns import qn
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, PageBreak, Table, TableStyle, Image, NextPageTemplate)
from PIL import Image as PILImage

BASE = r"D:\CHARLS\PSCI_traj\submission"
OUT = os.path.join(BASE, "IJS_Submission_Package_Proof.pdf")

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

styles = {
    "divider": ParagraphStyle("divider", fontName="Times-Bold", fontSize=20, leading=26,
                              spaceBefore=120, spaceAfter=12, textColor=colors.HexColor("#1a3a5c")),
    "dividersub": ParagraphStyle("dividersub", fontName="Times-Italic", fontSize=11, leading=15,
                                 textColor=colors.HexColor("#555555")),
    "title": ParagraphStyle("title", fontName="Times-Bold", fontSize=14, leading=18,
                            spaceBefore=10, spaceAfter=8),
    "h1": ParagraphStyle("h1", fontName="Times-Bold", fontSize=12.5, leading=16,
                         spaceBefore=12, spaceAfter=5, textColor=colors.HexColor("#1a3a5c")),
    "h2": ParagraphStyle("h2", fontName="Times-Bold", fontSize=11, leading=14,
                         spaceBefore=8, spaceAfter=4),
    "body": ParagraphStyle("body", fontName="Times-Roman", fontSize=10.5, leading=15,
                           spaceAfter=5, alignment=4),  # justify
    "cell": ParagraphStyle("cell", fontName="Times-Roman", fontSize=8.5, leading=11),
    "cellb": ParagraphStyle("cellb", fontName="Times-Bold", fontSize=8.5, leading=11),
    "caption": ParagraphStyle("caption", fontName="Times-Italic", fontSize=9.5, leading=13,
                              textColor=colors.HexColor("#444444"), spaceBefore=4),
}


def para_markup(p: DocxPara) -> str:
    parts = []
    for r in p.runs:
        t = html.escape(r.text)
        if not t:
            continue
        if r.font.superscript:
            t = "<super>" + t + "</super>"
        if r.font.subscript:
            t = "<sub>" + t + "</sub>"
        if r.bold:
            t = "<b>" + t + "</b>"
        if r.italic:
            t = "<i>" + t + "</i>"
        parts.append(t)
    return "".join(parts)


def iter_blocks(doc):
    body = doc.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield DocxPara(child, doc)
        elif child.tag == qn("w:tbl"):
            yield DocxTable(child, doc)


def docx_story(path):
    story = []
    doc = Document(path)
    for blk in iter_blocks(doc):
        if isinstance(blk, DocxPara):
            txt = para_markup(blk).strip()
            if not txt:
                continue
            sname = (blk.style.name or "").lower()
            if sname.startswith("title"):
                st = styles["title"]
            elif sname.startswith("heading 1"):
                st = styles["h1"]
            elif sname.startswith("heading"):
                st = styles["h2"]
            else:
                st = styles["body"]
            story.append(Paragraph(txt, st))
        else:  # table
            data = []
            for i, row in enumerate(blk.rows):
                line = []
                for cell in row.cells:
                    ctext = "<br/>".join(
                        html.escape(p.text) for p in cell.paragraphs if p.text.strip())
                    line.append(Paragraph(ctext or " ",
                                          styles["cellb"] if i == 0 else styles["cell"]))
                data.append(line)
            if not data:
                continue
            ncol = len(data[0])
            tw = Table(data, colWidths=[CONTENT_W / ncol] * ncol, repeatRows=1)
            tw.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf0f6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(Spacer(1, 4))
            story.append(tw)
            story.append(Spacer(1, 8))
    return story


def figure_story(img_path, title):
    with PILImage.open(img_path) as im:
        w, h = im.size
    max_w, max_h = CONTENT_W, PAGE_H - 2 * MARGIN - 30
    scale = min(max_w / w, max_h / h)
    img = Image(img_path, width=w * scale, height=h * scale)
    img.hAlign = "CENTER"
    return [Paragraph(title, styles["h2"]), img]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 8.5)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawCentredString(PAGE_W / 2, 10 * mm, str(doc.page))
    canvas.drawString(MARGIN, PAGE_H - 12 * mm,
                      "IJS submission package - proofreading copy (2026-11-15)")
    canvas.restoreState()


def main():
    doc = BaseDocTemplate(OUT, pagesize=A4,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=18 * mm, bottomMargin=16 * mm,
                          title="IJS Submission Package - Proofreading Copy")
    frame = Frame(MARGIN, 16 * mm, CONTENT_W, PAGE_H - 34 * mm, id="main")
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=footer)])

    story = []

    def add_section(title, subtitle, builder):
        story.append(Paragraph(title, styles["divider"]))
        story.append(Paragraph(subtitle, styles["dividersub"]))
        story.append(Spacer(1, 10))
        story.extend(builder)
        story.append(NextPageTemplate("page"))
        story.append(PageBreak())

    add_section("1. Cover Letter", "Cover_Letter_IJS.docx",
                docx_story(os.path.join(BASE, "Cover_Letter_IJS.docx")))
    add_section("2. Manuscript (title page + main text)",
                "Manuscript_IJS_Submission.docx",
                docx_story(os.path.join(BASE, "Manuscript_IJS_Submission.docx")))
    add_section("3. Tables 1-2", "Tables.docx",
                docx_story(os.path.join(BASE, "Tables.docx")))

    figs = [("Figure 1. Model-estimated cognitive trajectories (4 domains)", "Figure1.png"),
            ("Figure 2. Observed domain means with 95% CI", "Figure2.png"),
            ("Figure 3. Forest plot: main, subgroup and sensitivity analyses", "Figure3.png"),
            ("Figure 4. Cumulative incidence of PSCI (competing risk)", "Figure4.png"),
            ("Figure S1. STROBE flow diagram", "Supplementary_FigureS1.png")]
    story.append(Paragraph("4. Figures", styles["divider"]))
    story.append(Paragraph("Figure1-4.png + Supplementary_FigureS1.png", styles["dividersub"]))
    story.append(PageBreak())
    for i, (cap, fn) in enumerate(figs):
        story.extend(figure_story(os.path.join(BASE, fn), cap))
        story.append(PageBreak())

    add_section("5. Supplementary Tables S1-S5", "Supplementary_Tables.docx",
                docx_story(os.path.join(BASE, "Supplementary_Tables.docx")))
    add_section("6. STROBE Checklist", "STROBE_checklist.docx",
                docx_story(os.path.join(BASE, "STROBE_checklist.docx")))

    if story and isinstance(story[-1], PageBreak):
        story.pop()
    doc.build(story)
    print("OK ->", OUT)


if __name__ == "__main__":
    main()
