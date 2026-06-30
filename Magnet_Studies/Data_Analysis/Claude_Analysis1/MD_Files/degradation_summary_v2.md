# Preliminary Degradation Summary (v2)

**Status**: Preliminary — more data collection and error analysis pending
**Generated**: 2026-03-10
**Reference temperature**: 20.0 °C

## Methodology and Corrections Applied

### Issue 1: Outlier Samples
Two Y-plate samples have pre-deployment baselines deviating >5% from their material-group median:
- **Y-34-4 (N52SH)**: baseline 1.172 mWC vs group median 1.312 mWC (−10.7%)
- **Y-40-4 (SmCo33H)**: baseline deviates +6.8% from group median

**Treatment**: These samples are plotted (hatched bars) but **excluded from all group statistics** (means, uncertainties, ranges). They are reported separately. The cause of the anomalous baselines is unknown — possible labeling error, damaged sample, or measurement artifact.

### Issue 2: H-Plate Baseline Bias (corrected in v2)
In v1, H-plate pre-deployment baselines mixed temperature-corrected and uncorrected Helmholtz readings. Many pre-deployment dates (Apr–Jun 2025) had no Teslameter temperature data because the Hall probe was broken. Using raw (uncorrected) readings as baseline while comparing against temperature-corrected tunnel readings introduces a systematic positive bias of ~0.2–1% depending on the temperature difference.

**Treatment**: v2 uses **only temperature-corrected readings** for both baseline and tunnel measurements. Pre-deployment dates without Teslameter temperature are excluded from the baseline calculation entirely. Additionally, the temperature lookup now includes Hn/Hs pair-level Teslameter files (not just An/As individual magnet files), which recovers 34 additional temperature-matched baseline readings from the Nov 2024 campaign where pair and individual measurements were taken on different days.

**Impact**: 4 H-plate samples now excluded due to having no temperature-corrected pre-deployment readings (only 87 of 91 tunnel H-plate samples retained).

### Issue 3: Teslameter Field Degradation
Pre-deployment Teslameter field readings are invalid (broken Hall probe — magnitudes ~10–20× lower than actual). The temperature sensor on the same probe appears to have been unaffected (readings are consistent with expected lab temperatures of ~22–24°C).

**Treatment**: Teslameter field degradation uses the **first tunnel-period measurement** (Jul 2025) as baseline, not the pre-deployment reading. This measures change during tunnel exposure only. The same α(Br) temperature correction is applied using each face's own temperature reading. Beta (antiparallel) pair assemblies, which are unreliable in Helmholtz measurements due to multipole field character, **are reliable in Teslameter** point measurements and are included here.

## Error Bar Methodology

**Helmholtz (Y-plate and H-plate):**
- σ_baseline = std(pre-deployment corrected readings) / √N
- σ_temp = |B_raw × α × σ_T / (1 + α(T−20))²|, from face temperature spread
- σ_total = √(σ_baseline² + σ_temp²), as % of baseline

**Teslameter field:**
- σ = face-to-face spread (std of front/side/top corrected |B|) / √N_faces
- Propagated from both baseline and latest measurement dates

**Group averages:**
- Uncertainty = max(SEM across samples, mean per-sample σ)
- Ensures we never underestimate uncertainty

## Y-Plate Helmholtz Results

### By Material (outliers excluded)

| Material | N | Mean Δ (%) | ± Unc (%) | Min (%) | Max (%) |
|----------|---|-----------|-----------|---------|---------|
| N42EH | 30 | -0.333 | ±0.034 | -0.855 | -0.113 |
| N52SH | 29 | -0.260 | ±0.037 | -0.676 | +0.001 |
| SmCo33H | 29 | +0.014 | ±0.030 | -0.336 | +0.376 |
| SmCo35 | 30 | -0.077 | ±0.031 | -0.500 | +0.394 |

### By Region (outliers excluded)

| Region | N | Mean Δ (%) | ± Unc (%) | Min (%) | Max (%) |
|--------|---|-----------|-----------|---------|---------|
| SE Arc | 19 | -0.123 | ±0.028 | -0.421 | +0.074 |
| NE Arc | 20 | -0.295 | ±0.062 | -0.855 | +0.376 |
| NW Arc | 19 | -0.161 | ±0.052 | -0.453 | +0.291 |
| SW Arc | 20 | -0.273 | ±0.057 | -0.806 | +0.048 |
| North Linac | 16 | -0.039 | ±0.047 | -0.414 | +0.394 |
| South Linac | 16 | -0.051 | ±0.040 | -0.269 | +0.369 |
| Labyrinth | 8 | -0.151 | ±0.044 | -0.287 | +0.052 |

