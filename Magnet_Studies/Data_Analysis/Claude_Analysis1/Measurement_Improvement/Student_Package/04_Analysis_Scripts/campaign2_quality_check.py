#!/usr/bin/env python3
"""
Campaign 2 Initial Data Quality Check
First measurement day: 2026-04-20

Sections:
  1. Data Inventory -- file counts, anomalies, data gaps
  2. Y-14 Calibration Plate -- repeatability at 3 time points
  3. Temperature Survey -- all teslameter temps vs time of day
  4. Delta Slug Assessment -- field magnitudes, utility recommendation
  5. Fleet Overview -- C2 vs C1 comparison for tunnel Y-plates

Output: 2026_Data_Run/Analysis/
  C2-1_calibration_repeatability.png
  C2-2_temperature_evolution.png
  C2-3_campaign_comparison.png
  C2-4_material_distributions.png
  campaign2_summary.txt
  campaign2_vs_campaign1.csv

Usage: python3 2026_Data_Run/campaign2_quality_check.py [--date 2026-04-20]
"""

import os
import re
import sys
import argparse
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
import openpyxl

# ---- Paths & Constants ----------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.join(BASE, 'Analysis')
PROJECT_DIR = os.path.dirname(BASE)

HELM_DIR = os.path.join(BASE, '20260420_Helmholtz')
TESLA_DIR = os.path.join(BASE, '2026-04-20_Teslameter')
SPREADSHEET = os.path.join(PROJECT_DIR, 'Materials_Arrangements_Spreadsheet.xlsx')
C1_CSV = os.path.join(PROJECT_DIR, 'Data_Package', '02_Magnetic_Measurements',
                       'y_plate_degradation.csv')
INVENTORY_CSV = os.path.join(PROJECT_DIR, 'Data_Package', '01_Sample_Configuration',
                              'sample_inventory.csv')

T_REF = 20.0
SENTINEL = 1337
MIN_BASELINE = 0.1

ALPHA = {
    'N42EH': -0.0010, 'N52SH': -0.0011,
    'SmCo33H': -0.0004, 'SmCo35': -0.0004,
}
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
REGION_COLORS = {
    'NE Arc': '#CC4444', 'NW Arc': '#E06666', 'SE Arc': '#AA3333',
    'SW Arc': '#DD5555',
    'North Linac': '#4444CC', 'South Linac': '#6666DD',
    'Labyrinth': '#888888',
}
LAB_PLATES = {8, 14, 27, 28, 29, 31, 33, 35, 37}
CALIBRATION_PLATE = 14

# Known data-entry error: Y-17-2 file contains a reading (1.0745 mWC) that
# belongs to Y-17-3.  Y-17-2's true reading is the first entry (1.2967 mWC).
# We flag this and optionally rescue the misplaced value for Y-17-3.
KNOWN_MISPLACED = {
    'Y-17-2': {'bad_value_approx': 1.075, 'true_owner': 'Y-17-3'},
}


# ---- Parsers (from manager_summary_v3.py) ---------------------------------

def parse_helmholtz_file(filepath):
    """Parse Helmholtz .dat file -> list of (datetime, value, unit)."""
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
            dt = datetime.strptime('%s %s' % (dm.group(1), dm.group(2)),
                                   '%Y-%m-%d %H:%M:%S')
            rows.append((dt, val, unit))
    return rows


def parse_teslameter_file(filepath):
    """Parse Teslameter .dat file -> list of (datetime, [Bx,By,Bz], temp)."""
    rows = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = re.match(r'(\d{4}-\d{2}-\d{2})\t(\d{2}:\d{2}:\d{2})\t(.*)', line)
            if m:
                dt = datetime.strptime('%s %s' % (m.group(1), m.group(2)),
                                       '%Y-%m-%d %H:%M:%S')
                rest = m.group(3)
            else:
                m = re.match(r'(\d{4}-\d{2}-\d{2})-(\d{2}:\d{2}:\d{2})\t(.*)', line)
                if m:
                    dt = datetime.strptime('%s %s' % (m.group(1), m.group(2)),
                                           '%Y-%m-%d %H:%M:%S')
                    rest = m.group(3)
                else:
                    continue
            nums = re.findall(r'(-?\d+\.\d+)', rest)
            if len(nums) >= 4:
                rows.append((dt, [float(x) for x in nums[:3]], float(nums[3])))
    return rows


# ---- Data Loaders ---------------------------------------------------------

def load_y_materials():
    """Load material assignments for all Y-plates from spreadsheet."""
    wb = openpyxl.load_workbook(SPREADSHEET, data_only=True)
    materials = {}
    for sheet_name in ['Tunnel - Y Materials', 'Lab - Y Materials']:
        ws = wb[sheet_name]
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not row[0]:
                continue
            pm = re.match(r'[yY]-?(\d+)', str(row[0]).strip())
            if not pm:
                continue
            pn = pm.group(1)
            for i, v in enumerate(row[1:5], 1):
                if v:
                    mat = str(v).strip()
                    # Normalize variant spellings
                    if mat == 'SmCo33':
                        mat = 'SmCo33H'
                    materials['Y-%s-%d' % (pn, i)] = mat
    return materials


