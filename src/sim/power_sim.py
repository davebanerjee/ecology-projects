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
    n_clusters: int = 0            # 0 = every system is its own cluster (independent)

    def to_dict(self):
        return {"name": self.name, "n_systems": self.n_systems, "n_events": self.n_events, "scale": self.scale, "n_clusters": self.n_clusters}


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
    s_c2: float = 0.0              # cluster (survey unit / region) random-effect variance share
    rho: float = 0.5               # AR(1) of within-system noise
    episode_rule: str = "block"    # 'block' (new episode allowed once > refractory years after the last start) or 'run' (maximal alarm run = one episode; refractory from run end)
    boot_unit: str = "system"      # 'system' (stratified by dataset x event) or 'cluster'
    min_discordant: int = 5        # replicates with fewer discordant events are inconclusive
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
    ds_id, ev, seqs, cl = [], [], [], []
    cl_offset = 0
    for j, sp in enumerate(specs):
        n_sys = int(round(sp.n_systems * sp.scale))
        n_ev = int(round(sp.n_events * sp.scale))
        n_cl = sp.n_clusters if sp.n_clusters and sp.n_clusters > 0 else n_sys
        order = rng.permutation(n_sys)  # random cluster assignment so events are not all in the first clusters
        for i in range(n_sys):
            cl.append(cl_offset + int(order[i]) % n_cl)
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
        cl_offset += n_cl
    n = len(seqs)
    L = max(len(s) for s in seqs)
    Y = -np.ones((n, L), dtype=int)
    K = np.zeros((n, L), dtype=float)   # years before onset (for ramp); 0 for non-events
    for i, s in enumerate(seqs):
        Y[i, : len(s)] = s
        if ev[i]:
            npos = int(sum(s)); nneg = len(s) - npos
            # positives are the last npos of the 5 years before onset (k = npos..1);
            # negatives are eligible origins with onset outside the horizon, i.e. k >= 6
            ks = np.concatenate([np.arange(HORIZON + nneg, HORIZON, -1), np.arange(npos, 0, -1)])
            K[i, : len(s)] = ks
    return Y, K, np.array(ds_id), np.array(ev), np.array(cl)


def gen_scores(Y, K, ev, p: SimParams, mu_B, delta, rng, cl=None):
    n, L = Y.shape
    valid = Y >= 0
    u = rng.normal(0, np.sqrt(p.s_u2), size=(n, 1))
    if p.s_c2 > 0 and cl is not None:
        ceff = rng.normal(0, np.sqrt(p.s_c2), size=int(cl.max()) + 1)
        u = u + ceff[cl][:, None]
    e = np.zeros((n, L))
    eps = rng.normal(0, 1, size=(n, L))
    se = np.sqrt(1 - p.s_u2 - p.s_c2)
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
def episode_starts(S, Y, theta, refractory=HORIZON, rule="block"):
    """Boolean (n,L) array of episode starts for threshold theta.

    rule='block': a new episode may start whenever an alarm occurs more than
    `refractory` years after the previous episode START (a persistent alarm is
    re-scored every refractory+1 years).
    rule='run': a maximal run of consecutive alarmed years is one episode; a new
    run starting within `refractory` years of the previous episode's last
    alarmed year is merged into it (no new start).
    """
    n, L = S.shape
    A = np.where(np.isnan(S), False, S >= theta)
    starts = np.zeros((n, L), dtype=bool)
    if rule == "block":
        last = np.full(n, -10 ** 6)
        for t in range(L):
            can = A[:, t] & ((t - last) > refractory)
            starts[:, t] = can
            last = np.where(can, t, last)
    elif rule == "run":
        last_end = np.full(n, -10 ** 6)
        prev = np.zeros(n, dtype=bool)
        for t in range(L):
            a = A[:, t]
            can = a & (~prev) & ((t - last_end) > refractory)
            starts[:, t] = can
            last_end = np.where(a, t, last_end)
            prev = a
    else:
        raise ValueError(rule)
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


