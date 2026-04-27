#!/usr/bin/env python3
"""
Manager-Friendly Degradation Summary Plots — Version 5

Comprehensive combined Y-plate + H-plate analysis with:
  - Waterfall plots by region (A01-A03)
  - Regional & pass-number analysis (B01-B04)
  - Assembly configuration breakdown (C01-C02)
  - Overall summary & publication figures (D01-D04)
  - Time series (E01-E02)

Imports shared code from v3 (parsers, Y-plate loaders, gain systematic)
and v2 (H-plate loaders, placement mappings with line numbers).

Output: Cleanup_Claude/Manager_Plots_v5/v5_*.png (~16 plots)
"""

import os
import sys
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict

# ─── Add our directory to path for imports ───────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

# ─── Imports from v3 ─────────────────────────────────────────────────────────
from manager_summary_v3 import (
    load_all, get_gain_syst, compute_intra_plate_diffs,
    MAT_COLORS, MAT_LABELS, FLAGGED, T_REF, SENTINEL, ALPHA as ALPHA_V3,
    ALPHA_SLOT, REGION_ORDER, REGION_COLORS,
    PLACEMENTS as PLACEMENTS_SIMPLE,
)

# ─── Imports from v2 ─────────────────────────────────────────────────────────
from degradation_summary_v2 import (
    load_materials, build_temperature_lookup,
    compute_h_plate_degradation, compute_y_plate_degradation,
    PLACEMENTS as PLACEMENTS_FULL,
    Y_PLACEMENT, H_PLACEMENT,
    ALPHA, correct_helmholtz, compute_robust_baseline,
    get_all_mwc_rows, parse_helmholtz_file as parse_helmholtz_v2,
    parse_teslameter_file as parse_teslameter_v2,
    TUNNEL_START, FLAGGED_OUTLIERS, summarize_group,
)

# ─── Output directory ────────────────────────────────────────────────────────
PLOT_DIR = os.path.join(BASE, 'Manager_Plots_v5')
os.makedirs(PLOT_DIR, exist_ok=True)

# ─── New constants for v5 ────────────────────────────────────────────────────
CONFIG_COLORS = {
    'Alpha': '#1F77B4', 'Beta': '#FF7F0E',
    'Gamma': '#2CA02C', 'Delta': '#D62728',
}
CONFIG_HATCHES = {
    'Alpha': None, 'Beta': '///', 'Gamma': None, 'Delta': None,
}
HMAT_COLORS = {'NdFeB': '#CC4444', 'SmCo': '#44AA44'}

# Line number labels (arc positions: 1=top/lowest E, 5=bottom/highest E)
PASS_LABELS = {
    1: 'Line 1\n(lowest E)',
    2: 'Line 2',
    3: 'Line 3',
    4: 'Line 4',
    5: 'Line 5\n(highest E)',
}

# Build PLACEMENTS_WITH_LINE: plate_num -> {region, line, h_plate, sub_location}
PLACEMENTS_WITH_LINE = {}
for y, h, region, subloc, line in PLACEMENTS_FULL:
    ynum = int(y.replace('Y', ''))
    PLACEMENTS_WITH_LINE[ynum] = {
        'y_plate': y, 'h_plate': h, 'region': region,
        'sub_location': subloc, 'line': line,
    }


# ─── H-plate time series builder ────────────────────────────────────────────

def build_h_plate_timeseries(pair_arrangements, temp_lookup):
    """Build H-plate Helmholtz time series (date_pcts) for each pair assembly.

    Returns list of dicts with 'date_pcts' field, matching v3 Y-plate format.
    """
    helm_dir = os.path.join(BASE, 'Pair_Assemblies', 'Helmholtz')
    results = []

    for f in sorted(os.listdir(helm_dir)):
        m = re.match(r'(H[ns]-\d+-\d+)_helmholtz\.dat$', f)
        if not m:
            continue
        h_sample = m.group(1)
        hm = re.match(r'H([ns])-(\d+)-(\d+)', h_sample)
        if not hm:
            continue
        ns = hm.group(1)
        plate_num = int(hm.group(2))
        slot = int(hm.group(3))
        mat_type = 'NdFeB' if ns == 'n' else 'SmCo'
        alpha = ALPHA[mat_type]

        plate_key = '%s-%d' % (ns, plate_num)
        config = ''
        if plate_key in pair_arrangements:
            _, configs = pair_arrangements[plate_key]
            if slot - 1 < len(configs):
                config = configs[slot - 1]

        h_lookup_key = '%s%d' % ('N' if ns == 'n' else 'S', plate_num)
        placement = H_PLACEMENT.get(h_lookup_key)
        if not placement:
            continue

        fpath = os.path.join(helm_dir, f)
        raw_rows = get_all_mwc_rows(parse_helmholtz_v2(fpath))
        if not raw_rows:
            continue

        pre_corr_vals = []
        tunnel_corr = []
        for dt, h_raw in raw_rows:
            date_str = dt.strftime('%Y-%m-%d')
            key = (h_sample, date_str)
            if key in temp_lookup:
                t_mean, t_std = temp_lookup[key]
                h_corr, dh = correct_helmholtz(h_raw, alpha, t_mean, t_std)
                if dt < TUNNEL_START:
                    pre_corr_vals.append(h_corr)
                else:
                    tunnel_corr.append((dt, h_corr))

        if not pre_corr_vals or not tunnel_corr:
            continue

        bl = compute_robust_baseline(pre_corr_vals)
        if bl is None:
            continue
        baseline_mean = bl[0]
        n_kept = bl[2]
        if abs(baseline_mean) < 0.1:
            continue

        tunnel_corr.sort(key=lambda x: x[0])
        latest_corr = tunnel_corr[-1][1]
        pct_change = (latest_corr - baseline_mean) / baseline_mean * 100.0

        is_outlier = (abs(pct_change) > 5.0 or
                      (n_kept == 1 and abs(pct_change) > 2.0))

        date_pcts = []
        for dt, h_corr in tunnel_corr:
            date_pcts.append((dt, (h_corr - baseline_mean) / baseline_mean * 100.0))

        results.append({
            'sample': h_sample, 'plate': plate_num, 'slot': slot,
            'material': mat_type, 'config': config,
            'region': placement['region'], 'line': placement['line'],
            'pct_change': pct_change, 'is_outlier': is_outlier,
            'date_pcts': date_pcts,
            'bl_mean': baseline_mean, 'n_baseline': n_kept,
        })

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY A: Waterfall Plots
# ═══════════════════════════════════════════════════════════════════════════════

