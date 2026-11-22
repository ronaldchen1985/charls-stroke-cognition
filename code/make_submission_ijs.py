# -*- coding: utf-8 -*-
"""Build International Journal of Stroke (SAGE) submission package:
manuscript docx (Sage Vancouver superscript citations, IJS structure with
separate Aims section, Data access statement in abstract), cover letter,
STROBE checklist, TIFF figures, Supplementary Material PDFs.
All numbers = corrected event-timing rerun (628 refined anchors, 2026-11-19).
Trimmed to meet IJS 5,000-word total limit (incl. tables/legends/references).
2026-11-19 v2: 5 references added (Feigin WSO 2025; Calamia 2012; He 2023;
Rost 2022; El Husseini 2023) with full renumbering + offsetting trims."""
import os, shutil
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from PIL import Image as PILImage

BASE = os.environ.get("PROJ_ROOT", os.getcwd())  # run from repository root
SUB = os.path.join(BASE, "submission_IJS")
os.makedirs(SUB, exist_ok=True)

def set_style(doc):
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    st.paragraph_format.space_after = Pt(0)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.54)
        s.top_margin = s.bottom_margin = Cm(2.54)

def h1(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text); r.bold = True; r.font.size = Pt(14)
    p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(6)
    return p

def h2(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text); r.bold = True; r.font.size = Pt(12)
    p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(4)
    return p

def para(doc, segments, justify=True):
    if isinstance(segments, str):
        segments = [(segments, False, False)]
    p = doc.add_paragraph()
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for seg in segments:
        t = seg[0]
        b = seg[1] if len(seg) > 1 else False
        i = seg[2] if len(seg) > 2 else False
        r = p.add_run(t); r.bold = b; r.italic = i
        if len(seg) > 3 and seg[3]:
            r.font.superscript = True
    return p

def centered(doc, segments, size=12):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if isinstance(segments, str):
        segments = [(segments, False, False)]
    for seg in segments:
        t, b = seg[0], (seg[1] if len(seg) > 1 else False)
        r = p.add_run(t); r.bold = b; r.font.size = Pt(size)
    return p

# Sage Vancouver: superscript citation numbers, e.g. C("1,2")
C = lambda t: (t, False, False, True)
N = lambda t: (t, False, False)
B = lambda t: (t, True, False)
I = lambda t: (t, False, True)

# ============================================================
# 1. MAIN MANUSCRIPT
# ============================================================
doc = Document(); set_style(doc)

# ---------- TITLE PAGE ----------
centered(doc, [("Cognitive trajectories and risk of cognitive impairment after incident stroke: a 12-year nationwide cohort study in China", True)], size=16)
doc.add_paragraph()
para(doc, [("Gan Zhang", False), ("1,*", False, False, True), ("  ·  Can Sun", False), ("1,*", False, False, True), ("  ·  Qingli Sun", False), ("1", False, False, True), ("  ·  Yong Chen", False), ("1", False, False, True)], justify=False)
para(doc, [B("1 "), N("Department of Neurology, Peking University Third Hospital, No. 49 North Garden Road, Haidian District, Beijing 100191, China")], justify=False)
para(doc, [("*Gan Zhang and Can Sun contributed equally to this work (co-first authors).", False, True)], justify=False)
para(doc, [B("Corresponding author: "), N("Yong Chen, Department of Neurology, Peking University Third Hospital, No. 49 North Garden Road, Haidian District, Beijing 100191, China. E-mail: ronaldchen@bjmu.edu.cn; Tel: +86-18810975103; Fax: +86-10-82266699")], justify=False)
doc.add_paragraph()
para(doc, [B("Article type: "), N("Research Article")], justify=False)
para(doc, [B("Word count (main text, Introduction\u2013Conclusions): "), N("3,176"),
           B(" (total incl. abstract, references, legends, tables: \u22485,254)"),
           B("    Abstract word count: "), N("244")], justify=False)
para(doc, [B("Tables: "), N("2"), B("    Figures: "), N("4"),
           B("    Supplementary Material: "), N("Supplementary Material 1 (Tables S1–S5); Supplementary Material 2 (Fig. S1)")], justify=False)
doc.add_page_break()

# ---------- ABSTRACT (IJS structured: Background/Aims/Methods/Results/Conclusions + Data access) ----------
h1(doc, "Abstract")
para(doc, [B("Background: "), N("How cognition evolves around a first stroke and the excess impairment risk survivors carry are incompletely characterized in Asian populations; acute-effect estimates differ two-fold between Chinese and international cohorts.")])
para(doc, [B("Aims: "), N("We mapped domain-specific peri-stroke cognitive trajectories and quantified post-stroke cognitive impairment (PSCI) risk under competing mortality.")])
para(doc, [B("Methods: "), N("We analyzed 16,364 stroke-free participants aged ≥45 years from the China Health and Retirement Longitudinal Study (2011–2023; five cognitive waves). Domain scores were standardized within each interview year. Piecewise linear mixed models anchored at stroke onset estimated an acute step and pre-/post-stroke slope differences. Incident PSCI (memory z ≤ −1 SD) was analyzed with Fine–Gray models (death as competing event).")])
para(doc, [B("Results: "), N("Among 14,276 participants (1,197 incident strokes), stroke was followed by acute step declines in memory (−0.192 SD, 95% CI −0.262 to −0.122), orientation/calculation (−0.149 SD), visuospatial ability (−0.098 SD) and global cognition (−0.215 SD), without accelerated decline before or after the event. The acute memory estimate was robust across 9 scale-comparable sensitivity analyses (−0.181 to −0.252 SD). Stroke survivors had a 41% higher subhazard of PSCI (subdistribution hazard ratio 1.41, 95% CI 1.21–1.64); among those remaining under cognitive follow-up, 5-year cumulative incidence was 27.6% versus 22.4% (absolute excess ≈5 points).")])
para(doc, [B("Conclusions: "), N("Incident stroke was followed by an acute, multidomain cognitive step decline without measurable pre- or post-event acceleration, and moderately elevated long-term impairment risk. Much of the apparent East–West difference in acute-effect magnitude could arise from analytic conventions alone; residual population differences are not excluded.")])
para(doc, [B("Data access statement: "), N("CHARLS data are available to registered researchers at https://charls.pku.edu.cn.")])
para(doc, [B("Keywords: "), N("stroke; cognition; memory; post-stroke cognitive impairment; cohort study; China")])
doc.add_page_break()

