# LDRD Helmholtz + Teslameter Combined Analysis

**Data sources:** Jan_12_Helmholtz.zip, Oct_29_Helmholtz.zip, 20260108_Helmholtz.zip, JanTesla_tar.xz, Materials_Arrangements_Spreadsheet.xlsx

**Coverage:** 7654 Teslameter .dat files (front/side/top faces) + 451+ Helmholtz .dat files across 9 campaigns (July 2025 -- January 2026), 30 tunnel Y-plates with 4 material grades each

---

## 1. Temperature Data from Teslameter

The Teslameter files contain temperature readings in the 8th field. This is the first time co-located temperatures have been used in this analysis. The actual measured temperatures differ significantly from earlier assumed values.

**Campaign temperatures (averaged across all Y-plate Teslameter readings):**

| Date | Mean T (C) | Range (C) | n plates | Notes |
|------|-----------|-----------|----------|-------|
| 2024-11-05 | 25.1 | 22.0 -- 27.7 | ~24 | Pre-deployment (magnets not installed) |
| 2024-11-07 | 24.5 | 22.6 -- 25.9 | ~15 | Pre-deployment |
| 2025-07-15 | 24.6 | 23.0 -- 26.2 | 3 | Lab measurements (pre-tunnel) |
| 2025-07-17 | 32.3 | 28.8 -- 33.7 | 15 | First tunnel campaign (beam on) |
| 2025-07-30 | 31.5 | 30.7 -- 32.4 | 15 | Second tunnel campaign (beam on) |
| 2025-08-27 | 31.4 | 27.0 -- 33.2 | 31 | Full survey (beam on) |
| 2025-10-21 | 24.7 | 22.6 -- 27.9 | 15 | Tunnel access (beam OFF -- cooled) |
| 2025-10-23 | 28.5 | 25.8 -- 29.3 | 10 | Tunnel access |
| 2025-10-29 | 27.6 | 26.1 -- 28.2 | 5 | Tunnel access |
| 2026-01-08 | 27.7 | 24.5 -- 28.6 | 15 | Post-run (beam OFF, tunnel cooling) |
| 2026-01-12 | 27.2 | 25.2 -- 28.4 | 15 | Post-run |

**Critical findings about temperature:**

The October 21 campaign was at 24.7C (mean), NOT ~31C. This means the tunnel had already cooled substantially during this access, likely because beam was off for the measurement period. This is a major correction from the initial analysis, which assumed ~31.5C for all beam-on-era measurements.

The within-campaign temperature spread is large (up to 6C on Jul 17, Aug 27), indicating significant spatial variation in the tunnel. Plate-specific temperatures are essential for accurate correction.

**Broken probe sentinel:** Values of 1337 appear throughout the Jan-Jul 2025 period across all Teslameter files. This represents the broken probe period. The Sep 10 campaign also shows 1337s (another probe failure?). These measurements are excluded from all analysis.

---

## 2. Pre-Deployment Baselines

The Nov 2024 Teslameter readings show very low field values (Bx ~ 3-5 mT for Y-plates, vs. ~80-96 mT after installation). This confirms magnets were NOT installed during the Nov 2024 measurements. The Nov 2024 data represents empty-plate/holder background fields, not magnet baselines.

The first Teslameter readings with magnets installed are from July 2025 (Jul 17 or Jul 30 depending on the plate group). No pre-deployment Teslameter baselines with magnets in place are available in this dataset. If lab Teslameter baselines exist (measured before tunnel installation), they are in a separate dataset.

The Helmholtz files similarly begin with Jul 2025 as the earliest measurements.

---

## 3. Temperature-Corrected Teslameter Analysis (Front-Face Bx)

**Correction formula:** Bx_corr = Bx_raw / (1 + alpha/100 * (T - 25.0))

Using plate-specific temperatures from co-located Teslameter readings:

| Material | n | Raw mean change | Corrected mean | Std dev |
|----------|---|----------------|----------------|---------|
| N42EH | 24 | +0.649% | +0.218% | 0.630% |
| N52SH | 24 | +1.281% | +0.803% | 0.835% |
| SmCo33H | 24 | +0.588% | +0.416% | 0.501% |
| SmCo35 | 24 | +0.511% | +0.339% | 0.427% |

**Interpretation:** After temperature correction, all material means are positive (increasing Bx), which is the OPPOSITE direction from radiation-induced degradation. However, individual samples show a wide range from approximately -2% to +2.7%.

