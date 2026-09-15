"""Power curves for the v4.66 grids: P(meaningful) against the realized paired
sensitivity increment, one panel per decision rule, system weighting, four data
scenarios (fixed categorical order), grouped cross-fitting solid and 50 % hold-out
dashed.  Writes results/stage0/power_curves_v466.png."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "results/stage0"
PAL = {"F_RAMv466_only": "#2a78d6", "G_RAMv466+FishGlob+GPDD": "#eb6834",
       "Gns_RAMv466ns+FishGlob+GPDD": "#1baf7a", "H_G+LPD_projection": "#eda100"}
LABEL = {"F_RAMv466_only": "RAM v4.66 alone (111 events)", "G_RAMv466+FishGlob+GPDD": "accessible now (138)",
         "Gns_RAMv466ns+FishGlob+GPDD": "accessible, no salmon (119)", "H_G+LPD_projection": "+ LPD placeholder (170)"}
INK, MUTED, GRID, SURF = "#0b0b0b", "#898781", "#e1e0d9", "#fcfcfb"


def main():
    df = pd.read_csv(os.path.join(OUT, "power_grid_v466.csv"))
    df = df[df["weighting"] == "system"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True, facecolor=SURF)
    for ax, col, title in zip(axes, ["p_meaningful", "p_meaningful_alt"], ["Section 10 rule", "rule B (superiority + relevance)"]):
        ax.set_facecolor(SURF)
        for sc, colr in PAL.items():
            for design, ls in (("cv5", "-"), ("holdout", "--")):
                g = df[(df["scenario"] == sc) & (df["design"] == design)].sort_values("delta_realized")
                ax.plot(g["delta_realized"], g[col], ls, color=colr, lw=2, marker="o", ms=4,
                        label=f"{LABEL[sc]}, {'cross-fit' if design == 'cv5' else 'hold-out 50 %'}" if col == "p_meaningful" else None)
        ax.axhline(0.8, color=MUTED, lw=1, ls=":")
        ax.axvline(0.10, color=MUTED, lw=1, ls=":")
        ax.text(0.101, 0.02, "smallest useful effect", color=MUTED, fontsize=8, rotation=90, va="bottom")
        ax.text(-0.02, 0.81, "0.80 power", color=MUTED, fontsize=8, va="bottom")
        ax.set_title(title, color=INK, fontsize=11, loc="left")
        ax.set_xlabel("realized true increment in paired event sensitivity", color=INK)
        ax.set_xlim(-0.03, 0.19); ax.set_ylim(0, 1.02)
        ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color("#c3c2b7")
        ax.tick_params(colors=MUTED, labelcolor=INK)
    axes[0].set_ylabel("P(classified 'meaningful benefit')", color=INK)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.16))
    fig.suptitle("Power gate with the RAM v4.66 cohort (system weighting, block episode rule, 400 replicates per cell)",
                 color=INK, fontsize=11, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "power_curves_v466.png"), dpi=150, bbox_inches="tight", facecolor=SURF)
    print("written")


if __name__ == "__main__":
    main()
