"""Re-run the 'run' episode-rule cells with the constrained-optimum threshold search."""
import os, sys, time
from multiprocessing import Pool
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.sim.power_sim import SimParams, run_cell, calibrate
from src.sim.run_power_grid import load_specs, SCENARIOS
OUT = "results/stage0"
if __name__ == "__main__":
    specs = load_specs()
    sp = [specs[k] for k in SCENARIOS["D_RAMfull_x3+FishGlob+GPDD"]]
    cells = [(sp, dict(S_B=0.45, delta_true=d, dev_frac=0.6, design="cv5", weighting="system", episode_rule="run", n_boot=400, n_reps=300), "D_episode_rule=run_v2") for d in (0.0, 0.10)]
    def _cal(item):
        i, (sp_, pd_, name) = item
        return i, calibrate(sp_, SimParams(**pd_), np.random.default_rng(4242))
    with Pool(2) as pool:
        calibs = dict(pool.map(_cal, list(enumerate(cells))))
    cells = [(sp_, pd_, name, calibs[i]) for i, (sp_, pd_, name) in enumerate(cells)]
    rows = []
    with Pool(2) as pool:
        for r in pool.imap_unordered(run_cell, cells):
            rows.append(r); print(r["scenario"], r["delta_true"], r["delta_realized"], r["p_meaningful"], r["p_negligible"], r["mean_ci_width"], r["mean_faE_eval"], r["mean_sensB"], flush=True)
    old = pd.read_csv(os.path.join(OUT, "power_grid_dependence.csv"))
    old = old[old["scenario"] != "D_episode_rule=run"]
    pd.concat([old, pd.DataFrame(rows)], ignore_index=True).to_csv(os.path.join(OUT, "power_grid_dependence.csv"), index=False)
    print("DONE")