def load_campaign1_reference():
    """Load Campaign 1 per-sample baseline and endpoint values (temp-corrected)."""
    c1 = {}
    with open(C1_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row['sample_id']
            c1[sid] = {
                'plate': int(row['plate']),
                'slot': int(row['slot']),
                'material': row['material'],
                'region': row['region'],
                'environment': row['environment'],
                'baseline_mWC': float(row['baseline_mean_mWC']),
                'latest_mWC': float(row['latest_mWC']),
                'pct_change': float(row['pct_change']),
                'is_outlier': row['is_outlier'] == 'True',
            }
    return c1


def find_delta_slugs():
    """Find Delta-config pair-2 sample IDs (slugs) from inventory."""
    slugs = set()
    with open(INVENTORY_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('config') == 'Delta' and row['sample_id'].startswith('A'):
                if row['sample_id'].endswith('-2'):
                    slugs.add(row['sample_id'])
    return slugs


# ---- Utility Functions ----------------------------------------------------

def temp_correct(raw_mwc, temp, material):
    """Correct Helmholtz mWC reading to T_REF using material temp coefficient."""
    alpha = ALPHA.get(material, -0.0004)
    return raw_mwc / (1.0 + alpha * (temp - T_REF))


def get_y_helm_readings(target_date):
    """Get all Y-plate Helmholtz mWC readings for target date.

    Returns dict: sample_id -> list of (datetime, value) for target date.
    Also returns list of anomaly strings.
    """
    readings = defaultdict(list)
    anomalies = []

    for fname in sorted(os.listdir(HELM_DIR)):
        hm = re.match(r'(Y-(\d+)-(\d+))_helmholtz\.dat$', fname)
        if not hm:
            continue
        sid = hm.group(1)
        rows = parse_helmholtz_file(os.path.join(HELM_DIR, fname))
        all_date_rows = [(dt, v) for dt, v, u in rows
                         if dt.strftime('%Y-%m-%d') == target_date
                         and u == 'mWC'
                         and abs(v - SENTINEL) > 1]
        # Flag near-zero readings (failed measurements)
        target_rows = []
        for dt, v in all_date_rows:
            if abs(v) < MIN_BASELINE:
                anomalies.append(
                    '%s: near-zero reading %.4f mWC on %s (FAILED MEASUREMENT)'
                    % (sid, v, target_date))
            else:
                target_rows.append((dt, v))

        # Handle known misplaced readings
        if sid in KNOWN_MISPLACED:
            bad_approx = KNOWN_MISPLACED[sid]['bad_value_approx']
            true_owner = KNOWN_MISPLACED[sid]['true_owner']
            good = []
            rescued = []
            for dt, v in target_rows:
                if abs(v - bad_approx) < 0.01:
                    rescued.append((dt, v))
                    anomalies.append(
                        '%s: value %.4f mWC is misplaced (belongs to %s); excluded'
                        % (sid, v, true_owner))
                else:
                    good.append((dt, v))
            # Rescue value for the true owner
            for dt, v in rescued:
                readings[true_owner].append((dt, v))
            target_rows = good

        if len(target_rows) > 1:
            anomalies.append('%s: %d readings on %s (using first valid)'
                             % (sid, len(target_rows), target_date))

        for dt, v in target_rows:
            readings[sid].append((dt, v))

    return readings, anomalies


def get_y_tesla_temps(target_date):
    """Get teslameter temperatures for all Y-plates on target date.

    Returns dict: sample_id -> list of (datetime, temp).
    """
    temps = defaultdict(list)
    for fname in sorted(os.listdir(TESLA_DIR)):
        tm = re.match(r'(Y-\d+-\d+)_(front|side|top)\.dat$', fname)
        if not tm:
            continue
        sid = tm.group(1)
        rows = parse_teslameter_file(os.path.join(TESLA_DIR, fname))
        for dt, fields, temp in rows:
            if dt.strftime('%Y-%m-%d') == target_date and abs(temp - SENTINEL) > 1:
                temps[sid].append((dt, temp))
    return temps


# ---- Section 1: Data Inventory -------------------------------------------

def section_inventory(target_date, out):
    """Scan data directories, classify files, report anomalies and gaps."""
    out.append('=' * 70)
    out.append('SECTION 1: DATA INVENTORY')
    out.append('=' * 70)
    out.append('')

    # Regex for standard file names
    helm_re = re.compile(
        r'^(Y|Hn|Hs|An|As)-(\d+)-(\d+)(?:-(\d+))?_helmholtz\.dat$')
    tesla_re = re.compile(
        r'^(Y|Hn|Hs|An|As)-(\d+)-(\d+)(?:-(\d+))?_(front|side|top)\.dat$')

    # ---- Helmholtz ----
    helm_files = sorted(os.listdir(HELM_DIR))
    helm_counts = defaultdict(int)
    helm_plates = defaultdict(set)
    helm_anomalous = []

    for fname in helm_files:
        if fname.endswith('.zip'):
            continue
        m = helm_re.match(fname)
        if m:
            ftype = m.group(1)
            helm_counts[ftype] += 1
            helm_plates[ftype].add(int(m.group(2)))
        else:
            helm_anomalous.append(fname)

    out.append('Helmholtz directory: %s' % os.path.basename(HELM_DIR))
    out.append('  Total data files: %d' % sum(helm_counts.values()))
    for ftype in ['Y', 'Hn', 'Hs', 'An', 'As']:
        if ftype in helm_counts:
            out.append('  %-3s: %3d files  (%d plates)' %
                       (ftype, helm_counts[ftype], len(helm_plates[ftype])))
    if helm_anomalous:
        out.append('  Anomalous: %s' % ', '.join(helm_anomalous))

    # ---- Teslameter ----
    tesla_files = sorted(os.listdir(TESLA_DIR))
    tesla_counts = defaultdict(int)
    tesla_plates = defaultdict(set)
    tesla_anomalous = []

    for fname in tesla_files:
        if fname.endswith('.zip') or os.path.isdir(os.path.join(TESLA_DIR, fname)):
            continue
        m = tesla_re.match(fname)
        if m:
            ftype = m.group(1)
            tesla_counts[ftype] += 1
            tesla_plates[ftype].add(int(m.group(2)))
        else:
            tesla_anomalous.append(fname)

    out.append('')
    out.append('Teslameter directory: %s' % os.path.basename(TESLA_DIR))
    out.append('  Total data files: %d' % sum(tesla_counts.values()))
    for ftype in ['Y', 'Hn', 'Hs', 'An', 'As']:
        if ftype in tesla_counts:
            out.append('  %-3s: %3d files  (%d plates)' %
                       (ftype, tesla_counts[ftype], len(tesla_plates[ftype])))
    if tesla_anomalous:
        out.append('  Anomalous: %s' % ', '.join(tesla_anomalous))

    # ---- Y-plate date coverage ----
    out.append('')
    out.append('Y-plate Helmholtz coverage for %s:' % target_date)

    y_with_data = set()
    y_without_data = []

    for fname in sorted(os.listdir(HELM_DIR)):
        hm = re.match(r'(Y-(\d+)-(\d+))_helmholtz\.dat$', fname)
        if not hm:
            continue
        sid = hm.group(1)
        plate = int(hm.group(2))
        rows = parse_helmholtz_file(os.path.join(HELM_DIR, fname))
        has_date = any(r[0].strftime('%Y-%m-%d') == target_date
                       and r[2] == 'mWC' for r in rows)
        if has_date:
            y_with_data.add(sid)
        else:
            y_without_data.append(sid)

    # Partition by tunnel vs lab
    def plate_num(sid):
        return int(re.search(r'Y-(\d+)', sid).group(1))

    tunnel_with = sorted([s for s in y_with_data if plate_num(s) in PLACEMENTS])
    tunnel_without = sorted([s for s in y_without_data if plate_num(s) in PLACEMENTS])
    lab_with = sorted([s for s in y_with_data if plate_num(s) in LAB_PLATES])
    lab_without = sorted([s for s in y_without_data if plate_num(s) in LAB_PLATES])

    tunnel_plates_with = sorted(set(plate_num(s) for s in tunnel_with))
    tunnel_plates_all = sorted(PLACEMENTS.keys())
    tunnel_plates_missing = sorted(set(tunnel_plates_all) - set(tunnel_plates_with))

    out.append('  Tunnel plates with data: %d / %d  %s' %
               (len(tunnel_plates_with), len(tunnel_plates_all),
                sorted(tunnel_plates_with)))
    if tunnel_plates_missing:
        out.append('  Tunnel plates MISSING ALL data: Y-%s' %
                   ', Y-'.join(str(p) for p in tunnel_plates_missing))
    if tunnel_without:
        out.append('  Individual tunnel slots missing %s data: %s' %
                   (target_date, ', '.join(tunnel_without)))

    lab_plates_with = sorted(set(plate_num(s) for s in lab_with))
    lab_plates_without = sorted(set(plate_num(s) for s in lab_without) -
                                set(lab_plates_with))
    out.append('  Lab plates with data: Y-%s' %
               ', Y-'.join(str(p) for p in lab_plates_with) if lab_plates_with
               else '  Lab plates with data: none')
    if lab_plates_without:
        out.append('  Lab plates without %s data: Y-%s' %
                   (target_date, ', Y-'.join(str(p) for p in lab_plates_without)))

    # Note Y-2 absence
    all_y_plates = set()
    for fname in os.listdir(HELM_DIR):
        m = re.match(r'Y-(\d+)-\d+_helmholtz\.dat$', fname)
        if m:
            all_y_plates.add(int(m.group(1)))
    expected_tunnel = set(PLACEMENTS.keys())
    no_files = sorted(expected_tunnel - all_y_plates)
    if no_files:
        out.append('  NOTE: no Helmholtz files at all for Y-%s' %
                   ', Y-'.join(str(p) for p in no_files))

    out.append('')
    return y_with_data


# ---- Section 2: Y-14 Calibration -----------------------------------------

def section_calibration(target_date, materials, out):
    """Analyze Y-14 calibration plate: 3 time-point repeatability."""
    out.append('=' * 70)
    out.append('SECTION 2: Y-14 CALIBRATION PLATE REPEATABILITY')
    out.append('=' * 70)
    out.append('')

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('C2-1: Y-14 Calibration Plate Repeatability (%s)\n'
                 'Raw (dashed) vs Temperature-Corrected (solid)' % target_date,
                 fontsize=13, fontweight='bold')

    all_corr_repeats = []

    for slot in range(1, 5):
        sid = 'Y-14-%d' % slot
        mat = materials.get(sid, 'Unknown')
        alpha = ALPHA.get(mat, -0.0004)
        ax = axes[(slot - 1) // 2][(slot - 1) % 2]

        # Parse Helmholtz
        helm_path = os.path.join(HELM_DIR, '%s_helmholtz.dat' % sid)
        if not os.path.exists(helm_path):
            out.append('  %s: Helmholtz file not found' % sid)
            ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                    transform=ax.transAxes)
            continue

        helm_rows = parse_helmholtz_file(helm_path)
        helm_target = [(dt, v) for dt, v, u in helm_rows
                       if dt.strftime('%Y-%m-%d') == target_date and u == 'mWC']

        # Parse Teslameter (all 3 orientations)
        tesla_readings = []  # (datetime, temp, orientation)
        for orient in ['front', 'side', 'top']:
            tpath = os.path.join(TESLA_DIR, '%s_%s.dat' % (sid, orient))
            if not os.path.exists(tpath):
                continue
            trows = parse_teslameter_file(tpath)
            for dt, fields, temp in trows:
                if (dt.strftime('%Y-%m-%d') == target_date
                        and abs(temp - SENTINEL) > 1):
                    tesla_readings.append((dt, temp, orient))

        # Match each Helmholtz reading to nearest teslameter temps
        matched = []
        for h_dt, h_val in helm_target:
            nearby = [t for t in tesla_readings
                      if abs((t[0] - h_dt).total_seconds()) < 600]
            if nearby:
                avg_temp = np.mean([t[1] for t in nearby])
            elif tesla_readings:
                closest = min(tesla_readings,
                              key=lambda t: abs((t[0] - h_dt).total_seconds()))
                avg_temp = closest[1]
            else:
                avg_temp = 23.0
            h_corr = h_val / (1.0 + alpha * (avg_temp - T_REF))
            matched.append({
                'time': h_dt, 'raw': h_val,
                'temp': avg_temp, 'corrected': h_corr,
            })

        if not matched:
            out.append('  %s (%s): no %s data' % (sid, mat, target_date))
            ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                    transform=ax.transAxes)
            continue

        # Statistics
        raw_vals = np.array([m['raw'] for m in matched])
        corr_vals = np.array([m['corrected'] for m in matched])
        temps = np.array([m['temp'] for m in matched])

        raw_range = np.ptp(raw_vals)
        raw_mean = np.mean(raw_vals)
        raw_pct = raw_range / raw_mean * 100 if raw_mean else 0

        corr_range = np.ptp(corr_vals)
        corr_mean = np.mean(corr_vals)
        corr_pct = corr_range / corr_mean * 100 if corr_mean else 0
        all_corr_repeats.append(corr_pct)

        out.append('  %s (%s, alpha=%.4f %%/C):' % (sid, mat, alpha * 100))
        for m in matched:
            out.append('    %s  Raw=%.4f mWC  T=%.1f C  Corr@20C=%.4f mWC' %
                       (m['time'].strftime('%H:%M'), m['raw'],
                        m['temp'], m['corrected']))
        out.append('    Raw repeatability:  %.4f mWC  (%.3f%%)' %
                   (raw_range, raw_pct))
        out.append('    Corrected repeatability: %.4f mWC  (%.3f%%)' %
                   (corr_range, corr_pct))
        out.append('    Temperature range: %.1f - %.1f C  (swing = %.1f C)' %
                   (np.min(temps), np.max(temps), np.ptp(temps)))

        # End-of-day assessment
        if len(matched) >= 3:
            dev_morning = abs(corr_vals[0] - corr_mean) / corr_mean * 100
            dev_evening = abs(corr_vals[-1] - corr_mean) / corr_mean * 100
            out.append('    Morning deviation from mean: %.3f%%' % dev_morning)
            out.append('    Evening deviation from mean: %.3f%%' % dev_evening)
            if dev_evening > 2 * dev_morning and dev_evening > 0.05:
                out.append('    ** End-of-day reading shows larger deviation **')
        out.append('')

        # ---- Plot ----
        x = range(len(matched))
        labels = [m['time'].strftime('%H:%M') for m in matched]

        ax.plot(x, raw_vals, 'o--', color='#888888', markersize=8,
                label='Raw (%.3f%%)' % raw_pct)
        ax.plot(x, corr_vals, 's-', color=MAT_COLORS.get(mat, 'black'),
                markersize=9, linewidth=2,
                label='Corr@20C (%.3f%%)' % corr_pct)

        # Annotate temperatures
        for i, m in enumerate(matched):
            ax.annotate('%.1f\u00b0C' % m['temp'], (i, m['raw']),
                        textcoords='offset points', xytext=(0, 12),
                        fontsize=8, ha='center', color='#888888')

        ax.set_xticks(list(x))
        ax.set_xticklabels(labels)
        ax.set_ylabel('mWC')
        ax.set_title('Slot %d: %s' % (slot, MAT_LABELS.get(mat, mat)),
                     fontweight='bold')
        ax.legend(fontsize=9, loc='best')
        ax.grid(True, alpha=0.3)

        # Shade the y range to show spread
        y_pad = max(raw_range, corr_range) * 0.5
        ax.set_ylim(min(min(raw_vals), min(corr_vals)) - y_pad,
                     max(max(raw_vals), max(corr_vals)) + y_pad)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plot_path = os.path.join(ANALYSIS_DIR, 'C2-1_calibration_repeatability.png')
    fig.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    out.append('  Plot saved: %s' % os.path.basename(plot_path))

    if all_corr_repeats:
        out.append('  Overall corrected repeatability: mean %.3f%%, max %.3f%%' %
                   (np.mean(all_corr_repeats), np.max(all_corr_repeats)))
    out.append('')


# ---- Section 3: Temperature Survey ----------------------------------------

def section_temperature(target_date, out):
    """Extract all teslameter temps and plot vs time of day."""
    out.append('=' * 70)
    out.append('SECTION 3: TEMPERATURE SURVEY')
    out.append('=' * 70)
    out.append('')

    all_temps = []  # (datetime, temp, sample_type_letter)

    for fname in sorted(os.listdir(TESLA_DIR)):
        if not fname.endswith('.dat') or fname == 'config.dat':
            continue
        fpath = os.path.join(TESLA_DIR, fname)
        if os.path.isdir(fpath):
            continue

        # Determine sample type
        if fname.startswith('Y-'):
            stype = 'Y'
        elif fname.startswith('H'):
            stype = 'H'
        elif fname.startswith('A'):
            stype = 'A'
        else:
            stype = '?'

        try:
            rows = parse_teslameter_file(fpath)
        except Exception:
            continue

        for dt, fields, temp in rows:
            if dt.strftime('%Y-%m-%d') == target_date and abs(temp - SENTINEL) > 1:
                all_temps.append((dt, temp, stype))

    if not all_temps:
        out.append('  No temperature data found for %s' % target_date)
        out.append('')
        return

    all_temps.sort()
    temps_arr = np.array([t[1] for t in all_temps])

    out.append('  Total temperature readings: %d' % len(all_temps))
    out.append('  Overall range: %.1f - %.1f C  (swing = %.1f C)' %
               (np.min(temps_arr), np.max(temps_arr), np.ptp(temps_arr)))
    out.append('  Mean: %.1f C   Median: %.1f C   Std: %.2f C' %
               (np.mean(temps_arr), np.median(temps_arr), np.std(temps_arr)))
    out.append('')

    # Time windows
    windows = [
        ('Morning', 'before 11:00', 0, 11),
        ('Midday', '11:00-15:00', 11, 15),
        ('Afternoon', 'after 15:00', 15, 24),
    ]
    window_stats = {}
    for wname, desc, h0, h1 in windows:
        wt = np.array([t[1] for t in all_temps if h0 <= t[0].hour < h1])
        if len(wt) > 0:
            window_stats[wname] = (np.mean(wt), np.std(wt), len(wt),
                                    np.min(wt), np.max(wt))
            out.append('  %s (%s): N=%d, mean=%.1f +/- %.1f C, range=[%.1f, %.1f]' %
                       (wname, desc, len(wt), np.mean(wt), np.std(wt),
                        np.min(wt), np.max(wt)))
    out.append('')

    # ---- Plot ----
    fig, ax = plt.subplots(figsize=(12, 6))

    type_colors = {'Y': '#1F77B4', 'H': '#FF7F0E', 'A': '#2CA02C', '?': '#999999'}
    type_labels_done = set()

    for dt, temp, stype in all_temps:
        hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        lbl = '%s-plates' % stype if stype not in type_labels_done else None
        ax.scatter(hour, temp, c=type_colors.get(stype, '#999999'),
                   s=12, alpha=0.4, label=lbl)
        type_labels_done.add(stype)

    # Shaded windows + annotations
    window_shades = [('#3498db', 0.06), ('#f39c12', 0.06), ('#e74c3c', 0.06)]
    for (wname, desc, h0, h1), (wcolor, walpha) in zip(windows, window_shades):
        ax.axvspan(h0, h1, alpha=walpha, color=wcolor)
        if wname in window_stats:
            wmean, wstd, wn, _, _ = window_stats[wname]
            ax.text((h0 + min(h1, 20)) / 2.0, np.max(temps_arr) + 0.8,
                    '%s\n%.1f +/- %.1f C (N=%d)' % (wname, wmean, wstd, wn),
                    ha='center', fontsize=9, color=wcolor, fontweight='bold')

    ax.set_xlabel('Time of Day (hours)', fontsize=12)
    ax.set_ylabel('Teslameter Temperature (C)', fontsize=12)
    ax.set_title('C2-2: Temperature Survey, %s' % target_date, fontweight='bold')
    ax.legend(title='Sample Type', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(7, 21)

    plt.tight_layout()
    plot_path = os.path.join(ANALYSIS_DIR, 'C2-2_temperature_evolution.png')
    fig.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    out.append('  Plot saved: %s' % os.path.basename(plot_path))
    out.append('')


# ---- Section 4: Delta Slug Assessment ------------------------------------

def section_delta_slugs(target_date, out):
    """Assess delta slug field magnitudes from teslameter data."""
    out.append('=' * 70)
    out.append('SECTION 4: DELTA SLUG ASSESSMENT')
    out.append('=' * 70)
    out.append('')

    slugs = find_delta_slugs()
    out.append('  Delta slugs from inventory: %d' % len(slugs))

    slug_data = []       # (slug_id, avg_mag, n_orient)
    slug_detail = []     # (slug_id, orient, [Bx,By,Bz], temp)
    n_found = 0
    n_no_date = 0
    n_no_file = 0

    for slug_id in sorted(slugs):
        magnitudes = []
        any_file = False
        for orient in ['front', 'side', 'top']:
            tpath = os.path.join(TESLA_DIR, '%s_%s.dat' % (slug_id, orient))
            if not os.path.exists(tpath):
                continue
            any_file = True
            rows = parse_teslameter_file(tpath)
            for dt, fields, temp in rows:
                if dt.strftime('%Y-%m-%d') == target_date:
                    mag = np.sqrt(sum(f ** 2 for f in fields))
                    magnitudes.append(mag)
                    slug_detail.append((slug_id, orient, fields, temp))

        if magnitudes:
            n_found += 1
            slug_data.append((slug_id, np.mean(magnitudes), len(magnitudes)))
        elif any_file:
            n_no_date += 1
        else:
            n_no_file += 1

    out.append('  With %s teslameter data: %d' % (target_date, n_found))
    out.append('  Files present but no %s data: %d' % (target_date, n_no_date))
    out.append('  No teslameter files at all: %d' % n_no_file)
    out.append('')

    if slug_data:
        mags = np.array([s[1] for s in slug_data])
        out.append('  Vector magnitude statistics (mT):')
        out.append('    Mean:   %.3f' % np.mean(mags))
        out.append('    Median: %.3f' % np.median(mags))
        out.append('    Range:  %.3f - %.3f' % (np.min(mags), np.max(mags)))
        out.append('    Std:    %.3f' % np.std(mags))
        out.append('')

        # Component-level breakdown across all slugs
        all_bx = np.array([d[2][0] for d in slug_detail])
        all_by = np.array([d[2][1] for d in slug_detail])
        all_bz = np.array([d[2][2] for d in slug_detail])
        all_temps = np.array([d[3] for d in slug_detail])

        out.append('  Component-level breakdown (N=%d readings, all slugs):' %
                   len(slug_detail))
        out.append('    Axis    Mean(mT)  Std(mT)   |Mean|   |Max|')
        for label, arr in [('Bx', all_bx), ('By', all_by), ('Bz', all_bz)]:
            out.append('    %-4s  %+8.4f  %8.4f  %7.4f  %7.4f' %
                       (label, np.mean(arr), np.std(arr),
                        np.mean(np.abs(arr)), np.max(np.abs(arr))))
        out.append('')

        # Per-orientation breakdown
        out.append('  Per-orientation noise (vector magnitude, mT):')
        for orient in ['front', 'side', 'top']:
            o_mags = [np.sqrt(sum(f**2 for f in d[2]))
                      for d in slug_detail if d[1] == orient]
            if o_mags:
                o_arr = np.array(o_mags)
                out.append('    %-6s  N=%2d  mean=%.4f  std=%.4f  max=%.4f' %
                           (orient, len(o_arr), np.mean(o_arr),
                            np.std(o_arr), np.max(o_arr)))
        out.append('')

        # Check for axis anisotropy
        rms_bx = np.sqrt(np.mean(all_bx**2))
        rms_by = np.sqrt(np.mean(all_by**2))
        rms_bz = np.sqrt(np.mean(all_bz**2))
        rms_vals = [rms_bx, rms_by, rms_bz]
        rms_labels = ['Bx', 'By', 'Bz']
        max_rms = max(rms_vals)
        min_rms = min(rms_vals)
        out.append('  Axis anisotropy (RMS):  Bx=%.4f  By=%.4f  Bz=%.4f mT' %
                   (rms_bx, rms_by, rms_bz))
        if max_rms > 3 * min_rms and min_rms > 0:
            dominant = rms_labels[rms_vals.index(max_rms)]
            out.append('    ** %s axis dominates (%.1fx larger) '
                       '-- possible probe alignment bias or stray field **' %
                       (dominant, max_rms / min_rms))
        else:
            out.append('    Noise is roughly isotropic across axes.')
        out.append('')

        # Temperature at slug measurement times
        out.append('  Slug measurement temperatures:')
        out.append('    Mean: %.1f C   Range: %.1f - %.1f C' %
                   (np.mean(all_temps), np.min(all_temps), np.max(all_temps)))
        out.append('')

        out.append('  Individual readings:')
        for slug_id, avg_mag, n in slug_data:
            out.append('    %-15s  %.3f mT  (N=%d orient.)' %
                       (slug_id, avg_mag, n))
        out.append('')

        # Assessment
        med = np.median(mags)
        out.append('  ASSESSMENT: Slug fields at noise floor (median %.3f mT).' % med)
        out.append('  Slugs serve as zero-field references for characterizing:')
        out.append('    - Teslameter noise floor per measurement session')
        out.append('    - Time-of-day drift (co-located with real magnets)')
        out.append('    - Session-to-session instrument stability')
        out.append('    - Axis anisotropy and orientation-dependent systematics')
        out.append('  Continue measuring; track trends across Campaign 2.')
    else:
        out.append('  No delta slug data available for assessment.')

    out.append('')


# ---- Section 5: Fleet Overview --------------------------------------------

def section_fleet(target_date, materials, out):
    """Compare C2 readings to C1 reference for all tunnel Y-plates."""
    out.append('=' * 70)
    out.append('SECTION 5: FLEET OVERVIEW (C2 vs C1)')
    out.append('=' * 70)
    out.append('')

    c1_ref = load_campaign1_reference()
    helm_readings, helm_anomalies = get_y_helm_readings(target_date)
    y_temps = get_y_tesla_temps(target_date)

    if helm_anomalies:
        out.append('  Data anomalies detected:')
        for a in helm_anomalies:
            out.append('    %s' % a)
        out.append('')

    # Build fleet entries for tunnel plates only
    fleet = []
    for sid in sorted(helm_readings.keys()):
        pm = re.match(r'Y-(\d+)-(\d+)', sid)
        if not pm:
            continue
        plate = int(pm.group(1))
        slot = int(pm.group(2))

        if plate not in PLACEMENTS:
            continue

        mat = materials.get(sid)
        if not mat:
            continue

        readings = helm_readings[sid]
        if not readings:
            continue

        h_dt, h_raw = readings[0]  # first valid reading

        # Average teslameter temp for this sample on target date
        if sid in y_temps and y_temps[sid]:
            temp = np.mean([t[1] for t in y_temps[sid]])
        else:
            temp = None

        h_corr = temp_correct(h_raw, temp, mat) if temp is not None else None

        c1 = c1_ref.get(sid)
        c1_bl = c1['baseline_mWC'] if c1 else None
        c1_end = c1['latest_mWC'] if c1 else None
        c1_pct = c1['pct_change'] if c1 else None

        # Comparisons
        c2_vs_end = None
        c2_vs_bl = None
        if h_corr is not None and c1_end is not None and c1_end > MIN_BASELINE:
            c2_vs_end = (h_corr - c1_end) / c1_end * 100.0
        if h_corr is not None and c1_bl is not None and c1_bl > MIN_BASELINE:
            c2_vs_bl = (h_corr - c1_bl) / c1_bl * 100.0

        fleet.append({
            'sample_id': sid, 'plate': plate, 'slot': slot,
            'material': mat,
            'region': PLACEMENTS.get(plate, 'Unknown'),
            'c2_raw': h_raw, 'c2_temp': temp, 'c2_corrected': h_corr,
            'c2_time': h_dt,
            'c1_baseline': c1_bl, 'c1_endpoint': c1_end, 'c1_pct': c1_pct,
            'c2_vs_c1end_pct': c2_vs_end, 'c2_vs_baseline_pct': c2_vs_bl,
        })

    # ---- Summary statistics ----
    n_total = len(fleet)
    n_temp = sum(1 for e in fleet if e['c2_temp'] is not None)
    n_corr = sum(1 for e in fleet if e['c2_corrected'] is not None)
    n_match = sum(1 for e in fleet if e['c2_vs_c1end_pct'] is not None)

    out.append('  Tunnel Y-samples with %s Helmholtz: %d' % (target_date, n_total))
    out.append('  With teslameter temperature: %d' % n_temp)
    out.append('  Fully matched to C1 reference: %d' % n_match)
    out.append('')

    # Per-material: C2 vs C1 endpoint
    out.append('  C2 vs C1 Endpoint (should be ~0%% if no change during storage):')
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        vals = [e['c2_vs_c1end_pct'] for e in fleet
                if e['material'] == mat and e['c2_vs_c1end_pct'] is not None]
        if vals:
            arr = np.array(vals)
            out.append('    %-12s  N=%2d  mean=%+.3f%%  std=%.3f%%  '
                       'range=[%+.3f, %+.3f]%%' %
                       (MAT_LABELS.get(mat, mat), len(arr), np.mean(arr),
                        np.std(arr), np.min(arr), np.max(arr)))
    out.append('')

    # Per-material: C2 vs original baseline (should match C1 degradation)
    out.append('  C2 vs Original Baseline (should match C1 degradation):')
    out.append('  %-12s  %10s  %10s' % ('Material', 'C2 (%)', 'C1 (%)'))
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        c2_v = [e['c2_vs_baseline_pct'] for e in fleet
                if e['material'] == mat and e['c2_vs_baseline_pct'] is not None]
        c1_v = [e['c1_pct'] for e in fleet
                if e['material'] == mat and e['c1_pct'] is not None]
        if c2_v:
            out.append('  %-12s  %+.3f+/-%.3f  %+.3f+/-%.3f' %
                       (MAT_LABELS.get(mat, mat)[:12],
                        np.mean(c2_v), np.std(c2_v),
                        np.mean(c1_v), np.std(c1_v)))
    out.append('')

    # ---- Per-plate NdFeB-SmCo differential ----
    plate_c1_diff = {}
    plate_c2_diff = {}
    plate_region = {}

    for plate in sorted(PLACEMENTS.keys()):
        pe = [e for e in fleet
              if e['plate'] == plate and e['c2_vs_baseline_pct'] is not None]
        if len(pe) < 2:
            continue  # need at least one NdFeB and one SmCo

        ndfeb_c2 = [e['c2_vs_baseline_pct'] for e in pe
                    if e['material'] in ('N42EH', 'N52SH')]
        smco_c2 = [e['c2_vs_baseline_pct'] for e in pe
                   if e['material'].startswith('SmCo')]
        ndfeb_c1 = [e['c1_pct'] for e in pe
                    if e['material'] in ('N42EH', 'N52SH')]
        smco_c1 = [e['c1_pct'] for e in pe
                   if e['material'].startswith('SmCo')]

        if ndfeb_c2 and smco_c2 and ndfeb_c1 and smco_c1:
            plate_c2_diff[plate] = np.mean(ndfeb_c2) - np.mean(smco_c2)
            plate_c1_diff[plate] = np.mean(ndfeb_c1) - np.mean(smco_c1)
            plate_region[plate] = PLACEMENTS[plate]

    out.append('  NdFeB - SmCo differential per plate (from original baseline):')
    if plate_c2_diff:
        c2_d = np.array(list(plate_c2_diff.values()))
        c1_d = np.array(list(plate_c1_diff.values()))
        resid = np.array([plate_c2_diff[p] - plate_c1_diff[p]
                          for p in plate_c2_diff])
        out.append('    C2 mean diff: %+.3f +/- %.3f%%  (N=%d plates)' %
                   (np.mean(c2_d), np.std(c2_d) / np.sqrt(len(c2_d)),
                    len(c2_d)))
        out.append('    C1 mean diff: %+.3f +/- %.3f%%' %
                   (np.mean(c1_d), np.std(c1_d) / np.sqrt(len(c1_d))))
        out.append('    C2-C1 residual: %+.3f +/- %.3f%%' %
                   (np.mean(resid), np.std(resid)))
    out.append('')

    # End-of-day assessment: do afternoon readings show more scatter?
    out.append('  End-of-day assessment (C2 vs C1 endpoint scatter by time):')
    morning = [e for e in fleet
               if e['c2_time'].hour < 13 and e['c2_vs_c1end_pct'] is not None]
    afternoon = [e for e in fleet
                 if e['c2_time'].hour >= 13 and e['c2_vs_c1end_pct'] is not None]
    if morning:
        mv = np.array([e['c2_vs_c1end_pct'] for e in morning])
        out.append('    Before 13:00 (N=%d): mean=%+.3f%%, std=%.3f%%' %
                   (len(mv), np.mean(mv), np.std(mv)))
    if afternoon:
        av = np.array([e['c2_vs_c1end_pct'] for e in afternoon])
        out.append('    After 13:00  (N=%d): mean=%+.3f%%, std=%.3f%%' %
                   (len(av), np.mean(av), np.std(av)))
    if morning and afternoon:
        mv = np.array([e['c2_vs_c1end_pct'] for e in morning])
        av = np.array([e['c2_vs_c1end_pct'] for e in afternoon])
        if np.std(av) > 1.5 * np.std(mv):
            out.append('    ** Afternoon readings show notably larger scatter **')
        else:
            out.append('    No significant difference in scatter.')
    out.append('')

    # ==== PLOTS ====

    # ---- C2-3: Campaign comparison scatter ----
    if plate_c1_diff and plate_c2_diff:
        fig, ax = plt.subplots(figsize=(8, 8))

        for plate in sorted(plate_c1_diff.keys()):
            region = plate_region[plate]
            color = REGION_COLORS.get(region, '#999999')
            ax.scatter(plate_c1_diff[plate], plate_c2_diff[plate],
                       c=color, s=70, zorder=5,
                       edgecolors='black', linewidths=0.5)
            ax.annotate(str(plate),
                        (plate_c1_diff[plate], plate_c2_diff[plate]),
                        textcoords='offset points', xytext=(5, 5),
                        fontsize=7)

        # 1:1 line
        all_vals = (list(plate_c1_diff.values()) +
                    list(plate_c2_diff.values()))
        lim = max(abs(min(all_vals)), abs(max(all_vals))) * 1.3
        ax.plot([-lim, lim], [-lim, lim], 'k--', alpha=0.4,
                linewidth=1.5, label='1:1 line')
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)

        # Region legend
        for region in sorted(set(plate_region.values())):
            ax.scatter([], [], c=REGION_COLORS.get(region, '#999999'),
                       s=70, label=region, edgecolors='black', linewidths=0.5)
        ax.legend(fontsize=9, loc='upper left')

        ax.set_xlabel('C1 NdFeB-SmCo Differential (%)', fontsize=12)
        ax.set_ylabel('C2 NdFeB-SmCo Differential (%)', fontsize=12)
        ax.set_title('C2-3: Campaign 2 vs Campaign 1 Differential\n'
                     '(from original baseline; 1:1 = no change)',
                     fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        plt.tight_layout()
        p = os.path.join(ANALYSIS_DIR, 'C2-3_campaign_comparison.png')
        fig.savefig(p, dpi=150, bbox_inches='tight')
        plt.close(fig)
        out.append('  Plot saved: %s' % os.path.basename(p))

    # ---- C2-4: Material distributions ----
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('C2-4: Per-Material Degradation: C2 (Apr 2026) vs C1 (Jan 2026)\n'
                 'Both computed from original pre-deployment baseline',
                 fontsize=13, fontweight='bold')

    for i, mat in enumerate(['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']):
        ax = axes[i // 2][i % 2]

        c1_vals = np.array([e['c1_pct'] for e in fleet
                            if e['material'] == mat and e['c1_pct'] is not None])
        c2_vals = np.array([e['c2_vs_baseline_pct'] for e in fleet
                            if e['material'] == mat
                            and e['c2_vs_baseline_pct'] is not None])

        if len(c1_vals) == 0 and len(c2_vals) == 0:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                    transform=ax.transAxes)
            ax.set_title(MAT_LABELS.get(mat, mat), fontweight='bold')
            continue

        # Compute common bin range
        all_v = np.concatenate([c1_vals, c2_vals]) if len(c2_vals) else c1_vals
        vmin, vmax = np.min(all_v), np.max(all_v)
        pad = max(0.1, (vmax - vmin) * 0.2)
        bins = np.linspace(vmin - pad, vmax + pad, 20)

        if len(c1_vals):
            ax.hist(c1_vals, bins=bins, alpha=0.5, color='#AAAAAA',
                    edgecolor='#666666', linewidth=0.5,
                    label='C1 (mean=%+.3f%%)' % np.mean(c1_vals))
        if len(c2_vals):
            ax.hist(c2_vals, bins=bins, alpha=0.6,
                    color=MAT_COLORS[mat], edgecolor='black', linewidth=0.5,
                    label='C2 (mean=%+.3f%%)' % np.mean(c2_vals))

        ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.4)
        ax.set_xlabel('Change from Baseline (%)')
        ax.set_ylabel('Count')
        ax.set_title('%s (N=%d)' % (MAT_LABELS.get(mat, mat), len(c2_vals)),
                     fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.91])
    p = os.path.join(ANALYSIS_DIR, 'C2-4_material_distributions.png')
    fig.savefig(p, dpi=150, bbox_inches='tight')
    plt.close(fig)
    out.append('  Plot saved: %s' % os.path.basename(p))
    out.append('')

    return fleet