def choose_threshold(S, Y, ev, budget, refractory=HORIZON, n_grid=400, rule="block"):
    """Lowest threshold (max sensitivity) whose FA burden on this set is <= budget.

    FA burden is (near-)monotone non-increasing in the threshold, so we bisect
    over a quantile grid of observed scores instead of scanning linearly.
    """
    vals = S[~np.isnan(S)]
    qs = np.quantile(vals, np.linspace(0.3, 0.9995, n_grid))

    def fa_at(theta):
        st = episode_starts(S, Y, theta, refractory, rule)
        _, nf, ny = metrics_from_starts(st, Y, ev)
        return fa_burden(nf, ny)

    lo, hi = 0, n_grid - 1
    if fa_at(qs[hi]) > budget:
        return np.nanmax(S) + 1.0  # never alarm
    if fa_at(qs[lo]) <= budget:
        return qs[lo]
    while hi - lo > 1:               # invariant: fa(lo) > budget >= fa(hi)
        mid = (lo + hi) // 2
        if fa_at(qs[mid]) <= budget:
            hi = mid
        else:
            lo = mid
    return qs[hi]


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


def paired_bootstrap(detB, detE, nfB, nfE, ny, ev, ds, weighting, n_boot, rng, cl=None, boot_unit="system"):
    """Percentile bootstrap of the paired sensitivity difference.

    boot_unit='system': systems resampled within dataset x event-status strata
    (every dataset keeps its events); 'cluster': clusters resampled within
    dataset with all their systems.
    """
    diffs = np.empty(n_boot)
    faB = np.empty(n_boot)
    faE = np.empty(n_boot)
    if boot_unit == "cluster" and cl is not None:
        groups = []
        for d in np.unique(ds):
            m = ds == d
            cls = np.unique(cl[m])
            members = [np.where(m & (cl == c))[0] for c in cls]
            groups.append(members)
    else:
        strata = [np.where((ds == d) & (ev == e))[0] for d in np.unique(ds) for e in (0, 1)]
        strata = [ix for ix in strata if len(ix) > 0]
    for b in range(n_boot):
        if boot_unit == "cluster" and cl is not None:
            idx = np.concatenate([np.concatenate([members[i] for i in rng.integers(len(members), size=len(members))]) for members in groups])
        else:
            idx = np.concatenate([rng.choice(ix, size=len(ix), replace=True) for ix in strata])
        diffs[b] = sensitivity(detE[idx], ev[idx], ds[idx], weighting) - sensitivity(detB[idx], ev[idx], ds[idx], weighting)
        faB[b] = fa_burden(nfB[idx], ny[idx])
        faE[b] = fa_burden(nfE[idx], ny[idx])
    return diffs, faB, faE


def classify(d_hat, lo, hi, sesoi, n_disc=None, min_disc=0):
    if n_disc is not None and n_disc < min_disc:
        return "inconclusive"
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
def _pop_sens(specs, p, mu_B, delta, seed, n_cal_scale):
    """Population sensitivities of both models at the FA budget, using COMMON RANDOM
    NUMBERS (fixed seed) so that the bisection targets are monotone in mu_B/delta."""
    rng = np.random.default_rng(seed)
    big = [DatasetSpec(s.name, s.n_systems, s.n_events, s.pos_neg_event, s.neg_nonevent, s.scale * n_cal_scale, s.n_clusters) for s in specs]
    Y, K, ds, ev, cl = gen_population(big, rng)
    sB, sE = gen_scores(Y, K, ev, p, mu_B, delta, rng, cl)
    thB = choose_threshold(sB, Y, ev, p.fa_budget, p.refractory, rule=p.episode_rule)
    thE = choose_threshold(sE, Y, ev, p.fa_budget, p.refractory, rule=p.episode_rule)
    dB, _, _ = metrics_from_starts(episode_starts(sB, Y, thB, p.refractory, p.episode_rule), Y, ev)
    dE, _, _ = metrics_from_starts(episode_starts(sE, Y, thE, p.refractory, p.episode_rule), Y, ev)
    return sensitivity(dB, ev, ds, p.weighting), sensitivity(dE, ev, ds, p.weighting)


