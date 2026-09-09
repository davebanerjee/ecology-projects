# Stage 0 — proposed (not frozen) parameter choices and clarifications

Every item below is a PROPOSAL for the Stage 1 freeze (human checkpoint 3 in
PROTOCOL Section 17). Nothing here was chosen after looking at any
predictor–outcome relationship; the only inputs were metadata, outcome labels,
event counts, and pure simulations.

## A. Outcome definition (Section 5.1)

| Parameter | Provisional | Proposal | Basis |
|---|---|---|---|
| decline threshold | 0.20 × R(s) | keep 0.20 | 0.10 halves the fisheries events (43 → 23); 0.30 adds events (57) but relabels moderate declines as "collapse"; 0.20 keeps the outcome interpretable as an 80 % loss and matches common fisheries "collapse" usage (to be confirmed by the literature audit). |
| persistence | 2 low years | keep 2 | 3 years costs few events (43 → 41) but removes short collapses that recover; keep as sensitivity. |
| reference | max of trailing 5-year medians, ≥ 5 positive obs | keep | implemented exactly; note that the reference can only grow, so late-starting series with an early low period get a low reference (design feature, documented). |
| negative-label ascertainment | "observed through t+5" | exact rule: an onset must be RULED OUT at each of t+1..t+5, which needs x_{t+6} only when x_{t+5} is below threshold | implemented in `labels.py`; strictly stronger than the draft wording. |

## B. Eligibility (Section 4.3)

| Parameter | Provisional | Proposal | Basis |
|---|---|---|---|
| minimum history before an origin | 30 observations | **25** (technical floor = 24 for the provisional 15-year window + 10 trend points); present 20 only together with a 12-year window | 30 discards 63 of 106 fisheries collapses (proxy), most FishGlob origins, and most GPDD events; 25 recovers +13 fisheries events (+30 %) and roughly doubles FishGlob events; 20 recovers +25 fisheries events but forces a shorter indicator window. |
| follow-up for negatives | 5 years complete | keep | required by the estimand. |
| complete feature window | "complete regular windows" | require the trailing 24 years up to the origin to be fully observed (no imputation); gap-tolerant eligibility only in the state-space sensitivity | code review found 27 % of FishGlob and 24 % of GPDD origins had a missing year inside the window under the earlier census. |
| unconfirmed collapse | not specified | a low year whose confirmation year is missing censors all later origins of that series | prevents already-collapsed years from entering as positive origins. |
| method-change screen | narrative | explicit per-survey change-year table (FishGlob) + Notes keywords (GPDD) + assessment-model change (RAM `assessid`) | implemented for FishGlob and GPDD; RAM needs the full release. |
| zero-inflation | not specified | exclude series with > 20 % zero years from the primary cohort | census shows 16 of 38 GPDD series contain zeros; FishGlob zero-year fraction is the natural screen. |
| minimum hauls per survey-year (FishGlob) | not specified | 20 unflagged hauls | years below this become missing; affects early NS-IBTS years. |
| species occurrence (FishGlob) | not specified | ≥ 5 % of hauls | avoids rare-species indices dominated by zeros. |
| footprint standardization (FishGlob) | not specified | `flag_trimming_hex7_2` (moderate); hex7_0 and method 2 as sensitivity | provided by FishGlob; choice affects series starts (NS-IBTS Q1 begins 1980 after trimming). |
| GPDD reliability | not specified | require Reliability ≥ 2 IF the code means 1 = least reliable; verify | coding semantics unverified in the rgpdd bundle. |

## C. Horizon and alarm rules (Sections 5.2, 9.1)

| Parameter | Provisional | Proposal |
|---|---|---|
| primary horizon | 1–5 years | keep; 1–3 and 6–10 secondary |
| episode start rule | five-year refractory | TWO candidate rules, choice to be frozen in Stage 1: 'block' (new episode once t − t_start > 5; a persistent alarm is re-scored every six years and can still detect a late collapse) or 'run' (one maximal alarm run = one episode; a persistent early alarm is one false episode and the collapse is missed). Stage 0 recommends 'block' because it penalizes always-alarm strategies more heavily under the false-alarm budget and matches an annual management review, but reports power under both. |
| false-alarm denominator | "monitored non-event population-years" | number of eligible negative origins (each = one monitored non-event year); pre-window years of event systems count as non-event years, and alarms there are false |
| false-alarm budget | 1 per 20 | keep; report realized burden and a non-inferiority margin (proposal: +0.25 episodes per 20 years) |

## D. Smallest useful effect (Section 3.3, checkpoint 3)

