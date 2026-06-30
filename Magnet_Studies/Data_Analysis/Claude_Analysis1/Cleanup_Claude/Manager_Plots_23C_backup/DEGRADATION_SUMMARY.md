# LDRD FFA@CEBAF Magnet Radiation Study
## Preliminary Degradation Summary

**Date:** March 16, 2026 (updated from March 11)
**Status:** Preliminary — data collection ongoing
**Exposure Period:** July 2025 – January 2026 (~6 months in CEBAF tunnel)
**Measurement Method:** Helmholtz coil (integrated dipole moment), temperature-corrected to 20°C

---

## Executive Summary

After ~6 months in the CEBAF tunnel, **NdFeB permanent magnets show statistically significant degradation of 0.26–0.33% (Y-plate Helmholtz)**, while **SmCo magnets show no significant degradation** (<0.08%). The degradation is material-dependent and dose-correlated: arc regions (higher radiation dose) show ~2× more NdFeB degradation than linac regions.

**However:** The absolute degradation values are subject to a ±0.25% Helmholtz coil gain systematic that is comparable to the signal. The most robust result is the **intra-plate NdFeB−SmCo differential** (−0.27% ± 0.03%, 9.7σ), which cancels this systematic because both materials are measured on the same plate in the same session. **Lab control Y-plates** (no radiation) show a differential of −0.006% ± 0.019% (0.3σ) — essentially zero — confirming the tunnel signal is radiation-induced (tunnel−lab = 7.7σ). H-plate and Teslameter results carry larger systematics than the signal and are uninformative (neither confirming nor contradicting). **A-sample** (individual magnet) Helmholtz shows +0.085% (NdFeB) and +0.067% (SmCo), both positive — consistent with the H-plate gain-dominated results and carrying the same ±0.25% systematic. Both instruments (fluxmeter at 0.05% accuracy, Teslameter at 100 ppm) are far more precise than our measurement variability — the noise comes from session-to-session coil variability and probe positioning, not instrument limitations.

---

## Key Results

### Y-Plate Helmholtz Results (temperature-corrected)

| Material | Mean Change (%) | Stat. Unc. (%) | Significance | N samples | Positive/Negative |
|----------|:--------------:|:--------------:|:------------:|:---------:|:-----------------:|
| **NdFeB N42EH** | **−0.333** | ±0.034 | **10σ** | 30 | 0 pos / 30 neg |
| **NdFeB N52SH** | **−0.260** | ±0.037 | **7σ** | 29 | 1 pos / 28 neg |
| SmCo 33H | +0.012 | ±0.030 | n.s. | 29 | 13 pos / 16 neg |
| SmCo 35 | −0.077 | ±0.031 | 2σ | 30 | 9 pos / 21 neg |

**Combined:**
- **All NdFeB: −0.297 ± 0.025%(stat) ± ~0.25%(syst, gain) (12σ stat)**
- **All SmCo: −0.033 ± 0.022%(stat) ± ~0.25%(syst, gain) (n.s.)**

**About the positive SmCo changes:** 23 of 118 Y-plate samples show a net positive change (apparent field *increase*). All 23 are SmCo (13 SmCo33H, 9 SmCo35, 1 N52SH at +0.001%). **22 of 23 positive samples have exactly 1 pre-deployment baseline reading** (vs a median of 3 for all samples). Single-baseline samples have no internal consistency check — a single measurement on a day when the Helmholtz coil happened to read low would produce a spurious positive change. The absolute magnitudes are small (+0.001 to +0.004 mWC on ~1.0 mWC). Multi-baseline samples (≥2 pre-deployment readings) show zero positive SmCo changes. This correlation with baseline count is suggestive but not proof — it could also be statistical fluctuation on genuinely near-zero changes.

### Gain-Immune Differential (Most Robust Result)

| Metric | Value | Significance | Notes |
|--------|:-----:|:------------:|-------|
| **NdFeB − SmCo (baseline → latest, all 30 plates)** | **−0.266% ± 0.027%** | **9.7σ** | Intra-plate, cancels Helmholtz gain |
| **NdFeB − SmCo (Aug 27 → Jan 12, 15 plates)** | **−0.265% ± 0.037%** | **7.2σ** | Date-to-date, same Helmholtz session |
| NdFeB − SmCo (Aug 27 → Oct 21) | −0.50% ± 0.02% | 25σ | Likely inflated by thermal lag |

### H-Plate (Pair Assembly) Helmholtz Results

Analysis from `degradation_summary_v2.py`. Not in v3 plots (Y-plate only). **Note:** H-plates are single-material (all NdFeB or all SmCo), so no intra-plate gain-immune differential is possible. The absolute values below carry the full ±0.25% gain systematic.

| Material | N | Mean Change (%) | Stat. Unc. (%) | Notes |
|----------|:-:|:--------------:|:--------------:|-------|
| NdFeB (Hn) | 37 | **+0.026** | ±0.050 | Essentially zero — no degradation detected |
| SmCo (Hs) | 48 | **+0.148** | ±0.061 | Slightly positive (unexpected) |

**By H-plate configuration:**

| Config | Material | N | Mean Change (%) | Unc. (%) |
|--------|----------|:-:|:--------------:|:--------:|
| Alpha (parallel) | NdFeB | 12 | +0.079 | ±0.049 |
| Alpha (parallel) | SmCo | 16 | +0.056 | ±0.045 |
| Gamma (90°) | NdFeB | 12 | −0.113 | ±0.130 |
| Gamma (90°) | SmCo | 16 | +0.268 | ±0.160 |
| Delta (single+slug) | NdFeB | 13 | +0.105 | ±0.057 |
| Delta (single+slug) | SmCo | 16 | +0.119 | ±0.077 |

**Note:** Beta (antiparallel) excluded from Helmholtz due to multipole character.

**H-plate results are consistent with Y-plates once the gain systematic is included.** H-plate NdFeB: +0.03% ± 0.05%(stat) ± 0.25%(syst) → range [−0.22%, +0.28%]. Y-plate NdFeB: −0.33% ± 0.03%(stat) ± 0.25%(syst) → range [−0.58%, −0.08%]. These overlap. H-plates cannot see the signal through the gain noise because they lack the intra-plate differential technique. Additional factors that increase H-plate uncertainty:
- Fewer temperature-matched pre-deployment readings (only 87 of 91 retained)
- Anomalous baselines: several pairs (e.g., Hn-9-3, Hn-9-4) have Nov 2024 readings >50% different from all subsequent
- Smaller sample sizes per material-configuration cell (12-16 per group vs 29-30 for Y-plates)

### By Dose Region (Y-plates only)

| Region | NdFeB Change (%) | SmCo Change (%) | Notes |
|--------|:----------------:|:---------------:|-------|
| Arcs (NE, NW, SE, SW) | −0.35 to −0.40 | −0.01 to −0.14 | Highest dose |
| Linacs (North, South) | −0.08 to −0.21 | +0.01 to +0.07 | Lower dose |
| Labyrinth | −0.24 to −0.28 | −0.06 to −0.13 | Not a control — radiation detected |

NdFeB degradation scales with expected radiation dose:
- **Arcs (higher dose):** −0.38% ± 0.04% (NdFeB average)
- **Linacs (lower dose):** −0.21% ± 0.04% (NdFeB average)
- Arc-to-linac ratio: **~1.8×**, consistent with dose scaling

SmCo shows no dose-dependent signal within measurement precision. Some linac-region SmCo bars are net positive (up to +0.07%), but these are small and within statistical uncertainty.

---

## Methodology

### Temperature Correction (Critical)
- Raw Helmholtz readings vary ~1% for NdFeB and ~0.5% for SmCo due to tunnel temperature swings (21–34°C)
- Temperature measured by co-located Teslameter Hall probe (3 faces averaged: front, side, top)
- Correction: H_corr = H_raw / (1 + α(T − 20°C)), where α = −0.10%/°C (N42EH), −0.11%/°C (N52SH), −0.04%/°C (SmCo)
- **Without temperature correction, the degradation signal is undetectable**

### Baseline
- **Helmholtz pre-deployment baselines**: Reliable. Mean of all available pre-deployment temperature-corrected readings.
- **Single-baseline vulnerability**: 33 of 120 Y-plate samples have only 1 pre-deployment reading. These samples cannot be checked for internal baseline consistency. All 23 positive-change samples come from this group.
- **Teslameter pre-deployment field readings**: NOT used for field baselines — Hall probe was changed before tunnel deployment.
- **Teslameter pre-deployment temperature readings**: Still accurate, used for temperature correction.
- Only dates with co-located temperature data used (no mixing of corrected/uncorrected)

### Error Bars
- Per-sample: baseline SEM (std/√N of pre-deployment readings). For single-baseline samples, defaults to 1% of the baseline value.
- Group averages: SEM across samples within the group
- **The ±0.25% Helmholtz gain systematic is an additional systematic uncertainty not included in the error bars on individual plots (except where explicitly shown as gray bands in v3 plots).**

### Outlier Treatment
- 2 Y-plate samples excluded (Y-34-4, Y-40-4): pre-deployment baselines deviate >5% from material group — possible labeling or measurement error
- H-plate pair assemblies with |change| > 5% flagged as anomalous baselines
- Beta (antiparallel) pair assemblies excluded from Helmholtz analysis (multipole field character)

---

## Instrument Specifications (from manuals)

### Fluxmeter Model 2130 (Magnetic Instrumentation Inc.)
- **DC accuracy: 0.050% typical, 0.100% max** (of full-scale range)
- Integrator-based: measures total flux change (∫e·dt), proportional to dipole moment
- Automatic drift compensation within ±1% of range window
- **Key property for this study:** Helmholtz coil geometry makes measurement "fairly independent of the position of the sample within the coils" (manual §4.7). This is an integral measurement — the total dipole moment — not a point measurement. Repositioning the sample within the coil has minimal effect.
- **Sources of error (manual §4.13):** coil orientation alignment, coil parameter accuracy (resistance, area, turns, Helmholtz constant), sample volume, coil resistance temperature coefficient, interference during zero/self-test
- **Implication:** The 0.05% instrument accuracy is much better than our 0.3% NdFeB signal. The measurement noise we see (~0.25% session-to-session) is NOT an instrument precision limit — it is likely coil/cable/connection variability between sessions.

