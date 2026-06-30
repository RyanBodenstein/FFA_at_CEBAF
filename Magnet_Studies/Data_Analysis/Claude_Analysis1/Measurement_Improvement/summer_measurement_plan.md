# Summer Measurement Plan: Concrete Goals for 2026

## LDRD FFA@CEBAF Permanent Magnet Study
**Interns:** Moishe, Evelyn
**Duration:** ~10 weeks (June-August 2026)
**Last updated:** 2026-06-04

---

## Overview

This plan has two complementary goals:

1. **Improve measurement reliability:** Accumulate multi-session baselines,
   characterize temperature sensors, and quantify noise floors for both
   Helmholtz and Teslameter instruments.

2. **Enable dual-measurement publications:** Get the Teslameter precise
   enough to serve as an independent primary measurement, not just a
   cross-check. If we can show demagnetization in both integrated moment
   (Helmholtz) and spatially-resolved point field (Teslameter), across all
   three sample types (Y-plates, H-plates, A-samples), we are positioned
   for high-impact journal publications. H-plates are especially important
   because they directly represent Halbach/FFA magnet geometry.

The plan is organized into 6 priorities. All priorities can overlap; the
ordering reflects when each should start.

### Equipment Available

- Helmholtz coil + Fluxmeter Model 2130 (integrated magnetic moment, mWC)
- SENIS 3MH6-E Teslameter + Hall Probe Type C (3-axis field, mT)
- Arduino AM2302 temperature/humidity sensor (ambient temp + RH)
- 3D-printed Teslameter sample rigs (top, front, side faces)
- Lab Y-plates: Y-{8, 14, 27, 28, 29, 31, 33, 35, 37} (9 plates, 36 slots)
- Lab H-plates: 24 north + 24 south (48 plates, 192 slots)
- Lab A-samples: all lab A-sample pairs

### General Protocol (Every Session)

1. Power on Helmholtz and Teslameter. Allow 15+ minutes for thermal equilibration.
2. Start Arduino sensor logging.
3. Measure Y-14 calibration plate (all 4 slots, Helmholtz + Teslameter top).
4. Measure all scheduled samples.
5. Measure Y-14 again at end of session.
6. Record session notes: start/end times, any anomalies, room conditions.
7. Verify all data files saved and named correctly before shutdown.

---

## Priority 1: Lab Control Baseline Accumulation (Weeks 1-5)

### Goal

Measure every lab plate in 5-10 independent sessions to build a high-statistics
baseline that reduces per-plate noise as 1/sqrt(N).

### What to Measure

| Sample type | Count | Slots per plate | Total measurements per session |
|------------|-------|-----------------|-------------------------------|
| Lab Y-plates | 9 | 4 | 36 Helmholtz + 36 Teslameter (top) |
| Lab H-plates | 48 | 4 | 192 Helmholtz + 192 Teslameter (top) |
| Lab A-samples | All pairs | 2 per pair | ~96 Helmholtz + ~96 Teslameter |

**Instruments per sample:** Helmholtz (mWC) + Teslameter top face + Arduino temp.

### Cadence

~2 sessions per week for 5 weeks = 10 sessions.

Each session takes approximately:
- Y-plates: 9 plates x 4 slots x ~2 min = ~72 min
- H-plates: 48 plates x 4 slots x ~1.5 min = ~288 min (~5 hours)
- A-samples: ~96 pairs x ~1.5 min = ~144 min (~2.5 hours)
- Y-14 calibration: 2 x ~8 min = 16 min
- Total: ~8-9 hours per full session

**Recommendation:** Split into half-sessions if needed. Y-plates + Y-14 cal can
be a morning session (~1.5 hours). H-plates can be an afternoon session.
A-samples on alternating days.

**Important:** Do not neglect H-plates and A-samples in favor of Y-plates.
For the broader publication goals, H-plate and A-sample baselines are equally
critical. H-plates demonstrate degradation in Halbach (FFA-relevant) geometry;
A-samples provide paired field-vs-zero-field comparisons. Both need the same
multi-session baseline accumulation as Y-plates. The weekly schedule should
ensure all three sample types get equal attention.

### Statistical Target

With N=10 independent sessions per lab Y-plate:

| Metric | Current (N~1-2) | Target (N=10) | Improvement |
|--------|----------------|---------------|------------|
| Per-plate baseline std | ~0.2-0.3% | ~0.2-0.3% (unchanged) | - |
| Per-plate baseline SEM | ~0.2-0.3% | ~0.06-0.10% | 3-5x |
| Lab fleet differential SEM | 0.038% | ~0.012% | ~3x |

