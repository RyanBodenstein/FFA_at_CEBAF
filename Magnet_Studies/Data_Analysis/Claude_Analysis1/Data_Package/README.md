# LDRD FFA@CEBAF Magnet Radiation Study — Data Package

## Study Overview

This data package contains the complete processed data and analysis results from
the LDRD (Laboratory Directed Research & Development) study of permanent magnet
radiation degradation in the Continuous Electron Beam Accelerator Facility
(CEBAF) at Jefferson Lab.

**Objective**: Measure radiation-induced demagnetization of permanent magnets
deployed in the CEBAF tunnel to determine whether Fixed Field Alternating-gradient
(FFA) accelerator magnets can survive the CEBAF radiation environment.

**Study period**: Baselines measured April–November 2024 (lab). Magnets deployed
in the CEBAF tunnel July 2025. Post-exposure measurements July 2025–January 2026.

**Scale**: 30 tunnel-deployed Y-plates, 9 lab control Y-plates, ~120 H-plate
pair assemblies, ~400 A-samples (individual magnets), spanning 7 accelerator
regions. This is the world's largest study of this type.

## Sample Description

### Y-plates (primary measurement)
Large single magnets measured with a Helmholtz coil fluxmeter. Each Y-plate
has 4 material slots, one each of N42EH, N52SH, SmCo33H, and SmCo35 (slot
assignments randomized). 30 plates deployed in the CEBAF tunnel; 9 plates
kept in the lab as unexposed controls.

### H-plates (pair assemblies)
Each H-plate contains 4 pair slots in one of four magnetic configurations
(Alpha, Beta, Gamma, Delta). NdFeB pairs are on "n" plates (Hn-XX-Y),
SmCo on "s" plates (Hs-XX-Y). Measured with Helmholtz coil.

### A-samples (individual magnets)
Pairs of small magnets measured together in a fixed enclosure, extracted from
H-plate assemblies. Named An-XX-Y-Z (NdFeB) or As-XX-Y-Z (SmCo), where
XX=plate, Y=slot, Z=pair index (1 or 2). The Delta configuration's 2nd
A-sample is a "slug" (calibration standard).

### Materials
| Material | Type | Br (kGs) | Max Temp (C) | alpha_Br (%/C) | Hci (kOe) |
|----------|------|----------|--------------|----------------|-----------|
| N42EH    | NdFeB | 12.8-13.2 | 190 | -0.10 | >=30 |
| N52SH    | NdFeB | 14.2-14.5 | 140 | -0.11 | >=19 |
| SmCo33H  | Sm2Co17 | 11.2-11.5 | 350 | -0.040 | >=25 |
| SmCo35   | Sm2Co17 | 11.6-12.0 | 300 | -0.040 | >=18 |

All magnets manufactured by Allstar Magnetics.

## Tunnel Locations
30 Y-plates deployed at 7 locations in the CEBAF tunnel:
- **Arcs** (20 plates): SE Arc (5), NE Arc (5), NW Arc (5), SW Arc (5) —
  grouped in lines of 5 at specific girders
- **Linacs** (8 plates): North Linac (4), South Linac (4) — at NDX locations
- **Labyrinths** (2 plates): North and South access labyrinths

Each Y-plate is co-located with one H-plate for cross-checking.

## Key Results

### Headline: NdFeB-SmCo Differential
**-0.208% +/- 0.028% (stat) -- 7.6 sigma significance**

This is the gain-immune intra-plate differential: within each plate, NdFeB
degraded more than SmCo. Because both materials share the same Helmholtz
measurement session, any instrument gain drift cancels exactly.

### Per-Material Mean Changes (tunnel Y-plates, temperature-corrected)
| Material | Mean Change (%) | Stat. Uncertainty (%) | Syst. Uncertainty (%) |
|----------|-----------------|-----------------------|-----------------------|
| N42EH    | -0.252 | +/-0.036 | +/-0.12 |
| N52SH    | -0.170 | +/-0.036 | +/-0.12 |
| SmCo33H  | +0.037 | +/-0.031 | +/-0.12 |
| SmCo35   | -0.044 | +/-0.031 | +/-0.12 |

### Lab Controls
Lab Y-plate NdFeB-SmCo differential: -0.007% +/- 0.038% (0.2 sigma) —
consistent with zero, confirming the tunnel signal is radiation-induced.
Tunnel-Lab difference: -0.202% +/- 0.047% (4.3 sigma).

### Dose-Degradation Correlation
- Gamma dose does NOT correlate with degradation (rho=0.21, p=0.27)
- Neutron dose shows significant correlation (rho=0.389, p=0.03)
- Position (line number) dominates: Line 1 shows most degradation but least dose

## Directory Guide

