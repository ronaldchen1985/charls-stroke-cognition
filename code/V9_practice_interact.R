## ============================================================================
## V9: S13 练习效应敏感性 + 1-df step 交互检验
## (1) 主记忆模型 + 访次编号 (visit_n)：检验卒中前正斜率差是否由练习效应解释
## (2) step 特异的 1-df 交互 Wald 检验：sex / agegrp / education
## 输出: output/V9_practice_s13.csv, output/V9_step_interactions_1df.csv, output/V9_log.txt
## ============================================================================
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(lme4)})
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
con <- file(file.path(out, "output/V9_log.txt"), open = "wt"); sink(con, split = TRUE)
set.seed(20261115)  # 与 R2 主模型相同的锚点抽取

coh <- read.csv(file.path(out, "psci_baseline.csv"))
zcog <- read.csv(file.path(out, "psci_cog_long2.csv"))
cases_t <- coh$ev_t[coh$ev_wave != "never" & !is.na(coh$ev_t)]
coh$pseudo_t <- NA_real_; nc <- coh$ev_wave != "never" & !is.na(coh$ev_t)
coh$pseudo_t[nc] <- coh$ev_t[nc]; coh$pseudo_t[!nc] <- sample(cases_t, sum(!nc), TRUE)

d <- zcog %>% left_join(coh %>% select(ID11, ev_wave, pseudo_t, sex, edu, mar,
                        cesd11, smoke3, drink, htn11, dm11, dyslip11, heart11, bmi),
                        by = "ID11", suffix = c("", ".y")) %>%
  mutate(stroke = as.integer(ev_wave != "never"), tau = tyr - pseudo_t,
         pre_tau = pmin(tau, 0), post_tau = pmax(tau, 0),
         step = as.integer(stroke == 1 & tau >= 0),
         age_c = (age11 - 65) / 10,
         agegrp = ifelse(age11 < 65, "lt65", "ge65"),
         edu_any = ifelse(edu >= 2, "any", "none"),
         edu3 = cut(edu, c(-Inf, 1, 3, Inf), labels = c("low", "mid", "high")),
         married_f = factor(ifelse(is.na(mar), "unknown",
                            ifelse(mar %in% c(1, 2), "married", "other")),
                            levels = c("married", "other", "unknown")),
         cesd_c = (cesd11 - 8) / 5, bmi_c = (bmi - 24) / 3,
         bmi_na = as.integer(is.na(bmi)),
         drink_f = factor(ifelse(is.na(drink), 3, drink)), smoke3_f = factor(smoke3))
d$bmi_c[is.na(d$bmi_c)] <- 0
d <- d %>% filter(!is.na(sex), !is.na(edu3), !is.na(smoke3_f), !is.na(cesd_c))
## 访次编号：每人按访谈年排序的第 k 次认知测量
d <- d %>% arrange(ID11, tyr) %>% group_by(ID11) %>% mutate(visit_n = row_number()) %>% ungroup()

covs <- c("age_c", "factor(sex)", "edu3", "married_f", "cesd_c", "smoke3_f", "drink_f",
          "htn11", "dm11", "dyslip11", "heart11", "bmi_c", "bmi_na")
key  <- c("tau", "step", "stroke:pre_tau", "stroke:post_tau")

fit_ext <- function(rhs, label, terms = key) {
  dd <- d %>% filter(!is.na(z_wrmean))
  m <- lmer(reformulate(c(rhs, "(1 + tau | ID11)"), response = "z_wrmean"), data = dd,
            REML = FALSE, control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5)))
  s <- summary(m)$coefficients
  terms <- terms[terms %in% rownames(s)]
  data.frame(model = label, term = terms, est = s[terms, 1], se = s[terms, 2],
             lo = s[terms, 1] - 1.96 * s[terms, 2], hi = s[terms, 1] + 1.96 * s[terms, 2],
             p = 2 * pnorm(-abs(s[terms, 3])))
}

## ---------- (1) S13: 练习效应（访次调整） ----------
cat("== S13: 主模型 + 访次编号 ==\n")
r0 <- fit_ext(c(covs, "tau", "step", "stroke:pre_tau", "stroke:post_tau"), "S13_base_refit")
r1 <- fit_ext(c(covs, "visit_n", "tau", "step", "stroke:pre_tau", "stroke:post_tau"),
              "S13_visit_adj", terms = c(key, "visit_n"))
print(rbind(r0, r1))
write.csv(rbind(r0, r1), file.path(out, "output/V9_practice_s13.csv"), row.names = FALSE)

## ---------- (2) 1-df step 交互 ----------
cat("\n== 1-df step 交互 Wald 检验 ==\n")
i_sex <- fit_ext(c(covs, "tau", "step", "stroke:pre_tau", "stroke:post_tau",
                   "step:factor(sex)", "stroke:pre_tau:factor(sex)", "stroke:post_tau:factor(sex)"),
                 "sex", terms = "step:factor(sex)2")
i_age <- fit_ext(c(covs, "tau", "step", "stroke:pre_tau", "stroke:post_tau",
                   "step:agegrp", "stroke:pre_tau:agegrp", "stroke:post_tau:agegrp"),
                 "age", terms = grep("^step:agegrp", rownames(summary(lmer(reformulate(
                   c(covs, "tau", "step", "stroke:pre_tau", "stroke:post_tau", "step:agegrp",
                     "stroke:pre_tau:agegrp", "stroke:post_tau:agegrp", "(1 + tau | ID11)"),
                   response = "z_wrmean"), data = d %>% filter(!is.na(z_wrmean)), REML = FALSE,
                   control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))))$coefficients, value = TRUE))
i_edu <- fit_ext(c(covs, "tau", "step", "stroke:pre_tau", "stroke:post_tau",
                   "step:edu_any", "stroke:pre_tau:edu_any", "stroke:post_tau:edu_any"),
                 "education", terms = grep("^step:edu_any", rownames(summary(lmer(reformulate(
                   c(covs, "tau", "step", "stroke:pre_tau", "stroke:post_tau", "step:edu_any",
                     "stroke:pre_tau:edu_any", "stroke:post_tau:edu_any", "(1 + tau | ID11)"),
                   response = "z_wrmean"), data = d %>% filter(!is.na(z_wrmean)), REML = FALSE,
                   control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))))$coefficients, value = TRUE))
ii <- bind_rows(i_sex, i_age, i_edu)
print(ii)
write.csv(ii, file.path(out, "output/V9_step_interactions_1df.csv"), row.names = FALSE)
cat("\nV9 done\n")
