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

## 1. Literature audit (Section 3.1) — gate: PASSED at snippet level

243 dated WebSearch queries in four completed topic sweeps yielded 193 study
records. No record describes a study that already performs sequential,
fixed-horizon, out-of-sample prediction of population-abundance collapse with a
matched state/trend baseline, a common false-alarm budget and complete
follow-up. The closest precedents, which the manuscript must cite as such, are
Zhang et al. 2020 (Ecological Indicators; SD/AR1 vs productivity regime shifts
in 191 RAM Legacy populations), Cano, Jensen & Dakos 2025 (PNAS; dynamical-
footprint classification on RAM/ICES/FishGlob), Pélissié et al. 2026 (Science
Advances; abrupt productivity declines precede 25 % of collapses by 10–20
years), Burthe et al. 2016 and O'Brien et al. 2023. Prior work did quantify
false positives and include non-transitioning series, as the plan already
concedes. The audit could not open any full text (publisher hosts blocked);
five of nine planned sweeps, the key-paper extractions and the adversarial
refutations did not run because of session usage limits. The gate is passed
provisionally and must be confirmed on full texts (list in the audit report).
Two factual corrections to the plan: Gsell et al. 2016 analysed five
freshwater ecosystems, not nine lakes (the nine-lake set is O'Brien et al.
2023); Pélissié is not an author of Cano et al. 2025.

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

## 5. Power and precision gate (Section 3.3)

[POWER RESULTS PENDING — filled from the corrected grids]

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
* Design and allocation: see Section 5 (pending).
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
5. Full-text verification of Zhang 2020, Cano 2025, Pélissié 2026 designs.
6. The five literature sweeps that did not run (ML/multivariate EWS follow-
   ups, methodological critiques, evaluation methodology, GPDD/LPD/BioTIME
   applications, 2024–2026 recency).
7. Retrospective bias in assessment series (final vs as-assessed values)
   threatens a strict prequential claim for RAM-derived origins.
8. B2 state-space convergence check not run (would touch real series).
9. The power simulation is a latent-score model: it ignores model-fitting
   variance, dataset-level shocks and the possibility that the EWS block
   interacts with the baseline; a code review of the simulator was requested
   but had not completed at the time of writing.

## 8. Go / no-go recommendation

[PENDING — filled from the corrected grids]
