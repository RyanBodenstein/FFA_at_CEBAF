# Data Dictionary

Every CSV column in this data package is described below. Files are grouped
by directory. All values are in SI-compatible units unless noted otherwise.

---

## 01_Sample_Configuration/

### materials_arrangements.csv
Material assignment for every magnet slot, parsed from Materials_Arrangements.xlsx.

| Column | Type | Description |
|--------|------|-------------|
| sample_id | string | Unique sample identifier (e.g., "Y-15-1", "Hn-6-2", "An-6-2-1") |
| plate_number | int | Plate number (1-40 for Y; varies for H/A) |
| slot_number | int | Slot position within the plate (1-4) |
| material | string | Magnet material grade: N42EH, N52SH, SmCo33H, or SmCo35 (Y-plates); NdFeB or SmCo (H/A) |
| sample_type | string | "Y" (Y-plate), "H" (H-plate pair), or "A" (A-sample individual magnet) |
| environment | string | "tunnel" (deployed in CEBAF) or "lab" (unexposed control) |

### tunnel_placements.csv
Physical location of each tunnel-deployed Y-plate and its co-located H-plate.

| Column | Type | Description |
|--------|------|-------------|
| plate_number | int | Y-plate number (1-40, 30 tunnel plates) |
| y_plate | string | Y-plate label (e.g., "Y15") |
| h_plate | string | Co-located H-plate label (e.g., "N10", "S12") |
| region | string | Accelerator region: NE Arc, NW Arc, SE Arc, SW Arc, North Linac, South Linac, or Labyrinth |
| sub_location | string | Specific location within region (e.g., "upstream Girder 27", "NL NDX @ Girder 5") |
| line_position | int | Position within a line of 5 plates (1-5 for arcs; 0 for linacs/labyrinths) |

### sample_inventory.csv
Comprehensive list of every sample with its type, material, location, and configuration.

| Column | Type | Description |
|--------|------|-------------|
| sample_id | string | Unique identifier (Y-XX-S, Hn/Hs-XX-S, An/As-XX-S-P) |
| sample_type | string | "Y", "H", or "A" |
| material | string | Material grade (4 grades for Y; NdFeB/SmCo for H/A) |
| plate | int | Plate number |
| slot | int | Slot number (1-4) |
| environment | string | "tunnel" or "lab" |
| region | string | Accelerator region (empty for lab samples) |
| config | string | Magnetic configuration for H/A: Alpha, Beta, Gamma, Delta (empty for Y-plates) |

---

## 02_Magnetic_Measurements/

### y_plate_degradation.csv
Primary degradation results for all 39 Y-plates (30 tunnel + 9 lab).
Source: `manager_summary_v3.load_all()` (tunnel) and `manager_summary_v5_polish.load_lab_y_plates()` (lab).

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| plate | int | — | Plate number |
| slot | int | — | Slot number (1-4) |
| sample_id | string | — | e.g., "Y-15-1" |
| material | string | — | N42EH, N52SH, SmCo33H, or SmCo35 |
| region | string | — | Accelerator region (empty for lab) |
| line_position | int | — | Position in line of 5 (0 for non-arc / lab) |
| environment | string | — | "tunnel" or "lab" |
| baseline_mean_mWC | float | mWC | Mean pre-deployment Helmholtz reading, temperature-corrected to 20 C. 0.0 for lab plates (not stored). |
| latest_mWC | float | mWC | Latest post-deployment reading, temperature-corrected. 0.0 for lab plates. |
| pct_change | float | % | (latest - baseline) / baseline * 100. Negative = demagnetization. |
| baseline_sem_pct | float | % | Standard error of the mean baseline, as % of baseline. 0.0 for lab. |
| n_baseline | int | — | Number of baseline readings used |
| n_baseline_sessions | int | — | Number of distinct measurement dates in baseline |
| is_outlier | bool | — | True for Y-34-4 and Y-40-4 (known bad baselines) |

