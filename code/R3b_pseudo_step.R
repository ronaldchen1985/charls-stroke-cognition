## R3b: 伪锚点 20 次抽样 (阶跃版) —— 用法: Rscript R3b_pseudo_step.R <outcome>
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(lme4)})
args <- commandArgs(trailingOnly = TRUE)
OC <- if (length(args) >= 1) args[1] else "z_wrmean"
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
say <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n")
con <- file(file.path(out, paste0("output/R3b_log_", OC, ".txt")), open = "wt")
sink(con, split = TRUE)

coh <- read.csv(file.path(out, "psci_baseline.csv")); coh$ID11 <- as.character(coh$ID11)
zcog <- read.csv(file.path(out, "psci_cog_long2.csv")); zcog$ID11 <- as.character(zcog$ID11)
cases_t <- coh$ev_t[coh$ev_wave != "never" & !is.na(coh$ev_t)]
nc <- coh$ev_wave != "never" & !is.na(coh$ev_t)

base <- zcog %>% left_join(coh %>% select(ID11, ev_wave, ev_t, sex, edu, mar,
                        cesd11, smoke3, drink, htn11, dm11, dyslip11, heart11, bmi),
                        by = "ID11", suffix = c("", ".y")) %>%
  mutate(stroke = as.integer(ev_wave != "never"),
         age_c = (age11 - 65) / 10,
         edu3 = cut(edu, c(-Inf, 1, 3, Inf), labels = c("low", "mid", "high")),
         married_f = factor(ifelse(is.na(mar), "unknown",
                            ifelse(mar %in% c(1, 2), "married", "other")),
                            levels = c("married", "other", "unknown")),
         cesd_c = (cesd11 - 8) / 5, bmi_c = (bmi - 24) / 3,
         bmi_na = as.integer(is.na(bmi)),
         drink_f = factor(ifelse(is.na(drink), 3, drink)), smoke3_f = factor(smoke3))
base$bmi_c[is.na(base$bmi_c)] <- 0
base <- base %>% filter(!is.na(.data[[OC]]), !is.na(sex), !is.na(edu3), !is.na(smoke3_f), !is.na(cesd_c))
f <- reformulate(c("age_c", "factor(sex)", "edu3", "married_f", "cesd_c", "smoke3_f", "drink_f",
                   "htn11", "dm11", "dyslip11", "heart11", "bmi_c", "bmi_na",
                   "tau", "step", "stroke:pre_tau", "stroke:post_tau", "(1 + tau | ID11)"),
                 response = OC)

csv <- file.path(out, paste0("output/R3b_pseudo20_step_", OC, ".csv"))
if (file.exists(csv)) file.remove(csv)
for (i in 1:20) {
  set.seed(1000 + i)
  pseudo <- ifelse(nc, coh$ev_t, NA_real_)
  pseudo[!nc] <- sample(cases_t, sum(!nc), TRUE)
  pmap <- setNames(pseudo, coh$ID11)
  dd <- base %>% mutate(pseudo_t = pmap[ID11], tau = tyr - pseudo_t,
                        pre_tau = pmin(tau, 0), post_tau = pmax(tau, 0),
                        step = as.integer(stroke == 1 & tau >= 0))
  m <- tryCatch(lmer(f, data = dd, REML = FALSE,
                     control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 5e4))),
                error = function(e) NULL)
  if (!is.null(m)) {
    s <- summary(m)$coefficients
    ri <- data.frame(draw = i, term = "step", est = s["step", 1], se = s["step", 2],
                     lo = s["step", 1] - 1.96 * s["step", 2],
                     hi = s["step", 1] + 1.96 * s["step", 2],
                     p = 2 * pnorm(-abs(s["step", 3])))
    write.table(ri, csv, sep = ",", row.names = FALSE, col.names = !file.exists(csv),
                append = file.exists(csv))
    say("draw ", i, ": ", round(ri$est, 4))
  }
}
rr <- read.csv(csv)
say("20 次范围: ", round(min(rr$est), 3), " ~ ", round(max(rr$est), 3),
    "; 最大P=", format.pval(max(rr$p), digits = 2))
sink(); close(con)
cat("R3b ", OC, " done\n")