def calibrate(specs, p: SimParams, rng, n_cal_events=3000, n_iter=16):
    """Bisection for mu_B (target S_B) then delta (target S_B + delta_true).

    Uses a calibration population with >= n_cal_events events and common random
    numbers, then re-evaluates the calibrated pair on an independent population
    to report the REALIZED population increment (delta_realized), which is what
    the replicates actually estimate.  Returns (mu_B, delta, delta_realized, sB_realized).
    """
    n_ev = sum(int(round(s.n_events * s.scale)) for s in specs)
    n_cal_scale = max(1.0, n_cal_events / max(n_ev, 1))
    seed = int(rng.integers(1 << 31))
    lo, hi = 0.0, 6.0
    for _ in range(n_iter):
        mid = 0.5 * (lo + hi)
        sB, _ = _pop_sens(specs, p, mid, 0.0, seed, n_cal_scale)
        if sB < p.S_B:
            lo = mid
        else:
            hi = mid
    mu_B = 0.5 * (lo + hi)
    target = p.S_B + p.delta_true
    lo, hi = 0.0, 12.0
    for _ in range(n_iter):
        mid = 0.5 * (lo + hi)
        _, sE = _pop_sens(specs, p, mu_B, mid, seed, n_cal_scale)
        if sE < target:
            lo = mid
        else:
            hi = mid
    delta = 0.5 * (lo + hi)
    sB_r, sE_r = _pop_sens(specs, p, mu_B, delta, seed + 1, n_cal_scale)
    return mu_B, delta, float(sE_r - sB_r), float(sB_r)


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
    Y, K, ds, ev, cl = gen_population(specs, rng)
    sB, sE = gen_scores(Y, K, ev, p, mu_B, delta, rng, cl)
    n = len(ev)
    R = p.episode_rule
    if p.design == "holdout":
        dev = split_holdout(ds, ev, p.dev_frac, rng)
        thB = choose_threshold(sB[dev], Y[dev], ev[dev], p.fa_budget, p.refractory, rule=R)
        thE = choose_threshold(sE[dev], Y[dev], ev[dev], p.fa_budget, p.refractory, rule=R)
        te = ~dev
        detB, nfB, ny = metrics_from_starts(episode_starts(sB[te], Y[te], thB, p.refractory, R), Y[te], ev[te])
        detE, nfE, _ = metrics_from_starts(episode_starts(sE[te], Y[te], thE, p.refractory, R), Y[te], ev[te])
        ev_e, ds_e, cl_e = ev[te], ds[te], cl[te]
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
            thB = choose_threshold(sB[tr], Y[tr], ev[tr], p.fa_budget, p.refractory, rule=R)
            thE = choose_threshold(sE[tr], Y[tr], ev[tr], p.fa_budget, p.refractory, rule=R)
            detB[te], nfB[te], ny[te] = metrics_from_starts(episode_starts(sB[te], Y[te], thB, p.refractory, R), Y[te], ev[te])
            detE[te], nfE[te], _ = metrics_from_starts(episode_starts(sE[te], Y[te], thE, p.refractory, R), Y[te], ev[te])
        ev_e, ds_e, cl_e = ev, ds, cl
    sensB = sensitivity(detB, ev_e, ds_e, p.weighting)
    sensE = sensitivity(detE, ev_e, ds_e, p.weighting)
    d_hat = sensE - sensB
    n_disc = int(((detB != detE) & (ev_e == 1)).sum())
    diffs, faB, faE = paired_bootstrap(detB, detE, nfB, nfE, ny, ev_e, ds_e, p.weighting, p.n_boot, rng, cl_e, p.boot_unit)
    lo, hi = np.nanpercentile(diffs, [2.5, 97.5])
    return {"d_hat": d_hat, "ci_lo": lo, "ci_hi": hi, "ci_width": hi - lo, "sensB": sensB, "sensE": sensE,
            "faB": fa_burden(nfB, ny), "faE": fa_burden(nfE, ny), "n_events_eval": int((ev_e == 1).sum()),
            "n_systems_eval": int(len(ev_e)), "n_negyears_eval": int(ny.sum()), "n_disc": n_disc,
            "verdict": classify(d_hat, lo, hi, p.sesoi, n_disc, p.min_discordant)}


