# Error Analysis Reference Guide

## LDRD FFA@CEBAF Permanent Magnet Radiation Damage Study

**Audience:** Summer interns and new team members
**Last updated:** 2026-06-04

---

## Table of Contents

- [A. Overview and Context](#a-overview-and-context)
- [B. Instruments](#b-instruments)
- [C. Temperature Correction](#c-temperature-correction)
- [D. The Intra-Plate Differential](#d-the-intra-plate-differential)
- [E. Gain Systematic Quantification](#e-gain-systematic-quantification)
- [F. Within-Session Drift](#f-within-session-drift)
- [G. Calibration Plates](#g-calibration-plates)
- [H. Baseline Temperature](#h-baseline-temperature)
- [I. Teslameter Positioning Noise](#i-teslameter-positioning-noise)
- [J. Statistical Methods](#j-statistical-methods)
- [K. Outlier Handling](#k-outlier-handling)
- [L. Error Budget Table](#l-error-budget-table)
- [M. Lab Controls Validation](#m-lab-controls-validation)

---

## A. Overview and Context

### What Are We Measuring?

This experiment measures whether radiation in the CEBAF accelerator tunnel at
Jefferson Lab causes permanent magnets to lose their magnetization. This matters
because the proposed FFA (Fixed Field Alternating-gradient) accelerator upgrade
would use permanent magnets extensively, and they need to survive the tunnel
radiation environment for decades.

### The Physical Setup

We deployed 30 "Y-plates" in the CEBAF tunnel at 8 different locations for
approximately 12 months (January 2025 to January 2026). Each Y-plate holds
exactly 4 permanent magnets, one of each grade:

| Material | Family | Why it matters |
|----------|--------|----------------|
| **N42EH** | NdFeB (neodymium) | Strong, radiation-sensitive, contains 1-2% dysprosium |
| **N52SH** | NdFeB (neodymium) | Strongest grade, radiation-sensitive, 0% dysprosium |
| **SmCo33H** | SmCo (samarium cobalt) | Radiation-hard control, lower field |
| **SmCo35** | SmCo (samarium cobalt) | Radiation-hard control, lower field |

The 4 material slots on each plate are randomized (not always in the same order)
across 4 cyclic patterns (P1 through P4, with 8, 8, 7, and 7 plates each).

An additional 9 Y-plates are kept in the lab as unexposed controls:
Y-{8, 14, 27, 28, 29, 31, 33, 35, 37}. These never see tunnel radiation and
serve as our "null experiment."

There are also H-plates (Halbach-style assemblies, 4 slots each in Alpha/Beta/
Gamma/Delta configurations) and A-samples (small paired magnets). The Y-plates
are the primary discovery measurement because of the gain-immune differential
technique. However, the H-plates and A-samples are critical for the broader
science story: H-plates directly demonstrate degradation behavior in Halbach
field geometries (the actual FFA use case), and A-samples provide paired
field-vs-zero-field comparisons. For high-impact publications, demonstrating
consistent results across all three sample types, using both integrated moment
(Helmholtz) and spatially-resolved point field (Teslameter) measurements, is
the goal.

### What "Percent Change" Means

For every magnet sample, we measure its magnetic moment before deployment
(the "baseline") and after deployment. The percent change is:

```
Delta_i = (H_latest - H_baseline) / H_baseline x 100%
```

where H is the Helmholtz coil reading in milliWeber-centimeters (mWC), corrected
to a common reference temperature of 20 C.

- **Negative Delta** = demagnetization (lost field). This is what we expect from
  radiation damage.
- **Positive Delta** = apparent gain. Usually noise or a measurement artifact, but
  can indicate thermal aging recovery in SmCo.
- **Zero Delta** = no change, within noise.

Our headline result: NdFeB magnets lost ~0.17-0.25% of their field after 12 months
in the tunnel. SmCo magnets showed no statistically significant change. The
difference between these (the "differential") is -0.208%, detected at 7.6 sigma
statistical significance.

### Sample Types Quick Reference

| Type | Format | Example | Description |
|------|--------|---------|-------------|
| Y-plate | Y-{plate}-{slot} | Y-17-3 | Tunnel/lab plate, slot 1-4 |
| H-plate | H{n/s}-{plate}-{slot} | Hn-10-2 | Halbach north/south, slot 1-4 |
| A-sample | A{n/s}-{plate}-{slot}-{pair} | An-10-2-1 | Small paired magnet |

The sentinel value **1337** in any data file means "no measurement" (excluded
from all calculations).


---

## B. Instruments

We use two complementary instruments. They measure different physical quantities
and have very different noise characteristics.

### B.1 Helmholtz Coil + Fluxmeter (Model 2130)

**What it measures:** The total magnetic moment of a sample by integrating the
flux change when the sample is inserted into a calibrated Helmholtz coil pair.

**Output units:** milliWeber-centimeters (mWC), proportional to the sample's total
dipole moment.

**Key specifications:**
- DC accuracy: 0.050% typical, 0.100% maximum (of full scale)
- 12 ranges: 100 kMT to 100 MMT, with 4 3/4 digit resolution
- Auto drift compensation (+/-1% of range)
- Position-independent: reading is "fairly independent of sample position within
  the coils" as long as the sample is approximately centered

**Why we use it:** The Helmholtz measurement integrates over the entire sample
volume, so it gives a true total-moment measurement that is insensitive to
exactly where the magnet sits inside the coil. This is crucial because our
samples are hand-inserted.

**The big catch: gain drift.** The fluxmeter output drifts by 0.5-0.7% from
session to session. This is NOT the instrument's intrinsic accuracy (which is
0.05%); it comes from drifting coil parameters, cable connections, and
electronics temperature. This drift is the single largest systematic error for
any individual magnet measurement. The intra-plate differential technique
(Section D) eliminates it.

**Data file format:** Tab-separated `.dat` files with columns:
```
date    time    dosimeter_id    rod_id    value unit
2026-06-02  09:21:19  XA01080034Q  R-825  0.9123 mWC
```

### B.2 Teslameter (SENIS 3MH6-E) + Hall Probe Type C

**What it measures:** The magnetic field vector at a single point on the
magnet surface, using a 3-axis CMOS Hall sensor.

**Output units:** milliTesla (mT) for each axis (Bx, By, Bz). The magnitude
|B| = sqrt(Bx^2 + By^2 + Bz^2) is also computed.

**Key specifications:**
- DC accuracy: 0.01% (100 ppm) at +/-0.1T/+/-0.5T/+/-2T ranges
- Temperature stability: <20 ppm/C
- Resolution: ~1 uT RMS at 10 SPS (~0.5 ppm)
- 3-axis CMOS Hall probe, sensing volume ~100 x 10 x 100 um^3
- Built-in temperature sensor (reads probe junction temperature)
- Calibration stored in probe EEPROM; maintains 100 ppm on probe swap

**Why we use it:** Two reasons:
1. **Temperature:** The built-in probe temperature is our primary temperature
   measurement for the Helmholtz temperature correction (Section C).
2. **Independent cross-check:** Field measurements on three faces (top, front,
   side) provide an independent check on demagnetization trends.

**The big catch: positioning noise.** The Teslameter measures field at a single
point. If the sample sits 0.1 mm differently in the 3D-printed rig, the field
at the probe location changes. This "positioning noise" dominates the Teslameter
error budget (0.14-1.90% depending on face; see Section I).

**Data file format:** Tab-separated `.dat` files:
```
date    time    dosimeter_id    rod_id    Bx    By    Bz    temp_C
2026-06-02  09:24:59  XA01080034Q  R-825  -180.053  -4.250  -3.566  26.708
```

### B.3 Arduino AM2302 Temperature/Humidity Sensor (NEW, June 2026)

**What it measures:** Ambient air temperature and relative humidity near the
Helmholtz coil setup, via an ASAIR AM2302 (DHT22-equivalent) digital sensor
connected to an Arduino.

**Output units:** Temperature in degrees Celsius, relative humidity in percent.

**Key specifications:**
- Temperature accuracy: +/-0.5 C
- Temperature resolution: 0.1 C
- Response time: ~2 seconds (thermal time constant)
- Humidity accuracy: +/-2-3% RH
- Humidity range: 0-100% RH
- Update interval: ~2 seconds

**Why we added it:** The Teslameter's temperature reading comes from the Hall
probe junction, which is pressed against (or near) the magnet surface. This
means the "temperature" it reports is influenced by the magnet's temperature
(which may lag behind room temperature) and possibly by Joule heating in the
probe itself. The AM2302 measures ambient air temperature near the setup, which
is an independent data point.

**Important caveat:** Neither sensor directly measures the sample's true
internal temperature, which is what the temperature correction formula
actually needs. The Teslameter probe is in thermal contact with the sample
surface, so it may be closer to the sample temperature; the Arduino sensor
measures the surrounding air, which could differ from the sample temperature
if the sample hasn't fully equilibrated, or could be influenced by drafts,
laptop fans, or HVAC airflow near the sensor. Which sensor provides the
better proxy for the temperature correction is an open question that the
cross-calibration study (Priority 2 in the summer plan) is designed to answer.

**June 2026 data shows** the Teslameter reads 0-2.7 C higher than the Arduino
at low temperatures, with the discrepancy shrinking to near zero at high temps.
Possible explanations include probe self-heating, thermal lag in the magnet
(the sample may genuinely be warmer than the air early in the day), or
sensitivity of the Arduino to local air currents. Disentangling these effects
is a key goal of the summer cross-calibration work.

**Data file format:** Tab-separated `*_helmholtzTemp.dat` files:
```
date    time    dosimeter_id    rod_id    temp degC    humidity %
2026-06-02  09:21:19  XA01080034Q  R-825  25.80 degC  42.30 %
```

Each helmholtzTemp file corresponds to one Helmholtz measurement of one sample.
The Arduino reading is taken at the moment of the Helmholtz measurement, while
the Teslameter reading may be taken minutes later (when the sample is moved to
the Teslameter rig). There are 484 helmholtzTemp files from the June 2-3
measurement campaign.


---

## C. Temperature Correction

### Why Temperature Correction Matters

All permanent magnets get weaker when they warm up and stronger when they cool
down. This is a reversible, well-understood thermodynamic effect described by
the temperature coefficient of remanence, alpha(Br), expressed in percent per
degree Celsius.

If we do not correct for temperature, a magnet measured at 28 C will appear to
have lost about 0.8% of its field compared to a baseline taken at 20 C, even if
no radiation damage occurred. Since our signal is only ~0.2%, temperature
correction is essential.

### The Formula

All readings are corrected to a common reference temperature:

```
H_corrected = H_raw / (1 + alpha * (T_measured - T_ref))
```

where:
- `H_raw` = the raw Helmholtz reading in mWC
- `alpha` = temperature coefficient for this material (fractional, e.g. -0.0010)
- `T_measured` = temperature at the time of measurement, in degrees C
- `T_ref` = 20.0 C (our reference temperature)

### Temperature Coefficients (alpha values)

| Material | alpha (%/C) | alpha (fractional) | Source |
|----------|-------------|-------------------|--------|
| N42EH | -0.10 | -0.0010 | Allstar Magnetics datasheet |
| N52SH | -0.11 | -0.0011 | Allstar Magnetics datasheet |
| SmCo33H | -0.04 | -0.0004 | Allstar Magnetics datasheet |
| SmCo35 | -0.04 | -0.0004 | Allstar Magnetics datasheet |

Note: NdFeB magnets are about 2.5x more temperature-sensitive than SmCo magnets.
This asymmetry has important consequences (see below).

### Worked Example

Suppose you measure Y-17-1 (an N42EH magnet) in the Helmholtz coil and get:
- Raw reading: 0.9234 mWC
- Teslameter temperature: 27.5 C

Correction:
```
alpha = -0.0010 (for N42EH)
T_measured = 27.5
T_ref = 20.0

H_corrected = 0.9234 / (1 + (-0.0010) * (27.5 - 20.0))
            = 0.9234 / (1 + (-0.0010) * 7.5)
            = 0.9234 / (1 - 0.0075)
            = 0.9234 / 0.9925
            = 0.93037 mWC
```

The corrected value is higher than the raw value because the magnet was warm
(above 20 C), so its raw reading was artificially low.

### Why Temperature Matters for the Differential

Even though the differential compares NdFeB to SmCo on the same plate (same
temperature), the temperature correction does NOT perfectly cancel because
the alpha values are different:

```
Differential temperature sensitivity = alpha_NdFeB_mean - alpha_SmCo
= [(-0.10 + -0.11)/2] - (-0.04)
= -0.105 - (-0.04)
= -0.065 %/C
```

So for every 1 C error in our baseline temperature estimate, the differential
shifts by 0.065% (we round to 0.066%/C accounting for the exact weighted
average). This is the single largest remaining systematic: a +/-0.5 C
temperature uncertainty produces +/-0.033% uncertainty on the differential.

### Where Temperature Data Comes From

| Era | Source | Notes |
|-----|--------|-------|
| Pre-deployment (2024) | Teslameter probe only | Reads ~0.8 C higher than estimated ambient |
| Tunnel measurements (2025) | Teslameter probe | Tunnel temps 24-28 C |
| C2 April 2026 | Teslameter probe | Lab: 20.9-29.5 C (8.6 C swing) |
| C2 June 2026 | Teslameter probe + Arduino AM2302 | First dual-sensor data |

The Arduino was not available during Campaign 1, so all C1 temperature
corrections rely on the Teslameter probe. The cross-calibration between
sensors (see `temp_sensor_comparison.py`) is a priority for improving
future measurements.


---

## D. The Intra-Plate Differential

### The Problem: Gain Drift

The Helmholtz coil + fluxmeter system drifts by 0.5-0.7% between measurement
sessions. This is a multiplicative effect: every reading in a given session is
scaled by the same gain factor G.

If the gain on the day you took the baseline was G_pre = 1.003, and the gain on
the day you took the post-deployment measurement was G_post = 0.997, then every
magnet appears to have changed by about (0.997 - 1.003)/1.003 = -0.6%, even if
nothing physical happened. This is much larger than our ~0.2% signal.

### The Solution: Measure 4 Materials Together

Each Y-plate carries one magnet of each of the 4 grades. All 4 are measured in
the same session, typically within ~2 minutes of each other. The percentage
change for each magnet is:

```
Delta_i = (G_post * H_i_post - G_pre * H_i_pre) / (G_pre * H_i_pre) * 100%
```

where G_post and G_pre are the (unknown) session gain factors. When we take the
difference between the NdFeB average and the SmCo average:

```
delta = (Delta_N42EH + Delta_N52SH)/2 - (Delta_SmCo33H + Delta_SmCo35)/2
```

The gain factors cancel to first order because:

1. All 4 magnets in the baseline share the same G_pre
2. All 4 magnets in the post-deployment share the same G_post
3. The gain affects all readings as a common multiplicative factor
4. The difference removes the common-mode shift

This is why we call it the "gain-immune" or "intra-plate" differential. It
removes the +/-0.124% gain systematic entirely, improving precision by a factor
of ~4.4.

### Worked Example

Suppose Y-17 has these readings (temperature-corrected to 20 C):

**Baseline (Nov 2024):**
| Slot | Material | Baseline mWC |
|------|----------|-------------|
| 1 | N42EH | 0.9235 |
| 2 | SmCo33H | 1.0345 |
| 3 | N52SH | 0.9812 |
| 4 | SmCo35 | 1.0756 |

**Post-deployment (Jan 2026):**
| Slot | Material | Latest mWC |
|------|----------|-----------|
| 1 | N42EH | 0.9212 |
| 2 | SmCo33H | 1.0346 |
| 3 | N52SH | 0.9797 |
| 4 | SmCo35 | 1.0752 |

Percentage changes:
```
N42EH:   (0.9212 - 0.9235) / 0.9235 * 100 = -0.249%
SmCo33H: (1.0346 - 1.0345) / 1.0345 * 100 = +0.010%
N52SH:   (0.9797 - 0.9812) / 0.9812 * 100 = -0.153%
SmCo35:  (1.0752 - 1.0756) / 1.0756 * 100 = -0.037%
```

Differential:
```
NdFeB mean: (-0.249 + -0.153) / 2 = -0.201%
SmCo mean:  (+0.010 + -0.037) / 2 = -0.014%
Differential: -0.201 - (-0.014) = -0.187%
```

This plate shows NdFeB degraded ~0.19% more than SmCo. We compute this for
all 30 tunnel plates and take the fleet mean.

### Why This Works Even With Gain Drift

Imagine the gain was 0.5% high during the baseline and 0.3% low during the
post-deployment measurement. Both NdFeB and SmCo readings shift by the same
~0.8% (the difference in gains). When you subtract SmCo from NdFeB, the 0.8%
cancels. The only thing that survives is the real physical difference between
the materials.

**Key requirement:** All 4 slots must be measured in the same session, which
our protocol ensures. If you accidentally mix slots from different sessions
on the same plate, the differential is corrupted.


---

## E. Gain Systematic Quantification

### How We Measured the Gain Drift

We had 5 lab measurement sessions (April-June 2025) where every lab plate was
measured multiple times, compared against a pre-deployment baseline taken in
November 2024. Since lab plates were never exposed to tunnel radiation, any
variation between these sessions and the baseline is purely instrumental
(gain drift + noise).

### The Half-Range Method

For each magnet sample across the 5 sessions:

1. Compute the percent change between each session and the mean baseline
2. Find the maximum and minimum percent change across sessions
3. The half-range = (max - min) / 2

Then average over all samples to get the fleet-wide gain systematic.

### Cleaned vs Uncleaned

Two known outlier samples (Y-34-4 and Y-40-4) showed >3% variations due to
suspected baseline measurement errors. Including them inflates the systematic:

| Version | Gain systematic | Outlier handling |
|---------|----------------|------------------|
| **Cleaned** | +/-0.124% | Y-34-4 and Y-40-4 excluded |
| Uncleaned | +/-0.248% | All samples included |

We report the cleaned value (+/-0.124%) as the primary gain systematic, with
the uncleaned value as a conservative alternative.

### Impact on Results

| Measurement type | Gain systematic | Why |
|-----------------|----------------|-----|
| Individual material | +/-0.124% | Full gain drift affects absolute readings |
| Intra-plate differential | 0 (cancels) | Same gain for all 4 slots on one plate |

This is why the differential is so powerful: it turns a +/-0.124% systematic
into exactly zero.


---

## F. Within-Session Drift

### The Question

We established that session-to-session gain drift cancels in the intra-plate
differential. But what about drift WITHIN a session? If the Helmholtz coil
gain drifts while you are measuring a single plate's 4 slots (over ~2 minutes),
this could contaminate the differential.

### Analysis 1: Slot Timing

From second-precision timestamps in each data file, we measured the time
between the first and last slot measurement for every plate:

- **Median gap:** 102 seconds (1.70 minutes)
- **95th percentile:** 161 seconds (2.69 minutes)
- **Worst case:** Y-6 on January 8, 6.6 minutes (only 3 valid slots)

At a hypothetical drift rate of 1%/hour:
```
Drift in 102 sec = 1%/hr * (102/3600) hr = 0.028%
```

But the drift would be common-mode across slots (same direction), so the
residual on the NdFeB-SmCo differential would be even smaller (the drift
is partially randomized by the slot order on each plate).

### Analysis 2: Per-Session Spearman Correlation

For each of the 7 tunnel sessions with 8+ plates, we computed the Spearman
rank correlation between each plate's measurement timestamp and its intra-plate
differential:

| Session | N plates | Session span | rho | p-value | Sign |
|---------|----------|-------------|-----|---------|------|
| Jul 17 2025 | 15 | 200 min | +0.189 | 0.499 | + |
| Jul 30 2025 | 15 | 202 min | +0.496 | 0.060 | + |
| Aug 27 2025 | 30 | 396 min | -0.111 | 0.559 | - |
| Oct 21 2025 | 15 | 178 min | -0.018 | 0.950 | - |
| Oct 23 2025 | 10 | 159 min | -0.418 | 0.229 | - |
| Jan 08 2026 | 15 | 208 min | -0.086 | 0.761 | - |
| Jan 12 2026 | 15 | 184 min | +0.475 | 0.074 | + |

**Key observation:** No session reaches p < 0.05. The sign of the correlation
flips between sessions (3 positive, 4 negative; binomial p = 1.000). If there
were a real drift effect, the sign would be consistent.

### Analysis 3: Pooled Across All Sessions

Combining all 115 plates with normalized session time:

- Spearman rho = 0.146, p = 0.119
- Linear slope = 0.18%/session (R^2 = 0.0015, p = 0.68)
- Early-vs-late third: 0.27% difference, t-test p = 0.42

**None of these reach statistical significance.**

### Analysis 4: Y-14 Calibration Plate

Y-14 was measured repeatedly across a 10-hour span (09:00 to 19:00) on
April 20, 2026, with a 7 C temperature swing:

- Raw differential range: 0.14% (very stable, consistent with gain cancellation)
- Corrected differential range: 0.56% (amplified by NdFeB-SmCo alpha mismatch)

The corrected range is larger because temperature correction uses different
alpha values for NdFeB vs SmCo, so temperature fluctuations get "uncorrected"
differently. Over the extreme 7 C swing, this produces 0.066%/C * 7 = 0.46%
variation. This is not a gain drift effect; it is an expected consequence of
applying material-specific temperature corrections.

### Confounding Factor

Measurement order correlates with physical position along the beamline
(the operator walks from one location to the next). Position correlates with
radiation dose. So a non-zero correlation could reflect real dose-dependent
degradation, not drift. The sign inconsistency across sessions rules out drift
(which would always have the same sign) and is consistent with this position
confound.

### Verdict

No evidence of within-session drift affecting the intra-plate differential.
Pooled |rho| < 0.15, p > 0.1, no sign consistency across sessions. The error
budget entry for gain drift on the differential is zero.

**Script:** `Cleanup_Claude/within_session_drift.py`
**Output:** `Cleanup_Claude/Within_Session_Drift/WSD1-WSD4` plots


---

## G. Calibration Plates

### Purpose

Calibration plates are lab Y-plates measured multiple times per session to
track instrument stability and provide a real-time benchmark.

### Y-2: Campaign 1 Calibration Plate

Y-2 was designated as the C1 calibration plate. It was NOT measured for
dosimetry (no dosimeter was attached). It was measured alongside tunnel plates
to track session-to-session instrument behavior.

### Y-14: Campaign 2 Calibration Plate

Y-14 is a lab plate used as the C2 calibration plate. It is measured at the
start and end of each C2 session, and sometimes multiple times during a session.

**April 20, 2026 data (3 readings):**
- Corrected std per slot: 0.06-0.27%
- Demonstrates same-day repeatability

**June 2-3, 2026 data (5 readings per slot):**
- Corrected std per slot: 0.10-0.15%
- 8 total readings per slot (3 April + 5 June)
- Demonstrates multi-session repeatability at the 0.1-0.15% level

### How to Use Calibration Data

If Y-14's differential shifts systematically across the day, it indicates
instrument drift. If it stays flat (as observed: 0.14% raw range over 10 hours),
the instrument is stable enough for the differential measurement.

The calibration plate's variability (0.10-0.15% corrected std) sets a floor on
how precisely we can measure any single sample's differential in a single
session.


---

## H. Baseline Temperature

### The Problem

Before the Teslameter was consistently co-located with the Helmholtz
measurements, baseline temperatures were uncertain. The pre-deployment
measurements (September-November 2024) used the Teslameter probe, which reads
about 0.8 C higher than the estimated ambient temperature. This offset could
reflect probe self-heating, or it could indicate that the sample surface was
genuinely warmer than the room air (the probe is in thermal contact with the
magnet).

### The v1/v2/v3 Progression

Our temperature correction evolved through three versions as we understood the
temperature data better:

**Version 1 (v1): Raw probe temperatures**
- Used Teslameter temperatures as-is (24.6-26.7 C)
- Result: differential = -0.266% +/- 0.028% (9.6 sigma)
- Problem: Probe biased ~0.8 C high, overcorrects NdFeB more than SmCo

**Version 2 (v2): Blanket 23 C correction**
- Assumed all baselines were at 23 C
- Result: differential = -0.134% +/- 0.028% (4.9 sigma)
- Problem: SmCo33H anomalously positive (+0.083%, 2.7 sigma)

**Version 3 (v3, current): Per-date calibrated estimates**
- Used same-day Teslameter H-plate readings to calibrate Y-plate probe bias
- Baseline temperatures per session estimated at 23.8-25.8 C
- Result: differential = -0.208% +/- 0.028% (7.6 sigma)
- SmCo anomaly resolved; SmCo33H now +0.037% (1.2 sigma, consistent with zero)

### The +/-0.5 C Uncertainty

Our best estimate of the baseline temperature uncertainty is +/-0.5 C, based on:

1. Two same-day Y-H measurement cross-checks showing +0.77 and +0.87 C probe
   bias (mean +0.82 C, spread ~0.1 C)
2. Day-to-day lab temperature variation of ~3 C across November 2024
3. Per-date corrections where direct H-plate readings exist

Impact on the differential:
```
0.066%/C * 0.5 C = 0.033%
```

This +/-0.033% is the single largest systematic in the error budget.

### Robustness: Temperature Scan

Even scanning the assumed baseline temperature over its full plausible range
(23-25 C), the differential signal never drops below 4.9 sigma:

| Assumed baseline T | Differential | Significance |
|-------------------|-------------|-------------|
| 23.0 C (v2 blanket) | -0.134% | 4.9 sigma |
| 24.0 C | -0.199% | 7.2 sigma |
| ~24.1 C (v3 effective) | -0.208% | 7.6 sigma |
| 25.0 C | -0.264% | 9.6 sigma |

Note: v1 used raw per-reading probe temperatures (24.6-26.7 C across sessions),
not a single blanket value. Its result (-0.266%, 9.6 sigma) is close to but
not identical to the 25.0 C scan row because the per-reading approach weights
sessions differently than a blanket temperature.

The signal is robust against any reasonable temperature assumption.

### What the New Arduino Sensor Changes

The AM2302 provides an independent ambient air temperature measurement at the
time of each Helmholtz reading. Having two independent temperature data streams
(Arduino ambient + Teslameter probe) is strictly better than having one, because:

1. If both sensors agree, confidence in the temperature is high.
2. If they disagree, the disagreement itself is diagnostic (e.g., the sample
   may not have equilibrated to room temperature).

**Open question:** The temperature correction formula needs the sample
temperature, not the air temperature. The Teslameter probe, being in contact
with the sample, may be closer to the truth when the sample and air temperatures
differ (e.g., early morning when samples are still cool from overnight). The
Arduino, being an ambient air sensor, could be biased by drafts, laptop fans,
HVAC flow, or other local air currents. Conversely, the Teslameter probe may
have a self-heating bias. Determining which sensor (or what combination) gives
the most accurate temperature for the correction is a primary goal of the
summer cross-calibration campaign. Do not assume either sensor is "better"
until this work is complete.


---

## I. Teslameter Positioning Noise

### The Problem

The Teslameter measures the magnetic field at a single point on the magnet
surface. If the magnet sits slightly differently in the 3D-printed rig each
time you insert it, the probe location relative to the magnet changes, and
the field reading changes. This is "positioning noise."

### Per-Face Precision

From Campaign 1 data (repeated measurements of the same samples):

| Face | Standard deviation | Notes |
|------|-------------------|-------|
| **Top** | 0.14 - 0.29% | Best precision; least sensitive to alignment |
| **Front** | 0.57 - 0.91% | Moderate; field gradient steeper |
| **Side** | 0.90 - 1.90% | Worst; highest field gradient |

**Why top is best:** The top face has the flattest field gradient (the field
changes slowly with position), so a 0.1 mm shift produces less change in the
reading.

### H-Plate First-Tunnel Bias

The first time H-plates were measured in the tunnel (July 17, 2025), a
systematic bias appeared:

- 62% of front-face readings were >2% low compared to subsequent measurements
- 61% of side-face readings were >2% low
- Top face was unaffected

This is consistent with a different rig setup or calibration on the first
tunnel trip. It does not affect the Helmholtz results (which do not use the
Teslameter for demagnetization measurement).

### Impact on Helmholtz Results

The positioning noise does NOT affect Helmholtz readings (the Helmholtz
measurement integrates over the full sample volume and is position-independent).
The Teslameter is used only for temperature in the Helmholtz analysis pipeline.

### Impact on the Teslameter as an Independent Science Measurement

This is where positioning noise matters enormously. If the Teslameter noise can
be controlled (especially on the top face, where it is already 0.14-0.29%),
then Teslameter data becomes a primary science measurement in its own right,
not just a cross-check. The scientific value of showing both:

- **Integrated moment loss** (Helmholtz, volume-averaged) AND
- **Spatially-resolved point-field loss** (Teslameter, per-face, per-axis)

is much greater than either alone. A paper that demonstrates consistent
demagnetization signatures across two independent measurement techniques, on
multiple sample geometries (Y-plates, H-plates, A-samples), is qualitatively
stronger than Helmholtz-only results.

For H-plates in particular, the Teslameter measures field in a Halbach-like
configuration, which is the actual geometry relevant to FFA magnets. Showing
point-field degradation in Halbach geometry directly addresses the design
question.

### Improvement Opportunity

The 3D-printed rigs have inherent backlash and positioning tolerance. A machined
metal jig for top-face measurements could potentially reduce the 0.14-0.29%
noise floor. This is a high-priority target: getting top-face noise below ~0.15%
would make the Teslameter precise enough to independently detect the ~0.2%
demagnetization signal, transforming it from a noisy cross-check into a
publishable primary measurement.


---

## J. Statistical Methods

### Basic Statistics

**Mean:** The average of N values.
```
x_bar = (1/N) * sum(x_i)
```

**Standard deviation (sample):** A measure of spread. We use ddof=1 (Bessel's
correction) because we are estimating from a sample:
```
s = sqrt( (1/(N-1)) * sum( (x_i - x_bar)^2 ) )
```

In Python: `np.std(data, ddof=1)`

**Standard error of the mean (SEM):** How precisely we know the mean:
```
SEM = s / sqrt(N)
```

With 30 tunnel plates and std ~0.15%, the SEM is 0.15/sqrt(30) = 0.028%.

### Percentage Change Formula

For each sample:
```
pct_change = (latest_corrected - baseline_mean_corrected) / baseline_mean_corrected * 100
```

where "corrected" means temperature-corrected to 20 C.

### Per-Plate Differential

For each Y-plate with slots assigned to materials:
```
delta = mean(pct_change for NdFeB slots) - mean(pct_change for SmCo slots)
```

The fleet differential is the mean of delta across all tunnel plates.

### Sigma Significance

How many standard errors the result is from zero:
```
sigma = |result| / uncertainty
```

For example:
```
differential = -0.208%
SEM = 0.028%
sigma = 0.208 / 0.028 = 7.4  (approximately 7.6 with exact numbers)
```

Rough guide:
- 1 sigma: 68% confidence, not significant
- 2 sigma: 95% confidence, suggestive
- 3 sigma: 99.7% confidence, evidence
- 5 sigma: 1 in 3.5 million chance of noise, discovery-level

Our 7.6 sigma is extremely significant statistically.

### Combined Significance (Quadrature)

When multiple independent uncertainties contribute, combine them in quadrature:
```
sigma_combined = sqrt(sigma_stat^2 + sigma_syst1^2 + sigma_syst2^2 + ...)
```

For our differential:
```
sigma_combined = sqrt(0.028^2 + 0.033^2 + 0.014^2) = 0.045%
combined_significance = 0.208 / 0.045 = 4.6 sigma
```

### When to Use Paired vs Absolute Tests

**Paired (preferred for Y-plates):** Each plate has its own NdFeB-SmCo
differential. Compare the distribution of these differentials to zero. This is
what we do for the headline result.

**Absolute (for individual materials):** Compare the mean percent change for
all N42EH samples to zero. This carries the full gain systematic.

**Unpaired (for tunnel vs lab):** Compare the mean differential from 30 tunnel
plates to the mean from 9 lab plates. Different plates, so unpaired. Combined
SEM = sqrt(SEM_tunnel^2 + SEM_lab^2).


---

## K. Outlier Handling

### Flagged Samples

Two Y-plate samples are excluded from all fleet calculations:

| Sample | Material | Issue |
|--------|----------|-------|
| Y-34-4 | N52SH | Shows +11.3% change as of June 2026 (physically implausible) |
| Y-40-4 | SmCo33H | Shows -6.1% change as of June 2026 (physically implausible) |

These are suspected baseline measurement errors (e.g., wrong magnet measured,
data entry mistake, or rig malfunction during baseline). The specific
percentages vary by campaign but are always far outside the physical range;
their changes are 10-50x larger than anything else in the dataset.

### Threshold Exclusion

The gain systematic analysis uses a 3.0% threshold: any sample showing >3%
change in the pre-deployment sessions is excluded from the gain calculation.
Only Y-34-4 and Y-40-4 exceed this threshold.

### SmCo "Positive" Changes

Some SmCo samples show small positive changes (+0.2 to +0.4%). These are
within the noise floor and are NOT treated as outliers:

- The SmCo distribution has mean near zero and std ~0.17%
- Positive tails up to ~0.4% are expected from Gaussian statistics
- On an absolute mWC scale, the largest excursion (+0.0043 mWC) is only
  1.5-2x the single-reading noise (~0.002-0.003 mWC)

### How Outlier Exclusion Affects Results

| Metric | With outliers | Without outliers |
|--------|--------------|-----------------|
| Fleet differential | -0.204% | -0.208% |
| Gain systematic | +/-0.248% | +/-0.124% |

The differential changes by only 0.004% when outliers are removed, showing
the result is not driven by a few extreme points.


---

## L. Error Budget Table

### For the Gain-Immune Intra-Plate Differential

This is our primary measurement, and its error budget is what matters most.

| Source | Magnitude | How estimated |
|--------|-----------|---------------|
| Statistical (SEM, 30 plates) | +/-0.028% | std/sqrt(N) from data |
| Baseline temperature (+/-0.5 C) | +/-0.033% | 0.066%/C x 0.5 C |
| Alpha uncertainty (+/-10%) | +/-0.014% | Propagated from manufacturer tolerance |
| Gain systematic | **0** | Cancels by construction (intra-plate) |
| **Combined (quadrature)** | **+/-0.045%** | sqrt(0.028^2 + 0.033^2 + 0.014^2) |

**Final result:** -0.208% +/- 0.028% (stat) +/- 0.036% (syst) = -0.208% +/- 0.045% (combined)

**Significance:** 7.6 sigma (stat only), 4.6 sigma (combined)

### For Individual Materials

When quoting a single material's mean change, the gain systematic does not cancel:

| Source | Differential | Individual material |
|--------|-------------|-------------------|
| Statistical (SEM) | +/-0.028% | +/-0.036% |
| Baseline temperature | +/-0.033% | +/-0.050% |
| Alpha uncertainty | +/-0.014% | +/-0.021% |
| Gain systematic | 0 | +/-0.124% |
| **Combined** | **+/-0.045%** | **+/-0.140%** |

For individual materials, the gain systematic (+/-0.124%) dominates the error
budget, making the combined uncertainty ~3x worse than for the differential.

### Visual Summary

```
Differential error budget:

Statistical  ||||||||||||||||||||||||||||| 0.028%
Temperature  |||||||||||||||||||||||||||||||||| 0.033%
Alpha        |||||||||||||| 0.014%
Gain         (cancels)
Combined     |||||||||||||||||||||||||||||||||||||||||||||| 0.045%

Individual material error budget:

Statistical  ||||||||||||||||||||||||||||||||||||| 0.036%
Temperature  |||||||||||||||||||||||||||||||||||||||||||||||||| 0.050%
Alpha        ||||||||||||||||||||| 0.021%
Gain         |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| 0.124%
Combined     |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| 0.140%
```


---

## M. Lab Controls Validation

### The Logic

If our measurement system introduces a material-dependent bias (e.g., if the
temperature correction formula is wrong, or if NdFeB and SmCo respond
differently to some instrumental effect), then the lab control plates should
show the same bias as the tunnel plates. They do not.

### Lab Results

9 lab Y-plates, never exposed to tunnel radiation:

| Group | NdFeB mean | SmCo mean | Differential | Significance |
|-------|-----------|----------|-------------|-------------|
| Lab | +0.014% +/- 0.025% | +0.020% +/- 0.018% | -0.007% +/- 0.038% | 0.2 sigma |

The lab differential is -0.007%, consistent with zero. This means our entire
analysis pipeline (temperature correction, percentage change calculation,
differential computation) does NOT produce a spurious NdFeB-SmCo difference.

### Tunnel vs Lab Comparison

| | NdFeB (%) | SmCo (%) | Differential (%) | Significance |
|---|----------|---------|-----------------|-------------|
| Tunnel (30 plates) | -0.212 +/- 0.026 | -0.004 +/- 0.022 | -0.208 +/- 0.028 | 7.6 sigma |
| Lab (9 plates) | +0.014 +/- 0.025 | +0.020 +/- 0.018 | -0.007 +/- 0.038 | 0.2 sigma |
| **Tunnel - Lab** | **-0.226 +/- 0.036** | **-0.024 +/- 0.029** | **-0.202 +/- 0.047** | **4.3 sigma** |

The tunnel-minus-lab excess of -0.202% +/- 0.047% is independently significant
at 4.3 sigma. This tells us:

1. The signal exists only in tunnel plates (exposed to radiation)
2. Lab plates (same materials, same pipeline, no radiation) show null
3. The measurement system is unbiased at the 0.04% level
4. Any artifact that affected all plates equally (gain, temperature, etc.)
   would appear in both tunnel and lab, and cancel in the difference

### Why 9 Lab Plates Is Enough

With 9 plates and a per-plate differential std of ~0.11%, the lab SEM is
0.11/sqrt(9) = 0.037%, giving us ~3x resolution on any systematic bias at
the 0.1% level. A null result at 0.038% SEM means any real lab effect is
smaller than ~0.08% (2 sigma upper bound).

### What This Rules Out

The lab null result rules out:
- Systematic bias in the temperature correction
- Material-dependent aging in the absence of radiation (at least at our
  measurement precision, over this timeframe)
- Helmholtz coil response depending on material type
- Any analysis pipeline bug that produces a NdFeB-SmCo difference


---

## Appendix: Key Scripts Reference

| Script | Location | Purpose |
|--------|----------|---------|
| `temperature_corrected_analysis.py` | `Cleanup_Claude/` | Core temperature correction and differential calculation |
| `gain_systematic_analysis.py` | `Cleanup_Claude/` | Gain systematic deep-dive |
| `within_session_drift.py` | `Cleanup_Claude/` | Within-session drift validation |
| `manager_summary_v3.py` | `Cleanup_Claude/` | Fleet statistical summaries |
| `campaign2_quality_check.py` | `2026_Data_Run/` | C2 data quality and parsing |
| `c2_june_analysis.py` | `2026_Data_Run/` | June 2-3 analysis with temp data |
| `temp_sensor_comparison.py` | `Measurement_Improvement/` | Arduino vs Teslameter cross-calibration |
| `verify_results.py` | `Data_Package/` | 21-check standalone verification |

## Appendix: Glossary

| Term | Definition |
|------|-----------|
| **Baseline** | Pre-deployment measurement(s) of a sample's magnetic moment |
| **Campaign 1 (C1)** | Initial deployment, Jan 2025 to Jan 2026 |
| **Campaign 2 (C2)** | Ongoing deployment, started Apr 2026 |
| **Differential** | NdFeB mean % change minus SmCo mean % change (per plate) |
| **Fleet** | All 30 tunnel Y-plates collectively |
| **Gain** | Multiplicative calibration factor of the Helmholtz system |
| **mWC** | milliWeber-centimeter, unit of magnetic moment |
| **mT** | milliTesla, unit of magnetic field strength |
| **SEM** | Standard Error of the Mean = std / sqrt(N) |
| **Sentinel (1337)** | Missing data marker |
| **T_ref** | Reference temperature, 20.0 C |
| **Y-plate** | Primary sample holder with 4 randomized material slots |
