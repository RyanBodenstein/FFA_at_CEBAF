#!/usr/bin/env python3
"""
bugfix_slot_mapping.py — Regenerate plots affected by the slot-mapping bug.

BUG: compute_double_ratio() in manager_summary_v3.py hardcoded
     ALPHA_SLOT = {1: N42EH_alpha, 2: N52SH_alpha, 3: SmCo33H_alpha, 4: SmCo35_alpha}
     and assumed slots 1,2 = NdFeB, slots 3,4 = SmCo.

     In reality, materials are RANDOMIZED across slots (4 cyclic rotation patterns
     across the 30 Y-plates, per the Materials_Arrangements.xlsx spreadsheet).
     This caused:
       - Wrong temperature coefficients applied to ~half the plates
       - NdFeB/SmCo assignment swapped for ~half the plates
       - The differential was ATTENUATED (signal cancelled for misassigned plates)

FIX: compute_double_ratio() now accepts y_materials dict and uses correct
     per-sample material lookup for both alpha and NdFeB/SmCo grouping.

AFFECTED PLOTS (these used compute_double_ratio):
  - v3_D01: Comprehensive dashboard, panel (h) "Differential Timeline"
  - v4_C03: Intra-plate differential time series (Helmholtz panel)
  - Stdout "Double Ratio" printout

UNAFFECTED (use compute_intra_plate_diffs which groups by material name):
  - All per-material averages (N42EH: -0.333%, etc.)
  - The headline 9.7σ differential
  - All v5 plots

This script regenerates the affected v3 and v4 plots into Manager_Plots_v6_bugfix/.
"""

import sys
import os

# Ensure Cleanup_Claude is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict

from manager_summary_v3 import (
    load_all, get_gain_syst, compute_intra_plate_diffs,
    compute_double_ratio, load_teslameter_field,
    compute_gain_variability,
    MAT_COLORS, MAT_LABELS, FLAGGED, T_REF, SENTINEL, ALPHA,
    ALPHA_SLOT, MAT_BY_SLOT, REGION_ORDER, REGION_COLORS,
    PLACEMENTS, parse_teslameter_file, BASE,
)

PLOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'Manager_Plots_v6_bugfix')
os.makedirs(PLOT_DIR, exist_ok=True)


def compute_double_ratio_BUGGED(helm_raw, temp_final, ref_date, comp_date):
    """Original bugged version for comparison — hardcoded slot mapping."""
    all_plates = set(p for (p, s) in helm_raw)
    plate_diffs = []
    for plate in sorted(all_plates):
        slot_pcts = {}
        for slot in [1, 2, 3, 4]:
            key = (plate, slot)
            if key not in helm_raw:
                continue
            if ref_date not in helm_raw[key] or comp_date not in helm_raw[key]:
                continue
            ref_val = helm_raw[key][ref_date]
            comp_val = helm_raw[key][comp_date]
            sample = 'Y-%d-%d' % (plate, slot)
            ref_temp_data = temp_final.get((sample, ref_date))
            comp_temp_data = temp_final.get((sample, comp_date))
            if ref_temp_data is None or comp_temp_data is None:
                continue
            a = ALPHA_SLOT[slot]
            ref_corr = ref_val / (1 + a * (ref_temp_data[0] - T_REF))
            comp_corr = comp_val / (1 + a * (comp_temp_data[0] - T_REF))
            pct = (comp_corr - ref_corr) / ref_corr * 100.0
            slot_pcts[slot] = pct
        ndfeb_pcts = [slot_pcts[s] for s in [1, 2] if s in slot_pcts]
        smco_pcts = [slot_pcts[s] for s in [3, 4] if s in slot_pcts]
        if ndfeb_pcts and smco_pcts:
            diff = np.mean(ndfeb_pcts) - np.mean(smco_pcts)
            plate_diffs.append(diff)
    return plate_diffs


