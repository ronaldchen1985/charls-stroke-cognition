# -*- coding: utf-8 -*-
"""Supplementary tables S1-S5 (docx) — 修订版 (阶跃参数化 + FG 末次测点删失)"""
import os
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

OUT = os.environ.get("PROJ_ROOT", os.getcwd())  # run from repository root
os.makedirs(os.path.join(OUT, "output"), exist_ok=True)

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(10)
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(2.0)

def title(t):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(11)
    p.paragraph_format.space_before = Pt(12)

def foot(t):
    p = doc.add_paragraph(); r = p.add_run(t); r.font.size = Pt(8.5)

def add_table(rows):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = t.rows[i].cells[j]; c.text = str(v)
            for pr in c.paragraphs:
                pr.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
                for r in pr.runs:
                    r.font.size = Pt(9); r.bold = (i == 0)

fmt = lambda e, lo, hi: f"{e:.3f} ({lo:.3f} to {hi:.3f})"
pf = lambda p: f"{p:.1e}" if p < 0.001 else f"{p:.3f}"

# ---------------- S1: included vs excluded ----------------
title("Table S1. Characteristics of participants included in vs excluded from the trajectory analysis sample")
rows = [
 ["Characteristic", "Included (n=14,276)", "Excluded (n=2,088)"],
 ["Age at baseline, y (mean)", "59.1", "60.1"],
 ["Women, %", "52.0", "46.6"],
 ["No formal education, %", "26.5", "32.6"],
 ["Hypertension, %", "23.8", "23.2"],
 ["Incident stroke during follow-up, %", "8.4", "7.1"],
 ["Died during follow-up, %", "14.6", "17.9"],
]
add_table(rows)
foot("Exclusion was due to absence of any cognitive measurement or incomplete baseline covariates. "
     "Multiple imputation (analysis S9, m=20) re-included these participants and yielded a concordant acute estimate (−0.181 SD).")

# ---------------- S2: FG by definition ----------------
doc.add_page_break()
title("Table S2. Incident cognitive impairment after stroke under competing mortality (Fine–Gray models), by outcome definition and threshold")
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
add_table(rows)
foot("sHR = subdistribution hazard ratio (death as competing event), adjusted for baseline age, sex, education. "
     "Participants entered the risk set at the anchor only if ≥1 post-anchor cognitive measurement was available; "
     "event-free survivors were censored at their last post-anchor measurement, and deaths (from exit interviews) were "
     "treated as competing events at the imputed death date. "
     "Proportional subdistribution hazards assumption supported (stroke × log(time) P=0.47 for the primary definition; 0.30–0.89 for others). "
     "CIF: cumulative incidence function. "
     "Table P values are Fine–Gray model Wald P; the Gray test of CIF equality gave P=0.0004 for the primary definition. "
     "S12 rows were fitted with the Fine–Gray weighting (coxph) implementation and cluster-robust standard errors, "
     "adjusting for the full covariate set of the trajectory models (age, sex, education, marital status, CES-D 10, "
     "smoking, alcohol use, hypertension, diabetes, dyslipidemia, heart disease, body-mass index).")

# ---------------- S3: sensitivity battery ----------------
doc.add_page_break()
title("Table S3. Acute memory change at stroke onset across sensitivity analyses")
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
add_table(rows)
foot("Estimates from piecewise linear mixed-effects models for episodic memory z score with an acute step at stroke onset. "
     "The step parameterization improved model fit over the continuous level-shift (spline) parameterization "
     "(ΔAIC ≈ 17 for memory, 14 for global cognition). "
     "The positive pre-stroke slope differences observed in some models (main text) are interpreted descriptively; "
     "they indicate no evidence of accelerated pre-stroke decline.")

# ---------------- S4: attrition ----------------
doc.add_page_break()
title("Table S4. Stroke survivors with vs without post-stroke cognitive measurements")
rows = [
 ["Characteristic", "With post-stroke measurement (n=1,135)", "Without post-stroke measurement (n=211)", "P"],
 ["Age at baseline, y (mean)", "59.8", "65.5", "<0.001"],
 ["Baseline memory z score (mean)", "0.004", "−0.238", "<0.001"],
 ["Women, %", "51.3", "52.1", "0.88"],
 ["Died during follow-up, %", "11.9", "32.7", "<0.001"],
]
add_table(rows)
foot("Among all 1,346 incident stroke cases (irrespective of covariate completeness), 1,135 (84.3%) had at least one "
     "post-stroke cognitive measurement; 211 had none. "
     "Within the covariate-complete analytic sample (1,197 stroke cases), 1,019 had at least one post-stroke measurement. "
     "Differential attrition (older, cognitively lower, higher mortality among those without post-stroke measurements) "
     "is expected to bias post-stroke slope estimates toward the null.")

# ---------------- S5: pseudo-anchor draws ----------------
doc.add_page_break()
title("Table S5. Twenty independent pseudo-anchor draws: acute change estimates (step model)")
p20 = pd.read_csv(OUT + r"\output\R3b_pseudo20_step_z_wrmean.csv")
rows = [["Draw", "Memory estimate, SD", "95% CI", "P"]]
for _, r in p20.iterrows():
    rows.append([int(r.draw), f"{r.est:.3f}", f"{r.lo:.3f} to {r.hi:.3f}", pf(r.p)])
add_table(rows)
g20 = pd.read_csv(OUT + r"\output\R3b_pseudo20_step_z_glob.csv")
rows = [["Draw", "Global-cognition estimate, SD", "95% CI", "P"]]
for _, r in g20.iterrows():
    rows.append([int(r.draw), f"{r.est:.3f}", f"{r.lo:.3f} to {r.hi:.3f}", pf(r.p)])
add_table(rows)
foot(f"Memory across draws: mean {p20.est.mean():.3f} SD, range {p20.est.min():.3f} to {p20.est.max():.3f}, all P≤9e-8 "
     f"(primary estimate −0.192 SD). Global cognition across draws: mean {g20.est.mean():.3f} SD, "
     f"range {g20.est.min():.3f} to {g20.est.max():.3f}, all P≤5.8e-6 (primary estimate −0.215 SD). "
     "The primary model uses one random anchor assignment (fixed seed); the 20 draws assess stability "
     "under independent re-assignments.")

doc.save(OUT + r"\manuscript\Supplementary_Tables.docx")
print("supplementary tables saved")
