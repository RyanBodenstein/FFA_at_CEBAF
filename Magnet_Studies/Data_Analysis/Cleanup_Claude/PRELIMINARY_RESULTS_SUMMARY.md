# Preliminary Results: Magnet Radiation Degradation at CEBAF
## LDRD FFA@CEBAF — Magnet Radiation Study

**Status**: PRELIMINARY — dose data integrated (March 25, 2026)
**Date**: March 2026
**Samples**: 30 Y-plates (4 material grades each), 30 H-plates (pair assemblies), lab controls
**Instruments**: Helmholtz coil (fluxmeter, 0.05% accuracy) + Teslameter (100 ppm, 3D-printed rigs)
**Dosimetry**: Landauer InLight L02TN OSL + CR-39 badges, ~15 swap dates per plate, 782 plate-date entries (99.6% Landauer match)

---

## 1. Executive Summary

We observe statistically significant radiation-induced demagnetization of NdFeB permanent magnets deployed in the CEBAF tunnel. The primary result — the intra-plate NdFeB minus SmCo differential — is **−0.266% ± 0.027% (9.7σ)**, measured gain-immune by comparing materials on the same plate. This is confirmed by lab controls that show no such differential (−0.101% ± 0.045%, 2.0σ), yielding a tunnel-minus-lab difference of 3.7σ.

NdFeB grades (N42EH, N52SH) show clear degradation. SmCo grades (SmCo33H, SmCo35) show little to no degradation, consistent with their higher radiation resistance. Arc locations show approximately 2.4× more degradation than linac locations. Peak individual-sample degradation reaches −0.85%, nearly 3× the mean.

---

## 2. The Signal Exists

### 2.1 Per-Material Degradation (Y-plate Helmholtz, temperature-corrected)

| Grade | Type | Mean Change | Stat. Error | Significance | N |
|-------|------|-------------|-------------|--------------|---|
| N42EH | NdFeB | −0.333% | ± 0.034% | 9.8σ | 30 |
| N52SH | NdFeB | −0.260% | ± 0.037% | 7.1σ | 29 |
| SmCo33H | Sm₂Co₁₇ | +0.012% | ± 0.030% | 0.4σ (n.s.) | 29 |
| SmCo35 | Sm₂Co₁₇ | −0.077% | ± 0.031% | 2.5σ (marginal) | 30 |

All values carry an additional ±0.124% gain systematic (±0.248% before outlier cleaning). This systematic affects all absolute values equally but **cancels completely** in the intra-plate differential.

### 2.2 Gain-Immune Differential

The intra-plate NdFeB − SmCo differential compares materials measured on the same plate, in the same session, eliminating gain drift:

- **All 30 plates, baseline → latest**: −0.266% ± 0.027% **(9.7σ)**
- **15 plates, Aug 27 → Jan 12**: −0.265% ± 0.037% (7.2σ)

Materials are randomized across the 4 slots on each plate (4 cyclic rotation patterns), eliminating any positional radiation-gradient bias.

*(See: P1_material_comparison.png)*

---

## 3. It's Real (Lab Controls Confirm)

Nine Y-plates stored in the upstairs lab (no radiation exposure) serve as controls. Using the same Helmholtz measurement protocol:

| Measurement | NdFeB−SmCo Differential | Significance |
|-------------|------------------------|--------------|
| Tunnel (30 plates) | −0.266% ± 0.027% | 9.7σ |
| Lab control (9 plates) | −0.101% ± 0.045% | 2.0σ |
| **Tunnel − Lab** | **−0.165% ± 0.045%** | **3.7σ** |

The lab differential (−0.101%) is borderline (2.0σ) and likely reflects temperature bias: lab measurements lack co-incident temperature data, and a ~1.5°C difference from the 20°C reference would produce a −0.10% NdFeB−SmCo bias via the steeper NdFeB temperature coefficient (−0.10%/°C vs −0.04%/°C for SmCo). The tunnel−lab difference of 3.7σ confirms the radiation signal.

A comprehensive unexposed vs exposed analysis across all sample types (Y, H, A) is available in `Unexposed_vs_Exposed/` (plots U1–U3).

*(See: P4_lab_controls.png, U1_grand_comparison.png)*

