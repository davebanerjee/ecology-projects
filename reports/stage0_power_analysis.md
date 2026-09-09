# Stage 0 power and precision gate (Section 3.3)

Code: `src/sim/power_sim.py` (tests in `tests/test_power_sim.py`); grids:
`src/sim/run_power_grid.py` (core), `run_power_grid2.py` (events needed),
`run_power_grid3.py` (dependence, budget, cluster, episode rule), `run_power_grid_v2.py`
(both decision rules). Outputs: `results/stage0/power_grid*.csv`,
`power_gate_table.csv`, `power_gate_scaling.csv`, `power_curves.png`.
Summaries use the REALIZED population increment (the calibrated generator's
true increment, re-evaluated on an independent population), not the nominal
value, because calibration on a finite population is exact only to ±0.01–0.02.

## 1. What was simulated

The complete Sections 7–10 procedure on synthetic alarm scores whose
clustering structure comes from the census: for each dataset the number of
systems and of first-collapse events, the empirical (n positive, n negative)
origin pairs of event systems, the origin counts of non-event systems, and the
number of clusters (RAM regions 17, FishGlob survey units 4, GPDD locations
12). Scores follow a latent model with a system random effect (30 % of
variance), AR(1) within-system noise (ρ = 0.5), a risk ramp before onset
(pre-window alarms in event systems count as false), and an EWS-augmented
score = baseline + w·(δ·1[window] + noise), w = 0.3. μ_B and δ are calibrated
by bisection with common random numbers on a ≥ 3000-event population so that
the baseline's event sensitivity at the false-alarm budget is S_B = 0.45 and
the EWS model's is S_B + Δ. Per replicate: stratified split by dataset ×
event (hold-out, development fraction 0.5 or 0.7) or grouped 5-fold
cross-fitting; alarm thresholds chosen on development data for ≤ 1 false-alarm
episode per 20 non-event population-years (block episode rule; the run rule is
a sensitivity); paired event sensitivity difference on evaluation systems;
400-draw percentile bootstrap of systems within dataset × event strata (or of
clusters); Section 10 classification with the +0.10 smallest useful effect;
replicates with fewer than five discordant events are inconclusive. 400
replicates per cell.

Scenarios (systems / events): A accessible now (RAM proxy + FishGlob + GPDD:
337 / 70); B fisheries proxy only (170 / 43); C RAM ×3 projection (510 / 129);
D = C + FishGlob + GPDD (677 / 156); E = D + an LPD placeholder of 400 systems /
32 events (1077 / 188); D scaled ×1.5–×4 (235–624 events).

## 2. Gate result under the Section 10 decision rule

Gate: ≥ 0.80 power to classify a true +0.10 as "meaningful benefit" AND ≥ 0.80
probability of classifying a true 0 as "negligible". No configuration passes.

| scenario | design | weighting | events (eval) | power at +0.10 | power at +0.15 | P(negligible) at 0 | CI width at +0.10 |
|---|---|---|---|---|---|---|---|
| A accessible now | hold-out 50 % | system | 70 (35) | 0.28 | 0.53 | 0.16 | 0.23 |
| A accessible now | 5-fold cross-fit | system | 70 (70) | 0.47 | 0.75 | 0.58 | 0.17 |
| A accessible now | 5-fold cross-fit | dataset | 70 (70) | 0.32 | 0.58 | 0.61 | 0.20 |
| B fisheries proxy | 5-fold cross-fit | system | 43 (43) | 0.31 | 0.60 | 0.30 | 0.22 |
| C RAM ×3 | 5-fold cross-fit | system | 129 (129) | 0.49 | 0.90 | 0.76 | 0.13 |
| D RAM ×3 + FishGlob + GPDD | hold-out 50 % | system | 156 (79) | 0.54 | 0.85 | 0.56 | 0.16 |
| D | 5-fold cross-fit | system | 156 (156) | 0.51 | 0.91 | 0.86 | 0.12 |
| D | 5-fold cross-fit | dataset | 156 (156) | 0.52 | 0.76 | 0.61 | 0.19 |
| E D + LPD placeholder | 5-fold cross-fit | system | 188 (188) | 0.46 | 0.90 | 0.86 | 0.11 |
| E | hold-out 50 % | system | 188 (95) | 0.45 | 0.82 | 0.68 | 0.15 |
| D scaled ×2 | 5-fold cross-fit | system | 312 | 0.59 | 0.98 | 0.91 | 0.08 |
| D scaled ×4 | 5-fold cross-fit | system | 624 | 0.59 | 0.98 | 0.96 | 0.06 |

Three conclusions follow.

1. The negligible-effect criterion is reachable: with ≥ 150 events under
   cross-fitting, or ≥ 300 events under a 50 % hold-out, a true zero is
   classified negligible ≥ 0.8 of the time (system weighting).