The lab null becomes definitive: if the lab differential is truly zero, we will
measure 0.000% +/- 0.012%, ruling out any hidden systematic >0.024% (2-sigma).

### Data Naming Convention

Follow existing convention: `{sample_id}_helmholtzTemp.dat` for Arduino data,
`{sample_id}.dat` for Helmholtz, `{sample_id}_{face}.dat` for Teslameter.

Organize by date: `2026_Data_Run/YYYY-MM-DD_Helmholtz/` and
`2026_Data_Run/YYYY-MM-DD_Teslameter/`.


---

## Priority 2: Temperature Cross-Calibration (Weeks 2-5)

### Goal

Characterize the systematic difference between the Arduino AM2302 ambient
sensor and the Teslameter probe temperature, as a function of temperature,
time of day, and humidity.

### Protocol

Measure Y-14 (calibration plate, all 4 slots) at multiple times throughout
the day for 5+ separate days:

| Time | Purpose |
|------|---------|
| Morning (07:00-08:00) | Cold start; largest expected sensor disagreement (sample may lag air) |
| Mid-morning (09:00-10:00) | Room warming up |
| Midday (12:00-13:00) | Near steady-state |
| Afternoon (15:00-16:00) | Warmest; sensors likely most equilibrated |

For each measurement:
1. Record Arduino temperature and humidity (from `*_helmholtzTemp.dat`)
2. Record Teslameter temperature (from `*_top.dat`)
3. Note time since power-on of instruments
4. Note time since samples were placed on bench (equilibration time)

### Days to Target

- At least 2 "cold start" days: arrive early, measure before room warms up
- At least 2 "hot" days: ambient >27 C (expected in July-August)
- At least 1 day with humidity >55% (if possible)
- At least 5 total days with 3+ measurements per day

### Deliverables

1. Characterization of the Arduino-Teslameter offset: is it constant, linear
   in temperature, or more complex? (Do NOT assume either sensor is ground truth.)
2. Assessment of which sensor (or combination) better predicts Helmholtz
   residuals after temperature correction.
3. Humidity effect: does humidity correlate with temperature disagreement?
4. Equilibration study: how long after placing samples on the bench do the
   two sensors converge? This constrains whether the offset is due to sample
   thermal lag vs sensor bias.
5. Draft recommendation: what temperature source should be used for the
   correction formula, and with what estimated uncertainty?

**Key caution:** The Arduino measures ambient air temperature, which can be
influenced by cross-breezes, laptop fans, HVAC airflow, and distance from
the sample. The Teslameter probe is in contact with the magnet surface, so
it may be closer to the actual sample temperature in some conditions. Do not
assume either is "correct" without evidence.

### Statistical Target

Understand the offset well enough to reduce temperature uncertainty to <0.3 C,
which would bring the temperature systematic on the differential from +/-0.033%
to +/-0.020%.


---

## Priority 3: Teslameter Repeatability Study (Weeks 3-7)

### Goal

Quantify the Teslameter positioning noise per face, per material, per sample,
using a remove-and-reinsert protocol.

### Sample Selection

8 representative samples spanning all three sample types and all four materials:

| # | Sample | Type | Material | Why |
|---|--------|------|----------|-----|
| 1 | Y-14-1 | Y-plate | (check assignment) | Calibration plate, well-characterized |
| 2 | Y-14-2 | Y-plate | (check assignment) | Same plate, different material |
| 3 | Y-14-3 | Y-plate | (check assignment) | Same plate, different material |
| 4 | Y-14-4 | Y-plate | (check assignment) | Same plate, different material |
| 5 | One lab Hn | H-plate (north) | Mixed | Different rig geometry from Y-plates |
| 6 | One lab Hs | H-plate (south) | Mixed | North vs south comparison |
| 7 | One A-sample pair | A-sample | NdFeB | Smallest sample, potentially worst positioning |
| 8 | One A-sample pair | A-sample | SmCo | Material comparison for A-samples |

Including H-plate and A-sample geometries is essential because the rig
positioning noise may differ by sample type (different rig, different magnet
shape, different field gradients). If we only characterize Y-plate noise, we
cannot make claims about Teslameter precision on H-plates or A-samples.

### Protocol (Per Sample, Per Day)

1. Insert sample into rig for top face measurement
2. Record Teslameter reading (Bx, By, Bz, T)
3. Remove sample completely from rig
4. Re-insert sample
5. Record reading again
6. Repeat steps 3-5 until you have 10 readings per face
7. Move to front face rig; repeat 10x
8. Move to side face rig; repeat 10x
9. Total: 30 readings per sample per day

