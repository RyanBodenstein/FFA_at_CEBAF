# Signal-to-Noise Improvement Recommendations

## LDRD FFA@CEBAF Permanent Magnet Study
**Last updated:** 2026-06-04

---

## 1. Current Noise Sources (Ranked by Impact)

### 1.1 Teslameter Positioning Noise (0.14-1.90%)

**Impact:** Dominant noise source for Teslameter field measurements.

The 3D-printed sample rigs allow ~0.1-0.3 mm of play when a magnet is inserted.
Because the Hall probe measures field at a single point, this positional
uncertainty translates directly to measurement scatter:

| Face | Std (%) | Typical reading (mT) | 1-sigma noise (mT) |
|------|---------|---------------------|-------------------|
| Top | 0.14 - 0.29 | ~150-180 | ~0.2 - 0.5 |
| Front | 0.57 - 0.91 | ~30-50 | ~0.2 - 0.5 |
| Side | 0.90 - 1.90 | ~10-30 | ~0.1 - 0.6 |

The top face has the flattest field gradient, so positioning errors matter least
there. Front and side faces sit in steeper gradient regions.

**Current status:** This noise does not affect Helmholtz demagnetization results
(the Helmholtz integrates over the full sample volume). However, the Teslameter
is NOT merely a secondary cross-check: if positioning noise can be controlled,
Teslameter data becomes an independent primary measurement of spatially-resolved
point-field degradation. Showing both integrated moment loss (Helmholtz) and
point-field loss (Teslameter) on the same samples, across Y-plates, H-plates,
and A-samples, is the path to high-impact publications.

**Why this matters for H-plates especially:** H-plates are Halbach-geometry
assemblies that directly represent FFA magnet configurations. The Teslameter
measures field at specific locations on the Halbach assembly; demonstrating
degradation in the actual field geometry of interest is far more compelling to
accelerator designers than volume-averaged moment loss alone.

**Quantitative target:** Reduce top-face noise to <0.15%, which would make the
Teslameter precise enough to independently detect the ~0.2% demagnetization
signal. At <0.10%, it would be comparable to Helmholtz single-session
repeatability.

### 1.2 Temperature Uncertainty (up to 3.4 C sensor disagreement)

**Impact:** 0.066%/C on the NdFeB-SmCo differential; up to 0.033% at current
+/-0.5 C uncertainty level.

June 2-3, 2026 data (492 matched pairs from `temp_sensor_comparison.py`) shows
a systematic offset between the Teslameter probe and Arduino AM2302 readings:

Fleet statistics (Teslameter minus Arduino):
- Mean: **+1.00 C**
- Std: 0.74 C
- Range: -1.01 to +3.43 C

Temperature-dependent pattern:
- Low temp (<24 C, N=17): mean offset = **+1.87 C**
- High temp (>=27 C, N=401): mean offset = **+0.86 C**
- The offset shrinks as both sensors converge at higher temperatures.

Y-14 calibration plate examples:

| Measurement | Arduino (C) | Teslameter (C) | Diff (C) |
|------------|------------|----------------|----------|
| Jun 1 10:43 | 21.1 | 21.6 | +0.5 |
| Jun 2 09:04 | 20.3 | 22.7 | +2.4 |
| Jun 3 07:27 | 22.6 | 24.0 | +1.4 |
| Jun 3 08:32 | 27.4 | 27.9 | +0.5 |
| Jun 3 09:25 | 28.5 | 28.3 | -0.2 |

**Multiple possible explanations** (not yet resolved):
- Probe self-heating (Teslameter biased high)
- Thermal lag: samples may genuinely be warmer than the air early in the day
  (residual heat from previous day, slow equilibration), meaning the Teslameter
  probe, being in contact with the sample, is closer to the true sample
  temperature
- Arduino sensitivity to local air currents (cross-breezes, laptop fans, HVAC)
  could bias the Arduino reading away from the actual temperature near the
  sample

**Which sensor is "right" for the temperature correction is an open question.**
The correction formula needs the *sample* temperature, not necessarily the air
temperature. The Teslameter probe, being in thermal contact with the sample
surface, may actually be the better proxy in some conditions. The summer
cross-calibration study is designed to disentangle these effects.

Linear fit: T_tesla = 0.707 * T_arduino + 9.05 (fit residual std = 0.62 C).

**Quantitative target:** Understand the source of the disagreement well enough
to select (or combine) sensors with confidence. Target: reduce temperature
uncertainty to <0.3 C, which would bring the temperature systematic on the
differential from +/-0.033% to +/-0.020%.

