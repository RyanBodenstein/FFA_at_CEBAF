#!/usr/bin/env python3
"""
Extract C2 rod-to-plate mapping from April 2026 Teslameter .dat files.

Methodology: Same as C1 (rod_mapping.py). Each .dat file records the rod ID
and badge serial alongside the plate/sample name. We extract the 2026-04-20
entries to find which rods (R-741 to R-800) were installed on which plates.

Also extracts January 2026 entries (C1-final rods, R-681-R-740) and badge
serials for OSL cross-referencing.

Output:
  Analysis/c2_rod_plate_map.csv
  Analysis/c2_badge_plate_map.csv
"""

import os
import re
import csv
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
DAT_DIR = os.path.join(BASE, '2026-04-20_Teslameter')
OUT_DIR = os.path.join(BASE, 'Analysis')
os.makedirs(OUT_DIR, exist_ok=True)

# Sentinels for "no rod" or "no dosimeter"
ROD_SENTINELS = {'rnorod', 'rnorod ', 'rnord', 'norod', ''}
BADGE_SENTINELS = {'xnodose', 'xnodosimeter', 'notld', 'noTLD', ''}


def parse_dat_line(line):
    """Parse a .dat file line. Returns (date, badge, rod) or None."""
    line = line.strip()
    if not line:
        return None
    parts = line.split('\t')
    if len(parts) < 4:
        return None

    date_str = parts[0].strip()

    # New format: date<tab>time<tab>badge<tab>rod<tab>data...
    if re.match(r'\d{4}-\d{2}-\d{2}$', date_str):
        date_out = date_str
        badge_raw = parts[2].strip() if len(parts) > 2 else ''
        rod_raw = parts[3].strip() if len(parts) > 3 else ''
    # Old format: datetime<tab>badge<tab>rod<tab>data...
    elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        date_out = date_str[:10]
        badge_raw = parts[1].strip() if len(parts) > 1 else ''
        rod_raw = parts[2].strip() if len(parts) > 2 else ''
    else:
        return None

    # Normalize badge
    badge = None
    if badge_raw and badge_raw.lower() not in {s.lower() for s in BADGE_SENTINELS}:
        badge = badge_raw

    # Normalize rod
    rod = None
    if rod_raw.lower().strip() not in ROD_SENTINELS:
        m = re.match(r'R-?(\d+)', rod_raw, re.IGNORECASE)
        if m:
            rod = 'R-%s' % m.group(1)

    return date_out, badge, rod


def extract_from_dat_files():
    """Extract rod and badge mappings from all Y-plate _top.dat files.

    Returns:
        rod_map: {plate: {date: rod_id}}
        badge_map: {plate: {date: badge_serial}}
    """
    rod_map = defaultdict(dict)    # plate -> {date: rod}
    badge_map = defaultdict(dict)  # plate -> {date: badge}

    if not os.path.exists(DAT_DIR):
        print("ERROR: Directory not found: %s" % DAT_DIR)
        return rod_map, badge_map

    for fn in sorted(os.listdir(DAT_DIR)):
        # Only use _top.dat to avoid duplicate counting
        if not fn.endswith('_top.dat'):
            continue
        # Accept Y-plates, H-plates (Hn-, Hs-)
        if not (fn.startswith('Y-') or fn.startswith('Hn-') or fn.startswith('Hs-')):
            continue

        sample = fn.replace('_top.dat', '')  # e.g., Y-1-1 or Hn-20-1
        # Extract plate name
        # Y-NN-S -> Y-NN
        pm = re.match(r'(Y-\d+)-\d+', sample)
        if not pm:
            # Hn-NN-S -> Hn-NN, Hs-NN-S -> Hs-NN
            pm = re.match(r'(H[ns]-\d+)-\d+', sample)
        if not pm:
            continue
        plate = pm.group(1)

        filepath = os.path.join(DAT_DIR, fn)
        with open(filepath, 'rb') as f:
            content = f.read().decode('utf-8', errors='replace')

        for line in content.split('\n'):
            result = parse_dat_line(line)
            if result is None:
                continue
            date_out, badge, rod = result

            # Only keep 2026 entries (Jan and Apr)
            if not date_out.startswith('2026'):
                continue

            if rod and date_out not in rod_map[plate]:
                rod_map[plate][date_out] = rod

            if badge and date_out not in badge_map[plate]:
                badge_map[plate][date_out] = badge

    return rod_map, badge_map