---

## 4. It's Material-Dependent

### 4.1 NdFeB vs SmCo

Both NdFeB grades show significant degradation; both SmCo grades are consistent with zero (SmCo35 marginal at 2.5σ). This is consistent with the known radiation resistance hierarchy: SmCo (Sm₂Co₁₇) >> NdFeB.

### 4.2 Within NdFeB: N42EH Degrades More Than N52SH

An unexpected finding: **N42EH (−0.333%) degrades more than N52SH (−0.260%)**, despite N42EH having higher intrinsic coercivity (Hci ≥ 30 kOe vs ≥ 19 kOe). This is NOT a positional artifact — slot randomization confirms it.

Possible explanations:
- EH vs SH heat treatments may affect microstructure differently
- Boron content differences (¹⁰B neutron capture pathway)
- Operating point effects at the specific demagnetizing field

### 4.3 SmCo35 Marginal Signal

SmCo35 shows −0.077% ± 0.031% (2.5σ) — marginal. This is consistent with SmCo35 having lower Hci (≥ 18 kOe) and worse temperature coefficient of coercivity (β = −0.25%/°C) compared to SmCo33H (Hci ≥ 25 kOe, β = −0.20%/°C). SmCo35 ≠ SmCo33H for radiation resistance.

### 4.4 ΔT_crit Ranking

Using verified Allstar Magnetics specifications, the predicted radiation resistance ranking (via ΔT_crit at 5 kOe operating field):

| Grade | ΔT_crit | Predicted Resistance |
|-------|---------|---------------------|
| SmCo33H | 400°C | Best |
| SmCo35 | 289°C | Good |
| N42EH | 167°C | Moderate |
| N52SH | 123°C | Worst |

SmCo ranking matches observation. NdFeB ranking is **inverted** — N42EH should be more resistant but degrades more. This requires further investigation.

*(See: P6_tcrit_vs_observed.png)*

---

## 5. It's Position-Dependent

### 5.1 Arc vs Linac

NdFeB degradation varies strongly by tunnel region:

| Region | Mean NdFeB Change | Mean Body Dose (Sv)¹ | N |
|--------|-------------------|---------------------|---|
| Arcs (all 4) | −0.364% | >49.3 | 20 |
| North Linac | −0.154% | >100.3 | 4 |
| South Linac | −0.144% | >112.0 | 4 |
| Labyrinth | −0.244% | 0.9 | 2 |
| **Arc/Linac ratio** | **2.4×** | | |

¹ Dose values marked with `>` are **lower bounds** — 42/60 plates have ≥1 saturated OSL badge (saturation at 10 Gy per badge). Actual doses are higher than reported. Labyrinth doses are fully measured (no saturation).

**Counterintuitive: arcs show MORE degradation despite LOWER reported dose than linacs.** This is partially a saturation artifact (linac OSL saturates faster), but the pass-number trend within arcs (where saturation is less severe) confirms that position, not dose, is the dominant variable.

### 5.2 Peak vs Average

While the mean NdFeB degradation is −0.297%, individual samples range from −0.85% to near zero. The worst-case samples (NE Arc, high beam-loss regions) show degradation nearly **3× the average**.

This has implications for FFA magnet design: specifications should account for peak exposure, not just average.

### 5.3 Pass-Number Trend (Inverted — Unexplained)

Arc locations are organized by beamline pass (Line 1 = lowest energy, Line 5 = highest energy). The observed trend is **inverted from expectation**:

| Line | Mean NdFeB Change | Mean Body Dose (Sv)¹ | N |
|------|-------------------|---------------------|---|
| 1 | −0.554% | >21.0 | 4 |
| 2 | −0.390% | >54.0 | 4 |
| 3 | −0.298% | >60.6 | 4 |
| 4 | −0.261% | >55.8 | 4 |
| 5 | −0.316% | >55.1 | 4 |

¹ Lower bounds — most plates have saturated OSL badges.

**Line 1 receives the lowest dose but shows the most degradation.** This suggests the damage mechanism depends on radiation field quality (spectrum, geometry, beam optics) rather than total integrated dose. NDX dosimetry data from Kirsten may help resolve this.

