#!/usr/bin/env python3
"""
Parse all LDRD area dosimetry reports (Landauer OSL badges) into organized data.

Data sources:
  - 10 xlsx files in Dosimetry/OSL_Area/ (from BetterNaming)
  - 1 xlsx file in parent Areas/ folder (Oct 2025, missing from BetterNaming)
  - SpareAreas.txt for Part# -> Location mapping
  - PDF reports for neutron thermal/fast breakdown (not parsed here; see README)

Output:
  - Dosimetry/OSL_Area/master_doses.csv — all readings, all reports
  - Dosimetry/OSL_Area/spare_locations.csv — Part# -> Location from SpareAreas.txt
  - Dosimetry/OSL_Area/report_summary.csv — per-report statistics
  - Dosimetry/OSL_Area/README.md — documentation

Author: Claude Code (2026-03-17)
"""

import os
import csv
import re
from collections import defaultdict
from datetime import datetime

import openpyxl

# Paths
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Claude_Analysis1/
OSL_DIR = os.path.join(BASE, 'Cleanup_Claude', 'Dosimetry', 'OSL_Area')
AREAS_DIR = os.path.join(BASE, 'Radiation Info', 'Dosimetry Reports', 'Areas')
SPARE_FILE = os.path.join(BASE, 'Radiation Info', 'Logsheets', 'SpareAreas.txt')

# All xlsx sources: (report_date_label, filepath)
XLSX_SOURCES = []
BETTER_NAMING = os.path.join(AREAS_DIR, 'BetterNaming')

# BetterNaming files (canonical)
BN_DATES = ['20250227', '20250306', '20250331', '20250502', '20250516',
            '20250624', '20250804', '20250819', '20250915', '20250930']

# October 2025 (parent only, not in BetterNaming)
OCT_FILE = os.path.join(AREAS_DIR, 'DoseReport_20251024_051157_2526801163_738211.xlsx')

# March 2026 report (beam-off badges pulled Jan 2026, plus recovered Part 300)
MAR2026_FILE = os.path.join(AREAS_DIR, 'DoseReport_20260320_045552_2605600610_738211.xlsx')


def parse_spare_areas():
    """Parse SpareAreas.txt -> list of {part, serial, location, pull_date, install_date}"""
    entries = []
    if not os.path.exists(SPARE_FILE):
        print(f"WARNING: {SPARE_FILE} not found")
        return entries

    with open(SPARE_FILE, 'r') as f:
        for line in f:
            line = line.rstrip()
            if not line or line.startswith('NUMBER'):
                continue
            parts = line.split('\t')
            # Filter out empty elements but keep structure
            parts = [p.strip() for p in parts]
            parts = [p for p in parts if p]
            if len(parts) < 3:
                continue

            part_num = parts[0]
            serial = parts[1] if len(parts) > 1 else ''
            location = parts[2] if len(parts) > 2 else ''
            pull_date = parts[3] if len(parts) > 3 else ''
            install_date = parts[4] if len(parts) > 4 else ''

            # Validate part number is numeric
            if not re.match(r'^\d+$', part_num):
                continue

            entries.append({
                'part': int(part_num),
                'serial': serial,
                'location': location,
                'pull_date': pull_date,
                'install_date': install_date,
            })
    return entries


def parse_xlsx(filepath, report_label):
    """Parse a Landauer dose report xlsx into list of row dicts."""
    rows = []
    if not os.path.exists(filepath):
        print(f"WARNING: {filepath} not found, skipping")
        return rows

    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active

    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 2:  # Skip title + header rows
            continue

        part_nbr = row[1]
        badge_location = str(row[6]).strip() if row[6] else ''
        badge_type = str(row[5]).strip() if row[5] else ''
        badge_number = str(row[7]).strip() if row[7] else ''
        begin_wear = str(row[3]).strip() if row[3] else ''
        end_wear = str(row[4]).strip() if row[4] else ''

        # Parse dose values (may be int, float, empty string, or None)
        def safe_dose(val):
            if val is None or val == '' or val == ' ':
                return 0
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return 0

        skin = safe_dose(row[8])
        body = safe_dose(row[9])
        eye = safe_dose(row[10])
        beta = safe_dose(row[11])
        neutron = safe_dose(row[12])

        note_code = str(row[26]).strip() if row[26] else ''
        note_msg = str(row[27]).strip() if row[27] else ''

        # Determine saturation status
        saturated = False
        exceeded_1000rad = False
        neutron_exceeded = False
        irregular = False

        if note_code == 'LA':
            exceeded_1000rad = True
            # If all doses are 0 with LA code, the OSL was completely saturated
            if body == 0 and skin == 0 and neutron == 0:
                saturated = True
        if note_code == 'LH':
            irregular = True
        if 'neutron' in note_msg.lower() and 'exceeded' in note_msg.lower():
            neutron_exceeded = True

        rows.append({
            'report_date': report_label,
            'part_nbr': int(part_nbr) if part_nbr is not None else 0,
            'badge_type': badge_type,
            'badge_location': badge_location,
            'badge_number': badge_number,
            'begin_wear': begin_wear,
            'end_wear': end_wear,
            'skin_mrem': skin,
            'body_mrem': body,
            'eye_mrem': eye,
            'beta_mrem': beta,
            'neutron_mrem': neutron,
            'note_code': note_code,
            'note_message': note_msg,
            'exceeded_1000rad': exceeded_1000rad,
            'saturated_osl': saturated,
            'neutron_exceeded': neutron_exceeded,
            'irregular_exposure': irregular,
        })

    wb.close()
    return rows


