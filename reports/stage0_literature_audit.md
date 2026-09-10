# Stage 0 literature audit (Section 3.1)

Searches: 2026-09-08 to 2026-09-10. Engine: the sandbox's WebSearch tool.
Publisher sites, PubMed/PMC, Crossref, OpenAlex, Semantic Scholar, Google
Scholar, Web of Science, Scopus, Zenodo, Dryad, OSF, arXiv and bioRxiv were
blocked by the egress policy throughout, so no full text was read; details
below come from search-result snippets, from authors' public code
repositories, and (for two papers) from author-hosted PDFs on
raw.githubusercontent.com. Saved queries:
`data/metadata/literature_queries.json` (482 executed, 23 submitted after the
session's 200-query budget was exhausted and refused). Raw structured
outputs: `data/metadata/literature_sweeps_raw.json` (six sweep agents, 256
study records) and `data/metadata/literature_keypapers_raw.json` (eight
anchor-paper design extractions).

Coverage achieved: four topic sweeps with working search (fixed-horizon
prediction and false alarms; out-of-sample validation and forecasting
baselines; fisheries collapse prediction; lakes and communities), two
GitHub-only supplementary sweeps, and eight anchor-paper extractions. Five
planned sweeps (machine-learning and multivariate EWS; methodological
critiques; evaluation methodology; GPDD/LPD/BioTIME applications; a 2024-2026
recency sweep), three adversarial novelty refutations and the synthesis and
critic agents did not run: the session usage limit was reached three times
and the WebSearch budget is now spent. Those gaps are listed in Section 7.

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

## 7. Known gaps of this audit

No full text was read for any paper except Ward et al. 2014 and Lapeyrolerie &
Boettiger 2023, whose manuscripts are on GitHub. Five planned sweeps did not
run: machine-learning and multivariate EWS follow-ups, methodological
critiques (window and detrending sensitivity, sampling frequency, selection
bias), evaluation methodology (landmark and IPCW methods, seizure-prediction
metrics, equivalence testing), GPDD/LPD/BioTIME applications, and a dedicated
2024-2026 recency sweep. No adversarial refutation agent ran. The
GitHub-only supplements surfaced items worth following up: Ma, Zeng, Zhang &
Bury 2025 (Communications Physics 8:258, surrogate-trained ML with ROC); Liu
et al. 2024 (Phys Rev X, GIN-GRU tipping predictor); Looker, Rock & Dyson
(PLoS Comput Biol, doi:10.1371/journal.pcbi.1013524); Pélissié, Devictor &
Dakos 2024 (Biol Conserv, doi:10.1016/j.biocon.2023.110429, the abrupt-shift
classifier itself); Evers et al. `bifurcationEWS`; O'Brien & Clements 2025
(`lpi-multivariate-res`, which applies multivariate resilience methods to
Living Planet data and must be checked for overlap). Re-running the missing
searches from a machine with publisher access is the first Stage 1 action.