def plot_bugfix_comparison(helm_raw, temp_final, y_materials):
    """Side-by-side: bugged vs fixed differential timeline."""
    ref_date = '2025-08-27'
    dr_dates = sorted(['2025-07-17', '2025-07-30', '2025-10-21',
                       '2025-10-23', '2025-10-29', '2026-01-08', '2026-01-12'])

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # ── Panel 1: Bugged timeline ──
    ax = axes[0]
    ax.set_title('(a) BUGGED: Hardcoded Slot Mapping', fontsize=11,
                 fontweight='bold', color='red')
    for cd in dr_dates:
        diffs = compute_double_ratio_BUGGED(helm_raw, temp_final, ref_date, cd)
        if diffs:
            m = np.mean(diffs)
            s = np.std(diffs) / np.sqrt(len(diffs))
            dt = datetime.strptime(cd, '%Y-%m-%d')
            color = '#FF6600' if cd == '2025-10-21' else '#CC0000'
            ax.errorbar([dt], [m], yerr=[s], marker='D', markersize=6,
                        color=color, capsize=4, capthick=1.5, linewidth=0,
                        elinewidth=1.5)
            ax.annotate('%.3f%%\nN=%d' % (m, len(diffs)),
                        (dt, m), textcoords='offset points',
                        xytext=(0, 12), ha='center', fontsize=7)
    ax.plot(datetime.strptime(ref_date, '%Y-%m-%d'), 0, 'D',
            color='green', markersize=8, markeredgecolor='black',
            markeredgewidth=1.5, zorder=5, label='Reference (Aug 27)')
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_ylabel('NdFeB−SmCo Differential (%)', fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    # ── Panel 2: Fixed timeline ──
    ax = axes[1]
    ax.set_title('(b) FIXED: Spreadsheet Material Lookup', fontsize=11,
                 fontweight='bold', color='green')
    for cd in dr_dates:
        diffs, _ = compute_double_ratio(helm_raw, temp_final, ref_date, cd,
                                        y_materials=y_materials)
        if diffs:
            m = np.mean(diffs)
            s = np.std(diffs) / np.sqrt(len(diffs))
            dt = datetime.strptime(cd, '%Y-%m-%d')
            color = '#FF6600' if cd == '2025-10-21' else '#006600'
            ax.errorbar([dt], [m], yerr=[s], marker='D', markersize=6,
                        color=color, capsize=4, capthick=1.5, linewidth=0,
                        elinewidth=1.5)
            ax.annotate('%.3f%%\nN=%d' % (m, len(diffs)),
                        (dt, m), textcoords='offset points',
                        xytext=(0, 12), ha='center', fontsize=7)
    ax.plot(datetime.strptime(ref_date, '%Y-%m-%d'), 0, 'D',
            color='green', markersize=8, markeredgecolor='black',
            markeredgewidth=1.5, zorder=5, label='Reference (Aug 27)')
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_ylabel('NdFeB−SmCo Differential (%)', fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    # Match y-axis limits
    ymin = min(axes[0].get_ylim()[0], axes[1].get_ylim()[0])
    ymax = max(axes[0].get_ylim()[1], axes[1].get_ylim()[1])
    for a in axes[:2]:
        a.set_ylim(ymin - 0.05, ymax + 0.05)

    # ── Panel 3: Direct comparison overlay ──
    ax = axes[2]
    ax.set_title('(c) Overlay: Bug Impact', fontsize=11, fontweight='bold')

    bugged_pts, fixed_pts = [], []
    for cd in dr_dates:
        dt = datetime.strptime(cd, '%Y-%m-%d')
        diffs_b = compute_double_ratio_BUGGED(helm_raw, temp_final, ref_date, cd)
        diffs_f, _ = compute_double_ratio(helm_raw, temp_final, ref_date, cd,
                                          y_materials=y_materials)
        if diffs_b:
            mb = np.mean(diffs_b)
            sb = np.std(diffs_b) / np.sqrt(len(diffs_b))
            bugged_pts.append((dt, mb, sb))
        if diffs_f:
            mf = np.mean(diffs_f)
            sf = np.std(diffs_f) / np.sqrt(len(diffs_f))
            fixed_pts.append((dt, mf, sf))

    if bugged_pts:
        dts, ms, ss = zip(*bugged_pts)
        ax.errorbar(dts, ms, yerr=ss, marker='s', markersize=5,
                    color='red', capsize=3, linewidth=1.5, linestyle='--',
                    label='Bugged', alpha=0.7)
    if fixed_pts:
        dts, ms, ss = zip(*fixed_pts)
        ax.errorbar(dts, ms, yerr=ss, marker='D', markersize=5,
                    color='green', capsize=3, linewidth=1.5,
                    label='Fixed', alpha=0.9)

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_ylabel('NdFeB−SmCo Differential (%)', fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)

    fig.suptitle('Slot-Mapping Bug Fix: compute_double_ratio() Differential Timeline\n'
                 'Bug: hardcoded slots 1,2=NdFeB, 3,4=SmCo → wrong for ~half the plates\n'
                 'Fix: use Materials_Arrangements.xlsx for per-plate slot assignment',
                 fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, 'v6_bugfix_comparison.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: %s" % path)


def plot_fixed_v3_D01_panel_h(helm_raw, temp_final, y_materials):
    """Regenerate just the v3_D01 panel (h) differential timeline, now fixed."""
    fig, ax = plt.subplots(figsize=(8, 5))

    ref_date = '2025-08-27'
    dr_dates = sorted(['2025-07-17', '2025-07-30', '2025-10-21',
                       '2025-10-23', '2025-10-29', '2026-01-08', '2026-01-12'])

    for cd in dr_dates:
        diffs_list, _ = compute_double_ratio(helm_raw, temp_final, ref_date, cd,
                                             y_materials=y_materials)
        if diffs_list:
            m = np.mean(diffs_list)
            s = np.std(diffs_list) / np.sqrt(len(diffs_list))
            dt = datetime.strptime(cd, '%Y-%m-%d')
            color = '#FF6600' if cd == '2025-10-21' else '#8B0000'
            marker_size = 7 if cd in ('2026-01-08', '2026-01-12') else 5
            ax.errorbar([dt], [m], yerr=[s], marker='D', markersize=marker_size,
                        color=color, capsize=4, capthick=1.5, linewidth=0,
                        elinewidth=1.5)
            ax.annotate('%+.3f%% ± %.3f%%\n(%.1fσ, N=%d)' %
                        (m, s, abs(m/s) if s > 0 else 0, len(diffs_list)),
                        (dt, m), textcoords='offset points',
                        xytext=(0, 14), ha='center', fontsize=8,
                        fontweight='bold' if abs(m/s) > 3 else 'normal')

    ax.plot(datetime.strptime(ref_date, '%Y-%m-%d'), 0, 'D',
            color='#8B0000', markersize=9, markeredgecolor='gold',
            markeredgewidth=1.5, zorder=5)
    ax.annotate('Reference\n(Aug 27)', (datetime.strptime(ref_date, '%Y-%m-%d'), 0),
                textcoords='offset points', xytext=(0, -20), ha='center',
                fontsize=8, fontstyle='italic')

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1, linestyle=':',
               alpha=0.5)
    ax.annotate('Beam OFF', (datetime(2025, 10, 21), ax.get_ylim()[1]),
                textcoords='offset points', xytext=(5, -5), fontsize=7,
                color='gray', fontstyle='italic')

    ax.set_title('NdFeB−SmCo Intra-Plate Differential Timeline (FIXED)\n'
                 'Gain-immune metric, ref = Aug 27, temp-corrected',
                 fontsize=11, fontweight='bold')
    ax.set_ylabel('NdFeB − SmCo (%)', fontsize=11)
    ax.set_xlabel('Date', fontsize=11)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.grid(alpha=0.3)

    fig.text(0.02, 0.02,
             'FIX: Material assignment per slot now from spreadsheet\n'
             '(was hardcoded, wrong for ~half the plates)',
             fontsize=8, fontstyle='italic', color='green',
             transform=fig.transFigure)

    plt.tight_layout()
    path = os.path.join(PLOT_DIR, 'v6_differential_timeline_fixed.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: %s" % path)


def plot_fixed_v4_C03(helm_raw, temp_final, y_materials):
    """Regenerate v4_C03 Helmholtz differential timeline panel, now fixed."""
    fig, ax = plt.subplots(figsize=(8, 5))

    ref_date = '2025-08-27'
    dr_dates = sorted(['2025-07-17', '2025-07-30', '2025-10-21',
                       '2025-10-23', '2025-10-29', '2026-01-08', '2026-01-12'])

    dts_all, ms_all, ss_all, ns_all = [], [], [], []
    for cd in dr_dates:
        diffs, _ = compute_double_ratio(helm_raw, temp_final, ref_date, cd,
                                        y_materials=y_materials)
        if diffs:
            dt = datetime.strptime(cd, '%Y-%m-%d')
            m = np.mean(diffs)
            s = np.std(diffs) / np.sqrt(len(diffs))
            dts_all.append(dt)
            ms_all.append(m)
            ss_all.append(s)
            ns_all.append(len(diffs))

    # Plot with ref point
    ref_dt = datetime.strptime(ref_date, '%Y-%m-%d')
    dts_full = [ref_dt] + dts_all
    ms_full = [0.0] + ms_all
    ss_full = [0.0] + ss_all

    ax.errorbar(dts_full, ms_full, yerr=ss_full,
                color='#8B0000', marker='D', markersize=7,
                linewidth=2, capsize=5, capthick=2,
                label='Helmholtz NdFeB−SmCo (fixed)')

    # Annotate each point
    for dt, m, s, n in zip(dts_all, ms_all, ss_all, ns_all):
        sig = abs(m/s) if s > 0 else 0
        ax.annotate('%.3f%%\n%.1fσ, N=%d' % (m, sig, n),
                    (dt, m), textcoords='offset points',
                    xytext=(0, 12), ha='center', fontsize=7)

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1, linestyle=':')
    ax.annotate('Beam OFF', (datetime(2025, 10, 21), ax.get_ylim()[1] * 0.9),
                fontsize=8, color='gray', fontstyle='italic')

    ax.set_title('Helmholtz NdFeB−SmCo Intra-Plate Differential (FIXED)\n'
                 'Corrected slot-to-material mapping from spreadsheet',
                 fontsize=11, fontweight='bold')
    ax.set_ylabel('NdFeB − SmCo (%)', fontsize=11)
    ax.set_xlabel('Date', fontsize=11)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)

    plt.tight_layout()
    path = os.path.join(PLOT_DIR, 'v6_v4C03_differential_timeline_fixed.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  Saved: %s" % path)


def main():
    print("=" * 70)
    print("BUGFIX: Slot-Mapping Correction for compute_double_ratio()")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    results, helm_raw, temp_final, y_materials = load_all()
    clean = [r for r in results if not r['is_outlier']]
    print("  %d samples loaded (%d clean)" % (len(results), len(clean)))

    # ── Print comparison: bugged vs fixed ──
    print("\n" + "=" * 70)
    print("COMPARISON: Bugged vs Fixed Double Ratio")
    print("=" * 70)

    ref_date = '2025-08-27'
    comp_dates = ['2025-07-17', '2025-07-30', '2025-10-21',
                  '2025-10-23', '2025-10-29', '2026-01-08', '2026-01-12']

    print("\n%-12s  %-25s  %-25s  %s" % ('Date', 'BUGGED', 'FIXED', 'Change'))
    print("-" * 85)
    for cd in sorted(comp_dates):
        diffs_b = compute_double_ratio_BUGGED(helm_raw, temp_final, ref_date, cd)
        diffs_f, _ = compute_double_ratio(helm_raw, temp_final, ref_date, cd,
                                          y_materials=y_materials)
        if diffs_b and diffs_f:
            mb = np.mean(diffs_b)
            sb = np.std(diffs_b) / np.sqrt(len(diffs_b))
            mf = np.mean(diffs_f)
            sf = np.std(diffs_f) / np.sqrt(len(diffs_f))
            sig_b = abs(mb/sb) if sb > 0 else 0
            sig_f = abs(mf/sf) if sf > 0 else 0
            print("%-12s  %+.4f ± %.4f (%4.1fσ, N=%2d)  %+.4f ± %.4f (%4.1fσ, N=%2d)  Δ=%+.4f" %
                  (cd, mb, sb, sig_b, len(diffs_b),
                   mf, sf, sig_f, len(diffs_f),
                   mf - mb))

    # Also print the headline comparison
    print("\n" + "=" * 70)
    print("HEADLINE: compute_intra_plate_diffs (UNAFFECTED by bug)")
    print("=" * 70)
    intra_diffs, intra_details = compute_intra_plate_diffs(clean)
    if intra_diffs:
        m = np.mean(intra_diffs)
        s = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
        print("  NdFeB−SmCo differential: %+.3f%% ± %.3f%% (%.1fσ, N=%d)" %
              (m, s, abs(m/s), len(intra_diffs)))
        print("  (This uses material names from spreadsheet — always correct)")

    # ── Generate plots ──
    print("\n" + "=" * 70)
    print("Generating bugfix plots to: %s" % PLOT_DIR)
    print("=" * 70)

    plot_bugfix_comparison(helm_raw, temp_final, y_materials)
    plot_fixed_v3_D01_panel_h(helm_raw, temp_final, y_materials)
    plot_fixed_v4_C03(helm_raw, temp_final, y_materials)

    print("\n" + "=" * 70)
    print("Done. 3 plots saved to %s/" % PLOT_DIR)
    print("=" * 70)


if __name__ == '__main__':
    main()
