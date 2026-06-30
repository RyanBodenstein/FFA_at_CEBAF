# LDRD FFA@CEBAF Magnet Radiation Study: Full Project Inventory

**Date**: 2026-05-19
**Scope**: All tasks, subtasks, reviews, publications, data, and identified gaps

---

## PART 1: COMPLETED WORK

### A. Core Analysis Pipeline (Tasks 1-9, 17-22)

| Task | Description | Status | Key Output |
|------|-------------|--------|------------|
| 1-3 | Dose pipeline (OSL parsing, badge mapping, plate cumulative) | DONE 2026-03-25 | 782 entries, 99.6% match |
| 4 | Rod dosimetry + dose-degradation correlations | DONE 2026-03-27 | Gamma null, neutron significant (rho=0.389, p=0.034) |
| 5 | Gain systematic quantification | DONE 2026-03-25 | +/-0.124% cleaned, +/-0.248% uncleaned |
| 7 | Dose-region breakdowns | DONE 2026-03-25 | Dose-position inversion discovered |
| 8 | Tunnel vs lab (unexposed vs exposed) | DONE 2026-03-25 | Tunnel-Lab diff 4.3 sigma |
| 9 | Time series evolution | DONE 2026-03-26 | NdFeB-SmCo diff stable post-deployment |
| 11 | Memory hygiene | DONE 2026-03-26 | — |
| 13 | Lab temperature correction | DONE 2026-03-26 | Lab Y-plate diff 0.2 sigma (validated) |
| 17 | Merged into Task 4 | — | — |
| 18 | Re-run all 8 downstream scripts with per-date temps | DONE 2026-03-31 | Old plots archived |
| 19 | Memory/priority updates | DONE 2026-03-31 | — |
| 20 | Comprehensive systematic error analysis | DONE 2026-04-01 | Combined: -0.208% +/- 0.045% (4.6 sigma) |
| 21 | Error analysis sub-tasks (a,b,c,e,f) | DONE 2026-04-01 | Sensitivity, Y-only vs combined, H scatter, temp robustness, probe bias |
| 22 | Rod calibration uncertainty propagation | DONE 2026-04-02 | Error bars on R1-R4, uncertainty budget |

**Temperature correction evolution:**
- v1 (blanket 23C): -0.134% (5.0 sigma) -- overcorrected
- v2 (per-date, no probe bias): robust
- **v3 (per-date + 0.8C probe bias): -0.208% (7.6 sigma) -- CURRENT**

### B. Publication Readiness (Peer Review Tasks)

#### Tier 1 -- Required (ALL COMPLETE)

| Task | Description | Status |
|------|-------------|--------|
| T1-1 | Fix headline rounding (0.028/7.6 sigma) | DONE 2026-04-13 |
| T1-2 | Add error bar definitions to all plots | DONE 2026-04-14 |
| T1-3 | Literature comparison figure (P15) | DONE 2026-04-14 |
| T1-4 | Address dose-position inversion (Section 6.7, R7 plot) | DONE 2026-04-14 |
| T1-5 | State multiple-comparisons context | DONE 2026-04-13 |
| T1-6 | Reconcile P1 temperature label | DONE 2026-04-13 |
| T1-7 | Fix time series plots (T1, P2) | DONE 2026-04-14 |
| T1-8 | Fast vs thermal neutron correlation (R6 plot) | DONE 2026-04-13 |

#### Tier 2 -- Significantly strengthens (4/5 COMPLETE, 1 BLOCKED)

| Task | Description | Status |
|------|-------------|--------|
| T2-1 | NDX neutron dose-response curve | **BLOCKED** on Task 14 |
| T2-2 | Thermal spike model comparison (TS1 plot) | DONE 2026-04-14 |
| T2-3 | Frame gamma null as positive finding | DONE 2026-04-13 |
| T2-4 | Blind-analysis statement | DONE 2026-04-13 |
| T2-5 | Update DATA_DICTIONARY with Task 22 columns | DONE 2026-04-13 |

#### Tier 3 -- Ground-breaking (1/5 COMPLETE, 1 EXPERIMENTAL, 3 BLOCKED/NOT STARTED)

| Task | Description | Status |
|------|-------------|--------|
| T3-1 | Dy-content hypothesis (Allstar composition data) | DONE 2026-04-15 |
| T3-2 | Dedicated temperature coefficient measurement | EXPERIMENTAL (future) |
| T3-3 | Second exposure period (cumulative damage test) | C2 UNDERWAY |
| T3-4 | Neutron spectrum simulation (BDSIM) | NOT STARTED |
| T3-5 | H-plate Halbach configuration analysis | BLOCKED on Task 6 + Beta config |

