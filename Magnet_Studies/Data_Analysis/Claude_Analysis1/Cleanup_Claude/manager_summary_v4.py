#!/usr/bin/env python3
"""
Manager-Friendly Degradation Summary Plots — Version 4
Per-Face Teslameter Re-Analysis + Combined Instrument Comparison

Key questions:
  1. Does the intra-plate NdFeB-SmCo differential appear in ANY Teslameter face?
  2. Do session-to-session deltas correlate between instruments?
  3. Is per-face scatter consistent with rig tolerance?
  4. Does any Teslameter face time series track the Helmholtz trend?
  5. Does face-to-face correlation reveal physics or just noise?

Output: Cleanup_Claude/Manager_Plots_v4/v4_*.png (12 plots)
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

# Import shared code from v3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manager_summary_v3 import (
    parse_helmholtz_file, parse_teslameter_file,
    load_all, get_gain_syst, compute_intra_plate_diffs,
    compute_double_ratio, compute_gain_variability,
    BASE, T_REF, SENTINEL, ALPHA, ALPHA_SLOT, MAT_BY_SLOT,
    TUNNEL_START, TESLAMETER_FIELD_VALID_AFTER, MIN_BASELINE, FLAGGED,
    MAT_COLORS, MAT_LABELS, REGION_ORDER, PLACEMENTS, REGION_COLORS,
)

PLOT_DIR = os.path.join(BASE, 'Manager_Plots_v4')
os.makedirs(PLOT_DIR, exist_ok=True)

FACE_COLORS = {'top': '#2CA02C', 'front': '#1F77B4', 'side': '#FF7F0E'}
FACE_MARKERS = {'top': 'o', 'front': 's', 'side': '^'}
FACE_STYLES = {'top': '--', 'front': ':', 'side': '-.'}
HELM_COLOR = '#8B0000'

FACES = ['top', 'front', 'side']


# ─── Enhanced Teslameter Loader ──────────────────────────────────────────────

def load_teslameter_field_v4(y_materials):
    """Load Teslameter field data with full per-face time series.

    Returns list of per-sample dicts with:
      - pct_change: 3-face average endpoint % change
      - face_pcts: {face: endpoint_pct}
      - face_date_pcts: {face: [(datetime, pct), ...]}  per-face time series
      - face_date_fields: {face: {date_str: mean_field_corr}}  raw corrected fields
      - date_pcts: [(datetime, pct), ...]  3-face average time series
    """
    y_tesla_dir = os.path.join(BASE, 'Y_Plates', 'Teslameter')

    y_samples = set()
    for f in os.listdir(y_tesla_dir):
        m = re.match(r'(Y-\d+-\d+)_(front|side|top)\.dat$', f)
        if m:
            y_samples.add(m.group(1))

    results = []
    temp_history = defaultdict(list)

    for sample in sorted(y_samples):
        pm = re.match(r'Y-(\d+)-(\d+)', sample)
        if not pm:
            continue
        plate_num = int(pm.group(1))
        slot_num = int(pm.group(2))
        region = PLACEMENTS.get(plate_num, 'Unknown')
        if region == 'Unknown':
            continue
        material = y_materials.get(sample)
        if not material:
            continue
        material = material.strip()
        alpha = ALPHA.get(material)
        if alpha is None:
            continue

        face_data = {}  # face -> [(dt, mag_corr, temp), ...]
        for face in FACES:
            fpath = os.path.join(y_tesla_dir, '%s_%s.dat' % (sample, face))
            if not os.path.exists(fpath):
                continue
            rows = parse_teslameter_file(fpath)
            corrected = []
            for dt, fields, temp in rows:
                if dt < TESLAMETER_FIELD_VALID_AFTER:
                    continue
                if temp is None or abs(temp - SENTINEL) < 1:
                    continue
                mag = np.sqrt(sum(fi**2 for fi in fields))
                denom = 1.0 + alpha * (temp - T_REF)
                mag_corr = mag / denom
                corrected.append((dt, mag_corr, temp))
            if corrected:
                face_data[face] = sorted(corrected, key=lambda x: x[0])

        if not face_data:
            continue

        # Build per-face date-grouped data
        face_date_data = {}   # face -> {date_str: [mag_corr, ...]}
        face_date_fields = {} # face -> {date_str: mean_field_corr}
        for face, data in face_data.items():
            dfd = defaultdict(list)
            for dt, mag_corr, temp in data:
                d_str = dt.strftime('%Y-%m-%d')
                dfd[d_str].append(mag_corr)
                temp_history[d_str].append(temp)
            face_date_data[face] = dfd
            face_date_fields[face] = {d: np.mean(vals) for d, vals in dfd.items()}

        # Compute per-face % change and time series
        face_pcts = {}
        face_date_pcts = {}
        for face in FACES:
            if face not in face_date_data:
                continue
            dfd = face_date_data[face]
            sdates = sorted(dfd.keys())
            if len(sdates) < 2:
                continue
            bl_d = sdates[0]
            lt_d = sdates[-1]
            bl_mag = np.mean(dfd[bl_d])
            lt_mag = np.mean(dfd[lt_d])
            if abs(bl_mag) < 1.0:
                continue
            face_pcts[face] = (lt_mag - bl_mag) / bl_mag * 100.0

            # Time series for this face
            ts = []
            for d_str in sdates:
                d_val = np.mean(dfd[d_str])
                ts.append((datetime.strptime(d_str, '%Y-%m-%d'),
                           (d_val - bl_mag) / bl_mag * 100.0))
            face_date_pcts[face] = ts

        if not face_pcts:
            continue

        # 3-face average
        pct_change = np.mean(list(face_pcts.values()))
        is_outlier = sample in FLAGGED

        # 3-face average time series
        all_dates = set()
        for face in face_date_data:
            all_dates.update(face_date_data[face].keys())
        all_dates_sorted = sorted(all_dates)
        date_pcts_avg = []
        if len(all_dates_sorted) >= 2:
            bl_d = all_dates_sorted[0]
            for d_str in all_dates_sorted:
                face_pcts_d = []
                for face, dfd in face_date_data.items():
                    if bl_d in dfd and d_str in dfd:
                        bl_val = np.mean(dfd[bl_d])
                        d_val = np.mean(dfd[d_str])
                        if abs(bl_val) > 1.0:
                            face_pcts_d.append((d_val - bl_val) / bl_val * 100.0)
                if face_pcts_d:
                    date_pcts_avg.append((datetime.strptime(d_str, '%Y-%m-%d'),
                                         np.mean(face_pcts_d)))

        results.append({
            'sample': sample, 'plate': plate_num, 'slot': slot_num,
            'material': material, 'region': region,
            'pct_change': pct_change,
            'face_pcts': face_pcts,
            'face_date_pcts': face_date_pcts,
            'face_date_fields': face_date_fields,
            'date_pcts': date_pcts_avg,
            'is_outlier': is_outlier,
        })

    return results, temp_history


def compute_intra_plate_diffs_tesla(tesla_results, face_name):
    """Compute per-plate NdFeB-SmCo differential from Teslameter data for a given face.

    face_name: 'top', 'front', 'side', or '3face_avg'
    Returns (diffs_list, details_list).
    """
    clean = [r for r in tesla_results if not r['is_outlier']]
    plate_data = defaultdict(dict)

    for r in clean:
        if face_name == '3face_avg':
            val = r['pct_change']
        else:
            if face_name not in r['face_pcts']:
                continue
            val = r['face_pcts'][face_name]
        plate_data[r['plate']][r['material']] = val

    diffs = []
    details = []
    for plate, mat_pcts in plate_data.items():
        nd = [mat_pcts[m] for m in ['N42EH', 'N52SH'] if m in mat_pcts]
        sm = [mat_pcts[m] for m in ['SmCo33H', 'SmCo35'] if m in mat_pcts]
        if nd and sm:
            diff = np.mean(nd) - np.mean(sm)
            diffs.append(diff)
            details.append({
                'plate': plate,
                'region': PLACEMENTS.get(plate, 'Unknown'),
                'diff': diff,
                'ndfeb_pct': np.mean(nd),
                'smco_pct': np.mean(sm),
            })
    return diffs, details


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY A: Per-Face Core Analysis (4 plots)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_A01_per_face_material_bars(tesla_results):
    """Material bars, one panel per face + 3-face avg."""
    clean = [r for r in tesla_results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    face_labels = ['top', 'front', 'side', '3face_avg']
    panel_titles = ['Top Face (best rig fit)', 'Front Face', 'Side Face',
                    '3-Face Average']

    fig, axes = plt.subplots(1, 4, figsize=(18, 6), sharey=True)
    fig.suptitle('Teslameter Field Degradation by Face and Material\n'
                 'Baseline = first tunnel measurement, temp-corrected to 20°C',
                 fontsize=13, fontweight='bold')

    for pi, (face, title) in enumerate(zip(face_labels, panel_titles)):
        ax = axes[pi]
        for i, mat in enumerate(materials):
            if face == '3face_avg':
                vals = [r['pct_change'] for r in clean if r['material'] == mat]
            else:
                vals = [r['face_pcts'][face] for r in clean
                        if r['material'] == mat and face in r['face_pcts']]
            if not vals:
                continue
            m = np.mean(vals)
            sem = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.5
            std = np.std(vals, ddof=1) if len(vals) > 1 else 0.0
            sig = abs(m / sem) if sem > 0 else 0
            sig_str = '%.1fσ' % sig if sig >= 1.5 else 'n.s.'
            ax.bar(i, m, yerr=sem, color=MAT_COLORS[mat], capsize=5,
                   edgecolor='black', linewidth=0.5, alpha=0.85, width=0.6,
                   error_kw=dict(linewidth=1.5))
            ax.text(i, m - sem - 0.08 if m < 0 else m + sem + 0.02,
                    '%+.2f%%\n(%s)\nN=%d\nstd=%.2f%%' % (m, sig_str, len(vals), std),
                    ha='center', fontsize=6, va='top' if m < 0 else 'bottom')

        ax.axhline(0, color='black', linewidth=1)
        ax.set_xticks(range(4))
        ax.set_xticklabels([MAT_LABELS[m].replace('NdFeB ', '').replace('SmCo ', '')
                            for m in materials], fontsize=8)
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

    axes[0].set_ylabel('% Change from First Tunnel Measurement', fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(os.path.join(PLOT_DIR, 'v4_A01_per_face_material_bars.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  A01: Per-face material bars")


def plot_A02_per_face_timeseries(tesla_results):
    """Time series, one panel per face."""
    clean = [r for r in tesla_results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    face_labels = ['top', 'front', 'side', '3face_avg']
    panel_titles = ['Top Face', 'Front Face', 'Side Face', '3-Face Average']

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharey=True)
    fig.suptitle('Teslameter Field Degradation Over Time — Per Face\n'
                 'Lines = material means ± SEM per date',
                 fontsize=13, fontweight='bold')

    for pi, (face, title) in enumerate(zip(face_labels, panel_titles)):
        ax = axes[pi // 2][pi % 2]
        for mat in materials:
            if face == '3face_avg':
                samples = [r for r in clean if r['material'] == mat]
                date_vals = defaultdict(list)
                for r in samples:
                    for dt, pct in r['date_pcts']:
                        date_vals[dt.strftime('%Y-%m-%d')].append(pct)
            else:
                samples = [r for r in clean if r['material'] == mat
                           and face in r.get('face_date_pcts', {})]
                date_vals = defaultdict(list)
                for r in samples:
                    if face not in r['face_date_pcts']:
                        continue
                    for dt, pct in r['face_date_pcts'][face]:
                        date_vals[dt.strftime('%Y-%m-%d')].append(pct)

            if not date_vals:
                continue
            dates = sorted(d for d in date_vals if len(date_vals[d]) >= 5)
            if not dates:
                dates = sorted(d for d in date_vals if len(date_vals[d]) >= 3)
            if not dates:
                continue
            dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
            means = [np.mean(date_vals[d]) for d in dates]
            sems = [np.std(date_vals[d], ddof=1) / np.sqrt(len(date_vals[d]))
                    if len(date_vals[d]) > 1 else 0.1 for d in dates]
            ax.errorbar(dt_objs, means, yerr=sems,
                        color=MAT_COLORS[mat], marker='o', markersize=4,
                        linewidth=1.5, capsize=3, label=MAT_LABELS[mat])

        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1, linestyle=':')
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.grid(alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax.tick_params(labelsize=8)
        if pi == 0:
            ax.legend(fontsize=7, loc='lower left')

    axes[0][0].set_ylabel('% Change', fontsize=10)
    axes[1][0].set_ylabel('% Change', fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(os.path.join(PLOT_DIR, 'v4_A02_per_face_timeseries.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  A02: Per-face time series")


def plot_A03_intra_plate_diff_by_face(helm_results, tesla_results):
    """THE KEY PLOT: Intra-plate NdFeB-SmCo differential by face + Helmholtz."""
    clean_helm = [r for r in helm_results if not r['is_outlier']]
    helm_diffs, _ = compute_intra_plate_diffs(clean_helm)

    face_keys = ['top', 'front', 'side', '3face_avg']
    face_labels_plot = ['Helmholtz', 'Tesla\nTop', 'Tesla\nFront',
                        'Tesla\nSide', 'Tesla\n3-Face']
    all_diffs = [helm_diffs]
    all_ns = [len(helm_diffs)]

    for fk in face_keys:
        diffs, _ = compute_intra_plate_diffs_tesla(tesla_results, fk)
        all_diffs.append(diffs)
        all_ns.append(len(diffs))

    fig, ax = plt.subplots(figsize=(10, 7))

    bar_colors = [HELM_COLOR, FACE_COLORS['top'], FACE_COLORS['front'],
                  FACE_COLORS['side'], '#888888']
    x = np.arange(len(face_labels_plot))

    for i, (diffs, label) in enumerate(zip(all_diffs, face_labels_plot)):
        if not diffs:
            continue
        m = np.mean(diffs)
        sem = np.std(diffs) / np.sqrt(len(diffs)) if len(diffs) > 1 else 0.1
        sig = abs(m / sem) if sem > 0 else 0
        ax.bar(i, m, yerr=sem, color=bar_colors[i], capsize=8,
               edgecolor='black', linewidth=1 if i == 0 else 0.5,
               alpha=0.85, width=0.6,
               error_kw=dict(linewidth=2, capthick=2))

        sig_str = '%.1fσ' % sig
        ax.text(i, m - sem - 0.03 if m < 0 else m + sem + 0.01,
                '%+.3f%%\n±%.3f%%\n(%s)\nN=%d' % (m, sem, sig_str, len(diffs)),
                ha='center', fontsize=9, fontweight='bold' if i == 0 else 'normal',
                va='top' if m < 0 else 'bottom')

    ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax.set_xticks(x)
    ax.set_xticklabels(face_labels_plot, fontsize=11)
    ax.set_ylabel('NdFeB − SmCo Intra-Plate Differential (%)', fontsize=12)
    ax.set_title('Intra-Plate NdFeB−SmCo Differential: Helmholtz vs Each Teslameter Face\n'
                 'Gain-immune technique applied to both instruments',
                 fontsize=13, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # Highlight Helmholtz bar
    ax.annotate('Helmholtz:\npre-deployment baseline,\n9.7σ significance',
                xy=(0, np.mean(helm_diffs)),
                xytext=(1.5, 0.10),
                fontsize=9, ha='center', color=HELM_COLOR,
                arrowprops=dict(arrowstyle='->', color=HELM_COLOR, lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFE0E0',
                          edgecolor=HELM_COLOR))
    ax.annotate('Teslameter:\nfirst-tunnel baseline,\nrig positioning noise',
                xy=(3, 0),
                xytext=(3, 0.10),
                fontsize=9, ha='center', color='#555',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                          edgecolor='gray'))

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v4_A03_intra_plate_diff_by_face.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  A03: Intra-plate differential by face (KEY PLOT)")


def plot_A04_per_face_scatter_vs_helmholtz(helm_results, tesla_results):
    """Scatter: Helmholtz vs each Teslameter face per sample."""
    clean_helm = {r['sample']: r for r in helm_results if not r['is_outlier']}
    clean_tesla = {r['sample']: r for r in tesla_results if not r['is_outlier']}
    common = set(clean_helm.keys()) & set(clean_tesla.keys())

    face_keys = ['top', 'front', 'side', '3face_avg']
    panel_titles = ['Top Face', 'Front Face', 'Side Face', '3-Face Average']

    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    fig.suptitle('Helmholtz vs Teslameter Per-Sample Scatter — By Face\n'
                 'Different baselines: Helmholtz=pre-deployment, Tesla=first tunnel',
                 fontsize=13, fontweight='bold')

    for pi, (face, title) in enumerate(zip(face_keys, panel_titles)):
        ax = axes[pi // 2][pi % 2]
        helm_vals, tesla_vals = [], []

        for sample in sorted(common):
            hr = clean_helm[sample]
            tr = clean_tesla[sample]
            hv = hr['pct_change']
            if face == '3face_avg':
                tv = tr['pct_change']
            else:
                if face not in tr['face_pcts']:
                    continue
                tv = tr['face_pcts'][face]
            ax.scatter(hv, tv, c=MAT_COLORS[hr['material']], s=40,
                       alpha=0.7, edgecolors='black', linewidths=0.3, zorder=3)
            helm_vals.append(hv)
            tesla_vals.append(tv)

        # 1:1 line
        lims = [-1.5, 1.5]
        ax.plot(lims, lims, 'k--', linewidth=1, alpha=0.5)
        ax.axhline(0, color='gray', linewidth=0.5)
        ax.axvline(0, color='gray', linewidth=0.5)

        # Pearson r
        if len(helm_vals) >= 3:
            r_val = np.corrcoef(helm_vals, tesla_vals)[0, 1]
            ax.text(0.98, 0.02, 'r = %.3f\nN = %d' % (r_val, len(helm_vals)),
                    transform=ax.transAxes, fontsize=10, ha='right', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='gray', alpha=0.8))

        ax.set_xlabel('Helmholtz %', fontsize=9)
        ax.set_ylabel('Teslameter %', fontsize=9)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.grid(alpha=0.3)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_aspect('equal')

    # Legend on first panel
    handles = [mpatches.Patch(color=MAT_COLORS[m], label=MAT_LABELS[m])
               for m in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']]
    axes[0][0].legend(handles=handles, fontsize=7, loc='upper left')

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(PLOT_DIR, 'v4_A04_per_face_scatter_vs_helmholtz.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  A04: Per-face scatter vs Helmholtz")


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY B: Statistical Characterization (3 plots)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_B01_face_statistics_table(helm_results, tesla_results, gain_syst):
    """Comprehensive statistics rendered as figure table."""
    clean_helm = [r for r in helm_results if not r['is_outlier']]
    clean_tesla = [r for r in tesla_results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.axis('off')

    # Build table data
    row_labels = ['Helmholtz', 'Tesla Top', 'Tesla Front', 'Tesla Side',
                  'Tesla 3-Face']
    col_labels = []
    for mat in materials:
        col_labels.extend(['%s\nMean' % MAT_LABELS[mat],
                           '%s\nSEM' % MAT_LABELS[mat],
                           '%s\nStd' % MAT_LABELS[mat],
                           '%s\nN' % MAT_LABELS[mat]])
    col_labels.extend(['NdFeB−SmCo\nDiff', 'NdFeB−SmCo\nσ'])

    table_data = []

    # Helmholtz row
    row = []
    for mat in materials:
        vals = [r['pct_change'] for r in clean_helm if r['material'] == mat]
        if vals:
            row.extend(['%+.3f%%' % np.mean(vals),
                        '%.3f%%' % (np.std(vals, ddof=1)/np.sqrt(len(vals))),
                        '%.3f%%' % np.std(vals, ddof=1),
                        '%d' % len(vals)])
        else:
            row.extend(['—', '—', '—', '0'])
    helm_diffs, _ = compute_intra_plate_diffs(clean_helm)
    if helm_diffs:
        dm = np.mean(helm_diffs)
        ds = np.std(helm_diffs) / np.sqrt(len(helm_diffs))
        row.extend(['%+.3f%%' % dm, '%.1f' % (abs(dm/ds) if ds > 0 else 0)])
    else:
        row.extend(['—', '—'])
    table_data.append(row)

    # Teslameter rows
    for face_key, face_label in [('top', 'Tesla Top'), ('front', 'Tesla Front'),
                                  ('side', 'Tesla Side'), ('3face_avg', 'Tesla 3-Face')]:
        row = []
        for mat in materials:
            if face_key == '3face_avg':
                vals = [r['pct_change'] for r in clean_tesla if r['material'] == mat]
            else:
                vals = [r['face_pcts'][face_key] for r in clean_tesla
                        if r['material'] == mat and face_key in r['face_pcts']]
            if vals:
                row.extend(['%+.3f%%' % np.mean(vals),
                            '%.3f%%' % (np.std(vals, ddof=1)/np.sqrt(len(vals))),
                            '%.3f%%' % np.std(vals, ddof=1),
                            '%d' % len(vals)])
            else:
                row.extend(['—', '—', '—', '0'])
        diffs, _ = compute_intra_plate_diffs_tesla(tesla_results, face_key)
        if diffs:
            dm = np.mean(diffs)
            ds = np.std(diffs) / np.sqrt(len(diffs)) if len(diffs) > 1 else 0.1
            row.extend(['%+.3f%%' % dm, '%.1f' % (abs(dm/ds) if ds > 0 else 0)])
        else:
            row.extend(['—', '—'])
        table_data.append(row)

    table = ax.table(cellText=table_data, rowLabels=row_labels,
                     colLabels=col_labels, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 2.0)

    # Color headers
    for j in range(len(col_labels)):
        table[0, j].set_facecolor('#DDDDDD')
        table[0, j].set_text_props(fontweight='bold', fontsize=6)
    ncols = len(col_labels)
    for i in range(len(row_labels)):
        table[i+1, ncols-1].set_facecolor('#EEEEEE')
        table[i+1, ncols-2].set_facecolor('#EEEEEE')

    # Color row labels
    row_colors = [HELM_COLOR, FACE_COLORS['top'], FACE_COLORS['front'],
                  FACE_COLORS['side'], '#888888']
    for i, c in enumerate(row_colors):
        table[i+1, -1].set_text_props(fontweight='bold')

    ax.set_title('Comprehensive Per-Face Statistics — Teslameter vs Helmholtz\n'
                 'Helmholtz gain systematic: ±%.2f%%. Teslameter: no gain systematic '
                 'but positioning noise.' % gain_syst,
                 fontsize=13, fontweight='bold', pad=20)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v4_B01_face_statistics_table.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  B01: Face statistics table")


def plot_B02_face_to_face_correlation(tesla_results):
    """Scatter: do faces agree on which samples degraded?"""
    clean = [r for r in tesla_results if not r['is_outlier']]
    pairs = [('top', 'front'), ('top', 'side'), ('front', 'side')]
    pair_titles = ['Top vs Front', 'Top vs Side', 'Front vs Side']

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle('Face-to-Face Correlation: Do Different Faces Agree?\n'
                 'Each point = one sample. If faces measure same physics, they should correlate.',
                 fontsize=13, fontweight='bold')

    for pi, ((f1, f2), title) in enumerate(zip(pairs, pair_titles)):
        ax = axes[pi]
        v1_all, v2_all = [], []
        for r in clean:
            if f1 in r['face_pcts'] and f2 in r['face_pcts']:
                v1 = r['face_pcts'][f1]
                v2 = r['face_pcts'][f2]
                ax.scatter(v1, v2, c=MAT_COLORS[r['material']], s=30,
                           alpha=0.7, edgecolors='black', linewidths=0.3)
                v1_all.append(v1)
                v2_all.append(v2)

        lims = [-3, 3]
        ax.plot(lims, lims, 'k--', linewidth=1, alpha=0.4)
        ax.axhline(0, color='gray', linewidth=0.3)
        ax.axvline(0, color='gray', linewidth=0.3)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_aspect('equal')

        if len(v1_all) >= 3:
            r_val = np.corrcoef(v1_all, v2_all)[0, 1]
            ax.text(0.98, 0.02, 'r = %.3f\nN = %d' % (r_val, len(v1_all)),
                    transform=ax.transAxes, fontsize=10, ha='right', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='gray', alpha=0.8))

        ax.set_xlabel('%s Face (%%)' % f1.capitalize(), fontsize=10)
        ax.set_ylabel('%s Face (%%)' % f2.capitalize(), fontsize=10)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.grid(alpha=0.3)

    handles = [mpatches.Patch(color=MAT_COLORS[m], label=MAT_LABELS[m])
               for m in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']]
    axes[0].legend(handles=handles, fontsize=7, loc='upper left')

    fig.tight_layout(rect=[0, 0, 1, 0.88])
    fig.savefig(os.path.join(PLOT_DIR, 'v4_B02_face_to_face_correlation.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  B02: Face-to-face correlation")


def plot_B03_rig_tolerance_by_slot(tesla_results):
    """Per-slot scatter analysis: box plots for each slot × face."""
    clean = [r for r in tesla_results if not r['is_outlier']]

    fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
    fig.suptitle('Rig Tolerance: Per-Slot Distribution by Face\n'
                 'Slots 1-2 = NdFeB, Slots 3-4 = SmCo. '
                 'If rig tolerance varies by slot, expect different spreads.',
                 fontsize=13, fontweight='bold')

    for fi, face in enumerate(FACES):
        ax = axes[fi]
        slot_data = {s: [] for s in [1, 2, 3, 4]}
        for r in clean:
            if face in r['face_pcts']:
                slot_data[r['slot']].append(r['face_pcts'][face])

        data = [slot_data[s] for s in [1, 2, 3, 4]]
        slot_labels = ['Slot 1\nN42EH', 'Slot 2\nN52SH',
                       'Slot 3\nSmCo33H', 'Slot 4\nSmCo35']
        slot_colors = [MAT_COLORS[MAT_BY_SLOT[s]] for s in [1, 2, 3, 4]]

        bp = ax.boxplot(data, labels=slot_labels, widths=0.5,
                        patch_artist=True, showmeans=True,
                        meanprops=dict(marker='D', markerfacecolor='white',
                                       markeredgecolor='black', markersize=5))
        for j, patch in enumerate(bp['boxes']):
            patch.set_facecolor(slot_colors[j])
            patch.set_alpha(0.5)

        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        ax.set_title('%s Face' % face.capitalize(), fontsize=11, fontweight='bold',
                     color=FACE_COLORS[face])
        ax.grid(axis='y', alpha=0.3)
        ax.tick_params(labelsize=8)

        # Add std annotations
        for j, s in enumerate([1, 2, 3, 4]):
            if slot_data[s]:
                std = np.std(slot_data[s], ddof=1)
                ax.text(j + 1, ax.get_ylim()[0] * 0.9 if ax.get_ylim()[0] < 0 else -1,
                        'σ=%.2f%%\nN=%d' % (std, len(slot_data[s])),
                        ha='center', fontsize=7, color='gray')

    axes[0].set_ylabel('% Change from First Tunnel Measurement', fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    fig.savefig(os.path.join(PLOT_DIR, 'v4_B03_rig_tolerance_by_slot.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  B03: Rig tolerance by slot")


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY C: Combined Instrument Analysis (3 plots)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_C01_helmholtz_vs_teslameter_bars(helm_results, tesla_results, gain_syst):
    """Side-by-side instrument comparison: 5 panels same y-axis."""
    clean_helm = [r for r in helm_results if not r['is_outlier']]
    clean_tesla = [r for r in tesla_results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    panel_keys = ['helmholtz', 'top', 'front', 'side', '3face_avg']
    panel_titles = ['Helmholtz\n(±%.2f%% gain syst.)' % gain_syst,
                    'Tesla Top\n(best rig fit)',
                    'Tesla Front', 'Tesla Side',
                    'Tesla 3-Face\nAverage']

    fig, axes = plt.subplots(1, 5, figsize=(20, 6), sharey=True)
    fig.suptitle('Instrument Comparison: Helmholtz vs Teslameter Per-Face\n'
                 'All temperature-corrected to 20°C',
                 fontsize=13, fontweight='bold')

    for pi, (key, title) in enumerate(zip(panel_keys, panel_titles)):
        ax = axes[pi]
        for i, mat in enumerate(materials):
            if key == 'helmholtz':
                vals = [r['pct_change'] for r in clean_helm if r['material'] == mat]
            elif key == '3face_avg':
                vals = [r['pct_change'] for r in clean_tesla if r['material'] == mat]
            else:
                vals = [r['face_pcts'][key] for r in clean_tesla
                        if r['material'] == mat and key in r['face_pcts']]
            if not vals:
                continue
            m = np.mean(vals)
            sem = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.5
            ax.bar(i, m, yerr=sem, color=MAT_COLORS[mat], capsize=4,
                   edgecolor='black', linewidth=0.5, alpha=0.85, width=0.6,
                   error_kw=dict(linewidth=1.5))

        if key == 'helmholtz':
            ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)

        ax.axhline(0, color='black', linewidth=1)
        ax.set_xticks(range(4))
        ax.set_xticklabels([MAT_LABELS[m].replace('NdFeB ', '').replace('SmCo ', '')
                            for m in materials], fontsize=7, rotation=15)
        ax.set_title(title, fontsize=9, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

    axes[0].set_ylabel('% Change from Baseline', fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(os.path.join(PLOT_DIR, 'v4_C01_helmholtz_vs_teslameter_bars.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  C01: Helmholtz vs Teslameter bars")


def plot_C02_session_delta_comparison(helm_results, tesla_results, helm_raw,
                                      temp_final, y_materials):
    """Session-to-session deltas: avoids baseline problem."""
    clean_helm = {r['sample']: r for r in helm_results if not r['is_outlier']}
    clean_tesla = {r['sample']: r for r in tesla_results if not r['is_outlier']}
    common = set(clean_helm.keys()) & set(clean_tesla.keys())

    # Find common tunnel dates from Helmholtz data
    helm_tunnel_dates = set()
    for r in helm_results:
        for dt, pct in r['date_pcts']:
            helm_tunnel_dates.add(dt.strftime('%Y-%m-%d'))

    # Find common tunnel dates from Teslameter data
    tesla_tunnel_dates = set()
    for r in tesla_results:
        for dt, pct in r['date_pcts']:
            tesla_tunnel_dates.add(dt.strftime('%Y-%m-%d'))

    common_dates = sorted(helm_tunnel_dates & tesla_tunnel_dates)

    # Build per-sample per-date Helmholtz values
    helm_date_vals = defaultdict(dict)  # sample -> {date_str: pct}
    for r in helm_results:
        if r['is_outlier']:
            continue
        for dt, pct in r['date_pcts']:
            helm_date_vals[r['sample']][dt.strftime('%Y-%m-%d')] = pct

    # Build per-sample per-date Teslameter values (per face)
    tesla_face_date_vals = defaultdict(lambda: defaultdict(dict))
    for r in tesla_results:
        if r['is_outlier']:
            continue
        for face in FACES:
            if face not in r.get('face_date_pcts', {}):
                continue
            for dt, pct in r['face_date_pcts'][face]:
                tesla_face_date_vals[r['sample']][face][dt.strftime('%Y-%m-%d')] = pct

    # For consecutive date pairs, compute deltas
    face_keys = ['top', 'front', 'side']
    panel_titles = ['Top Face', 'Front Face', 'Side Face']

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle('Session-to-Session Deltas: Helmholtz vs Teslameter\n'
                 'Each point = one sample\'s change between consecutive dates. '
                 'Avoids different-baseline problem.',
                 fontsize=13, fontweight='bold')

    for fi, (face, title) in enumerate(zip(face_keys, panel_titles)):
        ax = axes[fi]
        helm_deltas_all, tesla_deltas_all = [], []

        for i in range(len(common_dates) - 1):
            d1, d2 = common_dates[i], common_dates[i + 1]
            for sample in common:
                if (d1 in helm_date_vals.get(sample, {}) and
                    d2 in helm_date_vals.get(sample, {})):
                    h_delta = helm_date_vals[sample][d2] - helm_date_vals[sample][d1]
                else:
                    continue
                t_dates = tesla_face_date_vals.get(sample, {}).get(face, {})
                if d1 in t_dates and d2 in t_dates:
                    t_delta = t_dates[d2] - t_dates[d1]
                else:
                    continue

                mat = clean_helm[sample]['material']
                ax.scatter(h_delta, t_delta, c=MAT_COLORS[mat], s=20,
                           alpha=0.6, edgecolors='none', zorder=3)
                helm_deltas_all.append(h_delta)
                tesla_deltas_all.append(t_delta)

        lims = [-1.0, 1.0]
        ax.plot(lims, lims, 'k--', linewidth=1, alpha=0.4)
        ax.axhline(0, color='gray', linewidth=0.3)
        ax.axvline(0, color='gray', linewidth=0.3)

        if len(helm_deltas_all) >= 3:
            r_val = np.corrcoef(helm_deltas_all, tesla_deltas_all)[0, 1]
            ax.text(0.98, 0.02, 'r = %.3f\nN = %d pts' %
                    (r_val, len(helm_deltas_all)),
                    transform=ax.transAxes, fontsize=10, ha='right', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='gray', alpha=0.8))

        ax.set_xlabel('Helmholtz Δ (%)', fontsize=10)
        ax.set_ylabel('Teslameter %s Δ (%%)' % face.capitalize(), fontsize=10)
        ax.set_title(title, fontsize=11, fontweight='bold',
                     color=FACE_COLORS[face])
        ax.grid(alpha=0.3)
        ax.set_xlim(lims)
        ax.set_ylim([-2, 2])

    handles = [mpatches.Patch(color=MAT_COLORS[m], label=MAT_LABELS[m])
               for m in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']]
    axes[0].legend(handles=handles, fontsize=7, loc='upper left')

    fig.tight_layout(rect=[0, 0, 1, 0.86])
    fig.savefig(os.path.join(PLOT_DIR, 'v4_C02_session_delta_comparison.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  C02: Session-delta comparison")


def plot_C03_intra_plate_diff_timeseries(helm_results, tesla_results,
                                          helm_raw, temp_final,
                                          y_materials=None):
    """NdFeB-SmCo intra-plate differential over time: Helmholtz + Teslameter faces."""
    clean_helm = [r for r in helm_results if not r['is_outlier']]
    clean_tesla = [r for r in tesla_results if not r['is_outlier']]

    fig, ax = plt.subplots(figsize=(12, 7))

    # Helmholtz differential over time (using double ratio vs Aug 27)
    ref_date = '2025-08-27'
    dr_dates = ['2025-07-17', '2025-07-30', '2025-10-21',
                '2025-10-23', '2025-10-29', '2026-01-08', '2026-01-12']

    helm_dt, helm_m, helm_s = [], [], []
    for cd in sorted(dr_dates):
        diffs_list, _ = compute_double_ratio(helm_raw, temp_final, ref_date, cd,
                                                y_materials=y_materials)
        if diffs_list:
            helm_dt.append(datetime.strptime(cd, '%Y-%m-%d'))
            helm_m.append(np.mean(diffs_list))
            helm_s.append(np.std(diffs_list) / np.sqrt(len(diffs_list)))

    # Add ref point
    helm_dt_full = [datetime.strptime(ref_date, '%Y-%m-%d')] + helm_dt
    helm_m_full = [0.0] + helm_m
    helm_s_full = [0.0] + helm_s

    ax.errorbar(helm_dt_full, helm_m_full, yerr=helm_s_full,
                color=HELM_COLOR, marker='D', markersize=6,
                linewidth=2.5, capsize=5, capthick=2,
                label='Helmholtz (pre-depl. baseline)', zorder=5)

    # Teslameter per-face differential over time
    for face in FACES:
        # Group by date: for each date, compute intra-plate diff
        # Get all dates available in this face's data
        date_set = set()
        for r in clean_tesla:
            if face in r.get('face_date_pcts', {}):
                for dt, pct in r['face_date_pcts'][face]:
                    date_set.add(dt.strftime('%Y-%m-%d'))

        dates_sorted = sorted(date_set)
        if len(dates_sorted) < 2:
            continue

        bl_date = dates_sorted[0]
        face_dt, face_m, face_s = [], [], []

        for d_str in dates_sorted:
            # For each plate: compute NdFeB face pct - SmCo face pct at this date
            plate_face_pcts = defaultdict(dict)
            for r in clean_tesla:
                if face not in r.get('face_date_fields', {}):
                    continue
                fdf = r['face_date_fields'][face]
                if bl_date not in fdf or d_str not in fdf:
                    continue
                bl_val = fdf[bl_date]
                d_val = fdf[d_str]
                if abs(bl_val) < 1.0:
                    continue
                pct = (d_val - bl_val) / bl_val * 100.0
                plate_face_pcts[r['plate']][r['material']] = pct

            # Compute intra-plate diff for this date
            diffs_d = []
            for plate, mat_pcts in plate_face_pcts.items():
                nd = [mat_pcts[m] for m in ['N42EH', 'N52SH'] if m in mat_pcts]
                sm = [mat_pcts[m] for m in ['SmCo33H', 'SmCo35'] if m in mat_pcts]
                if nd and sm:
                    diffs_d.append(np.mean(nd) - np.mean(sm))

            if len(diffs_d) >= 3:
                face_dt.append(datetime.strptime(d_str, '%Y-%m-%d'))
                face_m.append(np.mean(diffs_d))
                face_s.append(np.std(diffs_d) / np.sqrt(len(diffs_d)))

        if face_dt:
            ax.errorbar(face_dt, face_m, yerr=face_s,
                        color=FACE_COLORS[face],
                        marker=FACE_MARKERS[face], markersize=5,
                        linewidth=1.5, linestyle=FACE_STYLES[face],
                        capsize=3, label='Tesla %s' % face.capitalize())

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1, linestyle=':',
               alpha=0.7)
    ax.text(datetime(2025, 10, 24), ax.get_ylim()[1] * 0.9 if ax.get_ylim()[1] > 0 else 0.15,
            'Beam OFF', fontsize=9, color='gray')

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('NdFeB − SmCo Intra-Plate Differential (%)', fontsize=12)
    ax.set_title('Intra-Plate NdFeB−SmCo Differential Over Time\n'
                 'Helmholtz (solid) vs Teslameter per-face (dashed/dotted)',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=9, loc='lower left')
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v4_C03_intra_plate_diff_timeseries.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  C03: Intra-plate differential time series")


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY D: Summary (2 plots)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_D01_summary_dashboard(helm_results, tesla_results, gain_syst,
                                helm_raw, temp_final):
    """3×2 summary dashboard."""
    clean_helm = [r for r in helm_results if not r['is_outlier']]
    clean_tesla = [r for r in tesla_results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    helm_diffs, _ = compute_intra_plate_diffs(clean_helm)
    helm_diff_mean = np.mean(helm_diffs)
    helm_diff_sem = np.std(helm_diffs) / np.sqrt(len(helm_diffs))
    helm_diff_sig = abs(helm_diff_mean / helm_diff_sem) if helm_diff_sem > 0 else 0

    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('LDRD FFA@CEBAF — Per-Face Teslameter Re-Analysis (v4)\n'
                 'Combined instrument comparison with rig tolerance characterization',
                 fontsize=14, fontweight='bold', y=0.99)

    # (a) Intra-plate differentials by face + Helmholtz (compact A03)
    ax = fig.add_subplot(3, 2, 1)
    face_keys = ['top', 'front', 'side', '3face_avg']
    bar_labels = ['Helm.', 'Top', 'Front', 'Side', '3-Face']
    bar_colors = [HELM_COLOR, FACE_COLORS['top'], FACE_COLORS['front'],
                  FACE_COLORS['side'], '#888888']
    all_diffs_list = [helm_diffs]
    for fk in face_keys:
        d, _ = compute_intra_plate_diffs_tesla(tesla_results, fk)
        all_diffs_list.append(d)

    for i, (diffs, lbl) in enumerate(zip(all_diffs_list, bar_labels)):
        if not diffs:
            continue
        m = np.mean(diffs)
        s = np.std(diffs) / np.sqrt(len(diffs)) if len(diffs) > 1 else 0.1
        sig = abs(m / s) if s > 0 else 0
        ax.bar(i, m, yerr=s, color=bar_colors[i], capsize=4,
               edgecolor='black', linewidth=0.5, alpha=0.85, width=0.6,
               error_kw=dict(linewidth=1.5))
        ax.text(i, m - s - 0.01, '%.1fσ' % sig, ha='center', fontsize=7,
                fontweight='bold' if sig >= 3 else 'normal', va='top')
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_xticks(range(5))
    ax.set_xticklabels(bar_labels, fontsize=8)
    ax.set_ylabel('NdFeB−SmCo (%)', fontsize=8)
    ax.set_title('(a) Intra-Plate Differential', fontsize=10, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # (b) Top-face time series vs Helmholtz overlay
    ax = fig.add_subplot(3, 2, 2)
    ax.axhspan(-gain_syst, gain_syst, alpha=0.08, color='gray', zorder=0)
    for mat in materials:
        # Helmholtz
        date_vals = defaultdict(list)
        for r in clean_helm:
            if r['material'] != mat:
                continue
            for dt, pct in r['date_pcts']:
                date_vals[dt.strftime('%Y-%m-%d')].append(pct)
        dates = sorted(d for d in date_vals if len(date_vals[d]) >= 5)
        if dates:
            dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
            means_p = [np.mean(date_vals[d]) for d in dates]
            ax.plot(dt_objs, means_p, '-', color=MAT_COLORS[mat],
                    linewidth=1.5, alpha=0.5)

        # Top face Tesla
        date_vals_t = defaultdict(list)
        for r in clean_tesla:
            if r['material'] != mat:
                continue
            if 'top' not in r.get('face_date_pcts', {}):
                continue
            for dt, pct in r['face_date_pcts']['top']:
                date_vals_t[dt.strftime('%Y-%m-%d')].append(pct)
        dates_t = sorted(d for d in date_vals_t if len(date_vals_t[d]) >= 3)
        if dates_t:
            dt_objs_t = [datetime.strptime(d, '%Y-%m-%d') for d in dates_t]
            means_t = [np.mean(date_vals_t[d]) for d in dates_t]
            ax.plot(dt_objs_t, means_t, '--', color=MAT_COLORS[mat],
                    marker=FACE_MARKERS['top'], markersize=3, linewidth=1)

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_title('(b) Helmholtz (solid) vs Top-Face (dashed)\nover time',
                 fontsize=10, fontweight='bold')
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.tick_params(labelsize=7)

    # (c) Top-face scatter vs Helmholtz
    ax = fig.add_subplot(3, 2, 3)
    clean_helm_d = {r['sample']: r for r in clean_helm}
    clean_tesla_d = {r['sample']: r for r in clean_tesla}
    common = set(clean_helm_d.keys()) & set(clean_tesla_d.keys())
    hv_all, tv_all = [], []
    for sample in sorted(common):
        hr = clean_helm_d[sample]
        tr = clean_tesla_d[sample]
        if 'top' not in tr['face_pcts']:
            continue
        hv = hr['pct_change']
        tv = tr['face_pcts']['top']
        ax.scatter(hv, tv, c=MAT_COLORS[hr['material']], s=20,
                   alpha=0.6, edgecolors='none')
        hv_all.append(hv)
        tv_all.append(tv)
    lims = [-1.5, 1.0]
    ax.plot(lims, lims, 'k--', linewidth=0.5, alpha=0.4)
    ax.axhline(0, color='gray', linewidth=0.3)
    ax.axvline(0, color='gray', linewidth=0.3)
    if len(hv_all) >= 3:
        r_val = np.corrcoef(hv_all, tv_all)[0, 1]
        ax.text(0.98, 0.02, 'r=%.3f' % r_val, transform=ax.transAxes,
                fontsize=9, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.set_xlabel('Helmholtz %', fontsize=8)
    ax.set_ylabel('Tesla Top %', fontsize=8)
    ax.set_title('(c) Helmholtz vs Top-Face Scatter', fontsize=10, fontweight='bold')
    ax.grid(alpha=0.3)
    ax.tick_params(labelsize=7)

    # (d) Session-delta correlation (top face)
    ax = fig.add_subplot(3, 2, 4)
    helm_date_vals = defaultdict(dict)
    for r in clean_helm:
        for dt, pct in r['date_pcts']:
            helm_date_vals[r['sample']][dt.strftime('%Y-%m-%d')] = pct
    tesla_top_date_vals = defaultdict(dict)
    for r in clean_tesla:
        if 'top' not in r.get('face_date_pcts', {}):
            continue
        for dt, pct in r['face_date_pcts']['top']:
            tesla_top_date_vals[r['sample']][dt.strftime('%Y-%m-%d')] = pct

    h_dates = set()
    for s_data in helm_date_vals.values():
        h_dates.update(s_data.keys())
    t_dates = set()
    for s_data in tesla_top_date_vals.values():
        t_dates.update(s_data.keys())
    cd_list = sorted(h_dates & t_dates)

    hd_all, td_all = [], []
    for i in range(len(cd_list) - 1):
        d1, d2 = cd_list[i], cd_list[i + 1]
        for sample in common:
            if (d1 in helm_date_vals.get(sample, {}) and
                d2 in helm_date_vals.get(sample, {}) and
                d1 in tesla_top_date_vals.get(sample, {}) and
                d2 in tesla_top_date_vals.get(sample, {})):
                hd = helm_date_vals[sample][d2] - helm_date_vals[sample][d1]
                td = tesla_top_date_vals[sample][d2] - tesla_top_date_vals[sample][d1]
                mat = clean_helm_d[sample]['material']
                ax.scatter(hd, td, c=MAT_COLORS[mat], s=15, alpha=0.5, edgecolors='none')
                hd_all.append(hd)
                td_all.append(td)
    ax.plot([-1, 1], [-1, 1], 'k--', linewidth=0.5, alpha=0.4)
    ax.axhline(0, color='gray', linewidth=0.3)
    ax.axvline(0, color='gray', linewidth=0.3)
    if len(hd_all) >= 3:
        r_val = np.corrcoef(hd_all, td_all)[0, 1]
        ax.text(0.98, 0.02, 'r=%.3f\nN=%d' % (r_val, len(hd_all)),
                transform=ax.transAxes, fontsize=9, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.set_xlabel('Helmholtz Δ (%)', fontsize=8)
    ax.set_ylabel('Tesla Top Δ (%)', fontsize=8)
    ax.set_title('(d) Session Δ Correlation (top face)', fontsize=10, fontweight='bold')
    ax.grid(alpha=0.3)
    ax.tick_params(labelsize=7)

    # (e) Face statistics compact table
    ax = fig.add_subplot(3, 2, 5)
    ax.axis('off')
    row_labels_e = ['Helmholtz', 'Tesla Top', 'Tesla Front', 'Tesla Side']
    col_labels_e = ['NdFeB Mean', 'SmCo Mean', 'NdFeB−SmCo', 'Std (NdFeB)',
                    'Std (SmCo)']
    table_data_e = []
    for key in ['helmholtz', 'top', 'front', 'side']:
        if key == 'helmholtz':
            nd_vals = [r['pct_change'] for r in clean_helm
                       if r['material'] in ['N42EH', 'N52SH']]
            sm_vals = [r['pct_change'] for r in clean_helm
                       if r['material'] in ['SmCo33H', 'SmCo35']]
        else:
            nd_vals = [r['face_pcts'][key] for r in clean_tesla
                       if r['material'] in ['N42EH', 'N52SH']
                       and key in r['face_pcts']]
            sm_vals = [r['face_pcts'][key] for r in clean_tesla
                       if r['material'] in ['SmCo33H', 'SmCo35']
                       and key in r['face_pcts']]
        if nd_vals and sm_vals:
            table_data_e.append([
                '%+.3f%%' % np.mean(nd_vals),
                '%+.3f%%' % np.mean(sm_vals),
                '%+.3f%%' % (np.mean(nd_vals) - np.mean(sm_vals)),
                '%.3f%%' % np.std(nd_vals, ddof=1),
                '%.3f%%' % np.std(sm_vals, ddof=1),
            ])
        else:
            table_data_e.append(['—'] * 5)

    table = ax.table(cellText=table_data_e, rowLabels=row_labels_e,
                     colLabels=col_labels_e, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2.0)
    for j in range(len(col_labels_e)):
        table[0, j].set_facecolor('#DDDDDD')
        table[0, j].set_text_props(fontweight='bold')
    ax.set_title('(e) Face Statistics Summary', fontsize=10, fontweight='bold', pad=15)

    # (f) Key interpretation text
    ax = fig.add_subplot(3, 2, 6)
    ax.axis('off')
    text_lines = [
        'KEY FINDINGS (v4 Per-Face Analysis)',
        '',
        '1. Helmholtz gain-immune NdFeB−SmCo: %+.3f%% ± %.3f%% (%.1fσ)' %
        (helm_diff_mean, helm_diff_sem, helm_diff_sig),
        '',
    ]

    for fk in ['top', 'front', 'side', '3face_avg']:
        d, _ = compute_intra_plate_diffs_tesla(tesla_results, fk)
        if d:
            m = np.mean(d)
            s = np.std(d) / np.sqrt(len(d)) if len(d) > 1 else 0.1
            sig = abs(m / s) if s > 0 else 0
            text_lines.append('   Tesla %s: %+.3f%% ± %.3f%% (%.1fσ, N=%d)' %
                              (fk.replace('3face_avg', '3-face'), m, s, sig, len(d)))

    text_lines.extend([
        '',
        '2. Top face has lowest scatter (best rig fit)',
        '   but does NOT confirm the Helmholtz signal.',
        '',
        '3. Possible explanations:',
        '   • Teslameter precision insufficient (0.21% std',
        '     vs 0.13% expected signal per material)',
        '   • Different baselines (first tunnel vs pre-depl.)',
        '   • Helmholtz signal partly systematic',
        '',
        '4. Session-delta correlations and face-to-face',
        '   correlations provide additional cross-checks.',
    ])

    ax.text(0.05, 0.95, '\n'.join(text_lines),
            transform=ax.transAxes, fontsize=8, verticalalignment='top',
            fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow',
                      edgecolor='gray'))
    ax.set_title('(f) Interpretation', fontsize=10, fontweight='bold', pad=15)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(PLOT_DIR, 'v4_D01_summary_dashboard.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  D01: Summary dashboard")


def plot_D02_face_comparison_table(helm_results, tesla_results, gain_syst):
    """Clean comparison table as figure."""
    clean_helm = [r for r in helm_results if not r['is_outlier']]
    clean_tesla = [r for r in tesla_results if not r['is_outlier']]

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.axis('off')

    row_labels = ['Helmholtz absolute',
                  'Helmholtz gain-immune',
                  'Tesla top',
                  'Tesla front',
                  'Tesla side',
                  'Tesla 3-face']
    col_labels = ['NdFeB Mean', 'SmCo Mean', 'NdFeB−SmCo\nDiff',
                  'NdFeB−SmCo\nSig (σ)', 'Per-Sample\nStd (NdFeB)', 'Notes']

    table_data = []

    # Helmholtz absolute
    nd_h = [r['pct_change'] for r in clean_helm if r['material'] in ['N42EH', 'N52SH']]
    sm_h = [r['pct_change'] for r in clean_helm if r['material'] in ['SmCo33H', 'SmCo35']]
    table_data.append([
        '%+.3f%%' % np.mean(nd_h), '%+.3f%%' % np.mean(sm_h),
        '%+.3f%%' % (np.mean(nd_h) - np.mean(sm_h)),
        '—', '%.3f%%' % np.std(nd_h, ddof=1),
        '±%.2f%% gain syst.' % gain_syst,
    ])

    # Helmholtz gain-immune
    hd, _ = compute_intra_plate_diffs(clean_helm)
    if hd:
        dm = np.mean(hd)
        ds = np.std(hd) / np.sqrt(len(hd))
        sig = abs(dm / ds) if ds > 0 else 0
        table_data.append([
            '—', '—', '%+.3f%%' % dm, '%.1f' % sig, '—',
            'NO gain syst. N=%d plates' % len(hd),
        ])
    else:
        table_data.append(['—'] * 6)

    # Teslameter faces
    for fk, note in [('top', 'Best rig fit (lowest scatter)'),
                      ('front', 'Moderate rig slop'),
                      ('side', 'Worst rig tolerance'),
                      ('3face_avg', 'Diluted by noisy faces')]:
        if fk == '3face_avg':
            nd_v = [r['pct_change'] for r in clean_tesla
                    if r['material'] in ['N42EH', 'N52SH']]
            sm_v = [r['pct_change'] for r in clean_tesla
                    if r['material'] in ['SmCo33H', 'SmCo35']]
        else:
            nd_v = [r['face_pcts'][fk] for r in clean_tesla
                    if r['material'] in ['N42EH', 'N52SH']
                    and fk in r['face_pcts']]
            sm_v = [r['face_pcts'][fk] for r in clean_tesla
                    if r['material'] in ['SmCo33H', 'SmCo35']
                    and fk in r['face_pcts']]
        td, _ = compute_intra_plate_diffs_tesla(tesla_results, fk)
        if nd_v and sm_v and td:
            tdm = np.mean(td)
            tds = np.std(td) / np.sqrt(len(td)) if len(td) > 1 else 0.1
            sig = abs(tdm / tds) if tds > 0 else 0
            table_data.append([
                '%+.3f%%' % np.mean(nd_v), '%+.3f%%' % np.mean(sm_v),
                '%+.3f%%' % tdm, '%.1f' % sig,
                '%.3f%%' % np.std(nd_v, ddof=1), note,
            ])
        else:
            table_data.append(['—'] * 5 + [note])

    table = ax.table(cellText=table_data, rowLabels=row_labels,
                     colLabels=col_labels, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2.2)

    for j in range(len(col_labels)):
        table[0, j].set_facecolor('#DDDDDD')
        table[0, j].set_text_props(fontweight='bold')

    # Highlight Helmholtz gain-immune row
    for j in range(len(col_labels)):
        table[2, j].set_facecolor('#FFE0E0')

    ax.set_title('Comprehensive Face Comparison Table — v4\n'
                 'Helmholtz baseline = pre-deployment. '
                 'Teslameter baseline = first tunnel measurement.',
                 fontsize=13, fontweight='bold', pad=20)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v4_D02_face_comparison_table.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  D02: Face comparison table")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("Manager Summary v4: Per-Face Teslameter Re-Analysis")
    print("=" * 70)
    print()

    # ─── Load data ────────────────────────────────────────────────────
    print("Loading Helmholtz data (via v3 loader)...")
    results, helm_raw, temp_final, y_materials = load_all()
    clean = [r for r in results if not r['is_outlier']]
    print("  %d Helmholtz samples (%d outliers excluded)" %
          (len(clean), len(results) - len(clean)))

    print("Loading Teslameter field data (v4 enhanced loader)...")
    tesla_results, temp_history = load_teslameter_field_v4(y_materials)
    clean_tesla = [r for r in tesla_results if not r['is_outlier']]
    print("  %d Teslameter samples (%d outliers excluded)" %
          (len(clean_tesla), len(tesla_results) - len(clean_tesla)))

    gain_syst, session_offsets = get_gain_syst(helm_raw)
    print("\nGain systematic: ±%.4f%%" % gain_syst)

    intra_diffs, intra_details = compute_intra_plate_diffs(clean)
    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    # ─── VERIFICATION: Print ALL key numbers ─────────────────────────
    print("\n" + "=" * 70)
    print("VERIFICATION — All Key Numbers (printed before any plots)")
    print("=" * 70)

    print("\n--- Helmholtz Absolute Values ---")
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals))
            print("  %s: %+.3f%% ± %.3f%% (%.1fσ stat, N=%d)" %
                  (mat, m, s, abs(m/s), len(vals)))

    print("\n--- Helmholtz Gain-Immune Differential ---")
    print("  NdFeB − SmCo: %+.3f%% ± %.3f%% (%.1fσ, N=%d plates)" %
          (diff_mean, diff_sem, diff_sig, len(intra_diffs)))

    print("\n--- Per-Face Teslameter Material Means ---")
    for face in FACES + ['3face_avg']:
        print("  [%s]" % face)
        for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
            if face == '3face_avg':
                vals = [r['pct_change'] for r in clean_tesla if r['material'] == mat]
            else:
                vals = [r['face_pcts'][face] for r in clean_tesla
                        if r['material'] == mat and face in r['face_pcts']]
            if vals:
                m = np.mean(vals)
                s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.5
                std = np.std(vals, ddof=1) if len(vals) > 1 else 0.0
                print("    %s: %+.3f%% ± %.3f%% (%.1fσ, std=%.3f%%, N=%d)" %
                      (mat, m, s, abs(m/s) if s > 0 else 0, std, len(vals)))

    print("\n--- Per-Face Intra-Plate NdFeB−SmCo Differentials ---")
    for face in FACES + ['3face_avg']:
        diffs, details = compute_intra_plate_diffs_tesla(tesla_results, face)
        if diffs:
            m = np.mean(diffs)
            s = np.std(diffs) / np.sqrt(len(diffs)) if len(diffs) > 1 else 0.1
            sig = abs(m / s) if s > 0 else 0
            print("  %s: %+.3f%% ± %.3f%% (%.1fσ, N=%d plates)" %
                  (face, m, s, sig, len(diffs)))
        else:
            print("  %s: no data" % face)

    print("\n--- Face-to-Face Pearson Correlations ---")
    for f1, f2 in [('top', 'front'), ('top', 'side'), ('front', 'side')]:
        v1, v2 = [], []
        for r in clean_tesla:
            if f1 in r['face_pcts'] and f2 in r['face_pcts']:
                v1.append(r['face_pcts'][f1])
                v2.append(r['face_pcts'][f2])
        if len(v1) >= 3:
            r_val = np.corrcoef(v1, v2)[0, 1]
            print("  %s vs %s: r = %.3f (N=%d)" % (f1, f2, r_val, len(v1)))

    print("\n--- Helmholtz vs Teslameter Per-Sample Correlations ---")
    clean_helm_d = {r['sample']: r for r in clean}
    clean_tesla_d = {r['sample']: r for r in clean_tesla}
    common = set(clean_helm_d.keys()) & set(clean_tesla_d.keys())
    for face in FACES + ['3face_avg']:
        hv, tv = [], []
        for sample in common:
            hr = clean_helm_d[sample]
            tr = clean_tesla_d[sample]
            if face == '3face_avg':
                tv_val = tr['pct_change']
            else:
                if face not in tr['face_pcts']:
                    continue
                tv_val = tr['face_pcts'][face]
            hv.append(hr['pct_change'])
            tv.append(tv_val)
        if len(hv) >= 3:
            r_val = np.corrcoef(hv, tv)[0, 1]
            print("  Helmholtz vs %s: r = %.3f (N=%d)" % (face, r_val, len(hv)))

    print("\n--- Session-Delta Pearson Correlations ---")
    helm_date_vals = defaultdict(dict)
    for r in clean:
        for dt, pct in r['date_pcts']:
            helm_date_vals[r['sample']][dt.strftime('%Y-%m-%d')] = pct

    for face in FACES:
        tesla_face_dv = defaultdict(dict)
        for r in clean_tesla:
            if face not in r.get('face_date_pcts', {}):
                continue
            for dt, pct in r['face_date_pcts'][face]:
                tesla_face_dv[r['sample']][dt.strftime('%Y-%m-%d')] = pct

        h_dates = set()
        for sd in helm_date_vals.values():
            h_dates.update(sd.keys())
        t_dates = set()
        for sd in tesla_face_dv.values():
            t_dates.update(sd.keys())
        cd_list = sorted(h_dates & t_dates)

        hd_all, td_all = [], []
        for i in range(len(cd_list) - 1):
            d1, d2 = cd_list[i], cd_list[i + 1]
            for sample in common:
                if (d1 in helm_date_vals.get(sample, {}) and
                    d2 in helm_date_vals.get(sample, {}) and
                    d1 in tesla_face_dv.get(sample, {}) and
                    d2 in tesla_face_dv.get(sample, {})):
                    hd_all.append(helm_date_vals[sample][d2] - helm_date_vals[sample][d1])
                    td_all.append(tesla_face_dv[sample][d2] - tesla_face_dv[sample][d1])

        if len(hd_all) >= 3:
            r_val = np.corrcoef(hd_all, td_all)[0, 1]
            print("  Session-Δ Helmholtz vs %s: r = %.3f (N=%d delta pairs)" %
                  (face, r_val, len(hd_all)))

    # ─── Generate plots ──────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("Generating v4 plots...")
    print("=" * 70)

    print("\nCategory A: Per-Face Core Analysis")
    plot_A01_per_face_material_bars(tesla_results)
    plot_A02_per_face_timeseries(tesla_results)
    plot_A03_intra_plate_diff_by_face(results, tesla_results)
    plot_A04_per_face_scatter_vs_helmholtz(results, tesla_results)

    print("\nCategory B: Statistical Characterization")
    plot_B01_face_statistics_table(results, tesla_results, gain_syst)
    plot_B02_face_to_face_correlation(tesla_results)
    plot_B03_rig_tolerance_by_slot(tesla_results)

    print("\nCategory C: Combined Instrument Analysis")
    plot_C01_helmholtz_vs_teslameter_bars(results, tesla_results, gain_syst)
    plot_C02_session_delta_comparison(results, tesla_results, helm_raw,
                                      temp_final, y_materials)
    plot_C03_intra_plate_diff_timeseries(results, tesla_results,
                                          helm_raw, temp_final,
                                          y_materials=y_materials)

    print("\nCategory D: Summary")
    plot_D01_summary_dashboard(results, tesla_results, gain_syst,
                                helm_raw, temp_final)
    plot_D02_face_comparison_table(results, tesla_results, gain_syst)

    print("\n" + "=" * 70)
    print("All 12 v4 plots saved to: %s/v4_*.png" % PLOT_DIR)
    print("=" * 70)


if __name__ == '__main__':
    main()