### 1.3 Session-to-Session Gain Drift (0.5-0.7%)

**Impact:** +/-0.124% systematic on individual material measurements. Cancels
to zero in the intra-plate differential.

Measured from 5 pre-deployment sessions. The drift is a multiplicative shift
in the Helmholtz system output (coil parameter changes, cable connections,
electronics temperature). Nov 2024 sessions read ~0.7% higher than April-June
2025 sessions.

**Current status:** Fully handled by the intra-plate differential for Y-plates.
NOT handled for H-plates (no intra-plate differential possible) or absolute
measurements.

**Quantitative target:** Track and correct gain within sessions using a
reference magnet, reducing individual-material systematic to <0.05%.

### 1.4 First-Tunnel Bias for H-Plates (62% of front readings >2% low)

**Impact:** Corrupts the first tunnel measurement for H-plate front and side
faces, forcing use of only the second and subsequent measurements.

The first time H-plates were measured in the tunnel (July 17, 2025), a
systematic low bias appeared on front (62%) and side (61%) faces. Top face
was unaffected. Likely caused by different rig setup or insufficient
equilibration on the first trip.

**Current status:** Mitigated by using only post-first-tunnel data for H-plates.
Reduced effective baseline for some H-plates.

**Quantitative target:** Identify root cause (rig setup procedure? thermal
equilibration?) and eliminate for C2.

### 1.5 Single-Session Baselines

**Impact:** Most tunnel plates have only 1 qualifying pre-deployment session
with co-located Teslameter temperature. Baseline noise is not averaged down.

With a single baseline, the baseline uncertainty is the single-session
repeatability (~0.2-0.3% for Helmholtz). With N=5 independent sessions, this
drops to ~0.1-0.13%. The improvement is roughly 1/sqrt(N).

Example: Y-10 had 2 qualifying baseline sessions. Its per-material scatter
dropped by a factor of ~20 compared to single-baseline plates. (This is
partially because the two baselines happened to average out a measurement
fluke, but it demonstrates the principle.)

**Quantitative target:** 5-10 independent baseline sessions per lab plate.


---

## 2. Recommended Improvements

### 2.1 Multi-Insertion Averaging (Teslameter)

**What:** For each Teslameter measurement, remove the sample from the rig,
re-insert it, and re-measure. Repeat 3x per face. Report the mean +/- std.

**Why:** Directly measures the rig positioning tolerance for each individual
sample, in real time. The mean of 3 insertions has sqrt(3) = 1.7x better
precision than a single insertion. More importantly, the per-sample std tells
you whether that specific sample has good or poor rig fit.

**Protocol:**
1. Insert sample into rig, measure top face (Bx, By, Bz, T)
2. Remove sample completely from rig
3. Re-insert sample, measure top face again
4. Repeat once more (3 total insertions)
5. Record all 3 readings and compute mean, std
6. Repeat for front and side if desired

**Expected improvement:** Top-face std from 0.14-0.29% (single insertion) to
0.08-0.17% (mean of 3). Samples with std >0.3% can be flagged for rig
inspection.

**Time cost:** ~2 extra minutes per sample per face. For 120 Y-plate slots,
this adds ~4 hours to a full Teslameter survey if doing top face only.

### 2.2 Top-Face Priority

**What:** For routine trend tracking, measure only the top face on the
Teslameter. Reserve front and side for dedicated characterization campaigns.

**Why:** Top face is 3-6x more precise than other faces. For tracking
demagnetization trends over time, top-face-only provides adequate precision
with ~1/3 the measurement time.

**When to do all 3 faces:** Initial characterization, dedicated repeatability
studies, and whenever a result looks anomalous on top face.

### 2.3 Dual Temperature Sensors

**What:** Record both Arduino AM2302 and Teslameter temperatures for every
measurement. Neither is designated as "primary" until the cross-calibration
study determines which (or what combination) best represents the sample
temperature for the correction formula.

**Why:** The two sensors measure different things:
- **Arduino AM2302:** Ambient air temperature near the Helmholtz setup. May be
  influenced by cross-breezes, laptop fans, HVAC airflow, and distance from
  the sample.
- **Teslameter probe:** Temperature at the probe junction, in contact with (or
  very near) the magnet surface. May include self-heating bias, but is
  physically closer to the sample whose temperature we actually need.

Having both sensors lets us: (a) quantify their disagreement, (b) study which
correlates better with Helmholtz reading residuals, and (c) eventually select
or combine them for optimal temperature correction.