### Teslameter 3MH6-E (SENIS)
- **DC accuracy: 0.01% (100 ppm) of full scale** at ±0.1T, ±0.5T, ±2T ranges
- **Temperature stability: < 20 ppm/°C** (negligible for our temperature range)
- **Resolution: ~1 µT RMS** at 10 SPS on ±2T range (i.e., 0.5 ppm)
- Probe interchangeability maintains 100 ppm accuracy
- 24-bit A/D converter
- **Key property:** This is a POINT measurement (sensing volume 100 × 10 × 100 µm³). Field varies steeply near the magnet surface (dipole/multipole gradients).
- **Measurement setup:** Teslameter probe is placed in **3D-printed measuring rigs** (NOT hand-held). This provides repeatable positioning for each sample/face. However, different slots and prints have different mechanical tolerances:
  - **Top face:** Best/most reliable — tightest rig fit, least slop
  - **Side face:** More slop in the rig → more positioning scatter
  - **Front face:** More slop in the rig → more positioning scatter
  - Rig-to-rig and slot-to-slot tolerance variation contributes to inter-sample scatter
- **Possible probe movement:** Under the new cap system installed before tunnel deployment, there is concern the Hall probe *may* shift slightly within the rig. This is likely very minimal if it occurs at all, but could contribute to a small systematic offset between pre-deployment and tunnel measurements.
- **Implication:** The Teslameter measurement is MORE controlled than free-hand, but the ~0.5-2% per-sample scatter likely reflects rig tolerance differences between faces/slots, not random positioning error. Top-face data should be the most precise and may provide useful cross-validation if analyzed separately.

### Hall Probe Type C
- 3-axis CMOS Hall elements, 100 × 100 µm² per element
- Angular accuracy: < ±1-2° with respect to reference surface
- **Fragile** — ceramic construction, easily damaged by mechanical contact
- Operating temperature: +5 to +45°C
- Probe-to-probe interchangeability: calibration data stored in EEPROM

### Helmholtz Measurement Procedure Notes
- **Drift is the primary concern.** The integrator-based fluxmeter drifts due to offset voltages/currents varying with time and temperature (manual §4.9). The team **actively re-zeros** the instrument frequently during tunnel campaigns to mitigate this, but drift between zero operations still occurs.
- Helmholtz coil geometry makes the measurement insensitive to sample positioning within the coil, but coil connection and cable routing may vary session-to-session.

### Key Takeaway from Instrument Manuals
**Both instruments are far more precise than our measurement variability suggests.** The Helmholtz coil at 0.05% accuracy should easily resolve a 0.3% signal. The Teslameter at 100 ppm should resolve even smaller signals in a well-constrained rig. Our measurement uncertainties (~0.25% Helmholtz session-to-session, ~0.5-2% Teslameter face-dependent) come from practical factors: Helmholtz drift between re-zeros and session-to-session coil variability; Teslameter rig tolerances varying by face and slot.

### Combined Helmholtz + Teslameter Measurements
Helmholtz and Teslameter measurements on the same samples are taken at approximately the same time during each tunnel campaign. This means:
- Temperature conditions are matched — the Teslameter temperature reading is directly applicable to the Helmholtz measurement
- Both instruments see the same magnet at the same thermal state
- Combining the two provides complementary information: Helmholtz gives the precise integral (dipole moment), Teslameter gives point-field and temperature
- The combination could be exploited more carefully — e.g., using top-face-only Teslameter data as an independent cross-check with lower noise than the 3-face average

### Per-Face Teslameter Analysis (Y-plates, first-tunnel → latest, temp-corrected)

| Face | Sample std | NdFeB mean | SmCo mean | NdFeB−SmCo | Notes |
|------|:----------:|:----------:|:---------:|:----------:|-------|
| **Top** | **0.21%** | −0.024% ± 0.029% | −0.042% ± 0.024% | **+0.018% ± 0.038%** | Tightest rig fit |
| Front | 0.72% | +0.19% ± 0.11% | +0.20% ± 0.10% | −0.01% ± 0.15% | Positive bias (rig slop) |
| Side | 1.46% | −0.27% ± 0.26% | −0.40% ± 0.27% | +0.13% ± 0.37% | Most scatter |
| **3-face avg** | **0.54%** | +0.07% ± 0.07% | −0.08% ± 0.07% | +0.15% ± 0.10% | Diluted by noisy faces |

**Key findings:**
1. **Top face confirms the rig tolerance story:** std = 0.21% (top) vs 0.72% (front) vs 1.46% (side). Top is 3-7× tighter.
2. **Top face shows both materials near zero** (NdFeB: −0.024%, SmCo: −0.042%). NdFeB−SmCo differential = +0.018% ± 0.038% (0.5σ). This does NOT show the −0.27% NdFeB excess seen in Helmholtz.
3. **Front face has a systematic positive bias** (~+0.2-0.3% for all materials), possibly from probe seating deeper in the rig over time.
4. **Side face is too noisy** (std ~1.5%) to be useful for this analysis.
5. **The 3-face average is dominated by the noisy front/side data**, washing out the cleaner top-face information.

**Interpretation of top-face Teslameter vs Helmholtz:**
The top-face Teslameter, our best face, shows no NdFeB−SmCo differential (0.5σ), while the Helmholtz gain-immune differential is 9.7σ. Possible explanations:
- The Teslameter is a **point measurement** at a specific location on the magnet surface, while the Helmholtz integrates the **total dipole moment**. Radiation damage might affect the bulk moment differently than the surface field at one point.
- Even the top face has 0.21% per-sample scatter (comparable to the expected ~0.13% signal per material), so the Teslameter lacks statistical power for this comparison.
- The Teslameter baseline is first-tunnel (not pre-deployment), so it captures less of the total exposure period.
- Different temperature correction quality (Teslameter self-reports temperature vs. Helmholtz uses Teslameter temperature from a co-located measurement).

---

## Re-Assessment of H-Plate "Discrepancy" (Step-Back Analysis)

**Previous concern:** Y-plates show clear NdFeB degradation (−0.3%), but H-plates show no signal (+0.03%). This was flagged as a major unresolved discrepancy.

**Revised understanding after considering the gain systematic:**

The Y-plate gain-immune result works because NdFeB and SmCo are on the **same plate**, measured in the **same session** with the **same coil gain**. H-plates are all-NdFeB (Hn) or all-SmCo (Hs) — no intra-plate differential is possible.

When we include the ±0.25% gain systematic on the absolute values:
- **Y-plate NdFeB:** −0.33% ± 0.03%(stat) ± 0.25%(syst) → true value in [−0.58%, −0.08%]
- **H-plate NdFeB:** +0.03% ± 0.05%(stat) ± 0.25%(syst) → true value in [−0.22%, +0.28%]

**These ranges overlap.** The H-plate result is NOT inconsistent with the Y-plate result — it is simply too imprecise (because it carries the full gain systematic) to see the signal. The H-plate data neither confirms nor contradicts a −0.3% real degradation.

Similarly, the Teslameter results carry even larger systematics (positioning noise ~0.5-2%). They too are consistent with the Y-plate signal — just unable to resolve it.

**The "discrepancy" was the wrong framing.** The correct framing is:
1. **One measurement technique (Y-plate gain-immune differential) has sufficient precision** to detect a 0.3% signal at 9.7σ
2. **All other measurements (Y-plate absolute, H-plate absolute, Teslameter)** carry systematic uncertainties ≥ the signal size and are therefore uninformative — they neither confirm nor contradict
3. **No measurement contradicts** the gain-immune result

---

## Known Systematics

### 1. Helmholtz Coil Session-to-Session Gain Variability

**Observation:** Pre-deployment lab measurements (constant ~21°C, no radiation) show the session-mean Helmholtz reading drifting by up to 0.5% between measurement sessions. Five lab sessions (Apr–Jun 2025) all read 0.27–0.77% lower than the Nov 5, 2024 session. This drift is material-independent (all 4 grades shift equally), confirming it is a coil/instrument effect, not a magnet effect.

**Estimated systematic:** ±0.25% (half the range of session-mean offsets).

**Physical cause:** The Model 2130 fluxmeter uses a Miller integrator whose offset voltages drift with time and temperature (manual §4.9). The team re-zeros frequently during campaigns, but residual drift between re-zeros accumulates. Additionally, coil cable routing and connector seating may vary slightly between sessions, affecting the effective coil parameters.

**What this means for the results:**
- The absolute per-material degradation numbers (e.g., N42EH = −0.33%) compare a pre-deployment baseline to a Jan 2026 tunnel reading. If the coil gain was different on those two days, the result is biased.
- The NdFeB−SmCo differential cancels this because both materials are measured in the same session on the same plate.
- **Caveat:** The claim that the gain shift is material-independent rests on 5 lab sessions. A larger dataset would strengthen this. The C03 repeatability plot shows the raw data — the session means cluster near −0.6%, but individual samples scatter widely (IQR ~1.5%), and there are outliers at ±10-20% (these are samples with very small absolute moments, ~1 mWC, where digitization matters).

### 2. Single-Baseline Vulnerability

33 Y-plate samples have only 1 pre-deployment Helmholtz reading with co-located temperature data. These baselines cannot be checked for gain-session bias. The correlation between single-baseline status and positive changes (22 of 23 positive samples have N_pre=1) may indicate that gain variability is creating spurious scatter in the SmCo data — but it could also simply reflect that near-zero true changes (SmCo) are more likely to scatter positive than large negative true changes (NdFeB).

### 3. Oct 21 Thermal Lag

Oct 21 data shows an anomalously large NdFeB–SmCo differential (−0.50% vs −0.27% at equilibrium). The tunnel cooled from ~31°C to ~24.7°C after beam shutdown; magnets likely lagged behind the air temperature measured by the Teslameter.

### 4. Labyrinth Radiation

Labyrinth samples show NdFeB degradation comparable to linac regions. These are **not** control sites. True controls are the "upstairs" lab samples (not yet fully analyzed).

### 5. Teslameter Probe Positioning (3D-Printed Rigs)

Teslameter probe is placed in 3D-printed measuring rigs, NOT hand-held. However, rig tolerances vary:
- **Top face:** Tightest fit, most reliable, least scatter
- **Side/front faces:** More slop in the rig design → more positioning variability → more scatter
- H-plate first-tunnel measurements show ~2-3% low bias on front/side faces vs subsequent readings. Top face unaffected. This is consistent with the rig tolerance explanation.
- Possible minor probe shift under new cap system (pre-deployment → tunnel) — likely very small but not quantified.
- Does not impact Helmholtz results (independent instrument).

### 6. SmCo35 Marginal Signal

SmCo35 shows −0.08% ± 0.03% (2σ). Could be real small degradation, residual systematic, or fluctuation.

---

## Conclusions

