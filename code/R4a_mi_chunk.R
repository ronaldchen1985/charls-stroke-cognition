## R4a_chunk v4: 完全复刻 G6 已验证规格 (默认方法+全因子+quickpred), 仅改 maxit=3
## 用法: Rscript R4a_mi_chunk.R <seed>
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(mice)})
args <- commandArgs(trailingOnly = TRUE)
SD <- as.integer(args[1])
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
logf <- file.path(out, sprintf("output/R4_chunk_%d.txt", SD))
if (file.exists(logf)) file.remove(logf)
wlog <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n", file = logf, append = TRUE)

coh <- read.csv(file.path(out, "psci_baseline.csv")); coh$ID11 <- as.character(coh$ID11)
z1  <- read.csv(file.path(out, "psci_cog_long.csv"));  z1$ID11 <- as.character(z1$ID11)
base_wr <- z1 %>% filter(wave == 2011) %>% select(ID11, wr_base = wrmean)
bd <- coh %>% left_join(base_wr, by = "ID11") %>%
  mutate(ev = as.integer(ev_wave != "never"), dead = as.integer(!is.na(death_t)))
imp_dat <- bd %>% select(ID11, age11, sex, edu, mar, cesd11, smoke3, drink, bmi,
                         htn11, dm11, dyslip11, heart11, ev, dead, wr_base) %>%
  mutate(edu = factor(edu), mar = factor(mar), smoke3 = factor(smoke3),
         drink = factor(drink), sex = factor(sex))
pred <- quickpred(imp_dat, exclude = "ID11")
wlog("seed=", SD, " m=5 maxit=3 开始")
t0 <- Sys.time()
set.seed(SD)
imp <- mice(imp_dat, m = 5, maxit = 3, predictorMatrix = pred, printFlag = FALSE)
wlog("耗时 ", round(difftime(Sys.time(), t0, units = "secs"), 0), " 秒")
saveRDS(imp, file.path(out, sprintf("output/R4_mids_seed%d.rds", SD)))
wlog("saved")
