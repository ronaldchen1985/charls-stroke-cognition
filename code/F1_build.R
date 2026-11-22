## ============================================================================
## PSCI_traj F1: 正式分析数据集构建
## 研究: 卒中前后认知轨迹三相解构 (CHARLS 2011-2023)
## 输出: psci_baseline.csv (人级), psci_cog_long.csv (人-波长表)
## ============================================================================
options(width = 200)
suppressPackageStartupMessages({library(haven); library(dplyr)})
root <- Sys.getenv("CHARLS_DATA", "D:/CHARLS")  # parent dir of CHARLS wave folders (2011/, 2013/, ...); out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
say <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n")

rd <- function(...) haven::read_dta(file.path(root, ...))
harm_id <- function(id) { id <- as.character(id)
  ifelse(nchar(id) == 12 & substr(id, 10, 10) == "0",
         paste0(substr(id, 1, 9), substr(id, 11, 12)), id) }
cnt_words <- function(d, vars) {
  m <- sapply(vars, function(v) { x <- d[[v]]; if (is.null(x)) rep(NA_real_, nrow(d)) else as.numeric(x) })
  rowSums(!is.na(m) & m >= 1 & m <= 10) }
cnt_words18 <- function(d, vars) {
  m <- sapply(vars, function(v) { x <- d[[v]]; if (is.null(x)) rep(NA_real_, nrow(d)) else as.numeric(x) })
  ok <- rowSums(!is.na(m)) > 0; s <- rowSums(m == 1, na.rm = TRUE); s[!ok] <- NA; s }
yes1 <- function(x) { x <- as.numeric(x); ifelse(is.na(x), NA, as.integer(x == 1)) }

## ---------- 1) 2011 基线 ----------
demo11 <- rd("2011/demographic_background.dta")
h11 <- rd("2011/health_status_and_functioning.dta")
bio11 <- rd("2011/biomarkers.dta")
lab11b <- sapply(bio11, function(x) { l <- attr(x, "label"); if (is.null(l)) "" else l })
say("biomarkers 身高/体重候选:")
for (i in grep("height|weight|waist", lab11b, ignore.case = TRUE))
  cat(sprintf("   %-12s | %s\n", names(bio11)[i], lab11b[i]))

base <- data.frame(
  ID11 = harm_id(demo11$ID), sex = as.numeric(demo11$rgender),
  byr = as.numeric(demo11$ba002_1), bmo = as.numeric(demo11$ba002_2),
  edu = as.numeric(demo11$bd001), mar = as.numeric(demo11$be001))
base$age11 <- 2011.5 - (base$byr + ifelse(is.na(base$bmo), 6, base$bmo) / 12)
m <- match(base$ID11, harm_id(h11$ID))
dismap <- c(htn = "da007_1_", dyslip = "da007_2_", dm = "da007_3_",
            heart = "da007_7_", stroke = "da007_8_", memdx = "da007_12_")
for (nm in names(dismap)) base[[paste0(nm, "11")]] <- yes1(h11[[dismap[[nm]]]])[m]
## CES-D10 (dc009-dc018; dc013/dc016 反向)
ces <- sapply(sprintf("dc%03d", 9:18), function(v) as.numeric(h11[[v]])[m]) - 1  # 1-4 -> 0-3
colnames(ces) <- sprintf("dc%03d", 9:18)
ces[, "dc013"] <- 3 - ces[, "dc013"]; ces[, "dc016"] <- 3 - ces[, "dc016"]
base$cesd11 <- rowSums(ces); base$cesd11[rowSums(!is.na(ces)) < 10] <- NA
smk_ever <- yes1(h11$da059)[m]; smk_now <- yes1(h11$da061)[m]
base$smoke3 <- ifelse(smk_ever == 0, 0,
               ifelse(smk_ever == 1 & smk_now == 1, 2,
               ifelse(smk_ever == 1 & smk_now == 0, 1, NA_real_)))