def determine_monitoring_period(begin_wear, end_wear):
    """Categorize into H1 (Jan-Jun) or H2 (Jul-Dec) based on wear dates."""
    if '7/1' in begin_wear or '07/01' in begin_wear:
        return 'H2'
    elif '1/1' in begin_wear or '01/01' in begin_wear:
        return 'H1'
    return 'Unknown'


def build_location_lookup(spare_entries):
    """Build Part# -> Location lookup from SpareAreas.
    Multiple entries per part are possible (same dosimeter reused at different
    locations across campaigns). Returns dict of part -> list of location records."""
    lookup = defaultdict(list)
    for e in spare_entries:
        lookup[e['part']].append(e)
    return lookup


def main():
    print("=" * 70)
    print("LDRD Area Dosimetry Parser")
    print("=" * 70)

    # 1. Parse SpareAreas location mapping
    spare_entries = parse_spare_areas()
    print(f"\nSpareAreas.txt: {len(spare_entries)} entries parsed")
    location_lookup = build_location_lookup(spare_entries)
    print(f"  Unique Part#s with locations: {len(location_lookup)}")

    # 2. Parse all xlsx files
    all_rows = []

    # BetterNaming files
    for date_label in BN_DATES:
        # Use the copy in OSL_Area if it exists, else BetterNaming
        fp = os.path.join(OSL_DIR, f'{date_label}.xlsx')
        if not os.path.exists(fp):
            fp = os.path.join(BETTER_NAMING, f'{date_label}.xlsx')
        rows = parse_xlsx(fp, date_label)
        print(f"  {date_label}: {len(rows)} rows")
        all_rows.extend(rows)

    # October 2025 (parent only)
    if os.path.exists(OCT_FILE):
        rows = parse_xlsx(OCT_FILE, '20251024')
        print(f"  20251024: {len(rows)} rows")
        all_rows.extend(rows)
    else:
        print(f"  WARNING: October 2025 file not found: {OCT_FILE}")

    # March 2026 (beam-off badges + recovered Part 300)
    if os.path.exists(MAR2026_FILE):
        rows = parse_xlsx(MAR2026_FILE, '20260320')
        print(f"  20260320: {len(rows)} rows")
        all_rows.extend(rows)
    else:
        print(f"  WARNING: March 2026 file not found: {MAR2026_FILE}")

    print(f"\nTotal rows across all reports: {len(all_rows)}")

    # 3. Enrich with location data and monitoring period
    matched = 0
    for row in all_rows:
        pn = row['part_nbr']
        row['monitoring_period'] = determine_monitoring_period(
            row['begin_wear'], row['end_wear'])

        # Location from SpareAreas
        if pn in location_lookup:
            # Use most recent entry for this part
            entries = location_lookup[pn]
            # Find entry whose install_date is closest to begin_wear
            row['location'] = entries[-1]['location']  # most recent
            row['location_source'] = 'SpareAreas.txt'
            matched += 1
        else:
            row['location'] = ''
            row['location_source'] = ''

    print(f"Rows with location match: {matched}/{len(all_rows)} "
          f"({100*matched/len(all_rows):.1f}%)")

    # 4. Summary statistics
    print("\n--- Summary by Report ---")
    by_report = defaultdict(list)
    for row in all_rows:
        by_report[row['report_date']].append(row)

    report_summaries = []
    for rpt in sorted(by_report.keys()):
        rows = by_report[rpt]
        controls = [r for r in rows if r['badge_location'] == 'CONTROL']
        wholebody = [r for r in rows if r['badge_location'] == 'WHOLEBODY']
        nonzero = [r for r in wholebody if r['body_mrem'] > 0]
        saturated = [r for r in wholebody if r['saturated_osl']]
        exceeded = [r for r in wholebody if r['exceeded_1000rad']]
        max_body = max([r['body_mrem'] for r in wholebody], default=0)
        max_neutron = max([r['neutron_mrem'] for r in wholebody], default=0)
        periods = set(r['monitoring_period'] for r in wholebody)
        with_loc = [r for r in wholebody if r['location']]

        report_summaries.append({
            'report_date': rpt,
            'n_controls': len(controls),
            'n_wholebody': len(wholebody),
            'n_nonzero_body': len(nonzero),
            'n_saturated': len(saturated),
            'n_exceeded_1000rad': len(exceeded),
            'max_body_mrem': max_body,
            'max_neutron_mrem': max_neutron,
            'monitoring_periods': ','.join(sorted(periods)),
            'n_with_location': len(with_loc),
        })

        print(f"  {rpt}: {len(wholebody)} badges, "
              f"{len(nonzero)} nonzero, "
              f"{len(saturated)} saturated, "
              f"max body={max_body:,} mrem, "
              f"max neutron={max_neutron:,} mrem, "
              f"locations={len(with_loc)}")

    # 5. Global statistics
    wholebody_all = [r for r in all_rows if r['badge_location'] == 'WHOLEBODY']
    unique_parts = set(r['part_nbr'] for r in wholebody_all)
    print(f"\n--- Global Statistics ---")
    print(f"Total WHOLEBODY entries: {len(wholebody_all)}")
    print(f"Unique Part#s: {len(unique_parts)}")
    print(f"Part# range: {min(unique_parts)} - {max(unique_parts)}")

    nonzero_body = [r for r in wholebody_all if r['body_mrem'] > 0]
    if nonzero_body:
        max_r = max(nonzero_body, key=lambda r: r['body_mrem'])
        print(f"Max body dose: {max_r['body_mrem']:,} mrem "
              f"(Part# {max_r['part_nbr']}, report {max_r['report_date']})")
        print(f"  = {max_r['body_mrem']/100:.1f} rad "
              f"= {max_r['body_mrem']/100000:.4f} Gy")

    # Neutron statistics
    nonzero_neutron = [r for r in wholebody_all if r['neutron_mrem'] > 0]
    if nonzero_neutron:
        max_n = max(nonzero_neutron, key=lambda r: r['neutron_mrem'])
        print(f"\nMax neutron dose: {max_n['neutron_mrem']:,} mrem "
              f"(Part# {max_n['part_nbr']}, report {max_n['report_date']})")

    # Neutron fraction distribution
    neutron_fracs = []
    for r in wholebody_all:
        if r['body_mrem'] > 0 and r['neutron_mrem'] > 0:
            neutron_fracs.append(r['neutron_mrem'] / r['body_mrem'])
    if neutron_fracs:
        print(f"Neutron/Total fraction: "
              f"median={sorted(neutron_fracs)[len(neutron_fracs)//2]:.3f}, "
              f"max={max(neutron_fracs):.3f}")

    # 6. Write output files
    print(f"\n--- Writing Output Files ---")

    # Master doses CSV
    master_csv = os.path.join(OSL_DIR, 'master_doses.csv')
    fieldnames = [
        'report_date', 'part_nbr', 'badge_number', 'badge_type',
        'badge_location', 'begin_wear', 'end_wear', 'monitoring_period',
        'skin_mrem', 'body_mrem', 'eye_mrem', 'beta_mrem', 'neutron_mrem',
        'note_code', 'note_message',
        'exceeded_1000rad', 'saturated_osl', 'neutron_exceeded',
        'irregular_exposure', 'location', 'location_source',
    ]
    with open(master_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(all_rows, key=lambda r: (r['report_date'], r['part_nbr'])):
            writer.writerow(row)
    print(f"  {master_csv}: {len(all_rows)} rows")

    # Spare locations CSV
    spare_csv = os.path.join(OSL_DIR, 'spare_locations.csv')
    spare_fields = ['part', 'serial', 'location', 'install_date', 'pull_date']
    with open(spare_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=spare_fields)
        writer.writeheader()
        for e in sorted(spare_entries, key=lambda x: (x['install_date'], x['part'])):
            writer.writerow(e)
    print(f"  {spare_csv}: {len(spare_entries)} entries")

    # Report summary CSV
    summary_csv = os.path.join(OSL_DIR, 'report_summary.csv')
    with open(summary_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=report_summaries[0].keys())
        writer.writeheader()
        writer.writerows(report_summaries)
    print(f"  {summary_csv}: {len(report_summaries)} reports")

    # 7. Location coverage analysis
    print(f"\n--- Location Coverage ---")
    spare_parts = set(location_lookup.keys())
    data_parts = unique_parts
    overlap = spare_parts & data_parts
    print(f"SpareAreas Part#s: {len(spare_parts)}")
    print(f"Dose data Part#s: {len(data_parts)}")
    print(f"Overlap: {len(overlap)}")
    print(f"Data Part#s WITHOUT location: {len(data_parts - spare_parts)}")

    # Show which locations we DO have
    locs = set()
    for entries in location_lookup.values():
        for e in entries:
            locs.add(e['location'])
    print(f"\nKnown locations ({len(locs)}):")
    for loc in sorted(locs):
        count = sum(1 for e in spare_entries if e['location'] == loc)
        print(f"  {loc} ({count} entries)")

    print("\n--- Part#s in SpareAreas that appear in dose data ---")
    for pn in sorted(overlap):
        loc_entries = location_lookup[pn]
        dose_rows = [r for r in wholebody_all if r['part_nbr'] == pn]
        for dr in dose_rows:
            # Find matching spare entry by date proximity
            loc = loc_entries[-1]['location']
            print(f"  Part {pn:05d}: {dr['body_mrem']:>10,} mrem body, "
                  f"{dr['neutron_mrem']:>8,} mrem neutron | "
                  f"Location: {loc} | Report: {dr['report_date']}")

    print("\nDone.")


if __name__ == '__main__':
    main()
