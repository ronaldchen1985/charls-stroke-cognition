# -*- coding: utf-8 -*-
"""Build International Journal of Stroke (SAGE) submission package:
manuscript docx (Sage Vancouver superscript citations, IJS structure with
separate Aims section, Data access statement in abstract), cover letter,
STROBE checklist, TIFF figures, Supplementary Material PDFs.
2026-11-22 v3: full pipeline rebuild after (a) adding the 2020 cognitive wave
(Health Status module) and (b) fixing word-recall scoring (all-NA -> NA;
2018 HCAP word-list slot counting). All numbers = 2026-11-22 rerun.
Narrative change: East-West attribution narrowed — conventions move estimates
materially but no convention reproduces the international pooled magnitude."""
import os, shutil
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from PIL import Image as PILImage

BASE = r"D:\CHARLS\PSCI_traj"
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
para(doc, [B("Total word count (incl. abstract, references, legends, tables): "), N("4,995"),
           B("    Abstract word count: "), N("250")], justify=False)
para(doc, [B("Tables: "), N("2"), B("    Figures: "), N("4"),
           B("    Supplementary Material: "), N("Supplementary Material 1 (Tables S1–S5); Supplementary Material 2 (Fig. S1)")], justify=False)
doc.add_page_break()

# ---------- ABSTRACT (IJS structured: Background/Aims/Methods/Results/Conclusions + Data access) ----------
h1(doc, "Abstract")
para(doc, [B("Background: "), N("How cognition evolves around a first stroke, and survivors' excess impairment risk, is incompletely characterized in Asian populations; acute-effect estimates differ two-fold between Chinese and international cohorts.")])
para(doc, [B("Aims: "), N("We mapped domain-specific peri-stroke cognitive trajectories and quantified post-stroke cognitive impairment (PSCI) risk under competing mortality.")])
para(doc, [B("Methods: "), N("We analyzed 16,364 stroke-free participants aged ≥45 years from the China Health and Retirement Longitudinal Study (2011–2023; six cognitive waves). Domain scores were standardized within each interview year. Piecewise linear mixed models anchored at stroke onset estimated an acute step and pre-/post-stroke slope differences. Incident PSCI (memory z ≤ −1 SD) was analyzed with Fine–Gray models (death as competing event).")])
para(doc, [B("Results: "), N("Among 13,974 participants (1,187 incident strokes), stroke was followed by acute step declines in memory (−0.122 SD, 95% CI −0.186 to −0.058), orientation/calculation (−0.175 SD), visuospatial ability (−0.092 SD) and global cognition (−0.186 SD), without accelerated decline before or after the event. The acute memory estimate was robust across nine scale-comparable sensitivity analyses (−0.115 to −0.140 SD). Stroke survivors had a 26% higher subhazard of PSCI (subdistribution hazard ratio 1.26, 95% CI 1.08–1.47); 5-year cumulative incidence was 26.5% versus 23.5%.")])
para(doc, [B("Conclusions: "), N("Incident stroke was followed by an acute, multidomain cognitive step decline without measurable pre- or post-event acceleration, and modestly elevated long-term impairment risk. Acute-effect estimates moved materially with parameterization and standardization choices yet remained below international pooled estimates; the apparent East–West difference is unlikely to arise from analytic conventions alone.")])
para(doc, [B("Data access statement: "), N("CHARLS data are available to registered researchers at https://charls.pku.edu.cn.")])
para(doc, [B("Keywords: "), N("stroke; cognition; memory; post-stroke cognitive impairment; cohort study; China")])
doc.add_page_break()

# ---------- MAIN TEXT ----------
h1(doc, "Introduction")
para(doc, [N("Stroke is the leading cause of death and adult disability in China, and post-stroke cognitive impairment (PSCI) affects up to one-third of survivors within the first year, worsening functional recovery, quality of life, and dementia risk."), C("1–3"),
           N(" Two questions remain incompletely answered. First, when cognition deteriorates relative to stroke onset—before, at, or after the event—is contested, with implications for whether prevention should target pre-stroke risk control or post-stroke monitoring. Second, trajectory studies have described mean cognitive changes but rarely translated them into the quantity clinicians need: the excess risk of crossing a cognitive-impairment threshold after stroke, accounting for competing mortality.")])
