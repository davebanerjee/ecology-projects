"""Generic per-series census and attrition tables (metadata + outcome labels only)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .labels import summarize_series

LABEL_KW = dict(frac=0.20, window=5, min_positive_ref=5, persistence=2, horizon=5, min_history=30, min_complete_window=24)


def census_long(df: pd.DataFrame, id_col: str, year_col: str, value_col: str, **kw) -> pd.DataFrame:
    """Per-series census from a long table with one row per (series, year)."""
    kw = {**LABEL_KW, **kw}
    rows = []
    for sid, g in df.groupby(id_col, sort=False):
        g = g[[year_col, value_col]].dropna()
        d = summarize_series(g[year_col].to_numpy(), g[value_col].to_numpy(), **kw)
        d[id_col] = sid
        rows.append(d)
    out = pd.DataFrame(rows)
    return out.set_index(id_col)


def attrition(cens: pd.DataFrame, steps: list[tuple[str, pd.Series]]) -> pd.DataFrame:
    """Sequential attrition: each step is (name, boolean mask aligned to cens.index)."""
    keep = pd.Series(True, index=cens.index)
    rows = []
    for name, mask in steps:
        keep = keep & mask.reindex(cens.index).fillna(False).astype(bool)
        sub = cens[keep]
        rows.append({
            "criterion": name,
            "n_series": int(keep.sum()),
            "n_with_origins": int((sub["n_origins"] > 0).sum()),
            "n_origins": int(sub["n_origins"].sum()),
            "n_events_in_window": int(sub["event_in_eligible_window"].fillna(False).astype(bool).sum()) if "event_in_eligible_window" in sub else 0,
            "n_pos_origins": int(sub["n_pos"].sum()),
            "n_neg_origins": int(sub["n_neg"].sum()),
        })
    return pd.DataFrame(rows)


def sensitivity_grid(df: pd.DataFrame, id_col: str, year_col: str, value_col: str,
                     grid: list[dict]) -> pd.DataFrame:
    """Re-run the census under alternative outcome/eligibility parameters."""
    rows = []
    for kw in grid:
        c = census_long(df, id_col, year_col, value_col, **kw)
        rows.append({**kw,
                     "n_series_with_origins": int((c["n_origins"] > 0).sum()),
                     "n_origins": int(c["n_origins"].sum()),
                     "n_events_in_window": int(c["event_in_eligible_window"].fillna(False).astype(bool).sum()),
                     "n_pos_origins": int(c["n_pos"].sum()),
                     "n_neg_origins": int(c["n_neg"].sum()),
                     "n_series_with_any_onset": int(c["onset_year"].notna().sum())})
    return pd.DataFrame(rows)
