import numpy as np
import pandas as pd
import pytest

from src.census.labels import regularize, reference_levels, collapse_onset, forecast_origins, summarize_series


def test_regularize_fills_gaps():
    s = regularize([2000, 2001, 2003], [1.0, 2.0, 4.0])
    assert list(s.index) == [2000, 2001, 2002, 2003]
    assert np.isnan(s.loc[2002])


def test_reference_uses_only_past_windows():
    # 10 years at 100, then a jump to 1000 at year 10: R(10) must not see year 10
    vals = [100.0] * 10 + [1000.0] + [100.0] * 5
    x = regularize(range(2000, 2016), vals)
    R = reference_levels(x)
    assert R.loc[2010] == 100.0            # reference before the jump
    assert R.loc[2015] == pytest.approx(np.median([100, 100, 1000, 100, 100]))  # window ending 2012 includes 1000 -> median 100
    # max over medians: windows containing 1000 have median 100 (single outlier), so R stays 100
    assert R.loc[2015] == 100.0


def test_reference_undefined_before_five_positive_obs():
    x = regularize(range(2000, 2010), [0, 0, 0, 5, 5, 5, 5, 5, 5, 5])
    R = reference_levels(x)
    # windows: first complete window ends 2004 with values [0,0,0,5,5] -> median 0; running max 0 -> R undefined (must be >0)
    assert np.isnan(R.loc[2005])
    # by 2008, five positive obs exist before (2003..2007) and window 2003-2007 median 5 -> R(2008)=5
    assert R.loc[2008] == 5.0


def test_onset_requires_two_consecutive_lows_and_fixed_threshold():
    vals = [100.0] * 30 + [10.0, 50.0] + [100.0] * 3 + [15.0, 15.0, 15.0]
    yrs = list(range(1970, 1970 + len(vals)))
    x = regularize(yrs, vals)
    on = collapse_onset(x)
    # year 2000 is a single-year dip (10 then 50): not an onset
    assert on.onset_year == 2005
    assert on.reference_at_onset == 100.0
    assert on.threshold_at_onset == pytest.approx(20.0)
    assert on.onset_status.loc[2000] == 0
    assert on.onset_status.loc[2005] == 1


def test_onset_unknown_when_second_year_missing():
    vals = [100.0] * 30 + [10.0, np.nan, 100.0]
    x = regularize(range(1970, 1970 + len(vals)), vals)
    on = collapse_onset(x)
    assert on.onset_year is None
    assert on.onset_status.loc[2000] == -1


def test_each_series_has_at_most_one_onset():
    vals = [100.0] * 30 + [5.0] * 5 + [100.0] * 10 + [5.0] * 5
    x = regularize(range(1970, 1970 + len(vals)), vals)
    on = collapse_onset(x)
    assert on.onset_year == 2000
    orig = forecast_origins(x, on)
    assert (orig["year"] < 2000).all()


def test_negative_origin_needs_complete_ascertainment():
    # 40 years of 100, but year 2005 missing: origins whose horizon covers 2005 are excluded
    vals = [100.0] * 40
    yrs = list(range(1970, 2010))
    x = regularize(yrs, vals)
    x.loc[2005] = np.nan
    on = collapse_onset(x)
    assert on.onset_year is None
    orig = forecast_origins(x, on, horizon=5, min_history=30)
    years = set(orig["year"])
    # origin t needs 2005 not in t+1..t+5 -> t <= 1999 or t >= 2005; t must be observed and have >=30 history
    for t in range(2000, 2005):
        assert t not in years
    # 2006 would need 2007..2011 ascertained but the series ends 2009 -> only 1999 survives
    assert years == {1999}


def test_min_history_threshold():
    vals = [100.0] * 40
    x = regularize(range(1970, 2010), vals)
    on = collapse_onset(x)
    orig = forecast_origins(x, on, min_history=30)
    assert orig["year"].min() == 1999  # 30th observation is 1999
    assert orig["year"].max() == 2004  # needs 2005..2009 ascertained


def test_positive_labels_within_horizon():
    vals = [100.0] * 40 + [5.0, 5.0, 5.0]
    x = regularize(range(1970, 1970 + len(vals)), vals)
    on = collapse_onset(x)
    assert on.onset_year == 2010
    orig = forecast_origins(x, on, horizon=5, min_history=30)
    pos = orig.loc[orig.label == 1, "year"].tolist()
    assert pos == [2005, 2006, 2007, 2008, 2009]
    neg = orig.loc[orig.label == 0, "year"].tolist()
    assert neg == list(range(1999, 2005))


def test_negative_edge_case_last_year_below_threshold_unknown():
    # series ends with a single low year: onset at last year is unknown, so origin 5 years earlier is not ascertainable
    vals = [100.0] * 40 + [5.0]
    x = regularize(range(1970, 1970 + len(vals)), vals)
    on = collapse_onset(x)
    assert on.onset_year is None
    orig = forecast_origins(x, on)
    assert 2005 not in set(orig["year"])  # horizon 2006..2010 includes unknown 2010
    assert 2004 in set(orig["year"])


def test_low_then_missing_censors_origins():
    # a low year followed by a missing year is an unconfirmed collapse: origins from that year on are censored
    vals = [100.0] * 40 + [5.0, np.nan, 5.0, 5.0, 5.0]
    x = regularize(range(1970, 1970 + len(vals)), vals)
    on = collapse_onset(x)
    assert on.onset_year == 2012 and on.first_unknown_low == 2010 and on.censor_year == 2010
    orig = forecast_origins(x, on, min_complete_window=0)
    assert orig["year"].max() < 2010
    # origins whose horizon contains the unknown year but not the onset are excluded; those containing the onset are positive
    assert set(orig.loc[orig.label == 1, "year"]) == {2007, 2008, 2009}
    assert 2005 not in set(orig["year"]) and 2004 in set(orig["year"])


def test_undefined_reference_is_unknown_not_negative():
    # zeros only: reference never defined -> no negative origins
    vals = [0.0] * 36 + [3.0, 0, 0, 0, 0, 0]
    x = regularize(range(1970, 1970 + len(vals)), vals)
    on = collapse_onset(x)
    assert on.onset_year is None and (on.onset_status == -1).all()
    assert len(forecast_origins(x, on, min_complete_window=0)) == 0


def test_complete_window_required():
    vals = [100.0] * 45
    x = regularize(range(1970, 2015), vals)
    x.loc[1990] = np.nan
    on = collapse_onset(x)
    o24 = forecast_origins(x, on, min_history=30, min_complete_window=24)
    o0 = forecast_origins(x, on, min_history=30, min_complete_window=0)
    # with a 24-year complete window the first eligible origin is 2013 (1990 missing) -> but needs follow-up to 2018: none
    assert len(o24) == 0
    assert len(o0) > 0 and o0["year"].min() == 2000  # 30 observations reached in 2000 (1990 missing)


def test_summarize_series_counts():
    vals = [100.0] * 40 + [5.0, 5.0, 5.0]
    d = summarize_series(range(1970, 1970 + len(vals)), vals)
    assert d["onset_year"] == 2010 and d["n_pos"] == 5 and d["n_neg"] == 6 and d["censor_year"] == 2010
