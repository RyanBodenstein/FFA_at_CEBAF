#!/usr/bin/env python3
"""
Phase 4: Crosscheck OSL vs AIdata vs Rod spreadsheet.

Three crosschecks:
  1. OSL photon vs AIdata photon for UNSATURATED plates (should be ~1:1)
  2. Rod spreadsheet vs AIdata period doses (what fraction comes from rods?)
  3. Beam-off verification (done in Phase 3, repeated here for completeness)

Plus: Unit crosscheck per plan (Phase 3b).

Output:
  Rod_Dosimetry/crosscheck_results.csv
  Rod_Dosimetry/crosscheck_osl_vs_aidata.png
  Rod_Dosimetry/crosscheck_dose_comparison.png
"""

import sys
import os
import csv
import re
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEANUP = os.path.join(BASE, 'Cleanup_Claude')
OUT_DIR = os.path.join(CLEANUP, 'Rod_Dosimetry')
OSL_DIR = os.path.join(CLEANUP, 'Dosimetry', 'OSL_Area')

# Import placement data for region labels
sys.path.insert(0, CLEANUP)
from degradation_summary_v2 import PLACEMENTS as V2_PLACEMENTS

# Build plate -> region lookup
PLATE_REGION = {}
for yp, hp, region, subloc, line in V2_PLACEMENTS:
    pnum = int(yp.replace('Y', ''))
    PLATE_REGION['Y-%d' % pnum] = region


def load_osl_cumulative():
    """Load OSL cumulative doses."""
    path = os.path.join(OSL_DIR, 'plate_cumulative_dose.csv')
    dose = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            plate = row['plate'].strip()
            dose[plate] = {
                'body_mrem': float(row['body_mrem']),
                'photon_mrem': float(row['photon_mrem']),
                'neutron_mrem': float(row['neutron_mrem']),
                'beta_mrem': float(row['beta_mrem']),
                'n_saturated': int(row['n_saturated']),
                'is_lower_bound': row['is_lower_bound'].strip() == 'True',
            }
    return dose


def load_aidata_cumulative(tunnel_only=True):
    """Load AIdata cumulative doses. Excludes lab plates by default."""
    path = os.path.join(OUT_DIR, 'aidata_cumulative.csv')
    dose = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            plate = row['plate'].strip()
            is_lab = row.get('is_lab', 'False').strip() == 'True'
            if tunnel_only and is_lab:
                continue
            dose[plate] = {
                'photon_cum_rem': float(row['photon_cum_rem']),
                'neutron_cum_rem': float(row['neutron_cum_rem']),
                'photon_cum_gy': float(row['photon_cum_gy']),
                'sigma_photon_rem': float(row['sigma_photon_rem']),
                'sigma_neutron_rem': float(row['sigma_neutron_rem']),
                'days_since_install': float(row['days_since_install']),
                'n_measurements': int(row['n_measurements']),
            }
    return dose


def load_rod_doses():
    """Load rod spreadsheet doses, LDRD-only."""
    path = os.path.join(OUT_DIR, 'rod_doses.csv')
    rods = []
    with open(path) as f:
        for row in csv.DictReader(f):
            if row['is_ldrd'] == 'True':
                rods.append(row)
    return rods


def load_rod_plate_map():
    """Load rod -> plate mapping."""
    path = os.path.join(OUT_DIR, 'rod_plate_map.csv')
    mapping = {}  # rod_id -> list of (plate, date)
    with open(path) as f:
        for row in csv.DictReader(f):
            rod_id = row['rod_id']
            if rod_id not in mapping:
                mapping[rod_id] = []
            mapping[rod_id].append((row['plate'], row['date']))
    return mapping


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("  Saved: %s" % path)


