import os
OUT = os.environ.get("PROJ_ROOT", os.getcwd())  # run from repository root
os.makedirs(os.path.join(OUT, "submission_IJS"), exist_ok=True)
# -*- coding: utf-8 -*-
"""生成 J Neurol 推荐审稿人名单 docx"""
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

doc = Document()
st = doc.styles['Normal']
st.font.name = 'Times New Roman'; st.font.size = Pt(12)
st._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')

doc.add_paragraph('Suggested Reviewers').runs[0].bold = True
doc.add_paragraph('Manuscript: "Cognitive trajectories and risk of cognitive impairment after incident stroke: '
                  'a 12-year nationwide cohort study in China" (Research Article, International Journal of Stroke)')
doc.add_paragraph('All suggested reviewers are independent of the authors and have no conflicts of interest with this work. '
                  'E-mail addresses are available from the respective institutional pages.')
doc.add_paragraph()

revs = [
    ("1. Deborah A. Levine, MD, MPH",
     "Department of Internal Medicine and Neurology, University of Michigan, Ann Arbor, MI, USA",
     "Defined the field's reference method: piecewise linear mixed models with an acute step at stroke onset "
     "(Levine et al., JAMA 2015, using HRS). Ideally placed to judge our parameterization comparison and the "
     "interpretation of pre- and post-stroke slope differences."),
    ("2. Perminder S. Sachdev, MD, PhD",
     "Centre for Healthy Brain Ageing (CHeBA), University of New South Wales, Sydney, Australia",
     "Co-lead of the COSMIC consortium, whose 14-cohort individual-participant meta-analysis (JAMA Netw Open 2024) "
     "is the international benchmark against which our estimates are compared; expert in cross-cohort harmonization "
     "of cognitive data."),
    ("3. Vincent C.T. Mok, MD",
     "Division of Neurology, Department of Medicine and Therapeutics, The Chinese University of Hong Kong, Hong Kong SAR, China",
     "Leading authority on vascular cognitive impairment and post-stroke cognition in Asian populations; "
     "well suited to evaluate the clinical relevance of our PSCI incidence estimates in a Chinese cohort."),
    ("4. Sarah T. Pendlebury, DPhil, FRCP",
     "Wolfson Centre for Prevention of Stroke and Dementia, University of Oxford, Oxford, UK",
     "Oxford Vascular Study lead on dementia incidence after TIA and stroke (Lancet Neurol 2019); expert in "
     "ascertainment, attrition, and competing-risk issues in longitudinal post-stroke cognition studies."),
    ("5. Darren M. Lipnicki, PhD",
     "Centre for Healthy Brain Ageing (CHeBA), University of New South Wales, Sydney, Australia",
     "Methodologist of the COSMIC stroke analyses; expert in harmonized modelling of cognitive trajectories and "
     "the standardization conventions that are central to our manuscript."),
]
for name, aff, why in revs:
    doc.add_paragraph(name).runs[0].bold = True
    doc.add_paragraph(aff)
    doc.add_paragraph('Rationale: ' + why)
    doc.add_paragraph()

doc.add_paragraph('Opposed reviewers: none.').runs[0].italic = True
doc.save(os.path.join(OUT, "submission_IJS", "Suggested_Reviewers_IJS.docx"))
print('saved')
