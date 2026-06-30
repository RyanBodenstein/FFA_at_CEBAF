#!/usr/bin/env python3
"""
Campaign 2 June Analysis -- Overall Behavior Overview
======================================================

With 4 time points (C1 baseline, C1 endpoint Jan 2026, C2 Apr 20, C2 Jun 2-3),
this script tracks how tunnel Y-plate magnets behave over time. No dosimetry
is available yet for C2, so this is magnetic-measurement-only.

Data sources:
  C1 baseline / endpoint:  Data_Package/02_Magnetic_Measurements/y_plate_degradation.csv
  C2 April 20:             2026_Data_Run/Analysis/campaign2_vs_campaign1.csv
  C2 June 2-3:             2026_Data_Run/2026-6-3-Helmholtz/ + Teslameter folders

Output: 2026_Data_Run/Analysis/June_Analysis/
  c2_timeseries.csv
  june_analysis_summary.txt
  JA1_timeseries.png
  JA2_c2_progression.png
  JA3_differential_tracking.png
  JA4_june_vs_april.png
  JA5_y14_tracking.png

Usage: python3 2026_Data_Run/c2_june_analysis.py
"""

import os
import re
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
ANALYSIS_DIR = os.path.join(BASE, 'Analysis', 'June_Analysis')
PROJECT_DIR = os.path.dirname(BASE)

JUNE_HELM_DIR = os.path.join(BASE, '2026-6-3-Helmholtz')
JUNE_TESLA_DIRS = {
    '2026-06-02': os.path.join(BASE, '2026-06-02_Teslameter'),
    '2026-06-03': os.path.join(BASE, '2026-06-03_Teslameter'),
}
SPREADSHEET = os.path.join(PROJECT_DIR, 'Materials_Arrangements_Spreadsheet.xlsx')
C1_CSV = os.path.join(PROJECT_DIR, 'Data_Package', '02_Magnetic_Measurements',
                       'y_plate_degradation.csv')
APRIL_CSV = os.path.join(BASE, 'Analysis', 'campaign2_vs_campaign1.csv')
APRIL_TESLA_DIR = os.path.join(BASE, '2026-04-20_Teslameter')

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
MAT_ORDER = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

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
LAB_PLATES = {8, 14, 27, 28, 29, 31, 33, 35, 37}
CALIBRATION_PLATE = 14

# June dates to scan for fleet readings
JUNE_DATES = ['2026-06-01', '2026-06-02', '2026-06-03']


# ---- Parsers (copied from campaign2_quality_check.py) ----------------------

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


def temp_correct(raw_mwc, temp, material):
    """Correct Helmholtz mWC reading to T_REF using material temp coefficient."""
    alpha = ALPHA.get(material, -0.0004)
    return raw_mwc / (1.0 + alpha * (temp - T_REF))


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
                    if mat == 'SmCo33':
                        mat = 'SmCo33H'
                    materials['Y-%s-%d' % (pn, i)] = mat
    return materials


def load_campaign1():
    """Load C1 per-sample baseline and endpoint (temp-corrected to 20C)."""
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
                'endpoint_mWC': float(row['latest_mWC']),
                'c1_pct_change': float(row['pct_change']),
                'is_outlier': row['is_outlier'] == 'True',
            }
    return c1


