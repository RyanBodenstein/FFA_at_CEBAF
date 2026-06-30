#!/usr/bin/env python3
"""
slide36_timeseries.py -- Standalone script to regenerate the P2 time series
plot with fixed date formatting for presentation use.

Fixes from original P2:
  - Proper MonthLocator + DateFormatter so month labels don't double/overlap
  - Explicit xlim on all panels to match the actual data range
  - Fixed panel (c) date grouping: group by calendar date, not datetime,
    so samples measured at different times on the same day are matched
  - Tightened y-axis on top panels to show data clearly
  - Presentation-quality fonts, sizing, and layout

Output: slide36_timeseries.png (200 dpi)
"""

import sys
import os

# Add Cleanup_Claude to path so we can import manager_summary_v3
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANUP_DIR = os.path.join(SCRIPT_DIR, '..', 'Cleanup_Claude')
sys.path.insert(0, os.path.abspath(CLEANUP_DIR))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from collections import defaultdict

from manager_summary_v3 import load_all, get_gain_syst

# ── Colors ──────────────────────────────────────────────────────────────────
PRES_COLORS = {
    'N42EH': '#CC3333', 'N52SH': '#FF6644',
    'SmCo33H': '#3366CC', 'SmCo35': '#66AADD',
}

OUTPUT = os.path.join(SCRIPT_DIR, 'slide36_timeseries.png')


