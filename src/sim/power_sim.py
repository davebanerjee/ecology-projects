"""Simulation-based power and precision gate (PROTOCOL Section 3.3).

Simulates the ENTIRE split-and-evaluation procedure of Sections 7, 9 and 10 on
synthetic alarm scores whose clustering structure (systems, origins per
system, events, dataset imbalance) is drawn from the Stage 0 census tables.

Design of the generative model (latent-score, not time-series):
  * system i belongs to dataset d, has n_i consecutive annual forecast
    origins, and is an event system with probability pi_d.  Event systems
    have n_pos (1..5) positive origins at the end of their origin sequence
    (the 5 years before onset) preceded by negatives; the pair (n_pos, n_neg)
    is resampled from the census.
  * baseline score  s_B[t] = mu_B * g(k_t) + u_i + e_t   with u_i ~ N(0, s_u^2)
    a system random effect, e_t an AR(1) process (rho) with var 1 - s_u^2,
    and g(k) a proximity ramp: 1 within the 5-year window, exp(-(k-5)/tau)
    for k years before the window (risk rises as collapse approaches, so
    pre-window alarms in event systems are possible and count as FALSE).
  * EWS-augmented score s_E[t] = s_B[t] + w * (delta * 1[t in window] + z_t)
    with z_t ~ N(0,1) i.i.d.  Under the null delta = 0 (the block adds only
    noise, weight w).  mu_B and delta are calibrated by bisection so that the
    population event sensitivity at the false-alarm budget equals S_B and
    S_B + Delta respectively.
Evaluation (Section 9.1): consecutive alarmed years form one episode; a new
episode may start only >= `refractory` + 1 years after the previous start;
an episode is TRUE iff it starts at a positive origin (collapse 1-5 y later).
Thresholds are chosen on the development set to give <= `fa_budget`
false-alarm episodes per 20 non-event population-years, then frozen.  The
primary estimand is the paired difference in event sensitivity, with a
percentile bootstrap over systems within dataset.  Decision rules follow
Section 10 with the smallest useful effect `sesoi`.
Nothing here uses real data values or EWS features.
"""
from __future__ import annotations

import itertools
import json
import os
from dataclasses import dataclass, field, asdict
from multiprocessing import Pool

import numpy as np
import pandas as pd

HORIZON = 5


@dataclass
class DatasetSpec:
    name: str
    n_systems: int
    n_events: int
    pos_neg_event: np.ndarray      # (k,2) array of (n_pos, n_neg) pairs from event systems in the census
    neg_nonevent: np.ndarray       # 1-d array of n_neg for non-event systems
    scale: float = 1.0             # multiplier applied to n_systems and n_events (projections)

    def to_dict(self):
        return {"name": self.name, "n_systems": self.n_systems, "n_events": self.n_events, "scale": self.scale}


@dataclass
class SimParams:
    S_B: float = 0.45              # baseline event sensitivity at the FA budget
    delta_true: float = 0.10       # true increment in event sensitivity for the EWS model
    fa_budget: float = 1.0         # false-alarm episodes per 20 non-event population-years
    sesoi: float = 0.10            # smallest useful effect
    dev_frac: float = 0.6
    design: str = "holdout"        # 'holdout' or 'cv5'
    weighting: str = "system"      # 'system' or 'dataset'
    s_u2: float = 0.3              # system random-effect variance share
    rho: float = 0.5               # AR(1) of within-system noise
    tau: float = 3.0               # ramp decay (years) before the window
    w: float = 0.3                 # weight of the EWS block
    refractory: int = HORIZON
    n_boot: int = 300
    n_reps: int = 300
    seed: int = 20260908


# --------------------------------------------------------------------------- #
# population generation
# --------------------------------------------------------------------------- #
def gen_population(specs, rng):
    """Return padded arrays: labels Y (n,L) in {-1 pad, 0, 1}, k_before (n,L), dataset ids, event flags."""
    ds_id, ev, seqs = [], [], []
    for j, sp in enumerate(specs):
        n_sys = int(round(sp.n_systems * sp.scale))
        n_ev = int(round(sp.n_events * sp.scale))
        for i in range(n_sys):
            if i < n_ev:
                npos, nneg = sp.pos_neg_event[rng.integers(len(sp.pos_neg_event))]
                seq = [0] * int(nneg) + [1] * int(npos)
                ev.append(1)
            else:
                nneg = sp.neg_nonevent[rng.integers(len(sp.neg_nonevent))]
                seq = [0] * int(nneg)
                ev.append(0)
            seqs.append(seq)
            ds_id.append(j)
    n = len(seqs)
    L = max(len(s) for s in seqs)
    Y = -np.ones((n, L), dtype=int)
    K = np.zeros((n, L), dtype=float)   # years before onset (for ramp); 0 for non-events
    for i, s in enumerate(seqs):
        Y[i, : len(s)] = s
        if ev[i]:
            npos = sum(s)
            # last origin is 1 year before onset; k counts years before onset
            ks = np.arange(len(s), 0, -1)  # len(s) .. 1
            K[i, : len(s)] = ks
    return Y, K, np.array(ds_id), np.array(ev)


