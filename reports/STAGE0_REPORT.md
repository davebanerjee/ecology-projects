# Stage 0 report — literature, data access, deduplication, feasibility, power

Project: Do generic early-warning signals add useful predictive information
about ecological population collapse? (PROTOCOL.md, Version 2.0 draft)
Stage executed: Stage 0 only (Section 15). Dates: 2026-09-08 to 2026-09-09.
Branch: `claude/ews-collapse-stage-0-p85x0w`.

Stage 0 rules were respected: no EWS feature was computed on any real series
and no predictor–outcome association was examined. Everything below that
touches real data uses metadata, observation schedules and outcome labels
only. All parameter choices are PROPOSALS for the Stage 1 freeze.

Deliverables (repository paths):

| Item | Path |
|---|---|
| saved literature queries (243, dated) and raw sweep results | `data/metadata/literature_queries.json`, `data/metadata/literature_sweeps_raw.json` |
| literature audit and positioning | `reports/stage0_literature_audit.md` |
| data-source register (versions, licences, access, human actions) | `data/metadata/data_sources.json`, `MANIFEST.json`, `data/raw/README.md` |
| canonical system_id / deduplication plan and preliminary crosswalk | `data/metadata/system_crosswalk_plan.md`, `data/metadata/crosswalk_*.csv` |
| feasibility census (per source, attrition, sensitivity) | `reports/stage0_feasibility_census.md`, `results/stage0/*census*`, `*attrition*`, `*sensitivity_grid*` |
| outcome-label implementation and tests | `src/census/labels.py`, `tests/test_labels.py` |
| power/precision simulation and grids | `src/sim/power_sim.py`, `src/sim/run_power_grid*.py`, `results/stage0/power_*.csv`, `results/stage0/power_curves.png` |
| window-detectability simulation (Section 6.2) | `src/sim/ews_window_detectability.py`, `results/stage0/ews_window_detectability.csv` |
| proposed parameters and clarifications | `reports/stage0_proposed_parameters.md`, `CHANGELOG.md` |
| power analysis report | `reports/stage0_power_analysis.md` |

## 1. Literature audit (Section 3.1) — gate: PASSED, with a narrower claim

482 executed queries across four topic sweeps with working search, two
GitHub-only supplementary sweeps and eight anchor-paper design extractions
(256 study records). Detail in `reports/stage0_literature_audit.md`.

No study performs sequential, fixed-horizon prediction of first
population-abundance collapse with predictors restricted to data available at
each origin, alarm thresholds calibrated to a common false-alarm budget, a
matched state-and-trend baseline on the same origins, and complete outcome
ascertainment for negatives. The combination is novel.

The claim must be narrowed in four ways that a first pass missed. Cano et al.
(2025) already validate autocorrelation- and variance-type metrics
out-of-sample on RAM Legacy and FishGlob by leave-one-out cross-validation
across series, with AUC 0.84, 0.75 and 0.65 on RAM Legacy, ICES cod and
FishGlob. Zhang et al. (2020) already evaluate standard deviation and lag-1
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