### Schedule

Run on 3 different days (ideally different weeks) to test day-to-day
reproducibility.

Total: 8 samples x 3 faces x 10 insertions x 3 days = 720 readings.
Time estimate: ~10 min per sample per face per day, ~4 hours per day,
~12 hours total across 3 days.

### Analysis

For each sample/face combination:
- Mean, std, CV (coefficient of variation = std/mean * 100%)
- Within-day vs between-day variance (is day-to-day variation larger?)
- Compare to existing estimates (top 0.14-0.29%, front 0.57-0.91%, side
  0.90-1.90%)

### Decision Point

If top-face CV < 0.15%: current rig is adequate for top-face trend tracking.
If top-face CV > 0.30%: pursue machined jig (Priority 6 stretch goal).


---

## Priority 4: Helmholtz Repeatability Study (Weeks 5-8)

### Goal

Quantify the single-insertion reproducibility of the Helmholtz coil measurement.

### Samples

- Y-14 (calibration plate, all 4 slots)
- 2 additional lab Y-plates (e.g., Y-8, Y-27): 8 more slots
- Total: 12 slots

### Protocol (Per Session)

1. Measure all 12 slots normally (insert, record mWC, remove)
2. Re-measure all 12 slots (insert, record mWC, remove)
3. Repeat until each slot has 10 readings in the same session
4. Record Arduino temperature throughout (should be stable if room is
   equilibrated)
5. Total: 120 Helmholtz readings in a single session

### Time Estimate

~1 minute per insertion x 120 insertions = ~2 hours per session.
Do 2-3 sessions on different days.

### Analysis

For each slot:
- 10-reading mean, std, CV
- Compare to nominal instrument accuracy (0.05%)
- Check for systematic drift within the 10-reading sequence (does the reading
  drift up or down as the session progresses?)

### Expected Result

Single-insertion std of 0.02-0.05%. This would confirm that Helmholtz
positioning noise is negligible compared to gain drift (0.5-0.7%) and
statistical scatter (0.17-0.20%).


---

## Priority 5: Environmental Monitoring (Weeks 6-9)

### Goal

Characterize how room environment (temperature, humidity) varies during
measurement sessions and how it correlates with Helmholtz readings.

### Protocol

1. Arduino sensor logs continuously during all measurement sessions (it
   should already be doing this for Priority 1)
2. Additionally, run Arduino logging on 3-5 non-measurement days to capture
   baseline environmental patterns
3. Record HVAC status (on/off, set point) if accessible

### Analysis

- Temperature profile: typical daily range, rate of change, time-of-day pattern
- Humidity profile: range, correlation with temperature
- Helmholtz drift within sessions vs temperature change
- Is there a measurable correlation between Helmholtz reading and Arduino
  temperature beyond what the temperature correction formula predicts?

### Deliverable

Environmental characterization report with plots:
- Temperature vs time-of-day (5+ days overlaid)
- Humidity vs time-of-day
- Helmholtz residual (after temp correction) vs session temperature change
- Thermal equilibration timescale for samples (from Priority 2 data)


---

## Priority 6: Improved-Protocol Re-measurement (Weeks 8-10)

### Goal

If Priorities 1-4 are complete, re-measure all 30 tunnel Y-plates using the
improved protocol (multi-insertion Helmholtz, dual temperature sensors, Y-14
calibration at start and end).

### Protocol

For each tunnel Y-plate (4 slots):
1. Helmholtz: 3 insertions per slot, record all 3 readings
2. Arduino temperature recorded for each insertion
3. Teslameter top face: 3 insertions per slot
4. Y-14 measured at start and end of every batch of 5 plates

### Deliverable

"C2 improved" dataset: 120 tunnel Y-plate measurements with:
- Multi-insertion Helmholtz means and stds
- Dual temperature readings
- Y-14 calibration brackets
- Full Arduino environmental log

### Time Estimate

30 plates x 4 slots x 3 insertions x ~2 min = ~12 hours of Helmholtz.
Plus Teslameter: ~12 hours. Plus calibration: ~3 hours.
Total: ~27 hours, spread over ~4 days.


---

## Stretch Goals (If Time Permits)

### S1: Prototype Machined Teslameter Jig

If Priority 3 shows top-face CV > 0.30%, design and fabricate an aluminum
jig for top-face measurements. Requirements:
- Repeatable sample positioning to <0.05 mm
- Easy insertion/removal (no tools required during measurement)
- Compatible with Y-plate and H-plate sample dimensions

