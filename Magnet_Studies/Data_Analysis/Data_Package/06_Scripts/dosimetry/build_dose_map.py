#!/usr/bin/env python3
"""
Build the plate → badge → Landauer dose mapping.

Reads:
  - .dat files (Helmholtz + Teslameter) for badge numbers per plate per date
  - master_doses.csv for badge → dose data
  - neutron_breakdown.csv for NT/NF split

Output:
  - Dosimetry/OSL_Area/plate_dose_map.csv — plate, date, badge, doses per collection
  - Dosimetry/OSL_Area/plate_cumulative_dose.csv — cumulative dose per plate
  - Dosimetry/OSL_Area/plate_dose_timeline.csv — date-by-date running totals per plate

Saturation handling:
  - InLight OSL saturates at 1000 rad (1,000,000 mrem) for photon/beta
  - When saturated_osl=True and body=0, we substitute 1,000,000 mrem as floor value
  - When neutron_exceeded=True, neutron values are lower bounds (floor unknown)
  - All saturated entries are flagged; cumulative doses are LOWER BOUNDS

Units: All doses in mrem (dose equivalent). See README.md for Gy conversion.
"""

import os
import re
import csv
import zipfile
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANUP = os.path.join(BASE, 'Cleanup_Claude')
OSL_DIR = os.path.join(CLEANUP, 'Dosimetry', 'OSL_Area')

# Teslameter zip files contain the full badge history for every plate, including
# dosimetry-only swaps (1337 values) where badges were pulled but no magnet measurement
# was taken. These swaps are NOT in the extracted .dat files in Cleanup_Claude/.
# We scan these zips to capture all badge swaps for the dose pipeline.
TESLAMETER_ZIPS = [
    os.path.join(BASE, 'July30Teslameterdata.zip'),
    os.path.join(BASE, 'Aug27teslameter.zip'),
    os.path.join(BASE, '21OctTeslameter.zip'),
    os.path.join(BASE, '2025-10-23_Teslameter.zip'),
    os.path.join(BASE, '2025-10-29_Teslameter.zip'),
    os.path.join(BASE, '20260108_Teslameter.zip'),
    os.path.join(BASE, '20260112_Teslameter.zip'),
]

def extract_badges_from_zips(zip_paths):
    """Extract badge numbers from Teslameter zip files.
    Each zip contains .dat files with the full history of readings per sample.
    Returns dict: sample_name -> {date: badge_serial}
    Only returns entries with valid XA-prefix badge serials (skips XnoDosimeter, etc.)."""
    result = defaultdict(dict)
    for zip_path in zip_paths:
        if not os.path.exists(zip_path):
            continue
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for info in zf.infolist():
                if info.is_dir() or not info.filename.endswith('.dat'):
                    continue
                bname = os.path.basename(info.filename)
                # Extract sample name: Y-39-1_front.dat -> Y-39-1
                sample = bname.replace('_front.dat', '').replace('_top.dat', '')
                sample = sample.replace('_side.dat', '').replace('_helmholtz.dat', '')
                # Only tunnel plates (Y, H, A)
                if not (sample.startswith('Y-') or sample.startswith('Hn-') or
                        sample.startswith('Hs-') or sample.startswith('An-') or
                        sample.startswith('As-')):
                    continue
                try:
                    data = zf.read(info.filename).decode('utf-8', errors='replace')
                except Exception:
                    continue
                for line in data.strip().split('\n'):
                    line = line.strip()
                    parts = line.split('\t')
                    if len(parts) < 3:
                        continue
                    date_str = parts[0].strip()[:10]
                    if len(parts) >= 5 and re.match(r'\d{4}-\d{2}-\d{2}$', date_str):
                        badge = parts[2].strip()
                    elif len(parts) >= 4 and re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                        badge = parts[1].strip()
                    else:
                        continue
                    if (badge and badge.startswith('XA') and len(badge) == 11
                            and 'odosim' not in badge.lower()
                            and 'odose' not in badge.lower()):
                        if sample not in result or date_str not in result[sample]:
                            result[sample][date_str] = badge
    return result