para(doc, [N("In the REGARDS study, incident stroke was followed by an acute cognitive drop and accelerated decline thereafter."), C("4"),
           N(" A 2024 individual-participant meta-analysis of 14 population cohorts (COSMIC) confirmed a substantial acute decline (−0.25 SD in global cognition) and a small post-stroke acceleration (−0.038 SD/year), but found no pre-stroke slope difference"), C("5"),
           N(". Evidence in Chinese populations is conflicting: a CHARLS analysis of 2011–2015 data reported significantly faster pre-stroke decline"), C("6"),
           N(", whereas a larger CHARLS analysis of 2011–2018 data found no pre-stroke difference but domain-specific post-stroke acceleration"), C("7"),
           N(". Most recently, a four-cohort study across 23 countries reported significant pre-stroke acceleration and showed that recurrent stroke materially inflates acute-effect estimates."), C("8"),
           N(" Notably, acute-effect estimates are two-fold smaller in Chinese cohorts (≈−0.12 SD) than in international pooled analyses (≈−0.25 SD)—a gap that could reflect biology, standardization, or model parameterization, but has never been formally dissected. No study has used the full 12-year CHARLS follow-up including the 2020 and 2021–2023 waves—more than doubling prior CHARLS incident events—or quantified incident PSCI under competing mortality in this setting.")])

h1(doc, "Aims and hypothesis")
para(doc, "Using all six cognitive waves of CHARLS (2011–2023), we aimed to (1) determine how model parameterization and standardization conventions contribute to the two-fold East–West difference in acute-effect estimates; (2) decompose the peri-stroke trajectories of four cognitive domains into pre-stroke slope, acute step, and post-stroke slope; and (3) quantify absolute and relative risks of incident PSCI under a competing-risk framework. We hypothesized that incident stroke is followed by an acute step decline in episodic memory (primary hypothesis), with no acceleration of decline before or after the event.")

h1(doc, "Methods")
h2(doc, "Study population")
para(doc, [N("CHARLS is a nationally representative cohort of Chinese residents aged ≥45 years and their spouses, sampled by multistage stratified probability sampling in 2011 (17,705 respondents) and followed biennially."), C("9"),
           N(" Cognitive testing was administered at all six waves; in 2020 the battery was recorded in the Health Status and Functioning module. Deaths were ascertained at each wave through exit interviews with next of kin; death dates were imputed at the interval midpoint. We included participants aged ≥45 years at baseline (2011) who were free of self-reported physician-diagnosed stroke and memory-related disease, yielding 16,364 participants. The analytic sample comprised 13,974 participants with ≥1 cognitive measurement and complete covariates (62,962 person-wave observations; excluded participants were slightly older, less educated, and more likely to die; Supplementary Material 1, Table S1). The analysis followed the STROBE guidelines.")])
h2(doc, "Incident stroke ascertainment and event timing")
para(doc, "At each wave, participants reported whether a physician had ever diagnosed them with stroke. For 2013 and 2015, incident diagnoses were captured by the update question (\u201cdoctor told you since the last interview\u201d); the 2018 item applied to the full sample with \u201cever diagnosed\u201d semantics; the 2020 item captured new diagnoses among those without prior records; in 2021–2023, new diagnoses were identified by the updated disease module against carried-forward prior-diagnosis flags. The first stroke-positive wave defined the event interval. Event time was set to the reported diagnosis year (628/1,346 events, 46.7%) when it fell within the interval (0.6-year tolerance), and to the interval midpoint otherwise. Possible recurrent strokes were identifiable in the 2015 and 2021–2023 update items and addressed in sensitivity analyses.")
h2(doc, "Cognitive assessment")
para(doc, [N("Four outcomes were constructed at each cognitive wave. "), B("Episodic memory"), N(" (primary): mean of immediate and delayed recall of a 10-word list (0–10). "), B("Orientation/calculation (TICS-10):"), N(" five orientation items plus five serial-7 subtractions (0–10; adapted TICS items). "), B("Visuospatial ability:"), N(" figure copying (0–1). "), B("Global cognition:"), N(" the average of the three domain z scores, rescaled. The sixth wave comprised a 2021 main visit and 2022/2023 supplementary visits; the 2023 serial-7 component was prorated from items 2–5 (×5/4). To ensure cross-wave comparability—the word list changed at the 2018 and 2020 waves and the age structure shifts over time—scores were standardized within each interview year as residuals from a regression on age (natural spline, 3 df), education (3 levels), and sex, scaled to unit variance; a sensitivity analysis used baseline (2011) mean/SD standardization instead. Incident PSCI was defined as a post-event memory z ≤ −1 SD among participants whose pre-anchor measurements were all > −1 SD. This pragmatic single-domain definition is narrower than consensus criteria for vascular cognitive impairment (e.g., VASCOG)"), C("10"),
           N("; a global-cognition-based definition (global z ≤ −1 or −1.5 SD) was examined as sensitivity analysis S10.")])
