## ============================================================================
## R2: 修订版主模型 —— 阶跃参数化 (step = stroke x I(tau>=0)) + 婚姻状况协变量
## 主模型 B: z ~ covs + married + tau + step + stroke:pre_tau + stroke:post_tau
## 输出: 四域+亚域系数、样条/阶跃 AIC 对比、性别与年龄正式交互、Fig1 预测
## ============================================================================
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(lme4)})
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
say <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n")
con <- file(file.path(out, "output/R2_log.txt"), open = "wt"); sink(con, split = TRUE)
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
         edu3 = cut(edu, c(-Inf, 1, 3, Inf), labels = c("low", "mid", "high")),
         married_f = factor(ifelse(is.na(mar), "unknown",
                            ifelse(mar %in% c(1, 2), "married", "other")),
                            levels = c("married", "other", "unknown")),
         cesd_c = (cesd11 - 8) / 5, bmi_c = (bmi - 24) / 3,
         bmi_na = as.integer(is.na(bmi)),
         drink_f = factor(ifelse(is.na(drink), 3, drink)), smoke3_f = factor(smoke3))
d$bmi_c[is.na(d$bmi_c)] <- 0
d <- d %>% filter(!is.na(sex), !is.na(edu3), !is.na(smoke3_f), !is.na(cesd_c))
say("分析框架: ", n_distinct(d$ID11), " 人, ", nrow(d), " 人-波; married 缺失 ",
    sum(d$married_f == "unknown" & !duplicated(d$ID11)))

covs <- c("age_c", "factor(sex)", "edu3", "married_f", "cesd_c", "smoke3_f", "drink_f",
          "htn11", "dm11", "dyslip11", "heart11", "bmi_c", "bmi_na")
rhs_step   <- c(covs, "tau", "step", "stroke:pre_tau", "stroke:post_tau")
rhs_spline <- c(covs, "tau", "stroke", "stroke:pre_tau", "stroke:post_tau")
rhs_stepC  <- c(covs, "tau", "stroke", "step", "stroke:pre_tau", "stroke:post_tau")
key_step   <- c("tau", "step", "stroke:pre_tau", "stroke:post_tau")

fit_m <- function(outcome, rhs, data = d) {
  dd <- data %>% filter(!is.na(.data[[outcome]]))
  m <- lmer(reformulate(c(rhs, "(1 + tau | ID11)"), response = outcome), data = dd,
            REML = FALSE, control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5)))
  list(m = m, n = n_distinct(dd$ID11), npw = nrow(dd))
}
ext <- function(f, terms, model) {
  s <- summary(f$m)$coefficients
  terms <- terms[terms %in% rownames(s)]
  data.frame(model = model, term = terms, est = s[terms, 1], se = s[terms, 2],
             lo = s[terms, 1] - 1.96 * s[terms, 2], hi = s[terms, 1] + 1.96 * s[terms, 2],
             p = 2 * pnorm(-abs(s[terms, 3])), n_id = f$n, n_pw = f$npw)
}

res <- list(); models <- list()
## ---------- 1) 四域 + 亚域 (阶跃主模型) ----------
for (oc in c("z_wrmean", "z_tics", "z_visuo", "z_glob", "z_wr_i", "z_wr_d")) {
  say("阶跃拟合 ", oc, " ...")
  f <- fit_m(oc, rhs_step); models[[oc]] <- f
  res[[oc]] <- ext(f, key_step, paste0("step: ", oc))
  say("  acute=", round(summary(f$m)$coefficients["step", 1], 3),
      " n=", f$n, " pw=", f$npw)
}
## ---------- 2) 样条对照 + 阶跃C (记忆/全域, AIC 对比) ----------
aic_tab <- list()
for (oc in c("z_wrmean", "z_glob")) {
  fs <- fit_m(oc, rhs_spline); fc <- fit_m(oc, rhs_stepC)
  res[[paste0("spline_", oc)]] <- ext(fs, c("tau", "stroke", "stroke:pre_tau", "stroke:post_tau"),
                                      paste0("spline: ", oc))
  res[[paste0("stepC_", oc)]]   <- ext(fc, c("tau", "stroke", "step", "stroke:pre_tau", "stroke:post_tau"),
                                       paste0("step+main: ", oc))
  aic_tab[[oc]] <- data.frame(outcome = oc,
    AIC_spline = AIC(fs$m), AIC_step = AIC(models[[oc]]$m), AIC_stepC = AIC(fc$m))
}
aic_tab <- bind_rows(aic_tab); print(aic_tab)
write.csv(aic_tab, file.path(out, "output/R2_aic_compare.csv"), row.names = FALSE)

