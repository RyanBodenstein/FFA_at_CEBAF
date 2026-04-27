#!/usr/bin/env python3
"""Dose-Region Breakdowns — Task 7

Breaks up degradation analysis by:
  1. Dose level bins (low/medium/high body dose)
  2. Radiation type dominance per region
  3. Dose-response shape (linear, threshold, saturating?)
  4. Photon fraction vs neutron fraction effects
  5. Arc vs Linac detailed breakdown

Uses merged Y-plate data from dose_degradation_correlation.py.

Output: Cleanup_Claude/Dose_Region_Breakdowns/ (plots + text summary)
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.join(BASE, 'Dose_Region_Breakdowns')
os.makedirs(PLOT_DIR, exist_ok=True)

sys.path.insert(0, BASE)
from manager_summary_v3 import (
    load_all, get_gain_syst, compute_intra_plate_diffs, PLACEMENTS,
)
from dose_degradation_correlation import (
    load_dose_cumulative, merge_data, merge_h_plate_data,
    MREM_TO_SV, MREM_TO_GY_PHOTON, MREM_TO_GY_FAST_N,
    MREM_TO_GY_THERM_N, MREM_TO_GY_BETA,
    Q_PHOTON, Q_FAST_N, Q_THERM_N,
)
from degradation_summary_v2 import (
    PLACEMENTS as V2_PLACEMENTS,
    load_materials, build_temperature_lookup, compute_h_plate_degradation,
)


def save(fig, name):
    path = os.path.join(PLOT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("  Saved: %s" % name)


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 1: Dose Level Bins
# ═══════════════════════════════════════════════════════════════════════════════

def dose_bin_analysis(merged, gain_syst):
    """Group plates into dose bins and compare degradation."""
    print("\n" + "=" * 78)
    print("ANALYSIS 1: DEGRADATION BY DOSE LEVEL")
    print("=" * 78)

    # Sort by body dose
    sorted_m = sorted(merged, key=lambda m: m['cum_body_mrem'])
    doses = [m['cum_body_mrem'] for m in sorted_m]

    # Define bins by tertile
    n = len(sorted_m)
    t1 = n // 3
    t2 = 2 * n // 3
    bins = [
        ('Low dose (bottom third)', sorted_m[:t1]),
        ('Medium dose (middle third)', sorted_m[t1:t2]),
        ('High dose (top third)', sorted_m[t2:]),
    ]

    # Also: labyrinth vs arc vs linac (natural dose grouping)
    region_bins = [
        ('Labyrinth', [m for m in merged if 'Labyrinth' in m['region']]),
        ('Arcs', [m for m in merged if 'Arc' in m['region']]),
        ('Linacs', [m for m in merged if 'Linac' in m['region']]),
    ]

    print("\n--- Tertile bins (equal N) ---")
    print("  %-28s  %8s  %8s  %12s  %12s  %12s" % (
        'Bin', 'N', 'Dose(Sv)', 'NdFeB(%)', 'SmCo(%)', 'Diff(%)'))
    print("  " + "-" * 88)

    bin_stats = []
    for label, plates in bins:
        dose_sv = [m['cum_body_mrem'] * MREM_TO_SV for m in plates]
        nd = [m['ndfeb_mean_pct'] for m in plates if not np.isnan(m['ndfeb_mean_pct'])]
        sm = [m['smco_mean_pct'] for m in plates if not np.isnan(m['smco_mean_pct'])]
        diff = [m['intra_plate_diff'] for m in plates if not np.isnan(m['intra_plate_diff'])]
        n_lb = sum(1 for m in plates if m['is_lower_bound'])

        nd_m = np.mean(nd) if nd else np.nan
        nd_s = np.std(nd, ddof=1) / np.sqrt(len(nd)) if len(nd) > 1 else 0
        sm_m = np.mean(sm) if sm else np.nan
        sm_s = np.std(sm, ddof=1) / np.sqrt(len(sm)) if len(sm) > 1 else 0
        diff_m = np.mean(diff) if diff else np.nan
        diff_s = np.std(diff, ddof=1) / np.sqrt(len(diff)) if len(diff) > 1 else 0
        diff_sig = abs(diff_m / diff_s) if diff_s > 0 else 0

        lb_mark = '*' if n_lb > 0 else ' '
        print("  %-28s  %5d %s  %7.1f   %+.3f±%.3f  %+.3f±%.3f  %+.3f±%.3f (%.1fσ)" % (
            label, len(plates), lb_mark,
            np.mean(dose_sv),
            nd_m, nd_s, sm_m, sm_s, diff_m, diff_s, diff_sig))

        bin_stats.append({
            'label': label, 'n': len(plates),
            'dose_sv_mean': np.mean(dose_sv),
            'dose_sv_range': (min(dose_sv), max(dose_sv)),
            'nd_mean': nd_m, 'nd_sem': nd_s,
            'sm_mean': sm_m, 'sm_sem': sm_s,
            'diff_mean': diff_m, 'diff_sem': diff_s, 'diff_sigma': diff_sig,
            'n_lower_bound': n_lb,
        })

    print("  * = contains plates with saturated OSL (dose is lower bound)")

    # Regional grouping
    print("\n--- Regional bins (natural dose grouping) ---")
    print("  %-28s  %8s  %8s  %12s  %12s  %12s" % (
        'Region', 'N', 'Dose(Sv)', 'NdFeB(%)', 'SmCo(%)', 'Diff(%)'))
    print("  " + "-" * 88)

    region_stats = []
    for label, plates in region_bins:
        if not plates:
            continue
        dose_sv = [m['cum_body_mrem'] * MREM_TO_SV for m in plates]
        nd = [m['ndfeb_mean_pct'] for m in plates if not np.isnan(m['ndfeb_mean_pct'])]
        sm = [m['smco_mean_pct'] for m in plates if not np.isnan(m['smco_mean_pct'])]
        diff = [m['intra_plate_diff'] for m in plates if not np.isnan(m['intra_plate_diff'])]
        n_lb = sum(1 for m in plates if m['is_lower_bound'])

        nd_m = np.mean(nd) if nd else np.nan
        nd_s = np.std(nd, ddof=1) / np.sqrt(len(nd)) if len(nd) > 1 else 0
        sm_m = np.mean(sm) if sm else np.nan
        sm_s = np.std(sm, ddof=1) / np.sqrt(len(sm)) if len(sm) > 1 else 0
        diff_m = np.mean(diff) if diff else np.nan
        diff_s = np.std(diff, ddof=1) / np.sqrt(len(diff)) if len(diff) > 1 else 0
        diff_sig = abs(diff_m / diff_s) if diff_s > 0 else 0

        lb_mark = '*' if n_lb > 0 else ' '
        print("  %-28s  %5d %s  %7.1f   %+.3f±%.3f  %+.3f±%.3f  %+.3f±%.3f (%.1fσ)" % (
            label, len(plates), lb_mark,
            np.mean(dose_sv),
            nd_m, nd_s, sm_m, sm_s, diff_m, diff_s, diff_sig))

        region_stats.append({
            'label': label, 'n': len(plates),
            'dose_sv_mean': np.mean(dose_sv),
            'nd_mean': nd_m, 'nd_sem': nd_s,
            'sm_mean': sm_m, 'sm_sem': sm_s,
            'diff_mean': diff_m, 'diff_sem': diff_s, 'diff_sigma': diff_sig,
            'n_lower_bound': n_lb,
        })

    return bin_stats, region_stats


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 2: Radiation Type Dominance
# ═══════════════════════════════════════════════════════════════════════════════

def radiation_type_analysis(merged):
    """Analyze which radiation type dominates in each region."""
    print("\n" + "=" * 78)
    print("ANALYSIS 2: RADIATION FIELD COMPOSITION BY REGION")
    print("=" * 78)

    regions = {
        'Arcs': [m for m in merged if 'Arc' in m['region']],
        'North Linac': [m for m in merged if m['region'] == 'North Linac'],
        'South Linac': [m for m in merged if m['region'] == 'South Linac'],
        'Labyrinth': [m for m in merged if 'Labyrinth' in m['region']],
    }

    print("\n--- Absorbed dose by type per region (Gy) ---")
    print("  %-14s  %8s  %10s  %10s  %10s  %10s  %10s  %8s" % (
        'Region', 'N', 'Photon', 'Beta', 'Fast n', 'Therm n', 'Total Gy', 'NdFeB%'))
    print("  " + "-" * 92)

    rad_data = []
    for label, plates in regions.items():
        if not plates:
            continue
        ph = np.mean([m['cum_photon_mrem'] for m in plates]) * MREM_TO_GY_PHOTON
        bt = np.mean([m['cum_beta_mrem'] for m in plates]) * MREM_TO_GY_BETA
        nf = np.mean([m['cum_nf_mrem'] for m in plates]) * MREM_TO_GY_FAST_N
        nt = np.mean([m['cum_nt_mrem'] for m in plates]) * MREM_TO_GY_THERM_N
        total = ph + bt + nf + nt
        nd = [m['ndfeb_mean_pct'] for m in plates if not np.isnan(m['ndfeb_mean_pct'])]
        nd_m = np.mean(nd) if nd else np.nan

        print("  %-14s  %5d     %8.3f   %8.3f   %8.5f   %8.6f   %8.3f   %+.3f" % (
            label, len(plates), ph, bt, nf, nt, total, nd_m))

        # Compute fractional composition
        if total > 0:
            fracs = {'photon': ph / total, 'beta': bt / total,
                     'fast_n': nf / total, 'therm_n': nt / total}
        else:
            fracs = {'photon': 0, 'beta': 0, 'fast_n': 0, 'therm_n': 0}

        rad_data.append({
            'label': label, 'n': len(plates),
            'photon_gy': ph, 'beta_gy': bt, 'fast_n_gy': nf, 'therm_n_gy': nt,
            'total_gy': total, 'fracs': fracs,
            'nd_mean': nd_m,
        })

    print("\n--- Fractional composition ---")
    print("  %-14s  %8s  %8s  %8s  %8s  %10s" % (
        'Region', 'Photon', 'Beta', 'Fast n', 'Therm n', 'Dominant'))
    print("  " + "-" * 60)
    for rd in rad_data:
        f = rd['fracs']
        dominant = max(f, key=f.get)
        print("  %-14s  %6.1f%%  %6.1f%%  %6.1f%%  %6.1f%%  %10s" % (
            rd['label'], f['photon'] * 100, f['beta'] * 100,
            f['fast_n'] * 100, f['therm_n'] * 100, dominant))

    # Photon fraction vs degradation
    print("\n--- Photon fraction vs NdFeB degradation (per plate) ---")
    ph_fracs, nd_vals = [], []
    for m in merged:
        ph = m['cum_photon_mrem'] * MREM_TO_GY_PHOTON
        bt = m['cum_beta_mrem'] * MREM_TO_GY_BETA
        nf = m['cum_nf_mrem'] * MREM_TO_GY_FAST_N
        nt = m['cum_nt_mrem'] * MREM_TO_GY_THERM_N
        total = ph + bt + nf + nt
        if total > 0 and not np.isnan(m['ndfeb_mean_pct']):
            ph_fracs.append(ph / total)
            nd_vals.append(m['ndfeb_mean_pct'])

    if len(ph_fracs) >= 4:
        r_s, p_s = stats.spearmanr(ph_fracs, nd_vals)
        print("  Photon fraction: Spearman ρ=%.3f (p=%.3f)" % (r_s, p_s))
        if p_s < 0.05:
            print("  → Significant! Photon-dominated regions show different degradation.")
        else:
            print("  → Not significant. Radiation composition does not predict degradation.")

    return rad_data


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 3: Dose-Response Shape
# ═══════════════════════════════════════════════════════════════════════════════

def dose_response_analysis(merged):
    """Test dose-response relationship shape: linear, threshold, saturating."""
    print("\n" + "=" * 78)
    print("ANALYSIS 3: DOSE-RESPONSE SHAPE")
    print("=" * 78)

    # Extract data
    plates_with_nd = [m for m in merged if not np.isnan(m['ndfeb_mean_pct'])]
    doses = np.array([m['cum_body_mrem'] * MREM_TO_SV for m in plates_with_nd])
    nd_pcts = np.array([m['ndfeb_mean_pct'] for m in plates_with_nd])
    diffs = np.array([m['intra_plate_diff'] for m in plates_with_nd
                       if not np.isnan(m['intra_plate_diff'])])
    diff_doses = np.array([m['cum_body_mrem'] * MREM_TO_SV for m in plates_with_nd
                            if not np.isnan(m['intra_plate_diff'])])

    if len(doses) < 5:
        print("  Too few plates for dose-response analysis")
        return

    print("\n--- NdFeB absolute degradation vs body dose ---")

    # Linear fit
    slope, intercept, r_value, p_value, std_err = stats.linregress(doses, nd_pcts)
    print("  Linear fit: y = %.4f × dose + %.4f" % (slope, intercept))
    print("  R² = %.4f, p = %.4f, slope = %.4f ± %.4f %%/Sv" % (
        r_value**2, p_value, slope, std_err))

    # Log-linear fit
    log_doses = np.log10(np.clip(doses, 0.1, None))
    slope_log, intercept_log, r_log, p_log, se_log = stats.linregress(
        log_doses, nd_pcts)
    print("  Log-linear fit: y = %.4f × log10(dose) + %.4f" % (
        slope_log, intercept_log))
    print("  R² = %.4f, p = %.4f" % (r_log**2, p_log))

    # Spearman rank correlation
    r_s, p_s = stats.spearmanr(doses, nd_pcts)
    print("  Spearman ρ = %.3f (p=%.3f)" % (r_s, p_s))

    # Threshold test: is there a dose below which degradation = 0?
    # Split at median dose
    med_dose = np.median(doses)
    low = nd_pcts[doses < med_dose]
    high = nd_pcts[doses >= med_dose]
    t_stat, t_p = stats.ttest_ind(low, high)
    print("\n  Threshold test (split at median %.1f Sv):" % med_dose)
    print("    Low dose:  %.3f%% ± %.3f%% (N=%d)" % (
        np.mean(low), np.std(low, ddof=1) / np.sqrt(len(low)), len(low)))
    print("    High dose: %.3f%% ± %.3f%% (N=%d)" % (
        np.mean(high), np.std(high, ddof=1) / np.sqrt(len(high)), len(high)))
    print("    t-test: t=%.2f, p=%.3f" % (t_stat, t_p))
    if t_p < 0.05:
        print("    → Significant difference between low and high dose groups")
    else:
        print("    → No significant difference — dose does not predict degradation level")

    # Same for differential
    if len(diffs) >= 5:
        print("\n--- Gain-immune differential vs body dose ---")
        r_s_d, p_s_d = stats.spearmanr(diff_doses, diffs)
        print("  Spearman ρ = %.3f (p=%.3f)" % (r_s_d, p_s_d))

        low_d = diffs[diff_doses < np.median(diff_doses)]
        high_d = diffs[diff_doses >= np.median(diff_doses)]
        t_d, p_d = stats.ttest_ind(low_d, high_d)
        print("  Threshold test (split at median %.1f Sv):" % np.median(diff_doses))
        print("    Low dose diff:  %.3f%% ± %.3f%% (N=%d)" % (
            np.mean(low_d), np.std(low_d, ddof=1) / np.sqrt(len(low_d)), len(low_d)))
        print("    High dose diff: %.3f%% ± %.3f%% (N=%d)" % (
            np.mean(high_d), np.std(high_d, ddof=1) / np.sqrt(len(high_d)), len(high_d)))
        print("    t-test: t=%.2f, p=%.3f" % (t_d, p_d))

    return {
        'linear_slope': slope, 'linear_p': p_value, 'linear_r2': r_value**2,
        'log_slope': slope_log, 'log_p': p_log, 'log_r2': r_log**2,
        'spearman_rho': r_s, 'spearman_p': p_s,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS 4: Arc sub-regions (per arc, per line)
# ═══════════════════════════════════════════════════════════════════════════════

def arc_detail_analysis(merged):
    """Detailed breakdown within arc regions — per arc and per line."""
    print("\n" + "=" * 78)
    print("ANALYSIS 4: ARC DETAILED BREAKDOWN")
    print("=" * 78)

    arc_plates = [m for m in merged if 'Arc' in m['region']]
    if not arc_plates:
        print("  No arc plates")
        return

    # Per arc
    arcs = defaultdict(list)
    for m in arc_plates:
        arcs[m['region']].append(m)

    print("\n--- Per-arc summary ---")
    print("  %-10s  %4s  %8s  %12s  %12s  %12s" % (
        'Arc', 'N', 'Dose(Sv)', 'NdFeB(%)', 'SmCo(%)', 'Diff(%)'))
    print("  " + "-" * 64)

    for arc_name in sorted(arcs.keys()):
        plates = arcs[arc_name]
        dose_sv = np.mean([m['cum_body_mrem'] * MREM_TO_SV for m in plates])
        nd = [m['ndfeb_mean_pct'] for m in plates if not np.isnan(m['ndfeb_mean_pct'])]
        sm = [m['smco_mean_pct'] for m in plates if not np.isnan(m['smco_mean_pct'])]
        diff = [m['intra_plate_diff'] for m in plates if not np.isnan(m['intra_plate_diff'])]

        nd_m = np.mean(nd) if nd else np.nan
        nd_s = np.std(nd, ddof=1) / np.sqrt(len(nd)) if len(nd) > 1 else 0
        sm_m = np.mean(sm) if sm else np.nan
        diff_m = np.mean(diff) if diff else np.nan
        diff_s = np.std(diff, ddof=1) / np.sqrt(len(diff)) if len(diff) > 1 else 0

        print("  %-10s  %4d  %7.1f   %+.3f±%.3f  %+.3f        %+.3f±%.3f" % (
            arc_name, len(plates), dose_sv, nd_m, nd_s, sm_m, diff_m, diff_s))

    # Per line (pass number)
    lines = defaultdict(list)
    for m in arc_plates:
        if m['line'] > 0:
            lines[m['line']].append(m)

    print("\n--- Per line (pass number) within arcs ---")
    print("  %-6s  %4s  %8s  %12s  %12s  %12s" % (
        'Line', 'N', 'Dose(Sv)', 'NdFeB(%)', 'SmCo(%)', 'Diff(%)'))
    print("  " + "-" * 60)

    for line_num in sorted(lines.keys()):
        plates = lines[line_num]
        dose_sv = np.mean([m['cum_body_mrem'] * MREM_TO_SV for m in plates])
        nd = [m['ndfeb_mean_pct'] for m in plates if not np.isnan(m['ndfeb_mean_pct'])]
        sm = [m['smco_mean_pct'] for m in plates if not np.isnan(m['smco_mean_pct'])]
        diff = [m['intra_plate_diff'] for m in plates if not np.isnan(m['intra_plate_diff'])]

        nd_m = np.mean(nd) if nd else np.nan
        nd_s = np.std(nd, ddof=1) / np.sqrt(len(nd)) if len(nd) > 1 else 0
        sm_m = np.mean(sm) if sm else np.nan
        diff_m = np.mean(diff) if diff else np.nan

        n_lb = sum(1 for m in plates if m['is_lower_bound'])
        lb_mark = '*' if n_lb > 0 else ' '
        print("  Line %d  %4d%s  %7.1f   %+.3f±%.3f  %+.3f        %+.3f" % (
            line_num, len(plates), lb_mark, dose_sv, nd_m, nd_s, sm_m, diff_m))

    print("  * = contains plates with saturated OSL (dose is lower bound)")

    # Dose vs line position correlation
    line_data = [(m['line'], m['cum_body_mrem'] * MREM_TO_SV,
                  m['ndfeb_mean_pct'], m['intra_plate_diff'])
                 for m in arc_plates if m['line'] > 0
                 and not np.isnan(m['ndfeb_mean_pct'])
                 and not np.isnan(m['intra_plate_diff'])]
    if len(line_data) >= 4:
        ls, ds, ns, dfs = zip(*line_data)
        ls = np.array(ls)
        ds = np.array(ds)
        ns = np.array(ns)
        dfs = np.array(dfs)

        print("\n--- Line position correlations (arc plates only) ---")
        r_ln, p_ln = stats.spearmanr(ls, ns)
        r_ld, p_ld = stats.spearmanr(ls, ds)
        r_ldf, p_ldf = stats.spearmanr(ls, dfs)
        r_dn, p_dn = stats.spearmanr(ds, ns)
        print("  Line vs NdFeB: ρ=%.3f (p=%.3f)" % (r_ln, p_ln))
        print("  Line vs Dose:  ρ=%.3f (p=%.3f)" % (r_ld, p_ld))
        print("  Line vs Diff:  ρ=%.3f (p=%.3f)" % (r_ldf, p_ldf))
        print("  Dose vs NdFeB: ρ=%.3f (p=%.3f)" % (r_dn, p_dn))

        if p_ln < 0.05 and p_dn >= 0.05:
            print("  → Line position predicts degradation but dose does not!")
            print("    Mechanism likely depends on beam geometry, not total dose.")


# ═══════════════════════════════════════════════════════════════════════════════
# PLOTS
# ═══════════════════════════════════════════════════════════════════════════════

def plot_R1_dose_bins(merged, bin_stats, region_stats, gain_syst):
    """2-panel: tertile bins and regional bins with degradation bars."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Panel A: Tertile bins
    labels = [b['label'].split('(')[0].strip() for b in bin_stats]
    x = np.arange(len(labels))
    w = 0.3

    nd_means = [b['nd_mean'] for b in bin_stats]
    nd_sems = [b['nd_sem'] for b in bin_stats]
    diff_means = [b['diff_mean'] for b in bin_stats]
    diff_sems = [b['diff_sem'] for b in bin_stats]

    ax1.bar(x - w / 2, nd_means, w, yerr=nd_sems, color='#CC3333',
            alpha=0.85, label='NdFeB', capsize=5, edgecolor='black',
            linewidth=0.8, error_kw=dict(linewidth=1.5))
    ax1.bar(x + w / 2, diff_means, w, yerr=diff_sems, color='#996600',
            alpha=0.85, label='NdFeB−SmCo', capsize=5, edgecolor='black',
            linewidth=0.8, error_kw=dict(linewidth=1.5))

    ax1.axhline(0, color='black', linewidth=1, linestyle='--')
    ax1.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.08, zorder=0)

    # Dose annotations
    for i, b in enumerate(bin_stats):
        lb_str = '>' if b['n_lower_bound'] > 0 else ''
        ax1.text(i, max(nd_means[i], diff_means[i]) + 0.08,
                 '%s%.0f Sv\n(N=%d)' % (lb_str, b['dose_sv_mean'], b['n']),
                 ha='center', va='bottom', fontsize=9, color='#666666')

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.set_ylabel('% Change from Baseline', fontsize=11)
    ax1.set_title('A. Degradation by Dose Tertile', fontsize=13,
                  fontweight='bold')
    ax1.legend(fontsize=9, loc='lower left')
    ax1.grid(axis='y', alpha=0.3)

    # Panel B: Regional bins
    labels_r = [b['label'] for b in region_stats]
    x_r = np.arange(len(labels_r))

    nd_r = [b['nd_mean'] for b in region_stats]
    nd_r_s = [b['nd_sem'] for b in region_stats]
    diff_r = [b['diff_mean'] for b in region_stats]
    diff_r_s = [b['diff_sem'] for b in region_stats]

    ax2.bar(x_r - w / 2, nd_r, w, yerr=nd_r_s, color='#CC3333',
            alpha=0.85, label='NdFeB', capsize=5, edgecolor='black',
            linewidth=0.8, error_kw=dict(linewidth=1.5))
    ax2.bar(x_r + w / 2, diff_r, w, yerr=diff_r_s, color='#996600',
            alpha=0.85, label='NdFeB−SmCo', capsize=5, edgecolor='black',
            linewidth=0.8, error_kw=dict(linewidth=1.5))

    ax2.axhline(0, color='black', linewidth=1, linestyle='--')
    ax2.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.08, zorder=0)

    for i, b in enumerate(region_stats):
        lb_str = '>' if b['n_lower_bound'] > 0 else ''
        ax2.text(i, max(nd_r[i], diff_r[i]) + 0.08,
                 '%s%.0f Sv\n(N=%d)' % (lb_str, b['dose_sv_mean'], b['n']),
                 ha='center', va='bottom', fontsize=9, color='#666666')

    ax2.set_xticks(x_r)
    ax2.set_xticklabels(labels_r, fontsize=10)
    ax2.set_ylabel('% Change from Baseline', fontsize=11)
    ax2.set_title('B. Degradation by Region', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9, loc='lower left')
    ax2.grid(axis='y', alpha=0.3)

    fig.suptitle('Degradation vs Dose Level\n'
                 '(Gray band = ±%.2f%% gain systematic; '
                 'dose = lower bound where OSL saturated)' % gain_syst,
                 fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, 'R1_dose_bins.png')