1. **NdFeB degrades significantly more than SmCo** — the Y-plate intra-plate differential is −0.27% ± 0.03% (9.7σ), immune to Helmholtz gain shifts. This is the single robust result.
2. **Absolute NdFeB degradation is ~0.26–0.33%** with an additional ±0.25% systematic uncertainty from Helmholtz gain variability. Including the systematic, significance drops to ~1σ.
3. **SmCo shows no significant degradation** (−0.03% ± 0.02%), though ~40% of SmCo samples show small positive changes correlated with single-baseline status.
4. **Degradation is dose-dependent** — arc regions (higher dose) show ~2× more NdFeB degradation than linac regions, preserved even in the gain-immune differential.
5. **H-plate results are uninformative** — they carry the full ±0.25% gain systematic (no intra-plate differential possible), so the H-plate NdFeB range [−0.22%, +0.28%] overlaps with the Y-plate range [−0.58%, −0.08%].
6. **Top-face Teslameter is the best independent check but shows no NdFeB−SmCo differential** (+0.018% ± 0.038%, 0.5σ). With 0.21% per-sample scatter and a shorter baseline (first-tunnel, not pre-deployment), it lacks the precision to confirm or rule out the 0.27% Helmholtz signal — but the null result deserves attention. See "Per-Face Teslameter Analysis" section for details.
7. **Instrument precision is not the limiting factor.** The fluxmeter (0.05% accuracy) and Teslameter (100 ppm accuracy) are both far more precise than our measurement-to-measurement variability. The noise comes from Helmholtz drift between re-zeros and session-to-session coil variability, and from Teslameter rig tolerance differences by face.
8. **The gain-immune differential is the most robust result from this dataset**, but the top-face Teslameter null result means we should be cautious about over-interpreting it. Future work should focus on: (a) reducing the Helmholtz gain systematic with same-day reference standards, (b) tightening Teslameter rig tolerances or using only top-face data, (c) analyzing lab control samples for an independent baseline.

---

## Plot Descriptions (v3)

All v3 plots are in `Manager_Plots/v3_*.png`. Generated by `manager_summary_v3.py`. **All v3 plots use Y-plate data only.** H-plate analysis exists in `degradation_summary_v2.py` and `MD_Files/degradation_summary_v2.md` but is not yet in presentation-ready form.

### Category A: Remade Plots 1–7 with Gain Systematic Bands

These are updated versions of the original v1 plots (which are still in `1_*.png` through `7_*.png`). Each v3 A-plot shows the same data as the corresponding v1 plot, with a **gray shaded band at ±0.25%** representing the Helmholtz coil gain systematic estimated from pre-deployment lab data.

---

**`v3_A01_material_comparison.png` — Degradation by Material Grade**

*What it shows:* Four bars, one per material grade (N42EH, N52SH, SmCo33H, SmCo35). Bar height = mean % change from pre-deployment baseline to latest tunnel reading (Jan 2026), after temperature correction to 20°C. Black error bars = statistical uncertainty (SEM of the ~30 samples per grade). Gray band = ±0.25% Helmholtz gain systematic. Inset (upper-left): a single dark red bar showing the gain-immune NdFeB−SmCo intra-plate differential.

*How to read it:* N42EH and N52SH bars extend below the gray band, meaning the degradation exceeds the estimated gain systematic. SmCo33H and SmCo35 bars are within or near the gray band, meaning their changes are comparable to the instrument uncertainty. The inset shows that when you cancel the gain systematic by comparing NdFeB and SmCo on the same plate, the differential is −0.27% at 9.7σ.

*What to watch for:* SmCo33H is slightly positive (+0.01%). This is the mean of 29 samples, 13 of which are individually positive — see "About the positive SmCo changes" above.

---

**`v3_A02_ndfeb_vs_smco.png` — NdFeB vs SmCo + Gain-Immune Bar**

*What it shows:* Three bars. Left (red): all NdFeB combined (N42EH + N52SH, 59 samples). Middle (green): all SmCo combined (SmCo33H + SmCo35, 59 samples). Right (dark red, gold border): the intra-plate NdFeB−SmCo differential (30 plates). Gray bands sit behind the left and middle bars showing ±0.25% gain systematic. The right bar has NO gray band because the gain systematic cancels.

*How to read it:* The left two bars show absolute changes subject to the gain systematic. The right bar is the key result: −0.266% ± 0.027% (9.7σ) with purely statistical uncertainty. If the gain systematic were the sole cause of the NdFeB bar, the differential would be zero — instead it is nearly 10σ from zero.

---

**`v3_A03_regional_comparison.png` — Degradation by Region and Material**

*What it shows:* Grouped bars for 7 tunnel regions (NE Arc, SW Arc, NW Arc, SE Arc, North Linac, South Linac, Low Dose). Within each region, 4 bars (one per material grade). Gray band at ±0.25%. Colored backgrounds: red tint = arcs, blue tint = linacs, green tint = labyrinth ("Low Dose").

*How to read it:* Arc regions (left four groups) show NdFeB bars extending well below zero (−0.3 to −0.5%), while SmCo bars are near zero. Linac regions show smaller NdFeB degradation (−0.1 to −0.2%). The NdFeB bars in NE Arc are the most negative (−0.5%), suggesting higher dose there.

*What to watch for:* Some SmCo bars are **above zero** — particularly SmCo35 in North Linac (~+0.07%) and SmCo33H in NW Arc (~+0.10%) and South Linac (~+0.09%). These are small, within error bars, and within the gain systematic band. They may be real fluctuation around zero or baseline artifacts (see single-baseline discussion). NE Arc SmCo33H also shows a small positive bar.

---

**`v3_A04_arc_vs_linac.png` — Arcs vs Linacs vs Low Dose**

*What it shows:* Same data as A03 but grouped into three dose regions: Arcs (all 4 arc regions combined), Linacs (both linac regions), Low Dose (labyrinth). Gray gain band shown. Inset (bottom-right): gain-immune NdFeB−SmCo differential by dose region (red = arcs, blue = linacs, gray = labyrinth).

*How to read it:* The main plot shows absolute values; the inset removes the gain systematic. In the inset, arcs show a more negative differential (−0.29%) than linacs (−0.20%), consistent with dose scaling. The labyrinth (N=2 plates) has large error bars.

---

**`v3_A05_timeseries.png` — Degradation Over Time**

*What it shows:* Four colored lines (one per material) showing mean % change at each measurement date. Error bars = SEM. Gray band = gain systematic. Orange shading around Oct 21 = thermal lag suspect region. Gray dashed vertical line = beam OFF.

*How to read it:* All four materials dip sharply negative at Jul 17 and Jul 30, then partially recover by Aug 27. This **is not** real degradation and recovery — it reflects the Helmholtz gain being different in Jul vs Aug sessions (the dip is material-independent). From Aug 27 through Jan 2026, NdFeB gradually becomes more negative while SmCo stays near zero. The Oct 21 point (flagged orange) shows exaggerated divergence between NdFeB and SmCo, likely from thermal lag.

*What to watch for:* The Jan 2026 SmCo points are slightly positive relative to Aug 27 — the lines drift up, not down. This could mean: (a) the Jan 2026 Helmholtz gain is slightly higher than the pre-deployment gain used for baseline, or (b) there's a real small positive drift in SmCo measurements over time (unlikely physically). The note in the lower-left corner flags that positive shifts within the gray band are consistent with gain variability.

---

**`v3_A06_waterfall.png` — All Individual Samples Sorted**

*What it shows:* Horizontal bars for all 118 samples, sorted from most negative (top) to most positive (bottom). Color = material grade. Gray vertical band = ±0.25% gain systematic. Small colored squares on the left edge = region (red shades = arc, blue = linac, gray = labyrinth).

*How to read it:* Red/blue bars (NdFeB) dominate the top (most degraded). Green/orange bars (SmCo) are clustered near zero. Some green/orange bars extend into positive territory (right of zero). The gray band shows that most SmCo changes are within the estimated instrument noise.

*What to watch for:* The positive-extending SmCo bars (bottom of the plot). These are the 22 SmCo + 1 N52SH samples discussed above. The most positive is ~+0.4% (Y-4-2, SmCo35, single baseline).

---

**`v3_A07_dashboard.png` — 2×3 Dashboard Summary**

*What it shows:* Six panels summarizing the Y-plate Helmholtz analysis: (a) material degradation with gain systematic bands, (b) gain-immune NdFeB−SmCo differential, (c) time series, (d) gain-immune differential by region, (e) Helmholtz gain variability from lab data, (f) key results table showing stat and syst uncertainties.

*How to read it:* This is the "one-page summary" for presentations. Start with panel (b) — the single most robust number. Then panel (a) for context on absolute values. Panel (d) shows dose dependence is preserved even in the gain-immune metric. Panel (e) shows the evidence for the gain systematic.

---

### Category B: Teslameter Plots (Cross-Validation Attempt)

These plots use the Teslameter (hand-held Hall probe, 3 face measurements per sample) as an independent check on the Helmholtz results. **Baseline = first tunnel measurement (Jul 2025)**, not pre-deployment, because the Hall probe was changed before deployment.

---

**`v3_B01_teslameter_by_material.png` — Teslameter by Material**

*What it shows:* Four bars, same layout as A01, but using Teslameter field magnitude instead of Helmholtz. Baseline = first tunnel measurement (not pre-deployment). Error bars are much larger than Helmholtz (~±0.1% vs ±0.03%).

*How to read it:* N42EH shows a negative trend (−0.08%), consistent with Helmholtz direction. **But N52SH shows +0.21%** (positive, opposite to Helmholtz), and SmCo35 shows −0.17% (more negative than its Helmholtz value). These inconsistencies reflect the Teslameter's poor precision (~0.5% per-sample from hand-held probe placement variability) and the different baseline (first tunnel reading vs pre-deployment).

*Caveat:* The Teslameter does **not** independently confirm the Helmholtz degradation signal at the precision needed. The N52SH positive result is particularly problematic for any "confirmation" narrative. The Teslameter is useful for temperature monitoring but its field measurements are too noisy for this purpose.

---

**`v3_B02_temperature_history.png` — Tunnel Temperature Over Time**

*What it shows:* Mean tunnel temperature at each measurement date, with ±1σ range (darker blue band) and min-max range (lighter band). Orange square marks Oct 21 (beam OFF cooling event). Red dashed line = T_ref = 20°C.

*How to read it:* Temperature ranges from ~32°C in Jul 2025 to ~25°C in Oct/Jan. The large temperature swings (>10°C) are why temperature correction is critical — NdFeB's −0.10%/°C coefficient means a 10°C swing produces a 1% raw reading change, much larger than the 0.3% degradation signal. The Oct 21 point sits at ~24.7°C after rapid cooling from ~31°C — magnets may have been warmer than the air sensor.