*(See: P3_regional_breakdown.png, P8_waterfall_regional.png)*

---

## 6. Systematics Are Understood

### 6.1 Uncertainty Budget

| Source | Magnitude | Affects | Mitigation |
|--------|-----------|---------|------------|
| Helmholtz gain drift | ±0.124% (cleaned) | All absolute values | Cancels in intra-plate differential; ±0.248% uncleaned |
| Temperature correction | ~0.01–0.05% | Corrected values | Co-located Teslameter temps |
| Single baseline vulnerability | 33/120 samples | Baseline accuracy | Multi-baseline mean; future runs |
| Oct 21 thermal lag | ~0.3% inflation | Oct 21 only | Tunnel cooling faster than magnets |
| Jul 17 artifact | ~0.8% offset | Jul 17 group (15 plates) | Excluded from clean; shown flagged |
| Teslameter positioning | 0.3–16.5% std | Teslameter field only | Top face best (0.3%) |

**Key insight**: The dominant systematic (±0.124% cleaned / ±0.248% uncleaned gain drift) cancels completely in the intra-plate NdFeB−SmCo differential — our primary result. Cleaning excludes 2 flagged samples + 2 measurement outliers (>3% offset).

### 6.2 Jul 17 Data

The first tunnel campaign (Jul 17, 15 plates) shows a ~0.8% material-independent offset consistent with Helmholtz gain shift. All plots are shown both with and without this data for transparency. The Jul 17 data remains valid for the intra-plate differential (gain-immune).

### 6.3 Teslameter Assessment

The Teslameter field data is **uninformative for degradation detection** at the ~0.3% signal level:
- Top face positioning noise: 0.22% std (comparable to signal)
- Front face: 0.74% std
- Side face: 1.4% std
- SmCo A-sample top face: 16.5% std (catastrophic)

The Teslameter's primary value is providing co-located temperature measurements for Helmholtz correction. No pre-deployment field baseline exists (Hall probe and cap system changed before deployment).

*(See: P5_uncertainty_budget.png, P7_teslameter_summary.png, P2_timeseries_dual.png)*

---

## 7. Time Evolution

Temperature-corrected Helmholtz measurements across multiple campaigns show:
- Degradation present from the first clean measurement (Aug 27, 2025)
- Differential stable from Aug 27 through Jan 12 (double ratio = +0.067% ± 0.039%, 1.7σ — consistent with zero)
- No evidence of recovery during beam-off periods (as expected for permanent magnets at ~30°C)

*(See: P2_timeseries_dual.png)*

---

## 8. Additional Measurements

### 8.1 H-Plate (Pair Assembly) Results
- 30 H-plates with 85 pair assemblies passing temperature correction
- NdFeB H-plates: +0.026% ± 0.061% (within gain systematic)
- SmCo H-plates: +0.148% ± 0.061% (2.4σ positive — anomalous, likely gain artifact)
- H-plates carry full ±0.248% gain systematic (single-material plates, no intra-plate differential possible)

### 8.2 A-Sample (Individual Pair) Results
- 202 A-samples with temperature correction (90 NdFeB, 112 SmCo)
- NdFeB: +0.085% ± 0.022% — within gain systematic
- SmCo: +0.067% ± 0.016% — within gain systematic
- No NdFeB-SmCo separation possible (single-material plates)
- Positive shift consistent with gain drifting between pre-deployment and tunnel sessions

---

## 9. Dose-Degradation Correlation

### 9.1 Dosimetry Overview

Area dosimetry uses Landauer InLight L02TN badges (OSL + CR-39 track-etch + thermal neutron element) co-located with each plate. Badges were swapped approximately every 2 weeks by RADCON. The dose pipeline captures 782 plate-date entries across ~15 swap dates, with 99.6% successfully matched to Landauer reports.

**Critical caveat — OSL saturation**: The InLight OSL element saturates at 1000 rad (10 Gy) for photon/beta. At saturated positions, the reported body dose is a **lower bound** (1,000,000 mrem floor per saturated badge). CR-39 (neutron) does not saturate. **42 of 60 plates have at least one saturated badge**, meaning their cumulative doses are lower bounds. All tables and plots mark these with `>`.

### 9.2 Correlation Results