def gen_scores(Y, K, ev, p: SimParams, mu_B, delta, rng):
    n, L = Y.shape
    valid = Y >= 0
    u = rng.normal(0, np.sqrt(p.s_u2), size=(n, 1))
    e = np.zeros((n, L))
    eps = rng.normal(0, 1, size=(n, L))
    se = np.sqrt(1 - p.s_u2)
    e[:, 0] = eps[:, 0]
    for t in range(1, L):
        e[:, t] = p.rho * e[:, t - 1] + np.sqrt(1 - p.rho ** 2) * eps[:, t]
    e *= se
    ramp = np.zeros((n, L))
    evm = ev[:, None].astype(bool)
    inwin = (Y == 1)
    ramp[inwin] = 1.0
    pre = evm & (Y == 0) & valid
    ramp[pre] = np.exp(-(K[pre] - HORIZON) / p.tau)
    sB = mu_B * ramp + u + e
    z = rng.normal(0, 1, size=(n, L))
    sE = sB + p.w * (delta * inwin + z)
    sB[~valid] = np.nan
    sE[~valid] = np.nan
    return sB, sE


# --------------------------------------------------------------------------- #
# alarm episodes and metrics
# --------------------------------------------------------------------------- #
def episode_starts(S, Y, theta, refractory=HORIZON):
    """Boolean (n,L) array of episode starts for threshold theta."""
    n, L = S.shape
    A = np.where(np.isnan(S), False, S >= theta)
    starts = np.zeros((n, L), dtype=bool)
    last = np.full(n, -10 ** 6)
    for t in range(L):
        can = A[:, t] & ((t - last) > refractory)
        starts[:, t] = can
        last = np.where(can, t, last)
    return starts


def metrics_from_starts(starts, Y, ev):
    true_ep = starts & (Y == 1)
    false_ep = starts & (Y == 0)
    detected = true_ep.any(axis=1)                # per system
    n_false = false_ep.sum(axis=1)                # per system
    neg_years = (Y == 0).sum(axis=1)              # per system
    return detected, n_false, neg_years


def fa_burden(n_false, neg_years):
    ny = neg_years.sum()
    return np.inf if ny == 0 else n_false.sum() / (ny / 20.0)


def choose_threshold(S, Y, ev, budget, refractory=HORIZON, n_grid=300):
    """Lowest threshold (max sensitivity) whose FA burden on this set is <= budget."""
    vals = S[~np.isnan(S)]
    qs = np.quantile(vals, np.linspace(0.5, 0.999, n_grid))
    best = None
    for theta in qs:  # increasing thresholds -> decreasing FA (approximately)
        st = episode_starts(S, Y, theta, refractory)
        det, nf, ny = metrics_from_starts(st, Y, ev)
        if fa_burden(nf, ny) <= budget:
            best = theta
            break
    if best is None:
        best = np.nanmax(S) + 1.0  # never alarm
    return best


def sensitivity(detected, ev, ds, weighting):
    if weighting == "system":
        m = ev == 1
        return detected[m].mean() if m.any() else np.nan
    vals = []
    for d in np.unique(ds):
        m = (ds == d) & (ev == 1)
        if m.sum() > 0:
            vals.append(detected[m].mean())
    return float(np.mean(vals)) if vals else np.nan


def paired_bootstrap(detB, detE, nfB, nfE, ny, ev, ds, weighting, n_boot, rng):
    diffs = np.empty(n_boot)
    faB = np.empty(n_boot)
    faE = np.empty(n_boot)
    idx_by_ds = {d: np.where(ds == d)[0] for d in np.unique(ds)}
    for b in range(n_boot):
        idx = np.concatenate([rng.choice(ix, size=len(ix), replace=True) for ix in idx_by_ds.values()])
        diffs[b] = sensitivity(detE[idx], ev[idx], ds[idx], weighting) - sensitivity(detB[idx], ev[idx], ds[idx], weighting)
        faB[b] = fa_burden(nfB[idx], ny[idx])
        faE[b] = fa_burden(nfE[idx], ny[idx])
    return diffs, faB, faE


