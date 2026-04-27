#!/usr/bin/env python3
"""
time_series_evolution.py — Task 9: Time Series Degradation Evolution

Shows how magnet degradation evolves over the 8 tunnel measurement sessions
(Jul 2025 – Jan 2026), across all sample types (Y-plate, H-plate, A-sample).

Outputs (Time_Series/ subdirectory):
  T1: Ensemble mean degradation vs time (all sample types + differential)
  T2: Individual sample trajectories (spaghetti plot, by region)
  T3: Degradation vs cumulative dose (time-resolved)
  T4: Regional time evolution (NdFeB only)
  T5: Cumulative dose vs time by region (all plate types)
  T6: Dual-axis: NdFeB degradation + cumulative dose vs time by region
  T7: Per-plate dose timeline with Helmholtz measurement dates marked
  summary_table.txt: per-session statistics, dose at each date, linear fit slopes
"""

import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict
from scipy import stats

from manager_summary_v3 import (
    load_all, get_gain_syst, compute_intra_plate_diffs,
    MAT_COLORS, FLAGGED, PLACEMENTS, REGION_ORDER, REGION_COLORS,
)
from degradation_summary_v2 import (
    PLACEMENTS as V2_PLACEMENTS, Y_PLACEMENT, H_PLACEMENT,
    load_materials, build_temperature_lookup, compute_h_plate_degradation,
)
from manager_summary_v5_polish import load_a_sample_helmholtz
from dose_degradation_correlation import load_dose_timeline, MREM_TO_SV, MREM_TO_GY_PHOTON

BASE = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.join(BASE, 'Time_Series')
os.makedirs(PLOT_DIR, exist_ok=True)

# Beam-off date: last beam delivery was Sep 3, 2025
BEAM_OFF = datetime(2025, 9, 3)

# NdFeB materials
NDFEB_MATS = {'N42EH', 'N52SH', 'NdFeB'}
SMCO_MATS = {'SmCo33H', 'SmCo35', 'SmCo'}

# Presentation colors
PRES_COLORS = {
    'N42EH': '#CC3333', 'N52SH': '#FF6644',
    'SmCo33H': '#3366CC', 'SmCo35': '#66AADD',
    'NdFeB': '#CC3333', 'SmCo': '#3366CC',
}

REGION_GROUPS = {
    'Arc': ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc'],
    'North Linac': ['North Linac'],
    'South Linac': ['South Linac'],
    'Labyrinth': ['Labyrinth'],
}
REGION_GROUP_COLORS = {
    'Arc': '#CC4444',
    'North Linac': '#4444CC',
    'South Linac': '#6666DD',
    'Labyrinth': '#888888',
}


