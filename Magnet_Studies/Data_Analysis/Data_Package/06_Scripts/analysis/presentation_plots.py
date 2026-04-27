#!/usr/bin/env python3
"""
presentation_plots.py — Clean, presentation-ready plot set for preliminary results.

Generates 7 figures into Presentation_Plots/ telling the narrative:
  P1: Material comparison (the signal)
  P2: Time series — dual with/without Jul 17
  P3: Regional breakdown (arc vs linac)
  P4: Lab control validation
  P5: Uncertainty budget table
  P6: ΔT_crit predicted vs observed ranking
  P7: Teslameter honest summary
"""

import sys, os
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
    MAT_COLORS, FLAGGED, T_REF, ALPHA, PLACEMENTS,
    REGION_ORDER, REGION_COLORS,
)
from degradation_summary_v2 import (
    load_materials, build_temperature_lookup,
    compute_h_plate_degradation,
)
from manager_summary_v5_polish import load_a_sample_helmholtz

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PLOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'Presentation_Plots')
os.makedirs(PLOT_DIR, exist_ok=True)

# Presentation colors
PRES_COLORS = {
    'N42EH': '#CC3333', 'N52SH': '#FF6644',
    'SmCo33H': '#3366CC', 'SmCo35': '#66AADD',
}
PRES_LABELS = {
    'N42EH': 'N42EH\n(NdFeB)', 'N52SH': 'N52SH\n(NdFeB)',
    'SmCo33H': 'SmCo33H\n(Sm₂Co₁₇)', 'SmCo35': 'SmCo35\n(Sm₂Co₁₇)',
}