# ---------- MAIN TEXT ----------
h1(doc, "Introduction")
para(doc, [N("Stroke is the leading cause of death and adult disability in China, and post-stroke cognitive impairment (PSCI) affects up to one-third of survivors within the first year, worsening functional recovery, quality of life, and dementia risk."), C("1–3"),
           N(" Two questions remain incompletely answered. First, when cognition deteriorates relative to stroke onset—before, at, or after the event—is contested, with implications for whether prevention should target pre-stroke risk control or post-stroke monitoring. Second, trajectory studies have described mean cognitive changes but rarely translated them into the quantity clinicians need: the excess risk of crossing a cognitive-impairment threshold after stroke, accounting for competing mortality.")])
para(doc, [N("In the Health and Retirement Study, incident stroke was followed by an acute cognitive drop and accelerated decline thereafter."), C("4"),
           N(" A 2024 individual-participant meta-analysis of 14 population cohorts (COSMIC) confirmed a substantial acute decline (−0.25 SD in global cognition) and a small post-stroke acceleration (−0.038 SD/year), but found no pre-stroke slope difference"), C("5"),
           N(". Evidence on the pre-stroke phase is conflicting: an English Longitudinal Study of Ageing analysis reported significantly faster pre-stroke decline"), C("6"),
           N(", whereas a CHARLS analysis of 2011–2018 data found no pre-stroke difference but domain-specific post-stroke acceleration"), C("7"),
           N(". Most recently, a four-cohort study across 23 countries reported significant pre-stroke acceleration and showed that recurrent stroke materially inflates acute-effect estimates."), C("8"),
           N(" Notably, the largest CHARLS analysis reported an acute memory effect (≈−0.12 SD) roughly half the international pooled estimate (≈−0.25 SD)"), C("7"), N("—a gap that could reflect biology, standardization, or model parameterization, but has never been formally dissected. No study has used the full 12-year CHARLS follow-up including the sixth wave (2021–2023)—more than doubling prior CHARLS incident events—or quantified incident PSCI under competing mortality in this setting.")])

h1(doc, "Aims and hypothesis")
para(doc, "Using all five cognitive waves of CHARLS (2011–2023), we aimed to (1) determine how model parameterization and standardization conventions contribute to the two-fold East–West difference in acute-effect estimates; (2) decompose the peri-stroke trajectories of four cognitive domains into pre-stroke slope, acute step, and post-stroke slope; and (3) quantify absolute and relative risks of incident PSCI under a competing-risk framework. We hypothesized that incident stroke is followed by an acute step decline in episodic memory (primary hypothesis), with no acceleration of decline before or after the event.")

h1(doc, "Methods")
h2(doc, "Study population")
para(doc, [N("CHARLS is a nationally representative cohort of Chinese residents aged ≥45 years and their spouses, sampled by multistage stratified probability sampling in 2011 (17,705 respondents) and followed biennially."), C("9"),
           N(" The 2020 wave collected no cognitive measures and does not contribute a cognitive wave. Deaths were ascertained at each wave through exit interviews with next of kin; death dates were imputed at the interval midpoint. We included participants aged ≥45 years at baseline (2011) who were free of self-reported physician-diagnosed stroke and memory-related disease, yielding 16,364 participants. The analytic sample comprised 14,276 participants with ≥1 cognitive measurement and complete covariates (57,272 person-wave observations; excluded participants were slightly older, less educated, and more likely to die; Supplementary Material 1, Table S1). Ethics approval and consent are declared at the end of this article; the analysis followed the STROBE guidelines.")])
h2(doc, "Incident stroke ascertainment and event timing")
para(doc, "At each wave, participants reported whether a physician had ever diagnosed them with stroke. For 2013 and 2015, incident diagnoses were captured by the update question (\u201cdoctor told you since the last interview\u201d); the 2018 item applied to the full sample with \u201cever diagnosed\u201d semantics; the 2020 item captured new diagnoses among those without prior records; in 2021–2023, new diagnoses were identified by the updated disease module against carried-forward prior-diagnosis flags. The first stroke-positive wave defined the event interval. Event time was set to the reported diagnosis year (628/1,346 events, 46.7%) when it fell within the interval (0.6-year tolerance), and to the interval midpoint otherwise. Possible recurrent strokes were identifiable in the 2015 and 2021–2023 update items and addressed in sensitivity analyses.")
h2(doc, "Cognitive assessment")
para(doc, [N("Cognitive tests are administered only to participants responding for themselves; proxy interviews yield no cognitive scores, and item non-response accounts for the smaller domain-specific samples. Four outcomes were constructed at each cognitive wave. "), B("Episodic memory"), N(" (primary): mean of immediate and delayed recall of a 10-word list (0–10). "), B("Orientation/calculation (TICS-10):"), N(" five orientation items plus five serial-7 subtractions (0–10; adapted TICS items). "), B("Visuospatial ability:"), N(" figure copying (0–1). "), B("Global cognition:"), N(" the average of the three domain z scores, rescaled. The sixth wave comprised a 2021 main visit and 2022/2023 supplementary visits; the 2023 file lacked the first serial-7 answer, so that component was prorated from items 2–5 (×5/4); sixth-wave TICS means were continuous with 2021 values. To ensure cross-wave comparability given differing word lists and changing age structure, scores were standardized within each interview year as residuals from a regression on age (natural spline, 3 df), education (3 levels), and sex, scaled to unit variance; a sensitivity analysis used baseline (2011) mean/SD standardization instead. Incident PSCI was defined as a post-event memory z ≤ −1 SD among participants whose pre-anchor measurements were all > −1 SD. This pragmatic single-domain definition is narrower than consensus criteria for vascular cognitive impairment (e.g., VASCOG)"), C("10"),
           N("; a global-cognition-based definition (global z ≤ −1 or −1.5 SD) was examined as sensitivity analysis S10.")])