## smoke3: 0=从不 1=已戒 2=现在吸
base$drink <- as.numeric(h11$da067)[m]   # 1=每月>1次 2=每月<=1次 3=不喝
## BMI
mh <- match(base$ID11, harm_id(bio11$ID))
v_h <- "qi002"; v_w <- "ql002"
say("身高变量=", v_h, " 体重变量=", v_w)
ht <- as.numeric(bio11[[v_h]])[mh] / 100; wt <- as.numeric(bio11[[v_w]])[mh]
base$bmi <- wt / ht^2; base$bmi[base$bmi < 12 | base$bmi > 60] <- NA

## ---------- 2) 认知长表 (含即时/延迟分维度) ----------
h13 <- rd("2013/Health_Status_and_Functioning.dta")
h15 <- rd("2015/Health_Status_and_Functioning.dta")
g18 <- rd("2018/Cognition.dta")
c11 <- data.frame(ID11 = harm_id(h11$ID), wr_i = cnt_words(h11, paste0("dc006s", 1:11)),
                  wr_d = cnt_words(h11, paste0("dc027s", 1:11)))
c13 <- data.frame(ID11 = harm_id(h13$ID), wr_i = cnt_words(h13, paste0("dc006_1_s", 1:11)),
                  wr_d = cnt_words(h13, paste0("dc027s", 1:11)))
c15 <- data.frame(ID11 = harm_id(h15$ID), wr_i = cnt_words(h15, paste0("dc006s", 1:12)),
                  wr_d = cnt_words(h15, paste0("dc027s", 1:12)))
c18 <- data.frame(ID11 = harm_id(g18$ID), wr_i = cnt_words18(g18, paste0("dc028_w4_s", 1:10)),
                  wr_d = cnt_words18(g18, paste0("dc047_w4_s", 1:10)))
read_x <- function(yr) { d <- rd(paste0(yr, "/Cognition_Depression.dta"))
  data.frame(ID11 = harm_id(d$ID), wr_i = as.numeric(d$xscorewr),
             wr_d = as.numeric(d$xscoredr), wrmean = as.numeric(d$xscorewrmean),
             mmse = as.numeric(d$xscoremmse)) }
c21 <- read_x(2021); c22 <- read_x(2022); c23 <- read_x(2023)
for (cc in c("c11", "c13", "c15", "c18"))
  { d <- get(cc); d$wrmean <- (d$wr_i + d$wr_d)/2; d$mmse <- NA_real_; assign(cc, d) }
wave_yr <- c("2011" = 2011.5, "2013" = 2013.5, "2015" = 2015.5, "2018" = 2018.5,
             "2021" = 2021.6, "2022" = 2022.5, "2023" = 2023.5)
cog_long <- bind_rows(c11 %>% mutate(wave = "2011"), c13 %>% mutate(wave = "2013"),
                      c15 %>% mutate(wave = "2015"), c18 %>% mutate(wave = "2018"),
                      c21 %>% mutate(wave = "2021"), c22 %>% mutate(wave = "2022"),
                      c23 %>% mutate(wave = "2023")) %>%
  mutate(tyr = wave_yr[wave]) %>% filter(!is.na(wrmean)) %>% distinct(ID11, wave, .keep_all = TRUE)

## ---------- 3) 卒中: 状态 + 首诊年细化 ----------
comb <- function(a, b) { a <- yes1(a); b <- yes1(b)
  ifelse(a == 1 | b == 1, 1, ifelse(!is.na(a) | !is.na(b), 0, NA_real_)) }
