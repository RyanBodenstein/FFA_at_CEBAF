# Comprehensive Error Analysis — FFA@CEBAF Magnet Radiation Study
# Date: 2026-04-01 (v3: per-date temperature correction)
# Supersedes: v2 (23°C blanket, backed up as systematic_error_investigation_v2_23C.md)

---

## 1. Headline Result

The NdFeB-SmCo intra-plate differential from 30 tunnel Y-plates, corrected to per-date
baseline temperatures (~24°C), is:

> **-0.208% ± 0.028%(stat) (7.6σ)**

This is the gain-immune, randomized, Helmholtz-measured differential between
radiation-sensitive (NdFeB) and radiation-hard (SmCo) permanent magnets after
~18 months in the CEBAF tunnel.

Lab controls (9 Y-plates, zero radiation, identical measurement protocol):
- Lab differential: **-0.007% ± 0.038% (0.2σ)** — consistent with zero
- Tunnel minus Lab: **-0.202% ± 0.047% (4.3σ)** — independent confirmation

Individual materials (per-date correction, tunnel Y-plates):

| Material | Change (%) | SEM (%) | Notes |
|----------|-----------|---------|-------|
| N42EH | -0.252 | ±0.036 | Most degraded |
| N52SH | -0.170 | ±0.036 | Less degraded |
| SmCo33H | +0.037 | ±0.031 | Near zero (expected) |
| SmCo35 | -0.044 | ±0.031 | Near zero (expected) |

The NdFeB grades show clear radiation-induced degradation; SmCo grades are consistent
with zero, as expected for radiation-hard materials. N42EH degrades more than N52SH,
consistent with lower Dy content providing less radiation resistance.

---

## 2. Temperature Correction History

The single largest systematic in this analysis is the temperature assumed for the
pre-deployment baseline measurements (Nov 2024). Three correction versions have been
applied:

| Version | Assumed T | Method | Diff (%) | SEM (%) | Significance |
|---------|-----------|--------|----------|---------|-------------|
| v1 (original) | ~25°C (probe) | No correction, raw probe temps | -0.266 | 0.028 | 9.6σ |
| v2 (overcorrected) | 23.0°C (blanket) | Uniform 23°C for all dates | -0.134 | 0.028 | 4.9σ |
| **v3 (current)** | **~24°C (per-date)** | **Data-driven, per-date estimates** | **-0.208** | **0.028** | **7.6σ** |

Individual materials across all three corrections:

| Material | v1 (probe ~25°C) | v2 (blanket 23°C) | v3 (per-date ~24°C) |
|----------|-----------------|-------------------|---------------------|
| N42EH | -0.337% | -0.137% | **-0.252%** |
| N52SH | -0.265% | -0.044% | **-0.170%** |
| SmCo33H | +0.003% | +0.083% | **+0.037%** |
| SmCo35 | -0.079% | +0.001% | **-0.044%** |

### Why v3 is best-justified

1. **Data-driven per-date temperatures** based on same-day Y-H probe comparisons,
   not assumptions about room temperature on arbitrary dates.

2. **Physically sensible results**: SmCo near zero (radiation-hard, as expected),
   both NdFeB grades clearly negative, N42EH > N52SH (consistent with Dy content).
   - v2 (23°C) made SmCo33H anomalously positive (+0.083%)
   - v1 (probe) had SmCo35 at -0.079% (2.5σ degradation of a radiation-hard material)

3. **Robust regardless**: The signal is >5σ across the entire 23-25°C range. The
   question is magnitude, not existence.

---

## 3. Probe Bias Assessment

### Single instrument, single probe

There is only ONE Teslameter (SENIS 3MH6-E) with one Hall probe at any given time.
Y-plates, H-plates, and A-samples all use the SAME device. The probe was replaced
between Dec 2024 and Jul 2025 (it broke and was replaced before tunnel deployment).
Therefore, Y-vs-H temperature differences on the same date reflect measurement timing
and room conditions, NOT different probes.

### Same-day evidence

Only 2 pre-deployment dates have both Y and H readings with the old probe:

