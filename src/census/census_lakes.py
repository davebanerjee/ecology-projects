"""Lake/community challenge-set census from duncanobrien/ews-assessments (O'Brien et al. 2023).

Counts lakes, annual and monthly series lengths, and the published transition
classifications.  Kinneret and Kasumigaura raw data are NOT in the public file
(available on request only) and are excluded here.  No EWS features.
"""
import os, json
import pandas as pd
import pyreadr

SRC = "/home/user/duncanobrien/ews-assessments/Data"
OUT = "results/stage0"
NAMES = {"LZ": "Lower Zurich", "UZ": "Upper Zurich", "mad": "Mendota", "mon": "Monona", "wind": "Windermere", "wash": "Washington", "leve": "Loch Leven"}

if __name__ == "__main__":
    r = pyreadr.read_r(os.path.join(SRC, "wrangled_genus_plank_data_public.Rdata"))
    td = pd.read_csv(os.path.join(SRC, "transition_dates.csv"), index_col=0)
    rows = []
    for k, v in r.items():
        code, res = k.split("_")[0], k.split("_")[1]
        dcol = [c for c in v.columns if c.lower() == "date"][0]
        d = pd.to_numeric(v[dcol], errors="coerce")
        rows.append({"lake": NAMES.get(code, code), "resolution": "annual" if res == "yr" else "monthly", "n_obs": int(len(v)),
                     "n_taxa_columns": int(v.shape[1] - 1), "start": float(d.min()), "end": float(d.max())})
    cen = pd.DataFrame(rows).sort_values(["lake", "resolution"])
    trans = td[td["metric"] == "community"][["lake", "state_date", "temporal_date", "date_match", "threshold_date", "is_bimodal"]]
    cen = cen.merge(trans, on="lake", how="left")
    cen.to_csv(os.path.join(OUT, "lake_challenge_census.csv"), index=False)
    summ = {"lakes_public": int(cen["lake"].nunique()), "lakes_total_in_paper": 9, "lakes_restricted": ["Kinneret", "Kasumigaura"],
            "annual_series_lengths": cen[cen.resolution == "annual"].set_index("lake")["n_obs"].to_dict(),
            "monthly_series_lengths": cen[cen.resolution == "monthly"].set_index("lake")["n_obs"].to_dict(),
            "community_transition_dates": td[td.metric == "community"].set_index("lake")["threshold_date"].to_dict()}
    json.dump(summ, open(os.path.join(OUT, "lake_challenge_summary.json"), "w"), indent=1, default=str)
    print(cen.to_string()); print(json.dumps(summ, indent=1, default=str))