---

**`v3_B03_teslameter_vs_helmholtz.png` — Scatter Plot Comparison**

*What it shows:* Each point is one sample. X-axis = Helmholtz % change (pre-deployment baseline). Y-axis = Teslameter % change (first tunnel baseline). Color = material. Dashed line = 1:1 correspondence.

*How to read it:* If both instruments measured the same thing with the same baseline, points would cluster along the 1:1 line. Instead, the scatter is large (Teslameter varies from −1% to +1% for samples that Helmholtz says are −0.3%). This confirms the Teslameter lacks the precision for this measurement. The different baselines (pre-deployment vs first-tunnel) also shift points away from the 1:1 line.

*What to watch for:* There is essentially no correlation visible. This doesn't mean the Helmholtz is wrong — it means the Teslameter is too noisy to test it.

---

**`v3_B04_teslameter_per_face.png` — Per-Face Box Plots**

*What it shows:* Four panels (one per material). Within each panel, three box-and-whisker plots for front, side, and top Teslameter faces. Diamond markers = means.

*How to read it:* The boxes show the interquartile range of per-face % changes. The spread is enormous (IQR ~1-2%, outliers at ±6%). Side faces show the most scatter (consistent with the known probe positioning systematic). Top faces are tighter. The means (diamonds) vary erratically between faces and materials, reflecting noise rather than physics.

*What to watch for:* The outliers at −6% (N42EH side) and +10% (SmCo35 top, just off-screen). These are individual samples with probe placement issues. The per-face spread (~1-2%) explains why the Teslameter per-sample averages have ~0.5% uncertainty.

---

### Category C: Technical Detail Plots

---

**`v3_C01_waterfall_by_region.png` — Samples Grouped by Region**

*What it shows:* Same data as A06 (all 118 samples, horizontal bars) but grouped by tunnel region (labeled in bold text on the left), with samples sorted by magnitude within each region. Color = material.

*How to read it:* Within each region, the pattern is consistent: NdFeB bars (red/blue) extend left (negative), SmCo bars (green/orange) cluster near zero. The arc regions (top groups) show more NdFeB degradation than linac or labyrinth regions (bottom groups).

*What to watch for:* A few SmCo bars extend right (positive). Some individual plates show unusual patterns (e.g., Y-38 in NW Arc has one SmCo bar extending notably positive).

---

**`v3_C02_per_plate_breakdown.png` — 30-Panel Plate Grid**

*What it shows:* One small subplot for each of the 30 Y-plates, arranged by region (red titles = arc, blue = linac, gray = labyrinth). Each subplot has 4 bars: N42 (slot 1), N52 (slot 2), S33 (slot 3), S35 (slot 4).

*How to read it:* The prototypical plate shows N42 and N52 bars extending negative, S33 and S35 bars near zero. Most plates follow this pattern. Some plates deviate — look for plates where SmCo bars are as negative as NdFeB, or where NdFeB bars are near zero.

*What to watch for:* Y-39 (NE Arc) has an unusually large N52 bar. Y-21 (NE Arc) has an unusually large N42 bar. Y-09 (NE Arc) has very large values across all slots. The NE Arc plates generally show the largest degradation across all panels.

---

**`v3_C03_helmholtz_repeatability.png` — Pre-Deployment Repeatability**

*What it shows:* Five box-and-whisker plots, one per pre-deployment lab session (Apr 23 – Jun 17, 2025), showing the % change of each sample relative to its Nov 5, 2024 value. Red diamonds = session means. Pink shaded band = range of session means. Red label = session mean spread (0.497%).

*How to read it:* The session means (red diamonds) cluster in a narrow range (−0.77% to −0.27%), showing a systematic ~0.5% offset between Nov 2024 and the 2025 sessions. The box IQRs are tight (~1%), but there are extreme outliers at ±10-20%.

*What to watch for:* The extreme outliers are specific samples: Y-34-4 (+10%, already flagged as outlier), Y-21-2 (−20%), Y-39-3 (−17%). These are samples with very small absolute moments (~1.3 mWC) where small absolute changes produce large percentage swings. The important information is the **session means** (red diamonds), not the outliers — the session means show the 0.5% instrument gain drift that affects the degradation calculation.

*Limitation:* This plot is dominated by the outliers, making it hard to see the ~0.5% session mean spread. The y-axis extends to ±20% because of a few extreme points. A zoomed version focusing on ±3% would better show the gain drift.

---

**`v3_C04_gain_immune_detail.png` — The Punchline Plot**

*What it shows:* Two panels side-by-side. Left: four material bars with two sets of error bars each — black (statistical) and gray (stat ⊕ syst combined in quadrature). Gray shaded background = ±0.25% gain systematic. Right: single bar showing the gain-immune NdFeB−SmCo differential with statistical error only and a green "CANCELS here" label.

*How to read it:* Left panel: when you include the systematic uncertainty, N42EH drops from 10σ → 1.3σ and N52SH drops from 7σ → 1.0σ — the absolute values are barely significant against the gain systematic. SmCo values are completely insignificant. Right panel: the gain-immune differential remains 9.7σ because the systematic cancels. This is the argument for why the differential, not the absolute values, is the most meaningful number.

*What this does NOT prove:* This assumes the gain shift is perfectly material-independent. If the gain shift has a material-dependent component (e.g., different coil sensitivity to NdFeB vs SmCo geometries), the differential would not fully cancel. The lab data suggests material-independence (all 4 grades shift by ~0.65% together), but this is based on 5 sessions.

---

### Category D: Comprehensive Dashboard

**`v3_D01_comprehensive_dashboard.png` — 3×3 Dashboard**

*What it shows:* Nine panels combining the key results: (a) material degradation + gain bands, (b) gain-immune differential bar, (c) time series, (d) Teslameter confirmation attempt, (e) regional gain-immune differential, (f) gain variability, (g) Helmholtz vs Teslameter scatter, (h) double ratio timeline, (i) summary table.

*How to read it:* This is meant as a single-image summary. Panel (b) is the headline result. Panel (d) shows the Teslameter does NOT cleanly confirm the Helmholtz (note the positive N52SH bar). Panel (f) shows evidence for the gain systematic. Panel (i) gives the numbers.

---

## What is NOT in These Plots (v3/v4)

1. ~~**H-plate (pair assembly) data**~~ — **NOW IN v5.** H-plate Helmholtz results, assembly config breakdown, and combined Y+H comparisons are in `Manager_Plots_v5/`.
2. ~~**A-sample (individual magnet) data**~~ — **NOW IN v5 polish.** A-sample Helmholtz and Teslameter analysis in G01-G04 plots.
3. ~~**Co-located Y+H comparisons**~~ — **NOW IN v5** (waterfalls at same scale, overlay time series, heatmap, arc panels with co-located markers).
4. ~~**Lab control samples**~~ — **NOW IN v5 polish.** Lab Y-plate analysis in F01 plot. Lab differential = −0.006% ± 0.019% (0.3σ).
5. **Radiation dose correlation** — dosimetry data exists but dose-response analysis deferred until dosimetry is complete. Pass-number analysis in v5 provides a proxy for dose ordering (to be validated with actual dosimetry).

---

## Cross-Validation Summary

| Metric | Y-plate Helmholtz | Y-plate Teslameter | H-plate Helmholtz | A-sample Helmholtz | A-sample Teslameter (top) | Lab Y-plate | Consistent? |
|--------|:-----------------:|:------------------:|:-----------------:|:------------------:|:------------------------:|:-----------:|:-----------:|
| NdFeB degradation | **−0.30%** (10σ) | −0.08% (n.s.) | +0.03% (n.s.) | +0.09% (4.0σ pos!) | −0.53% (std=0.33%) | −0.06% (n.s.) | See below |
| SmCo stable | −0.03% (n.s.) | −0.09% (n.s.) | +0.15% (2.4σ pos) | +0.07% (4.1σ pos!) | −0.24% (std=16.5%!) | +0.02% (n.s.) | See below |
| NdFeB − SmCo differential | **−0.27% (9.7σ)** | +0.02% (0.5σ) | N/A | +0.02% (n.s.) | −0.29% (noisy) | **−0.006% (0.3σ)** | **Key result** |
| Arcs > Linacs | ~2× ratio | N/A | N/A | Trend visible | N/A | N/A | Y+A consistent |

**Interpretation of the cross-validation table:**

1. **The Y-plate gain-immune differential remains the single robust result** (9.7σ, immune to gain systematics).
2. **Lab controls confirm it**: Lab differential is 0.3σ from zero — the tunnel excess over lab is 7.7σ.
3. **All absolute measurements** (Y-plate, H-plate, A-sample Helmholtz) carry the ±0.25% gain systematic. H-plate and A-sample results are both slightly positive (~+0.05-0.15%), which is **consistent** with the Y-plate values when the gain systematic is included (Y-plate [−0.58%, −0.08%] overlaps with A-sample [−0.17%, +0.34%]).
4. **A-sample Helmholtz** is a new data point: 202 individual magnets from the same pair assemblies. The A-sample NdFeB mean (+0.085%) and SmCo mean (+0.067%) are nearly identical, showing **no NdFeB-SmCo separation** — same pattern as H-plates. The gain systematic dominates.
5. **A-sample Teslameter** confirms the SmCo Teslameter data has extreme outliers (std=16.5%). NdFeB top-face is tighter (std=0.33%) but shows −0.53% — more negative than Y-plate Helmholtz. The positioning noise in the A-sample Teslameter rigs is comparable to the Y-plate rigs for NdFeB but dramatically worse for SmCo (possibly different rig geometry for SmCo pair assemblies).
6. **A-sample vs H-plate correlation (G03)**: r = 0.24, moderate. The individual magnet and pair-level Helmholtz measurements track each other, with a mean residual of −0.017% and std of 0.39%. This confirms internal consistency between measurement levels.
7. **No measurement contradicts** the gain-immune result. All measurements are compatible when their respective systematics are accounted for.

**Priority for next phase:** Reduce the gain systematic (e.g., same-day reference standard, fixed coil setup) so absolute values become informative. Correlate with dosimetry data to validate the pass-number trend.

---

---

## v4: Per-Face Teslameter Re-Analysis (2026-03-11)

**Script:** `Cleanup_Claude/manager_summary_v4.py`
**Plots:** `Cleanup_Claude/Manager_Plots_v4/v4_*.png` (12 plots)
**Motivation:** v3 averaged all 3 Teslameter faces together, diluting top-face (best rig fit) with noisy side/front. v4 keeps faces separate and applies the gain-immune intra-plate technique to each Teslameter face independently.

