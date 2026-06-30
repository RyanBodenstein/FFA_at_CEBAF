#!/usr/bin/env python3
"""
Manager-Friendly Degradation Summary Plots — Version 2

Changes from v1 (manager_summary.py):
  - Quantifies and displays Helmholtz session-to-session gain systematic (~0.5-0.7%)
  - Adds gain-immune "double ratio" analysis: intra-plate NdFeB-SmCo differential
  - Flags Oct 21 thermal lag issue
  - All v2 plots are numbered 8+ to sit alongside original 1-7 plots

Key insight: The Helmholtz coil has 0.5-0.7% session-to-session gain variability
(measured in pre-deployment lab data). This is comparable to the 0.3% degradation
signal. The intra-plate NdFeB-SmCo differential cancels this systematic because
both materials are measured on the same plate in the same session.

Output: Cleanup_Claude/Manager_Plots/ (files 8_*.png through 14_*.png)
"""

import os
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict
import openpyxl

# ─── Paths & Constants ───────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.join(BASE, 'Manager_Plots')
os.makedirs(PLOT_DIR, exist_ok=True)

T_REF = 20.0
SENTINEL = 1337
ALPHA = {
    'N42EH': -0.0010, 'N52SH': -0.0011,
    'SmCo33H': -0.0004, 'SmCo35': -0.0004,
}
ALPHA_SLOT = {1: -0.0010, 2: -0.0011, 3: -0.0004, 4: -0.0004}
MAT_BY_SLOT = {1: 'N42EH', 2: 'N52SH', 3: 'SmCo33H', 4: 'SmCo35'}
TUNNEL_START = datetime(2025, 7, 1)
MIN_BASELINE = 0.1
FLAGGED = {'Y-34-4', 'Y-40-4'}

MAT_COLORS = {
    'N42EH': '#D62728', 'N52SH': '#1F77B4',
    'SmCo33H': '#2CA02C', 'SmCo35': '#FF7F0E',
}
MAT_LABELS = {
    'N42EH': 'NdFeB N42EH', 'N52SH': 'NdFeB N52SH',
    'SmCo33H': 'SmCo 33H', 'SmCo35': 'SmCo 35',
}

PLACEMENTS = {
    15: 'SE Arc', 3: 'SE Arc', 23: 'SE Arc', 26: 'SE Arc', 40: 'SE Arc',
    39: 'NE Arc', 7: 'NE Arc', 18: 'NE Arc', 21: 'NE Arc', 9: 'NE Arc',
    38: 'NW Arc', 6: 'NW Arc', 36: 'NW Arc', 25: 'NW Arc', 34: 'NW Arc',
    13: 'SW Arc', 32: 'SW Arc', 19: 'SW Arc', 10: 'SW Arc', 11: 'SW Arc',
    12: 'Labyrinth', 17: 'North Linac', 4: 'North Linac',
    16: 'North Linac', 22: 'North Linac',
    20: 'Labyrinth', 24: 'South Linac', 5: 'South Linac',
    1: 'South Linac', 30: 'South Linac',
}


# ─── Parsers ──────────────────────────────────────────────────────────────────

def parse_helmholtz_file(filepath):
    """Parse a Helmholtz .dat file. Returns [(datetime, value, unit), ...]"""
    rows = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            val_match = re.search(r'([+-]?\d+\.?\d*)\s+(mWC|kT|kBG|mT)', line)
            if not val_match:
                continue
            val, unit = float(val_match.group(1)), val_match.group(2)
            dm = re.match(r'\s*(\d{4}-\d{2}-\d{2})[-\t](\d{2}:\d{2}:\d{2})', line)
            if not dm:
                continue
            dt = datetime.strptime("%s %s" % (dm.group(1), dm.group(2)),
                                   "%Y-%m-%d %H:%M:%S")
            rows.append((dt, val, unit))
    return rows


def parse_teslameter_file(filepath):
    """Parse a Teslameter .dat file. Returns [(datetime, [Bx,By,Bz], temp), ...]"""
    rows = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = re.match(r'(\d{4}-\d{2}-\d{2})\t(\d{2}:\d{2}:\d{2})\t(.*)', line)
            if m:
                dt = datetime.strptime("%s %s" % (m.group(1), m.group(2)),
                                       "%Y-%m-%d %H:%M:%S")
                rest = m.group(3)
            else:
                m = re.match(r'(\d{4}-\d{2}-\d{2})-(\d{2}:\d{2}:\d{2})\t(.*)', line)
                if m:
                    dt = datetime.strptime("%s %s" % (m.group(1), m.group(2)),
                                           "%Y-%m-%d %H:%M:%S")
                    rest = m.group(3)
                else:
                    continue
            nums = re.findall(r'(-?\d+\.\d+)', rest)
            if len(nums) >= 4:
                rows.append((dt, [float(x) for x in nums[:3]], float(nums[3])))
    return rows


# ─── Load Data ────────────────────────────────────────────────────────────────

