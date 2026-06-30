#!/usr/bin/env python3
"""
Campaign 2 - June 2-3, 2026 Data Quality Check
Checks Helmholtz and Teslameter data from the June measurement days.

Sections:
  1. Data Inventory: file counts, plate coverage, date verification
  2. Y-14 Calibration: repeatability across all time points
  3. Slot Completeness: 4 slots per plate, flag missing/extra
  4. Value Range Check: flag outliers, compare to C1 and April C2
  5. Temperature Survey: Teslameter temps on June 2-3
  6. Timestamp Analysis: measurement order, session duration
  7. Cross-Check: June values vs April 20 values (C2 internal consistency)
  8. Data Anomalies: unusual filenames, parse failures, suspicious values

Output: 2026_Data_Run/Analysis/June_QC/
"""

import os
import re
import sys
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import defaultdict
import openpyxl

# ---- Paths & Constants -------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE)
OUT_DIR = os.path.join(BASE, 'Analysis', 'June_QC')
os.makedirs(OUT_DIR, exist_ok=True)

# June data folders
HELM_JUN2 = os.path.join(BASE, '202662Helmholtz')
HELM_JUN3 = os.path.join(BASE, '2026-6-3-Helmholtz')
TESLA_JUN2 = os.path.join(BASE, '2026-06-02_Teslameter')
TESLA_JUN3 = os.path.join(BASE, '2026-06-03_Teslameter')

# April data (for comparison)
HELM_APR = os.path.join(BASE, '20260420_Helmholtz')
TESLA_APR = os.path.join(BASE, '2026-04-20_Teslameter')

# Campaign 1 reference
C1_CSV = os.path.join(PROJECT_DIR, 'Data_Package', '02_Magnetic_Measurements',
                       'y_plate_degradation.csv')
SPREADSHEET = os.path.join(PROJECT_DIR, 'Materials_Arrangements_Spreadsheet.xlsx')

T_REF = 20.0
SENTINEL = 1337
ALPHA = {
    'N42EH': -0.0010, 'N52SH': -0.0011,
    'SmCo33H': -0.0004, 'SmCo35': -0.0004,
}
LAB_PLATES = {8, 14, 27, 28, 29, 31, 33, 35, 37}
TUNNEL_PLATES = set(range(1, 41)) - {2} - LAB_PLATES
CALIBRATION_PLATE = 14

# Expected sites per day
EXPECTED_JUNE2_SITES = 22
EXPECTED_JUNE3_SITES = 8


# ---- Parsers -----------------------------------------------------------------

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


# ---- Data Loaders ------------------------------------------------------------

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


def load_campaign1_reference():
    """Load Campaign 1 per-sample values."""
    c1 = {}
    if not os.path.exists(C1_CSV):
        print("WARNING: C1 reference CSV not found: %s" % C1_CSV)
        return c1
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
            }
    return c1


def extract_date_entries(helm_dir, target_dates):
    """
    From a Helmholtz folder, extract all Y-plate entries on target_dates.
    Returns: dict keyed by date_str -> {plate_num: [(slot, datetime, val, unit), ...]}
    Also returns: list of anomaly strings
    """
    data = {d: defaultdict(list) for d in target_dates}
    anomalies = []
    non_standard = []

    for fn in sorted(os.listdir(helm_dir)):
        if not fn.endswith('_helmholtz.dat'):
            continue
        if 'Temp' in fn:
            continue

        m = re.match(r'Y-(\d+)-(\d+)_helmholtz\.dat$', fn)
        if not m:
            if fn.startswith('Y-') or fn.startswith('Y_') or fn.startswith('y-'):
                non_standard.append(fn)
            continue

        plate, slot = int(m.group(1)), int(m.group(2))
        filepath = os.path.join(helm_dir, fn)
        try:
            rows = parse_helmholtz_file(filepath)
        except Exception as e:
            anomalies.append("PARSE FAILURE: %s: %s" % (fn, e))
            continue

        if not rows:
            anomalies.append("EMPTY FILE: %s" % fn)
            continue

        for dt, val, unit in rows:
            ds = dt.strftime('%Y-%m-%d')
            if ds in target_dates:
                data[ds][plate].append((slot, dt, val, unit))

    for fn in non_standard:
        anomalies.append("NON-STANDARD FILENAME: %s" % fn)

    return data, anomalies


