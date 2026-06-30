# OSL Area Dosimetry Data — LDRD FFA@CEBAF

## Overview

Landauer OSL (Optically Stimulated Luminescence) area dosimeters deployed in the CEBAF tunnel and surrounding areas. All dosimeters are type **L02TN** (InLight Model 2T + CR-39 + thermal neutron detector), monitoring photons (X/gamma), beta, and neutrons (fast + thermal).

**Account**: 738211 (Jefferson Lab, Radiation Control)

## Data Sources

### Spreadsheets (xlsx)
- **10 reports** from `BetterNaming/` (dates: 20250227 through 20250930)
- **1 additional report** from parent `Areas/` folder (20251024) — **identical to 20250930** (same Part#s, same values; later retrieval of same data)
- Columns: Part Nbr, Badge Number, Begin/End Wear Date, Skin/Body/Eye/Beta/Neutron Dose (mrem), Note Code/Message
- **All doses in mrem** (millirem). 1 mrem = 0.01 mSv.

### PDFs (full reports)
- Contain **neutron thermal/fast breakdown** (NT and NF components) not available in xlsx
- Contain radiation quality codes (P, B, N, PB, PN, PBN, NT, NF)
- Contain photon energy classification (PH = high >200keV, PM = medium 40-200keV, PL = low <40keV)
- Contain special notes on saturation, irregular exposure, reprocessing

### SpareAreas.txt
- Maps 78 Landauer Part Numbers to physical locations for "spare" (rotating) dosimeters
- Locations include: NDX positions (EARC, WARC), ILX cryomodule positions, labyrinths, hut, etc.

## Output Files

### master_doses.csv
All dosimeter readings from all 11 reports. Key columns:
- `report_date`: YYYYMMDD of report
- `part_nbr`: Landauer Part Number (dosimeter ID)
- `badge_number`: Landauer serial number (XA...)
- `badge_location`: CONTROL or WHOLEBODY
- `begin_wear` / `end_wear`: Monitoring period dates
- `monitoring_period`: H1 (Jan-Jun) or H2 (Jul-Dec)
- `skin_mrem`, `body_mrem`, `eye_mrem`, `beta_mrem`, `neutron_mrem`: Doses in mrem
- `exceeded_1000rad`: True if dosimeter exceeded 1000 rad (10 Gy) OSL limit
- `saturated_osl`: True if OSL completely saturated (body reads 0 despite exceeding limit)
- `neutron_exceeded`: True if neutron component exceeded reporting capability
- `irregular_exposure`: True if flagged by Landauer as irregular
- `location`: Physical location (from SpareAreas.txt, if available)
- `location_source`: Source of location data

### spare_locations.csv
Complete SpareAreas.txt mapping: Part# -> Serial -> Location -> Install/Pull dates.

### report_summary.csv
Per-report statistics: badge counts, max doses, saturation counts.

## Unit Conversions

**All doses are in mrem (millirem) = dose EQUIVALENT, not absorbed dose.**
- rem = rad x Q (quality factor for biological effectiveness)
- For material damage (magnets), we want **absorbed dose (Gy)**, not dose equivalent (Sv/rem)

### Dose equivalent → SI:
| From (mrem) | To | Factor |
|---|---|---|
| 1 mrem | mSv | x 0.01 |
| 1 mrem | Sv | x 0.00001 |

### Dose equivalent → Absorbed dose (requires Q factor):
| Radiation Type | Q | 1 mrem → mGy (absorbed) |
|---|---|---|
| Photon (X/gamma) | 1 | 0.01 mGy |
| Beta | 1 | 0.01 mGy |
| Thermal neutron | ~2-5 | 0.01/Q mGy (energy-dependent) |
| Fast neutron (1-10 MeV) | ~5-20 (typically ~10) | 0.01/Q mGy |

**For photons/beta**: mrem and mrad are numerically equal (Q=1), so 1 mrem = 0.01 mGy directly.

**For neutrons**: The Landauer mrem values ALREADY include Q. To get absorbed dose:
absorbed_mGy = neutron_mrem / (100 x Q_avg). The exact Q depends on the neutron energy spectrum.

**IMPORTANT**: The "Body Dose" column is DDE (Deep Dose Equivalent) at 1 cm tissue depth.

### For magnet damage analysis:
- Keep radiation types SEPARATE — different damage mechanisms:
  - Photons/gamma → Compton electrons → ionization → thermal spikes
  - Fast neutrons → displacement damage (PKA) → thermal spikes
  - Thermal neutrons → 10B capture in NdFeB → alpha + 7Li → severe local damage
- The 10B neutron capture pathway is especially relevant for NdFeB (contains boron)

## Monitoring Periods

| Period | Date Range | Reports |
|---|---|---|
| H2 2024 | 2024-07-01 to 2024-12-31 | 20250227 (some badges) |
| H1 2025 | 2025-01-01 to 2025-06-30 | 20250227-20250804 |
| H2 2025 | 2025-07-01 to 2025-12-31 | 20250804 (partial), 20250819-20251024 |

Note: The 20250804 report straddles both periods (H1 on pp 1-49, H2 on pp 50-55).

## Key Caveats

### Saturated Dosimeters
Many high-dose locations exceeded the InLight OSL reporting capability of **1000 rad (10 Gy)**. These dosimeters were reprocessed but may show:
- `body_mrem = 0` with `exceeded_1000rad = True` (completely saturated, no readable photon dose)
- Only neutron dose readable (CR-39 track-etch survived when OSL didn't)
- `saturated_osl = True` means the ACTUAL dose was **higher than any readable dosimeter nearby**

### Neutron Thermal/Fast Split
The xlsx files only have combined "Neutron Dose". The PDF reports break this into:
- **NT** (thermal neutron): typically 5-10% of total neutron
- **NF** (fast neutron): typically 90-95% of total neutron
This split is important for magnet radiation damage modeling (neutrons interact differently by energy).

### Location Mapping Gap
Only 78 of 1330 unique Part Numbers have known locations (from SpareAreas.txt). The complete Part# -> location mapping is maintained by JLab Radiation Control (Kirsten). The Dosimetry Table PDFs map physical "Area Numbers" (1-95) to locations, but the link from Area Number to Landauer Part Number rotates as dosimeters are swapped.

### Same Dosimeter, Multiple Reports
A Part Number can appear in multiple reports if:
1. It spans a long monitoring period read at different times
2. It was re-read/reprocessed

### Dose Timing
Doses represent the **cumulative** exposure over the entire wear period (begin_wear to end_wear). The dosimeter records total integrated dose — it does NOT tell you when during the period the exposure occurred. For dose-rate estimation, divide by the wear period duration.

## Location Key (from SpareAreas.txt)

| Location Pattern | Description |
|---|---|
| ILX{N}S0{M} | Linac cryomodule position (N=linac section, M=slot) |
| EARC, NDX | East Arc, near NDX neutron detector |
| WARC, NDX | West Arc, near NDX neutron detector |
| North/South Labyrinth {A-D} | Tunnel labyrinth positions |
| J(N) ILM... | Linac magnet positions |
| (N) Inside/Outside hut | BSY area positions |
| (N) US/DS of ... | Upstream/downstream of specific magnets |

## Script

`parse_area_dosimetry.py` in `Cleanup_Claude/` reads all sources and generates these output files. Run from the `Cleanup_Claude/` directory.
