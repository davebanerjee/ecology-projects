# Stage 0 literature audit (Section 3.1)

Date of searches: 2026-09-08 and 2026-09-09. Engine: the sandbox's WebSearch
tool only. Publisher sites, PubMed/PMC, Crossref, OpenAlex, Semantic Scholar,
Google Scholar, Web of Science, Scopus, Zenodo, Dryad, OSF, arXiv, bioRxiv and
EcoEvoRxiv were all blocked by the sandbox egress policy, so every design detail
below comes from search-result snippets (abstract level) or from the auditor's
prior knowledge, and is labelled accordingly. Full texts of the anchor papers
MUST be read by a human before the positioning statement is used in a
preregistration. Saved queries: `data/metadata/literature_queries.json`
(243 dated queries). Raw structured results of the four completed sweeps
(193 study records): `data/metadata/literature_sweeps_raw.json`.

Coverage achieved: four of nine planned topic sweeps completed (fixed-horizon
prediction and false alarms; out-of-sample/hindcast validation and forecasting
baselines; fisheries collapse prediction; lakes and communities). Five sweeps
(machine-learning and multivariate EWS; methodological critiques; evaluation
methodology; terrestrial GPDD/LPD/BioTIME; 2024–2026 recent work), the twelve
key-paper extractions, the four adversarial novelty refutations and the
synthesis/critic agents did not run because the session's usage limit was
reached twice. Their absence is a known gap (Section 7).

## 1. What the audit found on the novelty question

None of the 193 records describes a study that combines, for population-
abundance collapse, (i) sequential time-indexed forecast origins with fixed
1–5-year labels, (ii) held-out validation across biological systems, (iii) a
capacity-matched state/trend or conventional-forecast baseline, (iv) alarm
thresholds calibrated to a common false-alarm budget, and (v) explicit handling
of right-censored origins. All four sweeps reached this conclusion
independently, with the caveat that snippet-level evidence cannot rule out such
a design inside a paper whose abstract does not mention it. The two records
that most need full-text checking are:

* **Zhang, F. et al. (2020) Early warning signals of population productivity
  regime shifts in global fisheries, Ecological Indicators.** Snippets: SD and
  AR1 evaluated against productivity regime shifts in 191 RAM Legacy
  populations, lead times > 5 years for > 50 % of populations, a positive
  likelihood ratio reported. Whether origins were sequential, whether a
  baseline was used and how false alarms were counted is not visible. This is
  the closest fisheries-wide precedent and was not in the plan's source list.
* **Cano, Jensen & Dakos (2025) PNAS.** Snippets: machine learning on a
  "dynamical footprint" (variance, autocorrelation and other metrics) across
  three global fish datasets (RAM Legacy, ICES cod, FishGlob; one snippet says
  9,006 series) to classify series as abrupt/non-abrupt with "moderate
  accuracy"; PNAS page shows "No data available". This is whole-series
  classification after the fact, not sequential prediction, but its use of
  FishGlob and RAM is the same data base as ours and the paper must be read
  for its train/test design.

Prior work clearly did not ignore false positives or non-transitioning series,
consistent with the plan's stated non-claim: Burthe et al. 2016 (series-level
true/false classifications; true positives in only 8 % of series for variance
and 6 % for autocorrelation; false classifications in all but one series),
O'Brien et al. 2023 (true-negative lake series; most indicators at chance),
Buelo et al. 2022 (true- vs false-positive alarm rates in lake-years),
Litzow et al. 2013 (12 collapsing vs 2 non-collapsing Alaska fisheries),
Drake & Griffen 2010 (30 control populations), Carpenter 2011 / Seekell 2012 /
Batt 2013 (reference lake), Boettiger & Hastings 2012 (ROC; prosecutor's
fallacy).

Sequential, threshold-based alarm evaluation exists but not for population
collapse across systems: Wilkinson et al. 2018 ("quickest detection" in
whole-lake experiments vs a reference lake), Pace et al. 2017 (the only field
study with a preset prospective alarm threshold; n = 1 lake, no forecasting
baseline), and in epidemiology O'Brien & Clements 2021, Brett & Rohani 2020,
Gao et al. 2025 (rolling-origin, out-of-sample detection of outbreaks).