def main():
    print("Loading data...")
    results, helm_raw, temp_final, y_materials = load_all()
    gain_result = get_gain_syst(helm_raw)
    gain_syst = gain_result[0] if gain_result else 0.248

    clean = [r for r in results if not r['is_outlier']]
    print("  %d samples (%d clean)" % (len(results), len(clean)))

    # ── Group date_pcts by material ─────────────────────────────────────────
    mat_series = defaultdict(lambda: defaultdict(list))
    for r in clean:
        for dt, pct in r['date_pcts']:
            mat_series[r['material']][dt].append(pct)

    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    # ── Determine actual date range across all materials ────────────────────
    all_dates = []
    for mat in materials:
        all_dates.extend(mat_series[mat].keys())
    if not all_dates:
        print("ERROR: no date_pcts data found")
        return
    date_min = min(all_dates)
    date_max = max(all_dates)
    print("  Date range: %s to %s" % (date_min.strftime('%Y-%m-%d'),
                                       date_max.strftime('%Y-%m-%d')))

    # Pad the limits slightly for readability
    xlim_all = (date_min - timedelta(days=10), date_max + timedelta(days=15))
    # Panel (b) starts Aug 1 2025
    clean_start = datetime(2025, 8, 1)
    xlim_clean = (clean_start - timedelta(days=5), date_max + timedelta(days=15))

    # ── Build figure ────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 10))
    # Do NOT use sharey so we can set independent y-limits
    ax_all = fig.add_subplot(2, 2, 1)
    ax_clean = fig.add_subplot(2, 2, 2)
    ax_diff = fig.add_subplot(2, 1, 2)

    # ── Panels (a) and (b): per-material time series ────────────────────────
    beam_off = datetime(2025, 10, 21)

    for ax, title, filter_jul17, xlim in [
        (ax_all, '(a) All Data (Jul 17 artifact flagged)', False, xlim_all),
        (ax_clean, '(b) Clean: Aug 27 onward (all 30 plates)', True, xlim_clean),
    ]:
        for mat in materials:
            dts_plot, means_plot, sems_plot = [], [], []
            for dt in sorted(mat_series[mat]):
                if filter_jul17 and dt < clean_start:
                    continue
                vals = mat_series[mat][dt]
                dts_plot.append(dt)
                means_plot.append(np.mean(vals))
                sems_plot.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                                 if len(vals) > 1 else 0.1)

            ax.errorbar(dts_plot, means_plot, yerr=sems_plot,
                        color=PRES_COLORS[mat], marker='o', markersize=5,
                        linewidth=1.8, capsize=3, label=mat, alpha=0.85)

        # Gain systematic band
        ax.axhspan(-gain_syst, gain_syst, color='gold', alpha=0.1, zorder=0)
        ax.axhline(0, color='black', linewidth=0.8)

        # Beam OFF line
        ax.axvline(beam_off, color='gray', linewidth=1.5,
                   linestyle=':', alpha=0.7)
        ax.annotate('Beam OFF',
                    xy=(beam_off, 1), xycoords=('data', 'axes fraction'),
                    textcoords='offset points', xytext=(5, -14),
                    fontsize=9, color='gray', fontstyle='italic')

        # Jul 17 artifact shading (panel a only)
        if not filter_jul17:
            ax.axvspan(datetime(2025, 7, 10), datetime(2025, 8, 1),
                       color='red', alpha=0.05, zorder=0)
            ax.annotate('Jul 17 artifact\n(~0.8% offset)',
                        (datetime(2025, 7, 17), 0),
                        textcoords='offset points', xytext=(5, 30),
                        fontsize=8, color='red', fontstyle='italic',
                        arrowprops=dict(arrowstyle='->', color='red', lw=0.8))

        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_ylabel('Flux Change from Baseline (%)', fontsize=11)
        ax.set_xlabel('Date', fontsize=11)

        # Tighten y-axis: show +/- 1.5% for clean panel, wider for all-data
        if filter_jul17:
            ax.set_ylim(-1.0, 0.8)
        else:
            ax.set_ylim(-2.5, 2.5)

        # Proper date formatting
        ax.set_xlim(xlim)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
        ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO,
                                                          interval=2))
        ax.tick_params(axis='x', labelsize=9)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc='lower left')

    # ── Panel (c): NdFeB - SmCo intra-plate differential ───────────────────
    plate_results = defaultdict(list)
    for r in clean:
        plate_results[r['plate']].append(r)

    diff_dates_dict = defaultdict(list)
    for plate_id, recs in plate_results.items():
        # Group by DATE (not datetime) so samples measured at different
        # times on the same day are matched together
        date_by_mat = defaultdict(dict)
        for r in recs:
            for dt, pct in r['date_pcts']:
                day_key = dt.date()
                date_by_mat[day_key][r['material']] = pct

        for day_key, mat_vals in date_by_mat.items():
            ndfeb_vals = [v for m, v in mat_vals.items()
                          if m in ('N42EH', 'N52SH')]
            smco_vals = [v for m, v in mat_vals.items()
                         if m in ('SmCo33H', 'SmCo35')]
            if ndfeb_vals and smco_vals:
                # Convert back to datetime for plotting
                dt_plot = datetime.combine(day_key, datetime.min.time())
                diff_dates_dict[dt_plot].append(
                    np.mean(ndfeb_vals) - np.mean(smco_vals))

    diff_dates = sorted(diff_dates_dict.keys())
    diff_means = [np.mean(diff_dates_dict[dt]) for dt in diff_dates]
    diff_sems = [np.std(diff_dates_dict[dt], ddof=1) /
                 np.sqrt(len(diff_dates_dict[dt]))
                 if len(diff_dates_dict[dt]) > 1 else 0.05
                 for dt in diff_dates]
    diff_ns = [len(diff_dates_dict[dt]) for dt in diff_dates]

    print("  Panel (c): %d date points" % len(diff_dates))
    for dt, m, s, n in zip(diff_dates, diff_means, diff_sems, diff_ns):
        print("    %s: %+.3f%% +/- %.3f%% (N=%d)" %
              (dt.strftime('%Y-%m-%d'), m, s, n))

    ax_diff.errorbar(diff_dates, diff_means, yerr=diff_sems,
                     color='#8B0000', marker='D', markersize=6,
                     linewidth=2.5, capsize=4,
                     label='NdFeB - SmCo differential', zorder=5)
    ax_diff.fill_between(diff_dates,
                         [m - e for m, e in zip(diff_means, diff_sems)],
                         [m + e for m, e in zip(diff_means, diff_sems)],
                         alpha=0.15, color='#8B0000')
    ax_diff.axhline(0, color='black', linewidth=0.8)
    ax_diff.axvline(beam_off, color='gray', linewidth=1.5,
                    linestyle=':', alpha=0.7)
    ax_diff.annotate('Beam OFF',
                     xy=(beam_off, 1), xycoords=('data', 'axes fraction'),
                     textcoords='offset points', xytext=(5, -14),
                     fontsize=9, color='gray', fontstyle='italic')

    # Annotate final value
    if diff_dates:
        final_m = diff_means[-1]
        final_s = diff_sems[-1]
        final_sig = abs(final_m / final_s) if final_s > 0 else 0
        ax_diff.annotate('%+.3f%% +/- %.3f%% (%.1f sigma)\nN=%d plates' %
                         (final_m, final_s, final_sig, diff_ns[-1]),
                         xy=(diff_dates[-1], final_m),
                         textcoords='offset points', xytext=(-150, 30),
                         fontsize=10, fontweight='bold', color='#8B0000',
                         arrowprops=dict(arrowstyle='->', color='#8B0000',
                                         lw=0.8),
                         bbox=dict(boxstyle='round,pad=0.3',
                                   facecolor='white',
                                   edgecolor='#8B0000', alpha=0.9))

    ax_diff.annotate('Gain-immune: cancels intra-plate',
                     xy=(0.01, 0.93), xycoords='axes fraction',
                     fontsize=9, fontstyle='italic', color='green')

    ax_diff.set_title('(c) NdFeB - SmCo Intra-Plate Differential '
                      '(Gain-Immune)',
                      fontsize=12, fontweight='bold')
    ax_diff.set_ylabel('Differential (%)', fontsize=11)
    ax_diff.set_xlabel('Date', fontsize=11)
    ax_diff.set_ylim(-0.55, 0.15)

    # Proper date formatting for panel (c)
    ax_diff.set_xlim(xlim_all)
    ax_diff.xaxis.set_major_locator(mdates.MonthLocator())
    ax_diff.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax_diff.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO,
                                                           interval=2))
    ax_diff.tick_params(axis='x', labelsize=9)
    ax_diff.grid(alpha=0.3)
    ax_diff.legend(fontsize=9, loc='lower left')

    # ── Suptitle and footer ─────────────────────────────────────────────
    fig.suptitle('Temperature-Corrected Helmholtz Flux Change Over Time',
                 fontsize=14, fontweight='bold', y=0.99)
    fig.text(0.5, 0.005, 'PRELIMINARY -- LDRD FFA@CEBAF Magnet Radiation Study',
             ha='center', fontsize=10, fontstyle='italic', color='gray')
    fig.text(0.99, 0.005, 'Error bars: +/-1 SEM',
             ha='right', fontsize=8, fontstyle='italic', color='gray')

    plt.tight_layout(rect=[0, 0.02, 1, 0.97])
    fig.savefig(OUTPUT, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("\nSaved: %s" % OUTPUT)


if __name__ == '__main__':
    main()