### C. Allstar Composition Data (Task 12)

| Item | Status |
|------|--------|
| Spreadsheet received | DONE 2026-04-15 |
| N42EH: Dy 1-2%, N52SH: Dy 0% confirmed | DONE |
| Neutron capture budget computed (TS2 plot) | DONE |
| Dy = 98% of RE capture differential | DONE |
| SmCo paradox explained (Tc + Ha resistance) | DONE |
| Tech Note updated with composition table + analysis | DONE |

### D. Adversarial Review (Task 26) -- COMPLETE 2026-05-08

- 30+ weaknesses across 6 severity tiers
- **Tier 0 (factual errors)**: 3/3 fixed (18-month error, probe timeline, 6 bad bib entries)
- **Tier 1 (statistical)**: 5/5 addressed (Bonferroni, p-hacking optics, N=2 probe, significance range, CI)
- **Tier 2 (physics)**: 5/6 addressed (dose-position, theory gap, N42EH>N52SH, flat evolution, SmCo paradox). **2-5 BLOCKED** (no dose-response curve without NDX data)
- **Tier 3 (methodology)**: 4/4 addressed (single baseline, rod failure rate, blind analysis, within-session drift)
- **Tier 4-5 (presentation)**: all addressed
- Readability pass: 21 improvements, ~274 lines added, accessible to undergrads
- Reference verification: 10/10 PDFs in Reference_Sources/ (all verified)

### E. Pre-Presentation Verification (2026-05-12) -- COMPLETE

- All 6 analysis scripts re-run
- 55 claims verified against script output (CLAIMS_INVENTORY.md)
- 12 corrections made to main.tex (5-sigma claims x4, correlation table x3, body text x2, epistemic language x3)
- End-to-end code audit: raw .dat parsing through headline numbers verified
- Data Package fixes: lab mWC values, alpha_used bug, README rounding, headline_results expansion
- verify_results.py: 21 independent checks, all pass

### F. Publications

| Publication | Status | Location |
|-------------|--------|----------|
| Technical Note | READY FOR CO-AUTHOR REVIEW | `Technical_Note/main.tex` (~2840 lines) |
| IPAC26 Proceedings | **SUBMITTED** | `IPAC26_Magnet_LDRD/IPAC26.tex` |
| Talk (June 2, 2026) | OUTLINE + PLAN COMPLETE, SLIDES NOT YET BUILT | `TALK_PLAN.md`, `TALK_OUTLINE.md` |

### G. Data Package (Task 10) -- COMPLETE, updated 2026-05-12

- 7 subdirectories, 17 CSVs, 40+ plots, 20+ scripts, 8 READMEs
- DATA_DICTIONARY.md (comprehensive)
- verify_results.py (standalone, 21 checks)
- Reproducible: anyone with CSVs + numpy + scipy can replicate headlines

### H. Beam Schedule Context (2026-05-15) -- COMPLETE

- "12 months deployed (~6 months beam-on)" distinction added to:
  - main.tex (5 locations + Task 16 note)
  - TALK_OUTLINE.md (line 24 + backup slide 15)
  - TALK_PLAN.md (slide 3 + Q10 + Q11)

---

## PART 2: CAMPAIGN 2 (ONGOING)

### A. Magnet Measurements (2026-04-20) -- ANALYZED

| Item | Status | Key Result |
|------|--------|------------|
| Helmholtz + Teslameter data collected | DONE | 118/120 matched |
| campaign2_quality_check.py | DONE | Fleet offset -0.16% (instrumental). NdFeB-SmCo C2-C1 residual: -0.033 +/- 0.109% (zero storage effect) |
| Y-14 calibration repeatability | DONE | 0.06-0.27% |
| Delta slug noise floor | DONE | 0.061 mT median |
| Data gaps documented | DONE | Y-2 (calibration), Y-6-2, Y-17-3, Y-23-1 |
| Plots: C2-1 through C2-4 | DONE | In Analysis/ |

### B. C2 Rod Dosimetry (2026-05-18/19) -- ANALYZED

| Item | Status | Key Result |
|------|--------|------------|
| Raw readings parsed | DONE | 121 rods from Isurumali spreadsheet |
| Rod-plate mapping extracted | DONE | 60 plates, both Jan + Apr swaps |
| Decision tree applied (rod + OSL) | DONE | January: beam-off verified (max 0.0007 Gy). April: 3 NDX hotspots (363-566 Gy) |
| Data quality issues documented | DONE | Partial rows, range errors, R-685 re-read, R-636 provenance |
| C1 vs C2 dose comparison | DONE | NDX C2/C1 ~7-8%. Some locations C2 > C1 (beam loss pattern change at 0.69 GeV) |

