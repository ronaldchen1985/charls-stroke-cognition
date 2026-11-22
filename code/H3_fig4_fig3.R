## H3: Figure 4 —— PSCI 累积发病曲线 (Fine-Gray CIF, 记忆 -1 SD) + Fig3 加 S9 行
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(cmprsk); library(ggplot2)})
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
say <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n")
set.seed(20261115)

coh <- read.csv(file.path(out, "psci_baseline.csv")); coh$ID11 <- as.character(coh$ID11)
z1  <- read.csv(file.path(out, "psci_cog_long.csv"));  z1$ID11 <- as.character(z1$ID11)
cases_t <- coh$ev_t[coh$ev_wave != "never" & !is.na(coh$ev_t)]
coh$pseudo_t <- NA_real_; nc <- coh$ev_wave != "never" & !is.na(coh$ev_t)
coh$pseudo_t[nc] <- coh$ev_t[nc]; coh$pseudo_t[!nc] <- sample(cases_t, sum(!nc), TRUE)
d <- z1 %>% left_join(coh %>% select(ID11, ev_wave, pseudo_t, death_t, sex, age11, edu),
                      by = "ID11", suffix = c("", ".y")) %>%
  filter(!is.na(z_wrmean)) %>%
  mutate(stroke = as.integer(ev_wave != "never"), tau = tyr - pseudo_t)
pre_ok <- d %>% filter(tau < 0) %>% group_by(ID11) %>%
  summarise(min_pre_z = min(z_wrmean), .groups = "drop") %>% filter(min_pre_z > -1)
post_ci <- d %>% filter(tau > 0, ID11 %in% pre_ok$ID11) %>% group_by(ID11) %>%
  summarise(ci = as.integer(any(z_wrmean <= -1)),
            t_ci = ifelse(any(z_wrmean <= -1), min(tau[z_wrmean <= -1]), min(tau)),
            .groups = "drop")
fg <- coh %>% filter(ID11 %in% pre_ok$ID11) %>% left_join(post_ci, by = "ID11") %>%
  mutate(stroke = as.integer(ev_wave != "never"),
         t_end = pmin(ifelse(is.na(t_ci), Inf, pseudo_t + t_ci),
                      ifelse(is.na(death_t), Inf, death_t), 2023.5, na.rm = TRUE) - pseudo_t,
         status = case_when(
           !is.na(t_ci) & ci == 1 & (pseudo_t + t_ci) <= pmin(ifelse(is.na(death_t), Inf, death_t), 2023.5) ~ 1L,
           !is.na(death_t) & death_t <= pmin(ifelse(is.na(t_ci), Inf, pseudo_t + t_ci), 2023.5) ~ 2L,
           TRUE ~ 0L)) %>% filter(t_end > 0)

ci_obj <- cuminc(ftime = fg$t_end, fstatus = fg$status, group = fg$stroke, cencode = 0)
s1 <- ci_obj[["1 1"]]; s0 <- ci_obj[["0 1"]]
curve <- bind_rows(
  data.frame(t = s1$time, cif = s1$est, grp = "Incident stroke"),
  data.frame(t = s0$time, cif = s0$est, grp = "Stroke-free")) %>% filter(t <= 8)
## numbers at risk
tp <- c(0, 2, 4, 6, 8)
nr <- data.frame(t = tp,
                 stroke = sapply(tp, function(x) sum(fg$stroke == 1 & fg$t_end >= x)),
                 ctrl   = sapply(tp, function(x) sum(fg$stroke == 0 & fg$t_end >= x)))
say("Numbers at risk:"); print(nr)

theme_pub <- theme_classic(base_size = 12, base_family = "sans") +
  theme(legend.position = c(0.25, 0.85), legend.title = element_blank(),
        axis.title = element_text(size = 12, face = "bold"),
        axis.line = element_line(linewidth = 0.5))