**Valid ranges**: pct_change typically [-2%, +1%]. baseline_mean_mWC > 0.1 (filter applied).
**Sentinel**: 1337 in raw data means no valid measurement; these are excluded before export.

### h_plate_degradation.csv
H-plate (pair assembly) degradation results.
Source: `degradation_summary_v2.compute_h_plate_degradation()`.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| pair_id | string | — | e.g., "Hn-6-2" (NdFeB plate 6, slot 2) or "Hs-1-3" (SmCo plate 1, slot 3) |
| plate | int | — | Plate number |
| slot | int | — | Slot number (1-4) |
| material | string | — | "NdFeB" or "SmCo" (class-level, not grade) |
| region | string | — | Accelerator region |
| config | string | — | Alpha, Beta, Gamma, or Delta |
| baseline_mean | float | mWC | Mean pre-deployment Helmholtz, temperature-corrected to 20 C |
| latest_mean | float | mWC | Latest tunnel reading, temperature-corrected |
| pct_change | float | % | (latest - baseline) / baseline * 100 |
| n_baseline | int | — | Number of baseline readings |
| environment | string | — | Always "tunnel" in this export |
| is_outlier | bool | — | True if |pct_change| > 5% or (n_baseline=1 and |pct_change| > 2%) |

**Note**: Beta configuration (antiparallel) produces unreliable H-level readings.
Alpha and Gamma configurations are most reliable.

### a_sample_degradation.csv
A-sample (individual magnet pair) degradation results.
Source: `manager_summary_v5_polish.load_a_sample_helmholtz()`.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| assembly_id | string | — | e.g., "An-6-2-1" (NdFeB plate 6, slot 2, pair 1) |
| plate | int | — | Plate number |
| slot | int | — | H-plate slot (1-4) |
| pair | int | — | Pair index within slot (1 or 2). Delta config pair 2 = slug. |
| material | string | — | "NdFeB" or "SmCo" |
| region | string | — | Accelerator region |
| baseline_mean | float | mWC | Mean pre-deployment Helmholtz, temperature-corrected |
| latest_mean | float | mWC | Latest reading, temperature-corrected |
| pct_change | float | % | Percentage change from baseline |
| n_baseline | int | — | Number of baseline readings |
| temp_corrected | bool | — | True if temperature correction was applied |
| environment | string | — | "tunnel" |
| is_outlier | bool | — | Flagged by same criteria as H-plates |

### y_plate_time_series.csv
Per-date percentage change for each tunnel Y-plate sample across all
post-deployment measurement sessions.
Source: `date_pcts` from `manager_summary_v3.load_all()` results.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| plate | int | — | Plate number |
| slot | int | — | Slot number (1-4) |
| sample_id | string | — | e.g., "Y-15-1" |
| material | string | — | Material grade |
| region | string | — | Accelerator region |
| date | string | — | Measurement date (YYYY-MM-DD), post-deployment only |
| pct_change | float | % | Change relative to pre-deployment baseline on this date |

### temperature_corrections.csv
Temperature data and correction details for every (sample, date) pair with
Teslameter temperature readings.
Source: `temp_final` dict from `manager_summary_v3.load_all()`.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| sample_id | string | — | Y-plate sample ID |
| date | string | — | Measurement date (YYYY-MM-DD) |
| probe_temp_C | float | C | Mean temperature from Teslameter probe on this date |
| corrected_temp_C | float | C | Temperature used for correction (may differ from probe for pre-deployment dates) |
| temp_uncertainty_C | float | C | Uncertainty on the corrected temperature |
| correction_source | string | — | "Y_BASELINE_TEMP_LOOKUP" (calibrated estimate) or "teslameter_probe" (direct reading) |
| alpha_used | string | — | Temperature coefficient used (e.g., "-0.001"), or empty if not a Y-plate slot |

---

## 03_Dosimetry/