Hefley, Tyre & Blankenship 2013 (bobwhite quail) is the one record pairing an
EWS indicator with a state-space threshold-crossing forecast, but on a single
population and without comparative skill evaluation; it is a precedent for the
B2 comparator rather than for the benchmark.

Verdict (Stage 0, snippet-level evidence): the intended contribution survives
as a novel COMBINATION. It does not survive as "first to score false alarms",
"first to include non-transitioning series", or "first to evaluate EWS on RAM
Legacy at scale" (Zhang 2020, Cano 2025, Pélissié 2026 all precede it there).

## 2. Positioning against the anchor papers (to be verified on full text)

| Paper | What the snippets support | What it does not do relative to our task | Threat to novelty |
|---|---|---|---|
| Burthe et al. 2016 J Appl Ecol | 126 long-term marine and freshwater series, 55 taxa; indicator classifications cross-tabulated against detected nonlinear change; true positives rare; excluded cases near series ends (plan text; not visible in snippets) | no forecast origins, no horizon, no baseline, no out-of-sample fit | low |
| O'Brien et al. 2023 Nat Commun | lake plankton series incl. non-transitioning lakes; classical, multivariate and ML (EWSNet) EWS; chance (0.5) as reference; EWSmethods package | community regime shifts, monthly data; no state/trend baseline; whole-series classification | low (different endpoint) |
| Cano, Jensen & Dakos 2025 PNAS | ML classification of abrupt vs non-abrupt shapes from dynamical-footprint metrics on RAM/ICES/FishGlob series; "moderate accuracy" | retrospective series classification; no sequential origins or false-alarm budget visible; data availability "No data available" | moderate until read |
| Pélissié, Devictor, Jensen & Dakos 2026 Sci Adv (published 2026-09-04; PMC13537261) | 315 stocks since 1950; abrupt productivity shifts in > 25 % of stocks; abrupt declines precede collapse by 10–20 years in 25 % of cases; declines over-represented under larger SST increases | retrospective association of shift timing with later collapse; no origin-wise prediction, baseline or false-alarm accounting visible | moderate until read; supplies the B3 productivity-shift comparator |
| Lapeyrolerie & Boettiger 2023 MEE | deep-learning uncertainty for critical-transition forecasting; MCMC/AR comparators; out-of-sample on simulations | simulations, not empirical collapse | none |
| Zhang et al. 2020 Ecol Indic | SD/AR1 vs productivity regime shifts, 191 RAM populations, lead > 5 y | design not visible | moderate until read |
| Litzow, Mueter & Urban 2013 Ecol Appl | rising catch variability preceded 12 Alaska collapses; 2 non-collapsing contrasts; 1–4-y lead | no origins, baseline, or held-out test | low |
| Ward et al. 2014 Oikos | 49 forecasting models on RAM Legacy and GPDD; naive last-value and low-order AR hardest to beat | not an EWS study | none; supports B1/B2 |
| Hefley et al. 2013 Theor Ecol | EWS + state-space extinction forecast on one quail population | single system | none; supports B2 |

Corrections to the plan's own text surfaced by the sweeps: Gsell et al. 2016
PNAS analysed five freshwater ecosystems (not "nine lakes"); the "nine-lake"
challenge set in the plan corresponds to O'Brien et al. 2023; Pélissié is not
an author of Cano et al. 2025; Litzow et al. 2013 is in Ecological
Applications.

## 3. Design lessons taken from the literature

1. Baselines: naive last-value and low-order autoregressive forecasts are
   hard to beat on RAM/GPDD series (Ward 2014); diffusion-approximation
   quasi-extinction risk has been validated on held-out 10–30-year windows
   (Holmes 2005, 2007); fisheries hindcast cross-validation with tail cutting
   and MASE against a naive forecast is an established convention (HCXval,
   2024 PLOS ONE, authors not visible). B1/B2 should include a naive
   last-value/random-walk risk score and report MASE-style skill.
