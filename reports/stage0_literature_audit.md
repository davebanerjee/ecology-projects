# Stage 0 literature audit (Section 3.1)

Searches: 2026-09-08 to 2026-09-15. Engine: the sandbox's WebSearch tool.
Publisher sites, PubMed/PMC, Crossref, OpenAlex, Semantic Scholar, Google
Scholar, Web of Science, Scopus, Zenodo, Dryad, OSF, arXiv and bioRxiv were
blocked by the egress policy throughout, so no full text was read; details
below come from search-result snippets, from authors' public code
repositories, and (for two papers) from author-hosted PDFs on
raw.githubusercontent.com. Saved queries:
`data/metadata/literature_queries.json` (896 query strings executed, 878
unique, of which 21 are GitHub repository or code searches rather than web
searches; 31 submitted after the session's 200-query budget was exhausted
and refused; the budget was exhausted on 2026-09-10, 2026-09-12 and
2026-09-14). Raw structured outputs: `data/metadata/literature_sweeps_raw.json`
(thirteen sweep agents, including four GitHub-only supplements; 569 study
records, 339 unique by DOI or citation prefix, and about 411 unique after
manual merging of citation variants), `data/metadata/literature_keypapers_raw.json`
(eight anchor-paper design extractions), `data/metadata/literature_refutations_raw.json`
(angles A and B, and the three lenses plus adjudication of angle D),
`data/metadata/literature_synthesis_raw.json` (the synthesis agent's
structured output, Section 15) and `data/metadata/data_content_checks_raw.json`
(the three data-content checks, Section 16).

Coverage achieved: all nine planned topic sweeps (fixed-horizon prediction
and false alarms; out-of-sample validation and forecasting baselines;
fisheries collapse prediction; lakes and communities; machine-learning and
multivariate EWS; methodological critiques; evaluation methodology;
GPDD/LPD/BioTIME applications; 2024-2026 recency), four GitHub-only
supplements, eight anchor-paper extractions and two of three adversarial
refutations (fisheries angle; machine-learning benchmark angle). The
refutations ran after the search budget was spent and therefore mined the
saved sweep records and live GitHub searches rather than fresh web queries.
Not completed: the third refutation (recent and forthcoming work), three
data-content checks, and the automated synthesis and critique; this document
is the synthesis.

## 1. Novelty verdict

The intended contribution survives as a novel COMBINATION, but the margin is
narrower than a first pass suggested, and three fisheries papers now have to
be positioned explicitly rather than merely cited.

What we can claim: no study found performs sequential, fixed-horizon
prediction of first population-abundance collapse in which (i) every
predictor at origin t uses only data available by t, (ii) alarm thresholds
are calibrated in development data to a common false-alarm budget, (iii) a
matched state-and-trend or conventional-forecast baseline is scored on the
same origins, and (iv) negatives require complete outcome ascertainment
through the horizon.

What we must NOT claim: that prior work ignored false positives, ignored
non-transitioning series, lacked out-of-sample validation, or had not applied
autocorrelation- and variance-type indicators to RAM Legacy or FishGlob at
scale. Each of those has been done.

## 2. The three fisheries precedents

**Zhang, F. (2020). Early warning signals of population productivity regime
shifts in global fisheries. Ecological Indicators 115: 106371.** Verified from
abstract snippets: standard deviation and lag-1 autocorrelation evaluated for
predicting observed productivity regime shifts in 191 RAM Legacy populations;
a positive likelihood ratio is reported, which requires a false-positive rate,
and the paper explicitly asks whether the indicators are absent when there is
no shift; standard deviation outperformed autocorrelation on the likelihood
ratio; the two indicators agreed on fewer than half the shifts; more than five
years of warning for more than half the populations, longer in rockfish. Not
visible: forecast origins, any train/test split, any non-EWS comparator, and
how "no regime shift" was operationalized. Outcome is a productivity regime
shift, not a first abundance collapse. Threat to novelty: moderate. This paper
was absent from the plan's source list and is the closest RAM Legacy
precedent for the primary indicators.

**Cano, A. V., Jensen, O. P. & Dakos, V. (2025). PNAS 122: e2505461122.**
Verified: each series is classified by AICc into no-change, linear, quadratic
or abrupt, with `asdetect` confirmation; a "dynamical footprint" of seven
stability metrics (dominant eigenvalue from an S-map Jacobian, lag-1
autocorrelation, standard deviation, coefficient of variation, disparity,
dispersion, skewness) is computed both over the whole series and as a Kendall
tau trend using a rolling window of 50 % of series length; boosted regression
trees predict the class; **leave-one-out cross-validation across series gives
AUC 0.84 for RAM Legacy, 0.75 for ICES cod and 0.65 for FishGlob**; minimum
series length 20 years; abrupt-class sensitivity as low as 40 % in FishGlob.
Two features matter for us. First, this is genuinely out-of-sample across
series, which corrects an earlier reading of this audit. Second, and more
usefully, **non-abrupt series that the model predicts as abrupt are not
counted as false alarms but relabelled as populations "at risk" of future
shifts**, with no follow-up window and no later verification. That is exactly
the accounting our design replaces with a false-alarm budget, and it is a
precise, citable statement of what our benchmark adds. Threat: low, provided
we never claim to be first to apply these metrics to RAM Legacy or FishGlob.

**Pélissié, M., Devictor, V., Jensen, O. P. & Dakos, V. (2026). Science
Advances 12, doi:10.1126/sciadv.aed7911.** Verified: surplus-production
("productivity") trajectories of 315 assessed stocks classified by AICc into
four types with an independent breakpoint method for validation; productivity
abrupt shifts detected in more than a quarter of stocks; abrupt declines
overrepresented where warming has been fastest, abrupt increases under lower
fishing intensity. Critically for us, the paper quantifies its own false
alarms: **negative productivity shifts occurred in 23 % of collapsed stocks
and 12 % of non-collapsed stocks, and only 11 of 42 stocks (26 %) with a
negative shift went on to collapse**, with most shifts 4 to 12 years before
collapse. Collapse-threshold sensitivity used 10 % of maximum biomass and
15 %, 25 % and 50 % of average biomass. No forecast origins, no baseline, no
held-out evaluation. Threat: moderate, because it is the nearest neighbour on
data source, outcome and framing, and it was promoted publicly as a warning
system with roughly a decade of lead time. Our design's answer is that a
signal with a 26 % positive predictive value and no comparator is precisely
what an operating-point analysis is for.