def plot_A01_waterfall_by_region_Y(y_results, gain_syst):
    """Y-plate waterfall, grouped by region, colored by material grade."""
    clean = [r for r in y_results if not r['is_outlier']]

    fig, ax = plt.subplots(figsize=(12, 20))
    y_pos = 0
    yticks, ylabels = [], []
    region_boundaries = []

    for region in REGION_ORDER:
        group = sorted([r for r in clean if r['region'] == region],
                       key=lambda r: r['pct_change'])
        if not group:
            continue
        region_boundaries.append((y_pos, region))
        for r in group:
            color = MAT_COLORS.get(r['material'], '#888888')
            ax.barh(y_pos, r['pct_change'], height=0.7, color=color,
                    alpha=0.85, edgecolor='black', linewidth=0.3)
            yticks.append(y_pos)
            line_str = ' (L%d)' % r['line'] if r.get('line', 0) > 0 else ''
            ylabels.append('%s [%s]%s' % (r['sample'], r['material'], line_str))
            y_pos += 1
        y_pos += 1  # gap between regions

    # Gain systematic band
    ax.axvspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axvline(0, color='black', linewidth=0.8)

    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=6)
    ax.set_xlabel('% Change from Baseline (corrected to 20°C)', fontsize=11)
    ax.set_title('Y-Plate Degradation — All Samples by Region\n'
                 '(Gray band = Helmholtz gain systematic ±%.2f%%)' % gain_syst,
                 fontsize=13, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # Region labels
    for ystart, region in region_boundaries:
        ax.annotate(region, xy=(-0.01, ystart - 0.5),
                    xycoords=('axes fraction', 'data'),
                    fontsize=10, fontweight='bold', color='gray',
                    ha='right', va='bottom')

    # Legend
    handles = [mpatches.Patch(color=MAT_COLORS[m], label=MAT_LABELS[m])
               for m in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']]
    ax.legend(handles=handles, fontsize=8, loc='lower right')
    ax.invert_yaxis()

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v5_A01_waterfall_by_region_Y.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  A01: Y-plate waterfall by region")


def plot_A02_waterfall_by_region_H(h_results, gain_syst):
    """H-plate waterfall, grouped by region, colored by material, config annotated."""
    clean = [r for r in h_results if not r.get('is_outlier', False)]

    fig, ax = plt.subplots(figsize=(12, 16))
    y_pos = 0
    yticks, ylabels = [], []
    region_boundaries = []

    for region in REGION_ORDER:
        group = sorted([r for r in clean if r['region'] == region],
                       key=lambda r: r['pct_change'])
        if not group:
            continue
        region_boundaries.append((y_pos, region))
        for r in group:
            color = HMAT_COLORS.get(r['material'], '#888888')
            hatch = CONFIG_HATCHES.get(r.get('config', ''), None)
            bar = ax.barh(y_pos, r['pct_change'], height=0.7, color=color,
                          alpha=0.80, edgecolor='black', linewidth=0.3,
                          hatch=hatch)
            # Config annotation
            cfg = r.get('config', '')
            if cfg:
                x_pos = r['pct_change'] + 0.02 if r['pct_change'] >= 0 else r['pct_change'] - 0.02
                ha = 'left' if r['pct_change'] >= 0 else 'right'
                ax.text(x_pos, y_pos, cfg, fontsize=6, ha=ha, va='center',
                        color='#444444')
            yticks.append(y_pos)
            line_str = ' (L%d)' % r['line'] if r.get('line', 0) > 0 else ''
            ylabels.append('%s [%s]%s' % (r['sample'], r['material'], line_str))
            y_pos += 1
        y_pos += 1

    ax.axvspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axvline(0, color='black', linewidth=0.8)

    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=6)
    ax.set_xlabel('% Change from Baseline (corrected to 20°C)', fontsize=11)
    ax.set_title('H-Plate (Pair Assembly) Degradation — All Samples by Region\n'
                 '(Gray band = gain syst. ±%.2f%%; hatched = Beta/antiparallel)' % gain_syst,
                 fontsize=13, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    for ystart, region in region_boundaries:
        ax.annotate(region, xy=(-0.01, ystart - 0.5),
                    xycoords=('axes fraction', 'data'),
                    fontsize=10, fontweight='bold', color='gray',
                    ha='right', va='bottom')

    handles = [mpatches.Patch(color=HMAT_COLORS[m], label=m) for m in ['NdFeB', 'SmCo']]
    handles.append(mpatches.Patch(facecolor='white', edgecolor='black',
                                   hatch='///', label='Beta (unreliable)'))
    ax.legend(handles=handles, fontsize=8, loc='lower right')
    ax.invert_yaxis()

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v5_A02_waterfall_by_region_H.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  A02: H-plate waterfall by region")


def plot_A03_waterfall_combined(y_results, h_results, gain_syst):
    """Side-by-side Y + H waterfalls at same x-axis scale."""
    y_clean = [r for r in y_results if not r['is_outlier']]
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 14), sharey=False)

    # Determine common x-axis limits
    all_pcts = ([r['pct_change'] for r in y_clean] +
                [r['pct_change'] for r in h_clean])
    if all_pcts:
        xlim = (min(all_pcts) - 0.2, max(all_pcts) + 0.2)
    else:
        xlim = (-1.5, 1.5)

    # Y-plate panel
    y_sorted = sorted(y_clean, key=lambda r: r['pct_change'])
    for i, r in enumerate(y_sorted):
        color = MAT_COLORS.get(r['material'], '#888888')
        ax1.barh(i, r['pct_change'], height=0.7, color=color,
                 alpha=0.85, edgecolor='none')
    ax1.axvspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax1.axvline(0, color='black', linewidth=0.8)
    ax1.set_xlim(xlim)
    ax1.set_title('Y-Plate (N=%d)' % len(y_sorted), fontsize=12, fontweight='bold')
    ax1.set_xlabel('% Change from Baseline', fontsize=11)
    ax1.set_yticks([])
    ax1.grid(axis='x', alpha=0.3)
    handles = [mpatches.Patch(color=MAT_COLORS[m], label=MAT_LABELS[m])
               for m in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']]
    ax1.legend(handles=handles, fontsize=8, loc='lower right')

    # H-plate panel
    h_sorted = sorted(h_clean, key=lambda r: r['pct_change'])
    for i, r in enumerate(h_sorted):
        color = HMAT_COLORS.get(r['material'], '#888888')
        hatch = CONFIG_HATCHES.get(r.get('config', ''), None)
        ax2.barh(i, r['pct_change'], height=0.7, color=color,
                 alpha=0.80, edgecolor='none', hatch=hatch)
    ax2.axvspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax2.axvline(0, color='black', linewidth=0.8)
    ax2.set_xlim(xlim)
    ax2.set_title('H-Plate (N=%d)' % len(h_sorted), fontsize=12, fontweight='bold')
    ax2.set_xlabel('% Change from Baseline', fontsize=11)
    ax2.set_yticks([])
    ax2.grid(axis='x', alpha=0.3)
    handles2 = [mpatches.Patch(color=HMAT_COLORS[m], label=m) for m in ['NdFeB', 'SmCo']]
    ax2.legend(handles=handles2, fontsize=8, loc='lower right')

    fig.suptitle('Combined Waterfall: Y-Plate vs H-Plate Degradation\n'
                 '(Gray band = gain systematic ±%.2f%%)' % gain_syst,
                 fontsize=14, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(PLOT_DIR, 'v5_A03_waterfall_combined.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  A03: Combined waterfall (Y + H side-by-side)")


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY B: Regional & Pass Number
# ═══════════════════════════════════════════════════════════════════════════════

def plot_B01_regional_bars_Y(y_results, gain_syst):
    """Y-plate grouped bars by region x material."""
    clean = [r for r in y_results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(REGION_ORDER))
    width = 0.18
    offsets = [-1.5, -0.5, 0.5, 1.5]

    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)

    for i, mat in enumerate(materials):
        means, errs, ns = [], [], []
        for region in REGION_ORDER:
            vals = [r['pct_change'] for r in clean
                    if r['region'] == region and r['material'] == mat]
            if vals:
                means.append(np.mean(vals))
                errs.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                            if len(vals) > 1 else 0.05)
                ns.append(len(vals))
            else:
                means.append(0)
                errs.append(0)
                ns.append(0)
        bars = ax.bar(x + offsets[i] * width, means, width, yerr=errs,
                      color=MAT_COLORS[mat], capsize=3, alpha=0.85,
                      edgecolor='black', linewidth=0.5,
                      label=MAT_LABELS[mat])
        # N labels
        for j, (xi, n) in enumerate(zip(x + offsets[i] * width, ns)):
            if n > 0:
                ax.text(xi, -0.02, str(n), fontsize=6, ha='center',
                        va='top', color='#555')

    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(REGION_ORDER, fontsize=10, rotation=15)
    ax.set_ylabel('% Change from Baseline', fontsize=12)
    ax.set_title('Y-Plate Degradation by Region and Material\n'
                 '(Temp-corrected to 20°C; gray band = gain syst. ±%.2f%%)' % gain_syst,
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=9, loc='lower left')
    ax.grid(axis='y', alpha=0.3)

    # Highlight arcs vs linacs
    ax.axvspan(-0.5, 3.5, alpha=0.04, color='red')
    ax.axvspan(3.5, 5.5, alpha=0.04, color='blue')
    ax.axvspan(5.5, 6.5, alpha=0.04, color='green')

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v5_B01_regional_bars_Y.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  B01: Y-plate regional bars")


def plot_B02_pass_number_trend(y_results, h_results, gain_syst):
    """Degradation vs arc line position (pass number) — the key physics plot."""
    y_clean = [r for r in y_results if not r['is_outlier'] and r.get('line', 0) > 0]
    h_clean = [r for r in h_results if not r.get('is_outlier', False) and r.get('line', 0) > 0]

    # Enrich Y results with line numbers from PLACEMENTS_WITH_LINE
    for r in y_clean:
        if 'line' not in r or r['line'] == 0:
            info = PLACEMENTS_WITH_LINE.get(r['plate'])
            if info:
                r['line'] = info['line']

    fig, (ax, ax_inset) = plt.subplots(1, 2, figsize=(16, 7),
                                         gridspec_kw={'width_ratios': [3, 1]})

    lines = [1, 2, 3, 4, 5]

    # Y-plate NdFeB
    y_nd_means, y_nd_sems, y_nd_ns = [], [], []
    for line in lines:
        vals = [r['pct_change'] for r in y_clean
                if r['material'] in ['N42EH', 'N52SH'] and r['line'] == line]
        if vals:
            y_nd_means.append(np.mean(vals))
            y_nd_sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                             if len(vals) > 1 else 0.05)
            y_nd_ns.append(len(vals))
        else:
            y_nd_means.append(np.nan)
            y_nd_sems.append(0)
            y_nd_ns.append(0)

    # Y-plate SmCo
    y_sm_means, y_sm_sems = [], []
    for line in lines:
        vals = [r['pct_change'] for r in y_clean
                if r['material'] in ['SmCo33H', 'SmCo35'] and r['line'] == line]
        if vals:
            y_sm_means.append(np.mean(vals))
            y_sm_sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                             if len(vals) > 1 else 0.05)
        else:
            y_sm_means.append(np.nan)
            y_sm_sems.append(0)

    # H-plate NdFeB
    h_nd_means, h_nd_sems = [], []
    for line in lines:
        vals = [r['pct_change'] for r in h_clean
                if r['material'] == 'NdFeB' and r['line'] == line]
        if vals:
            h_nd_means.append(np.mean(vals))
            h_nd_sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                             if len(vals) > 1 else 0.05)
        else:
            h_nd_means.append(np.nan)
            h_nd_sems.append(0)

    # H-plate SmCo
    h_sm_means, h_sm_sems = [], []
    for line in lines:
        vals = [r['pct_change'] for r in h_clean
                if r['material'] == 'SmCo' and r['line'] == line]
        if vals:
            h_sm_means.append(np.mean(vals))
            h_sm_sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                             if len(vals) > 1 else 0.05)
        else:
            h_sm_means.append(np.nan)
            h_sm_sems.append(0)

    # Main panel
    offset = 0.08
    ax.errorbar(np.array(lines) - offset, y_nd_means, yerr=y_nd_sems,
                color='#CC4444', marker='o', markersize=8, linewidth=2,
                capsize=5, capthick=2, label='Y-plate NdFeB', zorder=5)
    ax.errorbar(np.array(lines) + offset, y_sm_means, yerr=y_sm_sems,
                color='#44AA44', marker='o', markersize=8, linewidth=2,
                capsize=5, capthick=2, label='Y-plate SmCo', zorder=5)
    ax.errorbar(np.array(lines) - offset, h_nd_means, yerr=h_nd_sems,
                color='#CC4444', marker='s', markersize=8, linewidth=1.5,
                capsize=5, capthick=1.5, linestyle='--', fillstyle='none',
                markeredgewidth=2, label='H-plate NdFeB', zorder=4)
    ax.errorbar(np.array(lines) + offset, h_sm_means, yerr=h_sm_sems,
                color='#44AA44', marker='s', markersize=8, linewidth=1.5,
                capsize=5, capthick=1.5, linestyle='--', fillstyle='none',
                markeredgewidth=2, label='H-plate SmCo', zorder=4)

    # Individual Y-plate points (scatter)
    for r in y_clean:
        if r['material'] in ['N42EH', 'N52SH']:
            ax.plot(r['line'] - offset + np.random.normal(0, 0.02),
                    r['pct_change'], '.', color='#CC4444', alpha=0.2, markersize=4)
        else:
            ax.plot(r['line'] + offset + np.random.normal(0, 0.02),
                    r['pct_change'], '.', color='#44AA44', alpha=0.2, markersize=4)

    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_xticks(lines)
    ax.set_xticklabels([PASS_LABELS[l] for l in lines], fontsize=10)
    ax.set_xlabel('Arc Line Position', fontsize=12)
    ax.set_ylabel('% Change from Baseline', fontsize=12)
    ax.set_title('Degradation vs Arc Line Position (Pass Number)\n'
                 'Line 1 = top (lowest beam energy) → Line 5 = bottom (highest beam energy)',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='lower left')
    ax.grid(alpha=0.3)

    # Inset: grouped bars for top (1-2) vs bottom (3-5)
    top_nd = [r['pct_change'] for r in y_clean
              if r['material'] in ['N42EH', 'N52SH'] and r['line'] in [1, 2]]
    bot_nd = [r['pct_change'] for r in y_clean
              if r['material'] in ['N42EH', 'N52SH'] and r['line'] in [3, 4, 5]]
    top_sm = [r['pct_change'] for r in y_clean
              if r['material'] in ['SmCo33H', 'SmCo35'] and r['line'] in [1, 2]]
    bot_sm = [r['pct_change'] for r in y_clean
              if r['material'] in ['SmCo33H', 'SmCo35'] and r['line'] in [3, 4, 5]]

    bar_data = []
    for label, vals, color in [('Top NdFeB', top_nd, '#CC4444'),
                                ('Bot NdFeB', bot_nd, '#EE8888'),
                                ('Top SmCo', top_sm, '#44AA44'),
                                ('Bot SmCo', bot_sm, '#88CC88')]:
        if vals:
            bar_data.append((label, np.mean(vals),
                             np.std(vals, ddof=1) / np.sqrt(len(vals))
                             if len(vals) > 1 else 0.05,
                             len(vals), color))

    if bar_data:
        bx = np.arange(len(bar_data))
        ax_inset.bar(bx, [b[1] for b in bar_data],
                     yerr=[b[2] for b in bar_data],
                     color=[b[4] for b in bar_data],
                     capsize=4, edgecolor='black', linewidth=0.5,
                     alpha=0.85, width=0.6)
        ax_inset.set_xticks(bx)
        ax_inset.set_xticklabels(['%s\n(N=%d)' % (b[0], b[3]) for b in bar_data],
                                  fontsize=7, rotation=15)
        ax_inset.axhline(0, color='black', linewidth=1, linestyle='--')
        ax_inset.set_ylabel('% Change', fontsize=10)
        ax_inset.set_title('Top Lines (1-2) vs\nBottom Lines (3-5)',
                           fontsize=10, fontweight='bold')
        ax_inset.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v5_B02_pass_number_trend.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  B02: Pass number trend")