h2(doc, "Covariates")
para(doc, "Baseline (2011) covariates: age, sex, education, marital status, depressive symptoms (CES-D 10), smoking, drinking frequency (missing n=26 assigned to \u201cnone\u201d), physician-diagnosed hypertension, dyslipidemia, diabetes, heart disease, and measured body mass index (indicator variable for missingness; multiple imputation in S9).")
h2(doc, "Statistical analysis")
para(doc, [N("Piecewise linear mixed-effects models were fitted with time anchored at stroke onset (τ = assessment year − event year). Following the parameterization used in the REGARDS and COSMIC analyses"), C("4,5"),
           N(", the model included a background linear slope (τ), a step term switching from 0 to 1 at stroke onset (the acute change; primary hypothesis), and interactions of stroke status with pre-anchor (min(τ,0)) and post-anchor (max(τ,0)) slopes, plus covariates and participant-level random intercepts and slopes; P values are Wald z approximations. Non-stroke participants received pseudo-anchor times drawn from the case event-time distribution; stability was verified over 20 independent draws (Supplementary Material 1, Table S5). A continuous-spline (level-shift) parameterization, constraining the trajectory to be continuous at the anchor, was compared by AIC (S11). Sex and baseline-age-group (<65 vs ≥65 years) differences were tested with 3-df interaction terms. Incident PSCI was analyzed with Fine–Gray subdistribution hazard models (death as competing event)"), C("11"),
           N(", adjusting for baseline age, sex, and education; a sensitivity model (S12) adjusted for the full covariate set using the Fine–Gray weighting implementation with cluster-robust standard errors. Participants entered the PSCI risk set at the anchor only if ≥1 post-anchor measurement was available; event-free survivors were censored at their last post-anchor measurement, and deaths were treated as competing events. Cumulative incidence functions were estimated at 2, 5, and 8 years; the proportional subdistribution hazards assumption was tested with a stroke × log(time) interaction; E-values quantified robustness to unmeasured confounding"), C("12"),
           N(". Sensitivity analyses (definitions in Supplementary Material 1, Table S3): (S1) midpoint-only event timing; (S2) excluding 2015–2018-interval events; (S3) pre-2020 events only; (S4) BMI-complete cases; (S5) demographics-only adjustment; (S6) first sixth-wave assessment only; (S7) baseline-distribution standardization; (S8) excluding 26 possible recurrent strokes; (S9) multiple imputation of baseline covariates (m=20)"), C("13"),
           N("; (S10) a global-cognition-based PSCI definition; (S11) the continuous-spline parameterization; (S13) adjustment for testing-visit number (practice effects). Estimates other than the primary hypothesis are nominal without multiplicity adjustment. Analyses were unweighted: CHARLS sampling weights are baseline-defined and do not extend to longitudinal trajectories. Primary-model Pearson residuals were approximately symmetric (skewness 0.17, kurtosis 3.41); 5 of 61,486 observations exceeded 4 SD, and refitting without them left the acute estimate unchanged (−0.121 vs −0.122 SD). Analyses used R 4.6.2 (lme4, cmprsk, mice). Two-sided P<0.05 was considered significant.")])

