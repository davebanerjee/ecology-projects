"""Preliminary canonical-system crosswalk (Stage 0, metadata only).

1. FishGlob survey x species  <->  RAM Legacy stocks (proxy table), by species
   name and a survey-region -> RAM-region map.  A match means the two records
   may measure the same biological population and must share a partition.
2. GPDD internal duplicates: same TaxonID x LocationID with several MainIDs
   (life stages, generations, alternative protocols) and same taxon at
   locations within 50 km.
Outputs go to data/metadata/.  No abundance values are used.
"""
from __future__ import annotations

import os
import sys
import json
import numpy as np
import pandas as pd
import pyreadr

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

OUT = "data/metadata"
RAM = "/home/user/cfree14/sst_recruitment/data/ramldb/data/ramldb_stock_recruit_data.Rdata"
RGPDD = "/home/user/ropensci/rgpdd/data"

# FishGlob survey -> RAM 'region' values that could hold the same population
SURVEY_TO_RAM_REGION = {
    "NEUS": ["US East Coast"], "SEUS": ["US Southeast and Gulf"], "GMEX": ["US Southeast and Gulf"],
    "EBS": ["US Alaska"], "AI": ["US Alaska"], "GOA": ["US Alaska"],
    "WCANN": ["US West Coast"], "WCTRI": ["US West Coast"],
    "DFO-QCS": ["Canada West Coast"], "DFO-HS": ["Canada West Coast"], "DFO-WCVI": ["Canada West Coast"], "DFO-WCHG": ["Canada West Coast"], "DFO-SOG": ["Canada West Coast"],
    "GSL-N": ["Canada East Coast"], "GSL-S": ["Canada East Coast"], "SCS": ["Canada East Coast"],
    "NS-IBTS": ["European Union", "Europe non EU"], "BITS": ["European Union"], "EVHOE": ["European Union"], "FR-CGFS": ["European Union"],
    "IE-IGFS": ["European Union"], "NIGFS": ["European Union"], "SWC-IBTS": ["European Union", "Europe non EU"], "ROCKALL": ["European Union", "Europe non EU"],
    "PT-IBTS": ["European Union"], "SP-ARSA": ["European Union"], "SP-NORTH": ["European Union"], "SP-PORC": ["European Union"],
    "Nor-BTS": ["Europe non EU", "European Union"], "NOR-BTS": ["Europe non EU", "European Union"],
}


def fishglob_ram():
    fg = pd.read_csv("results/stage0/fishglob_census.csv")
    fg = fg[fg["n_origins"] > 0]
    r = pyreadr.read_r(RAM)
    stocks = r["stocks"]
    rows = []
    for _, s in fg.iterrows():
        regions = SURVEY_TO_RAM_REGION.get(s["survey"], [])
        cand = stocks[(stocks["species"].str.lower() == str(s["species"]).lower()) & (stocks["region"].isin(regions))]
        for _, st in cand.iterrows():
            rows.append({"fishglob_system_id": s.name if isinstance(s.name, str) else s["system_id"], "survey_unit": s["survey_unit"], "species": s["species"],
                         "ram_stockid": st["stockid"], "ram_stocklong": st["stocklong"], "ram_region": st["region"], "ram_area": st["area"],
                         "match_rule": "species+region", "confidence": "candidate (needs boundary check)"})
    xw = pd.DataFrame(rows)
    xw.to_csv(os.path.join(OUT, "crosswalk_fishglob_ram_candidates.csv"), index=False)
    # species-level overlap regardless of region (upper bound)
    sp_overlap = set(fg["species"].str.lower()) & set(stocks["species"].str.lower())
    summ = {"fishglob_series_with_origins": int(len(fg)), "fishglob_species": int(fg["species"].nunique()),
            "ram_proxy_stocks": int(len(stocks)), "species_shared_any_region": int(len(sp_overlap)),
            "fishglob_series_with_candidate_ram_match": int(xw["fishglob_system_id"].nunique()) if len(xw) else 0,
            "ram_stocks_with_candidate_fishglob_match": int(xw["ram_stockid"].nunique()) if len(xw) else 0,
            "candidate_pairs": int(len(xw))}
    return summ


def gpdd_internal():
    t = {}
    for f in os.listdir(RGPDD):
        for k, v in pyreadr.read_r(os.path.join(RGPDD, f)).items():
            t[k] = v
    m = t["gpdd_main"].copy()
    m["MainID"] = m["MainID"].astype(int)
    loc = t["gpdd_location"][["LocationID", "LongDD", "LatDD", "ExactName"]]
    m = m.merge(loc, on="LocationID", how="left")
    cens = pd.read_csv("results/stage0/gpdd_census_annual.csv")
    elig = set(cens.loc[cens["n_origins"] > 0, "MainID"].astype(int))
    m["eligible"] = m["MainID"].isin(elig)
    # exact duplicates: same TaxonID x LocationID
    g = m.groupby(["TaxonID", "LocationID"])["MainID"].agg(list)
    dup_groups = g[g.apply(len) > 1]
    # near duplicates: same TaxonID within 50 km
    near = []
    for tax, grp in m[m["eligible"]].groupby("TaxonID"):
        if len(grp) < 2:
            continue
        pts = grp[["MainID", "LongDD", "LatDD", "LocationID"]].dropna()
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                a, b = pts.iloc[i], pts.iloc[j]
                if a["LocationID"] == b["LocationID"]:
                    continue
                dlat = np.radians(a["LatDD"] - b["LatDD"]); dlon = np.radians(a["LongDD"] - b["LongDD"])
                lat1, lat2 = np.radians(a["LatDD"]), np.radians(b["LatDD"])
                h = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
                km = 2 * 6371 * np.arcsin(np.sqrt(h))
                if km <= 50:
                    near.append({"TaxonID": tax, "MainID_a": int(a["MainID"]), "MainID_b": int(b["MainID"]), "km": round(float(km), 1)})
    near = pd.DataFrame(near)
    near.to_csv(os.path.join(OUT, "crosswalk_gpdd_near_duplicates_eligible.csv"), index=False)
    dup_rows = [{"TaxonID": k[0], "LocationID": k[1], "MainIDs": v, "n": len(v), "n_eligible": int(sum(x in elig for x in v))} for k, v in dup_groups.items()]
    pd.DataFrame(dup_rows).to_csv(os.path.join(OUT, "crosswalk_gpdd_taxon_location_groups.csv"), index=False)
    ds = m[m["eligible"]].groupby("DataSourceID")["MainID"].count()
    return {"gpdd_taxon_location_groups_with_multiple_mainids": int(len(dup_groups)),
            "eligible_series": int(len(elig)),
            "eligible_series_in_multi_mainid_groups": int(sum(r["n_eligible"] > 1 for r in dup_rows)),
            "eligible_near_duplicate_pairs_50km": int(len(near)),
            "eligible_series_per_datasource": ds.to_dict()}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    summ = {"fishglob_vs_ram_proxy": fishglob_ram(), "gpdd_internal": gpdd_internal()}
    with open(os.path.join(OUT, "crosswalk_prelim_summary.json"), "w") as f:
        json.dump(summ, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(json.dumps(summ, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