**C2 Rod Dosimetry Files:**
- `c2_rod_analysis.py`, `c2_rod_plate_mapping.py`, `c2_dosimetry_analysis.py`
- `Analysis/c2_rod_plate_map.csv`, `c2_rod_raw_summary.csv`, `c2_dosimetry_merged.csv`
- `Analysis/c2_rod_summary.md`, `c2_dosimetry_summary.md`

### C. C2 OSL Status

| Item | Status |
|------|--------|
| January 2026 OSLs (Landauer 20260320) | PARSED, in plate_dose_map.csv. All 0-62 mrem, zero neutron, zero saturated. |
| April 2026 OSLs | **NOT YET RECEIVED** from Landauer |

### D. C2 Still Needed

1. **April 2026 OSLs from Landauer** -- cross-check borderline rods, neutron data
2. **Kirsten's AIdata processing** -- proper calibration for raw rod readings
3. **Energy transition monitoring** -- beam switches to 2.12 GeV/pass ~late May 2026
4. **Next magnet measurement session** -- will provide C2 endpoint data
5. **Next rod swap + read** -- cumulative dose for C2 exposure period

---

## PART 3: BLOCKED / EXTERNAL DEPENDENCIES

| Task | Blocked On | Impact |
|------|-----------|--------|
| 6 | Honeywell lab temperature data (doesn't exist historically) | H/A baseline refinement, P1 update |
| 14 | NDX dose data from Kirsten (only 78/1330 mapped) | T2-1 dose-response curve, Tier 2-5 adversarial item |
| 15 | Pass-number trend resolution | Needs Task 14. Line 1 worst = lowest rigidity hypothesis |
| 16 | Actual beam pass schedule from machine | Quantitative dose rate estimates. Planning schedule available but insufficient |
| T2-1 | Task 14 | If NDX shows monotonic dose-response, paper becomes PRL candidate |
| T3-5 | Task 6 + Beta config measurement approach | H-plate Halbach configuration analysis |
| April OSLs | Landauer processing time | C2 dosimetry cross-check |

---

## PART 4: UPCOMING / PLANNED

| Item | Target | Dependencies |
|------|--------|-------------|
| **Build presentation slides** | Before June 2 | TALK_PLAN.md ready; need actual slides |
| **Meeting with Rossi + Shepherd** | Monday (today/tomorrow?) | Show tech note draft + outline |
| **Co-author review of Tech Note** | Before submission | Need to distribute draft |
| **Compile Tech Note in Overleaf** | Before submission | main.tex ready |
| **Campaign 2 endpoint measurement** | When magnets come out of tunnel | Second exposure data |
| **Campaign 2 cumulative analysis** | After C2 endpoint | Test linear/saturation hypothesis |

---

## PART 5: DEFERRED / NOT USEFUL

| Task | Reason |
|------|--------|
| 23. NL&SL survey data | Covers 2023-2024, not our 2025 run period |
| T3-4. Neutron spectrum simulation | Not started; needs physics input + BDSIM setup |

---

## PART 6: GAP ANALYSIS -- POTENTIAL HOLES

### Gaps in C1 Analysis

1. ~~**Alderman + Miyahara PDFs still missing**~~. RESOLVED 2026-05-19: both PDFs uploaded to `Reference_Sources/`. All 10/10 reference PDFs now verified.

2. **H-plate and A-sample analysis is limited by design**. The Y-plate differential is gain-immune; H/A are not. We correctly explain this, but a reviewer could still push on "why didn't H/A confirm?" The answer (gain systematic overwhelms 0.2% signal) is solid but could be strengthened if Task 6 ever unblocks.

3. **No April 2026 Landauer OSL data yet**. The 11 borderline April rod readings (2.0-2.8 krad) cannot be cross-checked. They may be real or noise. This is a known gap, pending Landauer.

4. **Task 14 (NDX mapping) is the single biggest blocked item**. It prevents T2-1 (dose-response curve) and Tier 2-5 (adversarial review). If Kirsten provides the full NDX mapping, the study could potentially reach PRL-level significance. This has been blocked since at least April.

5. **No independent temperature measurement for C1**. The probe bias rests on N=2 cross-checks. We've been transparent about this (Section 5.2, Q6 in talk plan). Task 6 (Honeywell) would help but historical data doesn't exist. For C2, independent logging was recommended.

6. **R-636 (Y-39 incident rod) provenance**. We know it was accidentally left from the Sep 10 swap, found in January. Its 3.7 krad reading is consistent with ~1 week of beam. But do we have documentation of the incident beyond memory notes? Should this be in the Tech Note?

### Gaps in C2 Analysis

7. **C2 rod readings are RAW, not Kirsten-processed**. Our decision tree is a reasonable approximation, but Kirsten's AIdata pipeline applies cross-wavelength averaging and proper calibration. The 3 high-dose readings near the Low-range limit (R-746 at 39.4 krad) particularly benefit from Kirsten's processing.

8. **Y-17 dose estimate uncertainty**. R-746 Low@600 = 39.4 krad (at limit), High@600 = 56.6 krad. We cascade to High, giving 566 Gy. But the two estimates (394 vs 567 Gy) differ by 44%. Kirsten's cross-wavelength method would narrow this.

9. **No C2 neutron data yet**. January OSLs show zero neutron (expected for shutdown). April OSLs (when they arrive) will provide the first C2 neutron readings. Without neutron data, we can't do dose-degradation correlations for C2.

10. **11 borderline April rods (2.0-2.8 krad) are ambiguous**. Without April OSLs, we can't distinguish noise from real dose. Some (at known beam loss locations like Hn-37) may be real; others (at quiet arc locations) are likely noise.

11. **C2 > C1 dose ratios at some locations (Y-40 = 3.1x, Hn-8 = 2.1x)**. These suggest different beam loss patterns at 0.69 GeV, but we have no beam loss simulation to confirm. Worth monitoring as energy increases to 2.12 GeV.

### Gaps in Presentation/Publication

12. **Slides not yet built** for the June 2 talk. TALK_PLAN.md and TALK_OUTLINE.md are comprehensive, but actual slide construction hasn't started.

13. **Co-author review hasn't happened yet**. The Tech Note is ready but hasn't been circulated. The meeting with Rossi + Shepherd is the next step.

14. **No Overleaf compile yet**. main.tex exists locally but hasn't been tested in Overleaf (biblatex/biber dependency, figure paths, etc.).

15. ~~**C2 rod results not yet in Tech Note**~~. RESOLVED: C2 will NOT be included in the Tech Note. Campaign 2 is ongoing with more data coming; it will be a separate analysis.

### Minor / Low-Priority Gaps

16. **Beta H-plate config (antiparallel) is absent from tunnel data** (N=0). This is the most interesting Halbach proxy for radiation damage studies. Multipole contamination makes Helmholtz measurement unreliable. A different measurement approach is needed.

17. **No beam loss simulation (BDSIM/GEANT4)**. T3-4 was identified but never started. Would connect rod dosimetry to accelerator physics models and predict bore-surface doses for FFA design.

18. **back_of_envelope_degradation_estimates.md** exists as informal notes. If the user ever wants to formalize lifetime projections, this needs proper simulation backing (especially the bore-surface dose multiplier).

---

## PART 7: FILE INVENTORY SUMMARY

### Scripts (19 analysis scripts)
- `Cleanup_Claude/`: manager_summary_v3.py, v5_polish.py, presentation_plots.py, time_series_evolution.py, unexposed_vs_exposed.py, gain_systematic_analysis.py, temperature_corrected_analysis.py, lab_ha_analysis.py, build_dose_map.py, export_data_package.py
- `Cleanup_Claude/Rod_Dosimetry/`: rod_mapping.py, parse_rod_spreadsheet.py, parse_aidata.py, build_merged_dose.py, rod_dose_correlation.py, rod_uncertainty_analysis.py, thermal_spike_comparison.py, rod_crosscheck.py, rod_correlation.py
- `2026_Data_Run/`: campaign2_quality_check.py, c2_rod_analysis.py, c2_rod_plate_mapping.py, c2_dosimetry_analysis.py
- `IPAC26_Magnet_LDRD/`: make_f1.py, make_f2.py, make_f4.py
- `Data_Package/06_Scripts/`: verify_results.py, export_data_package.py + subdirs

### Data Files
- Raw: 10 Landauer OSL spreadsheets, rod spreadsheets, Teslameter/Helmholtz .dat files (in zips + extracted)
- Processed: 17 CSVs in Data_Package, plus Analysis/ CSVs for C2
- Plots: 16 presentation PNGs, 9 dosimetry, 7 time series, 7 rod correlation, 3 unexposed, 3 IPAC26, 4 C2

### Documentation
- Tech Note: main.tex (~2840 lines) + references.bib (27 entries) + 40 figures
- CLAIMS_INVENTORY.md (55 verified claims)
- TALK_PLAN.md (15 slides + 11 Q&A entries)
- TALK_OUTLINE.md (shareable, 15 backup slides)
- DATA_DICTIONARY.md
- 10 Reference PDFs in Reference_Sources/
- Memory files: MEMORY.md + 15 topic files (7 active, 13 archived)
- `back_of_envelope_degradation_estimates.md` (informal, not for reports)
