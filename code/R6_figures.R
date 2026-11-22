## ============================================================================
## R6: 修订版图件 —— Fig1 阶跃轨迹(四域) / Fig3 森林图(新电池) / Fig4 新 CIF
## ============================================================================
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(ggplot2); library(gridExtra)})
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
say <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n")

theme_pub <- theme_classic(base_size = 11, base_family = "sans") +
  theme(legend.position = "top", legend.title = element_blank(),
        axis.title = element_text(size = 10.5, face = "bold"),
        plot.title = element_text(size = 11, face = "bold"),
        axis.line = element_line(linewidth = 0.5))

## ---------- Figure 1: 阶跃模型轨迹 (含锚点瞬时跌落) ----------
r2 <- read.csv(file.path(out, "output/R2_main_step.csv"))
domains <- c("z_wrmean", "z_tics", "z_visuo", "z_glob")
dnames <- c("Episodic memory", "Orientation/calculation (TICS-10)",
            "Visuospatial ability", "Global cognition")
tau_pre <- seq(-10, -0.01, by = 0.25); tau_post <- seq(0, 7, by = 0.25)
panels <- list()
for (k in seq_along(domains)) {
  cf <- r2 %>% filter(model == paste0("step: ", domains[k]))
  b_tau <- cf$est[cf$term == "tau"]; st <- cf$est[cf$term == "step"]
  gpre <- cf$est[cf$term == "stroke:pre_tau"]; gpost <- cf$est[cf$term == "stroke:post_tau"]
  a_lo <- cf$lo[cf$term == "step"]; a_hi <- cf$hi[cf$term == "step"]
  sh <- b_tau * (-10) + gpre * (-10)   # 卒中组 tau=-10 处归零
  df <- bind_rows(
    data.frame(tau = tau_pre,  grp = "Stroke-free",     y = b_tau * tau_pre - sh),
    data.frame(tau = tau_post, grp = "Stroke-free",     y = b_tau * tau_post - sh),
    data.frame(tau = tau_pre,  grp = "Incident stroke", y = b_tau * tau_pre + gpre * tau_pre - sh),
    data.frame(tau = tau_post, grp = "Incident stroke",
               y = b_tau * tau_post + st + gpost * tau_post - sh))
  df$grp <- factor(df$grp, levels = c("Stroke-free", "Incident stroke"))
  jump <- data.frame(y0 = b_tau * 0 + gpre * 0 - sh, y1 = b_tau * 0 + st - sh)
  acute_txt <- sprintf("Acute step: %.3f SD (%.3f to %.3f)", st, a_lo, a_hi)
  ymin_k <- min(df$y); rng_k <- diff(range(df$y)); if (rng_k < 0.05) rng_k <- 0.05
  panels[[k]] <- ggplot(df, aes(tau, y, color = grp, linetype = grp)) +
    geom_vline(xintercept = 0, linetype = 3, color = "grey60", linewidth = 0.4) +
    geom_line(linewidth = 0.9) +
    geom_segment(data = jump, aes(x = 0, xend = 0, y = y0, yend = y1),
                 color = "#D55E00", linewidth = 0.9, linetype = 1, inherit.aes = FALSE) +
    annotate("text", x = -9.7, y = ymin_k - 0.05 * rng_k, label = acute_txt,
             hjust = 0, size = 3.0, color = "grey20") +
    scale_color_manual(values = c("#0072B2", "#D55E00")) +
    scale_linetype_manual(values = c(2, 1)) +
    coord_cartesian(ylim = c(ymin_k - 0.14 * rng_k, NA)) +
    labs(title = paste0(LETTERS[k], ". ", dnames[k]),
         x = "Years from stroke onset / anchor (\u03c4)", y = "z score (shifted)") +
    theme_pub
}
p1 <- gridExtra::arrangeGrob(grobs = panels, layout_matrix = rbind(c(1, 2), c(3, 4)))
ggsave(file.path(out, "figures/Fig1_trajectory_EN.png"), p1, width = 9.5, height = 7.5, dpi = 600)
say("Fig1 阶跃轨迹图完成")

## ---------- Figure 3: 森林图 (新电池) ----------
r3 <- read.csv(file.path(out, "output/R3_subgroup_sens_step.csv"))
mi <- read.csv(file.path(out, "output/R4_mi20_pooled.csv"))
s13 <- read.csv(file.path(out, "output/V9_practice_s13.csv"))
spline_row <- r2 %>% filter(model == "spline: z_wrmean", term == "stroke")
rows <- bind_rows(
  r2 %>% filter(model == "step: z_wrmean", term == "step") %>%
    transmute(analysis = "Primary model (fully adjusted)", est, lo, hi),
  r3 %>% filter(term == "step") %>%
    transmute(analysis, est, lo, hi),
  mi %>% filter(term == "step") %>%
    transmute(analysis = "S9: Multiple imputation of covariates (m=20)", est, lo, hi),
  spline_row %>% transmute(analysis = "S11: Level-shift (spline) parameterization", est, lo, hi),
  s13 %>% filter(model == "S13_visit_adj", term == "step") %>%
    transmute(analysis = "S13: Adjustment for testing occasion", est, lo, hi))
