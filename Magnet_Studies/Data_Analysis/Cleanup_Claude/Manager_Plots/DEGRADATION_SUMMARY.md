# LDRD FFA@CEBAF Magnet Radiation Study
## Preliminary Degradation Summary

**Date:** March 10, 2026
**Status:** Preliminary — data collection ongoing
**Exposure Period:** July 2025 – January 2026 (~6 months in CEBAF tunnel)
**Measurement Method:** Helmholtz coil (integrated dipole moment), temperature-corrected to 20°C

---

## Executive Summary

After ~6 months in the CEBAF tunnel, **NdFeB permanent magnets show statistically significant degradation of 0.26–0.33%**, while **SmCo magnets show no significant degradation** (<0.08%). The degradation is material-dependent and dose-correlated: arc regions (higher radiation dose) show ~2× more NdFeB degradation than linac regions.

---

## Key Results

### By Material Grade (Y-plate Helmholtz, temp-corrected)

| Material | Mean Change (%) | Uncertainty (%) | Significance | N samples |
|----------|:--------------:|:--------------:|:------------:|:---------:|
| **NdFeB N42EH** | **−0.333** | ±0.034 | **10σ** | 30 |
| **NdFeB N52SH** | **−0.260** | ±0.037 | **7σ** | 29 |
| SmCo 33H | +0.012 | ±0.030 | n.s. | 29 |
| SmCo 35 | −0.077 | ±0.031 | 2σ | 30 |

**Combined:**
- **All NdFeB: −0.297 ± 0.025% (12σ)**
- **All SmCo: −0.033 ± 0.022% (n.s.)**

### By Dose Region

| Region | NdFeB Change (%) | SmCo Change (%) | Notes |
|--------|:----------------:|:---------------:|-------|
| Arcs (NE, NW, SE, SW) | −0.35 to −0.40 | −0.01 to −0.14 | Highest dose |
| Linacs (North, South) | −0.08 to −0.21 | +0.01 to +0.07 | Lower dose |
| Labyrinth | −0.24 to −0.28 | −0.06 to −0.13 | Not a control — radiation detected |

### Dose-Dependence

NdFeB degradation scales with expected radiation dose:
- **Arcs (higher dose):** −0.38% ± 0.04% (NdFeB average)
- **Linacs (lower dose):** −0.21% ± 0.04% (NdFeB average)
- Arc-to-linac ratio: **~1.8×**, consistent with dose scaling

SmCo shows no dose-dependent signal within measurement precision.

---

## Methodology

### Temperature Correction (Critical)
- Raw Helmholtz readings vary ~1% for NdFeB and ~0.5% for SmCo due to tunnel temperature swings (21–34°C)
- Temperature measured by co-located Teslameter Hall probe (3 faces averaged: front, side, top)
- Correction: H_corr = H_raw / (1 + α(T − 20°C)), where α = −0.10%/°C (N42EH), −0.11%/°C (N52SH), −0.04%/°C (SmCo)
- **Without temperature correction, the degradation signal is undetectable**

### Baseline
- **Helmholtz pre-deployment baselines**: Reliable. Pre-deployment Helmholtz coil measurements are the gold standard for field magnitude baseline.
- **Teslameter pre-deployment field readings**: NOT used for field baselines — the Hall probe was changed and a protective cap system installed before tunnel deployment, introducing an unknown offset. Teslameter field baselines use the first tunnel-period measurement instead.
- **Teslameter pre-deployment temperature readings**: Still accurate and used for temperature correction of co-located Helmholtz data.
- Only dates with co-located temperature data used (no mixing of corrected/uncorrected)
- Robust baseline: median-absolute-deviation outlier rejection for samples with ≥3 pre-deployment readings

### Error Bars
- Per-sample: quadrature sum of baseline uncertainty (std/√N of pre-deployment readings) and temperature propagation uncertainty
- Group averages: max(SEM across samples, mean per-sample uncertainty)
- Conservative: ensures we never underestimate uncertainty

### Outlier Treatment
- 2 Y-plate samples excluded (Y-34-4, Y-40-4): pre-deployment baselines deviate >5% from material group — possible labeling or measurement error
- H-plate pair assemblies with |change| > 5% flagged as anomalous baselines (physically impossible from radiation alone)
- Beta (antiparallel) pair assemblies excluded from Helmholtz analysis (multipole field character makes integrated moment unreliable)

---

## Known Systematics Under Investigation

### 1. Jul 17 vs Jul 30 Campaign Split
The first two tunnel campaigns measured different subsets of 15 plates each. Despite temperature correction, a ~0.2% systematic offset persists between the groups. This does not affect the final degradation values (which use the latest measurement vs baseline) but complicates the time-series interpretation.

### 2. Labyrinth Radiation
The labyrinth access tunnels show measurable radiation levels and NdFeB degradation comparable to linac regions. These are **not** control sites. The true controls are the "upstairs" lab samples, which have not yet been fully analyzed.

### 3. H-Plate Teslameter Probe Positioning
Hand-held Teslameter measurements of H-plate pair assemblies show a systematic ~2–3% low bias on front and side faces for the first tunnel measurement, likely due to inconsistent probe placement on the complex pair geometry. Top-face measurements are unaffected. This does not impact Helmholtz coil results (which enclose the entire sample).

### 4. SmCo35 Marginal Signal
SmCo35 shows a marginal −0.08% signal (2σ). This may be:
- Real but small degradation (SmCo is ~5× more radiation-resistant than NdFeB, so ~0.08% vs ~0.3% is plausible)
- A measurement systematic not fully corrected by temperature normalization
- Statistical fluctuation

Further measurements will resolve this.

---

## Conclusions

1. **NdFeB degradation is confirmed** at the 0.3% level after 6 months, with high statistical significance (10σ for N42EH, 7σ for N52SH)
2. **SmCo is radiation-resistant** at the current dose levels — no significant degradation detected
3. **Degradation is dose-dependent** — arc regions (higher dose) show ~2× more than linac regions
4. **Temperature correction is essential** — the raw measurement variation (~1%) is 3× larger than the degradation signal
5. **N42EH degrades slightly more than N52SH** (−0.33% vs −0.26%), consistent with the expected higher radiation sensitivity of the N42EH grade

---

## Plots

All plots are in `Manager_Plots/`:

| File | Description |
|------|-------------|
| `1_material_comparison.png` | Bar chart: degradation by material grade with significance |
| `2_ndfeb_vs_smco.png` | Simplified NdFeB vs SmCo comparison |
| `3_regional_comparison.png` | Grouped bar by tunnel region and material |
| `4_arc_vs_linac.png` | Dose-dependent comparison: arcs vs linacs vs labyrinth |
| `5_timeseries.png` | Degradation evolution over time |
| `6_all_samples_waterfall.png` | Every individual sample sorted by degradation |
| `7_dashboard.png` | One-page summary dashboard |

---

*Generated by temperature_corrected_analysis.py and manager_summary.py*
*Data: 30 Y-plates × 4 material slots = 120 samples (118 after outlier exclusion)*
