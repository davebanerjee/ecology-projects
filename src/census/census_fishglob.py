"""FishGlob feasibility census (FishGlob_data v2.1.0, CC BY 4.0).

Builds survey_unit x species annual abundance indices (mean weight CPUA over
unflagged hauls, zeros for hauls where the species was absent), applies the
Section 5.1 collapse rule and Section 4.3/5.2 eligibility, and writes census
tables.  Aggregation choices here are PROPOSED Stage 0 defaults, not frozen.
No EWS features are computed.
"""
from __future__ import annotations

import os
import sys
import glob
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.census.run_census import census_long, attrition, sensitivity_grid  # noqa: E402

PARQ = os.environ.get("FISHGLOB_PARQUET_DIR", "/tmp/claude-0/-home-user-ecology-projects/e9cdc0c9-87a1-52b8-8355-eba28a360be7/scratchpad")
OUT = os.environ.get("CENSUS_OUT", "results/stage0")

# Documented survey-level method changes (from metadata_docs/README.md and NEWS.md);
# years are the first year of the new regime.  Used only for attrition accounting.
METHOD_CHANGES = {
    "FR-CGFS": [2015],          # vessel + larger gear, station design change
    "GSL-S": [1985, 1992],      # vessel/gear changes; fixed-station design 1984-87
    "SCS": [1996],              # electronic scale replaced dial scale (small catches)
    "NOR-BTS": [2004],          # survey replaced (Barents-centred series from 2004)
    "GSL-N": [1990],            # vessel/gear correction guidance; series effectively starts 1990
}
IRREGULAR = {"AI", "WCTRI", "GOA", "HS", "QCS", "WCHG", "WCVI", "SOG"}  # biennial/triennial or irregular

MIN_HAULS = 20          # proposed: years with fewer unflagged hauls become missing
MIN_OCC = 0.05          # proposed: species present in >= 5% of hauls (all years)
FLAG_COL = "flag_trimming_hex7_2"   # proposed primary footprint standardization


def build_index(flag_col=FLAG_COL, min_hauls=MIN_HAULS, min_occ=MIN_OCC, value="wgt_cpua"):
    rows = []
    diag = []
    for f in sorted(glob.glob(os.path.join(PARQ, "fg_*_std_clean.parquet"))):
        cols = ["survey", "survey_unit", "year", "haul_id", "accepted_name", "rank", "wgt_cpua", "num_cpua", "flag_taxa", flag_col]
        df = pd.read_parquet(f, columns=cols)
        df = df[df[flag_col].isna()]                       # drop hauls flagged by footprint trimming
        for su, g in df.groupby("survey_unit"):
            hauls_year = g.groupby("year")["haul_id"].nunique()
            good_years = hauls_year[hauls_year >= min_hauls].index
            n_hauls_total = int(g["haul_id"].nunique())
            sp = g[(g["rank"] == "Species") & (g["flag_taxa"].isna()) & (g[value].notna()) & (g[value] > 0)]
            occ = sp.groupby("accepted_name")["haul_id"].nunique() / n_hauls_total
            keep_sp = occ[occ >= min_occ].index
            sp = sp[sp["accepted_name"].isin(keep_sp) & sp["year"].isin(good_years)]
            tot = sp.groupby(["accepted_name", "year"])[value].sum().reset_index()
            tot["value"] = tot[value] / tot["year"].map(hauls_year)
            # zero years: species in keep_sp with no positive record in a good year -> 0
            full = pd.MultiIndex.from_product([keep_sp, good_years], names=["accepted_name", "year"]).to_frame(index=False)
            tot = full.merge(tot[["accepted_name", "year", "value"]], on=["accepted_name", "year"], how="left").fillna({"value": 0.0})
            tot["survey"] = g["survey"].iloc[0]
            tot["survey_unit"] = su
            tot["system_id"] = "FG|" + su + "|" + tot["accepted_name"]
            rows.append(tot)
            diag.append({"survey": g["survey"].iloc[0], "survey_unit": su, "year_min": int(hauls_year.index.min()), "year_max": int(hauls_year.index.max()),
                         "n_years_total": int(len(hauls_year)), "n_years_good": int(len(good_years)),
                         "n_hauls_total": n_hauls_total, "n_species_candidates": int(len(keep_sp))})
    return pd.concat(rows, ignore_index=True), pd.DataFrame(diag)