def save(fig, name):
    path = os.path.join(PLOT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("  Saved: %s" % path)


# ═══════════════════════════════════════════════════════════════════════════════
# P1: Material Comparison — The Signal
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P1_material_comparison(results, gain_syst, intra_diffs,
                                gain_syst_raw=None):
    """4 material bars + gain band + differential inset."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig, (ax_main, ax_diff) = plt.subplots(1, 2, figsize=(14, 6),
                                            gridspec_kw={'width_ratios': [3, 1.2]})

    # Main: 4 bars
    means, sems, ns = [], [], []
    for mat in materials:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        means.append(np.mean(vals))
        sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals)))
        ns.append(len(vals))

    bars = ax_main.bar(range(4), means,
                       color=[PRES_COLORS[m] for m in materials],
                       edgecolor='black', linewidth=0.8, width=0.65,
                       yerr=sems, capsize=6, error_kw={'linewidth': 1.5})

    # Gain systematic band
    ax_main.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.15, zorder=0)
    if gain_syst_raw is not None:
        gain_label = '\u00b1%.2f%% gain syst. (\u00b1%.2f%% uncleaned)' % (gain_syst, gain_syst_raw)
    else:
        gain_label = '\u00b1%.2f%% gain systematic' % gain_syst
    ax_main.axhline(gain_syst, color='goldenrod', linewidth=1, linestyle='--',
                     alpha=0.5, label=gain_label)
    ax_main.axhline(-gain_syst, color='goldenrod', linewidth=1, linestyle='--',
                     alpha=0.5)

    ax_main.axhline(0, color='black', linewidth=0.8)
    ax_main.set_xticks(range(4))
    ax_main.set_xticklabels([PRES_LABELS[m] for m in materials], fontsize=10)
    ax_main.set_ylabel('Flux Change (%)', fontsize=12)
    ax_main.set_title('Helmholtz Flux Change by Material Grade\n'
                       '(baseline → latest, normalized to 20°C reference)',
                       fontsize=13, fontweight='bold')

    # N labels
    for i, (m, s, n) in enumerate(zip(means, sems, ns)):
        ax_main.annotate('%+.3f%% ± %.3f%%\n(N=%d)' % (m, s, n),
                         (i, m), textcoords='offset points',
                         xytext=(0, -28 if m < 0 else 18), ha='center',
                         fontsize=8, fontweight='bold')

    ax_main.legend(fontsize=9, loc='lower left')
    ax_main.set_ylim(-0.55, 0.35)
    ax_main.grid(axis='y', alpha=0.3)

    # Inset: differential
    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs, ddof=1) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem)

    ax_diff.bar([0], [diff_mean], color='#8B0000', edgecolor='black',
                linewidth=0.8, width=0.5, yerr=[diff_sem], capsize=8,
                error_kw={'linewidth': 2})
    ax_diff.axhline(0, color='black', linewidth=0.8)
    ax_diff.set_xticks([0])
    ax_diff.set_xticklabels(['NdFeB − SmCo\n(gain-immune)'], fontsize=10)
    ax_diff.set_ylabel('Differential (%)', fontsize=12)
    ax_diff.set_title('Intra-Plate Differential\n(N=%d plates)' % len(intra_diffs),
                       fontsize=12, fontweight='bold')
    ax_diff.annotate('%+.3f%% ± %.3f%%\n%.1fσ' % (diff_mean, diff_sem, diff_sig),
                     (0, diff_mean), textcoords='offset points',
                     xytext=(0, -32), ha='center', fontsize=10,
                     fontweight='bold', color='#8B0000')

    # Note: no gain systematic on differential
    ax_diff.annotate('No gain systematic\n(cancels intra-plate)',
                     xy=(0.5, 0.02), xycoords='axes fraction',
                     fontsize=8, fontstyle='italic', ha='center',
                     color='green')
    ax_diff.set_ylim(-0.4, 0.1)
    ax_diff.grid(axis='y', alpha=0.3)

    fig.text(0.5, -0.02, 'PRELIMINARY — LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    fig.text(0.99, -0.02, 'Error bars: ±1 SEM',
             ha='right', fontsize=8, fontstyle='italic', color='gray')

    plt.tight_layout()
    save(fig, 'P1_material_comparison.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P2: Time Series — Dual with/without Jul 17
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P2_timeseries_dual(results, gain_syst):
    """Three panels: (a) all data, (b) clean Aug 27+, (c) NdFeB-SmCo differential."""
    clean = [r for r in results if not r['is_outlier']]

    # Group date_pcts by material
    mat_series = defaultdict(lambda: defaultdict(list))
    for r in clean:
        for dt, pct in r['date_pcts']:
            mat_series[r['material']][dt].append(pct)

    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig = plt.figure(figsize=(18, 10))
    ax_all = fig.add_subplot(2, 2, 1)
    ax_clean = fig.add_subplot(2, 2, 2, sharey=ax_all)
    ax_diff = fig.add_subplot(2, 1, 2)

    # --- Panels (a) and (b): per-material time series ---
    for ax, title, filter_jul17 in [
        (ax_all, '(a) All Data (Jul 17 artifact flagged)', False),
        (ax_clean, '(b) Clean: Aug 27 onward (all 30 plates)', True),
    ]:
        for mat in materials:
            dts_plot, means_plot, sems_plot = [], [], []
            for dt in sorted(mat_series[mat]):
                if filter_jul17 and dt < datetime(2025, 8, 1):
                    continue
                vals = mat_series[mat][dt]
                dts_plot.append(dt)
                means_plot.append(np.mean(vals))
                sems_plot.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                                 if len(vals) > 1 else 0.1)

            ax.errorbar(dts_plot, means_plot, yerr=sems_plot,
                        color=PRES_COLORS[mat], marker='o', markersize=4,
                        linewidth=1.5, capsize=3, label=mat, alpha=0.85)

        ax.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.1, zorder=0)
        ax.axhline(0, color='black', linewidth=0.8)
        ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1.5,
                    linestyle=':', alpha=0.7)
        ax.annotate('Beam OFF', (datetime(2025, 10, 21),
                     ax.get_ylim()[1] if ax.get_ylim()[1] != 1 else 0.3),
                     textcoords='offset points', xytext=(5, -10),
                     fontsize=8, color='gray', fontstyle='italic')

        if not filter_jul17:
            ax.axvspan(datetime(2025, 7, 10), datetime(2025, 8, 1),
                       color='red', alpha=0.05, zorder=0)
            ax.annotate('Jul 17 artifact\n(~0.8% offset)',
                        (datetime(2025, 7, 17), 0),
                        textcoords='offset points', xytext=(5, 30),
                        fontsize=7, color='red', fontstyle='italic',
                        arrowprops=dict(arrowstyle='->', color='red', lw=0.8))

        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_ylabel('Flux Change from Baseline (%)', fontsize=10)
        ax.set_xlabel('Date', fontsize=10)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7, loc='lower left')

    # --- Panel (c): NdFeB-SmCo differential time evolution ---
    # Compute per-plate intra-plate differential at each date
    # Group results by plate
    plate_results = defaultdict(list)
    for r in clean:
        plate_results[r['plate']].append(r)

    # For each date, compute NdFeB mean - SmCo mean per plate, then average
    diff_dates_dict = defaultdict(list)
    for plate_id, recs in plate_results.items():
        # Get all measurement dates for this plate
        date_by_mat = defaultdict(dict)
        for r in recs:
            for dt, pct in r['date_pcts']:
                date_by_mat[dt][r['material']] = pct

        for dt, mat_vals in date_by_mat.items():
            ndfeb_vals = [v for m, v in mat_vals.items() if m in ('N42EH', 'N52SH')]
            smco_vals = [v for m, v in mat_vals.items() if m in ('SmCo33H', 'SmCo35')]
            if ndfeb_vals and smco_vals:
                diff_dates_dict[dt].append(np.mean(ndfeb_vals) - np.mean(smco_vals))

    diff_dates = sorted(diff_dates_dict.keys())
    diff_means = [np.mean(diff_dates_dict[dt]) for dt in diff_dates]
    diff_sems = [np.std(diff_dates_dict[dt], ddof=1) / np.sqrt(len(diff_dates_dict[dt]))
                 if len(diff_dates_dict[dt]) > 1 else 0.05
                 for dt in diff_dates]
    diff_ns = [len(diff_dates_dict[dt]) for dt in diff_dates]

    ax_diff.errorbar(diff_dates, diff_means, yerr=diff_sems,
                     color='#8B0000', marker='D', markersize=6,
                     linewidth=2.5, capsize=4, label='NdFeB \u2212 SmCo differential',
                     zorder=5)
    ax_diff.fill_between(diff_dates,
                          [m - e for m, e in zip(diff_means, diff_sems)],
                          [m + e for m, e in zip(diff_means, diff_sems)],
                          alpha=0.15, color='#8B0000')
    ax_diff.axhline(0, color='black', linewidth=0.8)
    ax_diff.axvline(datetime(2025, 10, 21), color='gray', linewidth=1.5,
                    linestyle=':', alpha=0.7)
    ax_diff.annotate('Beam OFF', (datetime(2025, 10, 21), 0),
                     textcoords='offset points', xytext=(5, 10),
                     fontsize=8, color='gray', fontstyle='italic')

    # Annotate final value
    if diff_dates:
        final_m = diff_means[-1]
        final_s = diff_sems[-1]
        final_sig = abs(final_m / final_s) if final_s > 0 else 0
        ax_diff.annotate('%+.3f%% \u00b1 %.3f%% (%.1f\u03c3)\nN=%d plates' %
                         (final_m, final_s, final_sig, diff_ns[-1]),
                         xy=(diff_dates[-1], final_m),
                         textcoords='offset points', xytext=(-80, 25),
                         fontsize=9, fontweight='bold', color='#8B0000',
                         arrowprops=dict(arrowstyle='->', color='#8B0000', lw=0.8),
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                   edgecolor='#8B0000', alpha=0.9))

    ax_diff.annotate('Gain-immune: cancels intra-plate',
                     xy=(0.01, 0.05), xycoords='axes fraction',
                     fontsize=8, fontstyle='italic', color='green')

    ax_diff.set_title('(c) NdFeB \u2212 SmCo Intra-Plate Differential (Gain-Immune)',
                       fontsize=11, fontweight='bold')
    ax_diff.set_ylabel('Differential (%)', fontsize=10)
    ax_diff.set_xlabel('Date', fontsize=10)
    ax_diff.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax_diff.grid(alpha=0.3)
    ax_diff.legend(fontsize=9, loc='lower left')
    ax_diff.set_ylim(-0.45, 0.15)

    fig.suptitle('Temperature-Corrected Helmholtz Flux Change Over Time',
                 fontsize=13, fontweight='bold', y=1.01)
    fig.text(0.5, -0.01, 'PRELIMINARY \u2014 LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    fig.text(0.99, -0.01, 'Error bars: \u00b11 SEM',
             ha='right', fontsize=8, fontstyle='italic', color='gray')

    plt.tight_layout(rect=[0, 0.01, 1, 0.98])
    save(fig, 'P2_timeseries_dual.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P3: Regional Breakdown
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P3_regional(results, gain_syst):
    """NdFeB degradation by region: arc vs linac vs labyrinth."""
    clean = [r for r in results if not r['is_outlier']]

    # Group NdFeB by region
    ndfeb = [r for r in clean if r['material'] in ('N42EH', 'N52SH')]
    region_vals = defaultdict(list)
    for r in ndfeb:
        region_vals[r['region']].append(r['pct_change'])

    # Aggregate: arcs vs linacs vs labyrinth
    agg = defaultdict(list)
    for region, vals in region_vals.items():
        if 'Arc' in region:
            agg['Arcs'].extend(vals)
        elif 'Linac' in region:
            agg['Linacs'].extend(vals)
        elif 'Labyrinth' in region:
            agg['Labyrinth'].extend(vals)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6),
                                    gridspec_kw={'width_ratios': [2, 1.5]})

    # Left: per-region bars
    regions_ordered = [r for r in REGION_ORDER if r in region_vals]
    x = range(len(regions_ordered))
    means = [np.mean(region_vals[r]) for r in regions_ordered]
    sems = [np.std(region_vals[r], ddof=1) / np.sqrt(len(region_vals[r]))
            for r in regions_ordered]
    ns = [len(region_vals[r]) for r in regions_ordered]
    colors = [REGION_COLORS.get(r, '#888888') for r in regions_ordered]

    ax1.bar(x, means, color=colors, edgecolor='black', linewidth=0.6,
            yerr=sems, capsize=5, width=0.7)
    ax1.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.15, zorder=0)
    ax1.axhline(0, color='black', linewidth=0.8)

    for i, (m, s, n) in enumerate(zip(means, sems, ns)):
        ax1.annotate('%+.2f%%\n(N=%d)' % (m, n),
                     (i, m), textcoords='offset points',
                     xytext=(0, -15 if m < 0 else 8), ha='center', fontsize=8)

    ax1.set_xticks(x)
    ax1.set_xticklabels(regions_ordered, rotation=30, ha='right', fontsize=9)
    ax1.set_ylabel('NdFeB Flux Change (%)', fontsize=11)
    ax1.set_title('NdFeB Degradation by Tunnel Region', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # Right: aggregated arc vs linac
    agg_order = ['Arcs', 'Linacs', 'Labyrinth']
    agg_colors = ['#CC3333', '#3366CC', '#888888']
    x2 = range(len(agg_order))
    agg_means = [np.mean(agg[k]) for k in agg_order]
    agg_sems = [np.std(agg[k], ddof=1) / np.sqrt(len(agg[k])) for k in agg_order]
    agg_ns = [len(agg[k]) for k in agg_order]

    ax2.bar(x2, agg_means, color=agg_colors, edgecolor='black', linewidth=0.8,
            yerr=agg_sems, capsize=6, width=0.5)
    ax2.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.15, zorder=0)
    ax2.axhline(0, color='black', linewidth=0.8)

    for i, (m, s, n) in enumerate(zip(agg_means, agg_sems, agg_ns)):
        ax2.annotate('%+.3f%% ± %.3f%%\n(N=%d)' % (m, s, n),
                     (i, m), textcoords='offset points',
                     xytext=(0, -20 if m < 0 else 8), ha='center',
                     fontsize=9, fontweight='bold')

    ax2.set_xticks(x2)
    ax2.set_xticklabels(agg_order, fontsize=11)
    ax2.set_ylabel('NdFeB Flux Change (%)', fontsize=11)
    ax2.set_title('Arc vs Linac (NdFeB)', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    ratio = agg_means[0] / agg_means[1] if agg_means[1] != 0 else 0
    ax2.annotate('Arc/Linac ratio: %.1f×' % ratio,
                 xy=(0.5, 0.95), xycoords='axes fraction',
                 fontsize=10, fontweight='bold', ha='center', va='top',
                 color='#8B0000')

    fig.text(0.5, -0.02, 'PRELIMINARY — LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    fig.text(0.99, -0.02, 'Error bars: ±1 SEM',
             ha='right', fontsize=8, fontstyle='italic', color='gray')
    plt.tight_layout()
    save(fig, 'P3_regional_breakdown.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P4: Lab Control Validation
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P4_lab_controls(results, intra_diffs, intra_details):
    """Lab vs tunnel differential comparison."""
    clean = [r for r in results if not r['is_outlier']]

    # Load lab data (same approach as v5_polish)
    from manager_summary_v5_polish import load_lab_y_plates
    lab_plates = load_lab_y_plates()

    lab_diffs = [p['diff'] for p in lab_plates.values()
                 if p.get('diff') is not None and not np.isnan(p['diff'])]
    tunnel_diff_mean = np.mean(intra_diffs)
    tunnel_diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    lab_diff_mean = np.mean(lab_diffs) if lab_diffs else 0
    lab_diff_sem = (np.std(lab_diffs, ddof=1) / np.sqrt(len(lab_diffs))
                    if len(lab_diffs) > 1 else 0.05)

    diff_of_diffs = tunnel_diff_mean - lab_diff_mean
    diff_of_diffs_err = np.sqrt(tunnel_diff_sem**2 + lab_diff_sem**2)
    diff_sig = abs(diff_of_diffs / diff_of_diffs_err) if diff_of_diffs_err > 0 else 0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6),
                                    gridspec_kw={'width_ratios': [1.5, 2]})

    # Left: 3 bars
    labels = ['Tunnel\n(30 plates)', 'Lab Control\n(%d plates)' % len(lab_diffs),
              'Tunnel − Lab']
    vals = [tunnel_diff_mean, lab_diff_mean, diff_of_diffs]
    errs = [tunnel_diff_sem, lab_diff_sem, diff_of_diffs_err]
    colors = ['#8B0000', '#3366CC', '#DAA520']

    ax1.bar(range(3), vals, color=colors, edgecolor='black', linewidth=0.8,
            yerr=errs, capsize=6, width=0.55, error_kw={'linewidth': 2})
    ax1.axhline(0, color='black', linewidth=0.8)

    for i, (v, e) in enumerate(zip(vals, errs)):
        sig = abs(v/e) if e > 0 else 0
        ax1.annotate('%+.3f%% ± %.3f%%\n(%.1fσ)' % (v, e, sig),
                     (i, v), textcoords='offset points',
                     xytext=(0, -20 if v < 0 else 10), ha='center',
                     fontsize=9, fontweight='bold')

    ax1.set_xticks(range(3))
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.set_ylabel('NdFeB − SmCo Differential (%)', fontsize=11)
    ax1.set_title('Tunnel vs Lab Control\n(NdFeB−SmCo Differential)',
                   fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    ax1.annotate('Lab controls confirm\nradiation signal (%.1fσ)' % diff_sig,
                 xy=(0.5, 0.95), xycoords='axes fraction',
                 fontsize=10, fontweight='bold', ha='center', va='top',
                 color='green',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen',
                           alpha=0.3))

    # Right: strip plot
    ax2.scatter(np.zeros(len(intra_diffs)) + np.random.RandomState(42).normal(0, 0.05, len(intra_diffs)),
                intra_diffs, color='#8B0000', alpha=0.5, s=30,
                edgecolors='black', linewidth=0.3, label='Tunnel plates (N=%d)' % len(intra_diffs))

    if lab_diffs:
        ax2.scatter(np.ones(len(lab_diffs)) + np.random.RandomState(42).normal(0, 0.03, len(lab_diffs)),
                    lab_diffs, color='#3366CC', alpha=0.6, s=40,
                    edgecolors='black', linewidth=0.3, marker='D',
                    label='Lab plates (N=%d)' % len(lab_diffs))

    # Mean lines
    ax2.hlines(tunnel_diff_mean, -0.3, 0.3, color='#8B0000', linewidth=2)
    if lab_diffs:
        ax2.hlines(lab_diff_mean, 0.7, 1.3, color='#3366CC', linewidth=2)

    ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(['Tunnel', 'Lab Control'], fontsize=11)
    ax2.set_ylabel('Per-Plate NdFeB − SmCo Differential (%)', fontsize=11)
    ax2.set_title('Individual Plate Differentials', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', alpha=0.3)

    ax2.annotate('Lab: temp-corrected (estimated temps)',
                 xy=(0.98, 0.02), xycoords='axes fraction',
                 fontsize=7, ha='right', fontstyle='italic', color='gray')

    fig.text(0.5, -0.02, 'PRELIMINARY — LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    fig.text(0.99, -0.02, 'Error bars: ±1 SEM',
             ha='right', fontsize=8, fontstyle='italic', color='gray')
    plt.tight_layout()
    save(fig, 'P4_lab_controls.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P5: Uncertainty Budget
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P5_uncertainty_budget(results, gain_syst, gain_syst_raw=None):
    """Uncertainty budget as a table figure.

    Parameters
    ----------
    gain_syst : float
        Cleaned gain systematic (±%).
    gain_syst_raw : float or None
        Uncleaned gain systematic (±%). If provided, shown in parenthetical.
    """
    clean = [r for r in results if not r['is_outlier']]

    # Count single-baseline samples
    n_single = sum(1 for r in results if r.get('bl_sem_pct', 0) > 0.5)

    # Format gain row depending on whether we have raw value
    if gain_syst_raw is not None:
        gain_mag = '\u00b1%.2f%%\n(\u00b1%.2f%% before cleaning)' % (gain_syst, gain_syst_raw)
        gain_mit = ('Cancels in intra-plate differential;\n'
                    'cleaned: excl. bad baselines + |offset|>3%;\n'
                    'future: start/end-of-day calibration')
    else:
        gain_mag = '\u00b1%.2f%%' % gain_syst
        gain_mit = ('Cancels in intra-plate differential;\n'
                    'future: start/end-of-day calibration')

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis('off')

    table_data = [
        ['Source', 'Magnitude', 'Affects', 'Mitigation'],
        ['Helmholtz gain\n(session-to-session)', gain_mag,
         'ALL absolute values\n(Y, H, A samples)', gain_mit],
        ['Temperature\ncorrection residual', '~0.01\u20130.05%',
         'Temp-corrected values',
         'Uses co-located Teslameter temps;\nT_ref = 20\u00b0C'],
        ['Single baseline\nvulnerability', '%d of %d samples\nhave only 1 baseline' % (n_single, len(results)),
         'Baseline accuracy\nfor those samples',
         'Multi-baseline mean more robust;\nfuture runs add more baselines'],
        ['Oct 21 thermal lag', '~0.3% inflation\nof differential',
         'Oct 21 data only',
         'Tunnel cooled rapidly;\nmagnets lag air temp'],
        ['Jul 17 measurement\nartifact', '~0.8% offset\n(material-independent)',
         'Jul 17 group only\n(15 plates)',
         'Excluded from clean analysis;\nshown flagged in full dataset'],
        ['Teslameter positioning', '0.3\u201316.5% std\n(face-dependent)',
         'Teslameter field data\n(NOT Helmholtz)',
         'Top face best (0.3%);\ntoo noisy for degradation signal'],
    ]

    colors = [['#D4E6F1'] * 4]  # header
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            colors.append(['#F8F8F8'] * 4)
        else:
            colors.append(['white'] * 4)

    table = ax.table(cellText=table_data, cellColours=colors,
                     loc='center', cellLoc='left')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 2.2)

    # Style header
    for j in range(4):
        table[0, j].set_text_props(fontweight='bold', fontsize=10)
        table[0, j].set_facecolor('#2C3E50')
        table[0, j].set_text_props(color='white', fontweight='bold')

    ax.set_title('Systematic Uncertainty Budget\n'
                 'Key insight: gain systematic (±%.2f%%) cancels in the '
                 'intra-plate NdFeB−SmCo differential' % gain_syst,
                 fontsize=13, fontweight='bold', pad=20)

    fig.text(0.5, 0.02, 'PRELIMINARY — LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    plt.tight_layout()
    save(fig, 'P5_uncertainty_budget.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P6: ΔT_crit Predicted vs Observed Ranking
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P6_tcrit_ranking(results):
    """ΔT_crit from Allstar specs vs observed degradation."""
    clean = [r for r in results if not r['is_outlier']]

    # Allstar-verified specs (from datasheets uploaded 2026-03-16)
    specs = {
        'N42EH':  {'Hci_min': 30, 'beta': 0.50, 'max_temp': 190, 'Tc': 330},
        'N52SH':  {'Hci_min': 19, 'beta': 0.60, 'max_temp': 140, 'Tc': 330},
        'SmCo33H': {'Hci_min': 25, 'beta': 0.20, 'max_temp': 350, 'Tc': 775},
        'SmCo35': {'Hci_min': 18, 'beta': 0.25, 'max_temp': 300, 'Tc': 775},
    }

    # ΔT_crit at |H_op| = 5 kOe, T0 = 40°C
    H_op = 5.0
    for mat, s in specs.items():
        s['dTcrit'] = (s['Hci_min'] - H_op) / (s['Hci_min'] * s['beta'] * 0.01)

    materials = ['SmCo33H', 'SmCo35', 'N42EH', 'N52SH']  # ordered by ΔT_crit

    # Observed degradation
    obs = {}
    for mat in materials:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        obs[mat] = {'mean': np.mean(vals), 'sem': np.std(vals, ddof=1) / np.sqrt(len(vals)),
                    'n': len(vals)}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: ΔT_crit bars
    dTcrits = [specs[m]['dTcrit'] for m in materials]
    colors_bar = [PRES_COLORS[m] for m in materials]
    ax1.barh(range(4), dTcrits, color=colors_bar, edgecolor='black',
             linewidth=0.8, height=0.5)
    ax1.set_yticks(range(4))
    ax1.set_yticklabels(materials, fontsize=11)
    ax1.set_xlabel('ΔT_crit (°C) at |H_op| = 5 kOe (398 kA/m)', fontsize=11)
    ax1.set_title('Predicted Radiation Resistance\n(from Allstar Magnetics specs)',
                   fontsize=12, fontweight='bold')

    for i, (m, dt) in enumerate(zip(materials, dTcrits)):
        s = specs[m]
        ax1.annotate('%.0f°C\n(Hci≥%d kOe / %d kA/m, β=%.2f%%/°C)' % (
                         dt, s['Hci_min'], int(s['Hci_min'] * 79.58), s['beta']),
                     (dt, i), textcoords='offset points',
                     xytext=(5, 0), va='center', fontsize=8)

    ax1.axvline(0, color='black', linewidth=0.5)
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()

    # Right: observed degradation
    obs_means = [obs[m]['mean'] for m in materials]
    obs_sems = [obs[m]['sem'] for m in materials]
    ax2.barh(range(4), obs_means, xerr=obs_sems, color=colors_bar,
             edgecolor='black', linewidth=0.8, height=0.5, capsize=5)
    ax2.set_yticks(range(4))
    ax2.set_yticklabels(materials, fontsize=11)
    ax2.set_xlabel('Observed Flux Change (%)', fontsize=11)
    ax2.set_title('Observed Degradation\n(Helmholtz, temp-corrected)',
                   fontsize=12, fontweight='bold')

    for i, m in enumerate(materials):
        o = obs[m]
        sig = abs(o['mean'] / o['sem']) if o['sem'] > 0 else 0
        # Place annotations to the left of negative bars, right of positive/near-zero
        if o['mean'] < -0.1:
            xoff, ha = (-8, 'right')
        else:
            xoff, ha = (8, 'left')
        ax2.annotate('%+.3f%%\n(%.1fσ, N=%d)' % (o['mean'], sig, o['n']),
                     (o['mean'], i), textcoords='offset points',
                     xytext=(xoff, 0), va='center', ha=ha,
                     fontsize=7.5, fontweight='bold')

    ax2.axvline(0, color='black', linewidth=0.8)
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()

    # Annotation about inversion
    fig.text(0.5, -0.04,
             'SmCo ranking matches prediction (SmCo33H > SmCo35). '
             'NdFeB ranking is INVERTED: N42EH degrades more than N52SH despite higher Hci.\n'
             'Possible explanation: EH/SH treatment differences, ¹⁰B content, or operating point effects.',
             ha='center', fontsize=9, fontstyle='italic', color='#8B0000',
             wrap=True)

    fig.text(0.5, -0.08, 'PRELIMINARY — LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    fig.text(0.99, -0.08, 'Error bars: ±1 SEM',
             ha='right', fontsize=8, fontstyle='italic', color='gray')
    plt.tight_layout()
    save(fig, 'P6_tcrit_vs_observed.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P7: Teslameter Honest Summary
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P7_teslameter_summary(results):
    """Honest Teslameter summary: what it tells us, what it doesn't."""
    clean = [r for r in results if not r['is_outlier']]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: signal vs noise comparison
    signal = 0.266  # our NdFeB-SmCo differential
    noises = {
        'Top face\n(best)': 0.22,
        'Front face': 0.74,
        'Side face': 1.40,
        'SmCo A-sample\ntop face': 16.5,
    }

    bars_x = range(len(noises) + 1)
    bars_vals = [signal] + list(noises.values())
    bars_labels = ['Expected\nsignal'] + list(noises.keys())
    bars_colors = ['#2ECC40'] + ['#FF4136'] * len(noises)

    ax1.bar(bars_x, bars_vals, color=bars_colors, edgecolor='black',
            linewidth=0.8, width=0.6, alpha=0.8)
    ax1.set_xticks(bars_x)
    ax1.set_xticklabels(bars_labels, fontsize=9)
    ax1.set_ylabel('Standard Deviation / Signal (%)', fontsize=11)
    ax1.set_title('Teslameter Positioning Noise vs Signal\n'
                   '(why field data is uninformative for degradation)',
                   fontsize=11, fontweight='bold')
    ax1.set_yscale('log')
    ax1.set_ylim(0.1, 30)

    for i, v in enumerate(bars_vals):
        ax1.annotate('%.2f%%' % v if v < 1 else '%.1f%%' % v,
                     (i, v), textcoords='offset points',
                     xytext=(0, 5), ha='center', fontsize=8, fontweight='bold')

    ax1.axhline(signal, color='green', linewidth=1, linestyle='--', alpha=0.5)
    ax1.grid(axis='y', alpha=0.3)

    # Right: what Teslameter IS good for
    ax2.axis('off')
    text_content = """
TESLAMETER ROLE IN THIS STUDY

✓  WHAT IT PROVIDES:
    • Co-located temperature measurements
      for Helmholtz correction (critical)
    • Confirms rig tolerance hierarchy
      (top > front > side)
    • Independent instrument cross-check
      (null result is informative)

✗  WHAT IT CANNOT DO:
    • Detect ~0.3% degradation signal
      (positioning noise 1-50× larger)
    • Provide pre-deployment field baseline
      (rig/cap changed before deployment)

→  PLANNED IMPROVEMENTS:
    • New beam run: establish clean baseline
    • Error analysis campaigns on lab samples
    • Lab Helmholtz with temperature data
    • More careful measurement methodologies
    """

    ax2.text(0.05, 0.95, text_content, transform=ax2.transAxes,
             fontsize=10, verticalalignment='top', fontfamily='sans-serif',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#F0F0F0',
                       edgecolor='gray', alpha=0.8))
    ax2.set_title('Teslameter Assessment', fontsize=12, fontweight='bold')

    fig.text(0.5, -0.02, 'PRELIMINARY — LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    plt.tight_layout()
    save(fig, 'P7_teslameter_summary.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P8: Waterfall by Region (NdFeB)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P8_waterfall_regional(results, gain_syst):
    """NdFeB waterfall sorted by degradation, grouped by region.

    Key message: average is ~0.3% but peak is much higher (>0.8%).
    """
    clean = [r for r in results if not r['is_outlier']]
    ndfeb = [r for r in clean if r['material'] in ('N42EH', 'N52SH')]

    # Group by arc vs linac vs labyrinth
    region_groups = [
        ('Arcs', ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc']),
        ('Linacs', ['North Linac', 'South Linac']),
        ('Labyrinth', ['Labyrinth']),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 8),
                              gridspec_kw={'width_ratios': [4, 2, 1]},
                              sharey=False)

    overall_min = min(r['pct_change'] for r in ndfeb)
    overall_max = max(r['pct_change'] for r in ndfeb)
    xlim = (min(overall_min * 1.15, -0.1), max(overall_max * 1.15, 0.15))

    all_ndfeb_mean = np.mean([r['pct_change'] for r in ndfeb])

    for ax_idx, (group_name, regions) in enumerate(region_groups):
        ax = axes[ax_idx]
        group = sorted([r for r in ndfeb if r['region'] in regions],
                       key=lambda r: r['pct_change'])

        if not group:
            ax.set_visible(False)
            continue

        y_pos = 0
        yticks, ylabels = [], []
        region_starts = {}

        # Sub-group by specific region
        for region in REGION_ORDER:
            if region not in regions:
                continue
            sub = sorted([r for r in group if r['region'] == region],
                         key=lambda r: r['pct_change'])
            if not sub:
                continue
            region_starts[region] = y_pos
            for r in sub:
                color = PRES_COLORS.get(r['material'], '#888')
                ax.barh(y_pos, r['pct_change'], height=0.7, color=color,
                        alpha=0.85, edgecolor='black', linewidth=0.3)
                yticks.append(y_pos)
                line_str = ' (L%d)' % r['line'] if r.get('line', 0) > 0 else ''
                ylabels.append('Y-%d-%d%s' % (r['plate'], r['slot'], line_str))
                y_pos += 1
            y_pos += 0.5  # small gap between sub-regions

        # Gain band
        ax.axvspan(-gain_syst, gain_syst, alpha=0.08, color='gray', zorder=0)
        ax.axvline(0, color='black', linewidth=0.8)

        # Mean line
        grp_vals = [r['pct_change'] for r in group]
        grp_mean = np.mean(grp_vals)
        ax.axvline(grp_mean, color='#8B0000', linewidth=1.5, linestyle='--',
                   alpha=0.7, zorder=3)

        ax.set_yticks(yticks)
        ax.set_yticklabels(ylabels, fontsize=5.5)
        ax.set_xlim(xlim)
        ax.set_title('%s (N=%d)\nmean: %.3f%%' % (group_name, len(group), grp_mean),
                     fontsize=11, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        ax.invert_yaxis()

        if ax_idx == 0:
            ax.set_xlabel('% Change from Baseline', fontsize=10)

        # Region divider labels
        for region, ystart in region_starts.items():
            short = region.replace(' Arc', '').replace(' Linac', '')
            ax.annotate(short, xy=(xlim[0], ystart - 0.3),
                        fontsize=7, fontweight='bold', color='#555',
                        ha='left', va='bottom')

    # Annotations on first panel
    ax0 = axes[0]
    worst = min(r['pct_change'] for r in ndfeb)
    best = max(r['pct_change'] for r in ndfeb
               if r['material'] in ('N42EH', 'N52SH'))

    fig.text(0.5, 0.97,
             'NdFeB Sample-by-Sample Degradation by Tunnel Region',
             ha='center', fontsize=14, fontweight='bold', va='top')
    fig.text(0.5, 0.94,
             'Peak: %.2f%%  |  Mean: %.3f%%  |  Gain systematic band: '
             '\u00b1%.2f%% (gray)' % (worst, all_ndfeb_mean, gain_syst),
             ha='center', fontsize=10, color='#8B0000', va='top')

    # Legend
    import matplotlib.patches as mpatches
    handles = [mpatches.Patch(color=PRES_COLORS['N42EH'], label='N42EH'),
               mpatches.Patch(color=PRES_COLORS['N52SH'], label='N52SH')]
    axes[0].legend(handles=handles, fontsize=8, loc='lower left')

    fig.text(0.5, -0.02, 'PRELIMINARY \u2014 LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    plt.tight_layout(rect=[0, 0.0, 1, 0.92])
    save(fig, 'P8_waterfall_regional.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P9: Waterfall by Region — All 4 Materials
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P9_waterfall_all_materials(results, gain_syst):
    """All-material waterfall sorted by degradation, grouped by region.

    Key message: NdFeB bars extend far left while SmCo clusters near zero.
    Shows all 4 grades so the material contrast is visually dramatic.
    """
    clean = [r for r in results if not r['is_outlier']]
    import matplotlib.patches as mpatches

    region_groups = [
        ('Arcs', ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc']),
        ('Linacs', ['North Linac', 'South Linac']),
        ('Labyrinth', ['Labyrinth']),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 12),
                              gridspec_kw={'width_ratios': [4, 2, 1]},
                              sharey=False)

    overall_min = min(r['pct_change'] for r in clean)
    overall_max = max(r['pct_change'] for r in clean)
    xlim = (min(overall_min * 1.15, -0.1), max(overall_max * 1.15, 0.5))

    for ax_idx, (group_name, regions) in enumerate(region_groups):
        ax = axes[ax_idx]
        group = [r for r in clean if r['region'] in regions]

        if not group:
            ax.set_visible(False)
            continue

        y_pos = 0
        yticks, ylabels = [], []
        region_starts = {}

        for region in REGION_ORDER:
            if region not in regions:
                continue
            sub = sorted([r for r in group if r['region'] == region],
                         key=lambda r: r['pct_change'])
            if not sub:
                continue
            region_starts[region] = y_pos
            for r in sub:
                color = PRES_COLORS.get(r['material'], '#888')
                ax.barh(y_pos, r['pct_change'], height=0.7, color=color,
                        alpha=0.85, edgecolor='black', linewidth=0.3)
                yticks.append(y_pos)
                line_str = ' (L%d)' % r['line'] if r.get('line', 0) > 0 else ''
                ylabels.append('Y-%d-%d%s' % (r['plate'], r['slot'], line_str))
                y_pos += 1
            y_pos += 0.5

        # Gain band
        ax.axvspan(-gain_syst, gain_syst, alpha=0.08, color='gray', zorder=0)
        ax.axvline(0, color='black', linewidth=0.8)

        # NdFeB mean line
        nd_vals = [r['pct_change'] for r in group
                   if r['material'] in ('N42EH', 'N52SH')]
        sm_vals = [r['pct_change'] for r in group
                   if r['material'] in ('SmCo33H', 'SmCo35')]
        if nd_vals:
            ax.axvline(np.mean(nd_vals), color='#8B0000', linewidth=1.5,
                       linestyle='--', alpha=0.7, zorder=3,
                       label='NdFeB mean' if ax_idx == 0 else None)
        if sm_vals:
            ax.axvline(np.mean(sm_vals), color='#3366CC', linewidth=1.5,
                       linestyle='--', alpha=0.7, zorder=3,
                       label='SmCo mean' if ax_idx == 0 else None)

        ax.set_yticks(yticks)
        ax.set_yticklabels(ylabels, fontsize=4.5)
        ax.set_xlim(xlim)

        n_nd = len(nd_vals)
        n_sm = len(sm_vals)
        ax.set_title('%s (N=%d)\nNdFeB: %.3f%% | SmCo: %.3f%%' % (
            group_name, len(group),
            np.mean(nd_vals) if nd_vals else 0,
            np.mean(sm_vals) if sm_vals else 0),
            fontsize=10, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        ax.invert_yaxis()

        if ax_idx == 0:
            ax.set_xlabel('% Change from Baseline', fontsize=10)

        for region, ystart in region_starts.items():
            short = region.replace(' Arc', '').replace(' Linac', '')
            ax.annotate(short, xy=(xlim[0], ystart - 0.3),
                        fontsize=6, fontweight='bold', color='#555',
                        ha='left', va='bottom')

    # Suptitle
    fig.text(0.5, 0.98,
             'All Materials: Sample-by-Sample Degradation by Tunnel Region',
             ha='center', fontsize=14, fontweight='bold', va='top')

    all_nd = [r['pct_change'] for r in clean
              if r['material'] in ('N42EH', 'N52SH')]
    all_sm = [r['pct_change'] for r in clean
              if r['material'] in ('SmCo33H', 'SmCo35')]
    fig.text(0.5, 0.955,
             'NdFeB mean: %.3f%% (red bars left) | SmCo mean: %.3f%% '
             '(blue bars near zero) | Gain band: \u00b1%.2f%% (gray)'
             % (np.mean(all_nd), np.mean(all_sm), gain_syst),
             ha='center', fontsize=9.5, color='#333', va='top')

    # Legend
    handles = [mpatches.Patch(color=PRES_COLORS[m], label=m)
               for m in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']]
    axes[0].legend(handles=handles, fontsize=7, loc='lower left')

    fig.text(0.5, -0.02, 'PRELIMINARY \u2014 LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    plt.tight_layout(rect=[0, 0.0, 1, 0.93])
    save(fig, 'P9_waterfall_all_materials.png')


# ═══════════════════════════════════════════════════════════════════════════════
# H/A helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _average_a_to_slot(a_results):
    """Average A-sample pairs to H-plate slot level.

    Each H-plate slot has 2 A-sample pairs (pair index 1 and 2).
    These share the same radiation exposure, so averaging to slot level
    gives the correct effective N for statistics.

    Returns list of dicts with one entry per (material, plate, slot).
    """
    from collections import defaultdict
    slot_data = defaultdict(list)
    slot_meta = {}
    for r in a_results:
        if r['is_outlier']:
            continue
        key = (r['material'], r['plate'], r['pair_slot'])
        slot_data[key].append(r['pct_change'])
        if key not in slot_meta:
            slot_meta[key] = r  # keep first entry's metadata

    out = []
    for key, pcts in slot_data.items():
        mat, plate, slot = key
        meta = slot_meta[key]
        out.append({
            'material': mat,
            'plate': plate,
            'pair_slot': slot,
            'pct_change': np.mean(pcts),
            'n_pairs': len(pcts),
            'is_outlier': False,
            'temp_corrected': meta.get('temp_corrected', False),
            'region': meta.get('region', 'Unknown'),
            'line': meta.get('line', 0),
            'h_sample': meta.get('h_sample', ''),
        })
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# P10: H-Plate Material Comparison (Tunnel)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P10_h_plate_material(h_results, gain_syst, gain_syst_raw=None):
    """H-plate pair assembly: NdFeB vs SmCo bar chart with individual points."""
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7),
                                    gridspec_kw={'width_ratios': [1, 1.3]})

    # ─── Left: Bar chart ───
    nd_vals = [r['pct_change'] for r in h_clean if r['material'] == 'NdFeB']
    sm_vals = [r['pct_change'] for r in h_clean if r['material'] == 'SmCo']

    nd_mean = np.mean(nd_vals) if nd_vals else 0
    nd_sem = np.std(nd_vals, ddof=1) / np.sqrt(len(nd_vals)) if len(nd_vals) > 1 else 0
    sm_mean = np.mean(sm_vals) if sm_vals else 0
    sm_sem = np.std(sm_vals, ddof=1) / np.sqrt(len(sm_vals)) if len(sm_vals) > 1 else 0

    nd_sig = abs(nd_mean / nd_sem) if nd_sem > 0 else 0
    sm_sig = abs(sm_mean / sm_sem) if sm_sem > 0 else 0

    bars = ax1.bar([0, 1], [nd_mean, sm_mean], yerr=[nd_sem, sm_sem],
                   color=['#CC3333', '#3366CC'], capsize=8, edgecolor='black',
                   linewidth=1, width=0.5, alpha=0.85,
                   error_kw=dict(linewidth=2, capthick=2))
    ax1.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax1.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.12, zorder=0)

    if gain_syst_raw is not None:
        gain_label = '\u00b1%.2f%% gain syst. (\u00b1%.2f%% uncleaned)' % (
            gain_syst, gain_syst_raw)
    else:
        gain_label = '\u00b1%.2f%% gain systematic' % gain_syst
    ax1.axhline(gain_syst, color='goldenrod', linewidth=1, linestyle='--',
                label=gain_label, alpha=0.7)
    ax1.axhline(-gain_syst, color='goldenrod', linewidth=1, linestyle='--',
                alpha=0.7)

    for i, (val, sem, sig, n) in enumerate([
            (nd_mean, nd_sem, nd_sig, len(nd_vals)),
            (sm_mean, sm_sem, sm_sig, len(sm_vals))]):
        y = val - sem - 0.03 if val < 0 else val + sem + 0.03
        va = 'top' if val < 0 else 'bottom'
        ax1.text(i, y, '%+.3f%% \u00b1 %.3f%%\n(%.1f\u03c3, N=%d)' % (
            val, sem, sig, n),
            ha='center', va=va, fontsize=10, fontweight='bold')

    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(['NdFeB\n(pair assembly)', 'SmCo\n(pair assembly)'],
                         fontsize=11)
    ax1.set_ylabel('% Change from Baseline', fontsize=12)
    ax1.set_title('H-Plate Pair Assembly Results', fontsize=14,
                  fontweight='bold')
    ax1.legend(fontsize=9, loc='lower left')
    ax1.grid(axis='y', alpha=0.3)

    # ─── Right: Strip plot by region ───
    rng = np.random.RandomState(42)
    regions = ['NdFeB', 'SmCo']
    for mat_idx, (mat, color) in enumerate(
            [('NdFeB', '#CC3333'), ('SmCo', '#3366CC')]):
        vals = [r['pct_change'] for r in h_clean if r['material'] == mat]
        x_base = mat_idx
        jitter = rng.normal(0, 0.08, len(vals))
        ax2.scatter(np.full(len(vals), x_base) + jitter, vals,
                    color=color, alpha=0.5, s=25, edgecolor='black',
                    linewidth=0.3, zorder=3)
        mean = np.mean(vals) if vals else 0
        ax2.hlines(mean, x_base - 0.25, x_base + 0.25, colors=color,
                   linewidth=2.5, zorder=4)

    ax2.axhline(0, color='black', linewidth=1, linestyle='--')
    ax2.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.12, zorder=0)
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(['NdFeB (N=%d)' % len(nd_vals),
                          'SmCo (N=%d)' % len(sm_vals)], fontsize=11)
    ax2.set_ylabel('% Change from Baseline', fontsize=12)
    ax2.set_title('Individual H-Plate Pairs', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    ax2.annotate('H-plates are single-material assemblies.\n'
                 'Unlike Y-plates, NdFeB\u2212SmCo difference is\n'
                 'between plates (carries full gain systematic).\n'
                 'All baselines are single-reading (1 date with\n'
                 'temperature data). Awaiting room temp data.',
                 xy=(0.98, 0.02), xycoords='axes fraction', ha='right',
                 va='bottom', fontsize=8, fontstyle='italic', color='#666666',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFFF0',
                           edgecolor='#CCCCCC', alpha=0.9))

    fig.suptitle('H-Plate (Pair Assembly) Degradation — Tunnel Samples',
                 fontsize=15, fontweight='bold', y=1.01)
    fig.text(0.5, -0.02, 'PRELIMINARY \u2014 LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    fig.text(0.99, -0.02, 'Error bars: \u00b11 SEM',
             ha='right', fontsize=8, fontstyle='italic', color='gray')
    fig.tight_layout(rect=[0, 0.0, 1, 0.96])
    save(fig, 'P10_h_plate_material.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P11: A-Sample Summary (Pairs, averaged to H-plate slot level)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P11_a_sample_summary(a_results, h_results, gain_syst):
    """A-sample (pair) results: NdFeB vs SmCo bars + A-vs-H correlation.

    Statistics computed at H-plate slot level (2 pairs per slot averaged)
    to avoid double-counting correlated measurements.
    """
    a_slot = _average_a_to_slot(a_results)
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # ─── Left: A-sample material bars (slot-level) ───
    for mat_idx, (mat, color) in enumerate(
            [('NdFeB', '#CC3333'), ('SmCo', '#3366CC')]):
        vals = [r['pct_change'] for r in a_slot if r['material'] == mat]
        if not vals:
            continue
        mean = np.mean(vals)
        sem = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0
        sig = abs(mean / sem) if sem > 0 else 0

        ax1.bar(mat_idx, mean, yerr=sem, color=color, capsize=8,
                edgecolor='black', linewidth=1, width=0.5, alpha=0.85,
                error_kw=dict(linewidth=2, capthick=2))

        y = mean - sem - 0.02 if mean < 0 else mean + sem + 0.02
        va = 'top' if mean < 0 else 'bottom'
        ax1.text(mat_idx, y, '%+.3f%% \u00b1 %.3f%%\n(%.1f\u03c3, N=%d slots)' % (
            mean, sem, sig, len(vals)),
            ha='center', va=va, fontsize=10, fontweight='bold')

    ax1.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax1.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.12, zorder=0)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(['NdFeB\n(pair)', 'SmCo\n(pair)'], fontsize=11)
    ax1.set_ylabel('% Change from Baseline', fontsize=12)
    ax1.set_title('A-Sample Results (Slot-Averaged)', fontsize=14,
                  fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    n_tc = sum(1 for r in a_slot if r.get('temp_corrected', False))
    ax1.annotate('A-samples are pairs (2 magnets in\n'
                 'enclosure, measured together). Averaged\n'
                 'to H-plate slot level (2 pairs/slot).\n'
                 '%d/%d slots temp-corrected.\n'
                 'Single-reading baselines.' % (n_tc, len(a_slot)),
                 xy=(0.98, 0.02), xycoords='axes fraction', ha='right',
                 va='bottom', fontsize=8, fontstyle='italic', color='#666666',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFFF0',
                           edgecolor='#CCCCCC', alpha=0.9))

    # ─── Right: A vs H correlation scatter (slot-level) ───
    h_lookup = {}
    for r in h_clean:
        h_lookup[r['sample']] = r['pct_change']

    a_vals, h_vals, colors_list = [], [], []
    for r in a_slot:
        h_key = r.get('h_sample', '')
        if h_key in h_lookup:
            a_vals.append(r['pct_change'])
            h_vals.append(h_lookup[h_key])
            colors_list.append('#CC3333' if r['material'] == 'NdFeB' else '#3366CC')

    if a_vals:
        ax2.scatter(h_vals, a_vals, c=colors_list, alpha=0.6, s=30,
                    edgecolor='black', linewidth=0.3, zorder=3)

        # 1:1 line
        all_vals = h_vals + a_vals
        vmin, vmax = min(all_vals), max(all_vals)
        pad = (vmax - vmin) * 0.1
        ax2.plot([vmin - pad, vmax + pad], [vmin - pad, vmax + pad],
                 'k--', linewidth=1, alpha=0.5, label='1:1 line')

        # Correlation
        from scipy import stats as sp_stats
        r_val, p_val = sp_stats.pearsonr(h_vals, a_vals)
        ax2.annotate('Pearson r = %.3f (p=%.3f)\nN = %d H-plate slots' % (
            r_val, p_val, len(a_vals)),
            xy=(0.05, 0.95), xycoords='axes fraction', ha='left',
            va='top', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                      edgecolor='orange', alpha=0.9))

        from matplotlib.lines import Line2D
        ax2.legend(handles=[
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#CC3333',
                   markersize=8, label='NdFeB'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#3366CC',
                   markersize=8, label='SmCo'),
            Line2D([0], [0], linestyle='--', color='black', label='1:1'),
        ], fontsize=9, loc='lower right')

    ax2.set_xlabel('H-Plate (slot-level) % change', fontsize=12)
    ax2.set_ylabel('A-Sample (slot-averaged) % change', fontsize=12)
    ax2.set_title('A-Sample vs Parent H-Plate Slot', fontsize=14,
                  fontweight='bold')
    ax2.grid(True, alpha=0.3)

    fig.suptitle('A-Sample (Pair) Analysis \u2014 Averaged to H-Plate Slot Level',
                 fontsize=15, fontweight='bold', y=1.01)
    fig.text(0.5, -0.02, 'PRELIMINARY \u2014 LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    fig.text(0.99, -0.02, 'Error bars: \u00b11 SEM',
             ha='right', fontsize=8, fontstyle='italic', color='gray')
    fig.tight_layout(rect=[0, 0.0, 1, 0.96])
    save(fig, 'P11_a_sample_summary.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P12: Combined Y+H+A Material Comparison
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P12_combined_YHA(y_results, h_results, a_results, gain_syst,
                          intra_diffs):
    """3-group comparison: Y, H, A for NdFeB and SmCo.

    A-samples averaged to H-plate slot level for correct N.
    """
    y_clean = [r for r in y_results if not r['is_outlier']]
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]
    a_slot = _average_a_to_slot(a_results)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # ─── Left: NdFeB across all types ───
    groups = []
    for label, data, mat_key in [
            ('Y-Plate\n(Helmholtz)', y_clean, ['N42EH', 'N52SH']),
            ('H-Plate\n(pair assembly)', h_clean, ['NdFeB']),
            ('A-Sample\n(pair, slot avg)', a_slot, ['NdFeB'])]:
        vals = [r['pct_change'] for r in data if r['material'] in mat_key]
        if vals:
            groups.append((label, np.mean(vals),
                           np.std(vals, ddof=1) / np.sqrt(len(vals)),
                           len(vals)))

    x = np.arange(len(groups))
    means = [g[1] for g in groups]
    sems = [g[2] for g in groups]
    ns = [g[3] for g in groups]
    labels = [g[0] for g in groups]

    ax1.bar(x, means, yerr=sems, color='#CC3333', capsize=8,
            edgecolor='black', linewidth=1, width=0.5, alpha=0.85,
            error_kw=dict(linewidth=2, capthick=2))
    ax1.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax1.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.12, zorder=0)

    for i, (m, s, n) in enumerate(zip(means, sems, ns)):
        sig = abs(m / s) if s > 0 else 0
        y = m - s - 0.02 if m < 0 else m + s + 0.02
        va = 'top' if m < 0 else 'bottom'
        ax1.text(i, y, '%+.3f%%\n(%.1f\u03c3, N=%d)' % (m, sig, n),
                 ha='center', va=va, fontsize=10, fontweight='bold')

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.set_ylabel('NdFeB % Change', fontsize=12)
    ax1.set_title('NdFeB Degradation Across All Sample Types', fontsize=14,
                  fontweight='bold', pad=15)
    ax1.grid(axis='y', alpha=0.3)

    # ─── Right: SmCo across all types ───
    groups_sm = []
    for label, data, mat_key in [
            ('Y-Plate\n(Helmholtz)', y_clean, ['SmCo33H', 'SmCo35']),
            ('H-Plate\n(pair assembly)', h_clean, ['SmCo']),
            ('A-Sample\n(pair, slot avg)', a_slot, ['SmCo'])]:
        vals = [r['pct_change'] for r in data if r['material'] in mat_key]
        if vals:
            groups_sm.append((label, np.mean(vals),
                              np.std(vals, ddof=1) / np.sqrt(len(vals)),
                              len(vals)))

    x_sm = np.arange(len(groups_sm))
    means_sm = [g[1] for g in groups_sm]
    sems_sm = [g[2] for g in groups_sm]
    ns_sm = [g[3] for g in groups_sm]
    labels_sm = [g[0] for g in groups_sm]

    ax2.bar(x_sm, means_sm, yerr=sems_sm, color='#3366CC', capsize=8,
            edgecolor='black', linewidth=1, width=0.5, alpha=0.85,
            error_kw=dict(linewidth=2, capthick=2))
    ax2.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax2.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.12, zorder=0)

    for i, (m, s, n) in enumerate(zip(means_sm, sems_sm, ns_sm)):
        sig = abs(m / s) if s > 0 else 0
        y = m - s - 0.02 if m < 0 else m + s + 0.02
        va = 'top' if m < 0 else 'bottom'
        ax2.text(i, y, '%+.3f%%\n(%.1f\u03c3, N=%d)' % (m, sig, n),
                 ha='center', va=va, fontsize=9, fontweight='bold')

    ax2.set_xticks(x_sm)
    ax2.set_xticklabels(labels_sm, fontsize=10)
    ax2.set_ylabel('SmCo % Change', fontsize=12)
    ax2.set_title('SmCo Stability Across All Sample Types', fontsize=14,
                  fontweight='bold', pad=15)
    ax2.grid(axis='y', alpha=0.3)

    # Match y-axis ranges with headroom for annotations
    ymin = min(ax1.get_ylim()[0], ax2.get_ylim()[0])
    ymax = max(ax1.get_ylim()[1], ax2.get_ylim()[1])
    margin = (ymax - ymin) * 0.12
    ax1.set_ylim(ymin, ymax + margin)
    ax2.set_ylim(ymin, ymax + margin)

    fig.suptitle('Permanent Magnet Degradation by Sample Type\n'
                 '(Gold band = \u00b1%.2f%% gain systematic)' % gain_syst,
                 fontsize=14, fontweight='bold', y=1.02)
    fig.text(0.5, -0.02, 'PRELIMINARY \u2014 LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    fig.text(0.99, -0.02, 'Error bars: \u00b11 SEM',
             ha='right', fontsize=8, fontstyle='italic', color='gray')
    fig.tight_layout(rect=[0, 0.0, 1, 0.95])
    save(fig, 'P12_combined_YHA.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P13: H/A Lab vs Tunnel (Unexposed vs Exposed for H/A)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P13_ha_lab_vs_tunnel(h_results, a_results, gain_syst):
    """Bar chart: tunnel vs lab for H-plate and A-sample NdFeB.

    Tunnel A-samples averaged to slot level for correct N.
    """
    import re as re_mod
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'Lab_Controls'))
    from lab_ha_analysis import (
        collect_all_lab_data, load_assembly_configs, analyze_lab_samples,
    )

    h_clean = [r for r in h_results if not r.get('is_outlier', False)]
    a_slot = _average_a_to_slot(a_results)

    # Load lab data
    configs = load_assembly_configs()
    lab_all = collect_all_lab_data()
    lab_results = analyze_lab_samples(lab_all, configs)
    lab_h = [r for r in lab_results if r['type'] == 'H'
             and not r['is_anomalous_baseline']
             and not r.get('is_delta_hplate', False)
             and r['config'].lower() not in ('beta', '')]
    lab_a = [r for r in lab_results if r['type'] == 'A'
             and not r['is_anomalous_baseline']
             and r['config'].lower() not in ('beta', '')]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    tunnel_color = '#8B0000'
    lab_color = '#3366CC'

    # ─── Left: H-plate tunnel vs lab ───
    for mat_idx, mat in enumerate(['NdFeB', 'SmCo']):
        t_vals = [r['pct_change'] for r in h_clean if r['material'] == mat]
        l_vals = [r['pct_change'] for r in lab_h if r['material'] == mat]
        x_t = mat_idx * 2.0
        x_l = mat_idx * 2.0 + 0.6

        for x, vals, color, label in [
                (x_t, t_vals, tunnel_color, 'Tunnel'),
                (x_l, l_vals, lab_color, 'Lab')]:
            if not vals:
                continue
            mean = np.mean(vals)
            sem = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0
            ax1.bar(x, mean, yerr=sem, color=color, capsize=6,
                    edgecolor='black', linewidth=0.8, width=0.5, alpha=0.85,
                    error_kw=dict(linewidth=1.5))
            y_ann = mean - sem - 0.05 if mean < 0 else mean + sem + 0.05
            ax1.text(x, y_ann, 'N=%d' % len(vals), ha='center',
                     va='top' if mean < 0 else 'bottom', fontsize=8)

    ax1.axhline(0, color='black', linewidth=1, linestyle='--')
    ax1.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.10, zorder=0)
    ax1.set_xticks([0.3, 2.3])
    ax1.set_xticklabels(['NdFeB', 'SmCo'], fontsize=11)
    ax1.set_ylabel('% Change from Baseline', fontsize=12)
    ax1.set_title('H-Plate: Tunnel vs Lab', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    from matplotlib.patches import Patch
    ax1.legend(handles=[
        Patch(facecolor=tunnel_color, edgecolor='black', label='Tunnel (exposed)'),
        Patch(facecolor=lab_color, edgecolor='black', label='Lab (unexposed)'),
    ], fontsize=9, loc='upper left')

    ax1.annotate('Lab: temp-corrected (estimated temps)', xy=(0.98, 0.02),
                 xycoords='axes fraction', ha='right', va='bottom',
                 fontsize=8, fontstyle='italic', color='#666666')

    # ─── Right: A-sample tunnel vs lab ───
    for mat_idx, mat in enumerate(['NdFeB', 'SmCo']):
        t_vals = [r['pct_change'] for r in a_slot if r['material'] == mat]
        l_vals = [r['pct_change'] for r in lab_a if r['material'] == mat]
        x_t = mat_idx * 2.0
        x_l = mat_idx * 2.0 + 0.6

        for x, vals, color in [
                (x_t, t_vals, tunnel_color),
                (x_l, l_vals, lab_color)]:
            if not vals:
                continue
            mean = np.mean(vals)
            sem = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0
            ax2.bar(x, mean, yerr=sem, color=color, capsize=6,
                    edgecolor='black', linewidth=0.8, width=0.5, alpha=0.85,
                    error_kw=dict(linewidth=1.5))
            y_ann = mean - sem - 0.05 if mean < 0 else mean + sem + 0.05
            ax2.text(x, y_ann, 'N=%d' % len(vals), ha='center',
                     va='top' if mean < 0 else 'bottom', fontsize=8)

    ax2.axhline(0, color='black', linewidth=1, linestyle='--')
    ax2.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.10, zorder=0)
    ax2.set_xticks([0.3, 2.3])
    ax2.set_xticklabels(['NdFeB', 'SmCo'], fontsize=11)
    ax2.set_ylabel('% Change from Baseline', fontsize=12)
    ax2.set_title('A-Sample: Tunnel vs Lab', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.annotate('Lab: temp-corrected (estimated temps)', xy=(0.98, 0.02),
                 xycoords='axes fraction', ha='right', va='bottom',
                 fontsize=8, fontstyle='italic', color='#666666')

    fig.suptitle('H-Plate & A-Sample: Tunnel (Exposed) vs Lab (Unexposed)\n'
                 '(Gold band = \u00b1%.2f%% gain systematic)' % gain_syst,
                 fontsize=14, fontweight='bold', y=1.02)
    fig.text(0.5, -0.02, 'PRELIMINARY \u2014 LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    fig.text(0.99, -0.02, 'Error bars: \u00b11 SEM',
             ha='right', fontsize=8, fontstyle='italic', color='gray')
    fig.tight_layout(rect=[0, 0.0, 1, 0.95])
    save(fig, 'P13_ha_lab_vs_tunnel.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P14: Co-located Y-plate Cross-Reference
# ═══════════════════════════════════════════════════════════════════════════════

# Co-location map from JLAB-TN-25-021: Y-plate → (H-prefix, H-plate-number)
# N = NdFeB H-plate, S = SmCo H-plate
COLOCATION = {
    # SE Arc
    15: ('N', 10), 3: ('N', 16), 23: ('N', 9), 26: ('N', 37), 40: ('N', 8),
    # NE Arc
    39: ('S', 12), 7: ('S', 16), 18: ('S', 20), 21: ('S', 6), 9: ('S', 14),
    # NW Arc
    38: ('N', 12), 6: ('N', 39), 36: ('N', 17), 25: ('N', 11), 34: ('N', 18),
    # SW Arc
    13: ('S', 1), 32: ('S', 2), 19: ('S', 17), 10: ('S', 10), 11: ('S', 3),
    # North Linac
    12: ('S', 4), 17: ('N', 20), 4: ('S', 7), 16: ('S', 15), 22: ('N', 15),
    # South Linac
    20: ('S', 5), 24: ('S', 13), 5: ('N', 19), 1: ('N', 6), 30: ('S', 18),
}


def _build_coloc_data(y_results, h_results):
    """Build co-located Y ↔ H comparison data.

    For each co-located pair:
      - H-plate mean degradation (across slots)
      - Y-plate same-material degradation (NdFeB grades for Hn, SmCo grades for Hs)
      - Y-plate SmCo mean (gain reference)
      - Y-plate intra-plate differential (gain-immune reference)

    Returns list of dicts.
    """
    from collections import defaultdict

    y_clean = [r for r in y_results if not r['is_outlier']]
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]

    # Y-plate per-material by plate
    y_by_plate = defaultdict(lambda: defaultdict(list))
    for r in y_clean:
        y_by_plate[r['plate']][r['material']].append(r['pct_change'])

    # H-plate mean by (prefix, plate)
    h_by_plate = defaultdict(list)
    h_region = {}
    for r in h_clean:
        ns = 'N' if r['material'] == 'NdFeB' else 'S'
        key = (ns, r['plate'])
        h_by_plate[key].append(r['pct_change'])
        h_region[key] = r.get('region', '')

    rows = []
    for y_num, (h_prefix, h_num) in COLOCATION.items():
        h_key = (h_prefix, h_num)
        h_pcts = h_by_plate.get(h_key, [])
        if not h_pcts:
            continue

        h_mat = 'NdFeB' if h_prefix == 'N' else 'SmCo'
        h_mean = np.mean(h_pcts)

        # Y same material as H
        if h_mat == 'NdFeB':
            y_same = (y_by_plate[y_num].get('N42EH', []) +
                      y_by_plate[y_num].get('N52SH', []))
        else:
            y_same = (y_by_plate[y_num].get('SmCo33H', []) +
                      y_by_plate[y_num].get('SmCo35', []))

        y_smco = (y_by_plate[y_num].get('SmCo33H', []) +
                  y_by_plate[y_num].get('SmCo35', []))
        y_ndfeb = (y_by_plate[y_num].get('N42EH', []) +
                   y_by_plate[y_num].get('N52SH', []))

        if not y_same or not y_smco or not y_ndfeb:
            continue

        y_diff = np.mean(y_ndfeb) - np.mean(y_smco)  # gain-immune

        rows.append({
            'y_plate': y_num,
            'h_plate': '%s%d' % (h_prefix, h_num),
            'h_material': h_mat,
            'h_mean': h_mean,
            'h_n': len(h_pcts),
            'y_same_mat': np.mean(y_same),
            'y_smco': np.mean(y_smco),
            'y_ndfeb': np.mean(y_ndfeb),
            'y_diff': y_diff,
            'region': h_region.get(h_key, ''),
        })

    return rows


def plot_P14_coloc_crossref(y_results, h_results, gain_syst):
    """Co-located Y ↔ H cross-reference: validate H-plate measurements.

    Left: scatter of Y same-material vs H-plate degradation at each location.
    Right: H-plate gain-corrected using co-located Y SmCo as reference.
    """
    from scipy import stats as sp_stats

    rows = _build_coloc_data(y_results, h_results)
    if not rows:
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    nd_rows = [r for r in rows if r['h_material'] == 'NdFeB']
    sm_rows = [r for r in rows if r['h_material'] == 'SmCo']

    # ─── Left: Y same-material vs H-plate degradation ───
    for rr, color, label in [(nd_rows, '#CC3333', 'NdFeB H-plate'),
                              (sm_rows, '#3366CC', 'SmCo H-plate')]:
        if not rr:
            continue
        x = [r['y_same_mat'] for r in rr]
        y = [r['h_mean'] for r in rr]
        ax1.scatter(x, y, color=color, alpha=0.7, s=50, edgecolor='black',
                    linewidth=0.5, label='%s (N=%d)' % (label, len(rr)), zorder=3)

    all_x = [r['y_same_mat'] for r in rows]
    all_y = [r['h_mean'] for r in rows]
    r_val, p_val = sp_stats.pearsonr(all_x, all_y)

    # 1:1 line
    vmin = min(min(all_x), min(all_y))
    vmax = max(max(all_x), max(all_y))
    pad = (vmax - vmin) * 0.15
    ax1.plot([vmin - pad, vmax + pad], [vmin - pad, vmax + pad],
             'k--', linewidth=1, alpha=0.4, label='1:1')
    ax1.axhline(0, color='gray', linewidth=0.5, alpha=0.5)
    ax1.axvline(0, color='gray', linewidth=0.5, alpha=0.5)

    ax1.annotate('Pearson r = %.3f (p=%.3f)\nN = %d locations' % (
        r_val, p_val, len(rows)),
        xy=(0.05, 0.95), xycoords='axes fraction', ha='left', va='top',
        fontsize=10, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                  edgecolor='orange', alpha=0.9))

    ax1.set_xlabel('Co-located Y-plate same-material % change', fontsize=11)
    ax1.set_ylabel('H-plate mean % change', fontsize=11)
    ax1.set_title('Y vs H at Same Location (Raw)', fontsize=14,
                  fontweight='bold')
    ax1.legend(fontsize=9, loc='lower right')
    ax1.grid(True, alpha=0.3)

    # ─── Right: Gain-corrected H using co-located Y SmCo ───
    # For NdFeB H-plates: (H_NdFeB - Y_SmCo) vs (Y_NdFeB - Y_SmCo)
    # Both quantities use the same Y-SmCo gain anchor
    for rr, color, label in [(nd_rows, '#CC3333', 'NdFeB'),
                              (sm_rows, '#3366CC', 'SmCo')]:
        if not rr:
            continue
        x = [r['y_same_mat'] - r['y_smco'] for r in rr]
        y = [r['h_mean'] - r['y_smco'] for r in rr]
        ax2.scatter(x, y, color=color, alpha=0.7, s=50, edgecolor='black',
                    linewidth=0.5, label='%s (N=%d)' % (label, len(rr)),
                    zorder=3)

    all_x2 = [r['y_same_mat'] - r['y_smco'] for r in rows]
    all_y2 = [r['h_mean'] - r['y_smco'] for r in rows]
    r2, p2 = sp_stats.pearsonr(all_x2, all_y2)

    vmin2 = min(min(all_x2), min(all_y2))
    vmax2 = max(max(all_x2), max(all_y2))
    pad2 = (vmax2 - vmin2) * 0.15
    ax2.plot([vmin2 - pad2, vmax2 + pad2], [vmin2 - pad2, vmax2 + pad2],
             'k--', linewidth=1, alpha=0.4, label='1:1')
    ax2.axhline(0, color='gray', linewidth=0.5, alpha=0.5)
    ax2.axvline(0, color='gray', linewidth=0.5, alpha=0.5)

    # NdFeB-only statistics for the gain-corrected values
    nd_h_corr = [r['h_mean'] - r['y_smco'] for r in nd_rows]
    nd_y_diff = [r['y_diff'] for r in nd_rows]  # Y-plate gain-immune diff
    if nd_h_corr:
        nd_corr_mean = np.mean(nd_h_corr)
        nd_corr_sem = np.std(nd_h_corr) / np.sqrt(len(nd_h_corr))
        nd_ydiff_mean = np.mean(nd_y_diff)
        r_nd, p_nd = sp_stats.pearsonr(nd_y_diff, nd_h_corr) if len(nd_h_corr) > 2 else (0, 1)

    ax2.annotate('r = %.3f (p=%.3f), N=%d\n\n'
                 'NdFeB H corrected: %+.3f%% \u00b1 %.3f%%\n'
                 'Y-plate differential: %+.3f%%\n'
                 'NdFeB-only r = %.3f (p=%.3f)' % (
                     r2, p2, len(rows),
                     nd_corr_mean, nd_corr_sem,
                     nd_ydiff_mean,
                     r_nd, p_nd),
        xy=(0.05, 0.95), xycoords='axes fraction', ha='left', va='top',
        fontsize=9, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                  edgecolor='orange', alpha=0.9))

    ax2.set_xlabel('(Y same-mat \u2212 Y SmCo) at same location', fontsize=11)
    ax2.set_ylabel('(H-plate \u2212 Y SmCo) at same location', fontsize=11)
    ax2.set_title('Gain-Corrected (Y SmCo as Reference)', fontsize=14,
                  fontweight='bold')
    ax2.legend(fontsize=9, loc='lower right')
    ax2.grid(True, alpha=0.3)

    fig.suptitle(
        'Co-located Y \u2194 H Cross-Reference\n'
        'Each point = one tunnel location (Y-plate + H-plate at same mount)',
        fontsize=14, fontweight='bold', y=1.02)
    fig.text(0.5, -0.02,
             'PRELIMINARY \u2014 LDRD FFA@CEBAF Magnet Radiation Study\n'
             'H-plate baselines are single-reading; awaiting room temp data.',
             ha='center', fontsize=9, fontstyle='italic', color='gray')
    fig.tight_layout(rect=[0, 0.01, 1, 0.95])
    save(fig, 'P14_coloc_crossref.png')


