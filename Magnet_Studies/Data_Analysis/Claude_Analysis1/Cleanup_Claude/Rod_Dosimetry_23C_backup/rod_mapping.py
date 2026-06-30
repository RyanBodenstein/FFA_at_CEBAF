#!/usr/bin/env python3
"""
Phase 1: Build R-### → Plate mapping from Teslameter/Helmholtz .dat files.

Scans all .dat files (extracted dirs + zip archives) to find which rod was
on which sample at which measurement date. Aggregates to plate level.

Output:
  Rod_Dosimetry/rod_plate_map.csv — (plate, date, rod_id, sample_source)

Follows patterns from build_dose_map.py.
"""

import os
import re
import csv
import zipfile
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEANUP = os.path.join(BASE, 'Cleanup_Claude')
OUT_DIR = os.path.join(CLEANUP, 'Rod_Dosimetry')
os.makedirs(OUT_DIR, exist_ok=True)

# Same zip list as build_dose_map.py
TESLAMETER_ZIPS = [
    os.path.join(BASE, 'July30Teslameterdata.zip'),
    os.path.join(BASE, 'Aug27teslameter.zip'),
    os.path.join(BASE, '21OctTeslameter.zip'),
    os.path.join(BASE, '2025-10-23_Teslameter.zip'),
    os.path.join(BASE, '2025-10-29_Teslameter.zip'),
    os.path.join(BASE, '20260108_Teslameter.zip'),
    os.path.join(BASE, '20260112_Teslameter.zip'),
]

# Rod sentinels — these mean "no rod installed"
ROD_SENTINELS = {'rnorod', 'rnorod ', 'rnord', ''}


def extract_rod_from_parts(parts):
    """Extract rod ID from a parsed .dat line.

    Returns normalized 'R-###' string or None.

    Format variations:
      Old (7 cols): datetime  badge  rod  data...
      New (8 cols): date  time  badge  rod  data...
      Old Helmholtz (4 cols): datetime  badge  rod  field
      New Helmholtz (5 cols): date  time  badge  rod  field
    """
    date_str = parts[0].strip()

    # Determine format by column count and date pattern
    if len(parts) >= 8 and re.match(r'\d{4}-\d{2}-\d{2}$', date_str[:10]):
        # New format: date time badge rod data...
        rod_raw = parts[3].strip()
    elif len(parts) >= 5 and re.match(r'\d{4}-\d{2}-\d{2}$', date_str[:10]):
        # New Helmholtz: date time badge rod field
        rod_raw = parts[3].strip()
    elif len(parts) >= 7 and re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        # Old Teslameter: datetime badge rod data...
        rod_raw = parts[2].strip()
    elif len(parts) >= 4 and re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        # Old Helmholtz: datetime badge rod field
        rod_raw = parts[2].strip()
    else:
        return None, None

    # Extract date (first 10 chars)
    date_out = date_str[:10]

    # Check for sentinel
    if rod_raw.lower().strip() in ROD_SENTINELS:
        return date_out, None

    # Normalize: expect R-### pattern
    m = re.match(r'R-?(\d+)', rod_raw, re.IGNORECASE)
    if m:
        return date_out, 'R-%s' % m.group(1)

    return date_out, None


def extract_rods_from_dat(directory):
    """Extract rod IDs from .dat files in a directory.
    Only uses _top.dat files to avoid duplicate counting.
    For Helmholtz, uses _helmholtz.dat.

    Returns dict: sample_name -> {date: rod_id}
    """
    result = defaultdict(dict)
    if not os.path.exists(directory):
        return result

    for fn in sorted(os.listdir(directory)):
        if not fn.endswith('.dat'):
            continue
        # Use _top.dat for Teslameter, _helmholtz.dat for Helmholtz
        # Skip _front.dat and _side.dat to avoid duplicates
        if '_front.dat' in fn or '_side.dat' in fn:
            continue

        filepath = os.path.join(directory, fn)
        # Extract sample name
        sample = fn.replace('_top.dat', '').replace('_helmholtz.dat', '')
        sample = sample.replace('_teslameter.dat', '')

        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('\t')
                if len(parts) < 3:
                    continue

                date_str, rod_id = extract_rod_from_parts(parts)
                if date_str and rod_id:
                    result[sample][date_str] = rod_id

    return result


def extract_rods_from_zips(zip_paths):
    """Extract rod IDs from Teslameter zip files.
    Only reads _top.dat files (or _helmholtz.dat if no _top).

    Returns dict: sample_name -> {date: rod_id}
    """
    result = defaultdict(dict)
    for zip_path in zip_paths:
        if not os.path.exists(zip_path):
            continue
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                bname = os.path.basename(info.filename)
                if not bname.endswith('.dat'):
                    continue
                # Only _top.dat to avoid duplicates
                if '_front.dat' in bname or '_side.dat' in bname:
                    continue

                # Extract sample name
                sample = bname.replace('_top.dat', '').replace('_helmholtz.dat', '')
                sample = sample.replace('_teslameter.dat', '')

                # Only tunnel plates
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
                    if not line:
                        continue
                    parts = line.split('\t')
                    if len(parts) < 3:
                        continue

                    date_str, rod_id = extract_rod_from_parts(parts)
                    if date_str and rod_id:
                        if date_str not in result[sample]:
                            result[sample][date_str] = rod_id

    return result


