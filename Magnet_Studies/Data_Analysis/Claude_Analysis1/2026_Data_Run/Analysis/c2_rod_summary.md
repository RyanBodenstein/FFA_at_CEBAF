# Campaign 2 Rod Dosimetry: Raw Reading Summary

**Date**: 2026-05-18
**Source**: `Rods_read_051526_Isurumali_Raw.xlsx` (read by Isurumali on 2026-05-15)
**Status**: RAW readings only; not yet processed through Kirsten's AIdata pipeline

---

## Overview

121 unique rods parsed from 250 data rows. Two distinct populations:

| Population | Rod IDs | N | When installed | Exposure period |
|------------|---------|---|---------------|----------------|
| C1-final | R-681 to R-740 | 60 | Jan 8-12, 2026 | Shutdown (no beam) + early C2 low-E run |
| C2-new | R-741 to R-800 | 60 | Between Apr 20 and May 15, 2026 | Days-to-weeks at 0.69 GeV/pass |
| Other | R-636 | 1 | Older batch (C1 era) | Unknown; asterisk in notes |

**Key context**: The machine was in shutdown from Sep 2025 through Mar 2026 (no beam).
Restore began mid-March 2026 at 0.69 GeV/pass (1/3 of C1's 2.12 GeV/pass).
Both rod populations therefore saw minimal radiation.

---

## Main Finding: Most Readings Below Detection

FWT-70 Low-range rods are valid at 600nm from 2 to 39 krad (20 to 390 Gy).

| Population | Below detection (<2 krad) | In valid range | Median (krad) |
|------------|--------------------------|---------------|---------------|
| C1-final | 44/59 (75%) | 15/60 (25%) | 1.48 |
| C2-new | 46/60 (77%) | 12/60 (20%) | 1.28 |

**This is exactly what we expect.** Shutdown + low-energy operation produced very little dose,
even at historically high-dose locations.

---

## C1-Final Rods (R-681 to R-740): Known Plate Assignments

These rods have plate mappings from the C1 measurement .dat files. Key observations:

**High-dose C1 locations show below-detection C2 readings:**
- R-730 (Y-22, NL Girder 26, C1: 23,451 Gy): only 0.52 krad. Below detection.
- R-702 (Y-30, SL Girder 25, C1: 22,102 Gy): only 1.34 krad. Below detection.
- R-685 (Y-16, NL Girder 23, C1: 15,837 Gy): only 1.89 krad. Below detection.
- R-706 (Y-1, SL Girder 23, C1: 14,714 Gy): only 1.50 krad. Below detection.

These were C1's hottest locations. The fact that they're all below detection confirms
the shutdown + early low-E operation produced negligible dose even at the worst spots.

**The 15 "in-range" C1-final readings (2.0-2.8 krad) show NO correlation with
C1 dose.** They include both low-dose arc plates (Y-38: 10 Gy in C1) and moderate-dose
positions (Y-9: 1,640 Gy in C1). This clustering just above threshold with no dose
dependence suggests these are noise at the detection boundary, not real dose signal.

---

## C2-New Rods (R-741 to R-800): Plate Mapping Available

**Plate assignment extracted from April 2026 Teslameter .dat files** using the
same methodology as C1 (rod IDs recorded alongside plate names during measurement).
All 60 C2-new rods mapped to 30 Y-plates + 30 H-plates (Y-2 excluded; calibration plate, no dosimetry by design).

**Three standout high readings:**

| Rod | Plate | Low@600 (krad) | High@600 (krad) | Location | C1 Dose (Gy) |
|-----|-------|---------------|----------------|----------|-------------|
| R-746 | Y-17 | 39.4 | 56.6 | NL NDX Girder 23 | 7,111 |
| R-758 | Y-24 | 40.6 | 44.3 | NL Girder 25 | 6,299 |
| R-745 | Hn-20 | 36.3 | 55.4 | NL NDX Girder 20 | 5,295 |

All three are at **North Linac NDX positions**, the same locations that dominated
C1 doses. C2/C1 ratios of 7-8% are physically consistent with the shorter exposure
time (weeks vs 6 months) and lower beam energy (0.69 vs 2.12 GeV/pass).

**Four moderate readings (3.8-9.3 krad = 38-93 Gy):**

| Rod | Plate | Dose (krad) | Location | C1 Dose (Gy) |
|-----|-------|-----------|----------|-------------|
| R-751 | Hs-13 | 9.3 | SL Girder 13 | 4,902 |
| R-752 | Y-5 | 4.9 | SL Girder 22 | 37 |
| R-781 | Y-40 | 4.2 | SE Arc Line 5 | 14 |
| R-768 | Hn-19 | 3.8 | NL Girder 19 | 30 |

Note: Y-40 and Hn-8 show C2 > C1 dose ratios, suggesting different beam loss
patterns at 0.69 GeV/pass vs 2.12 GeV/pass.

**Remaining 53 rods**: below or barely at detection threshold. Consistent with
low-dose arc and labyrinth positions during the low-energy run.

---

## Data Quality Notes

### Spreadsheet formatting patterns

Isurumali's data entry has a few recurring patterns that are NOT errors,
just workflow artifacts:

**Partial -> blank -> re-entry** (R-799, R-762, R-721, R-711): A row was
started with only the first replicate, followed by a blank row, then a
complete re-entry with both replicates. The complete re-entry is the
correct data; the partial first attempt should be discarded.

**Range column errors** (Range column wrong, Notes column correct):
- R-762, Row 35: Range says "High" but Notes says "R-762: Low" and ODs
  (0.357, 0.357) are clearly Low-range values. This is the re-entry of
  the partial R-762 Low from Row 34. The actual High reading is Row 36.
- R-689, Row 176: Range says "Low" but Notes says "R-689: High" and ODs
  (0.116, 0.124) are clearly High-range values. Trust the Notes.

**Rod ID typos** (minor, correctable): R-979 (likely R-797), R-7051
(likely R-705), R=712 (R-712), 1r-692 (R-692). All corrected in parsing.

### Genuine anomalies

**R-685 (Y-16, NL NDX Girder 23), Row 140**: First High-range replicate
OD (0.373) nearly matches the Low-range readings (0.379, 0.371). Most
likely Isurumali accidentally re-read the Low rod instead of the High rod
for the first measurement, then correctly read the High rod for the second
replicate (OD 0.109). Only the second High replicate should be used.

### R-636* (known provenance)

This is the rod from the Y-39 dosimetry chain that was accidentally left
on the EM dipole near Y-39 during the Sep 10, 2025 dosimetry-only swap
(the only known incident of dosimetry left behind). Found in January 2026.
It integrated ~7 days of beam (Aug 27 to Sep 3, 2025) plus residual
activation from Sep 3 to Jan 2026. Reading of 3.7 krad (37 Gy) is
physically consistent with ~1 week of beam at an arc Line 1 position.
The asterisk likely flags this history.

---

## Comparison to C1

| Metric | C1 (full campaign) | C2 (C1-final rods) | C2 (new rods) |
|--------|-------------------|--------------------|----|
| Beam-on time | ~6 months | ~2 months low-E | Days-to-weeks |
| Beam energy | 2.12 GeV/pass | 0.69 GeV/pass | 0.69 GeV/pass |
| Arc plate gamma | 10-1,700 Gy | Below detection | Below detection |
| NDX gamma | 6,000-23,000 Gy | Below detection | 360-410 Gy (3 rods) |
| % above detection | ~70% (with OSL) | 25% (borderline, OSL preferred) | 23% (7 real + 7 borderline) |

---

## What We Need Next

1. ~~**Plate mapping for R-741-800**~~: DONE. Extracted from April 2026 Teslameter
   .dat files. All 60 rods mapped. High-reading rods confirmed at NDX locations.

2. **April 2026 OSL badges from Landauer**: Will enable cross-checking the 11
   borderline April rod readings and provide neutron data for C2.

3. **Kirsten's processed data**: The raw calibration here is a simple linear model.
   Kirsten's AIdata pipeline applies validity checks, cross-wavelength integration,
   and OSL combination for a more reliable dose estimate.

4. **Energy transition monitoring**: When the beam switches to 2.12 GeV/pass
   (~late May 2026), the dose pattern should shift. Before/after comparison
   will be informative.

---

## Files Generated

- `c2_rod_raw_summary.csv`: Per-rod summary with doses, validity flags, C1 comparison
- `c2_rod_analysis.py`: Analysis script (reproducible)
- This file: `c2_rod_summary.md`
