#!/usr/bin/env python3
"""
Manager-Friendly Degradation Summary Plots — v5 Polish + A-Sample Analysis

Regenerates 3 polished key plots (D01, B02, D04), adds lab control (F01),
and adds A-sample (pair) analysis (G01-G04):
  - v5_D01_executive_summary.png  (polished: 4th info box, sans-serif, 200 dpi)
  - v5_B02_pass_number_trend.png  (polished: seeded jitter, trend line, N labels)
  - v5_D04_dashboard.png          (polished: N labels, ref lines, larger table)
  - v5_F01_lab_control_comparison.png (NEW: lab vs tunnel differential)
  - v5_G01_a_sample_helmholtz.png (NEW: A-sample Helmholtz material comparison)
  - v5_G02_a_sample_teslameter.png (NEW: A-sample Teslameter per-face)
  - v5_G03_a_vs_h_helmholtz.png  (NEW: A-sample vs H-plate Helmholtz correlation)
  - v5_G04_a_sample_summary.png  (NEW: combined A+H+Y dashboard)

A-samples are INDIVIDUAL MAGNETS from within H-plate pair assemblies.
Each H-plate has 4 pair slots × 2 magnets = 8 A-samples.
A-samples are always measured OUTSIDE the assembly (disassembled first).
Helmholtz pre-deployment baselines are valid (position-insensitive).
Teslameter baselines = first tunnel measurement (rig/cap changed before deployment).

Imports shared code from v3 + v2 (same chain as v5). Keeps v5.py untouched.
Output: Cleanup_Claude/Manager_Plots_v5/
"""

import os
import sys
import re
import numpy as np
import openpyxl
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
    ALPHA_SLOT, PLACEMENTS as PLACEMENTS_SIMPLE,
    parse_helmholtz_file, parse_teslameter_file,
    TESLAMETER_FIELD_VALID_AFTER,
)

# ─── Imports from v2 ─────────────────────────────────────────────────────────
from degradation_summary_v2 import (
    load_materials, build_temperature_lookup,
    compute_h_plate_degradation,
    PLACEMENTS as PLACEMENTS_FULL,
    H_PLACEMENT, ALPHA, correct_helmholtz, compute_robust_baseline,
    get_all_mwc_rows, parse_helmholtz_file as parse_helmholtz_v2,
    TUNNEL_START,
)

# ─── Imports from v5 ─────────────────────────────────────────────────────────
from manager_summary_v5 import (
    PLACEMENTS_WITH_LINE, HMAT_COLORS, CONFIG_COLORS, CONFIG_HATCHES,
    PASS_LABELS, build_h_plate_timeseries,
)

# ─── Output directory ────────────────────────────────────────────────────────
PLOT_DIR = os.path.join(BASE, 'Manager_Plots_v5')
os.makedirs(PLOT_DIR, exist_ok=True)

# ─── Slot-to-material mapping ────────────────────────────────────────────────
MAT_BY_SLOT = {1: 'N42EH', 2: 'N52SH', 3: 'SmCo33H', 4: 'SmCo35'}

# ─── Lab Y-plate numbers (not deployed in tunnel) ────────────────────────────
LAB_Y_PLATES = [8, 14, 27, 28, 29, 31, 33, 35, 37]


# ═══════════════════════════════════════════════════════════════════════════════
# LAB Y-PLATE LOADER
# ═══════════════════════════════════════════════════════════════════════════════

def load_lab_y_materials():
    """Load lab Y-plate material assignments from spreadsheet.

    Returns dict: sample_id -> material_name (e.g. 'Y-8-1' -> 'N52SH')
    Lab plates have RANDOMIZED slot-to-material mapping, just like tunnel.
    """
    wb = openpyxl.load_workbook(os.path.join(BASE, 'Materials_Arrangements.xlsx'),
                                 data_only=True)
    lab_mats = {}
    for row in wb['Lab - Y Materials'].iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        pm = re.match(r'[yY]-?(\d+)', str(row[0]).strip())
        if not pm:
            continue
        pn = pm.group(1)
        for i, v in enumerate(row[1:5], 1):
            if v:
                lab_mats['Y-%s-%d' % (pn, i)] = str(v).strip()
    return lab_mats


def load_lab_y_plates(apply_temp_correction=True):
    """Load lab control Y-plate Helmholtz data.

    For each lab plate, the Y_Plates/Helmholtz/ directory contains all dates
    (baseline + latest). Earliest date = baseline, latest date = final.

    Uses spreadsheet for correct slot-to-material mapping (randomized).
    When apply_temp_correction=True, corrects readings to T_ref=20°C using
    LAB_TEMP_LOOKUP from lab_ha_analysis.

    Returns dict of plate_num -> {plate, slot_pcts: {mat: pct},
        slot_pcts_raw: {mat: pct}, nd_mean, sm_mean, diff,
        temp_corrected, sigma_temp_pct: {mat: sigma}}
    """
    from Lab_Controls.lab_ha_analysis import (
        get_lab_temp, temp_correct_reading, T_REF as LAB_T_REF,
    )
    # Material-class alpha for Y-plate slots
    Y_ALPHA = {
        'N42EH': -0.0010, 'N52SH': -0.0011,
        'SmCo33H': -0.0004, 'SmCo35': -0.0004,
    }

    helm_dir = os.path.join(BASE, 'Y_Plates', 'Helmholtz')
    lab_mats = load_lab_y_materials()
    plate_results = {}

    for plate_num in LAB_Y_PLATES:
        slot_pcts = {}
        slot_pcts_raw = {}
        slot_sigma_temp = {}
        for slot in [1, 2, 3, 4]:
            sample = 'Y-%d-%d' % (plate_num, slot)
            fpath = os.path.join(helm_dir, '%s_helmholtz.dat' % sample)
            if not os.path.exists(fpath):
                continue
            rows = parse_helmholtz_file(fpath)
            mwc = [(dt, v) for dt, v, u in rows
                   if u == 'mWC' and abs(v - SENTINEL) > 1 and abs(v) >= 0.1]
            if len(mwc) < 2:
                continue

            mwc.sort(key=lambda x: x[0])
            baseline_dt, baseline_val = mwc[0]
            latest_dt, latest_val = mwc[-1]

            if abs(baseline_val) < 0.1:
                continue

            mat = lab_mats.get(sample, MAT_BY_SLOT.get(slot, 'Unknown'))
            pct_raw = (latest_val - baseline_val) / baseline_val * 100.0
            slot_pcts_raw[mat] = pct_raw

            if apply_temp_correction and mat in Y_ALPHA:
                alpha = Y_ALPHA[mat]
                bl_temp, bl_sig, _ = get_lab_temp(baseline_dt.strftime('%Y-%m-%d'))
                lt_temp, lt_sig, _ = get_lab_temp(latest_dt.strftime('%Y-%m-%d'))
                bl_corr = temp_correct_reading(baseline_val, bl_temp, alpha)
                lt_corr = temp_correct_reading(latest_val, lt_temp, alpha)
                pct = (lt_corr - bl_corr) / bl_corr * 100.0
                sigma_t = abs(alpha) * np.sqrt(bl_sig**2 + lt_sig**2) * 100.0
            else:
                pct = pct_raw
                sigma_t = 0.0

            slot_pcts[mat] = pct
            slot_sigma_temp[mat] = sigma_t

        if not slot_pcts:
            continue

        nd_vals = [slot_pcts[m] for m in ['N42EH', 'N52SH'] if m in slot_pcts]
        sm_vals = [slot_pcts[m] for m in ['SmCo33H', 'SmCo35'] if m in slot_pcts]

        nd_mean = np.mean(nd_vals) if nd_vals else np.nan
        sm_mean = np.mean(sm_vals) if sm_vals else np.nan
        diff = nd_mean - sm_mean if nd_vals and sm_vals else np.nan

        plate_results[plate_num] = {
            'plate': plate_num,
            'slot_pcts': slot_pcts,
            'slot_pcts_raw': slot_pcts_raw,
            'nd_mean': nd_mean,
            'sm_mean': sm_mean,
            'diff': diff,
            'temp_corrected': apply_temp_correction,
            'sigma_temp_pct': slot_sigma_temp,
        }

    return plate_results


# ═══════════════════════════════════════════════════════════════════════════════
# A-SAMPLE (INDIVIDUAL MAGNET) LOADERS
# ═══════════════════════════════════════════════════════════════════════════════

