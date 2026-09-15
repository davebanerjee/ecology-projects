# CHANGELOG

## 2026-09-15 — Stage 0 residual audit, RAM v4.66 census, power re-run — no frozen parameters

* Third adversarial novelty refutation (angle D: 2024-2026 work; three lenses,
  adjudicator): no equivalent study; 22 merged candidates, none rated equivalent
  or substantial overlap. Synthesis agent verdict `novel-combination-supported`
  with a manuscript-ready positioning statement (audit Sections 13, 15).
* Data-content checks (audit Section 16): RAM v4.66 `timeseries_values_views`
  read from a public derived mirror (RaphBnrd/RAMLDB_causality; upstream CC BY
  4.0) and independently recomputed; LPD published counts only (no mirror, by
  licence); BioTIME v1 June-2021 metadata (417 studies) as a floor.
* `src/census/census_ram_v466.py`: census of RAM v4.66 with a STOCK-LEVEL
  abundance-variable rule (SSB > TBbest > TB; never row-wise coalescing, which
  manufactures spurious drops), zeros kept, Pacific salmon reported separately.
  457 eligible stocks / 111 events (349 / 92 without salmon), between the x2
  and x3 projections used before. New proposed rules recorded in
  `reports/stage0_proposed_parameters.md` Section B (variable choice, zeros,
  salmon grouping).
* `src/dedup/crosswalk_ram_v466.py`: 53 of 156 FishGlob series match a v4.66
  stock by species and region (131 pairs; 10 of 22 FishGlob event series).
* `src/sim/run_power_grid_v466.py`: power gate re-run with the v4.66 cohort;
  accessible data pass at a true +0.15 with grouped cross-fitting under the
  Section 10 rule and sit just under rule B at +0.10; the locked 50 % hold-out
  still fails. Go/no-go revised to a conditional go with cross-fitting as the
  primary design (Stage 0 report Section 8).
* Query log, sweep/refutation/synthesis/data-check raw outputs, data-source
  register and MANIFEST updated; report count discrepancies reconciled.

## 2026-09-09 — Stage 0 (feasibility) — no frozen parameters

* Added collapse-onset and forecast-origin label code with tests (`src/census/labels.py`).
  Clarification recorded for Stage 1: a negative label at origin t requires that an
  onset be RULED OUT at every year t+1..t+5, which in the edge case where x_{t+5} is
  below threshold needs x_{t+6}; the draft wording "observed through t+5" is slightly
  weaker. Implemented the stricter exact-ascertainment rule.
* DECISION REQUIRED at Stage 1 (not a clarification): the alarm-episode rule. Two
  readings of Section 9.1 were implemented — 'block' (a persistent alarm is re-scored
  as a new episode once more than `horizon` years have passed since the previous
  episode start) and 'run' (a maximal run of consecutive alarmed years is one episode;
  a run starting within `horizon` years of the previous episode's last alarm is merged).
  They differ in the false-alarm denominator and in whether a persistent alarm that
  began early can ever count as a detection; the power grid reports both.
* Label rules tightened after code review (2026-09-09): an undefined reference year is
  'unknown' rather than 'ruled out'; a low year followed by a missing year marks an
  unconfirmed collapse and censors all later origins; the trailing 24-year window must
  be completely observed for an origin to be eligible (gap-tolerant counts are a
  sensitivity, matching the state-space gap-handling analysis of Section 4.3).
* Census of GPDD (rgpdd bundle), FishGlob v2.1.0, RAM v4.41 proxy and the O'Brien 2023
  lake set; attrition tables; sensitivity to outcome/eligibility parameters.
* Preliminary crosswalk FishGlob×RAM and GPDD internal duplicates; crosswalk plan.
* Simulation-based power/precision gate implemented; grid running.
* Proposed (NOT frozen) Stage 0 parameter choices are listed in `reports/STAGE0_REPORT.md`.
