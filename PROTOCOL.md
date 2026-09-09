# PROTOCOL (DRAFT — Version 2.0, 8 September 2026 — NOT FROZEN)

This file carries the revised research plan (Part II of the red-team review,
Version 2.0) that Stage 0 was executed against. Section numbers cited in
`reports/` refer to this document. Nothing in it is frozen: Stage 1 will freeze
the outcome, cohort, horizon, predictors, learners, weighting, smallest useful
effect, alarm definition, split and code skeleton, and post the protocol to OSF.
Stage 0 proposals and clarifications are recorded in `reports/STAGE0_REPORT.md`
and `CHANGELOG.md`, not here.

## 0. Title and study type

Working title: Do generic early-warning signals add useful predictive information about ecological population collapse? A preregistered prequential benchmark.

Retrospective forecast emulation using historical ecological monitoring data. At each forecast origin t, every predictor is reconstructed using only observations available at t. Models are developed without access to a locked evaluation set and evaluated on prespecified future horizons. The study does not call itself prospectively validated.

## 1. Primary question

Among regularly monitored ecological populations, does a prespecified classical EWS score increase the fraction of first collapses detected one to five years in advance, relative to a conventional state-and-trend forecasting model, when each model's alarm threshold is calibrated in development data to the same false-alarm target?

Secondary: (1) DEV, multivariate EWS, simulation-trained classifiers vs classical variance/AR1 trends; (2) flexible learner with vs without EWS block; (3) moderation by monitoring length, observation process, taxon, realm, annotated mechanism; (4) transfer across data sources.

## 2. Scope

