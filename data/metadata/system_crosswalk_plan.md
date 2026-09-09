# Canonical system identity (`system_id`) and deduplication plan — Stage 0 proposal

Status: PROPOSED (Stage 0). To be frozen at the Stage 1 protocol freeze after the
blinded manual audit (human checkpoint 2 in PROTOCOL Section 17).

## 1. Definition

A `system_id` denotes one biological population (or assessed stock) at one
defined site/area, measured by one or more records in one or more source
databases. All records that measure the same population, or populations that
are demographically nested (e.g., a survey index of a stock and the assessment
biomass of the same stock; a sub-area count and the whole-area count), share a
`system_id` or are linked by a `depends_on` edge. Linked records must always
fall in the same partition (development / calibration / evaluation; CV fold;
leave-one-dataset-out fold).

`system_id` format: `<realm>|<taxon_key>|<area_key>` where
* `taxon_key` = WoRMS AphiaID for marine taxa, GBIF usage key otherwise (fallback: normalized binomial);
* `area_key` = RAM `stockid` where a RAM stock exists; otherwise the survey unit (FishGlob `survey_unit`), GPDD `LocationID`, LPD population id, or BioTIME study×site.

## 2. Matching rules (applied in order; every rule logs its evidence)

| Rule | Sources | Evidence | Outcome |
|---|---|---|---|
| R1 identical identifier | RAM↔ICES SAG (`stockid`/ICES stock code), LPD↔GPDD (LPD `source` cites GPDD; GPDD `DataSourceID`) | exact id or citation | same `system_id` |
| R2 species + stock boundary | FishGlob survey_unit × species ↔ RAM stock | species AphiaID match AND survey footprint intersects the RAM stock boundary polygon (cfree14/ram_boundaries or RAM `areaid`) | `depends_on` (survey index of the assessed stock) |
| R3 species + region string | FishGlob ↔ RAM when no boundary is available | species match AND survey region ↔ RAM `region` map (`src/dedup/crosswalk_prelim.py`) | candidate; manual audit |
| R4 taxon + coordinates | GPDD, LPD, BioTIME | same taxon key AND site centroids within 50 km (haversine) AND overlapping years | candidate; manual audit |
| R5 taxon + location + life stage | GPDD internal | same `TaxonID` × `LocationID` (multiple `MainID`: life stages, generations, protocols) | same `system_id`; keep one primary record (rule: longest annual, highest reliability) |
| R6 published-set membership | lake challenge sets, Burthe 2016 series, Bury/EWSNet empirical sets | series name/reference match | flag `in_published_ews_set`; never in development if used for a challenge analysis |

Only metadata (identifiers, taxonomy, coordinates, years, references) are used;
abundance values are never compared, so no outcome information enters matching.

## 3. Blinded manual audit

Candidates from R3–R4 are listed with identifiers and metadata only (no
abundance, no labels) and adjudicated by a human before feature computation.
Decisions (`same`, `dependent`, `distinct`, `uncertain`) and reasons are logged
in `data/metadata/crosswalk_decisions.csv`. `uncertain` pairs are linked
(conservative) in the primary analysis and unlinked in a robustness analysis
(PROTOCOL Section 13, "removal of records with uncertain duplicate identity").

## 4. Preliminary results (Stage 0, proxy data)

From `data/metadata/crosswalk_prelim_summary.json`:

* FishGlob (261 series with eligible origins, 180 species) vs RAM v4.41 proxy (328 stocks):
  39 species are shared in some region; 44 FishGlob series have a species+region
  candidate match to 82 RAM stocks (89 candidate pairs). With the full RAM
  release the number of dependent pairs will be larger; expect most long FishGlob
  series of commercial species (NS-IBTS, NEUS, EBS, GMEX) to be dependent on a
  RAM stock. Consequence: FishGlob and RAM cannot be treated as independent
  evidence for those species; they must share partitions and the
  leave-one-dataset-out analysis must drop dependent records from the training
  side.
* GPDD internal: 274 taxon×location groups contain more than one MainID; 21 of
  the 280 eligible annual series sit in such groups; 27 eligible pairs of the
  same taxon lie within 50 km at different LocationIDs. Eligible GPDD series
  concentrate in a few data sources (DataSourceID 12: 84 series; 301: 39; 590: 32;
  762: 23), i.e., they are far from independent (same monitoring programme,
  same observers, often the same island or reserve).
* FishGlob internal: species within one survey_unit share survey-level shocks
  (gear/vessel changes, footprint trimming). Cluster bootstrap by survey_unit
  is proposed as a robustness analysis, and survey_unit is a stratification
  variable for partitioning.

## 5. Tests (to implement in Stage 2)

* every record maps to exactly one `system_id`;
* no `system_id` (or `depends_on` component) spans two partitions or two CV folds;
* published challenge-set records are excluded from development partitions;
* crosswalk decisions are reproducible from `crosswalk_decisions.csv` and the rule log.