def run_cell(args):
    specs, p_dict, label = args[:3]
    calib = args[3] if len(args) > 3 else None
    p = SimParams(**p_dict)
    rng = np.random.default_rng(p.seed)
    if calib is None:
        mu_B, delta, delta_realized, sB_realized = calibrate(specs, p, rng)
    else:
        mu_B, delta, delta_realized, sB_realized = calib
    rows = []
    for r in range(p.n_reps):
        rows.append(run_replicate(specs, p, mu_B, delta, rng))
    df = pd.DataFrame(rows)
    vc = df["verdict"].value_counts(normalize=True)
    out = {"scenario": label, **{k: v for k, v in p_dict.items()}, "mu_B": mu_B, "delta_cal": delta,
           "delta_realized": delta_realized, "sB_realized": sB_realized,
           "p_meaningful": vc.get("meaningful", 0.0), "p_negligible": vc.get("negligible", 0.0),
           "p_inconclusive": vc.get("inconclusive", 0.0), "p_harm": vc.get("harm", 0.0),
           "mean_d_hat": df["d_hat"].mean(), "sd_d_hat": df["d_hat"].std(), "mean_ci_width": df["ci_width"].mean(),
           "cover95_nominal": float(((df["ci_lo"] <= p.delta_true) & (df["ci_hi"] >= p.delta_true)).mean()),
           "cover95": float(((df["ci_lo"] <= delta_realized) & (df["ci_hi"] >= delta_realized)).mean()),
           "mean_sensB": df["sensB"].mean(), "mean_sensE": df["sensE"].mean(),
           "mean_faB_eval": df["faB"].replace(np.inf, np.nan).mean(), "mean_faE_eval": df["faE"].replace(np.inf, np.nan).mean(),
           "p_faE_gt_1.5": float((df["faE"] > 1.5).mean()),
           "p_degenerate_ci": float((df["ci_width"] == 0).mean()), "mean_n_disc": df["n_disc"].mean(),
           "n_events_eval": df["n_events_eval"].mean(), "n_systems_eval": df["n_systems_eval"].mean(),
           "n_negyears_eval": df["n_negyears_eval"].mean(),
           "n_systems_total": sum(int(round(s.n_systems * s.scale)) for s in specs),
           "n_events_total": sum(int(round(s.n_events * s.scale)) for s in specs)}
    return out


# --------------------------------------------------------------------------- #
# census-derived specs
# --------------------------------------------------------------------------- #
def spec_from_census(name, cens: pd.DataFrame, scale=1.0, cluster_col=None):
    c = cens[cens["n_origins"] > 0]
    n_cl = int(c[cluster_col].nunique()) if cluster_col and cluster_col in c else 0
    evm = c["event_in_eligible_window"].astype(bool)
    pn = c.loc[evm, ["n_pos", "n_neg"]].to_numpy()
    if len(pn) == 0:
        pn = np.array([[5, 5]])
    nn = c.loc[~evm, "n_neg"].to_numpy()
    if len(nn) == 0:
        nn = np.array([10])
    return DatasetSpec(name, int(len(c)), int(evm.sum()), pn, nn, scale, n_cl)


def synthetic_spec(name, n_systems, n_events, origins_mean=10, pos_mean=4.5):
    rng = np.random.default_rng(1)
    npos = np.clip(rng.poisson(pos_mean, 200), 1, 5)
    nneg = np.clip(rng.poisson(origins_mean, 200), 0, 40)
    return DatasetSpec(name, n_systems, n_events, np.stack([npos, nneg], axis=1), np.clip(rng.poisson(origins_mean, 400), 1, 40), 1.0)