| Correlation (all 30 Y-plates) | Spearman ρ | p-value | Significant? |
|-------------------------------|-----------|---------|-------------|
| NdFeB mean vs body dose | 0.336 | 0.070 | No |
| SmCo mean vs body dose | 0.003 | 0.988 | No |
| NdFeB−SmCo diff vs body dose | 0.240 | 0.202 | No |
| NdFeB mean vs neutron dose | 0.156 | 0.412 | No |

**No significant dose-degradation correlation exists for any material or radiation type.** This persists whether using body dose, neutron dose, photon dose, or fast/thermal neutron breakdowns. The 22/30 saturated plates severely limit dynamic range for body dose, but even neutron dose (which never saturates) shows no correlation.

### 9.3 Radiation Field Composition by Region

| Region | Absorbed Dose (Gy)¹ | Photon (Gy) | Fast n (mGy) | Thermal n (mGy) | NdFeB% |
|--------|---------------------|-------------|-------------|-----------------|--------|
| Arcs | >11.2 | >10.8 | 16.1 | 5.5 | −0.364% |
| North Linac | >2.6 | >1.9 | 21.6 | 6.0 | −0.154% |
| South Linac | >6.9 | >3.1 | 18.4 | 5.4 | −0.144% |
| Labyrinth | 0.7 | 0.7 | 21.9 | 8.0 | −0.244% |

¹ Absorbed dose uses Q=1 for photon/beta, Q=10 for fast neutron (ICRP 60), Q=2.5 for thermal neutron (ICRP 103 continuous w_R). Values with `>` are lower bounds (saturated OSL).

### 9.4 Beam-Off Residual Activation

The March 2026 Landauer report (badges pulled Jan 8/12, 2026) covers the beam-off period (Sep 3, 2025 onward). These show:
- 53/101 badges non-zero (5–71 mrem body, all photon, zero neutron)
- Position-dependent: linacs ~103 mrem/yr, arcs ~17 mrem/yr, labyrinths ~52 mrem/yr
- Root cause: residual activation of tunnel infrastructure (Co-60, Mn-54, Na-22 gamma decay)
- SmCo proximity hypothesis (Co-59 activation in magnets) was empirically REJECTED (p=0.59)

*(See: dose_vs_degradation_scatter.png, dose_by_region.png, dose_vs_line_position.png, dose_vs_differential.png in Dosimetry/OSL_Area/)*

---

## 10. What's Coming Next

### 10.1 Immediate (Before Next Beam Run)
- NDX dosimetry data (from Kirsten/RADCON) — improved location mapping + higher-dose-range measurements may resolve pass-number inversion
- Optichromic rod data — high-range gamma dosimetry that does NOT saturate at 10 Gy, enabling true dose measurement at high-dose positions
- EH vs SH Dy content from Allstar certificates — confirm N42EH > N52SH inversion mechanism
- Honeywell room temperature data — enable proper lab control temperature correction

### 10.2 Measurement Improvements for Next Beam Run
- **Calibration protocol**: Measure 1–2 designated calibration samples at beginning AND end of each measurement day to track Helmholtz gain stability
- **Teslameter error analysis campaigns** on lab-based samples
- **Lab Helmholtz with temperature measurements** (currently lacking)
- More careful measurement methodologies
- This will dramatically reduce the ±0.248% gain systematic

### 10.3 Longer Term
- Publication-ready figure set with dose-response curves
- FFA magnet specification recommendations based on peak exposure levels
- Continued monitoring through additional beam-on periods

---

## Plot Index

| Plot | File | Content |
|------|------|---------|
| P1 | P1_material_comparison.png | Material bars + gain band + differential inset |
| P2 | P2_timeseries_dual.png | Dual time series (with/without Jul 17) |
| P3 | P3_regional_breakdown.png | Regional breakdown (arc vs linac) |
| P4 | P4_lab_controls.png | Lab control validation |
| P5 | P5_uncertainty_budget.png | Uncertainty budget table |
| P6 | P6_tcrit_vs_observed.png | ΔT_crit predicted vs observed |
| P7 | P7_teslameter_summary.png | Teslameter honest assessment |
| P8 | P8_waterfall_regional.png | NdFeB waterfall by region (peak vs average) |
| P9 | P9_waterfall_all_materials.png | Waterfall chart — all 4 materials |
| P10 | P10_h_plate_material.png | H-plate NdFeB vs SmCo material comparison |
| P11 | P11_a_sample_summary.png | A-sample bars + A-vs-H correlation scatter |
| P12 | P12_combined_YHA.png | Combined Y+H+A comparison across sample types |
| P13 | P13_ha_lab_vs_tunnel.png | H/A lab vs tunnel comparison (2-panel) |
| P14 | P14_coloc_crossref.png | Co-located Y↔H cross-reference (raw + gain-corrected) |

