"""GPDD feasibility census (rgpdd bundle of GPDD v2010, CC0 package).

Reads the .rda tables, builds annual series, applies Section 5.1 labels and
Section 4.3/5.2 eligibility, and writes census tables.  No EWS features.
"""
from __future__ import annotations

import os
import sys
import json
import numpy as np
import pandas as pd
import pyreadr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.census.run_census import census_long, attrition, sensitivity_grid, LABEL_KW  # noqa: E402

RGPDD = os.environ.get("RGPDD_DIR", "/home/user/ropensci/rgpdd/data")
OUT = os.environ.get("CENSUS_OUT", "results/stage0")


def load():
    t = {}
    for f in os.listdir(RGPDD):
        for k, v in pyreadr.read_r(os.path.join(RGPDD, f)).items():
            t[k] = v
    return t


def main():
    os.makedirs(OUT, exist_ok=True)
    t = load()
    main_ = t["gpdd_main"].copy()
    data = t["gpdd_data"].copy()
    restricted = set(t["gpdd_restricted"]["MainID"].astype(int))
    taxon = t["gpdd_taxon"]
    loc = t["gpdd_location"]

    main_["MainID"] = main_["MainID"].astype(int)
    data["MainID"] = data["MainID"].astype(int)
    main_["SamplingFrequency"] = pd.to_numeric(main_["SamplingFrequency"], errors="coerce")
    main_["Reliability"] = pd.to_numeric(main_["Reliability"], errors="coerce")
    main_["DatasetLength"] = pd.to_numeric(main_["DatasetLength"], errors="coerce")
    main_["restricted"] = main_["MainID"].isin(restricted)

    # ---- metadata distributions -------------------------------------------------
    meta_summary = {
        "n_series_main": int(len(main_)),
        "n_series_with_data": int(data["MainID"].nunique()),
        "n_restricted_listed": int(len(restricted)),
        "n_restricted_with_data": int(data["MainID"].isin(restricted).sum() > 0 and data.loc[data["MainID"].isin(restricted), "MainID"].nunique()),
        "sampling_frequency_counts": main_["SamplingFrequency"].value_counts(dropna=False).to_dict(),
        "sampling_protocol_counts": main_["SamplingProtocol"].value_counts(dropna=False).head(20).to_dict(),
        "sampling_units_counts": main_["SamplingUnits"].value_counts(dropna=False).head(20).to_dict(),
        "sampling_effort_counts": main_["SamplingEffort"].value_counts(dropna=False).head(20).to_dict(),
        "reliability_counts": main_["Reliability"].value_counts(dropna=False).to_dict(),
        "dataset_length_quantiles": main_["DatasetLength"].quantile([0, .1, .25, .5, .75, .9, 1]).to_dict(),
    }
    # taxon class and biotope
    m2 = main_.merge(taxon[["TaxonID", "TaxonomicClass", "TaxonomicPhylum", "TaxonName"]], on="TaxonID", how="left")
    m2 = m2.merge(t["gpdd_biotope"], on="BiotopeID", how="left")
    m2 = m2.merge(loc[["LocationID", "Country", "Continent", "Ocean", "LongDD", "LatDD", "SpatialAccuracy"]], on="LocationID", how="left")
    meta_summary["taxonomic_class_counts"] = m2["TaxonomicClass"].value_counts(dropna=False).head(25).to_dict()
    meta_summary["biotope_type_counts"] = m2["BiotopeType"].value_counts(dropna=False).to_dict()

    # ---- annualize ---------------------------------------------------------------
    # Annual series: SamplingFrequency == 1 -> one observation per SampleYear.
    # Sub-annual: annual mean of PopulationUntransformed within SampleYear (sensitivity only).
    data["value"] = data["PopulationUntransformed"].astype(float)
    data["SampleYear"] = pd.to_numeric(data["SampleYear"], errors="coerce")
    n_bad_year = int((data["SampleYear"] < 0).sum())
    data = data[data["SampleYear"] >= 0].copy()
    data["SampleYear"] = data["SampleYear"].astype(int)
    neg_series = set(data.loc[data["value"] < 0, "MainID"])
    meta_summary["rows_dropped_negative_sampleyear"] = n_bad_year
    meta_summary["series_with_negative_values"] = int(len(neg_series))
    freq = main_.set_index("MainID")["SamplingFrequency"]
    data["freq"] = data["MainID"].map(freq)
    ann = data[data["freq"] == 1].groupby(["MainID", "SampleYear"], as_index=False)["value"].mean()
    dup_check = data[data["freq"] == 1].groupby(["MainID", "SampleYear"]).size()
    meta_summary["annual_series_with_duplicate_years"] = int((dup_check > 1).groupby(level=0).any().sum())
    sub = data[data["freq"] != 1].groupby(["MainID", "SampleYear"], as_index=False)["value"].mean()

    # ---- census ------------------------------------------------------------------
    cens = census_long(ann, "MainID", "SampleYear", "value")
    cens = cens.join(m2.set_index("MainID")[["TaxonName", "TaxonomicClass", "BiotopeType", "Country", "Continent",
                                              "SamplingProtocol", "SamplingUnits", "SamplingEffort", "SpatialDensity",
                                              "Reliability", "DatasetLength", "SamplingFrequency", "restricted", "Notes",
                                              "DataSourceID", "LocationID", "TaxonID", "LongDD", "LatDD"]], how="left")
    cens.to_csv(os.path.join(OUT, "gpdd_census_annual.csv"))

    notes = cens["Notes"].fillna("").str.lower()
    method_change_flag = notes.str.contains("method|protocol|changed|change in|effort|gear|survey area|different")
    harvest_like = cens["SamplingProtocol"].fillna("").str.lower().str.contains("harvest|catch|bag|kill|fur|pelt|hunt") | \
        cens["SamplingUnits"].fillna("").str.lower().str.contains("harvest|catch|kill|pelt|fur|bag")
    cens["has_negative_values"] = cens.index.isin(neg_series)
    steps = [
        ("all annual (SamplingFrequency==1) series with data", pd.Series(True, index=cens.index)),
        ("not in GPDD restricted list", ~cens["restricted"].fillna(False).astype(bool)),
        ("no negative values (abundance scale, not deviations)", ~cens["has_negative_values"]),
        ("reliability >= 2 (GPDD 1-5 scale; 1 = lowest)", cens["Reliability"].fillna(0) >= 2),
        ("n_obs >= 35 (30 history + 5 follow-up)", cens["n_obs"] >= 35),
        ("no method/effort-change keyword in Notes", ~method_change_flag),
        ("not harvest/catch/kill-type series (effort unknown)", ~harvest_like),
        (">=1 eligible forecast origin (complete follow-up, >=30 obs history)", cens["n_origins"] > 0),
    ]
    att = attrition(cens, steps)
    att.to_csv(os.path.join(OUT, "gpdd_attrition.csv"), index=False)

    # sensitivity grid on outcome / eligibility parameters
    grid = [
        {},
        {"min_complete_window": 0},
        {"frac": 0.10},
        {"frac": 0.30},
        {"persistence": 3},
        {"min_history": 20, "min_complete_window": 20},
        {"min_history": 25},
        {"horizon": 3},
        {"min_history": 20, "min_complete_window": 0},
    ]
    keep_ids = cens.index[(~cens["restricted"].astype(bool)) & (cens["Reliability"].fillna(0) >= 2) & (~harvest_like) & (~method_change_flag) & (~cens["has_negative_values"])]
    sg = sensitivity_grid(ann[ann["MainID"].isin(keep_ids)], "MainID", "SampleYear", "value", grid)
    sg.to_csv(os.path.join(OUT, "gpdd_sensitivity_grid.csv"), index=False)

    # sub-annual annualized (sensitivity)
    cens_sub = census_long(sub, "MainID", "SampleYear", "value")
    cens_sub.to_csv(os.path.join(OUT, "gpdd_census_subannual_annualized.csv"))
    meta_summary["subannual_annualized"] = {
        "n_series": int(len(cens_sub)), "n_with_origins": int((cens_sub["n_origins"] > 0).sum()),
        "n_events_in_window": int(cens_sub["event_in_eligible_window"].fillna(False).astype(bool).sum()),
        "n_origins": int(cens_sub["n_origins"].sum())}

    # primary cohort description
    prim = cens[cens.index.isin(keep_ids) & (cens["n_origins"] > 0)]
    meta_summary["primary_cohort"] = {
        "n_series": int(len(prim)),
        "n_events_in_window": int(prim["event_in_eligible_window"].astype(bool).sum()),
        "n_series_any_onset": int(prim["onset_year"].notna().sum()),
        "n_origins": int(prim["n_origins"].sum()),
        "n_pos_origins": int(prim["n_pos"].sum()),
        "n_neg_origins": int(prim["n_neg"].sum()),
        "origins_per_series_quantiles": prim["n_origins"].quantile([0, .25, .5, .75, .9, 1]).to_dict(),
        "n_obs_quantiles": prim["n_obs"].quantile([0, .25, .5, .75, .9, 1]).to_dict(),
        "onset_year_quantiles": prim["onset_year"].dropna().quantile([0, .25, .5, .75, 1]).to_dict() if prim["onset_year"].notna().any() else {},
        "class_counts": prim["TaxonomicClass"].value_counts().head(15).to_dict(),
        "biotope_counts": prim["BiotopeType"].value_counts().to_dict(),
        "protocol_counts": prim["SamplingProtocol"].value_counts().head(10).to_dict(),
        "country_counts": prim["Country"].value_counts().head(10).to_dict(),
        "n_distinct_taxa": int(prim["TaxonID"].nunique()),
        "n_distinct_locations": int(prim["LocationID"].nunique()),
        "n_distinct_sources": int(prim["DataSourceID"].nunique()),
        "n_zero_containing_series": int((prim["n_zero"] > 0).sum()),
    }
    with open(os.path.join(OUT, "gpdd_census_summary.json"), "w") as f:
        json.dump(meta_summary, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(json.dumps(meta_summary, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print(att.to_string())
    print(sg.to_string())


if __name__ == "__main__":
    main()
