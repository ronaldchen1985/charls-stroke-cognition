## H2: Figure 2 升级为 4 域观测图 (2x2)
## 注意: Figure 1 由 R6_figures.R 生成 (阶跃参数化), 本脚本不得再覆盖 Fig1。
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(ggplot2); library(gridExtra)})
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
say <- function(...) cat(format(Sys.time(), "[%H:%M:%S]"), ..., "\n")

theme_pub <- theme_classic(base_size = 11, base_family = "sans") +
  theme(legend.position = "top", legend.title = element_blank(),
        axis.title = element_text(size = 10.5, face = "bold"),
        plot.title = element_text(size = 11, face = "bold"),
        axis.line = element_line(linewidth = 0.5))

domains <- c("z_wrmean", "z_tics", "z_visuo", "z_glob")
dnames <- c("Episodic memory", "Orientation/calculation (TICS-10)",
            "Visuospatial ability", "Global cognition")

## ---------- Figure 2 (composite): 4 域观测均值 ----------
coh <- read.csv(file.path(out, "psci_baseline.csv"))
z2 <- read.csv(file.path(out, "psci_cog_long2.csv"))
set.seed(20261115)
cases_t <- coh$ev_t[coh$ev_wave != "never" & !is.na(coh$ev_t)]
coh$pseudo_t <- NA_real_; nc <- coh$ev_wave != "never" & !is.na(coh$ev_t)
coh$pseudo_t[nc] <- coh$ev_t[nc]; coh$pseudo_t[!nc] <- sample(cases_t, sum(!nc), TRUE)
d <- z2 %>% left_join(coh %>% select(ID11, ev_wave, pseudo_t), by = "ID11", suffix = c("", ".y")) %>%
  mutate(stroke = as.integer(ev_wave != "never"), tau = tyr - pseudo_t)
panels2 <- list()
for (k in seq_along(domains)) {
  zc <- domains[k]
  obs <- d %>% filter(!is.na(.data[[zc]]), tau >= -10, tau <= 5) %>%
    mutate(bin = round(tau), grp = factor(stroke, 0:1, c("Stroke-free", "Incident stroke"))) %>%
    group_by(grp, bin) %>%
    summarise(z = mean(.data[[zc]]), se = sd(.data[[zc]]) / sqrt(n()), n = n(), .groups = "drop") %>%
    filter(n >= 30)
  obs$sparse <- obs$n < 100
  ymin <- min(obs$z - 1.96 * obs$se); ymax <- max(obs$z + 1.96 * obs$se)
  rng <- max(ymax - ymin, 0.3)
  ## 注意: aes 是惰性求值, 循环中必须把 y 位置写进数据列
  obs$y_n1 <- ymin - 0.10 * rng
  obs$y_n2 <- ymin - 0.17 * rng
  ylab <- ymin - 0.135 * rng
  panels2[[k]] <- ggplot(obs, aes(bin, z, color = grp, shape = grp)) +
    geom_vline(xintercept = 0, linetype = 3, color = "grey60", linewidth = 0.4) +
    geom_hline(yintercept = 0, linetype = 3, color = "grey85", linewidth = 0.35) +
    geom_errorbar(aes(ymin = z - 1.96 * se, ymax = z + 1.96 * se,
                      alpha = ifelse(sparse, 0.35, 1)), width = 0.25, linewidth = 0.35) +
    geom_point(aes(alpha = ifelse(sparse, 0.35, 1)), size = 1.6) +
    geom_line(aes(alpha = ifelse(sparse, 0.35, 1)), linewidth = 0.6) +
    geom_text(data = obs %>% filter(grp == "Incident stroke"),
              aes(y = y_n1, label = n), size = 2.2, color = "#D55E00", show.legend = FALSE) +
    geom_text(data = obs %>% filter(grp == "Stroke-free"),
              aes(y = y_n2, label = n), size = 2.2, color = "#0072B2", show.legend = FALSE) +
    annotate("text", x = -10.6, y = ylab, label = "n:", size = 2.4, hjust = 0, color = "grey30") +
    scale_alpha_identity() +
    scale_color_manual(values = c("#0072B2", "#D55E00")) +
    coord_cartesian(ylim = c(ymin - 0.24 * rng, NA)) +
    labs(title = paste0(LETTERS[k], ". ", dnames[k]),
         x = "Years from stroke onset / anchor (τ)", y = "Observed z score (mean ± 95% CI)") +
    theme_pub
}
p2 <- gridExtra::arrangeGrob(grobs = panels2, layout_matrix = rbind(c(1, 2), c(3, 4)), top = NULL)
ggsave(file.path(out, "figures/Fig2_observed_EN.png"), p2, width = 9.5, height = 8, dpi = 600)
say("Fig2 四域合成图完成")