Samples showing the largest NEGATIVE corrected changes (possible degradation candidates):
- Y-10-2 (N42EH): -1.92%
- Y-22-4 (N52SH): -0.49%
- Y-13-1 (SmCo33H): -0.53% (among largest SmCo decreases)
- Y-40-2 (SmCo35): -1.19%

---

## 4. Temperature-Corrected Helmholtz Analysis

Using the SAME co-located Teslameter temperatures for correction:

| Material | n | Raw mean change | Corrected mean | Std dev |
|----------|---|----------------|----------------|---------|
| N42EH | 24 | +0.787% | +0.361% | 0.453% |
| N52SH | 24 | +0.850% | +0.375% | 0.577% |
| SmCo33H | 24 | +0.588% | +0.416% | 0.501% |
| SmCo35 | 24 | +0.511% | +0.339% | 0.427% |

The Helmholtz corrected means are similar to the Teslameter corrected means and also show positive (increasing) trends.

---

## 5. Teslameter vs. Helmholtz Discrepancy

A critical finding: the Teslameter and Helmholtz sometimes give OPPOSITE signs for the same sample. For example, Y-22 slot 4 (N52SH):

**Teslameter front Bx (corrected):**
| Date | Raw Bx | Corr Bx | T | Delta |
|------|--------|---------|---|-------|
| Jul 17 | 95.991 | 96.772 | 32.3C | baseline |
| Aug 27 | 93.773 | 94.614 | 33.1C | -2.23% |
| Oct 21 | 96.319 | 96.144 | 23.3C | -0.65% |
| Jan 12 | 95.966 | 96.300 | 27.9C | -0.49% |

**Helmholtz mWC (corrected):**
| Date | Raw mWC | Corr mWC | T | Delta |
|------|---------|----------|---|-------|
| Jul 17 | 1.2786 | 1.2890 | 32.3C | baseline |
| Aug 27 | 1.2841 | 1.2956 | 33.1C | +0.51% |
| Oct 21 | 1.2980 | 1.2956 | 23.3C | +0.51% |
| Jan 12 | 1.2974 | 1.3019 | 28.2C | +1.00% |

The Teslameter shows a -2.2% dip at Aug 27 and a net -0.49% decrease. The Helmholtz shows a monotonic +1.0% increase. These are the SAME physical magnet measured on the same dates.

This discrepancy likely arises from Teslameter probe positioning sensitivity. The Teslameter measures the field at a specific point on the magnet surface, where the field gradient is steep. A 0.5 mm shift in probe placement between campaigns can produce >1% variation in the reading. The Helmholtz coil integrates over the full magnet volume, making it insensitive to positioning.

The Y-22 slot 4 "dip" at Aug 27 does not appear on the side or top faces at comparable magnitude, further supporting a positioning artifact interpretation.

---

## 6. Jul 17 vs Jul 30 Group Systematic

The two groups of 15 plates (first measured Jul 17 vs Jul 30) continue to show systematic differences, though the pattern differs between instruments:

**Teslameter (corrected front Bx):**
| Material | Jul 17 group | Jul 30 group |
|----------|-------------|-------------|
| N42EH | +0.17% | +0.25% |
| N52SH | +0.59% | +1.00% |
| SmCo33H | +0.32% | +0.40% |
| SmCo35 | +0.06% | +0.24% |

In the Teslameter, the Jul 17 group shows SMALLER corrected changes than Jul 30.

**Helmholtz (corrected):**
The Helmholtz showed the OPPOSITE pattern (Jul 17 group larger than Jul 30) in the earlier analysis, with the difference being most pronounced for SmCo grades.

This reversal between instruments suggests the systematic is related to measurement conditions rather than genuine physical differences between the two plate groups.

---

## 7. Y-22 and Y-25 Detailed Time Series

### Y-22 (NL Girder 26, high-dose location, ~20 kGy estimated)

**Teslameter front Bx, temperature-corrected to 25C:**

| Slot | Material | Jul 17 | Aug 27 | Oct 21 | Jan 12 | Net change |
|------|----------|--------|--------|--------|--------|------------|
| 1 | SmCo35 | 79.389 | 79.424 | 79.381 | 79.422 | +0.04% |
| 2 | N42EH | 84.122 | 84.006 | 84.527 | 84.640 | +0.62% |
| 3 | SmCo33H | 75.883 | 75.813 | 75.905 | 75.719 | -0.22% |
| 4 | N52SH | 96.772 | 94.614 | 96.144 | 96.300 | -0.49% |