2. The power criterion, as the Section 10 rule is written, can never be met
   at a true increment equal to the smallest useful effect: "meaningful"
   requires the point estimate itself to be ≥ 0.10, which happens about half
   the time when the truth is 0.10, however large the sample (0.51 → 0.59 from
   156 to 624 events). Power at +0.15 does rise normally (0.91 at 156 events
   under cross-fitting; 0.98 at 312). The gate therefore needs either a
   decision rule of the standard superiority-plus-relevance form (Section 4) or
   a power target set at 1.5 × the smallest useful effect.
3. Design matters as much as sample size: hold-out with 70 % development is
   uniformly the worst (13–57 evaluation events, mostly inconclusive);
   hold-out with 50 % development is the best locked design; grouped
   cross-fitting of thresholds over all systems is better still, at the cost of
   describing the result as internally validated.

The dataset-weighted estimand (the protocol's primary) is less powerful and
less well calibrated than system weighting whenever a dataset has few events
(GPDD contributes 5): its realized increment at nominal zero drifts to 0.04
and its intervals are 20–50 % wider. A minimum of ~15 evaluation events per
dataset, or pooling of small datasets, is needed before equal-dataset
weighting can be primary.

## 3. Sensitivities (scenario D, cross-fitting unless noted)

| variation | power at +0.10 | P(negligible) at 0 | note |
|---|---|---|---|
| baseline sensitivity S_B = 0.30 / 0.60 (hold-out 0.6) | 0.41 / 0.55 | 0.53 / 0.58 | weak dependence on the baseline level |
| EWS-block weight w = 0.1 / 0.6 (hold-out 0.6) | 0.54 / 0.36 | 0.11 / 0.38 | w = 0.6 (models less correlated, closer to a learner with real estimation noise) costs a third of the power |
| false-alarm budget 0.5 / 2 per 20 years | 0.54 / 0.39 | 0.91 / 0.87 | realized burdens 0.49 / 2.0 |
| system-effect share 0.1 / 0.5 | 0.44 / 0.46 | 0.91 / 0.89 | |
| within-system AR 0.2 / 0.8 | 0.70 / 0.59 | 0.82 / 0.87 | |
| cluster shocks (15 % variance) + cluster bootstrap | 0.42 | 0.90 | cluster resampling widens intervals only slightly at 4–17 clusters per dataset because FishGlob and GPDD events are few |
| conservative case: w = 0.6 + cluster shocks + cluster bootstrap | 0.56* | 0.63 | *realized increment 0.102 |
| episode rule 'run' | see Section 5 | | |

The generator ignores learner estimation error (both scores are known
functions), so real paired intervals will be wider than simulated; the w = 0.6
row is the more honest planning case.

## 4. Alternative decision rule (Stage 0 proposal, not frozen)

[ALT-RULE RESULTS PENDING]

## 5. Episode rule

Under the 'run' rule (one maximal alarm run = one episode, refractory counted
from the run's end) the false-alarm burden is bounded by about one episode per
system, so the lowest threshold meeting the budget is far too permissive:
alarms start years before the window and every event is missed (the first
grid's run-rule cells were degenerate for this reason). The threshold must
then be chosen to maximize development sensitivity subject to the budget
(implemented as a scan). With that search, scenario D under cross-fitting
gives power 0.50 at a realized +0.10 and P(negligible) 0.81 at 0 (block rule:
0.51 and 0.86), with realized false-alarm burdens of 0.66–0.82 per 20 years
because the sensitivity-optimal threshold leaves part of the budget unused.
The two rules therefore give similar power once the threshold search is
matched to the rule, but they define different quantities (under the run rule
a persistent early alarm can never count as a detection). Stage 0 recommends
the block rule as primary because the budget constraint alone controls
persistent alarms and the threshold rule stays monotone; the choice must be
frozen explicitly in Stage 1.

## 6. Events needed (system weighting, cross-fitting, block rule)

| total events | power at +0.10 (Section 10 rule) | power at +0.15 | P(negligible) at 0 | CI half-width at +0.10 |
|---|---|---|---|---|
| 156 | 0.51 | 0.93 | 0.82 | 0.06 |
| 235 | 0.38 | 0.86 | 0.93 | 0.05 |
| 312 | 0.59 | 0.98 | 0.91 | 0.04 |
| 468 | 0.61 | 0.98 | 0.92 | 0.035 |
| 624 | 0.59 | 0.98 | 0.96 | 0.03 |

With a 50 % locked hold-out the same rows read 0.49 / 0.87 / 0.59, 0.48 / 0.85 /
0.82, 0.53 / 0.93 / 0.81, 0.57 / 0.96 / 0.87 and 0.54 / 0.97 / 0.92.

## 7. Limitations of the simulation

Latent-score model rather than fitted learners (no estimation error; B/E
correlation ≈ 0.96 at w = 0.3); clusters share a random effect but events are
not made to co-occur in time within clusters; the FishGlob and GPDD event
structures rest on 22 and 5 event templates; the LPD placeholder is a guess;
percentile intervals slightly under-cover at small sizes (0.79–0.93);
calibration drift of ±0.01–0.02 in the realized increment is absorbed by
interpolation. None of these would turn a failed gate into a passed one;
all of them argue for treating the "events needed" numbers as lower bounds.