### Per-Face Material Means (Teslameter, temp-corrected)

| Face | N42EH | N52SH | SmCo33H | SmCo35 | Std (N42EH) |
|------|:-----:|:-----:|:-------:|:------:|:-----------:|
| Top | −0.027% ± 0.025% | −0.035% ± 0.053% | −0.039% ± 0.037% | −0.046% ± 0.033% | 0.137% |
| Front | +0.188% ± 0.107% | +0.765% ± 0.169% | +0.307% ± 0.105% | +0.106% ± 0.105% | 0.589% |
| Side | −0.416% ± 0.294% | −0.116% ± 0.220% | −0.304% ± 0.167% | −0.581% ± 0.346% | 1.609% |
| 3-Face | −0.085% ± 0.103% | +0.205% ± 0.091% | −0.012% ± 0.070% | −0.174% ± 0.116% | 0.562% |

### Per-Face Intra-Plate NdFeB−SmCo Differentials

| Instrument/Face | Differential | Significance | N plates |
|----------------|:----------:|:------------:|:--------:|
| **Helmholtz** | **−0.266% ± 0.027%** | **9.7σ** | 30 |
| Tesla Top | +0.017% ± 0.032% | 0.5σ | 30 |
| Tesla Front | +0.285% ± 0.114% | 2.5σ | 30 |
| Tesla Side | +0.164% ± 0.236% | 0.7σ | 30 |
| Tesla 3-Face | +0.155% ± 0.090% | 1.7σ | 30 |

**Key finding:** The Helmholtz 9.7σ NdFeB−SmCo differential does NOT appear in any Teslameter face. The top face (best rig tolerance, σ=0.21%) shows +0.017% ± 0.032% — essentially zero. The front face shows a spurious 2.5σ *positive* signal (NdFeB > SmCo), consistent with its known systematic positive bias.

### Cross-Instrument Correlations

| Comparison | Pearson r | N |
|-----------|:---------:|:--:|
| Helmholtz vs Tesla top (per-sample) | 0.009 | 118 |
| Helmholtz vs Tesla front | −0.173 | 118 |
| Helmholtz vs Tesla side | −0.211 | 118 |
| Session-Δ Helmholtz vs Tesla top | 0.059 | 117 |
| Session-Δ Helmholtz vs Tesla front | −0.019 | 117 |
| Session-Δ Helmholtz vs Tesla side | 0.005 | 117 |
| Top vs Front (face-to-face) | 0.124 | 118 |
| Top vs Side | 0.058 | 118 |
| Front vs Side | −0.053 | 118 |

**All correlations are essentially zero.** Neither endpoint comparisons nor session-to-session deltas show any correlation between instruments. Face-to-face correlations are also negligible, indicating that Teslameter noise is dominated by rig positioning rather than actual physics.

### Interpretation

1. **Teslameter is uninformative at this signal level.** Top-face scatter (0.21%) is comparable to the expected per-material signal (~0.13%), giving insufficient statistical power. Side (1.6%) and front (0.7%) are far too noisy.
2. **No evidence against the Helmholtz result.** The Teslameter can neither confirm nor refute a 0.27% differential — it simply lacks the precision.
3. **Front-face positive bias confirmed.** All 4 materials show positive front-face changes (+0.1 to +0.8%), consistent with a systematic rig positioning shift rather than physics.
4. **Session-delta approach failed** — zero correlation suggests that measurement-to-measurement noise is purely repositioning noise, not tracking any real temporal signal.
5. **Face-to-face non-correlation** confirms that each face's noise is independent (different rig contact points), not a common-mode effect.

### v4 Plot Index

| Plot | Description |
|------|-------------|
| v4_A01 | Per-face material bars (4 panels: top, front, side, 3-face) |
| v4_A02 | Per-face time series (4 panels) |
| v4_A03 | **KEY PLOT:** Intra-plate NdFeB−SmCo differential — Helmholtz vs each face |
| v4_A04 | Per-sample scatter: Helmholtz vs each Teslameter face |
| v4_B01 | Comprehensive statistics table |
| v4_B02 | Face-to-face correlation (top vs front, top vs side, front vs side) |
| v4_B03 | Rig tolerance by slot (box plots per slot × face) |
| v4_C01 | Side-by-side instrument comparison (5 panels) |
| v4_C02 | Session-to-session delta correlation (3 panels) |
| v4_C03 | Intra-plate differential time evolution (Helmholtz + per-face) |
| v4_D01 | 3×2 summary dashboard |
| v4_D02 | Clean face comparison table |

---

## v5: Comprehensive Combined Y+H Analysis (2026-03-11)

**Script:** `Cleanup_Claude/manager_summary_v5.py`
**Plots:** `Cleanup_Claude/Manager_Plots_v5/v5_*.png` (16 plots)
**Motivation:** First combined Y-plate + H-plate presentation. Adds waterfall plots by region, pass-number (arc line position) analysis, assembly configuration breakdown, and clean summary/publication figures.

### New Analysis: Pass-Number (Arc Line Position) Trend

Each arc has 5 line positions (1=top/lowest beam energy through 5=bottom/highest beam energy). Y-plate NdFeB degradation by line:

| Line | Position | NdFeB Change (%) | SEM (%) | N |
|:----:|----------|:----------------:|:-------:|:-:|
| 1 | Top (lowest E) | **−0.554** | ±0.083 | 8 |
| 2 | | −0.390 | ±0.052 | 8 |
| 3 | | −0.298 | ±0.050 | 8 |
| 4 | | −0.261 | ±0.050 | 8 |
| 5 | Bottom (highest E) | −0.308 | ±0.063 | 7 |

**Line 5 − Line 1 differential: +0.246%** (Line 1 shows ~2× more degradation than Lines 3–5)

**This is unexpected.** If degradation scaled simply with beam energy, Line 5 (highest energy pass) should show the most degradation. Instead, Line 1 (lowest energy) shows the most. Possible explanations to investigate:
- Radiation dose may not scale monotonically with beam energy at these positions
- Line 1 (top of arc stack) may receive more scattered radiation from the beamline above
- Shielding geometry may differ by position
- Need to correlate with actual dosimetry data (NDX detectors, area dosimeters) to resolve

### New Analysis: H-Plate Assembly Configuration

All configs exclude Beta (unreliable Helmholtz due to multipole character). No Beta pairs survive the temperature-corrected baseline filter.

| Config | Material | N | Mean Change (%) | SEM (%) |
|--------|----------|:-:|:--------------:|:-------:|
| Alpha (parallel) | NdFeB | 12 | +0.079 | ±0.049 |
| Alpha (parallel) | SmCo | 16 | +0.056 | ±0.045 |
| Gamma (90°) | NdFeB | 12 | −0.113 | ±0.130 |
| Gamma (90°) | SmCo | 16 | +0.268 | ±0.160 |
| Delta (single+slug) | NdFeB | 13 | +0.105 | ±0.057 |
| Delta (single+slug) | SmCo | 16 | +0.119 | ±0.077 |

**Observations:**
- All config/material combinations are within the ±0.25% gain systematic — no config stands out
- Gamma shows the most scatter (large SEM), particularly SmCo/Gamma at +0.268% ± 0.160%
- No evidence that assembly configuration affects radiation sensitivity at this precision level
- Arc vs Linac breakdown (C02 plot) shows no clear config × location interaction

### v5 Plot Index

| Plot | Description |
|------|-------------|
| **Cat. A: Waterfalls** | |
| v5_A01 | Y-plate waterfall by region, color by material grade |
| v5_A02 | H-plate waterfall by region, config annotated, Beta hatched |
| v5_A03 | Side-by-side Y + H waterfall (same x-axis scale) |
| **Cat. B: Regional & Pass** | |
| v5_B01 | Y-plate grouped bars by region × material |
| v5_B02 | **KEY:** Degradation vs arc line position (pass number), Y+H |
| v5_B03 | 4-panel arc breakdown (SE, NE, NW, SW × 5 lines) |
| v5_B04 | Region × material heatmap (Y + H combined grid) |
| **Cat. C: Assembly Config** | |
| v5_C01 | H-plate by config (with and without Beta), 2-panel |
| v5_C02 | Config × region-type (Arc vs Linac) |
| **Cat. D: Summary** | |
| v5_D01 | Executive summary infographic (3 key-number boxes + bar chart) |
| v5_D02 | Publication-quality 2×2 multi-panel (all 6 materials, differential, regional, table) |
| v5_D03 | Comprehensive results table rendered as figure |
| v5_D04 | 3×2 dashboard (Y bars, H config, differential, pass trend, time series, table) |
| **Cat. E: Time Series** | |
| v5_E01 | Y-plate Helmholtz time series with SEM bands |
| v5_E02 | Combined Y + H overlay time series (solid=Y, dashed=H) |

### Oddities/Open Questions from v5 Plots (to investigate later)

1. **Pass-number trend is inverted** — Line 1 (lowest E) has most degradation, not Line 5 (highest E). Need dose data to understand.
2. **H-plate SmCo shows +0.148% ± 0.061% (2.4σ positive)** — unexpected. Could be gain shift, baseline artifact, or real. Y-plate SmCo is near zero. Investigate whether this is driven by specific plates.
3. **Gamma config has large scatter** — SmCo/Gamma at +0.268% ± 0.160%. Small N and possibly noisy baselines.
4. **Some v5 plots may need annotation improvements** — executive summary (D01), heatmap (B04), and dashboard (D04) could benefit from cleaner labeling and axis ranges once the user reviews them.
5. **H-plate time series (E02)** — dashed lines may be hard to see if few date points survive the N≥3 filter. Need to check visual quality.

---

## Review & Roadmap (2026-03-11 evening)

### Plot Directory Status
| Directory | Version | Plots | Status | Notes |
|-----------|---------|:-----:|--------|-------|
| `Manager_Plots/1-7` | v1 | 7 | **SUPERSEDED** | Original absolute-value plots. No gain syst bands. |
| `Manager_Plots/8-14` | v2 | 7 | **SUPERSEDED** | Gain systematic + double ratio. Partially covered by v3/v5. |
| `Manager_Plots/v3_*` | v3 | 16 | **CURRENT** | Y-plate Helmholtz comprehensive. Best-documented set. |
| `Manager_Plots_v4/v4_*` | v4 | 12 | **CURRENT** | Per-face Teslameter deep-dive. Specialized audience. |
| `Manager_Plots_v5/v5_*` | v5 | 16 | **CURRENT** | Combined Y+H. Needs polish. |
| `TempCorrected_Plots/A-I` | early | 9 | **SUPERSEDED** | Early exploratory. |
| `TempCorrected_Plots/degradation_v2_*` | v2 | 3 | **CURRENT** | v2 degradation summary. |