def extract_badges_from_dat(directory):
    """Extract badge numbers from .dat files.
    Returns dict: sample_name -> {date: badge_serial}"""
    result = defaultdict(dict)
    if not os.path.exists(directory):
        return result

    for fn in sorted(os.listdir(directory)):
        if not fn.endswith('.dat'):
            continue
        filepath = os.path.join(directory, fn)
        base = fn.replace('_helmholtz.dat', '').replace('_teslameter.dat', '')

        with open(filepath) as f:
            for line in f:
                line = line.strip()
                parts = line.split('\t')

                if len(parts) < 3:
                    continue

                date_str = parts[0].strip()[:10]

                # Badge is in field index 2 (for new format) or 1 (for old format)
                # New format: DATE TIME BADGE ROD FLUX...
                # Old format: DATETIME BADGE ROD FLUX...
                if len(parts) >= 5 and re.match(r'\d{4}-\d{2}-\d{2}$', date_str):
                    badge = parts[2].strip()
                elif len(parts) >= 4 and re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    badge = parts[1].strip()
                else:
                    continue

                if (badge and badge.startswith('XA') and len(badge) == 11
                        and 'odosim' not in badge.lower()
                        and 'odose' not in badge.lower()):
                    result[base][date_str] = badge

    return result


def load_landauer_by_badge(master_csv):
    """Load Landauer data indexed by badge serial number.
    Returns dict: badge_serial -> list of dose records"""
    by_badge = defaultdict(list)
    with open(master_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            badge = row['badge_number'].strip()
            if badge:
                by_badge[badge].append(row)
    return by_badge


def load_neutron_breakdown(neutron_csv):
    """Load neutron NT/NF data indexed by (report_date, part_nbr).
    Returns dict: (report_date, part_nbr) -> {nt_mrem, nf_mrem}"""
    result = {}
    if not os.path.exists(neutron_csv):
        return result
    with open(neutron_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['report_date'], int(row['part_nbr']))
            result[key] = {
                'nt_mrem': int(row['nt_mrem']),
                'nf_mrem': int(row['nf_mrem']),
            }
    return result


def aggregate_to_plate(sample_badges):
    """Aggregate per-slot/per-assembly badge data to plate level.
    Y-1-1, Y-1-2, Y-1-3, Y-1-4 all -> Y-1
    An-10-1-1, An-10-1-2, etc. all -> Hn-10 (H-plate level)
    """
    plate_badges = defaultdict(dict)  # plate -> {date: badge}

    for sample, dates in sample_badges.items():
        # Y-plate: Y-NN-S -> Y-NN
        ym = re.match(r'(Y-\d+)-\d+', sample)
        if ym:
            plate = ym.group(1)
            for date, badge in dates.items():
                plate_badges[plate][date] = badge
            continue

        # A-sample: An-NN-S-A or As-NN-S-A -> Hn-NN or Hs-NN
        am = re.match(r'A([ns])-(\d+)-\d+-\d+', sample)
        if am:
            plate = f'H{am.group(1)}-{am.group(2)}'
            for date, badge in dates.items():
                plate_badges[plate][date] = badge
            continue

        # H-plate: Hn-NN-S or Hs-NN-S -> Hn-NN or Hs-NN
        hm = re.match(r'(H[ns]-\d+)-\d+', sample)
        if hm:
            plate = hm.group(1)
            for date, badge in dates.items():
                plate_badges[plate][date] = badge
            continue

    return plate_badges


def main():
    print("=" * 70)
    print("Plate → Badge → Dose Mapping Builder")
    print("=" * 70)

    # 1. Extract badges from all .dat files
    print("\nExtracting badges from .dat files...")
    all_badges = {}

    dirs = [
        ('Y Helmholtz', os.path.join(CLEANUP, 'Y_Plates', 'Helmholtz')),
        ('Y Teslameter', os.path.join(CLEANUP, 'Y_Plates', 'Teslameter')),
        ('H Helmholtz', os.path.join(CLEANUP, 'Pair_Assemblies', 'Helmholtz')),
        ('H Teslameter', os.path.join(CLEANUP, 'Pair_Assemblies', 'Teslameter')),
    ]

    for label, d in dirs:
        badges = extract_badges_from_dat(d)
        print(f"  {label}: {len(badges)} samples with badges")
        # Merge (prefer Helmholtz entries)
        for sample, dates in badges.items():
            if sample not in all_badges:
                all_badges[sample] = {}
            for date, badge in dates.items():
                if date not in all_badges[sample]:
                    all_badges[sample][date] = badge

    # 1b. Extract badges from Teslameter zip files (captures dosimetry-only swaps)
    print("\nExtracting badges from Teslameter zip files...")
    zip_badges = extract_badges_from_zips(TESLAMETER_ZIPS)
    zip_sample_count = len(zip_badges)
    zip_new_entries = 0
    for sample, dates in zip_badges.items():
        if sample not in all_badges:
            all_badges[sample] = {}
        for date, badge in dates.items():
            if date not in all_badges[sample]:
                all_badges[sample][date] = badge
                zip_new_entries += 1
    print(f"  Zip samples: {zip_sample_count}, new (plate,date) entries: {zip_new_entries}")

    # 2. Aggregate to plate level
    plate_badges = aggregate_to_plate(all_badges)
    print(f"\nPlates with badge data: {len(plate_badges)}")

    y_plates = {k: v for k, v in plate_badges.items() if k.startswith('Y-')}
    h_plates = {k: v for k, v in plate_badges.items() if k.startswith('H')}
    print(f"  Y-plates: {len(y_plates)}")
    print(f"  H-plates: {len(h_plates)}")

    # 3. Load Landauer data
    print("\nLoading Landauer dose data...")
    master_csv = os.path.join(OSL_DIR, 'master_doses.csv')
    by_badge = load_landauer_by_badge(master_csv)
    print(f"  Unique badges in Landauer: {len(by_badge)}")

    neutron_csv = os.path.join(OSL_DIR, 'neutron_breakdown.csv')
    neutron_data = load_neutron_breakdown(neutron_csv)
    print(f"  Neutron breakdown entries: {len(neutron_data)}")

    # Saturation ceiling values (mrem)
    OSL_SATURATION_MREM = 1_000_000  # 1000 rad for InLight OSL (photon/beta)
    # CR-39 neutron saturation limit is less well-defined; flag but don't substitute

    # 4. Cross-reference: plate date badge -> Landauer dose
    print("\nCross-referencing...")
    matched = 0
    unmatched_badges = set()
    plate_dose_rows = []

    for plate in sorted(plate_badges.keys()):
        dates = plate_badges[plate]
        for date in sorted(dates.keys()):
            badge = dates[date]

            # Find in Landauer data
            landauer_records = by_badge.get(badge, [])

            if not landauer_records:
                unmatched_badges.add(badge)
                # Unmatched = likely from a report we don't have; record as unknown
                plate_dose_rows.append({
                    'plate': plate,
                    'collection_date': date,
                    'badge_serial': badge,
                    'landauer_part_nbr': '',
                    'landauer_report_date': '',
                    'begin_wear': '',
                    'end_wear': '',
                    'body_mrem': 0,
                    'skin_mrem': 0,
                    'eye_mrem': 0,
                    'beta_mrem': 0,
                    'neutron_mrem': 0,
                    'nt_mrem': 0,
                    'nf_mrem': 0,
                    'photon_mrem': 0,
                    'exceeded_1000rad': False,
                    'saturated_osl': False,
                    'neutron_exceeded': False,
                    'dose_status': 'NO_MATCH',
                })
                continue

            matched += 1

            # Use the WHOLEBODY record (not CONTROL)
            wb_records = [r for r in landauer_records
                         if r['badge_location'] == 'WHOLEBODY']
            if not wb_records:
                wb_records = landauer_records

            # If multiple records (same badge in multiple reports), pick the one
            # with the highest body dose (most complete reading)
            best = max(wb_records, key=lambda r: int(r['body_mrem']))

            # Get neutron breakdown
            part_nbr = int(best['part_nbr']) if best['part_nbr'] else 0
            report_date = best['report_date']
            nt_nf = neutron_data.get((report_date, part_nbr), {'nt_mrem': 0, 'nf_mrem': 0})

            body = int(best['body_mrem'])
            neutron = int(best['neutron_mrem'])
            beta = int(best['beta_mrem'])
            exceeded = best['exceeded_1000rad'] == 'True'
            saturated = best['saturated_osl'] == 'True'
            neutron_exc = best['neutron_exceeded'] == 'True'

            # Handle saturation: if OSL saturated (body=0 + exceeded), use ceiling
            # EXCEEDED_PARTIAL: Landauer reports body>0 with exceeded flag, but the
            # reported "body" is actually just the CR-39 neutron reading (photon OSL
            # is completely saturated). We must add the 1M mrem photon floor.
            if saturated and body == 0:
                body = OSL_SATURATION_MREM
                dose_status = 'SATURATED_FLOOR'
            elif exceeded and body > 0:
                # OSL saturated, but CR-39 gave a neutron reading.
                # The reported body == neutron (100% of cases in our data).
                # Add 1M mrem photon floor on top of the neutron reading.
                body = body + OSL_SATURATION_MREM
                dose_status = 'EXCEEDED_PARTIAL'
            elif neutron_exc and body == 0:
                # Only neutron exceeded, no photon reading
                dose_status = 'NEUTRON_SATURATED'
            else:
                dose_status = 'MEASURED'

            # Photon dose = body - neutron - beta (approximate)
            # For saturated/exceeded: photon is unknown (OSL dead), so mark as -1
            if dose_status in ('SATURATED_FLOOR', 'EXCEEDED_PARTIAL'):
                photon_approx = -1  # Unknown — OSL completely saturated
            else:
                photon_approx = max(0, body - neutron - beta)

            plate_dose_rows.append({
                'plate': plate,
                'collection_date': date,
                'badge_serial': badge,
                'landauer_part_nbr': part_nbr,
                'landauer_report_date': report_date,
                'begin_wear': best['begin_wear'],
                'end_wear': best['end_wear'],
                'body_mrem': body,
                'skin_mrem': int(best['skin_mrem']),
                'eye_mrem': int(best['eye_mrem']),
                'beta_mrem': beta,
                'neutron_mrem': neutron,
                'nt_mrem': nt_nf['nt_mrem'],
                'nf_mrem': nt_nf['nf_mrem'],
                'photon_mrem': photon_approx,
                'exceeded_1000rad': exceeded,
                'saturated_osl': saturated,
                'neutron_exceeded': neutron_exc,
                'dose_status': dose_status,
            })

    print(f"  Matched: {matched}")
    print(f"  Unmatched badges: {len(unmatched_badges)}")
    if unmatched_badges:
        print(f"  Examples: {list(unmatched_badges)[:5]}")

    # 5. Build date-by-date cumulative timeline per plate
    print("\n--- Building Date-by-Date Cumulative Timeline ---")
    # Group rows by plate, sort by date
    by_plate = defaultdict(list)
    for row in plate_dose_rows:
        by_plate[row['plate']].append(row)

    timeline_rows = []
    cumulative = {}

    for plate in sorted(by_plate.keys(),
                        key=lambda x: (x[0], int(re.search(r'\d+', x).group()))):
        rows = sorted(by_plate[plate], key=lambda r: r['collection_date'])
        running = {
            'body': 0, 'photon': 0, 'beta': 0,
            'neutron': 0, 'nt': 0, 'nf': 0,
            'n_badges': 0, 'n_matched': 0, 'n_saturated': 0,
            'n_exceeded': 0, 'n_neutron_exc': 0,
        }

        for row in rows:
            running['body'] += row['body_mrem']
            # photon_mrem = -1 means unknown (saturated); add 0 to cumulative,
            # but track that cumulative photon is a lower bound
            if row['photon_mrem'] >= 0:
                running['photon'] += row['photon_mrem']
            running['beta'] += row['beta_mrem']
            running['neutron'] += row['neutron_mrem']
            running['nt'] += row['nt_mrem']
            running['nf'] += row['nf_mrem']
            running['n_badges'] += 1
            if row['dose_status'] != 'NO_MATCH':
                running['n_matched'] += 1
            if row['saturated_osl'] or row['dose_status'] == 'EXCEEDED_PARTIAL':
                running['n_saturated'] += 1
            if row['exceeded_1000rad']:
                running['n_exceeded'] += 1
            if row['neutron_exceeded']:
                running['n_neutron_exc'] += 1

            timeline_rows.append({
                'plate': plate,
                'collection_date': row['collection_date'],
                'this_body_mrem': row['body_mrem'],
                'this_photon_mrem': row['photon_mrem'],
                'this_beta_mrem': row['beta_mrem'],
                'this_neutron_mrem': row['neutron_mrem'],
                'this_nt_mrem': row['nt_mrem'],
                'this_nf_mrem': row['nf_mrem'],
                'this_dose_status': row['dose_status'],
                'cum_body_mrem': running['body'],
                'cum_photon_mrem': running['photon'],
                'cum_beta_mrem': running['beta'],
                'cum_neutron_mrem': running['neutron'],
                'cum_nt_mrem': running['nt'],
                'cum_nf_mrem': running['nf'],
                'cum_n_badges': running['n_badges'],
                'cum_n_saturated': running['n_saturated'],
                'is_lower_bound': running['n_saturated'] > 0,
            })

        # Save final cumulative for summary
        ptype = 'Y' if plate.startswith('Y-') else ('Hn' if 'n' in plate else 'Hs')
        cumulative[plate] = {**running, 'plate_type': ptype,
                             'dates': [r['collection_date'] for r in rows]}

    # Print Y-plates summary
    print("\nY-Plates (cumulative body dose, mrem — with saturation floor applied):")
    for plate in sorted(cumulative.keys(),
                        key=lambda x: (x[0], int(re.search(r'\d+', x).group()))):
        if not plate.startswith('Y-'):
            continue
        c = cumulative[plate]
        lb = " [LOWER BOUND]" if c['n_saturated'] > 0 else ""
        sat = f" ({c['n_saturated']}x sat)" if c['n_saturated'] > 0 else ""
        print(f"  {plate}: {c['body']:>12,} mrem body, "
              f"{c['photon']:>12,} photon, "
              f"{c['neutron']:>8,} neutron "
              f"({c['n_matched']}/{c['n_badges']} matched){sat}{lb}")

    # Print H-plates NdFeB (top 10)
    print("\nH-Plates NdFeB (top 10 by body dose):")
    hn = sorted([(k, v) for k, v in cumulative.items() if k.startswith('Hn-')],
                key=lambda x: -x[1]['body'])
    for plate, c in hn[:10]:
        lb = " [LB]" if c['n_saturated'] > 0 else ""
        print(f"  {plate}: {c['body']:>12,} mrem body{lb}")

    # 6. Write output files
    print("\n--- Writing Output Files ---")

    # Per-plate-per-date detail
    detail_csv = os.path.join(OSL_DIR, 'plate_dose_map.csv')
    fieldnames = [
        'plate', 'collection_date', 'badge_serial',
        'landauer_part_nbr', 'landauer_report_date',
        'begin_wear', 'end_wear',
        'body_mrem', 'skin_mrem', 'eye_mrem', 'beta_mrem',
        'neutron_mrem', 'nt_mrem', 'nf_mrem', 'photon_mrem',
        'exceeded_1000rad', 'saturated_osl', 'neutron_exceeded',
        'dose_status',
    ]
    with open(detail_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(plate_dose_rows,
                          key=lambda r: (r['plate'], r['collection_date'])):
            writer.writerow(row)
    print(f"  {detail_csv}: {len(plate_dose_rows)} rows")

    # Date-by-date timeline (running cumulative)
    timeline_csv = os.path.join(OSL_DIR, 'plate_dose_timeline.csv')
    tl_fields = [
        'plate', 'collection_date',
        'this_body_mrem', 'this_photon_mrem', 'this_beta_mrem',
        'this_neutron_mrem', 'this_nt_mrem', 'this_nf_mrem',
        'this_dose_status',
        'cum_body_mrem', 'cum_photon_mrem', 'cum_beta_mrem',
        'cum_neutron_mrem', 'cum_nt_mrem', 'cum_nf_mrem',
        'cum_n_badges', 'cum_n_saturated', 'is_lower_bound',
    ]
    with open(timeline_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=tl_fields)
        writer.writeheader()
        writer.writerows(timeline_rows)
    print(f"  {timeline_csv}: {len(timeline_rows)} rows")

    # Cumulative per plate (final totals)
    cum_csv = os.path.join(OSL_DIR, 'plate_cumulative_dose.csv')
    cum_fields = [
        'plate', 'plate_type', 'n_badges', 'n_matched', 'n_saturated',
        'n_exceeded', 'n_neutron_exc', 'collection_dates',
        'body_mrem', 'photon_mrem', 'beta_mrem',
        'neutron_mrem', 'nt_mrem', 'nf_mrem',
        'is_lower_bound',
    ]
    cum_rows = []
    for plate in sorted(cumulative.keys(),
                        key=lambda x: (x[0], int(re.search(r'\d+', x).group()))):
        c = cumulative[plate]
        cum_rows.append({
            'plate': plate,
            'plate_type': c['plate_type'],
            'n_badges': c['n_badges'],
            'n_matched': c['n_matched'],
            'n_saturated': c['n_saturated'],
            'n_exceeded': c['n_exceeded'],
            'n_neutron_exc': c['n_neutron_exc'],
            'collection_dates': ';'.join(c['dates']),
            'body_mrem': c['body'],
            'photon_mrem': c['photon'],
            'beta_mrem': c['beta'],
            'neutron_mrem': c['neutron'],
            'nt_mrem': c['nt'],
            'nf_mrem': c['nf'],
            'is_lower_bound': c['n_saturated'] > 0,
        })

    with open(cum_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cum_fields)
        writer.writeheader()
        writer.writerows(cum_rows)
    print(f"  {cum_csv}: {len(cum_rows)} rows")

    # Summary
    total_badges = sum(c['n_badges'] for c in cumulative.values())
    total_matched = sum(c['n_matched'] for c in cumulative.values())
    n_sat_plates = sum(1 for c in cumulative.values() if c['n_saturated'] > 0)
    print(f"\n  Total plate-date entries: {total_badges}")
    print(f"  Matched to Landauer: {total_matched} ({100*total_matched/total_badges:.1f}%)")
    print(f"  Plates with saturated dosimeters: {n_sat_plates}/{len(cumulative)} "
          f"(cumulative doses are LOWER BOUNDS)")

    print("\nDone.")


if __name__ == '__main__':
    main()