h2(doc, "Covariates")
para(doc, "Baseline (2011) covariates: age, sex, education, marital status, depressive symptoms (CES-D 10), smoking, drinking frequency (missing n=26 assigned to \u201cnone\u201d), physician-diagnosed hypertension, dyslipidemia, diabetes, heart disease, and measured body mass index (indicator variable for missingness; multiple imputation in S9).")
h2(doc, "Statistical analysis")
para(doc, [N("Piecewise linear mixed-effects models were fitted with time anchored at stroke onset (τ = assessment year − event year). Following the parameterization used in the HRS and COSMIC analyses"), C("4,5"),
           N(", the model included a background linear slope (τ), a step term switching from 0 to 1 at stroke onset (the acute change; primary hypothesis), and interactions of stroke status with pre-anchor (min(τ,0)) and post-anchor (max(τ,0)) slopes, plus covariates and participant-level random intercepts and slopes; P values are Wald z approximations. Non-stroke participants received pseudo-anchor times drawn from the case event-time distribution; stability was verified over 20 independent draws (Supplementary Material 1, Table S5). A continuous-spline (level-shift) parameterization, constraining the trajectory to be continuous at the anchor, was compared by AIC (S11). Sex, baseline-age-group (<65 vs ≥65 years), and education differences were tested with 3-df interaction terms, complemented by step-specific 1-df Wald tests. Incident PSCI was analyzed with Fine–Gray subdistribution hazard models (death as competing event)"), C("11"),
           N(", adjusting for baseline age, sex, and education; a sensitivity model (S12) adjusted for the full covariate set using the Fine–Gray weighting implementation with cluster-robust standard errors. Participants entered the PSCI risk set at the anchor only if ≥1 post-anchor measurement was available; event-free survivors were censored at their last post-anchor measurement, and deaths were treated as competing events. Cumulative incidence functions were estimated at 2, 5, and 8 years; the proportional subdistribution hazards assumption was tested with a stroke × log(time) interaction; E-values quantified robustness to unmeasured confounding"), C("12"),
           N(" (reported with the conventional RR ≈ √HR approximation because the outcome is not rare). Sensitivity analyses (definitions in Supplementary Material 1, Table S3): (S1) midpoint-only event timing; (S2) excluding 2015–2018-interval events; (S3) pre-2020 events only; (S4) BMI-complete cases; (S5) demographics-only adjustment; (S6) first sixth-wave assessment only; (S7) baseline-distribution standardization; (S8) excluding 26 possible recurrent strokes; (S9) multiple imputation of baseline covariates (m=20)"), C("13"),
           N("; (S10) a global-cognition-based PSCI definition; (S11) the continuous-spline parameterization; (S13) adjustment for testing occasion (practice effects). S7 and S11 alter the outcome scale or parameterization; the remaining nine analyses (S1–S6, S8, S9, S13) are scale-comparable. Estimates other than the primary hypothesis are nominal without multiplicity adjustment. Analyses were unweighted: CHARLS sampling weights are baseline-defined and do not extend to longitudinal trajectories. Primary-model Pearson residuals were approximately symmetric (skewness 0.08, excess kurtosis 0.25); 5 of 55,897 observations exceeded 4 SD, and refitting without them left the acute estimate unchanged (−0.191 vs −0.192 SD). Analyses used R 4.6.2 (lme4, cmprsk, mice). Two-sided P<0.05 was considered significant.")])

