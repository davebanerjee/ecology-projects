"""Third power grid: sensitivity of the gate to the dependence assumptions
(system random-effect share s_u2, within-system AR(1) rho) and to the
false-alarm budget, for the pooled projection D at delta in {0, 0.10}."""
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
    cells = []
    for s_u2, rho in ((0.1, 0.5), (0.5, 0.5), (0.3, 0.2), (0.3, 0.8)):
        for d in (0.0, 0.10):
            cells.append((sp, dict(S_B=0.45, delta_true=d, dev_frac=0.6, design="cv5", weighting="system", s_u2=s_u2, rho=rho, n_boot=400, n_reps=400), f"D_su2={s_u2}_rho={rho}"))
    for budget in (0.5, 2.0):
        for d in (0.0, 0.10):
            cells.append((sp, dict(S_B=0.45, delta_true=d, dev_frac=0.6, design="cv5", weighting="system", fa_budget=budget, n_boot=400, n_reps=400), f"D_budget={budget}"))
    # cluster shocks + cluster bootstrap; episode rule 'run'; conservative EWS-block weight
    for d in (0.0, 0.10):
        cells.append((sp, dict(S_B=0.45, delta_true=d, dev_frac=0.6, design="cv5", weighting="system", s_c2=0.15, boot_unit="cluster", n_boot=400, n_reps=400), "D_cluster_sc2=0.15_clusterboot"))
        cells.append((sp, dict(S_B=0.45, delta_true=d, dev_frac=0.6, design="cv5", weighting="system", s_c2=0.15, n_boot=400, n_reps=400), "D_cluster_sc2=0.15_systemboot"))
        cells.append((sp, dict(S_B=0.45, delta_true=d, dev_frac=0.6, design="cv5", weighting="system", episode_rule="run", n_boot=400, n_reps=400), "D_episode_rule=run"))
        cells.append((sp, dict(S_B=0.45, delta_true=d, dev_frac=0.6, design="cv5", weighting="system", w=0.6, s_c2=0.15, boot_unit="cluster", n_boot=400, n_reps=400), "D_conservative_w0.6_cluster"))
    def _cal(item):
        i, (sp_, pd_, name) = item
        return i, calibrate(sp_, SimParams(**pd_), np.random.default_rng(999))
    t0 = time.time()
    with Pool(3) as pool:
        calibs = dict(pool.map(_cal, list(enumerate(cells))))
    cells = [(sp_, pd_, name, calibs[i]) for i, (sp_, pd_, name) in enumerate(cells)]
    rows = []
    with Pool(3) as pool:
        for i, r in enumerate(pool.imap_unordered(run_cell, cells)):
            rows.append(r)
            pd.DataFrame(rows).to_csv(os.path.join(OUT, "power_grid_dependence.csv"), index=False)
            print(f"[{i+1}/{len(cells)}] {r['scenario']} d={r['delta_true']} -> P(meaningful)={r['p_meaningful']:.2f} P(negl)={r['p_negligible']:.2f} width={r['mean_ci_width']:.3f} faE={r['mean_faE_eval']:.2f} ({round(time.time()-t0)}s)", flush=True)
