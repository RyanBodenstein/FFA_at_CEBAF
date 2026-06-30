# Files to Send to Summer Interns (Moishe, Evelyn)

All paths are relative to `Claude_Analysis1/`.

Last updated: 2026-06-04

---

## 1. LaTeX Documents (for Overleaf)

Upload these to a shared Overleaf project:

- [ ] `Measurement_Improvement/LaTeX/error_analysis_guide.tex`
- [ ] `Measurement_Improvement/LaTeX/sn_improvement.tex`
- [ ] `Measurement_Improvement/LaTeX/summer_measurement_plan.tex`

### Figures for Overleaf (upload alongside .tex files)

From `Cleanup_Claude/Presentation_Plots/`:
- [ ] `P1_material_comparison.png`
- [ ] `P4_lab_controls.png`
- [ ] `P5_uncertainty_budget.png`

From `Technical_Note/figures/`:
- [ ] `S1_temp_sensitivity.png`

From `Cleanup_Claude/Within_Session_Drift/`:
- [ ] `WSD2_differential_vs_time.png`
- [ ] `WSD3_pooled.png`

From `Measurement_Improvement/`:
- [ ] `TC1_temp_scatter.png`
- [ ] `TC3_timeofday.png`

From `2026_Data_Run/Analysis/`:
- [ ] `C2-1_calibration_repeatability.png`
- [ ] `C2-2_temperature_evolution.png`

---

## 2. Original Markdown Guides (for local reference)

- [ ] `Measurement_Improvement/error_analysis_guide.md`
- [ ] `Measurement_Improvement/teslameter_improvement.md`
- [ ] `Measurement_Improvement/summer_measurement_plan.md`

---

## 3. Temperature Cross-Calibration Script and Outputs

- [ ] `Measurement_Improvement/temp_sensor_comparison.py`
- [ ] `Measurement_Improvement/temp_comparison_results.csv`
- [ ] `Measurement_Improvement/temp_comparison_summary.txt`
- [ ] `Measurement_Improvement/TC1_temp_scatter.png`
- [ ] `Measurement_Improvement/TC2_residual_vs_temp.png`
- [ ] `Measurement_Improvement/TC3_timeofday.png`
- [ ] `Measurement_Improvement/TC4_humidity_effect.png`

---

## 4. Key Analysis Scripts (read-only reference)

These are the scripts discussed in the error analysis guide. Students should
read them to understand how the analysis pipeline works, but should not modify
the originals.

- [ ] `Cleanup_Claude/temperature_corrected_analysis.py` (core temp correction + differential)
- [ ] `Cleanup_Claude/gain_systematic_analysis.py` (gain systematic deep-dive)
- [ ] `Cleanup_Claude/within_session_drift.py` (within-session drift validation)
- [ ] `Cleanup_Claude/manager_summary_v3.py` (fleet statistical summaries)
- [ ] `2026_Data_Run/campaign2_quality_check.py` (C2 data quality and parsing)
- [ ] `2026_Data_Run/c2_june_analysis.py` (June 2-3 analysis with temp data)

---

## 5. Data Directories (needed to re-run cross-cal script)

Students will need the June 2-3 data if they want to re-run or extend
`temp_sensor_comparison.py`:

- [ ] `2026_Data_Run/2026-6-3-Helmholtz/` (Helmholtz .dat files, June 2-3)
- [ ] `2026_Data_Run/2026-6-3-Teslameter/` (Teslameter .dat files, June 2-3)

---

## 6. Technical Note (deeper reading)

For students who want to understand the full C1 analysis in detail:

- [ ] `Technical_Note/main.tex`
- [ ] `Technical_Note/references.bib`
- [ ] `Technical_Note/figures/` (all PNGs)

---

## 7. Verification Script

Standalone 21-check verification of all C1 results:

- [ ] `Data_Package/06_Scripts/verify_results.py`

---

## Notes

- The LaTeX documents compile with standard packages only (no custom .sty
  files). A fresh Overleaf project with the .tex files + figure PNGs will work.
- All scripts require Python 3.9+ with numpy, matplotlib, openpyxl, scipy.
- The sentinel value 1337 in data files means "no measurement."
- Y-14 is the calibration plate for Campaign 2.