h1(doc, "Results")
h2(doc, "Cohort and incident stroke")
para(doc, "Of 16,364 baseline participants (mean age 59.2±9.8 years; 51.3% women), 1,346 (8.2%) experienced an incident stroke over a median follow-up of 12.0 years (182,962 person-years, ≈11.2 years per participant; 2,463 deaths; stroke incidence 7.4 per 1,000 person-years). Mean age at stroke was 66.8±8.9 years (median event year 2017); 628 events (46.7%) had diagnosis-year refinement. Stroke survivors contributed a median of 4 (IQR 4–5) cognitive measurements; 1,106 (82.2%) had at least one pre- and one post-stroke measurement, and 462 (34.3%) had ≥2 in each phase. Stroke survivors were older and had more hypertension, diabetes, dyslipidemia, and heart disease at baseline than stroke-free participants; sex did not differ (P=0.97; Table 1).")
h2(doc, "Peri-stroke trajectory with an acute step")
para(doc, "Two conventions dominate this literature. Under the continuous-spline (level-shift) parameterization, the pre- and post-stroke slopes are forced to meet at the event, so an abrupt peri-event drop is absorbed into the slope estimates; under the step parameterization, a discontinuity at stroke onset separates the acute drop from the slopes. The two conventions answer different questions, and the choice moves acute-effect estimates substantially.")
para(doc, [N("The step parameterization fitted better than the continuous-spline parameterization (ΔAIC ≈ 17 for memory and ≈ 14 for global cognition). In stroke-free participants, memory declined by −0.0137 SD/year (95% CI −0.0156 to −0.0117). Incident stroke was associated with an acute step at stroke onset (primary hypothesis) of −0.192 SD (95% CI −0.262 to −0.122; P=7.9×10⁻⁸); a pre-stroke slope difference of +0.012 SD/year (95% CI 0.004 to 0.019; P=0.003)—decline did not accelerate before stroke; the positive sign is more plausibly explained by practice effects and selective retention (Discussion); and a post-stroke slope difference of +0.011 SD/year (95% CI −0.008 to 0.029; P=0.248), i.e., no post-stroke acceleration (Table 2, Figures 1 and 2).")])
para(doc, [N("Acute step declines were consistent across domains: immediate recall −0.206 SD, delayed recall −0.132 SD, TICS-10 −0.149 SD (P=0.0015), visuospatial ability −0.098 SD (P=0.033), and global cognition −0.215 SD (P=5.2×10⁻⁶). No domain showed post-stroke acceleration (post-stroke slope differences: TICS-10 −0.009 SD/year, P=0.49; global +0.002 SD/year, P=0.89). Refitting the memory model within the TICS-available sample (n=9,757) yielded a similar acute step (−0.227 SD, P=5.2×10⁻⁸), indicating the domain contrast is not attributable to sample composition.")])
h2(doc, "Subgroups and effect modification")
para(doc, "The acute memory step did not differ significantly by sex, age group, or education (step-specific interaction P=0.62, 0.42, and 0.61; 3-df joint P=0.85 and 0.81 for sex and age): women −0.179 SD, men −0.207 SD; baseline age <65 years −0.217 SD, ≥65 years −0.116 SD; no formal education −0.236 SD, any formal education −0.178 SD (Figure 3). Subgroup confidence intervals are wide—the age-stratified point estimates differ two-fold—so smaller subgroup differences cannot be excluded.")
h2(doc, "Incident PSCI: relative and absolute risk under competing mortality")
para(doc, "Among 7,308 participants cognitively intact before their anchor time and with ≥1 post-anchor measurement (Supplementary Material 2), 1,596 developed incident PSCI and 309 died as competing events; because the risk set conditions on ≥1 post-anchor assessment, deaths before first post-anchor contact are not captured. Stroke survivors had a 41% higher subdistribution hazard of PSCI (adjusted sHR 1.41, 95% CI 1.21–1.64; Gray test P=0.0004); at the stricter −1.5-SD threshold (565 events, 434 competing deaths), the association was similar (sHR 1.42, 95% CI 1.10–1.85). The proportional subdistribution hazards assumption was supported (stroke × log(time) P=0.47). The E-value was 2.17 (1.72 for the lower confidence bound) treating the sHR as a risk ratio, and 1.66 (1.43) after the √HR approximation for a non-rare outcome. In absolute terms, cumulative PSCI incidence among stroke survivors reached 13.1% at 2 years, 27.6% at 5 years, and 43.1% at 8 years, versus 10.3%, 22.4%, and 33.4% in stroke-free participants—an absolute excess of ≈5 percentage points at 5 years (Figure 4; estimates beyond 6 years rest on fewer than 200 at-risk stroke survivors). Full covariate adjustment (S12; n=6,857) left the association unchanged (sHR 1.42, 95% CI 1.20–1.67). With a multidomain (global-cognition) definition, associations were concordant: sHR 1.33 (95% CI 1.07–1.66) at z ≤ −1 SD (5-year incidence 26.7% vs 19.0%) and 1.85 (1.40–2.43) at z ≤ −1.5 SD (16.9% vs 7.8%; Supplementary Material 1, Table S2).")
h2(doc, "Sensitivity analyses")
para(doc, "The acute memory step was robust (S1–S9): midpoint-only event timing −0.217 SD; excluding 2015–2018-window events −0.252 SD; pre-2020 events −0.204 SD; BMI-complete cases −0.218 SD; demographics-only adjustment −0.192 SD; first sixth-wave assessment only −0.193 SD; excluding 26 possible recurrent strokes −0.191 SD; multiple imputation (m=20; 16,331 participants with memory measures) −0.181 SD (95% CI −0.248 to −0.115). Over 20 independent pseudo-anchor draws, the step estimate ranged from −0.195 to −0.191 SD for memory (all P≤9×10⁻⁸) and from −0.216 to −0.214 SD for global cognition (all P≤5.8×10⁻⁶). Under the continuous-spline parameterization (S11), the same data yielded an acute level shift of −0.096 SD—numerically approximating the earlier CHARLS estimate. With conventional baseline-distribution standardization (S7), the step estimate was −0.445 SD for memory and −0.172 SD for global cognition, illustrating that standardization conventions also move estimates substantially. Adjusting for testing occasion (S13) left the acute step (−0.188 SD) and the pre-stroke slope difference (+0.012 SD/year, P=0.003) essentially unchanged, while later occasions were associated with lower, not higher, scores (−0.039 SD per occasion, P=2.4×10⁻¹¹), arguing against practice effects as the source of the positive pre-stroke slope difference (Supplementary Material 1, Table S3).")

