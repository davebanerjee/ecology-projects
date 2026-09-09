"""Run the Stage 0 power/precision grid from census-derived structure.

Scenarios (systems / events) are built from results/stage0/*_census*.csv.
Projections for sources not reachable from the sandbox (full RAM Legacy,
Living Planet Database) are labelled as such and use census-derived
origin structure with scaled counts.
"""
from __future__ import annotations

import os
import sys
import json
import time
import itertools
from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.sim.power_sim import DatasetSpec, SimParams, spec_from_census, run_cell, calibrate  # noqa: E402

OUT = "results/stage0"


def load_specs():
    ram = pd.read_csv(os.path.join(OUT, "ram_proxy_census.csv"), index_col=0)
    gp = pd.read_csv(os.path.join(OUT, "gpdd_census_annual.csv"), index_col=0)
    gp_summary = json.load(open(os.path.join(OUT, "gpdd_census_summary.json")))
    fg = pd.read_csv(os.path.join(OUT, "fishglob_census.csv"), index_col=0)
    # GPDD primary cohort: reliability>=2, not restricted, not harvest, no method-change keyword (as in census_gpdd)
    notes = gp["Notes"].fillna("").str.lower()
    mc = notes.str.contains("method|protocol|changed|change in|effort|gear|survey area|different")
    harvest = gp["SamplingProtocol"].fillna("").str.lower().str.contains("harvest|catch|bag|kill|fur|pelt|hunt") | gp["SamplingUnits"].fillna("").str.lower().str.contains("harvest|catch|kill|pelt|fur|bag")
    gp_prim = gp[(~gp["restricted"].astype(bool)) & (gp["Reliability"].fillna(0) >= 2) & (~harvest) & (~mc)]
    # FishGlob primary: exclude irregular surveys and zero-inflated; method-change screen as in census_fishglob
    from src.census.census_fishglob import IRREGULAR, METHOD_CHANGES
    def nomc(row):
        ch = METHOD_CHANGES.get(row["survey"], [])
        if not ch or pd.isna(row["first_origin"]):
            return True
        return not any(row["first_origin"] - 30 <= c <= row["last_origin"] + 5 for c in ch)
    fg_prim = fg[(~fg["survey"].isin(IRREGULAR)) & (fg["zero_frac"] <= 0.2) & fg.apply(nomc, axis=1)]
    S = {
        "RAMproxy": spec_from_census("RAMproxy", ram),
        "GPDD": spec_from_census("GPDD", gp_prim),
        "FishGlob": spec_from_census("FishGlob", fg_prim),
    }
    # projections
    S["RAMfull_x3"] = spec_from_census("RAMfull_x3", ram, scale=3.0)
    S["LPD_proj"] = DatasetSpec("LPD_proj", 400, 32, S["GPDD"].pos_neg_event, S["GPDD"].neg_nonevent, 1.0)
    return S


SCENARIOS = {
    "A_accessible_now": ["RAMproxy", "GPDD", "FishGlob"],
    "B_fisheries_proxy_only": ["RAMproxy"],
    "C_RAMfull_x3_only": ["RAMfull_x3"],
    "D_RAMfull_x3+FishGlob+GPDD": ["RAMfull_x3", "GPDD", "FishGlob"],
    "E_D+LPD_projection": ["RAMfull_x3", "GPDD", "FishGlob", "LPD_proj"],
}


def build_grid(specs, quick=False):
    cells = []
    deltas = [0.0, 0.05, 0.10, 0.15, 0.20]
    base = dict(S_B=0.45, n_boot=200 if quick else 400, n_reps=60 if quick else 500)
    for name, keys in SCENARIOS.items():
        sp = [specs[k] for k in keys]
        for d in deltas:
            for dev_frac in (0.5, 0.7):
                cells.append((sp, {**base, "delta_true": d, "dev_frac": dev_frac, "design": "holdout", "weighting": "system"}, name))
            cells.append((sp, {**base, "delta_true": d, "dev_frac": 0.6, "design": "cv5", "weighting": "system"}, name))
        # dataset-weighted estimand for the pooled scenarios, primary delta values only
        if len(keys) > 1:
            for d in (0.0, 0.10, 0.20):
                cells.append((sp, {**base, "delta_true": d, "dev_frac": 0.6, "design": "holdout", "weighting": "dataset"}, name))
    # sensitivity to baseline sensitivity level and EWS-block weight (scenario D only)
    sp = [specs[k] for k in SCENARIOS["D_RAMfull_x3+FishGlob+GPDD"]]
    for S_B in (0.30, 0.60):
        for d in (0.0, 0.10):
            cells.append((sp, {**base, "S_B": S_B, "delta_true": d, "dev_frac": 0.6, "design": "holdout", "weighting": "system"}, "D_RAMfull_x3+FishGlob+GPDD"))
    for w in (0.1, 0.6):
        for d in (0.0, 0.10):
            cells.append((sp, {**base, "w": w, "delta_true": d, "dev_frac": 0.6, "design": "holdout", "weighting": "system"}, "D_RAMfull_x3+FishGlob+GPDD"))
    return cells


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    timing = "--time" in sys.argv
    specs = load_specs()
    json.dump({k: v.to_dict() for k, v in specs.items()}, open(os.path.join(OUT, "power_scenario_specs.json"), "w"), indent=1)
    print({k: v.to_dict() for k, v in specs.items()})
    if timing:
        sp = [specs[k] for k in SCENARIOS["A_accessible_now"]]
        t = time.time()
        r = run_cell((sp, dict(S_B=0.45, delta_true=0.10, dev_frac=0.6, design="holdout", weighting="system", n_boot=100, n_reps=10), "timing"))
        print("timing cell (10 reps, 100 boot):", round(time.time() - t, 1), "s"); print(r)
        sys.exit(0)
    cells = build_grid(specs, quick=quick)
    print("cells:", len(cells))
    t0 = time.time()
    # calibration is shared by cells with identical (scenario, S_B, delta_true, w)
    calib_keys = {}
    for sp, pd_, name in cells:
        calib_keys.setdefault((name, pd_["S_B"], pd_["delta_true"], pd_.get("w", 0.3)), (sp, pd_))
    def _cal(item):
        key, (sp, pd_) = item
        return key, calibrate(sp, SimParams(**pd_), np.random.default_rng(12345))
    with Pool(3) as pool:
        calibs = dict(pool.map(_cal, list(calib_keys.items())))
    print("calibrations done:", len(calibs), f"({round(time.time()-t0)}s)", flush=True)
    cells = [(sp, pd_, name, calibs[(name, pd_["S_B"], pd_["delta_true"], pd_.get("w", 0.3))]) for sp, pd_, name in cells]
    with Pool(3) as pool:
        rows = []
        for i, r in enumerate(pool.imap_unordered(run_cell, cells)):
            rows.append(r)
            pd.DataFrame(rows).to_csv(os.path.join(OUT, "power_grid_quick.csv" if quick else "power_grid.csv"), index=False)
            print(f"[{i+1}/{len(cells)}] {r['scenario']} d={r['delta_true']} design={r['design']} dev={r['dev_frac']} w={r['weighting']} -> P(meaningful)={r['p_meaningful']:.2f} P(negl)={r['p_negligible']:.2f} width={r['mean_ci_width']:.3f} ({round(time.time()-t0)}s)", flush=True)
