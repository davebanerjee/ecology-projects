"""Core + scaling cells with BOTH decision rules recorded (Section 10 rule and the
Stage 0 alternative rule).  Writes power_grid_v2.csv."""
import os, sys, time
from multiprocessing import Pool
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.sim.power_sim import DatasetSpec, SimParams, run_cell, calibrate
from src.sim.run_power_grid import load_specs, SCENARIOS
OUT = "results/stage0"
if __name__ == "__main__":
    specs = load_specs()
    cells = []
    base = dict(S_B=0.45, n_boot=400, n_reps=400)
    for name in ("A_accessible_now", "C_RAMfull_x3_only", "D_RAMfull_x3+FishGlob+GPDD", "E_D+LPD_projection"):
        sp = [specs[k] for k in SCENARIOS[name]]
        for d in (0.0, 0.05, 0.10, 0.15):
            for wt in (("system",) if name == "C_RAMfull_x3_only" else ("system", "dataset")):
                cells.append((sp, {**base, "delta_true": d, "dev_frac": 0.5, "design": "holdout", "weighting": wt}, name))
                cells.append((sp, {**base, "delta_true": d, "dev_frac": 0.6, "design": "cv5", "weighting": wt}, name))
    for factor in (1.5, 2.0, 3.0, 4.0):
        sp = [DatasetSpec(s.name, s.n_systems, s.n_events, s.pos_neg_event, s.neg_nonevent, s.scale * factor, s.n_clusters) for s in (specs[k] for k in SCENARIOS["D_RAMfull_x3+FishGlob+GPDD"])]
        for d in (0.0, 0.05, 0.10, 0.15):
            cells.append((sp, {**base, "delta_true": d, "dev_frac": 0.5, "design": "holdout", "weighting": "system"}, f"D_scaled_x{factor}"))
            cells.append((sp, {**base, "delta_true": d, "dev_frac": 0.6, "design": "cv5", "weighting": "system"}, f"D_scaled_x{factor}"))
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
            pd.DataFrame(rows).to_csv(os.path.join(OUT, "power_grid_v2.csv"), index=False)
            print(f"[{i+1}/{len(cells)}] {r['scenario']} d={r['delta_true']} {r['design']} {r['weighting']} -> rule10 {r['p_meaningful']:.2f}/{r['p_negligible']:.2f} alt {r['p_meaningful_alt']:.2f}/{r['p_negligible_alt']:.2f} ({round(time.time()-t0)}s)", flush=True)
    print("DONE")