def load_a_sample_helmholtz(temp_lookup):
    """Load A-sample Helmholtz data with temperature correction.

    A-samples = pairs (2 small magnets in a fixed enclosure, measured together).
    Each H-plate slot contains 2 A-samples (pairs).
    Naming: An-XX-Y-Z (NdFeB) or As-XX-Y-Z (SmCo), where
        XX = plate number, Y = H-plate slot (1-4), Z = pair within slot (1-2)
    Pre-deployment baselines are valid (Helmholtz is position-insensitive).

    Returns list of dicts with pct_change, material, plate, slot, pair index, etc.
    """
    helm_dir = os.path.join(BASE, 'Pair_Assemblies', 'Helmholtz')
    tesla_dir = os.path.join(BASE, 'Pair_Assemblies', 'Teslameter')
    results = []

    for f in sorted(os.listdir(helm_dir)):
        m = re.match(r'(A[ns]-\d+-\d+-\d+)_helmholtz\.dat$', f)
        if not m:
            continue
        a_sample = m.group(1)
        am = re.match(r'A([ns])-(\d+)-(\d+)-(\d+)', a_sample)
        if not am:
            continue
        ns = am.group(1)
        plate_num = int(am.group(2))
        pair_slot = int(am.group(3))
        magnet_idx = int(am.group(4))
        mat_type = 'NdFeB' if ns == 'n' else 'SmCo'
        alpha = ALPHA[mat_type]

        # Build per-date temperature from A-sample's own Teslameter
        a_temp = {}
        faces = ['front', 'side', 'top']
        for face in faces:
            tpath = os.path.join(tesla_dir, '%s_%s.dat' % (a_sample, face))
            if not os.path.exists(tpath):
                continue
            rows = parse_teslameter_file(tpath)
            for dt, fields, temp in rows:
                if temp is None or abs(temp - SENTINEL) < 1:
                    continue
                date_str = dt.strftime('%Y-%m-%d')
                if date_str not in a_temp:
                    a_temp[date_str] = []
                a_temp[date_str].append(temp)

        a_temp_mean = {}
        for date_str, temps in a_temp.items():
            a_temp_mean[date_str] = np.mean(temps)

        # Also check the H-plate level temp lookup as fallback
        h_sample = 'H%s-%d-%d' % (ns, plate_num, pair_slot)

        # Parse Helmholtz
        fpath = os.path.join(helm_dir, f)
        rows = parse_helmholtz_file(fpath)
        mwc = [(dt, v) for dt, v, u in rows
               if u == 'mWC' and abs(v - SENTINEL) > 1 and abs(v) >= 0.1]
        if not mwc:
            continue

        # Temperature-correct where possible
        pre_corr = []
        tunnel_corr = []
        pre_raw = []
        tunnel_raw = []
        for dt, h_raw in mwc:
            date_str = dt.strftime('%Y-%m-%d')
            # Try A-sample temp first, then H-plate temp lookup
            t_mean = None
            if date_str in a_temp_mean:
                t_mean = a_temp_mean[date_str]
            elif (h_sample, date_str) in temp_lookup:
                t_mean = temp_lookup[(h_sample, date_str)][0]
            elif (a_sample, date_str) in temp_lookup:
                t_mean = temp_lookup[(a_sample, date_str)][0]

            if t_mean is not None:
                h_corr = h_raw / (1 + alpha * (t_mean - T_REF))
                if dt < TUNNEL_START:
                    pre_corr.append(h_corr)
                else:
                    tunnel_corr.append((dt, h_corr))
            else:
                # No temp: use raw (will be flagged)
                if dt < TUNNEL_START:
                    pre_raw.append(h_raw)
                else:
                    tunnel_raw.append((dt, h_raw))

        # Use corrected if available, else raw
        if pre_corr and tunnel_corr:
            bl_mean = np.mean(pre_corr)
            tunnel_corr.sort(key=lambda x: x[0])
            latest = tunnel_corr[-1][1]
            pct = (latest - bl_mean) / bl_mean * 100.0
            temp_corrected = True
            n_baseline = len(pre_corr)
            date_pcts = [(dt, (v - bl_mean) / bl_mean * 100.0)
                         for dt, v in tunnel_corr]
        elif pre_raw and tunnel_raw:
            bl_mean = np.mean(pre_raw)
            tunnel_raw.sort(key=lambda x: x[0])
            latest = tunnel_raw[-1][1]
            pct = (latest - bl_mean) / bl_mean * 100.0
            temp_corrected = False
            n_baseline = len(pre_raw)
            date_pcts = [(dt, (v - bl_mean) / bl_mean * 100.0)
                         for dt, v in tunnel_raw]
        else:
            continue

        if abs(bl_mean) < 0.1:
            continue

        is_outlier = abs(pct) > 5.0 or (n_baseline == 1 and abs(pct) > 2.0)

        # Placement info from H_PLACEMENT
        h_lookup_key = '%s%d' % ('N' if ns == 'n' else 'S', plate_num)
        placement = H_PLACEMENT.get(h_lookup_key, {})
        region = placement.get('region', 'Unknown')
        line = placement.get('line', 0)

        results.append({
            'sample': a_sample, 'plate': plate_num, 'pair_slot': pair_slot,
            'magnet_idx': magnet_idx, 'material': mat_type,
            'pct_change': pct, 'is_outlier': is_outlier,
            'bl_mean': bl_mean, 'n_baseline': n_baseline,
            'temp_corrected': temp_corrected,
            'region': region, 'line': line,
            'date_pcts': date_pcts,
            'h_sample': h_sample,
        })

    return results


