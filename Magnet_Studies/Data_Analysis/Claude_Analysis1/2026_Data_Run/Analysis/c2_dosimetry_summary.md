# Campaign 2 Dosimetry: Combined Rod + OSL Analysis

**Date**: 2026-05-18
**Status**: Raw rod readings + January 2026 OSLs. Not yet processed through Kirsten's AIdata pipeline. April 2026 OSLs not yet available.

---

## Methodology

Applied Kirsten's decision tree to combine FWT-70 rod readings with Landauer OSL badge data:

1. Rod < 2 krad AND OSL not saturated: use OSL (more sensitive at low dose)
2. Rod < 2 krad AND OSL saturated: use 1.5 krad gap fill
3. Rod 2-39 krad (Low@600nm valid): use rod
4. Rod > 39 krad: cascade to High@600nm range

**Additional cross-check**: When rod is borderline (2-5 krad) but OSL shows < 1 Gy (not saturated), the OSL is preferred. This catches noise at the rod's detection boundary.

**Data sources**:
- Rod readings: `Rods_read_051526_Isurumali_Raw.xlsx` (read by Isurumali, 2026-05-15)
- Rod-plate mapping: Extracted from April 2026 Teslameter .dat files (same methodology as C1)
- January 2026 OSLs: Landauer report 20260320 (wear period Jul-Dec 2025)
- 60 plates mapped for each swap period (30 Y-plates + 30 H-plates)

---

## Population 1: January 2026 (Shutdown Period)

**Rods**: R-681 to R-740 (C1-final batch), installed Jan 8-12, 2026
**OSLs**: January 2026 collection (Landauer report 20260320)
**Exposure**: Shutdown period (Sep 2025 through Jan 2026, no beam)

### Results

| Metric | Value |
|--------|-------|
| Plates analyzed | 60 |
| OSL used (rod below detection) | 44 |
| OSL preferred (rod borderline, cross-check) | 15 |
| OSL only (no rod match) | 1 |
| Maximum dose | 0.0007 Gy (0.07 mrem equivalent) |
| OSL saturated | 0 |
| Neutron signal | 0 (all plates) |

### Beam-Off Verification

All January 2026 OSL readings are consistent with zero beam:
- Range: 0-62 mrem body dose (max 0.62 mSv at Y-16, an NDX location)
- Zero readings: 3/30 Y-plates, 8/30 H-plates
- No saturated badges. No neutron signal on any plate.
- The small photon signals (5-62 mrem) at NDX locations are residual activation from the C1 run, not beam-on radiation.

**This confirms that the shutdown period (Sep 2025 through Jan 2026) produced negligible radiation exposure**, consistent with no beam operations. The 15 C1-final rods that read 2.0-2.8 krad (barely above the FWT-70 detection threshold) show no correlation with plate location or C1 dose; they are noise at the detection boundary. The OSL cross-check correctly identifies them as such.

---

## Population 2: April 2026 (Early Low-Energy C2 Run)

**Rods**: R-741 to R-800 (C2-new batch), installed between Jan-Apr 2026
**OSLs**: Not yet available (April 2026 Landauer report pending)
**Exposure**: Days to weeks at 0.69 GeV/pass (low-energy restore/early operations)

### Results

| Category | N plates | Dose range |
|----------|----------|-----------|
| Below detection (rod < 2 krad, no OSL) | 46 | 0 |
| Borderline (rod 2.0-2.8 krad) | 11 | 20-28 Gy (raw); likely noise |
| Moderate (rod 3-10 krad) | 4 | 38-93 Gy |
| High (rod > 30 krad) | 3 | 363-566 Gy |

**Note**: The 11 borderline readings (2.0-2.8 krad) have no April OSL to cross-check against. They cluster at the detection threshold, similar to the January pattern. Some may be real (particularly at locations with known beam loss) and others may be noise. The April OSLs, when available, will resolve this.

### High-Dose Locations

| Plate | Rod | Dose (Gy) | C1 Dose (Gy) | C2/C1 Ratio | Location |
|-------|-----|-----------|-------------|------------|----------|
| Y-17 | R-746 | 566 | 7,111 | 0.080 | NL NDX Girder 23 |
| Y-24 | R-758 | 443 | 6,299 | 0.070 | NL Girder 25 |
| Hn-20 | R-745 | 363 | 5,295 | 0.069 | NL NDX Girder 20 |
| Hs-13 | R-751 | 93 | 4,902 | 0.019 | SL Girder 13 |