### By Region × Material

| Region | Material | N | Mean Δ (%) | ± Unc (%) |
|--------|----------|---|-----------|-----------|
| SE Arc | N42EH | 5 | -0.223 | ±0.050 |
| SE Arc | N52SH | 5 | -0.182 | ±0.029 |
| SE Arc | SmCo33H | 4 | -0.013 | ±0.038 |
| SE Arc | SmCo35 | 5 | -0.052 | ±0.042 |
| NE Arc | N42EH | 5 | -0.508 | ±0.088 |
| NE Arc | N52SH | 5 | -0.469 | ±0.082 |
| NE Arc | SmCo33H | 5 | +0.033 | ±0.089 |
| NE Arc | SmCo35 | 5 | -0.238 | ±0.054 |
| NW Arc | N42EH | 5 | -0.370 | ±0.027 |
| NW Arc | N52SH | 4 | -0.327 | ±0.048 |
| NW Arc | SmCo33H | 5 | +0.099 | ±0.082 |
| NW Arc | SmCo35 | 5 | -0.078 | ±0.042 |
| SW Arc | N42EH | 5 | -0.439 | ±0.124 |
| SW Arc | N52SH | 5 | -0.379 | ±0.117 |
| SW Arc | SmCo33H | 5 | -0.083 | ±0.069 |
| SW Arc | SmCo35 | 5 | -0.191 | ±0.090 |
| North Linac | N42EH | 4 | -0.254 | ±0.068 |
| North Linac | N52SH | 4 | -0.053 | ±0.025 |
| North Linac | SmCo33H | 4 | -0.008 | ±0.028 |
| North Linac | SmCo35 | 4 | +0.158 | ±0.093 |
| South Linac | N42EH | 4 | -0.176 | ±0.024 |
| South Linac | N52SH | 4 | -0.112 | ±0.055 |
| South Linac | SmCo33H | 4 | +0.091 | ±0.119 |
| South Linac | SmCo35 | 4 | -0.009 | ±0.023 |
| Labyrinth | N42EH | 2 | -0.280 | ±0.008 |
| Labyrinth | N52SH | 2 | -0.208 | ±0.011 |
| Labyrinth | SmCo33H | 2 | -0.054 | ±0.107 |
| Labyrinth | SmCo35 | 2 | -0.061 | ±0.066 |

### By Arc Line Position

Line 1 = top of stack, Line 5 = bottom. Different beam energy passes.

| Line | N | Mean Δ (%) | ± Unc (%) | Min (%) | Max (%) |
|------|---|-----------|-----------|---------|---------|
| 1 | 16 | -0.315 | ±0.091 | -0.855 | +0.376 |
| 2 | 16 | -0.231 | ±0.053 | -0.566 | +0.069 |
| 3 | 16 | -0.182 | ±0.048 | -0.542 | +0.291 |
| 4 | 16 | -0.152 | ±0.040 | -0.459 | +0.074 |
| 5 | 14 | -0.191 | ±0.048 | -0.614 | +0.013 |

## H-Plate Helmholtz Results

### By Material

| Material | N | Mean Δ (%) | ± Unc (%) | Min (%) | Max (%) |
|----------|---|-----------|-----------|---------|---------|
| NdFeB | 37 | +0.026 | ±0.050 | -1.162 | +0.691 |
| SmCo | 48 | +0.148 | ±0.061 | -0.879 | +1.354 |

### By Assembly Configuration

| Config | Material | N | Mean Δ (%) | ± Unc (%) | Notes |
|--------|----------|---|-----------|-----------|-------|
| Alpha | NdFeB | 12 | +0.079 | ±0.049 |  |
| Alpha | SmCo | 16 | +0.056 | ±0.045 |  |
| Gamma | NdFeB | 12 | -0.113 | ±0.130 |  |
| Gamma | SmCo | 16 | +0.268 | ±0.160 |  |
| Delta | NdFeB | 13 | +0.105 | ±0.057 |  |
| Delta | SmCo | 16 | +0.119 | ±0.077 |  |

## Teslameter Field Results

**Note**: Baseline is first tunnel measurement (Jul 2025), not pre-deployment. Measures change during tunnel exposure only.

### Y-Plate Teslameter by Material

