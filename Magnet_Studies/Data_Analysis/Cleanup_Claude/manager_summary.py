#!/usr/bin/env python3
"""
Manager-Friendly Degradation Summary Plots

Creates clear, presentation-ready plots for management review.
All Helmholtz readings temperature-corrected to 20°C reference.

Output: Cleanup_Claude/Manager_Plots/
"""

import os
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
    'NdFeB': -0.00105, 'SmCo': -0.0004,
}
TUNNEL_START = datetime(2025, 7, 1)
MIN_BASELINE = 0.1
FLAGGED = {'Y-34-4', 'Y-40-4'}

# Colors — colorblind-safe palette
MAT_COLORS = {
    'N42EH': '#D62728', 'N52SH': '#1F77B4',
    'SmCo33H': '#2CA02C', 'SmCo35': '#FF7F0E',
}
MAT_LABELS = {
    'N42EH': 'NdFeB N42EH', 'N52SH': 'NdFeB N52SH',
    'SmCo33H': 'SmCo 33H', 'SmCo35': 'SmCo 35',
}
REGION_ORDER = ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc',
                'North Linac', 'South Linac', 'Labyrinth']

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
            dt = datetime.strptime(f"{dm.group(1)} {dm.group(2)}", "%Y-%m-%d %H:%M:%S")
            rows.append((dt, val, unit))
    return rows


def parse_teslameter_file(filepath):
    rows = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = re.match(r'(\d{4}-\d{2}-\d{2})\t(\d{2}:\d{2}:\d{2})\t(.*)', line)
            if m:
                dt = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M:%S")
                rest = m.group(3)
            else:
                m = re.match(r'(\d{4}-\d{2}-\d{2})-(\d{2}:\d{2}:\d{2})\t(.*)', line)
                if m:
                    dt = datetime.strptime(f"{m.group(1)} {m.group(2)}",
                                           "%Y-%m-%d %H:%M:%S")
                    rest = m.group(3)
                else:
                    continue
            nums = re.findall(r'(-?\d+\.\d+)', rest)
            if len(nums) >= 4:
                rows.append((dt, [float(x) for x in nums[:3]], float(nums[3])))
    return rows


# ─── Load data ────────────────────────────────────────────────────────────────

def load_all():
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
                y_materials[f'Y-{pn}-{i}'] = str(v).strip()

    # Temperature lookup from Teslameter
    y_tesla_dir = os.path.join(BASE, 'Y_Plates', 'Teslameter')
    temp_lookup = defaultdict(list)
    for f in os.listdir(y_tesla_dir):
        m = re.match(r'(Y-\d+-\d+)_(front|side|top)\.dat$', f)
        if not m:
            continue
        sample = m.group(1)
        rows = parse_teslameter_file(os.path.join(y_tesla_dir, f))
        for dt, fields, temp in rows:
            if temp is None:
                continue
            temp_lookup[(sample, dt.strftime('%Y-%m-%d'))].append(temp)

    temp_final = {}
    for key, temps in temp_lookup.items():
        temp_final[key] = (np.mean(temps),
                           np.std(temps, ddof=1) if len(temps) > 1 else 0.5)

    # Helmholtz degradation per sample
    helm_dir = os.path.join(BASE, 'Y_Plates', 'Helmholtz')
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
        region = PLACEMENTS.get(plate_num, 'Unknown')
        is_outlier = sample in FLAGGED

        rows = parse_helmholtz_file(os.path.join(helm_dir, f))
        mwc = [(dt, v) for dt, v, u in rows
               if u == 'mWC' and abs(v - SENTINEL) > 1 and abs(v) >= MIN_BASELINE]

        # Temperature-corrected
        pre_corr = []
        tunnel_series = []  # (dt, h_corr)
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

        # Per-date pct changes for time series
        date_pcts = []
        for dt, h_corr in tunnel_series:
            date_pcts.append((dt, (h_corr - bl_mean) / bl_mean * 100.0))

        bl_sem = (np.std(pre_corr, ddof=1) / np.sqrt(len(pre_corr))
                  if len(pre_corr) > 1 else 0.01 * bl_mean)

        results.append({
            'sample': sample, 'plate': plate_num,
            'material': mat, 'region': region,
            'pct_change': pct, 'bl_mean': bl_mean,
            'bl_sem_pct': bl_sem / abs(bl_mean) * 100.0,
            'is_outlier': is_outlier,
            'date_pcts': date_pcts,
        })

    return results, y_materials