h1(doc, "Results")
h2(doc, "Cohort and incident stroke")
para(doc, "Of 16,364 baseline participants (mean age 59.2±9.8 years; 51.3% women), 1,346 (8.2%) experienced an incident stroke over a median follow-up of 12.0 years (182,962 person-years; 2,463 deaths). Mean age at stroke was 66.8±8.9 years (median event year 2017); 628 events (46.7%) had diagnosis-year refinement. Stroke survivors contributed a median of 5 (IQR 4–6) cognitive measurements; 1,094 (81.3%) had at least one pre- and one post-stroke measurement, and 705 (52.4%) had ≥2 in each phase. Stroke survivors were older and had more hypertension, diabetes, dyslipidemia, and heart disease at baseline than stroke-free participants; sex did not differ (P=0.97; Table 1).")
h2(doc, "Peri-stroke trajectory with an acute step")
para(doc, "Two conventions dominate this literature. Under the continuous-spline (level-shift) parameterization, the pre- and post-stroke slopes are forced to meet at the event, so an abrupt peri-event drop is absorbed into the slope estimates; under the step parameterization, a discontinuity at stroke onset separates the acute drop from the slopes. The two conventions answer different questions, and the choice moves acute-effect estimates substantially.")
para(doc, [N("The step parameterization fitted better than the continuous-spline parameterization (ΔAIC 4.8 for memory and 8.7 for global cognition). In stroke-free participants, memory changed little over calendar time (−0.001 SD/year), whereas global cognition declined modestly (−0.006 SD/year). Incident stroke was associated with an acute step at stroke onset (primary hypothesis) of −0.122 SD (95% CI −0.186 to −0.058; P=1.8×10⁻⁴); a pre-stroke slope difference of +0.016 SD/year (95% CI 0.007 to 0.024; P=2.5×10⁻⁴)—decline did not accelerate before stroke; the positive sign is addressed in the Discussion; and a post-stroke slope difference of −0.012 SD/year (95% CI −0.028 to 0.005; P=0.168), i.e., no post-stroke acceleration (Table 2, Figures 1 and 2).")])
para(doc, [N("Acute step declines were consistent across domains: immediate recall −0.136 SD, delayed recall −0.087 SD, TICS-10 −0.175 SD (P=3.7×10⁻⁵), visuospatial ability −0.092 SD (P=0.026), and global cognition −0.186 SD (P=1.2×10⁻⁵). No domain showed post-stroke acceleration (post-stroke slope differences: TICS-10 −0.003 SD/year, P=0.81; global −0.002 SD/year, P=0.85). Refitting the memory model within the TICS-available sample (n=9,593) yielded a concordant acute step (−0.149 SD, P=8.6×10⁻⁵), indicating the domain contrast is not attributable to sample composition.")])
h2(doc, "Subgroups and effect modification")
para(doc, "The acute memory step was homogeneous across subgroups: women −0.092 SD, men −0.155 SD (3-df stroke × sex interaction P=0.51); baseline age <65 years −0.127 SD, ≥65 years −0.098 SD (interaction P=0.72); no formal education −0.143 SD, any formal education −0.117 SD (1-df interaction P=0.86; Figure 3).")
h2(doc, "Incident PSCI: relative and absolute risk under competing mortality")
para(doc, "Among 7,765 participants cognitively intact before their anchor time and with ≥1 post-anchor measurement (of 15,630 participants with any memory measure, 699 had no pre-anchor measure, 4,702 were already impaired before the anchor, and 2,464 had no post-anchor measure; Supplementary Material 2), 1,669 developed incident PSCI and 287 died as competing events; because the risk set conditions on ≥1 post-anchor assessment, deaths before first post-anchor contact are not captured. Stroke survivors had a 26% higher subdistribution hazard of PSCI (adjusted sHR 1.26, 95% CI 1.08–1.47; Gray test P=0.003). At the stricter −1.5-SD threshold, the association was attenuated (sHR 1.25, 95% CI 1.02–1.54; Gray test P=0.060) with the proportionality test not supported (P=0.02); it should be read as an average over follow-up. The proportional subdistribution hazards assumption was supported for the primary definition (stroke × log(time) P=0.19). The E-value was 1.84 (1.37 for the lower confidence bound) treating the sHR as a risk ratio, and 1.50 (1.24) after the √HR approximation for a non-rare outcome. In absolute terms, cumulative PSCI incidence among stroke survivors reached 11.1% at 2 years, 26.5% at 5 years, and 43.6% at 8 years, versus 8.6%, 23.5%, and 36.4% in stroke-free participants—an absolute excess of ≈3 percentage points at 5 years (Figure 4; estimates beyond 6 years rest on fewer than 200 at-risk stroke survivors). Full covariate adjustment (S12; n=6,909) yielded a slightly stronger association (sHR 1.33, 95% CI 1.12–1.57). With a multidomain (global-cognition) definition, associations were concordant: sHR 1.33 (95% CI 1.09–1.62) at z ≤ −1 SD (5-year incidence 30.8% vs 23.5%) and 1.92 (1.52–2.41) at z ≤ −1.5 SD (20.9% vs 10.5%; Supplementary Material 1, Table S2).")
h2(doc, "Sensitivity analyses")
para(doc, "The acute memory step was robust across scale-comparable specifications (S1–S6, S8, S9, S13): midpoint-only event timing −0.131 SD; excluding 2015–2018-window events −0.140 SD; pre-2020 events −0.140 SD; BMI-complete cases −0.137 SD; demographics-only adjustment −0.129 SD; first sixth-wave assessment only −0.124 SD; excluding 26 possible recurrent strokes −0.115 SD; multiple imputation (m=20) −0.127 SD (95% CI −0.187 to −0.067); and adjustment for testing-visit number −0.123 SD (visit coefficient +0.051 SD per visit, P=9.6×10⁻²⁵). Over 20 independent pseudo-anchor draws, the step estimate ranged from −0.124 to −0.121 SD for memory (all P≤1.9×10⁻⁴) and from −0.216 to −0.214 SD for global cognition (all P≤6×10⁻⁶). Under the continuous-spline parameterization (S11), the same data yielded an acute level shift of −0.084 SD. With conventional baseline-distribution standardization (S7), the step estimate attenuated to −0.061 SD for memory (P=0.065) and +0.011 SD for global cognition (P=0.81), illustrating that standardization conventions also move estimates substantially (Supplementary Material 1, Table S3).")

