## R4b: ibind 合并 4x5=20 插补集, 阶跃主模型 + Rubin 合并
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(lme4); library(mice)})
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
logf <- file.path(out, "output/R4b_log.txt")
if (file.exists(logf)) file.remove(logf)
wlog <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n", file = logf, append = TRUE)

imp <- readRDS(file.path(out, "output/R4_mids_seed101.rds"))
for (sd in c(102, 103, 104)) {
  imp <- ibind(imp, readRDS(file.path(out, sprintf("output/R4_mids_seed%d.rds", sd))))
}
wlog("合并后 m=", imp$m)

coh <- read.csv(file.path(out, "psci_baseline.csv")); coh$ID11 <- as.character(coh$ID11)
z1  <- read.csv(file.path(out, "psci_cog_long.csv"));  z1$ID11 <- as.character(z1$ID11)
set.seed(20261115)
cases_t <- coh$ev_t[coh$ev_wave != "never" & !is.na(coh$ev_t)]
coh$pseudo_t <- NA_real_; nc <- coh$ev_wave != "never" & !is.na(coh$ev_t)
coh$pseudo_t[nc] <- coh$ev_t[nc]; coh$pseudo_t[!nc] <- sample(cases_t, sum(!nc), TRUE)

KEY <- c("tau", "step", "stroke:pre_tau", "stroke:post_tau")
ests <- matrix(NA, imp$m, 4); ses <- matrix(NA, imp$m, 4)
for (i in seq_len(imp$m)) {
  ci <- complete(imp, i)
  d <- z1 %>% select(ID11, wave, z_wrmean, tyr, sex, age11) %>%
    left_join(ci %>% transmute(ID11 = as.character(ID11),
                               edu_i = edu, mar_i = mar, cesd_i = cesd11,
                               smoke3_i = smoke3, drink_i = drink, bmi_i = bmi,
                               htn_i = htn11, dm_i = dm11, dyslip_i = dyslip11,
                               heart_i = heart11),
              by = "ID11") %>%
    left_join(coh %>% select(ID11, ev_wave, pseudo_t), by = "ID11") %>%
    mutate(stroke = as.integer(ev_wave != "never"), tau = tyr - pseudo_t,
           pre_tau = pmin(tau, 0), post_tau = pmax(tau, 0),
           step = as.integer(stroke == 1 & tau >= 0),
           age_c = (age11 - 65) / 10,
           edu3 = cut(as.numeric(as.character(edu_i)), c(-Inf, 1, 3, Inf),
                      labels = c("low", "mid", "high")),
           married_f = factor(ifelse(mar_i %in% c(1, 2), "married", "other"),
                              levels = c("married", "other")),
           cesd_c = (cesd_i - 8) / 5, bmi_c = (bmi_i - 24) / 3,
           bmi_na = 0L,
           drink_f = factor(drink_i), smoke3_f = factor(smoke3_i))
  d <- d %>% filter(!is.na(z_wrmean))
  m <- tryCatch(lmer(z_wrmean ~ age_c + factor(sex) + edu3 + married_f + cesd_c +
                       smoke3_f + drink_f + htn_i + dm_i + dyslip_i + heart_i +
                       bmi_c + bmi_na + tau + step + stroke:pre_tau + stroke:post_tau +
                       (1 + tau | ID11),
                     data = d, REML = FALSE,
                     control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 1e5))),
                error = function(e) { wlog("imp ", i, " ERROR: ", conditionMessage(e)); NULL })
  if (!is.null(m)) {
    s <- summary(m)$coefficients
    ests[i, ] <- s[KEY, 1]; ses[i, ] <- s[KEY, 2]
    wlog("imp ", i, " step=", round(s["step", 1], 4))
  }
}
## Rubin 合并
M <- colSums(!is.na(ests))
qbar <- colMeans(ests, na.rm = TRUE)
ubar <- colMeans(ses^2, na.rm = TRUE)
bvar <- apply(ests, 2, var, na.rm = TRUE)
tvar <- ubar + (1 + 1 / M) * bvar
pooled <- data.frame(term = KEY, est = qbar, se = sqrt(tvar),
                     lo = qbar - 1.96 * sqrt(tvar), hi = qbar + 1.96 * sqrt(tvar),
                     p = 2 * pnorm(-abs(qbar / sqrt(tvar))), m_used = M)
print(pooled, digits = 4)
write.csv(pooled, file.path(out, "output/R4_mi20_pooled.csv"), row.names = FALSE)
wlog("done")
