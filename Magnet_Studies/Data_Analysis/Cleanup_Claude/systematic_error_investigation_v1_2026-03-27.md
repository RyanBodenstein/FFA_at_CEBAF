# Systematic Error Investigation — Y-Plate Baseline Temperature Correction
# Date: 2026-03-27 (ORIGINAL version, before 2026-03-31 update)
# Saved as backup in case the updated version introduced errors

## 1. Temperature Correction Fix (Implemented)

The Y-plate Teslameter probe read ~2°C too high during Nov 2024 pre-deployment baselines.
- Probe showed ~24.5–25.4°C; actual lab temp ~22–23°C (from H/A Teslameter data)
- Fix: use Y_BASELINE_TEMP_LOOKUP in load_all() for pre-deployment dates
- Only existing baselines corrected; April 2025 readings NOT recovered (gain drift issue)

### Corrected Results (temp fix only, no April recovery)
| Material | Before (biased) | After (corrected) | Shift |
|----------|-----------------|-------------------|-------|
| N42EH | -0.333% ± 0.034% | -0.137% ± 0.036% | +0.196% |
| N52SH | -0.260% ± 0.037% | -0.044% ± 0.037% | +0.216% |
| SmCo33H | +0.012% ± 0.030% | +0.083% ± 0.031% | +0.071% |
| SmCo35 | -0.077% ± 0.031% | +0.001% ± 0.031% | +0.078% |
| **Differential** | **-0.266% ± 0.027% (9.7σ)** | **-0.134% ± 0.027% (5.0σ)** | **+0.132%** |

Physics check: NdFeB shifts +0.20% (|α|=0.001, ~2°C) and SmCo shifts +0.08% (|α|=0.0004, ~2°C). ✓
Mean temp correction: -1.9°C, uniform across materials. ✓
Double ratio UNCHANGED (uses tunnel dates only). ✓

### Planning Error
During planning, I incorrectly predicted the correction would make SmCo show degradation
and the differential would strengthen to -0.357%. This was a sign error — I subtracted
the bias instead of adding it. The correct direction is LESS negative, not more.

## 2. Raw Gain Drift Is Material-Dependent (Key Finding)

Raw (uncorrected) gain drift from Nov 5 baseline to later dates shows systematic
NdFeB-SmCo difference of -0.33% to -0.78%:

| Date | Type | All-mat mean | NdFeB-SmCo raw | Expected from ΔT | Residual |
|------|------|-------------|----------------|-------------------|----------|
| 2025-04-23 | Lab | -0.54% | -0.49% | ~0% (ΔT≈0) | -0.49% |
| 2025-05-07 | Lab | -0.57% | -0.61% | ~0% | -0.61% |
| 2025-06-17 | Lab | -0.78% | -0.78% | ~0% | -0.78% |
| 2025-08-27 | Tunnel | -0.84% | -0.78% | -0.48% (ΔT≈8°C) | -0.30% |
| 2025-10-21 | Tunnel | -0.23% | -0.33% | -0.12% (ΔT≈2°C) | -0.21% |
| 2026-01-08 | Tunnel | -0.36% | -0.50% | -0.30% (ΔT≈5°C) | -0.20% |

Key observations:
- Lab dates show LARGER material-dependent residuals (0.5–0.8%) than tunnel dates (0.2–0.3%)
- If these lab residuals are NOT from temperature, they indicate a material-dependent
  measurement artifact in the pre-deployment data
- BUT: the lab dates have unknown temperatures. If lab was 5–10°C warmer in spring/summer
  than in November, that could explain much of the lab residual
- The tunnel residual of ~-0.2% (after temp correction) is the true degradation signal

## 3. Known Systematics (from measurement_systematics.md)

- Helmholtz DC accuracy: 0.050% typical, 0.100% max
- Gain drift: ±0.124% (cleaned), ±0.248% (uncleaned)
- Nov 2024 reads ~0.7% higher than Apr-Jun 2025 (common-mode)
- Cap system changed before tunnel deployment (potential offset)
- Oct 21 thermal lag: ~0.3%
- Jul 17 offset: ~0.8% artifact
- α(Br): N42EH -0.10%/°C, N52SH -0.11%/°C, SmCo -0.040%/°C (manufacturer confirmed)

## 4. Error Budget (Preliminary)

### Differential (NdFeB-SmCo) — GAIN-IMMUNE
| Source | Magnitude | Notes |
|--------|-----------|-------|
| Statistical | ±0.027% | SEM of 30-plate differential |
| Baseline temp (probe bias) | +0.132% correction applied | ±0.03% from temp uncertainty |
| α coefficient uncertainty | ±0.03% | ±10% in α values |
| Baseline temp (exact value) | ±0.06% | ±1°C uncertainty in true lab temp |
| Cap change | unknown | Potentially material-dependent if cap affects position |

### Individual Materials — GAIN-SENSITIVE
| Source | Magnitude | Notes |
|--------|-----------|-------|
| Statistical | ±0.03% | Per-material SEM |
| Gain systematic | ±0.124% | Dominates! |
| Baseline temp | +0.08–0.22% correction | Applied |
| α uncertainty | ±0.02% | Smaller than gain |

## 5. Outstanding Questions

1. Why is the lab-date NdFeB-SmCo raw residual (0.5–0.8%) so much larger than the
   tunnel-date residual (~0.2%)? Temperature or artifact?
2. Could the cap change affect materials differently?
3. What are the tunnel temperatures for the Oct 21 beam-off measurements?
4. Can we empirically measure α from multi-temperature tunnel data?

## Status
- Temperature fix: IMPLEMENTED in manager_summary_v3.py
- Background agents: investigating (1) Helmholtz gain, (2) α uncertainty, (3) tunnel temps, (4) H/A cross-check
- Downstream scripts: NOT YET re-run
