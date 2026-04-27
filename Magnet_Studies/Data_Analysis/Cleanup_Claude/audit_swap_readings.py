#!/usr/bin/env python3
"""
Audit: find dosimetry-only swaps missing from the dose pipeline.

Scans all Teslameter zip files for badge serial numbers,
cross-references against plate_dose_map.csv to find (plate, date, badge)
entries that exist in zip data but NOT in the dose pipeline.

This catches cases like the Y-39 Sep 10 dosimetry-only swap.
"""

import os
import re
import csv
import zipfile
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OSL_DIR = os.path.join(BASE, 'Cleanup_Claude', 'Dosimetry', 'OSL_Area')

# All Teslameter zips
TESLAMETER_ZIPS = [
    os.path.join(BASE, 'July30Teslameterdata.zip'),
    os.path.join(BASE, 'Aug27teslameter.zip'),
    os.path.join(BASE, '21OctTeslameter.zip'),
    os.path.join(BASE, '2025-10-23_Teslameter.zip'),
    os.path.join(BASE, '2025-10-29_Teslameter.zip'),
    os.path.join(BASE, '20260108_Teslameter.zip'),
    os.path.join(BASE, '20260112_Teslameter.zip'),
]

# Also check Helmholtz zips for completeness
HELMHOLTZ_ZIPS = [
    os.path.join(BASE, 'July30Helmholtz.zip'),
    os.path.join(BASE, '082725_helmholtz.zip'),
    os.path.join(BASE, '102125_helmholtz.zip'),
    os.path.join(BASE, '2025-101-23_Helmholtz.zip'),
    os.path.join(BASE, 'Oct 29 Helmholtz.zip'),
    os.path.join(BASE, '20260108_Helmholtz.zip'),
    os.path.join(BASE, 'Jan_12_Helmholtz.zip'),
]


def extract_badges_from_zip(zip_path):
    """Extract (sample_name, date, badge) tuples from a zip file.

    Returns list of (sample_base, date_str, badge_serial, is_1337, zip_name)
    where sample_base is like 'Y-39-1' or 'Hn-10-2'.
    is_1337 = True if all measurement values are 1337 (dosimetry-only swap).
    """
    results = []
    if not os.path.exists(zip_path):
        print(f"  WARNING: {zip_path} not found")
        return results

    zip_name = os.path.basename(zip_path)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            fname = info.filename
            # Only process .dat files
            if not fname.endswith('.dat'):
                continue

            # Extract sample name from filename
            # e.g., "2025/Y-39-1_front.dat" -> "Y-39-1"
            bname = os.path.basename(fname)
            # Remove _front.dat, _top.dat, _side.dat, _helmholtz.dat suffixes
            sample = bname.replace('_front.dat', '').replace('_top.dat', '').replace('_side.dat', '')
            sample = sample.replace('_helmholtz.dat', '')

            # Only process Y-plates and H-plates (not lab)
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

                date_str = parts[0].strip()[:10]

                # Parse badge serial
                if len(parts) >= 5 and re.match(r'\d{4}-\d{2}-\d{2}$', date_str):
                    # New format: DATE TIME BADGE ROD VALUES...
                    badge = parts[2].strip()
                    values = parts[4:]
                elif len(parts) >= 4 and re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    # Old format: DATETIME BADGE ROD VALUES...
                    badge = parts[1].strip()
                    values = parts[3:]
                else:
                    continue

                if not (badge and badge.startswith('XA') and len(badge) == 11):
                    # Check for XnoDosimeter or other non-badge entries
                    if badge and 'nodosim' in badge.lower():
                        results.append((sample, date_str, 'NO_DOSIMETER', False, zip_name))
                    continue

                # Check if all values are 1337 (dosimetry-only swap)
                is_1337 = False
                try:
                    numeric_vals = [float(v) for v in values if v.strip()]
                    if numeric_vals and all(abs(v - 1337) < 0.1 for v in numeric_vals):
                        is_1337 = True
                except (ValueError, TypeError):
                    pass

                results.append((sample, date_str, badge, is_1337, zip_name))

    return results


def aggregate_to_plate(sample_name):
    """Convert sample name to plate name: Y-39-1 -> Y-39, Hn-10-2 -> Hn-10, etc."""
    ym = re.match(r'(Y-\d+)-\d+', sample_name)
    if ym:
        return ym.group(1)
    am = re.match(r'A([ns])-(\d+)-\d+-\d+', sample_name)
    if am:
        return f'H{am.group(1)}-{am.group(2)}'
    hm = re.match(r'(H[ns]-\d+)-\d+', sample_name)
    if hm:
        return hm.group(1)
    return sample_name


