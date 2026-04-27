# 01_Sample_Configuration

Sample identification, material assignments, and physical placement information.

## Files

### materials_arrangements.csv
Material assignment for every magnet slot in the study. Parsed directly from
`Materials_Arrangements.xlsx` (the authoritative source maintained by the
experimental team). Covers all Y-plates (tunnel and lab), H-plates, and
A-samples.

**Source**: `export_data_package.py` → `openpyxl` parse of `.xlsx`

### tunnel_placements.csv
Physical location of each tunnel-deployed Y-plate within the CEBAF accelerator.
Each Y-plate is co-located with an H-plate for cross-checking. The `line_position`
column (1-5) indicates position within a line of 5 plates at arc locations;
linac and labyrinth plates have line_position=0.

**Source**: `PLACEMENTS` list in `degradation_summary_v2.py`, derived from
JLAB-TN-25-021 (installation plan).

### sample_inventory.csv
Comprehensive inventory of every sample in the study, combining material
assignments, placement, and configuration information. The `config` column
applies only to H-plates and A-samples (Alpha, Beta, Gamma, Delta magnetic
configurations).

**Source**: `export_data_package.py`, merging xlsx data with placement info.

## Key Relationships
- Y-plates are identified by plate number (1-40) and slot (1-4).
  Tunnel: plates {1,3-7,9-13,15-26,30,32,34,36,38-40}. Lab: {8,14,27-29,31,33,35,37}.
- Each tunnel Y-plate is co-located with one H-plate (see tunnel_placements.csv).
- H-plates have a direction prefix: "n" = NdFeB, "s" = SmCo.
- A-samples are sub-components of H-plates, with an additional pair index (1 or 2).
- Slot-to-material assignments are RANDOMIZED (4 cyclic patterns), not fixed.