s13 <- data.frame(ID11 = harm_id(h13$ID), stroke = comb(h13$da007_8_, h13$da007_w2_2_8_))
s15 <- data.frame(ID11 = harm_id(h15$ID), stroke = comb(h15$da007_8_, h15$da007_w2_2_8_))
h18 <- rd("2018/Health_Status_and_Functioning.dta")
s18 <- data.frame(ID11 = harm_id(h18$ID), stroke = yes1(h18$da007_8_))
h20 <- rd("2020/Health_Status_and_Functioning.dta")
s20 <- data.frame(ID11 = harm_id(h20$ID), stroke = yes1(h20$da003_8_))
read_s6 <- function(yr) { d <- rd(paste0(yr, "/Health_Status_and_Functioning.dta"))
  data.frame(ID11 = harm_id(d$ID), stroke_new = yes1(d$da011_8_),
             dxyr = as.numeric(d$da016_1_8_)) }
s21 <- read_s6(2021); s22 <- read_s6(2022); s23 <- read_s6(2023)
## 首诊年候选: 2013 da009_1_8_ ; 2015 da009_1_8_/da010_1_8_? ; 2018 da009_1_8_
say("首诊年变量核查:")
for (tag in c("13", "15", "18")) {
  d <- get(paste0("h", tag))
  for (v in c("da009_1_8_", "da010_1_8_")) if (v %in% names(d)) {
    x <- as.numeric(d[[v]])
    cat(sprintf("   20%s %s: 有效n=%d 范围[%s]\n", tag, v, sum(!is.na(x) & x > 1900),
        paste(range(x[x > 1900], na.rm = TRUE), collapse = "-"))) } }
yr13 <- if ("da009_1_8_" %in% names(h13)) as.numeric(h13$da009_1_8_) else rep(NA_real_, nrow(h13))
yr15 <- if ("da009_1_8_" %in% names(h15)) as.numeric(h15$da009_1_8_) else rep(NA_real_, nrow(h15))
yr18 <- if ("da009_1_8_" %in% names(h18)) as.numeric(h18$da009_1_8_) else rep(NA_real_, nrow(h18))
s13$dxyr <- yr13; s15$dxyr <- yr15; s18$dxyr <- yr18; s20$dxyr <- NA_real_

## ---------- 4) 队列 + 事件波 + 事件时间 ----------
coh <- base %>% filter(!is.na(age11), age11 >= 45) %>%
  filter(!is.na(stroke11), stroke11 == 0) %>% filter(is.na(memdx11) | memdx11 == 0)
say("基线队列: n=", nrow(coh))
coh <- coh %>%
  left_join(s13 %>% select(ID11, st13 = stroke, yr13 = dxyr), by = "ID11") %>%
  left_join(s15 %>% select(ID11, st15 = stroke, yr15 = dxyr), by = "ID11") %>%
  left_join(s18 %>% select(ID11, st18 = stroke, yr18 = dxyr), by = "ID11") %>%
  left_join(s20 %>% select(ID11, st20 = stroke), by = "ID11") %>% mutate(yr20 = NA_real_) %>%
  left_join(s21 %>% select(ID11, st21 = stroke_new, yr21 = dxyr), by = "ID11") %>%
  left_join(s22 %>% select(ID11, st22 = stroke_new, yr22 = dxyr), by = "ID11") %>%
  left_join(s23 %>% select(ID11, st23 = stroke_new, yr23 = dxyr), by = "ID11")

wseq <- c("13", "15", "18", "20", "21", "22", "23")
res <- rep(NA_character_, nrow(coh)); cum <- rep(0, nrow(coh))
for (w in wseq) { v <- coh[[paste0("st", w)]]; v[is.na(v)] <- 0
  new <- cum == 0 & v == 1; res[new] <- w; cum <- cum + v }
res[cum == 0] <- "never"; coh$ev_wave <- res
midmap <- c("13" = 2012.5, "15" = 2014.5, "18" = 2017.0, "20" = 2019.5,
            "21" = 2021.0, "22" = 2022.0, "23" = 2023.0)
prevmap <- c("13" = 2011.5, "15" = 2013.5, "18" = 2015.5, "20" = 2018.5,
             "21" = 2020.5, "22" = 2021.6, "23" = 2022.5)