| Date | Y mean (°C) | H mean (°C) | Y-H (°C) | Y measured | H measured | Time gap |
|------|------------|------------|----------|-----------|-----------|---------|
| Sep 30, 2024 | 26.66 | 25.80 | **+0.87** | 16:36 | 15:18 | +1.3h later |
| Nov 20, 2024 | 25.38 | 24.62 | **+0.77** | 15:12 | 14:18 | +0.9h later |

The Y-H difference is only **~0.8°C**, largely explainable by measurement timing
(Y measured ~1 hour later → room slightly warmer in afternoon).

For comparison, tunnel-era data (new probe, near-simultaneous Y/H measurements) shows
Y-H = **-0.15°C ± 0.14°C** across 10 dates — confirming that same-probe, same-time
differences are small.

### The original +2°C assumption was wrong

The v2 correction assumed the probe was +2°C high, based on comparing Y-plate temps
on Nov 5/7 (~24.6-25.1°C) to an H reading of 22.8°C on Dec 4. But:

1. Nov 5/7 and Dec 4 are **different days** — lab temperature varied 23.0-26.3°C
   across November, so cross-day comparisons measure room variation, not probe bias.
2. The only **same-day** evidence (Sep 30, Nov 20) shows Y-H of +0.8°C, not +2°C.
3. The Dec 4 reading (22.8°C) was simply a cold day, not representative of November.

### Per-date temperature estimates (v3)

Using the +0.8°C same-day bias and direct H readings where available:

| Date | Y probe (°C) | Correction | Estimated true T (°C) | Source |
|------|-------------|-----------|----------------------|--------|
| Nov 5, 2024 | 25.1 | -0.8 (same-day bias) | **24.3** | Pooled same-day evidence |
| Nov 7, 2024 | 24.6 | -0.8 (same-day bias) | **23.8** | Pooled same-day evidence |
| Nov 20, 2024 | 25.4 | direct H available | **24.6** | Same-day H = 24.62°C |
| Sep 30, 2024 | 26.7 | direct H available | **25.8** | Same-day H = 25.80°C |

These values are implemented in `Y_BASELINE_TEMP_LOOKUP` in `manager_summary_v3.py`.

**Source**: `Sensitivity_Analysis/probe_bias_assessment.txt`, `probe_temperature_comparison.txt`

---

## 4. Temperature Sensitivity

### Linear dependence

The differential depends linearly on the assumed baseline temperature:

> **-0.066%/°C** shift in the NdFeB-SmCo differential per 1°C change in assumed lab temperature

This follows directly from the difference in temperature coefficients:
- NdFeB: α(Br) ≈ -0.105%/°C (average of N42EH=-0.10, N52SH=-0.11)
- SmCo: α(Br) ≈ -0.040%/°C
- Differential: Δα ≈ -0.065%/°C (predicted) vs -0.066%/°C (observed) — excellent agreement

### Scan across temperatures

| Assumed T (°C) | Differential (%) | Significance |
|----------------|-----------------|-------------|
| 23.0 (v2) | -0.134 | 5.0σ |
| 23.5 | -0.166 | 6.1σ |
| 24.0 | -0.199 | 7.2σ |
| **~24.1 (v3 mean)** | **-0.208** | **7.6σ** |
| 24.5 | -0.231 | 8.4σ |
| 25.0 (≈probe) | -0.264 | 9.6σ |

### Physical constraints — SmCo zero-crossings

SmCo should NOT show significant positive changes (it is radiation-hard):
- SmCo33H crosses zero at **T_lab ≈ 25.1°C**
- SmCo35 crosses zero at **T_lab ≈ 23.0°C**

The v3 per-date correction (~24°C mean) places SmCo33H slightly positive (+0.037%)
and SmCo35 slightly negative (-0.044%) — physically sensible. The v2 blanket (23°C)
made SmCo33H anomalously positive (+0.083%), suggesting overcorrection.

**Source**: `Sensitivity_Analysis/temp_sensitivity.py`, `sensitivity_results.txt`

---

## 5. Temperature Coefficient (α) Uncertainty

### Manufacturer values (Allstar Magnetics datasheets)

| Material | α(Br) (%/°C) | Code value |
|----------|-------------|-----------|
| N42EH | -0.10 | -0.0010 |
| N52SH | -0.11 | -0.0011 |
| SmCo33H | -0.040 | -0.0004 |
| SmCo35 | -0.040 | -0.0004 |