def main():
    print("=" * 70)
    print("Audit: Missed Swap-Only Readings")
    print("=" * 70)

    # 1. Load existing plate_dose_map
    dose_map_file = os.path.join(OSL_DIR, 'plate_dose_map.csv')
    existing = set()  # (plate, date)
    existing_badges = {}  # (plate, date) -> badge
    with open(dose_map_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['plate'], row['collection_date'])
            existing.add(key)
            existing_badges[key] = row['badge_serial']
    print(f"\nExisting plate_dose_map.csv: {len(existing)} (plate, date) entries")

    # 2. Extract all badges from Teslameter zips
    print("\n--- Scanning Teslameter Zips ---")
    all_zip_entries = []  # (sample, date, badge, is_1337, zip_name)

    for zpath in TESLAMETER_ZIPS:
        entries = extract_badges_from_zip(zpath)
        print(f"  {os.path.basename(zpath)}: {len(entries)} entries")
        all_zip_entries.extend(entries)

    # 3. Also scan Helmholtz zips
    print("\n--- Scanning Helmholtz Zips ---")
    for zpath in HELMHOLTZ_ZIPS:
        entries = extract_badges_from_zip(zpath)
        print(f"  {os.path.basename(zpath)}: {len(entries)} entries")
        all_zip_entries.extend(entries)

    # 4. Aggregate to plate level and find unique (plate, date, badge)
    zip_plate_dates = defaultdict(lambda: {'badges': set(), 'is_1337': False,
                                            'sources': set(), 'samples': set()})

    for sample, date, badge, is_1337, zip_name in all_zip_entries:
        plate = aggregate_to_plate(sample)
        key = (plate, date)
        info = zip_plate_dates[key]
        info['badges'].add(badge)
        info['sources'].add(zip_name)
        info['samples'].add(sample)
        if is_1337:
            info['is_1337'] = True

    print(f"\nUnique (plate, date) in zips: {len(zip_plate_dates)}")

    # 5. Find entries in zips but NOT in plate_dose_map
    print("\n" + "=" * 70)
    print("MISSING FROM DOSE PIPELINE:")
    print("=" * 70)

    missing = []
    for (plate, date), info in sorted(zip_plate_dates.items()):
        if (plate, date) not in existing:
            real_badges = [b for b in info['badges'] if b != 'NO_DOSIMETER']
            if real_badges:
                missing.append((plate, date, real_badges, info))
                swap_type = "DOSIMETRY-ONLY (1337)" if info['is_1337'] else "HAS MEASUREMENTS"
                print(f"  {plate:8s} @ {date}  badge={real_badges[0]}  "
                      f"[{swap_type}]  src={','.join(info['sources'])}")
            elif 'NO_DOSIMETER' in info['badges']:
                # No badge present — just a measurement without swap
                pass

    if not missing:
        print("  (none found — all zip entries are in the pipeline)")
    else:
        print(f"\n  TOTAL MISSING: {len(missing)} (plate, date) entries with badges")

    # 6. Check for badge mismatches (same plate+date, different badge)
    print("\n" + "=" * 70)
    print("BADGE MISMATCHES (same plate+date, different badge in zip vs pipeline):")
    print("=" * 70)

    mismatches = 0
    for (plate, date), info in sorted(zip_plate_dates.items()):
        if (plate, date) in existing:
            pipeline_badge = existing_badges[(plate, date)]
            real_badges = [b for b in info['badges'] if b != 'NO_DOSIMETER']
            for zb in real_badges:
                if zb != pipeline_badge:
                    mismatches += 1
                    print(f"  {plate:8s} @ {date}  pipeline={pipeline_badge}  zip={zb}  "
                          f"src={','.join(info['sources'])}")

    if mismatches == 0:
        print("  (none — all badges match)")

    # 7. Check for dates in pipeline NOT in any zip (orphan entries)
    print("\n" + "=" * 70)
    print("PIPELINE ENTRIES NOT IN ANY ZIP (may be from Helmholtz-only visits or manual):")
    print("=" * 70)

    zip_keys = set(zip_plate_dates.keys())
    orphans = 0
    for (plate, date) in sorted(existing):
        if (plate, date) not in zip_keys:
            badge = existing_badges[(plate, date)]
            orphans += 1
            if orphans <= 20:
                print(f"  {plate:8s} @ {date}  badge={badge}")
    if orphans > 20:
        print(f"  ... and {orphans - 20} more")
    if orphans == 0:
        print("  (none)")
    print(f"  Total: {orphans}")

    print("\nDone.")


if __name__ == '__main__':
    main()
