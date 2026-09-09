"""Summarize the power grids against the REALIZED increment.

Because the 'true' increment is set by calibration on a finite population, each
cell's realized population increment (delta_realized) differs slightly from the
nominal delta_true.  Power is therefore reported as a function of the realized
increment: for each scenario x design we interpolate P(meaningful) at a realized
increment of exactly 0.10 and P(negligible) at a realized increment of 0.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "results/stage0"
PAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]


def interp(x, y, x0):
    x, y = np.asarray(x, float), np.asarray(y, float)
    o = np.argsort(x)
    x, y = x[o], y[o]
    if x0 < x.min() or x0 > x.max():
        return np.nan
    return float(np.interp(x0, x, y))


def gate_table(df, group_cols):
    rows = []
    for key, g in df.groupby(group_cols):
        key = key if isinstance(key, tuple) else (key,)
        d = dict(zip(group_cols, key))
        d.update({"n_systems_total": int(g["n_systems_total"].iloc[0]), "n_events_total": int(g["n_events_total"].iloc[0]),
                  "n_events_eval": round(g["n_events_eval"].mean(), 1),
                  "realized_at_nominal0": round(g.loc[g["delta_true"] == 0, "delta_realized"].mean(), 3) if (g["delta_true"] == 0).any() else np.nan,
                  "power_at_realized_0.10": interp(g["delta_realized"], g["p_meaningful"], 0.10),
                  "power_at_realized_0.15": interp(g["delta_realized"], g["p_meaningful"], 0.15),
                  "P_negl_at_realized_0": interp(g["delta_realized"], g["p_negligible"], max(0.0, g["delta_realized"].min())),
                  "P_negl_at_realized_0.05": interp(g["delta_realized"], g["p_negligible"], 0.05),
                  "false_meaningful_at_0": interp(g["delta_realized"], g["p_meaningful"], max(0.0, g["delta_realized"].min())),
                  "ci_width_at_0.10": interp(g["delta_realized"], g["mean_ci_width"], 0.10),
                  "cover95_mean": round(g["cover95"].mean(), 3),
                  "faE_eval_mean": round(g["mean_faE_eval"].mean(), 3)})
        d["gate_pass"] = bool((d["power_at_realized_0.10"] >= 0.8) and (d["P_negl_at_realized_0"] >= 0.8)) if not np.isnan(d["power_at_realized_0.10"]) else False
        rows.append(d)
    return pd.DataFrame(rows)


def main():
    df = pd.read_csv(os.path.join(OUT, "power_grid.csv"))
    for c in ("w", "S_B", "s_u2", "rho", "fa_budget"):
        if c not in df:
            df[c] = np.nan
    df["w"] = df["w"].fillna(0.3)
    base = df[(df["S_B"] == 0.45) & (df["w"] == 0.3) & (df["weighting"] == "system")]
    gate = gate_table(base, ["scenario", "design", "dev_frac"]).sort_values(["scenario", "design", "dev_frac"])
    gate.to_csv(os.path.join(OUT, "power_gate_table.csv"), index=False)
    pd.set_option("display.width", 250)
    print("=== GATE TABLE (base params) ==="); print(gate.to_string(index=False))
    print("\n=== weighting comparison ===")
    print(df[df["weighting"] == "dataset"][["scenario", "delta_true", "delta_realized", "p_meaningful", "p_negligible", "mean_ci_width", "sd_d_hat"]].sort_values(["scenario", "delta_true"]).to_string(index=False))
    print("\n=== S_B / w sensitivity (scenario D, holdout 0.6) ===")
    print(df[(df["scenario"].str.startswith("D_")) & (df["design"] == "holdout") & (df["dev_frac"] == 0.6) & (df["weighting"] == "system")][["S_B", "w", "delta_true", "delta_realized", "p_meaningful", "p_negligible", "mean_ci_width", "mean_faE_eval"]].sort_values(["S_B", "w", "delta_true"]).to_string(index=False))
    # scaling grid
    if os.path.exists(os.path.join(OUT, "power_grid_scaling.csv")):
        sc = pd.read_csv(os.path.join(OUT, "power_grid_scaling.csv"))
        gs = gate_table(sc, ["scenario", "design"]).sort_values(["design", "n_events_total"])
        gs.to_csv(os.path.join(OUT, "power_gate_scaling.csv"), index=False)
        print("\n=== SCALING (events needed) ==="); print(gs.to_string(index=False))
    if os.path.exists(os.path.join(OUT, "power_grid_dependence.csv")):
        dp = pd.read_csv(os.path.join(OUT, "power_grid_dependence.csv"))
        print("\n=== dependence / budget sensitivity (scenario D, cv5) ===")
        print(dp[["scenario", "delta_true", "delta_realized", "p_meaningful", "p_negligible", "mean_ci_width", "mean_faE_eval"]].sort_values(["scenario", "delta_true"]).to_string(index=False))
    # figure
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    scen = sorted(base["scenario"].unique())
    for ax, des in zip(axes, ["holdout", "cv5"]):
        sub = base[base["design"] == des]
        if des == "holdout":
            sub = sub[sub["dev_frac"] == 0.5]
        for i, s in enumerate(scen):
            g = sub[sub["scenario"] == s].sort_values("delta_realized")
            if len(g) == 0:
                continue
            ax.plot(g["delta_realized"], g["p_meaningful"], "-o", lw=2, ms=5, color=PAL[i % len(PAL)], label=f"{s} ({int(g['n_events_total'].iloc[0])} events)")
        ax.axhline(0.8, color="#52514e", lw=1, ls="--"); ax.axvline(0.10, color="#52514e", lw=1, ls=":")
        ax.set_title("locked hold-out (50 % development)" if des == "holdout" else "grouped 5-fold cross-fitting (all systems)", fontsize=10)
        ax.set_xlabel("realized increment in event sensitivity"); ax.set_ylim(0, 1); ax.grid(alpha=0.25)
    axes[0].set_ylabel("P(classified 'meaningful benefit')"); axes[1].legend(fontsize=7, loc="lower right", frameon=False)
    fig.suptitle("Power to declare a meaningful benefit (S_B = 0.45; 1 false-alarm episode / 20 non-event years)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "power_curves.png"), dpi=150); print("figure written")


if __name__ == "__main__":
    main()