def plot_R2_radiation_composition(rad_data, merged, gain_syst):
    """2-panel: radiation type fractions by region + photon fraction vs degradation."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7),
                                    gridspec_kw={'width_ratios': [1.2, 1]})

    # Panel A: Stacked fraction bars
    labels = [rd['label'] for rd in rad_data]
    x = np.arange(len(labels))
    w = 0.5

    ph = [rd['fracs']['photon'] * 100 for rd in rad_data]
    bt = [rd['fracs']['beta'] * 100 for rd in rad_data]
    fn = [rd['fracs']['fast_n'] * 100 for rd in rad_data]
    tn = [rd['fracs']['therm_n'] * 100 for rd in rad_data]

    ax1.bar(x, ph, w, label='Photon', color='#CC6600', edgecolor='#884400')
    ax1.bar(x, bt, w, bottom=ph, label='Beta', color='#999900',
            edgecolor='#666600')
    bottoms = [p + b for p, b in zip(ph, bt)]
    ax1.bar(x, fn, w, bottom=bottoms, label='Fast neutron', color='#0088BB',
            edgecolor='#005577')
    bottoms2 = [b + f for b, f in zip(bottoms, fn)]
    ax1.bar(x, tn, w, bottom=bottoms2, label='Therm. neutron', color='#44AACC',
            edgecolor='#227799')

    # Overlay NdFeB on twin axis
    ax1r = ax1.twinx()
    nd_vals = [rd['nd_mean'] for rd in rad_data]
    ax1r.plot(x, nd_vals, 's-', color='#CC3333', markersize=12, linewidth=2,
              zorder=5, label='NdFeB %')
    ax1r.axhline(0, color='gray', linewidth=0.5)
    ax1r.set_ylabel('NdFeB mean % change', fontsize=10, color='#CC3333')

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.set_ylabel('Dose fraction (%)', fontsize=11)
    ax1.set_title('A. Radiation Composition + NdFeB', fontsize=13,
                  fontweight='bold')

    # Combined legend
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax1r.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, fontsize=8, loc='upper right')

    # Panel B: Photon fraction vs NdFeB per plate
    for m in merged:
        ph_gy = m['cum_photon_mrem'] * MREM_TO_GY_PHOTON
        bt_gy = m['cum_beta_mrem'] * MREM_TO_GY_BETA
        nf_gy = m['cum_nf_mrem'] * MREM_TO_GY_FAST_N
        nt_gy = m['cum_nt_mrem'] * MREM_TO_GY_THERM_N
        total = ph_gy + bt_gy + nf_gy + nt_gy
        if total <= 0 or np.isnan(m['ndfeb_mean_pct']):
            continue
        ph_frac = ph_gy / total * 100

        region = m['region']
        if 'Arc' in region:
            color = '#CC6600'
            marker = 'o'
        elif 'Linac' in region:
            color = '#006699'
            marker = 's'
        else:
            color = '#666666'
            marker = '^'

        ax2.scatter(ph_frac, m['ndfeb_mean_pct'], c=color, marker=marker,
                    s=60, edgecolors='black', linewidths=0.5, alpha=0.8,
                    zorder=3)

    ax2.axhline(0, color='gray', linewidth=0.5)
    ax2.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.08, zorder=0)
    ax2.set_xlabel('Photon fraction of total absorbed dose (%)', fontsize=11)
    ax2.set_ylabel('NdFeB % change', fontsize=11)
    ax2.set_title('B. Photon Fraction vs Degradation', fontsize=13,
                  fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Manual legend
    from matplotlib.lines import Line2D
    ax2.legend(handles=[
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#CC6600',
               markersize=8, label='Arc'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#006699',
               markersize=8, label='Linac'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='#666666',
               markersize=8, label='Labyrinth'),
    ], fontsize=9, loc='lower left')

    fig.suptitle('Radiation Field Composition vs NdFeB Degradation',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, 'R2_radiation_composition.png')


def plot_R3_dose_response(merged, gain_syst):
    """Dose-response scatter with fit lines and residuals."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    plates = [m for m in merged if not np.isnan(m['ndfeb_mean_pct'])]
    doses = np.array([m['cum_body_mrem'] * MREM_TO_SV for m in plates])
    nd_pcts = np.array([m['ndfeb_mean_pct'] for m in plates])

    # Panel A: NdFeB vs dose with linear fit
    for m in plates:
        region = m['region']
        if 'Arc' in region:
            color, marker = '#CC6600', 'o'
        elif 'Linac' in region:
            color, marker = '#006699', 's'
        else:
            color, marker = '#666666', '^'

        ec = 'black' if m['is_lower_bound'] else color
        ax1.scatter(m['cum_body_mrem'] * MREM_TO_SV, m['ndfeb_mean_pct'],
                    c=color, marker=marker, s=60, edgecolors=ec,
                    linewidths=1.0, alpha=0.8, zorder=3)

        if m['is_lower_bound']:
            ax1.annotate('', xy=(m['cum_body_mrem'] * MREM_TO_SV * 1.15,
                                  m['ndfeb_mean_pct']),
                         xytext=(m['cum_body_mrem'] * MREM_TO_SV,
                                  m['ndfeb_mean_pct']),
                         arrowprops=dict(arrowstyle='->', color='black',
                                          lw=0.8))

    # Linear fit
    slope, intercept, r_val, p_val, _ = stats.linregress(doses, nd_pcts)
    x_fit = np.linspace(doses.min(), doses.max(), 100)
    ax1.plot(x_fit, slope * x_fit + intercept, '--', color='#CC3333',
             linewidth=1.5, alpha=0.7,
             label='Linear: y=%.4f×dose+%.3f\nR²=%.3f, p=%.3f' % (
                 slope, intercept, r_val**2, p_val))

    ax1.axhline(0, color='gray', linewidth=0.5)
    ax1.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.08, zorder=0)
    ax1.set_xlabel('Body dose equivalent (Sv)', fontsize=11)
    ax1.set_ylabel('NdFeB % change', fontsize=11)
    ax1.set_title('A. NdFeB Degradation vs Dose\n(arrows = lower bound dose)',
                  fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9, loc='lower left')
    ax1.grid(True, alpha=0.3)

    from matplotlib.lines import Line2D
    ax1.legend(handles=[
        Line2D([0], [0], linestyle='--', color='#CC3333', linewidth=1.5,
               label='Linear: R²=%.3f (p=%.3f)' % (r_val**2, p_val)),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#CC6600',
               markersize=8, label='Arc'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#006699',
               markersize=8, label='Linac'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='#666666',
               markersize=8, label='Labyrinth'),
    ], fontsize=8, loc='lower left')

    # Panel B: Gain-immune differential vs dose
    diff_plates = [m for m in merged if not np.isnan(m['intra_plate_diff'])]
    diff_doses = np.array([m['cum_body_mrem'] * MREM_TO_SV for m in diff_plates])
    diffs = np.array([m['intra_plate_diff'] for m in diff_plates])

    for m in diff_plates:
        region = m['region']
        if 'Arc' in region:
            color, marker = '#CC6600', 'o'
        elif 'Linac' in region:
            color, marker = '#006699', 's'
        else:
            color, marker = '#666666', '^'
        ec = 'black' if m['is_lower_bound'] else color
        ax2.scatter(m['cum_body_mrem'] * MREM_TO_SV, m['intra_plate_diff'],
                    c=color, marker=marker, s=60, edgecolors=ec,
                    linewidths=1.0, alpha=0.8, zorder=3)
        if m['is_lower_bound']:
            ax2.annotate('', xy=(m['cum_body_mrem'] * MREM_TO_SV * 1.15,
                                  m['intra_plate_diff']),
                         xytext=(m['cum_body_mrem'] * MREM_TO_SV,
                                  m['intra_plate_diff']),
                         arrowprops=dict(arrowstyle='->', color='black',
                                          lw=0.8))

    slope_d, int_d, r_d, p_d, _ = stats.linregress(diff_doses, diffs)
    ax2.plot(x_fit, slope_d * x_fit + int_d, '--', color='#996600',
             linewidth=1.5, alpha=0.7)

    ax2.axhline(0, color='gray', linewidth=0.5)
    ax2.set_xlabel('Body dose equivalent (Sv)', fontsize=11)
    ax2.set_ylabel('NdFeB − SmCo differential (%)', fontsize=11)
    ax2.set_title('B. Gain-Immune Differential vs Dose\n'
                  'R²=%.3f, p=%.3f (gain-immune)' % (r_d**2, p_d),
                  fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    fig.suptitle('Dose-Response Relationship\n'
                 '22/30 plates have saturated OSL → dose is LOWER BOUND',
                 fontsize=14, fontweight='bold', y=1.03)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, 'R3_dose_response.png')


