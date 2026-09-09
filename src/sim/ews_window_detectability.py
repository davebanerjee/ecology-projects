"""Section 6.2 window-duration study on SIMULATED series only (no real data).

Question: for annual series with 25-60 years of history before the origin, which
indicator-window length (w) and trend length (k indicator estimates) give the
best detectability of critical slowing down 1-5 years before a fold-type
transition, at a fixed false-alarm rate on null series?  Also reports the
false-positive rate on red-noise nulls (no resilience loss), to expose
window choices that are fooled by autocorrelated noise.

Model (annual):  x_t = a_t x_{t-1} + sigma eps_t + observation error;
forced series: a_t rises linearly from a0 to 0.97 over the last `ramp` years
so the transition ("collapse") is at the end of the ramp;  null series keep
a_t = a0.  Red-noise nulls use a0 = 0.7.  Scores: Kendall tau of rolling
lag-1 autocorrelation and log variance (within-window linear detrend), averaged
after z-scaling against the null score distribution for the same (w, k).
"""
from __future__ import annotations

import itertools
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import kendalltau

OUT = "results/stage0"


def simulate(n, T, a0, ramp, rng, sigma=1.0, obs_sd=0.3):
    x = np.zeros((n, T))
    a = np.full(T, a0)
    if ramp:
        a[-ramp:] = np.linspace(a0, 0.97, ramp)
    eps = rng.normal(size=(n, T))
    for t in range(1, T):
        x[:, t] = a[t] * x[:, t - 1] + sigma * eps[:, t]
    return x + rng.normal(0, obs_sd, size=(n, T))


def rolling_indicators(x, w, detrend="mean"):
    """AR1 and log-variance of within-window detrended values, for every window end.

    detrend='mean' removes the window mean; 'linear' removes a within-window
    linear trend (which, for short windows, also removes most of the
    low-frequency signal that critical slowing down produces).
    """
    n, T = x.shape
    ar1 = np.full((n, T), np.nan)
    lv = np.full((n, T), np.nan)
    tt = np.arange(w)
    A = np.vstack([tt, np.ones(w)]).T if detrend == "linear" else np.ones((w, 1))
    P = np.eye(w) - A @ np.linalg.pinv(A)  # residual-maker
    for e in range(w - 1, T):
        seg = x[:, e - w + 1 : e + 1] @ P.T
        v = seg.var(axis=1)
        lv[:, e] = np.log(v + 1e-12)
        num = (seg[:, 1:] * seg[:, :-1]).sum(axis=1)
        den = (seg ** 2).sum(axis=1)
        ar1[:, e] = num / np.maximum(den, 1e-12)
    return ar1, lv


def tau_trend(ind, k):
    n, T = ind.shape
    out = np.full((n, T), np.nan)
    idx = np.arange(k)
    for e in range(T):
        seg = ind[:, e - k + 1 : e + 1] if e - k + 1 >= 0 else None
        if seg is None or np.isnan(seg).any():
            continue
        out[:, e] = [kendalltau(idx, row)[0] for row in seg]
    return out


def score_at(x, w, k, origins, detrend="mean"):
    ar1, lv = rolling_indicators(x, w, detrend)
    ta, tv = tau_trend(ar1, k), tau_trend(lv, k)
    s = 0.5 * (ta + tv)
    return s[:, origins]


def auroc(pos, neg):
    pos, neg = pos[~np.isnan(pos)], neg[~np.isnan(neg)]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    ranks = pd.Series(np.concatenate([pos, neg])).rank().to_numpy()
    return (ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def main(n=400, seed=1):
    rng = np.random.default_rng(seed)
    rows = []
    for hist in (25, 30, 40, 60):
        T = hist + 5                       # origins at T-6 .. T-2 are 1-5 years before the transition at T-1
        origins = np.arange(T - 6, T - 1)
        forced = simulate(n, T, 0.3, ramp=min(40, hist), rng=rng)
        null_w = simulate(n, T, 0.3, ramp=0, rng=rng)
        null_r = simulate(n, T, 0.7, ramp=0, rng=rng)
        for w, k, dt in itertools.product((10, 15, 20), (5, 10, 15), ("mean", "linear")):
            if w + k - 1 > hist:
                continue
            sf, sw, sr = score_at(forced, w, k, origins, dt), score_at(null_w, w, k, origins, dt), score_at(null_r, w, k, origins, dt)
            thr = np.nanquantile(sw, 0.95)
            rows.append({"history": hist, "w": w, "k": k, "detrend": dt, "min_obs_needed": w + k - 1,
                         "auroc_vs_white_null": auroc(sf.ravel(), sw.ravel()),
                         "auroc_vs_red_null": auroc(sf.ravel(), sr.ravel()),
                         "sens_at_5pct_FA": float(np.nanmean(sf >= thr)),
                         "FA_rate_red_null_at_white_thr": float(np.nanmean(sr >= thr))})
            print(rows[-1], flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "ews_window_detectability.csv"), index=False)
    print(df.to_string())


if __name__ == "__main__":
    main(n=int(sys.argv[1]) if len(sys.argv) > 1 else 400)