h1(doc, "Discussion")
h2(doc, "Principal findings")
para(doc, "This study set out to explain why estimated acute cognitive effects of stroke differ two-fold between Chinese (≈−0.12 SD) and international (≈−0.25 SD) cohorts. Within a single dataset we approximated both figures: the continuous level-shift specification yielded −0.096 SD, numerically close to the earlier CHARLS report, whereas the step parameterization used by the HRS and COSMIC analyses yielded −0.192 SD. Analytic conventions can therefore account for much of the observed East–West spread, although residual population differences cannot be excluded. Substantively, incident stroke in this 12-year nationally representative cohort was followed by an acute, multidomain step decline in cognition (≈0.1–0.2 SD, largest for global cognition and immediate recall), with no evidence that decline accelerates before or after the event once the acute step is modeled explicitly. Stroke survivors carried a 41–42% higher subhazard of crossing the cognitive-impairment threshold—more than one in four survivors remaining under cognitive follow-up versus 22.4% of stroke-free participants impaired by 5 years—after accounting for competing mortality.")
h2(doc, "Comparison with previous work")
para(doc, [N("Our primary acute memory estimate (−0.192 SD) sits between the earlier CHARLS estimate (−0.123 SD) and the international pooled estimate (−0.25 SD; COSMIC), and we can account for most of this spread within our own data. First, parameterization: the continuous-spline (level-shift) specification blends the acute jump into the slope terms (−0.096 SD in our data, approximating the earlier Chinese estimate), whereas the step specification used by Levine et al. and COSMIC separates it (−0.192 SD; ΔAIC ≈ 17)."), C("4,5,7"),
           N(" Second, standardization: baseline-distribution standardization (S7) inflated the step to −0.445 SD, plausibly because cross-wave test-form differences (e.g., changing word lists) leak in; we therefore designated within-wave standardization as primary. Analytic conventions can thus generate much of the apparent East–West difference, but population differences are not excluded: we could not re-derive earlier analytic pipelines, and baseline-distribution standardization moved the memory estimate beyond, not toward, the international pooled figure.")])
para(doc, [N("Our null findings on slopes align with COSMIC"), C("5"), N(" and the earlier CHARLS analysis"), C("7"), N(" (no pre-stroke slope difference) but contrast with the English Longitudinal Study of Ageing"), C("6"), N(" and a recent multi-cohort study"), C("8"), N(", which reported accelerated pre-stroke decline. Adjustment for testing occasion did not attenuate the positive pre-stroke slope differences (S13), arguing against practice effects"), C("14"),
           N(" as their sole explanation; selective participation of lower-functioning individuals in earlier waves and interval-censored event timing remain possible explanations. These differences should be read as absence of evidence for acceleration, not as a protective trend. Likewise, we did not reproduce the small post-stroke acceleration reported in HRS-based analyses (−0.038 SD/year in COSMIC); the 95% CI for the post-stroke slope difference excludes additional accelerations larger than ≈0.008 SD/year in memory, whereas accelerations up to ≈0.033 SD/year cannot be excluded in orientation/calculation."), C("4,5"),
           N(" In a 2025 pooled analysis of four US cohorts, ischemic stroke survivors declined ≈0.035 SD/year in global cognition after the event; without a stroke-free comparison group, such absolute decline cannot be separated from background aging, which in our data accounted for the post-event slope."), C("15"),
           N(" Finally, our PSCI analysis extends the REGARDS finding of elevated incident cognitive impairment after stroke"), C("16"),
           N(" by providing subdistribution hazard ratios and absolute cumulative incidence under competing mortality—quantities directly usable for planning cognitive surveillance after stroke. By comparison, a multicenter Chinese hospital study using a brief multidomain screen found 78.7% of first-ever ischemic stroke patients impaired"), C("17"),
           N("; our lower 5-year cumulative incidence (27.6%) reflects the community-dwelling sample, longer ascertainment intervals, and single-domain threshold.")])
h2(doc, "Mechanistic and clinical implications")
para(doc, [N("The trajectory shape—a one-time multidomain step down, with subsequent decline proceeding at the background age-related rate—supports a model in which the stroke lesion delivers an acute insult whose direct cognitive consequence does not progressively compound, at least at the resolution of biennial testing."), C("18,19"),
           N(" Clinically, the burden is carried by the acute step and the elevated threshold-crossing risk: more than one in four survivors under cognitive follow-up met the PSCI criterion within 5 years despite competing mortality; these data support incorporating cognitive assessment into post-stroke follow-up, as guidelines recommend"), C("20"),
           N(", although whether systematic screening improves outcomes was not tested.")])
h2(doc, "Strengths and limitations")
para(doc, [N("Strengths include the 12-year span with five cognitive waves—the longest single-cohort peri-stroke trajectory mapping in an Asian population and the first to use the 2021–2023 CHARLS wave—more than twice the incident events of previous CHARLS reports, diagnosis-year-refined event timing, domain-specific outcomes, a formally fit-compared step parameterization, absolute and relative PSCI risks under competing mortality with E-values, a 13-analysis sensitivity program with pseudo-anchor validation, and fully adjusted competing-risk models (S12). The most recent CHARLS analysis of cognitive decline in stroke was restricted to the 2011 and 2020 waves and 101 prevalent cases, underscoring the incremental value of the present design."), C("21")])
para(doc, [N("Limitations: (1) Stroke was self-reported physician diagnosis without subtype, severity, or imaging; misclassification would bias acute effects toward the null. (2) Event and PSCI onset are interval-censored between biennial waves: the step term captures the drop occurring anywhere within the first post-stroke interval, short-term incidence approximates impairment at first post-stroke contact, and transient peri-stroke improvement cannot be resolved"), C("20"), N("; robustness to midpoint imputation and pseudo-anchor reassignment was shown. (3) Attrition and competing death likely bias post-stroke slopes toward the null—survivors without post-stroke measurements were older, cognitively lower at baseline, and had nearly threefold higher mortality (Supplementary Material 1, Table S4)—and the PSCI risk set conditions on surviving to first post-anchor contact. (4) The battery lacks processing-speed measures, the visuospatial domain rests on a single binary item, and PSCI was defined by a pragmatic single-domain threshold, though the global-cognition definition yielded concordant associations. (5) Undercounted recurrent strokes, residual practice effects, unweighted estimation, and unmeasured confounding cannot be excluded, although recurrent-stroke exclusion, occasion adjustment (S13), and E-value analyses argued against major distortion.")])
h2(doc, "Conclusions")
para(doc, "In Chinese adults aged ≥45 years, incident stroke was associated with an acute multidomain cognitive step decline of a magnitude approaching international pooled estimates, without measurable acceleration of decline before or after the event, and with a 41–42% higher subhazard of incident cognitive impairment despite competing mortality. Much of the apparent East–West gap in acute-effect magnitude can arise from parameterization and standardization conventions, without excluding residual population differences. These findings support systematic post-stroke cognitive surveillance and harmonized analytic standards for cross-cohort comparison.")