Provisional +10 percentage points of event sensitivity at the fixed budget.
Sketch of the management decision analysis that should justify it: with ~40
first collapses per decade among ~500 monitored stocks (proxy rate), a +10-point
gain warns of ~4 additional collapses per decade 1–5 years ahead at no extra
false alarms; whether that is "useful" depends on the cost of an extra
assessment/response triggered per alarm and the avoided loss per warned
collapse. Stage 0 recommends keeping 10 points but notes that the power results
(Section E) make anything below 10 points untestable with the data likely to be
available.

## E. Design and allocation (Section 7) — to be finalized after the power grids

* Locked hold-out with 50 % development beats 70 % development on power in
  every scenario, because power is limited by evaluation-set events, not by
  threshold calibration precision.
* Grouped 5-fold cross-fitting of thresholds over all systems gives markedly
  narrower paired confidence intervals than any hold-out split of the same data.
* Equal-dataset weighting with datasets holding < 10 evaluation events (GPDD)
  roughly doubles the variance of the estimate; propose a minimum of 15 evaluation
  events for a dataset to enter the equal-weight estimand, otherwise pool it
  into a "small datasets" stratum.
* The numeric gate outcome is in `reports/stage0_power_analysis.md`.

## F. Classical EWS specification (Section 6.2) — from pure simulation only

`src/sim/ews_window_detectability.py` (results in
`results/stage0/ews_window_detectability.csv`): annual AR(1) series whose
coefficient ramps linearly toward 0.97 over the last ≤ 40 years (fold-type
loss of resilience) with observation error, versus white-noise and red-noise
(AR 0.7, no resilience loss) nulls; score = mean Kendall tau of rolling lag-1
autocorrelation and log variance over the last k window estimates; origins
1–5 years before the transition. 300 series per arm. Stylized, so the absolute
numbers are not forecasts of empirical performance; the ranking of choices is
the point.

| window w / trend k (min obs) | AUROC vs white null, history 30 / 40 | sensitivity at 5 % FA (history 30) | FA on red-noise null at the white-null threshold |
|---|---|---|---|
| 10 / 5 (14), linear detrend | 0.53 / 0.49 | 0.10 | 0.11 |
| 15 / 10 (24), linear detrend | 0.60 / 0.53 | 0.11 | 0.09 |
| 15 / 10 (24), mean removal | 0.63 / 0.60 | 0.19 | 0.12 |
| 15 / 15 (29), mean removal | 0.64 / 0.62 | 0.17 | 0.06 |
| 20 / 10 (29), mean removal | 0.64 / 0.64 | 0.14 | 0.06 |
| 20 / 15 (34), mean removal | — / 0.66 | 0.22 (h40) | 0.10 |

Findings and proposals:

1. Within-window linear detrending removes most of the critical-slowing-down
   signal in short annual windows; mean removal (or a detrend fitted on the
   pre-window history only) should be the provisional transform.
2. Detectability rises with both window length and trend length; the
   provisional 15-year window with 10 trend points (24 observations) is close
   to the floor of usable performance, and 15/15 or 20/10 (29 observations)
   is measurably better. This conflicts with the event-count case for a
   25-observation history minimum (Section B): a 25-observation minimum
   implies 15/10; a 30-observation minimum permits 20/10 or 15/15.
   Stage 1 must choose one pairing knowingly; Stage 0 proposes 15/10 with a
   25-observation minimum as primary and 20/10 with a 30-observation minimum
   as the single prespecified alternative (Section 13: "at most one
   best-in-development alternative chosen by a deterministic rule").
3. Red-noise nulls trigger 6–16 % false alarms at a threshold set on white
   noise, so the alarm threshold must be calibrated on real development data
   (as planned), never on white-noise nulls, and coloured-noise series must be
   in the falsification suite (Section 12).
4. Even under favourable forcing the two-indicator score reaches AUROC ≈ 0.6–
   0.66 and ~20 % sensitivity at 5 % false alarms on annual data; combined
   with Section 5 (power), the realistic prior for the primary hypothesis is a
   small increment, which is exactly why the smallest useful effect and the
   evaluation-set size matter.

## G. Items Stage 0 could not settle

* B2 state-space convergence check (Section 6.1): not run, because fitting to
  real series is outcome-blind but still touches the data; propose running it on
  simulated series of matching length and on real series with convergence
  diagnostics logged and no outcome linkage, before Stage 1.
* GPDD Reliability coding; KNB licence; LPD data-use terms; BioTIME per-study
  restrictions; RAM current version and stock counts.
* Whether the GMEX collapse cluster (24 of 40 FishGlob events) survives the
  method-change audit.