p4 <- ggplot(curve, aes(t, cif, color = grp)) +
  geom_step(linewidth = 0.9) +
  scale_color_manual(values = c("#D55E00", "#0072B2")) +
  scale_y_continuous(labels = scales::percent_format(accuracy = 1), limits = c(0, NA)) +
  scale_x_continuous(breaks = seq(0, 8, 2)) +
  annotate("text", x = 7.95, y = 0.665, label = "8-y: 62.4%", color = "#D55E00", size = 3.4, hjust = 1) +
  annotate("text", x = 7.95, y = 0.375, label = "8-y: 41.3%", color = "#0072B2", size = 3.4, hjust = 1) +
  labs(x = "Years from stroke onset / matched anchor",
       y = "Cumulative incidence of PSCI") +
  theme_pub
## 下方 numbers-at-risk 条带
nr_long <- data.frame(
  t = rep(nr$t, 2),
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
say("Fig4 CIF 曲线完成")

## ---- Fig3: 增加 S9 (MI) 行 ----
sens <- read.csv(file.path(out, "output/F3_subgroup_sensitivity.csv"))
main <- read.csv(file.path(out, "output/F2_main_keycoef.csv")); main$analysis <- "Primary model (fully adjusted)"
labmap <- c("亚组: 女性" = "Women", "亚组: 男性" = "Men",
            "亚组: 基线<65岁" = "Baseline age <65 y", "亚组: 基线≥65岁" = "Baseline age ≥65 y",
            "亚组: 低教育" = "No formal education", "亚组: 中高教育" = "Any formal education",
            "敏感S1: 纯中点插值" = "S1: Midpoint-only event timing",
            "敏感S2: 排除2018窗口事件" = "S2: Excluding 2018-window events",
            "敏感S3: 仅用2020年前事件" = "S3: Pre-2020 events only",
            "敏感S4: BMI完整病例" = "S4: BMI complete cases",
            "敏感S5: 仅人口学校正" = "S5: Demographics-only adjustment",
            "S6: W6去重(每人第六轮仅一次)" = "S6: First sixth-wave assessment only",
            "S7 baseline-standardized: zb_wrmean" = "S7: Baseline-distribution standardization",
            "S8: 排除疑似复发卒中" = "S8: Excluding possible recurrent stroke")
s6 <- read.csv(file.path(out, "output/S6_w6dedup.csv"))
g2b <- read.csv(file.path(out, "output/G2_domain_models.csv"))
s7 <- g2b %>% filter(model == "S7 baseline-standardized: zb_wrmean", term == "stroke")
s8 <- read.csv(file.path(out, "output/G3a_s8_recurrent.csv"))
mi <- read.csv(file.path(out, "output/G6_mi_pooled.csv")) %>%
  filter(term == "stroke") %>%
  transmute(analysis = "S9: Multiple imputation of covariates", est, lo, hi)
ss <- bind_rows(main %>% filter(term == "stroke") %>% transmute(analysis, est, lo, hi),
                sens %>% filter(term == "stroke") %>% transmute(analysis, est, lo, hi),
                s6 %>% filter(term == "stroke") %>% transmute(analysis, est, lo, hi),
                s7 %>% transmute(analysis = model, est, lo, hi),
                s8 %>% filter(term == "stroke") %>% transmute(analysis, est, lo, hi),
                mi)
ss$analysis <- unname(ifelse(ss$analysis %in% names(labmap), labmap[ss$analysis], ss$analysis))
ss$group <- c("Primary", rep("Subgroups", 6), rep("Sensitivity analyses", 9))
ss$analysis <- factor(ss$analysis, levels = rev(ss$analysis))
theme_for <- theme_classic(base_size = 12, base_family = "sans") +
  theme(legend.position = "top", legend.title = element_blank(),
        axis.title = element_text(size = 12, face = "bold"),
        axis.line = element_line(linewidth = 0.5))
p3 <- ggplot(ss, aes(est, analysis)) +
  geom_vline(xintercept = 0, linetype = 3, color = "grey50") +
  geom_errorbar(aes(xmin = lo, xmax = hi, orientation = "y"), width = 0.22, linewidth = 0.5) +
  geom_point(aes(size = group == "Primary"), color = "#B22222", show.legend = FALSE) +
  scale_size_manual(values = c(2.2, 3.2)) +
  labs(x = "Acute memory change at stroke onset, SD (95% CI)", y = NULL) +
  theme_for
ggsave(file.path(out, "figures/Fig3_forest_acute_EN.png"), p3, width = 8, height = 7.5, dpi = 600)
say("Fig3 已加入 S9 (MI)")
