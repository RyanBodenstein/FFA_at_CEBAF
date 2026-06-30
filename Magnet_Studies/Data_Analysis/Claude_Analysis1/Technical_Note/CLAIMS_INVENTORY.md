# Claims Inventory: Technical Note main.tex

Verified: 2026-05-12 | Verifier: Claude (automated re-run of all source scripts)

Status key: V = verified against script output, F = fixed this session, X = needs attention

---

## 1. Headline Results

| # | Claim | Value | Source | Lines | Status |
|---|-------|-------|--------|-------|--------|
| 1.1 | NdFeB-SmCo differential | -0.208% +/- 0.028%(stat) +/- 0.036%(syst) | y_plate_degradation.csv | 86, 987, 1056 | V |
| 1.2 | Statistical significance | 7.6 sigma | 0.208/0.028 | 87, 989 | V |
| 1.3 | Combined significance | 4.6 sigma | 0.208/sqrt(0.028^2+0.036^2) | 87 | V |
| 1.4 | N42EH mean | -0.252% +/- 0.036% | y_plate_degradation.csv | 1048 | V |
| 1.5 | N52SH mean | -0.170% +/- 0.036% | y_plate_degradation.csv | 1049 | V |
| 1.6 | SmCo33H mean | +0.037% +/- 0.031% | y_plate_degradation.csv | 1051 | V |
| 1.7 | SmCo35 mean | -0.044% +/- 0.031% | y_plate_degradation.csv | 1052 | V |
| 1.8 | Lab differential | -0.007% +/- 0.038% (0.2 sigma) | y_plate_degradation.csv | 88, 1116 | V |
| 1.9 | Tunnel-Lab excess | -0.202% +/- 0.047% (4.3 sigma) | computed from 1.1 and 1.8 | 89, 1121 | V |
| 1.10 | Temp scan: 23C = 4.9 sigma | 4.9 sigma | temperature_corrected_analysis.py | 746 | V |
| 1.11 | Temp scan: 25C = 9.6 sigma | 9.6 sigma | temperature_corrected_analysis.py | 751 | V |

## 2. Dosimetry Numbers

| # | Claim | Value | Source | Lines | Status |
|---|-------|-------|--------|-------|--------|
| 2.1 | Unique rod IDs | 736 | parse_rod_spreadsheet.py | 893 | V |
| 2.2 | LDRD rod rows | 1,358 | parse_rod_spreadsheet.py | 897 | V |
| 2.3 | Valid dose readings | 495 (36.5%) | parse_rod_spreadsheet.py | 897 | V |
| 2.4 | Failure rate | 63.5% | 1 - 495/1358 | 899 | V |
| 2.5 | Valid dose range | 2.0-726.1 krad | parse_rod_spreadsheet.py | (rod dosimetry section) | V |
| 2.6 | 30 tunnel plates with dose | 30 | build_merged_dose.py | (correlation section) | V |

## 3. Correlation Statistics (all updated to v3 temp correction this session)

| # | Claim | Value | Source | Lines | Status |
|---|-------|-------|--------|-------|--------|
| 3.1 | Gamma vs NdFeB mean | rho=+0.125, p=0.51, CI=[-0.25, 0.46] | rod_dose_correlation.py | 1533 | F |
| 3.2 | Gamma vs SmCo mean | rho=-0.093, p=0.63, CI=[-0.44, 0.28] | rod_dose_correlation.py | 1534 | F |
| 3.3 | Gamma vs Differential | rho=+0.210, p=0.27, CI=[-0.16, 0.53] | rod_dose_correlation.py | 1535 | V |
| 3.4 | Neutron vs NdFeB mean | rho=+0.459, p=0.011, CI=[0.12, 0.70] | rod_dose_correlation.py | 1537 | V |
| 3.5 | Neutron vs SmCo mean | rho=+0.089, p=0.64, CI=[-0.28, 0.44] | rod_dose_correlation.py | 1538 | F |
| 3.6 | Neutron vs Differential | rho=+0.389, p=0.034, CI=[0.03, 0.66] | rod_dose_correlation.py | 1539 | V |
| 3.7 | Line-position inversion | rho=+0.601, p=0.005 | rod_dose_correlation.py | 1780 | V |

## 4. Theoretical Predictions

| # | Claim | Value | Source | Lines | Status |
|---|-------|-------|--------|-------|--------|
| 4.1 | B-10(n,alpha) predicted loss | -0.001% (1.08e-3%) | thermal_spike_comparison.py | ~2098 | V |
| 4.2 | Measured NdFeB loss | -0.211% | thermal_spike_comparison.py | ~2100 | V |
| 4.3 | Measured/predicted ratio | ~196x | thermal_spike_comparison.py | ~2102 | V |
| 4.4 | Dy fraction of RE capture | 98% (0.414/0.421) | thermal_spike_comparison.py | 2217 | V |
| 4.5 | Sm capture cross-section | 51.8 cm^-1 | thermal_spike_comparison.py | 2217 area | V |
| 4.6 | Spike volume ratio SmCo/NdFeB | 1.86 | thermal_spike_comparison.py | ~1998 | V |
| 4.7 | Anisotropy ratio SmCo/NdFeB | 3.6 | thermal_spike_comparison.py | ~2000 | V |
| 4.8 | Combined SmCo resistance | 6.6x | thermal_spike_comparison.py | ~2002 | V |

## 5. Systematic Uncertainties

