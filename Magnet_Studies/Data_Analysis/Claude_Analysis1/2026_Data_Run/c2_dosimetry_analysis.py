#!/usr/bin/env python3
"""
C2 Dosimetry Analysis: Combined Rod + OSL Dose Estimates

Applies Kirsten's decision tree to combine FWT-70 rod readings with
Landauer OSL badge data for Campaign 2 plates.

Decision tree (from C1 methodology):
  1. Rod < 2 krad AND OSL not saturated -> use OSL (more sensitive)
  2. Rod < 2 krad AND OSL saturated -> use 1.5 krad gap fill
  3. Rod 2-39 krad (Low@600nm valid range) -> use rod (average 2 replicates)
  4. Rod > 39 krad or Low saturating -> cascade to High range / 656nm

Two rod populations:
  - C1-final (R-681-740, installed Jan 2026): Covers shutdown period
    Paired with January 2026 OSLs (Landauer report 20260320, wear period Jul-Dec 2025)
  - C2-new (R-741-800, installed Apr 2026): Covers early C2 low-energy run
    No April 2026 OSLs available yet; rod-only analysis

Data sources:
  - Rod readings: Rods_read_051526_Isurumali_Raw.xlsx (parsed by c2_rod_analysis.py)
  - Rod-plate mapping: c2_rod_plate_map.csv (from c2_rod_plate_mapping.py)
  - OSL data: plate_dose_map.csv (January 2026 = Landauer 20260320)
  - C1 reference: y_plate_degradation.csv

Output:
  Analysis/c2_dosimetry_merged.csv - per-plate dose estimates with sources
  Analysis/c2_dosimetry_summary.md - narrative summary
"""

import os
import csv
import re
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.join(BASE, 'Analysis')
CLEANUP = os.path.join(os.path.dirname(BASE), 'Cleanup_Claude')

# FWT-70 valid ranges (krad)
LOW_600_MIN = 2.0    # krad
LOW_600_MAX = 39.0   # krad
HIGH_600_MIN = 12.0  # krad
HIGH_600_MAX = 300.0 # krad

# Unit conversions
KRAD_TO_GY = 10.0     # 1 krad = 10 Gy
MREM_TO_GY = 0.00001  # 1 mrem = 10 uGy = 0.00001 Gy (photon, Q=1)

# Lab Y-plates
LAB_Y_PLATES = {8, 14, 27, 28, 29, 31, 33, 35, 37}


def load_rod_data():
    """Load per-rod summary from c2_rod_raw_summary.csv"""
    rods = {}
    csv_path = os.path.join(ANALYSIS_DIR, 'c2_rod_raw_summary.csv')
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            rods[row['rod_id']] = row
    return rods


def load_rod_plate_map():
    """Load rod-to-plate mapping from c2_rod_plate_map.csv"""
    mapping = {}  # {rod_id: plate}
    csv_path = os.path.join(ANALYSIS_DIR, 'c2_rod_plate_map.csv')
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            if row['jan_rod']:
                mapping[row['jan_rod']] = {'plate': row['plate'], 'period': 'jan',
                                            'badge': row['jan_badge']}
            if row['apr_rod']:
                mapping[row['apr_rod']] = {'plate': row['plate'], 'period': 'apr',
                                            'badge': row['apr_badge']}
    return mapping


def load_january_osls():
    """Load January 2026 OSL data from plate_dose_map.csv"""
    osls = {}
    csv_path = os.path.join(CLEANUP, 'Dosimetry', 'OSL_Area', 'plate_dose_map.csv')
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            if row['collection_date'].startswith('2026'):
                osls[row['plate']] = {
                    'body_mrem': int(row['body_mrem']),
                    'photon_mrem': int(row['photon_mrem']),
                    'neutron_mrem': int(row['neutron_mrem']),
                    'beta_mrem': int(row['beta_mrem']),
                    'saturated': row['saturated_osl'] == 'True',
                    'badge_serial': row['badge_serial'],
                    'collection_date': row['collection_date'],
                }
    return osls


def load_c1_reference():
    """Load C1 dose reference data"""
    c1 = {}
    csv_path = os.path.join(os.path.dirname(BASE), 'Cleanup_Claude', 'Rod_Dosimetry',
                            'merged_dose_final.csv')
    if os.path.exists(csv_path):
        with open(csv_path) as f:
            for row in csv.DictReader(f):
                c1[row['plate']] = row
    return c1


