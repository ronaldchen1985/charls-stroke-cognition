# -*- coding: utf-8 -*-
"""Build Springer ESM files: ESM_1.pdf (Tables S1-S5) and ESM_2.pdf (Fig S1 + caption)."""
import os
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Image)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

pdfmetrics.registerFont(TTFont("TNR", "C:/Windows/Fonts/times.ttf"))
pdfmetrics.registerFont(TTFont("TNR-B", "C:/Windows/Fonts/timesbd.ttf"))

OUT = os.environ.get("PROJ_ROOT", os.getcwd())  # run from repository root
os.makedirs(os.path.join(OUT, "output"), exist_ok=True)
SUB = os.path.join(OUT, "submission_IJS")

st_title = ParagraphStyle("t", fontName="TNR-B", fontSize=11, leading=14, spaceBefore=10, spaceAfter=4)
st_cell = ParagraphStyle("c", fontName="TNR", fontSize=8.5, leading=11)
st_cellb = ParagraphStyle("cb", fontName="TNR-B", fontSize=8.5, leading=11)
st_foot = ParagraphStyle("f", fontName="TNR", fontSize=8, leading=10, textColor=colors.HexColor("#333333"))

PAGE_W, PAGE_H = A4
CW = PAGE_W - 40 * mm

fmt = lambda e, lo, hi: f"{e:.3f} ({lo:.3f} to {hi:.3f})"
pf = lambda p: f"{p:.1e}" if p < 0.001 else f"{p:.3f}"

story = []

def add_table_block(title, rows, foot, w0=1.0):
    story.append(Paragraph(title, st_title))
    data = [[Paragraph(str(v), st_cellb if i == 0 else st_cell) for v in row] for i, row in enumerate(rows)]
    ncol = len(rows[0])
    widths = [CW * w0 / (w0 + ncol - 1)] + [CW / (w0 + ncol - 1)] * (ncol - 1)
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf0f6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)
    story.append(Paragraph(foot, st_foot))
    story.append(PageBreak())

# S1
add_table_block(
 "Table S1. Characteristics of participants included in vs excluded from the trajectory analysis sample",
 [["Characteristic", "Included (n=14,276)", "Excluded (n=2,088)"],
  ["Age at baseline, y (mean)", "59.1", "60.1"],
  ["Women, %", "52.0", "46.6"],
  ["No formal education, %", "26.5", "32.6"],
  ["Hypertension, %", "23.8", "23.2"],
  ["Incident stroke during follow-up, %", "8.4", "7.1"],
  ["Died during follow-up, %", "14.6", "17.9"]],
 "Exclusion was due to absence of any cognitive measurement or incomplete baseline covariates. "
 "Multiple imputation (analysis S9, m=20) re-included these participants and yielded a concordant acute estimate (−0.181 SD).")

# S2
fg = pd.read_csv(OUT + r"\output\R5_fg_final.csv")
rows = [["Definition / threshold", "n", "Events", "Competing deaths", "sHR (95% CI)", "P",
         "5-y CIF stroke vs stroke-free, %"]]
lab = {("z_wrmean", -1): "Memory z ≤ −1 SD (primary)",
       ("z_wrmean", -1.5): "Memory z ≤ −1.5 SD",
       ("z_glob", -1): "Global-cognition z ≤ −1 SD (S10)",
       ("z_glob", -1.5): "Global-cognition z ≤ −1.5 SD (S10)"}
for (dom, TH), lb in lab.items():
    r = fg[(fg.domain == dom) & (fg.threshold == TH)].iloc[0]
    rows.append([lb, f"{int(r.n):,}", int(r.n_event), int(r.n_death),
                 fmt(r.hr, r.lo, r.hi), pf(r.p), f"{r.cif5_s*100:.1f} vs {r.cif5_c*100:.1f}"])
v6 = pd.read_csv(OUT + r"\output\V6_fg_fulladj.csv")
for (dom, TH), lb in lab.items():
    r = v6[(v6.domain == dom) & (v6.threshold == TH)].iloc[0]
    rows.append([lb + " (S12: fully adjusted)", f"{int(r.n):,}", int(r.n_event), int(r.n_death),
                 fmt(r.hr, r.lo, r.hi), pf(r.p), "—"])
