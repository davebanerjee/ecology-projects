# CHANGELOG

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
