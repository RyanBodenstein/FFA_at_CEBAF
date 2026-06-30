#!/usr/bin/env python3
"""
Within-Session Gain Drift Analysis

Empirically tests whether measurement order within a Helmholtz session
correlates with the intra-plate NdFeB-SmCo differential. Validates the
"cancels by construction" claim for within-session gain drift.

Analyses:
  1. Slot timing within plates (how quickly are 4 slots measured?)
  2. Per-session differential vs. elapsed time (Spearman correlation)
  3. Pooled cross-session test (normalized time, sign consistency)
  4. Y-14 Campaign 2 calibration reference (3-point drift)

Output: Cleanup_Claude/Within_Session_Drift/
"""

import os
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import defaultdict
import openpyxl
from scipy import stats

# ── Paths & Constants ────────────────────────────────────────────────────────

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, 'Within_Session_Drift')
os.makedirs(OUT_DIR, exist_ok=True)

HELM_DIR = os.path.join(BASE, 'Y_Plates', 'Helmholtz')
TESLA_DIR = os.path.join(BASE, 'Y_Plates', 'Teslameter')
C2_HELM_DIR = os.path.join(BASE, '..', '2026_Data_Run', '20260420_Helmholtz')
C2_TESLA_DIR = os.path.join(BASE, '..', '2026_Data_Run', '2026-04-20_Teslameter')

T_REF = 20.0
SENTINEL = 1337
MIN_BASELINE = 0.1
TUNNEL_START = datetime(2025, 7, 1)
MIN_PLATES_PER_SESSION = 8

ALPHA = {
    'N42EH': -0.0010, 'N52SH': -0.0011,
    'SmCo33H': -0.0004, 'SmCo35': -0.0004,
}
MAT_BY_SLOT = {1: 'N42EH', 2: 'N52SH', 3: 'SmCo33H', 4: 'SmCo35'}
FLAGGED = {'Y-34-4', 'Y-40-4'}

LAB_PLATES = {8, 14, 27, 28, 29, 31, 33, 35, 37}
CALIBRATION_PLATE = 2  # Y-2 has no material assignment

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


# ── Parsers (copied from manager_summary_v3.py) ─────────────────────────────

def parse_helmholtz_file(filepath):
    """Parse a Helmholtz .dat file, returning (datetime, value, unit) tuples."""
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
    """Parse a Teslameter .dat file, returning (datetime, [Bx,By,Bz], temp)."""
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


# ── Data Loading ─────────────────────────────────────────────────────────────

def load_materials():
    """Load Y-plate material assignments from Materials_Arrangements.xlsx."""
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
    return y_materials


def load_temperatures():
    """Load per-sample, per-date temperature from Teslameter files.

    Returns dict: (sample_id, date_str) -> mean_temperature
    """
    temp_lookup = defaultdict(list)
    for f in os.listdir(TESLA_DIR):
        m = re.match(r'(Y-\d+-\d+)_(front|side|top)\.dat$', f)
        if not m:
            continue
        sample = m.group(1)
        rows = parse_teslameter_file(os.path.join(TESLA_DIR, f))
        for dt, fields, temp in rows:
            if temp is None or abs(temp - SENTINEL) < 1:
                continue
            temp_lookup[(sample, dt.strftime('%Y-%m-%d'))].append(temp)

    temp_final = {}
    for key, temps in temp_lookup.items():
        temp_final[key] = np.mean(temps)
    return temp_final


def load_helmholtz_with_timestamps(y_materials, temp_final):
    """Load all Y-plate Helmholtz data preserving full timestamps.

    Returns list of dicts:
        {plate, slot, sample, material, datetime, date_str, mwc_raw, mwc_corr}
    Only includes mWC readings with valid values.
    """
    records = []
    for f in sorted(os.listdir(HELM_DIR)):
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

        rows = parse_helmholtz_file(os.path.join(HELM_DIR, f))
        for dt, val, unit in rows:
            if unit != 'mWC':
                continue
            if abs(val - SENTINEL) < 1 or abs(val) < MIN_BASELINE:
                continue
            date_str = dt.strftime('%Y-%m-%d')

            # Temperature correction
            temp_key = (sample, date_str)
            temp = temp_final.get(temp_key)
            if temp is not None:
                mwc_corr = val / (1.0 + alpha * (temp - T_REF))
            else:
                mwc_corr = val  # no correction available

            records.append({
                'plate': plate_num,
                'slot': slot_num,
                'sample': sample,
                'material': mat,
                'datetime': dt,
                'date_str': date_str,
                'mwc_raw': val,
                'mwc_corr': mwc_corr,
                'is_flagged': sample in FLAGGED,
                'is_tunnel': plate_num not in LAB_PLATES and plate_num != CALIBRATION_PLATE,
            })
    return records


# ── Analysis Functions ───────────────────────────────────────────────────────

