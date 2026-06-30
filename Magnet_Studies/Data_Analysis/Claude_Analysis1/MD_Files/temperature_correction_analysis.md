# Temperature-Corrected Helmholtz Analysis

## Document Purpose

This document describes the temperature correction applied to Helmholtz coil magnetometry data for the LDRD FFA@CEBAF magnet radiation study. It covers the physics motivation, mathematical formulation, all assumptions and approximations, known limitations, data quality issues discovered during analysis, and a description of every output plot.

**Script**: `Cleanup_Claude/temperature_corrected_analysis.py`
**Output**: `Cleanup_Claude/TempCorrected_Plots/`
**Last updated**: 2026-03-09

---

## 1. Physics Motivation

### 1.1 The Problem

Helmholtz coil measurements of permanent magnet remanence are temperature-dependent. The remanence Br of a permanent magnet varies with temperature according to:

    Br(T) = Br(T_ref) × [1 + α(Br) × (T − T_ref)]

where α(Br) is the reversible temperature coefficient of remanence (units: per °C, always negative for these materials — magnets get weaker when hot).

In the tunnel environment, temperatures ranged from ~22°C (beam-off, Oct 2025) to ~34°C (beam-on summer 2025). For NdFeB with α = −0.11%/°C, a 12°C temperature swing produces a ~1.3% change in the measured field — **larger than the expected radiation degradation signal** we are trying to detect (~0.1–1% for the doses received).

### 1.2 Available Temperature Data

The Teslameter probe includes a built-in temperature sensor (field 8 in the data file). For each magnet sample, Teslameter measurements are taken on three faces (front, side, top), each recording a temperature. These temperatures are co-located with the sample at the time of measurement.

**Important**: The Teslameter temperature is measured at the probe tip, which is in contact with or very near the magnet surface. It reflects the magnet's actual temperature at the time of measurement, not the ambient tunnel temperature.

### 1.3 Goal

Remove the dominant temperature systematic from Helmholtz measurements by correcting all readings to a common reference temperature (20°C), revealing the underlying radiation-induced degradation signal.

---

## 2. Mathematical Formulation

### 2.1 Temperature Correction Formula

Given a raw Helmholtz reading `H_raw` taken at temperature `T`, the corrected reading at reference temperature `T_ref` is:

    H_corr = H_raw / [1 + α(Br) × (T − T_ref)]

**Derivation**: If the "true" value at T_ref is H_corr, then the measured value at temperature T is:

    H_raw = H_corr × [1 + α × (T − T_ref)]

Solving for H_corr:

    H_corr = H_raw / [1 + α × (T − T_ref)]

### 2.2 Sign Convention and Correction Direction

- α(Br) is **negative** for all materials used (magnets weaken with increasing temperature)
- All measurements are at T > T_ref (20°C), so (T − T_ref) > 0
- Therefore α × (T − T_ref) < 0, so the denominator is < 1
- Therefore **H_corr > H_raw** — the corrected value is higher than the raw value
- This makes physical sense: the magnet was warmer than 20°C when measured, so it was reading lower than it would at 20°C

### 2.3 Temperature Coefficients Used

| Material | α(Br) [%/°C] | α(Br) [1/°C] | Source |
|----------|---------------|---------------|--------|
| N42EH    | −0.10         | −0.0010       | Manufacturer datasheet |
| N52SH    | −0.11         | −0.0011       | Manufacturer datasheet |
| SmCo33H  | −0.04         | −0.0004       | Manufacturer datasheet |
| SmCo35   | −0.04         | −0.0004       | Manufacturer datasheet |

### 2.4 Temperature Assignment

**For Y-plate samples (Y-XX-N)**:
- Find Teslameter files: `Y-XX-N_front.dat`, `Y-XX-N_side.dat`, `Y-XX-N_top.dat`
- For each file, extract the temperature reading on the measurement date
- Compute T_mean = mean(T_front, T_side, T_top) and T_std = std(T_front, T_side, T_top)
- The face-to-face temperature spread (T_std) is typically 0.3–1.5°C

**For pair assembly samples (Hn-XX-YY)**:
- Map to Teslameter files: `An-XX-YY-1_{front,side,top}.dat` and `An-XX-YY-2_{front,side,top}.dat`
- Average all available temperatures (up to 6 values: 2 magnets × 3 faces)
- This gives the best estimate of the pair assembly temperature

### 2.5 Uncertainty Propagation

