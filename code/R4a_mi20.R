## R4a v3: mice m=20 —— 除 sex/married 外全部 pmm (含序数 smoke3/drink/edu)
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(mice)})
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
con <- file(file.path(out, "output/R4_mi_log.txt"), open = "wt"); sink(con, split = TRUE)
say <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n")
set.seed(20261115)

coh <- read.csv(file.path(out, "psci_baseline.csv")); coh$ID11 <- as.character(coh$ID11)
z1  <- read.csv(file.path(out, "psci_cog_long.csv"));  z1$ID11 <- as.character(z1$ID11)
base_wr <- z1 %>% filter(wave == 2011) %>% select(ID11, wr_base = wrmean)
bd <- coh %>% left_join(base_wr, by = "ID11") %>%
  mutate(ev = as.integer(ev_wave != "never"), dead = as.integer(!is.na(death_t)),
         married = as.integer(mar %in% c(1, 2)))
imp_dat <- bd %>% select(ID11, age11, sex, edu, married, cesd11, smoke3, drink, bmi,
                         htn11, dm11, dyslip11, heart11, ev, dead, wr_base) %>%
  mutate(sex = factor(sex), married = factor(married))
meth <- c("age11" = "pmm", "sex" = "logreg", "edu" = "pmm", "married" = "logreg",
          "cesd11" = "pmm", "smoke3" = "pmm", "drink" = "pmm", "bmi" = "pmm",
          "htn11" = "pmm", "dm11" = "pmm", "dyslip11" = "pmm", "heart11" = "pmm",
          "ev" = "", "dead" = "", "wr_base" = "pmm")
say("开始 mice (m=20, maxit=5, 全pmm+logreg)...")
t0 <- Sys.time()
imp <- mice(imp_dat, m = 20, maxit = 5, method = meth, printFlag = FALSE)
say("mice 耗时 ", round(difftime(Sys.time(), t0, units = "mins"), 1), " min")
saveRDS(imp, file.path(out, "output/R4_mids20.rds"))
sink(); close(con)
cat("R4a v3 done\n")