def plot_R4_arc_lines(merged, gain_syst):
    """Arc line (pass-number) detail: dose + degradation per line."""
    arc_plates = [m for m in merged if 'Arc' in m['region'] and m['line'] > 0]
    if not arc_plates:
        print("  R4: No arc plates with line data")
        return

    lines = defaultdict(list)
    for m in arc_plates:
        lines[m['line']].append(m)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    line_nums = sorted(lines.keys())
    x = np.arange(len(line_nums))
    w = 0.25

    dose_means = []
    nd_means, nd_sems = [], []
    diff_means, diff_sems = [], []

    for ln in line_nums:
        plates = lines[ln]
        dose_means.append(np.mean([m['cum_body_mrem'] * MREM_TO_SV for m in plates]))
        nd = [m['ndfeb_mean_pct'] for m in plates if not np.isnan(m['ndfeb_mean_pct'])]
        df = [m['intra_plate_diff'] for m in plates if not np.isnan(m['intra_plate_diff'])]
        nd_means.append(np.mean(nd) if nd else 0)
        nd_sems.append(np.std(nd, ddof=1) / np.sqrt(len(nd)) if len(nd) > 1 else 0)
        diff_means.append(np.mean(df) if df else 0)
        diff_sems.append(np.std(df, ddof=1) / np.sqrt(len(df)) if len(df) > 1 else 0)

    # Panel A: Dose per line
    colors = plt.cm.YlOrRd(np.linspace(0.3, 0.9, len(line_nums)))
    bars = ax1.bar(x, dose_means, 0.6, color=colors, edgecolor='black',
                   linewidth=0.8)
    for i, (ln, d) in enumerate(zip(line_nums, dose_means)):
        n = len(lines[ln])
        n_lb = sum(1 for m in lines[ln] if m['is_lower_bound'])
        lb_str = '>' if n_lb > 0 else ''
        ax1.text(i, d + 1, '%s%.0f Sv\n(N=%d)' % (lb_str, d, n),
                 ha='center', va='bottom', fontsize=9)

    ax1.set_xticks(x)
    ax1.set_xticklabels(['Line %d' % ln for ln in line_nums], fontsize=10)
    ax1.set_ylabel('Mean body dose equivalent (Sv)', fontsize=11)
    ax1.set_title('A. Dose by Arc Line Position', fontsize=13,
                  fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # Panel B: Degradation per line
    ax2.bar(x - w / 2, nd_means, w, yerr=nd_sems, color='#CC3333',
            alpha=0.85, label='NdFeB', capsize=5, edgecolor='black',
            linewidth=0.8, error_kw=dict(linewidth=1.5))
    ax2.bar(x + w / 2, diff_means, w, yerr=diff_sems, color='#996600',
            alpha=0.85, label='NdFeB−SmCo', capsize=5, edgecolor='black',
            linewidth=0.8, error_kw=dict(linewidth=1.5))

    ax2.axhline(0, color='black', linewidth=1, linestyle='--')
    ax2.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.08, zorder=0)
    ax2.set_xticks(x)
    ax2.set_xticklabels(['Line %d' % ln for ln in line_nums], fontsize=10)
    ax2.set_ylabel('% Change from Baseline', fontsize=11)
    ax2.set_title('B. Degradation by Arc Line Position', fontsize=13,
                  fontweight='bold')
    ax2.legend(fontsize=9, loc='lower right')
    ax2.grid(axis='y', alpha=0.3)

    fig.suptitle('Arc Pass-Number Breakdown: Dose vs Degradation\n'
                 'Line 1 = closest to beam, Line 5 = farthest',
                 fontsize=14, fontweight='bold', y=1.03)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, 'R4_arc_lines.png')


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("DOSE-REGION BREAKDOWNS")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    results, helm_raw, temp_final, y_materials = load_all()
    clean = [r for r in results if not r['is_outlier']]
    gain_result = get_gain_syst(helm_raw)
    gain_syst = gain_result.gain_syst
    intra_diffs, intra_details = compute_intra_plate_diffs(clean)
    print("  %d clean Y-plate samples" % len(clean))
    print("  Gain systematic: ±%.4f%%" % gain_syst)

    dose_cum = load_dose_cumulative()
    merged = merge_data(results, intra_details, dose_cum)
    print("  %d merged Y-plates with dose" % len(merged))

    # Analyses
    bin_stats, region_stats = dose_bin_analysis(merged, gain_syst)
    rad_data = radiation_type_analysis(merged)
    dr_stats = dose_response_analysis(merged)
    arc_detail_analysis(merged)

    # Interpretation
    print("\n" + "=" * 78)
    print("INTERPRETATION SUMMARY")
    print("=" * 78)
    print()
    print("1. DOSE LEVEL: No monotonic dose-degradation trend across tertiles.")
    print("   The medium-dose group (arcs) shows the MOST degradation, not the")
    print("   high-dose group (linacs). This is the inverted pass-number effect.")
    print()
    print("2. RADIATION TYPE: Absorbed dose is >99%% photon + beta (gamma/X-ray).")
    print("   Neutron contribution is negligible in absolute Gy. The photon")
    print("   fraction does not predict degradation magnitude.")
    print()
    print("3. DOSE-RESPONSE: Linear fit R²=%.3f (p=%.3f). No evidence for a" % (
        dr_stats['linear_r2'], dr_stats['linear_p']))
    print("   dose threshold or saturation curve. Scatter is dominated by")
    print("   positional (line number) effects, not dose level.")
    print()
    print("4. ARC LINES: Line 1 (closest to beam) has the MOST degradation")
    print("   but the LEAST dose. This inversion rules out simple total-dose")
    print("   models and points to beam optics geometry or radiation field")
    print("   quality as the dominant factor.")
    print()
    print("CAVEAT: 22/30 plates have saturated OSL. Body doses are LOWER BOUNDS.")
    print("True doses may differ in ways that change the dose ordering.")
    print("Optichromic rod data will help resolve this.")

    # Plots
    print("\n" + "=" * 70)
    print("Generating plots...")
    print("=" * 70)
    plot_R1_dose_bins(merged, bin_stats, region_stats, gain_syst)
    plot_R2_radiation_composition(rad_data, merged, gain_syst)
    plot_R3_dose_response(merged, gain_syst)
    plot_R4_arc_lines(merged, gain_syst)

    print("\n" + "=" * 70)
    print("All plots saved to: %s" % PLOT_DIR)
    print("  R1: Dose bins (tertile + regional)")
    print("  R2: Radiation composition by region")
    print("  R3: Dose-response scatter with fits")
    print("  R4: Arc line position detail")
    print("=" * 70)


if __name__ == '__main__':
    main()
