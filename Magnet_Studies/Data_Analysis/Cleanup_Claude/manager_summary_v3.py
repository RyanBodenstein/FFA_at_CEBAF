#!/usr/bin/env python3
"""
Manager-Friendly Degradation Summary Plots — Version 3

Comprehensive presentation-ready plots combining:
  - Remade v1 plots 1-7 with gain systematic uncertainty bands (A01-A07)
  - Teslameter-based independent confirmation plots (B01-B04)
  - Technical detail plots for supervisors (C01-C04)
  - Comprehensive 3x3 dashboard (D01)

Output: Cleanup_Claude/Manager_Plots/v3_*.png (16 plots)
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
TESLAMETER_FIELD_VALID_AFTER = datetime(2025, 7, 1)
MIN_BASELINE = 0.1
FLAGGED = {'Y-34-4', 'Y-40-4'}

# ─── Pre-deployment Lab Temperature Estimates (Y-plate baselines) ────────────
# Y-plate Teslameter probe was replaced between Dec 2024 and Jul 2025.
# ALL sample types (Y, H, A) used the SAME probe — not different instruments.
# Same-day Y-H offsets: Sep 30 +0.87°C, Nov 20 +0.77°C (Y measured ~1hr later).
# Best correction: subtract 0.8°C from Y-only dates; use H reading for same-day dates.
# See Sensitivity_Analysis/probe_bias_assessment.txt for full justification.
# Format: date_str -> (temp_estimate_°C, uncertainty_°C)
Y_BASELINE_TEMP_LOOKUP = {
    '2024-04-24': (22.4, 1.0),   # Y=22.3, A=23.0, ALL-mean=22.4 (same-day cross-check)
    '2024-04-26': (23.8, 1.5),   # Y-only=24.6, minus 0.8°C probe bias
    '2024-05-06': (24.5, 1.5),   # Y-only=25.3, minus 0.8°C
    '2024-06-24': (25.5, 1.5),   # Y-only=26.3, minus 0.8°C (summer)
    '2024-07-23': (22.2, 1.5),   # Y-only=23.0, minus 0.8°C
    '2024-08-12': (23.5, 2.0),   # no Teslameter data available
    '2024-09-30': (25.8, 0.5),   # same-day H=25.8°C (direct cross-check)
    '2024-11-05': (24.3, 1.0),   # Y=25.1, minus 0.8°C (nearest H: Nov 11=23.0, 6d away)
    '2024-11-07': (23.8, 1.0),   # Y=24.6, minus 0.8°C (nearest H: Nov 11=23.0, 4d away)
    '2024-11-20': (24.6, 0.5),   # same-day H=24.6°C (direct cross-check, N=72)
    '2025-04-23': (23.5, 2.0),   # Helmholtz-only recovery, no Teslameter data
    '2025-04-25': (23.5, 2.0),
    '2025-04-30': (23.5, 2.0),
}
Y_BASELINE_TEMP_DEFAULT = (23.5, 2.0)  # fallback for any other pre-deployment dates

# ─── Gain Systematic Cleaning Parameters ─────────────────────────────────────
GAIN_EXCLUDE = FLAGGED.copy()  # {'Y-34-4', 'Y-40-4'} — known bad baselines
GAIN_PCT_THRESHOLD = 3.0       # |offset| > 3% = measurement error, exclude


class GainSystematic:
    """Holds cleaned + uncleaned gain estimates.

    Unpacks as ``gain_syst, session_offsets = get_gain_syst(helm_raw)`` via
    __iter__, so ALL existing call-sites work unchanged.  New fields accessible
    via attribute access (.gain_syst_raw, .session_offsets_raw, etc.).
    """

    def __init__(self, gain_syst, session_offsets, gain_syst_raw,
                 session_offsets_raw, excluded_samples, pct_threshold):
        self.gain_syst = gain_syst                    # cleaned ±%
        self.session_offsets = session_offsets          # cleaned dict
        self.gain_syst_raw = gain_syst_raw              # uncleaned ±%
        self.session_offsets_raw = session_offsets_raw  # uncleaned dict
        self.excluded_samples = excluded_samples        # set of sample IDs
        self.pct_threshold = pct_threshold              # |pct| cutoff used

    def __iter__(self):
        yield self.gain_syst
        yield self.session_offsets

    def __getitem__(self, idx):
        if idx == 0:
            return self.gain_syst
        if idx == 1:
            return self.session_offsets
        raise IndexError(idx)

    def __bool__(self):
        return True


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

REGION_COLORS = {
    'NE Arc': '#CC4444', 'NW Arc': '#E06666', 'SE Arc': '#AA3333',
    'SW Arc': '#DD5555',
    'North Linac': '#4444CC', 'South Linac': '#6666DD',
    'Labyrinth': '#888888',
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
            dt = datetime.strptime("%s %s" % (dm.group(1), dm.group(2)),
                                   "%Y-%m-%d %H:%M:%S")
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
        results: list of per-sample dicts
        helm_raw: dict of (plate, slot) -> {date_str: raw_mWC_value}
        temp_final: dict of (sample, date_str) -> (temp_mean, temp_std)
        y_materials: dict of sample_id -> material_name
    """
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
            if temp is None or abs(temp - SENTINEL) < 1:
                continue
            temp_lookup[(sample, dt.strftime('%Y-%m-%d'))].append(temp)

    temp_final = {}
    for key, temps in temp_lookup.items():
        temp_final[key] = (np.mean(temps),
                           np.std(temps, ddof=1) if len(temps) > 1 else 0.5)

    # Helmholtz data
    helm_raw = defaultdict(dict)
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
        slot_num = int(pm.group(2))
        region = PLACEMENTS.get(plate_num, 'Unknown')
        is_outlier = sample in FLAGGED

        rows = parse_helmholtz_file(os.path.join(helm_dir, f))
        mwc = [(dt, v) for dt, v, u in rows
               if u == 'mWC' and abs(v - SENTINEL) > 1 and abs(v) >= MIN_BASELINE]

        for dt, v in mwc:
            helm_raw[(plate_num, slot_num)][dt.strftime('%Y-%m-%d')] = v

        pre_corr = []
        pre_dates = []
        tunnel_series = []
        for dt, h_raw in mwc:
            date_str = dt.strftime('%Y-%m-%d')
            key = (sample, date_str)
            if dt < TUNNEL_START:
                # Pre-deployment: fix temperature if sample had Teslameter data
                # (Y-plate probe read ~2°C high before it broke)
                if key not in temp_final:
                    continue  # no Teslameter data → skip (as before)
                if date_str in Y_BASELINE_TEMP_LOOKUP:
                    # Override biased probe temp with estimated lab temp
                    t_mean, t_unc = Y_BASELINE_TEMP_LOOKUP[date_str]
                    temp_final[key] = (t_mean, t_unc)
                else:
                    t_mean, _ = temp_final[key]
                h_corr = h_raw / (1 + alpha * (t_mean - T_REF))
                pre_corr.append(h_corr)
                pre_dates.append(date_str)
            else:
                # Tunnel: use actual Teslameter temps (new probe, accurate)
                if key not in temp_final:
                    continue
                t_mean, _ = temp_final[key]
                h_corr = h_raw / (1 + alpha * (t_mean - T_REF))
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

        n_baseline_sessions = len(set(pre_dates))
        bl_std = (np.std(pre_corr, ddof=1) if len(pre_corr) > 1 else 0.0)

        results.append({
            'sample': sample, 'plate': plate_num, 'slot': slot_num,
            'material': mat, 'region': region,
            'pct_change': pct, 'bl_mean': bl_mean,
            'bl_sem_pct': bl_sem / abs(bl_mean) * 100.0,
            'is_outlier': is_outlier,
            'date_pcts': date_pcts,
            'n_baseline': len(pre_corr),
            'n_baseline_sessions': n_baseline_sessions,
            'baseline_std': bl_std,
        })

    return results, helm_raw, temp_final, y_materials


# ─── Teslameter Field Loader ──────────────────────────────────────────────────

def load_teslameter_field(y_materials):
    """Load Teslameter field magnitude data for Y-plates.

    Baseline = first tunnel measurement (NOT pre-deployment).
    Returns list of per-sample dicts with pct_change, per-face breakdown, temp history.
    """
    y_tesla_dir = os.path.join(BASE, 'Y_Plates', 'Teslameter')
    faces = ['front', 'side', 'top']

    # Find all Y-plate samples
    y_samples = set()
    for f in os.listdir(y_tesla_dir):
        m = re.match(r'(Y-\d+-\d+)_(front|side|top)\.dat$', f)
        if m:
            y_samples.add(m.group(1))

    results = []
    temp_history = defaultdict(list)  # date_str -> [temps]

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

        face_data = {}
        face_pct_by_face = {}
        for face in faces:
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

        # Compute % change per face, baseline = first tunnel date
        face_pct_changes = []
        for face, data in face_data.items():
            dates_for_face = defaultdict(list)
            temps_for_face = defaultdict(list)
            for dt, mag_corr, temp in data:
                d_str = dt.strftime('%Y-%m-%d')
                dates_for_face[d_str].append(mag_corr)
                temps_for_face[d_str].append(temp)
                temp_history[d_str].append(temp)
            sdates = sorted(dates_for_face.keys())
            if len(sdates) < 2:
                continue
            bl_d = sdates[0]
            lt_d = sdates[-1]
            bl_mag = np.mean(dates_for_face[bl_d])
            lt_mag = np.mean(dates_for_face[lt_d])
            if abs(bl_mag) < 1.0:
                continue
            face_pct = (lt_mag - bl_mag) / bl_mag * 100.0
            face_pct_changes.append(face_pct)
            face_pct_by_face[face] = face_pct

        if not face_pct_changes:
            continue

        pct_change = np.mean(face_pct_changes)
        if len(face_pct_changes) > 1:
            sigma_pct = np.std(face_pct_changes, ddof=1) / np.sqrt(len(face_pct_changes))
        else:
            sigma_pct = 0.5

        is_outlier = sample in FLAGGED

        # Compute date series for this sample (averaged across faces)
        date_pcts_tesla = []
        # Get all dates from any face
        all_dates = set()
        face_date_data = {}
        for face, data in face_data.items():
            dfd = defaultdict(list)
            for dt, mag_corr, temp in data:
                dfd[dt.strftime('%Y-%m-%d')].append(mag_corr)
            face_date_data[face] = dfd
            all_dates.update(dfd.keys())

        all_dates_sorted = sorted(all_dates)
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
                    date_pcts_tesla.append((datetime.strptime(d_str, '%Y-%m-%d'),
                                           np.mean(face_pcts_d)))

        results.append({
            'sample': sample, 'plate': plate_num, 'slot': slot_num,
            'material': material, 'region': region,
            'pct_change': pct_change, 'sigma_pct': sigma_pct,
            'n_faces': len(face_pct_changes),
            'face_pcts': face_pct_by_face,
            'is_outlier': is_outlier,
            'date_pcts': date_pcts_tesla,
        })

    return results, temp_history


