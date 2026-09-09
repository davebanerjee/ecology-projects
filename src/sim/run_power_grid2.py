"""Second power grid: how many events does the gate need?  Scale the pooled
projection (RAM x3 + FishGlob + GPDD structure) by factors and evaluate the two
gate criteria (power at delta = 0.10; P(negligible) at delta = 0) for the
locked hold-out (dev 0.5) and grouped 5-fold cross-fitting designs."""
import os, sys, json, time
from multiprocessing import Pool
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.sim.power_sim import DatasetSpec, SimParams, run_cell, calibrate
from src.sim.run_power_grid import load_specs, SCENARIOS

OUT = "results/stage0"

if __name__ == "__main__":
    specs = load_specs()
    base_keys = SCENARIOS["D_RAMfull_x3+FishGlob+GPDD"]
    cells = []
    for factor in (1.0, 1.5, 2.0, 3.0, 4.0):
        sp = [DatasetSpec(s.name, s.n_systems, s.n_events, s.pos_neg_event, s.neg_nonevent, s.scale * factor) for s in (specs[k] for k in base_keys)]
        label = f"D_scaled_x{factor}"
        for d in (0.0, 0.05, 0.10, 0.15):
            cells.append((sp, dict(S_B=0.45, delta_true=d, dev_frac=0.5, design="holdout", weighting="system", n_boot=400, n_reps=400), label))
            cells.append((sp, dict(S_B=0.45, delta_true=d, dev_frac=0.6, design="cv5", weighting="system", n_boot=400, n_reps=400), label))
    calib_keys = {}
    for sp, pd_, name in cells:
        calib_keys.setdefault((name, pd_["S_B"], pd_["delta_true"]), (sp, pd_))
    def _cal(item):
        key, (sp, pd_) = item
        return key, calibrate(sp, SimParams(**pd_), np.random.default_rng(777))
    t0 = time.time()
    with Pool(3) as pool:
        calibs = dict(pool.map(_cal, list(calib_keys.items())))
    cells = [(sp, pd_, name, calibs[(name, pd_["S_B"], pd_["delta_true"])]) for sp, pd_, name in cells]
    rows = []
    with Pool(3) as pool:
        for i, r in enumerate(pool.imap_unordered(run_cell, cells)):
            rows.append(r)
            pd.DataFrame(rows).to_csv(os.path.join(OUT, "power_grid_scaling.csv"), index=False)
            print(f"[{i+1}/{len(cells)}] {r['scenario']} d={r['delta_true']} {r['design']} events={r['n_events_total']} -> P(meaningful)={r['p_meaningful']:.2f} P(negl)={r['p_negligible']:.2f} width={r['mean_ci_width']:.3f} ({round(time.time()-t0)}s)", flush=True)
