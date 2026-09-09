"""Outcome labels for Stage 0 feasibility census.

Implements the unique collapse-onset rule of PROTOCOL Section 5.1 and the
forecast-origin eligibility rules of Sections 4.3 and 5.2, on a regular
annual grid.  Nothing here touches early-warning-signal features.

Conventions
-----------
* A series is a pandas Series indexed by integer year, with NaN for years
  that were not observed.  The index must be a complete consecutive range
  (use ``regularize``).
* Reference level  R(s) = max_{u <= s-1} median(x[u-4..u]) over windows whose
  five values are all observed.  R(s) is undefined (NaN) unless at least
  ``min_positive_ref`` positive observations exist before s and at least one
  complete window exists.
* Collapse onset C = first s with x[s] < frac*R(s) and x[s+1] < frac*R(s)
  (threshold fixed at onset).  Both values must be observed.
* An onset at s is *ruled out* (ascertained negative) when R(s) is defined and
  x[s] is observed and x[s] >= frac*R(s), or when x[s] < frac*R(s) but x[s+1]
  is observed and x[s+1] >= frac*R(s).  When R(s) is undefined, or x[s] is
  missing, or x[s] is low and x[s+1] is missing, the status at s is *unknown*.
* The first year s* < C at which x[s*] is low but x[s*+1] is missing marks an
  unconfirmed collapse: origins at t >= s* are censored (the population may
  already be collapsed), as are all origins at t >= C.
* Forecast origin t is eligible when x[t] is observed, t < min(C, s*),
  at least ``min_history`` observations exist at years <= t, the trailing
  ``min_complete_window`` years up to t are all observed (no imputation), and
  the fixed-horizon label Y_t is ascertainable:  Y_t = 1 if C in {t+1..t+H};
  Y_t = 0 only if onset is ruled out at every s in {t+1..t+H}.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd


def regularize(years, values) -> pd.Series:
    """Return a Series on the complete consecutive integer-year grid."""
    years = np.asarray(years, dtype=int)
    values = np.asarray(values, dtype=float)
    if len(years) == 0:
        return pd.Series(dtype=float)
    s = pd.Series(values, index=years)
    s = s[~s.index.duplicated(keep="first")]
    full = pd.RangeIndex(int(years.min()), int(years.max()) + 1)
    return s.reindex(full).astype(float)


def reference_levels(x: pd.Series, window: int = 5, min_positive_ref: int = 5) -> pd.Series:
    """R(s) for every year s on the grid (NaN where undefined)."""
    vals = x.to_numpy(dtype=float)
    n = len(vals)
    med = np.full(n, np.nan)
    for u in range(window - 1, n):
        w = vals[u - window + 1 : u + 1]
        if np.all(np.isfinite(w)):
            med[u] = np.median(w)
    # running max of medians over u <= s-1
    R = np.full(n, np.nan)
    running = np.nan
    n_pos = 0
    for s in range(n):
        if s - 1 >= 0:
            m = med[s - 1]
            if np.isfinite(m):
                running = m if not np.isfinite(running) else max(running, m)
            v = vals[s - 1]
            if np.isfinite(v) and v > 0:
                n_pos += 1
        if np.isfinite(running) and n_pos >= min_positive_ref and running > 0:
            R[s] = running
    return pd.Series(R, index=x.index)


@dataclass
class OnsetResult:
    onset_year: Optional[int]
    threshold_at_onset: Optional[float]
    reference_at_onset: Optional[float]
    onset_status: pd.Series = field(repr=False)  # per year: 1=onset, 0=ruled out, -1=unknown
    first_unknown_low: Optional[int] = None      # first low year whose confirmation year is missing (before onset)

    @property
    def censor_year(self) -> Optional[int]:
        ys = [y for y in (self.onset_year, self.first_unknown_low) if y is not None]
        return min(ys) if ys else None


def collapse_onset(x: pd.Series, frac: float = 0.20, window: int = 5,
                   min_positive_ref: int = 5, persistence: int = 2) -> OnsetResult:
    """Unique first collapse onset per Section 5.1 (persistence=2 means x[s], x[s+1])."""
    R = reference_levels(x, window=window, min_positive_ref=min_positive_ref)
    vals = x.to_numpy(dtype=float)
    Rv = R.to_numpy(dtype=float)
    n = len(vals)
    status = np.full(n, -1, dtype=int)
    onset = None
    thr_at = None
    ref_at = None
    first_unknown_low = None
    for s in range(n):
        if not np.isfinite(Rv[s]):
            status[s] = -1  # no reference defined -> onset status cannot be determined at s
            continue
        thr = frac * Rv[s]
        if not np.isfinite(vals[s]):
            status[s] = -1
            continue
        if vals[s] >= thr:
            status[s] = 0
            continue
        # x[s] below threshold; need persistence-1 further consecutive lows
        st = 1
        for k in range(1, persistence):
            if s + k >= n or not np.isfinite(vals[s + k]):
                st = -1
                break
            if vals[s + k] >= thr:
                st = 0
                break
        status[s] = st
        if st == -1 and onset is None and first_unknown_low is None:
            first_unknown_low = int(x.index[s])
        if st == 1 and onset is None:
            onset = int(x.index[s])
            thr_at = float(thr)
            ref_at = float(Rv[s])
    return OnsetResult(onset, thr_at, ref_at, pd.Series(status, index=x.index), first_unknown_low)


@dataclass
class OriginTable:
    origins: pd.DataFrame  # columns: year, label (0/1), n_hist


def forecast_origins(x: pd.Series, onset: OnsetResult, horizon: int = 5,
                     min_history: int = 30, min_complete_window: int = 24) -> pd.DataFrame:
    """Eligible forecast origins with ascertained fixed-horizon labels.

    ``min_complete_window`` = length of the trailing window (years t-w+1..t)
    that must be fully observed (Section 4.3: complete regular windows, no
    imputation); 0 disables the check (gap-tolerant sensitivity).
    """
    vals = x.to_numpy(dtype=float)
    years = x.index.to_numpy()
    st = onset.onset_status.to_numpy()
    n = len(vals)
    fin = np.isfinite(vals)
    obs_cum = np.cumsum(fin)
    rows = []
    C = onset.onset_year
    cens = onset.censor_year
    for t in range(n):
        yr = int(years[t])
        if not fin[t]:
            continue
        if cens is not None and yr >= cens:
            break
        if obs_cum[t] < min_history:
            continue
        if min_complete_window > 0:
            if t - min_complete_window + 1 < 0 or not fin[t - min_complete_window + 1 : t + 1].all():
                continue
        # label
        if C is not None and C <= yr + horizon:
            label = 1
        else:
            # need onset ruled out at every s in t+1..t+H
            ok = True
            for k in range(1, horizon + 1):
                s = t + k
                if s >= n or st[s] != 0:
                    ok = False
                    break
            if not ok:
                continue
            label = 0
        rows.append({"year": yr, "label": label, "n_hist": int(obs_cum[t])})
    return pd.DataFrame(rows, columns=["year", "label", "n_hist"])


def summarize_series(years, values, *, frac=0.20, window=5, min_positive_ref=5,
                     persistence=2, horizon=5, min_history=30, min_complete_window=24) -> dict:
    """One-row census summary for a series (metadata + outcome only)."""
    x = regularize(years, values)
    n_obs = int(np.isfinite(x.to_numpy()).sum())
    out = {
        "n_obs": n_obs,
        "start": int(x.index.min()) if n_obs else None,
        "end": int(x.index.max()) if n_obs else None,
        "span": int(len(x)) if n_obs else 0,
        "n_missing_years": int(len(x) - n_obs) if n_obs else 0,
        "n_zero": int((x.to_numpy() == 0).sum()) if n_obs else 0,
        "onset_year": None, "censor_year": None, "n_origins": 0, "n_pos": 0, "n_neg": 0,
        "first_origin": None, "last_origin": None,
    }
    if n_obs == 0:
        return out
    on = collapse_onset(x, frac=frac, window=window, min_positive_ref=min_positive_ref,
                        persistence=persistence)
    orig = forecast_origins(x, on, horizon=horizon, min_history=min_history,
                            min_complete_window=min_complete_window)
    out["onset_year"] = on.onset_year
    out["censor_year"] = on.censor_year
    out["n_origins"] = int(len(orig))
    out["n_pos"] = int(orig["label"].sum()) if len(orig) else 0
    out["n_neg"] = int((orig["label"] == 0).sum()) if len(orig) else 0
    out["first_origin"] = int(orig["year"].min()) if len(orig) else None
    out["last_origin"] = int(orig["year"].max()) if len(orig) else None
    out["event_in_eligible_window"] = bool(out["n_pos"] > 0)
    return out
