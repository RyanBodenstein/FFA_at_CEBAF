# 06_Scripts

Reference copies of all Python analysis scripts. These are organized by
function but are **not directly executable** from this directory — import
paths reference the original `Cleanup_Claude/` layout.

**To execute**: Run from the `Cleanup_Claude/` directory in the parent
repository. See the main README.md for execution order.

## Requirements
- Python 3.9+
- numpy, matplotlib, openpyxl, scipy

## Script Organization

### core/ — Primary Analysis
| Script | Function | Outputs |
|--------|----------|---------|
| manager_summary_v3.py | Y-plate Helmholtz analysis with v3 temp correction | `load_all()`, gain systematic, Manager_Plots/v3_*.png |
| degradation_summary_v2.py | H-plate analysis, temperature lookup, robust baselines | `compute_h_plate_degradation()`, TempCorrected_Plots/ |
| manager_summary_v5_polish.py | Combined Y+H+A analysis, lab controls, polished plots | A-sample loading, lab Y-plate loading, Manager_Plots_v5/ |

### analysis/ — Downstream Analyses
| Script | Function | Outputs |
|--------|----------|---------|
| presentation_plots.py | Publication figures P1-P14 | Presentation_Plots/P*.png |
| time_series_evolution.py | Time-resolved degradation T1-T7 | Time_Series/T*.png |
| dose_degradation_correlation.py | Dose-degradation correlation | (integrated into rod_dose_correlation.py) |
| gain_systematic_analysis.py | Helmholtz gain drift study | stdout report |
| unexposed_vs_exposed.py | Lab vs tunnel comparison U1-U3 | Unexposed_vs_Exposed/U*.png |

### dosimetry/ — OSL Badge Processing
| Script | Function | Outputs |
|--------|----------|---------|
| parse_area_dosimetry.py | Parse Landauer OSL reports | master_doses.csv, neutron_breakdown.csv |
| build_dose_map.py | Build per-plate dose map from OSL | plate dose maps |

### rod_dosimetry/ — Rod Dosimetry Pipeline
| Script | Function | Outputs |
|--------|----------|---------|
| parse_aidata.py | Parse AIdata rod readings | aidata_cumulative.csv, aidata_timeline.csv |
| parse_rod_spreadsheet.py | Parse optichromic rod spreadsheet | rod_doses.csv |
| rod_mapping.py | Map rods to LDRD plates | rod_plate_map.csv |
| build_merged_dose.py | Merge dose sources (AIdata+OSL+rod) | merged_dose_final.csv |
| rod_dose_correlation.py | Dose-degradation correlations | rod_dose_degradation.csv, R1-R5 plots |
| rod_crosscheck.py | Cross-check dose sources | crosscheck plots |

### sensitivity/ — Sensitivity Studies
| Script | Function | Outputs |
|--------|----------|---------|
| temp_sensitivity.py | Temperature assumption sensitivity | S1 plot, sensitivity_results.txt |
| sample_type_comparison.py | Cross-type comparison | S2-S3 plots, sample_type_results.txt |

### lab_controls/ — Lab Control Analysis
| Script | Function | Outputs |
|--------|----------|---------|
| lab_ha_analysis.py | Lab H/A-plate analysis, temperature helpers | Lab control data |

### export_data_package.py
Generates all new CSVs in this Data_Package by importing from the core scripts.

## Dependency Tree
```
manager_summary_v3.py (standalone)
  └─> manager_summary_v5.py
       └─> manager_summary_v5_polish.py
            ├── imports from manager_summary_v3
            ├── imports from degradation_summary_v2
            └── imports from manager_summary_v5

degradation_summary_v2.py (standalone)

presentation_plots.py
  ├── imports from manager_summary_v3
  ├── imports from degradation_summary_v2
  └── imports from manager_summary_v5_polish

time_series_evolution.py
  └── imports from manager_summary_v3

unexposed_vs_exposed.py
  ├── imports from manager_summary_v3
  └── imports from manager_summary_v5_polish

export_data_package.py
  ├── imports from manager_summary_v3
  ├── imports from degradation_summary_v2
  └── imports from manager_summary_v5_polish
```

## Execution Order
1. Core: `manager_summary_v3.py` → `degradation_summary_v2.py`
2. Combined: `manager_summary_v5_polish.py`
3. Dosimetry: `parse_area_dosimetry.py` → `build_dose_map.py` →
   `Rod_Dosimetry/parse_aidata.py` → `Rod_Dosimetry/parse_rod_spreadsheet.py` →
   `Rod_Dosimetry/rod_mapping.py` → `Rod_Dosimetry/build_merged_dose.py` →
   `Rod_Dosimetry/rod_dose_correlation.py`
4. Analysis: `presentation_plots.py`, `time_series_evolution.py`,
   `gain_systematic_analysis.py`, `unexposed_vs_exposed.py`,
   `Sensitivity_Analysis/temp_sensitivity.py`,
   `Sensitivity_Analysis/sample_type_comparison.py`
5. Export: `export_data_package.py`