Manufacturer uncertainty: ±5-10% relative per grade, ±20% worst case.

### Empirical measurement (attempted, unsuccessful)

Teslameter positioning jig noise (0.14-1.9% std depending on face) dominates the
temperature signal (0.4-0.9% over ~9°C span in tunnel). With only 4 tunnel dates
having adequate temperature spread, empirical slopes scatter from 10% to 184% of
nominal — pure noise. A dedicated temperature sweep without removing the jig would
be needed.

### Impact on results

| α tolerance | Differential shift | Individual shift | Assessment |
|-------------|-------------------|-----------------|-----------|
| ±10% | ±0.014% | ±0.021% | Negligible vs stat (±0.028%) |
| ±20% (worst) | ±0.028% | ±0.042% | Comparable to stat, still negligible vs gain |

The α uncertainty is **negligible** relative to all other systematics.

---

## 6. Gain Drift Systematic

### Quantification

The Helmholtz coil system (Fluxmeter Model 2130) exhibits session-to-session gain
drift. From `gain_systematic_analysis.py`:

| Metric | Value |
|--------|-------|
| Gain systematic (cleaned, outliers removed) | **±0.124%** |
| Gain systematic (uncleaned) | ±0.248% |
| Outlier exclusions | Y-34-4, Y-40-4 (|change| > 3%) |
| Session-to-session drift | 0.5-0.7% typical |

### Known artifacts

- **Oct 21, 2025**: ~0.3% thermal lag artifact (beam-off period, tunnel cooling).
  Common-mode — affects all materials equally.
- **Jul 17, 2025**: ~0.8% offset (first tunnel measurement, only 15 plates, coil
  warmup/connection effects). Superseded by later full surveys.

### Cancellation in intra-plate differential

The Y-plate differential is computed **intra-plate**: each plate carries 4 magnets
(1 each of N42EH, N52SH, SmCo33H, SmCo35), measured in a single Helmholtz session.
Any multiplicative gain drift cancels exactly in the ratio:

> Δ_plate = (NdFeB_mean - SmCo_mean) / baseline

The gain factor is common to all 4 magnets on the same plate in the same session,
so the NdFeB-SmCo differential is **gain-immune by construction**.

This is why the Y-plate differential (±0.028% statistical uncertainty) is far more
precise than any individual material measurement (±0.036% stat + ±0.124% gain).

**Source**: `gain_systematic_analysis.py`

---

## 7. Sample Type Comparison

### Results by sample type (tunnel only, v3 correction)

| Type | NdFeB-SmCo Diff (%) | SEM (%) | Significance | N | Method |
|------|---------------------|---------|-------------|---|--------|
| **Y-plate** | **-0.208** | **0.028** | **7.6σ** | 30 plates | Intra-plate (gain-immune) |
| H-plate | -0.122 | 0.079 | 1.5σ | 37+48 pairs | Inter-sample (NOT gain-immune) |
| A-sample | +0.020 | 0.055 | 0.4σ | 13+16 slots | Inter-sample (NOT gain-immune) |

### Individual NdFeB results

| Type | NdFeB (%) | SEM (%) | Sig | N |
|------|-----------|---------|-----|---|
| Y-plate | -0.212 | 0.026 | 8.2σ | 59 slots |
| H-plate | +0.026 | 0.050 | 0.5σ | 37 pairs |
| A-sample | +0.087 | 0.043 | 2.0σ | 13 slots |

### Sample scatter

| Type | NdFeB std (%) | N | SmCo std (%) | N |
|------|--------------|---|-------------|---|
| Y-plate | 0.197 | 59 | 0.171 | 59 |
| H-plate | 0.307 | 37 | 0.424 | 48 |
| A-slot | 0.154 | 13 | 0.136 | 16 |

H-plates are 1.6× noisier (NdFeB) and 2.5× noisier (SmCo) than Y-plates.

### Why H-plates and A-samples show weaker signals

1. **Not gain-immune**: H and A measurements are inter-sample (comparing different
   plates/assemblies measured in different sessions), so they carry the full ±0.124%
   gain systematic.