## 3. The other anchor papers

| Paper | Verified design | Relative to our task | Threat |
|---|---|---|---|
| Burthe et al. 2016, J Appl Ecol 53:666-676 | 126 abundance datasets, 55 taxa, six aquatic systems (shallow lake, deep lake, coastal marine), all trophic levels; each series standardized by a GAM before turning-point detection; true positives, false negatives and false positives counted with a 10-year association window; false positives more prevalent than false negatives; variance and autocorrelation classified 43 % of series differently | retrospective whole-series classification; no forecast origins, no horizon, no baseline, no held-out fit | low |
| O'Brien et al. 2023, Nat Commun 14:7942 | nine lakes; rolling and expanding windows; classical univariate, multivariate and EWSNet indicators; Bayesian binomial models against a 0.5 chance reference; true-positive and true-negative rates reported separately (unscaled EWSNet: TP 0.93 monthly / 0.89 yearly but TN 0.19 / 0.05) | community regime shifts, not first population collapse; binary per-series fate; no fixed horizon, no lead-time analysis, no state/trend baseline | low |
| Bury et al. 2021, PNAS 118:e2106140118 | classifier trained on synthetic bifurcation libraries with a train/validation/test split, applied at sequential origins incremented by 10 points; null simulations and quasi-static segments as negatives; ROC/AUC against Kendall tau of rolling variance and autocorrelation; "early" and "late" relative windows rather than fixed horizons | no population-abundance data at all (empirical tests are thermoacoustic, paleoclimate and sediment records) | low |
| Ward et al. 2014, Oikos 123:652-661 | 2379 vertebrate population index series; models fit to all but the last five observations; 1-5 step-ahead forecasts scored by MASE against a random walk without drift (last observed value) as the explicit baseline; 49 model variants | no event outcome, no alarms, no calibration; a single hold-out origin per series | low; strongest precedent for our baseline |
| Lapeyrolerie & Boettiger 2023, MEE | simulation only (Nicholson-Bailey, May); probabilistic forecasts bracketed between MCMC given the true generative model (upper bound) and ARIMA (lower bound); no alarms, no thresholds, no false-alarm rate | no empirical data, no event outcome, no EWS predictor | low |

Corrections to the plan's own text, from the sweeps: Gsell et al. 2016 (PNAS)
analysed five freshwater ecosystems, not nine lakes; the nine-lake set is
O'Brien et al. 2023. Pélissié is not an author of Cano et al. 2025. Litzow
et al. 2013 is in Ecological Applications.

## 4. Design lessons adopted

1. **Add a random-walk baseline.** Ward et al. 2014 showed on 2379 vertebrate
   series that a random walk without drift (the last observed value) is the
   benchmark simple forecasts must beat, and that added model complexity
   usually cost accuracy at 1-5 year horizons. B1 should therefore include a
   last-value risk score, and skill should be reported in MASE-like terms
   alongside the alarm metrics.
2. **Bracket the conventional forecast.** Lapeyrolerie & Boettiger's
   upper-bound (correct model, MCMC) and lower-bound (ARIMA) framing is the
   right way to present B2: the state-space threshold-crossing probability is
   an achievable middle, not an oracle.
3. **Count false alarms as false alarms.** Cano et al. relabel predicted-abrupt
   non-abrupt series as "at risk"; Pélissié et al. report that 74 % of
   negative productivity shifts were not followed by collapse. Our episode
   accounting with a frozen budget is the direct remedy, and both papers give
   us the numbers to motivate it.
4. **Collapse-definition family.** Verified thresholds in use: 10 % of maximum
   biomass and 15 / 25 / 50 % of average biomass (Pélissié 2026); catch below
   10 % of maximum (Worm 2006); biomass at or below 25 % of the mean
   (Essington 2015); below 20 % of maximum observed (Hilborn 2014). Our 80 %
   decline from a trailing-median reference sits inside this family; the
   Pélissié thresholds should join the Section 5.1 sensitivity list.
5. **Association windows are the retrospective analogue of our horizon.**
   Burthe's 10-year window and Pélissié's 4-12 year observed lead distribution
   bracket our 1-5 year primary horizon and support reporting 6-10 years as a
   secondary.
6. **Directional caveat.** Critical speeding up in depensatory stocks
   (Entropy 2026 review) supports keeping that score separate and directional.
7. **Retrospective bias.** A 2024 Science paper (authors not visible) reports
   that assessment models overstate sustainability, implying the series
   available at time t differs from the final series. RAM-derived origins are
   therefore "as finally assessed", which must be stated, and survey-index
   robustness analyses matter more because of it.

## 5. Prior work that did quantify false positives