2. Collapse definitions in use: catch < 10 % of maximum (Worm 2006); biomass
   ≤ 25 % of mean (Essington 2015); < 20 % of maximum observed (Hilborn 2014);
   B_min < 0.2 B_MSY (attributed to Pinsky 2011 in snippets, unverified);
   < 10 % of maximum historical biomass (2024 Science); process-based turnover
   (Yletyinen 2018). The plan's 80 % decline from a trailing-median reference
   sits inside this family; the B/B_MSY < 0.5 sensitivity outcome is standard.
3. Confounds to anticipate in fisheries: fishing-induced age truncation
   raises variability (Hsieh 2006; Anderson 2008); survival variability rises
   at low abundance (Minto 2008); assessment series available at time t differ
   from final series (retrospective bias; 2024 Science "stock assessment
   models overstate sustainability"), which threatens a strict prequential
   claim built on final assessment output and argues for survey-index
   robustness analyses and for stating that assessment-derived origins are
   "as-finally-assessed".
4. Directional caveat: critical speeding up in depensatory stocks (Entropy
   2026 review; Titus & Watson) supports keeping the speeding-up score
   separate and directional.
5. Evaluation precedents for alarm episodes come from epidemiology
   (rolling-origin outbreak detection) and whole-lake quickest detection;
   the seizure-prediction "sensitivity at fixed false-prediction rate" family
   was not reached by the completed sweeps.

## 4. Verification status

* Bibliographic details verified from snippets (high confidence): Burthe
  2016; O'Brien 2023; Cano 2025; Pélissié 2026 (authors, journal, date, PMC
  id); Bury 2021; Litzow 2013; Ward 2014; Holmes 2007; Carpenter 2011;
  Wilkinson 2018; Pace 2017; Boettiger & Hastings 2012 (both papers).
* Partially verified (author lists or venue not visible): Zhang 2020 (first
  author only); the 2024 Science retrospective-bias paper; the 2024 HCXval
  paper; the 2026 Entropy review; the 2026 Nat Ecol Evol nonlinearity paper.
* Not reached: the five missing sweeps' topics (see Section 7).

## 5. Must-read before preregistration (full text)

Burthe 2016 (methods: series-end exclusions, classification rule); O'Brien
2023 (windowing, lake count, ROC supplement); Cano 2025 (train/test design,
footprint metrics, data availability); Pélissié 2026 (shift detector,
collapse definition, lead-time accounting); Zhang 2020; Buelo 2022; Wilkinson
2018; Hefley 2013; Ward 2014; Holmes 2007; the 2024 Science retrospective-bias
paper; Pinsky 2011 / Pinsky & Byler 2015 for collapse definitions.

## 6. Bottom line for the go/no-go

The novelty gate of Section 3.1 is PASSED at the snippet level: no prior
study performs the same time-indexed, baseline-controlled, out-of-sample task.
The contribution statement must be narrowed to the combination and must cite
Zhang 2020, Cano 2025 and Pélissié 2026 as the fisheries-scale precedents.
The gate cannot be called fully passed until the must-read list is checked.

## 7. Known gaps of this audit

Missing sweeps: ML/multivariate EWS follow-ups 2024–2026; methodological
critiques (window/detrending sensitivity, sampling frequency, selection bias);
evaluation methodology (landmark/IPCW, seizure-prediction metrics, equivalence
testing); GPDD/LPD/BioTIME EWS applications; and a dedicated 2024–2026 recency
sweep (the completed sweeps surfaced 2026 items only incidentally: Pélissié
2026, Benerradi/Dakos/Cano 2026, an Entropy 2026 review, a Nature Ecology &
Evolution 2026 nonlinearity paper, a Nature Communications 2026 compound-
climate paper). No refutation agents ran. Re-running those searches from a
machine with publisher access is the first Stage 1 action.
