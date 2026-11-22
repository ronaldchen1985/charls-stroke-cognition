## ============================================================================
## PSCI_traj G1: 构建 TICS-10 (定向5+连减5) / 视空间(画图) / 全域认知
## 变量映射:
##  2011/2013/2015: 定向 dc001s1(年) dc001s2(月) dc001s3(日) dc002(星期) dc003(季节)
##                  连减 dc019-dc023 (期望 93/86/79/72/65); 画图 dc025 (1=成功)
##  2018 (Cognition.dta): 定向 dc001_w4(年) dc006_w4(月) dc003_w4(日) dc005_w4(星期) dc002_w4(季节) 1=对5=错97=未测
##                  连减 dc014_w4_[1:5]_1; 画图 dc024_w4 1=对5=错
##  2021: 定向 dc001(年) dc005(月) dc003(日) dc004(星期) dc002(季节) 1=对5=错997=未测
##        连减 dc017_1-dc021_1; 画图 dc032 1=对5=错
##  2022/2023: 定向 dc109(年) dc113(月) dc111(日) dc112(星期) dc110(季节) 1=对2=错其他=NA
##        连减 dc128_1-dc132_1; 画图 dc146 1=对2=错其他=NA
## 输出: psci_cog_long2.csv = psci_cog_long + tics/visuo/z_tics/z_visuo/z_glob/zb_*
## ============================================================================
options(width = 200)
suppressPackageStartupMessages({library(haven); library(dplyr)})
root <- Sys.getenv("CHARLS_DATA", "D:/CHARLS")  # parent dir of CHARLS wave folders (2011/, 2013/, ...); out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
say <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n")
harm_id <- function(id) { id <- as.character(id)
  ifelse(nchar(id) == 12 & substr(id, 10, 10) == "0",
         paste0(substr(id, 1, 9), substr(id, 11, 12)), id) }
num <- function(x) suppressWarnings(as.numeric(x))
S7A <- c(93, 86, 79, 72, 65)

## --- 2011/2013/2015 提取 ---
extr_old <- function(path) {
  d <- read_dta(file.path(root, path))
  n <- nrow(d)
  yr_ok  <- !is.na(num(d$dc001s1)); mo_ok <- !is.na(num(d$dc001s2)); dy_ok <- !is.na(num(d$dc001s3))
  dow <- num(d$dc002); sea <- num(d$dc003)
  orient_m <- cbind(yr_ok, mo_ok, dy_ok, dow == 1, sea == 1)
  orient_allna <- is.na(dow) & is.na(sea) & !yr_ok & !mo_ok & !dy_ok
  orient <- rowSums(orient_m, na.rm = TRUE); orient[orient_allna] <- NA
  s7 <- sapply(paste0("dc0", 19:23), function(v) num(d[[v]]))
  s7ok <- sweep(!is.na(s7), 1, rep(1, n)) & sweep(s7, 2, S7A, `==`)
  s7ok[is.na(s7)] <- FALSE
  serial <- rowSums(s7ok); serial[rowSums(!is.na(s7)) == 0] <- NA
  dr <- num(d$dc025); visuo <- ifelse(dr == 1, 1, ifelse(dr == 2, 0, NA_real_))
  data.frame(ID11 = harm_id(d$ID), orient, serial, visuo)
}
## --- 2018 ---
extr_18 <- function() {
  d <- read_dta(file.path(root, "2018/Cognition.dta"))
  ov <- c("dc001_w4", "dc006_w4", "dc003_w4", "dc005_w4", "dc002_w4")
  om <- sapply(ov, function(v) { x <- num(d[[v]]); ifelse(x == 1, 1, ifelse(x == 5, 0, NA_real_)) })
  orient <- rowSums(om, na.rm = TRUE); orient[rowSums(!is.na(om)) == 0] <- NA
  s7 <- sapply(paste0("dc014_w4_", 1:5, "_1"), function(v) num(d[[v]]))
  s7ok <- !is.na(s7) & sweep(s7, 2, S7A, `==`)
  serial <- rowSums(s7ok); serial[rowSums(!is.na(s7)) == 0] <- NA
  x <- num(d$dc024_w4); visuo <- ifelse(x == 1, 1, ifelse(x == 5, 0, NA_real_))
  data.frame(ID11 = harm_id(d$ID), orient, serial, visuo)
}
## --- 2021 ---
extr_21 <- function(yr) {
  d <- read_dta(file.path(root, paste0(yr, "/Cognition_Depression.dta")))
  ov <- c("dc001", "dc005", "dc003", "dc004", "dc002")
  om <- sapply(ov, function(v) { x <- num(d[[v]]); ifelse(x == 1, 1, ifelse(x == 5, 0, NA_real_)) })
  orient <- rowSums(om, na.rm = TRUE); orient[rowSums(!is.na(om)) == 0] <- NA
  s7 <- sapply(paste0("dc0", 17:21, "_1"), function(v) num(d[[v]]))
  s7ok <- !is.na(s7) & sweep(s7, 2, S7A, `==`)
  serial <- rowSums(s7ok); serial[rowSums(!is.na(s7)) == 0] <- NA
  x <- num(d$dc032); visuo <- ifelse(x == 1, 1, ifelse(x == 5, 0, NA_real_))
  data.frame(ID11 = harm_id(d$ID), orient, serial, visuo)
}
## --- 2022/2023 ---
extr_22 <- function(yr) {
  d <- read_dta(file.path(root, paste0(yr, "/Cognition_Depression.dta")))
  ov <- c("dc109", "dc113", "dc111", "dc112", "dc110")
  om <- sapply(ov, function(v) { x <- num(d[[v]]); ifelse(x == 1, 1, ifelse(x == 2, 0, NA_real_)) })
  orient <- rowSums(om, na.rm = TRUE); orient[rowSums(!is.na(om)) == 0] <- NA
  if (yr == 2022) {
    s7 <- sapply(paste0("dc1", 28:32, "_1"), function(v) num(d[[v]]))
    s7ok <- !is.na(s7) & sweep(s7, 2, S7A, `==`)
    serial <- rowSums(s7ok); serial[rowSums(!is.na(s7)) == 0] <- NA
  } else {
    ## 2023: 第一次连减答案未发布; 用第2-5项(xdc129_1-xdc132_1, 期望86/79/72/65)按5/4折算
    s7 <- sapply(paste0("xdc1", 29:32, "_1"), function(v) num(d[[v]]))
    s7ok <- !is.na(s7) & sweep(s7, 2, S7A[2:5], `==`)
    st1 <- num(d$dc128)  # 1=已作答
    serial <- rowSums(s7ok) * 5 / 4
    serial[st1 != 1 | is.na(st1)] <- NA_real_
  }
  x <- num(d$dc146); visuo <- ifelse(x == 1, 1, ifelse(x == 2, 0, NA_real_))
  data.frame(ID11 = harm_id(d$ID), orient, serial, visuo)
}

