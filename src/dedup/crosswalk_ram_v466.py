"""FishGlob survey x species  <->  RAM Legacy v4.66 stocks, by scientific name and a
survey-region -> RAM-region map (same rule as crosswalk_prelim.fishglob_ram, but
against the full v4.66 stock list instead of the 328-stock v4.41 proxy).  A match
is a CANDIDATE that needs a stock-boundary check; it is not a confirmed duplicate."""
from __future__ import annotations
import os, sys, json
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.dedup.crosswalk_prelim import SURVEY_TO_RAM_REGION  # noqa: E402

OUT = "data/metadata"
RAM = os.environ.get("RAM_V466", "/tmp/claude-0/-home-user-ecology-projects/e9cdc0c9-87a1-52b8-8355-eba28a360be7/scratchpad/ramldb_v466/timeseries_clean-v4.66.csv")


def main():
    fg = pd.read_csv("results/stage0/fishglob_census.csv")
    fg = fg[fg["n_origins"] > 0]
    cens = pd.read_csv("results/stage0/ram_v466_census.csv", index_col=0)
    raw = pd.read_csv(RAM, low_memory=False, usecols=["stockid", "stocklong", "scientificname", "region", "areaid", "SSB", "TBbest", "TB"])
    stocks = raw[raw[["SSB", "TBbest", "TB"]].notna().any(axis=1)].drop_duplicates("stockid").set_index("stockid")
    stocks["eligible"] = cens["n_origins"].reindex(stocks.index).fillna(0) > 0
    stocks["event"] = cens["event_in_eligible_window"].reindex(stocks.index).fillna(False).astype(bool)
    rows = []
    for _, s in fg.iterrows():
        regions = SURVEY_TO_RAM_REGION.get(s["survey"], [])
        cand = stocks[(stocks["scientificname"].str.lower() == str(s["species"]).lower()) & (stocks["region"].isin(regions))]
        for sid, st in cand.iterrows():
            rows.append({"fishglob_system_id": s.iloc[0] if "system_id" not in fg.columns else s["system_id"], "survey_unit": s["survey_unit"], "species": s["species"],
                         "fishglob_event": bool(s["event_in_eligible_window"]),
                         "ram_stockid": sid, "ram_stocklong": st["stocklong"], "ram_region": st["region"], "ram_area": st["areaid"],
                         "ram_eligible": bool(st["eligible"]), "ram_event": bool(st["event"]),
                         "match_rule": "species+region", "confidence": "candidate (needs boundary check)"})
    xw = pd.DataFrame(rows)
    xw.to_csv(os.path.join(OUT, "crosswalk_fishglob_ram_v466_candidates.csv"), index=False)
    sp_overlap = set(fg["species"].str.lower()) & set(stocks["scientificname"].str.lower())
    summ = {"fishglob_series_with_origins": int(len(fg)), "fishglob_species": int(fg["species"].nunique()),
            "ram_v466_stocks_with_biomass": int(len(stocks)), "ram_v466_eligible_stocks": int(stocks["eligible"].sum()),
            "species_shared_any_region": int(len(sp_overlap)),
            "fishglob_series_with_candidate_ram_match": int(xw["fishglob_system_id"].nunique()) if len(xw) else 0,
            "fishglob_event_series_with_candidate_ram_match": int(xw.loc[xw["fishglob_event"], "fishglob_system_id"].nunique()) if len(xw) else 0,
            "ram_stocks_with_candidate_fishglob_match": int(xw["ram_stockid"].nunique()) if len(xw) else 0,
            "ram_eligible_stocks_with_candidate_fishglob_match": int(xw.loc[xw["ram_eligible"], "ram_stockid"].nunique()) if len(xw) else 0,
            "ram_event_stocks_with_candidate_fishglob_match": int(xw.loc[xw["ram_event"], "ram_stockid"].nunique()) if len(xw) else 0,
            "candidate_pairs": int(len(xw)),
            "pairs_by_survey": xw.groupby("survey_unit").size().to_dict() if len(xw) else {}}
    with open(os.path.join(OUT, "crosswalk_ram_v466_summary.json"), "w") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
