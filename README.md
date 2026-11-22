# Cognitive trajectories and risk of cognitive impairment after incident stroke: a 12-year nationwide cohort study in China

Analysis code for the manuscript submitted to *Cerebrovascular Diseases* (2026).

**Study**: Piecewise linear mixed-effects models with an acute step at stroke onset (four cognitive domains) and Fine–Gray competing-risk models for incident post-stroke cognitive impairment (PSCI), using all six cognitive waves of the China Health and Retirement Longitudinal Study (CHARLS), 2011–2023 (the 2020 cognitive battery is recorded in the Health Status and Functioning module).

**Authors**: Gan Zhang, Can Sun (co-first), Qingli Sun, Yong Chen (corresponding, ronaldchen@bjmu.edu.cn), Department of Neurology, Peking University Third Hospital, Beijing, China.

---

## 1. Data access

CHARLS data are **not** included in this repository (restricted-access). Registered researchers can obtain them at <https://charls.pku.edu.cn>. After approval, place the wave folders so that:

```
$CHARLS_DATA/2011/demographic_background.dta
$CHARLS_DATA/2011/health_status_and_functioning.dta
$CHARLS_DATA/2011/biomarkers.dta
$CHARLS_DATA/2013/..., 2015/..., 2018/..., 2020/..., 2021/..., 2022/..., 2023/...
```

Set two environment variables (or run with the defaults shown):

| Variable | Meaning | Default |
|---|---|---|
| `CHARLS_DATA` | Parent directory of the CHARLS wave folders | `D:/CHARLS` |
| `PROJ_ROOT` | Repository root (intermediate CSVs, `output/`, `figures/`, `manuscript/`, `submission_CED/` are read/written here) | current working directory |

## 2. Software requirements

- **R 4.6.2** (Windows path used during analysis; any platform works) with packages:
  `haven 2.5.5, dplyr 1.2.1, lme4 2.1-0, cmprsk 2.2-12, mice 3.19.0, survival 3.8-12, ggplot2 4.0.3, gridExtra 2.3.1, tableone 0.13.2`
- **Python ≥ 3.10** with `pandas, python-docx, matplotlib, Pillow, pypdf, reportlab` (only needed for manuscript/figure-document generation, not for the statistical analyses)
- All scripts that use random sampling set an explicit seed (`set.seed(20261115)` or per-run seeds); the 20 pseudo-anchor draws and the 20 multiple imputations are exactly reproducible.

## 3. Run order

Run from the repository root. Steps 1–8 produce every number in the manuscript; steps 9–12 regenerate the submission documents.

| # | Script | What it produces |
|---|---|---|
| 1 | `code/F1_build.R` | `psci_baseline.csv` (person level, N=16,364), `psci_cog_long.csv` (person-wave) from raw CHARLS `.dta` files; includes diagnosis-year event-time refinement (628/1,346 events) |
| 2 | `code/G1_build_domains.R` | `psci_cog_long2.csv`: adds TICS-10, visuospatial and global-cognition z scores (within-interview-year standardization) |
| 3 | `code/R2_main_step.R` | **Primary models**: step parameterization, four domains; step-vs-spline ΔAIC (S11); sex/age 3-df interactions; saves `output/R2_models.rds`, `R2_main_step.csv` |
| 4 | `code/R3_subgroup_sens_step.R` | Subgroups (sex/age/education) and sensitivity analyses S1–S8 → `R3_subgroup_sens_step.csv` |
| 5 | `code/R3b_pseudo_step.R <outcome>` | 20 pseudo-anchor draws (run once per outcome, e.g. `z_wrmean`) → `R3b_pseudo20_step_*.csv` (Table S5) |
| 6 | `code/R4a_mi_chunk.R <seed>` × 4 (seeds 101–104), then `code/R4b_mi_pool.R` | S9: multiple imputation (m=20) + pooled step model → `R4_mi20_pooled.csv` |
| 7 | `code/R5_fg_final.R` | **Fine–Gray models** (memory/global × −1/−1.5 SD thresholds = primary + S10), proportionality test, E-values (incl. √HR approximation), cumulative incidence at 2/5/8 y, STROBE flow counts → `R5_fg_final.csv` |
| 8 | `code/V6_fg_fulladj.R` | S12: fully adjusted Fine–Gray (survival::finegray + cluster-robust coxph) → `V6_fg_fulladj.csv` |
| 9 | `code/V5_resid_diag.R`, `code/V5b_resid_refit.R` | Residual diagnostics reported in Methods (skewness/kurtosis, 4-SD refit) |
| 9b | `code/V9_practice_interact.R`, `code/V9b_interact_1df.R` | S13: testing-occasion (practice-effect) adjustment → `V9_practice_s13.csv`; step-specific 1-df interaction tests (sex/age/education) → `V9_step_interactions_1df.csv` |
| 10 | `code/V8_descriptives.R` | Descriptive numbers quoted in Results/Table 1 → `V8_descriptives.txt` |
| 11 | `code/F7_table1_EN.R` | Table 1 (baseline characteristics) → `Table1_EN_raw.csv` |
| 12 | `code/R6_figures.R`, `code/H2_composite_figs.R`, `code/H3_fig4_fig3.R` | Figures 1–4 (PNG, converted to 600-dpi TIFF in step 13) |
| 13 | `code/make_figS1.py`, `make_tables_docx.py`, `make_suppl_tables.py`, `make_esm_jn.py` | Fig. S1 flow diagram; Tables.docx; Supplementary Material 1 (Tables S1–S5) and 2 (Fig. S1) PDFs |
| 14 | `code/make_submission_ced.py` | Manuscript, cover letter, STROBE checklist, 600-dpi TIFFs → `submission_CED/` (Cerebrovascular Diseases package; also prints word counts and citation-order check). `code/make_submission_ijs.py` is retained for the earlier International Journal of Stroke package. |
| 15 | `code/make_reviewers.py`, `code/make_proof_pdf.py` | Suggested reviewers; merged proofreading PDF |

> Debugging/verification scratch scripts used during peer-review preparation (files prefixed `dbg_`, `V1`–`V5`, `R4dbg`) are intentionally **not** part of this repository; every reported number regenerates from the scripts above alone.

## 4. Key analytic choices (for reviewers)

- **Step parameterization (primary)**: discontinuity at stroke onset separates the acute drop from pre-/post-stroke slopes; the continuous-spline (level-shift) parameterization is reported as S11 with ΔAIC comparison.
- **Within-interview-year standardization (primary)**: z scores are residuals from regression on age (natural spline, 3 df), education, and sex, scaled to unit variance within each interview year; baseline-distribution standardization is S7.
- **Event timing**: first stroke-positive wave defines the interval; event time = reported diagnosis year when inside the interval (0.6-y tolerance, 628/1,346 = 46.7% of events), interval midpoint otherwise (S1 = midpoint for all).
- **PSCI risk set**: participants cognitively intact before the anchor with ≥1 post-anchor measurement; death (exit-interview, midpoint-imputed) as competing event; last-assessment censoring.

## 5. License

Code is released under the MIT License (see `LICENSE`). CHARLS data remain subject to the CHARLS data-use agreement and must be obtained from the CHARLS project directly.

## 6. Citation

If you use this code, please cite the manuscript (citation to be updated upon publication).
