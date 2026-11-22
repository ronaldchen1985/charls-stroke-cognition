## V6: Fine-Gray 全协变量敏感性 (S12) —— survival::finegray + coxph (稳健)
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(survival)})
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
zz <- file.path(out, "output/V6_fg_fulladj.txt"); if (file.exists(zz)) file.remove(zz)
sink(zz, split = TRUE)
set.seed(20261115)

coh <- read.csv(file.path(out, "psci_baseline.csv")); coh$ID11 <- as.character(coh$ID11)
z2  <- read.csv(file.path(out, "psci_cog_long2.csv")); z2$ID11 <- as.character(z2$ID11)
cases_t <- coh$ev_t[coh$ev_wave != "never" & !is.na(coh$ev_t)]
coh$pseudo_t <- NA_real_; nc <- coh$ev_wave != "never" & !is.na(coh$ev_t)
coh$pseudo_t[nc] <- coh$ev_t[nc]; coh$pseudo_t[!nc] <- sample(cases_t, sum(!nc), TRUE)

run_fg_full <- function(zcol, TH) {
  d <- z2 %>% left_join(coh %>% select(ID11, ev_wave, pseudo_t, death_t, sex, age11, edu,
                                       mar, cesd11, smoke3, drink, htn11, dm11, dyslip11, heart11, bmi),
                        by = "ID11") %>%
    filter(!is.na(.data[[zcol]])) %>%
    mutate(stroke = as.integer(ev_wave != "never"), tau = tyr - pseudo_t)
  pre_ok <- d %>% filter(tau < 0) %>% group_by(ID11) %>%
    summarise(min_pre_z = min(.data[[zcol]]), .groups = "drop") %>% filter(min_pre_z > TH)
  post <- d %>% filter(tau > 0, ID11 %in% pre_ok$ID11) %>% group_by(ID11) %>%
    summarise(last_post_tau = max(tau),
              ci = as.integer(any(.data[[zcol]] <= TH)),
              t_ev = ifelse(any(.data[[zcol]] <= TH), min(tau[.data[[zcol]] <= TH]), NA_real_),
              .groups = "drop")
  fg <- coh %>% filter(ID11 %in% pre_ok$ID11) %>% inner_join(post, by = "ID11") %>%
    mutate(stroke = as.integer(ev_wave != "never"),
           dead = !is.na(death_t) & death_t <= 2023.5,
           status = case_when(!is.na(t_ev) ~ 1L, dead ~ 2L, TRUE ~ 0L),
           t_end = case_when(status == 1L ~ pseudo_t + t_ev, status == 2L ~ death_t,
                             TRUE ~ pseudo_t + last_post_tau) - pseudo_t,
           married = as.integer(!is.na(mar) & mar == 1),
           cesd_c = cesd11 - mean(cesd11, na.rm = TRUE),
           smoke3_f = factor(smoke3),
           drink_f = factor(ifelse(is.na(drink), 0L, drink)),
           bmi_na = as.integer(is.na(bmi)),
           bmi_c = ifelse(is.na(bmi), 0, bmi - mean(bmi, na.rm = TRUE)),
           edu3 = cut(edu, c(-Inf, 1, 3, Inf))) %>%
    filter(t_end > 0) %>%
    filter(complete.cases(sex, age11, edu3, married, cesd_c, smoke3_f, drink_f,
                          htn11, dm11, dyslip11, heart11, bmi_c, bmi_na))
  fg$id <- seq_len(nrow(fg))
  fg$status_f <- factor(fg$status, levels = c(0, 1, 2), labels = c("censor", "psci", "death"))
  fgd <- finegray(Surv(t_end, status_f) ~ .,
                  data = fg %>% select(t_end, status_f, id, stroke, age11, sex, edu3,
                                       married, cesd_c, smoke3_f, drink_f, htn11, dm11,
                                       dyslip11, heart11, bmi_c, bmi_na), id = id)
  fit <- coxph(Surv(fgstart, fgstop, fgstatus) ~ stroke + age11 + factor(sex) + edu3 +
                 married + cesd_c + smoke3_f + drink_f + htn11 + dm11 + dyslip11 +
                 heart11 + bmi_c + bmi_na + cluster(id), data = fgd, weights = fgwt)
  sf <- summary(fit)
  data.frame(domain = zcol, threshold = TH,
    hr = sf$conf.int["stroke", "exp(coef)"], lo = sf$conf.int["stroke", "lower .95"],
    hi = sf$conf.int["stroke", "upper .95"],
    p = sf$coefficients["stroke", "Pr(>|z|)"],
    n = nrow(fg), n_event = sum(fg$status == 1), n_death = sum(fg$status == 2),
    n_stroke = sum(fg$stroke == 1))
}

res <- bind_rows(run_fg_full("z_wrmean", -1), run_fg_full("z_wrmean", -1.5),
                 run_fg_full("z_glob", -1), run_fg_full("z_glob", -1.5))
print(res, digits = 3)
write.csv(res, file.path(out, "output/V6_fg_fulladj.csv"), row.names = FALSE)
sink()