# ─── Gain Systematic & Double Ratio ─────────────────────────────────────────

def compute_gain_variability(helm_raw, exclude_samples=None,
                              pct_threshold=None):
    """Quantify Helmholtz session-to-session gain variability from lab data.

    Parameters
    ----------
    helm_raw : dict
        {(plate, slot): {date_str: mWC_value, ...}, ...}
    exclude_samples : set or None
        Sample IDs (e.g. 'Y-34-4') to skip entirely.
    pct_threshold : float or None
        Drop individual offsets with |pct| > threshold (measurement errors).

    Returns
    -------
    session_offsets : dict
        {date_str: {'mean', 'std', 'sem', 'n', 'excluded_n'}, ...}
    """
    ref_date = '2024-11-05'
    lab_dates = ['2025-04-23', '2025-05-07', '2025-05-21',
                 '2025-06-11', '2025-06-17']
    if exclude_samples is None:
        exclude_samples = set()

    session_offsets = {}
    for check_date in lab_dates:
        offsets = []
        excluded_n = 0
        for (plate, slot), date_dict in helm_raw.items():
            sample_id = 'Y-%s-%s' % (plate, slot)
            if sample_id in exclude_samples:
                excluded_n += 1
                continue
            if ref_date in date_dict and check_date in date_dict:
                ref_v = date_dict[ref_date]
                check_v = date_dict[check_date]
                pct = (check_v - ref_v) / ref_v * 100.0
                if pct_threshold is not None and abs(pct) > pct_threshold:
                    excluded_n += 1
                    continue
                offsets.append(pct)
        if len(offsets) >= 5:
            session_offsets[check_date] = {
                'mean': np.mean(offsets),
                'std': np.std(offsets),
                'sem': np.std(offsets) / np.sqrt(len(offsets)),
                'n': len(offsets),
                'excluded_n': excluded_n,
            }
    return session_offsets


def get_gain_syst(helm_raw):
    """Compute gain systematic estimate (half the range of session offsets).

    Returns a GainSystematic object that unpacks as (gain_syst, session_offsets)
    for backward compatibility.  Also exposes .gain_syst_raw and
    .session_offsets_raw for the uncleaned (all-sample) estimate.
    """
    # Uncleaned (original): all samples, no threshold
    session_offsets_raw = compute_gain_variability(helm_raw)
    if session_offsets_raw:
        raw_offsets = [session_offsets_raw[d]['mean'] for d in session_offsets_raw]
        gain_syst_raw = (max(raw_offsets) - min(raw_offsets)) / 2.0
    else:
        gain_syst_raw = 0.3

    # Cleaned: exclude known-bad baselines + measurement errors
    session_offsets = compute_gain_variability(
        helm_raw, exclude_samples=GAIN_EXCLUDE, pct_threshold=GAIN_PCT_THRESHOLD)
    if session_offsets:
        clean_offsets = [session_offsets[d]['mean'] for d in session_offsets]
        gain_syst = (max(clean_offsets) - min(clean_offsets)) / 2.0
    else:
        gain_syst = 0.3

    return GainSystematic(
        gain_syst=gain_syst,
        session_offsets=session_offsets,
        gain_syst_raw=gain_syst_raw,
        session_offsets_raw=session_offsets_raw,
        excluded_samples=GAIN_EXCLUDE,
        pct_threshold=GAIN_PCT_THRESHOLD,
    )


def compute_intra_plate_diffs(clean):
    """Compute per-plate NdFeB-SmCo differential from clean results."""
    plate_data = defaultdict(dict)
    for r in clean:
        plate_data[r['plate']][r['material']] = r['pct_change']

    intra_diffs = []
    details = []
    for plate, mat_pcts in plate_data.items():
        nd = [mat_pcts[m] for m in ['N42EH', 'N52SH'] if m in mat_pcts]
        sm = [mat_pcts[m] for m in ['SmCo33H', 'SmCo35'] if m in mat_pcts]
        if nd and sm:
            diff = np.mean(nd) - np.mean(sm)
            intra_diffs.append(diff)
            details.append({
                'plate': plate,
                'region': PLACEMENTS.get(plate, 'Unknown'),
                'diff': diff,
                'ndfeb_pct': np.mean(nd),
                'smco_pct': np.mean(sm),
            })
    return intra_diffs, details


def compute_double_ratio(helm_raw, temp_final, ref_date, comp_date,
                          y_materials=None):
    """Compute intra-plate NdFeB-SmCo differential (gain-immune).

    Uses y_materials dict (sample_id -> material_name) for correct per-slot
    material assignment and temperature coefficient.  Falls back to hardcoded
    ALPHA_SLOT / slot-number grouping only if y_materials is not provided
    (legacy behaviour, known to be wrong for ~half the plates).
    """
    all_plates = set(p for (p, s) in helm_raw)
    plate_diffs = []
    plate_details = []

    for plate in sorted(all_plates):
        slot_data = {}          # slot -> (pct_change, material_name)
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

            # Correct alpha from material lookup, fallback to slot-based
            if y_materials and sample in y_materials:
                mat = y_materials[sample]
                a = ALPHA.get(mat, ALPHA_SLOT.get(slot, -0.0010))
            else:
                a = ALPHA_SLOT[slot]
                mat = MAT_BY_SLOT.get(slot, 'Unknown')

            ref_corr = ref_val / (1 + a * (ref_temp_data[0] - T_REF))
            comp_corr = comp_val / (1 + a * (comp_temp_data[0] - T_REF))
            pct = (comp_corr - ref_corr) / ref_corr * 100.0
            slot_data[slot] = (pct, mat)

        # Group by actual material family, not slot number
        ndfeb_pcts = [pct for pct, mat in slot_data.values()
                      if mat in ('N42EH', 'N52SH')]
        smco_pcts = [pct for pct, mat in slot_data.values()
                     if mat in ('SmCo33H', 'SmCo35')]
        if ndfeb_pcts and smco_pcts:
            diff = np.mean(ndfeb_pcts) - np.mean(smco_pcts)
            plate_diffs.append(diff)
            plate_details.append({
                'plate': plate,
                'region': PLACEMENTS.get(plate, 'Unknown'),
                'ndfeb_pct': np.mean(ndfeb_pcts),
                'smco_pct': np.mean(smco_pcts),
                'diff': diff,
            })

    return plate_diffs, plate_details


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY A: Remade Plots 1-7 with Gain Systematic Bands
# ═══════════════════════════════════════════════════════════════════════════════