# ─── Plot 1: The "Money Plot" — Material Comparison ──────────────────────────

def plot_material_comparison(results):
    """Simple bar chart: mean % degradation by material grade."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig, ax = plt.subplots(figsize=(10, 6))

    means, sems, colors, labels = [], [], [], []
    for mat in materials:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        if not vals:
            continue
        m = np.mean(vals)
        sem = np.std(vals, ddof=1) / np.sqrt(len(vals))
        sig = abs(m / sem) if sem > 0 else 0
        means.append(m)
        sems.append(sem)
        colors.append(MAT_COLORS[mat])
        sig_str = f'({sig:.0f}σ)' if sig >= 2 else '(n.s.)'
        labels.append(f'{MAT_LABELS[mat]}\n{m:+.2f} ± {sem:.2f}%\n{sig_str}\nN={len(vals)}')

    x = np.arange(len(labels))
    bars = ax.bar(x, means, yerr=sems, color=colors, capsize=8,
                  edgecolor='black', linewidth=0.8, alpha=0.85, width=0.6,
                  error_kw=dict(linewidth=2, capthick=2))

    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel('% Change from Baseline\n(temperature-corrected to 20°C)',
                  fontsize=12)
    ax.set_title('Magnet Degradation by Material Grade\n'
                 'CEBAF Tunnel Exposure: Jul 2025 – Jan 2026',
                 fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(-0.45, 0.15)

    # Add significance annotation
    ax.annotate('NdFeB grades show\nstatistically significant\ndegradation',
                xy=(0.5, means[0] - sems[0] - 0.02),
                xytext=(1.5, -0.38),
                fontsize=10, ha='center',
                arrowprops=dict(arrowstyle='->', color='#555'),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                          edgecolor='gray'))
    ax.annotate('SmCo grades are\nstable (no significant\ndegradation)',
                xy=(2.5, 0.02),
                xytext=(2.5, 0.10),
                fontsize=10, ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen',
                          edgecolor='gray', alpha=0.7))

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, '1_material_comparison.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 1: Material comparison")


# ─── Plot 2: NdFeB vs SmCo side by side ──────────────────────────────────────

def plot_ndfeb_vs_smco(results):
    """Two-material grouped comparison — the simplest view."""
    clean = [r for r in results if not r['is_outlier']]
    ndfeb = [r['pct_change'] for r in clean if r['material'] in ['N42EH', 'N52SH']]
    smco = [r['pct_change'] for r in clean if r['material'] in ['SmCo33H', 'SmCo35']]

    fig, ax = plt.subplots(figsize=(8, 6))

    groups = ['NdFeB\n(N42EH + N52SH)', 'SmCo\n(SmCo33H + SmCo35)']
    means = [np.mean(ndfeb), np.mean(smco)]
    sems = [np.std(ndfeb, ddof=1)/np.sqrt(len(ndfeb)),
            np.std(smco, ddof=1)/np.sqrt(len(smco))]
    colors = ['#CC4444', '#44AA44']

    bars = ax.bar([0, 1], means, yerr=sems, color=colors, capsize=10,
                  edgecolor='black', linewidth=1, alpha=0.85, width=0.5,
                  error_kw=dict(linewidth=2.5, capthick=2.5))

    for i, (m, s, n) in enumerate(zip(means, sems, [len(ndfeb), len(smco)])):
        sig = abs(m / s)
        ax.text(i, m - s - 0.025, f'{m:+.3f}%\n±{s:.3f}%\nN={n}',
                ha='center', va='top', fontsize=12, fontweight='bold')

    ax.axhline(0, color='black', linewidth=1.5)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(groups, fontsize=13)
    ax.set_ylabel('% Change from Baseline', fontsize=13)
    ax.set_title('NdFeB vs SmCo: Radiation Degradation Comparison\n'
                 'CEBAF Tunnel, Jul 2025 – Jan 2026',
                 fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(-0.40, 0.15)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, '2_ndfeb_vs_smco.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 2: NdFeB vs SmCo")


# ─── Plot 3: Regional comparison ─────────────────────────────────────────────

def plot_regional(results):
    """Grouped bar: degradation by tunnel region, colored by material."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    regions = ['NE Arc', 'SW Arc', 'NW Arc', 'SE Arc',
               'North Linac', 'South Linac', 'Labyrinth']

    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(regions))
    width = 0.18
    offsets = [-1.5, -0.5, 0.5, 1.5]

    for i, mat in enumerate(materials):
        means, errs = [], []
        for region in regions:
            vals = [r['pct_change'] for r in clean
                    if r['region'] == region and r['material'] == mat]
            if vals:
                means.append(np.mean(vals))
                errs.append(np.std(vals, ddof=1)/np.sqrt(len(vals))
                            if len(vals) > 1 else 0.05)
            else:
                means.append(0)
                errs.append(0)
        ax.bar(x + offsets[i] * width, means, width, yerr=errs,
               color=MAT_COLORS[mat], capsize=3, alpha=0.85,
               edgecolor='black', linewidth=0.5,
               label=MAT_LABELS[mat])

    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=11)
    ax.set_ylabel('% Change from Baseline', fontsize=12)
    ax.set_title('Degradation by Tunnel Region and Material\n'
                 '(Temperature-corrected to 20°C; outliers excluded)',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='lower left')
    ax.grid(axis='y', alpha=0.3)

    # Add dose context annotation
    ax.axvspan(-0.5, 3.5, alpha=0.05, color='red')
    ax.axvspan(3.5, 5.5, alpha=0.05, color='blue')
    ax.axvspan(5.5, 6.5, alpha=0.05, color='green')
    ax.text(1.5, ax.get_ylim()[1] * 0.95, 'Arcs (higher dose)',
            ha='center', fontsize=10, fontstyle='italic', color='#AA0000')
    ax.text(4.5, ax.get_ylim()[1] * 0.95, 'Linacs (lower dose)',
            ha='center', fontsize=10, fontstyle='italic', color='#0000AA')
    ax.text(6, ax.get_ylim()[1] * 0.95, 'Control',
            ha='center', fontsize=10, fontstyle='italic', color='#006600')

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, '3_regional_comparison.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 3: Regional comparison")