d11 <- extr_old("2011/health_status_and_functioning.dta") %>% mutate(wave = "2011")
d13 <- extr_old("2013/Health_Status_and_Functioning.dta") %>% mutate(wave = "2013")
d15 <- extr_old("2015/Health_Status_and_Functioning.dta") %>% mutate(wave = "2015")
d18 <- extr_18() %>% mutate(wave = "2018")
d21 <- extr_21(2021) %>% mutate(wave = "2021")
d22 <- extr_22(2022) %>% mutate(wave = "2022")
d23 <- extr_22(2023) %>% mutate(wave = "2023")
dom <- bind_rows(d11, d13, d15, d18, d21, d22, d23) %>%
  mutate(tics = ifelse(is.na(orient) | is.na(serial), NA_real_, orient + serial))

say("各波 TICS/视空间 有效n:")
print(dom %>% group_by(wave) %>% summarise(n_tics = sum(!is.na(tics)), n_visuo = sum(!is.na(visuo))))

## --- 合并进认知长表 ---
zc <- read.csv(file.path(out, "psci_cog_long.csv"))
zc$ID11 <- as.character(zc$ID11); zc$wave <- as.character(zc$wave)
zc <- zc %>% left_join(dom, by = c("ID11", "wave"))
say("合并后: ", nrow(zc), " 人-波; tics 有效 ", sum(!is.na(zc$tics)))

## --- 波内残差标准化 (与 F1 一致) ---
zc2 <- zc %>% group_by(wave) %>% group_modify(~{
  d <- .x
  for (outc in c("tics", "visuo")) {
    zv <- paste0("z_", outc); d[[zv]] <- NA_real_
    ok <- !is.na(d[[outc]]) & !is.na(d$age_w) & !is.na(d$sex) & !is.na(d$edu3)
    if (sum(ok) > 500) {
      fit <- lm(as.formula(paste0(outc, " ~ splines::ns(age_w, 3) + edu3 + factor(sex)")),
                data = d[ok, ])
      d[[zv]][ok] <- as.numeric(scale(resid(fit))) } }
  d$z_glob <- NA_real_
  ok <- !is.na(d$z_wrmean) & !is.na(d$z_tics) & !is.na(d$z_visuo)
  d$z_glob[ok] <- as.numeric(scale(rowMeans(
    cbind(d$z_wrmean[ok], d$z_tics[ok], d$z_visuo[ok]))))
  d }) %>% ungroup()

## --- 基线(2011)标准化 (S7) ---
b11 <- zc2 %>% filter(wave == "2011")
bm <- list()
for (v in c("wrmean", "tics", "visuo"))
  bm[[v]] <- c(mean(b11[[v]], na.rm = TRUE), sd(b11[[v]], na.rm = TRUE))
zc2$zb_wrmean <- (zc2$wrmean - bm$wrmean[1]) / bm$wrmean[2]
zc2$zb_tics   <- (zc2$tics   - bm$tics[1])   / bm$tics[2]
zc2$zb_visuo  <- (zc2$visuo  - bm$visuo[1])  / bm$visuo[2]
gsum <- zc2$zb_wrmean + zc2$zb_tics + zc2$zb_visuo
g11 <- gsum[zc2$wave == "2011"]
zc2$zb_glob <- (gsum - mean(g11, na.rm = TRUE)) / sd(g11, na.rm = TRUE)

say("z 有效n (z_tics / z_visuo / z_glob):")
print(zc2 %>% group_by(wave) %>% summarise(n_tics = sum(!is.na(z_tics)),
      n_visuo = sum(!is.na(z_visuo)), n_glob = sum(!is.na(z_glob))))
write.csv(zc2, file.path(out, "psci_cog_long2.csv"), row.names = FALSE)
say("已导出 psci_cog_long2.csv")