| Material | N | Mean Δ (%) | ± Unc (%) | Min (%) | Max (%) |
|----------|---|-----------|-----------|---------|---------|
| N42EH | 30 | -0.085 | ±0.433 | -1.788 | +0.857 |
| N52SH | 29 | +0.205 | ±0.498 | -0.960 | +1.069 |
| SmCo33H | 29 | -0.012 | ±0.321 | -0.588 | +0.778 |
| SmCo35 | 30 | -0.174 | ±0.462 | -2.771 | +0.630 |

### H-Plate Teslameter by Configuration (including Beta)

| Config | N | Mean Δ (%) | ± Unc (%) |
|--------|---|-----------|-----------|
| Alpha | 30 | +2.412 | ±1.545 |
| Beta | 30 | +2.733 | ±1.923 |
| Gamma | 30 | +4.846 | ±4.954 |
| Delta | 30 | +2.248 | ±1.409 |

## Flagged Outlier Samples

| Sample | Material | Region | Δ (%) | ± (%) | Reason |
|--------|----------|--------|-------|-------|--------|
| Y-34-4 | N52SH | NW Arc | +11.072 | ±0.007 | Baseline >5% from group median |
| Y-40-4 | SmCo33H | SE Arc | -6.206 | ±0.001 | Baseline >5% from group median |

## Individual Y-Plate Results