# ---------- DECLARATIONS (SAGE/IJS style) ----------
h1(doc, "Acknowledgements")
para(doc, "The authors thank the CHARLS research team and all participants.")

h2(doc, "Author contributions")
para(doc, "Gan Zhang: Conceptualization, Methodology, Formal analysis, Writing – original draft. Can Sun: Methodology, Formal analysis, Data curation, Writing – original draft. Qingli Sun: Investigation, Data curation, Writing – review & editing. Yong Chen: Conceptualization, Supervision, Funding acquisition, Writing – review & editing. All authors read and approved the final manuscript.")
h2(doc, "Declaration of conflicting interests")
para(doc, "The authors declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article.")
h2(doc, "Funding")
para(doc, "The authors disclosed receipt of the following financial support for the research, authorship, and/or publication of this article: the Peking University Medicine Sailing Program for Young Scholars' Scientific & Technological Innovation (grant number BMU2021PYB040) to Yong Chen.")
h2(doc, "Ethics approval and consent to participate")
para(doc, "CHARLS was approved by the Biomedical Ethics Review Committee of Peking University (IRB00001052-11015), and written informed consent was obtained from all participants at enrolment.")
h2(doc, "Data availability statement")
para(doc, "CHARLS data are available to registered researchers at https://charls.pku.edu.cn. Analysis code is available from the corresponding author on reasonable request.")

# ---------- REFERENCES (Sage Vancouver: numbered, ≤3 authors then et al.) ----------
h1(doc, "References")
refs = [
 "GBD 2019 Stroke Collaborators. Global, regional, and national burden of stroke and its risk factors, 1990–2019: a systematic analysis for the Global Burden of Disease Study 2019. Lancet Neurol 2021; 20: 795–820.",
 "Pendlebury ST and Rothwell PM. Incidence and prevalence of dementia associated with transient ischaemic attack and stroke: analysis of the population-based Oxford Vascular Study. Lancet Neurol 2019; 18: 248–258.",
 "Feigin VL, Brainin M, Norrving B, et al. World Stroke Organization: Global Stroke Fact Sheet 2025. Int J Stroke 2025; 20: 132–144.",
 "Levine DA, Galecki AT, Langa KM, et al. Trajectory of cognitive decline after incident stroke. JAMA 2015; 314: 41–51.",
 "Lo JW, Crawford JD, Lipnicki DM, et al. Trajectory of cognitive decline before and after stroke in 14 population cohorts. JAMA Netw Open 2024; 7: e2437133.",
 "Zheng F, Yan L, Zhong B, et al. Progression of cognitive decline before and after incident stroke. Neurology 2019; 93: e20–e28.",
 "Hua J, Dong J, Chen GC, et al. Trends in cognitive function before and after stroke in China. BMC Med 2023; 21: 204.",
 "Cai Y, Duan C, Wen S, et al. Progression of cognitive and functional decline before and after stroke: evidence from four prospective cohort studies across 23 countries. J Neurol 2025; 272: 779.",
 "Zhao Y, Hu Y, Smith JP, et al. Cohort profile: the China Health and Retirement Longitudinal Study (CHARLS). Int J Epidemiol 2014; 43: 61–68.",
 "Sachdev P, Kalaria R, O'Brien J, et al. Diagnostic criteria for vascular cognitive disorders: a VASCOG statement. Alzheimer Dis Assoc Disord 2014; 28: 206–218.",
 "Fine JP and Gray RJ. A proportional hazards model for the subdistribution of a competing risk. J Am Stat Assoc 1999; 94: 496–509.",
 "VanderWeele TJ and Ding P. Sensitivity analysis in observational research: introducing the E-value. Ann Intern Med 2017; 167: 268–274.",
 "van Buuren S and Groothuis-Oudshoorn K. mice: multivariate imputation by chained equations in R. J Stat Softw 2011; 45: 1–67.",
 "Calamia M, Markon K and Tranel D. Scoring higher the second time around: meta-analyses of practice effects in neuropsychological assessment. Clin Neuropsychol 2012; 26: 543–570.",
 "Levine DA, Whitney RT, Ye W, et al. Associations between stroke type, ischemic stroke subtypes, and poststroke cognitive trajectories. Stroke 2025; 56: 898–907.",
 "Levine DA, Wadley VG, Langa KM, et al. Risk factors for poststroke cognitive decline: the REGARDS study. Stroke 2018; 49: 987–994.",
 "He A, Wang Z, Wu X, et al. Incidence of post-stroke cognitive impairment in patients with first-ever ischemic stroke: a multicenter cross-sectional study in China. Lancet Reg Health West Pac 2023; 33: 100687.",
 "Rost NS, Brodtmann A, Pase MP, et al. Post-stroke cognitive impairment and dementia. Circ Res 2022; 130: 1252–1271.",
 "Iadecola C, Duering M, Hachinski V, et al. Vascular cognitive impairment and dementia: JACC Scientific Expert Panel. J Am Coll Cardiol 2019; 73: 3326–3344.",
 "El Husseini N, Katzan IL, Rost NS, et al. Cognitive impairment after ischemic and hemorrhagic stroke: a scientific statement from the American Heart Association/American Stroke Association. Stroke 2023; 54: e272–e291.",
 "Zhang J, Wang Z, Wu Y, et al. Comparison of cognitive decline rates and risk factors between stroke and non-stroke populations: an analysis of data from the China Health and Retirement Longitudinal Study (CHARLS). Cereb Circ Cogn Behav 2026; 11: 100554.",
]
for i, r in enumerate(refs, 1):
    p = para(doc, f"{i}. {r}", justify=False)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p.paragraph_format.space_after = Pt(4)