def plot_A01_material_comparison(results, gain_syst, intra_diffs):
    """Remade Plot 1: 4 material bars + gain systematic band + inset."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig, ax = plt.subplots(figsize=(11, 7))

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
        sig_str = '(%dσ)' % round(sig) if sig >= 2 else '(n.s.)'
        labels.append('%s\n%+.2f ± %.2f%%(stat)\n%s  N=%d' %
                      (MAT_LABELS[mat], m, sem, sig_str, len(vals)))

    x = np.arange(len(labels))
    bars = ax.bar(x, means, yerr=sems, color=colors, capsize=8,
                  edgecolor='black', linewidth=0.8, alpha=0.85, width=0.6,
                  error_kw=dict(linewidth=2, capthick=2))

    # Gain systematic band (gray)
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.text(3.35, gain_syst + 0.01,
            'Helmholtz gain systematic ±%.2f%%' % gain_syst,
            fontsize=9, color='gray', ha='right', va='bottom')

    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('% Change from Baseline\n(temperature-corrected to 20°C)',
                  fontsize=12)
    ax.set_title('Magnet Degradation by Material Grade — v3 (with systematic uncertainty)\n'
                 'CEBAF Tunnel Exposure: Jul 2025 – Jan 2026',
                 fontsize=13, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(-0.55, 0.25)

    # Annotations
    ax.annotate('NdFeB grades show\nstatistically significant\ndegradation',
                xy=(0.5, means[0] - sems[0] - 0.02),
                xytext=(1.5, -0.45),
                fontsize=10, ha='center',
                arrowprops=dict(arrowstyle='->', color='#555'),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                          edgecolor='gray'))
    ax.annotate('SmCo grades within\ngain systematic noise',
                xy=(2.5, 0.02),
                xytext=(2.5, 0.18),
                fontsize=10, ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen',
                          edgecolor='gray', alpha=0.7))

    # Inset: gain-immune differential
    axin = fig.add_axes([0.15, 0.55, 0.22, 0.30])
    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0
    axin.bar(0, diff_mean, yerr=diff_sem, color='#8B0000', capsize=6,
             edgecolor='black', linewidth=0.8, alpha=0.85, width=0.5,
             error_kw=dict(linewidth=1.5, capthick=1.5))
    axin.axhline(0, color='black', linewidth=1, linestyle='--')
    axin.set_xticks([0])
    axin.set_xticklabels(['NdFeB−SmCo\n(gain-immune)'], fontsize=8)
    axin.set_ylabel('% Diff', fontsize=8)
    axin.set_title('%+.3f%% ± %.3f%% (%.1fσ)\nN=%d plates' %
                   (diff_mean, diff_sem, diff_sig, len(intra_diffs)),
                   fontsize=8, fontweight='bold')
    axin.set_ylim(-0.45, 0.1)
    axin.grid(axis='y', alpha=0.3)
    axin.tick_params(labelsize=7)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v3_A01_material_comparison.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  A01: Material comparison (with gain systematic)")


def plot_A02_ndfeb_vs_smco(results, gain_syst, intra_diffs):
    """Remade Plot 2: NdFeB vs SmCo + gain-immune differential bar."""
    clean = [r for r in results if not r['is_outlier']]
    ndfeb = [r['pct_change'] for r in clean if r['material'] in ['N42EH', 'N52SH']]
    smco = [r['pct_change'] for r in clean if r['material'] in ['SmCo33H', 'SmCo35']]

    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    fig, ax = plt.subplots(figsize=(10, 7))

    bar_means = [np.mean(ndfeb), np.mean(smco), diff_mean]
    bar_sems = [np.std(ndfeb, ddof=1)/np.sqrt(len(ndfeb)),
                np.std(smco, ddof=1)/np.sqrt(len(smco)),
                diff_sem]
    bar_colors = ['#CC4444', '#44AA44', '#8B0000']
    bar_labels = ['NdFeB\n(absolute)', 'SmCo\n(absolute)',
                  'NdFeB − SmCo\n(gain-immune)']

    bars = ax.bar([0, 1, 2.2], bar_means, yerr=bar_sems, color=bar_colors,
                  capsize=10, edgecolor='black', linewidth=1, alpha=0.85,
                  width=0.5, error_kw=dict(linewidth=2.5, capthick=2.5))

    # Gain systematic band on absolute bars only
    for i in [0, 1]:
        xi = [0, 1][i]
        ax.fill_between([xi - 0.25, xi + 0.25],
                         [bar_means[i] - gain_syst]*2,
                         [bar_means[i] + gain_syst]*2,
                         alpha=0.15, color='gray', zorder=0)
    # Overall gain band
    ax.axhspan(-gain_syst, gain_syst, alpha=0.06, color='gray', zorder=0)

    # Labels
    for i, (xi, m, s, n_val) in enumerate(zip([0, 1, 2.2], bar_means, bar_sems,
                                               [len(ndfeb), len(smco), len(intra_diffs)])):
        sig_val = abs(m / s) if s > 0 else 0
        unit = 'plates' if i == 2 else 'samples'
        ax.text(xi, m - s - 0.03,
                '%+.3f%%\n±%.3f%%(stat)\nN=%d %s' % (m, s, n_val, unit),
                ha='center', va='top', fontsize=10, fontweight='bold')

    # Highlight gain-immune bar
    bars[2].set_edgecolor('gold')
    bars[2].set_linewidth(2.5)
    ax.annotate('No gain systematic\n(%.1fσ significance)' % diff_sig,
                xy=(2.2, diff_mean), xytext=(2.2, 0.12),
                fontsize=10, ha='center', fontweight='bold', color='#006600',
                arrowprops=dict(arrowstyle='->', color='#006600', lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#E0FFE0',
                          edgecolor='#006600'))

    ax.axhline(0, color='black', linewidth=1.5)
    ax.set_xticks([0, 1, 2.2])
    ax.set_xticklabels(bar_labels, fontsize=12)
    ax.set_ylabel('% Change from Baseline', fontsize=13)
    ax.set_title('NdFeB vs SmCo: Absolute Values + Gain-Immune Differential — v3\n'
                 'Gray band = Helmholtz gain systematic (±%.2f%%)' % gain_syst,
                 fontsize=13, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(-0.50, 0.20)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v3_A02_ndfeb_vs_smco.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  A02: NdFeB vs SmCo (with gain-immune bar)")


def plot_A03_regional_comparison(results, gain_syst):
    """Remade Plot 3: Grouped bar by region × material + gain band."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    regions = ['NE Arc', 'SW Arc', 'NW Arc', 'SE Arc',
               'North Linac', 'South Linac', 'Labyrinth']
    region_labels = ['NE Arc', 'SW Arc', 'NW Arc', 'SE Arc',
                     'North Linac', 'South Linac', 'Low Dose']

    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(regions))
    width = 0.18
    offsets = [-1.5, -0.5, 0.5, 1.5]

    # Gain systematic band
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.text(6.5, gain_syst + 0.01,
            'Helmholtz gain syst. ±%.2f%%' % gain_syst,
            fontsize=8, color='gray', ha='right', va='bottom')

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
    ax.set_xticklabels(region_labels, fontsize=11)
    ax.set_ylabel('% Change from Baseline', fontsize=12)
    ax.set_title('Degradation by Tunnel Region and Material — v3 (with systematic uncertainty)\n'
                 '(Temperature-corrected to 20°C; outliers excluded)',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='lower left')
    ax.grid(axis='y', alpha=0.3)

    ax.axvspan(-0.5, 3.5, alpha=0.05, color='red')
    ax.axvspan(3.5, 5.5, alpha=0.05, color='blue')
    ax.axvspan(5.5, 6.5, alpha=0.05, color='green')
    ax.text(1.5, ax.get_ylim()[1] * 0.95, 'Arcs (higher dose)',
            ha='center', fontsize=10, fontstyle='italic', color='#AA0000')
    ax.text(4.5, ax.get_ylim()[1] * 0.95, 'Linacs (lower dose)',
            ha='center', fontsize=10, fontstyle='italic', color='#0000AA')
    ax.text(6, ax.get_ylim()[1] * 0.95, 'Low Dose',
            ha='center', fontsize=10, fontstyle='italic', color='#006600')

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v3_A03_regional_comparison.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  A03: Regional comparison (with gain band)")


