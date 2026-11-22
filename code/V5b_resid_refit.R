suppressPackageStartupMessages(library(lme4))
out <- "D:/CHARLS/PSCI_traj"
mods <- readRDS(file.path(out, "output/R2_models.rds"))
m <- mods$z_wrmean$m
res <- character()
r <- as.numeric(resid(m, type = "pearson"))
ext <- abs(r) > 4
mf <- m@frame
mf$ID11 <- m@flist$ID11
names(mf) <- make.names(names(mf))
f <- as.formula(paste("z_wrmean ~ age_c + factor.sex. + edu3 + married_f + cesd_c +",
  "smoke3_f + drink_f + htn11 + dm11 + dyslip11 + heart11 + bmi_c + bmi_na +",
  "tau + step + stroke:pre_tau + stroke:post_tau + (1 + tau | ID11)"))
m2 <- try(lmer(f, data = mf[!ext, ], REML = FALSE,
               control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))), silent = TRUE)
if (inherits(m2, "try-error")) {
  res <- c(res, paste("重拟合失败:", substr(as.character(m2), 1, 300)))
} else {
  s2 <- summary(m2)$coefficients
  res <- c(res, sprintf("剔除 %d 例极端残差后 step = %.4f (%.4f ~ %.4f)",
    sum(ext), s2["step",1], s2["step",1]-1.96*s2["step",2], s2["step",1]+1.96*s2["step",2]))
}
writeLines(res, file.path(out, "output/V5_resid_refit.txt"))