def save(fig, name):
    path = os.path.join(PLOT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("  Saved: %s" % path)


def classify_ndfeb_smco(material):
    """Classify material as 'NdFeB' or 'SmCo' or None."""
    if material in NDFEB_MATS:
        return 'NdFeB'
    if material in SMCO_MATS:
        return 'SmCo'
    return None


def get_region_group(region):
    """Map detailed region to group (Arc, North Linac, South Linac, Labyrinth)."""
    for group, regions in REGION_GROUPS.items():
        if region in regions:
            return group
    return 'Unknown'


def short_location(pl):
    """Build a short descriptive location label from placement dict.

    Examples: 'SE Arc L2', 'N.Linac Gir.23', 'N.Labyrinth'
    """
    region = pl.get('region', '')
    line = pl.get('line', 0)
    subloc = pl.get('sub_location', '')

    if 'Arc' in region:
        # Arc plates have line numbers 1-5 (beam pass)
        if line and line > 0:
            return '%s L%d' % (region, line)
        return region

    if 'Linac' in region:
        # Extract girder number from sub_location like "NL NDX @ Girder 23"
        import re as _re
        gm = _re.search(r'Girder\s+(\d+)', subloc)
        if gm:
            short_r = 'N.Lin' if 'North' in region else 'S.Lin'
            return '%s Gir.%s' % (short_r, gm.group(1))
        # Special case: crossover
        if 'Crossover' in subloc or '0L05' in subloc:
            return 'N.Lin Crossover'
        return region.replace('North', 'N.').replace('South', 'S.') + ' Linac'

    if 'Labyrinth' in region or 'labyrinth' in subloc.lower():
        if 'North' in subloc:
            return 'N. Labyrinth'
        if 'South' in subloc:
            return 'S. Labyrinth'
        return 'Labyrinth'

    return region


def interpolate_plates_to_common_dates(plate_traces):
    """Interpolate per-plate cumulative dose to a common set of all dates.

    plate_traces: list of tuples; uses elements [1]=rg, [2]=dates, [3]=cum_gy.
    Returns: region -> dict of date -> [interpolated cum_gy values across plates]
    Only uses forward-fill (cumulative dose is monotonically non-decreasing).
    """
    # Collect all dates across all plates
    all_dates = set()
    for t in plate_traces:
        for d in t[2]:  # dates
            all_dates.add(d)
    all_dates = sorted(all_dates)

    if not all_dates:
        return {}

    # Interpolate each plate to all dates (step function: carry forward last known value)
    region_interp = defaultdict(lambda: defaultdict(list))
    for t in plate_traces:
        plate_label, rg, dates, cum_gy = t[0], t[1], t[2], t[3]
        if not dates:
            continue
        date_ords = [d.toordinal() for d in dates]
        for target_dt in all_dates:
            t_ord = target_dt.toordinal()
            if t_ord < date_ords[0]:
                # Before first measurement: dose = 0
                region_interp[rg][target_dt].append(0.0)
            elif t_ord >= date_ords[-1]:
                # After last measurement: carry forward final value
                region_interp[rg][target_dt].append(cum_gy[-1])
            else:
                # Step interpolation: use last known value ≤ target date
                # (cumulative dose only increases at collection dates)
                idx = np.searchsorted(date_ords, t_ord, side='right') - 1
                region_interp[rg][target_dt].append(cum_gy[idx])

    return region_interp


# ═════════════════════════════════════════════════════════════════════════════
# Data Aggregation
# ═════════════════════════════════════════════════════════════════════════════

def normalize_date(dt):
    """Strip time from datetime → midnight of that day. Groups by calendar date."""
    if isinstance(dt, datetime):
        return datetime(dt.year, dt.month, dt.day)
    return dt


def normalize_date_pcts(date_pcts):
    """Normalize date_pcts list to use date-only keys."""
    return [(normalize_date(dt), pct) for dt, pct in date_pcts]


def collect_time_series(y_results, h_results, a_results, gain_syst):
    """Collect per-date mean ± SEM for each sample type and material class.

    Returns dict of series_label -> list of (date, mean, sem, n).
    Also returns the raw per-sample trajectories.
    """
    # Organize by (source, material_class) -> date -> list of pct values
    buckets = defaultdict(lambda: defaultdict(list))
    trajectories = defaultdict(list)  # (source, material_class) -> [(sample, [(date, pct)])]

    # Y-plates (from v3 load_all — has date_pcts)
    for r in y_results:
        if r['is_outlier']:
            continue
        mat = r['material']
        cls = classify_ndfeb_smco(mat)
        if cls is None:
            continue
        dp = normalize_date_pcts(r.get('date_pcts', []))
        for dt, pct in dp:
            buckets[('Y', cls)][dt].append(pct)
        trajectories[('Y', cls)].append((r['sample'], r.get('region', ''), dp))

    # H-plates (from v2 — now has date_pcts)
    for r in h_results:
        if r.get('is_outlier', False):
            continue
        mat = r['material']
        cls = classify_ndfeb_smco(mat)
        if cls is None:
            continue
        dp = normalize_date_pcts(r.get('date_pcts', []))
        for dt, pct in dp:
            buckets[('H', cls)][dt].append(pct)
        trajectories[('H', cls)].append((r['sample'], r.get('region', ''), dp))

    # A-samples: average at slot level first (2 A-samples per slot)
    a_slot_data = defaultdict(lambda: defaultdict(list))  # (plate, slot, cls) -> date -> [pct]
    for r in a_results:
        if r.get('is_outlier', False):
            continue
        cls = classify_ndfeb_smco(r['material'])
        if cls is None:
            continue
        key = (r['plate'], r['pair_slot'], cls)
        for dt, pct in normalize_date_pcts(r.get('date_pcts', [])):
            a_slot_data[key][dt].append(pct)

    # Average within each slot, then treat as one sample
    for (plate, slot, cls), date_vals in a_slot_data.items():
        for dt, vals in date_vals.items():
            avg = np.mean(vals)
            buckets[('A', cls)][dt].append(avg)

    # Build ensemble series
    series = {}
    for key, date_dict in buckets.items():
        source, cls = key
        label = '%s %s' % (source, cls)
        points = []
        for dt in sorted(date_dict.keys()):
            vals = np.array(date_dict[dt])
            points.append((dt, np.mean(vals), np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.0, len(vals)))
        series[label] = points

    # Y-plate NdFeB−SmCo differential (gain-immune) per date
    y_nd_date = defaultdict(list)
    y_sm_date = defaultdict(list)
    for r in y_results:
        if r['is_outlier']:
            continue
        cls = classify_ndfeb_smco(r['material'])
        for dt, pct in normalize_date_pcts(r.get('date_pcts', [])):
            if cls == 'NdFeB':
                y_nd_date[dt].append((r['plate'], pct))
            elif cls == 'SmCo':
                y_sm_date[dt].append((r['plate'], pct))

    # Compute per-plate differential at each date
    diff_series = []
    for dt in sorted(set(y_nd_date.keys()) & set(y_sm_date.keys())):
        # Average NdFeB per plate, average SmCo per plate, then diff
        nd_by_p = defaultdict(list)
        sm_by_p = defaultdict(list)
        for p, v in y_nd_date[dt]:
            nd_by_p[p].append(v)
        for p, v in y_sm_date[dt]:
            sm_by_p[p].append(v)
        diffs = []
        for p in set(nd_by_p.keys()) & set(sm_by_p.keys()):
            diffs.append(np.mean(nd_by_p[p]) - np.mean(sm_by_p[p]))
        if diffs:
            diff_series.append((dt, np.mean(diffs),
                                np.std(diffs, ddof=1) / np.sqrt(len(diffs)) if len(diffs) > 1 else 0.0,
                                len(diffs)))
    series['Y NdFeB−SmCo diff'] = diff_series

    return series, trajectories, gain_syst


def interpolate_dose(dose_timeline, target_dates):
    """Interpolate cumulative dose to target dates for each plate.

    dose_timeline: dict plate_label -> list of {date, cum_body, ...}
    target_dates: list of datetime objects

    Returns dict plate_label -> list of (target_date, interpolated_cum_dose).
    """
    result = {}
    for plate, entries in dose_timeline.items():
        if not entries:
            continue
        # Sort by date
        sorted_entries = sorted(entries, key=lambda x: x['date'])
        dose_dates = [e['date'] for e in sorted_entries]
        dose_vals = [e['cum_body'] for e in sorted_entries]

        # Convert to ordinal for interpolation
        date_ords = [d.toordinal() for d in dose_dates]
        target_ords = [d.toordinal() for d in target_dates]

        interp_vals = []
        for t_ord, t_dt in zip(target_ords, target_dates):
            if t_ord <= date_ords[0]:
                # Before first dose measurement: extrapolate from 0
                interp_vals.append((t_dt, 0.0))
            elif t_ord >= date_ords[-1]:
                interp_vals.append((t_dt, dose_vals[-1]))
            else:
                # Linear interpolation
                val = np.interp(t_ord, date_ords, dose_vals)
                interp_vals.append((t_dt, val))

        result[plate] = interp_vals
    return result


# ═════════════════════════════════════════════════════════════════════════════
# T1: Ensemble Mean Degradation vs Time
# ═════════════════════════════════════════════════════════════════════════════

def plot_t1(series, gain_syst):
    """Ensemble mean ± SEM for all sample types + NdFeB−SmCo differential.

    Two panels: (a) full view with all series, (b) zoomed Y-plate view
    excluding Jul 17 artifact to show the real signal at readable scale.
    """
    fig, (ax_full, ax_zoom) = plt.subplots(2, 1, figsize=(12, 11),
                                            gridspec_kw={'height_ratios': [1, 1]})

    # Define line styles for each series
    styles = {
        'Y NdFeB':   dict(color='#CC3333', marker='o', ls='-', lw=2, label='Y-plate NdFeB'),
        'Y SmCo':    dict(color='#3366CC', marker='o', ls='-', lw=2, label='Y-plate SmCo'),
        'H NdFeB':   dict(color='#CC3333', marker='s', ls='--', lw=1.5, label='H-plate NdFeB'),
        'H SmCo':    dict(color='#3366CC', marker='s', ls='--', lw=1.5, label='H-plate SmCo'),
        'A NdFeB':   dict(color='#CC3333', marker='^', ls=':', lw=1.5, label='A-sample NdFeB (slot avg)'),
        'A SmCo':    dict(color='#3366CC', marker='^', ls=':', lw=1.5, label='A-sample SmCo (slot avg)'),
        'Y NdFeB\u2212SmCo diff': dict(color='#222222', marker='D', ls='--', lw=2.5, label='Y NdFeB\u2212SmCo diff (gain-immune)'),
    }

    # --- Panel (a): Full view, all series ---
    all_keys = ['Y NdFeB', 'Y SmCo', 'H NdFeB', 'H SmCo', 'A NdFeB', 'A SmCo', 'Y NdFeB\u2212SmCo diff']
    for key in all_keys:
        if key not in series or not series[key]:
            continue
        pts = series[key]
        dates = [p[0] for p in pts]
        means = [p[1] for p in pts]
        sems = [p[2] for p in pts]
        s = styles.get(key, dict(color='gray', marker='.', ls='-', lw=1, label=key))

        ax_full.plot(dates, means, **{k: v for k, v in s.items() if k != 'label'},
                     markersize=6, zorder=5)
        ax_full.fill_between(dates,
                              [m - e for m, e in zip(means, sems)],
                              [m + e for m, e in zip(means, sems)],
                              alpha=0.15, color=s['color'])
        ax_full.plot([], [], label=s['label'], color=s['color'], marker=s['marker'],
                     ls=s['ls'], lw=s['lw'])

    ax_full.axvline(BEAM_OFF, color='gray', linewidth=1, linestyle=':')
    ax_full.annotate('Beam OFF\n(Sep 3)', xy=(BEAM_OFF, 1.0), xycoords=('data', 'axes fraction'),
                     xytext=(10, -15), textcoords='offset points',
                     fontsize=8, color='gray', va='top')
    ax_full.axhspan(-gain_syst, gain_syst, color='orange', alpha=0.07, zorder=0)
    ax_full.text(0.01, 0.02, '\u00b1%.2f%% gain syst.' % gain_syst,
                 transform=ax_full.transAxes, fontsize=8, color='orange', alpha=0.7)
    ax_full.axhline(0, color='gray', linewidth=0.5, linestyle='-')
    ax_full.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax_full.xaxis.set_major_locator(mdates.MonthLocator())
    ax_full.set_ylabel('Mean Degradation (%)')
    ax_full.set_title('(a) All Sample Types — Full Range', fontsize=11, fontweight='bold')
    ax_full.legend(loc='lower left', fontsize=7, framealpha=0.9, ncol=2)
    ax_full.grid(True, alpha=0.3)

    # Flag Jul 17 artifact region
    ax_full.axvspan(datetime(2025, 7, 10), datetime(2025, 8, 1),
                    color='red', alpha=0.05, zorder=0)
    ax_full.annotate('Jul 17 artifact\n(~0.8% offset)',
                     xy=(datetime(2025, 7, 17), 0), xycoords='data',
                     textcoords='offset points', xytext=(5, 20),
                     fontsize=7, color='red', fontstyle='italic',
                     arrowprops=dict(arrowstyle='->', color='red', lw=0.8))

    # --- Panel (b): Zoomed Y-plate view, excluding Jul 17 artifact ---
    jul17_start = datetime(2025, 7, 10)
    jul17_end = datetime(2025, 8, 1)
    zoom_keys = ['Y NdFeB', 'Y SmCo', 'Y NdFeB\u2212SmCo diff']
    for key in zoom_keys:
        if key not in series or not series[key]:
            continue
        pts = series[key]
        # Exclude Jul 17 artifact window
        filtered = [p for p in pts
                    if not (jul17_start <= p[0] <= jul17_end)]
        if not filtered:
            continue
        dates = [p[0] for p in filtered]
        means = [p[1] for p in filtered]
        sems = [p[2] for p in filtered]
        s = styles[key]

        ax_zoom.plot(dates, means, **{k: v for k, v in s.items() if k != 'label'},
                     markersize=7, zorder=5)
        ax_zoom.fill_between(dates,
                              [m - e for m, e in zip(means, sems)],
                              [m + e for m, e in zip(means, sems)],
                              alpha=0.2, color=s['color'])
        ax_zoom.plot([], [], label=s['label'], color=s['color'], marker=s['marker'],
                     ls=s['ls'], lw=s['lw'])

    ax_zoom.axvline(BEAM_OFF, color='gray', linewidth=1, linestyle=':')
    ax_zoom.annotate('Beam OFF', xy=(BEAM_OFF, 1.0), xycoords=('data', 'axes fraction'),
                     xytext=(10, -15), textcoords='offset points',
                     fontsize=8, color='gray', va='top')
    ax_zoom.axhline(0, color='gray', linewidth=0.5, linestyle='-')
    ax_zoom.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax_zoom.xaxis.set_major_locator(mdates.MonthLocator())
    ax_zoom.set_xlabel('Measurement Date')
    ax_zoom.set_ylabel('Mean Degradation (%)')
    ax_zoom.set_title('(b) Y-Plate Zoomed — Jul 17 Artifact Excluded',
                       fontsize=11, fontweight='bold')
    ax_zoom.legend(loc='lower left', fontsize=8, framealpha=0.9)
    ax_zoom.grid(True, alpha=0.3)
    ax_zoom.set_ylim(-0.55, 0.15)

    # Annotate the differential value
    diff_key = 'Y NdFeB\u2212SmCo diff'
    if diff_key in series and series[diff_key]:
        last_pt = series[diff_key][-1]
        ax_zoom.annotate('Final diff: %.3f%%' % last_pt[1],
                         xy=(last_pt[0], last_pt[1]),
                         textcoords='offset points', xytext=(10, 10),
                         fontsize=9, fontweight='bold', color='#222222',
                         arrowprops=dict(arrowstyle='->', color='#222222', lw=0.8))

    fig.suptitle('T1: Ensemble Mean Degradation vs Time', fontsize=13, fontweight='bold')
    fig.text(0.99, 0.01, 'Shaded bands: \u00b11 SEM',
             ha='right', va='bottom', fontsize=7, fontstyle='italic', color='gray')
    fig.tight_layout(rect=[0, 0.02, 1, 0.97])
    save(fig, 'T1_ensemble_mean_vs_time.png')


# ═════════════════════════════════════════════════════════════════════════════
# T2: Individual Sample Trajectories (Spaghetti Plot)
# ═════════════════════════════════════════════════════════════════════════════

def plot_t2(trajectories, series):
    """Spaghetti plot: individual Y-plate trajectories, 2-panel NdFeB vs SmCo."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    for cls, ax, title in [('NdFeB', ax1, 'NdFeB (N42EH + N52SH)'),
                            ('SmCo', ax2, 'SmCo (33H + 35)')]:
        trajs = trajectories.get(('Y', cls), [])
        for sample, region, date_pcts in trajs:
            if not date_pcts:
                continue
            date_pcts_sorted = sorted(date_pcts)
            dates = [dp[0] for dp in date_pcts_sorted]
            pcts = [dp[1] for dp in date_pcts_sorted]
            rg = get_region_group(region)
            color = REGION_GROUP_COLORS.get(rg, '#999999')
            ax.plot(dates, pcts, color=color, alpha=0.3, linewidth=0.8, zorder=2)

        # Ensemble mean (bold)
        key = 'Y %s' % cls
        if key in series and series[key]:
            pts = series[key]
            ax.plot([p[0] for p in pts], [p[1] for p in pts],
                    color='black', linewidth=2.5, marker='o', markersize=5, zorder=10,
                    label='Ensemble mean')

        # Beam-off
        ax.axvline(BEAM_OFF, color='gray', linewidth=1, linestyle=':')
        ax.axhline(0, color='gray', linewidth=0.5)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        if cls == 'NdFeB':
            ax.set_ylabel('Degradation (%)')

    # Region legend
    handles = []
    for rg, color in REGION_GROUP_COLORS.items():
        handles.append(plt.Line2D([0], [0], color=color, alpha=0.5, lw=1.5, label=rg))
    handles.append(plt.Line2D([0], [0], color='black', lw=2.5, label='Ensemble mean'))
    ax2.legend(handles=handles, loc='lower left', fontsize=8, framealpha=0.9)

    fig.suptitle('T2: Individual Y-Plate Trajectories by Region', fontsize=13, y=1.01)
    fig.tight_layout()
    save(fig, 'T2_spaghetti_trajectories.png')


# ═════════════════════════════════════════════════════════════════════════════
# T3: Degradation vs Cumulative Dose (Time-Resolved)
# ═════════════════════════════════════════════════════════════════════════════

def plot_t3(y_results, dose_timeline):
    """Degradation vs cumulative dose at each measurement date."""
    # Collect all measurement dates from Y-plates (normalized to calendar day)
    all_dates = set()
    for r in y_results:
        if r['is_outlier']:
            continue
        for dt, pct in r.get('date_pcts', []):
            all_dates.add(normalize_date(dt))
    all_dates = sorted(all_dates)

    if not all_dates or not dose_timeline:
        print("  T3: No overlapping dose+degradation data, skipping.")
        return

    # Interpolate dose to measurement dates
    interp = interpolate_dose(dose_timeline, all_dates)

    # Build dose lookup: plate_num -> date -> cum_dose
    plate_dose = {}
    for plate_label, entries in interp.items():
        # plate_label like 'Y-3'
        if not plate_label.startswith('Y-'):
            continue
        try:
            pnum = int(plate_label.replace('Y-', ''))
        except ValueError:
            continue
        plate_dose[pnum] = {dt: dose for dt, dose in entries}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Color by date
    cmap = plt.cm.viridis
    date_norm = plt.Normalize(vmin=min(all_dates).toordinal(),
                               vmax=max(all_dates).toordinal())

    for cls, ax, title in [('NdFeB', ax1, 'NdFeB'), ('SmCo', ax2, 'SmCo')]:
        for r in y_results:
            if r['is_outlier']:
                continue
            if classify_ndfeb_smco(r['material']) != cls:
                continue
            pnum = r['plate']
            if pnum not in plate_dose:
                continue
            for dt, pct in normalize_date_pcts(r.get('date_pcts', [])):
                dose = plate_dose[pnum].get(dt)
                if dose is None or dose <= 0:
                    continue
                dose_sv = dose * 1e-5  # mrem → Sv
                color = cmap(date_norm(dt.toordinal()))
                ax.scatter(dose_sv, pct, color=color, s=20, alpha=0.6, edgecolor='none', zorder=3)

        ax.axhline(0, color='gray', linewidth=0.5)
        ax.set_xlabel('Cumulative Photon+Neutron Dose (Sv)')
        ax.set_ylabel('Degradation (%)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

    # Colorbar for date
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=date_norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=[ax1, ax2], pad=0.02, shrink=0.8)
    cbar.ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: datetime.fromordinal(int(x)).strftime('%b %y')))
    cbar.set_label('Measurement Date')

    fig.suptitle('T3: Degradation vs Cumulative Dose (Time-Resolved)', fontsize=13, y=1.01)
    fig.subplots_adjust(right=0.88)
    save(fig, 'T3_degradation_vs_dose_timeresolved.png')


# ═════════════════════════════════════════════════════════════════════════════
# T4: Regional Time Evolution (NdFeB only)
# ═════════════════════════════════════════════════════════════════════════════

def plot_t4(trajectories, series):
    """NdFeB degradation by region over time."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Collect NdFeB Y-plate trajectories by region group
    region_date_vals = defaultdict(lambda: defaultdict(list))
    trajs = trajectories.get(('Y', 'NdFeB'), [])
    for sample, region, date_pcts in trajs:
        rg = get_region_group(region)
        for dt, pct in date_pcts:
            region_date_vals[rg][dt].append(pct)

    for rg in ['Arc', 'North Linac', 'South Linac', 'Labyrinth']:
        if rg not in region_date_vals:
            continue
        dates_sorted = sorted(region_date_vals[rg].keys())
        means = []
        sems = []
        for dt in dates_sorted:
            vals = np.array(region_date_vals[rg][dt])
            means.append(np.mean(vals))
            sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.0)

        color = REGION_GROUP_COLORS[rg]
        ax.plot(dates_sorted, means, color=color, marker='o', lw=2, label='%s (N=%d)' % (rg, len(region_date_vals[rg][dates_sorted[0]])))
        ax.fill_between(dates_sorted,
                         [m - e for m, e in zip(means, sems)],
                         [m + e for m, e in zip(means, sems)],
                         alpha=0.15, color=color)

    # Ensemble mean
    key = 'Y NdFeB'
    if key in series and series[key]:
        pts = series[key]
        ax.plot([p[0] for p in pts], [p[1] for p in pts],
                color='black', linewidth=2.5, ls='--', marker='D', markersize=4,
                label='All NdFeB mean', zorder=10)

    ax.axvline(BEAM_OFF, color='gray', linewidth=1, linestyle=':')
    ax.annotate('Beam OFF', xy=(BEAM_OFF, 1.0), xycoords=('data', 'axes fraction'),
                xytext=(10, -15), textcoords='offset points', fontsize=8, color='gray', va='top')
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.set_xlabel('Measurement Date')
    ax.set_ylabel('NdFeB Mean Degradation (%)')
    ax.set_title('T4: Regional Time Evolution — NdFeB Y-Plates')
    ax.legend(loc='lower left', fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.annotate('Shaded bands: \u00b11 SEM', xy=(0.99, 0.01),
                xycoords='axes fraction', ha='right', va='bottom',
                fontsize=7, fontstyle='italic', color='gray')
    fig.tight_layout()
    save(fig, 'T4_regional_time_evolution.png')


# ═════════════════════════════════════════════════════════════════════════════
# T5: Cumulative Dose vs Time by Region
# ═════════════════════════════════════════════════════════════════════════════

def load_dose_timeline_full():
    """Load full dose timeline with all radiation types, keyed by plate label.

    Returns dict plate_label -> list of {date, cum_body, cum_photon, cum_neutron,
        cum_beta, cum_nf, cum_nt, status, is_lower_bound}.
    """
    path = os.path.join(BASE, 'Dosimetry', 'OSL_Area', 'plate_dose_timeline.csv')
    timeline = defaultdict(list)
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            plate = row['plate'].strip()
            date = datetime.strptime(row['collection_date'].strip(), '%Y-%m-%d')
            timeline[plate].append({
                'date': date,
                'cum_body': float(row['cum_body_mrem']),
                'cum_photon': float(row['cum_photon_mrem']),
                'cum_neutron': float(row['cum_neutron_mrem']),
                'cum_nf': float(row['cum_nf_mrem']),
                'cum_nt': float(row['cum_nt_mrem']),
                'cum_beta': float(row['cum_beta_mrem']),
                'this_body': float(row['this_body_mrem']),
                'status': row['this_dose_status'].strip(),
                'is_lower_bound': row['is_lower_bound'].strip() == 'True',
            })
    for plate in timeline:
        timeline[plate].sort(key=lambda x: x['date'])
    return dict(timeline)


def _collect_plate_traces(dose_full, prefix):
    """Collect plate traces for a given prefix (Y-, Hn-, Hs-).

    Returns list of (plate_label, rg, dates, cum_gy, is_lb, pl).
    """
    traces = []
    for plate_label, entries in dose_full.items():
        if not plate_label.startswith(prefix):
            continue
        try:
            pnum = int(plate_label.replace(prefix, '').split('-')[0])
        except ValueError:
            continue

        if prefix == 'Y-':
            pl = Y_PLACEMENT.get(pnum)
        elif prefix == 'Hn-':
            pl = H_PLACEMENT.get('N%d' % pnum)
        elif prefix == 'Hs-':
            pl = H_PLACEMENT.get('S%d' % pnum)
        else:
            pl = None

        if not pl:
            continue
        rg = get_region_group(pl['region'])

        dates = [e['date'] for e in entries]
        cum_gy = [e['cum_body'] * MREM_TO_GY_PHOTON for e in entries]
        is_lb = entries[-1].get('is_lower_bound', False)
        traces.append((plate_label, rg, dates, cum_gy, is_lb, pl))
    return traces


def plot_t5(dose_full):
    """Cumulative dose vs time by region — Y-plates, Hn-plates, Hs-plates.

    Uses step-interpolation to a common date grid before averaging, so the
    regional mean is monotonically non-decreasing.
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=False)

    plate_groups = [
        ('Y-plates', 'Y-', axes[0]),
        ('Hn-plates (NdFeB)', 'Hn-', axes[1]),
        ('Hs-plates (SmCo)', 'Hs-', axes[2]),
    ]

    for title, prefix, ax in plate_groups:
        traces = _collect_plate_traces(dose_full, prefix)

        # Plot individual plate traces (thin lines)
        # Track which regions have any saturated plates
        region_has_sat = defaultdict(bool)
        for plate_label, rg, dates, cum_gy, is_lb, pl in traces:
            color = REGION_GROUP_COLORS.get(rg, '#999999')
            ax.plot(dates, cum_gy, color=color, alpha=0.3, linewidth=0.8)
            if is_lb:
                region_has_sat[rg] = True
                # Mark saturation point with a triangle
                ax.plot(dates[-1], cum_gy[-1], marker='^', color=color,
                        markersize=5, alpha=0.6, zorder=4)

        # Interpolate to common dates, then plot monotonic regional means
        region_interp = interpolate_plates_to_common_dates(traces)
        for rg in ['Arc', 'North Linac', 'South Linac', 'Labyrinth']:
            if rg not in region_interp:
                continue
            dates_sorted = sorted(region_interp[rg].keys())
            means = [np.mean(region_interp[rg][d]) for d in dates_sorted]
            color = REGION_GROUP_COLORS[rg]
            sat_note = ' *' if region_has_sat.get(rg) else ''
            ax.plot(dates_sorted, means, color=color, lw=2.5, marker='o', markersize=3,
                    label='%s%s' % (rg, sat_note), zorder=5)

        # Mark beam-off
        ax.axvline(BEAM_OFF, color='gray', linewidth=1, linestyle=':')
        ax.annotate('Beam\nOFF', xy=(BEAM_OFF, 0.95), xycoords=('data', 'axes fraction'),
                    fontsize=7, color='gray', va='top', ha='right')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.set_ylabel('Cumulative Dose (Gy)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        leg = ax.legend(loc='upper left', fontsize=7, framealpha=0.9)
        # Add footnote for saturation
        if any(region_has_sat.values()):
            ax.text(0.02, 0.02, '* includes saturated badges (lower bounds)\n'
                    '▲ = saturated endpoint',
                    transform=ax.transAxes, fontsize=6, color='#666666', va='bottom')

    fig.suptitle('T5: Cumulative Dose Accumulation vs Time by Region', fontsize=13)
    fig.tight_layout()
    save(fig, 'T5_dose_accumulation_by_region.png')


# ═════════════════════════════════════════════════════════════════════════════
# T6: Dual-Axis — NdFeB Degradation + Dose vs Time by Region
# ═════════════════════════════════════════════════════════════════════════════

def plot_t6(trajectories, series, dose_full):
    """Dual-axis: NdFeB degradation (left) + cumulative Y-plate dose (right) vs time.

    Uses step-interpolation for dose so the mean is monotonically non-decreasing.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Collect NdFeB Y-plate trajectories by region group
    region_date_vals = defaultdict(lambda: defaultdict(list))
    trajs = trajectories.get(('Y', 'NdFeB'), [])
    for sample, region, date_pcts in trajs:
        rg = get_region_group(region)
        for dt, pct in date_pcts:
            region_date_vals[rg][dt].append(pct)

    # Collect Y-plate dose traces and interpolate
    y_traces = _collect_plate_traces(dose_full, 'Y-')
    region_interp = interpolate_plates_to_common_dates(y_traces)

    # Track saturation per region
    region_has_sat = defaultdict(bool)
    for _, rg, _, _, is_lb, _ in y_traces:
        if is_lb:
            region_has_sat[rg] = True

    for idx, rg in enumerate(['Arc', 'North Linac', 'South Linac', 'Labyrinth']):
        ax = axes[idx // 2][idx % 2]
        color_deg = REGION_GROUP_COLORS[rg]

        # Left axis: degradation
        dates_sorted = []
        n_plates = 0
        if rg in region_date_vals:
            dates_sorted = sorted(region_date_vals[rg].keys())
            means = [np.mean(region_date_vals[rg][d]) for d in dates_sorted]
            sems = [np.std(region_date_vals[rg][d], ddof=1) / np.sqrt(len(region_date_vals[rg][d]))
                    if len(region_date_vals[rg][d]) > 1 else 0.0 for d in dates_sorted]
            n_plates = len(region_date_vals[rg][dates_sorted[0]])
            ax.plot(dates_sorted, means, color=color_deg, marker='o', lw=2,
                    label='NdFeB degrad.', zorder=5)
            ax.fill_between(dates_sorted,
                            [m - e for m, e in zip(means, sems)],
                            [m + e for m, e in zip(means, sems)],
                            alpha=0.15, color=color_deg)

        ax.axhline(0, color='gray', linewidth=0.5)
        ax.axvline(BEAM_OFF, color='gray', linewidth=1, linestyle=':')
        ax.set_ylabel('NdFeB Degradation (%)', color=color_deg)
        ax.tick_params(axis='y', labelcolor=color_deg)

        # Right axis: cumulative dose (interpolated)
        ax2 = ax.twinx()
        if rg in region_interp:
            dose_dates = sorted(region_interp[rg].keys())
            dose_means = [np.mean(region_interp[rg][d]) for d in dose_dates]
            sat_note = ' (≥)' if region_has_sat.get(rg) else ''
            ax2.plot(dose_dates, dose_means, color='#E8A020', marker='s', lw=2,
                     ls='--', markersize=3, label='Cum. dose%s' % sat_note, zorder=4, alpha=0.8)
            ax2.fill_between(dose_dates, 0, dose_means, alpha=0.05, color='#E8A020')
        ax2.set_ylabel('Cumulative Dose (Gy)', color='#C08010')
        ax2.tick_params(axis='y', labelcolor='#C08010')
        ax2.set_ylim(bottom=0)

        ax.set_title('%s (N=%d Y-plates)' % (rg, n_plates))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.grid(True, alpha=0.2)

        # Combined legend
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='lower left', fontsize=7, framealpha=0.9)

    fig.suptitle('T6: NdFeB Degradation + Cumulative Dose vs Time by Region', fontsize=13)
    fig.text(0.99, 0.01, 'Shaded bands: \u00b11 SEM',
             ha='right', va='bottom', fontsize=7, fontstyle='italic', color='gray')
    fig.tight_layout()
    save(fig, 'T6_degradation_and_dose_by_region.png')


# ═════════════════════════════════════════════════════════════════════════════
# T7: Per-Plate Dose Timeline with Helmholtz Dates Marked
# ═════════════════════════════════════════════════════════════════════════════

def plot_t7(dose_full, y_results):
    """Individual Y-plate dose timelines, grouped by region, with Helmholtz dates marked.

    Legend uses descriptive location labels (e.g., 'SE Arc L2', 'N.Lin Gir.23').
    Saturated endpoints marked with ▲.
    """
    # Collect Helmholtz measurement dates
    helm_dates = set()
    for r in y_results:
        for dt, pct in r.get('date_pcts', []):
            helm_dates.add(normalize_date(dt))
    helm_dates = sorted(helm_dates)

    # Group Y-plates by region
    region_plates = defaultdict(list)
    for plate_label, entries in dose_full.items():
        if not plate_label.startswith('Y-'):
            continue
        try:
            pnum = int(plate_label.replace('Y-', ''))
        except ValueError:
            continue
        pl = Y_PLACEMENT.get(pnum)
        if not pl:
            continue
        rg = get_region_group(pl['region'])
        region_plates[rg].append((pnum, plate_label, entries, pl))

    regions = ['Arc', 'North Linac', 'South Linac', 'Labyrinth']
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    for idx, rg in enumerate(regions):
        ax = axes[idx // 2][idx % 2]
        plates = region_plates.get(rg, [])

        # Sort: arc plates by line number, others by plate number
        if rg == 'Arc':
            plates.sort(key=lambda x: (x[3].get('region', ''), x[3].get('line', 0)))
        else:
            plates.sort(key=lambda x: x[0])

        n_saturated = 0
        for pnum, plate_label, entries, pl in plates:
            dates = [e['date'] for e in entries]
            cum_gy = [e['cum_body'] * MREM_TO_GY_PHOTON for e in entries]
            is_lb = entries[-1].get('is_lower_bound', False)

            # Build descriptive label
            loc = short_location(pl)
            if is_lb:
                label = '%s ≥%.0f Gy' % (loc, cum_gy[-1])
                n_saturated += 1
            else:
                label = '%s %.0f Gy' % (loc, cum_gy[-1])

            line = ax.plot(dates, cum_gy, marker='.', markersize=4, lw=1.5,
                           label=label, zorder=3)

            # Mark saturated endpoint with triangle
            if is_lb:
                ax.plot(dates[-1], cum_gy[-1], marker='^', color=line[0].get_color(),
                        markersize=7, zorder=6)

        # Mark Helmholtz measurement dates
        for hd in helm_dates:
            ax.axvline(hd, color='green', linewidth=0.8, linestyle=':', alpha=0.5, zorder=1)
        if helm_dates:
            ax.axvline(helm_dates[0], color='green', linewidth=0.8, linestyle=':',
                       alpha=0.5, label='Helmholtz meas.')

        # Beam-off
        ax.axvline(BEAM_OFF, color='gray', linewidth=1, linestyle='--', alpha=0.7)
        ax.annotate('Beam OFF', xy=(BEAM_OFF, 0.97), xycoords=('data', 'axes fraction'),
                    fontsize=7, color='gray', rotation=90, va='top', ha='right')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.set_ylabel('Cumulative Dose (Gy)')
        sat_note = ' (%d/%d saturated)' % (n_saturated, len(plates)) if n_saturated else ''
        ax.set_title('%s — %d plates%s' % (rg, len(plates), sat_note))
        ax.grid(True, alpha=0.2)
        ncol = 2 if len(plates) > 6 else 1
        ax.legend(loc='upper left', fontsize=5.5, framealpha=0.9, ncol=ncol)

    fig.suptitle('T7: Per-Plate Dose Timeline with Helmholtz Measurement Dates\n'
                 '(▲ = saturated badge, dose is lower bound)', fontsize=12)
    fig.tight_layout()
    save(fig, 'T7_per_plate_dose_timeline.png')


# ═════════════════════════════════════════════════════════════════════════════
# Summary Table & Linear Fits
# ═════════════════════════════════════════════════════════════════════════════

def write_summary(series, dose_full=None):
    """Write per-session stats, dose at each date, and linear fit slopes."""
    lines = []
    lines.append("=" * 80)
    lines.append("TIME SERIES DEGRADATION EVOLUTION — SUMMARY")
    lines.append("=" * 80)

    # ── Degradation series ──
    for key in sorted(series.keys()):
        pts = series[key]
        if not pts:
            continue
        lines.append("")
        lines.append("--- %s ---" % key)
        lines.append("  %-12s  %8s  %8s  %5s" % ("Date", "Mean(%)", "SEM(%)", "N"))
        for dt, mean, sem, n in pts:
            lines.append("  %-12s  %+8.3f  %8.3f  %5d" % (dt.strftime('%Y-%m-%d'), mean, sem, int(n)))

        # Linear fit (pct vs months since first date)
        if len(pts) >= 3:
            t0 = pts[0][0]
            months = [(p[0] - t0).days / 30.44 for p in pts]
            means = [p[1] for p in pts]
            slope, intercept, r_value, p_value, std_err = stats.linregress(months, means)
            lines.append("  Linear fit: slope = %.4f %%/month (R² = %.3f, p = %.4f)" %
                          (slope, r_value**2, p_value))

            # First-half vs second-half
            mid = len(pts) // 2
            first_mean = np.mean([p[1] for p in pts[:mid]])
            second_mean = np.mean([p[1] for p in pts[mid:]])
            lines.append("  First-half mean: %.3f%%  |  Second-half mean: %.3f%%  |  Delta: %.3f%%" %
                          (first_mean, second_mean, second_mean - first_mean))

    # ── Cumulative dose at each dose collection date, by region ──
    if dose_full:
        lines.append("")
        lines.append("=" * 80)
        lines.append("CUMULATIVE DOSE AT EACH COLLECTION DATE (Gy, Q=1)")
        lines.append("=" * 80)

        # Y-plates by region
        for prefix, plate_type in [('Y-', 'Y-plates'), ('Hn-', 'Hn-plates (NdFeB)'), ('Hs-', 'Hs-plates (SmCo)')]:
            lines.append("")
            lines.append("--- %s ---" % plate_type)

            region_plates_data = defaultdict(list)  # rg -> [(plate_label, entries)]
            for plate_label, entries in dose_full.items():
                if not plate_label.startswith(prefix):
                    continue
                try:
                    pnum = int(plate_label.replace(prefix, '').split('-')[0])
                except ValueError:
                    continue
                if prefix == 'Y-':
                    pl = Y_PLACEMENT.get(pnum)
                elif prefix == 'Hn-':
                    pl = H_PLACEMENT.get('N%d' % pnum)
                elif prefix == 'Hs-':
                    pl = H_PLACEMENT.get('S%d' % pnum)
                else:
                    pl = None
                if not pl:
                    continue
                rg = get_region_group(pl['region'])
                region_plates_data[rg].append((plate_label, entries))

            for rg in ['Arc', 'North Linac', 'South Linac', 'Labyrinth']:
                plates = region_plates_data.get(rg, [])
                if not plates:
                    continue
                lines.append("")
                lines.append("  %s (N=%d plates):" % (rg, len(plates)))

                # Get all dates
                all_dates = set()
                for _, entries in plates:
                    for e in entries:
                        all_dates.add(e['date'])
                all_dates = sorted(all_dates)

                # Header
                lines.append("  %-12s  %10s  %10s  %10s  %10s  %5s" % (
                    "Date", "Body(Gy)", "Photon(Gy)", "Neutron(Gy)", "Beta(Gy)", "N"))

                for dt in all_dates:
                    body_vals = []
                    photon_vals = []
                    neutron_vals = []
                    beta_vals = []
                    for _, entries in plates:
                        for e in entries:
                            if e['date'] == dt:
                                body_vals.append(e['cum_body'] * MREM_TO_GY_PHOTON)
                                photon_vals.append(e['cum_photon'] * MREM_TO_GY_PHOTON)
                                neutron_vals.append(e['cum_neutron'] * MREM_TO_GY_PHOTON)
                                beta_vals.append(e['cum_beta'] * MREM_TO_GY_PHOTON)
                    if body_vals:
                        lines.append("  %-12s  %10.1f  %10.1f  %10.1f  %10.1f  %5d" % (
                            dt.strftime('%Y-%m-%d'),
                            np.mean(body_vals), np.mean(photon_vals),
                            np.mean(neutron_vals), np.mean(beta_vals),
                            len(body_vals)))

                # Final per-plate summary
                lines.append("")
                lines.append("  Per-plate final cumulative (Gy):")
                for plate_label, entries in sorted(plates, key=lambda x: x[0]):
                    final = entries[-1]
                    lb_mark = ' ≥' if final.get('is_lower_bound', False) else ''
                    lines.append("    %-10s  body=%8.1f  photon=%8.1f  neutron=%6.2f  beta=%6.2f%s" % (
                        plate_label,
                        final['cum_body'] * MREM_TO_GY_PHOTON,
                        final['cum_photon'] * MREM_TO_GY_PHOTON,
                        final['cum_neutron'] * MREM_TO_GY_PHOTON,
                        final['cum_beta'] * MREM_TO_GY_PHOTON,
                        lb_mark))

    lines.append("")
    lines.append("=" * 80)

    path = os.path.join(PLOT_DIR, 'summary_table.txt')
    with open(path, 'w') as f:
        f.write('\n'.join(lines))
    print("  Saved: %s" % path)

    # Print to stdout too
    for line in lines:
        print(line)


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("Task 9: Time Series Degradation Evolution")
    print("=" * 60)

    # Load Y-plate data
    print("\nLoading Y-plate data (v3)...")
    y_results, helm_raw, temp_final, y_materials = load_all()
    y_clean = [r for r in y_results if not r['is_outlier']]
    print("  %d Y-plate samples (%d clean)" % (len(y_results), len(y_clean)))

    # Get gain systematic
    gain_obj = get_gain_syst(helm_raw)
    gain_syst = gain_obj.gain_syst if hasattr(gain_obj, 'gain_syst') else gain_obj[0]
    print("  Gain systematic: ±%.3f%%" % gain_syst)

    # Load H-plate data
    print("Loading H-plate data (v2)...")
    y_mats_xl, pair_arrangements = load_materials()
    temp_lookup = build_temperature_lookup()
    h_results, h_excluded = compute_h_plate_degradation(pair_arrangements, temp_lookup)
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]
    print("  %d H-plate pairs (%d clean)" % (len(h_results), len(h_clean)))

    # Spot-check H-plate date_pcts
    h_with_dp = sum(1 for r in h_results if r.get('date_pcts'))
    print("  H-plates with date_pcts: %d / %d" % (h_with_dp, len(h_results)))

    # Load A-sample data
    print("Loading A-sample data (v5)...")
    a_results = load_a_sample_helmholtz(temp_lookup)
    a_clean = [r for r in a_results if not r.get('is_outlier', False)]
    print("  %d A-samples (%d clean)" % (len(a_results), len(a_clean)))

    # Collect time series
    print("\nCollecting time series data...")
    series, trajectories, gs = collect_time_series(y_clean, h_clean, a_clean, gain_syst)
    for key in sorted(series.keys()):
        pts = series[key]
        if pts:
            print("  %s: %d dates, latest mean = %+.3f%%" % (key, len(pts), pts[-1][1]))

    # Load dose timeline
    print("\nLoading dose timeline...")
    try:
        dose_timeline = load_dose_timeline()
        print("  %d plates with dose timeline (basic)" % len(dose_timeline))
    except Exception as e:
        print("  WARNING: Could not load dose timeline: %s" % e)
        dose_timeline = {}

    # Load full dose timeline (all radiation types)
    print("Loading full dose timeline...")
    try:
        dose_full = load_dose_timeline_full()
        y_dose = {k: v for k, v in dose_full.items() if k.startswith('Y-')}
        h_dose = {k: v for k, v in dose_full.items() if k.startswith('H')}
        print("  %d plates total (%d Y, %d H)" % (len(dose_full), len(y_dose), len(h_dose)))
    except Exception as e:
        print("  WARNING: Could not load full dose timeline: %s" % e)
        dose_full = {}

    # Generate plots
    print("\nGenerating plots...")
    plot_t1(series, gain_syst)
    plot_t2(trajectories, series)
    plot_t3(y_results, dose_timeline)
    plot_t4(trajectories, series)

    if dose_full:
        plot_t5(dose_full)
        plot_t6(trajectories, series, dose_full)
        plot_t7(dose_full, y_results)
    else:
        print("  T5-T7: Skipped (no dose data)")

    # Summary table
    print("\nWriting summary...")
    write_summary(series, dose_full)

    print("\nDone! Output in: %s" % PLOT_DIR)


if __name__ == '__main__':
    main()
