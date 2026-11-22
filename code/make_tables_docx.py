import os
OUT = os.environ.get("PROJ_ROOT", os.getcwd())  # run from repository root
os.makedirs(os.path.join(OUT, "manuscript"), exist_ok=True)
## 生成 Tables.docx: 修订版 (阶跃参数化 + 教育切点修正)
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2.0)

style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(10)
style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')

def set_cell(cell, text, bold=False, italic=False, align='left'):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = {'left': WD_ALIGN_PARAGRAPH.LEFT, 'center': WD_ALIGN_PARAGRAPH.CENTER}[align]
    r = p.add_run(text)
    r.font.bold = bold; r.font.italic = italic; r.font.size = Pt(9.5)

def add_hline(table, row_idx):
    for c in doc.tables[-1].rows[row_idx].cells:
        tcPr = c._tc.get_or_add_tcPr()
        borders = OxmlElement('w:tcBorders')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single'); bottom.set(qn('w:sz'), '8')
        borders.append(bottom); tcPr.append(borders)

# ============ TABLE 1 ============
doc.add_paragraph('Table 1. Baseline Characteristics of the Study Population by Incident Stroke Status (2011–2023)').runs[0].bold = True

t1_rows = [
    ("Characteristic", "Overall (N=16,364)", "No incident stroke (n=15,018)", "Incident stroke (n=1,346)", "P value"),
    ("Age, mean (SD), y", "59.2 (9.8)", "59.1 (9.8)", "60.7 (8.8)", "<0.001"),
    ("Female, n (%)", "8,394 (51.3)", "7,702 (51.3)", "692 (51.4)", "0.973"),
    ("Education, n (%)", "", "", "", "0.018"),
    ("    No formal education (illiterate)", "4,452 (27.2)", "4,053 (27.0)", "399 (29.7)", ""),
    ("    Literate without primary diploma (incl. home schooling)", "2,903 (17.8)", "2,667 (17.8)", "236 (17.5)", ""),
    ("    Primary or middle school", "6,886 (42.1)", "6,316 (42.1)", "570 (42.4)", ""),
    ("    High school or above", "2,101 (12.9)", "1,961 (13.1)", "140 (10.4)", ""),
    ("Married/partnered, n (%)", "14,278 (87.3)", "13,119 (87.4)", "1,159 (86.1)", "0.203"),
    ("CES-D 10 score, mean (SD)", "8.3 (6.3)", "8.2 (6.3)", "9.6 (6.5)", "<0.001"),
    ("Smoking, n (%)", "", "", "", "0.010"),
    ("    Never", "9,794 (62.2)", "9,005 (62.4)", "789 (60.0)", ""),
    ("    Former", "1,302 (8.3)", "1,165 (8.1)", "137 (10.4)", ""),
    ("    Current", "4,654 (29.5)", "4,266 (29.6)", "388 (29.5)", ""),
    ("Alcohol use, n (%)", "", "", "", "0.272"),
    ("    >1 time/month", "4,179 (25.6)", "3,828 (25.5)", "351 (26.2)", ""),
    ("    \u22641 time/month", "1,305 (8.0)", "1,213 (8.1)", "92 (6.9)", ""),
    ("    None", "10,854 (66.4)", "9,955 (66.4)", "899 (67.0)", ""),
    ("Hypertension, n (%)", "3,859 (23.7)", "3,324 (22.3)", "535 (39.8)", "<0.001"),
    ("Diabetes, n (%)", "889 (5.5)", "771 (5.2)", "118 (8.8)", "<0.001"),
    ("Dyslipidemia, n (%)", "1,414 (8.8)", "1,210 (8.2)", "204 (15.4)", "<0.001"),
    ("Heart disease, n (%)", "1,898 (11.6)", "1,647 (11.0)", "251 (18.7)", "<0.001"),
    ("Body-mass index, mean (SD), kg/m\u00b2*", "23.4 (3.9)", "23.3 (3.9)", "24.4 (4.0)", "<0.001"),
]
t = doc.add_table(rows=len(t1_rows), cols=5)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, row in enumerate(t1_rows):
    for j, v in enumerate(row):
        set_cell(t.rows[i].cells[j], v, bold=(i == 0), align='left' if j == 0 else 'center')
add_hline(t, 0); add_hline(t, len(t1_rows) - 1)
fn = doc.add_paragraph()
fn.add_run('CES-D 10 indicates 10-item Center for Epidemiologic Studies Depression scale (range 0–30, higher = more depressive symptoms). '
           'Chronic diseases are self-reported physician diagnoses at the 2011 baseline. '
           'Education categories follow the CHARLS bd001 codebook. '
           'Education data were missing for 22 participants, smoking data for 614, and chronic-disease items for 84 (hypertension), 141 (diabetes), 313 (dyslipidemia), and 69 (heart disease); percentages are computed among non-missing responses and may not sum to 100% owing to rounding; '
           'missing alcohol responses (n=26) were assigned to "None" in regression models. '
           '*Body-mass index from physical measurement (missing n=3,648); its P value is computed among participants with measured BMI; '
           'missingness was handled by an indicator variable in primary models and by multiple imputation in S9. '
           'P values from t tests (continuous) and \u03c7\u00b2 tests (categorical).').font.size = Pt(8.5)