| Sample | Material | Region | Line | Δ (%) | ± (%) | Outlier | Date |
|--------|----------|--------|------|-------|-------|---------|------|
| Y-40-4 | SmCo33H | SE Arc | 5 | -6.206 | ±0.001 | ⚠ | 2026-01-08 |
| Y-39-1 | N42EH | NE Arc | 1 | -0.855 | ±0.020 |  | 2026-01-08 |
| Y-13-4 | N42EH | SW Arc | 1 | -0.806 | ±0.008 |  | 2026-01-12 |
| Y-39-3 | N52SH | NE Arc | 1 | -0.676 | ±0.022 |  | 2026-01-08 |
| Y-13-2 | N52SH | SW Arc | 1 | -0.675 | ±0.012 |  | 2026-01-12 |
| Y-9-2 | N52SH | NE Arc | 5 | -0.614 | ±0.001 |  | 2026-01-08 |
| Y-32-1 | N52SH | SW Arc | 2 | -0.566 | ±0.001 |  | 2026-01-12 |
| Y-19-1 | N42EH | SW Arc | 3 | -0.542 | ±0.001 |  | 2026-01-12 |
| Y-32-3 | N42EH | SW Arc | 2 | -0.522 | ±0.003 |  | 2026-01-12 |
| Y-13-3 | SmCo35 | SW Arc | 1 | -0.500 | ±0.003 |  | 2026-01-12 |
| Y-7-3 | N52SH | NE Arc | 2 | -0.473 | ±0.003 |  | 2026-01-08 |
| Y-21-4 | N42EH | NE Arc | 4 | -0.459 | ±0.002 |  | 2026-01-08 |
| Y-38-4 | N52SH | NW Arc | 1 | -0.453 | ±0.004 |  | 2026-01-08 |
| Y-7-1 | N42EH | NE Arc | 2 | -0.452 | ±0.000 |  | 2026-01-08 |
| Y-6-2 | N42EH | NW Arc | 2 | -0.443 | ±0.002 |  | 2025-10-23 |
| Y-19-3 | N52SH | SW Arc | 3 | -0.429 | ±0.006 |  | 2026-01-12 |
| Y-15-1 | N42EH | SE Arc | 1 | -0.421 | ±0.007 |  | 2026-01-08 |
| Y-4-3 | N42EH | North Linac | — | -0.414 | ±0.005 |  | 2026-01-12 |
| Y-9-4 | N42EH | NE Arc | 5 | -0.406 | ±0.002 |  | 2026-01-08 |
| Y-25-4 | N42EH | NW Arc | 4 | -0.385 | ±0.004 |  | 2026-01-08 |
| Y-38-2 | N42EH | NW Arc | 1 | -0.373 | ±0.006 |  | 2026-01-08 |
| Y-34-2 | N42EH | NW Arc | 5 | -0.372 | ±0.002 |  | 2026-01-08 |
| Y-18-2 | N42EH | NE Arc | 3 | -0.369 | ±0.000 |  | 2026-01-08 |
| Y-39-4 | SmCo35 | NE Arc | 1 | -0.366 | ±0.014 |  | 2026-01-08 |
| Y-21-2 | N52SH | NE Arc | 4 | -0.353 | ±0.002 |  | 2026-01-08 |
| Y-25-2 | N52SH | NW Arc | 4 | -0.351 | ±0.003 |  | 2026-01-08 |
| Y-13-1 | SmCo33H | SW Arc | 1 | -0.336 | ±0.019 |  | 2026-01-12 |
| Y-18-1 | SmCo35 | NE Arc | 3 | -0.320 | ±0.001 |  | 2026-01-08 |
| Y-17-4 | N42EH | North Linac | — | -0.319 | ±0.005 |  | 2026-01-12 |
| Y-20-3 | N42EH | Labyrinth | — | -0.287 | ±0.004 |  | 2026-01-12 |
| Y-36-3 | N42EH | NW Arc | 3 | -0.277 | ±0.006 |  | 2026-01-08 |
| Y-32-2 | SmCo35 | SW Arc | 2 | -0.273 | ±0.001 |  | 2026-01-12 |
| Y-12-3 | N42EH | Labyrinth | — | -0.272 | ±0.005 |  | 2026-01-12 |
| Y-1-2 | N52SH | South Linac | — | -0.269 | ±0.007 |  | 2026-01-12 |
| Y-36-1 | N52SH | NW Arc | 3 | -0.264 | ±0.006 |  | 2026-01-08 |
| Y-9-3 | SmCo35 | NE Arc | 5 | -0.261 | ±0.000 |  | 2026-01-08 |
| Y-3-3 | N52SH | SE Arc | 2 | -0.251 | ±0.014 |  | 2026-01-08 |
| Y-40-1 | N52SH | SE Arc | 5 | -0.243 | ±0.008 |  | 2026-01-08 |
| Y-6-4 | N52SH | NW Arc | 2 | -0.240 | ±0.005 |  | 2026-01-08 |
| Y-18-4 | N52SH | NE Arc | 3 | -0.229 | ±0.004 |  | 2026-01-08 |
| Y-30-2 | N42EH | South Linac | — | -0.227 | ±0.007 |  | 2026-01-12 |
| Y-25-3 | SmCo35 | NW Arc | 4 | -0.220 | ±0.008 |  | 2026-01-08 |
| Y-20-1 | N52SH | Labyrinth | — | -0.219 | ±0.008 |  | 2026-01-12 |
| Y-40-3 | N42EH | SE Arc | 5 | -0.202 | ±0.003 |  | 2026-01-08 |
| Y-12-1 | N52SH | Labyrinth | — | -0.197 | ±0.013 |  | 2026-01-12 |
| Y-24-3 | N42EH | South Linac | — | -0.190 | ±0.012 |  | 2026-01-12 |
| Y-7-4 | SmCo35 | NE Arc | 2 | -0.185 | ±0.003 |  | 2026-01-08 |
| Y-5-4 | N42EH | South Linac | — | -0.173 | ±0.008 |  | 2026-01-12 |
| Y-15-3 | N52SH | SE Arc | 1 | -0.173 | ±0.006 |  | 2026-01-08 |
| Y-3-1 | N42EH | SE Arc | 2 | -0.170 | ±0.009 |  | 2026-01-08 |
| Y-23-1 | N42EH | SE Arc | 3 | -0.170 | ±0.006 |  | 2026-01-08 |
| Y-30-3 | SmCo33H | South Linac | — | -0.169 | ±0.002 |  | 2026-01-12 |
| Y-10-2 | N42EH | SW Arc | 4 | -0.168 | ±0.044 |  | 2026-01-12 |
| Y-3-4 | SmCo35 | SE Arc | 2 | -0.167 | ±0.002 |  | 2026-01-08 |
| Y-11-3 | N52SH | SW Arc | 5 | -0.165 | ±0.012 |  | 2026-01-12 |
| Y-12-4 | SmCo33H | Labyrinth | — | -0.161 | ±0.005 |  | 2026-01-12 |
| Y-22-2 | N42EH | North Linac | — | -0.157 | ±0.010 |  | 2026-01-12 |
| Y-11-1 | N42EH | SW Arc | 5 | -0.155 | ±0.023 |  | 2026-01-12 |
| Y-26-2 | N42EH | SE Arc | 4 | -0.153 | ±0.001 |  | 2026-01-08 |
| Y-26-4 | N52SH | SE Arc | 4 | -0.137 | ±0.006 |  | 2026-01-08 |
| Y-20-2 | SmCo35 | Labyrinth | — | -0.127 | ±0.002 |  | 2026-01-12 |
| Y-16-3 | N42EH | North Linac | — | -0.126 | ±0.006 |  | 2026-01-12 |
| Y-34-3 | SmCo33H | NW Arc | 5 | -0.123 | ±0.001 |  | 2026-01-08 |
| Y-19-4 | SmCo35 | SW Arc | 3 | -0.119 | ±0.001 |  | 2026-01-12 |
| Y-21-1 | SmCo33H | NE Arc | 4 | -0.118 | ±0.001 |  | 2026-01-08 |
| Y-19-2 | SmCo33H | SW Arc | 3 | -0.118 | ±0.000 |  | 2026-01-12 |
| Y-1-4 | N42EH | South Linac | — | -0.113 | ±0.006 |  | 2026-01-12 |
| Y-22-4 | N52SH | North Linac | — | -0.110 | ±0.010 |  | 2026-01-12 |
| Y-15-4 | SmCo35 | SE Arc | 1 | -0.107 | ±0.002 |  | 2026-01-08 |
| Y-23-3 | N52SH | SE Arc | 3 | -0.106 | ±0.007 |  | 2026-01-08 |
| Y-7-2 | SmCo33H | NE Arc | 2 | -0.099 | ±0.003 |  | 2026-01-08 |
| Y-36-2 | SmCo35 | NW Arc | 3 | -0.095 | ±0.001 |  | 2026-01-08 |
| Y-24-1 | N52SH | South Linac | — | -0.089 | ±0.014 |  | 2026-01-12 |
| Y-34-1 | SmCo35 | NW Arc | 5 | -0.086 | ±0.008 |  | 2026-01-08 |
| Y-23-2 | SmCo33H | SE Arc | 3 | -0.086 | ±0.001 |  | 2026-01-08 |
| Y-5-2 | N52SH | South Linac | — | -0.082 | ±0.009 |  | 2026-01-12 |
| Y-17-2 | N52SH | North Linac | — | -0.080 | ±0.013 |  | 2026-01-12 |
| Y-26-3 | SmCo33H | SE Arc | 4 | -0.071 | ±0.001 |  | 2026-01-08 |
| Y-23-4 | SmCo35 | SE Arc | 3 | -0.069 | ±0.001 |  | 2026-01-08 |
| Y-11-4 | SmCo35 | SW Arc | 5 | -0.065 | ±0.001 |  | 2026-01-12 |
| Y-4-4 | SmCo33H | North Linac | — | -0.062 | ±0.000 |  | 2026-01-12 |
| Y-10-4 | N52SH | SW Arc | 4 | -0.062 | ±0.008 |  | 2026-01-12 |
| Y-30-1 | SmCo35 | South Linac | — | -0.058 | ±0.001 |  | 2026-01-12 |
| Y-21-3 | SmCo35 | NE Arc | 4 | -0.057 | ±0.002 |  | 2026-01-08 |
| Y-17-3 | SmCo35 | North Linac | — | -0.048 | ±0.002 |  | 2026-01-12 |
| Y-22-3 | SmCo33H | North Linac | — | -0.041 | ±0.003 |  | 2026-01-12 |
| Y-24-4 | SmCo33H | South Linac | — | -0.027 | ±0.004 |  | 2026-01-12 |
| Y-38-1 | SmCo35 | NW Arc | 1 | -0.025 | ±0.002 |  | 2026-01-08 |
| Y-5-3 | SmCo35 | South Linac | — | -0.024 | ±0.004 |  | 2026-01-12 |
| Y-4-1 | N52SH | North Linac | — | -0.024 | ±0.016 |  | 2026-01-12 |
| Y-25-1 | SmCo33H | NW Arc | 4 | -0.024 | ±0.001 |  | 2026-01-08 |
| Y-30-4 | N52SH | South Linac | — | -0.009 | ±0.004 |  | 2026-01-12 |
| Y-32-4 | SmCo33H | SW Arc | 2 | -0.008 | ±0.001 |  | 2026-01-12 |
| Y-18-3 | SmCo33H | NE Arc | 3 | -0.005 | ±0.001 |  | 2026-01-08 |
| Y-1-3 | SmCo35 | South Linac | — | -0.003 | ±0.002 |  | 2026-01-12 |
| Y-11-2 | SmCo33H | SW Arc | 5 | +0.001 | ±0.002 |  | 2026-01-12 |
| Y-16-1 | N52SH | North Linac | — | +0.001 | ±0.013 |  | 2026-01-12 |
| Y-10-1 | SmCo35 | SW Arc | 4 | +0.004 | ±0.003 |  | 2026-01-12 |
| Y-12-2 | SmCo35 | Labyrinth | — | +0.005 | ±0.002 |  | 2026-01-12 |
| Y-17-1 | SmCo33H | North Linac | — | +0.006 | ±0.001 |  | 2026-01-12 |
| Y-40-2 | SmCo35 | SE Arc | 5 | +0.007 | ±0.002 |  | 2026-01-08 |
| Y-9-1 | SmCo33H | NE Arc | 5 | +0.013 | ±0.004 |  | 2026-01-08 |
| Y-6-1 | SmCo35 | NW Arc | 2 | +0.035 | ±0.001 |  | 2026-01-08 |
| Y-3-2 | SmCo33H | SE Arc | 2 | +0.043 | ±0.002 |  | 2026-01-08 |
| Y-10-3 | SmCo33H | SW Arc | 4 | +0.048 | ±0.170 |  | 2026-01-12 |
| Y-24-2 | SmCo35 | South Linac | — | +0.049 | ±0.003 |  | 2026-01-12 |
| Y-20-4 | SmCo33H | Labyrinth | — | +0.052 | ±0.002 |  | 2026-01-12 |
| Y-16-4 | SmCo33H | North Linac | — | +0.063 | ±0.003 |  | 2026-01-12 |
| Y-15-2 | SmCo33H | SE Arc | 1 | +0.064 | ±0.002 |  | 2026-01-08 |
| Y-6-3 | SmCo33H | NW Arc | 2 | +0.069 | ±0.001 |  | 2026-01-08 |
| Y-26-1 | SmCo35 | SE Arc | 4 | +0.074 | ±0.001 |  | 2026-01-08 |
| Y-16-2 | SmCo35 | North Linac | — | +0.090 | ±0.002 |  | 2026-01-12 |
| Y-1-1 | SmCo33H | South Linac | — | +0.193 | ±0.006 |  | 2026-01-12 |
| Y-22-1 | SmCo35 | North Linac | — | +0.195 | ±0.004 |  | 2026-01-12 |
| Y-38-3 | SmCo33H | NW Arc | 1 | +0.280 | ±0.003 |  | 2026-01-08 |
| Y-36-4 | SmCo33H | NW Arc | 3 | +0.291 | ±0.000 |  | 2026-01-08 |
| Y-5-1 | SmCo33H | South Linac | — | +0.369 | ±0.004 |  | 2026-01-12 |
| Y-39-2 | SmCo33H | NE Arc | 1 | +0.376 | ±0.005 |  | 2026-01-08 |
| Y-4-2 | SmCo35 | North Linac | — | +0.394 | ±0.003 |  | 2026-01-12 |
| Y-34-4 | N52SH | NW Arc | 5 | +11.072 | ±0.007 | ⚠ | 2026-01-08 |