h1(doc, "Discussion")
h2(doc, "Principal findings")
para(doc, "This study formally tested whether the two-fold difference in estimated acute cognitive effects of stroke between Chinese (≈−0.12 SD) and international (≈−0.25 SD) cohorts can be generated analytically. Within a single dataset, conventions moved estimates materially—parameterization by ≈0.04 SD for memory and ≈0.07 SD for global cognition, and standardization by more—yet under every convention examined the acute memory estimate remained close to the earlier CHARLS figure and well below the international pooled estimate. Analytic conventions therefore account for part of the observed East–West spread but are unlikely to explain it in full. Substantively, incident stroke in this 12-year nationally representative cohort was followed by an acute, multidomain step decline in cognition (≈0.1–0.2 SD), with no evidence that decline accelerates before or after the event once the acute step is modeled explicitly. Stroke survivors carried a 26% higher subhazard of crossing the cognitive-impairment threshold—26.5% versus 23.5% impaired by 5 years—after accounting for competing mortality.")
h2(doc, "Comparison with previous work")
para(doc, [N("Our primary acute memory estimate (−0.122 SD) is nearly identical to the earlier CHARLS estimate (−0.123 SD) and smaller than the international pooled estimate (−0.25 SD in global cognition; COSMIC), and we can account for part of this spread within our own data. First, parameterization: the continuous-spline (level-shift) specification blends the acute jump into the slope terms (−0.084 SD for memory and −0.115 SD for global cognition, the latter approximating the earlier Chinese global estimate), whereas the step specification used by Levine et al. and COSMIC separates it (−0.122 and −0.186 SD; ΔAIC 4.8–8.7 favoring the step)."), C("4,5,7"),
           N(" Second, standardization: baseline-distribution standardization (S7) attenuated the memory step to −0.061 SD, plausibly because cross-wave test-form differences (the word list changed at the 2018 and 2020 waves) leak into baseline-referenced scores; we therefore designated within-wave standardization as primary. However, no convention we examined brought the memory estimate near the international pooled figure, so analytic conventions alone cannot explain the East–West difference; residual differences in test content, age structure, stroke severity, and case mix are likely to contribute.")])