def plot_A04_arc_vs_linac(results, gain_syst, intra_diffs_details):
    """Remade Plot 4: Arc vs Linac vs Low Dose + inset gain-immune regional."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    groups = {
        'Arcs\n(higher radiation)': ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc'],
        'Linacs\n(lower radiation)': ['North Linac', 'South Linac'],
        'Low Dose\n(labyrinth)': ['Labyrinth'],
    }

    fig, ax = plt.subplots(figsize=(12, 7))
    group_names = list(groups.keys())
    x = np.arange(len(group_names))
    width = 0.18
    offsets = [-1.5, -0.5, 0.5, 1.5]

    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)

    for i, mat in enumerate(materials):
        means, errs = [], []
        for gname, regions in groups.items():
            vals = [r['pct_change'] for r in clean
                    if r['region'] in regions and r['material'] == mat]
            if vals:
                means.append(np.mean(vals))
                errs.append(np.std(vals, ddof=1)/np.sqrt(len(vals))
                            if len(vals) > 1 else 0.05)
            else:
                means.append(0)
                errs.append(0)
        ax.bar(x + offsets[i] * width, means, width, yerr=errs,
               color=MAT_COLORS[mat], capsize=4, alpha=0.85,
               edgecolor='black', linewidth=0.5,
               label=MAT_LABELS[mat])

    ax.axhline(0, color='black', linewidth=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(group_names, fontsize=12)
    ax.set_ylabel('% Change from Baseline', fontsize=13)
    ax.set_title('Dose-Dependent Degradation: Arcs vs Linacs vs Low Dose — v3\n'
                 'Gray band = Helmholtz gain systematic ±%.2f%%' % gain_syst,
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(axis='y', alpha=0.3)

    # Inset: gain-immune regional differential
    axin = fig.add_axes([0.62, 0.15, 0.30, 0.30])
    arc_diffs = [d['diff'] for d in intra_diffs_details if 'Arc' in d['region']]
    lin_diffs = [d['diff'] for d in intra_diffs_details if 'Linac' in d['region']]
    lab_diffs = [d['diff'] for d in intra_diffs_details if d['region'] == 'Labyrinth']

    gi_means, gi_sems, gi_labels, gi_colors = [], [], [], []
    for name, vals, col in [('Arcs', arc_diffs, '#CC4444'),
                             ('Linacs', lin_diffs, '#4444CC'),
                             ('Low Dose', lab_diffs, '#888888')]:
        if vals:
            gi_means.append(np.mean(vals))
            gi_sems.append(np.std(vals)/np.sqrt(len(vals)) if len(vals) > 1 else 0.05)
            gi_labels.append('%s\n(N=%d)' % (name, len(vals)))
            gi_colors.append(col)
    if gi_means:
        axin.bar(range(len(gi_means)), gi_means, yerr=gi_sems, color=gi_colors,
                 capsize=4, edgecolor='black', linewidth=0.5, alpha=0.85, width=0.5)
        axin.axhline(0, color='black', linewidth=1, linestyle='--')
        axin.set_xticks(range(len(gi_means)))
        axin.set_xticklabels(gi_labels, fontsize=7)
        axin.set_ylabel('NdFeB−SmCo (%)', fontsize=7)
        axin.set_title('Gain-Immune Differential\n(no syst. uncertainty)', fontsize=8,
                       fontweight='bold')
        axin.grid(axis='y', alpha=0.3)
        axin.tick_params(labelsize=7)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v3_A04_arc_vs_linac.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  A04: Arc vs Linac vs Low Dose (with gain-immune inset)")


def plot_A05_timeseries(results, gain_syst):
    """Remade Plot 5: Degradation over time + gain band + Oct 21 flag."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig, ax = plt.subplots(figsize=(12, 7))

    # Gain systematic band
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)

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

        # Color Oct 21 points orange
        for j, d in enumerate(dates):
            if d == '2025-10-21':
                ax.errorbar([dt_objs[j]], [means_list[j]], yerr=[sems[j]],
                            color='#FF8C00', marker='s', markersize=9,
                            linewidth=0, capsize=5, capthick=2, zorder=6)

        ax.errorbar(dt_objs, means_list, yerr=sems,
                    color=MAT_COLORS[mat], marker='o', markersize=7,
                    linewidth=2.5, capsize=5, capthick=2,
                    label=MAT_LABELS[mat])

    ax.axhline(0, color='black', linewidth=1, linestyle='--')

    # Beam OFF marker
    ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1.5,
               linestyle=':', alpha=0.7)
    ylims = ax.get_ylim()
    ax.text(datetime(2025, 10, 24), ylims[1] * 0.85,
            'Beam OFF\n(Oct 21)', fontsize=9, color='gray', ha='left', va='top')

    # Oct 21 thermal lag note
    ax.axvspan(datetime(2025, 10, 18), datetime(2025, 11, 1),
               alpha=0.06, color='orange')
    ax.text(datetime(2025, 10, 25), ylims[0] * 0.95,
            'Oct 21: thermal lag suspect\n(magnets warmer than sensor)',
            fontsize=8, color='#AA6600', ha='center', fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFF8F0',
                      edgecolor='#AA6600', alpha=0.8))

    # Note about positive shifts
    ax.text(0.02, 0.02,
            'Note: Positive shifts within gray band are consistent\n'
            'with Helmholtz gain variability, not real recovery.',
            transform=ax.transAxes, fontsize=8, color='#555',
            verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor='gray', alpha=0.8))

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(datetime(2025, 6, 15), datetime(2026, 2, 1))
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('% Change from Pre-Deployment Baseline', fontsize=12)
    ax.set_title('Magnet Degradation Over Time — v3 (with systematic uncertainty)\n'
                 '(Temperature-corrected Helmholtz; gray band = gain syst. ±%.2f%%)' % gain_syst,
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10, loc='lower left')
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v3_A05_timeseries.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  A05: Time series (with gain band + Oct 21 flag)")