doc.add_page_break()

# ============ TABLE 2 ============
doc.add_paragraph('Table 2. Peri-Stroke Cognitive Trajectory by Domain: Piecewise Linear Mixed-Effects Models With an Acute Step at Stroke Onset').runs[0].bold = True

t2_rows = [
    ("Trajectory parameter", "Memory (primary), z", "Immediate recall, z", "Delayed recall, z", "TICS-10, z", "Visuospatial, z", "Global cognition, z"),
    ("Background slope, SD per year (stroke-free)", "\u22120.0137 (\u22120.0156 to \u22120.0117)\u2021", "\u22120.0138 (\u22120.0158 to \u22120.0119)\u2021", "\u22120.0107 (\u22120.0127 to \u22120.0087)\u2021", "\u22120.0033 (\u22120.0059 to \u22120.0007)*", "\u22120.0013 (\u22120.0038 to 0.0011)", "\u22120.0055 (\u22120.0080 to \u22120.0029)\u2021"),
    ("Acute step at stroke onset, SD", "\u22120.192 (\u22120.262 to \u22120.122)\u2021", "\u22120.206 (\u22120.276 to \u22120.135)\u2021", "\u22120.132 (\u22120.204 to \u22120.060)\u2021", "\u22120.149 (\u22120.241 to \u22120.057)\u2020", "\u22120.098 (\u22120.189 to \u22120.008)*", "\u22120.215 (\u22120.307 to \u22120.122)\u2021"),
    ("Pre-stroke slope difference, SD per year", "0.012 (0.004 to 0.019); P=0.003", "0.012 (0.004 to 0.019); P=0.003", "0.010 (0.002 to 0.018); P=0.012", "0.015 (0.005 to 0.025); P=0.004", "0.005 (\u22120.004 to 0.015); P=0.272", "0.017 (0.007 to 0.028); P<0.001"),
    ("Post-stroke slope difference, SD per year", "0.011 (\u22120.008 to 0.029); P=0.248", "0.018 (\u22120.001 to 0.037); P=0.058", "0.002 (\u22120.017 to 0.021); P=0.863", "\u22120.009 (\u22120.033 to 0.016); P=0.493", "0.005 (\u22120.019 to 0.029); P=0.693", "0.002 (\u22120.022 to 0.026); P=0.892"),
]
t = doc.add_table(rows=len(t2_rows), cols=7)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, row in enumerate(t2_rows):
    for j, v in enumerate(row):
        set_cell(t.rows[i].cells[j], v, bold=(i == 0), align='left' if j == 0 else 'center')
add_hline(t, 0); add_hline(t, len(t2_rows) - 1)
fn = doc.add_paragraph()
fn.add_run('Values are fixed-effect estimates (95% CI) from piecewise linear mixed-effects models with time anchored at stroke onset. '
           'A step term (0 before, 1 at/after onset) captures the acute change, following prior HRS and COSMIC analyses; '
           'stroke-by-slope interactions estimate pre-/post-stroke slope differences; stroke-free participants received pseudo-anchor times '
           'drawn from the case event-time distribution. Models include participant-level random intercepts and slopes and adjust for '
           'baseline age, sex, education, marital status, CES-D 10, smoking, alcohol use, hypertension, diabetes, dyslipidemia, heart disease, and body-mass index. '
           'z scores standardized within each interview year (residuals from regression on age [natural spline, 3 df], education, and sex). '
           'TICS-10 = orientation (5 items) + serial-7 subtraction (5 items); visuospatial = figure copying; global = mean of memory, TICS-10, and visuospatial z scores, rescaled. '
           'The step parameterization improved fit over a level-shift (continuous-spline) parameterization (\u0394AIC \u2248 17 for memory). '
           'Analytic sample sizes (participants): memory 14,276 (57,272 person-waves; 1,197 incident strokes in the analytic sample); TICS-10 9,757; visuospatial 10,173; global 9,722. '
           'The acute memory change was the prespecified primary hypothesis; all other P values are nominal (no multiplicity adjustment). '
           'Positive pre-stroke slope differences denote slower decline in stroke survivors relative to stroke-free participants; negative differences would denote accelerated decline. '
           '*P<0.05; \u2020P<0.01; \u2021P<0.001.').font.size = Pt(8.5)

doc.save(os.path.join(OUT, "manuscript", "Tables.docx"))
print('saved Tables.docx')