def classify(d_hat, lo, hi, sesoi):
    if hi < 0:
        return "harm"
    if hi < sesoi:
        return "negligible"
    if d_hat >= sesoi and lo > 0:
        return "meaningful"
    return "inconclusive"


# --------------------------------------------------------------------------- #
# calibration of mu_B and delta
# --------------------------------------------------------------------------- #
def _pop_sens(specs, p, mu_B, delta, rng, n_cal_scale):
    big = [DatasetSpec(s.name, s.n_systems, s.n_events, s.pos_neg_event, s.neg_nonevent, s.scale * n_cal_scale) for s in specs]
    Y, K, ds, ev = gen_population(big, rng)
    sB, sE = gen_scores(Y, K, ev, p, mu_B, delta, rng)
    thB = choose_threshold(sB, Y, ev, p.fa_budget, p.refractory)
    thE = choose_threshold(sE, Y, ev, p.fa_budget, p.refractory)
    dB, _, _ = metrics_from_starts(episode_starts(sB, Y, thB, p.refractory), Y, ev)
    dE, _, _ = metrics_from_starts(episode_starts(sE, Y, thE, p.refractory), Y, ev)
    return dB[ev == 1].mean(), dE[ev == 1].mean()


def calibrate(specs, p: SimParams, rng, n_cal_scale=None):
    """Bisection for mu_B (target S_B) then delta (target S_B + delta_true)."""
    n_total = sum(int(round(s.n_systems * s.scale)) for s in specs)
    if n_cal_scale is None:
        n_cal_scale = max(1.0, 6000.0 / n_total)
    lo, hi = 0.0, 6.0
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        sB, _ = _pop_sens(specs, p, mid, 0.0, rng, n_cal_scale)
        if sB < p.S_B:
            lo = mid
        else:
            hi = mid
    mu_B = 0.5 * (lo + hi)
    target = p.S_B + p.delta_true
    lo, hi = 0.0, 12.0
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        _, sE = _pop_sens(specs, p, mu_B, mid, rng, n_cal_scale)
        if sE < target:
            lo = mid
        else:
            hi = mid
    delta = 0.5 * (lo + hi)
    return mu_B, delta


# --------------------------------------------------------------------------- #
# one replicate of the full procedure
# --------------------------------------------------------------------------- #
def split_holdout(ds, ev, dev_frac, rng):
    dev = np.zeros(len(ds), dtype=bool)
    for d in np.unique(ds):
        for e in (0, 1):
            ix = np.where((ds == d) & (ev == e))[0]
            rng.shuffle(ix)
            k = int(round(dev_frac * len(ix)))
            dev[ix[:k]] = True
    return dev


def run_replicate(specs, p: SimParams, mu_B, delta, rng):
    Y, K, ds, ev = gen_population(specs, rng)
    sB, sE = gen_scores(Y, K, ev, p, mu_B, delta, rng)
    n = len(ev)
    if p.design == "holdout":
        dev = split_holdout(ds, ev, p.dev_frac, rng)
        thB = choose_threshold(sB[dev], Y[dev], ev[dev], p.fa_budget, p.refractory)
        thE = choose_threshold(sE[dev], Y[dev], ev[dev], p.fa_budget, p.refractory)
        te = ~dev
        detB, nfB, ny = metrics_from_starts(episode_starts(sB[te], Y[te], thB, p.refractory), Y[te], ev[te])
        detE, nfE, _ = metrics_from_starts(episode_starts(sE[te], Y[te], thE, p.refractory), Y[te], ev[te])
        ev_e, ds_e = ev[te], ds[te]
    else:  # grouped 5-fold CV over all systems, thresholds from the other folds
        folds = np.zeros(n, dtype=int)
        for d in np.unique(ds):
            for e in (0, 1):
                ix = np.where((ds == d) & (ev == e))[0]
                rng.shuffle(ix)
                folds[ix] = np.arange(len(ix)) % 5
        detB = np.zeros(n, dtype=bool); detE = np.zeros(n, dtype=bool)
        nfB = np.zeros(n, dtype=int); nfE = np.zeros(n, dtype=int); ny = np.zeros(n, dtype=int)
        for f in range(5):
            tr, te = folds != f, folds == f
            thB = choose_threshold(sB[tr], Y[tr], ev[tr], p.fa_budget, p.refractory)
            thE = choose_threshold(sE[tr], Y[tr], ev[tr], p.fa_budget, p.refractory)
            detB[te], nfB[te], ny[te] = metrics_from_starts(episode_starts(sB[te], Y[te], thB, p.refractory), Y[te], ev[te])
            detE[te], nfE[te], _ = metrics_from_starts(episode_starts(sE[te], Y[te], thE, p.refractory), Y[te], ev[te])
        ev_e, ds_e = ev, ds
    sensB = sensitivity(detB, ev_e, ds_e, p.weighting)
    sensE = sensitivity(detE, ev_e, ds_e, p.weighting)
    d_hat = sensE - sensB
    diffs, faB, faE = paired_bootstrap(detB, detE, nfB, nfE, ny, ev_e, ds_e, p.weighting, p.n_boot, rng)
    lo, hi = np.nanpercentile(diffs, [2.5, 97.5])
    return {"d_hat": d_hat, "ci_lo": lo, "ci_hi": hi, "ci_width": hi - lo, "sensB": sensB, "sensE": sensE,
            "faB": fa_burden(nfB, ny), "faE": fa_burden(nfE, ny), "n_events_eval": int((ev_e == 1).sum()),
            "n_systems_eval": int(len(ev_e)), "n_negyears_eval": int(ny.sum()),
            "verdict": classify(d_hat, lo, hi, p.sesoi)}


