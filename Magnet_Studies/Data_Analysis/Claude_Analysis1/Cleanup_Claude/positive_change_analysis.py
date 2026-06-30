#!/usr/bin/env python3
"""
Analyze positive pct_change samples in Y-plate Helmholtz data.
Identify patterns by material, region, baseline quality.
"""

import os
import re
import numpy as np
from datetime import datetime
from collections import defaultdict
import openpyxl

BASE = os.path.dirname(os.path.abspath(__file__))

T_REF = 20.0
SENTINEL = 1337
ALPHA = {
    'N42EH': -0.0010, 'N52SH': -0.0011,
    'SmCo33H': -0.0004, 'SmCo35': -0.0004,
}
MAT_BY_SLOT = {1: 'N42EH', 2: 'N52SH', 3: 'SmCo33H', 4: 'SmCo35'}
TUNNEL_START = datetime(2025, 7, 1)
MIN_BASELINE = 0.1
FLAGGED = {'Y-34-4', 'Y-40-4'}

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


def load_all_extended():
    """Load all Y-plate Helmholtz + Teslameter data, keeping individual readings."""
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

        pre_raw = []
        pre_corr = []
        tunnel_raw = []
        tunnel_corr = []
        for dt, h_raw in mwc:
            key = (sample, dt.strftime('%Y-%m-%d'))
            if key not in temp_final:
                continue
            t_mean, _ = temp_final[key]
            h_corr = h_raw / (1 + alpha * (t_mean - T_REF))
            if dt < TUNNEL_START:
                pre_raw.append((dt, h_raw, t_mean, h_corr))
                pre_corr.append(h_corr)
            else:
                tunnel_raw.append((dt, h_raw, t_mean, h_corr))
                tunnel_corr.append((dt, h_corr))

        if not pre_corr or not tunnel_corr:
            continue

        bl_mean = np.mean(pre_corr)
        if abs(bl_mean) < MIN_BASELINE:
            continue

        tunnel_corr.sort()
        latest_dt, latest_corr = tunnel_corr[-1]
        pct = (latest_corr - bl_mean) / bl_mean * 100.0

        bl_sem = (np.std(pre_corr, ddof=1) / np.sqrt(len(pre_corr))
                  if len(pre_corr) > 1 else 0.01 * bl_mean)

        results.append({
            'sample': sample, 'plate': plate_num, 'slot': slot_num,
            'material': mat, 'region': region,
            'pct_change': pct, 'bl_mean': bl_mean,
            'bl_sem_pct': bl_sem / abs(bl_mean) * 100.0,
            'is_outlier': is_outlier,
            'n_pre': len(pre_corr),
            'pre_readings': pre_raw,
            'tunnel_readings': tunnel_raw,
            'pre_corr_values': pre_corr,
        })

    return results


# ─── Main Analysis ────────────────────────────────────────────────────────────

results = load_all_extended()

# Exclude flagged outliers
results = [r for r in results if not r['is_outlier']]

positive = [r for r in results if r['pct_change'] > 0]
negative = [r for r in results if r['pct_change'] <= 0]

print("=" * 90)
print("POSITIVE pct_change SAMPLES (temp-corrected, outliers excluded)")
print("=" * 90)
print(f"{'Sample':<12} {'Material':<10} {'Region':<15} {'pct_chg':>8} {'N_pre':>6} {'BL_SEM%':>8}")
print("-" * 90)
for r in sorted(positive, key=lambda x: -x['pct_change']):
    print(f"{r['sample']:<12} {r['material']:<10} {r['region']:<15} "
          f"{r['pct_change']:>+8.3f} {r['n_pre']:>6} {r['bl_sem_pct']:>8.3f}")

print()
print("=" * 90)
print("POSITIVE SAMPLES BY MATERIAL")
print("=" * 90)
mat_pos = defaultdict(list)
mat_all = defaultdict(list)
for r in results:
    mat_all[r['material']].append(r)
    if r['pct_change'] > 0:
        mat_pos[r['material']].append(r)

for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
    n_pos = len(mat_pos.get(mat, []))
    n_all = len(mat_all.get(mat, []))
    print(f"  {mat:<10}: {n_pos:>3} positive / {n_all:>3} total  "
          f"({100*n_pos/n_all:.1f}%)" if n_all > 0 else f"  {mat:<10}: 0 / 0")

print()
print("=" * 90)
print("POSITIVE SAMPLES BY REGION")
print("=" * 90)
reg_pos = defaultdict(list)
reg_all = defaultdict(list)
for r in results:
    reg_all[r['region']].append(r)
    if r['pct_change'] > 0:
        reg_pos[r['region']].append(r)

for reg in ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc', 'North Linac', 'South Linac', 'Labyrinth']:
    n_pos = len(reg_pos.get(reg, []))
    n_all = len(reg_all.get(reg, []))
    if n_all > 0:
        print(f"  {reg:<15}: {n_pos:>3} positive / {n_all:>3} total  ({100*n_pos/n_all:.1f}%)")

