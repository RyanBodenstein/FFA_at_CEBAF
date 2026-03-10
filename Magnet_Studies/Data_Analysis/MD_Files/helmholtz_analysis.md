# LDRD Helmholtz Coil Data Analysis

**Data sources:** Jan_12_Helmholtz.zip, Oct_29_Helmholtz.zip, 20260108_Helmholtz.zip, Materials_Arrangements_Spreadsheet.xlsx

**Coverage:** 451+ Helmholtz .dat files across 9 measurement campaigns (July 2025 - January 2026), 30 tunnel Y-plates with 4 material grades each, 14 NdFeB pair assemblies (n-plates), 24 SmCo pair assemblies (s-plates)

---

## 1. Data Format and Inventory

Each .dat file contains one line per measurement: date, time, dosimeter ID, optichromic rod ID, and Helmholtz reading in mWC (milli-Weber-cycles). Files accumulate measurements across campaigns, so later files contain all earlier readings plus the new one.

**Measurement campaigns:**

| Date | Y-plate measurements | Notes |
|------|---------------------|-------|
| 2025-07-17 | 60 (15 plates) | First campaign, plates 4,6,7,9,12,16,17,18,21,22,25,34,36,38,39 |
| 2025-07-30 | 59 (15 plates) | Second campaign, plates 1,3,5,10,11,13,15,19,20,23,24,26,30,32,40 |
| 2025-08-27 | 124 (all 30) | Full survey |
| 2025-10-21 | 60 | Partial survey |
| 2025-10-23 | 39 | Partial survey |
| 2025-10-29 | 20 | Partial survey |
| 2025-12-17 | 32 | Lab measurements (Adam R.) -- spare/reference plates |
| 2026-01-08 | 59 | Post-run survey (tunnel cooled, Teslameter ~28-29C) |
| 2026-01-12 | 60 | Post-run survey (tunnel cooled, Teslameter ~28-29C) |

The Jul 17 and Jul 30 campaigns measured different sets of 15 plates each. These two groups show systematically different behavior (see Section 3), suggesting they may occupy different physical locations or were measured under different conditions.

---

## 2. Raw Helmholtz Time Series Summary

### Material-averaged raw % change (first measurement to last)

| Material | n | Mean raw change | Std Dev | Min | Max |
|----------|---|-----------------|---------|-----|-----|
| N42EH | 30 | +1.240% | 2.117% | +0.180% | +12.335%* |
| N52SH | 30 | +0.917% | 0.582% | -1.043% | +1.697% |
| SmCo33H | 30 | +0.620% | 0.486% | -0.318% | +1.395% |
| SmCo35 | 30 | +0.562% | 0.449% | -0.232% | +1.311% |

*Y-32 slot 3 (N42EH) has an anomalous +12.3% jump likely due to a bad initial reading (first entry appears to be from wrong sample or measurement error).

**Key observation:** All materials show net POSITIVE (increasing) raw Helmholtz readings over the July 2025 to January 2026 period. This is opposite to the expected direction for radiation-induced degradation (which would decrease Br and thus decrease the Helmholtz reading). The positive trend is dominated by the tunnel cooling from ~31-32C during beam operations to ~28-29C after the run ended.

---

## 3. Temperature Systematics

### The dominant effect

The Helmholtz coil measures the total magnetic flux of the sample, which is directly proportional to Br(T). Since all four grades have negative alpha(Br) temperature coefficients, a cooler magnet reads higher:

| Grade | alpha(Br) | Effect of 1C cooling |
|-------|-----------|---------------------|
| N42EH | -0.10 %/C | +0.10% increase in reading |
| N52SH | -0.11 %/C | +0.11% increase in reading |
| SmCo33H | -0.04 %/C | +0.04% increase in reading |
| SmCo35 | -0.04 %/C | +0.04% increase in reading |

The tunnel temperature changes through the measurement period: ~31-32C during beam operations (Jul-Oct 2025), cooling to ~28-29C in January 2026 after the run ended (confirmed by Teslameter probe readings). This ~3C cooling would produce:

- NdFeB: ~+0.30% increase in Helmholtz reading
- SmCo: ~+0.12% increase in Helmholtz reading

### Jul 17 vs Jul 30 group systematic

The two groups of plates (first measured Jul 17 vs. Jul 30) show strikingly different raw changes:

| Material | Jul 17 group (n=15 plates) | Jul 30 group (n=15 plates) |
|----------|---------------------------|---------------------------|
| N42EH | +1.280% | +1.200% |
| N52SH | +1.379% | +0.456% |
| SmCo33H | +1.011% | +0.229% |
| SmCo35 | +0.976% | +0.149% |

The Jul 17 group shows roughly 2-4x larger changes than the Jul 30 group for SmCo and N52SH. This difference persists even within the beam-on period (Jul to Oct, where tunnel temperature should be similar):

| Material | Jul 17 to Oct (beam-on) | Jul 30 to Oct (beam-on) |
|----------|------------------------|------------------------|
| N42EH | +1.249% | +1.212% |
| N52SH | +1.299% | +0.443% |
| SmCo33H | +0.955% | +0.239% |
| SmCo35 | +0.924% | +0.176% |