2. **H-plate location confounding**: H-plates are identified by arc placement
   (N-prefix in SE/NW arcs, S-prefix in NE/SW arcs). NdFeB and SmCo are NOT
   randomly distributed across arcs — NdFeB (Hn) and SmCo (Hs) occupy different
   tunnel locations, confounding material type with radiation environment.

3. **A-sample statistics**: Only 13+16 slot-level points, vs 30 plates (59+59 slots)
   for Y-plates.

### Combining dilutes the signal

Inverse-variance weighted NdFeB mean:
- Y-only: -0.212% ± 0.026% (8.2σ)
- Combined Y+H+A: -0.107% ± 0.020% (5.3σ)

Combining **reduces** significance from 8.2σ to 5.3σ because H/A means are near
zero, pulling the combined average toward zero. H/A have fundamentally different
systematics (not gain-immune, different geometry, location confounding).

**Recommendation**: Present Y, H, and A results separately. Never average them.
The Y-plate differential is the headline result.

**Source**: `Sensitivity_Analysis/sample_type_comparison.py`, `sample_type_results.txt`

---

## 8. Lab Control Cross-Check

### Lab Y-plate differential

Nine Y-plates (plates 8, 14, 27, 28, 29, 31, 33, 35, 37) were stored in lab boxes
with zero radiation exposure. They underwent the identical measurement protocol
(same Helmholtz coil, same Teslameter, same schedule) as tunnel plates.

| Measurement | NdFeB (%) | SmCo (%) | Differential (%) | Sig |
|-------------|----------|---------|-----------------|-----|
| Tunnel Y (30 plates) | -0.212 ± 0.026 | -0.004 ± 0.022 | -0.208 ± 0.028 | 7.6σ |
| Lab Y (9 plates) | +0.014 ± 0.025 | +0.020 ± 0.018 | -0.007 ± 0.038 | 0.2σ |
| **Tunnel − Lab** | **-0.226 ± 0.036** | **-0.024 ± 0.029** | **-0.202 ± 0.047** | **4.3σ** |

### Interpretation

- **Lab differential = zero** (-0.007%): The measurement system introduces no
  material-dependent bias. This validates the Helmholtz + temperature correction
  pipeline.

- **Tunnel-Lab excess = -0.202%** (4.3σ): The tunnel Y-plates show degradation
  that lab controls do not. This is an independent confirmation of radiation-induced
  NdFeB degradation, using a completely different statistical test (two-population
  comparison rather than within-plate differential).

- **Lab H/A not directly comparable**: Lab H and A samples have different gain drift
  histories (different session schedules), so they cannot be used as clean controls
  for the inter-sample H/A measurements.

**Source**: `unexposed_vs_exposed.py`

---

## 9. Other Known Systematics

### Helmholtz DC accuracy

The Fluxmeter Model 2130 has DC accuracy of 0.050% typical, 0.100% max (of
full-scale). This is an absolute accuracy floor for any individual measurement but
is common-mode — it cancels in the intra-plate differential.

### Cap/rig changes

The Helmholtz cap system was changed before tunnel deployment (new cap + probe swap).
Any resulting baseline offset is common-mode and cancels in the NdFeB-SmCo
differential.

### Baseline vulnerability

Y-plate baselines are robust: measured in 2-3 pre-deployment sessions (Nov 2024) per
plate. However, some H/A samples have single-session baselines, making them more
vulnerable to measurement-day effects. Several H-plate pairs (e.g., Hn-9-3, Hn-9-4)
show anomalous first readings (>50% outliers), flagged and excluded.

### Teslameter positioning noise

Teslameter rig precision: top face 0.14-0.29% std, front face 0.57-0.91%, side face
0.90-1.90%. This is irrelevant for the Helmholtz-based results (the Helmholtz coil
integrates over the full sample volume and is fairly independent of sample position).
The Teslameter is used only for temperature readings, not for the degradation measurement.

### Dose-degradation correlations

Gamma dose does NOT correlate with degradation (Spearman ρ = 0.210, p = 0.27 for
differential). Neutron dose shows significant correlation (ρ = 0.389, p = 0.03 for
differential; ρ = 0.459, p = 0.01 for NdFeB). Position in the tunnel (beam line)
dominates over total accumulated dose: Line 1 shows the most degradation but the
least dose (inverted). This suggests the damage mechanism is neutron-dominated, not
gamma-dominated.

