"""RAM Legacy v4.66 census (target release, via a derived public mirror).

Source: ``timeseries_values_views`` from RAMLDB v4.66 (Zenodo 14043031, CC BY 4.0)
as redistributed in github.com/RaphBnrd/RAMLDB_causality (MIT; file
``data/timeseries_clean-v4.66.csv``, sha256 c910121955e461599913303bcd945744bc
315fd822bbee9d5ef2027da7a70864).  The table holds one preferred series per stock
from the most recent assessment (the standard 35 RAM columns) full-joined with a
stock-boundary SST table; 156 SST-only stockids carry no RAM series and are
dropped here, and four stocks with empty/non-consecutive years were removed by
the mirror author (HADNS, HERR30, HERRNS, SOLEIIIa).

The mirror is the exact target version by file name, README and preparation
script, but it is a derived extract: counts must be re-run on the official
Zenodo release before preregistration.  No EWS features are computed.

Abundance variable (stock level, not row level): SSB for the whole stock if the
stock has any SSB value, else TBbest, else TB.  A stock-level rule avoids the
hybrid TB/SSB series that row-wise coalescing produces (the SSB rows are lower
and appear as a spurious drop).  A TBbest-preferred variant is reported too.
Exact zeros are kept as observations in the primary run (15 SSB stocks, mostly
salmon escapement) and dropped in a sensitivity run.
"""
from __future__ import annotations

import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.census.run_census import census_long, attrition, sensitivity_grid  # noqa: E402

SRC = os.environ.get("RAM_V466", "/tmp/claude-0/-home-user-ecology-projects/e9cdc0c9-87a1-52b8-8355-eba28a360be7/scratchpad/ramldb_v466/timeseries_clean-v4.66.csv")
OUT = os.environ.get("CENSUS_OUT", "results/stage0")
META_COLS = ["stocklong", "scientificname", "commonname", "areaid", "region", "family", "FisheryType"]


def build_long(df: pd.DataFrame, prefer: tuple[str, ...], zeros_as_missing: bool = False) -> tuple[pd.DataFrame, pd.Series]:
    """One value column per stock-year using a stock-level preference order."""
    has = {c: df.groupby("stockid")[c].apply(lambda s: s.notna().any()) for c in prefer}
    choice = pd.Series(None, index=has[prefer[0]].index, dtype=object)
    for c in prefer:
        choice = choice.where(choice.notna(), np.where(has[c], c, None))
    choice = choice.dropna()
    parts = []
    for c in prefer:
        ids = choice.index[choice == c]
        sub = df[df["stockid"].isin(ids)][["stockid", "year", c]].rename(columns={c: "value"})
        parts.append(sub)
    long = pd.concat(parts, ignore_index=True).dropna(subset=["value"])
    if zeros_as_missing:
        long = long[long["value"] != 0]
    long = long[long["value"] >= 0]
    return long, choice