para(doc, [N("Our null findings on slopes align with COSMIC (no pre-stroke slope difference) but contrast with an earlier CHARLS analysis and a recent multi-cohort study reporting accelerated pre-stroke decline."), C("5,6,8"),
           N(" Practice effects"), C("14"),
           N(", selective participation of lower-functioning individuals in earlier waves, and interval-censored event timing could mask a modest pre-stroke acceleration; the small positive pre-stroke slope differences should be read as absence of evidence for acceleration, not as a protective trend. Likewise, we did not reproduce the small post-stroke acceleration reported in prior US cohort analyses (−0.038 SD/year in COSMIC); our 95% CIs exclude an acceleration of that magnitude in memory and global cognition, although smaller accelerations cannot be ruled out."), C("4,5"),
           N(" Finally, our PSCI analysis extends the REGARDS finding of elevated incident cognitive impairment after stroke"), C("15"),
           N(" by providing subdistribution hazard ratios and absolute cumulative incidence under competing mortality—quantities directly usable for planning cognitive surveillance after stroke. By comparison, a multicenter Chinese hospital study using a brief multidomain screen found 78.7% of first-ever ischemic stroke patients impaired"), C("16"),
           N("; our lower 5-year cumulative incidence (26.5%) reflects the community-dwelling sample, longer ascertainment intervals, and single-domain threshold.")])
h2(doc, "Mechanistic and clinical implications")
para(doc, [N("The trajectory shape—a one-time multidomain step down, with subsequent decline proceeding at the background age-related rate—supports a model in which the stroke lesion delivers an acute insult whose direct cognitive consequence does not progressively compound, at least at the resolution of biennial testing."), C("17,18"),
           N(" Clinically, the burden is carried by the acute step and the elevated threshold-crossing risk: about one in four survivors under cognitive follow-up met the PSCI criterion within 5 years despite competing mortality; these data support incorporating cognitive assessment into post-stroke follow-up, as guidelines recommend"), C("19"),
           N(", although whether systematic screening improves outcomes was not tested.")])