2.1 Confirmatory: univariate population-abundance or biomass series supporting a common outcome (large, persistent decline relative to an historical reference). Realms pooled only after dataset-specific estimates and under the Section 9 weighting rule.
2.2 Separate challenge analyses: lake/community regime shifts (nine-lake / O'Brien datasets with fixed published classifications); monthly analyses. Out of scope: recovery, repeated collapses, spatial EWS, causal identification of mechanisms.

## 3. Stage 0

May inspect metadata, series lengths, observation schedules, outcome labels, event counts. May not compute EWS features or predictor–outcome associations.
3.1 Literature audit (dated saved queries; position against Burthe et al. 2016, O'Brien et al. 2023, Cano et al. 2025, Pélissié et al. 2026; stop if the same time-indexed, baseline-controlled, out-of-sample task already exists).
3.2 Feasibility census per source: unique systems after deduplication; frequency, duration, gaps, method changes; qualifying events and eligible origins with complete 1–5-year follow-up; events/systems per partition; overlap; licences; availability of effort, observation-error, driver and reference-point data.
3.3 Power and precision gate: simulate the entire split-and-evaluation procedure; pass only with ≥ 80 % power for the smallest useful effect and ≥ 80 % probability of correctly classifying a negligible effect. Provisional smallest useful effect: +10 percentage points event sensitivity at ≤ 1 false-alarm episode per 20 monitored population-years. If the gate fails: acquire more events; narrow to fisheries; or run repeated nested CV described as internally validated.

## 4. Data sources and biological independence

4.1 RAM Legacy; FishGlob and eligible ICES surveys; GPDD; Living Planet Database public release (after human acceptance of terms); BioTIME 2.0 (constant-effort species × site series); lake/community challenge data. Exact versions frozen in a manifest.
4.2 Canonical `system_id`; linked records stay in one partition; blinded manual audit before feature computation.
4.3 Primary inclusion: annual(ized) abundance on a consistent scale; ≥ 30 observations before the first eligible origin; ≥ 5 years follow-up after a negative origin; no documented method/footprint/catchability/resolution/model change within the feature window unless harmonized; no imputation (complete regular windows; state-space gap handling is a sensitivity); known or stable effort for counts; ≥ 5 positive annual observations before the running reference.

## 5. Outcome and risk sets

5.1 R_i(s) = max_{u ≤ s−1} median(x_{i,u−4..u}); first onset C_i = first s with x_s and x_{s+1} below 0.20·R_i(s). Sensitivity outcomes: 90 % decline; 3-year persistence; best historical 10-year reference; B/B_MSY < 0.5 for two years. Abruptness classification after labels are frozen only.
5.2 At every eligible annual origin t < C_i, predictors use x_{1:t}; Y_{i,t} = 1 if C_i ∈ {t+1..t+5}; negatives only with ascertainable outcome through t+5; censor at and after first collapse; 1–3 and 6–10-year horizons secondary; IPCW sensitivity.

## 6. Predictors

6.1 B0 prevalence; B1 state and trend (relative abundance, distance to threshold, 5- and 10-year slopes, recent mean, history length, quality indicator); B2 local-linear state-space threshold-crossing probability (ARIMA/ETS fallback if convergence fails, chosen in Stage 0); B3 fisheries comparators (B/B_MSY, U/U_MSY, sequential productivity-shift signal). Primary comparator B1 + B2.
6.2 Classical EWS: directional trends (Kendall tau) of lag-1 autocorrelation and log variance in fixed-duration trailing windows, averaged with equal weights after outcome-blinded scaling; provisional 15-year indicator window, last 10 indicator estimates, ≥ 24 pre-origin observations; window durations chosen in Stage 0 from sampling-frequency/detectability simulations only. Critical speeding up is a separate directional secondary score.
6.3 Secondary EWS: SD/CV, skewness, return rate, spectral reddening, composites; expanding-window; DEV; multivariate (≥ 3 synchronous related series); pretrained Bury and EWSNet classifiers after an input-compatibility audit.
6.4 Learned model: two gradient-boosted models with identical budgets, baseline vs baseline + frozen EWS block.

## 7. Partitioning

By `system_id`; development set with nested grouped CV; calibration set or cross-fitted predictions for the alarm threshold; locked evaluation set used once; allocation from the Stage 0 power analysis; stratification by dataset, event, record length, data type (never EWS values); leave-one-dataset-out transportability; calendar splits only when histories do not overlap.

## 8. Fair comparisons

Paired predictions on identical origins: regularized logistic/discrete-time hazard (baseline vs + primary EWS); gradient boosting (baseline vs + EWS block, identical search budgets); fisheries-only domain baseline vs + EWS.

## 9. Evaluation

9.1 Alarm episodes (consecutive alarmed years; five-year refractory window); true if a first collapse begins 1–5 years after episode start. Thresholds chosen on development data for ≤ 1 false-alarm episode per 20 non-event population-years, then frozen. Primary estimand: paired increase in event sensitivity; report realized false-alarm burden; non-inferiority margin on false alarms frozen in Stage 1; normalized partial area under the sensitivity–false-alarm curve. Equal weight per dataset for the primary pooled estimate; population-year- and system-weighted estimates also reported.
9.2 Secondary: time-dependent AUROC/AUPRC at 5 years; Brier and calibration; lead time; false alarms per system and per 20 non-event years; decision-curve net benefit; per-dataset and leave-one-dataset-out results. Paired CIs by resampling systems within dataset.

## 10. Hypotheses and decision rules

H1 classical EWS incremental value; H2a learned EWS block; H2b pretrained classifiers (hierarchical order H2a then H2b). H1 classified as meaningful benefit (estimate ≥ smallest useful effect and 95 % CI excludes zero), negligible (upper bound below the smallest useful effect), harm (upper bound below zero), or inconclusive. Moderation analyses exploratory unless Stage 0 establishes stratum-specific power and an external annotation protocol.

## 11–13. Mechanism and observation-process analyses; simulation and falsification suite; robustness analyses

As in the Version 2.0 document (blinded external mechanism annotation; observation processes never pooled as equivalent; simulations with fold/transcritical/Hopf/Allee transitions, smooth declines, step changes, coloured noise, variance changes, effort changes, zero inflation, mixtures; negative controls with permutation at system level; robustness to thresholds, persistence, horizons, gap handling, survey-only, no assessment biomass, no zero-inflated series, leave-one-dataset-out, weightings, uncertain duplicates, alternative EWS windows, fisheries comparators).

## 14. Reproducibility

Repository layout as implemented; required tests (no future index; no unascertained negatives; one onset per series; linked systems never cross partitions; fold-internal scaling/selection/tuning; reference-value agreement within tolerance; shuffled-label and synthetic-null tests; clean-environment reproduction within declared tolerances); locked environments, seeds, workflow manager; human review for exclusions, identity matching, licences, annotations, claims.

## 15. Stages and gates

Stage 0 literature/feasibility/deduplication/power (this repository state). Stage 1 protocol freeze and preregistration. Stage 2 pipeline and simulation validation. Stage 3 development only. Stage 4 frozen evaluation. Stage 5 prespecified robustness and exploratory moderation. Stage 6 manuscript and benchmark release.

## 16–19. Narratives, human checkpoints, bottom line, key sources

Human approval required before: accepting restricted data terms; finalizing the crosswalk and manual exclusions; choosing the smallest useful effect and any Stage 0 change to the provisional outcome; posting the preregistration; opening or scoring the locked set; changing any frozen analysis; releasing data or assigning authorship.

Key sources: Burthe et al. 2016 J Appl Ecol 53:666–676 (10.1111/1365-2664.12519); O'Brien et al. 2023 Nat Commun 14:7942 (10.1038/s41467-023-43744-8); Cano, Jensen & Dakos 2025 PNAS 122:e2505461122; Pélissié, Devictor, Jensen & Dakos 2026 Sci Adv 12 (10.1126/sciadv.aed7911); Lapeyrolerie & Boettiger 2023 MEE (10.1111/2041-210X.14013).
