# Student Package: LDRD FFA@CEBAF Measurement Improvement

**For**: Moishe, Evelyn (summer interns, June-August 2026)
**Created**: 2026-06-04

Upload this entire folder to SharePoint. The subfolders are organized so you
can drag and drop into Overleaf (LaTeX) and work locally (everything else).

## Contents

### 01_LaTeX_Documents/
Three LaTeX guides, each in its own subfolder with all required figure PNGs.
Upload one subfolder at a time to Overleaf (each is a standalone document).

- `error_analysis_guide/` — Complete error analysis reference (sections A-M)
- `sn_improvement/` — Signal-to-noise improvement recommendations
- `summer_measurement_plan/` — 10-week summer measurement plan with priorities

### 02_Original_Markdown/
The same three guides in Markdown format for local reference/searching.

### 03_Temp_CrossCal/
Temperature sensor cross-calibration script and all outputs:
- `temp_sensor_comparison.py` — Run this to reproduce TC1-TC4 plots
- `temp_comparison_results.csv` — 492 matched Arduino/Teslameter pairs
- `temp_comparison_summary.txt` — Statistical summary
- `TC1-TC4` PNGs — Cross-calibration plots

### 04_Analysis_Scripts/
Key Campaign 1 and Campaign 2 analysis scripts (read-only reference).
These are the scripts discussed in the error analysis guide.

### 05_June_Data/
June 2-3, 2026 Helmholtz and Teslameter measurement files. Needed to re-run
or extend `temp_sensor_comparison.py`. Contains ~3000 .dat files total.

- `Helmholtz/` — June 2 and June 3 Helmholtz .dat files (+ 8 older session zips)
- `Teslameter/` — June 2 and June 3 Teslameter .dat files

### 06_Technical_Note/
The full Campaign 1 technical note for deeper reading:
- `main.tex` — ~2860 lines, compiles with biblatex/biber
- `references.bib` — 27 entries
- `figures/` — 41 PNGs

### 07_Verification/
- `verify_results.py` — Standalone script that checks 21 headline numbers
  from the Data_Package CSVs. Run to verify the Campaign 1 results.

## Requirements
- Python 3.9+ with numpy, matplotlib, openpyxl, scipy
- LaTeX: standard packages only (no custom .sty). Works in fresh Overleaf project.
- Sentinel value `1337` in data files means "no measurement"

## Key Reference
- Y-14 is the Campaign 2 calibration plate (lab plate, measured multiple times
  per session for instrument stability monitoring)
- Temperature coefficients: N42EH -0.10%/C, N52SH -0.11%/C, SmCo -0.04%/C
- Reference temperature: 20.0 C