add_table_block(
 "Table S2. Incident cognitive impairment after stroke under competing mortality (Fine–Gray models), by outcome definition and threshold",
 rows,
 "sHR = subdistribution hazard ratio (death as competing event), adjusted for baseline age, sex, education. "
 "Participants entered the risk set at the anchor only if ≥1 post-anchor cognitive measurement was available; "
 "event-free survivors were censored at their last post-anchor measurement, and deaths (from exit interviews) were "
 "treated as competing events at the imputed death date. "
 "Proportional subdistribution hazards assumption supported (stroke × log(time) P=0.47 for the primary definition; 0.30–0.89 for others). "
 "CIF: cumulative incidence function. "
 "Table P values are Fine–Gray model Wald P; the Gray test of CIF equality gave P=0.0004 for the primary definition. "
 "S12 rows were fitted with the Fine–Gray weighting (coxph) implementation and cluster-robust standard errors, "
 "adjusting for the full covariate set of the trajectory models (age, sex, education, marital status, CES-D 10, "
 "smoking, alcohol use, hypertension, diabetes, dyslipidemia, heart disease, body-mass index).", w0=1.8)

# S3
r2 = pd.read_csv(OUT + r"\output\R2_main_step.csv")
r3 = pd.read_csv(OUT + r"\output\R3_subgroup_sens_step.csv")
mi = pd.read_csv(OUT + r"\output\R4_mi20_pooled.csv")
rows = [["Analysis", "Acute change, SD (95% CI)", "P"]]
r = r2[(r2.model == "step: z_wrmean") & (r2.term == "step")].iloc[0]
rows.append(["Primary model (step parameterization, fully adjusted)", fmt(r.est, r.lo, r.hi), pf(r.p)])
lab = {"S1: midpoint imputation only": "S1: Midpoint-only event timing",
       "S2: exclude 2015-2018-window events": "S2: Excluding 2015–2018-window events",
       "S3: pre-2020 events only": "S3: Pre-2020 events only",
       "S4: BMI complete cases": "S4: BMI complete cases",
       "S5: demographics-only adjustment": "S5: Demographics-only adjustment",
       "S6: first sixth-wave assessment only": "S6: First sixth-wave assessment only",
       "S7: baseline-standardized, memory": "S7: Baseline-distribution standardization",
       "S8: exclude possible recurrent stroke": "S8: Excluding possible recurrent stroke (n=26)"}
for k, v in lab.items():
    r = r3[(r3.analysis == k) & (r3.term == "step")].iloc[0]
    rows.append([v, fmt(r.est, r.lo, r.hi), pf(r.p)])
r = mi[mi.term == "step"].iloc[0]
rows.append(["S9: Multiple imputation of covariates (m=20, chained equations)", fmt(r.est, r.lo, r.hi), pf(r.p)])
rows.append(["S10: Global-cognition PSCI definition", "see Table S2", "—"])
r = r2[(r2.model == "spline: z_wrmean") & (r2.term == "stroke")].iloc[0]
rows.append(["S11: Level-shift (continuous-spline) parameterization", fmt(r.est, r.lo, r.hi), pf(r.p)])
s13 = pd.read_csv(OUT + r"\output\V9_practice_s13.csv")
r = s13[(s13.model == "S13_visit_adj") & (s13.term == "step")].iloc[0]
rows.append(["S13: Adjustment for testing occasion (visit number)", fmt(r.est, r.lo, r.hi), pf(r.p)])
add_table_block(
 "Table S3. Acute memory change at stroke onset across sensitivity analyses",
 rows,
 "Estimates from piecewise linear mixed-effects models for episodic memory z score with an acute step at stroke onset. "
 "The step parameterization improved model fit over the continuous level-shift (spline) parameterization "
 "(ΔAIC ≈ 17 for memory, 14 for global cognition). "
 "The positive pre-stroke slope differences observed in some models (main text) are interpreted descriptively; "
 "they indicate no evidence of accelerated pre-stroke decline.")

