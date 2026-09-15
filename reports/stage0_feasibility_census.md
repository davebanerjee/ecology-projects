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
| RAM Legacy | v4.41 (2018) SSB/TB/R/catch extract for 328 stocks in cfree14/sst_recruitment | repo has no LICENSE; used only as a PROXY for sizing (superseded on 2026-09-14) | proxy only |
| RAM Legacy v4.66 (target release) | `timeseries_values_views` for v4.66 redistributed in github.com/RaphBnrd/RAMLDB_causality (commit 09766f2, 2026-06-08; Zenodo 10.5281/zenodo.20594195) | repo MIT; upstream CC BY 4.0 (Zenodo 14043031) | yes, as a derived mirror (official release still blocked) |
| Living Planet Database | livingplanetindex.org | data-use agreement; human acceptance required | blocked |
| BioTIME 2.0 | Zenodo 10932823 (latest record 15222193, v4, 2025-04-15) | CC BY plus a per-study LICENSE column (search snippets) | blocked; a June-2021 v1 metadata export (417 studies) read from github.com/gndaskalova/GlobalChangeSpace |
| ICES DATRAS / SAG | ices.dk | ICES data policy (CC BY 4.0 expected) | blocked |
| Lake challenge set | duncanobrien/ews-assessments (O'Brien et al. 2023) | no LICENSE; 2 of 9 lakes restricted | yes (7 lakes) |
| Bury et al. 2021 classifiers | ThomasMBury/deep-early-warnings-pnas | CC BY-NC-SA 4.0 | yes |

Checksums and commit hashes are in `MANIFEST.json`.

## 2. RAM Legacy v4.66 (target release, derived mirror; the v4.41 proxy is kept for comparison)

Source and caveats. On 2026-09-14 a data-content agent found the v4.66
`timeseries_values_views` table (one preferred series per stock from the most
recent assessment, all 35 standard columns, plus stock and taxonomy metadata)
redistributed in the public repository of Benerradi, Dakos & Cano (2026),
`RaphBnrd/RAMLDB_causality`. The upstream database is CC BY 4.0, so reading the
mirror is licence-compliant. It is a derived extract, not the official
`DBdata[asmt][v4.66].RData`: the mirror author dropped four stocks with empty or
non-consecutive years (HADNS, HERR30, HERRNS, SOLEIIIa) and added 156 SST-only
stockids by a full join (excluded here); the file carries no internal version
field, so the version rests on the file names, the README and the preparation
script (the 625 / 432 reference-point counts match the Zenodo record
description). A second agent recomputed every length and coverage count from
the file independently and reproduced them exactly; the two agents' collapse
flags differed only through a NaN-after-gap bug in the first script and
through row-wise versus stock-level TB/SSB coalescing, both avoided in the
census below. All counts must be re-run on the official Zenodo release before
preregistration (`src/census/census_ram_v466.py` takes the official table
unchanged).

Content. 1438 stocks carry at least one RAM series; 1091 carry SSB, TBbest or
TB (SSB 976 stocks, TBbest 475, TB 500; 358 of the 1091 are Pacific salmon
escapement series that all end by 2005). Series with at least 30 annual values:
SSB 639 (420 non-salmon), TBbest 357, TB 362. Years run 1872-2024 (one stock
starts in 1800). Nineteen pink-salmon SSB series are biennial and one rockfish
series is sampled at 2-3-year steps; 100 SSB and 10 TBbest series have internal
gaps. Fifteen SSB stocks contain exact zeros (14 salmon). B/BMSY-type
reference points exist for 488 stocks and U/UMSY-type for 569.

Abundance variable: SSB for the whole stock where any SSB exists, else TBbest,
else TB, chosen at stock level so that no series mixes two quantities (419
eligible stocks use SSB, 37 TBbest, 1 TB). Zeros are kept in the primary run.

| Step | stocks | stocks with >= 1 origin | origins | events | positive origins | negative origins |
|---|---|---|---|---|---|---|
| all stocks with SSB, TBbest or TB | 1091 | 457 | 8921 | 111 | 500 | 8421 |
| n_obs >= 30 | 698 | 457 | 8921 | 111 | 500 | 8421 |
| >= 1 eligible origin (complete 24-year window, 5-year follow-up) | 457 | 457 | 8921 | 111 | 500 | 8421 |
| ... excluding Pacific salmon | 349 | 349 | 7907 | 92 | 428 | 7479 |

* 316 of the 1091 stocks have a collapse onset under the 80 % rule at some
  point; 198 of those onsets fall within the first 30 observations and can
  never be a labelled event. Of the 241 stocks with >= 30 observations but no
  eligible origin, 147 collapsed before 30 observations, 32 are gapped or
  non-annual (the complete-window rule removes every biennial salmon series)
  and 106 are too short for a 5-year follow-up after a 30-year history.
* Onset decades of the 111 labelled events: 1890s 1, 1940s 3, 1950s 1, 1960s
  6, 1970s 6, 1980s 20, 1990s 32, 2000s 27, 2010s 15. Series end in 2016 at
  the median (IQR 2006-2020), so the follow-up problem of the proxy (series
  ending 2013-2016) is largely gone for non-salmon stocks.
* Origins per eligible stock: median 11 (IQR 5-25, max 99).
* Events by region: US West Coast 16, New Zealand 11, European Union 9,
  Canada East Coast 8, US Southeast and Gulf 8, Canada West Coast salmon 8,
  US Alaska salmon 8, Canada West Coast 7, Southern Africa 7, US East Coast
  6, South America 5, Australia 4, US Alaska 3, Russia/Japan salmon 3, others
  <= 2. Events by fishery type: other marine 22, Pacific salmon 19, gadids 16,
  rockfish 15, invertebrates 11, flatfish 10, forage fish 10, tuna and
  marlin 5, sharks/rays/skates 3.
* The 108 eligible Pacific-salmon stocks (19 events) are single-river
  escapement series in three regions; they share regional shocks and are
  an obvious cluster for the system grouping. Non-salmon totals are reported
  throughout as a sensitivity.
* Eligibility sensitivity (same stocks):

| variant | stocks with origins | origins | events |
|---|---|---|---|
| provisional (20 % of reference, 2-year persistence, 30-obs history, 5-y horizon) | 457 | 8921 | 111 |
| gap-tolerant window (min_complete_window = 0) | 460 | 8944 | 111 |
| 10 % of reference (90 % decline) | 529 | 10999 | 57 |
| 30 % of reference (70 % decline) | 379 | 7080 | 142 |
| 3-year persistence | 494 | 9412 | 99 |
| history >= 25 observations | 558 | 11486 | 134 |
| history >= 20 observations | 653 | 14576 | 167 |
| 3-year horizon | 486 | 9663 | 110 |
| zeros treated as missing | 456 | 8914 | 111 |
| TBbest preferred over SSB | 462 | 9034 | 106 |
| non-salmon only | 349 | 7907 | 92 |

Comparison with the proxy and the projections. The v4.41 proxy gave 170
eligible stocks and 43 events (Section 2a below); v4.66 gives 2.7 times as
many stocks and 2.6 times as many events, between the "x 2" central case and
the "x 3" upper bound used in the power analysis (340 / 86 and 510 / 129).
The gain comes from stocks absent from the stock-recruit extract (salmon,
invertebrates, tunas) and from eight to ten extra years of follow-up, not
from longer histories: the 30-observation minimum still discards 198 of 316
collapses.

### 2a. RAM Legacy v4.41 proxy (historical; superseded)

Abundance variable: spawning-stock biomass (all 170 eligible stocks use SSB;
total biomass is the fallback, coalesced row-wise). Series end in 2013-2016.

| Step | stocks | stocks with >= 1 origin | origins | events | positive origins | negative origins |
|---|---|---|---|---|---|---|
| all stocks with SSB/TB | 328 | 170 | 3107 | 43 | 204 | 2903 |
| n_obs >= 35 | 213 | 170 | 3107 | 43 | 204 | 2903 |
| >= 1 eligible origin | 170 | 170 | 3107 | 43 | 204 | 2903 |

106 of 328 stocks have a collapse onset at some point; 43 after >= 30
observations. Proxy sensitivity: 10 % of reference 198 / 3898 / 23; 30 %
151 / 2492 / 57; 3-year persistence 174 / 3207 / 41; history >= 25 225 / 4115 /
56; history >= 20 271 / 5368 / 68; 3-year horizon 185 / 3387 / 43.

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

* Against the full v4.66 stock list, 53 of the 156 FishGlob series with
  origins match a RAM stock by species and region (131 candidate pairs; 130
  RAM stocks, 67 of them eligible and 20 with events; NS-IBTS 87 pairs, EBS
  16, SCS 14, NEUS 7, GMEX 6, GSL-S 1). Ten of the 22 FishGlob event series
  have a candidate RAM match. Against the v4.41 proxy the figures were 30 of
  156 and 74 pairs. Every candidate needs a stock-boundary check
  (`data/metadata/crosswalk_fishglob_ram_v466_candidates.csv`).
* 21 of 280 eligible GPDD annual series sit in taxon x location groups with
  several MainIDs; 27 pairs of the same taxon lie within 50 km.
* Eligible series per source concentrate in a few programmes (GPDD: 12 data
  sources hold all 38 screened series; FishGlob: one GMEX unit holds 54 of 129
  screened series; RAM: 108 of 457 eligible stocks are Pacific salmon rivers
  in three regions).
* BioTIME's long marine fish studies are the ICES, NEFSC and DFO trawl
  programmes that also underlie FishGlob and RAM (Section 16 of the audit),
  so BioTIME will add few independent fisheries systems.

## 7. Attrition drivers, in order of importance

1. The 30-observation history minimum before the first origin (RAM v4.66:
   198 of 316 collapses lost; FishGlob: 89 -> 22 events; GPDD: 16 -> 5). The
   provisional classical EWS specification needs 24 pre-origin observations,
   so 25 is the technical floor (RAM: 134 events); 20 would require a shorter
   indicator window (RAM: 167 events).
2. The complete 24-year window (no imputation): FishGlob 42 -> 22 events;
   GPDD origins 376 -> 303; RAM v4.66 loses only 3 stocks and no events, but
   the rule removes all 19 biennial salmon series and 32 gapped stocks.
3. Complete 5-year follow-up for negatives: 106 RAM stocks with >= 30
   observations are too short for it; the v4.66 series end in 2016 at the
   median, so the proxy's follow-up loss is largely recovered.
4. Survey method changes (FishGlob) and unknown effort (GPDD harvest series).
5. Reliability coding (GPDD; semantics partly verified).

## 8. Accessible-now totals (provisional rules, complete windows)

| Source | systems with origins | events | origins (pos / neg) |
|---|---|---|---|
| RAM v4.66 (derived mirror) | 457 | 111 | 8921 (500 / 8421) |
| FishGlob (screened) | 129 | 22 | 756 (86 / 670) |
| GPDD (screened) | 38 | 5 | 303 (13 / 290) |
| total | 624 | 138 | 9980 (599 / 9381) |
| total without Pacific salmon | 516 | 119 | 8966 (527 / 8439) |
| (previous total with the v4.41 proxy) | 337 | 70 | 4166 |

Independent events are fewer: up to 10 FishGlob event series duplicate a RAM
stock (candidates), and about half of the FishGlob events sit in one Gulf of
Mexico survey unit pending the method-change audit, so 118-128 independent
first collapses is the defensible range for the accessible data. The Living
Planet Database and BioTIME 2.0 remain projections: published LPD counts say
most series are 6-10 years long and no count of populations with >= 30
annual observations or with 80 % declines is published; the BioTIME v1
metadata floor is 50 studies with >= 30 sampled years (22 gap-free), largely
the same trawl programmes as FishGlob. With those sources the totals could
plausibly reach 700-900 systems and 150-220 events, but every one of those
numbers is a projection until a human retrieves the blocked sources.
