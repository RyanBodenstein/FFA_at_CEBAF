#!/usr/bin/env python3
"""
Standalone Verification Script for LDRD FFA@CEBAF Data Package

This script reads ONLY the data package CSVs (no analysis code imports)
and reproduces all headline results from scratch. It serves as an
independent check that the published CSVs are internally consistent
and sufficient for reproduction.

Usage:
    cd Data_Package/
    python3 06_Scripts/verify_results.py

Requirements: numpy, scipy (standard scientific Python)
"""

import csv
import os
import sys
import numpy as np
from scipy import stats
from collections import defaultdict

# ── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.dirname(SCRIPT_DIR)


def load_csv(relpath):
    """Load a CSV file relative to the data package root."""
    path = os.path.join(PACKAGE_DIR, relpath)
    with open(path) as f:
        return list(csv.DictReader(f))


# ══════════════════════════════════════════════════════════════════════════════
# 1. HEADLINE DIFFERENTIAL from y_plate_degradation.csv
# ══════════════════════════════════════════════════════════════════════════════

def verify_headline_differential():
    """
    Reproduce the NdFeB-SmCo differential: -0.208% +/- 0.028% (7.6 sigma).

    Method:
      1. Load y_plate_degradation.csv
      2. Filter to tunnel samples, exclude outliers
      3. For each plate, compute:
           NdFeB_mean = mean(N42EH, N52SH pct_change)
           SmCo_mean  = mean(SmCo33H, SmCo35 pct_change)
           differential = NdFeB_mean - SmCo_mean
      4. Report mean and SEM of the 30 per-plate differentials
    """
    rows = load_csv('02_Magnetic_Measurements/y_plate_degradation.csv')

    # Step 1: Filter
    tunnel = [r for r in rows
              if r['environment'] == 'tunnel'
              and r['is_outlier'] == 'False']

    # Step 2: Group by plate
    plates = defaultdict(dict)
    for r in tunnel:
        plate = int(r['plate'])
        mat = r['material']
        pct = float(r['pct_change'])
        plates[plate][mat] = pct

    # Step 3: Compute per-plate differentials
    diffs = []
    for plate in sorted(plates.keys()):
        mats = plates[plate]
        nd_vals = [mats[m] for m in ['N42EH', 'N52SH'] if m in mats]
        sm_vals = [mats[m] for m in ['SmCo33H', 'SmCo35'] if m in mats]
        if nd_vals and sm_vals:
            nd_mean = np.mean(nd_vals)
            sm_mean = np.mean(sm_vals)
            diffs.append(nd_mean - sm_mean)

    # Step 4: Statistics
    diff_mean = np.mean(diffs)
    diff_sem = np.std(diffs, ddof=1) / np.sqrt(len(diffs))
    diff_sig = abs(diff_mean) / diff_sem

    return {
        'differential_pct': diff_mean,
        'sem_pct': diff_sem,
        'significance_sigma': diff_sig,
        'n_plates': len(diffs),
        'per_plate_diffs': diffs,
    }


# ══════════════════════════════════════════════════════════════════════════════
# 2. PER-MATERIAL MEANS
# ══════════════════════════════════════════════════════════════════════════════

def verify_per_material_means():
    """
    Reproduce per-material mean percent changes for tunnel Y-plates.

    Expected: N42EH -0.252%, N52SH -0.170%, SmCo33H +0.037%, SmCo35 -0.044%
    """
    rows = load_csv('02_Magnetic_Measurements/y_plate_degradation.csv')
    tunnel = [r for r in rows
              if r['environment'] == 'tunnel'
              and r['is_outlier'] == 'False']

    mat_groups = defaultdict(list)
    for r in tunnel:
        mat_groups[r['material']].append(float(r['pct_change']))

    results = {}
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        vals = mat_groups[mat]
        results[mat] = {
            'mean_pct': np.mean(vals),
            'sem_pct': np.std(vals, ddof=1) / np.sqrt(len(vals)),
            'n': len(vals),
        }
    return results


# ══════════════════════════════════════════════════════════════════════════════
# 3. LAB CONTROL DIFFERENTIAL
# ══════════════════════════════════════════════════════════════════════════════