**Protocol:**
1. Arduino sensor runs continuously, logging to `*_helmholtzTemp.dat` files
2. Arduino reading taken at the moment of Helmholtz measurement
3. Teslameter temperature recorded when sample is in Teslameter rig (may be
   minutes later)
4. Both temperatures recorded in the data file for each sample

**Cross-calibration script:** `Measurement_Improvement/temp_sensor_comparison.py`
uses the June 2-3 data to characterize the Arduino-Teslameter offset pattern.

**Expected improvement:** Once the relationship is understood, the temperature
systematic could drop from +/-0.033% toward +/-0.020% on the differential. But
this depends on understanding which sensor better represents the sample
temperature, not simply assuming one is correct.

### 2.4 Environmental Conditioning

**What:** Let samples equilibrate to room temperature before measurement.
Record the wait time. Use Arduino humidity data to flag condensation risk.

**Why:** If a sample is cooler or warmer than the room, the Teslameter
temperature (which reads the magnet surface) will not match the Arduino
temperature (which reads the air). Equilibration eliminates this discrepancy.

**Protocol:**
1. Place samples on bench in measurement room at least 30 minutes before
   starting
2. Record the time the samples were moved and the time measurement begins
3. Note Arduino humidity: if >60% and sample is cold, condensation risk exists
   (avoid measurement until humidity drops or sample warms)
4. For high-precision measurements, wait 1 hour and verify Arduino-Teslameter
   agreement is within 0.5 C

### 2.5 Multi-Session Baselines

**What:** Measure every lab plate in 5-10 independent sessions over 5 weeks.
Use the mean as the baseline.

**Why:** Noise reduces as 1/sqrt(N). With N=10 sessions, the baseline noise
contribution drops from ~0.2-0.3% (single session) to ~0.06-0.10%.

**Quantitative target:**
- Current lab SEM: 0.038% (9 plates, mostly single-session baselines)
- Target lab SEM: ~0.012% (9 plates, 10-session baselines)
- This would make the lab null result definitive at the 0.01% level

**Cadence:** 2 sessions per week for 5 weeks. Each session measures all 9
lab Y-plates (36 slots), all 48 lab H-plates (192 slots), and lab A-samples.
Arduino sensor on for all Helmholtz measurements.

### 2.6 Rig Improvement Assessment

**What:** Directly measure rig backlash and positioning tolerance using a
reference magnet. If >0.3%, consider designing a machined aluminum jig for
top-face measurements.

**Protocol:**
1. Select 1 reference magnet (e.g., a spare N42EH slug)
2. Insert into rig, measure top face. Do NOT remove.
3. Gently push sample to one extreme of rig play, measure again
4. Push to opposite extreme, measure again
5. Repeat 10x, characterize the range of readings

**Decision threshold:** If rig backlash alone accounts for >0.3% variation,
a machined jig is justified. A simple aluminum V-groove or flat-plate holder
with set screw could reduce positioning noise to <0.05%.


---

## 3. Helmholtz Improvement Ideas

### 3.1 Multiple Insertions per Helmholtz Measurement

**What:** Remove sample from Helmholtz coil, re-insert, re-measure. Repeat
3-5 times per sample.

**Why:** Helmholtz readings are position-independent "by design," but small
variations in sample centering may still contribute. Multiple insertions
quantify the single-insertion reproducibility directly.

**Expected result:** We expect the single-insertion std to be 0.02-0.05%
(much better than Teslameter), confirming that Helmholtz positioning noise
is negligible compared to gain drift.

**Time cost:** ~1 extra minute per insertion. For 120 samples x 3 extra
insertions = ~6 hours additional. Best done with a subset first (Y-14 + 2
other lab plates, 12 slots total, ~36 extra insertions in 30 minutes).

### 3.2 Same-Day Reference Magnet

**What:** Measure a designated reference magnet (always the same physical
sample) at the start, middle, and end of every session. Use it to track
within-session gain drift.

**Why:** Currently, within-session drift is an upper bound (we showed it is
consistent with zero, but did not directly measure it). A reference magnet
gives a direct, real-time gain monitor.

**Protocol:**
1. Designate one lab magnet as the session reference (e.g., Y-14 slot 1,
   or a standalone slug with known properties)
2. Measure it first thing, after every 10 plates, and last thing
3. Plot the reference readings vs time within the session
4. If drift is detected, apply a linear correction to all other readings

**Expected benefit:** Transforms the gain systematic from a session-wide
unknown into a measured, correctable quantity. Could reduce individual-material
systematic from +/-0.124% to <+/-0.05%.

### 3.3 Synchronous Temperature at Helmholtz Measurement