currmap <- c("13" = 2013.5, "15" = 2015.5, "18" = 2018.5, "20" = 2020.5,
             "21" = 2021.6, "22" = 2022.5, "23" = 2023.5)
coh$ev_t_mid <- unname(midmap[coh$ev_wave])
## 细化: 首诊年在 (上一波, 当前波] 内则采用 (修复 2026-11-19: 原实现逻辑向量长度不齐导致回收错位)
dxyr <- rep(NA_real_, nrow(coh))
for (w in wseq) {
  ix <- which(coh$ev_wave == w)
  yv <- coh[[paste0("yr", w)]][ix]
  ok <- !is.na(yv) & yv > prevmap[w] - 1 & yv <= currmap[w] + 0.6
  dxyr[ix[ok]] <- yv[ok]
}
coh$ev_yr <- dxyr
coh$ev_t <- ifelse(!is.na(coh$ev_yr), coh$ev_yr + 0.5, coh$ev_t_mid)
say("事件时间: 有首诊年细化=", sum(!is.na(coh$ev_yr)), "/", sum(coh$ev_wave != "never"))
print(table(coh$ev_wave))

## ---------- 5) 死亡 ----------
dw <- list()
for (y in c("2015", "2018", "2020", "2023")) { s <- rd(paste0(y, "/Sample_Infor.dta"))
  dw[[y]] <- data.frame(ID11 = harm_id(as.character(s$ID)), wave = as.integer(y),
                        died = as.integer(s$died)) }
sw <- bind_rows(dw) %>% filter(!is.na(died))
dth <- sw %>% filter(died == 1) %>% group_by(ID11) %>% slice_min(wave, n = 1) %>% ungroup()
dmid <- c("2015" = 2014.0, "2018" = 2016.75, "2020" = 2019.25, "2023" = 2021.75)
coh$death_t <- unname(dmid[as.character(dth$wave[match(coh$ID11, dth$ID11)])])
say("死亡: n=", sum(!is.na(coh$death_t)))

## ---------- 6) 每波 z 分 ----------
cogsel <- cog_long %>% filter(ID11 %in% coh$ID11) %>%
  left_join(coh %>% select(ID11, age11, sex, edu), by = "ID11") %>%
  mutate(age_w = age11 + (tyr - 2011.5),
         edu3 = cut(edu, breaks = c(-Inf, 1, 3, Inf), labels = c("low", "mid", "high")))
zcog <- cogsel %>% group_by(wave) %>% group_modify(~{
  d <- .x
  for (out in c("wrmean", "wr_i", "wr_d", "mmse")) {
    zv <- paste0("z_", out); d[[zv]] <- NA_real_
    ok <- !is.na(d[[out]]) & !is.na(d$age_w) & !is.na(d$sex) & !is.na(d$edu3)
    if (sum(ok) > 500) {
      fit <- lm(as.formula(paste0(out, " ~ splines::ns(age_w, 3) + edu3 + factor(sex)")),
                data = d[ok, ])
      d[[zv]][ok] <- as.numeric(scale(resid(fit))) } }
  d }) %>% ungroup()
say("z 有效n (z_wrmean):"); print(zcog %>% group_by(wave) %>% summarise(n = sum(!is.na(z_wrmean))))

## ---------- 7) 导出 ----------
write.csv(coh, file.path(out, "psci_baseline.csv"), row.names = FALSE)
write.csv(zcog, file.path(out, "psci_cog_long.csv"), row.names = FALSE)
say("已导出 psci_baseline.csv (n=", nrow(coh), ") 与 psci_cog_long.csv (n=", nrow(zcog), ")")
say("协变量缺失: edu=", sum(is.na(coh$edu)), " cesd=", sum(is.na(coh$cesd11)),
    " bmi=", sum(is.na(coh$bmi)), " smoke=", sum(is.na(coh$smoke_now)), " drink=", sum(is.na(coh$drink)))
