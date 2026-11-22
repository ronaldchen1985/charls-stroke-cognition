# -*- coding: utf-8 -*-
"""Regenerate Fig S1 STROBE flow diagram with PSCI-analysis branch."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(9.5, 9.5), dpi=600)
ax.set_xlim(0, 10); ax.set_ylim(0, 13); ax.axis("off")

def box(x, y, w, h, text, fc="#F4F7FB", ec="#34558B", fs=9.5, bold=False):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                       facecolor=fc, edgecolor=ec, linewidth=1.2)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal", linespacing=1.35)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=14, linewidth=1.1, color="#34558B"))

# main chain (center x=2.2, width 4.4)
main = [
    (12.0, "CHARLS 2011 baseline respondents\nN = 17,705"),
    (10.3, "Aged ≥45 years at baseline\nN = 17,156"),
    (8.6,  "Free of self-reported physician-diagnosed\nstroke at baseline\nN = 16,592"),
    (6.9,  "Free of memory-related disease at baseline\n(final cohort)\nN = 16,364"),
    (5.2,  "Trajectory analysis sample\n(≥1 cognitive measure + complete covariates)\nN = 13,974  |  62,962 person-waves\nincident stroke: 1,187"),
]
excl = [
    (11.15, "Excluded: aged <45 years\n(n = 549)"),
    (9.45,  "Excluded: prevalent stroke\n(n = 564)"),
    (7.75,  "Excluded: memory-related disease\n(n = 228)"),
    (6.05,  "Excluded: no cognitive measure\nor incomplete covariates (n = 2,390)"),
]
for (y, t) in main:
    box(1.2, y - 0.62, 4.6, 1.24, t, bold=True)
for (y, t) in excl:
    box(6.6, y - 0.42, 3.2, 0.84, t, fc="#FBF6EF", ec="#B08945", fs=8.5)
for i in range(len(main) - 1):
    arrow(3.5, main[i][0] - 0.66, 3.5, main[i + 1][0] + 0.66)
for (y, _) in excl:
    arrow(5.85, y, 6.55, y)

# PSCI branch (stems from final cohort 16,364: 16,364-734-699-4702-2464 = 7,765)
box(1.2, 2.9, 4.6, 1.5,
    "PSCI analysis sample\n(cognitively intact before anchor, memory z > −1 SD;\n≥1 post-anchor measure)\n"
    "N = 7,765\nPSCI events: 1,669 | competing deaths: 287",
    fc="#EFF7EF", ec="#3E7A3E", bold=True)
box(6.6, 3.05, 3.2, 1.24,
    "Excluded: no memory measure (n = 734);\nno pre-anchor measure (n = 699);\npre-anchor z ≤ −1 SD (n = 4,702);\nno post-anchor measure (n = 2,464)",
    fc="#FBF6EF", ec="#B08945", fs=8.5)
# 左侧绕行箭头: 从 16,364 框左边绕到 PSCI 框左边 (避开 14,276 框)
ax.plot([1.15, 0.55, 0.55, 1.15], [6.9, 6.9, 3.65, 3.65], color="#3E7A3E", linewidth=1.1)
ax.add_patch(FancyArrowPatch((0.56, 3.65), (1.14, 3.65), arrowstyle="-|>",
                             mutation_scale=14, linewidth=1.1, color="#3E7A3E"))
arrow(5.85, 3.68, 6.55, 3.68)

# anchor note
ax.text(3.5, 1.9, "Anchor = stroke onset year (cases) or pseudo-anchor drawn from the\n"
        "case event-time distribution (stroke-free participants), 20-draw validated",
        ha="center", va="top", fontsize=8.5, style="italic", color="#444444")

plt.tight_layout()
plt.savefig(r"D:\CHARLS\PSCI_traj\figures\FigS1_flow_EN.png", dpi=600,
            bbox_inches="tight", facecolor="white")
print("FigS1 saved")