# ---------- FIGURE LEGENDS ----------
h1(doc, "Figure legends")
para(doc, [B("Figure 1. "), N("Model-predicted peri-stroke cognitive trajectories by domain ((A) episodic memory; (B) orientation/calculation; (C) visuospatial ability; (D) global cognition) under the step parameterization, stroke survivors versus stroke-free participants. Acute step estimates (95% CI) are annotated; the vertical segment at τ=0 is the modelled acute drop. Curves are shifted so the incident-stroke group equals 0 at τ=−10.")], justify=False)
para(doc, [B("Figure 2. "), N("Observed domain z scores (mean ± 95% CI) by time to/from stroke (1-year bins; domains as in Figure 1); stroke-free participants use pseudo-anchor times from the case event-time distribution. Per-bin, per-group sample sizes are shown below each panel; points based on fewer than 100 observations are faded.")], justify=False)
para(doc, [B("Figure 3. "), N("Acute memory step at stroke onset across the primary model, subgroups, and sensitivity analyses S1–S9, S11 and S13 (definitions in Methods; S10 in Supplementary Material 1, Table S2). Points: estimates; whiskers: 95% CI.")], justify=False)
para(doc, [B("Figure 4. "), N("Cumulative incidence of post-stroke cognitive impairment (memory z ≤ −1 SD) among stroke survivors versus stroke-free participants, accounting for the competing risk of death (adjusted subdistribution hazard ratio 1.41, 95% CI 1.21–1.64). Event-free participants are censored at last assessment; curves truncate at 8 years (numbers at risk below; estimates beyond 6 years rest on fewer than 200 at-risk stroke survivors).")], justify=False)

# ---------- SUPPLEMENTARY CAPTIONS ----------
h1(doc, "Supplementary Material captions")
para(doc, [B("Supplementary Material 1 "), N("(PDF): Tables S1–S5 (inclusion/exclusion comparison; Fine–Gray results by outcome definition; sensitivity analyses S1–S13; attrition comparison; pseudo-anchor draws).")], justify=False)
para(doc, [B("Supplementary Material 2 "), N("(PDF): Fig. S1, STROBE participant flow diagram, including the PSCI analysis branch.")], justify=False)

doc.save(os.path.join(SUB, "Manuscript_IJS.docx"))
print("manuscript ok")

# ============================================================
# 2. COVER LETTER (International Journal of Stroke)
# ============================================================
cl = Document(); set_style(cl)
cl.styles["Normal"].paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
para(cl, "22 November 2026", justify=False)
para(cl, "", justify=False)
para(cl, "The Editors\nInternational Journal of Stroke", justify=False)
para(cl, "", justify=False)
para(cl, "Dear Editors,", justify=False)
para(cl, "We are pleased to submit our Research Article entitled \u201cCognitive trajectories and risk of cognitive impairment after incident stroke: a 12-year nationwide cohort study in China\u201d for consideration in the International Journal of Stroke.", justify=False)
para(cl, "How cognition evolves around a first stroke remains unresolved in Asian populations, and acute-effect estimates differ two-fold between Chinese (≈−0.12 SD) and international cohorts (≈−0.25 SD) for reasons never formally dissected. Using the full 12-year follow-up of the nationally representative CHARLS cohort (five cognitive waves, including the previously unused 2021–2023 wave, more than doubling prior CHARLS event counts), we show within a single dataset that much of this East–West gap can be generated analytically: a continuous level-shift specification approximates the earlier Chinese estimate (−0.096 SD), whereas the step parameterization used by the HRS and COSMIC analyses yields an acute memory decline of −0.192 SD—approaching the international pooled figure—with clearly better model fit. We further provide absolute risks of post-stroke cognitive impairment under competing mortality in this setting: more than one in four stroke survivors under cognitive follow-up crossed the cognitive-impairment threshold within 5 years (27.6% vs 22.4%; adjusted subdistribution hazard ratio 1.41), with no acceleration of decline before or after the event once the acute step is modelled.", justify=False)
para(cl, "We believe these results are well suited to the International Journal of Stroke's readership: they harmonize apparently conflicting evidence across Chinese and Western stroke cohorts, and they quantify an absolute cognitive-risk burden directly relevant to the follow-up care of stroke survivors.", justify=False)
para(cl, "The manuscript is original, has not been published previously, and is not under consideration by any other journal. All authors have read and approved the submission and declare no competing interests. CHARLS was approved by the Biomedical Ethics Review Committee of Peking University (IRB00001052-11015), and all participants provided written informed consent. The study is reported in accordance with the STROBE guideline (checklist enclosed).", justify=False)
para(cl, "", justify=False)
para(cl, "Yours sincerely,", justify=False)
para(cl, "Yong Chen, on behalf of all authors\nDepartment of Neurology, Peking University Third Hospital\nNo. 49 North Garden Road, Haidian District, Beijing 100191, China\nE-mail: ronaldchen@bjmu.edu.cn; Tel: +86-18810975103; Fax: +86-10-82266699", justify=False)
cl.save(os.path.join(SUB, "Cover_Letter_IJS.docx"))
print("cover letter ok")