# ═══════════════════════════════════════════════════════════════════════════════
# P15: Literature Comparison — Our Result in Context
# ═══════════════════════════════════════════════════════════════════════════════

def plot_P15_literature_comparison(intra_diffs, gain_syst):
    """P15: Our result vs published dose-response data.

    Two-panel figure:
      (a) Published landscape (0-100% demagnetization, log dose axis)
      (b) Our per-plate data at sub-percent scale

    Literature values from published text (not digitized figures).
    Approximate values are sufficient for context — see Shen (2018)
    J. Nucl. Mater. 503 for comprehensive review.
    """
    import csv

    # ─── Load per-plate data from rod dosimetry CSV ───
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'Rod_Dosimetry', 'rod_dose_degradation.csv')
    plates = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            plates.append(row)

    # ─── Literature data points (doses in Gy, from published text) ───
    #
    # Simos et al. (2018) IEEE Trans. Magn. 54(2)
    #   BNL BLIP, 118 MeV proton spallation → mixed field
    #   Nd2Fe14B plate-like: >85% at 50 Mrad (500 kGy)
    #   Pr2Fe14B: >87% at 10 Mrad (100 kGy)
    #   Sm2Co17 annular: ~insensitive up to 2 Grad (20 MGy)
    #
    # APS LS-290 (Luna, 2002): 5 GeV electrons → bremsstrahlung
    #   1% threshold: 760 Gy (low Hci) to 113 kGy (high Hci)
    #   Factor of >100 variation with coercivity/geometry
    #
    # Alderman et al. (ANL): pure gamma (APS bending magnet)
    #   NdFeB null at 700 Mrad (7 MGy)
    #
    # Bizen et al. (2016) Sci. Rep. 6: 8 GeV electrons at SACLA
    #   >30% flux loss in NdFeB undulator, magnetization reversal

    # ─── Figure setup ───
    fig, (ax_lit, ax_ours) = plt.subplots(
        2, 1, figsize=(14, 13), sharex=True,
        gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.12})

    # ═══ Panel (a): Literature landscape ═══

    # APS LS-290 threshold band (1% level, varies with coercivity)
    ls290_low, ls290_high = 760, 113000  # Gy
    ax_lit.fill_between([ls290_low, ls290_high], [1.5, 1.5], [-1, -1],
                        alpha=0.18, color='#DAA520', zorder=1)
    ax_lit.plot([ls290_low, ls290_high], [1, 1], color='#B8860B',
                linewidth=2.5, solid_capstyle='round', zorder=2)
    ax_lit.annotate('APS LS-290: 1%% threshold range\n(760 Gy – 113 kGy, varies with Hci)',
                    xy=(np.sqrt(ls290_low * ls290_high), 1),
                    xytext=(0, 18), textcoords='offset points',
                    ha='center', va='bottom', fontsize=9,
                    color='#8B6914', fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='#8B6914', lw=1.5))

    # Simos (2018) — NdFeB plate-like
    ax_lit.scatter(500e3, 85, marker='D', c='#E63946', s=200,
                   edgecolor='black', linewidth=1.2, zorder=5)
    ax_lit.annotate('Simos (2018)\nNd₂Fe₁₄B plate\n>85%% at 500 kGy',
                    xy=(500e3, 85), xytext=(-60, -20),
                    textcoords='offset points', ha='right', va='top',
                    fontsize=8.5, fontweight='bold', color='#E63946')

    # Simos (2018) — Pr2Fe14B
    ax_lit.scatter(100e3, 87, marker='D', c='#FF8C42', s=200,
                   edgecolor='black', linewidth=1.2, zorder=5)
    ax_lit.annotate('Simos (2018)\nPr₂Fe₁₄B\n>87%% at 100 kGy',
                    xy=(100e3, 87), xytext=(-15, 10),
                    textcoords='offset points', ha='right', va='bottom',
                    fontsize=8.5, fontweight='bold', color='#FF8C42')

    # Simos (2018) — Sm2Co17 null
    ax_lit.scatter(20e6, 1, marker='s', c='#457B9D', s=180,
                   edgecolor='black', linewidth=1.2, zorder=5)
    ax_lit.annotate('Simos (2018) Sm₂Co₁₇\n~null at 20 MGy',
                    xy=(20e6, 1), xytext=(0, 12),
                    textcoords='offset points', ha='center', va='bottom',
                    fontsize=8.5, fontweight='bold', color='#457B9D')
    # Downward arrow for null
    ax_lit.annotate('', xy=(20e6, 0), xytext=(20e6, 1),
                    arrowprops=dict(arrowstyle='->', color='#457B9D', lw=1.5))

    # Alderman (ANL) — gamma null
    ax_lit.scatter(7e6, 1, marker='X', c='#2A9D8F', s=200,
                   edgecolor='black', linewidth=1.2, zorder=5)
    ax_lit.annotate('Alderman (ANL)\nNdFeB, γ-only\nnull at 7 MGy',
                    xy=(7e6, 1), xytext=(-15, 20),
                    textcoords='offset points', ha='right', va='bottom',
                    fontsize=8.5, fontweight='bold', color='#2A9D8F')
    ax_lit.annotate('', xy=(7e6, 0), xytext=(7e6, 1),
                    arrowprops=dict(arrowstyle='->', color='#2A9D8F', lw=1.5))

    # Bizen (2016) — SACLA undulator
    ax_lit.scatter(100e3, 30, marker='p', c='#9B59B6', s=200,
                   edgecolor='black', linewidth=1.2, zorder=5)
    ax_lit.annotate('Bizen (2016)\nSACLA NdFeB\n>30%% flux loss',
                    xy=(100e3, 30), xytext=(15, 10),
                    textcoords='offset points', ha='left', va='bottom',
                    fontsize=8.5, fontweight='bold', color='#9B59B6')

    # Our dose range — green band spanning both panels
    our_dose_min, our_dose_max = 0.3, 23451  # Gy
    ax_lit.axvspan(our_dose_min, our_dose_max, alpha=0.08, color='green',
                   zorder=0)
    ax_lit.annotate('This study\n(0.3 – 23,451 Gy)',
                    xy=(np.sqrt(our_dose_min * our_dose_max), 92),
                    fontsize=10, fontweight='bold', color='#006400',
                    ha='center', va='top',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#90EE90',
                              alpha=0.5, edgecolor='#006400'))

    # Panel (a) formatting
    ax_lit.set_xscale('log')
    ax_lit.set_xlim(0.1, 5e7)
    ax_lit.set_ylim(-3, 100)
    ax_lit.set_ylabel('Reported Demagnetization (%)', fontsize=12)
    ax_lit.set_title('(a)  Published Permanent Magnet Radiation Damage Studies',
                     fontsize=13, fontweight='bold', loc='left')
    ax_lit.axhline(0, color='gray', linewidth=0.5)
    ax_lit.grid(True, alpha=0.2, which='both')

    # Radiation type legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='D', color='w', markerfacecolor='#E63946',
               markersize=10, markeredgecolor='k', label='Proton/spallation (mixed field)'),
        Line2D([0], [0], marker='X', color='w', markerfacecolor='#2A9D8F',
               markersize=10, markeredgecolor='k', label='Gamma-only'),
        Line2D([0], [0], marker='p', color='w', markerfacecolor='#9B59B6',
               markersize=10, markeredgecolor='k', label='8 GeV electrons'),
        Line2D([0], [0], color='#B8860B', linewidth=2.5, label='1%% threshold (electrons)'),
    ]
    ax_lit.legend(handles=legend_elements, fontsize=8.5, loc='center left',
                  framealpha=0.9)

    # ═══ Panel (b): Our per-plate data ═══

    doses, ndfeb_vals, smco_vals, diff_vals = [], [], [], []
    for p in plates:
        d = float(p['ai_photon_gy'])
        if d <= 0:
            continue
        doses.append(d)
        ndfeb_vals.append(float(p['ndfeb_mean_pct']))
        smco_vals.append(float(p['smco_mean_pct']))
        diff_vals.append(float(p['intra_plate_diff']))

    doses = np.array(doses)
    ndfeb_vals = np.array(ndfeb_vals)
    smco_vals = np.array(smco_vals)
    diff_vals = np.array(diff_vals)

    # Per-plate scatter
    ax_ours.scatter(doses, ndfeb_vals, c='#CC3333', alpha=0.55, s=45,
                    edgecolor='black', linewidth=0.3, zorder=3,
                    label='NdFeB mean (per plate)')
    ax_ours.scatter(doses, smco_vals, c='#3366CC', alpha=0.55, s=45,
                    edgecolor='black', linewidth=0.3, zorder=3,
                    label='SmCo mean (per plate)')
    ax_ours.scatter(doses, diff_vals, c='black', alpha=0.7, s=65,
                    marker='D', edgecolor='black', linewidth=0.5, zorder=4,
                    label='NdFeB\u2212SmCo diff (per plate)')

    # Mean lines
    nd_mean = np.mean(ndfeb_vals)
    sm_mean = np.mean(smco_vals)

    # Use the passed-in intra_diffs for the headline (matches P1 exactly)
    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs, ddof=1) / np.sqrt(len(intra_diffs))

    ax_ours.axhline(nd_mean, color='#CC3333', linewidth=1.5, linestyle=':',
                    alpha=0.5, zorder=2)
    ax_ours.axhline(sm_mean, color='#3366CC', linewidth=1.5, linestyle=':',
                    alpha=0.5, zorder=2)
    ax_ours.axhline(diff_mean, color='black', linewidth=2, linestyle='--',
                    alpha=0.7, zorder=2, label='Ensemble differential')
    ax_ours.axhline(0, color='gray', linewidth=0.8)

    # Gain systematic band
    ax_ours.axhspan(-gain_syst, gain_syst, alpha=0.08, color='gray',
                    zorder=0, label='\u00b1%.2f%% gain syst.' % gain_syst)

    # Green band matching panel (a)
    ax_ours.axvspan(our_dose_min, our_dose_max, alpha=0.05, color='green',
                    zorder=0)

    # Headline annotation
    sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0
    ax_ours.annotate(
        'NdFeB\u2212SmCo differential:\n'
        '%+.3f%% \u00b1 %.3f%% (%.1f\u03c3)\n'
        'N = %d tunnel Y-plates' % (diff_mean, diff_sem, sig, len(intra_diffs)),
        xy=(0.02, 0.05), xycoords='axes fraction',
        fontsize=11, fontweight='bold', va='bottom',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow',
                  edgecolor='orange', alpha=0.9))

    # Key context message
    ax_ours.annotate(
        'Effect detected at doses 100\u20131000\u00d7 below\n'
        'prior studies; neutron-driven (not gamma)',
        xy=(0.98, 0.05), xycoords='axes fraction',
        fontsize=9.5, fontweight='bold', ha='right', va='bottom',
        color='#006400',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#90EE90',
                  alpha=0.4, edgecolor='#006400'))

    # Panel (b) formatting
    ax_ours.set_ylabel('% Change from Baseline', fontsize=12)
    ax_ours.set_xlabel('Gamma Dose (Gy)', fontsize=12)
    ax_ours.set_title(
        '(b)  This Study \u2014 Per-Plate Degradation vs Dose (N=%d)' % len(doses),
        fontsize=13, fontweight='bold', loc='left')
    ax_ours.set_ylim(-0.7, 0.4)
    ax_ours.grid(True, alpha=0.2, which='both')
    ax_ours.legend(fontsize=8, loc='upper right', ncol=2)

    # Suptitle
    fig.suptitle(
        'Radiation-Induced Permanent Magnet Demagnetization:\n'
        'This Study in Context of Published Results',
        fontsize=15, fontweight='bold', y=0.99)

    fig.text(0.5, -0.01,
             'PRELIMINARY \u2014 LDRD FFA@CEBAF Magnet Radiation Study\n'
             'Literature values from published text (approximate). '
             'See Shen (2018) J. Nucl. Mater. 503 for comprehensive review.',
             ha='center', fontsize=9, fontstyle='italic', color='gray')
    plt.tight_layout(rect=[0, 0.02, 1, 0.96])
    save(fig, 'P15_literature_comparison.png')


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("Presentation Plots: Preliminary Results")
    print("Output: %s" % PLOT_DIR)
    print("=" * 70)
    print()

    print("Loading data...")
    results, helm_raw, temp_final, y_materials = load_all()
    clean = [r for r in results if not r['is_outlier']]
    print("  %d samples (%d clean)" % (len(results), len(clean)))

    gain_result = get_gain_syst(helm_raw)
    gain_syst = gain_result[0] if gain_result else 0.248
    gain_syst_raw = getattr(gain_result, 'gain_syst_raw', None)
    intra_diffs, intra_details = compute_intra_plate_diffs(clean)

    print("\nKey numbers:")
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        m = np.mean(vals)
        s = np.std(vals, ddof=1) / np.sqrt(len(vals))
        print("  %s: %+.3f%% ± %.3f%% (%.1fσ, N=%d)" % (mat, m, s, abs(m/s), len(vals)))
    diff_m = np.mean(intra_diffs)
    diff_s = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    print("  Differential: %+.3f%% ± %.3f%% (%.1fσ, N=%d)" %
          (diff_m, diff_s, abs(diff_m/diff_s), len(intra_diffs)))
    print("  Gain systematic (cleaned): ±%.3f%%" % gain_syst)
    if gain_syst_raw is not None:
        print("  Gain systematic (uncleaned): ±%.3f%%" % gain_syst_raw)

    # ─── Load H-plate and A-sample data ────────────────────────────────
    print("\nLoading H-plate data...")
    y_mats, pair_arrangements = load_materials()
    temp_lookup = build_temperature_lookup()
    h_results, h_excluded = compute_h_plate_degradation(
        pair_arrangements, temp_lookup)
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]
    print("  %d H-plate pairs (%d clean)" % (len(h_results), len(h_clean)))

    print("Loading A-sample data...")
    a_results = load_a_sample_helmholtz(temp_lookup)
    a_slot = _average_a_to_slot(a_results)
    print("  %d A-sample pairs → %d H-plate slots (after slot averaging)" % (
        len([r for r in a_results if not r['is_outlier']]), len(a_slot)))

    # ─── H/A key numbers ─────────────────────────────────────────────
    for mat in ['NdFeB', 'SmCo']:
        hv = [r['pct_change'] for r in h_clean if r['material'] == mat]
        if hv:
            hm = np.mean(hv)
            hs = np.std(hv, ddof=1) / np.sqrt(len(hv))
            print("  H %s: %+.3f%% ± %.3f%% (%.1fσ, N=%d pairs)" % (
                mat, hm, hs, abs(hm / hs) if hs > 0 else 0, len(hv)))
    for mat in ['NdFeB', 'SmCo']:
        av = [r['pct_change'] for r in a_slot if r['material'] == mat]
        if av:
            am = np.mean(av)
            ae = np.std(av, ddof=1) / np.sqrt(len(av))
            print("  A %s: %+.3f%% ± %.3f%% (%.1fσ, N=%d slots)" % (
                mat, am, ae, abs(am / ae) if ae > 0 else 0, len(av)))

    print("\nGenerating plots...")
    plot_P1_material_comparison(results, gain_syst, intra_diffs,
                                gain_syst_raw=gain_syst_raw)
    plot_P2_timeseries_dual(results, gain_syst)
    plot_P3_regional(results, gain_syst)
    plot_P4_lab_controls(results, intra_diffs, intra_details)
    plot_P5_uncertainty_budget(results, gain_syst, gain_syst_raw=gain_syst_raw)
    plot_P6_tcrit_ranking(results)
    plot_P7_teslameter_summary(results)
    plot_P8_waterfall_regional(results, gain_syst)
    plot_P9_waterfall_all_materials(results, gain_syst)

    # ─── New H/A presentation plots ───────────────────────────────────
    print("\nGenerating H/A presentation plots...")
    plot_P10_h_plate_material(h_results, gain_syst,
                               gain_syst_raw=gain_syst_raw)
    plot_P11_a_sample_summary(a_results, h_results, gain_syst)
    plot_P12_combined_YHA(results, h_results, a_results, gain_syst,
                          intra_diffs)
    plot_P13_ha_lab_vs_tunnel(h_results, a_results, gain_syst)
    plot_P14_coloc_crossref(results, h_results, gain_syst)

    # ─── Literature comparison ─────────────────────────────────────────
    print("\nGenerating literature comparison plot...")
    plot_P15_literature_comparison(intra_diffs, gain_syst)

    print("\n" + "=" * 70)
    print("Done. 15 presentation plots saved to: %s/" % PLOT_DIR)
    print("=" * 70)


if __name__ == '__main__':
    main()
