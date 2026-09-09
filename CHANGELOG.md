# CHANGELOG

## 2026-09-09 — Stage 0 (feasibility) — no frozen parameters

* Added collapse-onset and forecast-origin label code with tests (`src/census/labels.py`).
  Clarification recorded for Stage 1: a negative label at origin t requires that an
  onset be RULED OUT at every year t+1..t+5, which in the edge case where x_{t+5} is
  below threshold needs x_{t+6}; the draft wording "observed through t+5" is slightly
  weaker. Implemented the stricter exact-ascertainment rule.
* Clarification recorded for Stage 1: alarm episodes — a new episode may start only
  when more than `horizon` years have elapsed since the previous episode start
  (t − t0 > 5); an episode is true iff it starts at a positive origin.
* Census of GPDD (rgpdd bundle), FishGlob v2.1.0, RAM v4.41 proxy and the O'Brien 2023
  lake set; attrition tables; sensitivity to outcome/eligibility parameters.
* Preliminary crosswalk FishGlob×RAM and GPDD internal duplicates; crosswalk plan.
* Simulation-based power/precision gate implemented; grid running.
* Proposed (NOT frozen) Stage 0 parameter choices are listed in `reports/STAGE0_REPORT.md`.