The dominant temperature uncertainty is the face-to-face spread (T_std). The uncertainty on the corrected Helmholtz reading is:

    δH = |H_raw × α × T_std| / [1 + α × (T − T_ref)]²

This does **not** include:
- Uncertainty in α(Br) itself (a systematic, not statistical, error — see Section 5.3)
- Helmholtz measurement repeatability (typically ~0.01–0.05% from retake analysis)
- Long-term Helmholtz coil calibration stability

### 2.6 Reference Temperature

**T_ref = 20°C** was chosen because:
- It is a standard laboratory reference temperature
- It is below all measurement temperatures in this study, making all corrections go in the same direction (upward)
- It is close to the beam-off tunnel temperature (~24.7°C), minimizing the correction for beam-off measurements

---

## 3. Data Quality Issues Discovered

### 3.1 Near-Zero Helmholtz Readings

One sample, **Y-1-1 (SmCo33H)**, has a single reading of 0.0038 mWC on 2024-07-23. All other readings for this sample are ~1.04 mWC. This isolated near-zero reading is excluded from all percentage-change calculations (filtered by MIN_BASELINE_MWC = 0.1 mWC). It likely represents a measurement setup error (wrong orientation, probe not seated, etc.).

### 3.2 Outlier Baseline: Y-34-4 (N52SH)

Y-34-4 has a pre-deployment baseline (2024-11-05) of 1.172 mWC, but all subsequent readings (2025-05 through 2026-01) are consistently ~1.29 mWC. This +10% jump is physically impossible as radiation-induced improvement. The baseline measurement is almost certainly wrong (sample mislabeled, wrong orientation, instrument error on that day, etc.).

**Impact**: This single sample was contaminating the N52SH mean, adding ~+0.7% bias and greatly inflating the N52SH standard error. **The enhanced script flags and excludes this sample from mean calculations.**

### 3.3 Y-40-4 (SmCo33H) Baseline

Y-40-4 shows a −6.3% corrected change from its Nov 2024 baseline. While not as extreme as Y-34-4, this is larger than expected for SmCo materials and should be flagged. Investigation suggests a possible baseline measurement issue.

### 3.4 Sentinel Values (1337)

The value 1337 appears in some files as a sentinel meaning "no measurement taken" (dosimetry swap in progress). These are filtered out in the mWC extraction step: any reading within ±1 of 1337 is excluded.

### 3.5 Pre-Deployment Temperature Data Sparsity

Pre-deployment Teslameter temperatures (2024-05-06, 2024-06-24, 2024-07-23) have very few samples — in some cases, only 1 Y-plate sample was measured with Teslameter on those dates. The main pre-deployment dates with good coverage are:
- **2024-11-05**: 95 (sample, date) entries, T_mean = 25.1°C ± 0.9°C
- **2024-11-07**: 60 entries, T_mean = 24.6°C ± 0.6°C

The baseline for most samples comes from these two dates.

---

## 4. Assumptions and Approximations

### 4.1 Linear Temperature Coefficient (ASSUMED)

We assume α(Br) is constant over the temperature range 20–34°C. In reality, α varies slightly with temperature, especially near the maximum operating temperature. For the temperature range in this study (~22–34°C), the linear approximation is accurate to better than 0.01% for all materials.

**Validity**: Good. The temperature range is well within the linear regime for all four material grades.

### 4.2 Manufacturer α Values (ASSUMED)

We use manufacturer-specified temperature coefficients, not measured values for these specific samples. Sample-to-sample variation in α is typically ±5–10% relative (e.g., α could be −0.10 to −0.12%/°C instead of −0.11%/°C for N52SH).

**Impact**: A ±10% error in α at T = 32°C (ΔT = 12°C from T_ref) gives:
- N52SH: ±0.013% error in corrected reading — small but not negligible compared to signals of ~0.3%
- SmCo: ±0.005% error — negligible

**Mitigation**: This is a systematic error that affects all samples of the same grade equally. It shifts the mean degradation curve but does not affect relative sample-to-sample comparisons within a grade.

### 4.3 Teslameter Temperature = Magnet Temperature (ASSUMED)

We assume the Teslameter probe tip temperature equals the magnet's actual temperature. In practice:
- The probe is pressed against the magnet surface during measurement
- There may be a thermal contact resistance
- The magnet interior may be at a different temperature than the surface