h2(doc, "Strengths and limitations")
para(doc, "Strengths include the 12-year span with six cognitive waves—the longest single-cohort peri-stroke trajectory mapping in an Asian population and the first to use the 2020 and 2021–2023 CHARLS waves—more than twice the incident events of previous CHARLS reports, diagnosis-year-refined event timing, domain-specific outcomes, a formally fit-compared step parameterization, absolute and relative PSCI risks under competing mortality with E-values, a 13-analysis sensitivity program with pseudo-anchor validation, and fully adjusted competing-risk models (S12).")
para(doc, [N("Limitations: (1) Stroke was self-reported physician diagnosis without subtype, severity, or imaging; misclassification would bias acute effects toward the null, and recurrent strokes are only partially detectable (26 flagged; exclusion did not change estimates). (2) Event timing and PSCI onset are interval-censored: the step term captures the drop occurring anywhere within the first post-stroke inter-assessment interval, and short-term incidence approximates impairment at first post-stroke contact. (3) The battery lacks processing-speed measures, the visuospatial domain rests on a single binary item whose pass rate was lower in the 2020 wave (absorbed by within-wave standardization), and PSCI was defined by a single-domain threshold, narrower than consensus criteria; the global-cognition definition yielded concordant associations. (4) Attrition and competing death likely bias post-stroke slopes toward the null: survivors without post-stroke measurements were older (67.7 vs 59.5 years), cognitively lower at baseline (−0.24 vs −0.07 SD), and had nearly four-fold higher mortality (39.8% vs 11.0%; Supplementary Material 1, Table S4); the PSCI risk set conditions on surviving to first post-anchor contact, so the 287 competing deaths occurred after re-contact. (5) Practice effects from repeated testing (+0.05 SD per visit in S13) may contribute to the small positive pre-stroke slope differences, although adjusting for visit number left the acute estimate unchanged. (6) Cognitive waves are biennial, so transient peri-stroke recovery cannot be resolved, although early post-stroke improvement is documented in a substantial minority of patients"), C("19"), N(".")])
h2(doc, "Conclusions")
para(doc, "In Chinese adults aged ≥45 years, incident stroke was associated with an acute multidomain cognitive step decline, without measurable acceleration of decline before or after the event, and with a 26% higher subhazard of threshold-defined cognitive impairment despite competing mortality. Acute-effect estimates moved materially with parameterization and standardization conventions, yet remained below international pooled estimates under every convention examined; the apparent East–West difference is therefore unlikely to reflect analytic conventions alone. These findings support systematic post-stroke cognitive surveillance and harmonized analytic standards for cross-cohort comparison.")

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
para(doc, "CHARLS data are available to registered researchers at https://charls.pku.edu.cn. Analysis code is available at https://github.com/ronaldchen1985/charls-stroke-cognition.")

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
 "Levine DA, Wadley VG, Langa KM, et al. Risk factors for poststroke cognitive decline: the REGARDS study. Stroke 2018; 49: 987–994.",
 "He A, Wang Z, Wu X, et al. Incidence of post-stroke cognitive impairment in patients with first-ever ischemic stroke: a multicenter cross-sectional study in China. Lancet Reg Health West Pac 2023; 33: 100687.",
 "Rost NS, Brodtmann A, Pase MP, et al. Post-stroke cognitive impairment and dementia. Circ Res 2022; 130: 1252–1271.",
 "Iadecola C, Duering M, Hachinski V, et al. Vascular cognitive impairment and dementia: JACC Scientific Expert Panel. J Am Coll Cardiol 2019; 73: 3326–3344.",
 "El Husseini N, Katzan IL, Rost NS, et al. Cognitive impairment after ischemic and hemorrhagic stroke: a scientific statement from the American Heart Association/American Stroke Association. Stroke 2023; 54: e272–e291.",
]
for i, r in enumerate(refs, 1):
    p = para(doc, f"{i}. {r}", justify=False)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p.paragraph_format.space_after = Pt(4)