def load_a_sample_teslameter():
    """Load A-sample Teslameter field data.

    Baseline = first tunnel measurement (rig/cap changed before deployment,
    so pre-deployment field readings are not comparable).
    A-samples are always measured OUTSIDE the assembly.

    Returns list of per-sample dicts with per-face and mean % changes.
    """
    tesla_dir = os.path.join(BASE, 'Pair_Assemblies', 'Teslameter')
    faces = ['front', 'side', 'top']

    # Discover all A-samples
    a_samples = set()
    for f in os.listdir(tesla_dir):
        m = re.match(r'(A[ns]-\d+-\d+-\d+)_(front|side|top)\.dat$', f)
        if m:
            a_samples.add(m.group(1))

    results = []
    for a_sample in sorted(a_samples):
        am = re.match(r'A([ns])-(\d+)-(\d+)-(\d+)', a_sample)
        if not am:
            continue
        ns = am.group(1)
        plate_num = int(am.group(2))
        pair_slot = int(am.group(3))
        magnet_idx = int(am.group(4))
        mat_type = 'NdFeB' if ns == 'n' else 'SmCo'
        alpha = ALPHA[mat_type]

        h_lookup_key = '%s%d' % ('N' if ns == 'n' else 'S', plate_num)
        placement = H_PLACEMENT.get(h_lookup_key, {})
        region = placement.get('region', 'Unknown')
        if region == 'Unknown':
            continue

        face_pcts = {}
        for face in faces:
            fpath = os.path.join(tesla_dir, '%s_%s.dat' % (a_sample, face))
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
                corrected.append((dt, mag_corr))

            if len(corrected) < 2:
                continue
            corrected.sort(key=lambda x: x[0])
            bl_mag = corrected[0][1]
            lt_mag = corrected[-1][1]
            if abs(bl_mag) < 1.0:
                continue
            face_pcts[face] = (lt_mag - bl_mag) / bl_mag * 100.0

        if not face_pcts:
            continue

        mean_pct = np.mean(list(face_pcts.values()))

        results.append({
            'sample': a_sample, 'plate': plate_num, 'pair_slot': pair_slot,
            'magnet_idx': magnet_idx, 'material': mat_type,
            'region': region,
            'face_pcts': face_pcts,
            'mean_pct': mean_pct,
            'top_pct': face_pcts.get('top', np.nan),
            'front_pct': face_pcts.get('front', np.nan),
            'side_pct': face_pcts.get('side', np.nan),
        })

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# A-SAMPLE PLOTS (G01-G04)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_G01_a_helmholtz(a_helm_results, gain_syst):
    """A-sample Helmholtz material comparison: NdFeB vs SmCo."""
    clean = [r for r in a_helm_results if not r['is_outlier']]
    nd = [r['pct_change'] for r in clean if r['material'] == 'NdFeB']
    sm = [r['pct_change'] for r in clean if r['material'] == 'SmCo']

    nd_mean = np.mean(nd) if nd else 0
    sm_mean = np.mean(sm) if sm else 0
    nd_sem = np.std(nd, ddof=1) / np.sqrt(len(nd)) if len(nd) > 1 else 0.05
    sm_sem = np.std(sm, ddof=1) / np.sqrt(len(sm)) if len(sm) > 1 else 0.05

    nd_tc = [r for r in clean if r['material'] == 'NdFeB' and r['temp_corrected']]
    sm_tc = [r for r in clean if r['material'] == 'SmCo' and r['temp_corrected']]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7),
                                     gridspec_kw={'width_ratios': [1, 1.5]})

    # Left: material bars
    bars = ax1.bar([0, 1], [nd_mean, sm_mean], yerr=[nd_sem, sm_sem],
                   color=['#CC4444', '#44AA44'], capsize=10,
                   edgecolor='black', linewidth=1, alpha=0.85, width=0.5,
                   error_kw=dict(linewidth=2.5, capthick=2.5))
    ax1.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax1.axhline(0, color='black', linewidth=1.5)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(['NdFeB\n(N=%d)' % len(nd),
                          'SmCo\n(N=%d)' % len(sm)], fontsize=12)
    ax1.set_ylabel('% Change from Pre-Deployment Baseline', fontsize=11)
    ax1.set_title('A-Sample Helmholtz: Material Comparison\n'
                  '(pairs from H-plate slot assemblies)',
                  fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # Significance annotations
    for i, (val, sem, n, color) in enumerate(
            [(nd_mean, nd_sem, len(nd), '#CC4444'),
             (sm_mean, sm_sem, len(sm), '#44AA44')]):
        sig = abs(val / sem) if sem > 0 else 0
        y = val - sem - 0.01 if val < 0 else val + sem + 0.01
        va = 'top' if val < 0 else 'bottom'
        ax1.text(i, y, '%.1f\u03c3' % sig, ha='center', va=va,
                 fontsize=10, fontweight='bold', color=color)

    # Note about temp correction coverage
    tc_frac_nd = len(nd_tc) / len(nd) * 100 if nd else 0
    tc_frac_sm = len(sm_tc) / len(sm) * 100 if sm else 0
    ax1.annotate('Temp-corrected: NdFeB %.0f%%, SmCo %.0f%%' % (tc_frac_nd, tc_frac_sm),
                 xy=(0.02, 0.02), xycoords='axes fraction',
                 fontsize=8, color='#666666', fontstyle='italic')

    # Right: strip plot of all A-samples
    np.random.seed(42)
    for r in clean:
        x = 0 if r['material'] == 'NdFeB' else 1
        jitter = np.random.normal(0, 0.08)
        color = '#CC4444' if r['material'] == 'NdFeB' else '#44AA44'
        alpha_v = 0.3 if r['temp_corrected'] else 0.15
        ax2.scatter(x + jitter, r['pct_change'], s=12, color=color,
                    alpha=alpha_v, edgecolor='none', zorder=3)

    ax2.hlines(nd_mean, -0.3, 0.3, colors='#CC4444', linewidth=2.5, zorder=4)
    ax2.hlines(sm_mean, 0.7, 1.3, colors='#44AA44', linewidth=2.5, zorder=4)
    ax2.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax2.axhline(0, color='black', linewidth=1, linestyle='--')

    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(['NdFeB (N=%d)' % len(nd), 'SmCo (N=%d)' % len(sm)],
                         fontsize=11)
    ax2.set_ylabel('% Change from Pre-Deployment Baseline', fontsize=11)
    ax2.set_title('A-Sample Individual Distributions\n'
                  '(faint = uncorrected for temperature)',
                  fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_xlim(-0.5, 1.5)

    # Mean annotations
    ax2.annotate('%+.3f%%' % nd_mean, xy=(0.35, nd_mean),
                 fontsize=10, fontweight='bold', color='#CC4444', va='center')
    ax2.annotate('%+.3f%%' % sm_mean, xy=(1.35, sm_mean),
                 fontsize=10, fontweight='bold', color='#44AA44', va='center')

    fig.suptitle('A-Sample (Individual Magnet) Helmholtz Analysis\n'
                 'Gray band = \u00b1%.2f%% Helmholtz gain systematic' % gain_syst,
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(PLOT_DIR, 'v5_G01_a_sample_helmholtz.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  G01: A-sample Helmholtz material comparison")


def plot_G02_a_teslameter(a_tesla_results):
    """A-sample Teslameter per-face analysis."""
    nd = [r for r in a_tesla_results if r['material'] == 'NdFeB']
    sm = [r for r in a_tesla_results if r['material'] == 'SmCo']

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # (a) Per-face material bars
    ax = axes[0, 0]
    faces = ['top', 'front', 'side']
    face_labels = ['Top', 'Front', 'Side']
    x = np.arange(len(faces))
    width = 0.35

    for i, (data, mat, color) in enumerate([(nd, 'NdFeB', '#CC4444'),
                                             (sm, 'SmCo', '#44AA44')]):
        means, sems, ns_arr = [], [], []
        for face in faces:
            vals = [r['%s_pct' % face] for r in data
                    if np.isfinite(r.get('%s_pct' % face, np.nan))]
            if vals:
                means.append(np.mean(vals))
                sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                            if len(vals) > 1 else 0.5)
                ns_arr.append(len(vals))
            else:
                means.append(0); sems.append(0); ns_arr.append(0)
        offset = -width / 2 + i * width
        bars = ax.bar(x + offset, means, width, yerr=sems, color=color,
                      capsize=4, edgecolor='black', linewidth=0.5,
                      alpha=0.85, label='%s (N=%d)' % (mat, len(data)))
        for j in range(len(faces)):
            if ns_arr[j] > 0:
                ax.text(x[j] + offset, means[j] + (sems[j] + 0.05) * np.sign(means[j] + 0.01),
                        '%d' % ns_arr[j], ha='center', va='bottom', fontsize=7, color=color)

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_xticks(x)
    ax.set_xticklabels(face_labels, fontsize=11)
    ax.set_ylabel('% Change', fontsize=11)
    ax.set_title('(a) A-Sample Teslameter by Face', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # (b) Per-face box plots
    ax = axes[0, 1]
    bp_data = []
    bp_labels = []
    bp_colors = []
    for face in faces:
        for mat, data, color in [('Nd', nd, '#CC4444'), ('Sm', sm, '#44AA44')]:
            vals = [r['%s_pct' % face] for r in data
                    if np.isfinite(r.get('%s_pct' % face, np.nan))]
            bp_data.append(vals if vals else [0])
            bp_labels.append('%s\n%s' % (face.capitalize(), mat))
            bp_colors.append(color)

    bp = ax.boxplot(bp_data, labels=bp_labels, patch_artist=True, showmeans=True,
                    meanprops=dict(marker='D', markerfacecolor='black', markersize=4))
    for patch, color in zip(bp['boxes'], bp_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.4)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_ylabel('% Change', fontsize=11)
    ax.set_title('(b) Distribution by Face', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.tick_params(axis='x', labelsize=8)

    # (c) Per-face scatter: NdFeB−SmCo check
    ax = axes[1, 0]
    face_std = {}
    for face, label in zip(faces, face_labels):
        nd_vals = [r['%s_pct' % face] for r in nd
                   if np.isfinite(r.get('%s_pct' % face, np.nan))]
        sm_vals = [r['%s_pct' % face] for r in sm
                   if np.isfinite(r.get('%s_pct' % face, np.nan))]
        nd_m = np.mean(nd_vals) if nd_vals else np.nan
        sm_m = np.mean(sm_vals) if sm_vals else np.nan
        nd_s = np.std(nd_vals, ddof=1) if len(nd_vals) > 1 else 0
        sm_s = np.std(sm_vals, ddof=1) if len(sm_vals) > 1 else 0
        face_std[face] = {'nd_std': nd_s, 'sm_std': sm_s, 'nd_n': len(nd_vals), 'sm_n': len(sm_vals)}
        ax.annotate('%s: Nd=%.2f%% SmCo=%.2f%% (std %.2f%%, %.2f%%)' %
                    (label, nd_m, sm_m, nd_s, sm_s),
                    xy=(0.02, 0.95 - faces.index(face) * 0.08),
                    xycoords='axes fraction', fontsize=9)

    # Show top-face data as scatter
    nd_top = [r['top_pct'] for r in nd if np.isfinite(r.get('top_pct', np.nan))]
    sm_top = [r['top_pct'] for r in sm if np.isfinite(r.get('top_pct', np.nan))]
    np.random.seed(42)
    ax.scatter(np.random.normal(0, 0.06, len(nd_top)), nd_top,
               s=15, color='#CC4444', alpha=0.4, label='NdFeB top')
    ax.scatter(np.random.normal(1, 0.06, len(sm_top)), sm_top,
               s=15, color='#44AA44', alpha=0.4, label='SmCo top')
    if nd_top:
        ax.hlines(np.mean(nd_top), -0.3, 0.3, colors='#CC4444', linewidth=2)
    if sm_top:
        ax.hlines(np.mean(sm_top), 0.7, 1.3, colors='#44AA44', linewidth=2)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['NdFeB', 'SmCo'], fontsize=11)
    ax.set_ylabel('Top-Face % Change', fontsize=11)
    ax.set_title('(c) A-Sample Top Face (best precision)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)

    # (d) Summary statistics table
    ax = axes[1, 1]
    ax.axis('off')
    rows = []
    for face in faces:
        for mat_label, data in [('NdFeB', nd), ('SmCo', sm)]:
            vals = [r['%s_pct' % face] for r in data
                    if np.isfinite(r.get('%s_pct' % face, np.nan))]
            if vals:
                m = np.mean(vals)
                s = np.std(vals, ddof=1)
                sem = s / np.sqrt(len(vals))
                rows.append([face.capitalize(), mat_label, '%+.2f%%' % m,
                             '%.2f%%' % s, '%.2f%%' % sem, str(len(vals))])
    table = ax.table(cellText=rows,
                     colLabels=['Face', 'Material', 'Mean', 'Std', 'SEM', 'N'],
                     loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.6)
    for j in range(6):
        table[(0, j)].set_facecolor('#DDDDDD')
        table[(0, j)].set_text_props(fontweight='bold')
    ax.set_title('(d) A-Sample Teslameter Statistics', fontsize=12,
                 fontweight='bold', pad=20)

    fig.suptitle('A-Sample (Individual Magnet) Teslameter Analysis\n'
                 'Baseline = first tunnel measurement (rig changed before deployment)',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(PLOT_DIR, 'v5_G02_a_sample_teslameter.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  G02: A-sample Teslameter per-face")


def plot_G03_a_vs_h(a_helm_results, h_results):
    """Scatter plot: A-sample Helmholtz vs co-located H-plate Helmholtz."""
    a_clean = [r for r in a_helm_results if not r['is_outlier']]
    h_clean = {r['sample']: r for r in h_results if not r.get('is_outlier', False)}

    # Match: for each A-sample, find the corresponding H-plate result
    # A-sample An-XX-Y-Z corresponds to H-sample Hn-XX-Y
    pairs = []
    for a in a_clean:
        h_key = a['h_sample']
        if h_key in h_clean:
            pairs.append((a['pct_change'], h_clean[h_key]['pct_change'],
                          a['material'], a['sample']))

    if not pairs:
        print("  G03: No matched A-H pairs found, skipping")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Left: scatter A vs H
    nd_pairs = [(a, h) for a, h, m, _ in pairs if m == 'NdFeB']
    sm_pairs = [(a, h) for a, h, m, _ in pairs if m == 'SmCo']

    if nd_pairs:
        ax1.scatter([p[0] for p in nd_pairs], [p[1] for p in nd_pairs],
                    color='#CC4444', alpha=0.5, s=30, edgecolor='black',
                    linewidth=0.3, label='NdFeB (N=%d)' % len(nd_pairs), zorder=3)
    if sm_pairs:
        ax1.scatter([p[0] for p in sm_pairs], [p[1] for p in sm_pairs],
                    color='#44AA44', alpha=0.5, s=30, edgecolor='black',
                    linewidth=0.3, label='SmCo (N=%d)' % len(sm_pairs), zorder=3)

    # 1:1 line
    all_vals = [p[0] for p in pairs] + [p[1] for p in pairs]
    lim = max(abs(min(all_vals)), abs(max(all_vals))) * 1.2
    ax1.plot([-lim, lim], [-lim, lim], 'k--', alpha=0.3, linewidth=1, label='1:1')
    ax1.set_xlabel('A-Sample (pair) % Change', fontsize=11)
    ax1.set_ylabel('H-Plate (pair assembly) % Change', fontsize=11)
    ax1.set_title('A-Sample vs H-Plate Helmholtz\n(same magnet, different measurement level)',
                  fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.3)

    # Correlation
    if len(pairs) > 2:
        a_vals = np.array([p[0] for p in pairs])
        h_vals = np.array([p[1] for p in pairs])
        r_corr = np.corrcoef(a_vals, h_vals)[0, 1]
        ax1.annotate('r = %.3f (N=%d)' % (r_corr, len(pairs)),
                     xy=(0.02, 0.98), xycoords='axes fraction',
                     fontsize=10, fontweight='bold', va='top',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                               edgecolor='gray', alpha=0.8))

    # Right: residual (A - H) distribution
    residuals_nd = [a - h for a, h, m, _ in pairs if m == 'NdFeB']
    residuals_sm = [a - h for a, h, m, _ in pairs if m == 'SmCo']

    bins = np.linspace(-2, 2, 25)
    if residuals_nd:
        ax2.hist(residuals_nd, bins=bins, color='#CC4444', alpha=0.5,
                 edgecolor='black', linewidth=0.5, label='NdFeB')
    if residuals_sm:
        ax2.hist(residuals_sm, bins=bins, color='#44AA44', alpha=0.5,
                 edgecolor='black', linewidth=0.5, label='SmCo')
    ax2.axvline(0, color='black', linewidth=1.5, linestyle='--')
    ax2.set_xlabel('A-Sample minus H-Plate (% Change)', fontsize=11)
    ax2.set_ylabel('Count', fontsize=11)
    ax2.set_title('Residual Distribution (A \u2212 H)\nExpected ~0 if consistent',
                  fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', alpha=0.3)

    # Stats
    all_resid = [a - h for a, h, _, _ in pairs]
    ax2.annotate('Mean residual: %+.3f%%\nStd: %.3f%%' % (
        np.mean(all_resid), np.std(all_resid)),
        xy=(0.98, 0.98), xycoords='axes fraction',
        fontsize=10, ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                  edgecolor='gray', alpha=0.8))

    fig.suptitle('A-Sample (Individual Magnet) vs H-Plate (Pair Assembly) Consistency',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(PLOT_DIR, 'v5_G03_a_vs_h_helmholtz.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  G03: A-sample vs H-plate Helmholtz correlation")


def plot_G04_a_summary(a_helm_results, a_tesla_results, h_results,
                        y_results, gain_syst, intra_diffs):
    """Combined A+H+Y summary dashboard."""
    a_clean = [r for r in a_helm_results if not r['is_outlier']]
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]
    y_clean = [r for r in y_results if not r['is_outlier']]

    fig, axes = plt.subplots(2, 3, figsize=(20, 12))

    # (a) All three measurement levels: Y, H, A — NdFeB
    ax = axes[0, 0]
    levels = []
    for label, data, mat_filter in [
            ('Y-plate\n(4 grades)', y_clean, ['N42EH', 'N52SH']),
            ('H-plate\n(pair)', h_clean, ['NdFeB']),
            ('A-sample\n(individual)', a_clean, ['NdFeB'])]:
        vals = [r['pct_change'] for r in data if r['material'] in mat_filter]
        if vals:
            levels.append((label, np.mean(vals),
                           np.std(vals, ddof=1) / np.sqrt(len(vals)),
                           len(vals)))
    if levels:
        x = range(len(levels))
        bars = ax.bar(x, [l[1] for l in levels],
                      yerr=[l[2] for l in levels],
                      color='#CC4444', capsize=6, edgecolor='black',
                      linewidth=0.5, alpha=0.85, width=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(['%s\n(N=%d)' % (l[0], l[3]) for l in levels],
                            fontsize=9)
        for i, l in enumerate(levels):
            ax.text(i, l[1] - l[2] - 0.01, '%+.3f%%' % l[1],
                    ha='center', va='top', fontsize=9, fontweight='bold',
                    color='#CC4444')
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_ylabel('% Change', fontsize=11)
    ax.set_title('(a) NdFeB: Y vs H vs A', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # (b) SmCo comparison
    ax = axes[0, 1]
    levels = []
    for label, data, mat_filter in [
            ('Y-plate\n(4 grades)', y_clean, ['SmCo33H', 'SmCo35']),
            ('H-plate\n(pair)', h_clean, ['SmCo']),
            ('A-sample\n(individual)', a_clean, ['SmCo'])]:
        vals = [r['pct_change'] for r in data if r['material'] in mat_filter]
        if vals:
            levels.append((label, np.mean(vals),
                           np.std(vals, ddof=1) / np.sqrt(len(vals)),
                           len(vals)))
    if levels:
        x = range(len(levels))
        bars = ax.bar(x, [l[1] for l in levels],
                      yerr=[l[2] for l in levels],
                      color='#44AA44', capsize=6, edgecolor='black',
                      linewidth=0.5, alpha=0.85, width=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(['%s\n(N=%d)' % (l[0], l[3]) for l in levels],
                            fontsize=9)
        for i, l in enumerate(levels):
            y_pos = l[1] + l[2] + 0.01 if l[1] >= 0 else l[1] - l[2] - 0.01
            va = 'bottom' if l[1] >= 0 else 'top'
            ax.text(i, y_pos, '%+.3f%%' % l[1],
                    ha='center', va=va, fontsize=9, fontweight='bold',
                    color='#44AA44')
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_ylabel('% Change', fontsize=11)
    ax.set_title('(b) SmCo: Y vs H vs A', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # (c) A-sample Teslameter top-face: NdFeB vs SmCo
    ax = axes[0, 2]
    nd_top = [r['top_pct'] for r in a_tesla_results
              if r['material'] == 'NdFeB' and np.isfinite(r.get('top_pct', np.nan))]
    sm_top = [r['top_pct'] for r in a_tesla_results
              if r['material'] == 'SmCo' and np.isfinite(r.get('top_pct', np.nan))]
    top_data = []
    for label, vals, color in [('NdFeB', nd_top, '#CC4444'), ('SmCo', sm_top, '#44AA44')]:
        if vals:
            top_data.append((label, np.mean(vals),
                             np.std(vals, ddof=1) / np.sqrt(len(vals)),
                             len(vals), color))
    if top_data:
        bx = range(len(top_data))
        ax.bar(bx, [t[1] for t in top_data],
               yerr=[t[2] for t in top_data],
               color=[t[4] for t in top_data], capsize=6,
               edgecolor='black', linewidth=0.5, alpha=0.85, width=0.5)
        ax.set_xticks(bx)
        ax.set_xticklabels(['%s\n(N=%d)' % (t[0], t[3]) for t in top_data], fontsize=10)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_ylabel('% Change (top face)', fontsize=11)
    ax.set_title('(c) A-Sample Teslameter (top face)', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # (d) A-sample time series (Helmholtz)
    ax = axes[1, 0]
    for mat, color, label in [('NdFeB', '#CC4444', 'NdFeB'),
                                ('SmCo', '#44AA44', 'SmCo')]:
        date_vals = defaultdict(list)
        for r in a_clean:
            if r['material'] != mat:
                continue
            for dt, pct in r.get('date_pcts', []):
                date_vals[dt.strftime('%Y-%m-%d')].append(pct)
        dates = sorted(d for d in date_vals if len(date_vals[d]) >= 5)
        if not dates:
            continue
        dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        m_vals = [np.mean(date_vals[d]) for d in dates]
        ax.plot(dt_objs, m_vals, 'o-', color=color, markersize=5,
                linewidth=1.5, label='%s (N\u2265%d)' % (label, 5))
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.set_ylabel('% Change', fontsize=11)
    ax.set_title('(d) A-Sample Helmholtz Time Series', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # (e) A-sample by region
    ax = axes[1, 1]
    from manager_summary_v3 import REGION_ORDER, REGION_COLORS
    x_pos = np.arange(len(REGION_ORDER))
    width = 0.35
    for i, (mat, color) in enumerate([('NdFeB', '#CC4444'), ('SmCo', '#44AA44')]):
        means = []
        for region in REGION_ORDER:
            vals = [r['pct_change'] for r in a_clean
                    if r['material'] == mat and r['region'] == region]
            means.append(np.mean(vals) if vals else np.nan)
        offset = -width / 2 + i * width
        ax.bar(x_pos + offset, means, width, color=color,
               edgecolor='black', linewidth=0.5, alpha=0.85, label=mat)
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([r.replace(' ', '\n') for r in REGION_ORDER],
                        fontsize=8, rotation=0)
    ax.set_ylabel('% Change', fontsize=11)
    ax.set_title('(e) A-Sample by Region', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)

    # (f) Key numbers table
    ax = axes[1, 2]
    ax.axis('off')

    a_nd = [r['pct_change'] for r in a_clean if r['material'] == 'NdFeB']
    a_sm = [r['pct_change'] for r in a_clean if r['material'] == 'SmCo']
    h_nd = [r['pct_change'] for r in h_clean if r['material'] == 'NdFeB']
    h_sm = [r['pct_change'] for r in h_clean if r['material'] == 'SmCo']
    y_nd = [r['pct_change'] for r in y_clean if r['material'] in ['N42EH', 'N52SH']]
    y_sm = [r['pct_change'] for r in y_clean if r['material'] in ['SmCo33H', 'SmCo35']]

    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))

    rows = []
    for label, vals in [('Y NdFeB', y_nd), ('Y SmCo', y_sm),
                         ('H NdFeB', h_nd), ('H SmCo', h_sm),
                         ('A NdFeB', a_nd), ('A SmCo', a_sm)]:
        if vals:
            m = np.mean(vals)
            sem = np.std(vals, ddof=1) / np.sqrt(len(vals))
            sig = abs(m / sem) if sem > 0 else 0
            rows.append([label, '%+.3f%%' % m, '%.3f%%' % sem,
                         '%.1f\u03c3' % sig, str(len(vals))])

    rows.append(['Y NdFeB\u2212SmCo', '%+.3f%%' % diff_mean,
                 '%.3f%%' % diff_sem, '%.1f\u03c3' % (abs(diff_mean / diff_sem)),
                 '%d pl' % len(intra_diffs)])
    rows.append(['Gain syst.', '\u00b1%.3f%%' % gain_syst, '', '', ''])

    table = ax.table(cellText=rows,
                     colLabels=['Quantity', 'Value', 'SEM', 'Sig', 'N'],
                     loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.6)
    for j in range(5):
        table[(0, j)].set_facecolor('#DDDDDD')
        table[(0, j)].set_text_props(fontweight='bold')
    # Highlight gain-immune row
    for j in range(5):
        table[(len(rows) - 1, j)].set_facecolor('#FFF0CC')
    ax.set_title('(f) All Measurement Levels', fontsize=12,
                 fontweight='bold', pad=20)

    fig.suptitle('Combined Y-Plate + H-Plate + A-Sample Analysis\n'
                 'CEBAF Tunnel Jul 2025 \u2013 Jan 2026 (Preliminary)',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(PLOT_DIR, 'v5_G04_a_sample_summary.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  G04: Combined A+H+Y summary dashboard")


# ═══════════════════════════════════════════════════════════════════════════════
# PLOT 1: D01 — POLISHED EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

def plot_D01_polished(y_results, gain_syst, intra_diffs, lab_data,
                      gain_syst_raw=None):
    """Polished executive summary with 4 info boxes and sans-serif text."""
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

    # Lab differential
    lab_diffs = [v['diff'] for v in lab_data.values() if np.isfinite(v['diff'])]
    lab_diff_mean = np.mean(lab_diffs) if lab_diffs else 0
    lab_diff_sem = (np.std(lab_diffs, ddof=1) / np.sqrt(len(lab_diffs))
                    if len(lab_diffs) > 1 else 0.05)

    fig = plt.figure(figsize=(14, 11))
    plt.rcParams['font.family'] = 'sans-serif'

    # Title
    fig.text(0.5, 0.97, 'CEBAF Tunnel Magnet Radiation Exposure — Key Findings',
             fontsize=18, fontweight='bold', ha='center', va='top',
             fontfamily='sans-serif')
    fig.text(0.5, 0.935, 'Preliminary — ~6 months tunnel exposure (Jul 2025 – Jan 2026)',
             fontsize=12, ha='center', va='top', color='#666666',
             fontstyle='italic', fontfamily='sans-serif')

    # PRELIMINARY watermark
    fig.text(0.5, 0.50, 'PRELIMINARY', fontsize=60, ha='center', va='center',
             color='#EEEEEE', fontweight='bold', rotation=30, zorder=0,
             fontfamily='sans-serif')

    # 4 info boxes
    box_y = 0.68
    box_h = 0.17
    box_w = 0.21
    box_gap = 0.025

    syst_str = '\u00b1%.2f%%(syst)*' % gain_syst if gain_syst_raw else '\u00b1%.2f%%(syst)' % gain_syst
    boxes = [
        {
            'x': 0.03, 'title': 'NdFeB Degradation',
            'value': '%.2f%%' % nd_mean, 'sub': '\u00b1%.2f%%(stat) %s' % (nd_sem, syst_str),
            'fg': '#CC4444', 'bg': '#FFDDDD', 'edge': '#CC4444',
        },
        {
            'x': 0.03 + box_w + box_gap, 'title': 'SmCo Stable',
            'value': '%.2f%%' % sm_mean, 'sub': '\u00b1%.2f%%(stat) %s' % (sm_sem, syst_str),
            'fg': '#44AA44', 'bg': '#DDFFDD', 'edge': '#44AA44',
        },
        {
            'x': 0.03 + 2 * (box_w + box_gap), 'title': 'NdFeB \u2212 SmCo',
            'value': '%.3f%%' % diff_mean,
            'sub': '\u00b1%.3f%% (%.1f\u03c3)  N=%d plates' % (diff_sem, diff_sig, len(intra_diffs)),
            'fg': '#CC8800', 'bg': '#FFF8DD', 'edge': '#CC8800',
            'subtitle': '(gain-immune)',
        },
        {
            'x': 0.03 + 3 * (box_w + box_gap), 'title': 'Lab Controls',
            'value': '%.3f%%' % lab_diff_mean,
            'sub': '\u00b1%.3f%%  N=%d plates' % (lab_diff_sem, len(lab_diffs)),
            'fg': '#3366CC', 'bg': '#DDEEFF', 'edge': '#3366CC',
            'subtitle': '(NdFeB\u2212SmCo, no radiation)',
        },
    ]

    for b in boxes:
        ax = fig.add_axes([b['x'], box_y, box_w, box_h])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor=b['bg'],
                                    edgecolor=b['edge'], linewidth=3))
        ax.text(0.5, 0.82, b['title'], fontsize=12, fontweight='bold',
                ha='center', va='center', color=b['fg'], fontfamily='sans-serif')
        if 'subtitle' in b:
            ax.text(0.5, 0.68, b['subtitle'], fontsize=8, ha='center',
                    va='center', color=b['fg'], alpha=0.7, fontfamily='sans-serif')
        ax.text(0.5, 0.42, b['value'], fontsize=24, fontweight='bold',
                ha='center', va='center', color=b['fg'], fontfamily='sans-serif')
        ax.text(0.5, 0.12, b['sub'], fontsize=8, ha='center', va='center',
                color='#888888', fontfamily='sans-serif')
        ax.axis('off')

    # Simplified bar chart
    ax4 = fig.add_axes([0.08, 0.10, 0.38, 0.45])
    bars = ax4.bar([0, 1], [nd_mean, sm_mean],
                   yerr=[nd_sem, sm_sem],
                   color=['#CC4444', '#44AA44'], capsize=10,
                   edgecolor='black', linewidth=1, alpha=0.85, width=0.5,
                   error_kw=dict(linewidth=2.5, capthick=2.5))
    ax4.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax4.axhline(0, color='black', linewidth=1.5)
    ax4.set_xticks([0, 1])
    ax4.set_xticklabels(['NdFeB\n(N=%d)' % len(nd_vals),
                          'SmCo\n(N=%d)' % len(sm_vals)], fontsize=12,
                         fontfamily='sans-serif')
    ax4.set_ylabel('% Change from Baseline', fontsize=11, fontfamily='sans-serif')
    ax4.set_title('Y-Plate Helmholtz (temp-corrected)', fontsize=11,
                  fontweight='bold', fontfamily='sans-serif')
    ax4.grid(axis='y', alpha=0.3)
    ax4.text(0.5, gain_syst + 0.01, 'Gain syst. \u00b1%.2f%%' % gain_syst,
             fontsize=8, color='gray', ha='center', va='bottom',
             transform=ax4.get_xaxis_transform())

    # Key findings text — sans-serif with proper alignment
    ax5 = fig.add_axes([0.55, 0.10, 0.42, 0.45])
    ax5.set_xlim(0, 1)
    ax5.set_ylim(0, 1)

    findings = [
        ('KEY FINDINGS', True, 13),
        ('', False, 10),
        ('1.  NdFeB magnets show ~0.3% degradation after', False, 10),
        ('     ~6 months CEBAF tunnel exposure', False, 10),
        ('', False, 10),
        ('2.  SmCo magnets consistent with zero degradation', False, 10),
        ('     (within measurement precision)', False, 10),
        ('', False, 10),
        ('3.  NdFeB\u2212SmCo intra-plate differential of', False, 10),
        ('     %.3f%% is %.1f\u03c3 significant (gain-immune)' % (abs(diff_mean), diff_sig), False, 10),
        ('', False, 10),
        ('4.  Lab controls show ~0%% differential \u2014 confirms', False, 10),
        ('     tunnel signal is radiation-induced', False, 10),
        ('', False, 10),
        ('5.  Arc locations show ~2\u00d7 more NdFeB degradation', False, 10),
        ('     than linac locations', False, 10),
    ]

    for i, (text, bold, fs) in enumerate(findings):
        weight = 'bold' if bold else 'normal'
        ax5.text(0.02, 0.97 - i * 0.058, text, fontsize=fs,
                 fontweight=weight, va='top', fontfamily='sans-serif')
    ax5.axis('off')

    # Add footnote for cleaned gain systematic
    if gain_syst_raw is not None:
        fig.text(0.5, 0.005,
                 '*Gain syst. cleaned: \u00b1%.2f%% (excl. bad baselines + measurement errors); '
                 'uncleaned: \u00b1%.2f%%' % (gain_syst, gain_syst_raw),
                 ha='center', fontsize=8, fontstyle='italic', color='#666666',
                 fontfamily='sans-serif')

    fig.savefig(os.path.join(PLOT_DIR, 'v5_D01_executive_summary.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  D01: Executive summary (polished)")


# ═══════════════════════════════════════════════════════════════════════════════
# PLOT 2: B02 — POLISHED PASS NUMBER TREND
# ═══════════════════════════════════════════════════════════════════════════════

def plot_B02_polished(y_results, h_results, gain_syst):
    """Polished pass-number trend with seeded jitter, trend line, N labels."""
    np.random.seed(42)

    y_clean = [r for r in y_results if not r['is_outlier'] and r.get('line', 0) > 0]
    h_clean = [r for r in h_results if not r.get('is_outlier', False) and r.get('line', 0) > 0]

    # Enrich Y results with line numbers
    for r in y_clean:
        if 'line' not in r or r['line'] == 0:
            info = PLACEMENTS_WITH_LINE.get(r['plate'])
            if info:
                r['line'] = info['line']

    fig, (ax, ax_inset) = plt.subplots(1, 2, figsize=(16, 7),
                                         gridspec_kw={'width_ratios': [3, 1.2]})

    lines = [1, 2, 3, 4, 5]
    short_labels = ['1\n(low E)', '2', '3', '4', '5\n(high E)']

    # ─── Y-plate NdFeB ─────────────────
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

    # ─── Y-plate SmCo ──────────────────
    y_sm_means, y_sm_sems, y_sm_ns = [], [], []
    for line in lines:
        vals = [r['pct_change'] for r in y_clean
                if r['material'] in ['SmCo33H', 'SmCo35'] and r['line'] == line]
        if vals:
            y_sm_means.append(np.mean(vals))
            y_sm_sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                             if len(vals) > 1 else 0.05)
            y_sm_ns.append(len(vals))
        else:
            y_sm_means.append(np.nan)
            y_sm_sems.append(0)
            y_sm_ns.append(0)

    # ─── H-plate NdFeB ─────────────────
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

    # ─── H-plate SmCo ──────────────────
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

    # ─── Main panel ─────────────────────
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

    # Individual Y-plate scatter (seeded jitter)
    for r in y_clean:
        jitter = np.random.normal(0, 0.02)
        if r['material'] in ['N42EH', 'N52SH']:
            ax.plot(r['line'] - offset + jitter,
                    r['pct_change'], '.', color='#CC4444', alpha=0.2, markersize=4)
        else:
            ax.plot(r['line'] + offset + jitter,
                    r['pct_change'], '.', color='#44AA44', alpha=0.2, markersize=4)

    # N annotations on Y-plate NdFeB means
    for i, line in enumerate(lines):
        if y_nd_ns[i] > 0 and np.isfinite(y_nd_means[i]):
            ax.annotate('N=%d' % y_nd_ns[i],
                        xy=(line - offset, y_nd_means[i] - y_nd_sems[i] - 0.01),
                        fontsize=7, color='#CC4444', ha='center', va='top')
        if y_sm_ns[i] > 0 and np.isfinite(y_sm_means[i]):
            ax.annotate('N=%d' % y_sm_ns[i],
                        xy=(line + offset, y_sm_means[i] + y_sm_sems[i] + 0.01),
                        fontsize=7, color='#44AA44', ha='center', va='bottom')

    # Linear trend line for Y-plate NdFeB
    valid_idx = [i for i in range(len(lines)) if np.isfinite(y_nd_means[i])]
    if len(valid_idx) >= 2:
        x_fit = np.array([lines[i] for i in valid_idx])
        y_fit = np.array([y_nd_means[i] for i in valid_idx])
        coeffs = np.polyfit(x_fit, y_fit, 1)
        x_line = np.linspace(0.7, 5.3, 50)
        ax.plot(x_line, np.polyval(coeffs, x_line), ':', color='#CC4444',
                alpha=0.5, linewidth=1.5, zorder=3)
        ax.annotate('Slope: %+.3f%%/line' % coeffs[0],
                    xy=(0.98, 0.02), xycoords='axes fraction',
                    fontsize=9, ha='right', va='bottom', color='#CC4444',
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='#CC4444', alpha=0.8))

    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_xticks(lines)
    ax.set_xticklabels(short_labels, fontsize=10)
    ax.set_xlabel('Arc Line Position', fontsize=12)
    ax.set_ylabel('% Change from Baseline', fontsize=12)
    ax.set_title('Degradation vs Arc Line Position (Pass Number)\n'
                 'Line 1 = top (lowest beam energy) \u2192 Line 5 = bottom (highest beam energy)',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='lower left')
    ax.grid(alpha=0.3)

    # Annotation about inverted trend
    ax.annotate('Note: Inverted trend (more degradation at\n'
                'lower beam energy) — requires dose data to resolve',
                xy=(0.98, 0.98), xycoords='axes fraction',
                fontsize=8, ha='right', va='top', color='#666666',
                fontstyle='italic',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFFF0',
                          edgecolor='#CCCCCC', alpha=0.9))

    # ─── Inset: Top (1-2) vs Bottom (3-5) ───
    top_nd = [r['pct_change'] for r in y_clean
              if r['material'] in ['N42EH', 'N52SH'] and r['line'] in [1, 2]]
    bot_nd = [r['pct_change'] for r in y_clean
              if r['material'] in ['N42EH', 'N52SH'] and r['line'] in [3, 4, 5]]
    top_sm = [r['pct_change'] for r in y_clean
              if r['material'] in ['SmCo33H', 'SmCo35'] and r['line'] in [1, 2]]
    bot_sm = [r['pct_change'] for r in y_clean
              if r['material'] in ['SmCo33H', 'SmCo35'] and r['line'] in [3, 4, 5]]

    bar_data = []
    for label, vals, color in [('Top\nNdFeB', top_nd, '#CC4444'),
                                ('Bot\nNdFeB', bot_nd, '#EE8888'),
                                ('Top\nSmCo', top_sm, '#44AA44'),
                                ('Bot\nSmCo', bot_sm, '#88CC88')]:
        if vals:
            bar_data.append((label, np.mean(vals),
                             np.std(vals, ddof=1) / np.sqrt(len(vals))
                             if len(vals) > 1 else 0.05,
                             len(vals), color))

    if bar_data:
        bx = np.arange(len(bar_data))
        bars = ax_inset.bar(bx, [b[1] for b in bar_data],
                     yerr=[b[2] for b in bar_data],
                     color=[b[4] for b in bar_data],
                     capsize=4, edgecolor='black', linewidth=0.5,
                     alpha=0.85, width=0.6)
        ax_inset.set_xticks(bx)
        ax_inset.set_xticklabels(['%s\n(N=%d)' % (b[0], b[3]) for b in bar_data],
                                  fontsize=7)
        ax_inset.axhline(0, color='black', linewidth=1, linestyle='--')
        ax_inset.set_ylabel('% Change', fontsize=10)
        ax_inset.set_title('Top Lines (1-2) vs\nBottom Lines (3-5)',
                           fontsize=10, fontweight='bold')
        ax_inset.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v5_B02_pass_number_trend.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  B02: Pass number trend (polished)")


# ═══════════════════════════════════════════════════════════════════════════════
# PLOT 3: D04 — POLISHED DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def plot_D04_polished(y_results, h_results, gain_syst, intra_diffs, intra_details):
    """Polished 3x2 dashboard with N labels, reference lines, larger table."""
    y_clean = [r for r in y_results if not r['is_outlier']]
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]

    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    fig, axes = plt.subplots(3, 2, figsize=(20, 20))

    # ─── (a) Y-plate material bars + N labels ───
    ax = axes[0, 0]
    y_mats = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    means, sems, colors, ns = [], [], [], []
    for mat in y_mats:
        vals = [r['pct_change'] for r in y_clean if r['material'] == mat]
        if vals:
            means.append(np.mean(vals))
            sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                        if len(vals) > 1 else 0.05)
            colors.append(MAT_COLORS[mat])
            ns.append(len(vals))
        else:
            means.append(0); sems.append(0); colors.append('#888'); ns.append(0)

    bars_a = ax.bar(range(len(y_mats)), means, yerr=sems, color=colors,
                    capsize=5, edgecolor='black', linewidth=0.5, alpha=0.85,
                    width=0.6)
    # N labels on bars
    for i, (bar, n) in enumerate(zip(bars_a, ns)):
        y_pos = bar.get_height()
        offset_y = -0.01 if y_pos < 0 else 0.01
        va = 'top' if y_pos < 0 else 'bottom'
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos + offset_y,
                'N=%d' % n, ha='center', va=va, fontsize=8, fontweight='bold')

    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(range(len(y_mats)))
    ax.set_xticklabels(y_mats, fontsize=11)
    ax.set_ylabel('% Change', fontsize=11)
    ax.set_title('(a) Y-Plate by Material', fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # ─── (b) H-plate material + config bars ───
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
        offset_x = -width / 2 + i * width
        bars_b = ax.bar(x + offset_x, cfg_means, width, yerr=cfg_errs,
                        color=HMAT_COLORS[mat], capsize=4,
                        edgecolor='black', linewidth=0.5, alpha=0.85, label=mat)
        for j, cfg in enumerate(configs):
            if cfg == 'Beta':
                bars_b[j].set_hatch('///')
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(configs, fontsize=11)
    ax.set_ylabel('% Change', fontsize=11)
    ax.set_title('(b) H-Plate by Config', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # ─── (c) Gain-immune differential with ±1σ/±2σ lines ───
    ax = axes[1, 0]
    ax.bar(0, diff_mean, yerr=diff_sem, color='#8B0000', capsize=8,
           edgecolor='black', linewidth=1, alpha=0.85, width=0.4,
           error_kw=dict(linewidth=2.5, capthick=2.5))
    ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
    # ±1σ and ±2σ reference lines
    for ns_val, ls, alpha_v in [(1, '--', 0.3), (2, ':', 0.2)]:
        ax.axhline(ns_val * diff_sem, color='gray', linestyle=ls, alpha=alpha_v)
        ax.axhline(-ns_val * diff_sem, color='gray', linestyle=ls, alpha=alpha_v)
        ax.text(0.55, ns_val * diff_sem, '+%d\u03c3' % ns_val,
                fontsize=7, color='gray', va='bottom')
        ax.text(0.55, -ns_val * diff_sem, '-%d\u03c3' % ns_val,
                fontsize=7, color='gray', va='top')
    ax.set_xticks([0])
    ax.set_xticklabels(['NdFeB \u2212 SmCo\nN=%d plates' % len(intra_diffs)], fontsize=11)
    ax.set_ylabel('% Differential', fontsize=11)
    ax.set_title('(c) Gain-Immune: %+.3f%% (%.1f$\\sigma$)' % (diff_mean, diff_sig),
                 fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.set_xlim(-0.8, 0.8)

    # ─── (d) Pass-number trend with N annotations ───
    ax = axes[1, 1]
    y_arc = [r for r in y_clean if r.get('line', 0) > 0]
    lines_list = [1, 2, 3, 4, 5]
    offset_val = 0.1
    for mat_group, mat_filter, color, label in [
            ('NdFeB', ['N42EH', 'N52SH'], '#CC4444', 'NdFeB'),
            ('SmCo', ['SmCo33H', 'SmCo35'], '#44AA44', 'SmCo')]:
        lm, le, ln = [], [], []
        for line in lines_list:
            vals = [r['pct_change'] for r in y_arc
                    if r['material'] in mat_filter and r['line'] == line]
            lm.append(np.mean(vals) if vals else np.nan)
            le.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                      if len(vals) > 1 else (0.05 if vals else 0))
            ln.append(len(vals))
        off = -offset_val / 2 if mat_group == 'NdFeB' else offset_val / 2
        ax.errorbar(np.array(lines_list) + off, lm, yerr=le,
                    color=color, marker='o', markersize=7, linewidth=2,
                    capsize=4, label=label)
        # N annotations
        for i, line in enumerate(lines_list):
            if ln[i] > 0 and np.isfinite(lm[i]):
                ax.annotate('%d' % ln[i],
                            xy=(line + off, lm[i]),
                            xytext=(0, -12), textcoords='offset points',
                            fontsize=7, color=color, ha='center', fontweight='bold')

    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_xticks(lines_list)
    ax.set_xticklabels(['L%d' % l for l in lines_list], fontsize=11)
    ax.set_xlabel('Arc Line', fontsize=11)
    ax.set_ylabel('% Change', fontsize=11)
    ax.set_title('(d) Degradation vs Arc Line Position', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    # ─── (e) Time series with beam-OFF label positioned carefully ───
    ax = axes[2, 0]
    beam_off_dt = datetime(2025, 10, 21)
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
    ax.axvline(beam_off_dt, color='gray', linewidth=1, linestyle=':')
    # Place beam-OFF label at top of plot, slightly right of line
    ax.annotate('Beam OFF', xy=(beam_off_dt, 1.0), xycoords=('data', 'axes fraction'),
                xytext=(5, -5), textcoords='offset points',
                fontsize=8, color='gray', fontstyle='italic',
                ha='left', va='top')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.set_ylabel('% Change', fontsize=11)
    ax.set_title('(e) Y-Plate Helmholtz Time Series', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # ─── (f) Key numbers table — larger font, stronger highlight ───
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
    rows.append(['NdFeB\u2212SmCo (gain-immune)', '%+.3f%%' % diff_mean,
                 '%.3f%%' % diff_sem, '%d plates' % len(intra_diffs)])
    rows.append(['Gain systematic', '\u00b1%.3f%%' % gain_syst, '', ''])

    table = ax.table(cellText=rows,
                     colLabels=['Quantity', 'Value', 'Stat Unc', 'N'],
                     loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.0)

    # Header row styling
    for j in range(4):
        table[(0, j)].set_facecolor('#DDDDDD')
        table[(0, j)].set_text_props(fontweight='bold', fontsize=12)

    # Highlight differential row (second to last)
    diff_row_idx = len(rows) - 1  # gain syst is last
    for j in range(4):
        table[(diff_row_idx - 1 + 1, j)].set_facecolor('#FFF0CC')
        table[(diff_row_idx - 1 + 1, j)].set_text_props(fontweight='bold')
    # Also highlight gain systematic row
    for j in range(4):
        table[(len(rows), j)].set_facecolor('#F0F0F0')

    ax.set_title('(f) Key Numbers', fontsize=12, fontweight='bold', pad=20)

    fig.suptitle('Comprehensive Dashboard \u2014 Magnet Degradation Study\n'
                 'CEBAF Tunnel Jul 2025 \u2013 Jan 2026 (Preliminary)',
                 fontsize=15, fontweight='bold', y=1.01)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(PLOT_DIR, 'v5_D04_dashboard.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  D04: Comprehensive dashboard (polished)")


# ═══════════════════════════════════════════════════════════════════════════════
# PLOT 4: F01 — LAB CONTROL COMPARISON (NEW)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_F01_lab_control(intra_diffs, intra_details, lab_data):
    """2-panel figure: bars comparing tunnel/lab differentials + strip plot."""
    lab_diffs = [v['diff'] for v in lab_data.values() if np.isfinite(v['diff'])]
    tunnel_diffs = list(intra_diffs)

    tunnel_mean = np.mean(tunnel_diffs)
    tunnel_sem = np.std(tunnel_diffs) / np.sqrt(len(tunnel_diffs))
    tunnel_sig = abs(tunnel_mean / tunnel_sem) if tunnel_sem > 0 else 0

    lab_mean = np.mean(lab_diffs) if lab_diffs else 0
    lab_sem = (np.std(lab_diffs, ddof=1) / np.sqrt(len(lab_diffs))
               if len(lab_diffs) > 1 else 0.05)
    lab_sig = abs(lab_mean / lab_sem) if lab_sem > 0 else 0

    # Tunnel minus lab (worst case)
    wc_mean = tunnel_mean - lab_mean
    wc_sem = np.sqrt(tunnel_sem**2 + lab_sem**2)
    wc_sig = abs(wc_mean / wc_sem) if wc_sem > 0 else 0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8),
                                     gridspec_kw={'width_ratios': [1, 1.2]})

    # ─── Left panel: 3 grouped bars ───
    bar_x = [0, 1, 2]
    bar_vals = [tunnel_mean, lab_mean, wc_mean]
    bar_errs = [tunnel_sem, lab_sem, wc_sem]
    bar_colors = ['#8B0000', '#3366CC', '#CC8800']
    bar_labels = [
        'Tunnel\nNdFeB\u2212SmCo\n(N=%d plates)' % len(tunnel_diffs),
        'Lab Control\nNdFeB\u2212SmCo\n(N=%d plates)' % len(lab_diffs),
        'Tunnel \u2212 Lab\n(worst case)',
    ]
    bar_sigs = [tunnel_sig, lab_sig, wc_sig]

    bars = ax1.bar(bar_x, bar_vals, yerr=bar_errs, color=bar_colors,
                   capsize=8, edgecolor='black', linewidth=1, alpha=0.85,
                   width=0.6, error_kw=dict(linewidth=2, capthick=2))
    ax1.axhline(0, color='black', linewidth=1.5, linestyle='--')

    # Significance annotations
    for i, (bx, bv, sig) in enumerate(zip(bar_x, bar_vals, bar_sigs)):
        y_annot = bv - bar_errs[i] - 0.015 if bv < 0 else bv + bar_errs[i] + 0.015
        va = 'top' if bv < 0 else 'bottom'
        ax1.text(bx, y_annot, '%.1f\u03c3' % sig, ha='center', va=va,
                 fontsize=11, fontweight='bold', color=bar_colors[i])

    ax1.set_xticks(bar_x)
    ax1.set_xticklabels(bar_labels, fontsize=9)
    ax1.set_ylabel('NdFeB \u2212 SmCo Differential (%)', fontsize=11)
    ax1.set_title('Gain-Immune Differential:\nTunnel vs Lab Controls',
                  fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # Note about lab temp correction
    ax1.annotate('Lab samples temp-corrected\n'
                 '(estimated temps, see lab_ha_analysis.py)',
                 xy=(0.02, 0.02), xycoords='axes fraction',
                 fontsize=8, color='#666666', fontstyle='italic',
                 va='bottom', ha='left',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFFF0',
                           edgecolor='#CCCCCC', alpha=0.9))

    # ─── Right panel: strip/dot plot ───
    # Tunnel plates
    tunnel_x = np.zeros(len(tunnel_diffs)) + 0.0
    jitter_t = np.random.RandomState(42).normal(0, 0.06, len(tunnel_diffs))
    ax2.scatter(tunnel_x + jitter_t, tunnel_diffs, color='#8B0000',
                alpha=0.5, s=25, edgecolor='black', linewidth=0.3,
                zorder=3, label='Tunnel plates (N=%d)' % len(tunnel_diffs))

    # Lab plates
    lab_x = np.ones(len(lab_diffs)) * 1.0
    jitter_l = np.random.RandomState(43).normal(0, 0.06, len(lab_diffs))
    ax2.scatter(lab_x + jitter_l, lab_diffs, color='#3366CC',
                alpha=0.6, s=40, edgecolor='black', linewidth=0.3,
                zorder=3, label='Lab plates (N=%d)' % len(lab_diffs))

    # Mean lines
    ax2.hlines(tunnel_mean, -0.3, 0.3, colors='#8B0000', linewidth=2.5,
               zorder=4)
    ax2.hlines(lab_mean, 0.7, 1.3, colors='#3366CC', linewidth=2.5,
               zorder=4)

    # Mean annotations
    ax2.annotate('%.3f%%' % tunnel_mean, xy=(0.35, tunnel_mean),
                 fontsize=10, fontweight='bold', color='#8B0000',
                 va='center', ha='left')
    ax2.annotate('%.3f%%' % lab_mean, xy=(1.35, lab_mean),
                 fontsize=10, fontweight='bold', color='#3366CC',
                 va='center', ha='left')

    ax2.axhline(0, color='black', linewidth=1, linestyle='--')
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(['Tunnel\n(radiation)', 'Lab\n(no radiation)'],
                         fontsize=11)
    ax2.set_ylabel('Per-Plate NdFeB \u2212 SmCo Differential (%)', fontsize=11)
    ax2.set_title('Individual Plate Differentials:\nTunnel vs Lab Controls',
                  fontsize=13, fontweight='bold')
    ax2.set_xlim(-0.5, 1.8)
    ax2.legend(fontsize=9, loc='lower right')
    ax2.grid(axis='y', alpha=0.3)

    fig.suptitle('Lab Controls Confirm Radiation-Induced NdFeB Degradation',
                 fontsize=15, fontweight='bold', y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(PLOT_DIR, 'v5_F01_lab_control_comparison.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  F01: Lab control comparison (new)")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("Manager Summary v5 Polish + A-Sample Analysis")
    print("=" * 70)
    print()

    # ─── Load Y-plate data (from v3) ─────────────────────────────────
    print("Loading Y-plate Helmholtz data (v3 loader)...")
    y_results, helm_raw, temp_final, y_materials = load_all()
    y_clean = [r for r in y_results if not r['is_outlier']]
    print("  %d Y-plate Helmholtz samples (%d outliers excluded)" %
          (len(y_clean), len(y_results) - len(y_clean)))

    # Enrich with line numbers
    for r in y_results:
        info = PLACEMENTS_WITH_LINE.get(r['plate'])
        if info:
            if 'line' not in r or r.get('line', 0) == 0:
                r['line'] = info['line']
            if 'h_plate' not in r:
                r['h_plate'] = info['h_plate']

    # ─── Load H-plate data (from v2) ─────────────────────────────────
    print("Loading H-plate data (v2 loader)...")
    y_mats_xl, pair_arrangements = load_materials()
    temp_lookup = build_temperature_lookup()
    h_results, h_excluded = compute_h_plate_degradation(pair_arrangements, temp_lookup)
    h_clean = [r for r in h_results if not r.get('is_outlier', False)]
    print("  %d H-plate pairs (%d clean)" % (len(h_results), len(h_clean)))

    # ─── Gain systematic ─────────────────────────────────────────────
    gain_result = get_gain_syst(helm_raw)
    gain_syst = gain_result[0]
    gain_syst_raw = getattr(gain_result, 'gain_syst_raw', None)
    print("\nGain systematic (cleaned): \u00b1%.4f%%" % gain_syst)
    if gain_syst_raw is not None:
        print("Gain systematic (uncleaned): \u00b1%.4f%%" % gain_syst_raw)

    # ─── Intra-plate differential ─────────────────────────────────────
    intra_diffs, intra_details = compute_intra_plate_diffs(y_clean)
    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    # ─── Load lab Y-plate data ────────────────────────────────────────
    print("\nLoading lab control Y-plate data...")
    lab_data = load_lab_y_plates()
    lab_diffs = [v['diff'] for v in lab_data.values() if np.isfinite(v['diff'])]
    lab_diff_mean = np.mean(lab_diffs) if lab_diffs else 0
    lab_diff_sem = (np.std(lab_diffs, ddof=1) / np.sqrt(len(lab_diffs))
                    if len(lab_diffs) > 1 else 0.05)
    lab_diff_sig = abs(lab_diff_mean / lab_diff_sem) if lab_diff_sem > 0 else 0
    print("  %d lab Y-plates loaded" % len(lab_data))

    # ─── Load A-sample data ───────────────────────────────────────────
    print("\nLoading A-sample (pair) data...")
    a_helm_results = load_a_sample_helmholtz(temp_lookup)
    a_clean = [r for r in a_helm_results if not r['is_outlier']]
    a_tc = [r for r in a_clean if r['temp_corrected']]
    print("  %d A-sample Helmholtz (%d clean, %d temp-corrected)" %
          (len(a_helm_results), len(a_clean),  len(a_tc)))

    print("Loading A-sample Teslameter data...")
    a_tesla_results = load_a_sample_teslameter()
    print("  %d A-sample Teslameter (field) results" % len(a_tesla_results))

    # ═══════════════════════════════════════════════════════════════════
    # VERIFICATION — Print all key numbers BEFORE plotting
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("VERIFICATION — Key Numbers")
    print("=" * 70)

    print("\n--- Y-Plate Helmholtz (Tunnel) ---")
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        vals = [r['pct_change'] for r in y_clean if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals))
            print("  %s: %+.3f%% \u00b1 %.3f%% (%.1f\u03c3, N=%d)" %
                  (mat, m, s, abs(m / s) if s > 0 else 0, len(vals)))

    print("\n--- Gain-Immune Intra-Plate Differential ---")
    print("  NdFeB \u2212 SmCo: %+.3f%% \u00b1 %.3f%% (%.1f\u03c3, N=%d plates)" %
          (diff_mean, diff_sem, diff_sig, len(intra_diffs)))

    print("\n--- Lab Control Y-Plates ---")
    for pnum in sorted(lab_data):
        d = lab_data[pnum]
        print("  Y-%d: NdFeB=%+.3f%%, SmCo=%+.3f%%, diff=%+.3f%%" %
              (pnum, d['nd_mean'], d['sm_mean'], d['diff']))
    print("  Lab NdFeB\u2212SmCo differential: %+.3f%% \u00b1 %.3f%% (%.1f\u03c3, N=%d)" %
          (lab_diff_mean, lab_diff_sem, lab_diff_sig, len(lab_diffs)))

    print("\n--- Tunnel \u2212 Lab (worst case) ---")
    wc_mean = diff_mean - lab_diff_mean
    wc_sem = np.sqrt(diff_sem**2 + lab_diff_sem**2)
    wc_sig = abs(wc_mean / wc_sem) if wc_sem > 0 else 0
    print("  Tunnel\u2212Lab: %+.3f%% \u00b1 %.3f%% (%.1f\u03c3)" %
          (wc_mean, wc_sem, wc_sig))

    print("\n--- H-Plate Helmholtz ---")
    for mat in ['NdFeB', 'SmCo']:
        vals = [r['pct_change'] for r in h_clean if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.1
            print("  %s: %+.3f%% \u00b1 %.3f%% (%.1f\u03c3, N=%d)" %
                  (mat, m, s, abs(m / s) if s > 0 else 0, len(vals)))

    print("\n--- A-Sample Helmholtz ---")
    for mat in ['NdFeB', 'SmCo']:
        vals = [r['pct_change'] for r in a_clean if r['material'] == mat]
        vals_tc = [r['pct_change'] for r in a_clean
                   if r['material'] == mat and r['temp_corrected']]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.1
            print("  %s: %+.3f%% \u00b1 %.3f%% (%.1f\u03c3, N=%d, %d temp-corr)" %
                  (mat, m, s, abs(m / s) if s > 0 else 0, len(vals), len(vals_tc)))

    print("\n--- A-Sample Teslameter (top face) ---")
    for mat in ['NdFeB', 'SmCo']:
        vals = [r['top_pct'] for r in a_tesla_results
                if r['material'] == mat and np.isfinite(r.get('top_pct', np.nan))]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.5
            print("  %s top: %+.3f%% \u00b1 %.3f%% (std=%.3f%%, N=%d)" %
                  (mat, m, s, np.std(vals, ddof=1), len(vals)))

    print("\n--- A-Sample Teslameter (all faces) ---")
    for face in ['top', 'front', 'side']:
        for mat in ['NdFeB', 'SmCo']:
            vals = [r['%s_pct' % face] for r in a_tesla_results
                    if r['material'] == mat and np.isfinite(r.get('%s_pct' % face, np.nan))]
            if vals:
                m = np.mean(vals)
                s = np.std(vals, ddof=1)
                print("  %s %s: %+.3f%% (std=%.2f%%, N=%d)" %
                      (mat, face, m, s, len(vals)))

    print("\n--- Pass Number (Y-plate NdFeB, arcs only) ---")
    for line in [1, 2, 3, 4, 5]:
        vals = [r['pct_change'] for r in y_clean
                if r['material'] in ['N42EH', 'N52SH'] and r.get('line', 0) == line]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.05
            print("  Line %d: %+.3f%% \u00b1 %.3f%% (N=%d)" %
                  (line, m, s, len(vals)))

    # ═══════════════════════════════════════════════════════════════════
    # GENERATE POLISHED PLOTS
    # ═══════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("Generating plots...")
    print("=" * 70)

    print("\nPolished plots (D01, B02, D04):")
    plot_D01_polished(y_results, gain_syst, intra_diffs, lab_data,
                      gain_syst_raw=gain_syst_raw)
    plot_B02_polished(y_results, h_results, gain_syst)
    plot_D04_polished(y_results, h_results, gain_syst, intra_diffs, intra_details)

    print("\nNew plots (F01, G01-G04):")
    plot_F01_lab_control(intra_diffs, intra_details, lab_data)
    plot_G01_a_helmholtz(a_helm_results, gain_syst)
    plot_G02_a_teslameter(a_tesla_results)
    plot_G03_a_vs_h(a_helm_results, h_results)
    plot_G04_a_summary(a_helm_results, a_tesla_results, h_results,
                        y_results, gain_syst, intra_diffs)

    print("\n" + "=" * 70)
    print("8 plots saved to: %s/" % PLOT_DIR)
    print("  v5_D01_executive_summary.png  (polished)")
    print("  v5_B02_pass_number_trend.png  (polished)")
    print("  v5_D04_dashboard.png          (polished)")
    print("  v5_F01_lab_control_comparison.png (lab controls)")
    print("  v5_G01_a_sample_helmholtz.png (A-sample Helmholtz)")
    print("  v5_G02_a_sample_teslameter.png (A-sample Teslameter)")
    print("  v5_G03_a_vs_h_helmholtz.png   (A vs H correlation)")
    print("  v5_G04_a_sample_summary.png   (combined A+H+Y)")
    print("=" * 70)


if __name__ == '__main__':
    main()