Two of four slots (SmCo33H, N52SH) show net negative (degradation-like) changes. But the Aug 27 anomaly on N52SH (-2.2%) suggests probe positioning dominates the scatter.

**Helmholtz mWC, temperature-corrected:**

| Slot | Material | Jul 17 | Aug 27 | Oct 21 | Jan 12 | Net change |
|------|----------|--------|--------|--------|--------|------------|
| 1 | SmCo35 | 1.0701 | 1.0753 | 1.0783 | 1.0803 | +0.95% |
| 2 | N42EH | 1.1589 | 1.1654 | 1.1672 | 1.1703 | +0.98% |
| 3 | SmCo33H | 1.0293 | 1.0377 | 1.0380 | 1.0403 | +1.07% |
| 4 | N52SH | 1.2890 | 1.2956 | 1.2956 | 1.3019 | +1.00% |

All four Helmholtz slots show ~+1% corrected increases, with no material dependence. This uniformity across materials (despite different alpha values) is suspicious and warrants investigation.

### Y-25 (SE Arc, lower-dose location, ~0.6 kGy estimated)

Similar patterns: Teslameter shows mixed signs; Helmholtz shows uniform ~+0.8-1.0% increases.

---

## 8. Discussion: Why Corrected Values Show Increases

Both instruments show, on average, positive corrected changes from Jul 2025 to Jan 2026. Several possible explanations:

**a) Incomplete temperature correction.** The alpha(Br) coefficient is itself temperature-dependent. At 32C, the actual alpha may differ from the nominal room-temperature value by 5-10%. This could systematically bias the correction. Additionally, the Teslameter probe temperature may not perfectly reflect the magnet body temperature, especially during tunnel access when thermal equilibrium may not have been reached.

**b) Initial magnetization settling.** Newly magnetized or recently handled permanent magnets can show a small initial increase in remanence as the domain structure relaxes into a more stable configuration. This "aging" or "stabilization" typically occurs over the first weeks/months and is on the order of +0.1 to +0.5%.

**c) Helmholtz coil systematic.** The Helmholtz coil calibration may drift between campaigns if the electronics, cable routing, or coil spacing change slightly. A ~1% systematic shift would explain the uniform increase seen across all materials.

**d) Probe replacement offset.** The broken probe (1337 sentinel values) was replaced between the Jan-Jul 2025 period and the Jul 17 first measurements. If the replacement probe has a different calibration constant or sensitivity, all subsequent readings would be offset relative to any baselines taken with the original probe. This is consistent with the user's note about "offsets due to a broken probe from our baselines."

---

## 9. Reconciliation with TN-25-069

The tech note reports "0 to -2% raw degradation" relative to baselines. My analysis shows +0.2 to +0.8% corrected increases. The most likely explanation for this discrepancy is:

1. **The baselines are not in this dataset.** The lab baselines (taken with the original probe at ~22-24C before deployment) would show HIGHER fields than the in-tunnel readings. The lab-to-tunnel temperature offset alone accounts for -0.7 to -1.1% for NdFeB and -0.3 to -0.4% for SmCo.

2. **Probe replacement offset.** If the original probe read slightly higher than the replacement, this would add an apparent negative offset to all post-replacement measurements when compared to pre-replacement baselines.

3. **My in-tunnel-only analysis** (Jul 2025 to Jan 2026) cannot capture the full baseline-to-current degradation. It only captures the within-tunnel trend, which is dominated by temperature variations and potentially masked by measurement systematics.

4. **The degradation signal may emerge more clearly** when the analysis includes the actual lab baselines and accounts for the probe replacement offset -- which is likely what the TN-25-069 plots show.

---

## 10. Recommendations

1. **Provide the lab baseline data.** The pre-deployment Helmholtz and Teslameter measurements taken at lab temperature with the original probe are needed to compute absolute degradation from baseline.

2. **Characterize the probe replacement offset.** If reference magnets (known stable) were measured with both the old and new probes, the offset can be quantified and removed.

3. **Focus on the Helmholtz for degradation tracking.** The Helmholtz coil is an integrating measurement that is insensitive to probe positioning, making it more reliable for tracking sub-1% changes than the Teslameter point measurement. The Teslameter's value is in providing co-located temperatures and field mapping information.

4. **Consider the ~+1% Helmholtz systematic.** The uniform +1% corrected increase across all four materials on Y-22 is not physically consistent with either radiation damage or temperature effects (which should differ by material). This suggests a measurement systematic that should be investigated.