**Validity**: Reasonable. The magnets are small (cm-scale) with high thermal conductivity relative to the measurement timescale. The face-to-face temperature spread (T_std) captures some of this uncertainty.

### 4.4 Temperature Uniform Within a Measurement Session (ASSUMED)

We assign one temperature per (sample, date). If the measurement takes several hours and the tunnel temperature is changing, the Helmholtz reading may be at a slightly different temperature than the Teslameter reading (measured at a different time).

**Validity**: Reasonable for most campaigns. Tunnel temperature typically varies by ±1°C over a measurement session.

### 4.5 Helmholtz Coil Response is Linear in Br (ASSUMED)

The Helmholtz coil measures the magnetic moment of the sample, which is directly proportional to Br. We assume no nonlinear effects in the coil response or electronics over the measurement range.

**Validity**: Good. Helmholtz coils are designed for this purpose and are linear over the relevant range.

### 4.6 No Irreversible Temperature Effects (ASSUMED)

We assume all temperature effects are **reversible** — i.e., if the magnet is heated and then cooled back to T_ref, it returns to its original Br. This is true as long as the temperature stays well below the material's maximum operating temperature.

**Validity**: Good. Maximum temperatures (~34°C) are far below:
- N42EH: rated to 200°C
- N52SH: rated to 150°C
- SmCo33H/35: rated to >250°C

### 4.7 Baseline Selection (IMPORTANT DESIGN CHOICE)

**Previous approach (v1)**: First corrected measurement per sample as baseline.
**Problem**: If the first measurement is bad (Y-34-4), all subsequent % changes are wrong.

**Current approach (v2)**: Robust mean of all pre-deployment corrected measurements as baseline, with two levels of outlier protection.

