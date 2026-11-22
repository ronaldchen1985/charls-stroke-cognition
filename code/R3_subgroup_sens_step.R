## ============================================================================
## R3: 修订版亚组 + 敏感性电池 (阶跃参数化 + 婚姻协变量)
## 亚组x6; S1中点 S2排除2018窗 S3仅2020前 S4BMI完整 S5仅人口学
##        S6 W6去重 S7基线标准化 S8排除疑似复发; TICS样本内记忆模型
## ============================================================================
options(width = 200)
suppressPackageStartupMessages({library(haven); library(dplyr); library(lme4)})
root <- Sys.getenv("CHARLS_DATA", "D:/CHARLS")  # parent dir of CHARLS wave folders (2011/, 2013/, ...)
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
say <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n")
con <- file(file.path(out, "output/R3_log.txt"), open = "wt"); sink(con, split = TRUE)
set.seed(20261115)
harm_id <- function(id) { id <- as.character(id)
  ifelse(nchar(id) == 12 & substr(id, 10, 10) == "0",
         paste0(substr(id, 1, 9), substr(id, 11, 12)), id) }
yes1 <- function(x) { x <- as.numeric(x); ifelse(is.na(x), NA, as.integer(x == 1)) }

coh <- read.csv(file.path(out, "psci_baseline.csv")); coh$ID11 <- as.character(coh$ID11)
zcog <- read.csv(file.path(out, "psci_cog_long2.csv")); zcog$ID11 <- as.character(zcog$ID11)
cases_t <- coh$ev_t[coh$ev_wave != "never" & !is.na(coh$ev_t)]
coh$pseudo_t <- NA_real_; nc <- coh$ev_wave != "never" & !is.na(coh$ev_t)
coh$pseudo_t[nc] <- coh$ev_t[nc]; coh$pseudo_t[!nc] <- sample(cases_t, sum(!nc), TRUE)

d0 <- zcog %>% left_join(coh %>% select(ID11, ev_wave, ev_t, ev_t_mid, pseudo_t, sex, edu, mar,
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
d0$bmi_c[is.na(d0$bmi_c)] <- 0
COVS <- c("age_c", "factor(sex)", "edu3", "married_f", "cesd_c", "smoke3_f", "drink_f",
          "htn11", "dm11", "dyslip11", "heart11", "bmi_c", "bmi_na")
KEY <- c("tau", "step", "stroke:pre_tau", "stroke:post_tau")

fit_one <- function(dd, label, outcome = "z_wrmean", drop = character(0), minimal = FALSE) {
  dd <- dd %>% filter(!is.na(.data[[outcome]]), !is.na(sex), !is.na(edu3), !is.na(smoke3_f), !is.na(cesd_c))
  cv <- if (minimal) c("age_c", "factor(sex)", "edu3") else setdiff(COVS, drop)
  f <- reformulate(c(cv, "tau", "step", "stroke:pre_tau", "stroke:post_tau", "(1 + tau | ID11)"),
                   response = outcome)
  m <- tryCatch(lmer(f, data = dd, REML = FALSE,
                     control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 1e5))),
                error = function(e) { say(label, " ERROR: ", conditionMessage(e)); NULL })
  if (is.null(m)) return(NULL)
  s <- summary(m)$coefficients; kr <- s[KEY, , drop = FALSE]
  data.frame(analysis = label, outcome = outcome, n_id = n_distinct(dd$ID11),
             n_case = n_distinct(dd$ID11[dd$stroke == 1]),
             term = KEY, est = kr[, 1], se = kr[, 2],
             lo = kr[, 1] - 1.96 * kr[, 2], hi = kr[, 1] + 1.96 * kr[, 2],
             p = 2 * pnorm(-abs(kr[, 3])))
}

res <- list()
## ---------- 亚组 ----------
res$female   <- fit_one(d0 %>% filter(sex == 2), "Subgroup: women", drop = "factor(sex)")
res$male     <- fit_one(d0 %>% filter(sex == 1), "Subgroup: men", drop = "factor(sex)")
res$age_lt65 <- fit_one(d0 %>% filter(age11 < 65), "Subgroup: baseline age <65 y")
res$age_ge65 <- fit_one(d0 %>% filter(age11 >= 65), "Subgroup: baseline age >=65 y")
res$edu_low  <- fit_one(d0 %>% filter(edu <= 1 | is.na(edu)), "Subgroup: no formal education", drop = "edu3")
res$edu_high <- fit_one(d0 %>% filter(!is.na(edu) & edu > 1), "Subgroup: any formal education", drop = "edu3")
## ---------- 敏感性 ----------
res$s1 <- fit_one(d0 %>% mutate(pseudo_t = ifelse(stroke == 1, ev_t_mid, pseudo_t),
                                tau = tyr - pseudo_t, pre_tau = pmin(tau, 0),
                                post_tau = pmax(tau, 0),
                                step = as.integer(stroke == 1 & tau >= 0)),
                  "S1: midpoint imputation only")