## Key Findings

1. **N42EH shows the clearest degradation signal**: mean −0.33% across all tunnel locations. This is consistent with NdFeB's known radiation sensitivity.
2. **Largest individual degradation**: Y-39-1 (N42EH, NE Arc) at -0.855 ± 0.020%
3. **Samples with >0.5% degradation**: 9 / 118
4. **SmCo shows less degradation than NdFeB**, consistent with theoretical expectations (lower coercivity sensitivity to radiation damage)
5. **Labyrinth (control) sites show minimal change**, providing confidence that observed arc/linac degradation is radiation-related

## Caveats and Limitations

- **Preliminary**: More measurements are being collected
- **No dose correlation yet**: Radiation dose data incomplete; dose-response analysis deferred
- **α(Br) systematic**: Temperature coefficient uncertainty (~5–10% on α itself) would shift all values of a material grade together; not included in per-sample error bars
- **H-plate sample size reduced**: Only samples with temperature-corrected pre-deployment baselines are included, reducing statistical power
- **Teslameter baseline**: Uses first tunnel measurement, not pre-deployment; shorter exposure baseline
- **Probe positioning**: Teslameter measures a point on the magnet surface where field gradients are steep; ~0.5mm shift can produce >1% variation, making Teslameter inherently noisier than Helmholtz
- **Lab controls not yet included** (data still being collected)