| Directory | Contents |
|-----------|----------|
| `01_Sample_Configuration/` | Material assignments, tunnel placements, sample inventory |
| `02_Magnetic_Measurements/` | Degradation results (Y, H, A), time series, temperature corrections |
| `03_Dosimetry/` | Cumulative dose data (OSL badges, optichromic rods, neutron) |
| `04_Results/` | Headline numbers, systematic error analysis, sensitivity studies |
| `05_Plots/` | All publication-quality figures organized by category |
| `06_Scripts/` | Python analysis scripts (reference copies) |
| `07_Reference_Documents/` | Material specs, instrument specs |

## How to Reproduce the Analysis

### Requirements
- Python 3.9+
- numpy, matplotlib, openpyxl, scipy

### Steps
1. The raw `.dat` measurement files (~52,000 files, ~100 MB) are in the parent
   directory structure (`Cleanup_Claude/Y_Plates/`, `Cleanup_Claude/Pair_Assemblies/`).
   These are NOT included in this package due to size.

2. Core analysis chain (run from `Cleanup_Claude/` directory):
   ```
   python3 manager_summary_v3.py          # Y-plate analysis + v3 plots
   python3 degradation_summary_v2.py      # H-plate analysis + v2 plots
   python3 manager_summary_v5_polish.py   # Combined Y+H+A analysis
   ```

3. Downstream analyses:
   ```
   python3 presentation_plots.py          # P1-P15 presentation figures
   python3 time_series_evolution.py       # T1-T7 time series plots
   python3 gain_systematic_analysis.py    # Gain systematic study
   python3 dose_degradation_correlation.py # Dose correlation analysis
   python3 Sensitivity_Analysis/temp_sensitivity.py
   python3 Sensitivity_Analysis/sample_type_comparison.py
   python3 unexposed_vs_exposed.py        # Lab vs tunnel comparison
   python3 within_session_drift.py        # WSD1-WSD4 drift validation
   ```

4. Dosimetry pipeline:
   ```
   python3 parse_area_dosimetry.py        # Parse OSL badge data
   python3 build_dose_map.py              # Build per-plate dose map
   python3 Rod_Dosimetry/parse_aidata.py  # Parse AIdata rod readings
   python3 Rod_Dosimetry/parse_rod_spreadsheet.py
   python3 Rod_Dosimetry/rod_mapping.py
   python3 Rod_Dosimetry/build_merged_dose.py
   python3 Rod_Dosimetry/rod_dose_correlation.py
   python3 Rod_Dosimetry/rod_crosscheck.py
   ```

5. Export this data package:
   ```
   python3 export_data_package.py         # Generates all CSVs in Data_Package/
   ```

## Quick Reproduction from CSVs

To verify the headline results without running the full analysis pipeline,
use the standalone verification script:

```
cd Data_Package/
python3 06_Scripts/verify_results.py
```

This script reads only the package CSVs and reproduces all 21 headline numbers
(differential, lab control, per-material means, dose correlations, uncertainties).

### Step-by-step: Computing the differential by hand

1. Load `02_Magnetic_Measurements/y_plate_degradation.csv`
2. Filter to `environment == "tunnel"` and `is_outlier == False` (118 samples)
3. For each plate, compute:
   - `NdFeB_mean = mean(N42EH pct_change, N52SH pct_change)` for that plate
   - `SmCo_mean  = mean(SmCo33H pct_change, SmCo35 pct_change)` for that plate
   - `differential = NdFeB_mean - SmCo_mean`
   - Note: outlier plates (34, 40) each have one flagged slot excluded,
     leaving 3 samples. The remaining slots still contribute to the
     per-plate averages.
4. Take the mean of all 30 differentials: -0.208%
5. SEM = std(30 differentials, ddof=1) / sqrt(30) = 0.028%
6. Significance = |mean| / SEM = 7.6 sigma

For lab controls, repeat with `environment == "lab"` (9 plates, 36 samples).

## Sentinel Values
- `1337` or `1337.0` in measurement data = no valid reading (sensor error or
  missing measurement)

## Temperature Correction
All Helmholtz readings are corrected to a reference temperature of 20.0 C using:
```
H_corrected = H_raw / (1 + alpha * (T_measured - 20.0))
```
where alpha is the material's temperature coefficient of remanence (alpha_Br).
Pre-deployment Y-plate temperatures use calibrated estimates (see
`02_Magnetic_Measurements/temperature_corrections.csv` and
`04_Results/probe_bias_assessment.txt`).

## Data Provenance
All CSVs in this package were generated by `export_data_package.py` from the
same analysis scripts that produced the published results. The export script
imports directly from `manager_summary_v3.py`, `degradation_summary_v2.py`,
and `manager_summary_v5_polish.py` — there is no manual data entry.

## Contact
[Placeholder for PI contact information]

## Citation
[Placeholder for publication reference]

---
*Package generated 2026-05-12 by export_data_package.py. Within-session drift analysis (WSD1-WSD4) added 2026-06-04.*