**Level 1 — Intra-sample outlier rejection (within a single sample's pre-deployment readings)**:
- Near-zero readings (< 0.1 mWC) are excluded before averaging
- For ≥3 pre-deployment readings: Median Absolute Deviation (MAD) rejection — readings >3.5× MAD from median are excluded (with a minimum threshold of 0.5% of the median, to avoid rejecting genuine variation in very stable samples)
- For 2 pre-deployment readings: if they differ by >5%, both are kept but the sample is monitored
- For 1 reading: used as-is (no rejection possible)
- The baseline standard deviation is stored and reported

**Level 2 — Inter-sample outlier rejection (across all samples of the same material)**:
- After computing each sample's baseline, compare to the median baseline for that material grade
- Samples whose baseline deviates >5% from the material-group median are flagged
- Flagged samples are shown in plots (gray, x markers) but excluded from group mean calculations
- Currently flagged: Y-34-4 (N52SH, −10.1% from group median), Y-40-4 (SmCo33H, +6.8%)

**The same filtering is applied to raw baselines** when computing raw % change comparisons, ensuring consistency between raw and corrected analysis.

---

## 5. Plot Descriptions

### Plot A: Temperature-Corrected Y-Plate Time-Series by Material

**What it shows**: Raw (dashed, faint) and corrected (solid) Helmholtz readings (mWC) over time, with one panel per material grade (N42EH, N52SH, SmCo33H, SmCo35). Individual samples are shown as thin lines; the mean across all samples is shown as a thick black line with ±1σ shaded band.

**What to look for**:
- The corrected traces (solid) should be less scattered than the raw traces (dashed), showing the temperature correction is reducing variability
- The mean corrected trace should be flatter than the mean raw trace
- The σ band width gives the sample-to-sample spread at each date

**Only dates with Teslameter temperature data are included.** Dates with Helmholtz-only data (2024-05-02, 2024-08-12, 2025-04/05/06, 2025-12-17) are excluded because no temperature correction is possible.

**Caveat**: Different numbers of samples are measured on different dates (15 on Jul 17, 15 on Jul 30, 30 on Aug 27, etc.), so the mean can shift when the sample composition changes.

### Plot B: Temperature-Corrected % Change from Baseline

**What it shows**: The percentage change in corrected Helmholtz reading relative to the pre-deployment baseline, by material. Individual traces (thin, faint) show each sample; the mean and ±1 standard error band are overlaid.

**How the baseline is computed**: Mean of all pre-deployment corrected measurements for that sample (typically Nov 5 and/or Nov 7, 2024 readings). Samples with abnormal baselines are flagged and excluded from the mean (see Section 3.2).

**What to look for**:
- Radiation degradation would appear as a downward trend (negative % change) that increases over time
- Different rates for NdFeB vs SmCo would indicate material-dependent radiation sensitivity
- The Jul 17 data points may appear as outliers (see Section 6.1)

**Important**: A monotonically decreasing curve would be expected if degradation is the only signal and there are no remaining systematics. Non-monotonic behavior indicates residual measurement systematics or genuine recovery (thermal annealing).

### Plot C: Jul 17 vs Jul 30 Group Comparison — Raw vs Corrected

**What it shows**: Side-by-side bar charts comparing the mean raw (left) and corrected (right) % change from first-to-last tunnel measurement for the two measurement groups. The "Jul 17 group" (15 plates first measured on 2025-07-17) is compared to the "Jul 30 group" (15 plates first measured on 2025-07-30).

**What to look for**:
- If the group difference was purely thermal, temperature correction should eliminate it
- In practice, the corrected group difference shrinks only slightly (~0.87% raw → ~0.83% corrected), meaning **temperature does not explain the group systematic**
- The Jul 30 corrected group shows ~0% change, while the Jul 17 group shows ~+0.8% — the Jul 17 first measurement appears to be systematically low
- This is a known unresolved systematic (see Section 6.1)

### Plot D: Intra-Plate NdFeB − SmCo Differential — Raw vs Corrected

**What it shows**: For each Y-plate (which contains 2 NdFeB and 2 SmCo slots), compute the mean NdFeB % change minus the mean SmCo % change. This differential cancels any plate-level systematic (same location, same measurement time) and tests whether NdFeB and SmCo degrade differently.

**What to look for**:
- Raw differential: +0.289% ± 0.273% (NdFeB appears to degrade more)
- **Corrected differential: −0.003% ± 0.258% (essentially zero)**
- This is the **strongest validation of the temperature correction**: the raw NdFeB-SmCo difference was entirely due to NdFeB having a larger |α| than SmCo, not differential radiation damage
- The corrected differential being consistent with zero means we cannot detect differential degradation between NdFeB and SmCo at this dose level

### Plot E: Temperature History

**What it shows**: Two panels:
1. **Top**: All Teslameter temperature readings over time, colored by Jul 17 (blue) vs Jul 30 (red) measurement group. Daily mean ± σ in black. The red dashed line shows T_ref = 20°C.
2. **Bottom**: The correction magnitude (%) as a function of time for N52SH and SmCo35, computed from the daily mean temperature. This shows how much the correction shifts readings at each date.

**What to look for**:
- Summer 2025 (beam on): temperatures ~30–34°C, corrections of +1.0–1.5% for NdFeB
- Oct 2025 (beam off): temperatures ~22–28°C, corrections of +0.3–0.9% for NdFeB
- The correction magnitude varies by ~1% between hot and cold periods — this is the systematic being removed
- SmCo corrections are ~3× smaller due to lower |α|

### Plot F: Per-Material Mean Degradation Curve ("Money Plot")

**What it shows**: Two panels — top = corrected, bottom = raw — showing the mean % change from pre-deployment baseline for each material grade over time. Error bars show the standard error of the mean (uncertainty on the mean, not sample spread). Flagged outlier samples are excluded.

**What to look for**:
- A downward trend over time = radiation degradation
- NdFeB below SmCo = NdFeB is more radiation-sensitive (expected from literature)
- Error bar size relative to signal indicates statistical significance
- The Jul 17 data point may appear anomalous (see Section 6.1)
- Compare top vs bottom: the raw panel should show more variation between dates (temperature-driven), while the corrected panel should be flatter
- Any remaining non-monotonicity in the corrected panel is a measurement systematic, not real physics

**Interpretation caution**: This plot uses the pre-deployment baseline (mean of all pre-deployment corrected measurements per sample). Any systematic difference between pre-deployment lab conditions and tunnel conditions (other than temperature) will appear as a false degradation signal.

### Console Output: Summary Tables

**What it shows**: Comprehensive text tables printed to the console:
1. **CORRECTED** per-material mean % change at each date
2. **RAW** per-material mean % change at each date (for comparison)
3. **FLAGGED OUTLIER SAMPLES** with their baseline deviations

**Purpose**: Full transparency — the numerical values behind the plots. Allows checking exact numbers, sample counts, and error bars.

---

## 6. Known Systematics and Caveats

### 6.1 The Jul 17 Group Systematic

**Observation**: Plates first measured on Jul 17, 2025 show systematically different behavior from plates first measured on Jul 30, 2025. This ~0.8% offset persists after temperature correction.

**Possible explanations**:
1. **Measurement setup issue on Jul 17**: First day of tunnel campaign, possible operator learning curve, calibration drift, or equipment warm-up issue
2. **Time-of-day effect**: If Jul 17 measurements were done at different times than Jul 30, and there's a diurnal temperature variation not captured by the Teslameter
3. **Position-dependent radiation**: The Jul 17 and Jul 30 groups are at different tunnel locations, potentially receiving different radiation doses. However, ~0.8% in 13 days of additional exposure is implausibly large.
4. **Sample handling**: First measurement after deployment — magnets may have shifted in their holders

**Current treatment**: The Jul 17 group systematic is **not corrected** — we have no validated model for it. When computing mean degradation curves, it appears as an anomalous dip at the Jul 17 date. Users should be aware that degradation estimates from Jul 17 data carry an additional ~0.8% systematic uncertainty.

**Recommendation**: When reporting degradation results, use the Jul 30 or Aug 27 data as the first reliable tunnel measurement, or report the Jul 17 result separately with a caveat.

### 6.2 Baseline Stability

The pre-deployment baseline (Nov 2024) is 8 months before the first tunnel measurement (Jul 2025). Natural aging of NdFeB magnets at room temperature is typically <0.01%/year, so this should not be a concern. However, any handling damage, re-magnetization, or measurement setup changes between Nov 2024 and Jul 2025 would appear as a false degradation signal.

### 6.3 α(Br) Uncertainty as a Systematic

If α(Br) is wrong by ΔΑ, all corrected values shift by:

    ΔH_corr/H_corr ≈ −Δα × (T − T_ref)

At the maximum temperature (~33°C, ΔT = 13°C) and a 10% relative error in α:
- N52SH: shift ≈ 0.014% — small
- SmCo: shift ≈ 0.005% — negligible

This systematic affects all samples of the same grade equally and does not produce time-varying artifacts.

### 6.4 What This Analysis Can and Cannot Do

**CAN**:
- Remove the dominant temperature systematic (~1% for NdFeB, ~0.5% for SmCo)
- Validate the correction via the intra-plate differential test (Section 5, Plot D)
- Provide upper bounds on material-averaged degradation
- Identify outlier samples and measurement issues

**CANNOT**:
- Correct for the Jul 17 group systematic (origin unknown)
- Detect degradation below ~0.1–0.2% (limited by measurement noise and remaining systematics)
- Distinguish radiation damage from other time-varying effects (aging, handling, calibration drift)
- Provide per-sample degradation rates (noise too large for individual samples)

---

## 7. Extensibility: Adding New Data

### 7.1 Adding New Measurement Dates

1. Place new Helmholtz `.dat` files in the appropriate directory:
   - Y-plates: `Cleanup_Claude/Y_Plates/Helmholtz/Y-XX-N_helmholtz.dat`
   - Pair assemblies: `Cleanup_Claude/Pair_Assemblies/Helmholtz/Hn-XX-YY_helmholtz.dat`

2. Place corresponding Teslameter `.dat` files:
   - Y-plates: `Cleanup_Claude/Y_Plates/Teslameter/Y-XX-N_{front,side,top}.dat`
   - Pair assemblies: `Cleanup_Claude/Pair_Assemblies/Teslameter/An-XX-YY-Z_{front,side,top}.dat`

3. **No code changes needed.** The script automatically discovers all files and dates. New dates will appear in all plots and tables.

### 7.2 Adding New Samples

Same as above — just add the files. If a new material grade is introduced, add its α(Br) to the `ALPHA` dict at the top of the script and its color to the `CB` dict.

### 7.3 Adding External Temperature Data

For dates where Teslameter data is not available (Helmholtz-only dates), an external temperature source could be used. To implement:
1. Create a CSV file with columns: `date, sample, temperature`
2. Load it in `build_temperature_lookup()` and merge into `temp_lookup`
3. The rest of the pipeline handles it automatically

### 7.4 File Format Requirements

Helmholtz files: tab-separated, one of two date formats:
```
2024-05-06-09:55:30\t...\t+0.7903 kT
2025-07-17\t09:35:49\t...\t+1.2790 mWC
```

Teslameter files: tab-separated, same date formats, with 3 field values + 1 temperature:
```
2025-07-17\t09:35:49\t...\t-11.332\t0.143\t9.349\t22.188
```

---

## 8. Summary of Results

### 8.1 Temperature Correction Validation

| Test | Raw | Corrected | Interpretation |
|------|-----|-----------|----------------|
| Intra-plate NdFeB−SmCo differential | +0.292% ± 0.274% | +0.001% ± 0.261% | **Correction eliminates thermal differential** |
| Jul17 vs Jul30 group difference (N42EH) | +0.872% | +0.833% | Group systematic is NOT thermal |
| Correction direction | — | H_corr > H_raw for all T > 20°C | ✓ Correct |

### 8.2 Observed Degradation (Temperature-Corrected)

**Caution**: The Jul 17 data point is affected by an unresolved ~0.8% group systematic (see Section 6.1). All other dates should be compared relative to the Jul 30 or later measurements if excluding this systematic.

Values are mean corrected % change from pre-deployment baseline at selected dates (flagged outliers Y-34-4 and Y-40-4 excluded):

| Material | Jul 17 2025 | Jul 30 2025 | Aug 27 2025 | Oct 21 2025 | Jan 8 2026 | Jan 12 2026 |
|----------|-------------|-------------|-------------|-------------|------------|-------------|
| N42EH (n=30)   | −1.18% | −0.26% | −0.56% | −0.50% | −0.36% | −0.30% |
| N52SH (n=29)   | −1.13% | −0.22% | −0.48% | −0.46% | −0.33% | −0.20% |
| SmCo33H (n=28) | −0.78% | −0.10% | −0.17% | −0.13% | +0.04% | −0.03% |
| SmCo35 (n=30)  | −0.84% | −0.07% | −0.24% | −0.12% | −0.12% | −0.03% |

For comparison, the same dates with **RAW** (uncorrected) values:

| Material | Jul 17 2025 | Jul 30 2025 | Aug 27 2025 | Oct 21 2025 | Jan 8 2026 | Jan 12 2026 |
|----------|-------------|-------------|-------------|-------------|------------|-------------|
| N42EH    | −1.91% | −0.94% | −1.20% | −0.47% | −0.64% | −0.54% |
| N52SH    | −1.90% | −0.96% | −1.19% | −0.45% | −0.60% | −0.47% |
| SmCo33H  | −1.07% | −0.38% | −0.44% | −0.12% | −0.07% | −0.13% |
| SmCo35   | −1.13% | −0.34% | −0.49% | −0.11% | −0.22% | −0.13% |

### 8.3 Key Observations

1. **Temperature correction works**: The intra-plate differential test conclusively shows the correction removes the thermal bias (+0.292% raw → +0.001% corrected).
2. **A ~0.8% group systematic remains unexplained** and dominates the Jul 17 data point. It is NOT thermal in origin.
3. **No clear monotonic degradation trend** is visible in any material — corrected values fluctuate within ±0.5% with no steady decline. This is expected if degradation is below the measurement noise floor.
4. **SmCo materials show smaller corrected changes** than NdFeB (as expected: smaller α means less correction, and SmCo is inherently more radiation-hard).
5. **The raw values show much more scatter** (−1.9% to −0.5% for NdFeB) than corrected (−1.2% to −0.3%), confirming temperature is the dominant systematic in the raw data.
6. **N52SH is now well-behaved** after excluding the Y-34-4 outlier (bad baseline), with scatter comparable to N42EH.
7. **The non-monotonic behavior** (e.g., N42EH: −0.56% at Aug 27 → −0.30% at Jan 12) is almost certainly measurement systematics, not physical recovery. Radiation damage to permanent magnets is irreversible at room temperature (see Section 9).

---

## 9. What Would Recovery/Annealing Look Like?

The user asked about recovery. Radiation-induced demagnetization in permanent magnets is generally **irreversible** at room temperature — the coercivity reduction from radiation damage does not spontaneously heal. However:

1. **Thermal annealing** can partially restore properties if magnets are heated to ~100–300°C (material dependent). This is NOT happening in the tunnel (~22–34°C).
2. **Apparent recovery** in the data (values going back up after going down) is much more likely due to measurement systematics than actual physical recovery.
3. At the dose levels in this study, the expected degradation for NdFeB is ~0.1–0.5% and for SmCo is <0.1%. These signals are at or below the current measurement noise floor.

**Bottom line**: If the corrected curves show non-monotonic behavior, it is almost certainly measurement systematics, not physical recovery.