**What:** The Arduino AM2302 records temperature at the moment of each
Helmholtz measurement, while the Teslameter temperature is recorded 1-5
minutes later (when the sample is moved to the Teslameter rig). Having a
temperature reading synchronous with the Helmholtz measurement is valuable
regardless of which sensor ultimately proves more accurate.

**Why:** The Teslameter reading is time-delayed relative to the Helmholtz
measurement, during which the room temperature may change. However, the Arduino
measures ambient air, not sample temperature; the Teslameter probe is in
contact with the sample. In a rapidly warming room, the Arduino may track the
air faster while the sample lags; in a stable room, the time delay matters less.

**Implementation:** The `*_helmholtzTemp.dat` files already contain per-sample
Arduino temperatures. The analysis pipeline should be updated to include both
temperature sources as columns, and the cross-calibration study should determine
which (or what weighted combination) produces smaller Helmholtz residuals.


---

## 4. Measurement Priority Matrix

| Improvement | Effort | Impact on differential | Impact on individual | Priority |
|------------|--------|----------------------|---------------------|----------|
| Multi-session baselines | High (5 weeks) | Moderate (stat only) | Large (stat + gain) | **1** |
| Dual temperature sensors | Low (already in place) | Moderate (if offset understood) | Moderate | **2** |
| Multi-insertion Teslameter | Medium (extra 4 hrs/survey) | None (Helmholtz-only) | **HIGH (enables dual-measurement publications)** | 3 |
| Multi-insertion Helmholtz | Low (30 min pilot) | Small (quantify floor) | Small | **4** |
| Reference magnet tracking | Low-Medium | None (diff. already 0) | Large (gain control) | **5** |
| Rig assessment | Low (1 hour) | None | **HIGH (gates Teslameter as science)** | 6 |
| Environmental conditioning | Low (protocol change) | Small (<0.01%) | Small | 7 |

**Note:** "Impact on differential" matters for the headline Y-plate science
result. "Impact on individual" matters for per-material tracking, H-plate
analysis, and the broader publication story. For high-tier publications, the
goal is to show consistent demagnetization signatures across BOTH measurement
techniques (integrated + point-field) and all three sample types (Y, H, A).
The Teslameter improvements are what unlock this.

---

## 5. Expected Outcomes

### With Full Implementation (End of Summer)

| Parameter | Current | Target | Method |
|-----------|---------|--------|--------|
| Lab Y-plate differential SEM | 0.038% | 0.012% | 10-session baselines |
| Temperature systematic | +/-0.033% | +/-0.020% | Dual-sensor cross-calibration |
| Helmholtz single-insertion std | Unknown | Measured (expect 0.02-0.05%) | Multi-insertion study |
| Teslameter top-face std | 0.14-0.29% | <0.15% (measured) | Multi-insertion + rig characterization |
| Individual material gain syst. | +/-0.124% | +/-0.05% | Reference magnet protocol |

### Impact on Science and Publications

**Near-term (Tech Note, IPAC-class):** With reduced lab SEM, the lab null
result becomes definitive, strengthening the existing C1 conclusion.

**High-impact (journal publication):** The transformative outcome is if
the Teslameter noise reduction succeeds. Currently:

- We have a strong Helmholtz result (integrated moment, gain-immune
  differential, 7.6 sigma) but only on Y-plates.
- H-plate Helmholtz data carries the full gain systematic (+/-0.124%) because
  H-plates have no intra-plate differential. The gain dominates and the
  results are noisy.
- Teslameter data is currently too noisy (0.14-1.90%) to independently
  confirm the ~0.2% signal.

If the summer improvements achieve <0.15% Teslameter top-face precision AND
multi-session baselines bring the gain systematic under control:

1. **Dual-measurement confirmation:** The same demagnetization signal seen in
   both integrated moment AND spatially-resolved point field, on the same
   samples. This is a qualitatively different level of evidence.
2. **H-plate Halbach results:** Degradation measured in the actual field
   geometry relevant to FFA magnets, using both techniques. This directly
   answers the design question that motivates the entire study.
3. **A-sample paired comparisons:** Field-vs-zero-field degradation in
   identical material pairs. Combined with both measurement techniques,
   this constrains the degradation mechanism.
4. **Per-face, per-axis spatial information:** Where on the magnet is the
   field lost? Is it uniform or concentrated? The Teslameter's 3-axis,
   3-face data provides this; the Helmholtz cannot.

The difference between "Y-plate Helmholtz differential" and "Y + H + A
samples, Helmholtz + Teslameter, with noise characterized and controlled"
is the difference between a solid technical note and a definitive journal
publication.