name_map <- c("Subgroup: women" = "Women", "Subgroup: men" = "Men",
              "Subgroup: baseline age <65 y" = "Baseline age <65 y",
              "Subgroup: baseline age >=65 y" = "Baseline age \u226565 y",
              "Subgroup: no formal education" = "No formal education",
              "Subgroup: any formal education" = "Any formal education",
              "S1: midpoint imputation only" = "S1: Midpoint-only event timing",
              "S2: exclude 2015-2018-window events" = "S2: Excluding 2015\u20132018-window events",
              "S3: pre-2020 events only" = "S3: Pre-2020 events only",
              "S4: BMI complete cases" = "S4: BMI complete cases",
              "S5: demographics-only adjustment" = "S5: Demographics-only adjustment",
              "S6: first sixth-wave assessment only" = "S6: First sixth-wave assessment only",
              "S7: baseline-standardized, memory" = "S7: Baseline-distribution standardization",
              "S8: exclude possible recurrent stroke" = "S8: Excluding possible recurrent stroke")
rows$analysis <- unname(ifelse(rows$analysis %in% names(name_map),
                               name_map[rows$analysis], rows$analysis))
rows <- rows %>% filter(analysis != "S7: Baseline-distribution standardization" |
                          !is.na(est))
## 去掉 TICS 样本内行(不属于森林图电池) 与 S7 全域行
rows <- rows %>% filter(!grepl("TICS-assessed", analysis),
                        !(analysis == "S7: baseline-standardized, global"))
rows$group <- c("Primary", rep("Subgroups", 6), rep("Sensitivity analyses", nrow(rows) - 7))
rows$analysis <- factor(rows$analysis, levels = rev(rows$analysis))
theme_for <- theme_classic(base_size = 12, base_family = "sans") +
  theme(legend.position = "top", legend.title = element_blank(),
        axis.title = element_text(size = 12, face = "bold"),
        axis.line = element_line(linewidth = 0.5))
p3 <- ggplot(rows, aes(est, analysis)) +
  geom_vline(xintercept = 0, linetype = 3, color = "grey50") +
  geom_vline(xintercept = rows$est[rows$analysis == "Primary model (fully adjusted)"],
             linetype = 2, color = "grey80") +
  geom_errorbar(aes(xmin = lo, xmax = hi, orientation = "y"), width = 0.22, linewidth = 0.5) +
  geom_point(aes(size = group == "Primary"), color = "#B22222", show.legend = FALSE) +
  scale_size_manual(values = c(2.2, 3.2)) +
  labs(x = "Acute memory change at stroke onset, SD (95% CI)", y = NULL) +
  theme_for
ggsave(file.path(out, "figures/Fig3_forest_acute_EN.png"), p3, width = 8, height = 7.5, dpi = 600)
say("Fig3 完成, 行数=", nrow(rows))
write.csv(rows, file.path(out, "output/R6_fig3_rows.csv"), row.names = FALSE)

## ---------- Figure 4: 修正版 CIF ----------
gry <- readRDS(file.path(out, "output/R5_gry.rds"))
ci_obj <- gry$m1
s1 <- ci_obj[["1 1"]]; s0 <- ci_obj[["0 1"]]
curve <- bind_rows(
  data.frame(t = s1$time, cif = s1$est, grp = "Incident stroke"),
  data.frame(t = s0$time, cif = s0$est, grp = "Stroke-free")) %>% filter(t <= 8)
nr <- read.csv(file.path(out, "output/R5_atrisk.csv"))
tp <- c(0, 2, 4, 6, 8)
nr <- data.frame(t = tp, ctrl = as.numeric(nr[1, ]), stroke = as.numeric(nr[2, ]))
theme_pub4 <- theme_classic(base_size = 12, base_family = "sans") +
  theme(legend.position = c(0.25, 0.85), legend.title = element_blank(),
        axis.title = element_text(size = 12, face = "bold"),
        axis.line = element_line(linewidth = 0.5))
p4 <- ggplot(curve, aes(t, cif, color = grp)) +
  geom_step(linewidth = 0.9) +
  scale_color_manual(values = c("#D55E00", "#0072B2")) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1), limits = c(0, NA)) +
  scale_x_continuous(breaks = seq(0, 8, 2)) +
  annotate("text", x = 7.95, y = 0.475, label = "8-y: 43.1%", color = "#D55E00", size = 3.4, hjust = 1) +
  annotate("text", x = 7.95, y = 0.285, label = "8-y: 33.4%", color = "#0072B2", size = 3.4, hjust = 1) +
  annotate("text", x = 7.95, y = 0.03, label = "Adjusted sHR 1.41 (95% CI 1.21\u20131.64)",
           color = "grey20", size = 3.4, hjust = 1) +
  labs(x = "Years from stroke onset / pseudo-anchor",
       y = "Cumulative incidence of PSCI") +
  theme_pub4
nr_long <- data.frame(t = rep(nr$t, 2),
                      grp = rep(c("Incident stroke", "Stroke-free"), each = nrow(nr)),
                      n = c(nr$stroke, nr$ctrl))
pnr <- ggplot(nr_long, aes(t, grp, label = n)) +
  geom_text(size = 3.2) +
  scale_y_discrete(limits = c("Stroke-free", "Incident stroke")) +
  scale_x_continuous(breaks = seq(0, 8, 2)) +
  labs(x = NULL, y = "No. at risk") +
  theme_classic(base_size = 10) +
  theme(axis.title.x = element_blank(), axis.text.x = element_blank(),
        axis.ticks.x = element_blank(), axis.line.x = element_blank(),
        axis.title.y = element_text(size = 9))
pg <- gridExtra::arrangeGrob(p4, pnr, ncol = 1, heights = c(4, 1))
ggsave(file.path(out, "figures/Fig4_cif_psci_EN.png"), pg, width = 7.5, height = 5.6, dpi = 600)
say("Fig4 完成; at-risk stroke: ", paste(nr$stroke, collapse = "/"))