def plot_A06_waterfall(results, gain_syst):
    """Remade Plot 6: All samples sorted, with gain syst band + region colors."""
    clean = [r for r in results if not r['is_outlier']]
    clean.sort(key=lambda r: r['pct_change'])

    fig, ax = plt.subplots(figsize=(10, 16))

    # Gain systematic band (vertical)
    ax.axvspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.text(gain_syst + 0.01, len(clean) - 1,
            'Gain syst.\n±%.2f%%' % gain_syst,
            fontsize=8, color='gray', va='top')

    y_pos = np.arange(len(clean))
    colors = [MAT_COLORS[r['material']] for r in clean]
    pcts = [r['pct_change'] for r in clean]

    bars = ax.barh(y_pos, pcts, color=colors, edgecolor='none', height=0.7,
                   alpha=0.8)

    # Add region color on edges
    for i, r in enumerate(clean):
        rc = REGION_COLORS.get(r['region'], '#888888')
        ax.plot(-0.02, i, 's', color=rc, markersize=4, clip_on=False,
                transform=ax.get_yaxis_transform())

    labels = ['Y-%02d-%s (%s, %s)' % (r['plate'], r['sample'].split('-')[2],
              r['material'], r['region'].replace(' Arc', 'A').replace(' Linac', 'L').replace('Labyrinth', 'Lab'))
              for r in clean]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=5.5)
    ax.axvline(0, color='black', linewidth=1)
    ax.set_xlabel('% Change from Baseline', fontsize=12)
    ax.set_title('All Y-Plate Samples: Individual Degradation — v3\n'
                 '(sorted by magnitude; gray band = gain syst. ±%.2f%%)' % gain_syst,
                 fontsize=13, fontweight='bold')

    handles = [mpatches.Patch(color=MAT_COLORS[m], label=MAT_LABELS[m])
               for m in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']]
    ax.legend(handles=handles, fontsize=9, loc='lower right')
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v3_A06_waterfall.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  A06: Waterfall (with gain band + region markers)")


def plot_A07_dashboard(results, gain_syst, helm_raw, temp_final, intra_diffs,
                       session_offsets):
    """Remade Plot 7: 2×3 dashboard with systematic awareness."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    ndfeb_vals = [r['pct_change'] for r in clean
                  if r['material'] in ['N42EH', 'N52SH']]
    smco_vals = [r['pct_change'] for r in clean
                 if r['material'] in ['SmCo33H', 'SmCo35']]
    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('LDRD FFA@CEBAF Magnet Radiation Study — Preliminary Results (v3)\n'
                 'With Helmholtz gain systematic uncertainty',
                 fontsize=15, fontweight='bold', y=0.99)

    # (a) Material + syst
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
    ax1.set_xticklabels([MAT_LABELS[m] for m in materials], fontsize=7, rotation=15)
    ax1.set_ylabel('% Change', fontsize=9)
    ax1.set_title('(a) Degradation by Material\n(gray = gain syst. ±%.2f%%)' % gain_syst,
                  fontsize=10, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # (b) Gain-immune bar
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.bar(0, diff_mean, yerr=diff_sem, color='#8B0000', capsize=8,
            edgecolor='black', linewidth=1, alpha=0.85, width=0.5,
            error_kw=dict(linewidth=2, capthick=2))
    ax2.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax2.set_xticks([0])
    ax2.set_xticklabels(['NdFeB − SmCo\n(intra-plate)'], fontsize=9)
    ax2.set_ylabel('% Differential', fontsize=9)
    ax2.set_title('(b) Gain-Immune Result\n%+.3f%% ± %.3f%% (%.1fσ)' %
                  (diff_mean, diff_sem, diff_sig),
                  fontsize=10, fontweight='bold')
    ax2.text(0, diff_mean + diff_sem + 0.01,
             'NO gain systematic\nN = %d plates' % len(intra_diffs),
             ha='center', fontsize=8, color='#006600', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_ylim(-0.5, 0.15)

    # (c) Time series
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
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
        means_plot = [np.mean(date_vals[d]) for d in dates]
        ax3.plot(dt_objs, means_plot, 'o-', color=MAT_COLORS[mat], markersize=3,
                 linewidth=1.5, label=MAT_LABELS[mat])
    ax3.axhline(0, color='black', linewidth=1, linestyle='--')
    ax3.axvline(datetime(2025, 10, 21), color='gray', linewidth=1, linestyle=':')
    ax3.set_ylabel('% Change', fontsize=9)
    ax3.set_title('(c) Degradation Over Time', fontsize=10, fontweight='bold')
    ax3.legend(fontsize=6, loc='lower left')
    ax3.grid(alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

    # (d) Regional
    ax4 = fig.add_subplot(2, 3, 4)
    plate_data = defaultdict(dict)
    for r in clean:
        plate_data[r['plate']][r['material']] = r['pct_change']
    details = []
    for plate, mat_pcts in plate_data.items():
        nd = [mat_pcts[m] for m in ['N42EH', 'N52SH'] if m in mat_pcts]
        sm = [mat_pcts[m] for m in ['SmCo33H', 'SmCo35'] if m in mat_pcts]
        if nd and sm:
            details.append({'plate': plate, 'region': PLACEMENTS.get(plate, 'Unknown'),
                            'diff': np.mean(nd) - np.mean(sm)})
    if details:
        region_diffs = defaultdict(list)
        for d in details:
            region_diffs[d['region']].append(d['diff'])
        idx = 0
        x_labels = []
        for region in REGION_ORDER:
            vals = region_diffs.get(region, [])
            if vals:
                color = '#CC4444' if 'Arc' in region else '#4444CC' if 'Linac' in region else '#888888'
                ax4.bar(idx, np.mean(vals),
                        yerr=np.std(vals)/np.sqrt(len(vals)) if len(vals) > 1 else 0.05,
                        color=color, capsize=4, edgecolor='black',
                        linewidth=0.5, alpha=0.85, width=0.6)
                x_labels.append(region.replace(' Arc', '').replace(' Linac', ' Lin').replace('Labyrinth', 'Lab'))
                idx += 1
        ax4.axhline(0, color='black', linewidth=1, linestyle='--')
        ax4.set_xticks(range(idx))
        ax4.set_xticklabels(x_labels, fontsize=7, rotation=30)
    ax4.set_ylabel('NdFeB−SmCo (%)', fontsize=9)
    ax4.set_title('(d) By Region (gain-immune)\nRed=arc, blue=linac', fontsize=10,
                  fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)

    # (e) Gain variability
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

    # (f) Summary table
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.axis('off')
    table_data = []
    headers = ['Metric', 'Value', 'Uncertainty', 'N']
    for mat in materials:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        m = np.mean(vals)
        sem = np.std(vals, ddof=1) / np.sqrt(len(vals))
        sig = abs(m / sem)
        sig_label = '%dσ' % round(sig) if sig >= 2 else 'n.s.'
        table_data.append([MAT_LABELS[mat], '%+.3f%%' % m,
                          '±%.3f(stat)\n±%.2f(syst)' % (sem, gain_syst),
                          '%d' % len(vals)])
    table_data.append(['', '', '', ''])
    table_data.append(['NdFeB−SmCo\n(gain-immune)', '%+.3f%%' % diff_mean,
                      '±%.3f%%\n(%.1fσ)' % (diff_sem, diff_sig),
                      '%d plates' % len(intra_diffs)])

    table = ax6.table(cellText=table_data, colLabels=headers,
                      loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)
    for j in range(len(headers)):
        table[0, j].set_facecolor('#CCCCCC')
        table[0, j].set_text_props(fontweight='bold')
    for i in range(4):
        table[i+1, 0].set_facecolor(MAT_COLORS[materials[i]] + '22')
    table[6, 0].set_facecolor('#8B000022')
    table[6, 1].set_facecolor('#8B000022')
    ax6.set_title('(f) Key Results', fontsize=10, fontweight='bold', pad=15)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(PLOT_DIR, 'v3_A07_dashboard.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  A07: Dashboard (2x3 with systematic awareness)")


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY B: Teslameter Plots
# ═══════════════════════════════════════════════════════════════════════════════

def plot_B01_teslameter_by_material(tesla_results):
    """Teslameter field % change by material grade (bar chart)."""
    clean = [r for r in tesla_results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig, ax = plt.subplots(figsize=(10, 6))

    means, sems, colors, labels = [], [], [], []
    for mat in materials:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        if not vals:
            continue
        m = np.mean(vals)
        sem = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.5
        sig = abs(m / sem) if sem > 0 else 0
        means.append(m)
        sems.append(sem)
        colors.append(MAT_COLORS[mat])
        sig_str = '(%dσ)' % round(sig) if sig >= 2 else '(n.s.)'
        labels.append('%s\n%+.2f ± %.2f%%\n%s  N=%d' %
                      (MAT_LABELS[mat], m, sem, sig_str, len(vals)))

    x = np.arange(len(labels))
    ax.bar(x, means, yerr=sems, color=colors, capsize=8,
           edgecolor='black', linewidth=0.8, alpha=0.85, width=0.6,
           error_kw=dict(linewidth=2, capthick=2))

    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('% Change from First Tunnel Measurement\n(temperature-corrected to 20°C)',
                  fontsize=11)
    ax.set_title('Teslameter Field Magnitude Degradation by Material Grade\n'
                 'Independent confirmation (baseline = first tunnel measurement)',
                 fontsize=13, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    ax.text(0.02, 0.02,
            'Caveat: Teslameter has ~0.5% per-sample precision\n'
            '(hand-held probe placement variability).\n'
            'Baseline is first tunnel measurement, not pre-deployment.',
            transform=ax.transAxes, fontsize=8, color='#555',
            verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                      edgecolor='gray', alpha=0.8))

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v3_B01_teslameter_by_material.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  B01: Teslameter by material")


def plot_B02_temperature_history(temp_history):
    """Tunnel temperature over time from Teslameter readings."""
    fig, ax = plt.subplots(figsize=(12, 6))

    dates = sorted(temp_history.keys())
    dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
    t_means = [np.mean(temp_history[d]) for d in dates]
    t_stds = [np.std(temp_history[d]) for d in dates]
    t_mins = [min(temp_history[d]) for d in dates]
    t_maxs = [max(temp_history[d]) for d in dates]
    ns = [len(temp_history[d]) for d in dates]

    ax.fill_between(dt_objs, t_mins, t_maxs, alpha=0.15, color='steelblue',
                    label='Min–Max range')
    ax.fill_between(dt_objs,
                    [m - s for m, s in zip(t_means, t_stds)],
                    [m + s for m, s in zip(t_means, t_stds)],
                    alpha=0.3, color='steelblue', label='±1σ range')
    ax.plot(dt_objs, t_means, 'o-', color='steelblue', markersize=5,
            linewidth=2, label='Mean temperature')

    # Highlight Oct 21
    for i, d in enumerate(dates):
        if d == '2025-10-21':
            ax.plot(dt_objs[i], t_means[i], 's', color='orange', markersize=12,
                    zorder=6, markeredgecolor='black')
            ax.annotate('Beam OFF: tunnel cooled\nto ~%.1f°C (magnets warmer)' % t_means[i],
                        (dt_objs[i], t_means[i]),
                        textcoords='offset points', xytext=(60, 20),
                        fontsize=9, color='#AA6600',
                        arrowprops=dict(arrowstyle='->', color='#AA6600'),
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF8F0',
                                  edgecolor='#AA6600'))

    ax.axhline(T_REF, color='red', linewidth=1, linestyle='--', alpha=0.5,
               label='T_ref = 20°C')

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Temperature (°C)', fontsize=12)
    ax.set_title('CEBAF Tunnel Temperature (Teslameter Readings)\n'
                 'Showing thermal environment during magnet exposure',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v3_B02_temperature_history.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  B02: Temperature history")


def plot_B03_teslameter_vs_helmholtz(helm_results, tesla_results):
    """Scatter: Helmholtz vs Teslameter % change per sample."""
    clean_helm = {r['sample']: r for r in helm_results if not r['is_outlier']}
    clean_tesla = {r['sample']: r for r in tesla_results if not r['is_outlier']}

    common = set(clean_helm.keys()) & set(clean_tesla.keys())

    fig, ax = plt.subplots(figsize=(8, 8))

    for sample in common:
        hr = clean_helm[sample]
        tr = clean_tesla[sample]
        ax.scatter(hr['pct_change'], tr['pct_change'],
                   c=MAT_COLORS[hr['material']], s=50, alpha=0.7,
                   edgecolors='black', linewidths=0.3, zorder=3)

    # 1:1 line
    lims = [-1.5, 1.0]
    ax.plot(lims, lims, 'k--', linewidth=1, alpha=0.5, label='1:1 line')
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)

    handles = [mpatches.Patch(color=MAT_COLORS[m], label=MAT_LABELS[m])
               for m in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']]
    handles.append(plt.Line2D([0], [0], color='black', linestyle='--', label='1:1 line'))
    ax.legend(handles=handles, fontsize=9, loc='upper left')

    ax.set_xlabel('Helmholtz % Change (pre-deployment baseline)', fontsize=11)
    ax.set_ylabel('Teslameter % Change (first tunnel baseline)', fontsize=11)
    ax.set_title('Helmholtz vs Teslameter: Cross-Validation\n'
                 'Different baselines — correlation expected, not exact agreement',
                 fontsize=13, fontweight='bold')
    ax.grid(alpha=0.3)
    ax.set_aspect('equal')
    ax.set_xlim(lims)
    ax.set_ylim(lims)

    ax.text(0.02, 0.98,
            'Caveat: Different baselines\nHelmholtz: pre-deployment\n'
            'Teslameter: first tunnel measurement',
            transform=ax.transAxes, fontsize=8, color='#555',
            verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                      edgecolor='gray', alpha=0.8))

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v3_B03_teslameter_vs_helmholtz.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  B03: Teslameter vs Helmholtz scatter")


def plot_B04_teslameter_per_face(tesla_results):
    """Box-and-whisker of % change per face by material."""
    clean = [r for r in tesla_results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    faces = ['front', 'side', 'top']

    fig, axes = plt.subplots(1, 4, figsize=(16, 6), sharey=True)
    fig.suptitle('Teslameter Field Change by Face and Material\n'
                 'Testing degradation isotropy (baseline = first tunnel measurement)',
                 fontsize=13, fontweight='bold')

    for i, mat in enumerate(materials):
        ax = axes[i]
        mat_data = [r for r in clean if r['material'] == mat]
        face_vals = {face: [] for face in faces}
        for r in mat_data:
            for face in faces:
                if face in r['face_pcts']:
                    face_vals[face].append(r['face_pcts'][face])

        data = [face_vals[f] for f in faces]
        positions = range(len(faces))
        bp = ax.boxplot(data, positions=positions, widths=0.5,
                        patch_artist=True, showmeans=True,
                        meanprops=dict(marker='D', markerfacecolor='white',
                                       markeredgecolor='black', markersize=6))
        for patch in bp['boxes']:
            patch.set_facecolor(MAT_COLORS[mat])
            patch.set_alpha(0.5)

        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        ax.set_xticks(positions)
        ax.set_xticklabels(faces, fontsize=10)
        ax.set_title(MAT_LABELS[mat], fontsize=11, fontweight='bold',
                     color=MAT_COLORS[mat])
        ax.grid(axis='y', alpha=0.3)

        # Add N labels
        for j, face in enumerate(faces):
            n = len(face_vals[face])
            ax.text(j, ax.get_ylim()[0] * 0.8 if ax.get_ylim()[0] < 0 else -0.5,
                    'N=%d' % n, ha='center', fontsize=8, color='gray')

    axes[0].set_ylabel('% Change from First Tunnel Measurement', fontsize=11)

    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(os.path.join(PLOT_DIR, 'v3_B04_teslameter_per_face.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  B04: Teslameter per-face box plots")


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY C: Technical Detail Plots
# ═══════════════════════════════════════════════════════════════════════════════

def plot_C01_waterfall_by_region(results):
    """All samples waterfall, grouped/sorted by region, colored by material."""
    clean = [r for r in results if not r['is_outlier']]

    # Group by region, then sort within each region
    region_groups = defaultdict(list)
    for r in clean:
        region_groups[r['region']].append(r)
    for region in region_groups:
        region_groups[region].sort(key=lambda r: r['pct_change'])

    ordered = []
    region_boundaries = []
    for region in REGION_ORDER:
        if region in region_groups:
            region_boundaries.append((len(ordered), region))
            ordered.extend(region_groups[region])

    fig, ax = plt.subplots(figsize=(10, 16))

    y_pos = np.arange(len(ordered))
    colors = [MAT_COLORS[r['material']] for r in ordered]
    pcts = [r['pct_change'] for r in ordered]
    labels = ['Y-%02d-%s (%s)' % (r['plate'], r['sample'].split('-')[2],
              r['material']) for r in ordered]

    ax.barh(y_pos, pcts, color=colors, edgecolor='none', height=0.7, alpha=0.8)
    ax.axvline(0, color='black', linewidth=1)

    # Region dividers and labels
    for start_idx, region in region_boundaries:
        ax.axhline(start_idx - 0.5, color='gray', linewidth=0.5, linestyle='-',
                    alpha=0.5)
        # Find end of this region
        end_idx = start_idx
        for r in range(start_idx, len(ordered)):
            if ordered[r]['region'] == region:
                end_idx = r
        mid = (start_idx + end_idx) / 2.0
        rc = '#CC4444' if 'Arc' in region else '#4444CC' if 'Linac' in region else '#888888'
        ax.text(ax.get_xlim()[0] if ax.get_xlim()[0] != 0 else -0.8, mid,
                region, fontsize=8, fontweight='bold', color=rc,
                ha='right', va='center')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=5.5)
    ax.set_xlabel('% Change from Baseline', fontsize=12)
    ax.set_title('All Y-Plate Samples by Region — v3\n'
                 '(grouped by region, sorted by magnitude within each)',
                 fontsize=13, fontweight='bold')

    handles = [mpatches.Patch(color=MAT_COLORS[m], label=MAT_LABELS[m])
               for m in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']]
    ax.legend(handles=handles, fontsize=9, loc='lower right')
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v3_C01_waterfall_by_region.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  C01: Waterfall by region")


def plot_C02_per_plate_breakdown(results):
    """30-panel grid, one per plate, 4 bars each (material slots)."""
    clean = [r for r in results if not r['is_outlier']]
    plate_data = defaultdict(dict)
    for r in clean:
        plate_data[r['plate']][r['slot']] = r

    # Sort plates by region then plate number
    region_order_map = {r: i for i, r in enumerate(REGION_ORDER)}
    plates_sorted = sorted(plate_data.keys(),
                           key=lambda p: (region_order_map.get(PLACEMENTS.get(p, 'Unknown'), 99), p))

    n_plates = len(plates_sorted)
    ncols = 6
    nrows = (n_plates + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(18, nrows * 2.5), sharey=True)
    fig.suptitle('Per-Plate Degradation Breakdown (4 material slots per plate) — v3\n'
                 'Arranged by tunnel region',
                 fontsize=14, fontweight='bold', y=1.01)

    for idx, plate in enumerate(plates_sorted):
        row, col = idx // ncols, idx % ncols
        ax = axes[row][col] if nrows > 1 else axes[col]
        region = PLACEMENTS.get(plate, '?')
        slots = plate_data[plate]

        for slot in [1, 2, 3, 4]:
            if slot in slots:
                r = slots[slot]
                ax.bar(slot - 1, r['pct_change'], color=MAT_COLORS[r['material']],
                       edgecolor='black', linewidth=0.3, alpha=0.85, width=0.7)

        ax.axhline(0, color='black', linewidth=0.8)
        ax.set_xticks([0, 1, 2, 3])
        ax.set_xticklabels(['N42', 'N52', 'S33', 'S35'], fontsize=6)
        rc = '#CC4444' if 'Arc' in region else '#4444CC' if 'Linac' in region else '#888888'
        ax.set_title('Y-%02d (%s)' % (plate, region), fontsize=7,
                     fontweight='bold', color=rc)
        ax.tick_params(labelsize=6)
        ax.grid(axis='y', alpha=0.2)

    # Hide unused subplots
    for idx in range(n_plates, nrows * ncols):
        row, col = idx // ncols, idx % ncols
        ax = axes[row][col] if nrows > 1 else axes[col]
        ax.set_visible(False)

    if nrows > 1:
        axes[0][0].set_ylabel('% Change', fontsize=9)
    else:
        axes[0].set_ylabel('% Change', fontsize=9)

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(PLOT_DIR, 'v3_C02_per_plate_breakdown.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  C02: Per-plate breakdown grid")


def plot_C03_helmholtz_repeatability(helm_raw):
    """Pre-deployment session-to-session scatter (box plots per session)."""
    ref_date = '2024-11-05'
    lab_dates = ['2025-04-23', '2025-05-07', '2025-05-21',
                 '2025-06-11', '2025-06-17']

    fig, ax = plt.subplots(figsize=(12, 6))

    all_offsets = []
    date_labels = []
    for check_date in lab_dates:
        offsets = []
        for (plate, slot), date_dict in helm_raw.items():
            if ref_date in date_dict and check_date in date_dict:
                pct = (date_dict[check_date] - date_dict[ref_date]) / date_dict[ref_date] * 100.0
                offsets.append(pct)
        if offsets:
            all_offsets.append(offsets)
            dt = datetime.strptime(check_date, '%Y-%m-%d')
            date_labels.append(dt.strftime('%b %d\n%Y'))

    if all_offsets:
        bp = ax.boxplot(all_offsets, labels=date_labels, widths=0.5,
                        patch_artist=True, showmeans=True,
                        meanprops=dict(marker='D', markerfacecolor='red',
                                       markeredgecolor='black', markersize=6))
        for patch in bp['boxes']:
            patch.set_facecolor('#CCCCEE')
            patch.set_alpha(0.7)

        # Add N labels
        for i, offs in enumerate(all_offsets):
            ax.text(i + 1, ax.get_ylim()[0] if ax.get_ylim()[0] < -1 else min(offs) - 0.3,
                    'N=%d' % len(offs), ha='center', fontsize=9, color='gray')

        # Add spread annotation
        session_means = [np.mean(o) for o in all_offsets]
        spread = max(session_means) - min(session_means)
        ax.axhspan(min(session_means) - 0.05, max(session_means) + 0.05,
                    alpha=0.08, color='red')
        ax.text(len(all_offsets) + 0.3, np.mean(session_means),
                'Session mean spread:\n%.3f%%' % spread,
                fontsize=10, color='#AA0000', fontweight='bold', va='center')

    ax.axhline(0, color='black', linewidth=1.5, linestyle='--',
               label='Nov 5 2024 reference')
    ax.set_xlabel('Pre-Deployment Lab Session', fontsize=12)
    ax.set_ylabel('% Change from Nov 5, 2024 Reference', fontsize=12)
    ax.set_title('Helmholtz Coil Repeatability: Pre-Deployment Lab Sessions\n'
                 'No radiation, constant ~21°C — variation is instrument gain drift',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'v3_C03_helmholtz_repeatability.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  C03: Helmholtz repeatability")


def plot_C04_gain_immune_detail(results, gain_syst, intra_diffs):
    """Side-by-side: absolute with stat+syst error bars vs gain-immune with stat only."""
    clean = [r for r in results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('The Punchline: Absolute Values vs Gain-Immune Differential\n'
                 'Left: subject to ±%.2f%% instrument gain systematic. '
                 'Right: gain systematic cancels.' % gain_syst,
                 fontsize=13, fontweight='bold')

    # Left: absolute values with combined stat+syst error bars
    means_abs, sems_stat = [], []
    for mat in materials:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        means_abs.append(np.mean(vals))
        sems_stat.append(np.std(vals, ddof=1) / np.sqrt(len(vals)))

    x = np.arange(4)
    colors = [MAT_COLORS[m] for m in materials]

    # Statistical error bars
    ax1.bar(x, means_abs, yerr=sems_stat, color=colors, capsize=8,
            edgecolor='black', linewidth=0.8, alpha=0.85, width=0.6,
            error_kw=dict(linewidth=2, capthick=2, color='black'))

    # Systematic error bars (wider, lighter)
    for i in range(4):
        total_err = np.sqrt(sems_stat[i]**2 + gain_syst**2)
        ax1.errorbar(i, means_abs[i], yerr=total_err,
                     fmt='none', capsize=12, capthick=1.5,
                     ecolor='gray', elinewidth=1.5, zorder=0)

    ax1.axhline(0, color='black', linewidth=1)
    ax1.axhspan(-gain_syst, gain_syst, alpha=0.08, color='gray', zorder=0)
    ax1.set_xticks(x)
    labels_left = []
    for i, mat in enumerate(materials):
        sig_stat = abs(means_abs[i] / sems_stat[i]) if sems_stat[i] > 0 else 0
        total_err = np.sqrt(sems_stat[i]**2 + gain_syst**2)
        sig_total = abs(means_abs[i] / total_err) if total_err > 0 else 0
        labels_left.append('%s\n%+.3f%%\n±%.3f(stat) ±%.2f(syst)\n'
                           'Stat: %dσ  Total: %.1fσ' %
                           (MAT_LABELS[mat], means_abs[i], sems_stat[i],
                            gain_syst, round(sig_stat), sig_total))
    ax1.set_xticklabels(labels_left, fontsize=8)
    ax1.set_ylabel('% Change from Baseline', fontsize=12)
    ax1.set_title('(a) Absolute Values\n(black = stat error, gray = stat⊕syst)',
                  fontsize=12, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim(-0.7, 0.5)

    # Right: gain-immune differential (stat only)
    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    ax2.bar(0, diff_mean, yerr=diff_sem, color='#8B0000', capsize=10,
            edgecolor='black', linewidth=1.5, alpha=0.85, width=0.5,
            error_kw=dict(linewidth=3, capthick=3))
    ax2.axhline(0, color='black', linewidth=1.5, linestyle='--')

    ax2.set_xticks([0])
    ax2.set_xticklabels(['NdFeB − SmCo\n(intra-plate differential)\n\n'
                         '%+.3f%% ± %.3f%%\n%.1fσ significance\n'
                         'N = %d plates' %
                         (diff_mean, diff_sem, diff_sig, len(intra_diffs))],
                        fontsize=10)
    ax2.set_ylabel('% Differential', fontsize=12)
    ax2.set_title('(b) Gain-Immune Differential\n(statistical error only — '
                  'NO gain systematic)',
                  fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_ylim(-0.7, 0.5)

    # Big green "NO GAIN SYSTEMATIC" label
    ax2.text(0, 0.35, 'Gain systematic\nCANCELS here',
             ha='center', fontsize=14, fontweight='bold', color='#006600',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#E0FFE0',
                       edgecolor='#006600', linewidth=2))

    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(os.path.join(PLOT_DIR, 'v3_C04_gain_immune_detail.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  C04: Gain-immune detail (the punchline plot)")


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORY D: Comprehensive Dashboard
# ═══════════════════════════════════════════════════════════════════════════════

def plot_D01_comprehensive_dashboard(results, gain_syst, helm_raw, temp_final,
                                     intra_diffs, intra_details, session_offsets,
                                     tesla_results, temp_history,
                                     y_materials=None):
    """3×3 comprehensive dashboard."""
    clean = [r for r in results if not r['is_outlier']]
    clean_tesla = [r for r in tesla_results if not r['is_outlier']]
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    fig = plt.figure(figsize=(18, 12))
    fig.suptitle('LDRD FFA@CEBAF Magnet Radiation Study — Comprehensive Results (v3)\n'
                 'Helmholtz + Teslameter cross-validation, with gain systematic analysis',
                 fontsize=15, fontweight='bold', y=0.99)

    # (a) Material + syst
    ax = fig.add_subplot(3, 3, 1)
    for i, mat in enumerate(materials):
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        m = np.mean(vals)
        s = np.std(vals, ddof=1) / np.sqrt(len(vals))
        ax.bar(i, m, yerr=s, color=MAT_COLORS[mat], capsize=4,
               edgecolor='black', linewidth=0.5, alpha=0.85, width=0.6,
               error_kw=dict(linewidth=1.5))
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(range(4))
    ax.set_xticklabels([MAT_LABELS[m].replace('NdFeB ', '').replace('SmCo ', '')
                        for m in materials], fontsize=7)
    ax.set_ylabel('% Change', fontsize=8)
    ax.set_title('(a) By Material\n(gray = syst. ±%.2f%%)' % gain_syst,
                 fontsize=9, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # (b) Gain-immune bar
    ax = fig.add_subplot(3, 3, 2)
    ax.bar(0, diff_mean, yerr=diff_sem, color='#8B0000', capsize=8,
           edgecolor='black', linewidth=1, alpha=0.85, width=0.5,
           error_kw=dict(linewidth=2, capthick=2))
    ax.axhline(0, color='black', linewidth=1.5, linestyle='--')
    ax.set_xticks([0])
    ax.set_xticklabels(['NdFeB−SmCo'], fontsize=8)
    ax.set_title('(b) Gain-Immune\n%+.3f%% ± %.3f%% (%.1fσ)' %
                 (diff_mean, diff_sem, diff_sig),
                 fontsize=9, fontweight='bold')
    ax.set_ylabel('% Diff', fontsize=8)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(-0.5, 0.15)

    # (c) Timeseries
    ax = fig.add_subplot(3, 3, 3)
    ax.axhspan(-gain_syst, gain_syst, alpha=0.10, color='gray', zorder=0)
    for mat in materials:
        date_vals = defaultdict(list)
        for r in clean:
            if r['material'] != mat:
                continue
            for dt, pct in r['date_pcts']:
                date_vals[dt.strftime('%Y-%m-%d')].append(pct)
        dates = sorted(d for d in date_vals if len(date_vals[d]) >= 10)
        if not dates:
            dates = sorted(d for d in date_vals if len(date_vals[d]) >= 5)
        if not dates:
            continue
        dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        means_p = [np.mean(date_vals[d]) for d in dates]
        ax.plot(dt_objs, means_p, 'o-', color=MAT_COLORS[mat], markersize=3,
                linewidth=1.5, label=MAT_LABELS[mat])
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1, linestyle=':')
    ax.set_title('(c) Over Time', fontsize=9, fontweight='bold')
    ax.legend(fontsize=5, loc='lower left')
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.tick_params(labelsize=6)

    # (d) Teslameter confirmation
    ax = fig.add_subplot(3, 3, 4)
    for i, mat in enumerate(materials):
        vals = [r['pct_change'] for r in clean_tesla if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.5
            ax.bar(i, m, yerr=s, color=MAT_COLORS[mat], capsize=4,
                   edgecolor='black', linewidth=0.5, alpha=0.85, width=0.6,
                   error_kw=dict(linewidth=1.5))
    ax.axhline(0, color='black', linewidth=1)
    ax.set_xticks(range(4))
    ax.set_xticklabels([MAT_LABELS[m].replace('NdFeB ', '').replace('SmCo ', '')
                        for m in materials], fontsize=7)
    ax.set_ylabel('% Change', fontsize=8)
    ax.set_title('(d) Teslameter Confirmation\n(first tunnel baseline)', fontsize=9,
                 fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # (e) Regional gain-immune
    ax = fig.add_subplot(3, 3, 5)
    region_diffs = defaultdict(list)
    for d in intra_details:
        region_diffs[d['region']].append(d['diff'])
    idx = 0
    x_labels = []
    for region in REGION_ORDER:
        vals = region_diffs.get(region, [])
        if vals:
            color = '#CC4444' if 'Arc' in region else '#4444CC' if 'Linac' in region else '#888888'
            ax.bar(idx, np.mean(vals),
                   yerr=np.std(vals)/np.sqrt(len(vals)) if len(vals) > 1 else 0.05,
                   color=color, capsize=4, edgecolor='black',
                   linewidth=0.5, alpha=0.85, width=0.6)
            x_labels.append(region.replace(' Arc', '').replace(' Linac', ' Lin').replace('Labyrinth', 'Lab'))
            idx += 1
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.set_xticks(range(idx))
    ax.set_xticklabels(x_labels, fontsize=6, rotation=30)
    ax.set_ylabel('NdFeB−SmCo (%)', fontsize=8)
    ax.set_title('(e) By Region (gain-immune)', fontsize=9, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # (f) Gain variability
    ax = fig.add_subplot(3, 3, 6)
    if session_offsets:
        dates = sorted(session_offsets.keys())
        dt_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
        off_means = [session_offsets[d]['mean'] for d in dates]
        off_sems = [session_offsets[d]['sem'] for d in dates]
        ax.errorbar(dt_objs, off_means, yerr=off_sems, marker='s',
                    markersize=5, color='#333', linewidth=1.5, capsize=4)
        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        spread = max(off_means) - min(off_means)
        ax.axhspan(min(off_means)-0.05, max(off_means)+0.05,
                    alpha=0.08, color='red')
        ax.text(dt_objs[len(dt_objs)//2], max(off_means)+0.08,
                '%.2f%%' % spread, fontsize=8, ha='center',
                color='#AA0000', fontweight='bold')
    ax.set_title('(f) Gain Variability', fontsize=9, fontweight='bold')
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.tick_params(labelsize=6)

    # (g) Teslameter vs Helmholtz scatter
    ax = fig.add_subplot(3, 3, 7)
    clean_helm_d = {r['sample']: r for r in clean}
    clean_tesla_d = {r['sample']: r for r in clean_tesla}
    common = set(clean_helm_d.keys()) & set(clean_tesla_d.keys())
    for sample in common:
        hr = clean_helm_d[sample]
        tr = clean_tesla_d[sample]
        ax.scatter(hr['pct_change'], tr['pct_change'],
                   c=MAT_COLORS[hr['material']], s=20, alpha=0.6,
                   edgecolors='none', zorder=3)
    lims = [-1.5, 1.0]
    ax.plot(lims, lims, 'k--', linewidth=0.5, alpha=0.5)
    ax.axhline(0, color='gray', linewidth=0.3)
    ax.axvline(0, color='gray', linewidth=0.3)
    ax.set_xlabel('Helmholtz %', fontsize=7)
    ax.set_ylabel('Teslameter %', fontsize=7)
    ax.set_title('(g) Helmholtz vs Teslameter', fontsize=9, fontweight='bold')
    ax.grid(alpha=0.3)
    ax.tick_params(labelsize=6)

    # (h) Double ratio timeline
    ax = fig.add_subplot(3, 3, 8)
    ref_date = '2025-08-27'
    dr_dates = ['2025-07-17', '2025-07-30', '2025-10-21',
                '2025-10-23', '2025-10-29', '2026-01-08', '2026-01-12']
    for cd in dr_dates:
        diffs_list, _ = compute_double_ratio(helm_raw, temp_final, ref_date, cd,
                                                y_materials=y_materials)
        if diffs_list:
            m = np.mean(diffs_list)
            s = np.std(diffs_list) / np.sqrt(len(diffs_list))
            dt = datetime.strptime(cd, '%Y-%m-%d')
            color = '#FF6600' if cd == '2025-10-21' else '#8B0000'
            ax.errorbar([dt], [m], yerr=[s], marker='D', markersize=5,
                        color=color, capsize=3, capthick=1.5, linewidth=0,
                        elinewidth=1.5)
    ax.plot(datetime.strptime(ref_date, '%Y-%m-%d'), 0, 'D',
            color='#8B0000', markersize=7, markeredgecolor='gold',
            markeredgewidth=1.5)
    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    ax.axvline(datetime(2025, 10, 21), color='gray', linewidth=1, linestyle=':')
    ax.set_title('(h) Differential Timeline', fontsize=9, fontweight='bold')
    ax.set_ylabel('NdFeB−SmCo (%)', fontsize=8)
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.tick_params(labelsize=6)

    # (i) Summary table
    ax = fig.add_subplot(3, 3, 9)
    ax.axis('off')
    ndfeb_vals = [r['pct_change'] for r in clean
                  if r['material'] in ['N42EH', 'N52SH']]
    smco_vals = [r['pct_change'] for r in clean
                 if r['material'] in ['SmCo33H', 'SmCo35']]
    table_data = [
        ['NdFeB (abs)', '%+.3f%%' % np.mean(ndfeb_vals),
         '±%.3f(s) ±%.2f(sy)' % (np.std(ndfeb_vals,ddof=1)/np.sqrt(len(ndfeb_vals)), gain_syst),
         '%d' % len(ndfeb_vals)],
        ['SmCo (abs)', '%+.3f%%' % np.mean(smco_vals),
         '±%.3f(s) ±%.2f(sy)' % (np.std(smco_vals,ddof=1)/np.sqrt(len(smco_vals)), gain_syst),
         '%d' % len(smco_vals)],
        ['', '', '', ''],
        ['NdFeB−SmCo\n(gain-imm.)', '%+.3f%%' % diff_mean,
         '±%.3f%% (%.1fσ)' % (diff_sem, diff_sig),
         '%d pl.' % len(intra_diffs)],
    ]
    headers = ['Metric', 'Value', 'Uncertainty', 'N']
    table = ax.table(cellText=table_data, colLabels=headers,
                     loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.8)
    for j in range(len(headers)):
        table[0, j].set_facecolor('#CCCCCC')
        table[0, j].set_text_props(fontweight='bold')
    table[1, 0].set_facecolor('#CC444422')
    table[2, 0].set_facecolor('#44AA4422')
    table[4, 0].set_facecolor('#8B000022')
    table[4, 1].set_facecolor('#8B000022')
    ax.set_title('(i) Key Results', fontsize=9, fontweight='bold', pad=10)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(PLOT_DIR, 'v3_D01_comprehensive_dashboard.png'),
                dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("  D01: Comprehensive 3x3 dashboard")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("Manager Summary v3: Comprehensive Presentation-Ready Plots")
    print("=" * 70)
    print()

    # ─── Load Helmholtz data ─────────────────────────────────────────
    print("Loading Helmholtz data...")
    results, helm_raw, temp_final, y_materials = load_all()
    clean = [r for r in results if not r['is_outlier']]
    print("  %d Helmholtz samples (%d outliers excluded)" %
          (len(clean), len(results) - len(clean)))

    # Baseline quality summary
    total_bl = sum(r.get('n_baseline', 0) for r in results)
    multi_session = sum(1 for r in results if r.get('n_baseline_sessions', 0) > 1)
    print("  Total baseline readings: %d  (samples with multi-session baselines: %d)" %
          (total_bl, multi_session))

    # ─── Load Teslameter field data ──────────────────────────────────
    print("Loading Teslameter field data...")
    tesla_results, temp_history = load_teslameter_field(y_materials)
    clean_tesla = [r for r in tesla_results if not r['is_outlier']]
    print("  %d Teslameter samples (%d outliers excluded)" %
          (len(clean_tesla), len(tesla_results) - len(clean_tesla)))

    # ─── Compute gain systematic ─────────────────────────────────────
    gain_result = get_gain_syst(helm_raw)
    gain_syst, session_offsets = gain_result  # unpack for backward compat
    print("\nGain systematic (cleaned): ±%.4f%%  [excl. %d flagged + >%.0f%% outliers]"
          % (gain_syst, len(gain_result.excluded_samples),
             gain_result.pct_threshold))
    print("Gain systematic (uncleaned): ±%.4f%%  [all samples]"
          % gain_result.gain_syst_raw)

    # ─── Compute intra-plate differential ────────────────────────────
    intra_diffs, intra_details = compute_intra_plate_diffs(clean)
    diff_mean = np.mean(intra_diffs)
    diff_sem = np.std(intra_diffs) / np.sqrt(len(intra_diffs))
    diff_sig = abs(diff_mean / diff_sem) if diff_sem > 0 else 0

    # ─── VERIFICATION: Print key numbers ─────────────────────────────
    print("\n" + "=" * 70)
    print("VERIFICATION — Key Numbers")
    print("=" * 70)

    print("\n--- Helmholtz Absolute Values (same as v1) ---")
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        vals = [r['pct_change'] for r in clean if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals))
            print("  %s: %+.3f%% ± %.3f%% (%.1fσ stat, N=%d)" %
                  (mat, m, s, abs(m/s), len(vals)))

    print("\n--- Gain-Immune Intra-Plate Differential ---")
    print("  NdFeB − SmCo: %+.3f%% ± %.3f%% (%.1fσ, N=%d plates)" %
          (diff_mean, diff_sem, diff_sig, len(intra_diffs)))

    print("\n--- Gain Systematic (from pre-deployment lab) ---")
    if session_offsets:
        for d in sorted(session_offsets):
            so = session_offsets[d]
            excl = so.get('excluded_n', 0)
            excl_str = ' (%d excl)' % excl if excl else ''
            print("  %s: %+.3f%% ± %.3f%% (N=%d%s)" %
                  (d, so['mean'], so['sem'], so['n'], excl_str))
        offsets = [session_offsets[d]['mean'] for d in session_offsets]
        print("  Range: %.3f%% to %.3f%% (spread=%.3f%%)" %
              (min(offsets), max(offsets), max(offsets)-min(offsets)))
        print("  Estimated systematic (cleaned): ±%.4f%% (half-range)" % gain_syst)
        print("  Estimated systematic (uncleaned): ±%.4f%%" % gain_result.gain_syst_raw)

    print("\n--- Double Ratio (Aug 27 → Jan 12) ---")
    diffs_dr, details_dr = compute_double_ratio(helm_raw, temp_final,
                                                 '2025-08-27', '2026-01-12',
                                                 y_materials=y_materials)
    if diffs_dr:
        m = np.mean(diffs_dr)
        s = np.std(diffs_dr) / np.sqrt(len(diffs_dr))
        print("  %+.3f%% ± %.3f%% (%.1fσ, N=%d plates)" %
              (m, s, abs(m/s), len(diffs_dr)))

    print("\n--- Teslameter Field Summary ---")
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        vals = [r['pct_change'] for r in clean_tesla if r['material'] == mat]
        if vals:
            m = np.mean(vals)
            s = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.5
            sig = abs(m / s) if s > 0 else 0
            print("  %s: %+.3f%% ± %.3f%% (%.1fσ, N=%d)" %
                  (mat, m, s, sig, len(vals)))

    # ─── Generate plots ──────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("Generating v3 plots...")
    print("=" * 70)

    print("\nCategory A: Remade plots 1-7 with gain systematic bands")
    plot_A01_material_comparison(results, gain_syst, intra_diffs)
    plot_A02_ndfeb_vs_smco(results, gain_syst, intra_diffs)
    plot_A03_regional_comparison(results, gain_syst)
    plot_A04_arc_vs_linac(results, gain_syst, intra_details)
    plot_A05_timeseries(results, gain_syst)
    plot_A06_waterfall(results, gain_syst)
    plot_A07_dashboard(results, gain_syst, helm_raw, temp_final, intra_diffs,
                       session_offsets)

    print("\nCategory B: Teslameter plots")
    plot_B01_teslameter_by_material(tesla_results)
    plot_B02_temperature_history(temp_history)
    plot_B03_teslameter_vs_helmholtz(results, tesla_results)
    plot_B04_teslameter_per_face(tesla_results)

    print("\nCategory C: Technical detail plots")
    plot_C01_waterfall_by_region(results)
    plot_C02_per_plate_breakdown(results)
    plot_C03_helmholtz_repeatability(helm_raw)
    plot_C04_gain_immune_detail(results, gain_syst, intra_diffs)

    print("\nCategory D: Comprehensive dashboard")
    plot_D01_comprehensive_dashboard(results, gain_syst, helm_raw, temp_final,
                                     intra_diffs, intra_details, session_offsets,
                                     tesla_results, temp_history,
                                     y_materials=y_materials)

    print("\n" + "=" * 70)
    print("All 16 v3 plots saved to: %s/v3_*.png" % PLOT_DIR)
    print("=" * 70)


if __name__ == '__main__':
    main()
