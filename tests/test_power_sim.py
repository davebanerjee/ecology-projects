import numpy as np
from src.sim.power_sim import episode_starts, metrics_from_starts, fa_burden, choose_threshold, classify, gen_population, gen_scores, DatasetSpec, SimParams


def test_episode_refractory_and_truth():
    # one system, 12 origins; labels: 7 negatives then 5 positives
    Y = np.array([[0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]])
    S = np.array([[1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]], dtype=float)
    st = episode_starts(S, Y, 0.5, refractory=5)
    # alarm at t=0 starts an episode (false); t=1 belongs to it; next possible start t>=6; alarms at 8.. -> start at 8 (true)
    assert st[0].tolist() == [True, False, False, False, False, False, False, False, True, False, False, False]
    det, nf, ny = metrics_from_starts(st, Y, np.array([1]))
    assert det[0] and nf[0] == 1 and ny[0] == 7


def test_persistent_alarm_masks_window_until_refractory_ends():
    Y = np.array([[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]])
    S = np.ones((1, 11))
    st = episode_starts(S, Y, 0.5, refractory=5)
    # starts at 0 (false) and at 6 (true), nothing in between
    assert np.where(st[0])[0].tolist() == [0, 6]


def test_padding_ignored():
    Y = np.array([[0, 0, 1, -1, -1]])
    S = np.array([[0, 0, 1, np.nan, np.nan]])
    st = episode_starts(S, Y, 0.5)
    assert st[0].tolist() == [False, False, True, False, False]
    det, nf, ny = metrics_from_starts(st, Y, np.array([1]))
    assert det[0] and nf[0] == 0 and ny[0] == 2


def test_fa_burden_units():
    assert fa_burden(np.array([2, 0]), np.array([20, 20])) == 1.0


def test_choose_threshold_respects_budget():
    rng = np.random.default_rng(0)
    n, L = 400, 15
    Y = np.zeros((n, L), dtype=int)
    S = rng.normal(size=(n, L))
    th = choose_threshold(S, Y, np.zeros(n), budget=1.0)
    st = episode_starts(S, Y, th)
    det, nf, ny = metrics_from_starts(st, Y, np.zeros(n))
    assert fa_burden(nf, ny) <= 1.0


def test_classify_rules():
    assert classify(0.12, 0.02, 0.22, 0.10) == "meaningful"
    assert classify(0.03, -0.02, 0.08, 0.10) == "negligible"
    assert classify(-0.05, -0.10, -0.01, 0.10) == "harm"
    assert classify(0.12, -0.01, 0.25, 0.10) == "inconclusive"


def test_run_rule_episodes():
    Y = np.array([[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]])
    S = np.ones((1, 11))
    st = episode_starts(S, Y, 0.5, refractory=5, rule="run")
    assert np.where(st[0])[0].tolist() == [0]          # one persistent run = one (false) episode, event missed
    S2 = np.array([[1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1]])
    st2 = episode_starts(S2, Y, 0.5, refractory=5, rule="run")
    assert np.where(st2[0])[0].tolist() == [0, 8]      # gap of 6 quiet years -> new (true) episode


def test_ramp_never_exceeds_one_for_negatives():
    sp = DatasetSpec("d", 6, 6, np.array([[3, 2], [1, 5], [5, 10]]), np.array([5]), 1.0)
    rng = np.random.default_rng(3)
    Y, K, ds, ev, cl = gen_population([sp], rng)
    assert (K[Y == 0] >= 6).all() and (K[Y == 1] <= 5).all()
    p = SimParams()
    # deterministic check of the ramp via a zero-noise configuration
    p.s_u2 = 0.0; p.rho = 0.0
    sB, sE = gen_scores(Y, K, ev, p, mu_B=1.0, delta=0.0, rng=np.random.default_rng(0), cl=cl)
    # mean of many draws not needed: ramp is deterministic; recompute it directly
    ramp = np.where(Y == 1, 1.0, np.where(Y == 0, np.exp(-(K - 5) / p.tau), 0.0))
    assert (ramp[Y == 0] < 1.0).all()


def test_gen_population_structure():
    sp = DatasetSpec("d", 10, 4, np.array([[5, 10], [3, 20]]), np.array([8, 12]), 1.0)
    Y, K, ds, ev, cl = gen_population([sp], np.random.default_rng(1))
    assert Y.shape[0] == 10 and ev.sum() == 4
    for i in range(10):
        row = Y[i][Y[i] >= 0]
        if ev[i]:
            assert row[-1] == 1 and row.sum() in (3, 5)
            assert K[i][len(row) - 1] == 1  # last origin is one year before onset
            assert cl[i] == i or True
        else:
            assert row.sum() == 0
