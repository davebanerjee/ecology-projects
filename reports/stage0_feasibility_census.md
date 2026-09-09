# Stage 0 feasibility census

Date: 2026-09-09. Scope: metadata, observation schedules, outcome labels and
event counts only (PROTOCOL Section 3.2). No early-warning-signal feature was
computed and no predictor–outcome association was examined.

All counts use the PROVISIONAL outcome and eligibility rules of PROTOCOL
Sections 4.3, 5.1 and 5.2 exactly as implemented in `src/census/labels.py`
(unit tests in `tests/test_labels.py`):

* collapse onset = first year s with x_s < 0.20·R(s) and x_{s+1} < 0.20·R(s),
  R(s) = max over u ≤ s−1 of the median of the complete 5-year window ending at u,
  defined only after ≥ 5 positive observations;
* forecast origin t eligible if x_t observed, t < onset (and before any
  unconfirmed low year), ≥ 30 observations at years ≤ t, the trailing 24 years
  fully observed (no imputation), and the 5-year label ascertainable (Y=1 if
  onset ∈ {t+1..t+5}; Y=0 only if an onset is ruled out at every year t+1..t+5;
  an undefined reference or a missing year makes a year "unknown", not ruled out).

These rules were tightened after the code review of 2026-09-09; the earlier
(gap-tolerant) counts are retained in the sensitivity grids as the
`min_complete_window = 0` rows.

"Event" below means a system whose unique onset falls inside the horizon of at
least one eligible origin (i.e., a first collapse that the benchmark could
score). Systems that collapse before accumulating 30 observations contribute
nothing (all their origins are censored), which turns out to be the dominant
loss.

## 1. Sources reached from the sandbox

