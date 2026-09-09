"""Summarize the power grid: tables and a power-curve figure (matplotlib PNG)."""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "results/stage0"
PAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]  # validated categorical order


def main():
    df = pd.read_csv(os.path.join(OUT, "power_grid.csv"))
    for c in ("w", "S_B"):
        if c not in df:
            df[c] = np.nan
    df["w"] = df["w"].fillna(0.3)
    base = df[(df["S_B"] == 0.45) & (df["w"] == 0.3) & (df["weighting"] == "system")]
    # gate table: power at delta=0.10 and P(negligible) at delta=0
    rows = []
    for (sc, des, dev), g in base.groupby(["scenario", "design", "dev_frac"]):
        g = g.set_index("delta_true")
        rows.append({"scenario": sc, "design": des, "dev_frac": dev,
                     "n_systems_total": int(g["n_systems_total"].iloc[0]), "n_events_total": int(g["n_events_total"].iloc[0]),
                     "n_events_eval": round(g["n_events_eval"].iloc[0], 1),
                     "power_d0.10": g["p_meaningful"].get(0.10, np.nan), "power_d0.15": g["p_meaningful"].get(0.15, np.nan), "power_d0.20": g["p_meaningful"].get(0.20, np.nan),
                     "P_negl_d0": g["p_negligible"].get(0.0, np.nan), "P_negl_d0.05": g["p_negligible"].get(0.05, np.nan),
                     "false_meaningful_d0": g["p_meaningful"].get(0.0, np.nan),
                     "ci_width_d0.10": g["mean_ci_width"].get(0.10, np.nan), "cover95_d0.10": g["cover95"].get(0.10, np.nan),
                     "faE_eval_d0.10": g["mean_faE_eval"].get(0.10, np.nan),
                     "gate_pass": bool(g["p_meaningful"].get(0.10, 0) >= 0.8 and g["p_negligible"].get(0.0, 0) >= 0.8)})
    gate = pd.DataFrame(rows).sort_values(["scenario", "design", "dev_frac"])
    gate.to_csv(os.path.join(OUT, "power_gate_table.csv"), index=False)
    print(gate.to_string(index=False))
    # weighting comparison
    wt = df[(df["S_B"] == 0.45) & (df["w"] == 0.3) & (df["design"] == "holdout") & (df["dev_frac"].isin([0.6]) | (df["weighting"] == "dataset"))]
    print("\nweighting comparison (holdout):")
    print(df[(df["weighting"] == "dataset") | ((df["design"] == "holdout") & (df["dev_frac"] == 0.5) & (df["weighting"] == "system") & df["delta_true"].isin([0, 0.1, 0.2]))][["scenario", "weighting", "dev_frac", "delta_true", "p_meaningful", "p_negligible", "mean_ci_width", "sd_d_hat"]].sort_values(["scenario", "weighting", "delta_true"]).to_string(index=False))
    print("\nsensitivity to S_B and w (scenario D, holdout dev 0.6):")
    print(df[(df["scenario"].str.startswith("D_")) & (df["design"] == "holdout") & (df["dev_frac"] == 0.6) & (df["weighting"] == "system")][["S_B", "w", "delta_true", "p_meaningful", "p_negligible", "mean_ci_width", "mean_faE_eval"]].sort_values(["S_B", "w", "delta_true"]).to_string(index=False))

    # figure: power vs delta, one panel per design, lines per scenario (dev 0.5 for holdout)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    scen = sorted(base["scenario"].unique())
    for ax, des in zip(axes, ["holdout", "cv5"]):
        sub = base[base["design"] == des]
        if des == "holdout":
            sub = sub[sub["dev_frac"] == 0.5]
        for i, sc in enumerate(scen):
            g = sub[sub["scenario"] == sc].sort_values("delta_true")
            if len(g) == 0:
                continue
            ax.plot(g["delta_true"], g["p_meaningful"], "-o", lw=2, ms=5, color=PAL[i % len(PAL)], label=f"{sc} ({int(g['n_events_total'].iloc[0])} events)")
        ax.axhline(0.8, color="#52514e", lw=1, ls="--")
        ax.axvline(0.10, color="#52514e", lw=1, ls=":")
        ax.set_title("locked hold-out (50 % development)" if des == "holdout" else "grouped 5-fold cross-fitting (all systems)", fontsize=10)
        ax.set_xlabel("true increment in event sensitivity")
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("P(classified 'meaningful benefit')")
    axes[1].legend(fontsize=7, loc="lower right", frameon=False)
    fig.suptitle("Power to declare a meaningful benefit (S_B = 0.45, 1 false alarm / 20 non-event years)", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "power_curves.png"), dpi=150)
    print("figure written")


if __name__ == "__main__":
    main()
