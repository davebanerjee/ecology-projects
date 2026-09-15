# Stage 0 report — literature, data access, deduplication, feasibility, power

Project: Do generic early-warning signals add useful predictive information
about ecological population collapse? (PROTOCOL.md, Version 2.0 draft)
Stage executed: Stage 0 only (Section 15). Dates: 2026-09-08 to 2026-09-15
(the residual audit pieces, the RAM v4.66 census and the power re-run were
added on 2026-09-14/15).
Branch: `claude/ews-collapse-stage-0-p85x0w`.

Stage 0 rules were respected: no EWS feature was computed on any real series
and no predictor–outcome association was examined. Everything below that
touches real data uses metadata, observation schedules and outcome labels
only. All parameter choices are PROPOSALS for the Stage 1 freeze.

Deliverables (repository paths):

| Item | Path |
|---|---|
| saved literature queries (896 executed, dated) and raw sweep, refutation, synthesis and data-check outputs | `data/metadata/literature_queries.json`, `data/metadata/literature_sweeps_raw.json`, `literature_refutations_raw.json`, `literature_synthesis_raw.json`, `data_content_checks_raw.json` |
| literature audit and positioning | `reports/stage0_literature_audit.md` |
| data-source register (versions, licences, access, human actions) | `data/metadata/data_sources.json`, `MANIFEST.json`, `data/raw/README.md` |
| canonical system_id / deduplication plan and preliminary crosswalk | `data/metadata/system_crosswalk_plan.md`, `data/metadata/crosswalk_*.csv` |
| feasibility census (per source, attrition, sensitivity; RAM v4.66 via a derived mirror) | `reports/stage0_feasibility_census.md`, `src/census/census_ram_v466.py`, `results/stage0/*census*`, `*attrition*`, `*sensitivity_grid*` |
| outcome-label implementation and tests | `src/census/labels.py`, `tests/test_labels.py` |
| power/precision simulation and grids | `src/sim/power_sim.py`, `src/sim/run_power_grid*.py`, `results/stage0/power_*.csv`, `results/stage0/power_curves.png` |
| window-detectability simulation (Section 6.2) | `src/sim/ews_window_detectability.py`, `results/stage0/ews_window_detectability.csv` |
| proposed parameters and clarifications | `reports/stage0_proposed_parameters.md`, `CHANGELOG.md` |
| power analysis report | `reports/stage0_power_analysis.md` |

## 1. Literature audit (Section 3.1) — gate: PASSED, with a narrower claim

896 executed queries across all nine planned topic sweeps, four GitHub-only
supplementary sweeps, eight anchor-paper design extractions, all three
adversarial novelty refutations (angle D on 2024-2026 work ran on
2026-09-14 with three lenses and an adjudicator) and a synthesis agent
(569 raw study records, about 411 unique). All three refutations returned
"no equivalent study found" and the synthesis verdict is
`novel-combination-supported`; its manuscript-ready positioning statement is
in Section 15 of `reports/stage0_literature_audit.md`.

No study performs sequential, fixed-horizon prediction of first
population-abundance collapse with predictors restricted to data available at
each origin, alarm thresholds calibrated to a common false-alarm budget, a
matched state-and-trend baseline on the same origins, and complete outcome
ascertainment for negatives. The combination is novel.

The claim must be narrowed in four ways that a first pass missed. Cano et al.
(2025) already validate autocorrelation- and variance-type metrics
out-of-sample on RAM Legacy and FishGlob by leave-one-out cross-validation
across series, with AUC 0.84, 0.75 and 0.65 on RAM Legacy, ICES cod and
FishGlob. Zhang (2020) already evaluates standard deviation and lag-1
autocorrelation on 191 RAM Legacy populations with a positive likelihood ratio
and lead times beyond five years for more than half of them. Pélissié et al.
(2026) already quantify their signal's false alarms: 26 % of stocks with a
negative productivity shift went on to collapse, against base rates of 23 % in
collapsed and 12 % in non-collapsed stocks. Burthe et al. (2016) already
counted true positives, false negatives and false positives across 126
datasets with a ten-year association window, finding false positives more
common than false negatives. So we are not first to score false alarms, first
to include non-transitioning series, first to validate out-of-sample, or first
to apply these indicators at scale to our datasets.