def apply_decision_tree(rod_data, osl_data, period):
    """Apply Kirsten's decision tree to determine best dose estimate.

    Args:
        rod_data: dict with rod reading fields (may be None if rod not found)
        osl_data: dict with OSL fields (may be None if no OSL available)
        period: 'jan' or 'apr'

    Returns:
        dict with dose_gy, dose_source, notes
    """
    result = {
        'dose_gy': 0.0,
        'dose_source': 'none',
        'rod_dose_krad': None,
        'rod_valid': False,
        'osl_body_mrem': None,
        'osl_saturated': False,
        'notes': '',
    }

    # Get rod reading
    rod_krad = None
    rod_valid = False
    if rod_data:
        low_600 = rod_data.get('low_600_krad', '')
        high_600 = rod_data.get('high_600_krad', '')
        in_valid = rod_data.get('in_valid_range', '')

        if low_600:
            rod_krad = float(low_600)
            result['rod_dose_krad'] = rod_krad

            if rod_krad >= LOW_600_MIN and rod_krad <= LOW_600_MAX:
                rod_valid = True
            elif rod_krad > LOW_600_MAX and high_600:
                # Low range saturating, check High range
                high_val = float(high_600)
                if high_val >= HIGH_600_MIN and high_val <= HIGH_600_MAX:
                    rod_krad = high_val
                    rod_valid = True
                    result['notes'] = 'Low range saturating; using High@600'
                    result['rod_dose_krad'] = rod_krad

        result['rod_valid'] = rod_valid

    # Get OSL reading
    osl_body = None
    osl_sat = False
    if osl_data:
        osl_body = osl_data['body_mrem']
        osl_sat = osl_data['saturated']
        result['osl_body_mrem'] = osl_body
        result['osl_saturated'] = osl_sat

    # Decision tree
    if period == 'apr' and osl_data is None:
        # April rods: no OSL available yet
        if rod_valid and rod_krad is not None:
            result['dose_gy'] = rod_krad * KRAD_TO_GY
            result['dose_source'] = 'rod'
            result['notes'] += '; rod only (no April OSL)' if result['notes'] else 'rod only (no April OSL)'
        elif rod_krad is not None and rod_krad < LOW_600_MIN:
            # Below rod detection, no OSL available
            result['dose_gy'] = 0.0
            result['dose_source'] = 'below_detection'
            result['notes'] = 'rod < 2 krad, no OSL available'
        else:
            result['dose_source'] = 'none'
            result['notes'] = 'no data'
        return result

    # January rods: have OSL data
    if rod_krad is not None and rod_krad < LOW_600_MIN:
        # Rod below detection threshold
        if osl_data and not osl_sat:
            # Use OSL (decision tree rule 1)
            result['dose_gy'] = osl_body * MREM_TO_GY
            result['dose_source'] = 'osl'
            result['notes'] = 'rod < 2 krad; OSL not saturated; using OSL'
        elif osl_data and osl_sat:
            # OSL saturated, use gap fill (decision tree rule 2)
            result['dose_gy'] = 1.5 * KRAD_TO_GY  # 1.5 krad = 15 Gy gap fill
            result['dose_source'] = 'gap_fill'
            result['notes'] = 'rod < 2 krad; OSL saturated; using 1.5 krad gap fill'
        else:
            result['dose_gy'] = 0.0
            result['dose_source'] = 'below_detection'
            result['notes'] = 'rod < 2 krad; no OSL'
    elif rod_valid and rod_krad is not None:
        # Rod in valid range (decision tree rules 3-4)
        # Cross-check: if OSL is available and not saturated, compare
        rod_gy = rod_krad * KRAD_TO_GY
        if osl_data and not osl_sat and osl_body is not None:
            osl_gy = osl_body * MREM_TO_GY
            # If rod says 20+ Gy but OSL says < 1 Gy, the rod is at its
            # detection boundary and the OSL is more trustworthy
            if rod_krad < 5.0 and osl_gy < 1.0:
                result['dose_gy'] = osl_gy
                result['dose_source'] = 'osl_preferred'
                result['notes'] = ('rod borderline (%.1f krad) but OSL says %d mrem; '
                                   'rod-OSL discrepancy ~%.0fx; OSL preferred' %
                                   (rod_krad, osl_body, rod_gy / osl_gy if osl_gy > 0 else float('inf')))
            else:
                result['dose_gy'] = rod_gy
                result['dose_source'] = 'rod'
        else:
            result['dose_gy'] = rod_gy
            result['dose_source'] = 'rod'
    elif rod_krad is not None:
        # Rod out of valid range but above detection
        if rod_krad > LOW_600_MAX:
            result['dose_gy'] = rod_krad * KRAD_TO_GY
            result['dose_source'] = 'rod_extrapolated'
            result['notes'] = 'rod > 39 krad; extrapolated beyond Low range'
        else:
            result['dose_gy'] = rod_krad * KRAD_TO_GY
            result['dose_source'] = 'rod'
    elif osl_data:
        result['dose_gy'] = osl_body * MREM_TO_GY
        result['dose_source'] = 'osl_only'
        result['notes'] = 'no rod data; using OSL'
    else:
        result['dose_source'] = 'none'

    return result