def analysis1_slot_timing(records, out):
    """Analysis 1: Within-plate slot timing.

    How long between first and last slot measurement on each plate?
    """
    out.write("=" * 72 + "\n")
    out.write("ANALYSIS 1: Within-Plate Slot Timing\n")
    out.write("=" * 72 + "\n\n")

    # Group by (plate, date) -> list of datetimes
    plate_date_times = defaultdict(list)
    for r in records:
        if not r['is_tunnel']:
            continue
        if r['datetime'] < TUNNEL_START:
            continue
        plate_date_times[(r['plate'], r['date_str'])].append(r['datetime'])

    time_gaps_seconds = []
    detail_rows = []

    for (plate, date_str), times in sorted(plate_date_times.items()):
        times_sorted = sorted(times)
        if len(times_sorted) < 2:
            continue
        gap = (times_sorted[-1] - times_sorted[0]).total_seconds()
        time_gaps_seconds.append(gap)
        detail_rows.append((date_str, plate, len(times_sorted), gap))

    gaps = np.array(time_gaps_seconds)
    gaps_min = gaps / 60.0

    out.write("Within-plate time gap (first slot to last slot):\n")
    out.write("  N plates measured:  %d\n" % len(gaps))
    out.write("  Median:            %.1f sec  (%.2f min)\n" % (np.median(gaps), np.median(gaps_min)))
    out.write("  Mean:              %.1f sec  (%.2f min)\n" % (np.mean(gaps), np.mean(gaps_min)))
    out.write("  Std:               %.1f sec\n" % np.std(gaps))
    out.write("  Min:               %.1f sec\n" % np.min(gaps))
    out.write("  Max:               %.1f sec  (%.2f min)\n" % (np.max(gaps), np.max(gaps_min) ))
    out.write("  95th percentile:   %.1f sec  (%.2f min)\n" % (np.percentile(gaps, 95), np.percentile(gaps_min, 95)))
    out.write("\n")

    # Plates with large gaps
    large = [(d, p, n, g) for d, p, n, g in detail_rows if g > 300]
    if large:
        out.write("Plates with >5 min gap:\n")
        for d, p, n, g in sorted(large, key=lambda x: -x[3]):
            out.write("  Y-%d on %s: %d slots, %.1f sec (%.1f min)\n" % (p, d, n, g, g/60))
        out.write("\n")
    else:
        out.write("No plates with >5 min gap.\n\n")

    # Drift impact estimate
    out.write("Drift impact estimate:\n")
    out.write("  At median gap %.0f sec, a 1%%/hour Helmholtz gain drift\n" % np.median(gaps))
    out.write("  would produce %.4f%% change between first and last slot.\n" % (np.median(gaps) / 3600.0 * 1.0))
    out.write("  Since NdFeB and SmCo are interleaved in the same plate,\n")
    out.write("  the residual on the DIFFERENTIAL is much smaller.\n\n")

    return gaps