### What Should Be Re-Done
1. **A "best-of" presentation set** — pick the ~8-10 strongest plots from v3+v5, polish them with consistent styling, fonts, annotations. Target: manager presentation + expert review.
2. **v5 D01 (executive summary)** — fonts and layout could be cleaner. The infographic approach is right but needs refinement.
3. **v5 B02 (pass number)** — the key new physics plot. Worth polishing with better labels and possibly adding dose data overlay when available.
4. **v5 D04 (dashboard)** — should be the "one figure" for conferences. Needs careful axis scaling and annotation.
5. **Early plots (v1 1-7)** — some of these have useful structural ideas (e.g., the original waterfall, per-plate breakdown) that should be reimagined with current understanding (gain bands, outlier flagging, H-plate data).

### What's Missing (Data-Side)
1. **Lab control plate material assignments** — user says they updated the Materials_Arrangements.xlsx lab tabs, but file on disk (mod date Feb 26, 2026) shows them empty. Need to resolve — may be a different file or unsaved changes.
2. **Lab control plate temperature data** — no Teslameter temperature for upstairs samples. Would need to assume T_lab ≈ 21–24°C with larger uncertainty. This limits precision of control comparisons.
3. **Radiation dose data** — NDX dosimetry exists in `Radiation Info/Integrated_Dose_Data/` but not yet correlated with magnet degradation. This is the major pending analysis.
4. **Optichromic rod data after Nov 10, 2025** — still missing.

### Lab Control (Upstairs) Data Inventory (2026-03-11)

**Spreadsheet**: `Materials_Arrangements_Spreadsheet.xlsx` (root dir, NOT Cleanup_Claude copy)
- **9 Lab Y-plates**: y-8, y-14, y-27, y-28, y-29, y-31, y-33, y-35, y-37
  - Note: y-29, y-33, y-37 list "SmCo33" (not "SmCo33H") in slot 1 — verify if typo
- **48 Lab H-plates**: 24 NdFeB (n-1,2,3,5,7,13,14,21-23,25-36,38,40) + 24 SmCo (s-8,9,11,19,21-40)

**Data files available**:
| Source | Location | Samples | Type |
|--------|----------|---------|------|
| Compare_Lab_Tunnel | `Compare_Lab_Tunnel/Lab/` | Y-8, Hs-29, As-29 | Helmholtz + Teslameter |
| Adam R. Dec 2025 | `Lab_Measurements/2025-12-17_AdamR/` | 8 Y-plates (y-14,27,28,29,31,33,35,37), Hs-23, As-23 | Helmholtz only |
| Upstairs 2026 | `Lab_Measurements/Upstairs_2026/` | 24 NdFeB + 20 SmCo H-plates (An/As/Hn/Hs) | Helmholtz only, 436 files |

**Key limitation**: No Teslameter temperature data for lab samples. Must assume T_lab ≈ 21-24°C. This introduces ~0.1-0.3% additional uncertainty for NdFeB (α = −0.10%/°C × ΔT_uncertainty ≈ ±3°C).

**Analysis value**: Even with wider temperature uncertainty, lab controls can:
1. Confirm Helmholtz gain stability over time (same plates measured repeatedly, no radiation)
2. Provide a baseline for "natural" measurement variability without radiation
3. Check if the ±0.25% gain systematic estimate is consistent with lab-only data
4. If any lab NdFeB shows −0.3% "degradation", that would undermine the radiation hypothesis

---

## Lab Control (Upstairs) Y-Plate Analysis (2026-03-11)

**9 lab Y-plates** kept upstairs with no radiation exposure. These are the true controls.

### Data Coverage
- 8 plates (Y-14,27,28,29,31,33,35,37): baseline Nov 2024 (`April0825/`), latest Dec 17, 2025 (Adam R.), span ~13 months
- 1 plate (Y-8): baseline Aug 26, 2025 (`Compare_Lab_Tunnel/Lab/`), latest Mar 9, 2026, span ~6 months
- **No temperature correction** — no Teslameter data for lab plates. Assumes lab temp ~21-24°C.

### Per-Material Mean % Change (8 plates, Nov 2024 → Dec 2025, NOT temp-corrected)

| Material | Mean Change | SEM | N |
|----------|:-----------:|:---:|:-:|
| N42EH | −0.064% | ±0.026% | 8 |
| N52SH | −0.042% | ±0.025% | 8 |
| SmCo33H | +0.018% | ±0.012% | 8 |
| SmCo35 | +0.019% | ±0.029% | 8 |

Overall mean: −0.017% (essentially zero). **No gain drift** between Nov 2024 and Dec 2025 sessions for Y-plates.

### Intra-Plate NdFeB−SmCo Differential (THE KEY CONTROL CHECK)

**Updated 2026-03-16** — re-computed using all available data in `Y_Plates/Helmholtz/` (earliest date = baseline, latest = final). Previous session used a different baseline selection; current values use consistent methodology.

| Plate | NdFeB Change | SmCo Change | Differential |
|-------|:-----------:|:-----------:|:-----------:|
| Y-8 | −0.557% | −0.641% | +0.084% |
| Y-14 | −0.025% | −0.009% | −0.016% |
| Y-27 | −0.000% | +0.022% | −0.022% |
| Y-28 | +0.008% | +0.016% | −0.008% |
| Y-29 | −0.035% | +0.063% | −0.097% |
| Y-31 | −0.129% | −0.137% | +0.007% |
| Y-33 | +0.011% | −0.054% | +0.065% |
| Y-35 | −0.039% | +0.035% | −0.075% |
| Y-37 | +0.001% | −0.005% | +0.006% |

**Lab control differential: −0.006% ± 0.019% (0.3σ) — essentially zero**

**Note on Y-8:** Y-8's baseline is Apr 2025 (not Nov 2024 like the others), and its NdFeB and SmCo both show −0.6% changes. This is likely a Helmholtz gain shift between the Apr 2025 baseline and the Aug 2025 "latest" reading — consistent with the known 0.5-0.7% session-to-session gain variability. The differential (+0.084%) is small, confirming gain shifts are material-independent.

### Interpretation

The lab control differential of −0.006% is consistent with zero — **no NdFeB-SmCo separation at the 0.02% level in unirradiated samples.**

Previous analysis (using a different baseline selection) yielded −0.065% ± 0.021% (3.0σ), which was attributable to ~1°C uncorrected temperature. The current analysis yields an even smaller value, reinforcing the conclusion.

**Comparison to tunnel result:**

| Metric | Value | Significance |
|--------|:-----:|:-----------:|
| **Tunnel differential (temp-corrected)** | **−0.266% ± 0.027%** | **9.7σ** |
| Lab control differential (NOT temp-corrected) | −0.006% ± 0.019% | 0.3σ |
| Tunnel minus lab (worst case) | −0.260% ± 0.034% | **7.7σ** |

The tunnel excess over lab is **7.7σ** — even more significant than the previous estimate of 5.5σ. **The lab controls strongly confirm the radiation-induced signal.**

### Anomalies
- **Y-31**: Mild outlier (all 4 slots ~0.13% more negative than other plates). Plate-level effect, possibly positioning or local temperature.
- **Y-29 repeatability**: 5 repeat readings on Apr 30, 2025 show 0.17-0.32% per-slot spread — consistent with known Helmholtz variability.

---

### Recommended Priority for Next Session
1. ~~**Polish key plots**~~ — **DONE** (v5 polish, 2026-03-16). D01, B02, D04 polished; F01 (lab) and G01-G04 (A-sample) added.
2. **Dose data correlation** — bring in NDX data, overlay on degradation by position
3. **Investigate pass-number inversion** with dose data
4. **Lab H-plate analysis** — 48 H-plates measured in Upstairs_2026, but no cross-session repeats found. Limited value for gain-stability check.

---

## v5 Polish + A-Sample Analysis (2026-03-16)

**Script:** `Cleanup_Claude/manager_summary_v5_polish.py`
**Plots:** `Cleanup_Claude/Manager_Plots_v5/v5_{D01,B02,D04,F01,G01-G04}.png` (8 plots)
**Motivation:** Polish 3 key v5 plots for presentation quality, add lab control comparison plot, and add first comprehensive A-sample (individual magnet) analysis.

### Polished Plots (D01, B02, D04)

---

**`v5_D01_executive_summary.png` — Polished Executive Summary**

*What changed from original:* Sans-serif fonts throughout (no monospace in findings text). Added 4th info box for "Lab Controls" showing −0.006% differential in blue — visually confirms radiation signal is real. Findings text uses proper bullet alignment instead of monospace block. "PRELIMINARY" watermark more prominent (60pt rotated). 200 dpi output.

*What it shows:* Four colored info boxes across the top: (1) NdFeB degradation (red, −0.30%), (2) SmCo stable (green, −0.03%), (3) NdFeB−SmCo gain-immune differential (gold, −0.266% at 9.7σ), (4) Lab controls (blue, −0.006% — essentially zero). Below: a simple 2-bar chart (NdFeB vs SmCo with gain systematic band) and 5 key findings in sans-serif text.

*How to read it:* Start with the 4 boxes — they tell the complete story in one glance. Box 3 (gold) is the most robust result. Box 4 (blue) is the independent confirmation that the tunnel signal isn't an artifact. The bar chart provides visual context; the findings text expands on each point.

*Key numbers:* NdFeB: −0.30% ± 0.03%(stat) ± 0.25%(syst). SmCo: −0.03% ± 0.02%(stat) ± 0.25%(syst). Differential: −0.266% ± 0.027% (9.7σ). Lab: −0.006% ± 0.019% (0.3σ).

---

**`v5_B02_pass_number_trend.png` — Polished Pass-Number Trend**

*What changed from original:* Reproducible scatter jitter (`np.random.seed(42)`). Shorter x-labels: "1 (low E)" through "5 (high E)". N annotations at each mean data point showing sample count. Linear trend line for Y-plate NdFeB with annotated slope (+0.062%/line). Wider inset panel with cleaner labels. Annotation box noting the inverted trend is unexpected and requires dose data to resolve.

*What it shows:* Main panel: degradation vs arc line position (1=top/lowest beam energy through 5=bottom/highest beam energy) for Y-plate NdFeB (solid red circles), Y-plate SmCo (solid green circles), H-plate NdFeB (open red squares), and H-plate SmCo (open green squares). Error bars = SEM. Gray band = gain systematic. Individual Y-plate scatter shown as faint dots. A red dotted trend line shows the linear fit to Y-plate NdFeB means.