# ─── Plot 4: Arc vs Linac vs Labyrinth ───────────────────────────────────────

def plot_arc_vs_linac(results):
    """Grouped bar: Arc (high dose) vs Linac (low dose) vs Labyrinth (control)."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    groups = {
        'Arcs\n(higher radiation)': ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc'],
        'Linacs\n(lower radiation)': ['North Linac', 'South Linac'],
        'Labyrinth\n(low dose)': ['Labyrinth'],
    }

    fig, ax = plt.subplots(figsize=(12, 7))
    group_names = list(groups.keys())
    x = np.arange(len(group_names))
    width = 0.18
    offsets = [-1.5, -0.5, 0.5, 1.5]

    for i, mat in enumerate(materials):
        means, errs, ns = [], [], []
        for gname, regions in groups.items():
            vals = [r['pct_change'] for r in clean
                    if r['region'] in regions and r['material'] == mat]
            if vals:
                means.append(np.mean(vals))
                errs.append(np.std(vals, ddof=1)/np.sqrt(len(vals))
                            if len(vals) > 1 else 0.05)
                ns.append(len(vals))
            else:
                means.append(0)
                errs.append(0)
                ns.append(0)
        bars = ax.bar(x + offsets[i] * width, means, width, yerr=errs,
                      color=MAT_COLORS[mat], capsize=4, alpha=0.85,
                      edgecolor='black', linewidth=0.5,
                      label=MAT_LABELS[mat])

    ax.axhline(0, color='black', linewidth=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(group_names, fontsize=12)
    ax.set_ylabel('% Change from Baseline', fontsize=13)
    ax.set_title('Dose-Dependent Degradation: Arcs vs Linacs vs Control\n'
                 'NdFeB shows larger degradation in higher-dose arc regions',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, '4_arc_vs_linac.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 4: Arc vs Linac vs Labyrinth")


# ─── Plot 5: Time series ─────────────────────────────────────────────────────

def plot_timeseries(results):
    """Mean degradation over time by material.

    Uses dates with >=10 samples per material to ensure statistics.
    Jul 17 and Jul 30 campaigns measured different plate groups, so both
    are shown but the key comparison is Aug 27 onwards (all 30 plates).
    """
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig, ax = plt.subplots(figsize=(12, 6))

    for mat in materials:
        date_vals = defaultdict(list)
        for r in clean:
            if r['material'] != mat:
                continue
            for dt, pct in r['date_pcts']:
                date_vals[dt.strftime('%Y-%m-%d')].append(pct)

        if not date_vals:
            continue

        dates = sorted(d for d in date_vals if len(date_vals[d]) >= 10)
        if not dates:
            dates = sorted(d for d in date_vals if len(date_vals[d]) >= 5)
        if not dates:
            continue

        dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        means_list = [np.mean(date_vals[d]) for d in dates]
        sems = [np.std(date_vals[d], ddof=1)/np.sqrt(len(date_vals[d]))
                if len(date_vals[d]) > 1 else 0.05 for d in dates]

        ax.errorbar(dt_objs, means_list, yerr=sems,
                    color=MAT_COLORS[mat], marker='o', markersize=7,
                    linewidth=2.5, capsize=5, capthick=2,
                    label=MAT_LABELS[mat])

    ax.axhline(0, color='black', linewidth=1, linestyle='--')

    # Beam OFF marker
    ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1.5,
               linestyle=':', alpha=0.7)
    ylims = ax.get_ylim()
    ax.text(datetime(2025, 10, 23), ylims[1] * 0.85,
            'Beam OFF\n(Oct 21)', fontsize=9, color='gray',
            ha='left', va='top')

    # Annotate the Jul 17/30 group systematic
    ax.annotate('Jul campaigns:\ndifferent plate\nsubsets measured',
                xy=(datetime(2025, 7, 20), -0.8),
                xytext=(datetime(2025, 8, 15), -1.1),
                fontsize=8, color='gray', ha='center',
                arrowprops=dict(arrowstyle='->', color='gray', lw=0.8),
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                          edgecolor='gray', alpha=0.8))

    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(datetime(2025, 6, 15), datetime(2026, 2, 1))

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('% Change from Pre-Deployment Baseline', fontsize=12)
    ax.set_title('Magnet Degradation Over Time\n'
                 '(Temperature-corrected Helmholtz coil measurements)',
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='lower left')
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, '5_timeseries.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 5: Time series")


# ─── Plot 6: Individual sample waterfall ──────────────────────────────────────

def plot_waterfall(results):
    """All individual samples sorted by degradation magnitude."""
    clean = [r for r in results if not r['is_outlier']]
    clean.sort(key=lambda r: r['pct_change'])

    fig, ax = plt.subplots(figsize=(10, 16))

    y_pos = np.arange(len(clean))
    colors = [MAT_COLORS[r['material']] for r in clean]
    pcts = [r['pct_change'] for r in clean]
    labels = [f"Y-{r['plate']:02d}-{r['sample'].split('-')[2]} "
              f"({r['material']})"
              for r in clean]

    ax.barh(y_pos, pcts, color=colors, edgecolor='none', height=0.7, alpha=0.8)
    ax.axvline(0, color='black', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=6)
    ax.set_xlabel('% Change from Baseline', fontsize=12)
    ax.set_title('All Y-Plate Samples: Individual Degradation\n'
                 '(sorted by magnitude)',
                 fontsize=14, fontweight='bold')

    # Legend
    handles = [mpatches.Patch(color=MAT_COLORS[m], label=MAT_LABELS[m])
               for m in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']]
    ax.legend(handles=handles, fontsize=10, loc='lower right')
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, '6_all_samples_waterfall.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 6: All samples waterfall")


# ─── Plot 7: Summary dashboard ───────────────────────────────────────────────

def plot_dashboard(results):
    """One-page dashboard combining key findings."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('LDRD FFA@CEBAF Magnet Radiation Study — Preliminary Results\n'
                 'CEBAF Tunnel Exposure: July 2025 – January 2026',
                 fontsize=16, fontweight='bold', y=0.98)

    # Panel A: Material comparison
    ax1 = fig.add_subplot(2, 2, 1)
    means, sems, cols = [], [], []
    for mat in materials:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        means.append(np.mean(vals))
        sems.append(np.std(vals, ddof=1)/np.sqrt(len(vals)))
        cols.append(MAT_COLORS[mat])
    ax1.bar(range(4), means, yerr=sems, color=cols, capsize=6,
            edgecolor='black', linewidth=0.5, alpha=0.85, width=0.6)
    ax1.axhline(0, color='black', linewidth=1)
    ax1.set_xticks(range(4))
    ax1.set_xticklabels([MAT_LABELS[m] for m in materials], fontsize=9)
    ax1.set_ylabel('% Change', fontsize=10)
    ax1.set_title('(a) Degradation by Material', fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # Panel B: NdFeB vs SmCo
    ax2 = fig.add_subplot(2, 2, 2)
    ndfeb = [r['pct_change'] for r in clean
             if r['material'] in ['N42EH', 'N52SH']]
    smco = [r['pct_change'] for r in clean
            if r['material'] in ['SmCo33H', 'SmCo35']]
    groups = ['Arcs\n(high dose)', 'Linacs\n(low dose)', 'Labyrinth\n(low dose)']
    arc_r = ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc']
    lin_r = ['North Linac', 'South Linac']
    lab_r = ['Labyrinth']

    for i, (gname, regs) in enumerate(zip(groups, [arc_r, lin_r, lab_r])):
        nd = [r['pct_change'] for r in clean
              if r['region'] in regs and r['material'] in ['N42EH', 'N52SH']]
        sm = [r['pct_change'] for r in clean
              if r['region'] in regs and r['material'] in ['SmCo33H', 'SmCo35']]
        if nd:
            ax2.bar(i - 0.15, np.mean(nd), 0.28,
                    yerr=np.std(nd, ddof=1)/np.sqrt(len(nd)),
                    color='#CC4444', capsize=4, edgecolor='black',
                    linewidth=0.5, alpha=0.85)
        if sm:
            ax2.bar(i + 0.15, np.mean(sm), 0.28,
                    yerr=np.std(sm, ddof=1)/np.sqrt(len(sm)) if len(sm) > 1 else 0.05,
                    color='#44AA44', capsize=4, edgecolor='black',
                    linewidth=0.5, alpha=0.85)
    ax2.axhline(0, color='black', linewidth=1)
    ax2.set_xticks(range(3))
    ax2.set_xticklabels(groups, fontsize=9)
    ax2.set_ylabel('% Change', fontsize=10)
    ax2.set_title('(b) NdFeB (red) vs SmCo (green) by Dose Region',
                  fontsize=12, fontweight='bold')
    ax2.legend([mpatches.Patch(color='#CC4444'), mpatches.Patch(color='#44AA44')],
               ['NdFeB', 'SmCo'], fontsize=9)
    ax2.grid(axis='y', alpha=0.3)

    # Panel C: Time series (filtered to dates with >=15 samples)
    ax3 = fig.add_subplot(2, 2, 3)
    for mat in materials:
        date_vals = defaultdict(list)
        for r in clean:
            if r['material'] != mat:
                continue
            for dt, pct in r['date_pcts']:
                date_vals[dt.strftime('%Y-%m-%d')].append(pct)
        if not date_vals:
            continue
        dates = sorted(d for d in date_vals if len(date_vals[d]) >= 10)
        if not dates:
            dates = sorted(d for d in date_vals if len(date_vals[d]) >= 5)
        if not dates:
            continue
        dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        means = [np.mean(date_vals[d]) for d in dates]
        ax3.plot(dt_objs, means, 'o-', color=MAT_COLORS[mat], markersize=4,
                 linewidth=1.5, label=MAT_LABELS[mat])
    ax3.axhline(0, color='black', linewidth=1, linestyle='--')
    ax3.axvline(datetime(2025, 10, 21), color='gray', linewidth=1, linestyle=':')
    ax3.set_ylabel('% Change', fontsize=10)
    ax3.set_title('(c) Degradation Over Time', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=8, loc='lower left')
    ax3.grid(alpha=0.3)
    fig.autofmt_xdate()

    # Panel D: Key numbers table
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')
    table_data = []
    headers = ['Material', 'Mean Δ (%)', '± Unc (%)', 'Significance', 'N']
    for mat in materials:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        m = np.mean(vals)
        sem = np.std(vals, ddof=1) / np.sqrt(len(vals))
        sig = abs(m / sem)
        sig_label = f'{sig:.0f}σ' if sig >= 2 else 'n.s.'
        table_data.append([MAT_LABELS[mat], f'{m:+.3f}', f'±{sem:.3f}',
                          sig_label, str(len(vals))])

    # Add combined NdFeB/SmCo rows
    table_data.append(['', '', '', '', ''])
    m_nd, m_sm = np.mean(ndfeb), np.mean(smco)
    s_nd = np.std(ndfeb, ddof=1)/np.sqrt(len(ndfeb))
    s_sm = np.std(smco, ddof=1)/np.sqrt(len(smco))
    table_data.append(['All NdFeB', f'{m_nd:+.3f}', f'±{s_nd:.3f}',
                      f'{abs(m_nd/s_nd):.0f}σ', str(len(ndfeb))])
    table_data.append(['All SmCo', f'{m_sm:+.3f}', f'±{s_sm:.3f}',
                      f'{abs(m_sm/s_sm):.0f}σ' if abs(m_sm/s_sm) >= 2 else 'n.s.',
                      str(len(smco))])

    table = ax4.table(cellText=table_data, colLabels=headers,
                      loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.6)

    # Color the cells
    for i in range(len(table_data)):
        for j in range(len(headers)):
            cell = table[i + 1, j]
            if i < 4:
                cell.set_facecolor(MAT_COLORS[materials[i]] + '22')
            elif i == 5:
                cell.set_facecolor('#CC444422')
            elif i == 6:
                cell.set_facecolor('#44AA4422')
    for j in range(len(headers)):
        table[0, j].set_facecolor('#CCCCCC')
        table[0, j].set_text_props(fontweight='bold')

    ax4.set_title('(d) Summary Statistics', fontsize=12, fontweight='bold',
                  pad=20)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(PLOT_DIR, '7_dashboard.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  Plot 7: Dashboard")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    results, y_materials = load_all()
    clean = [r for r in results if not r['is_outlier']]
    print(f"  {len(clean)} samples (excl. {len(results)-len(clean)} outliers)")

    print("\nGenerating manager-friendly plots...")
    plot_material_comparison(results)
    plot_ndfeb_vs_smco(results)
    plot_regional(results)
    plot_arc_vs_linac(results)
    plot_timeseries(results)
    plot_waterfall(results)
    plot_dashboard(results)

    print(f"\nAll plots saved to: {PLOT_DIR}/")


if __name__ == '__main__':
    main()