def main():
    print("=" * 70)
    print("C2 Rod-to-Plate Mapping Extractor")
    print("=" * 70)

    rod_map, badge_map = extract_from_dat_files()

    # Separate by date
    jan_rods = {}  # plate -> rod (Jan 2026, C1-final rods)
    apr_rods = {}  # plate -> rod (Apr 2026, C2-new rods)
    jan_badges = {}
    apr_badges = {}

    for plate, dates in rod_map.items():
        for date, rod in dates.items():
            if date.startswith('2026-01'):
                jan_rods[plate] = rod
            elif date.startswith('2026-04'):
                apr_rods[plate] = rod

    for plate, dates in badge_map.items():
        for date, badge in dates.items():
            if date.startswith('2026-01'):
                jan_badges[plate] = badge
            elif date.startswith('2026-04'):
                apr_badges[plate] = badge

    # Report
    print("\n--- January 2026 (C1-final rods, R-681-740) ---")
    print("  Plates with rods: %d" % len(jan_rods))
    if jan_rods:
        rod_nums = [int(r.split('-')[1]) for r in jan_rods.values()]
        print("  Rod range: R-%d to R-%d" % (min(rod_nums), max(rod_nums)))
    print("  Plates with badges: %d" % len(jan_badges))

    print("\n--- April 2026 (C2-new rods, R-741-800) ---")
    print("  Plates with rods: %d" % len(apr_rods))
    if apr_rods:
        rod_nums = [int(r.split('-')[1]) for r in apr_rods.values()]
        print("  Rod range: R-%d to R-%d" % (min(rod_nums), max(rod_nums)))
    print("  Plates with badges: %d" % len(apr_badges))

    # Print full April mapping
    print("\n--- Full C2 Rod-Plate Mapping (April 2026) ---")
    for plate in sorted(apr_rods.keys(), key=lambda x: int(x.split('-')[1])):
        badge = apr_badges.get(plate, 'N/A')
        print("  %s: rod=%s, badge=%s" % (plate, apr_rods[plate], badge))

    # Check for plates without April rods
    all_tunnel_plates = set('Y-%d' % i for i in range(1, 31))
    # Lab plates: 8, 14, 27-29, 31, 33, 35, 37
    lab_plates = {'Y-8', 'Y-14', 'Y-27', 'Y-28', 'Y-29', 'Y-31', 'Y-33', 'Y-35', 'Y-37'}
    tunnel_plates = all_tunnel_plates - lab_plates
    # Also Y-32 through Y-40 not in lab set are tunnel
    for i in range(32, 41):
        p = 'Y-%d' % i
        if p not in lab_plates:
            tunnel_plates.add(p)

    missing = tunnel_plates - set(apr_rods.keys())
    if missing:
        print("\n  WARNING: Tunnel plates without April rod mapping:")
        for p in sorted(missing, key=lambda x: int(x.split('-')[1])):
            print("    %s" % p)

    # Also check January mapping
    print("\n--- Full January Rod-Plate Mapping (C1-final) ---")
    for plate in sorted(jan_rods.keys(), key=lambda x: int(x.split('-')[1])):
        badge = jan_badges.get(plate, 'N/A')
        print("  %s: rod=%s, badge=%s" % (plate, jan_rods[plate], badge))

    # Write CSV: combined rod_plate_map
    rows = []
    all_plates = sorted(set(list(jan_rods.keys()) + list(apr_rods.keys())),
                        key=lambda x: int(x.split('-')[1]))
    for plate in all_plates:
        row = {
            'plate': plate,
            'jan_rod': jan_rods.get(plate, ''),
            'jan_badge': jan_badges.get(plate, ''),
            'apr_rod': apr_rods.get(plate, ''),
            'apr_badge': apr_badges.get(plate, ''),
        }
        rows.append(row)

    out_csv = os.path.join(OUT_DIR, 'c2_rod_plate_map.csv')
    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['plate', 'jan_rod', 'jan_badge',
                                                'apr_rod', 'apr_badge'])
        writer.writeheader()
        writer.writerows(rows)
    print("\nWrote %s (%d rows)" % (out_csv, len(rows)))

    # Cross-check: do all April rods fall in R-741-800?
    print("\n--- Rod Range Verification ---")
    out_of_range = []
    for plate, rod in apr_rods.items():
        num = int(rod.split('-')[1])
        if num < 741 or num > 800:
            out_of_range.append((plate, rod))
    if out_of_range:
        print("  WARNING: April rods outside R-741-800 range:")
        for plate, rod in out_of_range:
            print("    %s: %s" % (plate, rod))
    else:
        print("  All April rods in expected R-741-800 range: OK")

    # Cross-check January rods
    out_of_range_jan = []
    for plate, rod in jan_rods.items():
        num = int(rod.split('-')[1])
        if num < 681 or num > 740:
            out_of_range_jan.append((plate, rod))
    if out_of_range_jan:
        print("  WARNING: January rods outside R-681-740 range:")
        for plate, rod in out_of_range_jan:
            print("    %s: %s" % (plate, rod))
    else:
        print("  All January rods in expected R-681-740 range: OK")

    # Summary stats
    print("\n--- Summary ---")
    print("  Total plates mapped (Jan): %d" % len(jan_rods))
    print("  Total plates mapped (Apr): %d" % len(apr_rods))
    unique_apr_rods = set(apr_rods.values())
    print("  Unique April rod IDs: %d" % len(unique_apr_rods))

    # Check for duplicate rod assignments (same rod on multiple plates)
    rod_to_plates = defaultdict(list)
    for plate, rod in apr_rods.items():
        rod_to_plates[rod].append(plate)
    dupes = {r: ps for r, ps in rod_to_plates.items() if len(ps) > 1}
    if dupes:
        print("  WARNING: Rods assigned to multiple plates:")
        for rod, plates in dupes.items():
            print("    %s: %s" % (rod, ', '.join(plates)))
    else:
        print("  No duplicate rod assignments: OK")

    return jan_rods, apr_rods, jan_badges, apr_badges


if __name__ == '__main__':
    jan_rods, apr_rods, jan_badges, apr_badges = main()