def load_april_c2():
    """Load C2 April 20 data from campaign2_vs_campaign1.csv."""
    apr = {}
    with open(APRIL_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row['sample_id']
            apr[sid] = {
                'raw_mWC': float(row['c2_raw_mWC']),
                'temp_C': float(row['c2_temp_C']),
                'corrected_mWC': float(row['c2_corrected_mWC']),
                'time': row['c2_time'],
            }
    return apr


# ---- June Data Parsing ----------------------------------------------------

def get_june_helmholtz():
    """Parse all Y-plate Helmholtz files for June readings.

    Returns dict: sample_id -> list of (datetime, value) for June dates.
    Also returns list of anomaly strings.
    """
    readings = defaultdict(list)
    anomalies = []

    for fname in sorted(os.listdir(JUNE_HELM_DIR)):
        hm = re.match(r'(Y-(\d+)-(\d+))_helmholtz\.dat$', fname)
        if not hm:
            continue
        sid = hm.group(1)
        rows = parse_helmholtz_file(os.path.join(JUNE_HELM_DIR, fname))

        for dt, v, u in rows:
            date_str = dt.strftime('%Y-%m-%d')
            if date_str not in JUNE_DATES:
                continue
            if u != 'mWC':
                continue
            if abs(v - SENTINEL) < 1:
                continue
            if abs(v) < MIN_BASELINE:
                anomalies.append(
                    '%s: near-zero reading %.4f mWC on %s (FAILED)'
                    % (sid, v, date_str))
                continue
            readings[sid].append((dt, v))

    return readings, anomalies


def get_june_teslameter_temps(target_date):
    """Get teslameter temperatures for Y-plates on a specific June date.

    Returns dict: sample_id -> list of (datetime, temp).
    """
    tesla_dir = JUNE_TESLA_DIRS.get(target_date)
    if not tesla_dir or not os.path.isdir(tesla_dir):
        return {}

    temps = defaultdict(list)
    for fname in sorted(os.listdir(tesla_dir)):
        tm = re.match(r'(Y-\d+-\d+)_(front|side|top)\.dat$', fname)
        if not tm:
            continue
        sid = tm.group(1)
        rows = parse_teslameter_file(os.path.join(tesla_dir, fname))
        for dt, fields, temp in rows:
            if (dt.strftime('%Y-%m-%d') == target_date
                    and abs(temp - SENTINEL) > 1):
                temps[sid].append((dt, temp))
    return temps


def resolve_june_readings(readings, materials, anomalies):
    """For each sample, pick the appropriate June reading.

    For non-calibration tunnel/lab plates: use the LAST reading on the
    latest June date (handles Y-3-2 duplicate).
    For Y-14 calibration: keep ALL readings (including April) for tracking.

    Returns:
      fleet: dict sid -> {raw, temp, corrected, date, datetime}
      cal_readings: list of dicts for Y-14 all readings
    """
    # Gather all June teslameter temps (both days)
    all_temps = {}
    for date_str in JUNE_DATES:
        day_temps = get_june_teslameter_temps(date_str)
        for sid, tlist in day_temps.items():
            if sid not in all_temps:
                all_temps[sid] = []
            all_temps[sid].extend(tlist)

    # Also gather April teslameter temps for Y-14 calibration tracking
    if os.path.isdir(APRIL_TESLA_DIR):
        for fname in sorted(os.listdir(APRIL_TESLA_DIR)):
            tm = re.match(r'(Y-14-\d+)_(front|side|top)\.dat$', fname)
            if not tm:
                continue
            sid = tm.group(1)
            rows_t = parse_teslameter_file(os.path.join(APRIL_TESLA_DIR, fname))
            for dt, fields, temp in rows_t:
                if (dt.strftime('%Y-%m-%d') == '2026-04-20'
                        and abs(temp - SENTINEL) > 1):
                    if sid not in all_temps:
                        all_temps[sid] = []
                    all_temps[sid].append((dt, temp))

    fleet = {}
    cal_readings = []

    for sid, rlist in sorted(readings.items()):
        plate_num = int(re.search(r'Y-(\d+)', sid).group(1))
        mat = materials.get(sid, 'Unknown')

        if plate_num == CALIBRATION_PLATE:
            # Keep all readings for calibration tracking (including April)
            # Re-parse to get ALL dates (not just June-filtered)
            helm_path = os.path.join(JUNE_HELM_DIR, '%s_helmholtz.dat' % sid)
            if os.path.exists(helm_path):
                all_rows = parse_helmholtz_file(helm_path)
                cal_all = []
                for dt, v, u in all_rows:
                    ds = dt.strftime('%Y-%m-%d')
                    if u != 'mWC' or abs(v - SENTINEL) < 1 or abs(v) < MIN_BASELINE:
                        continue
                    # Keep April and June readings
                    if ds == '2026-04-20' or ds in JUNE_DATES:
                        cal_all.append((dt, v))
                rlist = cal_all

            for dt, v in sorted(rlist, key=lambda x: x[0]):
                date_str = dt.strftime('%Y-%m-%d')
                # Find temps near this reading
                sid_temps = all_temps.get(sid, [])
                nearby = [t for _, t in sid_temps
                          if abs((_ - dt).total_seconds()) < 600
                          for _ in [_]]
                # Re-do: iterate properly
                nearby_temps = []
                for t_dt, t_temp in sid_temps:
                    if abs((t_dt - dt).total_seconds()) < 600:
                        nearby_temps.append(t_temp)
                if nearby_temps:
                    avg_temp = np.mean(nearby_temps)
                elif sid_temps:
                    # Use nearest teslameter reading on same date
                    same_day = [(t_dt, t_temp) for t_dt, t_temp in sid_temps
                                if t_dt.strftime('%Y-%m-%d') == date_str]
                    if same_day:
                        closest = min(same_day,
                                      key=lambda t: abs((t[0] - dt).total_seconds()))
                        avg_temp = closest[1]
                    else:
                        closest = min(sid_temps,
                                      key=lambda t: abs((t[0] - dt).total_seconds()))
                        avg_temp = closest[1]
                else:
                    avg_temp = 23.0  # fallback

                corrected = temp_correct(v, avg_temp, mat)
                cal_readings.append({
                    'sample_id': sid, 'slot': int(sid.split('-')[2]),
                    'material': mat, 'datetime': dt,
                    'date': date_str, 'time': dt.strftime('%H:%M:%S'),
                    'raw_mWC': v, 'temp_C': avg_temp,
                    'corrected_mWC': corrected,
                })
            continue

        # Non-calibration: use last reading on the latest available date
        sorted_readings = sorted(rlist, key=lambda x: x[0])
        if not sorted_readings:
            continue

        # Use the LAST reading (handles Y-3-2 duplicate)
        dt, v = sorted_readings[-1]
        date_str = dt.strftime('%Y-%m-%d')

        if len(sorted_readings) > 1:
            # Check if multiple readings on same date
            dates_seen = set(r[0].strftime('%Y-%m-%d') for r in sorted_readings)
            june_dates_seen = [d for d in dates_seen if d.startswith('2026-06')]
            if len(sorted_readings) > 1:
                vals = [r[1] for r in sorted_readings if r[0].strftime('%Y-%m-%d').startswith('2026-06')]
                if len(vals) > 1:
                    anomalies.append(
                        '%s: %d June readings (values: %s); using last (%.4f)'
                        % (sid, len(vals),
                           ', '.join('%.4f' % x for x in vals), v))

        # Get temperature for this reading
        sid_temps = all_temps.get(sid, [])
        nearby_temps = []
        for t_dt, t_temp in sid_temps:
            if abs((t_dt - dt).total_seconds()) < 600:
                nearby_temps.append(t_temp)
        if nearby_temps:
            avg_temp = np.mean(nearby_temps)
        elif sid_temps:
            same_day = [(t_dt, t_temp) for t_dt, t_temp in sid_temps
                        if t_dt.strftime('%Y-%m-%d') == date_str]
            if same_day:
                closest = min(same_day,
                              key=lambda t: abs((t[0] - dt).total_seconds()))
                avg_temp = closest[1]
            else:
                closest = min(sid_temps,
                              key=lambda t: abs((t[0] - dt).total_seconds()))
                avg_temp = closest[1]
        else:
            avg_temp = 23.0
            anomalies.append('%s: no teslameter temp found, using 23.0C' % sid)

        corrected = temp_correct(v, avg_temp, mat)
        fleet[sid] = {
            'raw_mWC': v, 'temp_C': avg_temp,
            'corrected_mWC': corrected,
            'date': date_str, 'datetime': dt,
        }

    return fleet, cal_readings


# ---- Master CSV ------------------------------------------------------------

def build_timeseries(c1, apr, june_fleet, materials):
    """Build the master timeseries: one row per tunnel sample.

    Returns list of dicts (rows) and list of notes.
    """
    rows = []
    notes = []

    tunnel_plates = sorted(PLACEMENTS.keys())
    for plate in tunnel_plates:
        for slot in range(1, 5):
            sid = 'Y-%d-%d' % (plate, slot)
            mat = materials.get(sid, 'Unknown')
            region = PLACEMENTS.get(plate, 'Unknown')

            # C1 data
            c1_data = c1.get(sid)
            if not c1_data:
                notes.append('%s: no C1 reference data, skipping' % sid)
                continue

            baseline = c1_data['baseline_mWC']
            endpoint = c1_data['endpoint_mWC']
            c1_pct = c1_data['c1_pct_change']

            # April C2
            apr_data = apr.get(sid)
            apr_raw = apr_data['raw_mWC'] if apr_data else None
            apr_temp = apr_data['temp_C'] if apr_data else None
            apr_corr = apr_data['corrected_mWC'] if apr_data else None
            apr_date = '2026-04-20' if apr_data else ''

            # June C2
            jun_data = june_fleet.get(sid)
            jun_raw = jun_data['raw_mWC'] if jun_data else None
            jun_temp = jun_data['temp_C'] if jun_data else None
            jun_corr = jun_data['corrected_mWC'] if jun_data else None
            jun_date = jun_data['date'] if jun_data else ''

            # Derived: percent changes vs baseline
            apr_vs_baseline = (100.0 * (apr_corr - baseline) / baseline
                               if apr_corr and baseline else None)
            jun_vs_baseline = (100.0 * (jun_corr - baseline) / baseline
                               if jun_corr and baseline else None)
            jun_vs_apr = (100.0 * (jun_corr - apr_corr) / apr_corr
                          if jun_corr and apr_corr else None)
            jun_vs_c1end = (100.0 * (jun_corr - endpoint) / endpoint
                            if jun_corr and endpoint else None)

            is_outlier = c1_data.get('is_outlier', False)

            row = {
                'sample_id': sid, 'plate': plate, 'slot': slot,
                'material': mat, 'region': region, 'environment': 'tunnel',
                'is_outlier': is_outlier,
                'c1_baseline_mWC': baseline,
                'c1_endpoint_mWC': endpoint,
                'c1_pct_change': c1_pct,
                'c2_apr_raw_mWC': apr_raw,
                'c2_apr_temp_C': apr_temp,
                'c2_apr_corrected_mWC': apr_corr,
                'c2_apr_date': apr_date,
                'c2_jun_raw_mWC': jun_raw,
                'c2_jun_temp_C': jun_temp,
                'c2_jun_corrected_mWC': jun_corr,
                'c2_jun_date': jun_date,
                'c2_apr_vs_baseline_pct': apr_vs_baseline,
                'c2_jun_vs_baseline_pct': jun_vs_baseline,
                'c2_jun_vs_apr_pct': jun_vs_apr,
                'c2_jun_vs_c1end_pct': jun_vs_c1end,
            }
            rows.append(row)

    return rows, notes


def write_timeseries_csv(rows, filepath):
    """Write master timeseries CSV."""
    fieldnames = [
        'sample_id', 'plate', 'slot', 'material', 'region', 'environment',
        'is_outlier',
        'c1_baseline_mWC', 'c1_endpoint_mWC', 'c1_pct_change',
        'c2_apr_raw_mWC', 'c2_apr_temp_C', 'c2_apr_corrected_mWC', 'c2_apr_date',
        'c2_jun_raw_mWC', 'c2_jun_temp_C', 'c2_jun_corrected_mWC', 'c2_jun_date',
        'c2_apr_vs_baseline_pct', 'c2_jun_vs_baseline_pct',
        'c2_jun_vs_apr_pct', 'c2_jun_vs_c1end_pct',
    ]
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            # Format floats, leave None as empty
            out = {}
            for k in fieldnames:
                v = row[k]
                if v is None:
                    out[k] = ''
                elif isinstance(v, float):
                    out[k] = '%.4f' % v
                else:
                    out[k] = v
            writer.writerow(out)


# ---- Summary Text ---------------------------------------------------------

def write_summary(rows, cal_readings, anomalies, notes, filepath):
    """Write june_analysis_summary.txt."""
    lines = []
    lines.append('=' * 70)
    lines.append('C2 JUNE ANALYSIS SUMMARY')
    lines.append('Generated: %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    lines.append('=' * 70)
    lines.append('')

    # Data inventory
    n_total = len(rows)
    n_with_jun = sum(1 for r in rows if r['c2_jun_corrected_mWC'] is not None)
    n_with_apr = sum(1 for r in rows if r['c2_apr_corrected_mWC'] is not None)
    n_both = sum(1 for r in rows
                 if r['c2_jun_corrected_mWC'] is not None
                 and r['c2_apr_corrected_mWC'] is not None)
    lines.append('DATA INVENTORY')
    lines.append('  Tunnel samples in C1 reference: %d' % n_total)
    lines.append('  With June data:  %d' % n_with_jun)
    lines.append('  With April data: %d' % n_with_apr)
    lines.append('  With both Apr + Jun: %d' % n_both)
    lines.append('')

    # Missing samples
    missing_jun = [r['sample_id'] for r in rows
                   if r['c2_jun_corrected_mWC'] is None]
    missing_apr = [r['sample_id'] for r in rows
                   if r['c2_apr_corrected_mWC'] is None]
    if missing_jun:
        lines.append('  Missing June: %s' % ', '.join(missing_jun))
    if missing_apr:
        lines.append('  Missing April: %s' % ', '.join(missing_apr))
    # Jun-only (have June but not April)
    jun_only = [r['sample_id'] for r in rows
                if r['c2_jun_corrected_mWC'] is not None
                and r['c2_apr_corrected_mWC'] is None]
    if jun_only:
        lines.append('  June-only (no April): %s' % ', '.join(jun_only))
    lines.append('')

    # Per-material stats at each time point (% change from baseline)
    # Report CLEAN (outlier-excluded) as primary, with ALL noted
    lines.append('-' * 70)
    lines.append('PER-MATERIAL STATISTICS (% change from C1 baseline)')
    lines.append('  Outlier-excluded (clean). Known outliers: Y-34-4, Y-40-4.')
    lines.append('-' * 70)
    lines.append('')

    # Build arrays by material (clean only)
    clean_rows = [r for r in rows if not r.get('is_outlier', False)]
    outlier_rows = [r for r in rows if r.get('is_outlier', False)]
    if outlier_rows:
        lines.append('  Excluded outliers: %s'
                     % ', '.join('%s (%s, C1=%.1f%%)'
                                 % (r['sample_id'], r['material'], r['c1_pct_change'])
                                 for r in outlier_rows))
        lines.append('')

    by_mat = defaultdict(lambda: {
        'c1_pct': [], 'apr_pct': [], 'jun_pct': [],
        'jun_vs_apr_pct': [], 'jun_vs_c1end_pct': [],
    })
    for r in clean_rows:
        mat = r['material']
        by_mat[mat]['c1_pct'].append(r['c1_pct_change'])
        if r['c2_apr_vs_baseline_pct'] is not None:
            by_mat[mat]['apr_pct'].append(r['c2_apr_vs_baseline_pct'])
        if r['c2_jun_vs_baseline_pct'] is not None:
            by_mat[mat]['jun_pct'].append(r['c2_jun_vs_baseline_pct'])
        if r['c2_jun_vs_apr_pct'] is not None:
            by_mat[mat]['jun_vs_apr_pct'].append(r['c2_jun_vs_apr_pct'])
        if r['c2_jun_vs_c1end_pct'] is not None:
            by_mat[mat]['jun_vs_c1end_pct'].append(r['c2_jun_vs_c1end_pct'])

    for mat in MAT_ORDER:
        d = by_mat[mat]
        lines.append('  %s (%s):' % (mat, MAT_LABELS.get(mat, mat)))
        for label, key in [('C1 endpoint vs baseline', 'c1_pct'),
                           ('C2 Apr vs baseline', 'apr_pct'),
                           ('C2 Jun vs baseline', 'jun_pct'),
                           ('C2 Jun vs Apr (internal)', 'jun_vs_apr_pct'),
                           ('C2 Jun vs C1 endpoint', 'jun_vs_c1end_pct')]:
            vals = d[key]
            if vals:
                arr = np.array(vals)
                lines.append('    %-30s  mean=%+.3f%%  std=%.3f%%  N=%d'
                             % (label, np.mean(arr), np.std(arr, ddof=1)
                                if len(arr) > 1 else 0.0, len(arr)))
            else:
                lines.append('    %-30s  (no data)' % label)
        lines.append('')

    # NdFeB-SmCo differential at each time point
    lines.append('-' * 70)
    lines.append('NdFeB-SmCo DIFFERENTIAL (gain-immune headline metric)')
    lines.append('-' * 70)
    lines.append('')
    lines.append('Differential = mean(NdFeB pct) - mean(SmCo pct) per plate,')
    lines.append('then fleet mean +/- SEM across plates.')
    lines.append('')

    # Use clean_rows for differential (exclude outlier plates entirely)
    outlier_plates = set(r['plate'] for r in outlier_rows)

    for tp_label, pct_key in [('C1 endpoint', 'c1_pct_change'),
                               ('C2 Apr vs baseline', 'c2_apr_vs_baseline_pct'),
                               ('C2 Jun vs baseline', 'c2_jun_vs_baseline_pct')]:
        plate_diffs = []
        for plate in sorted(PLACEMENTS.keys()):
            if plate in outlier_plates:
                continue
            ndfeb_vals = []
            smco_vals = []
            for slot in range(1, 5):
                sid = 'Y-%d-%d' % (plate, slot)
                row = next((r for r in rows if r['sample_id'] == sid), None)
                if not row:
                    continue
                val = row[pct_key]
                if val is None:
                    continue
                mat = row['material']
                if mat in ('N42EH', 'N52SH'):
                    ndfeb_vals.append(val)
                elif mat in ('SmCo33H', 'SmCo35'):
                    smco_vals.append(val)
            if ndfeb_vals and smco_vals:
                diff = np.mean(ndfeb_vals) - np.mean(smco_vals)
                plate_diffs.append(diff)

        if plate_diffs:
            arr = np.array(plate_diffs)
            sem = np.std(arr, ddof=1) / np.sqrt(len(arr))
            sig = abs(np.mean(arr)) / sem if sem > 0 else float('inf')
            lines.append('  %-25s  diff=%+.3f%% +/- %.3f%% (%.1f sigma, N=%d plates)'
                         % (tp_label, np.mean(arr), sem, sig, len(arr)))
        else:
            lines.append('  %-25s  (insufficient data)' % tp_label)

    # C2-internal differential (June vs April)
    lines.append('')
    lines.append('  C2-internal (Jun vs Apr):')
    plate_diffs_c2 = []
    for plate in sorted(PLACEMENTS.keys()):
        if plate in outlier_plates:
            continue
        ndfeb_vals = []
        smco_vals = []
        for slot in range(1, 5):
            sid = 'Y-%d-%d' % (plate, slot)
            row = next((r for r in rows if r['sample_id'] == sid), None)
            if not row:
                continue
            val = row['c2_jun_vs_apr_pct']
            if val is None:
                continue
            mat = row['material']
            if mat in ('N42EH', 'N52SH'):
                ndfeb_vals.append(val)
            elif mat in ('SmCo33H', 'SmCo35'):
                smco_vals.append(val)
        if ndfeb_vals and smco_vals:
            diff = np.mean(ndfeb_vals) - np.mean(smco_vals)
            plate_diffs_c2.append(diff)

    if plate_diffs_c2:
        arr = np.array(plate_diffs_c2)
        sem = np.std(arr, ddof=1) / np.sqrt(len(arr))
        sig = abs(np.mean(arr)) / sem if sem > 0 else float('inf')
        lines.append('    diff=%+.3f%% +/- %.3f%% (%.1f sigma, N=%d plates)'
                     % (np.mean(arr), sem, sig, len(arr)))
    lines.append('')

    # Y-14 calibration tracking
    lines.append('-' * 70)
    lines.append('Y-14 CALIBRATION PLATE')
    lines.append('-' * 70)
    lines.append('')
    if cal_readings:
        for slot in range(1, 5):
            slot_data = [c for c in cal_readings if c['slot'] == slot]
            if not slot_data:
                continue
            mat = slot_data[0]['material']
            lines.append('  Y-14-%d (%s):' % (slot, mat))
            for c in sorted(slot_data, key=lambda x: x['datetime']):
                lines.append('    %s %s  raw=%.4f  T=%.1fC  corr=%.4f mWC'
                             % (c['date'], c['time'],
                                c['raw_mWC'], c['temp_C'], c['corrected_mWC']))
            corr_vals = np.array([c['corrected_mWC'] for c in slot_data])
            if len(corr_vals) > 1:
                spread = 100.0 * np.ptp(corr_vals) / np.mean(corr_vals)
                lines.append('    Corrected range: %.4f  spread: %.3f%%'
                             % (np.ptp(corr_vals), spread))
            lines.append('')
    else:
        lines.append('  No Y-14 calibration readings found in June data.')
        lines.append('')

    # Temperature summary for June
    lines.append('-' * 70)
    lines.append('JUNE TEMPERATURE SUMMARY')
    lines.append('-' * 70)
    lines.append('')
    jun_temps = [r['c2_jun_temp_C'] for r in rows
                 if r['c2_jun_temp_C'] is not None]
    if jun_temps:
        arr = np.array(jun_temps)
        lines.append('  Fleet (tunnel):  min=%.1fC  max=%.1fC  mean=%.1fC  range=%.1fC'
                     % (arr.min(), arr.max(), arr.mean(), np.ptp(arr)))
    lines.append('')

    # Anomalies and notes
    if anomalies:
        lines.append('-' * 70)
        lines.append('ANOMALIES')
        lines.append('-' * 70)
        for a in anomalies:
            lines.append('  ' + a)
        lines.append('')
    if notes:
        lines.append('-' * 70)
        lines.append('NOTES')
        lines.append('-' * 70)
        for n in notes:
            lines.append('  ' + n)
        lines.append('')

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return lines


# ---- Plots -----------------------------------------------------------------

def plot_ja1_timeseries(rows, filepath):
    """JA-1: Full 4-point time series, one panel per material."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('JA-1: Magnet Field Strength Time Series\n'
                 '(% change from C1 baseline, temp-corrected to 20C)',
                 fontsize=13, fontweight='bold')

    time_labels = ['C1\nBaseline', 'C1\nEndpoint\n(Jan 2026)',
                   'C2\nApr 2026', 'C2\nJun 2026']
    x_pos = [0, 1, 2.5, 3.5]  # Gap between C1 and C2

    for idx, mat in enumerate(MAT_ORDER):
        ax = axes[idx // 2][idx % 2]
        mat_rows = [r for r in rows if r['material'] == mat]
        clean_mat = [r for r in mat_rows if not r.get('is_outlier', False)]
        outlier_mat = [r for r in mat_rows if r.get('is_outlier', False)]

        traces = []
        for r in mat_rows:
            vals = [0.0, r['c1_pct_change']]  # baseline=0, C1 endpoint
            mask = [True, True]
            for key in ['c2_apr_vs_baseline_pct', 'c2_jun_vs_baseline_pct']:
                v = r[key]
                vals.append(v if v is not None else 0.0)
                mask.append(v is not None)
            traces.append((vals, mask, r['sample_id'],
                           r.get('is_outlier', False)))

        # Individual traces
        for vals, mask, sid, is_out in traces:
            x_plot = [x_pos[i] for i in range(4) if mask[i]]
            y_plot = [vals[i] for i in range(4) if mask[i]]
            if is_out:
                ax.plot(x_plot, y_plot, color='gray',
                        marker='x', alpha=0.5, markersize=6, linewidth=1.2,
                        linestyle=':', zorder=3)
                # Label outlier
                if y_plot:
                    ax.annotate(sid, (x_plot[-1], y_plot[-1]),
                                fontsize=6, color='gray', alpha=0.7,
                                xytext=(5, 5), textcoords='offset points')
            else:
                ax.plot(x_plot, y_plot, '-o', color=MAT_COLORS[mat],
                        alpha=0.2, markersize=3, linewidth=0.8)

        # Material mean at each time point (CLEAN ONLY)
        clean_traces = [(v, m, s) for v, m, s, o in traces if not o]
        means = []
        errs = []
        x_mean = []
        for j in range(4):
            point_vals = [t[0][j] for t in clean_traces if t[1][j]]
            if point_vals:
                means.append(np.mean(point_vals))
                errs.append(np.std(point_vals, ddof=1) / np.sqrt(len(point_vals))
                            if len(point_vals) > 1 else 0.0)
                x_mean.append(x_pos[j])

        ax.errorbar(x_mean, means, yerr=errs, fmt='s-',
                    color=MAT_COLORS[mat], linewidth=2.5, markersize=8,
                    capsize=5, capthick=2, zorder=10,
                    label='Mean +/- SEM (N=%d)' % len(clean_mat))

        # Vertical dashed line separating C1 and C2
        ax.axvline(x=1.75, color='gray', linestyle='--', alpha=0.5)
        ax.text(0.5, 0.97, 'C1', transform=ax.transAxes, fontsize=9,
                ha='center', va='top', color='gray', alpha=0.7)
        ax.text(0.85, 0.97, 'C2', transform=ax.transAxes, fontsize=9,
                ha='center', va='top', color='gray', alpha=0.7)

        ax.axhline(y=0, color='black', linewidth=0.5, alpha=0.3)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(time_labels, fontsize=8)
        ax.set_ylabel('% change from baseline')
        ax.set_title(MAT_LABELS[mat], fontsize=11, fontweight='bold',
                     color=MAT_COLORS[mat])
        ax.legend(fontsize=8, loc='lower left')
        ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print('  Saved %s' % os.path.basename(filepath))


def plot_ja2_c2_progression(rows, filepath):
    """JA-2: C2-only April vs June, paired comparison."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('JA-2: C2 Progression (April to June 2026)\n'
                 'Within-C2 change, temp-corrected to 20C',
                 fontsize=13, fontweight='bold')

    # Left panel: box/strip plot of Jun-vs-Apr pct by material (clean only)
    ax = axes[0]
    data_by_mat = {}
    for mat in MAT_ORDER:
        vals = [r['c2_jun_vs_apr_pct'] for r in rows
                if r['material'] == mat and r['c2_jun_vs_apr_pct'] is not None
                and not r.get('is_outlier', False)]
        data_by_mat[mat] = vals

    positions = range(len(MAT_ORDER))
    bp = ax.boxplot([data_by_mat[m] for m in MAT_ORDER],
                    positions=list(positions), widths=0.5,
                    patch_artist=True, showfliers=False)
    for i, mat in enumerate(MAT_ORDER):
        bp['boxes'][i].set_facecolor(MAT_COLORS[mat])
        bp['boxes'][i].set_alpha(0.3)
        bp['medians'][i].set_color('black')
        # Strip plot overlay
        vals = data_by_mat[mat]
        jitter = np.random.default_rng(42).normal(0, 0.08, len(vals))
        ax.scatter([i + j for j in jitter], vals,
                   color=MAT_COLORS[mat], alpha=0.6, s=25, zorder=5)
        # Mean marker
        if vals:
            ax.scatter([i], [np.mean(vals)], color=MAT_COLORS[mat],
                       marker='D', s=80, zorder=10, edgecolors='black',
                       linewidths=1.0)

    ax.set_xticks(list(positions))
    ax.set_xticklabels([MAT_LABELS[m] for m in MAT_ORDER], fontsize=9)
    ax.axhline(y=0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
    ax.set_ylabel('June vs April (% change)')
    ax.set_title('Per-sample change', fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')

    # Right panel: paired scatter (April pct vs June pct, both vs baseline)
    ax2 = axes[1]
    for mat in MAT_ORDER:
        mat_rows = [r for r in rows
                    if r['material'] == mat
                    and r['c2_apr_vs_baseline_pct'] is not None
                    and r['c2_jun_vs_baseline_pct'] is not None
                    and not r.get('is_outlier', False)]
        if not mat_rows:
            continue
        apr = [r['c2_apr_vs_baseline_pct'] for r in mat_rows]
        jun = [r['c2_jun_vs_baseline_pct'] for r in mat_rows]
        ax2.scatter(apr, jun, color=MAT_COLORS[mat], alpha=0.7, s=30,
                    label=MAT_LABELS[mat])

    # 1:1 line
    all_apr = [r['c2_apr_vs_baseline_pct'] for r in rows
               if r['c2_apr_vs_baseline_pct'] is not None]
    all_jun = [r['c2_jun_vs_baseline_pct'] for r in rows
               if r['c2_jun_vs_baseline_pct'] is not None]
    if all_apr and all_jun:
        lo = min(min(all_apr), min(all_jun)) - 0.1
        hi = max(max(all_apr), max(all_jun)) + 0.1
        ax2.plot([lo, hi], [lo, hi], 'k--', alpha=0.4, linewidth=1,
                 label='1:1 line')
        ax2.set_xlim(lo, hi)
        ax2.set_ylim(lo, hi)

    ax2.set_xlabel('C2 April vs baseline (%)')
    ax2.set_ylabel('C2 June vs baseline (%)')
    ax2.set_title('April vs June (% from baseline)', fontsize=11)
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print('  Saved %s' % os.path.basename(filepath))


def plot_ja3_differential_tracking(rows, filepath):
    """JA-3: NdFeB-SmCo differential tracked across all 4 time points.

    Two-panel figure:
      Left:  Overall trajectory (absolute differential at each time point)
      Right: Phase-by-phase paired changes between consecutive transitions
    """
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 7),
                                             gridspec_kw={'width_ratios': [1.2, 1]})
    fig.suptitle('JA-3: NdFeB-SmCo Differential Tracking (gain-immune)',
                 fontsize=14, fontweight='bold')

    time_labels = ['C1\nBaseline', 'C1\nEndpoint\n(Jan 2026)',
                   'C2\nApr 2026', 'C2\nJun 2026']
    x_pos = [0, 1, 2.5, 3.5]

    # Compute per-plate differentials at each time point
    pct_keys = [None, 'c1_pct_change',
                'c2_apr_vs_baseline_pct', 'c2_jun_vs_baseline_pct']

    outlier_plates = set(r['plate'] for r in rows if r.get('is_outlier', False))

    plate_traces = {}
    for plate in sorted(PLACEMENTS.keys()):
        diffs = []
        for j, key in enumerate(pct_keys):
            if key is None:
                diffs.append(0.0)
                continue
            ndfeb = []
            smco = []
            for slot in range(1, 5):
                sid = 'Y-%d-%d' % (plate, slot)
                row = next((r for r in rows if r['sample_id'] == sid), None)
                if not row:
                    continue
                val = row[key]
                if val is None:
                    continue
                mat = row['material']
                if mat in ('N42EH', 'N52SH'):
                    ndfeb.append(val)
                elif mat in ('SmCo33H', 'SmCo35'):
                    smco.append(val)
            if ndfeb and smco:
                diffs.append(np.mean(ndfeb) - np.mean(smco))
            else:
                diffs.append(None)
        plate_traces[plate] = diffs

    # Clean plates only
    clean_traces = {p: d for p, d in plate_traces.items()
                    if p not in outlier_plates}

    # ---- LEFT PANEL: Overall trajectory ------------------------------------
    ax = ax_left

    # Individual plate traces
    for plate, diffs in plate_traces.items():
        x_plot = [x_pos[i] for i in range(4) if diffs[i] is not None]
        y_plot = [diffs[i] for i in range(4) if diffs[i] is not None]
        is_out = plate in outlier_plates
        ax.plot(x_plot, y_plot,
                color='#888888' if not is_out else 'red',
                marker='o' if not is_out else 'x',
                alpha=0.25 if not is_out else 0.5,
                markersize=3 if not is_out else 6,
                linewidth=0.8, linestyle='-' if not is_out else ':')

    # Fleet mean
    means = []
    sems = []
    x_mean = []
    for j in range(4):
        vals = [d[j] for d in clean_traces.values() if d[j] is not None]
        if vals:
            means.append(np.mean(vals))
            sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals))
                        if len(vals) > 1 else 0.0)
            x_mean.append(x_pos[j])

    ax.errorbar(x_mean, means, yerr=sems, fmt='s-',
                color='#CC0000', linewidth=3, markersize=10,
                capsize=6, capthick=2, zorder=10,
                label='Fleet mean +/- SEM')

    # Annotate absolute values
    for xp, m, s in zip(x_mean, means, sems):
        if s > 0:
            sig = abs(m) / s
            ax.annotate('%.3f%%\n(%.1f$\\sigma$ vs 0)' % (m, sig),
                        (xp, m), textcoords='offset points',
                        xytext=(12, 10), fontsize=9, color='#CC0000',
                        fontweight='bold')

    # Phase labels between time points
    phase_info = [
        (0.5, '6 mo beam\n2.12 GeV'),
        (1.75, '3 mo off'),
        (3.0, '6 wk beam\n0.69 GeV'),
    ]
    ylim_top = ax.get_ylim()[1]
    for xp, label in phase_info:
        ax.annotate(label, (xp, 0), fontsize=8, color='#555555',
                    ha='center', va='bottom',
                    xytext=(0, 5), textcoords='offset points',
                    style='italic')

    # Vertical dashed lines separating phases
    ax.axvline(x=1.75, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(y=0, color='black', linewidth=0.8, linestyle='--', alpha=0.4)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(time_labels, fontsize=10)
    ax.set_ylabel('NdFeB - SmCo differential (% change)', fontsize=11)
    ax.set_title('Overall Trajectory', fontsize=12)
    ax.legend(fontsize=9, loc='lower left')
    ax.grid(True, alpha=0.3, axis='y')

    # ---- RIGHT PANEL: Phase-by-phase paired changes -----------------------
    ax = ax_right

    # Compute paired changes for each transition
    # Transition 0: C1 effect (baseline->endpoint, = absolute value at endpoint)
    # Transition 1: Beam-off (C1 endpoint -> C2 April)
    # Transition 2: C2 low-E (C2 April -> C2 June)

    transitions = [
        {
            'label': 'C1 beam\n(6 mo, 2.12 GeV)',
            'desc': 'Baseline to\nC1 endpoint',
            'from_idx': 0, 'to_idx': 1,
        },
        {
            'label': 'Beam-off\n(3 mo shutdown)',
            'desc': 'C1 endpoint\nto C2 April',
            'from_idx': 1, 'to_idx': 2,
        },
        {
            'label': 'C2 low-E\n(6 wk, 0.69 GeV)',
            'desc': 'C2 April\nto C2 June',
            'from_idx': 2, 'to_idx': 3,
        },
    ]

    bar_x = []
    bar_means = []
    bar_sems = []
    bar_sigs = []
    bar_labels = []
    bar_colors = []
    colors = ['#CC0000', '#888888', '#4444CC']

    for i, tr in enumerate(transitions):
        fi, ti = tr['from_idx'], tr['to_idx']
        changes = []
        for plate, diffs in clean_traces.items():
            if diffs[fi] is not None and diffs[ti] is not None:
                changes.append(diffs[ti] - diffs[fi])
        if changes:
            arr = np.array(changes)
            m = np.mean(arr)
            sem = np.std(arr, ddof=1) / np.sqrt(len(arr))
            sig = abs(m) / sem if sem > 0 else 0.0
            bar_x.append(i)
            bar_means.append(m)
            bar_sems.append(sem)
            bar_sigs.append(sig)
            bar_labels.append(tr['label'])
            bar_colors.append(colors[i])

    # Plot as points with error bars (cleaner than bars for small values)
    for i in range(len(bar_x)):
        ax.errorbar(bar_x[i], bar_means[i], yerr=bar_sems[i],
                    fmt='s', color=bar_colors[i], markersize=12,
                    capsize=8, capthick=2.5, linewidth=2.5,
                    markeredgecolor='black', markeredgewidth=0.5,
                    zorder=10)
        # Annotation
        sig_str = '%.1f$\\sigma$' % bar_sigs[i]
        ax.annotate('%+.3f%%\n$\\pm$ %.3f%%\n(%s)'
                    % (bar_means[i], bar_sems[i], sig_str),
                    (bar_x[i], bar_means[i]),
                    textcoords='offset points',
                    xytext=(45, 0), fontsize=10,
                    color=bar_colors[i], fontweight='bold',
                    ha='left', va='center',
                    arrowprops=dict(arrowstyle='->', color=bar_colors[i],
                                    alpha=0.5))

    ax.axhline(y=0, color='black', linewidth=1.2, linestyle='--', alpha=0.5)
    ax.set_xticks(bar_x)
    ax.set_xticklabels(bar_labels, fontsize=10)
    ax.set_ylabel('Paired change in differential (%)', fontsize=11)
    ax.set_title('Phase-by-Phase Changes (paired test)', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')

    # Set symmetric y-limits so zero is centered
    y_abs_max = max(abs(m) + s for m, s in zip(bar_means, bar_sems)) * 3
    ax.set_ylim(-y_abs_max, y_abs_max)
    ax.set_xlim(-0.5, len(bar_x) - 0.5 + 0.8)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print('  Saved %s' % os.path.basename(filepath))


def plot_ja4_june_vs_april(rows, filepath):
    """JA-4: June vs April corrected mWC scatter."""
    fig, ax = plt.subplots(figsize=(8, 8))

    for mat in MAT_ORDER:
        mat_rows = [r for r in rows
                    if r['material'] == mat
                    and r['c2_apr_corrected_mWC'] is not None
                    and r['c2_jun_corrected_mWC'] is not None]
        if not mat_rows:
            continue
        apr = [r['c2_apr_corrected_mWC'] for r in mat_rows]
        jun = [r['c2_jun_corrected_mWC'] for r in mat_rows]
        ax.scatter(apr, jun, color=MAT_COLORS[mat], alpha=0.7, s=40,
                   label='%s (N=%d)' % (MAT_LABELS[mat], len(mat_rows)))

    # 1:1 line
    all_vals = []
    for r in rows:
        if r['c2_apr_corrected_mWC'] is not None:
            all_vals.append(r['c2_apr_corrected_mWC'])
        if r['c2_jun_corrected_mWC'] is not None:
            all_vals.append(r['c2_jun_corrected_mWC'])
    if all_vals:
        lo = min(all_vals) - 0.01
        hi = max(all_vals) + 0.01
        ax.plot([lo, hi], [lo, hi], 'k--', alpha=0.4, linewidth=1,
                label='1:1 line')
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)

    ax.set_xlabel('C2 April corrected (mWC)', fontsize=11)
    ax.set_ylabel('C2 June corrected (mWC)', fontsize=11)
    ax.set_title('JA-4: June vs April Corrected Field\n'
                 '(instrumental consistency check)',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print('  Saved %s' % os.path.basename(filepath))


def plot_ja5_y14_tracking(cal_readings, filepath):
    """JA-5: Y-14 calibration plate tracking across all measurement dates."""
    if not cal_readings:
        print('  SKIP JA-5: no calibration readings')
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('JA-5: Y-14 Calibration Plate Tracking\n'
                 'All measurement dates (raw dashed, corrected solid)',
                 fontsize=13, fontweight='bold')

    for slot in range(1, 5):
        ax = axes[(slot - 1) // 2][(slot - 1) % 2]
        slot_data = sorted(
            [c for c in cal_readings if c['slot'] == slot],
            key=lambda x: x['datetime'])

        if not slot_data:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                    transform=ax.transAxes)
            continue

        mat = slot_data[0]['material']
        color = MAT_COLORS.get(mat, 'gray')

        x_idx = []
        raw_vals = []
        corr_vals = []
        labels = []
        temps = []

        for i, c in enumerate(slot_data):
            x_idx.append(i)
            raw_vals.append(c['raw_mWC'])
            corr_vals.append(c['corrected_mWC'])
            labels.append('%s\n%s' % (c['date'][5:], c['time'][:5]))
            temps.append(c['temp_C'])

        corr_arr = np.array(corr_vals)
        corr_mean = np.mean(corr_arr)
        corr_std = np.std(corr_arr, ddof=1) if len(corr_arr) > 1 else 0.0
        spread_pct = 100.0 * np.ptp(corr_arr) / corr_mean if len(corr_arr) > 1 else 0.0

        # Raw values connected (they track temperature)
        ax.plot(x_idx, raw_vals, 'o--', color=color, alpha=0.5,
                label='Raw', markersize=6)

        # Corrected values as scatter (NOT connected; no trend implied)
        ax.scatter(x_idx, corr_vals, marker='s', color=color, s=50,
                   zorder=5, label='Corrected')

        # Horizontal band: corrected mean +/- 1 std
        ax.axhline(y=corr_mean, color=color, linewidth=1.5, alpha=0.7,
                   linestyle='-')
        ax.axhspan(corr_mean - corr_std, corr_mean + corr_std,
                   color=color, alpha=0.12,
                   label='Mean +/- 1 std (%.3f%%)' % (100.0 * corr_std / corr_mean))

        # Temperature on secondary axis
        ax2 = ax.twinx()
        ax2.plot(x_idx, temps, 'v-', color='darkorange', alpha=0.6,
                 markersize=5, linewidth=1.2)
        ax2.set_ylabel('Temp (C)', fontsize=9, color='darkorange')
        ax2.tick_params(axis='y', labelsize=8, colors='darkorange')
        ax2.set_ylim(18, 32)
        for xi, ti in zip(x_idx, temps):
            ax2.annotate('%.0fC' % ti, (xi, ti), fontsize=6,
                         color='darkorange', ha='center',
                         xytext=(0, -12), textcoords='offset points')

        ax.set_xticks(x_idx)
        ax.set_xticklabels(labels, fontsize=7, rotation=45, ha='right')
        ax.set_ylabel('mWC')
        ax.set_title('Y-14-%d (%s)' % (slot, MAT_LABELS.get(mat, mat)),
                     fontsize=11, fontweight='bold', color=color)
        ax.legend(fontsize=7, loc='lower left')
        ax.grid(True, alpha=0.3, axis='y')

        # Annotate spread and alpha
        alpha_val = ALPHA.get(mat, -0.0004)
        if len(corr_arr) > 1:
            ax.text(0.98, 0.02,
                    'alpha = %.2f%%/C\nSpread: %.3f%%\nStd: %.3f%%'
                    % (alpha_val * 100, spread_pct,
                       100.0 * corr_std / corr_mean),
                    transform=ax.transAxes, fontsize=8,
                    ha='right', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              alpha=0.8))

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print('  Saved %s' % os.path.basename(filepath))


# ---- Verification ----------------------------------------------------------

def verify_results(rows, june_fleet, cal_readings, anomalies):
    """Run verification checks and print results."""
    print('\n' + '=' * 60)
    print('VERIFICATION CHECKS')
    print('=' * 60)
    checks_passed = 0
    checks_total = 0

    # Check 1: Y-14 June values should be present
    checks_total += 1
    y14_jun = [c for c in cal_readings if c['date'].startswith('2026-06')]
    if y14_jun:
        print('  [PASS] Y-14 has %d June calibration readings' % len(y14_jun))
        checks_passed += 1
    else:
        print('  [FAIL] Y-14 has no June calibration readings')

    # Check 2: Y-3-2 should show corrected value (~1.033), not misfile (~1.296)
    checks_total += 1
    y32 = june_fleet.get('Y-3-2')
    if y32 and abs(y32['raw_mWC'] - 1.0333) < 0.01:
        print('  [PASS] Y-3-2 raw=%.4f (correct, not misfile 1.2963)' % y32['raw_mWC'])
        checks_passed += 1
    elif y32:
        print('  [FAIL] Y-3-2 raw=%.4f (expected ~1.0333)' % y32['raw_mWC'])
    else:
        print('  [FAIL] Y-3-2 not found in June fleet')

    # Check 3: Total N should be ~120 matched samples
    checks_total += 1
    n_with_jun = sum(1 for r in rows if r['c2_jun_corrected_mWC'] is not None)
    if n_with_jun >= 115:
        print('  [PASS] %d tunnel samples with June data (expected ~120)' % n_with_jun)
        checks_passed += 1
    else:
        print('  [WARN] Only %d tunnel samples with June data' % n_with_jun)

    # Check 4: Material value ranges should be reasonable
    checks_total += 1
    reasonable = True
    for mat in MAT_ORDER:
        mat_vals = [r['c2_jun_corrected_mWC'] for r in rows
                    if r['material'] == mat
                    and r['c2_jun_corrected_mWC'] is not None]
        if mat_vals:
            lo, hi = min(mat_vals), max(mat_vals)
            if lo < 0.5 or hi > 2.0:
                print('  [WARN] %s range [%.3f, %.3f] looks unusual' % (mat, lo, hi))
                reasonable = False
    if reasonable:
        print('  [PASS] Material value ranges look reasonable')
        checks_passed += 1

    # Check 5: Y-6-2 and Y-23-1 present in June
    checks_total += 1
    y62_ok = 'Y-6-2' in june_fleet
    y231_ok = 'Y-23-1' in june_fleet
    if y62_ok and y231_ok:
        print('  [PASS] Y-6-2 and Y-23-1 both present in June (were missing/failed in April)')
        checks_passed += 1
    else:
        msg = []
        if not y62_ok:
            msg.append('Y-6-2 missing')
        if not y231_ok:
            msg.append('Y-23-1 missing')
        print('  [WARN] %s' % ', '.join(msg))

    print('\n  %d / %d checks passed' % (checks_passed, checks_total))
    return checks_passed, checks_total


# ---- Main ------------------------------------------------------------------

def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    print('C2 June Analysis')
    print('Output: %s' % ANALYSIS_DIR)
    print()

    # Load reference data
    print('Loading data...')
    materials = load_y_materials()
    c1 = load_campaign1()
    apr = load_april_c2()

    # Parse June data
    print('Parsing June Helmholtz data...')
    june_raw, anomalies = get_june_helmholtz()
    print('  Found %d Y-samples with June readings' % len(june_raw))

    print('Resolving June readings (temp correction)...')
    june_fleet, cal_readings = resolve_june_readings(june_raw, materials, anomalies)
    print('  Fleet: %d samples, Calibration: %d readings'
          % (len(june_fleet), len(cal_readings)))

    # Build timeseries
    print('Building master timeseries...')
    rows, notes = build_timeseries(c1, apr, june_fleet, materials)
    print('  %d tunnel sample rows' % len(rows))

    # Write CSV
    csv_path = os.path.join(ANALYSIS_DIR, 'c2_timeseries.csv')
    write_timeseries_csv(rows, csv_path)
    print('  Saved c2_timeseries.csv')

    # Write summary
    summary_path = os.path.join(ANALYSIS_DIR, 'june_analysis_summary.txt')
    write_summary(rows, cal_readings, anomalies, notes, summary_path)
    print('  Saved june_analysis_summary.txt')

    # Plots
    print('\nGenerating plots...')
    plot_ja1_timeseries(rows,
                        os.path.join(ANALYSIS_DIR, 'JA1_timeseries.png'))
    plot_ja2_c2_progression(rows,
                            os.path.join(ANALYSIS_DIR, 'JA2_c2_progression.png'))
    plot_ja3_differential_tracking(rows,
                                   os.path.join(ANALYSIS_DIR, 'JA3_differential_tracking.png'))
    plot_ja4_june_vs_april(rows,
                           os.path.join(ANALYSIS_DIR, 'JA4_june_vs_april.png'))
    plot_ja5_y14_tracking(cal_readings,
                          os.path.join(ANALYSIS_DIR, 'JA5_y14_tracking.png'))

    # Verification
    verify_results(rows, june_fleet, cal_readings, anomalies)

    print('\nDone.')


if __name__ == '__main__':
    main()