res$s2 <- fit_one(d0 %>% filter(ev_wave != "18"), "S2: exclude 2015-2018-window events")
res$s3 <- fit_one(d0 %>% filter(!(ev_wave %in% c("21", "22", "23"))),
                  "S3: pre-2020 events only")
res$s4 <- fit_one(d0 %>% filter(!is.na(bmi)) %>% mutate(bmi_na = 0),
                  "S4: BMI complete cases")
res$s5 <- fit_one(d0, "S5: demographics-only adjustment", minimal = TRUE)
## S6: W6 去重
z6 <- zcog %>% arrange(ID11, tyr) %>%
  mutate(is_w6 = wave %in% c("2021", "2022", "2023")) %>%
  group_by(ID11) %>% filter(!is_w6 | cumsum(is_w6) == 1) %>% ungroup()
d6 <- z6 %>% left_join(coh %>% select(ID11, ev_wave, pseudo_t, sex, edu, mar,
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
         cesd_c = (cesd11 - 8) / 5, bmi_c = (bmi - 24) / 3, bmi_na = as.integer(is.na(bmi)),
         drink_f = factor(ifelse(is.na(drink), 3, drink)), smoke3_f = factor(smoke3))
d6$bmi_c[is.na(d6$bmi_c)] <- 0
res$s6 <- fit_one(d6, "S6: first sixth-wave assessment only")
## S7: 基线分布标准化 (波内可比性去除)
res$s7m <- fit_one(d0, "S7: baseline-standardized, memory", outcome = "zb_wrmean")
res$s7g <- fit_one(d0, "S7: baseline-standardized, global", outcome = "zb_glob")
## S8: 排除疑似复发
say("S8: 重建疑似复发名单 ...")
h15 <- read_dta(file.path(root, "2015/Health_Status_and_Functioning.dta"))
r15 <- data.frame(ID11 = harm_id(h15$ID), new15 = yes1(h15$da007_w2_2_8_))
r21 <- data.frame(ID11 = harm_id(read_dta(file.path(root, "2021/Health_Status_and_Functioning.dta"))$ID),
                  new21 = yes1(read_dta(file.path(root, "2021/Health_Status_and_Functioning.dta"))$da011_8_))
r22 <- data.frame(ID11 = harm_id(read_dta(file.path(root, "2022/Health_Status_and_Functioning.dta"))$ID),
                  new22 = yes1(read_dta(file.path(root, "2022/Health_Status_and_Functioning.dta"))$da011_8_))
r23 <- data.frame(ID11 = harm_id(read_dta(file.path(root, "2023/Health_Status_and_Functioning.dta"))$ID),
                  new23 = yes1(read_dta(file.path(root, "2023/Health_Status_and_Functioning.dta"))$da011_8_))
rec <- coh %>% filter(ev_wave != "never") %>% select(ID11, ev_wave) %>%
  left_join(r15, by = "ID11") %>% left_join(r21, by = "ID11") %>%
  left_join(r22, by = "ID11") %>% left_join(r23, by = "ID11")
worder <- c("13" = 2, "15" = 3, "18" = 4, "20" = 5, "21" = 6, "22" = 7, "23" = 8)
rec$w0 <- worder[rec$ev_wave]
rec$recur <- as.integer(
  (rec$w0 < 3 & !is.na(rec$new15) & rec$new15 == 1) |
  (rec$w0 < 6 & !is.na(rec$new21) & rec$new21 == 1) |
  (rec$w0 < 7 & !is.na(rec$new22) & rec$new22 == 1) |
  (rec$w0 < 8 & !is.na(rec$new23) & rec$new23 == 1))
recur_ids <- rec$ID11[rec$recur == 1 & !is.na(rec$recur)]
say("疑似复发: ", length(recur_ids), " 例")
res$s8 <- fit_one(d0 %>% filter(!ID11 %in% recur_ids), "S8: exclude possible recurrent stroke")
## ---------- TICS 样本内记忆模型 (域间可比性) ----------
tics_ids <- d0$ID11[!is.na(d0$z_tics)] %>% unique()
res$tics_mem <- fit_one(d0 %>% filter(ID11 %in% tics_ids),
                        "Memory model within TICS-assessed sample")

allres <- bind_rows(res)
write.csv(allres, file.path(out, "output/R3_subgroup_sens_step.csv"), row.names = FALSE)
say("\n===== 急性效应 (step) 汇总 =====")
allres %>% filter(term == "step") %>%
  select(analysis, outcome, n_case, est, lo, hi, p) %>% print(digits = 3)
say("\n===== 卒中前斜率差 =====")
allres %>% filter(term == "stroke:pre_tau") %>%
  select(analysis, est, lo, hi, p) %>% print(digits = 3)
sink(); close(con)
cat("R3 done\n")
