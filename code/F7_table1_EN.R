## F7: Table 1 英文版 (CHARLS bd001 正确分组; 婚姻/慢病改为 n(%))
options(width = 200)
suppressPackageStartupMessages({library(dplyr); library(tableone)})
out <- Sys.getenv("PROJ_ROOT", getwd())  # run from repository root
con <- file(file.path(out, "output/F7_table1_en.txt"), open = "wt"); sink(con)

coh <- read.csv(file.path(out, "psci_baseline.csv"))
## bd001 (2011): 1=文盲 2=未读完小学但识字 3=私塾/家庭学校 4=小学 5=初中 6=高中
##               7=中专 8=大专 9=本科 10=硕士 11=博士
t1d <- coh %>% mutate(
  grp = factor(ifelse(ev_wave == "never", "No incident stroke", "Incident stroke"),
               levels = c("No incident stroke", "Incident stroke")),
  sex_f = factor(sex, 1:2, c("Male", "Female")),
  edu4 = cut(edu, c(-Inf, 1, 3, 5, Inf),
             c("No formal education (illiterate)",
               "Literate without primary diploma (incl. home schooling)",
               "Primary or middle school", "High school or above")),
  married = factor(ifelse(mar %in% c(1, 2), "Married/partnered", "Other")),
  smoke_f = factor(smoke3, 0:2, c("Never", "Former", "Current")),
  drink_f = factor(drink, 1:3, c(">1 time/month", "<=1 time/month", "None")),
  htn = factor(htn11, 0:1, c("No", "Yes")), dm = factor(dm11, 0:1, c("No", "Yes")),
  dyslip = factor(dyslip11, 0:1, c("No", "Yes")), heart = factor(heart11, 0:1, c("No", "Yes")))
vars <- c("age11", "sex_f", "edu4", "married", "cesd11", "smoke_f", "drink_f",
          "htn", "dm", "dyslip", "heart", "bmi")
fvars <- c("sex_f", "edu4", "married", "smoke_f", "drink_f", "htn", "dm", "dyslip", "heart")
t1 <- CreateTableOne(vars = vars, strata = "grp", data = t1d, factorVars = fvars,
                     addOverall = TRUE)
t1m <- print(t1, printToggle = FALSE, showAllLevels = FALSE, contDigits = 1,
             catDigits = 1, pDigits = 3)
print(t1m)
write.csv(t1m, file.path(out, "output/Table1_EN_raw.csv"))
sink(); close(con)
cat("done\n")