**Note on Y-17 dose**: R-746 has Low@600nm = 39.4 krad (at the upper limit of the Low range). The decision tree cascades to High@600nm = 56.6 krad. The High-range value is more reliable near the Low-range saturation point.

### Moderate-Dose Locations

| Plate | Rod | Dose (Gy) | C1 Dose (Gy) | C2/C1 Ratio | Location |
|-------|-----|-----------|-------------|------------|----------|
| Y-5 | R-752 | 49 | 37 | 1.32 | SL Girder 22 |
| Y-40 | R-781 | 42 | 14 | 3.07 | SE Arc Line 5 |
| Hn-19 | R-768 | 38 | 30 | 1.27 | NL Girder 19 |
| Hn-8 | R-778 | 28 | 13 | 2.10 | NL Girder 8 |

---

## C1 vs C2 Dose Comparison

### NDX Hotspots (high-loss linac locations)
The top 3 C2 plates (Y-17, Y-24, Hn-20) are all in the North Linac NDX region, the same locations that dominated C1 doses. C2/C1 ratios of 7-8% are physically consistent with the shorter exposure time (weeks vs 6 months) and lower beam energy (0.69 vs 2.12 GeV/pass). The lower energy means less secondary radiation per beam loss event, and the shorter time means fewer events.

### Surprising C2 > C1 Locations
Several plates show C2 dose exceeding their full C1 dose despite much shorter exposure:
- **Y-40** (SE Arc, Line 5): C2/C1 = 3.1. This location saw only 14 Gy during all of C1 but 42 Gy in just weeks of C2. Suggests the low-energy beam has a different loss pattern in the arcs.
- **Hn-8** (NL Girder 8): C2/C1 = 2.1. Same pattern.
- **Y-5** (SL Girder 22): C2/C1 = 1.3.
- **Hn-37** (NE Arc): C2/C1 = 2.0.

These elevated ratios at moderate-dose locations may indicate that the 0.69 GeV/pass beam has tighter aperture constraints or different beam loss patterns compared to the 2.12 GeV/pass C1 beam. This is worth monitoring as the beam energy increases later in C2.

### Hs-13 Anomaly
Hs-13 has a notably low C2/C1 ratio (0.019) compared to the other NDX plates (0.07-0.08). This may indicate that beam loss at this South Linac location is different at 0.69 GeV than at 2.12 GeV.

---

## Data Quality

All data quality issues documented in `c2_rod_summary.md` apply here. Key items:
- Partial-to-re-entry rows handled by preferring complete entries
- Range column errors corrected using Notes + OD cross-check (R-762, R-689)
- R-685 first High replicate nulled (accidental Low rod re-read)
- Rod ID typos corrected (R-979->R-797, R-7051->R-705, R=712->R-712, 1r-692->R-692)

---

## What We Still Need

1. **April 2026 OSLs from Landauer**: Will enable cross-checking the 11 borderline April rod readings and provide neutron data for C2.
2. **Kirsten's AIdata processing**: Her pipeline applies validity checks and cross-wavelength integration for more reliable dose estimates, particularly important for the 3 high-reading rods near the Low-range limit.
3. **Energy transition monitoring**: When the beam switches to 2.12 GeV/pass (~late May 2026), the dose pattern should shift to match C1. Comparing before/after the energy change will be informative.

---

## Files Generated

- `c2_rod_plate_map.csv`: Rod-to-plate mapping (January + April)
- `c2_dosimetry_merged.csv`: Per-plate dose estimates with decision tree sources
- `c2_rod_raw_summary.csv`: Per-rod summary (from c2_rod_analysis.py)
- `c2_rod_summary.md`: Rod-only analysis narrative
- This file: `c2_dosimetry_summary.md`

## Scripts

- `c2_rod_analysis.py`: Parse raw rod spreadsheet
- `c2_rod_plate_mapping.py`: Extract rod-plate mapping from .dat files
- `c2_dosimetry_analysis.py`: Combined rod+OSL analysis with decision tree