Fast neutron dose correlates more strongly than thermal (ρ = 0.308 vs 0.187 for
NdFeB; ρ = 0.215 vs 0.151 for differential), suggesting displacement cascades as
the dominant damage mechanism rather than nuclear capture. However, neither
component reaches significance individually; the total neutron sum (which reduces
measurement noise) produces the strongest correlation.

**Multiple comparisons context**: The analysis tests correlations for 7 degradation
metrics × 3 dose types = 21 hypothesis tests. The neutron-differential p = 0.03
would not survive a Bonferroni correction (threshold = 0.05/21 = 0.0024). However,
this test is properly framed as a *directed hypothesis test*, not exploratory data
mining: the radiation damage hierarchy (neutron >> gamma) is well-established in
the literature (Shen 2018, Simos 2018, Bizen 2016), and our correlation analysis
was designed to test this specific physical prediction. The neutron correlation is
further supported by: (1) NdFeB-specific effect (SmCo null, p = 0.64), consistent
with lower Curie temperature making NdFeB more susceptible; (2) the gamma null
result, consistent with the Alderman et al. (2002) ⁶⁰Co gamma null at 700 Mrad; (3) the fast >
thermal trend matching the displacement cascade mechanism expected at accelerator
neutron energies. We report the uncorrected p-values throughout and note that a
Bonferroni correction would render the individual neutron results non-significant
at the 5% level.

**Source**: `Rod_Dosimetry/rod_correlation_stats.txt`

---

## 10. Formal Error Budget

### Gain-immune differential (NdFeB-SmCo) — HEADLINE RESULT

| Source | Magnitude | Notes |
|--------|-----------|-------|
| Statistical (SEM) | ±0.028% | From 30 Y-plate data |
| Baseline temp (±0.5°C) | ±0.033% | 0.066%/°C × 0.5°C |
| α uncertainty (±10%) | ±0.014% | Manufacturer tolerance |
| Gain systematic | **0 (cancels)** | Intra-plate cancellation |
| **Combined (quadrature)** | **±0.045%** | |
| | | |
| **Result** | **-0.208% ± 0.045%** | **4.6σ combined significance** |

Derivation: √(0.028² + 0.033² + 0.014²) = √(0.000784 + 0.001089 + 0.000196)
= √0.002014 = 0.045%.

### Individual materials (gain-sensitive)

| Source | Magnitude | Notes |
|--------|-----------|-------|
| Statistical (SEM) | ±0.036% | Per-material (NdFeB) |
| Baseline temp (±0.5°C) | ±0.05% | 0.105%/°C × 0.5°C (NdFeB) |
| α uncertainty (±10%) | ±0.021% | Conservative |
| Gain systematic | **±0.124%** | Dominates |
| **Combined (quadrature)** | **±0.140%** | Gain-dominated |

Individual material results should be presented with ±0.14% systematic uncertainty,
but the **differential is the primary measurement** because gain cancels.

### Temperature uncertainty justification

The ±0.5°C uncertainty on baseline temperature is based on:
1. Same-day Y-H measurements showing +0.77°C and +0.87°C (mean +0.82°C)
2. Day-to-day lab temperature variation of ~3°C across November 2024
3. The per-date correction uses H readings directly where available (Nov 20, Sep 30)
   and applies the +0.8°C bias for Y-only dates (Nov 5, Nov 7)
4. The residual uncertainty after this data-driven correction is ±0.5°C or better

---

## 11. Summary and Conclusions

### The signal is real

The NdFeB-SmCo differential of **-0.208% ± 0.028%(stat)** is significant at:
- **7.6σ statistical** (from 30 intra-plate measurements)
- **4.6σ combined** (including ±0.033% temp + ±0.014% α systematics in quadrature)
- **4.3σ independently** from the tunnel-lab excess comparison

### Robust across all reasonable temperatures

| Temperature range | Differential | Statistical significance |
|-------------------|-------------|------------------------|
| 23.0-25.0°C | -0.134% to -0.264% | 5.0σ to 9.6σ |
| 23.5-24.5°C (best estimate) | -0.166% to -0.231% | 6.1σ to 8.4σ |
| **~24.1°C (v3 per-date)** | **-0.208%** | **7.6σ** |