## ---------- 3) 正式交互: 性别 + 年龄组 (记忆主结局) ----------
say("性别交互 LRT ...")
f_sex <- fit_m("z_wrmean", c(rhs_step, "step:factor(sex)", "stroke:pre_tau:factor(sex)",
                             "stroke:post_tau:factor(sex)"))
lrt_sex <- anova(models[["z_wrmean"]]$m, f_sex$m)
print(lrt_sex)
s_sex <- summary(f_sex$m)$coefficients
print(s_sex[grep("step:factor|pre_tau:factor|post_tau:factor", rownames(s_sex)), ], digits = 3)

say("年龄组交互 LRT ...")
d$agegrp <- factor(ifelse(d$age11 >= 65, "ge65", "lt65"))
f_age <- fit_m("z_wrmean", c(rhs_step, "step:agegrp", "stroke:pre_tau:agegrp",
                             "stroke:post_tau:agegrp"), data = d)
lrt_age <- anova(models[["z_wrmean"]]$m, f_age$m)
print(lrt_age)
s_age <- summary(f_age$m)$coefficients
print(s_age[grep("agegrp", rownames(s_age)), ], digits = 3)
write.csv(data.frame(test = c("sex_interaction_3df", "age_interaction_3df"),
                     chisq = c(lrt_sex$Chisq[2], lrt_age$Chisq[2]),
                     df = c(lrt_sex$Df[2], lrt_age$Df[2]),
                     p = c(lrt_sex$`Pr(>Chisq)`[2], lrt_age$`Pr(>Chisq)`[2])),
          file.path(out, "output/R2_interactions.csv"), row.names = FALSE)

## ---------- 4) Fig1 预测轨迹 (阶跃模型, 四域) ----------
tau_grid <- seq(-10, 7, by = 0.25)
pred_all <- list()
for (oc in c("z_wrmean", "z_tics", "z_visuo", "z_glob")) {
  f <- models[[oc]]; dd <- f$m@frame
  newd <- dd[rep(1, 2 * length(tau_grid)), , drop = FALSE]
  newd$tau <- rep(tau_grid, 2); newd$stroke <- rep(0:1, each = length(tau_grid))
  newd$pre_tau <- pmin(newd$tau, 0); newd$post_tau <- pmax(newd$tau, 0)
  newd$step <- as.integer(newd$stroke == 1 & newd$tau >= 0)
  newd$age_c <- 0; newd$sex <- 2; newd$edu3 <- factor("low", levels = c("low", "mid", "high"))
  newd$married_f <- factor("married", levels = c("married", "other", "unknown"))
  newd$cesd_c <- 0; newd$smoke3_f <- factor("0", levels = levels(d$smoke3_f))
  newd$drink_f <- factor("3", levels = levels(d$drink_f))
  newd$htn11 <- 0; newd$dm11 <- 0; newd$dyslip11 <- 0; newd$heart11 <- 0
  newd$bmi_c <- 0; newd$bmi_na <- 0
  newd$ID11 <- paste0("NEW", seq_len(nrow(newd)))
  newd$pred <- as.numeric(predict(f$m, newdata = newd, re.form = NA, allow.new.levels = TRUE))
  shift <- newd$pred[newd$stroke == 1 & newd$tau == -10]
  pred_all[[oc]] <- data.frame(outcome = oc, tau = newd$tau, stroke = newd$stroke,
                               pred = newd$pred - shift)
}
pred_all <- bind_rows(pred_all)
write.csv(pred_all, file.path(out, "output/R2_pred_traj_step.csv"), row.names = FALSE)

allres <- bind_rows(res)
write.csv(allres, file.path(out, "output/R2_main_step.csv"), row.names = FALSE)
saveRDS(models, file.path(out, "output/R2_models.rds"))
say("\n===== 主模型关键系数 (阶跃) =====")
print(allres %>% filter(grepl("^step:", model)), digits = 3)
say("\n===== 样条对照 =====")
print(allres %>% filter(grepl("^spline:", model)), digits = 3)
sink(); close(con)
cat("R2 done\n")
