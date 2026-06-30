# 04_Results

Summary results, systematic error analyses, and sensitivity studies.

## Files

### headline_results.csv
Key numerical results in machine-readable format. Includes per-material mean
changes, the NdFeB-SmCo differential, gain systematic estimates, and
temperature coefficients.

**Source**: `export_data_package.py`

### systematic_error_analysis.md
Comprehensive analysis of systematic uncertainties, including:
- Helmholtz gain drift quantification
- Temperature correction methodology and probe bias assessment
- Baseline temperature estimation from same-day cross-checks
- Sensitivity of results to temperature assumptions

This is the primary reference for understanding the error budget.

**Source**: `Cleanup_Claude/systematic_error_investigation.md` (v3, current)

### sensitivity_results.txt
Output from temperature sensitivity analysis. Shows how the headline
differential changes as a function of assumed baseline temperature,
demonstrating robustness of the NdFeB-SmCo differential across
reasonable temperature ranges.

**Source**: `Sensitivity_Analysis/temp_sensitivity.py` output

### sample_type_results.txt
Comparison of results across sample types (Y-plate, H-plate, A-sample)
and measurement methods (Helmholtz, Teslameter).

**Source**: `Sensitivity_Analysis/sample_type_comparison.py` output

### probe_bias_assessment.txt
Detailed justification for the 0.8 C probe bias correction applied to
pre-deployment Y-plate temperatures. Based on same-day Y-plate and H-plate
temperature comparisons (Sep 30: +0.87 C, Nov 20: +0.77 C offset).

**Source**: `Sensitivity_Analysis/probe_bias_assessment.txt`

### rod_correlation_stats.txt
Full Spearman correlation analysis between dose (gamma, neutron, combined)
and magnet degradation (per-material and differential). Includes fast vs
thermal neutron breakdown from CR-39 track-etch data: fast neutron shows
stronger correlation than thermal, pointing to displacement cascades as
dominant mechanism.

**Source**: `Rod_Dosimetry/rod_dose_correlation.py` output

### gain_systematic_report.txt
Captured stdout from the gain systematic analysis script, documenting
session-to-session Helmholtz gain variability, cleaning methodology,
and per-session offset values.

**Source**: `gain_systematic_analysis.py` stdout capture

### uncertainty_budget.txt
Full rod dosimetry uncertainty budget. Covers: (1) dose uncertainty from
optichromic rod calibration (FWT-70 log-linear fits, 2 batches × 2 wavelengths),
(2) replicate OD measurement spread (~5–11% median), (3) OSL-matched plate
assignment (10% Landauer stated accuracy for 9/30 plates), (4) cross-check of
Kirsten's propagated sigma vs independent calibration estimate, and
(5) degradation baseline SEM propagation. Includes per-plate summary table.

**Source**: `Rod_Dosimetry/rod_uncertainty_analysis.py` output