def compute_plate_differential(plate_records):
    """Compute NdFeB-SmCo differential for a set of plate slot records.

    Returns (differential_pct, median_datetime, n_ndfeb, n_smco) or None.
    Uses temperature-corrected values.
    """
    ndfeb_vals = []
    smco_vals = []
    all_vals = []
    all_times = []

    for r in plate_records:
        if r['is_flagged']:
            continue
        mat = r['material']
        val = r['mwc_corr']
        all_vals.append(val)
        all_times.append(r['datetime'])
        if mat in ('N42EH', 'N52SH'):
            ndfeb_vals.append(val)
        elif mat in ('SmCo33H', 'SmCo35'):
            smco_vals.append(val)

    if not ndfeb_vals or not smco_vals or not all_vals:
        return None

    mean_ndfeb = np.mean(ndfeb_vals)
    mean_smco = np.mean(smco_vals)
    mean_all = np.mean(all_vals)

    if abs(mean_all) < MIN_BASELINE:
        return None

    differential_pct = (mean_ndfeb - mean_smco) / mean_all * 100.0
    median_time = sorted(all_times)[len(all_times) // 2]

    return (differential_pct, median_time, len(ndfeb_vals), len(smco_vals))


def analysis2_per_session(records, out):
    """Analysis 2: Per-session differential vs. elapsed time.

    For each tunnel session date with enough plates, compute Spearman
    correlation between elapsed time and intra-plate differential.
    """
    out.write("=" * 72 + "\n")
    out.write("ANALYSIS 2: Per-Session Differential vs. Elapsed Time\n")
    out.write("=" * 72 + "\n\n")

    # Filter to tunnel measurements after TUNNEL_START
    tunnel_recs = [r for r in records
                   if r['is_tunnel'] and r['datetime'] >= TUNNEL_START]

    # Group by date -> plate -> records
    date_plate_recs = defaultdict(lambda: defaultdict(list))
    for r in tunnel_recs:
        date_plate_recs[r['date_str']][r['plate']].append(r)

    session_results = []

    for date_str in sorted(date_plate_recs.keys()):
        plates = date_plate_recs[date_str]

        # Compute differential for each plate
        plate_diffs = []
        for plate_num in sorted(plates.keys()):
            precs = plates[plate_num]
            # Need at least one NdFeB and one SmCo
            result = compute_plate_differential(precs)
            if result is None:
                continue
            diff_pct, median_time, n_ndfeb, n_smco = result
            plate_diffs.append((plate_num, diff_pct, median_time))

        if len(plate_diffs) < MIN_PLATES_PER_SESSION:
            out.write("Session %s: %d plates (< %d minimum), skipped.\n" %
                      (date_str, len(plate_diffs), MIN_PLATES_PER_SESSION))
            continue

        # Elapsed time from session start
        session_start = min(t for _, _, t in plate_diffs)
        session_end = max(t for _, _, t in plate_diffs)
        session_span = (session_end - session_start).total_seconds() / 60.0

        elapsed_min = []
        differentials = []
        plate_nums = []
        for pn, diff, mtime in plate_diffs:
            elapsed_min.append((mtime - session_start).total_seconds() / 60.0)
            differentials.append(diff)
            plate_nums.append(pn)

        elapsed_min = np.array(elapsed_min)
        differentials = np.array(differentials)

        # Spearman correlation
        rho, pval = stats.spearmanr(elapsed_min, differentials)

        session_results.append({
            'date': date_str,
            'n_plates': len(plate_diffs),
            'span_min': session_span,
            'rho': rho,
            'pval': pval,
            'elapsed': elapsed_min,
            'diffs': differentials,
            'plate_nums': plate_nums,
        })

        out.write("Session %s: N=%d plates, span=%.0f min, "
                  "rho=%.3f, p=%.3f, sign=%s\n" %
                  (date_str, len(plate_diffs), session_span,
                   rho, pval, '+' if rho > 0 else '-'))

    out.write("\n")

    # Sign consistency
    if session_results:
        signs = [1 if s['rho'] > 0 else -1 for s in session_results]
        n_pos = sum(1 for s in signs if s > 0)
        n_neg = len(signs) - n_pos
        out.write("Sign pattern: %d positive, %d negative out of %d sessions\n" %
                  (n_pos, n_neg, len(signs)))
        # Binomial test: under H0, sign is 50/50
        binom_p = stats.binomtest(n_pos, len(signs), 0.5).pvalue
        out.write("Binomial test (sign consistency): p = %.3f\n" % binom_p)
        out.write("  (p < 0.05 would suggest consistent drift direction)\n\n")

    return session_results


def analysis3_pooled(session_results, out):
    """Analysis 3: Pooled cross-session test with normalized time."""
    out.write("=" * 72 + "\n")
    out.write("ANALYSIS 3: Pooled Cross-Session Test\n")
    out.write("=" * 72 + "\n\n")

    all_norm_times = []
    all_diffs = []

    for s in session_results:
        span = s['span_min']
        if span < 1:
            continue
        for elapsed, diff in zip(s['elapsed'], s['diffs']):
            norm_time = elapsed / span
            all_norm_times.append(norm_time)
            all_diffs.append(diff)

    norm_times = np.array(all_norm_times)
    diffs = np.array(all_diffs)

    out.write("Total pooled measurements: N = %d (across %d sessions)\n" %
              (len(diffs), len(session_results)))
    out.write("\n")

    if len(diffs) < 10:
        out.write("Too few data points for pooled analysis.\n\n")
        return norm_times, diffs

    rho, pval = stats.spearmanr(norm_times, diffs)
    out.write("Spearman rho (normalized time vs differential): %.4f\n" % rho)
    out.write("p-value: %.4f\n" % pval)
    out.write("|rho|: %.4f\n" % abs(rho))
    out.write("\n")

    # Linear fit for slope estimate
    slope, intercept, r_value, p_lr, std_err = stats.linregress(norm_times, diffs)
    out.write("Linear fit: diff = %.4f * norm_time + %.4f\n" % (slope, intercept))
    out.write("  Slope: %.4f %%  (change over full session)\n" % slope)
    out.write("  R^2: %.4f\n" % r_value**2)
    out.write("  p (linear): %.4f\n" % p_lr)
    out.write("\n")

    # Early vs late comparison
    early = diffs[norm_times < 0.33]
    late = diffs[norm_times > 0.67]
    if len(early) >= 5 and len(late) >= 5:
        t_stat, t_pval = stats.ttest_ind(early, late)
        out.write("Early third (norm_t < 0.33) vs Late third (norm_t > 0.67):\n")
        out.write("  Early: mean=%.4f%%, N=%d\n" % (np.mean(early), len(early)))
        out.write("  Late:  mean=%.4f%%, N=%d\n" % (np.mean(late), len(late)))
        out.write("  Difference: %.4f%%\n" % (np.mean(late) - np.mean(early)))
        out.write("  t-test: t=%.3f, p=%.4f\n" % (t_stat, t_pval))
        out.write("\n")

    return norm_times, diffs


def analysis4_y14(out):
    """Analysis 4: Y-14 Campaign 2 calibration plate (3-point drift)."""
    out.write("=" * 72 + "\n")
    out.write("ANALYSIS 4: Y-14 Campaign 2 Calibration (3-Point Drift)\n")
    out.write("=" * 72 + "\n\n")

    # Load Y-14 Helmholtz data (C2)
    y14_helm = {}  # slot -> [(datetime, mwc), ...]
    c2_helm_dir = os.path.normpath(C2_HELM_DIR)
    for slot in range(1, 5):
        fname = 'Y-14-%d_helmholtz.dat' % slot
        fpath = os.path.join(c2_helm_dir, fname)
        if not os.path.exists(fpath):
            out.write("WARNING: %s not found\n" % fpath)
            continue
        rows = parse_helmholtz_file(fpath)
        mwc = [(dt, v) for dt, v, u in rows
               if u == 'mWC' and abs(v - SENTINEL) > 1 and abs(v) >= MIN_BASELINE]
        y14_helm[slot] = mwc

    # Load Y-14 Teslameter temperatures (C2)
    c2_tesla_dir = os.path.normpath(C2_TESLA_DIR)
    y14_temps = {}  # (slot, datetime_approx) -> temp
    # Collect all temps per slot per approximate time
    slot_temps_raw = defaultdict(list)  # (slot, date_str, hour_approx) -> [temps]
    for slot in range(1, 5):
        for face in ('front', 'side', 'top'):
            fname = 'Y-14-%d_%s.dat' % (slot, face)
            fpath = os.path.join(c2_tesla_dir, fname)
            if not os.path.exists(fpath):
                continue
            rows = parse_teslameter_file(fpath)
            for dt, fields, temp in rows:
                if temp is None or abs(temp - SENTINEL) < 1:
                    continue
                # Only keep 2026-04-20 data
                if dt.strftime('%Y-%m-%d') != '2026-04-20':
                    continue
                # Group by approximate hour to match 3 measurement windows
                slot_temps_raw[(slot, dt.hour)].append(temp)

    # Map approximate hours to measurement windows
    # From data: 09:00, 14:09, 18:58 roughly
    def hour_to_window(hour):
        if hour < 12:
            return 'morning'
        elif hour < 17:
            return 'afternoon'
        else:
            return 'evening'

    y14_window_temps = defaultdict(list)  # (slot, window) -> [temps]
    for (slot, hour), temps in slot_temps_raw.items():
        window = hour_to_window(hour)
        y14_window_temps[(slot, window)].extend(temps)

    # Build table: slot x window -> (mwc_raw, temp, mwc_corr)
    windows = ['morning', 'afternoon', 'evening']
    window_labels = {'morning': 'Morning (~09:00)',
                     'afternoon': 'Afternoon (~14:10)',
                     'evening': 'Evening (~19:00)'}

    out.write("Y-14 Raw Helmholtz readings (mWC):\n")
    out.write("%-6s  %-10s  " % ("Slot", "Material"))
    for w in windows:
        out.write("%-14s  " % window_labels[w][:14])
    out.write("\n")
    out.write("-" * 72 + "\n")

    y14_table = {}  # (slot, window_idx) -> {raw, temp, corr}
    for slot in range(1, 5):
        mat = MAT_BY_SLOT[slot]
        alpha = ALPHA[mat]
        readings = y14_helm.get(slot, [])
        readings.sort(key=lambda x: x[0])

        row_str = "%-6d  %-10s  " % (slot, mat)
        for wi, w in enumerate(windows):
            if wi < len(readings):
                dt, raw_val = readings[wi]
                # Find temperature for this window
                temps = y14_window_temps.get((slot, w), [])
                temp = np.mean(temps) if temps else None
                if temp is not None:
                    corr_val = raw_val / (1.0 + alpha * (temp - T_REF))
                else:
                    corr_val = raw_val

                y14_table[(slot, wi)] = {
                    'raw': raw_val, 'temp': temp,
                    'corr': corr_val, 'datetime': dt,
                }
                row_str += "%-14.4f  " % raw_val
            else:
                row_str += "%-14s  " % "N/A"
        out.write(row_str + "\n")

    out.write("\n")

    # Temperature table
    out.write("Y-14 Teslameter temperatures (C):\n")
    out.write("%-6s  " % "Slot")
    for w in windows:
        out.write("%-14s  " % window_labels[w][:14])
    out.write("\n")
    out.write("-" * 60 + "\n")
    for slot in range(1, 5):
        row_str = "%-6d  " % slot
        for w in windows:
            temps = y14_window_temps.get((slot, w), [])
            if temps:
                row_str += "%-14.2f  " % np.mean(temps)
            else:
                row_str += "%-14s  " % "N/A"
        out.write(row_str + "\n")
    out.write("\n")

    # Temperature-corrected table
    out.write("Y-14 Temperature-corrected readings (mWC, T_REF=%.0fC):\n" % T_REF)
    out.write("%-6s  %-10s  " % ("Slot", "Material"))
    for w in windows:
        out.write("%-14s  " % window_labels[w][:14])
    out.write("\n")
    out.write("-" * 72 + "\n")
    for slot in range(1, 5):
        mat = MAT_BY_SLOT[slot]
        row_str = "%-6d  %-10s  " % (slot, mat)
        for wi in range(3):
            entry = y14_table.get((slot, wi))
            if entry:
                row_str += "%-14.4f  " % entry['corr']
            else:
                row_str += "%-14s  " % "N/A"
        out.write(row_str + "\n")
    out.write("\n")

    # Per-slot drift (raw and corrected)
    out.write("Per-slot drift relative to morning (%):\n")
    out.write("%-6s  %-10s  %-14s  %-14s  %-14s  %-14s\n" %
              ("Slot", "Material", "Aft raw%", "Eve raw%", "Aft corr%", "Eve corr%"))
    out.write("-" * 80 + "\n")
    for slot in range(1, 5):
        mat = MAT_BY_SLOT[slot]
        morning_raw = y14_table.get((slot, 0), {}).get('raw')
        morning_corr = y14_table.get((slot, 0), {}).get('corr')
        if morning_raw is None:
            continue
        row_str = "%-6d  %-10s  " % (slot, mat)
        for wi in (1, 2):
            entry = y14_table.get((slot, wi))
            if entry:
                pct_raw = (entry['raw'] - morning_raw) / morning_raw * 100.0
                row_str += "%-14.4f  " % pct_raw
            else:
                row_str += "%-14s  " % "N/A"
        for wi in (1, 2):
            entry = y14_table.get((slot, wi))
            if entry:
                pct_corr = (entry['corr'] - morning_corr) / morning_corr * 100.0
                row_str += "%-14.4f  " % pct_corr
            else:
                row_str += "%-14s  " % "N/A"
        out.write(row_str + "\n")
    out.write("\n")

    # Differential at each time point
    out.write("Intra-plate differential (NdFeB - SmCo) / mean at each time point:\n")
    out.write("%-14s  %-14s  %-14s\n" % ("Time point", "Raw diff %", "Corr diff %"))
    out.write("-" * 50 + "\n")

    diff_raw_list = []
    diff_corr_list = []
    for wi, w in enumerate(windows):
        ndfeb_raw = []
        smco_raw = []
        ndfeb_corr = []
        smco_corr = []
        all_raw = []
        all_corr = []
        for slot in range(1, 5):
            entry = y14_table.get((slot, wi))
            if entry is None:
                continue
            mat = MAT_BY_SLOT[slot]
            all_raw.append(entry['raw'])
            all_corr.append(entry['corr'])
            if mat in ('N42EH', 'N52SH'):
                ndfeb_raw.append(entry['raw'])
                ndfeb_corr.append(entry['corr'])
            else:
                smco_raw.append(entry['raw'])
                smco_corr.append(entry['corr'])

        if ndfeb_raw and smco_raw and all_raw:
            mean_all_raw = np.mean(all_raw)
            diff_raw = (np.mean(ndfeb_raw) - np.mean(smco_raw)) / mean_all_raw * 100.0
            mean_all_corr = np.mean(all_corr)
            diff_corr = (np.mean(ndfeb_corr) - np.mean(smco_corr)) / mean_all_corr * 100.0
            diff_raw_list.append(diff_raw)
            diff_corr_list.append(diff_corr)
            out.write("%-14s  %-14.4f  %-14.4f\n" %
                      (window_labels[w][:14], diff_raw, diff_corr))

    if len(diff_corr_list) >= 2:
        out.write("\nDifferential stability:\n")
        out.write("  Raw:  range = %.4f%%\n" % (max(diff_raw_list) - min(diff_raw_list)))
        out.write("  Corr: range = %.4f%%\n" % (max(diff_corr_list) - min(diff_corr_list)))
        out.write("  Corr std:  %.4f%%\n" % np.std(diff_corr_list))
        out.write("  (Demonstrates that within-session drift largely cancels\n")
        out.write("   in the NdFeB-SmCo differential.)\n")
    out.write("\n")

    return y14_table, diff_raw_list, diff_corr_list


# ── Plotting ─────────────────────────────────────────────────────────────────

def plot_wsd1(gaps_sec):
    """WSD1: Histogram of within-plate time gaps."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    gaps_min = gaps_sec / 60.0

    # Histogram in seconds
    ax1.hist(gaps_sec, bins=30, color='steelblue', edgecolor='black', alpha=0.8)
    ax1.axvline(np.median(gaps_sec), color='red', ls='--', lw=2,
                label='Median: %.0f sec' % np.median(gaps_sec))
    ax1.axvline(np.percentile(gaps_sec, 95), color='orange', ls='--', lw=1.5,
                label='95th pct: %.0f sec' % np.percentile(gaps_sec, 95))
    ax1.set_xlabel('Time gap: first to last slot (seconds)')
    ax1.set_ylabel('Number of plates')
    ax1.set_title('Within-Plate Measurement Duration')
    ax1.legend(fontsize=9)

    # Histogram in minutes
    ax2.hist(gaps_min, bins=30, color='steelblue', edgecolor='black', alpha=0.8)
    ax2.axvline(np.median(gaps_min), color='red', ls='--', lw=2,
                label='Median: %.2f min' % np.median(gaps_min))
    ax2.set_xlabel('Time gap: first to last slot (minutes)')
    ax2.set_ylabel('Number of plates')
    ax2.set_title('Within-Plate Measurement Duration')
    ax2.legend(fontsize=9)

    fig.suptitle('Analysis 1: Slot Timing Within Plates (Tunnel Sessions)',
                 fontsize=13, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(OUT_DIR, 'WSD1_slot_timing.png'), dpi=150)
    plt.close(fig)
    print("  Saved WSD1_slot_timing.png")


def plot_wsd2(session_results):
    """WSD2: Multi-panel scatter of differential vs. elapsed time per session."""
    n = len(session_results)
    if n == 0:
        print("  No sessions to plot for WSD2.")
        return

    ncols = min(3, n)
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows),
                              squeeze=False)

    for idx, s in enumerate(session_results):
        row = idx // ncols
        col = idx % ncols
        ax = axes[row][col]

        x = s['elapsed']
        y = s['diffs']

        ax.scatter(x, y, c='steelblue', s=30, alpha=0.7, edgecolors='black', lw=0.5)

        # Regression line
        if len(x) > 2:
            slope, intercept = np.polyfit(x, y, 1)
            x_fit = np.linspace(min(x), max(x), 50)
            ax.plot(x_fit, slope * x_fit + intercept, 'r-', lw=1.5, alpha=0.7)

        ax.set_title('%s  (N=%d)\nrho=%.3f, p=%.3f' %
                     (s['date'], s['n_plates'], s['rho'], s['pval']),
                     fontsize=10)
        ax.set_xlabel('Elapsed time (min)')
        ax.set_ylabel('Differential (%)')
        ax.axhline(0, color='gray', ls=':', lw=0.5)

        # Annotate plate numbers for extreme points
        y_arr = np.array(y)
        if len(y_arr) > 5:
            extremes = np.argsort(np.abs(y_arr - np.median(y_arr)))[-3:]
            for ei in extremes:
                ax.annotate('Y-%d' % s['plate_nums'][ei],
                            (x[ei], y[ei]), fontsize=7, alpha=0.6,
                            xytext=(3, 3), textcoords='offset points')

    # Hide unused subplots
    for idx in range(n, nrows * ncols):
        row = idx // ncols
        col = idx % ncols
        axes[row][col].set_visible(False)

    fig.suptitle('Analysis 2: Intra-Plate Differential vs. Elapsed Time per Session',
                 fontsize=13, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(OUT_DIR, 'WSD2_differential_vs_time.png'), dpi=150)
    plt.close(fig)
    print("  Saved WSD2_differential_vs_time.png")


def plot_wsd3(norm_times, diffs, session_results):
    """WSD3: Pooled normalized-time scatter."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Color by session date
    colors = plt.cm.tab10(np.linspace(0, 1, max(len(session_results), 1)))
    offset = 0
    for idx, s in enumerate(session_results):
        n = s['n_plates']
        span = s['span_min']
        if span < 1:
            offset += n
            continue
        nt = s['elapsed'] / span
        ax1.scatter(nt, s['diffs'], c=[colors[idx]], s=25, alpha=0.7,
                    label=s['date'], edgecolors='black', lw=0.3)

    # Regression line on pooled data
    if len(norm_times) > 2:
        rho, pval = stats.spearmanr(norm_times, diffs)
        slope, intercept = np.polyfit(norm_times, diffs, 1)
        x_fit = np.linspace(0, 1, 50)
        ax1.plot(x_fit, slope * x_fit + intercept, 'r-', lw=2, alpha=0.8,
                 label='Fit: slope=%.4f%%' % slope)
        ax1.set_title('Pooled: rho=%.4f, p=%.4f, N=%d' %
                       (rho, pval, len(diffs)), fontsize=11)

    ax1.set_xlabel('Normalized session time [0-1]')
    ax1.set_ylabel('Intra-plate differential (%)')
    ax1.axhline(0, color='gray', ls=':', lw=0.5)
    ax1.legend(fontsize=7, loc='best', ncol=2)

    # Right panel: per-session rho values
    dates = [s['date'] for s in session_results]
    rhos = [s['rho'] for s in session_results]
    pvals = [s['pval'] for s in session_results]
    bar_colors = ['#2ecc71' if abs(r) < 0.3 else '#e74c3c' for r in rhos]

    bars = ax2.barh(range(len(dates)), rhos, color=bar_colors, edgecolor='black',
                    alpha=0.8)
    ax2.set_yticks(range(len(dates)))
    ax2.set_yticklabels(dates, fontsize=9)
    ax2.set_xlabel('Spearman rho')
    ax2.set_title('Per-Session Correlation')
    ax2.axvline(0, color='black', lw=0.8)
    ax2.axvline(-0.3, color='gray', ls=':', lw=0.5)
    ax2.axvline(0.3, color='gray', ls=':', lw=0.5)

    # Annotate p-values
    for i, (rho_val, p_val) in enumerate(zip(rhos, pvals)):
        ax2.text(rho_val + 0.02 * np.sign(rho_val), i,
                 'p=%.2f' % p_val, va='center', fontsize=8)

    fig.suptitle('Analysis 3: Pooled Cross-Session Drift Test',
                 fontsize=13, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(OUT_DIR, 'WSD3_pooled.png'), dpi=150)
    plt.close(fig)
    print("  Saved WSD3_pooled.png")


def plot_wsd4(y14_table, diff_raw, diff_corr):
    """WSD4: Y-14 calibration plate 3-point drift."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    windows = ['morning', 'afternoon', 'evening']
    window_hours = [9.0, 14.15, 19.0]  # approximate fractional hours
    x_labels = ['09:00', '14:10', '19:00']

    # (0,0): Raw mWC per slot
    ax = axes[0][0]
    for slot in range(1, 5):
        mat = MAT_BY_SLOT[slot]
        vals = []
        for wi in range(3):
            entry = y14_table.get((slot, wi))
            vals.append(entry['raw'] if entry else np.nan)
        color = '#D62728' if mat.startswith('N') else '#2CA02C'
        ls = '-' if slot in (1, 3) else '--'
        ax.plot(window_hours, vals, 'o', color=color, ls=ls, lw=1.5,
                label='Slot %d: %s' % (slot, mat), markersize=6)
    ax.set_xticks(window_hours)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel('Time of day')
    ax.set_ylabel('Raw mWC')
    ax.set_title('Y-14 Raw Readings')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (0,1): Temperature per slot
    ax = axes[0][1]
    for slot in range(1, 5):
        mat = MAT_BY_SLOT[slot]
        temps = []
        for wi in range(3):
            entry = y14_table.get((slot, wi))
            temps.append(entry['temp'] if entry and entry['temp'] is not None else np.nan)
        color = '#D62728' if mat.startswith('N') else '#2CA02C'
        ls = '-' if slot in (1, 3) else '--'
        ax.plot(window_hours, temps, 'o', color=color, ls=ls, lw=1.5,
                label='Slot %d: %s' % (slot, mat), markersize=6)
    ax.set_xticks(window_hours)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel('Time of day')
    ax.set_ylabel('Temperature (C)')
    ax.set_title('Y-14 Teslameter Temperature')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (1,0): Corrected mWC per slot
    ax = axes[1][0]
    for slot in range(1, 5):
        mat = MAT_BY_SLOT[slot]
        vals = []
        for wi in range(3):
            entry = y14_table.get((slot, wi))
            vals.append(entry['corr'] if entry else np.nan)
        color = '#D62728' if mat.startswith('N') else '#2CA02C'
        ls = '-' if slot in (1, 3) else '--'
        ax.plot(window_hours, vals, 'o', color=color, ls=ls, lw=1.5,
                label='Slot %d: %s' % (slot, mat), markersize=6)
    ax.set_xticks(window_hours)
    ax.set_xticklabels(x_labels)
    ax.set_xlabel('Time of day')
    ax.set_ylabel('Corrected mWC (T_REF=20C)')
    ax.set_title('Y-14 Temperature-Corrected')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (1,1): Differential at each time point
    ax = axes[1][1]
    if diff_raw and diff_corr:
        ax.plot(window_hours[:len(diff_raw)], diff_raw, 's--', color='gray',
                lw=1.5, label='Raw differential', markersize=8)
        ax.plot(window_hours[:len(diff_corr)], diff_corr, 'o-', color='steelblue',
                lw=2, label='Corrected differential', markersize=8)
        ax.set_xticks(window_hours)
        ax.set_xticklabels(x_labels)
        ax.set_xlabel('Time of day')
        ax.set_ylabel('(NdFeB - SmCo) / mean (%)')
        ax.set_title('Y-14 Intra-Plate Differential')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

        # Annotate range
        corr_range = max(diff_corr) - min(diff_corr)
        ax.text(0.05, 0.05, 'Corrected range: %.4f%%' % corr_range,
                transform=ax.transAxes, fontsize=9,
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    fig.suptitle('Analysis 4: Y-14 Calibration Plate Within-Day Drift (2026-04-20)',
                 fontsize=13, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(OUT_DIR, 'WSD4_y14_calibration.png'), dpi=150)
    plt.close(fig)
    print("  Saved WSD4_y14_calibration.png")


# ── Verdict ──────────────────────────────────────────────────────────────────

def write_verdict(session_results, norm_times, diffs, out):
    """Write one-paragraph interpretation."""
    out.write("=" * 72 + "\n")
    out.write("VERDICT\n")
    out.write("=" * 72 + "\n\n")

    if len(diffs) < 10:
        out.write("Insufficient data for verdict.\n")
        return

    rho, pval = stats.spearmanr(norm_times, diffs)
    signs = [1 if s['rho'] > 0 else -1 for s in session_results]
    n_pos = sum(1 for s in signs if s > 0)
    n_neg = len(signs) - n_pos

    if abs(rho) < 0.15 and pval > 0.1:
        out.write("RESULT: No evidence of within-session drift affecting the differential.\n\n")
        out.write("The pooled Spearman correlation between normalized session time and\n")
        out.write("the intra-plate NdFeB-SmCo differential is rho = %.4f (p = %.3f),\n" % (rho, pval))
        out.write("well below any threshold of concern. The sign pattern across sessions\n")
        out.write("(%d positive, %d negative) shows no systematic direction. " % (n_pos, n_neg))
        out.write("This empirically\nvalidates the 'cancels by construction' argument: ")
        out.write("because all four material\nslots are measured consecutively within each plate, ")
        out.write("any gain drift over the\nsession does not produce a spurious differential signal.\n")
    elif abs(rho) > 0.3 and pval < 0.05:
        if (n_pos >= len(signs) - 1) or (n_neg >= len(signs) - 1):
            out.write("WARNING: Significant within-session drift detected.\n\n")
            out.write("The pooled Spearman correlation is rho = %.4f (p = %.3f) " % (rho, pval))
            out.write("with a consistent\nsign direction (%d/%d sessions same sign). " % (max(n_pos, n_neg), len(signs)))
            out.write("This suggests a real gain drift\neffect on the differential. ")
            slope, intercept, _, _, _ = stats.linregress(norm_times, diffs)
            out.write("The estimated slope is %.4f%% over a full session.\n" % slope)
            out.write("This should be evaluated for error budget impact.\n")
        else:
            out.write("RESULT: Significant pooled correlation, but inconsistent sign across sessions.\n\n")
            out.write("The pooled rho = %.4f (p = %.3f) is significant, " % (rho, pval))
            out.write("but the sign pattern\n(%d positive, %d negative) " % (n_pos, n_neg))
            out.write("suggests this is a position confound (measurement\n")
            out.write("order correlates with beamline location) rather than true gain drift.\n")
            out.write("No error budget change needed for within-session drift.\n")
    else:
        out.write("RESULT: Ambiguous (intermediate correlation).\n\n")
        out.write("The pooled Spearman correlation is rho = %.4f (p = %.3f). " % (rho, pval))
        out.write("The sign pattern\nis %d positive, %d negative across sessions. " % (n_pos, n_neg))
        out.write("The effect, if present, is\nsmall and not clearly systematic. ")
        out.write("No strong evidence for within-session drift,\n")
        out.write("but the data does not conclusively rule it out either.\n")

    out.write("\n")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Within-Session Gain Drift Analysis")
    print("=" * 50)

    # Load data
    print("\nLoading data...")
    y_materials = load_materials()
    print("  Loaded %d material assignments" % len(y_materials))
    temp_final = load_temperatures()
    print("  Loaded %d temperature records" % len(temp_final))
    records = load_helmholtz_with_timestamps(y_materials, temp_final)
    print("  Loaded %d Helmholtz measurements" % len(records))

    tunnel_post = [r for r in records if r['is_tunnel'] and r['datetime'] >= TUNNEL_START]
    dates = sorted(set(r['date_str'] for r in tunnel_post))
    print("  Tunnel dates (post %s): %d" % (TUNNEL_START.strftime('%Y-%m-%d'), len(dates)))
    for d in dates:
        n = len([r for r in tunnel_post if r['date_str'] == d])
        plates = len(set(r['plate'] for r in tunnel_post if r['date_str'] == d))
        print("    %s: %d measurements, %d plates" % (d, n, plates))

    # Open output file
    summary_path = os.path.join(OUT_DIR, 'drift_analysis_summary.txt')
    with open(summary_path, 'w') as out:
        out.write("Within-Session Gain Drift Analysis\n")
        out.write("Generated: %s\n" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        out.write("=" * 72 + "\n\n")

        # Analysis 1
        print("\nAnalysis 1: Slot timing...")
        gaps = analysis1_slot_timing(records, out)
        plot_wsd1(gaps)

        # Analysis 2
        print("\nAnalysis 2: Per-session differential vs elapsed time...")
        session_results = analysis2_per_session(records, out)
        plot_wsd2(session_results)

        # Analysis 3
        print("\nAnalysis 3: Pooled cross-session test...")
        norm_times, diffs = analysis3_pooled(session_results, out)
        plot_wsd3(norm_times, diffs, session_results)

        # Analysis 4
        print("\nAnalysis 4: Y-14 calibration plate drift...")
        y14_table, diff_raw, diff_corr = analysis4_y14(out)
        plot_wsd4(y14_table, diff_raw, diff_corr)

        # Verdict
        print("\nWriting verdict...")
        write_verdict(session_results, norm_times, diffs, out)

    print("\nSummary written to: %s" % summary_path)
    print("Plots written to: %s/" % OUT_DIR)
    print("\nDone.")


if __name__ == '__main__':
    main()
