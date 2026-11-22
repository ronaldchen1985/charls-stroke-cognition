# -*- coding: utf-8 -*-
"""Proofreading PDF for the International Journal of Stroke submission package."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, PageBreak, NextPageTemplate)
import make_proof_pdf as P

BASE = os.path.join(os.environ.get("PROJ_ROOT", os.getcwd()), "submission_IJS")
OUT = os.path.join(BASE, "IJS_Submission_Package_Proof.pdf")
MARGIN = 20 * mm
PAGE_W, PAGE_H = A4

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 8.5)
    canvas.setFillColor(P.colors.HexColor("#777777"))
    canvas.drawCentredString(PAGE_W / 2, 10 * mm, str(doc.page))
    canvas.drawString(MARGIN, PAGE_H - 12 * mm,
                      "Int J Stroke submission package - proofreading copy (2026-11-22)")
    canvas.restoreState()

def main():
    doc = P.BaseDocTemplate(OUT, pagesize=A4,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=18 * mm, bottomMargin=16 * mm,
                            title="IJS Submission Package - Proofreading Copy")
    frame = Frame(MARGIN, 16 * mm, PAGE_W - 2 * MARGIN, PAGE_H - 34 * mm, id="main")
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=footer)])

    story = []

    def add_section(title, subtitle, builder):
        story.append(Paragraph(title, P.styles["divider"]))
        story.append(Paragraph(subtitle, P.styles["dividersub"]))
        story.append(Spacer(1, 10))
        story.extend(builder)
        story.append(NextPageTemplate("page"))
        story.append(PageBreak())

    add_section("1. Cover Letter", "Cover_Letter_IJS.docx",
                P.docx_story(os.path.join(BASE, "Cover_Letter_IJS.docx")))
    add_section("2. Manuscript (title page + abstract + main text + declarations + references + legends)",
                "Manuscript_IJS.docx",
                P.docx_story(os.path.join(BASE, "Manuscript_IJS.docx")))
    add_section("3. Tables 1-2", "Tables.docx",
                P.docx_story(os.path.join(BASE, "Tables.docx")))

    figs = [("Figure 1  Model-estimated cognitive trajectories (4 domains, step parameterization)", "Fig1.tif"),
            ("Figure 2  Observed domain means with 95% CI", "Fig2.tif"),
            ("Figure 3  Forest plot: main, subgroup and sensitivity analyses", "Fig3.tif"),
            ("Figure 4  Cumulative incidence of PSCI (competing risk)", "Fig4.tif")]
    story.append(Paragraph("4. Figures", P.styles["divider"]))
    story.append(Paragraph("Fig1-4.tif (600 dpi)", P.styles["dividersub"]))
    story.append(PageBreak())
    for cap, fn in figs:
        story.extend(P.figure_story(os.path.join(BASE, fn), cap))
        story.append(PageBreak())

    add_section("5. Supplementary Material 1 (Tables S1-S5)",
                "Supplementary_Material_1.pdf -> rendered from docx source",
                P.docx_story(os.path.join(os.environ.get("PROJ_ROOT", os.getcwd()), "manuscript", "Supplementary_Tables.docx")))
    story.append(Paragraph("6. Supplementary Material 2 (Fig. S1)", P.styles["divider"]))
    story.append(Paragraph("Supplementary_Material_2.pdf", P.styles["dividersub"]))
    story.append(PageBreak())
    story.extend(P.figure_story(os.path.join(os.environ.get("PROJ_ROOT", os.getcwd()), "figures", "FigS1_flow_EN.png"),
                                "Fig. S1  STROBE flow diagram"))
    story.append(PageBreak())
    add_section("7. STROBE Checklist", "STROBE_checklist_IJS.docx",
                P.docx_story(os.path.join(BASE, "STROBE_checklist_IJS.docx")))
    add_section("8. Suggested Reviewers", "Suggested_Reviewers_IJS.docx",
                P.docx_story(os.path.join(BASE, "Suggested_Reviewers_IJS.docx")))

    if story and isinstance(story[-1], PageBreak):
        story.pop()
    doc.build(story)
    print("OK ->", OUT)

if __name__ == "__main__":
    main()