print()
print("=" * 90)
print("TOTAL POSITIVE vs NEGATIVE BY MATERIAL")
print("=" * 90)
for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
    pos = [r for r in results if r['material'] == mat and r['pct_change'] > 0]
    neg = [r for r in results if r['material'] == mat and r['pct_change'] <= 0]
    pos_vals = [r['pct_change'] for r in pos]
    neg_vals = [r['pct_change'] for r in neg]
    print(f"  {mat:<10}: {len(pos):>3} positive (mean {np.mean(pos_vals):+.3f}% if any)"
          if pos_vals else f"  {mat:<10}: {len(pos):>3} positive", end="")
    print(f"  |  {len(neg):>3} negative (mean {np.mean(neg_vals):+.3f}%)"
          if neg_vals else f"  |  {len(neg):>3} negative")

print()
print("=" * 90)
print("DETAIL: Positive SmCo samples in Arcs/Linacs — individual readings")
print("=" * 90)
smco_pos_detail = [r for r in positive
                   if r['material'] in ('SmCo33H', 'SmCo35')
                   and r['region'] not in ('Labyrinth', 'Unknown')]

for r in sorted(smco_pos_detail, key=lambda x: -x['pct_change']):
    print(f"\n--- {r['sample']} ({r['material']}, {r['region']}) ---")
    print(f"    pct_change = {r['pct_change']:+.4f}%,  baseline mean = {r['bl_mean']:.3f} mWC,  "
          f"BL SEM = {r['bl_sem_pct']:.4f}%")
    print(f"    Pre-deployment readings ({r['n_pre']}):")
    for dt, raw, temp, corr in r['pre_readings']:
        print(f"      {dt.strftime('%Y-%m-%d')}  raw={raw:.3f} mWC  T={temp:.1f}C  corr={corr:.3f}")
    if r['n_pre'] > 1:
        print(f"      StdDev of corrected = {np.std(r['pre_corr_values'], ddof=1):.4f} mWC  "
              f"({np.std(r['pre_corr_values'], ddof=1)/abs(r['bl_mean'])*100:.4f}%)")
    print(f"    Tunnel readings ({len(r['tunnel_readings'])}):")
    for dt, raw, temp, corr in r['tunnel_readings']:
        pct_vs_bl = (corr - r['bl_mean']) / r['bl_mean'] * 100
        print(f"      {dt.strftime('%Y-%m-%d')}  raw={raw:.3f} mWC  T={temp:.1f}C  "
              f"corr={corr:.3f}  vs_bl={pct_vs_bl:+.3f}%")

# Also show detail for ALL positive samples (non-SmCo too) that have only 1-2 baselines
print()
print("=" * 90)
print("DETAIL: ALL positive samples with N_pre <= 2 — potential bad baselines")
print("=" * 90)
few_bl = [r for r in positive if r['n_pre'] <= 2]
if not few_bl:
    print("  (none)")
else:
    for r in sorted(few_bl, key=lambda x: -x['pct_change']):
        print(f"\n--- {r['sample']} ({r['material']}, {r['region']}) ---")
        print(f"    pct_change = {r['pct_change']:+.4f}%,  N_pre = {r['n_pre']}")
        print(f"    Pre-deployment readings:")
        for dt, raw, temp, corr in r['pre_readings']:
            print(f"      {dt.strftime('%Y-%m-%d')}  raw={raw:.3f} mWC  T={temp:.1f}C  corr={corr:.3f}")
        print(f"    Latest tunnel reading:")
        dt, raw, temp, corr = r['tunnel_readings'][-1]
        pct_vs_bl = (corr - r['bl_mean']) / r['bl_mean'] * 100
        print(f"      {dt.strftime('%Y-%m-%d')}  raw={raw:.3f} mWC  T={temp:.1f}C  "
              f"corr={corr:.3f}  vs_bl={pct_vs_bl:+.3f}%")

# Cross-check: is pct_change correlated with N_pre?
print()
print("=" * 90)
print("BASELINE COUNT vs SIGN OF CHANGE")
print("=" * 90)
for n_pre_thresh in [1, 2, 3]:
    sub = [r for r in results if r['n_pre'] <= n_pre_thresh]
    n_pos_sub = sum(1 for r in sub if r['pct_change'] > 0)
    print(f"  N_pre <= {n_pre_thresh}: {len(sub)} samples, {n_pos_sub} positive "
          f"({100*n_pos_sub/len(sub):.1f}%)" if sub else "")
sub = [r for r in results if r['n_pre'] > 3]
n_pos_sub = sum(1 for r in sub if r['pct_change'] > 0)
if sub:
    print(f"  N_pre >  3: {len(sub)} samples, {n_pos_sub} positive ({100*n_pos_sub/len(sub):.1f}%)")

print()
print("=" * 90)
print("SUMMARY STATISTICS")
print("=" * 90)
print(f"Total samples (excl outliers): {len(results)}")
print(f"Positive: {len(positive)} ({100*len(positive)/len(results):.1f}%)")
print(f"Negative: {len(negative)} ({100*len(negative)/len(results):.1f}%)")