def extract_teslameter_temps(tesla_dir, target_dates):
    """
    From a Teslameter folder, extract Y-plate temperatures on target_dates.
    Returns: dict keyed by date_str -> {plate_num: [(slot, datetime, temp), ...]}
    """
    data = {d: defaultdict(list) for d in target_dates}

    for fn in sorted(os.listdir(tesla_dir)):
        m = re.match(r'Y-(\d+)-(\d+)_(front|side|top)\.dat$', fn)
        if not m:
            continue
        plate, slot = int(m.group(1)), int(m.group(2))
        filepath = os.path.join(tesla_dir, fn)
        try:
            rows = parse_teslameter_file(filepath)
        except:
            continue
        for dt, bvals, temp in rows:
            ds = dt.strftime('%Y-%m-%d')
            if ds in target_dates:
                data[ds][plate].append((slot, dt, temp))

    return data


# ---- Main Analysis -----------------------------------------------------------

def main():
    log = []
    def P(s=''):
        print(s)
        log.append(s)

    P("=" * 72)
    P("CAMPAIGN 2 — JUNE 2-3, 2026 DATA QUALITY CHECK")
    P("=" * 72)
    P()

    materials = load_y_materials()
    c1_ref = load_campaign1_reference()

    target_dates = ['2026-06-01', '2026-06-02', '2026-06-03']

    # Use June 3 folder as primary (most complete, contains all cumulative data)
    P("Using June 3 Helmholtz folder as primary source (cumulative files)")
    P("Cross-checking against June 2 folder for consistency")
    P()

    # Extract data from June 3 folder (most complete)
    helm_data, anomalies = extract_date_entries(HELM_JUN3, target_dates)
    # Also extract from June 2 folder to cross-check
    helm_data_jun2, anomalies_jun2 = extract_date_entries(HELM_JUN2,
                                                          ['2026-06-01', '2026-06-02'])

    # Extract teslameter data
    tesla_data_jun2 = extract_teslameter_temps(TESLA_JUN2, ['2026-06-01', '2026-06-02'])
    tesla_data_jun3 = extract_teslameter_temps(TESLA_JUN3, target_dates)

    # Also extract April 20 data for comparison (from June 3 folder, which has cumulative files)
    apr_data, _ = extract_date_entries(HELM_JUN3, ['2026-04-20'])
    tesla_apr = extract_teslameter_temps(TESLA_JUN2, ['2026-04-20'])

    # ===================================================================
    # SECTION 1: DATA INVENTORY
    # ===================================================================
    P("=" * 72)
    P("SECTION 1: DATA INVENTORY")
    P("=" * 72)
    P()

    for date in target_dates:
        plates = helm_data[date]
        n_plates = len(plates)
        n_entries = sum(len(v) for v in plates.values())
        plate_list = sorted(plates.keys())

        P("  %s: %d unique plates, %d slot readings" % (date, n_plates, n_entries))
        P("    Plates: %s" % plate_list)

        # Classify plates
        tunnel_on_day = [p for p in plate_list if p in TUNNEL_PLATES]
        lab_on_day = [p for p in plate_list if p in LAB_PLATES]
        if tunnel_on_day:
            P("    Tunnel plates: %s (%d)" % (sorted(tunnel_on_day), len(tunnel_on_day)))
        if lab_on_day:
            P("    Lab/Cal plates: %s (%d)" % (sorted(lab_on_day), len(lab_on_day)))
        P()

    # Check site counts
    jun2_tunnel = [p for p in helm_data['2026-06-02'].keys() if p in TUNNEL_PLATES]
    jun3_tunnel = [p for p in helm_data['2026-06-03'].keys() if p in TUNNEL_PLATES]
    P("  June 2 tunnel sites: %d (expected %d)" % (len(jun2_tunnel), EXPECTED_JUNE2_SITES))
    P("  June 3 tunnel sites: %d (expected %d)" % (len(jun3_tunnel), EXPECTED_JUNE3_SITES))
    P("  Combined: %d unique tunnel plates" % len(set(jun2_tunnel + jun3_tunnel)))
    missing = TUNNEL_PLATES - set(jun2_tunnel) - set(jun3_tunnel)
    if missing:
        P("  WARNING: Missing tunnel plates: %s" % sorted(missing))
    else:
        P("  OK: All 30 tunnel plates accounted for")
    P()

    # June 1 check
    if helm_data['2026-06-01']:
        P("  NOTE: June 1 data found (day before campaign):")
        for plate, entries in sorted(helm_data['2026-06-01'].items()):
            slots = sorted(set(s for s, _, _, _ in entries))
            times = [dt.strftime('%H:%M:%S') for _, dt, _, _ in sorted(entries, key=lambda x: x[1])]
            P("    Y-%d: slots %s, times %s" % (plate, slots, times))
        P()

    # Non-standard files
    if anomalies:
        P("  DATA ANOMALIES:")
        for a in anomalies:
            P("    %s" % a)
        P()

    # ===================================================================
    # SECTION 2: CROSS-CHECK JUNE 2 vs JUNE 3 FOLDERS
    # ===================================================================
    P("=" * 72)
    P("SECTION 2: CROSS-CHECK BETWEEN FOLDERS")
    P("=" * 72)
    P()
    P("  June 2 folder should contain data up to June 2.")
    P("  June 3 folder should contain data up to June 3.")
    P()

    # Check if June 2 folder has June 3 data (shouldn't)
    jun3_in_jun2_folder, _ = extract_date_entries(HELM_JUN2, ['2026-06-03'])
    if jun3_in_jun2_folder['2026-06-03']:
        P("  WARNING: June 2 folder contains June 3 data!")
        for plate in sorted(jun3_in_jun2_folder['2026-06-03'].keys()):
            P("    Y-%d" % plate)
    else:
        P("  OK: June 2 folder has no June 3 data")

    # Cross-check June 2 data matches between folders
    mismatches = 0
    checked = 0
    for plate in helm_data['2026-06-02']:
        entries_jun3_folder = sorted(helm_data['2026-06-02'][plate],
                                     key=lambda x: (x[0], x[1]))
        entries_jun2_folder = sorted(helm_data_jun2.get('2026-06-02', {}).get(plate, []),
                                     key=lambda x: (x[0], x[1]))
        for e3, e2 in zip(entries_jun3_folder, entries_jun2_folder):
            checked += 1
            if abs(e3[2] - e2[2]) > 0.0001:
                mismatches += 1
                P("  MISMATCH: Y-%d-%d: Jun3_folder=%.4f, Jun2_folder=%.4f" %
                  (plate, e3[0], e3[2], e2[2]))
    P("  Cross-checked %d readings: %d mismatches" % (checked, mismatches))
    P()

    # ===================================================================
    # SECTION 3: SLOT COMPLETENESS
    # ===================================================================
    P("=" * 72)
    P("SECTION 3: SLOT COMPLETENESS")
    P("=" * 72)
    P()

    for date in ['2026-06-02', '2026-06-03']:
        P("  --- %s ---" % date)
        plates = helm_data[date]
        for plate_num in sorted(plates.keys()):
            entries = plates[plate_num]
            slots_present = sorted(set(s for s, _, _, _ in entries))

            if plate_num == CALIBRATION_PLATE:
                # Calibration: count readings per slot
                n_readings = len(entries) // max(len(slots_present), 1)
                if date == '2026-06-02':
                    expected_readings = 1
                    expected_msg = "beginning only"
                else:
                    expected_readings = 3
                    expected_msg = "beginning, middle, end"
                P("    Y-14 (calibration): slots %s, %d total readings (%s)"
                  % (slots_present, len(entries), expected_msg))
                if len(slots_present) != 4:
                    P("      WARNING: Expected 4 slots, found %d" % len(slots_present))
                if date == '2026-06-02' and len(entries) != 4:
                    P("      WARNING: Expected 4 entries (1 per slot), found %d" % len(entries))
                elif date == '2026-06-03' and len(entries) != 12:
                    P("      WARNING: Expected 12 entries (3 per slot), found %d" % len(entries))
            else:
                if len(slots_present) != 4:
                    P("    Y-%d: MISSING SLOTS! Have %s (expected [1,2,3,4])"
                      % (plate_num, slots_present))
                elif len(entries) != 4:
                    P("    Y-%d: slots %s OK but %d entries (expected 4)"
                      % (plate_num, slots_present, len(entries)))

                # Check for duplicate readings (same slot, same day, but different times)
                slot_counts = defaultdict(int)
                for s, _, _, _ in entries:
                    slot_counts[s] += 1
                for s, c in sorted(slot_counts.items()):
                    if c > 1:
                        vals = [(dt.strftime('%H:%M:%S'), v) for ss, dt, v, _ in entries if ss == s]
                        P("    Y-%d-%d: DUPLICATE (%d readings): %s"
                          % (plate_num, s, c, vals))
        P()

    # ===================================================================
    # SECTION 4: VALUE RANGE CHECK
    # ===================================================================
    P("=" * 72)
    P("SECTION 4: VALUE RANGE & SANITY CHECK")
    P("=" * 72)
    P()

    # Collect all June measurements into a flat structure
    june_measurements = {}  # (plate, slot) -> {date: val}
    for date in ['2026-06-02', '2026-06-03']:
        for plate_num, entries in helm_data[date].items():
            if plate_num == CALIBRATION_PLATE and date == '2026-06-03':
                # Use first reading for comparison
                for slot in [1, 2, 3, 4]:
                    slot_entries = [(s, dt, v, u) for s, dt, v, u in entries if s == slot]
                    if slot_entries:
                        slot_entries.sort(key=lambda x: x[1])
                        first = slot_entries[0]
                        key = (plate_num, slot)
                        if key not in june_measurements:
                            june_measurements[key] = {}
                        june_measurements[key][date] = first[2]
            elif plate_num == CALIBRATION_PLATE and date == '2026-06-02':
                for s, dt, v, u in entries:
                    key = (plate_num, s)
                    if key not in june_measurements:
                        june_measurements[key] = {}
                    june_measurements[key][date] = v
            else:
                for s, dt, v, u in entries:
                    key = (plate_num, s)
                    if key not in june_measurements:
                        june_measurements[key] = {}
                    june_measurements[key][date] = v

    # Collect April measurements for comparison
    apr_measurements = {}
    for plate_num, entries in apr_data.get('2026-04-20', {}).items():
        for s, dt, v, u in entries:
            key = (plate_num, s)
            if key not in apr_measurements:
                apr_measurements[key] = []
            apr_measurements[key].append(v)

    # Compare June vs April and C1
    P("  --- Value comparison: June vs April 20 (C2 internal) ---")
    P("  %-10s %-8s %-10s %-10s %-10s %-10s %-10s" %
      ("Sample", "Material", "C1_last", "Apr20", "June", "Jun-Apr%", "Jun-C1%"))
    P("  " + "-" * 72)

    big_changes = []
    for plate_num in sorted(set(p for p, s in june_measurements.keys())):
        for slot in [1, 2, 3, 4]:
            key = (plate_num, slot)
            sid = "Y-%d-%d" % (plate_num, slot)
            mat = materials.get(sid, '???')

            # Get June value
            june_vals = june_measurements.get(key, {})
            if not june_vals:
                continue
            # Use whichever date this sample was measured on
            june_date = sorted(june_vals.keys())[-1]
            june_val = june_vals[june_date]

            # Get April value
            apr_vals = apr_measurements.get(key, [])
            apr_val = None
            if apr_vals:
                # For most plates, just use first reading; for Y-14, use corresponding time
                apr_val = apr_vals[0]

            # Get C1 value
            c1_val = None
            if sid in c1_ref:
                c1_val = c1_ref[sid]['latest_mWC']

            # Compute changes
            jun_apr_pct = None
            jun_c1_pct = None
            if apr_val and apr_val > 0.1:
                jun_apr_pct = (june_val - apr_val) / apr_val * 100
            if c1_val and c1_val > 0.1:
                jun_c1_pct = (june_val - c1_val) / c1_val * 100

            # Flag suspicious values
            flags = []
            if june_val < 0.1:
                flags.append("LOW VALUE")
            if june_val == SENTINEL:
                flags.append("SENTINEL")
            if jun_apr_pct is not None and abs(jun_apr_pct) > 1.0:
                flags.append("BIG CHANGE vs Apr (%.2f%%)" % jun_apr_pct)
            if jun_c1_pct is not None and abs(jun_c1_pct) > 2.0:
                flags.append("BIG CHANGE vs C1 (%.2f%%)" % jun_c1_pct)

            # Check unit consistency
            for date, plate_entries in helm_data.items():
                if plate_num in plate_entries:
                    for s, dt, v, u in plate_entries[plate_num]:
                        if s == slot and u != 'mWC':
                            flags.append("WRONG UNIT: %s" % u)

            if flags:
                P("  %-10s %-8s %-10s %-10s %-10s %-10s %-10s  << %s" %
                  (sid, mat,
                   "%.4f" % c1_val if c1_val else "N/A",
                   "%.4f" % apr_val if apr_val else "N/A",
                   "%.4f" % june_val,
                   "%.3f%%" % jun_apr_pct if jun_apr_pct is not None else "N/A",
                   "%.3f%%" % jun_c1_pct if jun_c1_pct is not None else "N/A",
                   "; ".join(flags)))
                big_changes.append((sid, flags))

    if not big_changes:
        P("  No anomalous values found.")
    P()

    # Overall range check
    P("  --- June value ranges by material ---")
    mat_vals = defaultdict(list)
    for (plate, slot), date_vals in june_measurements.items():
        sid = "Y-%d-%d" % (plate, slot)
        mat = materials.get(sid, '???')
        for v in date_vals.values():
            mat_vals[mat].append(v)

    for mat in sorted(mat_vals.keys()):
        vals = mat_vals[mat]
        P("    %s: N=%d, range=[%.4f, %.4f], mean=%.4f, std=%.4f" %
          (mat, len(vals), min(vals), max(vals), np.mean(vals), np.std(vals)))
    P()

    # ===================================================================
    # SECTION 5: Y-14 CALIBRATION ANALYSIS
    # ===================================================================
    P("=" * 72)
    P("SECTION 5: Y-14 CALIBRATION PLATE")
    P("=" * 72)
    P()

    P("  Y-14 is the calibration plate (no dosimetry). It should be stable.")
    P("  June 1: tested once (pre-campaign)")
    P("  June 2: read at beginning of day only")
    P("  June 3: read beginning, middle, and end of short day")
    P()

    # Collect all Y-14 readings across all dates (including April)
    y14_readings = defaultdict(list)  # slot -> [(date, time, val)]

    for date in target_dates + ['2026-04-20']:
        source = helm_data if date in target_dates else apr_data
        entries = source.get(date, {}).get(14, [])
        for s, dt, v, u in entries:
            y14_readings[s].append((dt, v))

    P("  Y-14 all readings (raw mWC):")
    P("  %-12s %-10s %-10s %-10s %-10s %-10s" %
      ("Date", "Time", "Slot-1", "Slot-2", "Slot-3", "Slot-4"))
    P("  " + "-" * 64)

    # Group by timestamp
    all_y14_times = set()
    for s in [1, 2, 3, 4]:
        for dt, v in y14_readings[s]:
            all_y14_times.add(dt)

    for dt in sorted(all_y14_times):
        row = [dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M:%S')]
        for s in [1, 2, 3, 4]:
            val = None
            for ddt, v in y14_readings[s]:
                if abs((ddt - dt).total_seconds()) < 120:  # within 2 min
                    val = v
                    break
            row.append("%.4f" % val if val else "  ---")
        P("  %-12s %-10s %-10s %-10s %-10s %-10s" % tuple(row))

    # Repeatability stats
    P()
    P("  Y-14 per-slot statistics (all available readings):")
    for s in [1, 2, 3, 4]:
        vals = [v for _, v in y14_readings[s]]
        if len(vals) >= 2:
            P("    Slot %d: N=%d, mean=%.4f, std=%.4f, range=%.4f, CV=%.3f%%" %
              (s, len(vals), np.mean(vals), np.std(vals),
               max(vals) - min(vals), np.std(vals) / np.mean(vals) * 100))

    # June 3 within-day repeatability
    P()
    P("  Y-14 June 3 within-day repeatability:")
    for s in [1, 2, 3, 4]:
        jun3_vals = [v for dt, v in y14_readings[s]
                     if dt.strftime('%Y-%m-%d') == '2026-06-03']
        if len(jun3_vals) >= 2:
            P("    Slot %d: readings=%s, range=%.4f mWC (%.3f%%)" %
              (s, ['%.4f' % v for v in jun3_vals],
               max(jun3_vals) - min(jun3_vals),
               (max(jun3_vals) - min(jun3_vals)) / np.mean(jun3_vals) * 100))
    P()

    # ===================================================================
    # SECTION 6: TEMPERATURE SURVEY
    # ===================================================================
    P("=" * 72)
    P("SECTION 6: TEMPERATURE SURVEY")
    P("=" * 72)
    P()

    all_temps = {}  # date -> list of (time, temp, plate)
    for date_str, tesla_data in [('2026-06-02', tesla_data_jun2),
                                  ('2026-06-03', tesla_data_jun3)]:
        temps_on_day = []
        for date_key in [date_str]:
            if date_key in tesla_data:
                for plate, entries in tesla_data[date_key].items():
                    for s, dt, temp in entries:
                        if dt.strftime('%Y-%m-%d') == date_str:
                            temps_on_day.append((dt, temp, plate))
        all_temps[date_str] = sorted(temps_on_day)

        if temps_on_day:
            temp_vals = [t for _, t, _ in temps_on_day]
            times = [dt for dt, _, _ in temps_on_day]
            P("  %s: N=%d readings, T range=[%.1f, %.1f] C, mean=%.1f C" %
              (date_str, len(temp_vals), min(temp_vals), max(temp_vals),
               np.mean(temp_vals)))
            P("    Time span: %s to %s" %
              (min(times).strftime('%H:%M'), max(times).strftime('%H:%M')))
        else:
            P("  %s: No temperature data found!" % date_str)
    P()

    # ===================================================================
    # SECTION 7: TIMESTAMP ANALYSIS
    # ===================================================================
    P("=" * 72)
    P("SECTION 7: TIMESTAMP / MEASUREMENT ORDER")
    P("=" * 72)
    P()

    for date in ['2026-06-02', '2026-06-03']:
        P("  --- %s ---" % date)
        plates = helm_data[date]
        plate_times = []
        for plate_num in sorted(plates.keys()):
            if plate_num == CALIBRATION_PLATE:
                continue
            entries = plates[plate_num]
            times = [dt for _, dt, _, _ in entries]
            if times:
                median_t = sorted(times)[len(times) // 2]
                plate_times.append((median_t, plate_num))

        plate_times.sort()
        P("  Measurement order (by median timestamp):")
        for i, (mt, pn) in enumerate(plate_times):
            P("    %2d. Y-%-3d at %s" % (i + 1, pn, mt.strftime('%H:%M:%S')))

        if len(plate_times) >= 2:
            total_duration = (plate_times[-1][0] - plate_times[0][0]).total_seconds() / 60
            P("  Session duration: %.0f minutes (%.1f hours)" %
              (total_duration, total_duration / 60))
        P()

    # ===================================================================
    # SECTION 8: C2 INTERNAL CONSISTENCY (June vs April)
    # ===================================================================
    P("=" * 72)
    P("SECTION 8: C2 INTERNAL CONSISTENCY (June vs April 20)")
    P("=" * 72)
    P()
    P("  Comparing June readings to April 20 (same campaign, ~6 weeks apart).")
    P("  Small changes expected (ongoing irradiation + instrumental).")
    P()

    jun_apr_diffs = []
    P("  %-10s %-8s %-10s %-10s %-8s" %
      ("Sample", "Material", "Apr20", "June", "Delta%"))
    P("  " + "-" * 50)

    for plate_num in sorted(set(p for p, s in june_measurements.keys())):
        for slot in [1, 2, 3, 4]:
            key = (plate_num, slot)
            sid = "Y-%d-%d" % (plate_num, slot)
            mat = materials.get(sid, '???')

            june_vals = june_measurements.get(key, {})
            apr_vals = apr_measurements.get(key, [])

            if not june_vals or not apr_vals:
                continue

            june_date = sorted(june_vals.keys())[-1]
            june_val = june_vals[june_date]
            apr_val = apr_vals[0]  # first reading on April 20

            if apr_val < 0.1:
                continue

            delta_pct = (june_val - apr_val) / apr_val * 100
            jun_apr_diffs.append((sid, mat, delta_pct))

            # Only print if notable
            if abs(delta_pct) > 0.5:
                P("  %-10s %-8s %-10.4f %-10.4f %+.3f%%  << NOTABLE" %
                  (sid, mat, apr_val, june_val, delta_pct))

    if jun_apr_diffs:
        diffs_arr = np.array([d for _, _, d in jun_apr_diffs])
        P()
        P("  Overall June-April statistics (N=%d):" % len(diffs_arr))
        P("    Mean: %+.4f%%" % np.mean(diffs_arr))
        P("    Std:  %.4f%%" % np.std(diffs_arr))
        P("    Min:  %+.4f%%  Max: %+.4f%%" % (np.min(diffs_arr), np.max(diffs_arr)))

        # By material
        P()
        P("  By material:")
        for mat in sorted(set(m for _, m, _ in jun_apr_diffs)):
            mat_diffs = [d for _, m, d in jun_apr_diffs if m == mat]
            P("    %s: N=%d, mean=%+.4f%%, std=%.4f%%" %
              (mat, len(mat_diffs), np.mean(mat_diffs), np.std(mat_diffs)))
    P()

    # ===================================================================
    # SECTION 9: DETAILED ANOMALY SCAN
    # ===================================================================
    P("=" * 72)
    P("SECTION 9: DETAILED ANOMALY SCAN")
    P("=" * 72)
    P()

    # Check for values outside expected ranges
    P("  Checking for values outside material-typical ranges...")
    range_flags = []
    for date in ['2026-06-02', '2026-06-03']:
        for plate_num, entries in helm_data[date].items():
            for s, dt, v, u in entries:
                sid = "Y-%d-%d" % (plate_num, s)
                mat = materials.get(sid, '???')
                # NdFeB typically 0.9-1.35 mWC, SmCo typically 0.75-1.05 mWC
                if 'SmCo' in mat:
                    if v < 0.5 or v > 1.3:
                        range_flags.append((sid, mat, date, v, "SmCo out of range"))
                elif 'N' in mat and mat in ALPHA:
                    if v < 0.8 or v > 1.5:
                        range_flags.append((sid, mat, date, v, "NdFeB out of range"))
                if v == SENTINEL:
                    range_flags.append((sid, mat, date, v, "SENTINEL 1337"))

    if range_flags:
        for sid, mat, date, v, reason in range_flags:
            P("    FLAG: %s (%s) on %s: %.4f mWC - %s" % (sid, mat, date, v, reason))
    else:
        P("    No out-of-range values found.")
    P()

    # Check for potential slot swaps (value doesn't match expected material)
    P("  Checking for potential slot swaps (NdFeB in SmCo range or vice versa)...")
    swap_flags = []
    for date in ['2026-06-02', '2026-06-03']:
        for plate_num, entries in helm_data[date].items():
            plate_vals = {}
            for s, dt, v, u in entries:
                plate_vals[s] = v

            if len(plate_vals) != 4:
                continue

            for s, v in plate_vals.items():
                sid = "Y-%d-%d" % (plate_num, s)
                mat = materials.get(sid, '???')
                other_vals = {s2: v2 for s2, v2 in plate_vals.items() if s2 != s}

                # Check if this slot's value is very different from expected pattern
                # NdFeB > SmCo generally
                if 'SmCo' in mat and v > 1.15:
                    swap_flags.append(
                        "%s (%s): %.4f mWC - unusually high for SmCo" % (sid, mat, v))
                elif mat in ['N42EH', 'N52SH'] and v < 0.85:
                    swap_flags.append(
                        "%s (%s): %.4f mWC - unusually low for NdFeB" % (sid, mat, v))

    if swap_flags:
        for f in swap_flags:
            P("    FLAG: %s" % f)
    else:
        P("    No potential slot swaps detected.")
    P()

    # Check for duplicate/extra entries in non-calibration plates
    P("  Checking for duplicate entries on non-calibration plates...")
    dup_found = False
    for date in ['2026-06-02', '2026-06-03']:
        for plate_num, entries in helm_data[date].items():
            if plate_num == CALIBRATION_PLATE:
                continue
            slot_counts = defaultdict(int)
            for s, _, _, _ in entries:
                slot_counts[s] += 1
            for s, c in slot_counts.items():
                if c > 1:
                    dup_found = True
                    vals = [(dt.strftime('%H:%M:%S'), v)
                            for ss, dt, v, _ in entries if ss == s]
                    P("    DUPLICATE: Y-%d-%d on %s: %d readings: %s" %
                      (plate_num, s, date, c, vals))
    if not dup_found:
        P("    No duplicates found on non-calibration plates.")
    P()

    # Check the Y-Plate-1 file
    P("  Checking non-standard file: Y-Plate-1_helmholtz.dat")
    for folder, name in [(HELM_JUN2, 'Jun2'), (HELM_JUN3, 'Jun3')]:
        fp = os.path.join(folder, 'Y-Plate-1_helmholtz.dat')
        if os.path.exists(fp):
            try:
                rows = parse_helmholtz_file(fp)
                if rows:
                    P("    %s folder: %d entries" % (name, len(rows)))
                    for dt, v, u in rows:
                        P("      %s: %.4f %s" % (dt.strftime('%Y-%m-%d %H:%M:%S'), v, u))
                else:
                    P("    %s folder: file exists but no parseable entries" % name)
            except:
                P("    %s folder: parse error" % name)
    P()

    # ===================================================================
    # SUMMARY
    # ===================================================================
    P("=" * 72)
    P("SUMMARY")
    P("=" * 72)
    P()

    n_jun2 = len([p for p in helm_data['2026-06-02'] if p != CALIBRATION_PLATE])
    n_jun3 = len([p for p in helm_data['2026-06-03'] if p != CALIBRATION_PLATE])
    P("  Plates measured: %d on June 2, %d on June 3, %d total"
      % (n_jun2, n_jun3, n_jun2 + n_jun3))
    P("  Y-14 calibration: 1 reading on June 2, 3 readings on June 3")
    P("  All 30 tunnel plates: %s" %
      ("COMPLETE" if not missing else "INCOMPLETE - missing %s" % sorted(missing)))
    P()

    issues = []
    if anomalies:
        issues.extend(anomalies)
    if big_changes:
        issues.extend(["%s: %s" % (s, "; ".join(f)) for s, f in big_changes])
    if range_flags:
        issues.extend(["%s (%s): %s" % (s, m, r) for s, m, _, _, r in range_flags])
    if swap_flags:
        issues.extend(swap_flags)

    if issues:
        P("  ISSUES TO REVIEW:")
        for i, issue in enumerate(issues, 1):
            P("    %d. %s" % (i, issue))
    else:
        P("  No issues found. Data looks clean.")
    P()

    # Save log
    log_path = os.path.join(OUT_DIR, 'june_qc_summary.txt')
    with open(log_path, 'w') as f:
        f.write('\n'.join(log))
    print("\nSaved summary to: %s" % log_path)


if __name__ == '__main__':
    main()