def plot_B03_arc_panels(y_results, h_results, gain_syst):
    """4-panel: one per arc (SE, NE, NW, SW), 5 lines each."""
    y_clean = [r for r in y_results if not r['is_outlier']]
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]
    arcs = ['SE Arc', 'NE Arc', 'NW Arc', 'SW Arc']
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    lines = [1, 2, 3, 4, 5]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12), sharey=True)

    for idx, (arc, ax) in enumerate(zip(arcs, axes.flat)):
        x = np.arange(len(lines))
        width = 0.18
        offsets = [-1.5, -0.5, 0.5, 1.5]

        ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)

        for i, mat in enumerate(materials):
            means = []
            for line in lines:
                vals = [r['pct_change'] for r in y_clean
                        if r['region'] == arc and r['material'] == mat
                        and r.get('line', 0) == line]
                means.append(np.mean(vals) if vals else np.nan)
            ax.bar(x + offsets[i] * width, means, width,
                   color=MAT_COLORS[mat], alpha=0.85,
                   edgecolor='black', linewidth=0.5,
                   label=MAT_LABELS[mat] if idx == 0 else None)

        # H-plate markers
        for r in h_clean:
            if r['region'] == arc and r.get('line', 0) > 0:
                marker_color = HMAT_COLORS.get(r['material'], '#888888')
                ax.plot(r['line'] - 1, r['pct_change'], 'D',
                        color=marker_color, markersize=8, markeredgecolor='black',
                        markeredgewidth=1, zorder=6, alpha=0.7)

        ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
        ax.set_xticks(x)
        ax.set_xticklabels(['L%d' % l for l in lines], fontsize=10)
        ax.set_title(arc, fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        if idx % 2 == 0:
            ax.set_ylabel('% Change', fontsize=11)

    # Add common legend
    handles = [mpatches.Patch(color=MAT_COLORS[m], label=MAT_LABELS[m])
               for m in materials]
    handles.append(plt.Line2D([], [], marker='D', color='gray', linestyle='',
                               markersize=8, markeredgecolor='black',
                               label='H-plate (co-located)'))
    fig.legend(handles=handles, fontsize=9, loc='lower center', ncol=5,
               bbox_to_anchor=(0.5, -0.02))

    fig.suptitle('Degradation by Arc and Line Position\n'
                 '(Line 1 = top/lowest E, Line 5 = bottom/highest E)',
                 fontsize=14, fontweight='bold')
    fig.tight_layout(rect=[0, 0.03, 1, 0.93])
    fig.savefig(os.path.join(PLOT_DIR, 'v5_B03_arc_panels.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  B03: Arc panels (4 arcs x 5 lines)")


def plot_B04_region_heatmap(y_results, h_results):
    """Region x material degradation grid (heatmap)."""
    y_clean = [r for r in y_results if not r['is_outlier']]
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]

    regions = REGION_ORDER
    y_mats = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    h_mats = ['NdFeB', 'SmCo']
    all_cols = y_mats + ['H-' + m for m in h_mats]

    grid = np.full((len(regions), len(all_cols)), np.nan)
    n_grid = np.zeros((len(regions), len(all_cols)), dtype=int)

    for ri, region in enumerate(regions):
        for ci, mat in enumerate(y_mats):
            vals = [r['pct_change'] for r in y_clean
                    if r['region'] == region and r['material'] == mat]
            if vals:
                grid[ri, ci] = np.mean(vals)
                n_grid[ri, ci] = len(vals)
        for ci2, mat in enumerate(h_mats):
            ci = len(y_mats) + ci2
            vals = [r['pct_change'] for r in h_clean
                    if r['region'] == region and r['material'] == mat]
            if vals:
                grid[ri, ci] = np.mean(vals)
                n_grid[ri, ci] = len(vals)

    fig, ax = plt.subplots(figsize=(12, 7))

    # Use diverging colormap: red=negative, white=zero, green=positive
    vmax = max(abs(np.nanmin(grid)), abs(np.nanmax(grid)), 0.5)
    im = ax.imshow(grid, cmap='RdYlGn', vmin=-vmax, vmax=vmax, aspect='auto')
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, label='Mean % Change')

    ax.set_xticks(range(len(all_cols)))
    ax.set_xticklabels(all_cols, fontsize=10, rotation=30, ha='right')
    ax.set_yticks(range(len(regions)))
    ax.set_yticklabels(regions, fontsize=10)

    # Annotate cells
    for ri in range(len(regions)):
        for ci in range(len(all_cols)):
            if not np.isnan(grid[ri, ci]):
                text_color = 'white' if abs(grid[ri, ci]) > vmax * 0.6 else 'black'
                ax.text(ci, ri, '%+.2f%%\n(N=%d)' % (grid[ri, ci], n_grid[ri, ci]),
                        ha='center', va='center', fontsize=8, color=text_color,
                        fontweight='bold')
            else:
                ax.text(ci, ri, '—', ha='center', va='center', fontsize=10,
                        color='gray')

    # Vertical line separating Y and H
    ax.axvline(len(y_mats) - 0.5, color='black', linewidth=2)
    ax.text(len(y_mats) / 2 - 0.5, -0.8, 'Y-Plate', ha='center', fontsize=11,
            fontweight='bold')
    ax.text(len(y_mats) + len(h_mats) / 2 - 0.5, -0.8, 'H-Plate', ha='center',
            fontsize=11, fontweight='bold')

    ax.set_title('Degradation Heatmap: Region × Material\n'
                 '(Temperature-corrected Helmholtz, outliers excluded)',
                 fontsize=13, fontweight='bold')

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v5_B04_region_heatmap.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  B04: Region x material heatmap")


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY C: Assembly Configuration
# ═══════════════════════════════════════════════════════════════════════════════

def plot_C01_assembly_config_bars(h_results, gain_syst):
    """H-plate by config (4 configs x 2 materials)."""
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]
    configs = ['Alpha', 'Beta', 'Gamma', 'Delta']
    h_mats = ['NdFeB', 'SmCo']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Panel 1: All configs
    x = np.arange(len(configs))
    width = 0.35
    for i, mat in enumerate(h_mats):
        means, errs, ns = [], [], []
        for cfg in configs:
            vals = [r['pct_change'] for r in h_clean
                    if r['material'] == mat and r.get('config', '') == cfg]
            if vals:
                means.append(np.mean(vals))
                errs.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                            if len(vals) > 1 else 0.1)
                ns.append(len(vals))
            else:
                means.append(0)
                errs.append(0)
                ns.append(0)
        offset = -width / 2 + i * width
        bars = ax1.bar(x + offset, means, width, yerr=errs,
                       color=HMAT_COLORS[mat], capsize=5,
                       edgecolor='black', linewidth=0.5, alpha=0.85,
                       label=mat)
        # Hatch Beta bars
        for j, cfg in enumerate(configs):
            if cfg == 'Beta':
                bars[j].set_hatch('///')
        # N labels
        for j, (xi, n) in enumerate(zip(x + offset, ns)):
            if n > 0:
                ax1.text(xi, means[j] + errs[j] + 0.02 if means[j] >= 0
                         else means[j] - errs[j] - 0.02,
                         'N=%d' % n, fontsize=7, ha='center',
                         va='bottom' if means[j] >= 0 else 'top')

    ax1.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax1.axhline(0, color='black', linewidth=1)
    ax1.set_xticks(x)
    ax1.set_xticklabels(configs, fontsize=11)
    ax1.set_ylabel('% Change from Baseline', fontsize=12)
    ax1.set_title('H-Plate Degradation by Assembly Configuration\n'
                  '(All configs; Beta hatched = unreliable)',
                  fontsize=12, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(axis='y', alpha=0.3)

    # Panel 2: Excluding Beta
    configs_nb = ['Alpha', 'Gamma', 'Delta']
    x2 = np.arange(len(configs_nb))
    for i, mat in enumerate(h_mats):
        means, errs, ns = [], [], []
        for cfg in configs_nb:
            vals = [r['pct_change'] for r in h_clean
                    if r['material'] == mat and r.get('config', '') == cfg]
            if vals:
                means.append(np.mean(vals))
                errs.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                            if len(vals) > 1 else 0.1)
                ns.append(len(vals))
            else:
                means.append(0)
                errs.append(0)
                ns.append(0)
        offset = -width / 2 + i * width
        ax2.bar(x2 + offset, means, width, yerr=errs,
                color=HMAT_COLORS[mat], capsize=5,
                edgecolor='black', linewidth=0.5, alpha=0.85,
                label=mat)
        for j, (xi, n) in enumerate(zip(x2 + offset, ns)):
            if n > 0:
                ax2.text(xi, means[j] + errs[j] + 0.02 if means[j] >= 0
                         else means[j] - errs[j] - 0.02,
                         'N=%d' % n, fontsize=7, ha='center',
                         va='bottom' if means[j] >= 0 else 'top')

    ax2.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax2.axhline(0, color='black', linewidth=1)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(configs_nb, fontsize=11)
    ax2.set_ylabel('% Change from Baseline', fontsize=12)
    ax2.set_title('H-Plate Degradation (Excluding Beta)\n'
                  '(Beta/antiparallel excluded — unreliable Helmholtz readings)',
                  fontsize=12, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v5_C01_assembly_config_bars.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  C01: Assembly configuration bars")


def plot_C02_assembly_config_by_region(h_results, gain_syst):
    """Config x region-type (Arc vs Linac)."""
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]
    configs = ['Alpha', 'Beta', 'Gamma', 'Delta']
    region_types = {
        'Arc': ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc'],
        'Linac': ['North Linac', 'South Linac'],
    }

    fig, ax = plt.subplots(figsize=(12, 7))
    x = np.arange(len(configs))
    width = 0.35

    for i, (rtype, regions) in enumerate(region_types.items()):
        means, errs, ns = [], [], []
        for cfg in configs:
            vals = [r['pct_change'] for r in h_clean
                    if r.get('config', '') == cfg and r['region'] in regions]
            if vals:
                means.append(np.mean(vals))
                errs.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                            if len(vals) > 1 else 0.1)
                ns.append(len(vals))
            else:
                means.append(0)
                errs.append(0)
                ns.append(0)
        offset = -width / 2 + i * width
        color = '#CC4444' if rtype == 'Arc' else '#4444CC'
        bars = ax.bar(x + offset, means, width, yerr=errs,
                      color=color, capsize=5,
                      edgecolor='black', linewidth=0.5, alpha=0.85,
                      label=rtype)
        for j, cfg in enumerate(configs):
            if cfg == 'Beta':
                bars[j].set_hatch('///')
        for j, (xi, n) in enumerate(zip(x + offset, ns)):
            if n > 0:
                ax.text(xi, means[j] + errs[j] + 0.02 if means[j] >= 0
                         else means[j] - errs[j] - 0.02,
                         'N=%d' % n, fontsize=7, ha='center',
                         va='bottom' if means[j] >= 0 else 'top')

    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(configs, fontsize=11)
    ax.set_ylabel('% Change from Baseline', fontsize=12)
    ax.set_title('H-Plate: Assembly Config × Location Type\n'
                 '(Both materials combined; hatched = Beta/unreliable)',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v5_C02_assembly_config_by_region.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  C02: Assembly config by region type")


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY D: Overall Summary
# ═══════════════════════════════════════════════════════════════════════════════

def plot_D01_executive_summary(y_results, gain_syst, intra_diffs):
    """Clean infographic for non-specialists."""
    y_clean = [r for r in y_results if not r['is_outlier']]

    nd_vals = [r['pct_change'] for r in y_clean
               if r['material'] in ['N42EH', 'N52SH']]
    sm_vals = [r['pct_change'] for r in y_clean
               if r['material'] in ['SmCo33H', 'SmCo35']]

    nd_mean = np.mean(nd_vals) if nd_vals else 0
    sm_mean = np.mean(sm_vals) if sm_vals else 0
    nd_sem = np.std(nd_vals, ddof=1) / np.sqrt(len(nd_vals)) if len(nd_vals) > 1 else 0
    sm_sem = np.std(sm_vals, ddof=1) / np.sqrt(len(sm_vals)) if len(sm_vals) > 1 else 0

    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    fig = plt.figure(figsize=(14, 10))

    # Title
    fig.text(0.5, 0.96, 'CEBAF Tunnel Magnet Radiation Exposure — Key Findings',
             fontsize=18, fontweight='bold', ha='center', va='top')
    fig.text(0.5, 0.92, 'Preliminary — ~6 months tunnel exposure (Jul 2025 – Jan 2026)',
             fontsize=12, ha='center', va='top', color='#666666', fontstyle='italic')

    # Large info boxes
    box_y = 0.68
    box_h = 0.18
    box_w = 0.26

    # NdFeB box (red)
    ax1 = fig.add_axes([0.06, box_y, box_w, box_h])
    ax1.set_xlim(0, 1); ax1.set_ylim(0, 1)
    ax1.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor='#FFDDDD',
                                 edgecolor='#CC4444', linewidth=3))
    ax1.text(0.5, 0.75, 'NdFeB Degradation', fontsize=13, fontweight='bold',
             ha='center', va='center', color='#CC4444')
    ax1.text(0.5, 0.40, '%.2f%%' % nd_mean, fontsize=28, fontweight='bold',
             ha='center', va='center', color='#CC4444')
    ax1.text(0.5, 0.12, '±%.2f%%(stat) ±%.2f%%(syst)' % (nd_sem, gain_syst),
             fontsize=9, ha='center', va='center', color='#888888')
    ax1.axis('off')

    # SmCo box (green)
    ax2 = fig.add_axes([0.37, box_y, box_w, box_h])
    ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
    ax2.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor='#DDFFDD',
                                 edgecolor='#44AA44', linewidth=3))
    ax2.text(0.5, 0.75, 'SmCo Stable', fontsize=13, fontweight='bold',
             ha='center', va='center', color='#44AA44')
    ax2.text(0.5, 0.40, '%.2f%%' % sm_mean, fontsize=28, fontweight='bold',
             ha='center', va='center', color='#44AA44')
    ax2.text(0.5, 0.12, '±%.2f%%(stat) ±%.2f%%(syst)' % (sm_sem, gain_syst),
             fontsize=9, ha='center', va='center', color='#888888')
    ax2.axis('off')

    # Differential box (gold highlight)
    ax3 = fig.add_axes([0.68, box_y, box_w, box_h])
    ax3.set_xlim(0, 1); ax3.set_ylim(0, 1)
    ax3.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor='#FFF8DD',
                                 edgecolor='#CC8800', linewidth=3))
    ax3.text(0.5, 0.80, 'NdFeB − SmCo', fontsize=11, fontweight='bold',
             ha='center', va='center', color='#CC8800')
    ax3.text(0.5, 0.65, '(gain-immune)', fontsize=9, ha='center', va='center',
             color='#AA7700')
    ax3.text(0.5, 0.38, '%.3f%%' % diff_mean, fontsize=26, fontweight='bold',
             ha='center', va='center', color='#CC8800')
    ax3.text(0.5, 0.15, '±%.3f%% (%.1f$\\sigma$)  N=%d plates' % (
        diff_sem, diff_sig, len(intra_diffs)),
             fontsize=9, ha='center', va='center', color='#888888')
    ax3.axis('off')

    # Simplified bar chart
    ax4 = fig.add_axes([0.10, 0.12, 0.40, 0.45])
    bars = ax4.bar([0, 1], [nd_mean, sm_mean],
                   yerr=[nd_sem, sm_sem],
                   color=['#CC4444', '#44AA44'], capsize=10,
                   edgecolor='black', linewidth=1, alpha=0.85, width=0.5,
                   error_kw=dict(linewidth=2.5, capthick=2.5))
    ax4.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax4.axhline(0, color='black', linewidth=1.5)
    ax4.set_xticks([0, 1])
    ax4.set_xticklabels(['NdFeB\n(N=%d)' % len(nd_vals),
                          'SmCo\n(N=%d)' % len(sm_vals)], fontsize=12)
    ax4.set_ylabel('% Change from Baseline', fontsize=11)
    ax4.set_title('Y-Plate Helmholtz (temp-corrected)', fontsize=11, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    ax4.text(0.5, gain_syst + 0.01, 'Gain syst. ±%.2f%%' % gain_syst,
             fontsize=8, color='gray', ha='center', va='bottom',
             transform=ax4.get_xaxis_transform())

    # Key findings text
    ax5 = fig.add_axes([0.58, 0.12, 0.38, 0.45])
    ax5.set_xlim(0, 1); ax5.set_ylim(0, 1)
    findings = [
        'KEY FINDINGS:',
        '',
        '1. NdFeB magnets show ~0.3% degradation',
        '   after ~6 months CEBAF tunnel exposure',
        '',
        '2. SmCo magnets are consistent with zero',
        '   degradation (within measurement precision)',
        '',
        '3. NdFeB-SmCo intra-plate differential',
        '   of %.3f%% is %.1f-sigma significant' % (abs(diff_mean), diff_sig),
        '   (gain-immune, no systematic uncertainty)',
        '',
        '4. Arc locations show ~2x more NdFeB',
        '   degradation than linac locations',
        '',
        '5. H-plates carry full ±%.2f%% gain' % gain_syst,
        '   systematic — insufficient precision',
        '   to confirm/deny Y-plate signal',
    ]
    for i, line in enumerate(findings):
        weight = 'bold' if i == 0 else 'normal'
        fontsize = 11 if i == 0 else 9
        ax5.text(0.05, 0.96 - i * 0.062, line, fontsize=fontsize,
                 fontweight=weight, va='top', fontfamily='monospace')
    ax5.axis('off')

    fig.savefig(os.path.join(PLOT_DIR, 'v5_D01_executive_summary.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  D01: Executive summary")


def plot_D02_publication_summary(y_results, h_results, gain_syst, intra_diffs,
                                  intra_details):
    """Publication-quality 2x2 multi-panel."""
    y_clean = [r for r in y_results if not r['is_outlier']]
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]

    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # (a) All 6 material bars
    ax = axes[0, 0]
    y_mats = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    h_mats_list = ['NdFeB', 'SmCo']
    all_labels, all_means, all_stat, all_colors = [], [], [], []

    for mat in y_mats:
        vals = [r['pct_change'] for r in y_clean if r['material'] == mat]
        if vals:
            all_labels.append('Y-%s\n(N=%d)' % (mat, len(vals)))
            all_means.append(np.mean(vals))
            all_stat.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                            if len(vals) > 1 else 0.05)
            all_colors.append(MAT_COLORS[mat])

    for mat in h_mats_list:
        vals = [r['pct_change'] for r in h_clean if r['material'] == mat]
        if vals:
            all_labels.append('H-%s\n(N=%d)' % (mat, len(vals)))
            all_means.append(np.mean(vals))
            all_stat.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                            if len(vals) > 1 else 0.1)
            all_colors.append(HMAT_COLORS[mat])

    bx = np.arange(len(all_labels))
    ax.bar(bx, all_means, yerr=all_stat, color=all_colors,
           capsize=5, edgecolor='black', linewidth=0.5, alpha=0.85, width=0.6,
           error_kw=dict(linewidth=1.5, capthick=1.5))
    # Syst error bars (outer)
    for i in range(len(all_means)):
        ax.plot([i, i], [all_means[i] - gain_syst, all_means[i] + gain_syst],
                color='gray', linewidth=3, alpha=0.3, zorder=0)
    ax.axhspan(-gain_syst, gain_syst, alpha=0.06, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(bx)
    ax.set_xticklabels(all_labels, fontsize=8)
    ax.set_ylabel('% Change', fontsize=10)
    ax.set_title('(a) All Materials — Y-plate + H-plate', fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    # Vertical divider
    ax.axvline(len(y_mats) - 0.5, color='gray', linewidth=1, linestyle=':')

    # (b) Gain-immune differential bar
    ax = axes[0, 1]
    ax.bar(0, diff_mean, yerr=diff_sem, color='#8B0000', capsize=8,
           edgecolor='black', linewidth=1, alpha=0.85, width=0.4,
           error_kw=dict(linewidth=2.5, capthick=2.5))
    ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax.set_xticks([0])
    ax.set_xticklabels(['NdFeB − SmCo\n(intra-plate differential)\nN=%d plates' %
                         len(intra_diffs)], fontsize=10)
    ax.set_ylabel('% Differential', fontsize=10)
    ax.set_title('(b) Gain-Immune Result: %.1f$\\sigma$' % diff_sig,
                 fontsize=11, fontweight='bold')
    ax.text(0, diff_mean - diff_sem - 0.02,
            '%+.3f%% ± %.3f%%' % (diff_mean, diff_sem),
            ha='center', va='top', fontsize=11, fontweight='bold', color='#8B0000')
    ax.text(0, 0.08, 'No Helmholtz gain\nsystematic uncertainty',
            ha='center', va='bottom', fontsize=9, color='#006600',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#E0FFE0',
                      edgecolor='#006600', alpha=0.8))
    ax.grid(axis='y', alpha=0.3)
    ax.set_xlim(-0.8, 0.8)

    # (c) Arc vs Linac gain-immune comparison
    ax = axes[1, 0]
    arc_diffs = [d['diff'] for d in intra_details if 'Arc' in d['region']]
    lin_diffs = [d['diff'] for d in intra_details if 'Linac' in d['region']]
    lab_diffs = [d['diff'] for d in intra_details if d['region'] == 'Labyrinth']

    gi_data = []
    for name, vals, col in [('Arcs', arc_diffs, '#CC4444'),
                             ('Linacs', lin_diffs, '#4444CC'),
                             ('Labyrinth', lab_diffs, '#888888')]:
        if vals:
            gi_data.append((name, np.mean(vals),
                            np.std(vals) / np.sqrt(len(vals)) if len(vals) > 1 else 0.05,
                            len(vals), col))

    if gi_data:
        bx = np.arange(len(gi_data))
        ax.bar(bx, [d[1] for d in gi_data], yerr=[d[2] for d in gi_data],
               color=[d[4] for d in gi_data], capsize=6,
               edgecolor='black', linewidth=0.5, alpha=0.85, width=0.5,
               error_kw=dict(linewidth=1.5, capthick=1.5))
        ax.set_xticks(bx)
        ax.set_xticklabels(['%s\n(N=%d plates)' % (d[0], d[3]) for d in gi_data],
                           fontsize=9)
    ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax.set_ylabel('NdFeB − SmCo (%)', fontsize=10)
    ax.set_title('(c) Gain-Immune Differential by Region', fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # (d) Results table
    ax = axes[1, 1]
    ax.axis('off')

    table_data = []
    for mat in y_mats:
        vals = [r['pct_change'] for r in y_clean if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.05
            sig = abs(m / s) if s > 0 else 0
            sig_str = '%.1f$\\sigma$' % sig if sig >= 2 else 'n.s.'
            table_data.append(['Y-%s' % mat, '%+.3f' % m, '%.3f' % s,
                               '%.2f' % gain_syst, sig_str, str(len(vals))])

    for mat in h_mats_list:
        vals = [r['pct_change'] for r in h_clean if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.1
            sig = abs(m / s) if s > 0 else 0
            sig_str = '%.1f$\\sigma$' % sig if sig >= 2 else 'n.s.'
            table_data.append(['H-%s' % mat, '%+.3f' % m, '%.3f' % s,
                               '%.2f' % gain_syst, sig_str, str(len(vals))])

    # Differential row
    table_data.append(['NdFeB-SmCo', '%+.3f' % diff_mean, '%.3f' % diff_sem,
                       'N/A', '%.1f$\\sigma$' % diff_sig,
                       '%d plates' % len(intra_diffs)])

    col_labels = ['Source', 'Mean %', 'Stat Unc', 'Syst Unc', 'Signif.', 'N']
    table = ax.table(cellText=table_data, colLabels=col_labels,
                     loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)

    # Color header
    for j in range(len(col_labels)):
        table[(0, j)].set_facecolor('#DDDDDD')
        table[(0, j)].set_text_props(fontweight='bold')
    # Highlight last row (differential)
    for j in range(len(col_labels)):
        table[(len(table_data), j)].set_facecolor('#FFF8DD')
        table[(len(table_data), j)].set_text_props(fontweight='bold')

    ax.set_title('(d) Summary Table', fontsize=11, fontweight='bold', pad=20)

    fig.suptitle('Magnet Degradation Summary — CEBAF Tunnel (Jul 2025 – Jan 2026)\n'
                 'Temperature-corrected Helmholtz data; outliers excluded',
                 fontsize=14, fontweight='bold', y=1.01)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(PLOT_DIR, 'v5_D02_publication_summary.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  D02: Publication summary (2x2)")


def plot_D03_results_table(y_results, h_results, gain_syst, intra_diffs):
    """Comprehensive results table rendered as figure."""
    y_clean = [r for r in y_results if not r['is_outlier']]
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]

    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('off')

    table_data = []
    row_colors = []

    y_mats = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    mat_row_colors = {
        'N42EH': '#FFE0E0', 'N52SH': '#E0E0FF',
        'SmCo33H': '#E0FFE0', 'SmCo35': '#FFF8E0',
    }

    for mat in y_mats:
        vals = [r['pct_change'] for r in y_clean if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.05
            sig = abs(m / s) if s > 0 else 0
            sig_str = '%.1f' % sig if sig >= 2 else 'n.s.'
            notes = 'NdFeB' if mat in ['N42EH', 'N52SH'] else 'SmCo'
            table_data.append(['Y-plate %s' % mat, '%+.3f%%' % m,
                               '%.3f%%' % s, '±%.2f%%' % gain_syst,
                               sig_str, str(len(vals)), notes])
            row_colors.append(mat_row_colors[mat])

    for mat in ['NdFeB', 'SmCo']:
        vals = [r['pct_change'] for r in h_clean if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.1
            sig = abs(m / s) if s > 0 else 0
            sig_str = '%.1f' % sig if sig >= 2 else 'n.s.'
            table_data.append(['H-plate %s' % mat, '%+.3f%%' % m,
                               '%.3f%%' % s, '±%.2f%%' % gain_syst,
                               sig_str, str(len(vals)),
                               'Full gain syst.'])
            row_colors.append('#F0F0F0')

    # Headline: differential
    table_data.append(['NdFeB−SmCo (gain-immune)', '%+.3f%%' % diff_mean,
                       '%.3f%%' % diff_sem, 'None',
                       '%.1f' % diff_sig, '%d plates' % len(intra_diffs),
                       'HEADLINE RESULT'])
    row_colors.append('#FFF0CC')

    col_labels = ['Measurement', 'Mean Change', 'Stat Unc.', 'Syst Unc.',
                  'Significance (σ)', 'N', 'Notes']
    table = ax.table(cellText=table_data, colLabels=col_labels,
                     loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.0)

    # Style header
    for j in range(len(col_labels)):
        table[(0, j)].set_facecolor('#333333')
        table[(0, j)].set_text_props(color='white', fontweight='bold')

    # Style data rows
    for i, color in enumerate(row_colors):
        for j in range(len(col_labels)):
            table[(i + 1, j)].set_facecolor(color)
    # Bold headline row
    last = len(table_data)
    for j in range(len(col_labels)):
        table[(last, j)].set_text_props(fontweight='bold')

    ax.set_title('Comprehensive Results Table — Magnet Degradation\n'
                 'CEBAF Tunnel Exposure: Jul 2025 – Jan 2026 (Preliminary)',
                 fontsize=14, fontweight='bold', pad=20)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v5_D03_results_table.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  D03: Results table")


def plot_D04_dashboard(y_results, h_results, gain_syst, intra_diffs, intra_details):
    """3x2 comprehensive dashboard."""
    y_clean = [r for r in y_results if not r['is_outlier']]
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]

    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    fig, axes = plt.subplots(3, 2, figsize=(18, 18))

    # (a) Y-plate material bars + gain band
    ax = axes[0, 0]
    y_mats = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    means, sems, colors = [], [], []
    for mat in y_mats:
        vals = [r['pct_change'] for r in y_clean if r['material'] == mat]
        if vals:
            means.append(np.mean(vals))
            sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                        if len(vals) > 1 else 0.05)
            colors.append(MAT_COLORS[mat])
        else:
            means.append(0); sems.append(0); colors.append('#888')
    ax.bar(range(len(y_mats)), means, yerr=sems, color=colors,
           capsize=5, edgecolor='black', linewidth=0.5, alpha=0.85, width=0.6)
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(range(len(y_mats)))
    ax.set_xticklabels(y_mats, fontsize=9)
    ax.set_ylabel('% Change', fontsize=10)
    ax.set_title('(a) Y-Plate by Material', fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # (b) H-plate material + config bars
    ax = axes[0, 1]
    configs = ['Alpha', 'Beta', 'Gamma', 'Delta']
    x = np.arange(len(configs))
    width = 0.35
    for i, mat in enumerate(['NdFeB', 'SmCo']):
        cfg_means, cfg_errs = [], []
        for cfg in configs:
            vals = [r['pct_change'] for r in h_clean
                    if r['material'] == mat and r.get('config', '') == cfg]
            if vals:
                cfg_means.append(np.mean(vals))
                cfg_errs.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                                if len(vals) > 1 else 0.1)
            else:
                cfg_means.append(0); cfg_errs.append(0)
        offset = -width / 2 + i * width
        bars = ax.bar(x + offset, cfg_means, width, yerr=cfg_errs,
                      color=HMAT_COLORS[mat], capsize=4,
                      edgecolor='black', linewidth=0.5, alpha=0.85, label=mat)
        for j, cfg in enumerate(configs):
            if cfg == 'Beta':
                bars[j].set_hatch('///')
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(configs, fontsize=9)
    ax.set_ylabel('% Change', fontsize=10)
    ax.set_title('(b) H-Plate by Config', fontsize=11, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)

    # (c) Gain-immune differential
    ax = axes[1, 0]
    ax.bar(0, diff_mean, yerr=diff_sem, color='#8B0000', capsize=8,
           edgecolor='black', linewidth=1, alpha=0.85, width=0.4,
           error_kw=dict(linewidth=2.5, capthick=2.5))
    ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax.set_xticks([0])
    ax.set_xticklabels(['NdFeB − SmCo\nN=%d plates' % len(intra_diffs)], fontsize=10)
    ax.set_ylabel('% Differential', fontsize=10)
    ax.set_title('(c) Gain-Immune: %+.3f%% (%.1f$\\sigma$)' % (diff_mean, diff_sig),
                 fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.set_xlim(-0.8, 0.8)

    # (d) Pass-number trend (compact — arcs only, Y-plate)
    ax = axes[1, 1]
    y_arc = [r for r in y_clean if r.get('line', 0) > 0]
    lines_list = [1, 2, 3, 4, 5]
    offset_val = 0.1
    for mat_group, mat_filter, color, label in [
            ('NdFeB', ['N42EH', 'N52SH'], '#CC4444', 'NdFeB'),
            ('SmCo', ['SmCo33H', 'SmCo35'], '#44AA44', 'SmCo')]:
        lm, le = [], []
        for line in lines_list:
            vals = [r['pct_change'] for r in y_arc
                    if r['material'] in mat_filter and r['line'] == line]
            lm.append(np.mean(vals) if vals else np.nan)
            le.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                      if len(vals) > 1 else (0.05 if vals else 0))
        off = -offset_val / 2 if mat_group == 'NdFeB' else offset_val / 2
        ax.errorbar(np.array(lines_list) + off, lm, yerr=le,
                    color=color, marker='o', markersize=7, linewidth=2,
                    capsize=4, label=label)
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_xticks(lines_list)
    ax.set_xticklabels(['L%d' % l for l in lines_list], fontsize=9)
    ax.set_xlabel('Arc Line', fontsize=10)
    ax.set_ylabel('% Change', fontsize=10)
    ax.set_title('(d) Degradation vs Arc Line Position', fontsize=11, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # (e) Time series (Y-plate 4 materials)
    ax = axes[2, 0]
    for mat in y_mats:
        date_vals = defaultdict(list)
        for r in y_clean:
            if r['material'] != mat:
                continue
            for dt, pct in r.get('date_pcts', []):
                date_vals[dt.strftime('%Y-%m-%d')].append(pct)
        if not date_vals:
            continue
        dates = sorted(d for d in date_vals if len(date_vals[d]) >= 5)
        if not dates:
            continue
        dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        m_vals = [np.mean(date_vals[d]) for d in dates]
        ax.plot(dt_objs, m_vals, 'o-', color=MAT_COLORS[mat],
                markersize=5, linewidth=1.5, label=MAT_LABELS[mat])
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1, linestyle=':')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.set_ylabel('% Change', fontsize=10)
    ax.set_title('(e) Y-Plate Helmholtz Time Series', fontsize=11, fontweight='bold')
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)

    # (f) Key numbers table
    ax = axes[2, 1]
    ax.axis('off')
    nd_all = [r['pct_change'] for r in y_clean
              if r['material'] in ['N42EH', 'N52SH']]
    sm_all = [r['pct_change'] for r in y_clean
              if r['material'] in ['SmCo33H', 'SmCo35']]
    h_nd = [r['pct_change'] for r in h_clean if r['material'] == 'NdFeB']
    h_sm = [r['pct_change'] for r in h_clean if r['material'] == 'SmCo']

    rows = [
        ['Y NdFeB (combined)', '%+.3f%%' % np.mean(nd_all),
         '%.3f%%' % (np.std(nd_all, ddof=1) / np.sqrt(len(nd_all))),
         str(len(nd_all))],
        ['Y SmCo (combined)', '%+.3f%%' % np.mean(sm_all),
         '%.3f%%' % (np.std(sm_all, ddof=1) / np.sqrt(len(sm_all))),
         str(len(sm_all))],
    ]
    if h_nd:
        rows.append(['H NdFeB', '%+.3f%%' % np.mean(h_nd),
                     '%.3f%%' % (np.std(h_nd, ddof=1) / np.sqrt(len(h_nd))
                                 if len(h_nd) > 1 else 0.1),
                     str(len(h_nd))])
    if h_sm:
        rows.append(['H SmCo', '%+.3f%%' % np.mean(h_sm),
                     '%.3f%%' % (np.std(h_sm, ddof=1) / np.sqrt(len(h_sm))
                                 if len(h_sm) > 1 else 0.1),
                     str(len(h_sm))])
    rows.append(['NdFeB-SmCo (gain-immune)', '%+.3f%%' % diff_mean,
                 '%.3f%%' % diff_sem, '%d plates' % len(intra_diffs)])
    rows.append(['Gain systematic', '±%.3f%%' % gain_syst, '', ''])

    table = ax.table(cellText=rows,
                     colLabels=['Quantity', 'Value', 'Stat Unc', 'N'],
                     loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)
    for j in range(4):
        table[(0, j)].set_facecolor('#DDDDDD')
        table[(0, j)].set_text_props(fontweight='bold')
    # Highlight differential row
    diff_row = len(rows) - 1  # gain syst is last, diff is second to last
    for j in range(4):
        table[(diff_row, j)].set_facecolor('#FFF0CC')
        table[(diff_row, j)].set_text_props(fontweight='bold')
    ax.set_title('(f) Key Numbers', fontsize=11, fontweight='bold', pad=20)

    fig.suptitle('Comprehensive Dashboard — Magnet Degradation Study\n'
                 'CEBAF Tunnel Jul 2025 – Jan 2026 (Preliminary)',
                 fontsize=15, fontweight='bold', y=1.01)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(PLOT_DIR, 'v5_D04_dashboard.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  D04: Comprehensive dashboard (3x2)")


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY E: Time Series
# ═══════════════════════════════════════════════════════════════════════════════

def plot_E01_timeseries_Y(y_results, gain_syst):
    """Enhanced Y-plate Helmholtz time series with SEM bands."""
    clean = [r for r in y_results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)

    for mat in materials:
        date_vals = defaultdict(list)
        for r in clean:
            if r['material'] != mat:
                continue
            for dt, pct in r.get('date_pcts', []):
                date_vals[dt.strftime('%Y-%m-%d')].append(pct)
        if not date_vals:
            continue
        dates = sorted(d for d in date_vals if len(date_vals[d]) >= 5)
        if not dates:
            continue
        dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        means_list = [np.mean(date_vals[d]) for d in dates]
        sems = [np.std(date_vals[d], ddof=1) / np.sqrt(len(date_vals[d]))
                if len(date_vals[d]) > 1 else 0.05 for d in dates]

        ax.errorbar(dt_objs, means_list, yerr=sems,
                    color=MAT_COLORS[mat], marker='o', markersize=7,
                    linewidth=2.5, capsize=5, capthick=2,
                    label=MAT_LABELS[mat])
        # SEM band
        ax.fill_between(dt_objs,
                         [m - s for m, s in zip(means_list, sems)],
                         [m + s for m, s in zip(means_list, sems)],
                         color=MAT_COLORS[mat], alpha=0.1)

    ax.axhline(0, color='black', linewidth=1, linestyle='--')

    # Beam OFF marker
    ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1.5,
               linestyle=':', alpha=0.7)
    ylims = ax.get_ylim()
    ax.text(datetime(2025, 10, 24), ylims[1] * 0.85,
            'Beam OFF\n(Oct 21)', fontsize=9, color='gray', ha='left', va='top')

    # Oct 21 thermal lag note
    ax.axvspan(datetime(2025, 10, 18), datetime(2025, 11, 1),
               alpha=0.06, color='orange')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(datetime(2025, 6, 15), datetime(2026, 2, 1))
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('% Change from Pre-Deployment Baseline', fontsize=12)
    ax.set_title('Y-Plate Helmholtz Time Series\n'
                 '(Temperature-corrected; gray band = gain syst. ±%.2f%%; '
                 'error bars = SEM)' % gain_syst,
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='lower left')
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v5_E01_timeseries_Y.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  E01: Y-plate time series")


def plot_E02_timeseries_combined(y_results, h_ts_results, gain_syst):
    """Combined Y + H overlay time series."""
    y_clean = [r for r in y_results if not r['is_outlier']]
    h_clean = [r for r in h_ts_results if not r.get('is_outlier', False)]

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)

    # Y-plate: solid lines
    y_nd_dates = defaultdict(list)
    y_sm_dates = defaultdict(list)
    for r in y_clean:
        for dt, pct in r.get('date_pcts', []):
            d_str = dt.strftime('%Y-%m-%d')
            if r['material'] in ['N42EH', 'N52SH']:
                y_nd_dates[d_str].append(pct)
            else:
                y_sm_dates[d_str].append(pct)

    for label, date_vals, color, ls in [
            ('Y NdFeB', y_nd_dates, '#CC4444', '-'),
            ('Y SmCo', y_sm_dates, '#44AA44', '-')]:
        dates = sorted(d for d in date_vals if len(date_vals[d]) >= 5)
        if not dates:
            continue
        dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        means_list = [np.mean(date_vals[d]) for d in dates]
        sems = [np.std(date_vals[d], ddof=1) / np.sqrt(len(date_vals[d]))
                if len(date_vals[d]) > 1 else 0.05 for d in dates]
        ax.errorbar(dt_objs, means_list, yerr=sems,
                    color=color, marker='o', markersize=7,
                    linewidth=2.5, capsize=4, linestyle=ls,
                    label=label)

    # H-plate: dashed lines
    h_nd_dates = defaultdict(list)
    h_sm_dates = defaultdict(list)
    for r in h_clean:
        for dt, pct in r.get('date_pcts', []):
            d_str = dt.strftime('%Y-%m-%d')
            if r['material'] == 'NdFeB':
                h_nd_dates[d_str].append(pct)
            else:
                h_sm_dates[d_str].append(pct)

    for label, date_vals, color, ls in [
            ('H NdFeB', h_nd_dates, '#EE8888', '--'),
            ('H SmCo', h_sm_dates, '#88CC88', '--')]:
        dates = sorted(d for d in date_vals if len(date_vals[d]) >= 3)
        if not dates:
            continue
        dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        means_list = [np.mean(date_vals[d]) for d in dates]
        sems = [np.std(date_vals[d], ddof=1) / np.sqrt(len(date_vals[d]))
                if len(date_vals[d]) > 1 else 0.1 for d in dates]
        ax.errorbar(dt_objs, means_list, yerr=sems,
                    color=color, marker='s', markersize=6,
                    linewidth=2, capsize=4, linestyle=ls,
                    label=label, alpha=0.8)

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1.5,
               linestyle=':', alpha=0.7)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(datetime(2025, 6, 15), datetime(2026, 2, 1))
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('% Change from Pre-Deployment Baseline', fontsize=12)
    ax.set_title('Combined Y-Plate + H-Plate Helmholtz Time Series\n'
                 '(Solid = Y-plate, dashed = H-plate; gray = gain syst. ±%.2f%%)' %
                 gain_syst, fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='lower left')
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v5_E02_timeseries_combined.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  E02: Combined time series (Y + H)")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("Manager Summary v5: Comprehensive Combined Y + H Analysis")
    print("=" * 70)
    print()

    # ─── Load Y-plate data (from v3) ─────────────────────────────────
    print("Loading Y-plate Helmholtz data (v3 loader)...")
    y_results_v3, helm_raw, temp_final, y_materials = load_all()
    y_clean = [r for r in y_results_v3 if not r['is_outlier']]
    print("  %d Y-plate Helmholtz samples (%d outliers excluded)" %
          (len(y_clean), len(y_results_v3) - len(y_clean)))

    # Enrich with line numbers from PLACEMENTS_WITH_LINE
    for r in y_results_v3:
        info = PLACEMENTS_WITH_LINE.get(r['plate'])
        if info and ('line' not in r or r.get('line', 0) == 0):
            r['line'] = info['line']
            r['h_plate'] = info['h_plate']
            r['sub_location'] = info['sub_location']
        elif info:
            # Still enrich even if line exists
            if 'h_plate' not in r:
                r['h_plate'] = info['h_plate']
            if 'sub_location' not in r:
                r['sub_location'] = info['sub_location']

    # ─── Load H-plate data (from v2) ─────────────────────────────────
    print("Loading H-plate data (v2 loader)...")
    y_mats_xl, pair_arrangements = load_materials()
    temp_lookup = build_temperature_lookup()

    h_results, h_excluded = compute_h_plate_degradation(pair_arrangements, temp_lookup)
    h_outliers = sum(1 for r in h_results if r.get('is_outlier', False))
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]
    print("  %d H-plate pairs (%d outliers excluded, %d excluded for other reasons)" %
          (len(h_clean), h_outliers, len(h_excluded)))

    # Build H-plate time series
    print("Building H-plate time series...")
    h_ts_results = build_h_plate_timeseries(pair_arrangements, temp_lookup)
    h_ts_clean = [r for r in h_ts_results if not r.get('is_outlier', False)]
    print("  %d H-plate pairs with time series (%d outliers excluded)" %
          (len(h_ts_clean), len(h_ts_results) - len(h_ts_clean)))

    # ─── Gain systematic ─────────────────────────────────────────────
    gain_result = get_gain_syst(helm_raw)
    gain_syst, session_offsets = gain_result
    print("\nGain systematic (cleaned): ±%.4f%%" % gain_syst)
    gain_syst_raw = getattr(gain_result, 'gain_syst_raw', None)
    if gain_syst_raw is not None:
        print("Gain systematic (uncleaned): ±%.4f%%" % gain_syst_raw)

    # ─── Intra-plate differential ─────────────────────────────────────
    intra_diffs, intra_details = compute_intra_plate_diffs(y_clean)
    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    # ═════════════════════════════════════════════════════════════════
    # VERIFICATION — Print all key numbers BEFORE any plotting
    # ═════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("VERIFICATION — Key Numbers")
    print("=" * 70)

    print("\n--- Y-Plate Helmholtz ---")
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        vals = [r['pct_change'] for r in y_clean if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals))
            print("  %s: %+.3f%% ± %.3f%% (%.1fσ stat, N=%d)" %
                  (mat, m, s, abs(m / s) if s > 0 else 0, len(vals)))

    print("\n--- Gain-Immune Intra-Plate Differential ---")
    print("  NdFeB − SmCo: %+.3f%% ± %.3f%% (%.1fσ, N=%d plates)" %
          (diff_mean, diff_sem, diff_sig, len(intra_diffs)))

    print("\n--- H-Plate Helmholtz ---")
    for mat in ['NdFeB', 'SmCo']:
        vals = [r['pct_change'] for r in h_clean if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.1
            sig = abs(m / s) if s > 0 else 0
            print("  %s: %+.3f%% ± %.3f%% (%.1fσ, N=%d)" %
                  (mat, m, s, sig, len(vals)))

    print("\n--- H-Plate by Assembly Config ---")
    for cfg in ['Alpha', 'Beta', 'Gamma', 'Delta']:
        vals = [r['pct_change'] for r in h_clean if r.get('config', '') == cfg]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.1
            note = ' (UNRELIABLE)' if cfg == 'Beta' else ''
            print("  %s: %+.3f%% ± %.3f%% (N=%d)%s" %
                  (cfg, m, s, len(vals), note))

    print("\n--- H-Plate by Config × Material ---")
    for mat in ['NdFeB', 'SmCo']:
        for cfg in ['Alpha', 'Beta', 'Gamma', 'Delta']:
            vals = [r['pct_change'] for r in h_clean
                    if r['material'] == mat and r.get('config', '') == cfg]
            if vals:
                m = np.mean(vals)
                s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.1
                print("  %s/%s: %+.3f%% ± %.3f%% (N=%d)" %
                      (mat, cfg, m, s, len(vals)))

    print("\n--- Pass Number (Y-plate NdFeB, arcs only) ---")
    for line in [1, 2, 3, 4, 5]:
        vals = [r['pct_change'] for r in y_clean
                if r['material'] in ['N42EH', 'N52SH'] and r.get('line', 0) == line]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.05
            print("  Line %d: %+.3f%% ± %.3f%% (N=%d)" %
                  (line, m, s, len(vals)))
    # Line 5 vs Line 1
    l1 = [r['pct_change'] for r in y_clean
          if r['material'] in ['N42EH', 'N52SH'] and r.get('line', 0) == 1]
    l5 = [r['pct_change'] for r in y_clean
          if r['material'] in ['N42EH', 'N52SH'] and r.get('line', 0) == 5]
    if l1 and l5:
        print("  Line 5 − Line 1 differential: %+.3f%%" %
              (np.mean(l5) - np.mean(l1)))

    print("\n--- H-Plate Outlier Count ---")
    print("  Total H results: %d" % len(h_results))
    print("  Outliers: %d" % h_outliers)
    print("  Clean: %d" % len(h_clean))

    print("\n--- Gain Systematic ---")
    print("  ±%.4f%%" % gain_syst)

    # ═════════════════════════════════════════════════════════════════
    # GENERATE PLOTS
    # ═════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("Generating v5 plots...")
    print("=" * 70)

    print("\nCategory A: Waterfall plots")
    plot_A01_waterfall_by_region_Y(y_results_v3, gain_syst)
    plot_A02_waterfall_by_region_H(h_results, gain_syst)
    plot_A03_waterfall_combined(y_results_v3, h_results, gain_syst)

    print("\nCategory B: Regional & Pass Number")
    plot_B01_regional_bars_Y(y_results_v3, gain_syst)
    plot_B02_pass_number_trend(y_results_v3, h_results, gain_syst)
    plot_B03_arc_panels(y_results_v3, h_results, gain_syst)
    plot_B04_region_heatmap(y_results_v3, h_results)

    print("\nCategory C: Assembly Configuration")
    plot_C01_assembly_config_bars(h_results, gain_syst)
    plot_C02_assembly_config_by_region(h_results, gain_syst)

    print("\nCategory D: Overall Summary")
    plot_D01_executive_summary(y_results_v3, gain_syst, intra_diffs)
    plot_D02_publication_summary(y_results_v3, h_results, gain_syst,
                                  intra_diffs, intra_details)
    plot_D03_results_table(y_results_v3, h_results, gain_syst, intra_diffs)
    plot_D04_dashboard(y_results_v3, h_results, gain_syst, intra_diffs, intra_details)

    print("\nCategory E: Time Series")
    plot_E01_timeseries_Y(y_results_v3, gain_syst)
    plot_E02_timeseries_combined(y_results_v3, h_ts_results, gain_syst)

    print("\n" + "=" * 70)
    print("All v5 plots saved to: %s/v5_*.png" % PLOT_DIR)
    print("=" * 70)


if __name__ == '__main__':
    main()