The signal exceeds 5σ for any baseline temperature in the 23-25°C range.

### Lab controls independently confirm

Lab Y-plates show zero material-dependent bias (-0.007% ± 0.038%), proving the
measurement system is clean. The 4.3σ tunnel-lab excess is a completely independent
confirmation using a different statistical method.

### Analyst bias mitigation (in lieu of blind analysis)

No formal blind analysis was performed. However, the experimental design contains
multiple structural features that mitigate analyst bias:

1. **Randomized material assignments**: The 4 material grades (N42EH, N52SH,
   SmCo33H, SmCo35) were randomly assigned to slots on each Y-plate before
   deployment. The analyst had no control over which material occupied which
   position, eliminating selection bias.

2. **Algorithmic headline result**: The NdFeB-SmCo differential is computed from
   a fixed formula (mean of NdFeB slots minus mean of SmCo slots, per plate,
   then averaged) applied identically to all 30 tunnel and 9 lab plates. There
   is no subjective judgment in the computation.

3. **Gain cancellation by construction**: The intra-plate differential cancels
   Helmholtz gain drift — the dominant instrumental systematic — regardless of
   analyst choices. This is a property of the measurement geometry, not a
   correction applied post hoc.

4. **Temperature correction from independent data**: The per-date baseline
   temperatures are derived from same-day H-plate readings and a measured probe
   bias (+0.8°C), not tuned to optimize the differential. All three correction
   versions (v1/v2/v3) are reported, demonstrating that the signal persists
   (5-10σ) across the full reasonable range.

5. **Identical treatment of controls**: Lab Y-plates follow the same measurement
   protocol, data reduction pipeline, and temperature correction as tunnel plates.
   Their null result (-0.007% ± 0.038%) provides independent confirmation that
   the pipeline does not generate spurious material-dependent signals.

A formal blind analysis — where tunnel/lab identity is hidden during data
reduction — would strengthen the result further, and is recommended for any
future exposure campaign.

### What matters and what doesn't

| Factor | Matters? | Impact |
|--------|---------|--------|
| Baseline temperature | Yes — largest systematic | ±0.033% on differential |
| Gain drift | **No** — cancels in differential | ±0.124% on individual only |
| α coefficient uncertainty | No — negligible | ±0.014% on differential |
| Helmholtz DC accuracy | No — common-mode | Cancels in differential |
| Teslameter positioning | No — separate measurement | Not used for degradation |
| Sample type (H/A) | Dilutes signal | Present Y separately |

### Awaiting resolution

1. **Honeywell room temperature data** (Task 6): Independent lab temperature record
   that would definitively resolve the pre-deployment baseline temperature.
2. **Dy weight percent** (Task 12): Would quantify the N42EH vs N52SH difference.
3. **NDX neutron dose data** (Task 14): Would complement the existing CR-39 neutron
   measurements and strengthen the dose-degradation correlation.
4. **Pass-number analysis** (Tasks 15-16): Would test whether degradation scales
   with beam exposure time.

---

## Appendix: Version History

| Version | Date | Correction | Headline | File |
|---------|------|-----------|----------|------|
| v1 | 2026-03-27 | None (probe temps) | -0.266% (9.6σ) | `_v1_2026-03-27.md` |
| v2 | 2026-03-27 | Blanket 23°C | -0.134% (4.9σ) | `_v2_23C.md` |
| **v3** | **2026-04-01** | **Per-date ~24°C** | **-0.208% (7.6σ)** | **this file** |

## Data Sources

All numbers verified against actual script outputs:
- `manager_summary_v3.py` — per-date correction, material means, lab controls
- `Sensitivity_Analysis/temp_sensitivity.py` — temperature scan, 0.066%/°C slope
- `Sensitivity_Analysis/sample_type_comparison.py` — Y vs H vs A, combining test
- `Sensitivity_Analysis/probe_temperature_comparison.py` — same-day Y-H evidence
- `gain_systematic_analysis.py` — ±0.124% cleaned, session-by-session drift
- `unexposed_vs_exposed.py` — tunnel-lab comparison, 4.3σ excess
- `Rod_Dosimetry/rod_correlation_stats.txt` — dose-degradation correlations
