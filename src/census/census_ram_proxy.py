"""RAM Legacy PROXY census.

The canonical RAM Legacy database (Zenodo, CC BY 4.0) is not reachable from this
sandbox.  As a stand-in for Stage 0 sizing we use the RAM v4.41 (2018) extract
redistributed in github.com/cfree14/sst_recruitment (Free et al. 2019 Science):
SSB / total biomass / recruitment / catch for 328 stocks.  Counts from this
extract are LOWER BOUNDS for the current database (v4.66+), which holds far
more stocks and ~8 more years of data.  No EWS features are computed.
"""
from __future__ import annotations

import os
import sys
import json
import numpy as np
import pandas as pd
import pyreadr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.census.run_census import census_long, attrition, sensitivity_grid  # noqa: E402

SRC = os.environ.get("RAM_PROXY", "/home/user/cfree14/sst_recruitment/data/ramldb/data/ramldb_stock_recruit_data.Rdata")
OUT = os.environ.get("CENSUS_OUT", "results/stage0")


def main():
    os.makedirs(OUT, exist_ok=True)
    r = pyreadr.read_r(SRC)
    data, stocks = r["data"], r["stocks"]
    data["year"] = data["year"].astype(int)
    summary = {"n_stocks": int(stocks["stockid"].nunique()), "n_rows": int(len(data)),
               "regions": stocks["region"].value_counts().to_dict(),
               "methods": stocks["method"].value_counts().head(15).to_dict(),
               "nyr_quantiles": stocks["nyr"].quantile([0, .25, .5, .75, .9, 1]).to_dict(),
               "yr2_quantiles": stocks["yr2"].quantile([0, .25, .5, .75, 1]).to_dict()}
    # abundance variable: SSB preferred, else total biomass
    long = data.copy()
    long["value"] = long["ssb"].where(long["ssb"].notna(), long["tb"])
    long["var"] = np.where(long["ssb"].notna(), "ssb", np.where(long["tb"].notna(), "tb", None))
    long = long.dropna(subset=["value"])
    cens = census_long(long, "stockid", "year", "value")
    var_used = long.groupby("stockid")["var"].agg(lambda s: s.value_counts().index[0])
    cens = cens.join(var_used.rename("var_used")).join(stocks.set_index("stockid")[["stocklong", "species", "region", "area", "method", "country", "yr1", "yr2", "nyr", "family"]])
    cens.to_csv(os.path.join(OUT, "ram_proxy_census.csv"))
    steps = [
        ("all stocks with SSB or TB series", pd.Series(True, index=cens.index)),
        ("n_obs >= 35", cens["n_obs"] >= 35),
        (">=1 eligible forecast origin", cens["n_origins"] > 0),
    ]
    att = attrition(cens, steps)
    att.to_csv(os.path.join(OUT, "ram_proxy_attrition.csv"), index=False)
    grid = [{}, {"min_complete_window": 0}, {"frac": 0.10}, {"frac": 0.30}, {"persistence": 3}, {"min_history": 20, "min_complete_window": 20}, {"min_history": 25}, {"horizon": 3}]
    sg = sensitivity_grid(long, "stockid", "year", "value", grid)
    sg.to_csv(os.path.join(OUT, "ram_proxy_sensitivity_grid.csv"), index=False)
    prim = cens[cens["n_origins"] > 0]
    summary["primary"] = {
        "n_stocks": int(len(prim)), "n_events_in_window": int(prim["event_in_eligible_window"].astype(bool).sum()),
        "n_any_onset": int(prim["onset_year"].notna().sum()),
        "n_origins": int(prim["n_origins"].sum()), "n_pos": int(prim["n_pos"].sum()), "n_neg": int(prim["n_neg"].sum()),
        "origins_per_stock_quantiles": prim["n_origins"].quantile([0, .25, .5, .75, .9, 1]).to_dict(),
        "onset_years": sorted(prim["onset_year"].dropna().astype(int).tolist()),
        "regions": prim["region"].value_counts().to_dict(),
        "events_by_region": prim[prim["event_in_eligible_window"].astype(bool)]["region"].value_counts().to_dict(),
        "var_used": prim["var_used"].value_counts().to_dict(),
    }
    with open(os.path.join(OUT, "ram_proxy_census_summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(json.dumps(summary, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print(att.to_string()); print(sg.to_string())


if __name__ == "__main__":
    main()