# S4 (updated: full 1,346-case basis)
add_table_block(
 "Table S4. Stroke survivors with vs without post-stroke cognitive measurements",
 [["Characteristic", "With post-stroke measurement (n=1,135)", "Without post-stroke measurement (n=211)", "P"],
  ["Age at baseline, y (mean)", "59.8", "65.5", "<0.001"],
  ["Baseline memory z score (mean)", "0.004", "−0.238", "<0.001"],
  ["Women, %", "51.3", "52.1", "0.88"],
  ["Died during follow-up, %", "11.9", "32.7", "<0.001"]],
 "Among all 1,346 incident stroke cases (irrespective of covariate completeness), 1,135 (84.3%) had at least one "
 "post-stroke cognitive measurement; 211 had none. "
 "Within the covariate-complete analytic sample (1,197 stroke cases), 1,019 had at least one post-stroke measurement. "
 "Differential attrition (older, cognitively lower, higher mortality among those without post-stroke measurements) "
 "is expected to bias post-stroke slope estimates toward the null.")

# S5 (compact style so both panels + footnote fit one page)
p20 = pd.read_csv(OUT + r"\output\R3b_pseudo20_step_z_wrmean.csv")
g20 = pd.read_csv(OUT + r"\output\R3b_pseudo20_step_z_glob.csv")
rows = [["Draw", "Episodic memory estimate, SD", "95% CI", "P"]]
for _, r in p20.iterrows():
    rows.append([int(r.draw), f"{r.est:.3f}", f"{r.lo:.3f} to {r.hi:.3f}", pf(r.p)])
rows.append(["Draw", "Global-cognition estimate, SD", "95% CI", "P"])
for _, r in g20.iterrows():
    rows.append([int(r.draw), f"{r.est:.3f}", f"{r.lo:.3f} to {r.hi:.3f}", pf(r.p)])
story.append(Paragraph(
 "Table S5. Twenty independent pseudo-anchor draws: acute change estimates (step model), "
 "for episodic memory (upper panel) and global cognition (lower panel)", st_title))
hdr_idx = {0, 21}
data = [[Paragraph(str(v), st_cellb if i in hdr_idx else st_cell) for v in row] for i, row in enumerate(rows)]
t = Table(data, colWidths=[CW * 0.10, CW * 0.38, CW * 0.32, CW * 0.20], repeatRows=1)
t.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf0f6")),
    ("BACKGROUND", (0, 21), (-1, 21), colors.HexColor("#eaf0f6")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 1.2),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
]))
story.append(t)
story.append(Paragraph(
 f"Memory across draws: mean {p20.est.mean():.3f} SD, range {p20.est.min():.3f} to {p20.est.max():.3f}, all P≤9e-8 "
 f"(primary estimate −0.192 SD). Global cognition across draws: mean {g20.est.mean():.3f} SD, "
 f"range {g20.est.min():.3f} to {g20.est.max():.3f}, all P≤5.8e-6 (primary estimate −0.215 SD). "
 "The primary model uses one random anchor assignment (fixed seed); the 20 draws assess stability under independent re-assignments.",
 st_foot))
story.append(PageBreak())

if story and isinstance(story[-1], PageBreak):
    story.pop()
SimpleDocTemplate(os.path.join(SUB, "Supplementary_Material_1.pdf"), pagesize=A4,
                  leftMargin=20 * mm, rightMargin=20 * mm,
                  topMargin=18 * mm, bottomMargin=16 * mm,
                  title="Supplementary Material 1: Supplementary Tables S1-S5").build(story)
print("ESM_1 ok")

# ---------------- ESM_2: Fig S1 ----------------
img_path = os.path.join(OUT, r"figures\FigS1_flow_EN.png")
with PILImage.open(img_path) as im:
    w, h = im.size
scale = min(CW / w, (PAGE_H - 60 * mm) / h)
s2 = [Paragraph("Fig. S1 STROBE participant flow diagram, including the PSCI analysis branch", st_title),
      Spacer(1, 6),
      Image(img_path, width=w * scale, height=h * scale)]
SimpleDocTemplate(os.path.join(SUB, "Supplementary_Material_2.pdf"), pagesize=A4,
                  leftMargin=20 * mm, rightMargin=20 * mm,
                  topMargin=18 * mm, bottomMargin=16 * mm,
                  title="Supplementary Material 2: Fig. S1").build(s2)
print("ESM_2 ok")
