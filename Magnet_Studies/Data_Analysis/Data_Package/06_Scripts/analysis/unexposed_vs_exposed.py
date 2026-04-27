#!/usr/bin/env python3
"""Unexposed vs Exposed Comparison — All Sample Types

Compares lab (unexposed) vs tunnel (exposed) samples across Y-plates,
H-plates, and A-samples to validate that observed degradation is
radiation-induced, not systematic drift.

Sample types:
  Y-plates: 4 materials on one plate (intra-plate differential is gain-immune)
    - 30 tunnel, 9 lab
  H-plates: Single-material pair assemblies
    - 30 tunnel (14n + 16s), 48 lab (24n + 24s)
  A-samples: Individual magnets from H-plate pairs
    - Tunnel: measured when retrieved from tunnel
    - Lab: measured alongside tunnel magnets

TEMPERATURE NOTE:
  Tunnel Y-plates: temp-corrected (Teslameter co-incident)
  Lab Y-plates: temp-corrected (estimated temps, see LAB_TEMP_LOOKUP)
  Tunnel H/A: temp-corrected where Teslameter data available
  Lab H/A: temp-corrected (estimated temps, see LAB_TEMP_LOOKUP)
  All corrected to T_ref=20°C. Per-sample sigma_temp_pct tracks uncertainty.

Output: Cleanup_Claude/Unexposed_vs_Exposed/ (plots + summary)
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.join(BASE, 'Unexposed_vs_Exposed')
os.makedirs(PLOT_DIR, exist_ok=True)

# Import from existing scripts
sys.path.insert(0, BASE)
from manager_summary_v3 import (
    load_all, get_gain_syst, compute_intra_plate_diffs, MAT_BY_SLOT,
    FLAGGED, PLACEMENTS,
)
from manager_summary_v5_polish import (
    load_lab_y_plates, load_lab_y_materials, LAB_Y_PLATES,
    load_materials, build_temperature_lookup, compute_h_plate_degradation,
    load_a_sample_helmholtz,
)

# Lab H/A loader
sys.path.insert(0, os.path.join(BASE, 'Lab_Controls'))
from lab_ha_analysis import (
    collect_all_lab_data, load_assembly_configs, analyze_lab_samples,
    classify_sample,
)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════

def load_all_data():
    """Load all tunnel and lab data for Y, H, and A sample types.

    Returns dict with keys: tunnel_y, lab_y, tunnel_h, lab_h, lab_a,
    gain_syst, gain_syst_raw.
    """
    print("=" * 70)
    print("Loading all data for unexposed vs exposed comparison")
    print("=" * 70)

    # --- Y-plates (tunnel) ---
    print("\n1. Tunnel Y-plates (temp-corrected)...")
    y_results, helm_raw, temp_final, y_materials = load_all()
    y_clean = [r for r in y_results if not r['is_outlier']]
    print("   %d tunnel Y-plate samples (%d materials × %d plates)" %
          (len(y_clean), 4, len(set(r['plate'] for r in y_clean))))

    # --- Gain systematic ---
    gain_result = get_gain_syst(helm_raw)
    gain_syst = gain_result.gain_syst
    gain_syst_raw = gain_result.gain_syst_raw
    print("   Gain systematic: ±%.4f%% (cleaned) / ±%.4f%% (uncleaned)" %
          (gain_syst, gain_syst_raw))

    # --- Y-plates (lab) ---
    print("\n2. Lab Y-plates (temp-corrected to T_ref=20°C)...")
    lab_y_data = load_lab_y_plates(apply_temp_correction=True)
    print("   %d lab Y-plates loaded" % len(lab_y_data))

    # --- H-plates (tunnel) ---
    print("\n3. Tunnel H-plates (temp-corrected where available)...")
    y_mats_xl, pair_arrangements = load_materials()
    temp_lookup = build_temperature_lookup()
    h_results, h_excluded = compute_h_plate_degradation(
        pair_arrangements, temp_lookup)
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]
    print("   %d tunnel H-plate pairs (%d clean)" %
          (len(h_results), len(h_clean)))

    # --- H/A (lab) ---
    print("\n4. Lab H/A samples (temp-corrected to T_ref=20°C)...")
    configs = load_assembly_configs()
    lab_all_data = collect_all_lab_data()
    lab_results = analyze_lab_samples(lab_all_data, configs, apply_temp_correction=True)
    lab_h = [r for r in lab_results if r['type'] == 'H'
             and not r['is_anomalous_baseline']
             and not r.get('is_delta_hplate', False)]
    lab_a = [r for r in lab_results if r['type'] == 'A'
             and not r['is_anomalous_baseline']]
    print("   %d lab H-plate samples, %d lab A-samples" %
          (len(lab_h), len(lab_a)))

    # --- A-samples (tunnel) ---
    print("\n5. Tunnel A-samples (temp-corrected where available)...")
    a_helm_results = load_a_sample_helmholtz(temp_lookup)
    a_clean = [r for r in a_helm_results if not r['is_outlier']]
    print("   %d tunnel A-samples (%d clean)" %
          (len(a_helm_results), len(a_clean)))

    return {
        'tunnel_y': y_clean,
        'lab_y': lab_y_data,
        'tunnel_h': h_clean,
        'lab_h': lab_h,
        'tunnel_a': a_clean,
        'lab_a': lab_a,
        'gain_syst': gain_syst,
        'gain_syst_raw': gain_syst_raw,
        'intra_diffs': compute_intra_plate_diffs(y_clean),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

def compute_stats(values, label=""):
    """Compute mean, SEM, sigma from zero for a list of values."""
    if not values:
        return {'mean': np.nan, 'sem': np.nan, 'sigma': 0, 'n': 0,
                'std': np.nan, 'label': label}
    arr = np.array(values)
    mean = np.mean(arr)
    std = np.std(arr, ddof=1) if len(arr) > 1 else 0
    sem = std / np.sqrt(len(arr)) if len(arr) > 1 else 0
    sigma = abs(mean / sem) if sem > 0 else 0
    return {'mean': mean, 'sem': sem, 'sigma': sigma, 'n': len(arr),
            'std': std, 'label': label}


def difference_stats(stats_a, stats_b):
    """Compute A - B difference with propagated errors."""
    diff = stats_a['mean'] - stats_b['mean']
    err = np.sqrt(stats_a['sem']**2 + stats_b['sem']**2)
    sigma = abs(diff / err) if err > 0 else 0
    return {'mean': diff, 'sem': err, 'sigma': sigma,
            'n_a': stats_a['n'], 'n_b': stats_b['n']}


# ═══════════════════════════════════════════════════════════════════════════════
# PRINT SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

def print_comprehensive_summary(data):
    """Print the full unexposed vs exposed comparison."""
    print("\n" + "=" * 78)
    print("UNEXPOSED vs EXPOSED COMPARISON — ALL SAMPLE TYPES")
    print("=" * 78)
    print()
    print("Purpose: Validate that observed NdFeB degradation is radiation-induced,")
    print("         not systematic drift (gain, temperature, aging).")
    print()
    print("Controls: Lab samples stored in same lab, never deployed in tunnel.")
    print("          Measured with identical instruments on identical schedules.")
    print()
    print("TEMPERATURE: Lab Y/H/A samples now corrected to T_ref=20°C using")
    print("  estimated room temps (teslameter where available, ~23°C estimated")
    print("  otherwise). Per-sample sigma_temp_pct tracks temp uncertainty.")
    print()

    tunnel_y = data['tunnel_y']
    lab_y = data['lab_y']
    tunnel_h = data['tunnel_h']
    lab_h = data['lab_h']
    tunnel_a = data['tunnel_a']
    lab_a = data['lab_a']
    gain_syst = data['gain_syst']

    # ─── Section 1: Y-Plate Comparison ────────────────────────────────────
    print("-" * 78)
    print("SECTION 1: Y-PLATES (4 materials per plate, Helmholtz)")
    print("  Tunnel: 30 plates (temp-corrected)  |  Lab: 9 plates (RAW)")
    print("-" * 78)
    print()

    # Per-material comparison
    print("  %-10s  %20s  %20s  %20s" % (
        'Material', 'Tunnel (N=30)', 'Lab (N=9)', 'Tunnel − Lab'))
    print("  " + "-" * 74)

    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    for mat in materials:
        t_vals = [r['pct_change'] for r in tunnel_y if r['material'] == mat]
        l_vals = []
        for pdata in lab_y.values():
            if mat in pdata['slot_pcts']:
                l_vals.append(pdata['slot_pcts'][mat])

        t_stats = compute_stats(t_vals, 'Tunnel ' + mat)
        l_stats = compute_stats(l_vals, 'Lab ' + mat)
        d_stats = difference_stats(t_stats, l_stats)

        print("  %-10s  %+.3f±%.3f%% (%4.1fσ)  %+.3f±%.3f%% (%4.1fσ)  "
              "%+.3f±%.3f%% (%4.1fσ)" % (
                  mat,
                  t_stats['mean'], t_stats['sem'], t_stats['sigma'],
                  l_stats['mean'], l_stats['sem'], l_stats['sigma'],
                  d_stats['mean'], d_stats['sem'], d_stats['sigma']))

    # NdFeB aggregate
    t_nd = [r['pct_change'] for r in tunnel_y
            if r['material'] in ('N42EH', 'N52SH')]
    l_nd = []
    for pdata in lab_y.values():
        for m in ('N42EH', 'N52SH'):
            if m in pdata['slot_pcts']:
                l_nd.append(pdata['slot_pcts'][m])
    t_sm = [r['pct_change'] for r in tunnel_y
            if r['material'] in ('SmCo33H', 'SmCo35')]
    l_sm = []
    for pdata in lab_y.values():
        for m in ('SmCo33H', 'SmCo35'):
            if m in pdata['slot_pcts']:
                l_sm.append(pdata['slot_pcts'][m])

    print()
    t_nd_s = compute_stats(t_nd)
    l_nd_s = compute_stats(l_nd)
    t_sm_s = compute_stats(t_sm)
    l_sm_s = compute_stats(l_sm)

    print("  NdFeB agg  %+.3f±%.3f%% (N=%d)    %+.3f±%.3f%% (N=%d)" % (
        t_nd_s['mean'], t_nd_s['sem'], t_nd_s['n'],
        l_nd_s['mean'], l_nd_s['sem'], l_nd_s['n']))
    print("  SmCo agg   %+.3f±%.3f%% (N=%d)    %+.3f±%.3f%% (N=%d)" % (
        t_sm_s['mean'], t_sm_s['sem'], t_sm_s['n'],
        l_sm_s['mean'], l_sm_s['sem'], l_sm_s['n']))

    # Gain-immune differential
    intra_diffs, intra_details = data['intra_diffs']
    t_diff_s = compute_stats(intra_diffs)
    l_diffs = [v['diff'] for v in lab_y.values() if np.isfinite(v['diff'])]
    l_diff_s = compute_stats(l_diffs)
    tl_diff = difference_stats(t_diff_s, l_diff_s)

    print()
    print("  GAIN-IMMUNE DIFFERENTIAL (NdFeB − SmCo per plate):")
    print("    Tunnel: %+.3f%% ± %.3f%% (%.1fσ, N=%d)" % (
        t_diff_s['mean'], t_diff_s['sem'], t_diff_s['sigma'], t_diff_s['n']))
    print("    Lab:    %+.3f%% ± %.3f%% (%.1fσ, N=%d)" % (
        l_diff_s['mean'], l_diff_s['sem'], l_diff_s['sigma'], l_diff_s['n']))
    print("    T − L:  %+.3f%% ± %.3f%% (%.1fσ) ← RADIATION SIGNAL" % (
        tl_diff['mean'], tl_diff['sem'], tl_diff['sigma']))

    # ─── Section 2: H-Plate Comparison ────────────────────────────────────
    print()
    print("-" * 78)
    print("SECTION 2: H-PLATES (single-material pair assemblies, Helmholtz)")
    print("  Tunnel: %d pairs (temp-corrected)  |  Lab: %d samples (RAW)" % (
        len(tunnel_h), len(lab_h)))
    print("-" * 78)
    print()

    print("  %-10s  %22s  %22s  %22s" % (
        'Material', 'Tunnel', 'Lab', 'Tunnel − Lab'))
    print("  " + "-" * 78)

    for mat in ['NdFeB', 'SmCo']:
        t_vals = [r['pct_change'] for r in tunnel_h if r['material'] == mat]
        l_vals = [r['pct_change'] for r in lab_h if r['material'] == mat
                  and r['config'].lower() not in ('beta', '')]

        t_s = compute_stats(t_vals)
        l_s = compute_stats(l_vals)
        d_s = difference_stats(t_s, l_s)

        print("  %-10s  %+.3f±%.3f%% (%4.1fσ,N=%d)  "
              "%+.3f±%.3f%% (%4.1fσ,N=%d)  "
              "%+.3f±%.3f%% (%4.1fσ)" % (
                  mat,
                  t_s['mean'], t_s['sem'], t_s['sigma'], t_s['n'],
                  l_s['mean'], l_s['sem'], l_s['sigma'], l_s['n'],
                  d_s['mean'], d_s['sem'], d_s['sigma']))

    # ─── Section 3: A-Sample Comparison ───────────────────────────────────
    print()
    print("-" * 78)
    print("SECTION 3: A-SAMPLES (pairs, Helmholtz)")
    print("  Tunnel: %d samples  |  Lab: %d samples (RAW)" % (
        len(tunnel_a), len(lab_a)))
    print("-" * 78)
    print()

    print("  %-10s  %22s  %22s  %22s" % (
        'Material', 'Tunnel', 'Lab', 'Tunnel − Lab'))
    print("  " + "-" * 78)

    for mat in ['NdFeB', 'SmCo']:
        t_vals = [r['pct_change'] for r in tunnel_a if r['material'] == mat]
        l_vals = [r['pct_change'] for r in lab_a if r['material'] == mat
                  and r['config'].lower() not in ('beta', '')]

        t_s = compute_stats(t_vals)
        l_s = compute_stats(l_vals)
        d_s = difference_stats(t_s, l_s) if t_s['n'] > 0 and l_s['n'] > 0 else {
            'mean': np.nan, 'sem': np.nan, 'sigma': 0}

        t_str = ("%+.3f±%.3f%% (%4.1fσ,N=%d)" % (
            t_s['mean'], t_s['sem'], t_s['sigma'], t_s['n'])
            if t_s['n'] > 0 else "no data")
        l_str = ("%+.3f±%.3f%% (%4.1fσ,N=%d)" % (
            l_s['mean'], l_s['sem'], l_s['sigma'], l_s['n'])
            if l_s['n'] > 0 else "no data")
        d_str = ("%+.3f±%.3f%% (%4.1fσ)" % (
            d_s['mean'], d_s['sem'], d_s['sigma'])
            if np.isfinite(d_s.get('mean', np.nan)) else "—")

        print("  %-10s  %-22s  %-22s  %-22s" % (mat, t_str, l_str, d_str))

    # ─── Section 4: Grand Summary ─────────────────────────────────────────
    print()
    print("=" * 78)
    print("GRAND SUMMARY — Exposed vs Unexposed")
    print("=" * 78)
    print()
    print("  %-22s  %12s  %12s  %12s  %8s" % (
        'Comparison', 'Tunnel', 'Lab', 'T − L', 'Signal'))
    print("  " + "-" * 70)

    rows = []

    # Y differential
    rows.append(('Y NdFeB−SmCo diff',
                 '%+.3f±%.3f' % (t_diff_s['mean'], t_diff_s['sem']),
                 '%+.3f±%.3f' % (l_diff_s['mean'], l_diff_s['sem']),
                 '%+.3f±%.3f' % (tl_diff['mean'], tl_diff['sem']),
                 '%.1fσ' % tl_diff['sigma']))

    # Y NdFeB
    d = difference_stats(compute_stats(t_nd), compute_stats(l_nd))
    rows.append(('Y NdFeB (absolute)',
                 '%+.3f±%.3f' % (t_nd_s['mean'], t_nd_s['sem']),
                 '%+.3f±%.3f' % (l_nd_s['mean'], l_nd_s['sem']),
                 '%+.3f±%.3f' % (d['mean'], d['sem']),
                 '%.1fσ' % d['sigma']))

    # Y SmCo
    d = difference_stats(compute_stats(t_sm), compute_stats(l_sm))
    rows.append(('Y SmCo (absolute)',
                 '%+.3f±%.3f' % (t_sm_s['mean'], t_sm_s['sem']),
                 '%+.3f±%.3f' % (l_sm_s['mean'], l_sm_s['sem']),
                 '%+.3f±%.3f' % (d['mean'], d['sem']),
                 '%.1fσ' % d['sigma']))

    # H NdFeB
    ht_nd = compute_stats([r['pct_change'] for r in tunnel_h
                           if r['material'] == 'NdFeB'])
    hl_nd = compute_stats([r['pct_change'] for r in lab_h
                           if r['material'] == 'NdFeB'
                           and r['config'].lower() not in ('beta', '')])
    if ht_nd['n'] > 0 and hl_nd['n'] > 0:
        d = difference_stats(ht_nd, hl_nd)
        rows.append(('H NdFeB (absolute)',
                     '%+.3f±%.3f' % (ht_nd['mean'], ht_nd['sem']),
                     '%+.3f±%.3f' % (hl_nd['mean'], hl_nd['sem']),
                     '%+.3f±%.3f' % (d['mean'], d['sem']),
                     '%.1fσ' % d['sigma']))

    # H SmCo
    ht_sm = compute_stats([r['pct_change'] for r in tunnel_h
                           if r['material'] == 'SmCo'])
    hl_sm = compute_stats([r['pct_change'] for r in lab_h
                           if r['material'] == 'SmCo'
                           and r['config'].lower() not in ('beta', '')])
    if ht_sm['n'] > 0 and hl_sm['n'] > 0:
        d = difference_stats(ht_sm, hl_sm)
        rows.append(('H SmCo (absolute)',
                     '%+.3f±%.3f' % (ht_sm['mean'], ht_sm['sem']),
                     '%+.3f±%.3f' % (hl_sm['mean'], hl_sm['sem']),
                     '%+.3f±%.3f' % (d['mean'], d['sem']),
                     '%.1fσ' % d['sigma']))

    # A NdFeB
    at_nd = compute_stats([r['pct_change'] for r in tunnel_a
                           if r['material'] == 'NdFeB'])
    al_nd = compute_stats([r['pct_change'] for r in lab_a
                           if r['material'] == 'NdFeB'
                           and r['config'].lower() not in ('beta', '')])
    if at_nd['n'] > 0 and al_nd['n'] > 0:
        d = difference_stats(at_nd, al_nd)
        rows.append(('A NdFeB (absolute)',
                     '%+.3f±%.3f' % (at_nd['mean'], at_nd['sem']),
                     '%+.3f±%.3f' % (al_nd['mean'], al_nd['sem']),
                     '%+.3f±%.3f' % (d['mean'], d['sem']),
                     '%.1fσ' % d['sigma']))

    # A SmCo
    at_sm = compute_stats([r['pct_change'] for r in tunnel_a
                           if r['material'] == 'SmCo'])
    al_sm = compute_stats([r['pct_change'] for r in lab_a
                           if r['material'] == 'SmCo'
                           and r['config'].lower() not in ('beta', '')])
    if at_sm['n'] > 0 and al_sm['n'] > 0:
        d = difference_stats(at_sm, al_sm)
        rows.append(('A SmCo (absolute)',
                     '%+.3f±%.3f' % (at_sm['mean'], at_sm['sem']),
                     '%+.3f±%.3f' % (al_sm['mean'], al_sm['sem']),
                     '%+.3f±%.3f' % (d['mean'], d['sem']),
                     '%.1fσ' % d['sigma']))

    for row in rows:
        print("  %-22s  %12s  %12s  %12s  %8s" % row)

    print()
    print("  Notes:")
    print("  - σ = significance of departure from zero")
    print("  - Gain-immune differential (row 1) is the strongest test")
    print("  - Absolute values carry ±%.3f%% gain systematic" % gain_syst)
    print("  - Lab samples temp-corrected to 20°C (est. room temps)")
    print("  - Beta/antiparallel configs excluded from lab H/A")

    return rows


# ═══════════════════════════════════════════════════════════════════════════════
# PLOTS
# ═══════════════════════════════════════════════════════════════════════════════

def plot_U1_grand_comparison(data):
    """4-panel plot: Y differential, Y per-material, H per-material, A per-material.

    Each panel shows tunnel vs lab bars with error bars and significance.
    """
    tunnel_y = data['tunnel_y']
    lab_y = data['lab_y']
    tunnel_h = data['tunnel_h']
    lab_h = data['lab_h']
    tunnel_a = data['tunnel_a']
    lab_a = data['lab_a']
    gain_syst = data['gain_syst']
    intra_diffs, intra_details = data['intra_diffs']

    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

    tunnel_color = '#8B0000'
    lab_color = '#3366CC'

    # ─── Panel A: Y-plate gain-immune differential ─────────────────────
    ax = axes[0, 0]
    t_diffs = list(intra_diffs)
    l_diffs = [v['diff'] for v in lab_y.values() if np.isfinite(v['diff'])]

    t_s = compute_stats(t_diffs)
    l_s = compute_stats(l_diffs)
    tl = difference_stats(t_s, l_s)

    bars = ax.bar([0, 1], [t_s['mean'], l_s['mean']],
                  yerr=[t_s['sem'], l_s['sem']],
                  color=[tunnel_color, lab_color],
                  capsize=8, edgecolor='black', linewidth=1, width=0.5,
                  error_kw=dict(linewidth=2, capthick=2))
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Tunnel\n(N=%d)' % t_s['n'],
                         'Lab\n(N=%d)' % l_s['n']], fontsize=10)
    ax.set_ylabel('NdFeB − SmCo (%)', fontsize=11)
    ax.set_title('A. Y-Plate Gain-Immune Differential', fontsize=13,
                 fontweight='bold')

    # Annotate significance
    for i, (val, sem, sig, col) in enumerate([
            (t_s['mean'], t_s['sem'], t_s['sigma'], tunnel_color),
            (l_s['mean'], l_s['sem'], l_s['sigma'], lab_color)]):
        y = val - sem - 0.02 if val < 0 else val + sem + 0.02
        va = 'top' if val < 0 else 'bottom'
        ax.text(i, y, '%.1fσ' % sig, ha='center', va=va,
                fontsize=11, fontweight='bold', color=col)

    ax.annotate('Tunnel − Lab = %.1fσ' % tl['sigma'],
                xy=(0.5, 0.95), xycoords='axes fraction', ha='center',
                fontsize=11, fontweight='bold', color='#CC6600',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                          edgecolor='orange'))
    ax.grid(axis='y', alpha=0.3)

    # ─── Panel B: Y-plate per material ────────────────────────────────
    ax = axes[0, 1]
    mats = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    x_pos = np.arange(len(mats))
    bar_w = 0.35

    t_means, t_sems, l_means, l_sems = [], [], [], []
    for mat in mats:
        tv = [r['pct_change'] for r in tunnel_y if r['material'] == mat]
        lv = []
        for pd in lab_y.values():
            if mat in pd['slot_pcts']:
                lv.append(pd['slot_pcts'][mat])
        ts = compute_stats(tv)
        ls = compute_stats(lv)
        t_means.append(ts['mean'])
        t_sems.append(ts['sem'])
        l_means.append(ls['mean'])
        l_sems.append(ls['sem'])

    ax.bar(x_pos - bar_w / 2, t_means, bar_w, yerr=t_sems,
           color=tunnel_color, alpha=0.85, label='Tunnel',
           capsize=5, edgecolor='black', linewidth=0.8,
           error_kw=dict(linewidth=1.5, capthick=1.5))
    ax.bar(x_pos + bar_w / 2, l_means, bar_w, yerr=l_sems,
           color=lab_color, alpha=0.85, label='Lab',
           capsize=5, edgecolor='black', linewidth=0.8,
           error_kw=dict(linewidth=1.5, capthick=1.5))

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.10, zorder=0)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(mats, fontsize=9)
    ax.set_ylabel('% Change from Baseline', fontsize=11)
    ax.set_title('B. Y-Plate Per-Material Comparison', fontsize=13,
                 fontweight='bold')
    ax.legend(fontsize=9, loc='lower left')
    ax.grid(axis='y', alpha=0.3)

    # ─── Panel C: H-plate per material ────────────────────────────────
    ax = axes[1, 0]
    h_mats = ['NdFeB', 'SmCo']
    x_pos = np.arange(len(h_mats))

    t_means, t_sems, l_means, l_sems = [], [], [], []
    for mat in h_mats:
        tv = [r['pct_change'] for r in tunnel_h if r['material'] == mat]
        lv = [r['pct_change'] for r in lab_h if r['material'] == mat
              and r['config'].lower() not in ('beta', '')]
        ts = compute_stats(tv)
        ls = compute_stats(lv)
        t_means.append(ts['mean'])
        t_sems.append(ts['sem'])
        l_means.append(ls['mean'])
        l_sems.append(ls['sem'])

    ax.bar(x_pos - bar_w / 2, t_means, bar_w, yerr=t_sems,
           color=tunnel_color, alpha=0.85, label='Tunnel',
           capsize=5, edgecolor='black', linewidth=0.8,
           error_kw=dict(linewidth=1.5, capthick=1.5))
    ax.bar(x_pos + bar_w / 2, l_means, bar_w, yerr=l_sems,
           color=lab_color, alpha=0.85, label='Lab',
           capsize=5, edgecolor='black', linewidth=0.8,
           error_kw=dict(linewidth=1.5, capthick=1.5))

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.10, zorder=0)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(h_mats, fontsize=10)
    ax.set_ylabel('% Change from Baseline', fontsize=11)
    ax.set_title('C. H-Plate Per-Material Comparison', fontsize=13,
                 fontweight='bold')
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    ax.annotate('Lab H: temp-corrected (est.)\nBeta configs excluded',
                xy=(0.98, 0.02), xycoords='axes fraction', ha='right',
                va='bottom', fontsize=8, fontstyle='italic', color='#666666')

    # ─── Panel D: A-sample per material ───────────────────────────────
    ax = axes[1, 1]
    t_means, t_sems, l_means, l_sems = [], [], [], []
    for mat in h_mats:
        tv = [r['pct_change'] for r in tunnel_a if r['material'] == mat]
        lv = [r['pct_change'] for r in lab_a if r['material'] == mat
              and r['config'].lower() not in ('beta', '')]
        ts = compute_stats(tv)
        ls = compute_stats(lv)
        t_means.append(ts['mean'] if ts['n'] > 0 else 0)
        t_sems.append(ts['sem'] if ts['n'] > 0 else 0)
        l_means.append(ls['mean'] if ls['n'] > 0 else 0)
        l_sems.append(ls['sem'] if ls['n'] > 0 else 0)

    ax.bar(x_pos - bar_w / 2, t_means, bar_w, yerr=t_sems,
           color=tunnel_color, alpha=0.85, label='Tunnel',
           capsize=5, edgecolor='black', linewidth=0.8,
           error_kw=dict(linewidth=1.5, capthick=1.5))
    ax.bar(x_pos + bar_w / 2, l_means, bar_w, yerr=l_sems,
           color=lab_color, alpha=0.85, label='Lab',
           capsize=5, edgecolor='black', linewidth=0.8,
           error_kw=dict(linewidth=1.5, capthick=1.5))

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.10, zorder=0)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(h_mats, fontsize=10)
    ax.set_ylabel('% Change from Baseline', fontsize=11)
    ax.set_title('D. A-Sample Per-Material Comparison', fontsize=13,
                 fontweight='bold')
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    ax.annotate('Lab A: temp-corrected (est.)\nBeta configs excluded',
                xy=(0.98, 0.02), xycoords='axes fraction', ha='right',
                va='bottom', fontsize=8, fontstyle='italic', color='#666666')

    fig.suptitle('Unexposed vs Exposed: All Sample Types\n'
                 '(Gray band = ±%.2f%% gain systematic)' % gain_syst,
                 fontsize=15, fontweight='bold', y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(PLOT_DIR, 'U1_grand_comparison.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  U1: Grand comparison (4-panel)")


def plot_U2_strip_all_types(data):
    """Strip plot showing individual sample distributions for tunnel vs lab.

    3 columns (Y, H, A), each with tunnel and lab distributions side by side.
    """
    tunnel_y = data['tunnel_y']
    lab_y = data['lab_y']
    tunnel_h = data['tunnel_h']
    lab_h = data['lab_h']
    tunnel_a = data['tunnel_a']
    lab_a = data['lab_a']
    gain_syst = data['gain_syst']

    fig, axes = plt.subplots(1, 3, figsize=(20, 8), sharey=True)
    rng = np.random.RandomState(42)

    tunnel_color = '#8B0000'
    lab_color = '#3366CC'

    # ─── Panel 1: Y-plates (NdFeB only, for visibility) ──────────────
    ax = axes[0]
    t_nd = [r['pct_change'] for r in tunnel_y
            if r['material'] in ('N42EH', 'N52SH')]
    l_nd = []
    for pd in lab_y.values():
        for m in ('N42EH', 'N52SH'):
            if m in pd['slot_pcts']:
                l_nd.append(pd['slot_pcts'][m])

    t_sm = [r['pct_change'] for r in tunnel_y
            if r['material'] in ('SmCo33H', 'SmCo35')]
    l_sm = []
    for pd in lab_y.values():
        for m in ('SmCo33H', 'SmCo35'):
            if m in pd['slot_pcts']:
                l_sm.append(pd['slot_pcts'][m])

    # NdFeB: positions 0 (tunnel), 1 (lab)
    # SmCo: positions 2.5 (tunnel), 3.5 (lab)
    groups = [
        (0, t_nd, tunnel_color, 'Tunnel NdFeB'),
        (1, l_nd, lab_color, 'Lab NdFeB'),
        (2.5, t_sm, tunnel_color, 'Tunnel SmCo'),
        (3.5, l_sm, lab_color, 'Lab SmCo'),
    ]
    for xc, vals, col, label in groups:
        jitter = rng.normal(0, 0.12, len(vals))
        ax.scatter(np.full(len(vals), xc) + jitter, vals,
                   color=col, alpha=0.5, s=20, edgecolor='black',
                   linewidth=0.3, zorder=3)
        mean = np.mean(vals) if vals else 0
        ax.hlines(mean, xc - 0.3, xc + 0.3, colors=col, linewidth=2.5,
                  zorder=4)

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.08, zorder=0)
    ax.set_xticks([0.5, 3])
    ax.set_xticklabels(['NdFeB\n(N42EH+N52SH)', 'SmCo\n(33H+35)'], fontsize=9)
    ax.set_ylabel('% Change from Baseline', fontsize=11)
    ax.set_title('Y-Plates (4-slot, temp-corr)', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=tunnel_color,
               markersize=8, label='Tunnel (exposed)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=lab_color,
               markersize=8, label='Lab (unexposed)'),
    ]
    ax.legend(handles=legend_elements, fontsize=9, loc='lower left')

    # ─── Panel 2: H-plates ───────────────────────────────────────────
    ax = axes[1]
    for mat_idx, mat in enumerate(['NdFeB', 'SmCo']):
        xc_t = mat_idx * 2.5
        xc_l = mat_idx * 2.5 + 1
        tv = [r['pct_change'] for r in tunnel_h if r['material'] == mat]
        lv = [r['pct_change'] for r in lab_h if r['material'] == mat
              and r['config'].lower() not in ('beta', '')]

        for xc, vals, col in [(xc_t, tv, tunnel_color), (xc_l, lv, lab_color)]:
            if not vals:
                continue
            jitter = rng.normal(0, 0.12, len(vals))
            ax.scatter(np.full(len(vals), xc) + jitter, vals,
                       color=col, alpha=0.5, s=20, edgecolor='black',
                       linewidth=0.3, zorder=3)
            ax.hlines(np.mean(vals), xc - 0.3, xc + 0.3, colors=col,
                      linewidth=2.5, zorder=4)

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.08, zorder=0)
    ax.set_xticks([0.5, 3])
    ax.set_xticklabels(['NdFeB', 'SmCo'], fontsize=10)
    ax.set_title('H-Plates (pair assembly)', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.annotate('Lab: temp-corrected (est.)', xy=(0.98, 0.02),
                xycoords='axes fraction', ha='right', va='bottom',
                fontsize=8, fontstyle='italic', color='#666666')

    # ─── Panel 3: A-samples ──────────────────────────────────────────
    ax = axes[2]
    for mat_idx, mat in enumerate(['NdFeB', 'SmCo']):
        xc_t = mat_idx * 2.5
        xc_l = mat_idx * 2.5 + 1
        tv = [r['pct_change'] for r in tunnel_a if r['material'] == mat]
        lv = [r['pct_change'] for r in lab_a if r['material'] == mat
              and r['config'].lower() not in ('beta', '')]

        for xc, vals, col in [(xc_t, tv, tunnel_color), (xc_l, lv, lab_color)]:
            if not vals:
                continue
            jitter = rng.normal(0, 0.12, len(vals))
            ax.scatter(np.full(len(vals), xc) + jitter, vals,
                       color=col, alpha=0.5, s=20, edgecolor='black',
                       linewidth=0.3, zorder=3)
            ax.hlines(np.mean(vals), xc - 0.3, xc + 0.3, colors=col,
                      linewidth=2.5, zorder=4)

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.08, zorder=0)
    ax.set_xticks([0.5, 3])
    ax.set_xticklabels(['NdFeB', 'SmCo'], fontsize=10)
    ax.set_title('A-Samples (pair)', fontsize=12,
                 fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.annotate('Lab: temp-corrected (est.)', xy=(0.98, 0.02),
                xycoords='axes fraction', ha='right', va='bottom',
                fontsize=8, fontstyle='italic', color='#666666')

    fig.suptitle('Individual Sample Distributions: Tunnel (Exposed) vs Lab (Unexposed)\n'
                 'Horizontal lines = group means; Gray band = ±%.2f%% gain systematic' % gain_syst,
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(PLOT_DIR, 'U2_strip_all_types.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  U2: Strip plot — all sample types")


def plot_U3_effect_size_forest(data):
    """Forest plot showing tunnel−lab effect sizes across all comparisons."""
    tunnel_y = data['tunnel_y']
    lab_y = data['lab_y']
    tunnel_h = data['tunnel_h']
    lab_h = data['lab_h']
    tunnel_a = data['tunnel_a']
    lab_a = data['lab_a']
    gain_syst = data['gain_syst']
    intra_diffs, _ = data['intra_diffs']

    # Compute all tunnel−lab differences
    comparisons = []

    # Y differential (gain-immune)
    t_diffs = list(intra_diffs)
    l_diffs = [v['diff'] for v in lab_y.values() if np.isfinite(v['diff'])]
    ts = compute_stats(t_diffs)
    ls = compute_stats(l_diffs)
    d = difference_stats(ts, ls)
    comparisons.append(('Y NdFeB−SmCo\n(gain-immune)', d['mean'], d['sem'],
                         d['sigma'], True))

    # Per material Y
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        tv = [r['pct_change'] for r in tunnel_y if r['material'] == mat]
        lv = []
        for pd in lab_y.values():
            if mat in pd['slot_pcts']:
                lv.append(pd['slot_pcts'][mat])
        if tv and lv:
            d = difference_stats(compute_stats(tv), compute_stats(lv))
            comparisons.append(('Y %s' % mat, d['mean'], d['sem'],
                                 d['sigma'], False))

    # H per material
    for mat in ['NdFeB', 'SmCo']:
        tv = [r['pct_change'] for r in tunnel_h if r['material'] == mat]
        lv = [r['pct_change'] for r in lab_h if r['material'] == mat
              and r['config'].lower() not in ('beta', '')]
        if tv and lv:
            d = difference_stats(compute_stats(tv), compute_stats(lv))
            comparisons.append(('H %s' % mat, d['mean'], d['sem'],
                                 d['sigma'], False))

    # A per material
    for mat in ['NdFeB', 'SmCo']:
        tv = [r['pct_change'] for r in tunnel_a if r['material'] == mat]
        lv = [r['pct_change'] for r in lab_a if r['material'] == mat
              and r['config'].lower() not in ('beta', '')]
        if tv and lv:
            d = difference_stats(compute_stats(tv), compute_stats(lv))
            comparisons.append(('A %s' % mat, d['mean'], d['sem'],
                                 d['sigma'], False))

    if not comparisons:
        print("  U3: No comparisons available (skipped)")
        return

    fig, ax = plt.subplots(figsize=(12, max(6, len(comparisons) * 0.8)))
    y_positions = list(range(len(comparisons) - 1, -1, -1))

    for i, (label, mean, sem, sigma, is_headline) in enumerate(comparisons):
        y = y_positions[i]
        color = '#8B0000' if mean < 0 else '#3366CC'
        marker = 'D' if is_headline else 'o'
        size = 100 if is_headline else 60

        ax.errorbar(mean, y, xerr=sem, fmt='none', color=color,
                    capsize=6, linewidth=2, capthick=2, zorder=3)
        ax.scatter(mean, y, s=size, color=color, marker=marker,
                   edgecolor='black', linewidth=1, zorder=4)

        # Significance label
        sig_color = '#8B0000' if sigma >= 3 else ('#CC6600' if sigma >= 2 else '#888888')
        ax.text(mean + sem + 0.02, y, '%.1fσ' % sigma,
                va='center', ha='left', fontsize=10, fontweight='bold',
                color=sig_color)

    ax.axvline(0, color='black', linewidth=1.5, linestyle='--')
    ax.axvspan(-gain_syst, gain_syst, color='gray', alpha=0.08, zorder=0)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([c[0] for c in comparisons], fontsize=10)
    ax.set_xlabel('Tunnel − Lab Effect Size (% change)', fontsize=12)
    ax.set_title('Forest Plot: Tunnel − Lab Effect Sizes\n'
                 '(Negative = more degradation in tunnel)',
                 fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # Annotations
    ax.annotate('Gray: ±%.2f%% gain systematic' % gain_syst,
                xy=(0.98, 0.02), xycoords='axes fraction', ha='right',
                va='bottom', fontsize=9, fontstyle='italic', color='#666666')
    ax.annotate('Lab H/A: temp-corrected (est. room temps)\n'
                'Per-sample temp uncertainty tracked',
                xy=(0.02, 0.02), xycoords='axes fraction', ha='left',
                va='bottom', fontsize=8, fontstyle='italic', color='#666666')

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'U3_forest_effect_sizes.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  U3: Forest plot — effect sizes")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    data = load_all_data()

    print()
    rows = print_comprehensive_summary(data)

    print("\n" + "=" * 70)
    print("Generating plots...")
    print("=" * 70)
    plot_U1_grand_comparison(data)
    plot_U2_strip_all_types(data)
    plot_U3_effect_size_forest(data)

    print("\n" + "=" * 70)
    print("All plots saved to: %s" % PLOT_DIR)
    print("  U1: Grand comparison (4-panel bar chart)")
    print("  U2: Strip plot — individual sample distributions")
    print("  U3: Forest plot — tunnel−lab effect sizes")
    print("=" * 70)


if __name__ == '__main__':
    main()
