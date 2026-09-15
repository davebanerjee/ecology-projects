import numpy as np
import pandas as pd
from src.census.census_ram_v466 import build_long


def _frame():
    rows = []
    # stock A: SSB for 1990-1999 and TB for 1985-1999 -> SSB chosen for the WHOLE stock (no TB rows spliced in)
    for y in range(1985, 2000):
        rows.append({"stockid": "A", "year": y, "SSB": float(y) if y >= 1990 else np.nan, "TBbest": np.nan, "TB": 2.0 * y})
    # stock B: TBbest only
    for y in range(1990, 2000):
        rows.append({"stockid": "B", "year": y, "SSB": np.nan, "TBbest": 1.0, "TB": 1.0})
    # stock C: SST-only row (no RAM series)
    rows.append({"stockid": "C", "year": 1995, "SSB": np.nan, "TBbest": np.nan, "TB": np.nan})
    # stock D: SSB with zeros and one negative value
    for y, v in zip(range(1990, 1995), [1.0, 0.0, 2.0, -1.0, 3.0]):
        rows.append({"stockid": "D", "year": y, "SSB": v, "TBbest": np.nan, "TB": np.nan})
    return pd.DataFrame(rows)


def test_stock_level_preference_not_row_level():
    long, choice = build_long(_frame(), ("SSB", "TBbest", "TB"))
    assert choice["A"] == "SSB" and choice["B"] == "TBbest" and "C" not in choice.index
    a = long[long["stockid"] == "A"]
    assert a["year"].min() == 1990 and len(a) == 10  # TB years before 1990 are NOT spliced in
    assert set(long["stockid"]) == {"A", "B", "D"}


def test_tbbest_preferred_variant_and_zero_handling():
    long, choice = build_long(_frame(), ("TBbest", "TB", "SSB"))
    assert choice["A"] == "TB" and choice["B"] == "TBbest"
    assert len(long[long["stockid"] == "A"]) == 15
    d_keep, _ = build_long(_frame(), ("SSB", "TBbest", "TB"))
    d_drop, _ = build_long(_frame(), ("SSB", "TBbest", "TB"), zeros_as_missing=True)
    assert len(d_keep[d_keep["stockid"] == "D"]) == 4   # negative dropped, zero kept
    assert len(d_drop[d_drop["stockid"] == "D"]) == 3   # zero dropped too