### Dosimetry Plots (in `Dosimetry/OSL_Area/`)

| Plot | File | Content |
|------|------|---------|
| D1 | dose_vs_degradation_scatter.png | 4-panel scatter by material (body dose vs % change) |
| D2 | dose_by_region.png | Regional dose vs degradation bars |
| D3 | dose_vs_line_position.png | Arc pass-number dose + degradation trend |
| D4 | dose_vs_differential.png | Gain-immune differential vs dose |
| D5 | dose_timeline_overlay.png | Representative plate dose time series |
| D6 | dose_by_radiation_type_ndfeb.png | Radiation type breakdown vs NdFeB |
| D7 | dose_by_radiation_type_differential.png | Radiation type vs differential |
| D8 | dose_regional_composition.png | Regional dose composition (photon/neutron/beta) |
| D9 | dose_vs_degradation_YHA.png | Combined Y+H+A scatter |

### Unexposed vs Exposed (in `Unexposed_vs_Exposed/`)

| ID | File | Description |
|----|------|-------------|
| U1 | U1_grand_comparison.png | 4-panel bar chart: Y differential, Y per-material, H per-material, A per-material |
| U2 | U2_strip_all_types.png | Strip plot — individual sample distributions (tunnel vs lab) |
| U3 | U3_forest_effect_sizes.png | Forest plot — tunnel−lab effect sizes across all comparisons |

### Time Series Evolution (in `Time_Series/`)

| ID | File | Description |
|----|------|-------------|
| T1 | T1_ensemble_mean_vs_time.png | Ensemble mean ± SEM vs time — all sample types (Y/H/A) + NdFeB−SmCo differential |
| T2 | T2_spaghetti_trajectories.png | Individual Y-plate trajectories (spaghetti) — 2-panel NdFeB vs SmCo, color by region |
| T3 | T3_degradation_vs_dose_timeresolved.png | Degradation vs cumulative dose, color by measurement date |
| T4 | T4_regional_time_evolution.png | Regional time evolution — NdFeB Y-plates by Arc/Linac/Labyrinth |
| T5 | T5_dose_accumulation_by_region.png | Cumulative dose vs time by region — Y-plates, Hn-plates, Hs-plates |
| T6 | T6_degradation_and_dose_by_region.png | Dual-axis: NdFeB degradation + cumulative dose vs time, 4 regional panels |
| T7 | T7_per_plate_dose_timeline.png | Per-plate dose timeline with Helmholtz measurement dates marked |

### Dose-Region Breakdowns (in `Dose_Region_Breakdowns/`)

| ID | File | Description |
|----|------|-------------|
| R1 | R1_dose_bins.png | Degradation by dose tertile and region |
| R2 | R2_radiation_composition.png | Radiation type fractions + photon fraction vs degradation |
| R3 | R3_dose_response.png | Dose-response scatter with linear fits |
| R4 | R4_arc_lines.png | Arc line position: dose and degradation side by side |

---

*Generated from analysis scripts in `Cleanup_Claude/`. Primary data analysis: `manager_summary_v3.py` (Y-plate Helmholtz), `manager_summary_v5.py` (combined Y+H), `presentation_plots.py` (presentation figures), `dose_degradation_correlation.py` (dose analysis), `build_dose_map.py` (dose pipeline), `unexposed_vs_exposed.py` (lab vs tunnel comparisons), `dose_region_breakdowns.py` (dose-region breakdowns), `time_series_evolution.py` (time series analysis). Full technical details in `Manager_Plots/DEGRADATION_SUMMARY.md`.*