def load_all():
    """Load all Y-plate Helmholtz + Teslameter data.

    Returns:
        results: list of per-sample dicts (same as v1 manager_summary.py)
        helm_raw: dict of (plate, slot) -> {date_str: raw_mWC_value}
        temp_final: dict of (sample, date_str) -> (temp_mean, temp_std)
        y_materials: dict of sample_id -> material_name
    """
    # Materials
    wb = openpyxl.load_workbook(os.path.join(BASE, 'Materials_Arrangements.xlsx'),
                                data_only=True)
    y_materials = {}
    for row in wb['Tunnel - Y Materials'].iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        pm = re.match(r'[yY]-?(\d+)', str(row[0]).strip())
        if not pm:
            continue
        pn = pm.group(1)
        for i, v in enumerate(row[1:5], 1):
            if v:
                y_materials['Y-%s-%d' % (pn, i)] = str(v).strip()

    # Temperature lookup from Teslameter (3 faces averaged)
    y_tesla_dir = os.path.join(BASE, 'Y_Plates', 'Teslameter')
    temp_lookup = defaultdict(list)
    for f in os.listdir(y_tesla_dir):
        m = re.match(r'(Y-\d+-\d+)_(front|side|top)\.dat$', f)
        if not m:
            continue
        sample = m.group(1)
        rows = parse_teslameter_file(os.path.join(y_tesla_dir, f))
        for dt, fields, temp in rows:
            if temp is None or abs(temp - SENTINEL) < 1:
                continue
            temp_lookup[(sample, dt.strftime('%Y-%m-%d'))].append(temp)

    temp_final = {}
    for key, temps in temp_lookup.items():
        temp_final[key] = (np.mean(temps),
                           np.std(temps, ddof=1) if len(temps) > 1 else 0.5)

    # Load raw Helmholtz values keyed by (plate, slot) -> {date_str: value}
    helm_raw = defaultdict(dict)
    helm_dir = os.path.join(BASE, 'Y_Plates', 'Helmholtz')

    # Also build the per-sample result list (same format as v1)
    results = []

    for f in sorted(os.listdir(helm_dir)):
        if not f.endswith('_helmholtz.dat'):
            continue
        sample = f.replace('_helmholtz.dat', '')
        mat = y_materials.get(sample)
        if not mat:
            continue
        alpha = ALPHA.get(mat)
        if alpha is None:
            continue
        pm = re.match(r'Y-(\d+)-(\d+)', sample)
        if not pm:
            continue
        plate_num = int(pm.group(1))
        slot_num = int(pm.group(2))
        region = PLACEMENTS.get(plate_num, 'Unknown')
        is_outlier = sample in FLAGGED

        rows = parse_helmholtz_file(os.path.join(helm_dir, f))
        mwc = [(dt, v) for dt, v, u in rows
               if u == 'mWC' and abs(v - SENTINEL) > 1 and abs(v) >= MIN_BASELINE]

        # Store raw values by (plate, slot, date)
        for dt, v in mwc:
            helm_raw[(plate_num, slot_num)][dt.strftime('%Y-%m-%d')] = v

        # Temperature-corrected per-sample analysis (same as v1)
        pre_corr = []
        tunnel_series = []
        for dt, h_raw in mwc:
            key = (sample, dt.strftime('%Y-%m-%d'))
            if key not in temp_final:
                continue
            t_mean, _ = temp_final[key]
            h_corr = h_raw / (1 + alpha * (t_mean - T_REF))
            if dt < TUNNEL_START:
                pre_corr.append(h_corr)
            else:
                tunnel_series.append((dt, h_corr))

        if not pre_corr or not tunnel_series:
            continue

        bl_mean = np.mean(pre_corr)
        if abs(bl_mean) < MIN_BASELINE:
            continue

        tunnel_series.sort()
        latest_dt, latest_corr = tunnel_series[-1]
        pct = (latest_corr - bl_mean) / bl_mean * 100.0

        date_pcts = []
        for dt, h_corr in tunnel_series:
            date_pcts.append((dt, (h_corr - bl_mean) / bl_mean * 100.0))

        bl_sem = (np.std(pre_corr, ddof=1) / np.sqrt(len(pre_corr))
                  if len(pre_corr) > 1 else 0.01 * bl_mean)

        results.append({
            'sample': sample, 'plate': plate_num, 'slot': slot_num,
            'material': mat, 'region': region,
            'pct_change': pct, 'bl_mean': bl_mean,
            'bl_sem_pct': bl_sem / abs(bl_mean) * 100.0,
            'is_outlier': is_outlier,
            'date_pcts': date_pcts,
        })

    return results, helm_raw, temp_final, y_materials


# ─── Double Ratio Computation ─────────────────────────────────────────────────

def compute_double_ratio(helm_raw, temp_final, ref_date, comp_date):
    """Compute intra-plate NdFeB-SmCo differential (gain-immune).

    For each plate on comp_date vs ref_date:
      1. Temperature-correct both readings for each slot
      2. Compute % change per slot
      3. Return (NdFeB mean % change) - (SmCo mean % change)

    Returns list of per-plate diffs, plus breakdowns.
    """
    all_plates = set(p for (p, s) in helm_raw)
    plate_diffs = []
    plate_details = []

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

            ref_t = ref_temp_data[0]
            comp_t = comp_temp_data[0]

            a = ALPHA_SLOT[slot]
            ref_corr = ref_val / (1 + a * (ref_t - T_REF))
            comp_corr = comp_val / (1 + a * (comp_t - T_REF))

            pct = (comp_corr - ref_corr) / ref_corr * 100.0
            slot_pcts[slot] = pct

        ndfeb_pcts = [slot_pcts[s] for s in [1, 2] if s in slot_pcts]
        smco_pcts = [slot_pcts[s] for s in [3, 4] if s in slot_pcts]

        if ndfeb_pcts and smco_pcts:
            diff = np.mean(ndfeb_pcts) - np.mean(smco_pcts)
            plate_diffs.append(diff)
            plate_details.append({
                'plate': plate,
                'region': PLACEMENTS.get(plate, 'Unknown'),
                'ndfeb_pct': np.mean(ndfeb_pcts),
                'smco_pct': np.mean(smco_pcts),
                'diff': diff,
                'slot_pcts': slot_pcts,
            })

    return plate_diffs, plate_details


def compute_gain_variability(helm_raw):
    """Quantify Helmholtz session-to-session gain variability from lab data.

    Uses pre-deployment measurements (lab conditions, ~21C, no radiation).
    Returns per-session mean offset from Nov 5 2024 baseline.
    """
    ref_date = '2024-11-05'
    lab_dates = ['2025-04-23', '2025-05-07', '2025-05-21',
                 '2025-06-11', '2025-06-17']

    session_offsets = {}
    for check_date in lab_dates:
        offsets = []
        for (plate, slot), date_dict in helm_raw.items():
            if ref_date in date_dict and check_date in date_dict:
                ref_v = date_dict[ref_date]
                check_v = date_dict[check_date]
                pct = (check_v - ref_v) / ref_v * 100.0
                offsets.append(pct)
        if len(offsets) >= 5:
            session_offsets[check_date] = {
                'mean': np.mean(offsets),
                'std': np.std(offsets),
                'sem': np.std(offsets) / np.sqrt(len(offsets)),
                'n': len(offsets),
            }
    return session_offsets


# ─── Plot 8: Helmholtz Gain Variability ───────────────────────────────────────