*How to read it:* Line 1 (lowest beam energy) shows the most NdFeB degradation (−0.55%), while Lines 3-5 cluster around −0.27 to −0.31%. The trend line slope is +0.062%/line, meaning each line step upward (higher energy) shows ~0.06% less degradation. This is unexpected — if degradation scaled with beam energy, Line 5 should be worst.

*Inset panel:* Groups data into "Top Lines (1-2)" vs "Bottom Lines (3-5)" for a cleaner comparison. Top NdFeB (−0.47%, N=16) vs Bottom NdFeB (−0.29%, N=23) — the difference is significant.

*Why this matters:* The pass-number trend is the key physics plot for understanding whether degradation scales with dose, beam energy, or geometric position. The inverted trend suggests that radiation dose at Line 1 may be higher than at Line 5 despite lower beam energy — possibly due to scattered radiation or shielding geometry. Actual dosimetry data is needed to resolve this.

---

**`v5_D04_dashboard.png` — Polished 3×2 Dashboard**

*What changed from original:* Figure enlarged to 20×20 (from 18×18). Panel (a): N labels on each bar showing sample count. Panel (c): ±1σ and ±2σ dashed reference lines for visual significance assessment. Panel (d): N annotations at each pass-number data point. Panel (e): "Beam OFF" label repositioned to avoid data overlap (placed at top of panel, right of the vertical line). Panel (f): table font increased to 11pt, differential row more strongly highlighted (gold background, bold text). Overall: consistent 11pt axis labels throughout.

*What it shows:* Six panels: (a) Y-plate by material grade with N labels, (b) H-plate by assembly configuration, (c) gain-immune NdFeB−SmCo differential with significance reference lines, (d) degradation vs arc line position (Y-plate only), (e) Y-plate Helmholtz time series with "Beam OFF" marker, (f) key numbers table with all Y, H, and differential values.

*How to read it:* This is the "one-figure summary" for conference presentations. Panel (c) is the punchline — the dark red bar extends far beyond the ±2σ lines, visually demonstrating the 9.7σ significance. Panel (f) provides the exact numbers for anyone who needs them.

---

### New Plot: F01 — Lab Control Comparison

**`v5_F01_lab_control_comparison.png` — Lab Controls Confirm Radiation Signal**

*What it shows:* Two panels side-by-side.

**Left panel:** Three bars comparing the gain-immune NdFeB−SmCo differential across contexts:
1. Tunnel (dark red, −0.266%, 9.7σ) — the main result
2. Lab control (blue, −0.006%, 0.3σ) — unirradiated plates showing essentially zero
3. Tunnel minus lab, worst case (gold, −0.260%, 7.7σ) — even conservatively subtracting lab "noise"

Significance annotations (σ values) appear below each bar. A note in the bottom-left corner flags that lab samples are NOT temperature-corrected (no Teslameter data available).

**Right panel:** Strip/dot plot showing all 30 individual tunnel plate differentials (dark red dots, clustered around −0.27%) and all 9 lab plate differentials (blue dots, clustered around 0%). Horizontal lines mark the means. This visual makes the separation between tunnel and lab immediately obvious — the two distributions barely overlap.

*How to read it:* The left panel gives the quantitative summary. The right panel provides the visual "gut check" — the tunnel plates are clearly shifted negative relative to lab, with minimal overlap. The 7.7σ worst-case significance means even if we assume the entire lab differential is a real systematic (rather than temperature), the tunnel signal survives at high significance.

*Key numbers:* Tunnel differential: −0.266% ± 0.027% (9.7σ). Lab differential: −0.006% ± 0.019% (0.3σ). Tunnel−Lab: −0.260% ± 0.034% (7.7σ).

*Caveats:* Lab samples are NOT temperature-corrected. The lab NdFeB−SmCo differential could be biased by ~0.07% per °C of temperature difference between baseline and final measurement sessions (NdFeB has larger α than SmCo). The fact that the lab differential is essentially zero (0.3σ) suggests either: (a) the lab temperature was well-matched between sessions, or (b) temperature effects are small at the 0.02% level. Y-8 is a mild outlier (differential = +0.084%) because its baseline (Apr 2025) and final (Aug 2025) span a different date range than the other plates.

---

### New Plots: G01-G04 — A-Sample (Individual Magnet) Analysis

**Background:** A-samples are individual magnets from within H-plate pair assemblies. Each H-plate has 4 pair slots, each containing 2 magnets. The H measurement is the pair assembly (both magnets together, measured in the Helmholtz coil while assembled). The A measurement is each magnet individually, measured **outside the assembly** — the pair is disassembled, and each magnet is measured separately by both Helmholtz and Teslameter.

This provides a THIRD measurement level: Y-plates (4 material grades per plate, integral dipole), H-plates (2-magnet pair assembly, integral dipole), and A-samples (single magnets, integral dipole + point field). The A-sample Helmholtz measures the same magnets as the H-plate Helmholtz, just one at a time instead of as a pair.

**Data summary:**
- 202 A-sample Helmholtz results (90 NdFeB from 20 plates, 112 SmCo from 23 plates), ALL temperature-corrected
- 210 A-sample Teslameter results (98 NdFeB, 112 SmCo), baseline = first tunnel measurement
- Tunnel plates: An from plates 6-12, 15-20, 26, 30, 35, 37-39; As from plates 1-7, 9-18, 20, 22-23, 29, 36, 40

**Teslameter baseline note:** A-sample Teslameter shows a dramatic field magnitude jump between pre-deployment (~20-30 mT on top face) and first tunnel measurement (~135-150 mT on top face). This is NOT because the magnet was in an assembly — A-samples are always measured outside the assembly. The jump is due to the **rig/cap change** before tunnel deployment (same issue as Y-plate and H-plate Teslameter baselines). Therefore, A-sample Teslameter baseline = first tunnel measurement, same as all other Teslameter baselines.

---

**`v5_G01_a_sample_helmholtz.png` — A-Sample Helmholtz Material Comparison**

*What it shows:* Two panels.

**Left:** Two bars — NdFeB (red, +0.085% ± 0.022%, 4.0σ, N=90) and SmCo (green, +0.067% ± 0.016%, 4.1σ, N=112). Gray band = ±0.25% gain systematic. Both bars are slightly positive and well within the gain band. Significance annotations show the statistical significance.

**Right:** Strip/dot plot showing all 202 individual A-sample % changes, with horizontal mean lines. Faint dots would indicate uncorrected samples (all 202 are temperature-corrected, so none are faint). Both distributions cluster around zero, with NdFeB and SmCo nearly indistinguishable.

*How to read it:* A-sample Helmholtz shows NO NdFeB-SmCo separation. Both materials are slightly positive (~+0.07-0.09%), which is the same pattern seen in H-plate Helmholtz. This is fully consistent with a Helmholtz gain shift between pre-deployment and latest tunnel sessions. The A-sample results carry the same ±0.25% gain systematic as H-plates — no intra-plate differential technique is possible because each A-sample is a single material.

*Key numbers:* NdFeB: +0.085% ± 0.022% (N=90). SmCo: +0.067% ± 0.016% (N=112). NdFeB−SmCo: +0.018% (not significant). 100% temperature-corrected.

---

**`v5_G02_a_sample_teslameter.png` — A-Sample Teslameter Per-Face Analysis**

*What it shows:* Four panels.

**(a) Per-face material bars:** NdFeB and SmCo bars for top, front, and side faces. NdFeB top face: −0.53% ± 0.03% (tight, meaningful). SmCo top face: −0.24% ± 1.56% (enormous error bar — dominated by a few extreme outliers with std=16.5%). Front and side faces have intermediate scatter.

**(b) Distribution box plots:** Six box-and-whisker plots (top/front/side × NdFeB/SmCo). SmCo side and front show extreme outliers extending to ±100% — these are individual A-samples where the Teslameter reading changed dramatically, likely due to rig positioning differences between sessions.

**(c) Top face scatter:** NdFeB top-face data (std=0.33%) vs SmCo top-face data (std=16.5%). NdFeB top is well-behaved with a clear negative mean. SmCo top has wild outliers that destroy precision.

**(d) Statistics table:** Full per-face, per-material statistics showing mean, std, SEM, and N for all 6 combinations.

*How to read it:* NdFeB A-sample Teslameter top face is reasonably well-behaved (std=0.33%, similar to Y-plate top-face std of 0.21%). But **SmCo A-sample Teslameter has catastrophic scatter** — the std of 16.5% on top face means the rig positioning for SmCo pair assembly A-samples is far worse than for Y-plates (where SmCo top std was ~0.3%). This may reflect different rig geometry for pair assembly magnets vs Y-plate magnets.

*Key numbers:* NdFeB top: −0.527% ± 0.033% (std=0.33%, N=98). SmCo top: −0.241% ± 1.563% (std=16.54%, N=112). The SmCo number is meaningless due to outliers.

---

**`v5_G03_a_vs_h_helmholtz.png` — A-Sample vs H-Plate Helmholtz Correlation**

*What it shows:* Two panels.

**Left (scatter):** Each point is one A-sample, plotted at (A-sample % change, H-plate % change for the corresponding pair). NdFeB = red (N=60), SmCo = green (N=80). A 1:1 dashed line shows perfect agreement. The correlation r = 0.24 (N=140) — moderate, positive.

**Right (residual histogram):** Distribution of (A-sample − H-plate) residuals. Mean residual: −0.017%. Std: 0.389%. The distribution is centered near zero, confirming the two measurement levels are consistent on average.

*How to read it:* The moderate correlation (r=0.24) means individual magnets and their pair assemblies partially track each other, but there's substantial scatter. This is expected — the pair Helmholtz measurement integrates both magnets together, while the A-sample measures each individually. If one magnet in a pair degraded more than the other, the A-sample would show different values for the two while the H-plate would show the average. The near-zero mean residual (−0.017%) confirms no systematic bias between measurement levels.

*Key numbers:* r = 0.24 (N=140). Mean residual: −0.017%. Std: 0.389%.

---

**`v5_G04_a_sample_summary.png` — Combined Y + H + A Dashboard**

*What it shows:* Six panels providing a complete cross-comparison of all three measurement levels.

**(a) NdFeB: Y vs H vs A:** Three red bars showing NdFeB % change at each level. Y-plate (−0.297%, N=59), H-plate (+0.026%, N=37), A-sample (+0.085%, N=90). Gray gain band shown. All three are consistent within the gain systematic.