# ---- CSV Output -----------------------------------------------------------

def write_csv(fleet, out):
    """Write per-sample comparison CSV."""
    csv_path = os.path.join(ANALYSIS_DIR, 'campaign2_vs_campaign1.csv')
    fields = [
        'sample_id', 'plate', 'slot', 'material', 'region',
        'c2_raw_mWC', 'c2_temp_C', 'c2_corrected_mWC', 'c2_time',
        'c1_baseline_mWC', 'c1_endpoint_mWC', 'c1_pct_change',
        'c2_vs_c1end_pct', 'c2_vs_baseline_pct',
    ]

    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for e in sorted(fleet, key=lambda x: (x['plate'], x['slot'])):
            row = {
                'sample_id': e['sample_id'],
                'plate': e['plate'],
                'slot': e['slot'],
                'material': e['material'],
                'region': e['region'],
                'c2_raw_mWC': '%.4f' % e['c2_raw'],
                'c2_temp_C': ('%.1f' % e['c2_temp']
                              if e['c2_temp'] is not None else ''),
                'c2_corrected_mWC': ('%.4f' % e['c2_corrected']
                                     if e['c2_corrected'] is not None else ''),
                'c2_time': e['c2_time'].strftime('%H:%M:%S'),
                'c1_baseline_mWC': ('%.4f' % e['c1_baseline']
                                    if e['c1_baseline'] is not None else ''),
                'c1_endpoint_mWC': ('%.4f' % e['c1_endpoint']
                                    if e['c1_endpoint'] is not None else ''),
                'c1_pct_change': ('%.4f' % e['c1_pct']
                                  if e['c1_pct'] is not None else ''),
                'c2_vs_c1end_pct': ('%.4f' % e['c2_vs_c1end_pct']
                                    if e['c2_vs_c1end_pct'] is not None else ''),
                'c2_vs_baseline_pct': ('%.4f' % e['c2_vs_baseline_pct']
                                       if e['c2_vs_baseline_pct'] is not None
                                       else ''),
            }
            writer.writerow(row)

    out.append('  CSV saved: %s' % os.path.basename(csv_path))


