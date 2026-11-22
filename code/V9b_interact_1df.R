## V9b: 1-df step 交互 Wald 检验（sex / agegrp / education）—— 输出 output/V9_step_interactions_1df.csv
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(lme4)})
out <- Sys.getenv("PROJ_ROOT", getwd())
set.seed(20261115)

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
         agegrp = factor(ifelse(age11 < 65, "lt65", "ge65"), levels = c("lt65", "ge65")),
         edu_any = factor(ifelse(edu >= 2, "any", "none"), levels = c("none", "any")),
         edu3 = cut(edu, c(-Inf, 1, 3, Inf), labels = c("low", "mid", "high")),
         married_f = factor(ifelse(is.na(mar), "unknown",
                            ifelse(mar %in% c(1, 2), "married", "other")),
                            levels = c("married", "other", "unknown")),
         cesd_c = (cesd11 - 8) / 5, bmi_c = (bmi - 24) / 3,
         bmi_na = as.integer(is.na(bmi)),
         drink_f = factor(ifelse(is.na(drink), 3, drink)), smoke3_f = factor(smoke3))
d$bmi_c[is.na(d$bmi_c)] <- 0
d <- d %>% filter(!is.na(sex), !is.na(edu3), !is.na(smoke3_f), !is.na(cesd_c), !is.na(z_wrmean))

covs <- c("age_c", "factor(sex)", "edu3", "married_f", "cesd_c", "smoke3_f", "drink_f",
          "htn11", "dm11", "dyslip11", "heart11", "bmi_c", "bmi_na")

run <- function(extra, label, token) {
  m <- lmer(reformulate(c(covs, "tau", "step", "stroke:pre_tau", "stroke:post_tau", extra,
                          "(1 + tau | ID11)"), response = "z_wrmean"), data = d, REML = FALSE,
            control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5)))
  s <- summary(m)$coefficients
  trm <- grep(token, rownames(s), value = TRUE)
  trm <- trm[grepl("step", trm) & !grepl("stroke", trm)]
  data.frame(group = label, term = trm, est = s[trm, 1], se = s[trm, 2],
             lo = s[trm, 1] - 1.96 * s[trm, 2], hi = s[trm, 1] + 1.96 * s[trm, 2],
             p = 2 * pnorm(-abs(s[trm, 3])))
}

r <- bind_rows(
  run(c("step:factor(sex)", "stroke:pre_tau:factor(sex)", "stroke:post_tau:factor(sex)"),
      "sex", "factor\\(sex\\)"),
  run(c("step:agegrp", "stroke:pre_tau:agegrp", "stroke:post_tau:agegrp"),
      "age", "agegrp"),
  run(c("step:edu_any", "stroke:pre_tau:edu_any", "stroke:post_tau:edu_any"),
      "education", "edu_any"))
print(r)
write.csv(r, file.path(out, "output/V9_step_interactions_1df.csv"), row.names = FALSE)
cat("V9b done\n")