**(b) SmCo: Y vs H vs A:** Three green bars. Y-plate (−0.033%, N=59), H-plate (+0.148%, N=48), A-sample (+0.067%, N=112). H-plate SmCo is the highest (2.4σ positive), but still within the gain band.

**(c) A-sample Teslameter top face:** NdFeB and SmCo bars for Teslameter top-face data. NdFeB is well-defined (−0.53%); SmCo error bar extends to ±1.5% due to outliers.

**(d) A-sample Helmholtz time series:** NdFeB (red) and SmCo (green) mean % change at each measurement date. Shows the time evolution of A-sample Helmholtz readings.

**(e) A-sample by region:** NdFeB and SmCo bars for each of the 7 tunnel regions. Some regions show NdFeB more negative than SmCo (arcs), others show no separation (linacs).

**(f) Key numbers table:** All Y, H, and A results in one table, plus the gain-immune differential and gain systematic. The differential row is highlighted in gold.

*How to read it:* This is the "everything on one page" summary. Panels (a) and (b) show that all three measurement levels agree within the gain systematic — no contradictions. The Y-plate gain-immune differential (bottom of table, 9.7σ) remains the only measurement that can resolve the signal from the noise. The A-sample data adds 202 new measurements that are consistent with, but cannot independently confirm, the Y-plate result.

### A-Sample Key Findings Summary

1. **A-sample Helmholtz** (202 individual magnets): NdFeB +0.085% ± 0.022%, SmCo +0.067% ± 0.016%. Both slightly positive, no NdFeB-SmCo separation. Same pattern as H-plates — dominated by Helmholtz gain systematic.

2. **A-sample Teslameter** (210 samples): NdFeB top face std=0.33% (comparable to Y-plate), but SmCo has catastrophic scatter (std=16.5%) making SmCo A-sample Teslameter data uninformative.

3. **A vs H consistency**: Moderate correlation (r=0.24), near-zero mean residual (−0.017%), confirming individual magnet and pair-level measurements are consistent.

4. **No new physics from A-samples at this precision.** The A-sample data provides a third measurement level that is consistent with all other measurements but cannot independently resolve the ~0.3% degradation signal through the ±0.25% gain systematic. The A-sample Teslameter was hoped to provide better individual-magnet field measurements, but the SmCo rig positioning issues prevent this.

5. **Value of A-samples going forward:** If the Helmholtz gain systematic is reduced (e.g., same-day reference standard), A-samples would provide 8× more individual measurements per H-plate, dramatically improving statistical power. A-sample Teslameter for NdFeB (std=0.33%) may also be useful if SmCo rig issues are resolved.

---

### Updated v5 Plot Index (including polish)

| Plot | Description | Status |
|------|-------------|--------|
| v5_A01-A03 | Waterfall plots (Y, H, combined) | Original |
| v5_B01 | Y-plate regional bars | Original |
| **v5_B02** | **Pass-number trend (POLISHED)** | **Polished** |
| v5_B03-B04 | Arc panels, region heatmap | Original |
| v5_C01-C02 | Assembly config breakdown | Original |
| **v5_D01** | **Executive summary (POLISHED, 4 boxes)** | **Polished** |
| v5_D02 | Publication 2×2 | Original |
| v5_D03 | Results table | Original |
| **v5_D04** | **Dashboard 3×2 (POLISHED)** | **Polished** |
| v5_E01-E02 | Time series (Y, Y+H) | Original |
| **v5_F01** | **Lab control comparison** | **NEW** |
| **v5_G01** | **A-sample Helmholtz material comparison** | **NEW** |
| **v5_G02** | **A-sample Teslameter per-face** | **NEW** |
| **v5_G03** | **A vs H Helmholtz correlation** | **NEW** |
| **v5_G04** | **Combined A+H+Y summary dashboard** | **NEW** |

---

---

## v6: Slot-Mapping Bug Fix (2026-03-16)

**Script:** `Cleanup_Claude/bugfix_slot_mapping.py`
**Plots:** `Cleanup_Claude/Manager_Plots_v6_bugfix/` (3 plots)

### Bug Description

The `compute_double_ratio()` function in `manager_summary_v3.py` had two hardcoded assumptions:

1. **`ALPHA_SLOT = {1: N42EH_α, 2: N52SH_α, 3: SmCo33H_α, 4: SmCo35_α}`** — applied wrong temperature coefficients to ~half the plates
2. **`slots [1,2] = NdFeB, [3,4] = SmCo`** — swapped material assignment for ~half the plates

**In reality, materials are RANDOMIZED across slots** using 4 cyclic rotation patterns (from `Materials_Arrangements.xlsx`). Only ~8 of 30 plates have the hardcoded pattern. For plates where NdFeB occupies slots {1,3} and SmCo occupies {2,4}, the bug computed `mean(NdFeB, SmCo) − mean(SmCo, NdFeB) ≈ 0`, attenuating the real signal. Conversely, for some date pairs the mixing created spurious signals.

### What Was Affected

- **v3_D01 panel (h)** — "Differential Timeline" (Aug 27 ref, time series of NdFeB−SmCo)
- **v4_C03** — Helmholtz intra-plate differential time series
- **Stdout "Double Ratio" numbers** in v3/v4

### What Was NOT Affected

- **The headline 9.7σ result** (`compute_intra_plate_diffs`, groups by material name from spreadsheet) — **CORRECT, unchanged**
- **All per-material averages** (N42EH: −0.333%, etc.) — loaded via `load_all()` which reads spreadsheet — **CORRECT**
- **All v5 and v5_polish plots** — use `compute_intra_plate_diffs`, not `compute_double_ratio`

### Corrected Results

The fixed `compute_double_ratio` (Aug 27 → comparison date, 15 plates with temp correction):

| Date | BUGGED | FIXED | Impact |
|------|--------|-------|--------|
| Jul 17 | +0.052% (1.5σ) | +0.041% (1.1σ) | Minor |
| Jul 30 | +0.868% (1.3σ) | −0.266% (0.7σ) | **Sign flip** |
| Oct 21 | −0.412% (11.3σ) | −0.081% (2.0σ) | **5× weaker** |
| Oct 23 | −0.200% (4.1σ) | +0.067% (1.3σ) | **Sign flip** |
| Oct 29 | −0.358% (12.2σ) | −0.060% (1.3σ) | **6× weaker** |
| Jan 08 | −0.235% (5.4σ) | +0.055% (1.1σ) | **Sign flip** |
| Jan 12 | −0.265% (7.2σ) | +0.067% (1.7σ) | **Sign flip** |

### Physical Interpretation

The fixed double-ratio (Aug 27 → Jan 12) is **+0.067% ± 0.039% (1.7σ)** — essentially zero. This means:

- The NdFeB−SmCo differential was already established by Aug 27 and **remained stable** through Jan 2026
- The bugged version showed −0.265%, numerically matching the headline −0.266% by coincidence
- The true picture: degradation accumulated during beam-on operations (pre-deployment → Aug 2025), then stopped evolving after beam-off (Oct 2025)
- Oct 21 still shows a mild dip (−0.081%, 2.0σ) — residual thermal lag effect (tunnel cooling from ~31°C to 24.7°C)

### Slot Randomization Design (confirmed by user)

Materials are deliberately randomized across the 4 Y-plate slots using cyclic rotations:

| Pattern | Count | Slot 1 | Slot 2 | Slot 3 | Slot 4 |
|---------|-------|--------|--------|--------|--------|
| P1 | 8 | N52SH | SmCo35 | N42EH | SmCo33H |
| P2 | 8 | SmCo35 | N42EH | SmCo33H | N52SH |
| P3 | 7 | SmCo33H | N52SH | SmCo35 | N42EH |
| P4 | 7 | N42EH | SmCo33H | N52SH | SmCo35 |

NdFeB and SmCo always alternate (never adjacent). This eliminates positional radiation-gradient bias between materials on the same plate — the intra-plate differential is a true material comparison.

### Allstar Magnetics Verified Specifications (from uploaded datasheets)

| Parameter | N42EH | N52SH | SmCo33H | SmCo35 |
|-----------|-------|-------|---------|--------|
| Hci (kOe) | ≥30 | ≥19 | ≥25 | ≥18 |
| Max Temp (°C) | 190 | 140 | 350 | 300 |
| α(Br) (%/°C) | −0.10 | −0.11 | −0.040 | −0.040 |
| β(Hci) (%/°C) | −0.50 | −0.60 | −0.20 | −0.25 |

**SmCo35 is NOT equivalent to SmCo33H** for radiation resistance: lower Hci (18 vs 25 kOe) and worse β (−0.25 vs −0.20). This explains the marginal SmCo35 signal (−0.08%, 2σ) while SmCo33H is at zero.

**N42EH vs N52SH inversion**: N42EH degrades MORE (−0.333%) than N52SH (−0.260%) despite higher Hci. Possible physics: (a) more Dy→more boron→more ¹⁰B(n,α) pathway, (b) different operating point, (c) different thermal stabilization history. Slot randomization confirms this is not a positional artifact.

### v6 Plot Index

| Plot | Description |
|------|-------------|
| v6_bugfix_comparison.png | Side-by-side: bugged vs fixed vs overlay |
| v6_differential_timeline_fixed.png | Corrected v3_D01 panel (h) |
| v6_v4C03_differential_timeline_fixed.png | Corrected v4_C03 Helmholtz panel |

---

### Recommended Priority for Next Session
1. **Dose data correlation** — bring in NDX data (when Kirsten delivers), overlay on degradation by position
2. **Investigate pass-number inversion** with dose data
3. **Temnykh Td validation** — compare ΔT_crit ranking with observed degradation per grade
4. **N42EH > N52SH inversion** — investigate ¹⁰B content and thermal stabilization history
5. **Restructure presentation plots** per analysis directives (dual with/without Jul 17, honest Teslameter caveats)

---

*v1 generated by manager_summary.py; v2 by manager_summary_v2.py; v3 by manager_summary_v3.py; v4 by manager_summary_v4.py; v5 by manager_summary_v5.py; v5 polish by manager_summary_v5_polish.py; v6 bugfix by bugfix_slot_mapping.py*
*Data: 30 Y-plates × 4 slots = 120 samples; 85 H-plate pairs; 202 A-samples (90 NdFeB + 112 SmCo); 9 lab Y-plates*
*Allstar Magnetics datasheets: NdFeB_Grades_Properties_AllstarMagnetics.pdf, SmCO_Grades_Properties_AllstarMagnetics.pdf*