| Source | Version / route | Licence (as seen) | Reached? |
|---|---|---|---|
| FishGlob | v2.1.0, github.com/AquaAuma/FishGlob_data (commit c817762, 2026-08-28) | CC BY 4.0 (LICENSE in repo) | yes |
| GPDD | v2010 rev 2.0 as bundled in ropensci/rgpdd (commit 7406de2) | rgpdd package CC0; KNB data terms not verifiable (egress blocked) | yes |
| RAM Legacy | v4.41 (2018) SSB/TB/R/catch extract for 328 stocks in cfree14/sst_recruitment | repo has no LICENSE; used only as a PROXY for sizing | proxy only |
| RAM Legacy current (v4.66+) | ramlegacy.org / Zenodo | CC BY 4.0 expected (unverified) | blocked |
| Living Planet Database | livingplanetindex.org | data-use agreement; human acceptance required | blocked |
| BioTIME 2.0 | Zenodo 10932823 | CC BY 4.0 expected (unverified) | blocked |
| ICES DATRAS / SAG | ices.dk | ICES data policy (CC BY 4.0 expected) | blocked |
| Lake challenge set | duncanobrien/ews-assessments (O'Brien et al. 2023) | no LICENSE; 2 of 9 lakes restricted | yes (7 lakes) |
| Bury et al. 2021 classifiers | ThomasMBury/deep-early-warnings-pnas | CC BY-NC-SA 4.0 | yes |

Checksums and commit hashes are in `MANIFEST.json`.

## 2. RAM Legacy (v4.41 proxy; lower bound for the current release)

Abundance variable: spawning-stock biomass (all 170 eligible stocks use SSB;
total biomass is the fallback). Series end in 2013–2016 in this extract; the
current release adds ~8–10 years, which matters because eligibility needs a
5-year follow-up.

| Step | stocks | stocks with ≥1 origin | origins | events | positive origins | negative origins |
|---|---|---|---|---|---|---|
| all stocks with SSB/TB | 328 | 170 | 3107 | 43 | 204 | 2903 |
| n_obs ≥ 35 | 213 | 170 | 3107 | 43 | 204 | 2903 |
| ≥ 1 eligible origin | 170 | 170 | 3107 | 43 | 204 | 2903 |

* 106 of 328 stocks have a collapse onset under the 80 % rule at some point;
  only 43 of those onsets occur after ≥ 30 observations. Onset decades of all
  106: 1940s 1, 1950s 1, 1960s 7, 1970s 14, 1980s 16, 1990s 35, 2000s 28, 2010s 4.
* Origins per eligible stock: median 10 (IQR 5–25, max 98). Long series (US
  West Coast, New Zealand, Alaska) dominate the population-year estimand.
* Events by region: New Zealand 8, US West Coast 7, South America 4, EU 4,
  Canada West Coast 4, US Southeast/Gulf 3, Europe non-EU 3, others ≤ 2.
* Eligibility sensitivity (same stocks):

| variant | stocks with origins | origins | events |
|---|---|---|---|
| provisional (20 % of reference, 2-year persistence, 30-obs history, 5-y horizon) | 170 | 3107 | 43 |
| 10 % of reference (90 % decline) | 198 | 3898 | 23 |
| 30 % of reference (70 % decline) | 151 | 2492 | 57 |
| 3-year persistence | 174 | 3207 | 41 |
| history ≥ 25 observations | 225 | 4115 | 56 |
| history ≥ 20 observations | 271 | 5368 | 68 |
| 3-year horizon | 185 | 3387 | 43 |

Projection to the current release (uncertain): the v4.41 extract holds 328
stocks with stock–recruit data; the full v4.66 database holds well over 1000
stocks with time series, of which perhaps 500–700 have ≥ 35 years of SSB or
total biomass. The power analysis therefore includes a "RAM ×3" projection
(≈ 510 eligible stocks, ≈ 130 events) labelled as a projection.

## 3. FishGlob v2.1.0 (survey indices)

Proposed aggregation (to be frozen in Stage 1): `survey_unit` (survey ×
quarter/season) × species; hauls flagged by footprint-trimming method
`flag_trimming_hex7_2` removed; years with < 20 unflagged hauls set missing;
species retained if caught in ≥ 5 % of hauls; index = mean weight CPUA
(kg km⁻²) over hauls with zeros for absences; species-years with catches but
no positive weight record set missing.

| Step | series | with ≥1 origin | origins | events |
|---|---|---|---|---|
| all survey_unit × species candidates | 1662 | 156 | 1027 | 40 |
| not irregular-interval survey (AI, GOA, WCTRI, DFO surveys, SOG) | 1535 | 156 | 1027 | 40 |
| n_obs ≥ 35 | 394 | 156 | 1027 | 40 |
| ≥ 1 eligible origin (complete 24-year window) | 156 | 156 | 1027 | 40 |
| no documented survey method change inside feature window / follow-up (FR-CGFS 2015; GSL-S 1985, 1992; SCS 1996; NOR-BTS 2004; GSL-N 1990) | 132 | 132 | 771 | 25 |
| zero fraction ≤ 0.2 | 129 | 129 | 756 | 22 |

* The complete-window requirement removes every survey unit with a missing
  year inside the 24-year window (GMEX-Summer, NEUS-Fall, SWC-IBTS). Only four
  units remain: GMEX-Fall 54 series (11 events), NS-IBTS-Q1 35 (4), EBS 25 (5),
  NEUS-Spring 15 (2). Origins per series: median 4 (IQR 3–7, max 18).
* Gap-tolerant eligibility (state-space sensitivity) gives 219 series, 42
  events and 1115 origins; the earlier census (before the review) reported 212
  / 40 / 1079 under that rule.
* Events cluster by survey and year: half the screened events are Gulf of
  Mexico series with onsets in 2016–2020 (the GMEX data were re-merged in
  v2.1.0 and the SEAMAP survey has documented vessel/gear transitions). These
  are not independent collapses; a survey-level shift is the more likely
  explanation and must be adjudicated in the method-change audit before any
  FishGlob event enters the confirmatory cohort.
* FishGlob series of commercial species duplicate RAM stocks (Section 6 below).
* History-minimum sensitivity (complete window of the same length): ≥ 25
  observations → 303 series, 51 events; ≥ 20 → 344 series, 89 events.

## 4. GPDD v2010

3613 series are annual (`SamplingFrequency == 1`) after dropping 2930 rows
with negative sample years; 60 annual series contain negative values (index or
deviation scales) and are excluded; 856 sub-annual series were annualized as a
sensitivity and yield no eligible origin. Restricted-availability MainIDs
(685) carry no data in the bundle.

| Step | series | with ≥1 origin | origins | events |
|---|---|---|---|---|
| all annual series | 3613 | 245 | 3756 | 76 |
| not restricted | 3613 | 245 | 3756 | 76 |
| no negative values | 3553 | 245 | 3756 | 76 |
| Reliability ≥ 2 | 2084 | 53 | 440 | 10 |
| n_obs ≥ 35 | 100 | 53 | 440 | 10 |
| no method/effort-change keyword in Notes | 94 | 51 | 421 | 9 |
| not harvest/catch/kill series | 68 | 38 | 303 | 5 |
| ≥ 1 eligible origin (complete 24-year window) | 38 | 38 | 303 | 5 |

* The 38 surviving series are 35 bird counts from 12 locations and 12 data
  sources (mostly UK island/reserve censuses and North American counts) with
  onsets in 1937–1978; 16 contain zeros. They are far from independent.
* The Reliability filter is the second-largest loss. A published GPDD summary
  (IWC document SC/A10/MSYR1) states that higher codes are more reliable, that
  series with Reliability ≥ 3 "should be accepted" and that 2 is "probably too
  unreliable"; the value −1 (1023 series) is undocumented in the bundle. With
  ≥ 3 the screened cohort is 36 series and 5 events; with ≥ 4, 33 and 4. The
  long harvest series (Reliability 1 and −1) are excluded anyway by the effort
  rule. Confirm against the GPDD user guide on KNB before Stage 1.
* History-minimum sensitivity on the screened pool: ≥ 25 → 46 series, 8 events;
  ≥ 20 (20-year complete window) → 90 series, 16 events; gap-tolerant ≥ 20 →
  139 series, 22 events.

## 5. Lake / community challenge set (separate analysis)

`duncanobrien/ews-assessments` provides genus-aggregated plankton data for 7 of
the 9 lakes of O'Brien et al. (2023); Kinneret and Kasumigaura are available
only on request. Annual series are 9–28 years long (Loch Leven 12, Lower Zurich
28, Mendota 15, Monona 12, Upper Zurich 17, Washington 9, Windermere 20);
monthly series 97–332 observations. Published community-level threshold
transition dates: Washington 1975, Lower Zurich 2002, Mendota 2012 (Kinneret
1998, Kasumigaura 2009 restricted); Loch Leven, Monona, Upper Zurich and
Windermere have no confirmed community transition. The annual series are far
too short for the confirmatory rules; the challenge analysis can only use the
monthly data with the published classifications, as the protocol anticipates.

## 6. Independence and overlap

* 30 of the 156 FishGlob series with origins match a RAM v4.41 stock by species
  and region (74 candidate pairs, 74 RAM stocks); with the full RAM release most
  long commercial-species survey series will be dependent on an assessed stock.
* 21 of 280 eligible GPDD annual series sit in taxon×location groups with
  several MainIDs; 27 pairs of the same taxon lie within 50 km.
* Eligible series per source concentrate in a few programmes (GPDD: 12 data
  sources hold all 38 screened series; FishGlob: one GMEX unit holds 54 of 129
  screened series).

## 7. Attrition drivers, in order of importance

1. The 30-observation history minimum before the first origin (RAM: 63 of 106
   collapses lost; FishGlob: 89 → 22 events; GPDD: 16 → 5). The provisional
   classical EWS specification needs 24 pre-origin observations, so 25 is the
   technical floor; 20 would require a shorter indicator window.
2. The complete 24-year window (no imputation): FishGlob 42 → 22 events;
   GPDD origins 376 → 303; RAM unaffected (assessment series are gap-free).
3. Complete 5-year follow-up for negatives (series ending 2013–2016 in the
   proxy lose their last five years of origins; the current RAM release recovers most).
4. Survey method changes (FishGlob) and unknown effort (GPDD harvest series).
5. Reliability coding (GPDD; semantics partly verified).

## 8. Accessible-now totals (provisional rules, complete windows)

| Source | systems with origins | events | origins (pos / neg) |
|---|---|---|---|
| RAM v4.41 proxy | 170 | 43 | 3107 (204 / 2903) |
| FishGlob (screened) | 129 | 22 | 756 (86 / 670) |
| GPDD (screened) | 38 | 5 | 303 (13 / 290) |
| total | 337 | 70 | 4166 |

With the current RAM release, LPD and BioTIME the totals could plausibly reach
600–1200 systems and 130–300 events, but every one of those numbers is a
projection until a human retrieves the blocked sources.