The persistence of this difference during the beam-on period (when all plates are at similar tunnel temperature) points to a systematic offset in the first measurement of the Jul 17 group. Possible explanations: the Jul 17 plates were measured at a higher temperature than the Jul 30 plates (e.g., in a warmer section of the tunnel, or before the measurement equipment equilibrated); or the Jul 17 initial measurements were affected by some other systematic.

---

## 4. Intra-Plate Material Differential (Temperature-Controlled Analysis)

### Methodology

The most robust analysis compares materials within the same plate, because all four samples on a plate share the same temperature, location, and measurement conditions. The NdFeB-minus-SmCo differential cancels all plate-specific systematics.

### Results (28 plates, excluding Y-20 and Y-32 outliers)

| Statistic | Value |
|-----------|-------|
| Mean NdFeB - SmCo differential | +0.331% |
| Std dev | 0.146% |
| Standard error of mean | 0.028% |

The positive differential means NdFeB readings increase more than SmCo on the same plate. This is consistent with the temperature coefficient difference:

- Implied temperature change to explain the differential purely from alpha(Br) difference: **5.1C**
- Expected from known tunnel cooling (31-32C to 28-29C): **3-4C**

The 5.1C estimate is somewhat higher than the expected 3-4C, which could indicate the initial measurements were taken at slightly higher temperatures than 31-32C, or that the tunnel had already partially cooled for some October measurements.

### What this means for detecting a radiation signal

If radiation were preferentially degrading NdFeB relative to SmCo (as the DeltaT_crit framework predicts), this would push the NdFeB-SmCo differential more NEGATIVE (NdFeB losing more flux). The observed differential is fully positive and consistent with temperature alone. At current dose levels, the radiation-induced material-dependent degradation signal is below the detection threshold set by temperature uncertainty.

A 1C error in assumed temperature produces a 0.065% error in the NdFeB-SmCo differential. To detect a radiation-induced NdFeB-SmCo difference of, say, 0.1%, the temperature of each measurement would need to be known to better than ~1.5C.

---

## 5. Pair Assembly Configuration Comparison

### Results

| Config | Material | n | Mean raw change | Std Dev |
|--------|----------|---|-----------------|---------|
| Alpha | NdFeB | 28 | +0.927% | 0.385% |
| Alpha | SmCo | 32 | +0.459% | 0.428% |
| Beta | NdFeB | 28 | +0.893% | 0.435% |
| Beta | SmCo | 32 | +0.609% | 0.357% |
| Gamma | NdFeB | 28 | +0.935% | 0.489% |
| Gamma | SmCo | 32 | +0.570% | 0.332% |
| Delta | NdFeB | 14 | +0.848% | 0.441% |
| Delta | SmCo | 16 | +0.629% | 0.367% |

No statistically significant configuration dependence is observed. Alpha, Beta, Gamma, and Delta configurations show indistinguishable raw changes for NdFeB (~0.85-0.94%) and for SmCo (~0.46-0.63%).

**Caveat per JLAB-TN-25-069:** Beta (antiparallel) Helmholtz readings are unreliable due to the nonlinear multipole character of the antiparallel field.

---

## 6. Plate Inventory Notes

### Tunnel Y-plates with material assignments (from spreadsheet)
y-1, y-3, y-4, y-5, y-6, y-7, y-9, y-10, y-11, y-12, y-13, y-15, y-16, y-17, y-18, y-19, y-20, y-21, y-22, y-23, y-24, y-25, y-26, y-30 (24 plates)

### Pair assemblies (from spreadsheet)
14 NdFeB n-plates: n-6, n-8, n-9, n-10, n-11, n-12, n-15, n-16, n-17, n-18, n-19, n-20, n-37, n-39
24 SmCo s-plates: s-1 through s-7, s-10, s-12, s-13, plus others

### Plates with data but not in tunnel materials spreadsheet
Y-8, Y-14, Y-27, Y-28, Y-29, Y-31, Y-33, Y-35, Y-37 -- likely lab reference samples or spares (Y-14, Y-27, etc. have single measurements from 2025-12-17 lab campaign).

---

## 7. Conclusions and Implications

1. **Temperature correction is the critical systematic.** The raw Helmholtz data cannot be interpreted as degradation trends without per-measurement temperature correction. The magnitude of the temperature effect (+0.3 to +1% from tunnel cooling) exceeds the expected radiation signal at current dose levels.

2. **The NdFeB-SmCo material ranking is qualitatively consistent** with both the temperature coefficient difference (larger |alpha| for NdFeB) and the predicted radiation sensitivity ranking (NdFeB more sensitive than SmCo). The two effects work in the same direction for the intra-plate comparison, making them difficult to separate.

3. **No configuration-dependent (operating-point-dependent) signal is detected** in the pair assemblies. The DeltaT_crit framework predicts Beta > Alpha degradation, but this is not resolvable above the temperature noise floor at current dose levels.

4. **The "0 to -2% raw degradation" reported in JLAB-TN-25-069** is computed relative to pre-deployment lab baselines (measured at ~22-24C). The lab-to-tunnel temperature offset alone accounts for approximately -1.0% for NdFeB and -0.4% for SmCo. Within the tunnel-only data (this analysis), values monotonically INCREASE as the tunnel cools post-run.

5. **Co-located temperature measurement is the single highest-impact improvement** for future measurement campaigns. Even a simple RTD or thermocouple reading of the sample holder temperature at each measurement would enable first-order temperature correction and potentially reveal the radiation signal currently masked by the thermal systematic.