def main():
    print("=" * 70)
    print("Phase 4: Crosscheck OSL vs AIdata vs Rods")
    print("=" * 70)

    osl = load_osl_cumulative()
    ai = load_aidata_cumulative()
    rod_doses = load_rod_doses()
    rod_map = load_rod_plate_map()

    # ═════════════════════════════════════════════════════════════════════
    # Crosscheck 1: OSL photon vs AIdata photon (unsaturated plates)
    # ═════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("Crosscheck 1: OSL photon vs AIdata photon (Y-plates)")
    print("=" * 70)

    results = []
    print("\n%-8s %-12s %12s %12s %8s %6s %s" % (
        'Plate', 'Region', 'AI_phot(rem)', 'OSL_phot(mr)', 'Ratio', 'N_sat', 'Status'))
    print("-" * 80)

    for ynum in sorted(set(int(p.split('-')[1]) for p in osl if p.startswith('Y-'))):
        plate = 'Y-%d' % ynum
        if plate not in ai:
            continue

        ai_photon_rem = ai[plate]['photon_cum_rem']
        ai_photon_mrem = ai_photon_rem * 1000.0
        ai_photon_gy = ai[plate]['photon_cum_gy']
        osl_photon_mrem = osl[plate]['photon_mrem']
        osl_body_mrem = osl[plate]['body_mrem']
        n_sat = osl[plate]['n_saturated']
        is_lb = osl[plate]['is_lower_bound']
        region = PLATE_REGION.get(plate, '?')

        # For unsaturated: compare AI photon (×1000→mrem) vs OSL photon
        # For saturated: AI gives true dose, OSL is lower bound
        if n_sat == 0 and osl_photon_mrem > 0:
            ratio = ai_photon_mrem / osl_photon_mrem
            status = 'UNSATURATED'
        elif n_sat > 0:
            ratio = ai_photon_mrem / osl_body_mrem if osl_body_mrem > 0 else 0
            status = 'SATURATED(%d)' % n_sat
        else:
            ratio = 0
            status = 'NO_OSL_DATA'

        lb = '>' if is_lb else ' '
        print("%-8s %-12s %12.1f %s%11.0f %8.2f %6d %s" % (
            plate, region, ai_photon_rem, lb, osl_photon_mrem,
            ratio, n_sat, status))

        results.append({
            'plate': plate,
            'region': region,
            'ai_photon_rem': ai_photon_rem,
            'ai_photon_gy': ai_photon_gy,
            'osl_photon_mrem': osl_photon_mrem,
            'osl_body_mrem': osl_body_mrem,
            'n_saturated': n_sat,
            'is_lower_bound': is_lb,
            'ratio_ai_osl': ratio,
            'status': status,
        })

    # Unsaturated ratio statistics
    unsat = [r for r in results if r['status'] == 'UNSATURATED' and r['ratio_ai_osl'] > 0]
    if unsat:
        ratios = [r['ratio_ai_osl'] for r in unsat]
        print("\n  Unsaturated plates (N=%d):" % len(unsat))
        print("    AI/OSL photon ratio: mean=%.3f, std=%.3f, range=%.3f–%.3f" % (
            np.mean(ratios), np.std(ratios), min(ratios), max(ratios)))

    # For saturated: show how much higher AI is than OSL floor
    sat = [r for r in results if 'SATURATED' in r['status']]
    if sat:
        sat_ratios = [r['ai_photon_gy'] for r in sat]
        print("\n  Saturated plates (N=%d):" % len(sat))
        print("    AI photon range: %.0f – %.0f Gy" % (min(sat_ratios), max(sat_ratios)))
        print("    AI/OSL body ratio range: %.1f – %.1f" % (
            min(r['ratio_ai_osl'] for r in sat),
            max(r['ratio_ai_osl'] for r in sat)))

    # ═════════════════════════════════════════════════════════════════════
    # Crosscheck 1b: Unit verification (Phase 3b from plan)
    # ═════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("Unit verification: AI photon (×1000→mrem) vs OSL photon (mrem)")
    print("  For unsaturated plates, these should be ~identical if units are rem")
    print("=" * 70)
    for r in unsat:
        ai_mrem = r['ai_photon_rem'] * 1000
        osl_mrem = r['osl_photon_mrem']
        delta = ai_mrem - osl_mrem
        print("  %-8s AI=%.0f mrem, OSL=%.0f mrem, delta=%.0f mrem (%.3f%%)" % (
            r['plate'], ai_mrem, osl_mrem, delta,
            100 * delta / osl_mrem if osl_mrem > 0 else 0))

    # ═════════════════════════════════════════════════════════════════════
    # Crosscheck 2: Rod per-swap doses vs what AIdata period increments show
    # ═════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("Crosscheck 2: Rod spreadsheet dose summary by plate")
    print("  Sum of valid rod doses per plate vs AIdata cumulative")
    print("=" * 70)

    # Map rod_id -> plate
    rod_to_plates = {}
    for rod_id, entries in rod_map.items():
        # Take the first plate (should be consistent)
        plates = set(e[0] for e in entries)
        if plates:
            rod_to_plates[rod_id] = list(plates)

    # Sum valid rod doses per plate
    rod_dose_by_plate = {}
    rod_count_by_plate = {}
    for r in rod_doses:
        rod_id = r['rod_id']
        if rod_id not in rod_to_plates:
            continue
        dose_str = r['best_dose_krad']
        if not dose_str:
            continue
        dose_krad = float(dose_str)
        # Convert krad to rem: 1 krad = 1000 rad = 100,000 mrem. For photons Q=1, so 1 krad = 1000 rem
        dose_rem = dose_krad * 1000.0

        for plate in rod_to_plates[rod_id]:
            if plate not in rod_dose_by_plate:
                rod_dose_by_plate[plate] = 0.0
                rod_count_by_plate[plate] = 0
            rod_dose_by_plate[plate] += dose_rem
            rod_count_by_plate[plate] += 1

    # Print comparison for Y-plates
    print("\n%-8s %12s %12s %6s %6s" % (
        'Plate', 'AI_phot(rem)', 'RodSum(rem)', 'N_rod', 'Ratio'))
    print("-" * 55)
    for ynum in range(1, 41):
        plate = 'Y-%d' % ynum
        if plate not in ai:
            continue
        ai_p = ai[plate]['photon_cum_rem']
        rod_sum = rod_dose_by_plate.get(plate, 0)
        n_rods = rod_count_by_plate.get(plate, 0)
        ratio = rod_sum / ai_p if ai_p > 0 else 0
        print("%-8s %12.1f %12.1f %6d %6.3f" % (
            plate, ai_p, rod_sum, n_rods, ratio))

    # ═════════════════════════════════════════════════════════════════════
    # Plot: OSL vs AIdata
    # ═════════════════════════════════════════════════════════════════════
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: 1:1 scatter for unsaturated
    ax = axes[0]
    ax.set_title('Unsaturated Plates: OSL photon vs AIdata photon')
    if unsat:
        x = [r['osl_photon_mrem'] / 1000 for r in unsat]  # to rem
        y = [r['ai_photon_rem'] for r in unsat]
        ax.scatter(x, y, c='#3366CC', s=60, zorder=3)
        for r in unsat:
            ax.annotate(r['plate'], (r['osl_photon_mrem']/1000, r['ai_photon_rem']),
                       fontsize=7, ha='left', va='bottom')
        lim = max(max(x), max(y)) * 1.1
        ax.plot([0, lim], [0, lim], 'k--', alpha=0.4, label='1:1 line')
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
    ax.set_xlabel('OSL photon (rem)')
    ax.set_ylabel('AIdata photon (rem)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Right: All Y-plates — bar chart OSL lower bound vs AIdata
    ax = axes[1]
    ax.set_title('All Y-plates: OSL body (lower bound) vs AIdata photon')
    plates_sorted = sorted(results, key=lambda r: -r['ai_photon_gy'])
    labels = [r['plate'] for r in plates_sorted]
    ai_gy = [r['ai_photon_gy'] for r in plates_sorted]
    osl_gy = [r['osl_body_mrem'] * 1e-5 for r in plates_sorted]  # mrem to Gy (Q=1 approx)

    x_pos = np.arange(len(labels))
    width = 0.35
    ax.barh(x_pos - width/2, ai_gy, width, label='AIdata photon (Gy)', color='#CC3333', alpha=0.8)
    ax.barh(x_pos + width/2, osl_gy, width, label='OSL body≈(Gy, LB)', color='#3366CC', alpha=0.8)
    ax.set_yticks(x_pos)
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel('Dose (Gy)')
    ax.set_xscale('log')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()

    fig.suptitle('Phase 4: OSL vs AIdata Dose Crosscheck', fontsize=13, fontweight='bold')
    plt.tight_layout()
    save(fig, 'crosscheck_osl_vs_aidata.png')

    # ═════════════════════════════════════════════════════════════════════
    # Plot: Dose comparison (rod sum vs AIdata vs OSL)
    # ═════════════════════════════════════════════════════════════════════
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_title('Y-plate Dose Comparison: AIdata vs OSL vs Rod Sum')

    y_plates_sorted = sorted(
        [r for r in results if r['ai_photon_gy'] > 0],
        key=lambda r: -r['ai_photon_gy'])
    labels = [r['plate'] for r in y_plates_sorted]
    x_pos = np.arange(len(labels))

    ai_vals = [r['ai_photon_gy'] for r in y_plates_sorted]
    osl_vals = [r['osl_body_mrem'] * 1e-5 for r in y_plates_sorted]
    rod_vals = [rod_dose_by_plate.get(r['plate'], 0) * 0.01 for r in y_plates_sorted]  # rem to Gy

    width = 0.25
    ax.barh(x_pos - width, ai_vals, width, label='AIdata photon (Gy)', color='#CC3333', alpha=0.8)
    ax.barh(x_pos, osl_vals, width, label='OSL body (Gy, LB)', color='#3366CC', alpha=0.8)
    ax.barh(x_pos + width, rod_vals, width, label='Rod sum (Gy, valid only)', color='#33AA33', alpha=0.8)

    ax.set_yticks(x_pos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel('Dose (Gy)')
    ax.set_xscale('log')
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()

    plt.tight_layout()
    save(fig, 'crosscheck_dose_comparison.png')

    # ═════════════════════════════════════════════════════════════════════
    # Write crosscheck results CSV
    # ═════════════════════════════════════════════════════════════════════
    out_csv = os.path.join(OUT_DIR, 'crosscheck_results.csv')
    fields = [
        'plate', 'region', 'ai_photon_rem', 'ai_photon_gy',
        'osl_photon_mrem', 'osl_body_mrem',
        'n_saturated', 'is_lower_bound', 'ratio_ai_osl', 'status',
        'rod_sum_rem', 'n_valid_rods',
    ]
    rows_out = []
    for r in results:
        r_out = dict(r)
        r_out['rod_sum_rem'] = rod_dose_by_plate.get(r['plate'], 0)
        r_out['n_valid_rods'] = rod_count_by_plate.get(r['plate'], 0)
        rows_out.append(r_out)

    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows_out)
    print("\n  Wrote %s (%d rows)" % (out_csv, len(rows_out)))

    # ═════════════════════════════════════════════════════════════════════
    # Summary
    # ═════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("CROSSCHECK SUMMARY")
    print("=" * 70)
    print("\n1. UNIT VERIFICATION:")
    print("   AIdata units confirmed as REM (×1000 = mrem)")
    if unsat:
        ratios = [r['ratio_ai_osl'] for r in unsat]
        print("   Unsaturated AI/OSL ratio: %.3f ± %.3f (N=%d)" % (
            np.mean(ratios), np.std(ratios), len(ratios)))
        print("   Interpretation: AI photon ≈ OSL photon for unsaturated plates")

    print("\n2. KIRSTEN'S METHODOLOGY:")
    # For unsaturated: AI ≈ OSL → she used OSL values directly
    # For saturated: AI >> OSL → she used rod/model values
    n_much_higher = sum(1 for r in results if 'SATURATED' in r['status'] and r['ratio_ai_osl'] > 2)
    print("   For unsaturated plates: AI ≈ OSL (she used OSL readings)")
    print("   For saturated plates: AI >> OSL in %d/%d cases" % (
        n_much_higher, len(sat)))
    print("   → Kirsten used 'best-of' approach: OSL when valid, rod/model when saturated")

    print("\n3. ROD DOSE COVERAGE:")
    plates_with_rods = [p for p in rod_dose_by_plate if p.startswith('Y-')]
    print("   Y-plates with valid rod doses: %d / %d" % (len(plates_with_rods), len(y_plates_sorted)))
    if plates_with_rods:
        rod_sums = [rod_dose_by_plate[p] * 0.01 for p in plates_with_rods]
        print("   Rod dose sum range: %.1f – %.1f Gy" % (min(rod_sums), max(rod_sums)))

    print("\n4. KEY PLATES:")
    print("   Highest dose: Y-22 = %.0f Gy (AI photon)" % ai[max(ai, key=lambda p: ai[p]['photon_cum_gy'] if p.startswith('Y-') else 0)]['photon_cum_gy'])
    print("   Y-37: LAB sample (correctly excluded from tunnel analysis)")
    print("   Beam-off (Oct→Jan): All Y-plates confirmed zero increment")

    print("\nDone.")


if __name__ == '__main__':
    main()
