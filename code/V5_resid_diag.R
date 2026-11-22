suppressPackageStartupMessages(library(lme4))
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
mods <- readRDS(file.path(out, "output/R2_models.rds"))
m <- mods$z_wrmean$m   # 主模型（阶跃参数化, 记忆）
res <- c(sprintf("class: %s", paste(class(m), collapse=",")))
r <- as.numeric(resid(m, type = "pearson"))
n <- length(r)
sk <- mean((r - mean(r))^3) / sd(r)^3
ku <- mean((r - mean(r))^4) / sd(r)^4
ext <- abs(r) > 4
res <- c(res,
  sprintf("n_obs=%d", n),
  sprintf("Pearson 残差偏度=%.3f 峰度=%.3f(正态=3)", sk, ku),
  sprintf("|残差|>4SD: %d (%.3f%%)", sum(ext), 100*mean(ext)),
  sprintf("Shapiro-Wilk(5000) P=%.3g", shapiro.test(sample(r, 5000))$p.value))
mf <- m@frame
mf$ID11 <- m@flist$ID11
mf2 <- mf[!ext, ]
m2 <- try(lmer(formula(m), data = mf2, REML = FALSE,
               control = lmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))), silent = TRUE)
if (inherits(m2, "try-error")) {
  res <- c(res, paste("重拟合失败:", substr(as.character(m2), 1, 200)))
} else {
  s2 <- summary(m2)$coefficients
  res <- c(res, sprintf("剔除极端残差(%d)后 step = %.4f (%.4f ~ %.4f)",
    sum(ext), s2["stroke",1], s2["stroke",1]-1.96*s2["stroke",2], s2["stroke",1]+1.96*s2["stroke",2]))
}
writeLines(res, file.path(out, "output/V5_resid_diag.txt"))