This is the single highest-leverage stretch goal: if the rig is the noise
bottleneck, fixing it unlocks the Teslameter as a primary science measurement.

### S2: Humidity-Field Investigation

With Arduino humidity data: is there a measurable correlation between relative
humidity and Helmholtz or Teslameter readings? Anecdotally, magnetic
measurements can be affected by condensation or air moisture, but this has
never been tested on our setup.

### S3: Tunnel H-Plate and A-Sample Re-measurement

Re-measure all tunnel H-plates and A-samples with the improved protocol
(multi-insertion, dual temp sensors). Combined with the lab baselines from
Priority 1 and the Teslameter noise characterization from Priority 3, this
creates a dataset suitable for dual-measurement (point + integrated)
publication on H-plate and A-sample degradation.


---

## Weekly Schedule Template

| Week | Priority 1 (Baselines) | Priority 2 (Temp Cal) | Priority 3 (Tesla Rep.) | Other |
|------|----------------------|---------------------|----------------------|-------|
| 1 | Sessions 1-2 (Y + Y-14 cal; learn protocol) | - | - | Training, setup |
| 2 | Sessions 3-4 (Y + H-plates) | Start temp cal | - | - |
| 3 | Sessions 5-6 (Y + H + A, full sessions) | Continue temp cal | Start repeatability | - |
| 4 | Sessions 7-8 (Y + H + A, full sessions) | Wrap up temp cal | Continue repeatability | - |
| 5 | Sessions 9-10 (Y + H + A, full sessions) | Final day if needed | Continue repeatability | Start P4 pilot |
| 6 | Catch-up if needed | - | Wrap up | Helmholtz repeatability |
| 7 | Additional H/A sessions if behind | - | Analysis + writeup | Helmholtz repeatability |
| 8 | - | - | - | Begin improved re-measurement |
| 9 | Wrap-up | - | - | Improved re-measurement |
| 10 | - | - | - | Final analysis, reports |

Note: Weeks 1-2 ramp up gradually (Y-plates first to learn the protocol, then
add H-plates and A-samples). By week 3, every session should include all three
sample types. Do not let H-plates and A-samples fall behind Y-plates.


---

## Success Metrics

By the end of summer, we should have:

1. **10 independent measurement sessions** for all 9 lab Y-plates, all 48
   lab H-plates, and lab A-samples, producing a lab Y-plate differential
   SEM of ~0.012% and meaningful H-plate/A-sample baselines

2. **Temperature cross-calibration** characterizing the Arduino-Teslameter
   offset with a clear recommendation for which sensor (or combination) to
   use, targeting temperature uncertainty <0.3 C (+/-0.020% on differential)

3. **Teslameter positioning noise** quantified per face, per material, per
   sample type (Y, H, A), from a 720-reading dataset across 3 days.
   Determines whether the Teslameter can serve as an independent primary
   measurement for publication.

4. **Helmholtz single-insertion std** measured (expect 0.02-0.05%), confirming
   negligible positioning noise

5. **Environmental characterization** showing typical temperature/humidity
   patterns during measurement sessions

6. (Stretch) **Improved-protocol tunnel Y-plate dataset** for C2 comparison

### Publication Readiness Checkpoint

At the end of the summer, evaluate:
- Can we show consistent demagnetization in both Helmholtz and Teslameter
  data on Y-plates? (Requires top-face Teslameter noise <0.15%)
- Do H-plate results, measured with improved baselines and both instruments,
  support the Y-plate story? (Requires multi-session H-plate baselines)
- Are A-sample paired comparisons informative? (Requires A-sample baselines)

If all three are "yes," we have the dataset for a high-impact journal paper
showing dual-measurement, multi-geometry evidence for radiation-induced
permanent magnet demagnetization in an operating accelerator.


---

## Important Reminders

- **Y-14 is the calibration plate.** Measure it at the start and end of EVERY
  session. It is the anchor for all cross-session comparisons.

- **Arduino sensor must be on for ALL Helmholtz measurements.** This is the
  only way to get synchronous ambient temperature.

- **1337 = missing data.** If a measurement fails, record 1337 (not 0, not
  blank). The analysis scripts know to skip this value.

- **Record anomalies.** If something unusual happens (power glitch, sample
  dropped, instrument reset), note it in the session log with the time.
  Better to have too many notes than too few.

- **Do not mix sessions.** All 4 slots of a Y-plate must be measured in the
  same session. If you cannot finish a plate, restart it in the next session.

- **Save data immediately.** After each plate, verify the data file was saved.
  Data loss from a 9-hour session would be devastating.