| # | Claim | Value | Source | Lines | Status |
|---|-------|-------|--------|-------|--------|
| 5.1 | Gain systematic (cleaned) | +/-0.124% | gain_systematic_analysis.py | 1042 | V |
| 5.2 | Gain systematic (uncleaned) | +/-0.248% | gain_systematic_analysis.py | 1042 | V |
| 5.3 | Temperature systematic | +/-0.033% | temperature_corrected_analysis.py | 1060 | V |
| 5.4 | Alpha uncertainty systematic | +/-0.014% | temperature_corrected_analysis.py | 1061 | V |
| 5.5 | Total systematic (differential) | +/-0.036% | sqrt(0.033^2 + 0.014^2) | 1061 | V |
| 5.6 | Probe bias (v3) | +0.8C | temperature_corrected_analysis.py | ~680 | V |
| 5.7 | Temp coeff N42EH | -0.10 %/C | Allstar spec sheet | 261 | V |
| 5.8 | Temp coeff N52SH | -0.11 %/C | Allstar spec sheet | 262 | V |
| 5.9 | Temp coeff SmCo | -0.040 %/C | Allstar spec sheet | 263-264 | V |
| 5.10 | Differential temp sensitivity | 0.066 %/C | computed: mean_NdFeB_alpha - mean_SmCo_alpha | 728-730 | V |

## 6. Campaign 2 Numbers

| # | Claim | Value | Source | Lines | Status |
|---|-------|-------|--------|-------|--------|
| 6.1 | Matched samples | 118/120 | campaign2_quality_check.py | (C2 section) | V |
| 6.2 | Fleet offset from C1 | ~-0.16% | campaign2_quality_check.py | (C2 section) | V |
| 6.3 | C2-C1 differential residual | -0.033 +/- 0.109% | campaign2_quality_check.py | (C2 section) | V |
| 6.4 | Temperature range | 20.9-29.5C (8.6C swing) | campaign2_quality_check.py | (C2 section) | V |
| 6.5 | Delta slug median | 0.061 mT | campaign2_quality_check.py | (C2 section) | V |
| 6.6 | Y-14 corrected repeatability | 0.06-0.27% | campaign2_quality_check.py | (C2 section) | V |
| 6.7 | Missing: Y-6-2, Y-17-3, Y-23-1 | data gaps | campaign2_quality_check.py | (C2 section) | V |

## 7. Sample/Study Scale

| # | Claim | Value | Source | Lines | Status |
|---|-------|-------|--------|-------|--------|
| 7.1 | Y-plates tunnel | 30 | data inventory | multiple | V |
| 7.2 | Y-plates lab | 9 | data inventory | multiple | V |
| 7.3 | Material slots per plate | 4 | experimental design | 226 | V |
| 7.4 | Tunnel samples (non-outlier) | 118 | y_plate_degradation.csv | multiple | V |
| 7.5 | Lab samples (non-outlier) | 36 | y_plate_degradation.csv | (computed) | V |
| 7.6 | Outlier samples | 2 (Y-34-4, Y-40-4) | manager_summary_v3.py | ~528 | V |
| 7.7 | "World's largest" | N=39 plates, 4 materials, real accelerator | comparison to prior work | 2340 | V |

## 8. Literature Comparisons

| # | Claim | Value | Source | Lines | Status |
|---|-------|-------|--------|-------|--------|
| 8.1 | Simos (2018) N=3 samples | 3 magnets, Mrad-Grad level | Simos IEEE paper | 177 | V (from ref) |
| 8.2 | Alderman multi-source study | X-ray null (280 Mrad), gamma null (700 Mrad), fast neutron damage (>2e13 n/cm2), thermal null (3e12 n/cm2) | Alderman NIM A 481 (2002) | 882, 1648, 2339 | V (from ref, 2026-05-19 corrected: was described as gamma-only, now full 4-source study) |
| 8.2b | Miyahara 10 MeV neutron study | 0.6% at 1.1 kGy, 6.9% at 3.7 kGy, 47.3% at 7.4 kGy; non-continuous 14% less damage | Miyahara NIM B 268 (2010) | 1654, 2353 | V (from ref, added 2026-05-19) |
| 8.3 | APS LS-290 threshold | 1% at 760 Gy - 113 kGy | APS report | (refs section) | V (from ref) |
| 8.4 | Our dose vs Alderman gamma null | 300x below | 23451 Gy vs 7 MGy gamma null (not the full Alderman study) | 1655 | V (updated 2026-05-19) |

---

## Corrections Made This Session (2026-05-12)

1. **5-sigma claims**: 4 text locations claimed "exceeds 5 sigma for 23-25C" but 23C = 4.9 sigma. Changed to "4.9 sigma or above" (lines 661, 669, 741, 2511).

2. **Correlation table**: 3 of 6 rows had stale pre-temperature-fix values:
   - Gamma NdFeB: 0.270 -> 0.125 (line 1533)
   - Gamma SmCo: +0.125 -> -0.093 (line 1534)
   - Neutron SmCo: +0.075 -> +0.089 (line 1538)
   Root cause: table was never updated after v3 per-date temperature correction.

3. **Body text SmCo correlations**: Updated to match corrected table (lines 1483-1484, 1598).

4. **Epistemic language**: "proves" -> "demonstrates" (2 instances), "definitive proof" -> "strong evidence" (1 instance).

---

## Items NOT Verified (blocked or out of scope)

- Line-position inversion rho=0.601: VERIFIED (re-run confirmed p=0.0051)
- H-plate and A-sample analysis (not part of current Y-plate analysis pipeline)
- Individual rod dose values (too many to verify individually; pipeline validated)
- Literature reference details (verified in prior sessions, refs in Reference_Sources/)