def main():
    os.makedirs(OUT, exist_ok=True)
    df = pd.read_csv(SRC, low_memory=False)
    df["year"] = df["year"].astype(int)
    ram_cols = ["TBbest", "SSB", "TB"]
    any_ram = df[ram_cols].notna().any(axis=1)
    ram_ids = set(df.loc[any_ram, "stockid"])
    stocks = df.drop_duplicates("stockid").set_index("stockid")[META_COLS]
    stocks["salmon"] = stocks["FisheryType"].eq("Pacific Salmon")
    summary = {
        "source": "RAMLDB v4.66 timeseries_values_views via github.com/RaphBnrd/RAMLDB_causality (derived mirror; CC BY 4.0 upstream)",
        "n_stockid_in_file": int(df["stockid"].nunique()),
        "n_stocks_with_biomass_series": len(ram_ids),
        "n_stocks_with_any_ram_series": int(df.loc[df.iloc[:, 3:38].notna().any(axis=1), "stockid"].nunique()),
        "n_pacific_salmon_with_biomass": int(stocks.loc[list(ram_ids), "salmon"].sum()),
        "year_range": [int(df.loc[any_ram, "year"].min()), int(df.loc[any_ram, "year"].max())],
    }

    # ---- primary: SSB > TBbest > TB, stock level, zeros kept ----
    long, choice = build_long(df, ("SSB", "TBbest", "TB"))
    cens = census_long(long, "stockid", "year", "value")
    cens = cens.join(choice.rename("var_used")).join(stocks)
    n_zero = long[long["value"] == 0].groupby("stockid").size()
    cens["n_zero_values"] = n_zero.reindex(cens.index).fillna(0).astype(int)
    cens.to_csv(os.path.join(OUT, "ram_v466_census.csv"))

    steps = [
        ("all stocks with SSB, TBbest or TB series", pd.Series(True, index=cens.index)),
        ("n_obs >= 30", cens["n_obs"] >= 30),
        (">=1 eligible forecast origin (complete 24-yr window, 5-yr follow-up)", cens["n_origins"] > 0),
        ("... and not Pacific salmon", ~cens["salmon"]),
    ]
    att = attrition(cens, steps)
    att.to_csv(os.path.join(OUT, "ram_v466_attrition.csv"), index=False)

    grid = [{}, {"min_complete_window": 0}, {"frac": 0.10}, {"frac": 0.30}, {"persistence": 3},
            {"min_history": 20, "min_complete_window": 20}, {"min_history": 25}, {"horizon": 3}]
    sg = sensitivity_grid(long, "stockid", "year", "value", grid)
    sg["variant"] = "SSB>TBbest>TB, zeros kept"
    # variants: zeros as missing; TBbest preferred; non-salmon only
    long_z, _ = build_long(df, ("SSB", "TBbest", "TB"), zeros_as_missing=True)
    sg_z = sensitivity_grid(long_z, "stockid", "year", "value", [{}]); sg_z["variant"] = "SSB>TBbest>TB, zeros dropped"
    long_tb, choice_tb = build_long(df, ("TBbest", "TB", "SSB"))
    sg_tb = sensitivity_grid(long_tb, "stockid", "year", "value", [{}]); sg_tb["variant"] = "TBbest>TB>SSB, zeros kept"
    ns_ids = stocks.index[~stocks["salmon"]]
    sg_ns = sensitivity_grid(long[long["stockid"].isin(ns_ids)], "stockid", "year", "value", [{}]); sg_ns["variant"] = "SSB>TBbest>TB, non-salmon only"
    sg_all = pd.concat([sg, sg_z, sg_tb, sg_ns], ignore_index=True)
    sg_all.to_csv(os.path.join(OUT, "ram_v466_sensitivity_grid.csv"), index=False)

    prim = cens[cens["n_origins"] > 0]
    ev = prim["event_in_eligible_window"].fillna(False).astype(bool)
    summary["primary"] = {
        "n_stocks": int(len(prim)), "n_events_in_window": int(ev.sum()),
        "n_any_onset": int(prim["onset_year"].notna().sum()),
        "n_origins": int(prim["n_origins"].sum()), "n_pos": int(prim["n_pos"].sum()), "n_neg": int(prim["n_neg"].sum()),
        "origins_per_stock_quantiles": prim["n_origins"].quantile([0, .25, .5, .75, .9, 1]).to_dict(),
        "onset_years": sorted(prim.loc[ev, "onset_year"].dropna().astype(int).tolist()),
        "regions": prim["region"].value_counts().to_dict(),
        "events_by_region": prim.loc[ev, "region"].value_counts().to_dict(),
        "fishery_types": prim["FisheryType"].value_counts(dropna=False).to_dict(),
        "events_by_fishery_type": prim.loc[ev, "FisheryType"].value_counts(dropna=False).to_dict(),
        "var_used": prim["var_used"].value_counts().to_dict(),
        "events_by_var_used": prim.loc[ev, "var_used"].value_counts().to_dict(),
        "n_salmon": int(prim["salmon"].sum()), "n_salmon_events": int((ev & prim["salmon"]).sum()),
        "stocks_with_zero_values": int((prim["n_zero_values"] > 0).sum()),
        "events_onset_on_zero": int(sum(1 for sid in prim.index[ev] if ((long["stockid"] == sid) & (long["year"] == prim.loc[sid, "onset_year"]) & (long["value"] == 0)).any())),
        "end_year_quantiles": prim["end"].quantile([0, .25, .5, .75, 1]).to_dict(),
        "start_year_quantiles": prim["start"].quantile([0, .25, .5, .75, 1]).to_dict(),
    }
    ns = prim[~prim["salmon"]]
    evn = ns["event_in_eligible_window"].fillna(False).astype(bool)
    summary["primary_non_salmon"] = {
        "n_stocks": int(len(ns)), "n_events_in_window": int(evn.sum()),
        "n_origins": int(ns["n_origins"].sum()), "n_pos": int(ns["n_pos"].sum()), "n_neg": int(ns["n_neg"].sum()),
        "regions": ns["region"].value_counts().to_dict(),
        "events_by_region": ns.loc[evn, "region"].value_counts().to_dict(),
        "onset_years": sorted(ns.loc[evn, "onset_year"].dropna().astype(int).tolist()),
    }
    with open(os.path.join(OUT, "ram_v466_census_summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(json.dumps(summary, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print(att.to_string()); print(sg_all.to_string())


if __name__ == "__main__":
    main()
