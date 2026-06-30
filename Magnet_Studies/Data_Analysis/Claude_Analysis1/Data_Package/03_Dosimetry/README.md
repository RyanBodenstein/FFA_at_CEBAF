# 03_Dosimetry

Radiation dose measurements from three independent systems: OSL badges
(Landauer), optichromic rods (AIdata), and CR-39 neutron track-etch detectors.

## Files

### plate_cumulative_dose.csv
Cumulative photon and neutron dose per plate from AIdata optichromic rod
measurements. AIdata units are REM (converted from native units).

**Source**: `Rod_Dosimetry/parse_aidata.py`

### merged_dose_final.csv
**Authoritative dose file**. Merges AIdata, OSL, and rod dosimetry using a
cascading decision tree (AIdata preferred when available, OSL as supplement,
rod data to fill gaps). True gamma dose range: 0.3 Gy (labyrinth) to
23,451 Gy (Y-22, North Linac).

**Source**: `Rod_Dosimetry/build_merged_dose.py`

### master_doses.csv
Complete OSL badge database from Landauer radiation monitoring reports. Contains
1,677 rows spanning all monitoring periods. Most OSL elements at high-dose
locations are saturated (>1000 rad), making these lower bounds.

**Source**: `parse_area_dosimetry.py`

### rod_doses.csv
Optichromic rod dosimetry measurements. 495 of 1,358 LDRD rods have valid
readings (2-726 krad). Rods are identified by R-### numbers.

**Source**: `Rod_Dosimetry/parse_rod_spreadsheet.py`

### neutron_breakdown.csv
Thermal vs. fast neutron dose decomposition from OSL CR-39 track-etch
detectors. "M" flags indicate minimum detectable level (not a real reading).

**Source**: `parse_pdf_neutron.py`

### dose_vs_degradation.csv
Pre-merged dataset for dose-degradation correlation analysis. Each row is one
tunnel Y-plate with its dose measurements and per-material degradation values.
The `intra_plate_diff` column gives the gain-immune NdFeB-SmCo differential.

**Source**: `Rod_Dosimetry/rod_dose_correlation.py`

### rod_dose_degradation.csv
Extended dose-degradation merge with uncertainty columns. Includes per-plate
dose uncertainties (`ai_sigma_photon_gy`), per-material baseline SEMs
(`sem_N42EH`, etc.), propagated uncertainties (`sigma_ndfeb_pct`,
`sigma_smco_pct`, `sigma_diff_pct`), and CR-39 fast/thermal neutron breakdown
(`osl_nt_mrem`, `osl_nf_mrem`). 9 OSL-matched plates use 10% Landauer
stated accuracy; 21 rod-derived plates carry Kirsten's propagated sigma.

**Source**: `Rod_Dosimetry/rod_dose_correlation.py`

### rod_uncertainty_budget.csv
Per-plate uncertainty budget with dose uncertainty (Gy and %), uncertainty
source classification (`rod_propagated` or `Landauer_10pct`), and propagated
degradation uncertainties for NdFeB mean, SmCo mean, and differential.

**Source**: `Rod_Dosimetry/rod_uncertainty_analysis.py`

## Key Finding
Gamma dose does NOT correlate with degradation (Spearman rho=0.21, p=0.27).
Neutron dose shows significant correlation (rho=0.389, p=0.03 for differential;
rho=0.459, p=0.01 for NdFeB-only). Position (line number) dominates:
Line 1 shows most degradation but receives the least dose (inverted).

See `04_Results/rod_correlation_stats.txt` for full statistical analysis.

## Dose Units
- **rem** (Roentgen Equivalent Man): dose equivalent; 1 rem = 0.01 Sv
- **mrem**: millirems; 1000 mrem = 1 rem
- **Gy** (Gray): absorbed dose; 1 Gy = 100 rad
- **krad**: kilorads; 1 krad = 10 Gy
- Conversion (photons): 1 rem ≈ 0.01 Gy (quality factor ≈ 1)