Corrections to the plan's text: Gsell et al. 2016 analysed five freshwater
ecosystems, not nine lakes (the nine-lake set is O'Brien et al. 2023);
Pélissié is not an author of Cano et al. 2025; Litzow et al. 2013 is in
Ecological Applications. Caveats: no full text was read except Ward et al.
2014 and Lapeyrolerie & Boettiger 2023 (both on GitHub), because publisher
hosts are blocked; five planned sweeps and all three refutation agents did not
run, and the session's 200-query search budget is now spent.

## 2. Data access and licensing (Section 3.2)

| Source | Reached | Licence / terms (evidence) | Human action before Stage 1 |
|---|---|---|---|
| RAM Legacy | blocked (proxy v4.41 extract used) | v4.66 on Zenodo (record 14043031, 2024-11-06), CC BY 4.0 per record metadata seen in search results | download release; freeze DOI/version/checksum; confirm licence text; extract B/BMSY, U/UMSY |
| FishGlob v2.1.0 | yes | CC BY 4.0 (LICENSE file) + citation policy (linked Google Doc, unread) | read the disclaimer; decide on GMEX after audit |
| ICES DATRAS / SAG | blocked | ICES Data Policy; DATRAS open data CC BY 4.0 (snippets) | only for surveys/stocks absent from FishGlob/RAM |
| GPDD v2010 | yes (rgpdd bundle) | package CC0; KNB terms unverified; Reliability: higher = more reliable (IWC summary) | verify KNB licence and the user guide's reliability definitions |
| Living Planet Database | blocked | LPI Data Use Policy: non-commercial free use; substantial-use publications must contact LPI; derived data only passed on under the same terms; confidential records excluded | register, accept terms, record release; confirm that labels/partitions may be published (checkpoint 1) |
| BioTIME 2.0 | blocked | CC BY 4.0 expected (Zenodo 10932823; unverified) | download; check per-study terms |
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
blinded audit protocol and partition-integrity tests. Preliminary pass:
30 of 156 FishGlob series with eligible origins match a RAM v4.41 stock by
species and region (74 candidate pairs); with the full RAM release most long
commercial-species survey series will be dependent on an assessed stock, so
FishGlob and RAM cannot be treated as independent evidence for those species.
GPDD eligible series concentrate in a few data sources, some sit in
multi-MainID groups and 27 pairs of the same taxon lie within 50 km. Species within one FishGlob
survey unit share survey-level shocks; a survey-unit cluster bootstrap is
proposed as a robustness analysis.

## 4. Feasibility census (Section 3.2) — provisional rules, complete windows

| Source | systems with eligible origins | first collapses inside eligible windows | origins (positive / negative) |
|---|---|---|---|
| RAM v4.41 proxy (328 stocks) | 170 | 43 | 3107 (204 / 2903) |
| FishGlob v2.1.0 (screened) | 129 | 22 | 756 (86 / 670) |
| GPDD v2010 (screened) | 38 | 5 | 303 (13 / 290) |
| total accessible now | 337 | 70 | 4166 |

Dominant attrition driver: the 30-observation history minimum. It discards
63 of the 106 proxy fisheries collapses (most occurred inside the first 30
years of the assessment series), reduces FishGlob events from 89 (20-year
minimum) to 22, and GPDD from 16 to 5. A 25-observation minimum (the technical
floor for the provisional 15-year window + 10 trend points) recovers 56
fisheries events and 51 FishGlob events. Second driver: the no-imputation
rule (a complete 24-year window), which halves FishGlob events (42 → 22).
Third: complete 5-year follow-up (the proxy ends 2013–2016; the current RAM
release recovers most). Fourth: survey method changes and unknown effort.
FishGlob events are clustered: half sit in one Gulf of Mexico survey unit with
onsets in 2016–2020, more plausibly a survey-level shift than independent
collapses; they must not enter the confirmatory cohort before the
method-change audit. GPDD's
surviving cohort is 35 bird counts from 12 locations with onsets in 1937–1978.
The lake challenge set offers 7 public lakes with 9–28 annual and 97–332
monthly observations; annual series are far too short for the confirmatory
rules. Projections for blocked sources: RAM v4.66 ≈ 3 × the proxy (≈ 510
eligible stocks, ≈ 130 events; uncertain); LPD and BioTIME unknown (a 400-
system / 32-event placeholder was used in the power scenarios).
Structure of eligible origins: RAM median 10 origins per stock (IQR 5–25);
FishGlob median 4 (3–7); GPDD median 8 (6–12).

## 5. Power and precision gate (Section 3.3) — gate: FAILED on accessible data

Full detail in `reports/stage0_power_analysis.md`; figure
`results/stage0/power_curves.png`. The whole Sections 7–10 procedure was
simulated on census-derived structure (systems, events, origin counts,
clusters, dataset imbalance) with calibrated latent alarm scores, 400
replicates per cell and a 400-draw paired bootstrap.

| data scenario | events | best design | power at +0.10 (Section 10 rule) | power at +0.15 | P(negligible) at 0 | verdict |
|---|---|---|---|---|---|---|
| accessible now (RAM proxy + FishGlob + GPDD) | 70 | grouped cross-fitting | 0.44 | 0.75 | 0.68 | fail |
| accessible now | 70 | locked hold-out, 50 % development | 0.31 | 0.53 | 0.18 | fail |
| RAM ×3 projection alone | 129 | grouped cross-fitting | 0.51 | 0.86 | 0.75 | fail |
| RAM ×3 + FishGlob + GPDD | 156 | grouped cross-fitting | 0.50 | 0.91 | 0.86 | fails at +0.10, passes at +0.15 |
| RAM ×3 + FishGlob + GPDD | 156 | locked hold-out, 50 % | 0.52 | 0.86 | 0.60 | fail |
| + LPD placeholder | 188 | grouped cross-fitting | 0.43 | 0.84 | 0.86 | fails at +0.10, passes at +0.15 |
| pooled projection ×2 | 312 | locked hold-out, 50 % | 0.50 | 0.91 | 0.87 | fails at +0.10, passes at +0.15 |

Two findings dominate. First, the Section 10 rule ("estimate ≥ 0.10 and CI
excludes 0") cannot reach 80 % power at a true +0.10 whatever the sample
size, because the point estimate is below 0.10 half the time when the truth
is 0.10; the gate must be defined at a larger true increment (0.15
recommended) or use a superiority-plus-relevance rule (rule B in the power
report: passes at ≈ 150 events with cross-fitting and ≈ 300 with a 50 %
hold-out, but calls a true +0.05 "meaningful" 20–45 % of the time). Second,
design dominates: 70 % development leaves too few evaluation events for any
conclusion; a 50 % locked hold-out needs ≈ 300 events; grouped cross-fitting
of thresholds over all systems needs ≈ 150 events but must be described as
internally validated (gate alternative 3). The dataset-weighted estimand is
under-powered and mis-calibrated while GPDD contributes 5 events (system
weighting, or a 15-event floor per dataset, is needed). Sensitivities: a less
correlated EWS model (w = 0.6, closer to a real learner) costs about a third
of the power; cluster shocks and cluster bootstrap change little at 4–17
clusters per dataset; the 'run' episode rule gives similar power once its
threshold search maximizes sensitivity under the budget; the simulator
ignores learner estimation error, so all "events needed" figures are lower
bounds. The Section 6.2 window simulation (`ews_window_detectability.csv`)
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

1. RAM Legacy current release: exact stock counts with ≥ 25–35 years of
   biomass, and the number of collapses after 2013 (recovers follow-up).
2. LPD and BioTIME: series lengths, effort constancy, event rates, licence
   consequences for releasing labels; whether LPD populations duplicate GPDD.
3. Whether the GMEX event cluster is real.
4. GPDD Reliability code semantics and the KNB licence.
5. Full-text verification of Zhang 2020, Cano 2025, Pélissié 2026 designs;
   in particular how Zhang operationalized "no regime shift" and whether
   Cano's leave-one-out protocol leaks information across related stocks.
6. The five literature sweeps that did not run (ML/multivariate EWS follow-
   ups, methodological critiques, evaluation methodology, GPDD/LPD/BioTIME
   applications, 2024–2026 recency), plus three novelty-refutation agents.
   One surfaced item needs checking for direct overlap: O'Brien & Clements
   2025 (`lpi-multivariate-res`), which applies multivariate resilience
   methods to Living Planet data.
7. Retrospective bias in assessment series (final vs as-assessed values)
   threatens a strict prequential claim for RAM-derived origins.
8. B2 state-space convergence check not run (would touch real series).
9. The power simulation is a latent-score model: it ignores model-fitting
   variance, dataset-level shocks and the possibility that the EWS block
   interacts with the baseline; a code review of the simulator was requested
   but had not completed at the time of writing.

## 8. Go / no-go recommendation

**No-go for the confirmatory study on the data accessible from this sandbox**
(≈ 340 systems, 70 first collapses): no design, weighting or decision rule
comes close to the Section 3.3 gate, and an imprecise null would not be
interpretable.

**Conditional go, in three steps.**

1. Human acquisition of the blocked sources (RAM Legacy v4.66 from Zenodo,
   Living Planet Database under its data-use agreement, BioTIME 2.0), and a
   re-run of the census scripts with the tightened label rules. The decisive
   numbers are the count of first collapses with a complete 24-year window
   and 5-year follow-up, and how many of them are biologically independent
   after the crosswalk (FishGlob survey series that duplicate RAM stocks do
   not add events; the GMEX cluster must be audited).
2. Design chosen by that count: ≥ 300 independent events → locked 50 %
   hold-out with the Section 10 rule and a 0.15 power target (gate
   alternative 1, the preferred design); 150–300 events → grouped nested
   cross-fitting as the primary analysis with a small single-use lockbox,
   reported as internally validated (gate alternative 3); < 150 events →
   narrow to a fisheries-only, estimation-focused study (gate alternative 2)
   and drop equivalence claims.
3. Stage 1 freezes, with human sign-off: the 25-observation history minimum
   with the 15/10 EWS windows (or 30 with 20/10), the block episode rule, the
   smallest useful effect and power target, system weighting (or a per-dataset
   event floor), and the FishGlob/GPDD screening rules listed in Section 6.

The literature gate is provisionally passed (novel combination; Zhang 2020,
Cano 2025 and Pélissié 2026 must be read in full first). The licensing
position is workable: RAM, FishGlob, ICES and (pending the KNB check) GPDD
allow redistribution of raw values with attribution; LPD raw values cannot be
released and derived labels only under the same terms.
