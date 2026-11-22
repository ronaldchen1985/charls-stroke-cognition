## ============================================================================
## R5: PSCI Fine-Gray 定稿 (末次测点删失) —— 记忆/全域 x -1/-1.5 SD
## + 比例假设检验 + E-value (朴素与 sqrt 近似) + 在险人数 + 流程数字
## ============================================================================
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(cmprsk)})
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
logf <- file.path(out, "output/R5_log.txt"); if (file.exists(logf)) file.remove(logf)
wlog <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n", file = logf, append = TRUE)
set.seed(20261115)

coh <- read.csv(file.path(out, "psci_baseline.csv")); coh$ID11 <- as.character(coh$ID11)
z2  <- read.csv(file.path(out, "psci_cog_long2.csv")); z2$ID11 <- as.character(z2$ID11)
cases_t <- coh$ev_t[coh$ev_wave != "never" & !is.na(coh$ev_t)]
coh$pseudo_t <- NA_real_; nc <- coh$ev_wave != "never" & !is.na(coh$ev_t)
coh$pseudo_t[nc] <- coh$ev_t[nc]; coh$pseudo_t[!nc] <- sample(cases_t, sum(!nc), TRUE)

eval_rr  <- function(rr) rr + sqrt(rr * (rr - 1))
run_fg_z <- function(zcol, TH) {
  d <- z2 %>% left_join(coh %>% select(ID11, ev_wave, pseudo_t, death_t, sex, age11, edu),
                        by = "ID11") %>%
    filter(!is.na(.data[[zcol]])) %>%
    mutate(stroke = as.integer(ev_wave != "never"), tau = tyr - pseudo_t)
  pre_all <- d %>% filter(tau < 0) %>% group_by(ID11) %>%
    summarise(min_pre_z = min(.data[[zcol]]), .groups = "drop")
  pre_ok <- pre_all %>% filter(min_pre_z > TH)
  n_with <- n_distinct(d$ID11); n_nopre <- n_with - nrow(pre_all)
  n_pre_imp <- nrow(pre_all) - nrow(pre_ok)
  post <- d %>% filter(tau > 0, ID11 %in% pre_ok$ID11) %>% group_by(ID11) %>%
    summarise(last_post_tau = max(tau), n_post = n(),
              ci = as.integer(any(.data[[zcol]] <= TH)),
              t_ev = ifelse(any(.data[[zcol]] <= TH), min(tau[.data[[zcol]] <= TH]), NA_real_),
              .groups = "drop")
  fg <- coh %>% filter(ID11 %in% pre_ok$ID11) %>% inner_join(post, by = "ID11") %>%
    mutate(stroke = as.integer(ev_wave != "never"),
           dead = !is.na(death_t) & death_t <= 2023.5,
           status = case_when(!is.na(t_ev) ~ 1L, dead ~ 2L, TRUE ~ 0L),
           t_end = case_when(status == 1L ~ pseudo_t + t_ev, status == 2L ~ death_t,
                             TRUE ~ pseudo_t + last_post_tau) - pseudo_t) %>%
    filter(t_end > 0)
  covm <- model.matrix(~ stroke + age11 + factor(sex) + cut(edu, c(-Inf, 1, 3, Inf)),
                       data = fg)[, -1]
  fgr <- crr(ftime = fg$t_end, fstatus = fg$status, cov1 = covm, failcode = 1, cencode = 0)
  sf <- summary(fgr)
  gry <- cuminc(ftime = fg$t_end, fstatus = fg$status, group = fg$stroke, cencode = 0)
  tp <- timepoints(gry, times = c(2, 5, 8))
  i_s <- grep("^1 ", rownames(tp$est))[1]; i_c <- grep("^0 ", rownames(tp$est))[1]
  ## 比例子分布假设: stroke x log(t)
  cov2 <- matrix(fg$stroke, ncol = 1)
  fgr_tv <- crr(ftime = fg$t_end, fstatus = fg$status, cov1 = covm, cov2 = cov2,
                tf = function(uft) cbind(log(uft)), failcode = 1, cencode = 0)
  ph_p <- summary(fgr_tv)$coef[nrow(summary(fgr_tv)$coef), "p-value"]
  ## 在险人数
  atr <- sapply(c(0, 2, 4, 6, 8), function(tt)
    c(sum(fg$stroke == 0 & fg$t_end >= tt), sum(fg$stroke == 1 & fg$t_end >= tt)))
  hr <- sf$coef["stroke", "exp(coef)"]
  summ <- data.frame(domain = zcol, threshold = TH,
    hr = hr, lo = sf$conf.int["stroke", "2.5%"], hi = sf$conf.int["stroke", "97.5%"],
    p = sf$coef["stroke", "p-value"], gray_p = gry$Tests[1, 2], ph_p = ph_p,
    evalue_naive = eval_rr(hr), evalue_sqrt = eval_rr(sqrt(hr)),
    n = nrow(fg), n_event = sum(fg$status == 1), n_death = sum(fg$status == 2),
    n_stroke = sum(fg$stroke == 1), n_nopre = n_nopre, n_pre_imp = n_pre_imp,
    cif2_c = tp$est[i_c, "2"], cif5_c = tp$est[i_c, "5"], cif8_c = tp$est[i_c, "8"],
    cif2_s = tp$est[i_s, "2"], cif5_s = tp$est[i_s, "5"], cif8_s = tp$est[i_s, "8"])
  list(summ = summ, fg = fg, gry = gry, atrisk = atr)
}

wlog("===== 记忆 -1 SD (主) =====")
m1 <- run_fg_z("z_wrmean", -1);  print(m1$summ, digits = 3)
wlog("===== 记忆 -1.5 SD =====")
m15 <- run_fg_z("z_wrmean", -1.5); print(m15$summ, digits = 3)
wlog("===== 全域 -1 SD (S10) =====")
g1 <- run_fg_z("z_glob", -1);  print(g1$summ, digits = 3)
wlog("===== 全域 -1.5 SD =====")
g15 <- run_fg_z("z_glob", -1.5); print(g15$summ, digits = 3)

allres <- bind_rows(m1$summ, m15$summ, g1$summ, g15$summ)
write.csv(allres, file.path(out, "output/R5_fg_final.csv"), row.names = FALSE)
write.csv(m1$atr, file.path(out, "output/R5_atrisk.csv"), row.names = FALSE)
saveRDS(list(m1 = m1$gry, m15 = m15$gry, g1 = g1$gry, g15 = g15$gry,
             fg_m1 = m1$fg), file.path(out, "output/R5_gry.rds"))

## 流程数字 (记忆 -1 SD 主定义)
d0 <- z2 %>% filter(!is.na(z_wrmean))
flow <- data.frame(
  step = c("with_memory_measure", "no_pre_anchor_measure", "pre_anchor_impaired",
           "no_post_anchor_measure", "psci_analysis_sample"),
  n = c(n_distinct(d0$ID11), m1$summ$n_nopre, m1$summ$n_pre_imp,
        m1$summ$n_nopre * 0 + (n_distinct(d0$ID11) - m1$summ$n_nopre - m1$summ$n_pre_imp - nrow(m1$fg)),
        nrow(m1$fg)))
print(flow)
write.csv(flow, file.path(out, "output/R5_psci_flow.csv"), row.names = FALSE)
wlog("R5 done")
