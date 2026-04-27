# Instrument Specifications

## Helmholtz Coil Fluxmeter (Model 2130)

Primary measurement instrument for magnetic moment (flux integral).

| Parameter | Value |
|-----------|-------|
| DC Accuracy | 0.050% typical, 0.100% max (of full-scale) |
| Display | 4.75 digit resolution |
| Ranges | 12 ranges: 100 kMT to 100 MMT |
| Drift Compensation | Auto (within +/-1% of range) |

**Measurement principle**: Integrates voltage induced in a Helmholtz coil pair
when a magnetized sample is inserted/removed. Result in milliWeber-centimeters
(mWC), proportional to magnetic moment.

**Position sensitivity**: "Fairly independent of sample position within coils"
(manufacturer spec, section 4.7). This is critical — it means pre-deployment and
post-deployment readings are directly comparable even if exact placement differs.

**Systematic uncertainties in this study**:
- Session-to-session gain variability: +/-0.124% (cleaned), +/-0.248% (uncleaned)
- This gain drift is NOT instrument noise — it reflects coil connection
  variability, thermal drift, and setup differences between measurement campaigns
- Intrinsic accuracy (0.05%) is approximately 6x better than our 0.3% signal
- Team re-zeros the instrument frequently during campaigns

**Reference**: Fluxmeter_Manual.pdf (63 pp, Rev 3, 2013)

## Teslameter (SENIS 3MH6-E) with Type C Hall Probe

Secondary measurement instrument for point magnetic field (3-axis).

| Parameter | Value |
|-----------|-------|
| DC Accuracy | 0.01% (100 ppm) |
| Ranges | +/-0.1T, +/-0.5T, +/-2T |
| Temperature Stability | < 20 ppm/C |
| Resolution | ~1 uT RMS at 10 SPS (~0.5 ppm) |
| Sensing Volume | ~100 x 10 x 100 um3 (CMOS Hall sensor) |
| Probe Interchangeability | Calibration stored in EEPROM, maintains 100 ppm |

**Measurement principle**: 3-axis CMOS Hall probe measures magnetic field
components (Bx, By, Bz) and probe temperature simultaneously. Field magnitude
|B| = sqrt(Bx^2 + By^2 + Bz^2). Temperature used for Helmholtz correction.

**3D-printed measurement rigs**: Samples are placed in custom 3D-printed rigs
(NOT hand-held). Each sample has front, side, and top face measurements.

**Positioning systematic uncertainties in this study**:
- Top face precision: 0.14-0.29% (best)
- Front face precision: 0.57-0.91%
- Side face precision: 0.90-1.90% (worst)
- Positioning noise dominates over instrument noise
- Rig/cap system was changed before tunnel deployment, introducing a small
  baseline offset for Teslameter field readings (but NOT for temperature)

**Temperature readings**: Valid for all dates (pre- and post-deployment).
The temperature sensor is separate from the field sensors and was not affected
by the probe replacement that occurred between December 2024 and July 2025.

**Probe history**:
- Pre-deployment (2024): Original probe. Temperature valid, field readings
  valid but with different rig geometry.
- Post-deployment (Jul 2025+): Replacement probe + new rig/cap. Temperature
  and field both valid. First tunnel measurement used as Teslameter baseline.

**Reference**: Teslameter_Datasheet.pdf (7 pp, Rev 3.4, Nov 2025),
Hall-probe-type-C datasheet (6 pp, Rev 1.2, Nov 2024)