def verify_lab_differential():
    """
    Reproduce lab control differential: -0.007% +/- 0.038% (0.2 sigma).

    Same computation as tunnel, but filtered to environment='lab'.
    """
    rows = load_csv('02_Magnetic_Measurements/y_plate_degradation.csv')
    lab = [r for r in rows if r['environment'] == 'lab']

    plates = defaultdict(dict)
    for r in lab:
        plate = int(r['plate'])
        mat = r['material']
        pct = float(r['pct_change'])
        plates[plate][mat] = pct

    diffs = []
    for plate in sorted(plates.keys()):
        mats = plates[plate]
        nd_vals = [mats[m] for m in ['N42EH', 'N52SH'] if m in mats]
        sm_vals = [mats[m] for m in ['SmCo33H', 'SmCo35'] if m in mats]
        if nd_vals and sm_vals:
            diffs.append(np.mean(nd_vals) - np.mean(sm_vals))

    lab_mean = np.mean(diffs)
    lab_sem = np.std(diffs, ddof=1) / np.sqrt(len(diffs))
    lab_sig = abs(lab_mean) / lab_sem if lab_sem > 0 else 0

    return {
        'differential_pct': lab_mean,
        'sem_pct': lab_sem,
        'significance_sigma': lab_sig,
        'n_plates': len(diffs),
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4. TUNNEL-LAB EXCESS
# ══════════════════════════════════════════════════════════════════════════════

def verify_tunnel_lab_excess(tunnel_result, lab_result):
    """
    Reproduce tunnel-lab excess: -0.202% +/- 0.047% (4.3 sigma).

    excess = tunnel_differential - lab_differential
    sem = sqrt(tunnel_sem^2 + lab_sem^2)
    """
    excess = tunnel_result['differential_pct'] - lab_result['differential_pct']
    sem = np.sqrt(tunnel_result['sem_pct']**2 + lab_result['sem_pct']**2)
    sig = abs(excess) / sem if sem > 0 else 0

    return {
        'excess_pct': excess,
        'sem_pct': sem,
        'significance_sigma': sig,
    }


# ══════════════════════════════════════════════════════════════════════════════
# 5. DOSE-DEGRADATION CORRELATIONS
# ══════════════════════════════════════════════════════════════════════════════

def verify_dose_correlations():
    """
    Reproduce Spearman rank correlations between dose and degradation.

    Expected (6 key values):
      Gamma vs NdFeB mean:    rho=+0.125, p=0.51
      Gamma vs SmCo mean:     rho=-0.093, p=0.63
      Gamma vs Differential:  rho=+0.210, p=0.27
      Neutron vs NdFeB mean:  rho=+0.459, p=0.011
      Neutron vs SmCo mean:   rho=+0.089, p=0.64
      Neutron vs Differential: rho=+0.389, p=0.034

    Method: Spearman on log10(dose) vs degradation metric
    """
    rows = load_csv('03_Dosimetry/dose_vs_degradation.csv')

    results = {}
    for dose_type, dose_col, label in [
        ('gamma', 'ai_photon_gy', 'AIdata photon (Gy)'),
        ('neutron', 'ai_neutron_rem', 'AIdata neutron (rem)'),
    ]:
        doses = []
        ndfeb = []
        smco = []
        diff = []
        for r in rows:
            d = float(r[dose_col])
            if d > 0:
                doses.append(np.log10(d))
                ndfeb.append(float(r['ndfeb_mean_pct']))
                smco.append(float(r['smco_mean_pct']))
                diff.append(float(r['intra_plate_diff']))

        for metric_name, vals in [
            ('ndfeb_mean', ndfeb),
            ('smco_mean', smco),
            ('differential', diff),
        ]:
            rho, p = stats.spearmanr(doses, vals)
            key = '%s_vs_%s' % (dose_type, metric_name)
            results[key] = {'rho': rho, 'p': p, 'n': len(doses)}

    return results


# ══════════════════════════════════════════════════════════════════════════════
# 6. COMBINED UNCERTAINTY
# ══════════════════════════════════════════════════════════════════════════════

def verify_combined_uncertainty(stat_sem):
    """
    Reproduce combined uncertainty: 0.045% = sqrt(0.028^2 + 0.033^2 + 0.014^2).

    Components:
      - Statistical: SEM of 30 per-plate differentials (0.028%)
      - Temperature systematic: 0.033% (half-range of v2-v3 spread)
      - Alpha uncertainty: 0.014% (propagated from manufacturer spec uncertainty)
      - Total systematic: sqrt(0.033^2 + 0.014^2) = 0.036%
      - Combined: sqrt(stat^2 + syst^2)

    Note: Gain systematic (0.124%) cancels in intra-plate differential.
    """
    temp_syst = 0.033
    alpha_syst = 0.014
    total_syst = np.sqrt(temp_syst**2 + alpha_syst**2)
    combined = np.sqrt(stat_sem**2 + total_syst**2)
    combined_sig = 0.208 / combined  # using rounded headline value

    return {
        'stat_sem': stat_sem,
        'temp_systematic': temp_syst,
        'alpha_systematic': alpha_syst,
        'total_systematic': total_syst,
        'combined_uncertainty': combined,
        'combined_significance_sigma': combined_sig,
    }


# ══════════════════════════════════════════════════════════════════════════════
# MAIN: Run all verifications and report
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("LDRD FFA@CEBAF Data Package — Independent Verification")
    print("=" * 70)
    print()

    all_pass = True

    def check(label, computed, expected, tol=0.01):
        nonlocal all_pass
        match = abs(computed - expected) < tol
        status = "PASS" if match else "FAIL"
        if not match:
            all_pass = False
        print("  %-45s %8.4f  (expected %8.4f)  [%s]" %
              (label, computed, expected, status))
        return match

    # ── 1. Headline Differential ──────────────────────────────────────────

    print("1. HEADLINE DIFFERENTIAL")
    print("   Source: 02_Magnetic_Measurements/y_plate_degradation.csv")
    tunnel = verify_headline_differential()
    check("NdFeB-SmCo differential (%)", tunnel['differential_pct'], -0.208, 0.001)
    check("SEM (%)", tunnel['sem_pct'], 0.028, 0.001)
    check("Significance (sigma)", tunnel['significance_sigma'], 7.6, 0.1)
    print("   N = %d plates" % tunnel['n_plates'])
    print()

    # ── 2. Per-Material Means ─────────────────────────────────────────────

    print("2. PER-MATERIAL MEANS")
    mats = verify_per_material_means()
    check("N42EH mean (%)", mats['N42EH']['mean_pct'], -0.252, 0.001)
    check("N52SH mean (%)", mats['N52SH']['mean_pct'], -0.170, 0.001)
    check("SmCo33H mean (%)", mats['SmCo33H']['mean_pct'], 0.037, 0.001)
    check("SmCo35 mean (%)", mats['SmCo35']['mean_pct'], -0.044, 0.001)
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        print("   %s: N=%d, SEM=%.3f%%" %
              (mat, mats[mat]['n'], mats[mat]['sem_pct']))
    print()

    # ── 3. Lab Control ────────────────────────────────────────────────────

    print("3. LAB CONTROL DIFFERENTIAL")
    lab = verify_lab_differential()
    check("Lab differential (%)", lab['differential_pct'], -0.007, 0.001)
    check("Lab SEM (%)", lab['sem_pct'], 0.038, 0.001)
    check("Lab significance (sigma)", lab['significance_sigma'], 0.2, 0.1)
    print("   N = %d plates" % lab['n_plates'])
    print()

    # ── 4. Tunnel-Lab Excess ──────────────────────────────────────────────

    print("4. TUNNEL-LAB EXCESS")
    excess = verify_tunnel_lab_excess(tunnel, lab)
    check("Tunnel-Lab excess (%)", excess['excess_pct'], -0.202, 0.001)
    check("Excess SEM (%)", excess['sem_pct'], 0.047, 0.001)
    check("Excess significance (sigma)", excess['significance_sigma'], 4.3, 0.1)
    print()

    # ── 5. Dose-Degradation Correlations ──────────────────────────────────

    print("5. DOSE-DEGRADATION CORRELATIONS")
    print("   Source: 03_Dosimetry/dose_vs_degradation.csv")
    corr = verify_dose_correlations()
    check("Gamma vs NdFeB rho", corr['gamma_vs_ndfeb_mean']['rho'], 0.125, 0.001)
    check("Gamma vs SmCo rho", corr['gamma_vs_smco_mean']['rho'], -0.093, 0.001)
    check("Gamma vs Differential rho", corr['gamma_vs_differential']['rho'], 0.210, 0.001)
    check("Neutron vs NdFeB rho", corr['neutron_vs_ndfeb_mean']['rho'], 0.459, 0.001)
    check("Neutron vs SmCo rho", corr['neutron_vs_smco_mean']['rho'], 0.089, 0.001)
    check("Neutron vs Differential rho", corr['neutron_vs_differential']['rho'], 0.389, 0.001)
    print("   N = %d plates with dose data" % corr['neutron_vs_differential']['n'])
    print()

    # ── 6. Combined Uncertainty ───────────────────────────────────────────

    print("6. COMBINED UNCERTAINTY")
    unc = verify_combined_uncertainty(tunnel['sem_pct'])
    check("Total systematic (%)", unc['total_systematic'], 0.036, 0.001)
    check("Combined uncertainty (%)", unc['combined_uncertainty'], 0.045, 0.002)
    check("Combined significance (sigma)", unc['combined_significance_sigma'], 4.6, 0.1)
    print("   Components: stat=%.3f%%, temp=%.3f%%, alpha=%.3f%%" %
          (unc['stat_sem'], unc['temp_systematic'], unc['alpha_systematic']))
    print()

    # ── Summary ───────────────────────────────────────────────────────────

    print("=" * 70)
    if all_pass:
        print("ALL CHECKS PASSED — Data package reproduces all headline results.")
    else:
        print("SOME CHECKS FAILED — See details above.")
    print("=" * 70)

    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
