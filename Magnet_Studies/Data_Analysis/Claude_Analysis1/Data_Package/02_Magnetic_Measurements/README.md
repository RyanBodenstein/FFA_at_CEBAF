# 02_Magnetic_Measurements

Degradation results for all sample types, time series data, and temperature
correction details.

## Files

### y_plate_degradation.csv
**Primary results**. Percentage change in Helmholtz flux integral for all 39
Y-plates (30 tunnel, 9 lab). Each row represents one magnet slot. All readings
are temperature-corrected to T_ref = 20 C.

Outlier samples (Y-34-4, Y-40-4) have `is_outlier=True` and should be
excluded from group statistics.

**Source**: `manager_summary_v3.load_all()` (tunnel), `manager_summary_v5_polish.load_lab_y_plates()` (lab)

### h_plate_degradation.csv
Percentage change for H-plate pair assemblies (87 pairs with valid data).
H-plates carry the full gain systematic (no intra-plate differential possible).
The `config` column indicates magnetic configuration; Beta (antiparallel)
produces less reliable H-level readings.

**Source**: `degradation_summary_v2.compute_h_plate_degradation()`

### a_sample_degradation.csv
Percentage change for A-sample individual magnets (202 with valid data).
A-samples are always measured outside their assembly, so Helmholtz baselines
are valid regardless of configuration changes.

**Source**: `manager_summary_v5_polish.load_a_sample_helmholtz()`

### y_plate_time_series.csv
Per-date percentage change for tunnel Y-plates, enabling time-resolved analysis.
Multiple measurement dates per sample are available from July 2025 onward.

**Source**: `date_pcts` field from `load_all()` results

### temperature_corrections.csv
Temperature data for every (sample, date) pair. For pre-deployment Y-plate
measurements, the `correction_source` column indicates whether the temperature
was taken from the Teslameter probe directly or overridden using calibrated
estimates (Y_BASELINE_TEMP_LOOKUP) based on same-day H-plate cross-checks.

See `04_Results/probe_bias_assessment.txt` for the full justification of the
0.8 C probe bias correction applied to pre-deployment Y-plate temperatures.

**Source**: `temp_final` dict from `load_all()`

## Raw Data
The raw `.dat` measurement files are in the parent repository:
- `Cleanup_Claude/Y_Plates/Helmholtz/` — Y-plate Helmholtz files (Y-XX-S_helmholtz.dat)
- `Cleanup_Claude/Y_Plates/Teslameter/` — Y-plate Teslameter files (Y-XX-S_face.dat)
- `Cleanup_Claude/Pair_Assemblies/Helmholtz/` — H-plate and A-sample Helmholtz files
- `Cleanup_Claude/Pair_Assemblies/Teslameter/` — H-plate and A-sample Teslameter files

Format: tab-separated, `YYYY-MM-DD\tHH:MM:SS\tvalue unit` (Helmholtz) or
`YYYY-MM-DD\tHH:MM:SS\tF1\tF2\tF3\tTemp` (Teslameter, 3-axis field + temperature).

Sentinel value `1337` = no valid reading (sensor error). Readings with
|value| < 0.1 mWC are filtered as near-zero.

## Interpreting Results
- Negative `pct_change` = demagnetization (field loss)
- The gain-immune metric is the **intra-plate NdFeB-SmCo differential**:
  within each plate, subtract SmCo mean from NdFeB mean. This cancels
  any session-to-session Helmholtz gain drift.
- Individual material means carry a systematic uncertainty of +/-0.12%
  from Helmholtz gain drift.
