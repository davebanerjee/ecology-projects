# data/raw

Raw data are never committed. Stage 0 used the following retrieval routes
(details, checksums and licences in `MANIFEST.json`):

| Source | Route used in Stage 0 | Status |
|---|---|---|
| FishGlob v2.1.0 | `git clone https://github.com/AquaAuma/FishGlob_data` (outputs/Cleaned_data/*_std_clean.RData) | retrieved |
| GPDD v2010 (rgpdd bundle) | `git clone https://github.com/ropensci/rgpdd` (data/*.rda) | retrieved |
| RAM Legacy v4.41 extract (proxy) | `git clone https://github.com/cfree14/sst_recruitment` (data/ramldb/data/ramldb_stock_recruit_data.Rdata) | retrieved (proxy only) |
| RAM Legacy current release (Zenodo) | https://www.ramlegacy.org / Zenodo | BLOCKED by egress policy; human download required |
| Living Planet Database | https://livingplanetindex.org/data_portal | BLOCKED; requires human acceptance of terms |
| BioTIME 2.0 | https://doi.org/10.5281/zenodo.10932823 | BLOCKED by egress policy |
| ICES DATRAS / SAG | https://datras.ices.dk | BLOCKED by egress policy |
| Lake challenge (O'Brien et al. 2023) | `git clone https://github.com/duncanobrien/ews-assessments` (Data/) | retrieved (7 public lakes; 2 restricted) |
| Bury et al. 2021 classifiers | `git clone https://github.com/ThomasMBury/deep-early-warnings-pnas` | retrieved (CC BY-NC-SA 4.0) |
