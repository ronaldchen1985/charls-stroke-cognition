## ============================================================================
## V8: 校正锚点后的稿件描述性数字 (供 IJS 版正文/表格/流程图更新)
## 输出: output/V8_descriptives.txt
## ============================================================================
options(width = 200)
suppressPackageStartupMessages({library(dplyr)})
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
zz <- file.path(out, "output/V8_descriptives.txt"); if (file.exists(zz)) file.remove(zz)
sink(zz, split = TRUE)
set.seed(20261115)

coh <- read.csv(file.path(out, "psci_baseline.csv")); coh$ID11 <- as.character(coh$ID11)
zcog <- read.csv(file.path(out, "psci_cog_long2.csv")); zcog$ID11 <- as.character(zcog$ID11)
ev <- coh %>% filter(ev_wave != "never")

cat("== 1) 卒中时年龄 / 事件年份 ==\n")
age_at_ev <- ev$age11 + (ev$ev_t - 2011.5)
cat("mean age at stroke:", round(mean(age_at_ev), 1), "+-", round(sd(age_at_ev), 1), "\n")
cat("median event year:", median(ev$ev_t), "\n")
cat("refinement:", sum(!is.na(ev$ev_yr)), "/", nrow(ev), "=", round(mean(!is.na(ev$ev_yr))*100, 1), "%\n")

cat("\n== 2) 测量次数 (全 1,346 例) ==\n")
cg <- zcog %>% filter(ID11 %in% ev$ID11) %>%
  left_join(ev %>% select(ID11, ev_t), by = "ID11") %>%
  mutate(pre = tyr < ev_t, post = tyr >= ev_t)
per <- cg %>% group_by(ID11) %>%
  summarise(n_tot = n(), n_pre = sum(pre), n_post = sum(post), .groups = "drop")
cat("median total measures:", median(per$n_tot), " IQR:", paste(quantile(per$n_tot, c(.25,.75)), collapse="-"), "\n")
cat(">=1 pre & >=1 post:", sum(per$n_pre >= 1 & per$n_post >= 1),
    "(", round(mean(per$n_pre >= 1 & per$n_post >= 1)*100, 1), "% )\n")
cat(">=2 pre & >=2 post:", sum(per$n_pre >= 2 & per$n_post >= 2),
    "(", round(mean(per$n_pre >= 2 & per$n_post >= 2)*100, 1), "% )\n")
cat(">=1 post:", sum(per$n_post >= 1), "(", round(mean(per$n_post >= 1)*100, 1), "% )\n")

cat("\n== 3) Table S4: 有/无卒中后测点 (全 1,346 例) ==\n")
s4 <- ev %>% left_join(per %>% select(ID11, n_post), by = "ID11") %>%
  mutate(has_post = !is.na(n_post) & n_post >= 1)
## 基线记忆 z (2011 波)
z11 <- zcog %>% filter(wave == "2011") %>% select(ID11, z11 = z_wrmean)
s4 <- s4 %>% left_join(z11, by = "ID11") %>%
  mutate(dead = !is.na(death_t), female = sex == 2)
cat("with post:", sum(s4$has_post), " without:", sum(!s4$has_post), "\n")
cat("age11: ", round(tapply(s4$age11, s4$has_post, mean), 1), " P=",
    format.pval(t.test(age11 ~ has_post, data = s4)$p.value, digits = 2, eps = 1e-3), "\n")
cat("z11: ", round(tapply(s4$z11, s4$has_post, mean, na.rm = TRUE), 3), " P=",
    format.pval(t.test(z11 ~ has_post, data = s4)$p.value, digits = 2, eps = 1e-3), "\n")
cat("female %: ", round(tapply(s4$female, s4$has_post, mean)*100, 1), " P=",
    format.pval(chisq.test(s4$female, s4$has_post)$p.value, digits = 2, eps = 1e-3), "\n")
cat("died %: ", round(tapply(s4$dead, s4$has_post, mean)*100, 1), " P=",
    format.pval(chisq.test(s4$dead, s4$has_post)$p.value, digits = 2, eps = 1e-3), "\n")

cat("\n== 4) 分析样本内 (1,197 例) 有后测点例数 ==\n")
cov_ok <- coh %>% filter(!is.na(sex), !is.na(edu), !is.na(smoke3), !is.na(cesd11)) %>%
  filter(ev_wave != "never") %>% pull(ID11)
per_a <- per %>% filter(ID11 %in% cov_ok)
cat("analytic stroke cases:", length(cov_ok), " with >=1 post:", sum(per$n_post >= 1), "\n")

cat("\n== 5) R2 样条对照 (S11) 与 AIC ==\n")
r2 <- read.csv(file.path(out, "output/R2_main_step.csv"))
print(r2 %>% filter(grepl("spline", model)))
print(read.csv(file.path(out, "output/R2_aic_compare.csv")))
cat("\n== 6) 交互检验 ==\n")
print(read.csv(file.path(out, "output/R2_interactions.csv")))
cat("\n== 7) R2 全部阶跃系数 (Table 2 用) ==\n")
print(r2 %>% filter(grepl("^step:", model)) %>% select(model, term, est, lo, hi, p), digits = 3)
cat("\n== 8) 伪锚点 20 次 ==\n")
for (f in c("R3b_pseudo20_step_z_wrmean.csv", "R3b_pseudo20_step_z_glob.csv")) {
  dd <- read.csv(file.path(out, "output", f))
  cat(f, ": est ", round(min(dd$est), 3), " to ", round(max(dd$est), 3),
      "; P max ", format.pval(max(dd$p), digits = 1, eps = 1e-10), "\n") }
sink()
cat("V8 done\n")
