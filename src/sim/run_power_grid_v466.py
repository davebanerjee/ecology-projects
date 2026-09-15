"""Power/precision gate re-run with the RAM Legacy v4.66 census replacing the
v4.41 proxy and its x2/x3 projections.  Both decision rules are recorded (Section
10 rule and the Stage 0 alternative rule).  Writes power_grid_v466.csv and
power_gate_table_v466.csv.

Scenarios
  F_RAMv466_only            RAM v4.66 primary cohort (457 stocks / 111 events)
  G_RAMv466+FishGlob+GPDD   F plus the accessible FishGlob and GPDD cohorts
  Gns_RAMv466ns+FG+GPDD     as G but Pacific salmon stocks removed from RAM
  H_G+LPD_projection        G plus the placeholder LPD projection (400 / 32)
"""
import os, sys, time, json
from multiprocessing import Pool
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.sim.power_sim import DatasetSpec, SimParams, spec_from_census, run_cell, calibrate
from src.sim.run_power_grid import load_specs
from src.sim.summarize_power import gate_table

OUT = "results/stage0"


def load_specs_v466():
    S = load_specs()
    ram = pd.read_csv(os.path.join(OUT, "ram_v466_census.csv"), index_col=0)
    S["RAMv466"] = spec_from_census("RAMv466", ram, cluster_col="region")
    S["RAMv466ns"] = spec_from_census("RAMv466ns", ram[~ram["salmon"].astype(bool)], cluster_col="region")
    return S


SCENARIOS_V466 = {
    "F_RAMv466_only": ["RAMv466"],
    "G_RAMv466+FishGlob+GPDD": ["RAMv466", "GPDD", "FishGlob"],
    "Gns_RAMv466ns+FishGlob+GPDD": ["RAMv466ns", "GPDD", "FishGlob"],
    "H_G+LPD_projection": ["RAMv466", "GPDD", "FishGlob", "LPD_proj"],
}


def gate_both_rules(df):
    g10 = gate_table(df, ["scenario", "design", "dev_frac", "weighting"]); g10["rule"] = "section10"
    alt = df.copy()
    for c in ("p_meaningful", "p_negligible", "p_inconclusive", "p_harm"):
        alt[c] = alt[c + "_alt"]
    galt = gate_table(alt, ["scenario", "design", "dev_frac", "weighting"]); galt["rule"] = "alternative_B"
    return pd.concat([g10, galt], ignore_index=True).sort_values(["scenario", "weighting", "design", "rule"])


if __name__ == "__main__":
    specs = load_specs_v466()
    json.dump({k: v.to_dict() for k, v in specs.items()}, open(os.path.join(OUT, "power_scenario_specs_v466.json"), "w"), indent=1)
    cells = []
    base = dict(S_B=0.45, n_boot=400, n_reps=400)
    for name, keys in SCENARIOS_V466.items():
        sp = [specs[k] for k in keys]
        for d in (0.0, 0.05, 0.10, 0.15):
            for wt in (("system",) if len(keys) == 1 else ("system", "dataset")):
                cells.append((sp, {**base, "delta_true": d, "dev_frac": 0.5, "design": "holdout", "weighting": wt}, name))
                cells.append((sp, {**base, "delta_true": d, "dev_frac": 0.6, "design": "cv5", "weighting": wt}, name))
    calib_keys = {}
    for sp, pd_, name in cells:
        calib_keys.setdefault((name, pd_["delta_true"], pd_["weighting"]), (sp, pd_))

    def _cal(item):
        key, (sp, pd_) = item
        return key, calibrate(sp, SimParams(**pd_), np.random.default_rng(2026))

    t0 = time.time()
    with Pool(3) as pool:
        calibs = dict(pool.map(_cal, list(calib_keys.items())))
    print("calibrations", len(calibs), round(time.time() - t0), "s", flush=True)
    cells = [(sp, pd_, name, calibs[(name, pd_["delta_true"], pd_["weighting"])]) for sp, pd_, name in cells]
    rows = []
    with Pool(3) as pool:
        for i, r in enumerate(pool.imap_unordered(run_cell, cells)):
            rows.append(r)
            pd.DataFrame(rows).to_csv(os.path.join(OUT, "power_grid_v466.csv"), index=False)
            print(f"[{i+1}/{len(cells)}] {r['scenario']} d={r['delta_true']} {r['design']} {r['weighting']} -> rule10 {r['p_meaningful']:.2f}/{r['p_negligible']:.2f} alt {r['p_meaningful_alt']:.2f}/{r['p_negligible_alt']:.2f} ({round(time.time()-t0)}s)", flush=True)
    df = pd.DataFrame(rows)
    gate = gate_both_rules(df)
    gate.to_csv(os.path.join(OUT, "power_gate_table_v466.csv"), index=False)
    pd.set_option("display.width", 250)
    print(gate.to_string(index=False))
    print("DONE")