What the audit did strengthen is the motivation. Cano et al. relabel
predicted-abrupt non-abrupt series as populations "at risk" rather than
counting them as false alarms, with no follow-up window and no later
verification; Pélissié et al. report a signal with a 26 % positive predictive
value and no comparator. An operating-point analysis against a matched
baseline is the direct remedy for both, and that is the paper's contribution.
Ward et al. (2014), verified from the authors' PDF, supplies the baseline
convention: on 2379 vertebrate series a random walk without drift is the
benchmark that 49 more complex models mostly failed to beat at 1-5 year
horizons.

Two further precedents belong in the fisheries comparator set: Pinsky &
Byler (2015) fit boosted regression trees predicting collapse across 154 RAM
Legacy populations from fishing pressure, growth rate and climate
variability, and Burgess et al. (2013) proposed a forecastable collapse
score; neither uses early-warning signals. The evaluation-methodology sweep
supplies established names and tests for the protocol's design elements
(landmarking, the seizure-prediction characteristic with event-time
surrogates as the chance null, internal-external cross-validation, Riley
sample-size targets, Van Calster calibration hierarchy). Corrections to the
plan's text: Gsell et al. 2016 analysed five freshwater ecosystems, not nine
lakes (the nine-lake set is O'Brien et al. 2023); Pélissié is not an author
of Cano et al. 2025; Litzow et al. 2013 is in Ecological Applications.
Caveats: no full text was read except Ward et al. 2014 and Lapeyrolerie &
Boettiger 2023 (both on GitHub), because publisher hosts are blocked. A
completeness critic ran last (Section 17 of the audit) and its verified
missing-study claims are listed there.

## 2. Data access and licensing (Section 3.2)

| Source | Reached | Licence / terms (evidence) | Human action before Stage 1 |
|---|---|---|---|
| RAM Legacy v4.66 | official release blocked; the v4.66 `timeseries_values_views` table was read from a public derived mirror (RaphBnrd/RAMLDB_causality, MIT; upstream CC BY 4.0) and verified by an independent recomputation | v4.66 on Zenodo (record 14043031, 2024-11-06), CC BY 4.0 per record metadata seen in search results | download the official release; freeze DOI/version/checksum; confirm licence text; re-run `census_ram_v466.py` on the official table (expect identical counts); decide zero-escapement handling and the salmon grouping |
| FishGlob v2.1.0 | yes | CC BY 4.0 (LICENSE file) + citation policy (linked Google Doc, unread) | read the disclaimer; decide on GMEX after audit |
| ICES DATRAS / SAG | blocked | ICES Data Policy; DATRAS open data CC BY 4.0 (snippets) | only for surveys/stocks absent from FishGlob/RAM |
| GPDD v2010 | yes (rgpdd bundle) | package CC0; KNB terms unverified; Reliability: higher = more reliable (IWC summary) | verify KNB licence and the user guide's reliability definitions |
| Living Planet Database | blocked | LPI Data Use Policy: non-commercial free use; substantial-use publications must contact LPI; derived data only passed on under the same terms; confidential records excluded | register, accept terms, record release; confirm that labels/partitions may be published (checkpoint 1) |
| BioTIME 2.0 | blocked (a June-2021 v1 metadata export with 417 studies was read from a collaborator's public repository as a floor) | CC BY for the database plus a per-study LICENSE column (v1 subset: 36 CC BY, 5 PDDL, 4 ODC-BY, 3 CC0, 3 ODbL, 2 CC BY-NC) | download record 15222193 (v4); recompute long-series counts for all 708 studies; read per-study licences; derive species x cell series |
| Lake challenge (O'Brien 2023) | yes (7 of 9 lakes) | no LICENSE; two lakes on request only | request restricted lakes if the challenge analysis proceeds |
| Bury 2021 classifiers | yes | CC BY-NC-SA 4.0 | confirm compatibility with benchmark release |
| EWSNet weights | yes (in O'Brien repo) | unverified | confirm licence |

Redistribution consequence: raw LPD values can never be released; FishGlob,
RAM (CC BY) and GPDD-derived labels can, subject to attribution and the KNB
check.

## 3. Deduplication plan (Section 4.2)

`data/metadata/system_crosswalk_plan.md` defines `system_id`, six matching
rules (identifier, species + stock boundary, species + region, taxon +
coordinates, GPDD taxon × location groups, published-set membership), a
blinded audit protocol and partition-integrity tests. Preliminary pass
against the full v4.66 stock list: 53 of 156 FishGlob series with eligible
origins match a RAM stock by species and region (131 candidate pairs, 130
RAM stocks of which 67 are eligible and 20 carry events; 10 of the 22
FishGlob event series have a candidate match), so FishGlob and RAM cannot be
treated as independent evidence for those species. Against the v4.41 proxy
the figures were 30 series and 74 pairs.
GPDD eligible series concentrate in a few data sources, some sit in
multi-MainID groups and 27 pairs of the same taxon lie within 50 km. Species within one FishGlob
survey unit share survey-level shocks; a survey-unit cluster bootstrap is
proposed as a robustness analysis.

## 4. Feasibility census (Section 3.2) — provisional rules, complete windows

| Source | systems with eligible origins | first collapses inside eligible windows | origins (positive / negative) |
|---|---|---|---|
| RAM v4.66 (1091 stocks with biomass; derived mirror) | 457 | 111 | 8921 (500 / 8421) |
| ... of which not Pacific salmon | 349 | 92 | 7907 (428 / 7479) |
| FishGlob v2.1.0 (screened) | 129 | 22 | 756 (86 / 670) |
| GPDD v2010 (screened) | 38 | 5 | 303 (13 / 290) |
| total accessible now | 624 | 138 | 9980 (599 / 9381) |
| (previous total with the RAM v4.41 proxy: 170 / 43) | 337 | 70 | 4166 |

Dominant attrition driver: the 30-observation history minimum. It discards
198 of the 316 RAM v4.66 collapses (most occurred inside the first 30
years of the assessment series), reduces FishGlob events from 89 (20-year
minimum) to 22, and GPDD from 16 to 5. A 25-observation minimum (the technical
floor for the provisional 15-year window + 10 trend points) gives 134 RAM
events and 51 FishGlob events; 20 observations gives 167 RAM events. Second
driver: the no-imputation rule (a complete 24-year window), which halves
FishGlob events (42 → 22) and removes every biennial salmon series. Third:
complete 5-year follow-up (106 RAM stocks with ≥ 30 observations are too
short for it; the v4.66 series end in 2016 at the median, so the proxy's
follow-up loss is largely recovered). Fourth: survey method changes and unknown effort.
FishGlob events are clustered: half sit in one Gulf of Mexico survey unit with
onsets in 2016–2020, more plausibly a survey-level shift than independent
collapses; they must not enter the confirmatory cohort before the
method-change audit. GPDD's
surviving cohort is 35 bird counts from 12 locations with onsets in 1937–1978.
The lake challenge set offers 7 public lakes with 9–28 annual and 97–332
monthly observations; annual series are far too short for the confirmatory
rules. RAM v4.66 is no longer a projection: the derived mirror gives 457 eligible
stocks and 111 events (2.7 × and 2.6 × the proxy, between the × 2 and × 3
cases used before), of which 108 stocks and 19 events are Pacific-salmon
escapement series ending by 2005. Independent events after the crosswalk
are fewer: up to 10 FishGlob event series duplicate a RAM stock and the GMEX
cluster is unaudited, so 118–128 independent first collapses is the
defensible range for the accessible data. LPD and BioTIME remain unknown
(published LPD counts say most series are 6–10 years long; the BioTIME v1
metadata floor is 50 studies with ≥ 30 sampled years, mostly the same trawl
programmes as FishGlob; the 400-system / 32-event placeholder is kept in the
power scenarios).
Structure of eligible origins: RAM median 11 origins per stock (IQR 5–25);
FishGlob median 4 (3–7); GPDD median 8 (6–12).

## 5. Power and precision gate (Section 3.3) — gate: FAILED at +0.10 on accessible data; PASSED at +0.15 with grouped cross-fitting

Full detail in `reports/stage0_power_analysis.md`; figures
`results/stage0/power_curves.png` (proxy-era grids) and
`results/stage0/power_curves_v466.png` (grids with the v4.66 cohort). The whole
Sections 7–10 procedure was simulated on census-derived structure (systems,
events, origin counts, clusters, dataset imbalance) with calibrated latent
alarm scores, 400 replicates per cell and a 400-draw paired bootstrap. The
grids were re-run on 2026-09-15 with the RAM v4.66 census in place of the
v4.41 proxy and its × 2 / × 3 projections (`power_grid_v466.csv`,
`power_gate_table_v466.csv`); the earlier grids are kept for comparison.

| data scenario | events (evaluated) | design | power at +0.10, Section 10 rule / rule B | power at +0.15, Section 10 rule / rule B | P(negligible) at 0 | verdict |
|---|---|---|---|---|---|---|
| RAM v4.66 alone | 111 (111) | grouped cross-fitting | 0.47 / 0.77 | 0.92 / 0.99 | 0.81 | fails at +0.10; passes at +0.15 under the Section 10 rule |
| RAM v4.66 alone | 111 (55) | locked hold-out, 50 % | 0.41 / 0.44 | 0.76 / 0.77 | 0.44 | fail |
| RAM v4.66 + FishGlob + GPDD (accessible now) | 138 (138) | grouped cross-fitting | 0.49 / 0.77 | 0.89 / 0.97 | 0.83 | fails at +0.10 (rule B just under 0.80); passes at +0.15 |
| accessible now | 138 (69) | locked hold-out, 50 % | 0.50 / 0.55 | 0.81 / 0.83 | 0.50 | fail (P(negligible) far below 0.80) |
| accessible now, dataset weighting | 138 (138) | grouped cross-fitting | 0.34 / 0.56 | 0.66 / 0.84 | 0.61 | fail; coverage 0.79 |
| accessible now without Pacific salmon | 119 (119) | grouped cross-fitting | 0.57 / 0.84 | ≈ 0.92 at +0.146 | 0.85 (raw, at true 0) | passes at +0.15; rule B power passes at +0.10 |
| accessible now without Pacific salmon | 119 (60) | locked hold-out, 50 % | 0.50 / 0.56 | 0.76 / 0.80 | 0.50 | fail |
| + LPD placeholder (400 systems / 32 events) | 170 (170) | grouped cross-fitting | 0.54 / 0.92 | 0.89 / 1.00 at +0.13 | 0.89 | PASS under rule B; passes at +0.15 under the Section 10 rule |
| + LPD placeholder | 170 (85) | locked hold-out, 50 % | 0.49 / 0.68 | 0.77 / 0.89 at +0.13 | 0.68 | fail |
| (previous accessible-now scenario with the RAM proxy) | 70 (70) | grouped cross-fitting | 0.44 / 0.56 | 0.83 / 0.87 | 0.68 | fail |

Power is read at the realized increment (the calibration drifts by up to
0.02 from nominal), so the +0.15 entries for the two scenarios whose realized
increments capped at 0.13–0.146 are quoted at the realized value.

Two findings dominate, and the v4.66 cohort sharpens rather than changes
them. First, the Section 10 rule ("estimate ≥ 0.10 and CI excludes 0") cannot
reach 80 % power at a true +0.10 whatever the sample size, because the point
estimate is below 0.10 half the time when the truth is 0.10; the gate must be
defined at a larger true increment (0.15) or use a superiority-plus-relevance
rule (rule B). Under rule B the accessible cohort with grouped cross-fitting
sits just under the gate (0.77 at 138 events; 0.84 without the salmon
cluster, whose calibration drifted low) and rule B calls a true +0.05
"meaningful" 26–45 % of the time; under the Section 10 rule with a 0.15
target the accessible cohort passes (0.89 power, 0.83 probability of calling
a true zero negligible) and calls a true +0.05 meaningful 7–11 % of the time.
Second, design dominates: a 50 % locked hold-out leaves 55–85 evaluation
events, which gives at most 0.50 power at +0.10 and a 0.44–0.68 chance of
calling a true zero negligible, so the locked hold-out still needs ≈ 300
events; grouped cross-fitting of thresholds over all systems reaches the
0.15 target now but must be described as internally validated (gate
alternative 3). The dataset-weighted estimand is under-powered and
mis-calibrated (coverage 0.76–0.79) while GPDD contributes 5 events. The
usual caveats hold: a less correlated EWS model (w = 0.6) costs about a
third of the power; the simulator ignores learner estimation error, so all
"events needed" figures are lower bounds; and the 138 accessible events are
118–128 after the crosswalk (Section 4), which the salmon-free scenario
brackets. The Section 6.2 window simulation (`ews_window_detectability.csv`)
shows AUROC ≈ 0.6–0.66 for the classical two-indicator score on annual data
even under favourable forcing, with mean removal clearly better than
within-window linear detrending and 15/10 (24 obs) near the floor of usable
performance.

## 6. Proposed parameter choices (not frozen)

Summarized from `reports/stage0_proposed_parameters.md`:

* Outcome: keep 0.20 × reference with 2-year persistence; keep the exact
  negative-ascertainment rule implemented in `labels.py`.
* History minimum: propose 25 observations (floor 24 for the provisional EWS
  spec); report 20 with a 12-year window as an alternative; 30 is too costly.
* Horizon 1–5 years; episode rule "new episode only when t − t_start > 5";
  false-alarm denominator = eligible negative origins; budget 1 per 20.
* Smallest useful effect: keep +10 points pending the management decision
  sketch and human sign-off (checkpoint 3).
* Design and allocation: locked hold-out with 50 % development only if ≥ 300
  independent events are available; otherwise grouped nested cross-fitting as
  the primary (described as internally validated) with a small lockbox used
  once for confirmation; never 70 % development.
* Power gate target: keep the Section 10 rule and evaluate power at a true
  increment of 0.15 (1.5 × the smallest useful effect), or adopt rule B; the
  human decides at checkpoint 3.
* Weighting: equal-dataset estimand only for datasets with ≥ 15 evaluation
  events; otherwise pool small datasets.
* FishGlob aggregation: survey_unit × species, hex7_2 footprint trimming,
  ≥ 20 hauls per year, ≥ 5 % occurrence, mean weight CPUA with zeros;
  ≤ 20 % zero years.
* GPDD: annual series only; Reliability ≥ 3 (semantics to verify); harvest
  and effort-unknown series excluded.
* Classical EWS transform: mean-removal rather than within-window linear
  detrending for short annual windows (simulation in Section 5).

## 7. Unresolved uncertainties

1. RAM Legacy v4.66: the census now rests on a derived public mirror of the
   `timeseries_values_views` table (verified internally by an independent
   recomputation, but not against the official Zenodo file, which carries
   the only authoritative version stamp); the official release must be
   downloaded and the census re-run. Two labelling decisions surfaced:
   whether zero escapement counts are observations (15 SSB stocks; no
   event onset falls on a zero) and how the 108 eligible Pacific-salmon
   rivers are grouped into biological systems.
2. LPD and BioTIME: no published count of LPD populations with ≥ 30 annual
   observations or with 80 % declines exists (modal length 6–10 years);
   BioTIME 2.0 long-series counts are known only from a v1 floor (50
   studies with ≥ 30 sampled years), per-study licences vary, and the long
   marine studies duplicate FishGlob/RAM surveys; whether LPD populations
   duplicate GPDD is unpublished.
3. Whether the GMEX event cluster is real.
4. GPDD Reliability code semantics and the KNB licence.
5. Full-text verification of Zhang 2020, Cano 2025, Pélissié 2026 designs;
   in particular how Zhang operationalized "no regime shift" and whether
   Cano's leave-one-out protocol leaks information across related stocks.
6. Full texts of the ~12 papers listed in the audit's Section 6 and the
   title-only items in its Section 14; the unresolved author attributions
   (TipPFN, Falmagne et al.) noted in Section 15.
7. Retrospective bias in assessment series (final vs as-assessed values)
   threatens a strict prequential claim for RAM-derived origins.
8. B2 state-space convergence check not run (would touch real series).
9. The power simulation is a latent-score model: it ignores model-fitting
   variance, dataset-level shocks and the possibility that the EWS block
   interacts with the baseline; a code review of the simulator was requested
   but had not completed at the time of writing.

## 8. Go / no-go recommendation

**Conditional go, narrower than the plan assumed.** With the RAM v4.66
cohort the accessible data hold 624 systems and 138 first collapses (118–128
independent after the FishGlob crosswalk; 516 systems and 119 events without
the Pacific-salmon rivers). That is enough for a confirmatory study only
under one specific design: grouped nested cross-fitting of alarm thresholds
over all systems as the primary analysis (reported as internally validated,
gate alternative 3), system weighting, the block episode rule, and the
Section 10 decision rule with the smallest useful effect kept at +0.10 but
the power target defined at a true +0.15 (0.89 power; 0.83 probability of
calling a true zero negligible; 7–11 % chance of calling a true +0.05
meaningful). It is not enough for the plan's preferred design: a 50 %
locked hold-out reaches 0.50 power at +0.10 and 0.81 at +0.15 but calls a
true zero negligible only half the time, so an imprecise null would not be
interpretable. Rule B (superiority plus relevance) reaches 0.77–0.84 power at
+0.10 with cross-fitting but labels a true +0.05 meaningful a third of the
time and is not recommended as the primary rule.

**Three conditions before Stage 1.**

1. Human acquisition of the official RAM Legacy v4.66 release from Zenodo
   and a re-run of `census_ram_v466.py` on it (the Stage 0 counts come from
   a derived public mirror, verified internally but not against the official
   file), plus the Living Planet Database and BioTIME 2.0 if the locked
   hold-out design is wanted: with ≈ 32 further independent events the
   cross-fitting design passes under either rule, and the hold-out design
   needs ≈ 300 events in total.
2. The independence audit: the 10 FishGlob event series with a candidate RAM
   match, the GMEX cluster, and the grouping of the 108 salmon rivers into
   systems, all decided blind to any predictor.
3. Stage 1 freezes, with human sign-off: the 25-observation history minimum
   with the 15/10 EWS windows (or 30 with 20/10; 25 gives 134 RAM events),
   the block episode rule, the stock-level abundance-variable rule and the
   zero-value rule for RAM, the smallest useful effect and the 0.15 power
   target, system weighting (or a per-dataset event floor), and the
   FishGlob/GPDD screening rules listed in Section 6.

If the official RAM file or the independence audit removes more than about
20 events, the study should narrow to a fisheries-only, estimation-focused
design (gate alternative 2) and drop equivalence claims. The literature gate
is passed (novel combination, three refutations, synthesis verdict
supported; Zhang 2020, Cano 2025 and Pélissié 2026 must be read in full
first). The licensing position is workable: RAM, FishGlob, ICES and (pending
the KNB check) GPDD allow redistribution of raw values with attribution; LPD
raw values cannot be released and derived labels only under the same terms;
BioTIME carries per-study licences that must be read.