# ---- Main -----------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Campaign 2 Initial Data Quality Check')
    parser.add_argument('--date', default='2026-04-20',
                        help='Target measurement date (YYYY-MM-DD)')
    args = parser.parse_args()
    target_date = args.date

    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    print('Campaign 2 Data Quality Check')
    print('Target date: %s' % target_date)
    print('Output dir:  %s/' % ANALYSIS_DIR)
    print()

    out = []
    out.append('Campaign 2 Initial Data Quality Check')
    out.append('Target date: %s' % target_date)
    out.append('Generated:   %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    out.append('')

    # Load materials
    materials = load_y_materials()
    print('Loaded %d material assignments' % len(materials))

    # Section 1: Data Inventory
    print('Section 1: Data Inventory...')
    y_with_data = section_inventory(target_date, out)

    # Section 2: Y-14 Calibration
    print('Section 2: Y-14 Calibration...')
    section_calibration(target_date, materials, out)

    # Section 3: Temperature Survey
    print('Section 3: Temperature Survey...')
    section_temperature(target_date, out)

    # Section 4: Delta Slug Assessment
    print('Section 4: Delta Slug Assessment...')
    section_delta_slugs(target_date, out)

    # Section 5: Fleet Overview
    print('Section 5: Fleet Overview...')
    fleet = section_fleet(target_date, materials, out)

    # Write outputs
    if fleet:
        write_csv(fleet, out)

    summary_path = os.path.join(ANALYSIS_DIR, 'campaign2_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(out))
    print('\nSummary: %s' % summary_path)
    print('Done.')


if __name__ == '__main__':
    main()