# ---------- FIGURE LEGENDS ----------
h1(doc, "Figure legends")
para(doc, [B("Figure 1. "), N("Model-predicted peri-stroke cognitive trajectories by domain (a episodic memory; b orientation/calculation; c visuospatial ability; d global cognition) under the step parameterization, stroke survivors versus stroke-free participants. Acute step estimates (95% CI) are annotated; the vertical segment at τ=0 is the modelled acute drop. Curves are shifted so the incident-stroke group equals 0 at τ=−10.")], justify=False)
para(doc, [B("Figure 2. "), N("Observed domain z scores (mean ± 95% CI) by time to/from stroke (1-year bins; domains as in Figure 1), among all participants contributing cognitive data; stroke-free participants use pseudo-anchor times from the case event-time distribution. Per-bin sample sizes are shown below each panel; bins with n<100 are faded.")], justify=False)
para(doc, [B("Figure 3. "), N("Acute memory step at stroke onset across the primary model, subgroups, and sensitivity analyses S1–S9, S11 and S13 (definitions in Methods; S10 in Supplementary Material 1, Table S2). Points: estimates; whiskers: 95% CI.")], justify=False)
para(doc, [B("Figure 4. "), N("Cumulative incidence of post-stroke cognitive impairment (memory z ≤ −1 SD) among stroke survivors versus stroke-free participants, accounting for the competing risk of death (adjusted subdistribution hazard ratio 1.26, 95% CI 1.08–1.47). Event-free participants are censored at last assessment; curves truncate at 8 years (numbers at risk below; estimates beyond 6 years rest on fewer than 200 at-risk stroke survivors).")], justify=False)

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
para(cl, "[Date]", justify=False)
para(cl, "", justify=False)
para(cl, "The Editors\nInternational Journal of Stroke", justify=False)
para(cl, "", justify=False)
para(cl, "Dear Editors,", justify=False)
para(cl, "We are pleased to submit our Research Article entitled \u201cCognitive trajectories and risk of cognitive impairment after incident stroke: a 12-year nationwide cohort study in China\u201d for consideration in the International Journal of Stroke.", justify=False)
para(cl, "How cognition evolves around a first stroke remains unresolved in Asian populations, and acute-effect estimates differ two-fold between Chinese (≈−0.12 SD) and international cohorts (≈−0.25 SD) for reasons never formally dissected. Using the full 12-year follow-up of the nationally representative CHARLS cohort (six cognitive waves, including the previously unused 2020 and 2021–2023 waves, more than doubling prior CHARLS event counts), we formally tested whether this gap can be generated analytically: model parameterization (step vs continuous level-shift) moved the acute memory estimate between −0.084 and −0.122 SD and standardization conventions moved it further, yet no convention brought the estimate near the international pooled figure—direct evidence that the East–West difference is not an analytic artifact alone. We further provide absolute risks of post-stroke cognitive impairment under competing mortality in this setting: about one in four stroke survivors under cognitive follow-up crossed the cognitive-impairment threshold within 5 years (26.5% vs 23.5%; adjusted subdistribution hazard ratio 1.26, 95% CI 1.08–1.47), with no acceleration of decline before or after the event once the acute step is modelled.", justify=False)
para(cl, "We believe these results are well suited to the International Journal of Stroke's readership: they provide the longest single-cohort peri-stroke trajectory mapping in an Asian population, they subject a widely debated cross-cohort discrepancy to a formal within-cohort test, and they quantify an absolute cognitive-risk burden directly relevant to the follow-up care of stroke survivors.", justify=False)
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
 ("Setting", "5", "CHARLS, nationwide China, 2011–2023; six cognitive waves (2020 battery in Health Status module)", "Methods – Study population"),
 ("Participants", "6", "Eligibility criteria; sampling; flow incl. PSCI branch in Supplementary Material 2", "Methods – Study population; Supplementary Material 2"),
 ("Variables", "7", "Outcomes, exposure, covariates defined; PSCI definition vs VASCOG discussed", "Methods – Cognitive assessment; Covariates"),
 ("Data sources/measurement", "8", "Cognitive battery, stroke ascertainment, death via exit interviews (midpoint-imputed)", "Methods"),
 ("Bias", "9", "Interval censoring, attrition, misclassification, multiple comparisons addressed", "Statistical analysis; Sensitivity analyses; Limitations"),
 ("Study size", "10", "All eligible participants used; N=16,364", "Results – Cohort"),
 ("Quantitative variables", "11", "Z-score standardization; thresholds −1/−1.5 SD", "Methods – Cognitive assessment"),
 ("Statistical methods", "12", "Piecewise LMM with step term (AIC-compared vs spline); Fine–Gray with last-assessment censoring + proportionality test; E-values incl. √HR approximation; S1–S13 incl. multiple imputation (m=20), fully adjusted Fine–Gray models (S12) and practice-effect adjustment (S13)", "Methods – Statistical analysis"),
 ("Participants (results)", "13", "Numbers at each stage; reasons for non-participation", "Results – Cohort; Supplementary Material 2"),
 ("Descriptive data", "14", "Baseline characteristics by stroke status", "Table 1"),
 ("Outcome data", "15", "1,346 incident strokes; 1,669 PSCI events; 287 competing deaths", "Results"),
 ("Main results", "16", "Estimates with 95% CI; primary hypothesis designated, others nominal", "Table 2; Results"),
 ("Other analyses", "17", "Subgroups with formal interaction tests, sensitivity analyses incl. MI, global-PSCI definition, fully adjusted competing-risk models (S12) and practice-effect adjustment (S13)", "Results; Figure 3"),
 ("Key results (discussion)", "18", "Summarised with reference to objectives", "Discussion – Principal findings"),
 ("Limitations", "19", "Nine limitations with direction of bias", "Discussion – Strengths and limitations"),
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