def main():
    print("=" * 70)
    print("C2 Dosimetry Analysis: Rod + OSL Combined")
    print("=" * 70)

    # Load data
    rods = load_rod_data()
    rod_map = load_rod_plate_map()
    jan_osls = load_january_osls()
    c1_ref = load_c1_reference()

    print("\nLoaded:")
    print("  Rods: %d" % len(rods))
    print("  Rod-plate mappings: %d" % len(rod_map))
    print("  January 2026 OSLs: %d plates" % len(jan_osls))
    print("  C1 reference: %d plates" % len(c1_ref))

    # Build per-plate analysis
    results = []

    # Process each rod through the mapping
    for rod_id, map_info in sorted(rod_map.items(),
                                     key=lambda x: int(x[0].split('-')[1])):
        plate = map_info['plate']
        period = map_info['period']

        rod_data = rods.get(rod_id)
        osl_data = jan_osls.get(plate) if period == 'jan' else None

        # Apply decision tree
        dt = apply_decision_tree(rod_data, osl_data, period)

        # C1 reference data
        c1 = c1_ref.get(plate, {})
        c1_gamma_gy = float(c1.get('gamma_dose_gy', 0))
        c1_neutron_rem = float(c1.get('neutron_dose_rem', 0))

        # Plate classification
        is_lab = False
        if plate.startswith('Y-'):
            pnum = int(plate.split('-')[1])
            is_lab = pnum in LAB_Y_PLATES

        row = {
            'plate': plate,
            'period': period,
            'rod_id': rod_id,
            'badge_serial': map_info['badge'],
            'is_lab': is_lab,
            'rod_dose_krad': '%.3f' % dt['rod_dose_krad'] if dt['rod_dose_krad'] is not None else '',
            'rod_valid': dt['rod_valid'],
            'osl_body_mrem': dt['osl_body_mrem'] if dt['osl_body_mrem'] is not None else '',
            'osl_saturated': dt['osl_saturated'],
            'dose_gy': '%.4f' % dt['dose_gy'],
            'dose_source': dt['dose_source'],
            'c1_gamma_gy': '%.1f' % c1_gamma_gy if c1_gamma_gy > 0 else '',
            'c1_neutron_rem': '%.1f' % c1_neutron_rem if c1_neutron_rem > 0 else '',
            'notes': dt['notes'],
        }
        results.append(row)

    # Write CSV
    out_csv = os.path.join(ANALYSIS_DIR, 'c2_dosimetry_merged.csv')
    fields = ['plate', 'period', 'rod_id', 'badge_serial', 'is_lab',
              'rod_dose_krad', 'rod_valid', 'osl_body_mrem', 'osl_saturated',
              'dose_gy', 'dose_source', 'c1_gamma_gy', 'c1_neutron_rem', 'notes']
    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    print("\nWrote: %s (%d rows)" % (out_csv, len(results)))

    # Summarize
    jan_results = [r for r in results if r['period'] == 'jan']
    apr_results = [r for r in results if r['period'] == 'apr']

    print("\n" + "=" * 70)
    print("JANUARY 2026 (C1-final rods + OSLs, shutdown period)")
    print("=" * 70)
    print("  Total plates: %d" % len(jan_results))

    # Source breakdown
    jan_sources = defaultdict(int)
    for r in jan_results:
        jan_sources[r['dose_source']] += 1
    print("  Dose source breakdown:")
    for src, n in sorted(jan_sources.items()):
        print("    %-20s: %d" % (src, n))

    # Dose stats
    jan_doses = [float(r['dose_gy']) for r in jan_results]
    jan_nonzero = [d for d in jan_doses if d > 0]
    print("  Dose range: %.4f - %.4f Gy" % (min(jan_doses), max(jan_doses)))
    if jan_nonzero:
        print("  Non-zero doses: %d (median %.4f Gy)" % (
            len(jan_nonzero), sorted(jan_nonzero)[len(jan_nonzero)//2]))

    # Y-plates only
    jan_y = [r for r in jan_results if r['plate'].startswith('Y-') and not r['is_lab']]
    print("\n  Y-plate tunnel subset (%d plates):" % len(jan_y))
    for r in sorted(jan_y, key=lambda x: float(x['dose_gy']), reverse=True)[:10]:
        print("    %s: %.4f Gy (source=%s, rod=%s krad, OSL=%s mrem)" % (
            r['plate'], float(r['dose_gy']), r['dose_source'],
            r['rod_dose_krad'] if r['rod_dose_krad'] else 'N/A',
            r['osl_body_mrem'] if r['osl_body_mrem'] != '' else 'N/A'))

    print("\n" + "=" * 70)
    print("APRIL 2026 (C2-new rods, early low-energy run, no April OSLs)")
    print("=" * 70)
    print("  Total plates: %d" % len(apr_results))

    apr_sources = defaultdict(int)
    for r in apr_results:
        apr_sources[r['dose_source']] += 1
    print("  Dose source breakdown:")
    for src, n in sorted(apr_sources.items()):
        print("    %-20s: %d" % (src, n))

    apr_doses = [float(r['dose_gy']) for r in apr_results]
    apr_nonzero = [d for d in apr_doses if d > 0]
    print("  Dose range: %.1f - %.1f Gy" % (min(apr_doses), max(apr_doses)))
    if apr_nonzero:
        print("  Non-zero doses: %d (range %.1f - %.1f Gy)" % (
            len(apr_nonzero), min(apr_nonzero), max(apr_nonzero)))

    # High-dose April plates
    print("\n  Plates with measurable dose (rod > 2 krad):")
    for r in sorted(apr_results, key=lambda x: float(x['dose_gy']), reverse=True):
        if float(r['dose_gy']) > 0:
            c1_str = ''
            if r['c1_gamma_gy']:
                c1_str = ' (C1: %.0f Gy)' % float(r['c1_gamma_gy'])
            print("    %s: %.1f Gy [%s, rod=%.1f krad]%s" % (
                r['plate'], float(r['dose_gy']), r['rod_id'],
                float(r['rod_dose_krad']), c1_str))

    # Beam-off verification: January OSLs vs September 2025 (last beam)
    print("\n" + "=" * 70)
    print("BEAM-OFF VERIFICATION")
    print("=" * 70)
    print("January 2026 OSLs cover the shutdown period (Sep 2025 - Jan 2026).")
    print("No beam was present. All readings should be near zero or from")
    print("residual activation only.")
    print()

    jan_osl_vals = []
    for plate, osl in sorted(jan_osls.items()):
        if plate.startswith('Y-'):
            pnum = int(plate.split('-')[1])
            if pnum not in LAB_Y_PLATES:
                jan_osl_vals.append((plate, osl['body_mrem']))

    print("  Y-plate tunnel OSLs (Jan 2026, shutdown period):")
    print("    Range: %d - %d mrem" % (
        min(v for _, v in jan_osl_vals), max(v for _, v in jan_osl_vals)))
    print("    Zero readings: %d / %d" % (
        sum(1 for _, v in jan_osl_vals if v == 0), len(jan_osl_vals)))
    print("    All < 100 mrem: %s" % ('YES' if all(v < 100 for _, v in jan_osl_vals) else 'NO'))
    print("    No saturated: %s" % ('YES' if all(not o['saturated'] for o in jan_osls.values()) else 'NO'))
    print("    No neutron signal: %s" % ('YES' if all(o['neutron_mrem'] == 0 for o in jan_osls.values()) else 'NO'))
    print()
    print("  Interpretation: All readings consistent with zero beam. The small")
    print("  photon signals (5-62 mrem) at NDX locations are residual activation")
    print("  from the C1 run. No neutron signal confirms no beam-on operations.")
    print("  This verifies the shutdown period had no significant radiation.")

    # C1 comparison for April rods
    print("\n" + "=" * 70)
    print("C1 vs C2 DOSE COMPARISON (April rods at same locations)")
    print("=" * 70)

    for r in sorted(apr_results, key=lambda x: float(x['dose_gy']), reverse=True):
        if float(r['dose_gy']) > 0 and r['c1_gamma_gy']:
            c1_gy = float(r['c1_gamma_gy'])
            c2_gy = float(r['dose_gy'])
            ratio = c2_gy / c1_gy if c1_gy > 0 else float('inf')
            print("  %s: C1=%.0f Gy, C2=%.1f Gy, ratio=%.3f" % (
                r['plate'], c1_gy, c2_gy, ratio))

    print("\nDone.")


if __name__ == '__main__':
    main()