def main():
    os.makedirs(OUT, exist_ok=True)
    long, diag = build_index()
    diag.to_csv(os.path.join(OUT, "fishglob_survey_units.csv"), index=False)
    cens = census_long(long, "system_id", "year", "value")
    meta = long.groupby("system_id").agg(survey=("survey", "first"), survey_unit=("survey_unit", "first"), species=("accepted_name", "first"))
    cens = cens.join(meta)
    cens["zero_frac"] = cens["n_zero"] / cens["n_obs"]
    cens.to_csv(os.path.join(OUT, "fishglob_census.csv"))

    def no_method_change(row):
        ch = METHOD_CHANGES.get(row["survey"], [])
        if not ch or row["first_origin"] is None or pd.isna(row["first_origin"]):
            return True
        # a change inside any eligible origin's feature window (30 y) or follow-up invalidates the series
        lo = row["first_origin"] - 30
        hi = row["last_origin"] + 5
        return not any(lo <= c <= hi for c in ch)

    steps = [
        ("all survey_unit x species candidates (>=5% occurrence, unflagged hauls, >=20 hauls/yr)", pd.Series(True, index=cens.index)),
        ("not irregular-interval survey", ~cens["survey"].isin(IRREGULAR)),
        ("n_obs >= 35", cens["n_obs"] >= 35),
        (">=1 eligible forecast origin", cens["n_origins"] > 0),
        ("no documented survey method change within feature window/follow-up", cens.apply(no_method_change, axis=1)),
        ("zero_frac <= 0.2 (not zero-inflated)", cens["zero_frac"] <= 0.2),
    ]
    att = attrition(cens, steps)
    att.to_csv(os.path.join(OUT, "fishglob_attrition.csv"), index=False)
    ok = cens.index[(~cens["survey"].isin(IRREGULAR)) & cens.apply(no_method_change, axis=1) & (cens["zero_frac"] <= 0.2)]
    grid = [{}, {"frac": 0.10}, {"frac": 0.30}, {"persistence": 3}, {"min_history": 20}, {"min_history": 25}, {"horizon": 3}]
    sg = sensitivity_grid(long[long["system_id"].isin(ok)], "system_id", "year", "value", grid)
    sg.to_csv(os.path.join(OUT, "fishglob_sensitivity_grid.csv"), index=False)
    prim = cens.loc[ok]
    prim = prim[prim["n_origins"] > 0]
    summary = {
        "n_survey_units": int(diag["survey_unit"].nunique()), "n_surveys": int(diag["survey"].nunique()),
        "n_candidate_series": int(len(cens)), "primary": {
            "n_series": int(len(prim)), "n_surveys": int(prim["survey"].nunique()), "n_survey_units": int(prim["survey_unit"].nunique()),
            "n_species": int(prim["species"].nunique()),
            "n_events_in_window": int(prim["event_in_eligible_window"].astype(bool).sum()),
            "n_origins": int(prim["n_origins"].sum()), "n_pos": int(prim["n_pos"].sum()), "n_neg": int(prim["n_neg"].sum()),
            "series_by_survey_unit": prim["survey_unit"].value_counts().to_dict(),
            "events_by_survey_unit": prim[prim["event_in_eligible_window"].astype(bool)]["survey_unit"].value_counts().to_dict(),
            "origins_per_series_quantiles": prim["n_origins"].quantile([0, .25, .5, .75, 1]).to_dict(),
            "onset_years": sorted(prim["onset_year"].dropna().astype(int).tolist()),
        }}
    with open(os.path.join(OUT, "fishglob_census_summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(json.dumps(summary, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print(diag.to_string()); print(att.to_string()); print(sg.to_string())


if __name__ == "__main__":
    main()