def run_cell(args):
    specs, p_dict, label = args
    p = SimParams(**p_dict)
    rng = np.random.default_rng(p.seed)
    mu_B, delta = calibrate(specs, p, rng)
    rows = []
    for r in range(p.n_reps):
        rows.append(run_replicate(specs, p, mu_B, delta, rng))
    df = pd.DataFrame(rows)
    vc = df["verdict"].value_counts(normalize=True)
    out = {"scenario": label, **{k: v for k, v in p_dict.items()}, "mu_B": mu_B, "delta_cal": delta,
           "p_meaningful": vc.get("meaningful", 0.0), "p_negligible": vc.get("negligible", 0.0),
           "p_inconclusive": vc.get("inconclusive", 0.0), "p_harm": vc.get("harm", 0.0),
           "mean_d_hat": df["d_hat"].mean(), "sd_d_hat": df["d_hat"].std(), "mean_ci_width": df["ci_width"].mean(),
           "cover95": float(((df["ci_lo"] <= p.delta_true) & (df["ci_hi"] >= p.delta_true)).mean()),
           "mean_sensB": df["sensB"].mean(), "mean_sensE": df["sensE"].mean(),
           "mean_faB_eval": df["faB"].replace(np.inf, np.nan).mean(), "mean_faE_eval": df["faE"].replace(np.inf, np.nan).mean(),
           "p_faE_gt_1.5": float((df["faE"] > 1.5).mean()),
           "n_events_eval": df["n_events_eval"].mean(), "n_systems_eval": df["n_systems_eval"].mean(),
           "n_negyears_eval": df["n_negyears_eval"].mean(),
           "n_systems_total": sum(int(round(s.n_systems * s.scale)) for s in specs),
           "n_events_total": sum(int(round(s.n_events * s.scale)) for s in specs)}
    return out


# --------------------------------------------------------------------------- #
# census-derived specs
# --------------------------------------------------------------------------- #
def spec_from_census(name, cens: pd.DataFrame, scale=1.0):
    c = cens[cens["n_origins"] > 0]
    evm = c["event_in_eligible_window"].astype(bool)
    pn = c.loc[evm, ["n_pos", "n_neg"]].to_numpy()
    if len(pn) == 0:
        pn = np.array([[5, 5]])
    nn = c.loc[~evm, "n_neg"].to_numpy()
    if len(nn) == 0:
        nn = np.array([10])
    return DatasetSpec(name, int(len(c)), int(evm.sum()), pn, nn, scale)


def synthetic_spec(name, n_systems, n_events, origins_mean=10, pos_mean=4.5):
    rng = np.random.default_rng(1)
    npos = np.clip(rng.poisson(pos_mean, 200), 1, 5)
    nneg = np.clip(rng.poisson(origins_mean, 200), 0, 40)
    return DatasetSpec(name, n_systems, n_events, np.stack([npos, nneg], axis=1), np.clip(rng.poisson(origins_mean, 400), 1, 40), 1.0)