### plate_cumulative_dose.csv
Cumulative radiation dose from AIdata (optichromic rod) measurements per plate.
Source: `Rod_Dosimetry/parse_aidata.py`.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| plate | int | — | Plate number |
| is_lab | bool | — | True for lab control plates |
| final_date | string | — | Date of last AIdata measurement |
| days_since_install | int | days | Days between install and last reading |
| photon_cum_rem | float | rem | Cumulative photon dose |
| sigma_photon_rem | float | rem | Uncertainty on photon dose |
| neutron_cum_rem | float | rem | Cumulative neutron dose |
| sigma_neutron_rem | float | rem | Uncertainty on neutron dose |
| photon_cum_gy | float | Gy | Photon dose in Gray (1 rem ≈ 0.01 Gy for photons) |
| n_measurements | int | — | Number of measurement campaigns |

### merged_dose_final.csv
Authoritative dose for each plate, merging AIdata (rods), OSL badges, and
rod dosimetry with a cascading decision tree.
Source: `Rod_Dosimetry/build_merged_dose.py`.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| plate | int | — | Plate number |
| is_lab | bool | — | True for lab |
| gamma_dose_rem | float | rem | Best-estimate gamma dose |
| gamma_dose_gy | float | Gy | Gamma dose in Gray |
| gamma_sigma_rem | float | rem | Gamma dose uncertainty |
| gamma_source | string | — | Data source for gamma ("aidata", "osl", "rod") |
| neutron_dose_rem | float | rem | Best-estimate neutron dose |
| neutron_sigma_rem | float | rem | Neutron dose uncertainty |
| neutron_source | string | — | Data source for neutron |
| beta_dose_mrem | float | mrem | Beta dose from OSL |
| osl_body_mrem | float | mrem | OSL body dose (often saturated) |
| osl_photon_mrem | float | mrem | OSL photon dose |
| osl_neutron_mrem | float | mrem | OSL neutron dose (CR-39 track etch) |
| osl_n_saturated | int | — | Number of saturated OSL elements |
| osl_is_lower_bound | bool | — | True if OSL dose is a lower bound (saturated) |
| ai_days_since_install | int | days | AIdata deployment duration |
| ai_n_measurements | int | — | Number of AIdata campaigns |

### master_doses.csv
Full OSL badge database from Landauer reports.
Source: `parse_area_dosimetry.py`.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| report_date | string | — | Landauer report date |
| part_nbr | string | — | Badge part number |
| badge_number | string | — | Badge serial number |
| badge_type | string | — | Badge type code |
| badge_location | string | — | Physical location description |
| begin_wear | string | — | Wear period start date |
| end_wear | string | — | Wear period end date |
| monitoring_period | string | — | Monitoring period identifier |
| skin_mrem | float | mrem | Skin dose |
| body_mrem | float | mrem | Body (deep) dose |
| eye_mrem | float | mrem | Eye (lens) dose |
| beta_mrem | float | mrem | Beta dose |
| neutron_mrem | float | mrem | Neutron dose (CR-39) |
| note_code | string | — | Landauer note code |
| note_message | string | — | Note text |
| exceeded_1000rad | bool | — | True if dose exceeded 1000 rad |
| saturated_osl | bool | — | True if OSL element saturated |
| neutron_exceeded | bool | — | True if neutron exceeded range |
| irregular_exposure | bool | — | True if irregular exposure pattern |
| location | string | — | Mapped LDRD location |
| location_source | string | — | How location was determined |