# ============================================================
# 3. STROBE CHECKLIST
# ============================================================
st = Document(); set_style(st)
st.styles["Normal"].paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
st.styles["Normal"].font.size = Pt(10)
h1(st, "STROBE Statement—Checklist of items for cohort studies")
para(st, [B("Manuscript: "), N("Cognitive trajectories and risk of cognitive impairment after incident stroke: a 12-year nationwide cohort study in China")], justify=False)
items = [
 ("Title and abstract", "1", "(a) Design in title/abstract: 'nationwide cohort study'; (b) structured abstract", "Title; Abstract"),
 ("Background/rationale", "2", "Scientific background and rationale", "Introduction, para 1–2"),
 ("Objectives", "3", "Three prespecified objectives and primary hypothesis", "Aims and hypothesis"),
 ("Study design", "4", "Prospective cohort (secondary analysis)", "Methods – Study population"),
 ("Setting", "5", "CHARLS, nationwide China, 2011–2023; 2020 wave had no cognitive measures", "Methods – Study population"),
 ("Participants", "6", "Eligibility criteria; sampling; flow incl. PSCI branch in Supplementary Material 2", "Methods – Study population; Supplementary Material 2"),
 ("Variables", "7", "Outcomes, exposure, covariates defined; PSCI definition vs VASCOG discussed", "Methods – Cognitive assessment; Covariates"),
 ("Data sources/measurement", "8", "Cognitive battery, stroke ascertainment, death via exit interviews (midpoint-imputed)", "Methods"),
 ("Bias", "9", "Interval censoring, attrition, misclassification, multiple comparisons addressed", "Statistical analysis; Sensitivity analyses; Limitations"),
 ("Study size", "10", "All eligible participants used; N=16,364", "Results – Cohort"),
 ("Quantitative variables", "11", "Z-score standardization; thresholds −1/−1.5 SD", "Methods – Cognitive assessment"),
 ("Statistical methods", "12", "Piecewise LMM with step term (AIC-compared vs spline); Fine–Gray with last-assessment censoring + proportionality test; E-values incl. √HR approximation; S1–S12 incl. multiple imputation (m=20) and fully adjusted Fine–Gray models", "Methods – Statistical analysis"),
 ("Participants (results)", "13", "Numbers at each stage; reasons for non-participation", "Results – Cohort; Supplementary Material 2"),
 ("Descriptive data", "14", "Baseline characteristics by stroke status", "Table 1"),
 ("Outcome data", "15", "1,346 incident strokes; 1,596 PSCI events; 309 competing deaths", "Results"),
 ("Main results", "16", "Estimates with 95% CI; primary hypothesis designated, others nominal", "Table 2; Results"),
 ("Other analyses", "17", "Subgroups with formal interaction tests, sensitivity analyses incl. MI, global-PSCI definition, and fully adjusted competing-risk models (S12)", "Results; Figure 3"),
 ("Key results (discussion)", "18", "Summarised with reference to objectives", "Discussion – Principal findings"),
 ("Limitations", "19", "Five core limitations with direction of bias", "Discussion – Strengths and limitations"),
 ("Interpretation", "20", "Cautious interpretation considering objectives and bias", "Discussion"),
 ("Generalisability", "21", "Chinese adults ≥45; external validity discussed", "Discussion"),
 ("Funding", "22", "Funding statement included", "Declarations"),
]
table = st.add_table(rows=1, cols=3)
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr = table.rows[0].cells
for c, t in zip(hdr, ["Item", "No", "Recommendation / where reported"]):
    c.paragraphs[0].add_run(t).bold = True
for name, no, rec, loc in items:
    row = table.add_row().cells
    row[0].text = name; row[1].text = no
    row[2].text = f"{rec} — {loc}"
st.save(os.path.join(SUB, "STROBE_checklist_IJS.docx"))
print("strobe ok")

# ============================================================
# 4. Figures as TIFF (600 dpi) + Tables.docx copy + reviewers copy
# ============================================================
figmap = [
 (r"figures\Fig1_trajectory_EN.png", "Fig1.tif"),
 (r"figures\Fig2_observed_EN.png", "Fig2.tif"),
 (r"figures\Fig3_forest_acute_EN.png", "Fig3.tif"),
 (r"figures\Fig4_cif_psci_EN.png", "Fig4.tif"),
]
for src, dst in figmap:
    im = PILImage.open(os.path.join(BASE, src)).convert("RGB")
    im.save(os.path.join(SUB, dst), dpi=(600, 600), compression="tiff_lzw")
    print("tiff ok:", dst)
shutil.copy2(os.path.join(BASE, r"manuscript\Tables.docx"), os.path.join(SUB, "Tables.docx"))
print("tables copy ok")
src_rev = os.path.join(BASE, "submission_JNeurol", "Suggested_Reviewers_JNeurol.docx")
if os.path.exists(src_rev):
    shutil.copy2(src_rev, os.path.join(SUB, "Suggested_Reviewers_IJS.docx"))
    print("reviewers copy ok")

# ============================================================
# 5. Word counts + citation-order check
# ============================================================
import re
from docx import Document as _D
d = _D(os.path.join(SUB, "Manuscript_IJS.docx"))
txts = [p.text for p in d.paragraphs]
total_wc = sum(len(t.split()) for t in txts)
i0 = txts.index("Abstract")
iak = next(i for i in range(i0, len(txts)) if txts[i].startswith("Keywords"))
abs_wc = sum(len(t.split()) for t in txts[i0 + 1:iak])
print("MANUSCRIPT WORDS (excl. tables file):", total_wc)
print("ABSTRACT WORDS (incl. headings + data access, excl. keywords):", abs_wc)
# citation first-appearance order check (superscript runs)
d2 = _D(os.path.join(SUB, "Manuscript_IJS.docx"))
first_seen = []
for p in d2.paragraphs:
    if p.text.strip().startswith(tuple(f"{i}." for i in range(1, 30))):
        continue  # skip reference list
    for r in p.runs:
        if r.font.superscript and r.text.strip():
            for tok in re.split(r"[,–]", r.text.strip()):
                tok = tok.strip()
                if tok.isdigit() and int(tok) not in first_seen:
                    first_seen.append(int(tok))
print("CITATION FIRST-APPEARANCE ORDER:", first_seen)
print("ORDER OK" if first_seen == sorted(first_seen) else "!!! ORDER PROBLEM")