def plot_gain_variability(helm_raw):
    """Show the Helmholtz session-to-session gain systematic."""
    session_offsets = compute_gain_variability(helm_raw)

    if not session_offsets:
        print("  Plot 8: SKIPPED (no session offset data)")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Helmholtz Coil Session-to-Session Gain Variability\n'
                 'Pre-deployment lab measurements (constant ~21\u00b0C, no radiation)',
                 fontsize=14, fontweight='bold')

    # Left panel: session offsets from Nov 5 2024
    dates = sorted(session_offsets.keys())
    dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
    means = [session_offsets[d]['mean'] for d in dates]
    sems = [session_offsets[d]['sem'] for d in dates]
    ns = [session_offsets[d]['n'] for d in dates]

    ax1.errorbar(dt_objs, means, yerr=sems, marker='s', markersize=8,
                 color='#333333', linewidth=2, capsize=6, capthick=2)
    ax1.axhline(0, color='black', linewidth=1, linestyle='--',
                label='Nov 5 2024 reference')

    for i, (d, m, n) in enumerate(zip(dt_objs, means, ns)):
        ax1.annotate('N=%d' % n, (d, m), textcoords='offset points',
                     xytext=(0, 12), ha='center', fontsize=8, color='gray')

    ax1.set_ylabel('% Offset from Nov 5 2024 Baseline', fontsize=11)
    ax1.set_xlabel('Measurement Date', fontsize=11)
    ax1.set_title('(a) Lab Session Offsets', fontsize=12, fontweight='bold')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=9)

    # Shade the range
    all_means = [session_offsets[d]['mean'] for d in dates]
    spread = max(all_means) - min(all_means)
    ax1.axhspan(min(all_means) - 0.1, max(all_means) + 0.1,
                alpha=0.08, color='red')
    ax1.text(dt_objs[0], max(all_means) + 0.15,
             'Session-to-session spread: %.2f%%' % spread,
             fontsize=10, color='#AA0000', fontweight='bold')

    # Right panel: by-material breakdown for one comparison (Nov 5 vs Jun 11)
    ref_date = '2024-11-05'
    check_date = '2025-06-11'
    by_mat = defaultdict(list)
    for (plate, slot), date_dict in helm_raw.items():
        if ref_date in date_dict and check_date in date_dict:
            mat = MAT_BY_SLOT[slot]
            pct = (date_dict[check_date] - date_dict[ref_date]) / date_dict[ref_date] * 100.0
            by_mat[mat].append(pct)

    mats = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    mat_means = []
    mat_sems = []
    mat_cols = []
    mat_labels_full = []
    for mat in mats:
        vals = by_mat.get(mat, [])
        if vals:
            m = np.mean(vals)
            s = np.std(vals) / np.sqrt(len(vals))
            mat_means.append(m)
            mat_sems.append(s)
            mat_cols.append(MAT_COLORS[mat])
            mat_labels_full.append('%s\n%.2f%% (N=%d)' % (MAT_LABELS[mat], m, len(vals)))

    if mat_means:
        x = np.arange(len(mat_means))
        ax2.bar(x, mat_means, yerr=mat_sems, color=mat_cols,
                capsize=6, edgecolor='black', linewidth=0.5, alpha=0.85,
                width=0.5)
        ax2.axhline(0, color='black', linewidth=1, linestyle='--')
        ax2.set_xticks(x)
        ax2.set_xticklabels(mat_labels_full, fontsize=9)
        ax2.set_ylabel('% Offset (Nov 5 2024 \u2192 Jun 11 2025)', fontsize=11)
        ax2.set_title('(b) By Material: All ~\u22120.65%\n(material-independent \u2192 gain shift)',
                       fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

        # Annotate
        ax2.annotate('All 4 materials show the SAME offset\n'
                     '\u2192 Helmholtz coil gain shift, NOT material effect',
                     xy=(1.5, np.mean(mat_means)),
                     xytext=(1.5, np.mean(mat_means) + 0.4),
                     fontsize=9, ha='center',
                     arrowprops=dict(arrowstyle='->', color='#555'),
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                               edgecolor='gray'))

    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(os.path.join(PLOT_DIR, '8_gain_systematic.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 8: Helmholtz gain variability")


# ─── Plot 9: Double Ratio Time Series (THE KEY NEW PLOT) ─────────────────────

def plot_double_ratio_timeseries(helm_raw, temp_final):
    """The gain-immune NdFeB-SmCo differential over time.

    Uses Aug 27 as reference (all 30 plates measured).
    Shows the differential at each subsequent date.
    """
    ref_date = '2025-08-27'
    # Only dates where we have temperature data for correction
    comp_dates = ['2025-07-17', '2025-07-30', '2025-10-21',
                  '2025-10-23', '2025-10-29', '2026-01-08', '2026-01-12']

    fig, ax = plt.subplots(figsize=(12, 7))

    dt_objs = []
    means = []
    sems = []
    ns = []
    annotations = []

    for cd in comp_dates:
        diffs, details = compute_double_ratio(helm_raw, temp_final, ref_date, cd)
        if not diffs:
            continue
        m = np.mean(diffs)
        s = np.std(diffs) / np.sqrt(len(diffs))
        sig = abs(m / s) if s > 0 else 0

        dt_objs.append(datetime.strptime(cd, '%Y-%m-%d'))
        means.append(m)
        sems.append(s)
        ns.append(len(diffs))
        annotations.append((cd, m, s, sig, len(diffs)))

    # Plot
    ax.errorbar(dt_objs, means, yerr=sems, marker='D', markersize=9,
                color='#8B0000', linewidth=2.5, capsize=8, capthick=2.5,
                zorder=5, label='NdFeB \u2212 SmCo differential')
    ax.axhline(0, color='black', linewidth=1.5, linestyle='--',
               label='No differential = no material-dependent degradation')

    # Reference point at Aug 27 (by definition = 0)
    ax.plot(datetime.strptime(ref_date, '%Y-%m-%d'), 0, 'D',
            color='#8B0000', markersize=12, zorder=6,
            markeredgecolor='gold', markeredgewidth=2)
    ax.annotate('Reference\n(Aug 27)', xy=(datetime.strptime(ref_date, '%Y-%m-%d'), 0),
                xytext=(datetime(2025, 9, 10), 0.25),
                fontsize=10, ha='center',
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                          edgecolor='gray'))

    # Annotate each point with significance
    for cd, m, s, sig, n in annotations:
        dt = datetime.strptime(cd, '%Y-%m-%d')
        sig_str = '%.1f\u03c3' % sig if sig >= 2 else 'n.s.'
        label = '%+.2f%%\n\u00b1%.2f%%\n%s (N=%d)' % (m, s, sig_str, n)

        # Position annotations to avoid overlap
        if cd == '2025-10-21':
            ax.annotate(label, (dt, m), textcoords='offset points',
                        xytext=(-60, -20), fontsize=8, ha='center',
                        arrowprops=dict(arrowstyle='->', color='gray', lw=0.8),
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFF0F0',
                                  edgecolor='gray', alpha=0.9))
        elif cd == '2025-10-23':
            ax.annotate(label, (dt, m), textcoords='offset points',
                        xytext=(50, 30), fontsize=8, ha='center',
                        arrowprops=dict(arrowstyle='->', color='gray', lw=0.8))
        elif cd == '2026-01-12':
            ax.annotate(label, (dt, m), textcoords='offset points',
                        xytext=(50, -15), fontsize=8, ha='center',
                        arrowprops=dict(arrowstyle='->', color='gray', lw=0.8),
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFF0F0',
                                  edgecolor='gray', alpha=0.9))
        else:
            ax.annotate(label, (dt, m), textcoords='offset points',
                        xytext=(0, -45 if m < 0 else 20), fontsize=8, ha='center')

    # Shade the Oct 21 thermal lag region
    ax.axvspan(datetime(2025, 10, 18), datetime(2025, 11, 1),
               alpha=0.08, color='orange')
    ax.text(datetime(2025, 10, 25), ax.get_ylim()[0] * 0.1 + ax.get_ylim()[1] * 0.9,
            'Beam OFF + thermal lag\n(magnets not equilibrated)',
            fontsize=8, ha='center', color='#AA6600', fontstyle='italic')

    # Beam OFF marker
    ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1.5,
               linestyle=':', alpha=0.7)

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('NdFeB \u2212 SmCo  Differential (% change from Aug 27)',
                  fontsize=12)
    ax.set_title('Gain-Immune Degradation Metric: Intra-Plate NdFeB\u2212SmCo Differential\n'
                 'This metric cancels Helmholtz session-to-session gain variability',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(datetime(2025, 6, 15), datetime(2026, 2, 1))

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, '9_double_ratio_timeseries.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 9: Double ratio time series (gain-immune)")


# ─── Plot 10: Material Comparison with Systematic Uncertainty ─────────────────

def plot_material_comparison_v2(results, helm_raw):
    """Same as v1 Plot 1 but with gain systematic uncertainty shown."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    # Estimate gain systematic from pre-deployment data
    session_offsets = compute_gain_variability(helm_raw)
    if session_offsets:
        gain_offsets = [session_offsets[d]['mean'] for d in session_offsets]
        gain_syst = np.std(gain_offsets)  # ~0.15-0.2% from spread of session means
        # But the real issue is that any SINGLE session can be off by up to 0.7%
        # Conservative: use the full range / 2
        gain_syst = (max(gain_offsets) - min(gain_offsets)) / 2.0
    else:
        gain_syst = 0.3  # default estimate

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Magnet Degradation: Absolute Values vs Gain-Immune Differential\n'
                 'CEBAF Tunnel Exposure: Jul 2025 \u2013 Jan 2026',
                 fontsize=14, fontweight='bold')

    # Left panel: absolute values (as before) with gain systematic band
    means_abs, sems_stat, colors, labels_abs = [], [], [], []
    for mat in materials:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        if not vals:
            continue
        m = np.mean(vals)
        sem = np.std(vals, ddof=1) / np.sqrt(len(vals))
        sig_stat = abs(m / sem) if sem > 0 else 0
        means_abs.append(m)
        sems_stat.append(sem)
        colors.append(MAT_COLORS[mat])
        labels_abs.append('%s\n%+.2f%% \u00b1 %.2f%%(stat)\n\u00b1 %.2f%%(syst)' %
                          (MAT_LABELS[mat], m, sem, gain_syst))

    x = np.arange(len(materials))
    bars = ax1.bar(x, means_abs, yerr=sems_stat, color=colors, capsize=8,
                   edgecolor='black', linewidth=0.8, alpha=0.85, width=0.6,
                   error_kw=dict(linewidth=2, capthick=2))

    # Add systematic uncertainty as shaded band
    for i, (m, ss) in enumerate(zip(means_abs, sems_stat)):
        ax1.fill_between([i - 0.3, i + 0.3],
                         [m - gain_syst, m - gain_syst],
                         [m + gain_syst, m + gain_syst],
                         alpha=0.15, color='gray', zorder=0)

    ax1.axhline(0, color='black', linewidth=1)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels_abs, fontsize=9)
    ax1.set_ylabel('% Change from Baseline\n(temperature-corrected to 20\u00b0C)',
                   fontsize=11)
    ax1.set_title('(a) Absolute Values\n(gray band = Helmholtz gain systematic)',
                  fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim(-0.7, 0.7)

    # Right panel: gain-immune differential
    # NdFeB combined vs SmCo combined, using intra-plate differential
    ndfeb_vals = [r['pct_change'] for r in clean
                  if r['material'] in ['N42EH', 'N52SH']]
    smco_vals = [r['pct_change'] for r in clean
                 if r['material'] in ['SmCo33H', 'SmCo35']]

    # Compute per-plate differential directly
    plate_diffs = defaultdict(dict)  # plate -> {mat: pct}
    for r in clean:
        plate_diffs[r['plate']][r['material']] = r['pct_change']

    intra_diffs = []
    for plate, mat_pcts in plate_diffs.items():
        nd = [mat_pcts[m] for m in ['N42EH', 'N52SH'] if m in mat_pcts]
        sm = [mat_pcts[m] for m in ['SmCo33H', 'SmCo35'] if m in mat_pcts]
        if nd and sm:
            intra_diffs.append(np.mean(nd) - np.mean(sm))

    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    # Also compute per-material absolute with systematic
    nd_mean = np.mean(ndfeb_vals)
    nd_sem = np.std(ndfeb_vals, ddof=1) / np.sqrt(len(ndfeb_vals))
    sm_mean = np.mean(smco_vals)
    sm_sem = np.std(smco_vals, ddof=1) / np.sqrt(len(smco_vals))

    bar_labels = ['NdFeB\n(absolute)',
                  'SmCo\n(absolute)',
                  'NdFeB \u2212 SmCo\n(gain-immune)']
    bar_means = [nd_mean, sm_mean, diff_mean]
    bar_errs = [nd_sem, sm_sem, diff_sem]
    bar_colors = ['#CC4444', '#44AA44', '#8B0000']

    x2 = np.arange(3)
    bars2 = ax2.bar(x2, bar_means, yerr=bar_errs, color=bar_colors, capsize=8,
                    edgecolor='black', linewidth=0.8, alpha=0.85, width=0.5,
                    error_kw=dict(linewidth=2, capthick=2))

    # Add gain systematic band to absolute bars only (not to differential)
    for i in [0, 1]:
        ax2.fill_between([i - 0.25, i + 0.25],
                         [bar_means[i] - gain_syst, bar_means[i] - gain_syst],
                         [bar_means[i] + gain_syst, bar_means[i] + gain_syst],
                         alpha=0.15, color='gray', zorder=0)

    ax2.axhline(0, color='black', linewidth=1)
    ax2.set_xticks(x2)

    # Significance labels
    nd_sig = abs(nd_mean / nd_sem)
    sm_sig = abs(sm_mean / sm_sem)
    sig_labels = ['%+.3f%% \u00b1 %.3f%%(stat)\n\u00b1 %.2f%%(syst)\nN=%d' %
                  (nd_mean, nd_sem, gain_syst, len(ndfeb_vals)),
                  '%+.3f%% \u00b1 %.3f%%(stat)\n\u00b1 %.2f%%(syst)\nN=%d' %
                  (sm_mean, sm_sem, gain_syst, len(smco_vals)),
                  '%+.3f%% \u00b1 %.3f%%\n%.1f\u03c3 (NO gain syst)\nN=%d plates' %
                  (diff_mean, diff_sem, diff_sig, len(intra_diffs))]
    ax2.set_xticklabels(sig_labels, fontsize=9)
    ax2.set_ylabel('% Change', fontsize=11)
    ax2.set_title('(b) Absolute vs Gain-Immune Comparison\n'
                  '(gray band = gain systematic; absent for differential)',
                  fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_ylim(-0.7, 0.7)

    # Highlight the differential bar
    bars2[2].set_edgecolor('gold')
    bars2[2].set_linewidth(2.5)

    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(os.path.join(PLOT_DIR, '10_material_comparison_v2.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 10: Material comparison v2 (with gain systematic)")


# ─── Plot 11: Regional Double Ratio ──────────────────────────────────────────

def plot_regional_double_ratio(helm_raw, temp_final, results):
    """NdFeB-SmCo differential by tunnel region — gain-immune dose dependence.

    Uses the intra-plate baseline-to-latest differential (all 30 plates)
    rather than Aug27->Jan12 (only 15 plates, missing NE/NW/SE arcs).
    """
    clean = [r for r in results if not r['is_outlier']]

    # Compute per-plate NdFeB-SmCo differential using pre-deployment baseline
    plate_data = defaultdict(dict)
    for r in clean:
        plate_data[r['plate']][r['material']] = r['pct_change']

    details = []
    for plate, mat_pcts in plate_data.items():
        nd = [mat_pcts[m] for m in ['N42EH', 'N52SH'] if m in mat_pcts]
        sm = [mat_pcts[m] for m in ['SmCo33H', 'SmCo35'] if m in mat_pcts]
        if nd and sm:
            diff = np.mean(nd) - np.mean(sm)
            details.append({
                'plate': plate,
                'region': PLACEMENTS.get(plate, 'Unknown'),
                'diff': diff,
            })

    if not details:
        print("  Plot 11: SKIPPED (no data)")
        return

    # Group by region
    region_order = ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc',
                    'North Linac', 'South Linac', 'Labyrinth']
    region_diffs = defaultdict(list)
    for d in details:
        region_diffs[d['region']].append(d['diff'])

    fig, ax = plt.subplots(figsize=(12, 7))

    # Bar plot by region
    x_vals = []
    y_means = []
    y_sems = []
    x_labels = []
    bar_colors = []

    for i, region in enumerate(region_order):
        vals = region_diffs.get(region, [])
        if vals:
            x_vals.append(i)
            y_means.append(np.mean(vals))
            y_sems.append(np.std(vals) / np.sqrt(len(vals)) if len(vals) > 1 else 0.05)
            x_labels.append('%s\nN=%d' % (region, len(vals)))
            if 'Arc' in region:
                bar_colors.append('#CC4444')
            elif 'Linac' in region:
                bar_colors.append('#4444CC')
            else:
                bar_colors.append('#888888')

    ax.bar(x_vals, y_means, yerr=y_sems, color=bar_colors,
           capsize=6, edgecolor='black', linewidth=0.8, alpha=0.85, width=0.6,
           error_kw=dict(linewidth=2, capthick=2))

    ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax.set_xticks(x_vals)
    ax.set_xticklabels(x_labels, fontsize=10)
    ax.set_ylabel('NdFeB \u2212 SmCo Differential (% change from pre-deployment)',
                  fontsize=11)
    ax.set_title('Gain-Immune Degradation by Tunnel Region (all 30 plates)\n'
                 'More negative = NdFeB degraded more relative to SmCo',
                 fontsize=13, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # Shade regions
    ax.axvspan(-0.5, 3.5, alpha=0.05, color='red')
    ax.axvspan(3.5, 5.5, alpha=0.05, color='blue')
    ax.text(1.5, ax.get_ylim()[1] * 0.9, 'Arcs (higher dose)',
            ha='center', fontsize=10, fontstyle='italic', color='#AA0000')
    ax.text(4.5, ax.get_ylim()[1] * 0.9, 'Linacs (lower dose)',
            ha='center', fontsize=10, fontstyle='italic', color='#0000AA')

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, '11_regional_double_ratio.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 11: Regional double ratio")


# ─── Plot 12: Oct 21 Thermal Lag Diagnostic ──────────────────────────────────

def plot_thermal_lag(helm_raw, temp_final):
    """Show evidence for thermal lag on Oct 21."""
    ref_date = '2025-08-27'

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Oct 21 Thermal Lag Diagnostic\n'
                 'Beam OFF \u2192 tunnel cooled rapidly, magnets may not have equilibrated',
                 fontsize=13, fontweight='bold')

    # Left: double ratio for Oct 21 vs Jan 12 (same plates where possible)
    comp_dates = ['2025-10-21', '2025-10-23', '2025-10-29',
                  '2026-01-08', '2026-01-12']

    for cd in comp_dates:
        diffs, details = compute_double_ratio(helm_raw, temp_final, ref_date, cd)
        if diffs:
            m = np.mean(diffs)
            s = np.std(diffs) / np.sqrt(len(diffs))
            dt = datetime.strptime(cd, '%Y-%m-%d')
            color = '#FF6600' if '2025-10' in cd else '#8B0000'
            marker = 's' if '2025-10' in cd else 'D'
            ax1.errorbar([dt], [m], yerr=[s], marker=marker, markersize=9,
                         color=color, linewidth=0, capsize=6, capthick=2,
                         elinewidth=2, zorder=5)
            ax1.annotate('%+.2f%%\u00b1%.2f%%\n(N=%d)' % (m, s, len(diffs)),
                         (dt, m), textcoords='offset points',
                         xytext=(0, -30 if m < -0.3 else 15), fontsize=8,
                         ha='center')

    ax1.axhline(0, color='black', linewidth=1, linestyle='--')
    ax1.axvspan(datetime(2025, 10, 18), datetime(2025, 11, 1),
                alpha=0.1, color='orange', label='Beam OFF period')
    ax1.set_ylabel('NdFeB \u2212 SmCo Differential (%)', fontsize=11)
    ax1.set_title('(a) Double Ratio Timeline', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    # Right: temperature vs date to show the rapid cooling
    dates_check = ['2025-08-27', '2025-10-21', '2025-10-23', '2025-10-29',
                   '2026-01-08', '2026-01-12']
    date_temps = {}
    for (sample, date_str), (tmean, tstd) in temp_final.items():
        if date_str in dates_check:
            if date_str not in date_temps:
                date_temps[date_str] = []
            date_temps[date_str].append(tmean)

    if date_temps:
        dt_objs = []
        t_means = []
        t_mins = []
        t_maxs = []
        for d in dates_check:
            if d in date_temps:
                dt_objs.append(datetime.strptime(d, '%Y-%m-%d'))
                temps = date_temps[d]
                t_means.append(np.mean(temps))
                t_mins.append(min(temps))
                t_maxs.append(max(temps))

        ax2.fill_between(dt_objs, t_mins, t_maxs, alpha=0.2, color='steelblue')
        ax2.plot(dt_objs, t_means, 'o-', color='steelblue', markersize=8,
                 linewidth=2, label='Teslameter (air temp)')

        # Show what a 5C lag would mean on Oct 21
        oct21_idx = None
        for i, d in enumerate(dates_check):
            if d == '2025-10-21' and i < len(dt_objs):
                oct21_idx = i
                break
        if oct21_idx is not None:
            ax2.plot(dt_objs[oct21_idx], t_means[oct21_idx] + 5, 'v',
                     color='red', markersize=12, zorder=6,
                     label='Estimated magnet T (~5\u00b0C lag)')
            ax2.annotate('Magnet T\n(estimated)',
                         (dt_objs[oct21_idx], t_means[oct21_idx] + 5),
                         textcoords='offset points', xytext=(40, 5),
                         fontsize=9, color='red',
                         arrowprops=dict(arrowstyle='->', color='red'))

        ax2.set_ylabel('Temperature (\u00b0C)', fontsize=11)
        ax2.set_title('(b) Tunnel Temperature', fontsize=12, fontweight='bold')
        ax2.legend(fontsize=9)
        ax2.grid(alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(os.path.join(PLOT_DIR, '12_thermal_lag_diagnostic.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 12: Thermal lag diagnostic")


# ─── Plot 13: Per-Plate Double Ratio Waterfall ───────────────────────────────

def plot_double_ratio_waterfall(helm_raw, temp_final, results):
    """Every plate's NdFeB-SmCo differential, sorted by magnitude.

    Uses baseline-to-latest differential for all 30 plates.
    """
    clean = [r for r in results if not r['is_outlier']]
    plate_data = defaultdict(dict)
    for r in clean:
        plate_data[r['plate']][r['material']] = r['pct_change']

    details = []
    for plate, mat_pcts in plate_data.items():
        nd = [mat_pcts[m] for m in ['N42EH', 'N52SH'] if m in mat_pcts]
        sm = [mat_pcts[m] for m in ['SmCo33H', 'SmCo35'] if m in mat_pcts]
        if nd and sm:
            details.append({
                'plate': plate,
                'region': PLACEMENTS.get(plate, 'Unknown'),
                'diff': np.mean(nd) - np.mean(sm),
            })

    if not details:
        print("  Plot 13: SKIPPED")
        return

    details.sort(key=lambda d: d['diff'])

    fig, ax = plt.subplots(figsize=(10, 8))

    y_pos = np.arange(len(details))
    colors = []
    labels = []
    for d in details:
        region = d['region']
        if 'Arc' in region:
            colors.append('#CC4444')
        elif 'Linac' in region:
            colors.append('#4444CC')
        else:
            colors.append('#888888')
        labels.append('Plate %d (%s)' % (d['plate'], region))

    ax.barh(y_pos, [d['diff'] for d in details], color=colors,
            edgecolor='none', height=0.7, alpha=0.8)
    ax.axvline(0, color='black', linewidth=1)

    # Add mean line
    mean_val = np.mean([d['diff'] for d in details])
    ax.axvline(mean_val, color='#8B0000', linewidth=2, linestyle='--',
               label='Mean: %+.3f%%' % mean_val)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel('NdFeB \u2212 SmCo Differential (% change from pre-deployment baseline)',
                  fontsize=11)
    ax.set_title('Per-Plate Gain-Immune Degradation Differential (all 30 plates)\n'
                 '(sorted by magnitude; red=arc, blue=linac, gray=labyrinth)',
                 fontsize=13, fontweight='bold')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)

    handles = [mpatches.Patch(color='#CC4444', label='Arc (higher dose)'),
               mpatches.Patch(color='#4444CC', label='Linac (lower dose)'),
               mpatches.Patch(color='#888888', label='Labyrinth')]
    ax.legend(handles=handles, fontsize=10, loc='lower right')

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, '13_double_ratio_waterfall.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 13: Double ratio waterfall")


# ─── Plot 14: Updated Dashboard ──────────────────────────────────────────────

def plot_dashboard_v2(results, helm_raw, temp_final):
    """One-page dashboard incorporating gain systematic analysis."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    # Compute key numbers
    session_offsets = compute_gain_variability(helm_raw)
    if session_offsets:
        gain_offsets = [session_offsets[d]['mean'] for d in session_offsets]
        gain_syst = (max(gain_offsets) - min(gain_offsets)) / 2.0
    else:
        gain_syst = 0.3

    ndfeb_vals = [r['pct_change'] for r in clean
                  if r['material'] in ['N42EH', 'N52SH']]
    smco_vals = [r['pct_change'] for r in clean
                 if r['material'] in ['SmCo33H', 'SmCo35']]

    # Intra-plate differential
    plate_diffs = defaultdict(dict)
    for r in clean:
        plate_diffs[r['plate']][r['material']] = r['pct_change']
    intra_diffs = []
    for plate, mat_pcts in plate_diffs.items():
        nd = [mat_pcts[m] for m in ['N42EH', 'N52SH'] if m in mat_pcts]
        sm = [mat_pcts[m] for m in ['SmCo33H', 'SmCo35'] if m in mat_pcts]
        if nd and sm:
            intra_diffs.append(np.mean(nd) - np.mean(sm))

    # Double ratio time series
    ref_date = '2025-08-27'
    dr_dates = ['2025-07-17', '2025-07-30', '2025-10-21', '2026-01-08', '2026-01-12']

    fig = plt.figure(figsize=(18, 11))
    fig.suptitle('LDRD FFA@CEBAF Magnet Radiation Study \u2014 Updated Preliminary Results (v2)\n'
                 'Incorporating Helmholtz gain systematic analysis',
                 fontsize=15, fontweight='bold', y=0.99)

    # ─── Panel A: Absolute values with systematic ─────────────────
    ax1 = fig.add_subplot(2, 3, 1)
    for i, mat in enumerate(materials):
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        m = np.mean(vals)
        s = np.std(vals, ddof=1) / np.sqrt(len(vals))
        ax1.bar(i, m, yerr=s, color=MAT_COLORS[mat], capsize=5,
                edgecolor='black', linewidth=0.5, alpha=0.85, width=0.6,
                error_kw=dict(linewidth=1.5))
        ax1.fill_between([i-0.3, i+0.3], [m-gain_syst]*2, [m+gain_syst]*2,
                         alpha=0.12, color='gray', zorder=0)
    ax1.axhline(0, color='black', linewidth=1)
    ax1.set_xticks(range(4))
    ax1.set_xticklabels([MAT_LABELS[m] for m in materials], fontsize=8)
    ax1.set_ylabel('% Change', fontsize=9)
    ax1.set_title('(a) Absolute Degradation\n(gray = gain syst. \u00b1%.2f%%)' % gain_syst,
                  fontsize=10, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # ─── Panel B: Gain-immune differential ─────────────────
    ax2 = fig.add_subplot(2, 3, 2)
    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    ax2.bar(0, diff_mean, yerr=diff_sem, color='#8B0000', capsize=8,
            edgecolor='black', linewidth=1, alpha=0.85, width=0.5,
            error_kw=dict(linewidth=2, capthick=2))
    ax2.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax2.set_xticks([0])
    ax2.set_xticklabels(['NdFeB \u2212 SmCo\n(intra-plate)'], fontsize=9)
    ax2.set_ylabel('% Differential', fontsize=9)
    ax2.set_title('(b) Gain-Immune Result\n%+.3f%% \u00b1 %.3f%% (%.1f\u03c3)' %
                  (diff_mean, diff_sem, diff_sig),
                  fontsize=10, fontweight='bold')
    ax2.text(0, diff_mean + diff_sem + 0.01,
             'NO gain systematic\nN = %d plates' % len(intra_diffs),
             ha='center', fontsize=8, color='#006600', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_ylim(-0.5, 0.15)

    # ─── Panel C: Double ratio time series ─────────────────
    ax3 = fig.add_subplot(2, 3, 3)
    for cd in dr_dates:
        diffs_list, _ = compute_double_ratio(helm_raw, temp_final, ref_date, cd)
        if diffs_list:
            m = np.mean(diffs_list)
            s = np.std(diffs_list) / np.sqrt(len(diffs_list))
            dt = datetime.strptime(cd, '%Y-%m-%d')
            color = '#FF6600' if cd == '2025-10-21' else '#8B0000'
            ax3.errorbar([dt], [m], yerr=[s], marker='D', markersize=7,
                         color=color, capsize=4, capthick=1.5, linewidth=0,
                         elinewidth=1.5)
    # Reference point
    ax3.plot(datetime.strptime(ref_date, '%Y-%m-%d'), 0, 'D',
             color='#8B0000', markersize=9, markeredgecolor='gold',
             markeredgewidth=2)
    ax3.axhline(0, color='black', linewidth=1, linestyle='--')
    ax3.axvline(datetime(2025, 10, 21), color='gray', linewidth=1, linestyle=':')
    ax3.set_ylabel('NdFeB\u2212SmCo (%)', fontsize=9)
    ax3.set_title('(c) Differential Over Time\n(orange = thermal lag suspect)',
                  fontsize=10, fontweight='bold')
    ax3.grid(alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

    # ─── Panel D: Regional double ratio (baseline approach, all 30 plates) ───
    ax4 = fig.add_subplot(2, 3, 4)
    # Use baseline-to-latest per-plate differential for full coverage
    plate_data_d = defaultdict(dict)
    for r in clean:
        plate_data_d[r['plate']][r['material']] = r['pct_change']
    details_d = []
    for plate, mat_pcts in plate_data_d.items():
        nd = [mat_pcts[m] for m in ['N42EH', 'N52SH'] if m in mat_pcts]
        sm = [mat_pcts[m] for m in ['SmCo33H', 'SmCo35'] if m in mat_pcts]
        if nd and sm:
            details_d.append({'plate': plate, 'region': PLACEMENTS.get(plate, 'Unknown'),
                              'diff': np.mean(nd) - np.mean(sm)})
    if details_d:
        region_order = ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc',
                        'North Linac', 'South Linac', 'Labyrinth']
        region_diffs = defaultdict(list)
        for d in details_d:
            region_diffs[d['region']].append(d['diff'])

        idx = 0
        for region in region_order:
            vals = region_diffs.get(region, [])
            if vals:
                color = '#CC4444' if 'Arc' in region else '#4444CC' if 'Linac' in region else '#888888'
                ax4.bar(idx, np.mean(vals),
                        yerr=np.std(vals)/np.sqrt(len(vals)) if len(vals) > 1 else 0.05,
                        color=color, capsize=4, edgecolor='black',
                        linewidth=0.5, alpha=0.85, width=0.6)
                idx += 1

        ax4.axhline(0, color='black', linewidth=1, linestyle='--')
        ax4.set_xticks(range(idx))
        short_names = [r.replace(' Arc', '').replace(' Linac', ' Lin')
                       for r in region_order if region_diffs.get(r)]
        ax4.set_xticklabels(short_names, fontsize=8, rotation=30)
    ax4.set_ylabel('NdFeB\u2212SmCo (%)', fontsize=9)
    ax4.set_title('(d) By Region (gain-immune)\nRed=arc, blue=linac',
                  fontsize=10, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)

    # ─── Panel E: Gain systematic visualization ─────────────────
    ax5 = fig.add_subplot(2, 3, 5)
    if session_offsets:
        dates = sorted(session_offsets.keys())
        dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        off_means = [session_offsets[d]['mean'] for d in dates]
        off_sems = [session_offsets[d]['sem'] for d in dates]
        ax5.errorbar(dt_objs, off_means, yerr=off_sems, marker='s',
                     markersize=6, color='#333', linewidth=1.5, capsize=4)
        ax5.axhline(0, color='black', linewidth=1, linestyle='--')
        spread = max(off_means) - min(off_means)
        ax5.axhspan(min(off_means)-0.05, max(off_means)+0.05,
                     alpha=0.08, color='red')
        ax5.text(dt_objs[len(dt_objs)//2], max(off_means)+0.1,
                 'Spread: %.2f%%' % spread, fontsize=9, ha='center',
                 color='#AA0000', fontweight='bold')
    ax5.set_ylabel('% offset from Nov 2024', fontsize=9)
    ax5.set_title('(e) Helmholtz Gain Variability\n(pre-deployment lab data)',
                  fontsize=10, fontweight='bold')
    ax5.grid(alpha=0.3)
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

    # ─── Panel F: Summary table ─────────────────
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.axis('off')

    table_data = [
        ['NdFeB (abs)', '%+.3f%%' % np.mean(ndfeb_vals),
         '\u00b1%.3f%%(stat)\n\u00b1%.2f%%(syst)' % (
             np.std(ndfeb_vals,ddof=1)/np.sqrt(len(ndfeb_vals)), gain_syst),
         '%d' % len(ndfeb_vals)],
        ['SmCo (abs)', '%+.3f%%' % np.mean(smco_vals),
         '\u00b1%.3f%%(stat)\n\u00b1%.2f%%(syst)' % (
             np.std(smco_vals,ddof=1)/np.sqrt(len(smco_vals)), gain_syst),
         '%d' % len(smco_vals)],
        ['', '', '', ''],
        ['NdFeB\u2212SmCo\n(gain-immune)', '%+.3f%%' % diff_mean,
         '\u00b1%.3f%%\n(%.1f\u03c3)' % (diff_sem, diff_sig),
         '%d plates' % len(intra_diffs)],
    ]
    headers = ['Metric', 'Value', 'Uncertainty', 'N']

    table = ax6.table(cellText=table_data, colLabels=headers,
                      loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.0)

    for j in range(len(headers)):
        table[0, j].set_facecolor('#CCCCCC')
        table[0, j].set_text_props(fontweight='bold')
    table[1, 0].set_facecolor('#CC444422')
    table[2, 0].set_facecolor('#44AA4422')
    table[4, 0].set_facecolor('#8B000022')
    table[4, 1].set_facecolor('#8B000022')
    table[4, 2].set_facecolor('#8B000022')
    table[4, 3].set_facecolor('#8B000022')

    ax6.set_title('(f) Key Results', fontsize=10, fontweight='bold', pad=15)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(PLOT_DIR, '14_dashboard_v2.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 14: Dashboard v2")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Manager Summary v2: With Helmholtz Gain Systematic Analysis")
    print("=" * 60)
    print()
    print("Loading data...")
    results, helm_raw, temp_final, y_materials = load_all()
    clean = [r for r in results if not r['is_outlier']]
    print("  %d samples (%d outliers excluded)" % (len(clean), len(results) - len(clean)))

    # Print key numbers for verification
    ndfeb = [r['pct_change'] for r in clean if r['material'] in ['N42EH', 'N52SH']]
    smco = [r['pct_change'] for r in clean if r['material'] in ['SmCo33H', 'SmCo35']]
    print("\n--- VERIFICATION: Absolute values (same as v1) ---")
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals))
            print("  %s: %+.3f%% +/- %.3f%% (%.1f sig, N=%d)" %
                  (mat, m, s, abs(m/s), len(vals)))

    # Compute gain systematic
    session_offsets = compute_gain_variability(helm_raw)
    if session_offsets:
        print("\n--- Helmholtz gain variability (pre-deployment lab) ---")
        for d in sorted(session_offsets):
            so = session_offsets[d]
            print("  %s: %+.3f%% +/- %.3f%% (N=%d)" %
                  (d, so['mean'], so['sem'], so['n']))
        offsets = [session_offsets[d]['mean'] for d in session_offsets]
        print("  Range: %.3f%% to %.3f%% (spread=%.3f%%)" %
              (min(offsets), max(offsets), max(offsets)-min(offsets)))

    # Compute gain-immune double ratio
    print("\n--- Gain-immune double ratio (Aug 27 -> Jan 12) ---")
    diffs, details = compute_double_ratio(helm_raw, temp_final, '2025-08-27', '2026-01-12')
    if diffs:
        m = np.mean(diffs)
        s = np.std(diffs) / np.sqrt(len(diffs))
        print("  NdFeB - SmCo: %+.3f%% +/- %.3f%% (%.1f sig, N=%d plates)" %
              (m, s, abs(m/s), len(diffs)))

    # Also compute using intra-plate from baseline
    plate_diffs_bl = defaultdict(dict)
    for r in clean:
        plate_diffs_bl[r['plate']][r['material']] = r['pct_change']
    intra_diffs = []
    for plate, mat_pcts in plate_diffs_bl.items():
        nd = [mat_pcts[m] for m in ['N42EH', 'N52SH'] if m in mat_pcts]
        sm = [mat_pcts[m] for m in ['SmCo33H', 'SmCo35'] if m in mat_pcts]
        if nd and sm:
            intra_diffs.append(np.mean(nd) - np.mean(sm))
    if intra_diffs:
        m = np.mean(intra_diffs)
        s = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
        print("  Intra-plate (baseline->latest): %+.3f%% +/- %.3f%% (%.1f sig, N=%d)" %
              (m, s, abs(m/s), len(intra_diffs)))

    print("\nGenerating v2 plots (numbered 8-14)...")
    print("NOTE: Original plots 1-7 are PRESERVED (not overwritten).")
    print()
    plot_gain_variability(helm_raw)
    plot_double_ratio_timeseries(helm_raw, temp_final)
    plot_material_comparison_v2(results, helm_raw)
    plot_regional_double_ratio(helm_raw, temp_final, results)
    plot_thermal_lag(helm_raw, temp_final)
    plot_double_ratio_waterfall(helm_raw, temp_final, results)
    plot_dashboard_v2(results, helm_raw, temp_final)

    print("\nAll v2 plots saved to: %s/" % PLOT_DIR)
    print("Original v1 plots (1-7) are unchanged.")


if __name__ == '__main__':
    main()