def aggregate_to_plate(sample_rods):
    """Aggregate per-slot rod data to plate level.
    Y-1-1, Y-1-2, ... -> Y-1
    An-10-1-1, An-10-1-2, ... -> Hn-10
    Hn-6-1, Hn-6-2, ... -> Hn-6
    """
    plate_rods = defaultdict(dict)  # plate -> {date: rod_id}

    for sample, dates in sample_rods.items():
        # Y-plate: Y-NN-S -> Y-NN
        ym = re.match(r'(Y-\d+)-\d+', sample)
        if ym:
            plate = ym.group(1)
            for date, rod in dates.items():
                if date not in plate_rods[plate]:
                    plate_rods[plate][date] = rod
            continue

        # A-sample: An-NN-S-A or As-NN-S-A -> Hn-NN or Hs-NN
        am = re.match(r'A([ns])-(\d+)-\d+-\d+', sample)
        if am:
            plate = 'H%s-%s' % (am.group(1), am.group(2))
            for date, rod in dates.items():
                if date not in plate_rods[plate]:
                    plate_rods[plate][date] = rod
            continue

        # H-plate: Hn-NN-S or Hs-NN-S -> Hn-NN or Hs-NN
        hm = re.match(r'(H[ns]-\d+)-\d+', sample)
        if hm:
            plate = hm.group(1)
            for date, rod in dates.items():
                if date not in plate_rods[plate]:
                    plate_rods[plate][date] = rod
            continue

    return plate_rods


def main():
    print("=" * 70)
    print("Phase 1: R-### -> Plate Mapping Builder")
    print("=" * 70)

    # 1. Extract rods from extracted .dat files
    print("\nExtracting rods from .dat files...")
    all_rods = {}

    dirs = [
        ('Y Helmholtz', os.path.join(CLEANUP, 'Y_Plates', 'Helmholtz')),
        ('Y Teslameter', os.path.join(CLEANUP, 'Y_Plates', 'Teslameter')),
        ('H Helmholtz', os.path.join(CLEANUP, 'Pair_Assemblies', 'Helmholtz')),
        ('H Teslameter', os.path.join(CLEANUP, 'Pair_Assemblies', 'Teslameter')),
    ]

    for label, d in dirs:
        rods = extract_rods_from_dat(d)
        n_rods = sum(len(v) for v in rods.values())
        print("  %s: %d samples, %d (sample,date) rod entries" % (label, len(rods), n_rods))
        for sample, dates in rods.items():
            if sample not in all_rods:
                all_rods[sample] = {}
            for date, rod in dates.items():
                if date not in all_rods[sample]:
                    all_rods[sample][date] = rod

    # 2. Extract rods from Teslameter zips
    print("\nExtracting rods from Teslameter zip files...")
    zip_rods = extract_rods_from_zips(TESLAMETER_ZIPS)
    zip_new = 0
    for sample, dates in zip_rods.items():
        if sample not in all_rods:
            all_rods[sample] = {}
        for date, rod in dates.items():
            if date not in all_rods[sample]:
                all_rods[sample][date] = rod
                zip_new += 1
    print("  Zip samples: %d, new (sample,date) entries: %d" % (len(zip_rods), zip_new))

    # 3. Collect all unique R-### IDs
    all_rod_ids = set()
    for sample, dates in all_rods.items():
        for rod in dates.values():
            all_rod_ids.add(rod)

    print("\n--- Rod Summary ---")
    print("  Unique R-### IDs found: %d" % len(all_rod_ids))
    print("  Rod ID range: %s to %s" % (
        min(all_rod_ids, key=lambda r: int(r.split('-')[1])),
        max(all_rod_ids, key=lambda r: int(r.split('-')[1])),
    ))

    # 4. Aggregate to plate level
    plate_rods = aggregate_to_plate(all_rods)

    y_plates = sorted([k for k in plate_rods if k.startswith('Y-')],
                       key=lambda x: int(x.split('-')[1]))
    hn_plates = sorted([k for k in plate_rods if k.startswith('Hn-')],
                        key=lambda x: int(x.split('-')[1]))
    hs_plates = sorted([k for k in plate_rods if k.startswith('Hs-')],
                        key=lambda x: int(x.split('-')[1]))

    print("  Y-plates with rods: %d" % len(y_plates))
    print("  Hn-plates with rods: %d" % len(hn_plates))
    print("  Hs-plates with rods: %d" % len(hs_plates))

    # 5. Write rod_plate_map.csv
    rows = []
    for plate in sorted(plate_rods.keys(),
                        key=lambda x: (x[0], int(re.search(r'\d+', x).group()))):
        dates = plate_rods[plate]
        for date in sorted(dates.keys()):
            rows.append({
                'plate': plate,
                'date': date,
                'rod_id': dates[date],
            })

    out_csv = os.path.join(OUT_DIR, 'rod_plate_map.csv')
    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['plate', 'date', 'rod_id'])
        writer.writeheader()
        writer.writerows(rows)
    print("\n  Wrote %s (%d rows)" % (out_csv, len(rows)))

    # 6. Print sample of mapping for verification
    print("\n--- Sample Y-plate rod timeline ---")
    for plate in y_plates[:5]:
        dates = sorted(plate_rods[plate].items())
        rods_str = ', '.join('%s:%s' % (d, r) for d, r in dates)
        print("  %s: %s" % (plate, rods_str))

    # 7. Report rod swap statistics
    print("\n--- Rod Swap Statistics ---")
    swap_dates = set()
    for plate, dates in plate_rods.items():
        for d in dates:
            swap_dates.add(d)
    swap_dates = sorted(swap_dates)
    print("  Unique swap dates: %d" % len(swap_dates))
    for d in swap_dates:
        n_plates = sum(1 for p in plate_rods if d in plate_rods[p])
        print("    %s: %d plates" % (d, n_plates))

    print("\nDone.")
    return all_rod_ids, plate_rods


if __name__ == '__main__':
    all_rod_ids, plate_rods = main()