Burthe et al. 2016 (explicit TP/FN/FP tally; FP more common than FN);
O'Brien et al. 2023 (true-negative rates in non-transitioning lakes, most
indicators near chance); Zhang et al. 2020 (positive likelihood ratio);
Pélissié et al. 2026 (26 % positive predictive value); Buelo et al. 2022
(true- versus false-positive alarm rates in lake-years); Litzow et al. 2013
(two non-collapsing contrast fisheries); Drake & Griffen 2010 (30 control
populations); Carpenter 2011, Seekell 2012, Batt 2013 (reference lake);
Bury et al. 2021 and the measles-EWS work (null simulations as negatives);
Boettiger & Hastings 2012 (ROC; the prosecutor's fallacy). Sequential,
threshold-based alarms exist in whole-lake experiments (Wilkinson et al. 2018
quickest detection; Pace et al. 2017, the one field study with a preset
prospective threshold, n = 1 lake) and in epidemiology (O'Brien & Clements
2021; Brett & Rohani 2020; Harris et al. 2020, a rolling forecast on a single
malaria series; Gao et al. 2025).

## 6. Must-read in full before preregistration

Zhang 2020 (design, false-alarm operationalization); Cano 2025 (BRT features,
LOO-CV protocol, relabelling rule); Pélissié 2026 (shift detector, collapse
definition, lead-time accounting); Burthe 2016 (turning-point rule, series-end
handling); O'Brien 2023 (windowing, thresholds); Buelo 2022; Wilkinson 2018;
Hefley 2013; Ward 2014 (already read via the authors' PDF); the 2024 Science
retrospective-bias paper; Pinsky 2011 and Pinsky & Byler 2015 for collapse
definitions.

## 7. Living Planet Database precedents (checked 2026-09-12)

Three items were checked directly because they could overlap with the
terrestrial component or supply annotations.

* **Capdevila, Noviello, McRae, Freeman & Clements (2022). Global patterns of
  resilience decline in vertebrate populations. Ecology Letters 25: 240-251.**
  Resilience (resistance and recovery, estimated from changes in the
  population growth rate) computed for Living Planet Database vertebrate time
  series; resilience is declining worldwide and faster under multiple
  threats. A resilience-indicator trend analysis at LPD scale, not a
  collapse-prediction benchmark; no forecast origins, alarms or baselines are
  visible. Threat to novelty: low. It establishes that LPD-scale
  resilience analyses exist and must be cited in the terrestrial positioning.
* **Capdevila, O'Brien, Marconi, Johnson, Freeman, McRae & Clements (2026).
  Halting predicted vertebrate declines requires tackling multiple drivers of
  biodiversity loss. Science Advances 12(7): eadx7973 (bioRxiv
  2025.01.02.630023; code at duncanobrien/multiple-threats, Zenodo 18775663).**
  3129 LPD vertebrate population time series with documented exposure to
  single and multiple threats; populations under disease, invasive species,
  pollution and climate change decline faster than those under habitat loss
  or exploitation alone; counterfactual analyses of threat mitigation. A
  threat-attribution and trend study, not an early-warning benchmark. Threat
  to novelty: none. Its value for us is different: the per-population threat
  annotations are exactly the kind of external, outcome-blind annotation the
  Section 11 mechanism analysis needs, and the code repository is public.
* **Smith, Morr, Schötz & Boers (2026). Estimating the resilience of
  non-stationary systems. arXiv:2604.24345 (submitted 2026-04-27).** A
  regression-based Langevin formulation of critical slowing down that is
  robust to gaps and irregular sampling and returns uncertainty bounds.
  Relevant as a candidate for the Section 13 gap-handling sensitivity
  analysis, since our primary cohort requires complete windows and loses
  half of the FishGlob events to that rule.

The `lpi-multivariate-res` repository (O'Brien & Clements 2025) surfaced by
the GitHub-only sweep did not appear in any search result and remains
unverified; it should be inspected directly before preregistration.

## 8. Machine-learning and multivariate early-warning signals (sweep of 48 queries, 37 records)

No search result showed a pretrained deep-learning classifier (Bury et al.
2021 and 2023, EWSNet, TipPFN, SDML) evaluated on population-abundance
collapse in RAM Legacy, GPDD, the Living Planet Database or BioTIME with
sequential origins, a fixed calendar horizon and complete follow-up; targeted
queries for such applications returned nothing. The closest empirical test
remains O'Brien et al. 2023 on lake communities (EWSNet true-negative rates
0.05-0.20; multivariate indicators only weakly better than univariate).
False positives are quantified in several machine-learning papers (Bury 2021
ROC against AR(1) nulls; Bury 2023 and Ma et al. 2025 sensitivity and
specificity; Falmagne, Stephenson & Levin 2026: half of transitions detected
at a 3.6 % false-positive rate with a held-out year; Masuda 2026: low
false-positive rates from sequential adjudication of variance growth), so
the preregistration must not claim that machine-learning EWS work ignored
false alarms. None of the visible results used a state-and-trend forecasting
baseline; comparators were classical indicators, surrogate nulls, chance, or
other learners.

Items that change the protocol:

* **Dablander & Bury (2022, PNAS letter)**: the Bury et al. 2021 classifier
  learned features of the detrending filter applied to its training set. The
  Section 6.3 input-compatibility audit must therefore reproduce each
  classifier's documented preprocessing exactly, and preprocessing must be
  frozen before any classifier is applied.
* **Masuda (2026, PNAS Nexus 5: pgag126, "TIPMOC")**: a sequential
  variance-only test that adjudicates between linear and power-law variance
  divergence, robust to uneven sampling and coloured noise. This is a
  candidate secondary EWS for Section 6.3 and one of the few sequential
  methods with an explicit false-positive rate.
* **Huang et al. (2024, Nature Machine Intelligence)** and **Arumugam,
  Guichard & Lutscher (2024)**: rate-induced tipping, where critical slowing
  down is not expected; the Section 12 falsification suite should include
  rate-induced transitions alongside bifurcations.
* **Sevinchan et al. (2026, TipPFN preprint)**: argues that existing deep
  classifiers do not extrapolate beyond their training regimes; supports
  treating H2b as a hierarchically gated secondary hypothesis.
* Weinans et al. 2021 (Scientific Reports) remains the reference evaluation
  of multivariate indicators; Grziwotz et al. 2023 (DEV) and Kulkarni, Deb &
  Dutta 2024 are the DEV sources for Section 6.3.

## 9. Methodological critiques (sweep of 36 executed queries, 40 records)

The critique literature converges on five constraints that the protocol
already anticipates and should now cite explicitly.

1. **Selection bias.** Boettiger & Hastings (2012, Proc R Soc B, "the
   prosecutor's fallacy") distinguish selecting systems because they
   transitioned from forecasting for systems one wishes to monitor; Gsell et
   al. 2016 chose five systems because they transitioned; the Entropy 2026
   review names conditional sampling bias directly. Our risk-set design and
   the inclusion of all monitored systems are the answer, and the manuscript
   should say so in these terms.
2. **Detection limits and error rates.** Boettiger & Hastings (2012, J R Soc
   Interface) frame evaluation as false alarms versus missed warnings and
   show error rates "can be quite severe for common indicators even under
   favorable assumptions"; Perretti & Munch (2012) show failure at
   ecological noise levels; Clements et al. (2015) show subsampling muffles
   or magnifies signals; Arkilanian et al. (2020) suggest a minimum of
   roughly 5-10 generations of data. These bound expectations for the
   effect size and justify the smallest-useful-effect framing.
3. **No warning for some transitions.** Hastings & Wysham (2010); Boettiger &
   Hastings (2013, large-deviation theory: conditioning on a stochastic
   transition can mimic an early warning); van der Bolt, van Nes & Scheffer
   (2021, J R Soc Interface: records must be long enough to capture the
   response rate, and drivers must change slowly); the 2025 Scientific
   Reports paper on rapidly changing parameters (warnings arrive after the
   bifurcation). These are the null data-generating processes for Section 12.
4. **Non-specificity and false positives.** Kéfi et al. (2013): critical
   slowing down precedes non-catastrophic transitions too; Jäger & Füllsack
   (2019): whole classes of systems always show warnings without
   transitions; Wagner & Eisenman (2015): autocorrelation rose while variance
   fell in a model with no bifurcation; Titus & Watson (2020): critical
   speeding up. These justify the directional, separate speeding-up score
   and the coloured-noise and variance-change nulls.
5. **Window, detrending and missing-data sensitivity.** Dakos et al. (2012)
   and Lenton et al. (2012) document dependence on window width, bandwidth
   and aggregation; a 2026 Science Advances paper (Beijing Normal
   University, TU Munich and PIK; authors not visible) shows that the
   agreement between variance- and autocorrelation-based indicators is
   driven by the series' initial data point and is weakened substantially by
   missing values. The last result bears directly on our complete-window
   rule and on the choice of a mean-removal transform (Section 6.2 window
   simulation), and must be read in full.

Also relevant: Ben-Yami et al. (2024) and Rietkerk et al. (2025) on the
ambiguity of climate tipping warnings; Litzow & Hunsicker (2016) on testing
for nonlinearity before trusting a warning; Dakos et al. (2024, Earth System
Dynamics) for the taxonomy of warnings that do and do not rely on critical
slowing down.

## 10. Evaluation methodology to borrow (sweep of 54 queries, 59 records)

The protocol's evaluation design has direct precedents outside ecology that
should be cited and, where possible, reused rather than reinvented.

* **Sequential fixed-horizon labels.** Landmarking (van Houwelingen 2007,
  Scand J Stat) fits at each landmark time to the individuals still at risk
  using only information observed by then, over a horizon window of fixed
  length after the landmark; the discrete-time person-period formulation
  (Suresh, Severn & Ghosh 2022, BMC Med Res Methodol) is the tabular form our
  origin × label table already takes. A review of horizon definitions
  (PMC13182843) distinguishes fixed-length windows after the landmark from
  fixed calendar horizons; ours is the former and should say so.
* **Censoring, if any origins are retained with incomplete follow-up.**
  Inverse-probability-of-censoring-weighted time-dependent AUC and Brier
  scores (Heagerty, Lumley & Pepe 2000; Uno et al. 2007; Graf et al. 1999;
  Blanche, Dartigues & Jacqmin-Gadda 2013; Blanche et al. 2015 for landmark
  AUC(s,t) with paired comparison tests). The complete-case primary analysis
  avoids these; the IPCW sensitivity should use Blanche et al. 2015.
* **Alarm-episode metrics.** The seizure-prediction literature defines the
  quantities we need: occurrence period, prediction horizon, sensitivity at a
  fixed false-prediction rate, and the "seizure prediction characteristic"
  (Winterhalder et al. 2003); event-time surrogates as the chance null
  (Andrzejak et al. 2003; Schelter et al. 2006); the expected performance of
  a chance predictor under the scoring rule as the control in a hypothesis
  test (Snyder et al. 2008); and the cautionary history in which optimistic
  results were not reproduced under rigorous evaluation (Mormann et al.
  2007). Andrzejak et al. (2026, Epilepsia) warn that "better than chance"
  is underspecified unless the null is stated; our permutation null at the
  system level answers that. Clinical early-warning-score work supplies the
  episode-aware framework (Scully & Daluwatte 2017; Gadhoumi et al. 2021),
  alarm burden per unit time, and the argument that the C-statistic misleads
  when events are rare (Romero-Brufau et al. 2015: prevalence 0.02 per
  patient-day). Operational warning verification uses the 2 × 2 event table
  with probability of detection, false-alarm ratio and lead time (Wilks
  2011; NOAA NWS materials); quickest-detection theory controls false alarms
  through the average run length (Mei 2008).
* **Calibration and decision value.** Calibration hierarchy and
  intercept/slope reporting (Van Calster et al. 2016, 2019); decision-curve
  net benefit with confidence intervals (Vickers & Elkin 2006; Vickers et al.
  2023); minimum sample sizes for external validation targeting the
  calibration slope, C-statistic and net benefit (Riley et al. 2021), which
  should be run alongside the Stage 0 simulation as a check.
* **Paired comparisons and increments.** Pepe et al. (2013) prove that
  testing for improvement in AUC from an added predictor is equivalent to
  testing that predictor's coefficient, so a likelihood-ratio test on the
  development set is not evidence of out-of-sample improvement (as the
  protocol already states); DeLong et al. (1988) and Obuchowski (1997, for
  clustered data) for paired AUC differences; LeDell, Petersen & van der
  Laan (2015) for cross-validated AUC intervals; two one-sided tests against
  a smallest effect size of interest (Lakens 2017; Riesthuis 2024 for
  simulation-based power with a confidence-interval approach) and paired
  non-inferiority tests for diagnostic accuracy.
* **Prequential evaluation and leakage.** Dawid (1984) and Gneiting et al.
  (2007) for the prequential principle; Bergmeir & Benítez (2012) for
  rolling-origin evaluation; Roberts et al. (2017) for blocked
  cross-validation under temporal, spatial and hierarchical structure;
  Takada et al. (2021) for internal-external cross-validation, which is our
  leave-one-dataset-out analysis under its established name; Kapoor &
  Narayanan (2023) for the leakage taxonomy the Section 14 tests should map
  onto.

## 11. Terrestrial and freshwater population applications (sweep of 72 queries, 51 records)

No study was visible that applies classical EWS across GPDD, the Living
Planet Database or BioTIME at scale with sequential out-of-sample evaluation
against matched baselines; BioTIME with EWS returned nothing. The visible
wild-population tests are single systems or small sets: Hefley et al. 2013
(bobwhite quail, threshold-crossing forecast plus an indicator); Krkošek &
Drake 2014 (120 salmon stocks; increased variability and autocorrelation in
pink salmon stocks with growth parameters near zero); Rozek, Camp & Reed
2017 (no critical slowing down in two endangered Hawaiian honeycreepers,
with the remark that EWS methods are rarely applied to population-size data
from wild populations); Burant et al. 2021 (seasonal timing of the stressor
changes detectability). The experimental lineage (Drake & Griffen 2010; Dai
et al. 2012, 2013, 2015; Clements & Ozgul 2016; Baruah et al. 2019, 2020,
2022; Arkilanian et al. 2020; Cerini et al. 2025) establishes detectability
under controlled forcing, the value of trait information, and a minimum of
roughly 5-10 generations of data.

Facts that bear on the census and the outcome definition:

* Reed et al. (2003): severe die-offs occur at roughly 14 % per generation
  in vertebrate populations and their frequency scales with generation
  length; Anderson et al. (2017, PNAS): black-swan events are mainly crashes
  (86 %) and heavy-tailed process noise is common. Both imply that a
  fraction of first collapses will be genuinely unforecastable shocks, which
  bounds achievable sensitivity and belongs in the falsification suite.
* Leung et al. (2020, Nature): the Living Planet Index decline is driven by
  fewer than 3 % of populations, with clusters of extreme decline in 16
  systems; Daskalova, Myers-Smith & Godlee (2020): 15 % of LPD populations
  declined, 18 % increased, 67 % showed no net change. The LPD event rate for
  an 80 % decline is therefore likely to be low and clustered, consistent
  with the small placeholder used in the power scenarios.
* Buschke et al. (2021) and Wauchope et al. (2019): random fluctuations
  bias index-based trend estimates and short series mislead; both argue for
  the complete-window and minimum-history rules.
* Holmes et al. (2007): quasi-extinction forecasts from a 20-year
  parameterization period were validated over 10-30-year windows, a
  precedent for B2 on GPDD-type data. Fagan & Holmes (2006) and Williams et
  al. (2021, LPD): rate of decline and growth-rate variability increase as
  extinction approaches, which is a state-and-trend signal, not a
  critical-slowing-down signal, and is exactly what B1 must capture so that
  EWS are not credited for it.
* Di Fonzo, Collen & Mace (2013) provide a trajectory-shape method for
  diagnosing rapid declines in wild vertebrate populations, an alternative
  outcome-labelling family to Pélissié et al.

## 12. Recent and forthcoming work, 2024-2026 (sweep of 74 queries, 48 records)

New fisheries items beyond those already positioned: Walter, Lewis, Hobbs &
Rypel (2025; GitHub `fish-ewi-ms`) apply CV and lag-1 autocorrelation in
five-year windows to San Francisco Estuary fish CPUE series to quantify
stability change, without a collapse outcome or prediction evaluation; Tao,
Hsieh, Hidalgo & Dakos (2025) track dynamic stability of North Sea cod with
empirical dynamic modelling; Benerradi, Dakos & Cano (2026) attribute
productivity changes to fishing and temperature across stocks; Medeiros et
al. (2025, PNAS) infer unseen dynamical regimes from population series;
Brock, Carpenter, Pace & Wilkinson (2026) show that driver rate alters
indicator behaviour in ecosystem experiments; Sguotti et al. (2024) estimate
resilience from a stochastic cusp model; Jafari et al. (2026) offer a
discrete-time benchmark for critical-slowing-down indicators; Ling & Keane
(2024, Nature Communications) report incipient spatial warnings of kelp
collapse. A GitHub manuscript by Rocha et al. counts break points in RAM
Legacy v4.44 biomass series: 373 stocks with more than 25 years, of which
119 fell below 50 % of their historical average. That count is the only
independent calibration of our RAM projection found: the "RAM × 3"
scenario (510 eligible stocks) is an upper-end guess, and a × 2 case is the
more defensible central projection.

## 13. Adversarial refutation (three angles completed)

Two agents were asked to assume the study had already been done and to find
it, one from the fisheries side and one from the machine-learning benchmark
side. Both worked from the saved sweep records plus live GitHub repository
and code searches, because the web-search budget was exhausted. Both
returned `equivalent_study_found = false`. Their candidate lists coincide
with Sections 2, 3 and 8 above; the closest partial overlaps named were
Cano et al. 2025 (leave-one-out across series, not across time; static
per-series prediction; false positives relabelled "at risk"), Zhang 2020,
Pélissié et al. 2026, Deb et al. 2022 (EWSNet against logistic regression,
SVM, random forest and MLP, but every comparator is fed EWS features, so
there is no state/trend baseline), Falmagne et al. 2026 (methodologically
the nearest template: gradient-boosted trees, fixed horizon, held-out year,
explicit false-positive rate, but an online-game system) and Gao et al.
2025 (epidemiology). Two additional precedents surfaced that belong in the
manuscript: Pinsky & Byler (2015, Proc R Soc B) fit boosted regression
trees predicting collapse versus depletion across 154 RAM Legacy populations
from fishing pressure, growth rate and climate variability, with
non-collapsing populations included; and Burgess et al. (2013, PNAS)
proposed a forecastable T-score for flagging weak incidentally caught stocks.
Neither uses EWS, but both are collapse-risk models on RAM Legacy and the
first is a natural addition to the fisheries comparator set in Section 6.1.
The `lpi-multivariate-res` repository was resolved: it is O'Brien & Clements
(2025), a study of how stability metrics behave across data qualities and
community sizes, not a prediction benchmark.

Angle D (recent and forthcoming work, run 2026-09-14) used three lenses:
group-by-group searches for 2024-2026 output from the Dakos, Clements,
Boettiger, Bury, Munch, Jensen, Pinsky, Ozgul and allied groups (37
queries); preprint servers, conference abstracts and theses (45 queries plus
GitHub searches); and a close reading of the two nearest anchors, Cano et al.
2025 and Pélissié et al. 2026, against five design criteria (30 queries). An
adjudicator merged 36 candidate entries into 22, and none was rated
equivalent or substantial overlap, so the planned skeptic pass had nothing to
check. `equivalent_study_found = false` for the third time.

For the anchors, the criterion-by-criterion verdicts are: Cano et al. 2025
issue one static shape classification per series (no sequential origins),
validate by leave-one-out across series rather than across time, report ROC
curves and confusion matrices but calibrate no operating point to a
false-alarm budget, and relabel non-abrupt series predicted abrupt as "50
populations at risk" without a follow-up window; a state or trend comparator
is not visible. Pélissié et al. 2026 classify full productivity trajectories
of 315 stocks retrospectively and report a relative risk (an abrupt decline
roughly doubles the chance of later collapse, with a lead of about a decade;
the preprint says 10-20 years in a quarter of cases), with no predictive
validation, comparator, calibrated alarm rate or censoring treatment visible.
The one 2026 follow-up from the same group, Benerradi, Dakos & Cano (2026, J.
R. Soc. Interface), is an empirical-dynamic-modelling causality analysis of
155 stocks, not a prediction study; its public repository is the source of
the RAM v4.66 extract used in Section 16. Angle D reported that neither
anchor has a GitHub repository; that is wrong for Cano et al. 2025
(`alejvcano/dynfoot2025`, read by the key-paper extraction) and for Pélissié
et al. 2026 (`matpelissie/ocean_warming_fisheries`, found by angle B), and
the audit follows the earlier findings.

New candidates worth citing, none of which threatens the claim: TipPFN
(arXiv 2605.12308; a prior-data-fitted transformer evaluated on 14
semi-real and real systems with real non-transitioning series scored; the
author list differs between sweep 8 and angle D and is unresolved); Cerini,
Jackson, O'Brien, Childs & Clements (2025, Ecology; behavioural and
morphological signals precede abundance EWS in a Paramecium experiment, with
the remark that abundance EWS are prone to false positives); Babazadeh
Maghsoodlo, Anand & Bauch (2025, arXiv 2509.04683; a flickering detector with
a deliberately variance-inflating null); Ma, Zeng, Zhang & Bury (2025, Comm.
Phys.; surrogate-trained classifiers beat variance and AR1 on sensitivity and
specificity, but on non-ecological data; lens D1 had misattributed this paper
to Deb et al.); Mullett (2026, arXiv 2606.00329; detectors compared under a
locked equal-false-positive contract, a methodological neighbour of our
calibration); Ashwin, Bastiaansen, von der Heydt & Ritchie (2025, Proc. R.
Soc. A; horizon-specific ROC skill for EWS); Masuda et al. (2026, PNAS Nexus;
a sequential variance-only test with explicit false-positive control, not yet
applied to empirical data); Antão et al. (2026, Nature Communications; more
than 60,000 BioTIME populations, trend-based association with extinction risk);
and the Alvarez-Martinez & Miramontes (2026, Entropy) review, whose reference
list should be checked in full at submission.

## 14. Remaining gaps

No full text was read for any paper except Ward et al. 2014 and Lapeyrolerie
& Boettiger 2023; every design judgement about Zhang 2020, Cano 2025,
Pélissié 2026, Burthe 2016, O'Brien 2023, Bury 2021, Deb 2022 and Falmagne
2026 rests on snippets, abstracts and public code and must be confirmed
against the published methods and supplements before the novelty statement is
frozen. All three refutation angles have now run (Section 13), and the three
data-content checks have run against public mirrors where a licence-compliant
mirror exists (Section 16); the Living Planet Database check could use
published counts only. Still open: whether Cano et al. 2025 used the
label-informed truncation (`cut=TRUE` with `asclassif` detrending) that their
code defaults to, which would make the leave-one-out AUCs partly reflect label
leakage; Pélissié et al. 2026's handling of right-censored stocks and whether
only first collapses were used; the TipPFN author list and whether any
monitored population series are among its real systems; and items surfaced
only by title (Ma et al. 2025; Liu et al. 2024; Looker, Rock & Dyson;
Pélissié, Devictor & Dakos 2024; Evers et al. `bifurcationEWS`; Laitinen,
Dakos & Lahti, arXiv:2205.07576; Munch & Rogers 2026, PNAS, forecasting on
Living Planet series; the 2024 Science retrospective-bias paper; the 2026
Science Advances paper on initial-data-point dependence of indicator
agreement; arXiv 2605.28260, 2608.06608, 2605.04024, 2607.15423, 2603.14944).
EcoEvoRxiv, bioRxiv and the ESA, ICES, ASLO and BES abstract databases are
poorly indexed by the search engine and unreachable by fetch, so an unindexed
sequential-prediction sequel from the Montpellier group cannot be excluded;
the claim is made "to our knowledge" and will be re-checked at submission.

## 15. Synthesis: positioning statement and reconciliation (2026-09-14)

A synthesis agent read this audit, the eight key-paper extractions, the three
refutations and the sweep records and returned the verdict
`novel-combination-supported`. Its positioning statement is reproduced
verbatim below as a manuscript draft; every judgement in it rests on
snippets and public code, as Section 14 says.

> Generic early-warning signals (EWS) of critical slowing down, rising lag-1 autocorrelation and variance, have been tested on ecological monitoring data for more than a decade, and the largest tests have been sobering. Burthe et al. (2016) tallied true positives, false negatives and false positives for variance and autocorrelation across 126 abundance series from six UK aquatic systems within a 10-year association window and found false positives more prevalent than false negatives and true positives in fewer than one series in ten. O'Brien et al. (2023) evaluated classical, multivariate and machine-learning (EWSNet; Deb et al. 2022) indicators in transitioning and non-transitioning lake plankton series and reported that most indicators performed no better than a 0.5 chance reference, with unscaled EWSNet reaching true-positive probabilities of about 0.9 only at true-negative probabilities of 0.05-0.19. In fisheries, Zhang (2020) evaluated standard deviation and AR1 against productivity regime shifts in 191 RAM Legacy populations with an explicit true-negative and positive-likelihood-ratio framing; Cano, Jensen and Dakos (2025) trained boosted regression trees on a "dynamical footprint" that includes AR1 and SD across RAM Legacy, ICES cod and FishGlob series and obtained leave-one-out AUCs of 0.84, 0.75 and 0.65; and Pélissié et al. (2026) showed that abrupt productivity declines in 315 assessed stocks were followed by biomass collapse in 11 of 42 cases (26%), negative shifts being present in 23% of collapsed and 12% of non-collapsed stocks. Whole-lake experiments (Pace et al. 2017; Wilkinson et al. 2018; Buelo et al. 2022) and laboratory systems (Drake and Griffen 2010; Jarvis-Cross et al. 2025; Cerini et al. 2025) supply reference systems or controls and explicit true- versus false-alarm rates. We therefore do not claim that prior work ignored false positives or non-transitioning series, nor that AR1/variance-type indicators have not been applied to RAM Legacy or FishGlob at scale; each of those has been done.
>
> What has not been done, to our knowledge, is to ask whether a prespecified EWS score adds detection of first population-abundance collapses beyond what the current state and recent trend of the same series already provide, at a common false-alarm burden, in a design that is time-indexed and complete in follow-up. Every empirical EWS evaluation above is retrospective or static. Burthe et al. and O'Brien et al. classify whole series after the fact; Zhang locates shifts in the full record and looks back; Cano et al. assign one footprint and one class per series, validate across series rather than across time, and relabel non-abrupt series predicted abrupt as 50 populations "at risk" with no follow-up window; Pélissié et al. date shifts with hindsight and report a relative risk rather than a calibrated alarm. None scores a state-or-trend comparator on the same origins. The forecasting literature supplies that comparator but has not connected it to EWS: Ward et al. (2014) showed on 2379 vertebrate series that a random walk without drift is essentially unbeatable at 1-5-year horizons; Holmes et al. (2007) validated diffusion-approximation quasi-extinction forecasts from 20-year parameterization windows; Hefley et al. (2013) paired an indicator with a state-space threshold-crossing model in a single quail population; and Pinsky and Byler (2015) predicted collapse across 154 RAM Legacy populations from fishing pressure, growth rate and climate variability without any EWS. Machine-learning EWS work has the evaluation machinery we borrow. Bury et al. (2021) and Ma et al. (2025) report ROC or sensitivity and specificity against variance and AR1; Falmagne et al. (2026) detect half of transitions within a fixed window at a 3.6% false-positive rate on a held-out year; Deb et al. (2022) compare EWSNet with logistic regression, SVM, random forest and MLP. But its negatives are surrogates, nulls or non-ecological systems, every comparator is itself fed EWS features, and no study uses monitored population series with a calendar horizon. Outside ecology, Mullett (2026) evaluates detectors under a locked equal-false-positive contract, and the seizure-prediction and landmarking literatures define sensitivity at a fixed false-prediction rate with event-time surrogates; we import these conventions rather than reinvent them.
>
> Our contribution is therefore the combination, not any single element: (i) sequential forecast origins at which every predictor uses only data available by that year; (ii) fixed 1-5-year horizons with negatives requiring complete follow-up, so that right-censored origins are never counted as non-events, a treatment not visible in any anchor paper; (iii) alarm thresholds for the EWS score and for a capacity-matched state-and-trend baseline (abundance relative to reference, recent slope, a local-linear state-space threshold-crossing forecast, and a last-value score after Ward et al.) calibrated in development data to the same false-alarm budget; and (iv) evaluation grouped by biological system across RAM Legacy, survey indices, GPDD, the Living Planet Database and BioTIME, with lake regime shifts as a separate challenge analysis positioned against O'Brien et al. (2023). The quantities Cano et al. and Pélissié et al. report, 50 at-risk populations without later verification and a 26% positive predictive fraction with no comparator, are exactly what an operating-point analysis against a matched baseline is designed to adjudicate, and Boettiger and Hastings' (2012) warning against selecting systems because they transitioned is answered by the risk-set design.
>
> Two caveats bound the claim. First, every judgment about prior designs rests on abstracts, search snippets and public code; full text was read only for Ward et al. (2014) and Lapeyrolerie and Boettiger (2023). The methods of Zhang (2020), Cano et al. (2025) and Pélissié et al. (2026), especially pre-shift windowing, the operationalization of "no shift" and series-end handling, must be confirmed against the published supplements before the novelty statement is frozen. Second, the search could not reach EcoEvoRxiv, ESA/ICES/ASLO abstracts or the reference list of the 2026 Entropy review, and a very recent sequential-prediction sequel from the Montpellier group cannot be excluded; the claim is made "to our knowledge" and will be re-checked at submission.

The synthesis also listed contradictions between the audit, the raw records
and the Stage 0 report. They were resolved as follows. Query and record
counts: the header now quotes the query log directly (896 executed, 878
unique, 31 refused) and gives the raw record count (569) alongside the
deduplicated count. Zhang 2020 is a sole-author paper and the Stage 0 report
now says "Zhang (2020)"; its article number is uncertain (106344 or 106371).
Cano et al. 2025 do have a code repository (`alejvcano/dynfoot2025`) and
Pélissié et al. 2026 do (`matpelissie/ocean_warming_fisheries`); the angle D
claim to the contrary is superseded (Section 13). Pélissié's lead-time figure
differs by source (4-12 years in the PMC results text, "about a decade" in
the abstract, 12 years in the press release, 10-20 years in a quarter of
cases in the preprint); the audit quotes the results-text figure and notes
the range. Falmagne et al. 2026's author initials and false-positive rate
(3.6 % versus 3.7 %) differ between sweeps and remain unverified. The
TipPFN author list (Sevinchan versus Ramien) is unresolved. Medeiros,
Sorenson, Johnson, Palkovacs & Munch (2025, PNAS) is the better-supported
attribution for the "unseen dynamical regimes" paper. Jarvis-Cross et al.
2025 is published (PLOS Global Public Health 5(10): e0005142), not a preprint.
Ward et al. 2014 used LPI, BBS, RSPB, RAM recruits-per-spawner and Pacific
salmon series, with GPDD entering only through the LPI. Burthe et al. 2016
true-positive figures exist at series level (8 % / 6 %) and case level (9 % /
13 %); the report should specify the level when quoting them. The O'Brien et
al. 2023 lake count (nine, with Upper and Lower Zurich counted separately)
follows the key-paper extraction.

Design lessons the synthesis added to Sections 5 and 10: include a last-value
(random walk without drift) score in the baseline set and report a MASE-like
skill alongside alarm metrics (Ward et al. 2014); count relabelled
false alarms as false alarms with a frozen budget (Cano's 50 "at risk"
populations; Pélissié's 31 of 42 negative shifts not followed by collapse);
bracket the conventional forecast between an idealized and a phenomenological
model (Lapeyrolerie & Boettiger 2023); preregister a collapse-definition
family that includes Pélissié's 25 %-of-to-date-average rule and Pinsky's
Bmin < 0.2 BMSY; keep the critical-speeding-up score separate and
directional; state that RAM-derived origins are "as finally assessed" and
treat survey indices as the robustness set; freeze preprocessing before any
classifier is applied (Dablander & Bury 2022); include rate-induced and
noise-driven transitions in the falsification suite; name the risk-set design
as the answer to the prosecutor's fallacy (Boettiger & Hastings 2012); borrow
landmarking, IPCW time-dependent AUC and fixed-false-prediction-rate
conventions rather than inventing them; and cite Mullett 2026 and Ashwin et
al. 2025 as methodological neighbours only.

## 16. Data-content checks (2026-09-14)

Three agents checked what the blocked sources contain, using published
counts and, where a licence permits, a public mirror; a second agent
recomputed every mirror-derived count independently. Structured outputs are
in `data/metadata/data_content_checks_raw.json`; the census consequences are
in `reports/stage0_feasibility_census.md` Section 2 and Section 8.

* RAM Legacy v4.66: the `timeseries_values_views` table for v4.66 is
  redistributed (CC BY 4.0 upstream) in `RaphBnrd/RAMLDB_causality`, the
  repository of Benerradi, Dakos & Cano (2026). It holds 1438 stocks with any
  series, 1091 with SSB, TBbest or TB, 639 SSB stocks with >= 30 annual
  values (420 non-salmon), 357 TBbest stocks with >= 30, 488 stocks with
  B/BMSY-type and 569 with U/UMSY-type reference points (625 with either,
  432 with both, matching the Zenodo record description). The verifier
  reproduced all length and coverage counts exactly; the only discrepancies
  were a NaN-after-gap bug and row-wise TB/SSB coalescing in the first
  agent's collapse flags, both avoided in the census. The official stock
  count is inferred as 1442 and cannot be checked from the mirror.
* Living Planet Database: no mirror was used (the data-use agreement forbids
  redistribution, so a mirror would itself violate it). Published counts:
  the 2024 index uses 34,836 populations of 5,495 species (1970-2020, public
  release without confidential records); the whole database holds almost
  42,000 populations, about 18 % confidential; the modal series length is
  6-10 years, more than 2,000 records sit at the 2-year minimum and "more
  than 2,000" span 1970 to 2011-2015; Leung et al. 2020 lost 52 % of series
  with a 10-point minimum. No published count of populations with >= 30
  annual observations or with 80 % declines exists; the GPDD is listed as an
  LPI source but the number of GPDD-sourced populations is not published.
  These must be computed from the official download.
* BioTIME 2.0: no public mirror of the 2.0 data or metadata exists (one
  repository tracks the query file through git-LFS only). A June-2021 v1
  metadata export (417 studies, including about 8 % non-public studies
  used with permission) was read as a floor: 50 studies have >= 30 sampled
  years (22 gap-free), 27 have >= 35, 101 have >= 20; by realm the >= 30
  studies are marine 19, terrestrial 23, freshwater 8, and by taxon birds 11,
  fish 10, terrestrial invertebrates 6. The long marine fish studies are the
  ICES, NEFSC and DFO trawl programmes that also underlie FishGlob and RAM.
  BioTIME 2.0 has 708 studies, and each study carries its own licence (in a
  53-study v1 subset: 36 CC BY, 5 PDDL, 4 ODC-BY, 3 CC0, 3 ODbL, 2 CC BY-NC).
  The verifier confirmed every count and flagged that DATA_POINTS counts
  distinct years rather than years under constant effort, that GRAIN_SQ_KM
  is zero for 213 studies, and that 17 studies' title year ranges disagree
  with their metadata years.