### rod_doses.csv
Optichromic rod dosimetry measurements.
Source: `Rod_Dosimetry/parse_rod_spreadsheet.py`.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| row_num | int | — | Row number in source spreadsheet |
| project | string | — | Project identifier |
| location | string | — | Rod location |
| rod_id | string | — | Unique rod identifier (R-###) |
| is_ldrd | bool | — | True if this rod belongs to the LDRD study |
| range | string | — | Dose range category |
| date_read | string | — | Date the rod was read |
| od_600nm_1, od_600nm_2 | float | — | Optical density readings at 600 nm |
| od_656nm_1, od_656nm_2 | float | — | Optical density readings at 656 nm |
| dose_600_1_krad, dose_600_2_krad | float | krad | Dose from 600 nm readings |
| dose_656_1_krad, dose_656_2_krad | float | krad | Dose from 656 nm readings |
| avg_dose_600_krad | float | krad | Average dose from 600 nm |
| avg_dose_656_krad | float | krad | Average dose from 656 nm |
| flag_600, flag_656 | string | — | Quality flags |
| best_dose_krad | float | krad | Best-estimate dose |
| best_source | string | — | Which wavelength was used for best estimate |
| notes | string | — | Additional notes |

### neutron_breakdown.csv
Neutron dose decomposition from OSL reports (thermal vs. fast).
Source: `parse_pdf_neutron.py`.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| report_date | string | — | Report date |
| part_nbr | string | — | Badge part number |
| nt_mrem | float | mrem | Thermal neutron dose |
| nf_mrem | float | mrem | Fast neutron dose |
| nt_is_M | bool | — | True if thermal neutron reading is "M" (minimum detectable) |
| nf_is_M | bool | — | True if fast neutron is minimum detectable |
| neutron_exceeded | bool | — | True if exceeded range |

### dose_vs_degradation.csv
Merged dose and degradation data for correlation analysis.
Source: `Rod_Dosimetry/rod_dose_correlation.py`.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| plate | int | — | Plate number |
| plate_label | string | — | Plate label (e.g., "Y15") |
| region | string | — | Accelerator region |
| sub_location | string | — | Specific location |
| line | int | — | Line position |
| ai_photon_rem | float | rem | AIdata photon dose |
| ai_photon_gy | float | Gy | AIdata photon dose in Gray |
| ai_neutron_rem | float | rem | AIdata neutron dose |
| ai_sigma_photon_rem | float | rem | Photon dose uncertainty |
| osl_body_mrem | float | mrem | OSL body dose |
| osl_photon_mrem | float | mrem | OSL photon dose |
| osl_neutron_mrem | float | mrem | OSL neutron dose |
| osl_n_saturated | int | — | Saturated OSL elements |
| osl_is_lower_bound | bool | — | OSL dose is lower bound |
| N42EH_pct | float | % | N42EH degradation |
| N52SH_pct | float | % | N52SH degradation |
| SmCo33H_pct | float | % | SmCo33H degradation |
| SmCo35_pct | float | % | SmCo35 degradation |
| ndfeb_mean_pct | float | % | Mean NdFeB degradation |
| smco_mean_pct | float | % | Mean SmCo degradation |
| intra_plate_diff | float | % | NdFeB mean - SmCo mean (gain-immune) |

### rod_dose_degradation.csv
Extended dose-degradation merge with uncertainty columns and fast/thermal neutron
breakdown. Superset of `dose_vs_degradation.csv` with additional fields from
Task 22 (uncertainty propagation) and T1-8 (fast/thermal neutron).
Source: `Rod_Dosimetry/rod_dose_correlation.py`.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| plate | int | — | Plate number |
| plate_label | string | — | Plate label (e.g., "Y-15") |
| region | string | — | Accelerator region |
| sub_location | string | — | Specific location |
| line | int | — | Line position |
| ai_photon_rem | float | rem | AIdata photon dose |
| ai_photon_gy | float | Gy | AIdata photon dose in Gray |
| ai_neutron_rem | float | rem | AIdata neutron dose |
| ai_sigma_photon_rem | float | rem | Photon dose uncertainty (Kirsten's propagated sigma; 0 for OSL-matched plates) |
| ai_sigma_neutron_rem | float | rem | Neutron dose uncertainty |
| ai_sigma_photon_gy | float | Gy | Photon dose uncertainty in Gray (10% Landauer fallback for OSL-matched plates) |
| osl_body_mrem | float | mrem | OSL body dose |
| osl_photon_mrem | float | mrem | OSL photon dose |
| osl_neutron_mrem | float | mrem | OSL total neutron dose (CR-39) |
| osl_nt_mrem | float | mrem | OSL thermal neutron dose (CR-39 track-etch) |
| osl_nf_mrem | float | mrem | OSL fast neutron dose (CR-39 track-etch) |
| osl_n_saturated | int | — | Number of saturated OSL elements |
| osl_is_lower_bound | bool | — | True if OSL dose is lower bound (saturated) |
| N42EH_pct | float | % | N42EH degradation |
| N52SH_pct | float | % | N52SH degradation |
| SmCo33H_pct | float | % | SmCo33H degradation |
| SmCo35_pct | float | % | SmCo35 degradation |
| ndfeb_mean_pct | float | % | Mean NdFeB degradation (average of N42EH and N52SH) |
| smco_mean_pct | float | % | Mean SmCo degradation (average of SmCo33H and SmCo35) |
| intra_plate_diff | float | % | NdFeB mean - SmCo mean (gain-immune differential) |
| sem_N42EH | float | % | Baseline SEM for N42EH on this plate |
| sem_N52SH | float | % | Baseline SEM for N52SH on this plate |
| sem_SmCo33H | float | % | Baseline SEM for SmCo33H on this plate |
| sem_SmCo35 | float | % | Baseline SEM for SmCo35 on this plate |
| sigma_ndfeb_pct | float | % | Propagated NdFeB mean SEM = sqrt(sem_N42EH^2 + sem_N52SH^2) / 2 |
| sigma_smco_pct | float | % | Propagated SmCo mean SEM |
| sigma_diff_pct | float | % | Propagated differential SEM = sqrt(sigma_ndfeb^2 + sigma_smco^2) |

### rod_uncertainty_budget.csv
Per-plate uncertainty budget combining dose and degradation uncertainties.
Source: `Rod_Dosimetry/rod_uncertainty_analysis.py`.

| Column | Type | Units | Description |
|--------|------|-------|-------------|
| plate | int | — | Plate number |
| plate_label | string | — | Plate label |
| region | string | — | Accelerator region |
| dose_gy | float | Gy | Best-estimate photon dose |
| sigma_dose_gy | float | Gy | Dose uncertainty in Gray |
| sigma_dose_pct | float | % | Dose uncertainty as percentage of dose |
| sigma_source | string | — | "rod_propagated" (21 plates, Kirsten's sigma) or "Landauer_10pct" (9 OSL-matched plates) |
| ndfeb_pct | float | % | NdFeB mean degradation |
| sigma_ndfeb | float | % | NdFeB degradation SEM |
| smco_pct | float | % | SmCo mean degradation |
| sigma_smco | float | % | SmCo degradation SEM |
| diff_pct | float | % | NdFeB-SmCo differential |
| sigma_diff | float | % | Differential SEM |

---

## 04_Results/

### headline_results.csv
Machine-readable summary of key results.
Source: `export_data_package.py`.

| Column | Type | Description |
|--------|------|-------------|
| metric | string | Result identifier (e.g., "NdFeB_minus_SmCo_differential_pct") |
| value | float | Central value |
| uncertainty | float | Statistical uncertainty (0 if not applicable) |
| significance | string | Statistical significance (e.g., "7.6 sigma") |
| notes | string | Description and sample size |

---

## Notes

### Units
- **mWC**: milliWeber-centimeter (Helmholtz coil flux integral; proportional to magnetic moment)
- **mrem**: millirem (radiation dose equivalent; 1 rem = 10 mSv)
- **Gy**: Gray (absorbed dose; 1 Gy = 100 rad)
- **krad**: kilorad (1 krad = 10 Gy)
- **%**: Percentage change from baseline
- **C**: Degrees Celsius

### Boolean Values
Boolean columns are stored as Python string representations: "True" or "False".

### Missing Data
Empty strings indicate unavailable data. Numeric fields may be 0.0 when the
underlying data was not stored by the analysis pipeline (noted in column descriptions).
