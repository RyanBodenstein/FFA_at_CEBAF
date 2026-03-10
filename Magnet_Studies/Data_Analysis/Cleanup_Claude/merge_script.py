#!/usr/bin/env python3
"""
Merge script for LDRD FFA@CEBAF magnet measurement data.
Collects .dat files from all data sources (folders, zips), deduplicates by datetime,
excludes 1337 sentinel values, and writes merged files to Cleanup_Claude/.

Usage:
    python3 merge_script.py

Output structure:
    Cleanup_Claude/
    ├── Y_Plates/Helmholtz/       # Y-plate Helmholtz merged files
    ├── Y_Plates/Teslameter/      # Y-plate Teslameter merged files
    ├── Pair_Assemblies/Helmholtz/ # H/A pair assembly Helmholtz files
    ├── Pair_Assemblies/Teslameter/# A pair assembly Teslameter files
    ├── Lab_Measurements/         # Lab reference measurements
    └── Dosimetry/                # Dosimetry data (copied separately)
"""

import os
import re
import sys
import shutil
import zipfile
import json
from collections import defaultdict
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# If script is in Cleanup_Claude/, BASE_DIR = parent = Claude_Analysis1/
OUT_DIR = os.path.join(BASE_DIR, "Cleanup_Claude")

# ─── Data Sources ────────────────────────────────────────────────────────────

# Pre-deployment accumulated folders (chronological order, later = more rows)
PREDEPLOYMENT_FOLDERS = [
    "Feb1825",
    "Mar52025",
    "Mar122025",
    "MAr25_2025",
    "April0825",
    "April23",
    "May07_2025",
    "MAY212025",
    "June112025",
    "June172025_merged",
    "July2_2025_merge",
    "July17_2025_merge",      # Most complete pre-deployment accumulation
    "July17_2025_clean",
]

# Folders with campaign-specific or accumulated data
CAMPAIGN_FOLDERS = [
    "July17_2025_Helmholtz",   # Jul 17 Helmholtz only (new format, single rows)
    "July 17 Teslameter",      # Jul 17 Teslameter (accumulated)
]

# Zip files containing tunnel campaign data (accumulated or incremental)
CAMPAIGN_ZIPS = [
    "July30Helmholtz.zip",
    "July30Teslameterdata.zip",
    "082725_helmholtz.zip",
    "Aug27teslameter.zip",
    "DosimetrySept10.zip",        # Most complete accumulated (old+new format through Sep 10)
    "102125_helmholtz.zip",
    "21OctTeslameter.zip",
    "2025-101-23_Helmholtz.zip",
    "2025-10-23_Teslameter.zip",
    "Oct 29 Helmholtz.zip",       # Contains both helmholtz and teslameter accumulated
    "2025-10-29_Teslameter.zip",
    "20260108_Helmholtz.zip",
    "20260108_Teslameter.zip",
    "Jan_12_Helmholtz.zip",
    "20260112_Teslameter.zip",
]

# Lab measurement zips (separate output)
LAB_ZIPS = [
    "2025-12-17_Helmholtz_Lab_Measurements_AdamR.zip",
]

# Upstairs measurement zips (separate output)
UPSTAIRS_ZIPS = [
    "Upstairs_Helmholtz_Adam_2026-1-30.zip",
    "Upstairs_Helmholtz_Adam_2026-2-6.zip",
    "2026-2-13_Adam_Upstairs_Hn-29-2_helmholtz.zip",
    "2026-2-20_Adam_Upstairs_Helmholtz.zip",
    "2026-3-2_Helmholtz_Adam_Upstairs.zip",
]

# Baseline folder
BASELINE_FOLDER = "Magnet measurements baseline (after labeling fix)"

# ─── Naming Normalization ────────────────────────────────────────────────────

# Known naming inconsistencies and their corrections
# These are logged but we attempt to normalize where unambiguous
NAMING_LOG = []

def normalize_sample_name(filename):
    """
    Normalize sample names from filenames.
    Returns (normalized_name, measurement_type) or (None, None) if should be skipped.

    measurement_type is one of: 'helmholtz', 'front', 'side', 'top'
    """
    basename = os.path.basename(filename)

    # Skip non-dat files
    if not basename.endswith('.dat'):
        return None, None

    # Skip config.dat and similar
    if basename in ('config.dat',):
        return None, None

    # Extract measurement type
    mtype = None
    for suffix in ('_helmholtz.dat', '_front.dat', '_side.dat', '_top.dat'):
        if basename.endswith(suffix):
            mtype = suffix.replace('.dat', '').lstrip('_')
            sample = basename[:-len(suffix)]
            break

    if mtype is None:
        NAMING_LOG.append(f"SKIP: Cannot parse measurement type from '{basename}'")
        return None, None

    # Skip bare names with no sample prefix (e.g., "_helmholtz.dat", "-1_helmholtz.dat")
    if sample == '' or re.match(r'^-?\d*$', sample):
        NAMING_LOG.append(f"SKIP: Bare/incomplete name '{basename}' (sample='{sample}')")
        return None, None

    original = sample

    # Normalize known naming issues
    # An--X-Y → unknown plate, flag but keep
    if re.match(r'^An--\d+-\d+$', sample):
        NAMING_LOG.append(f"FLAG: '{basename}' has missing plate number (An--X-Y pattern)")
        # Keep as-is, will be flagged in report

    # An-plate-X-Y, An-pplate-X-Y, Anplate-X-Y → unknown plate number
    elif re.match(r'^An-?p?plate-\d+-\d+$', sample):
        NAMING_LOG.append(f"FLAG: '{basename}' has 'plate' placeholder instead of plate number")

    # Hn-plate-X, Hnplate-X, Hs-plate-X → unknown plate number
    elif re.match(r'^H[ns]-?plate-\d+$', sample):
        NAMING_LOG.append(f"FLAG: '{basename}' has 'plate' placeholder instead of plate number")

    # Y-plate-X → unknown plate number
    elif re.match(r'^Y-plate-\d+$', sample):
        NAMING_LOG.append(f"FLAG: '{basename}' has 'plate' placeholder instead of plate number")

    # A-2-X-Y → could be An or As plate 2
    elif re.match(r'^A-\d+-\d+-\d+$', sample):
        NAMING_LOG.append(f"FLAG: '{basename}' has ambiguous 'A-' prefix (could be An or As)")

    # H-X-Y → could be Hn or Hs
    elif re.match(r'^H-\d+-\d+$', sample):
        NAMING_LOG.append(f"FLAG: '{basename}' has ambiguous 'H-' prefix (could be Hn or Hs)")

    # As-plate-X-Y
    elif re.match(r'^As-plate-\d+-\d+$', sample):
        NAMING_LOG.append(f"FLAG: '{basename}' has 'plate' placeholder instead of plate number")

    # Fix doubled names like "Hs-19-1Hs-19-1"
    doubled = re.match(r'^((?:H[ns]|Y|A[ns]?)-[\w-]+)\1$', sample)
    if doubled:
        sample = doubled.group(1)
        NAMING_LOG.append(f"FIX: Doubled name '{original}' → '{sample}'")

    # Fix "HHn-" prefix (typo)
    if sample.startswith('HHn-'):
        fixed = 'Hn-' + sample[4:]
        NAMING_LOG.append(f"FIX: Typo '{original}' → '{fixed}'")
        sample = fixed

    # Fix "An-15-2" (missing magnet number - this is an H-type name used for A)
    if re.match(r'^An-\d+-\d+$', sample) and not re.match(r'^An--\d+-\d+$', sample):
        NAMING_LOG.append(f"FLAG: '{basename}' looks like H-type name but has An prefix")

    return sample, mtype


# ─── Row Parsing ─────────────────────────────────────────────────────────────

def parse_datetime(line):
    """
    Extract a datetime key from a .dat row. Handles two formats:
    Old: ' YYYY-MM-DD-HH:MM:SS\t...'
    New: ' YYYY-MM-DD\tHH:MM:SS\t...'
    Returns (datetime_str, rest_of_line) or (None, None) for unparseable lines.
    """
    line = line.rstrip('\r\n')
    if not line.strip():
        return None, None

    # Try new format first: YYYY-MM-DD<tab>HH:MM:SS
    m = re.match(r'\s*(\d{4}-\d{2}-\d{2})\t(\d{2}:\d{2}:\d{2})(.*)', line)
    if m:
        dt_str = f"{m.group(1)}-{m.group(2)}"
        return dt_str, line

    # Try old format: YYYY-MM-DD-HH:MM:SS
    m = re.match(r'\s*(\d{4}-\d{2}-\d{2}-\d{2}:\d{2}:\d{2})(.*)', line)
    if m:
        dt_str = m.group(1)
        return dt_str, line

    return None, None


def is_sentinel_row(line):
    """Check if a row contains the 1337 sentinel value."""
    # Match "1337 nonunits" or standalone 1337 readings in teslameter
    stripped = line.strip()
    if '1337 nonunits' in stripped:
        return True
    # Teslameter sentinel: all readings are 1337
    # e.g., "...R-479\t1337\t1337\t1337\t1337"
    parts = stripped.split('\t')
    # Check if all numeric fields are 1337
    readings = [p.strip() for p in parts if re.match(r'^1337\.?0*$', p.strip())]
    if len(readings) >= 3:  # At least 3 fields are 1337 → sentinel
        return True
    return False


def has_valid_reading(line, mtype):
    """Check if a row has a valid (non-empty, non-sentinel) reading."""
    if is_sentinel_row(line):
        return False
    stripped = line.strip()
    if not stripped:
        return False
    parts = stripped.split('\t')

    if mtype == 'helmholtz':
        # Old format: datetime + 3 empty tabs + value
        # New format: datetime + time + serial + rod + value
        # Check if there's a reading value somewhere
        for p in parts:
            p = p.strip()
            if re.match(r'^[+-]?\d+\.\d+\s*(kT|mWC|kBG)', p):
                return True
        return False
    else:
        # Teslameter: need numeric readings
        for p in parts:
            p = p.strip()
            if re.match(r'^-?\d+\.\d{2,}$', p):
                return True
        return False


def normalize_row(line):
    """
    Normalize a row to a canonical format for output.
    Strips trailing \r characters, preserves tabs.
    """
    return line.rstrip('\r\n').rstrip('\r') + '\n'


# ─── File Collection ─────────────────────────────────────────────────────────

def collect_from_folder(folder_path):
    """
    Collect all .dat files from a folder.
    Returns dict: {(sample_name, mtype): [list of file contents as strings]}
    """
    result = defaultdict(list)
    if not os.path.isdir(folder_path):
        return result

    for fname in os.listdir(folder_path):
        fpath = os.path.join(folder_path, fname)
        if not os.path.isfile(fpath) or not fname.endswith('.dat'):
            continue
        sample, mtype = normalize_sample_name(fname)
        if sample is None:
            continue
        try:
            with open(fpath, 'r', errors='replace') as f:
                content = f.read()
            result[(sample, mtype)].append(content)
        except Exception as e:
            NAMING_LOG.append(f"ERROR: Cannot read '{fpath}': {e}")

    return result


def collect_from_zip(zip_path):
    """
    Collect all .dat files from a zip.
    Returns dict: {(sample_name, mtype): [list of file contents as strings]}
    """
    result = defaultdict(list)
    if not os.path.isfile(zip_path):
        print(f"  WARNING: Zip not found: {zip_path}")
        return result

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                fname = os.path.basename(info.filename)
                if not fname.endswith('.dat'):
                    continue
                sample, mtype = normalize_sample_name(fname)
                if sample is None:
                    continue
                try:
                    with zf.open(info) as f:
                        content = f.read().decode('utf-8', errors='replace')
                    result[(sample, mtype)].append(content)
                except Exception as e:
                    NAMING_LOG.append(f"ERROR: Cannot read '{info.filename}' in '{zip_path}': {e}")
    except zipfile.BadZipFile:
        print(f"  WARNING: Bad zip file: {zip_path}")

    return result


# ─── Merge Logic ─────────────────────────────────────────────────────────────

def merge_rows(contents_list, mtype):
    """
    Merge multiple file contents (strings) for the same sample.
    Deduplicates by datetime key, excludes sentinels and empty rows.
    Returns list of (datetime_key, normalized_line) sorted chronologically.
    """
    seen = {}  # datetime_key -> line
    conflicts = []

    for content in contents_list:
        for line in content.split('\n'):
            line = line.rstrip('\r\n')
            if not line.strip():
                continue

            dt_key, _ = parse_datetime(line)
            if dt_key is None:
                continue

            if is_sentinel_row(line):
                continue

            if not has_valid_reading(line, mtype):
                continue

            if dt_key in seen:
                # Check for conflict (different readings for same timestamp)
                existing = seen[dt_key].strip()
                new = line.strip()
                if existing != new:
                    # Check if they're substantively different (not just whitespace/\r)
                    e_clean = re.sub(r'\s+', ' ', existing)
                    n_clean = re.sub(r'\s+', ' ', new)
                    if e_clean != n_clean:
                        conflicts.append((dt_key, existing, new))
                        # Keep the one with more data (longer line)
                        if len(new) > len(existing):
                            seen[dt_key] = line
            else:
                seen[dt_key] = line

    # Sort by datetime
    def sort_key(item):
        try:
            # Parse YYYY-MM-DD-HH:MM:SS
            return datetime.strptime(item[0], "%Y-%m-%d-%H:%M:%S")
        except ValueError:
            return datetime.min

    sorted_rows = sorted(seen.items(), key=sort_key)
    return sorted_rows, conflicts


# ─── Output Classification ──────────────────────────────────────────────────

def classify_sample(sample_name, mtype):
    """
    Determine output directory for a sample.
    Returns (category, output_path) where category is 'Y', 'Pair', 'skip'.
    """
    if sample_name.startswith('Y-'):
        if mtype == 'helmholtz':
            return 'Y', os.path.join(OUT_DIR, 'Y_Plates', 'Helmholtz')
        else:
            return 'Y', os.path.join(OUT_DIR, 'Y_Plates', 'Teslameter')

    # H-type (Hn, Hs, H) and A-type (An, As, A) → Pair Assemblies
    if re.match(r'^(Hn|Hs|H|An|As|A)-', sample_name):
        if mtype == 'helmholtz':
            return 'Pair', os.path.join(OUT_DIR, 'Pair_Assemblies', 'Helmholtz')
        else:
            return 'Pair', os.path.join(OUT_DIR, 'Pair_Assemblies', 'Teslameter')

    NAMING_LOG.append(f"SKIP: Cannot classify sample '{sample_name}' (mtype={mtype})")
    return 'skip', None


def output_filename(sample_name, mtype):
    """Generate output filename."""
    return f"{sample_name}_{mtype}.dat"


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("LDRD Magnet Data Merge Script")
    print("=" * 70)

    # Collect all data from all sources
    all_data = defaultdict(list)  # (sample, mtype) -> [content strings]

    # 1. Pre-deployment folders
    print("\n--- Scanning pre-deployment folders ---")
    for folder in PREDEPLOYMENT_FOLDERS:
        fpath = os.path.join(BASE_DIR, folder)
        if os.path.isdir(fpath):
            data = collect_from_folder(fpath)
            count = sum(len(v) for v in data.values())
            print(f"  {folder}: {len(data)} samples, {count} file versions")
            for key, contents in data.items():
                all_data[key].extend(contents)
        else:
            print(f"  {folder}: NOT FOUND")

    # 2. Baseline folder
    print("\n--- Scanning baseline folder ---")
    bpath = os.path.join(BASE_DIR, BASELINE_FOLDER)
    if os.path.isdir(bpath):
        data = collect_from_folder(bpath)
        count = sum(len(v) for v in data.values())
        print(f"  {BASELINE_FOLDER}: {len(data)} samples, {count} file versions")
        for key, contents in data.items():
            all_data[key].extend(contents)

    # 3. Campaign folders
    print("\n--- Scanning campaign folders ---")
    for folder in CAMPAIGN_FOLDERS:
        fpath = os.path.join(BASE_DIR, folder)
        if os.path.isdir(fpath):
            data = collect_from_folder(fpath)
            count = sum(len(v) for v in data.values())
            print(f"  {folder}: {len(data)} samples, {count} file versions")
            for key, contents in data.items():
                all_data[key].extend(contents)
        else:
            print(f"  {folder}: NOT FOUND")

    # 4. Campaign zips
    print("\n--- Scanning campaign zips ---")
    for zname in CAMPAIGN_ZIPS:
        zpath = os.path.join(BASE_DIR, zname)
        data = collect_from_zip(zpath)
        count = sum(len(v) for v in data.values())
        print(f"  {zname}: {len(data)} samples, {count} file versions")
        for key, contents in data.items():
            all_data[key].extend(contents)

    print(f"\n--- Total unique (sample, mtype) combinations: {len(all_data)} ---")

    # Merge and write output
    print("\n--- Merging and writing output ---")

    stats = {
        'Y_helmholtz': 0, 'Y_teslameter': 0,
        'Pair_helmholtz': 0, 'Pair_teslameter': 0,
        'skipped': 0, 'conflicts': 0,
        'total_rows': 0,
    }
    sample_stats = {}  # sample_name -> {mtype: {rows, min_date, max_date}}
    all_conflicts = []

    for (sample, mtype), contents_list in sorted(all_data.items()):
        category, out_dir = classify_sample(sample, mtype)
        if category == 'skip' or out_dir is None:
            stats['skipped'] += 1
            continue

        merged_rows, conflicts = merge_rows(contents_list, mtype)

        if not merged_rows:
            continue

        # Write output
        fname = output_filename(sample, mtype)
        out_path = os.path.join(out_dir, fname)

        with open(out_path, 'w') as f:
            for dt_key, line in merged_rows:
                f.write(normalize_row(line))

        # Track stats
        if category == 'Y':
            if mtype == 'helmholtz':
                stats['Y_helmholtz'] += 1
            else:
                stats['Y_teslameter'] += 1
        else:
            if mtype == 'helmholtz':
                stats['Pair_helmholtz'] += 1
            else:
                stats['Pair_teslameter'] += 1

        stats['total_rows'] += len(merged_rows)

        if conflicts:
            stats['conflicts'] += len(conflicts)
            for dt, old, new in conflicts:
                all_conflicts.append((sample, mtype, dt, old, new))

        # Per-sample stats
        if sample not in sample_stats:
            sample_stats[sample] = {}
        dates = [r[0] for r in merged_rows]
        sample_stats[sample][mtype] = {
            'rows': len(merged_rows),
            'min_date': dates[0] if dates else None,
            'max_date': dates[-1] if dates else None,
        }

    # Handle lab measurements — clean \r and strip whitespace
    print("\n--- Extracting lab measurements ---")
    for zname in LAB_ZIPS:
        zpath = os.path.join(BASE_DIR, zname)
        if not os.path.isfile(zpath):
            print(f"  {zname}: NOT FOUND")
            continue
        out_dir = os.path.join(OUT_DIR, 'Lab_Measurements', '2025-12-17_AdamR')
        with zipfile.ZipFile(zpath, 'r') as zf:
            count = 0
            for info in zf.infolist():
                if info.is_dir():
                    continue
                fname = os.path.basename(info.filename)
                if fname.endswith('.dat'):
                    with zf.open(info) as f:
                        content = f.read().decode('utf-8', errors='replace')
                    # Clean: strip \r, remove blank lines
                    cleaned_lines = []
                    for line in content.split('\n'):
                        line = line.rstrip('\r\n').rstrip('\r')
                        if line.strip():
                            cleaned_lines.append(line)
                    with open(os.path.join(out_dir, fname), 'w') as f:
                        for line in cleaned_lines:
                            f.write(line + '\n')
                    count += 1
            print(f"  {zname}: {count} files extracted")

    # Handle upstairs measurements — merge/dedup across zips, clean \r
    print("\n--- Extracting upstairs measurements ---")
    upstairs_data = defaultdict(list)  # fname -> [content strings from each zip]
    for zname in UPSTAIRS_ZIPS:
        zpath = os.path.join(BASE_DIR, zname)
        if not os.path.isfile(zpath):
            print(f"  {zname}: NOT FOUND")
            continue
        with zipfile.ZipFile(zpath, 'r') as zf:
            zip_count = 0
            for info in zf.infolist():
                if info.is_dir():
                    continue
                fname = os.path.basename(info.filename)
                if fname.endswith('.dat'):
                    with zf.open(info) as f:
                        content = f.read().decode('utf-8', errors='replace')
                    upstairs_data[fname].append((zname, content))
                    zip_count += 1
            print(f"  {zname}: {zip_count} files found")

    # Merge and deduplicate upstairs files
    out_dir = os.path.join(OUT_DIR, 'Lab_Measurements', 'Upstairs_2026')
    upstairs_count = 0
    for fname, sources in sorted(upstairs_data.items()):
        # Collect all unique rows by datetime key
        seen_rows = {}  # dt_key -> cleaned line
        raw_lines = []  # fallback for files without parseable datetimes
        for zname, content in sources:
            for line in content.split('\n'):
                line = line.rstrip('\r\n').rstrip('\r')
                if not line.strip():
                    continue
                dt_key, _ = parse_datetime(line)
                if dt_key:
                    if dt_key not in seen_rows:
                        seen_rows[dt_key] = line
                else:
                    raw_lines.append(line)

        # Sort by datetime and write
        def sort_key(item):
            try:
                return datetime.strptime(item[0], "%Y-%m-%d-%H:%M:%S")
            except ValueError:
                return datetime.min

        sorted_rows = sorted(seen_rows.items(), key=sort_key)

        outpath = os.path.join(out_dir, fname)
        with open(outpath, 'w') as f:
            for dt_key, line in sorted_rows:
                f.write(line + '\n')
        upstairs_count += 1

    print(f"  Total upstairs files written: {upstairs_count}")

    # Copy dosimetry data
    print("\n--- Copying dosimetry data ---")

    # OSL Area dosimeters
    osl_src = os.path.join(BASE_DIR, "Radiation Info", "Dosimetry Reports", "Areas", "BetterNaming")
    osl_dst = os.path.join(OUT_DIR, "Dosimetry", "OSL_Area")
    if os.path.isdir(osl_src):
        count = 0
        for f in os.listdir(osl_src):
            if f.endswith('.xlsx'):
                shutil.copy2(os.path.join(osl_src, f), os.path.join(osl_dst, f))
                count += 1
        print(f"  OSL Area: {count} xlsx files copied")

    # Optichromic rods
    rod_src = os.path.join(BASE_DIR, "Radiation Info", "Dosimetry Reports", "Rods", "LDRD_11102025_commentfix.xlsx")
    rod_dst = os.path.join(OUT_DIR, "Dosimetry", "Optichromic_Rods")
    if os.path.isfile(rod_src):
        shutil.copy2(rod_src, os.path.join(rod_dst, os.path.basename(rod_src)))
        print(f"  Optichromic Rods: copied LDRD_11102025_commentfix.xlsx")

    # Integrated doses
    intd_src = os.path.join(BASE_DIR, "Radiation Info", "Integrated_Dose_Data")
    intd_dst = os.path.join(OUT_DIR, "Dosimetry", "Integrated_Doses")
    if os.path.isdir(intd_src):
        count = 0
        for f in os.listdir(intd_src):
            src = os.path.join(intd_src, f)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(intd_dst, f))
                count += 1
        print(f"  Integrated Doses: {count} files copied")

    # Copy Materials spreadsheet
    mat_src = os.path.join(BASE_DIR, "Materials_Arrangements_Spreadsheet.xlsx")
    if os.path.isfile(mat_src):
        shutil.copy2(mat_src, os.path.join(OUT_DIR, "Materials_Arrangements.xlsx"))
        print(f"  Materials spreadsheet: copied")

    # ─── Print Summary ───────────────────────────────────────────────────────

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Y-plate Helmholtz files:      {stats['Y_helmholtz']}")
    print(f"  Y-plate Teslameter files:     {stats['Y_teslameter']}")
    print(f"  Pair Assembly Helmholtz files: {stats['Pair_helmholtz']}")
    print(f"  Pair Assembly Teslameter files:{stats['Pair_teslameter']}")
    print(f"  Total merged rows:            {stats['total_rows']}")
    print(f"  Skipped samples:              {stats['skipped']}")
    print(f"  Timestamp conflicts:          {stats['conflicts']}")

    # Date range summary
    all_min = None
    all_max = None
    for sample, mtypes in sample_stats.items():
        for mt, info in mtypes.items():
            if info['min_date']:
                if all_min is None or info['min_date'] < all_min:
                    all_min = info['min_date']
            if info['max_date']:
                if all_max is None or info['max_date'] > all_max:
                    all_max = info['max_date']

    print(f"  Date range: {all_min} to {all_max}")

    # Sample type breakdown
    y_samples = set()
    hn_samples = set()
    hs_samples = set()
    an_samples = set()
    as_samples = set()
    other_samples = set()

    for sample in sample_stats:
        if sample.startswith('Y-'):
            y_samples.add(sample)
        elif sample.startswith('Hn-'):
            hn_samples.add(sample)
        elif sample.startswith('Hs-'):
            hs_samples.add(sample)
        elif sample.startswith('An-'):
            an_samples.add(sample)
        elif sample.startswith('As-'):
            as_samples.add(sample)
        else:
            other_samples.add(sample)

    print(f"\n  Unique Y-plate samples:  {len(y_samples)}")
    print(f"  Unique Hn samples:       {len(hn_samples)}")
    print(f"  Unique Hs samples:       {len(hs_samples)}")
    print(f"  Unique An samples:       {len(an_samples)}")
    print(f"  Unique As samples:       {len(as_samples)}")
    if other_samples:
        print(f"  Other/ambiguous samples: {len(other_samples)} → {sorted(other_samples)}")

    # Write naming log
    log_path = os.path.join(OUT_DIR, "naming_log.txt")
    with open(log_path, 'w') as f:
        f.write("Naming Normalization Log\n")
        f.write("=" * 70 + "\n\n")
        # Deduplicate log entries
        unique_entries = sorted(set(NAMING_LOG))
        for entry in unique_entries:
            f.write(entry + "\n")
    print(f"\n  Naming log: {len(set(NAMING_LOG))} unique entries → {log_path}")

    # Write conflicts log
    if all_conflicts:
        conf_path = os.path.join(OUT_DIR, "conflicts_log.txt")
        with open(conf_path, 'w') as f:
            f.write("Timestamp Conflicts Log\n")
            f.write("=" * 70 + "\n\n")
            for sample, mtype, dt, old, new in all_conflicts:
                f.write(f"Sample: {sample}, Type: {mtype}, DateTime: {dt}\n")
                f.write(f"  Kept:     {old}\n")
                f.write(f"  Dropped:  {new}\n\n")
        print(f"  Conflicts log: {len(all_conflicts)} entries → {conf_path}")

    # Write sample stats JSON for README generation
    stats_path = os.path.join(OUT_DIR, "sample_stats.json")
    with open(stats_path, 'w') as f:
        json.dump({
            'summary': stats,
            'samples': {
                s: {
                    mt: {
                        'rows': info['rows'],
                        'min_date': info['min_date'],
                        'max_date': info['max_date'],
                    }
                    for mt, info in mtypes.items()
                }
                for s, mtypes in sample_stats.items()
            },
            'sample_counts': {
                'Y': len(y_samples),
                'Hn': len(hn_samples),
                'Hs': len(hs_samples),
                'An': len(an_samples),
                'As': len(as_samples),
                'other': sorted(list(other_samples)),
            }
        }, f, indent=2)
    print(f"  Stats JSON: {stats_path}")

    # ─── Generate README ─────────────────────────────────────────────────────

    generate_readme(stats, sample_stats, all_conflicts,
                    y_samples, hn_samples, hs_samples, an_samples, as_samples, other_samples)

    print("\nDone!")


def generate_readme(stats, sample_stats, all_conflicts,
                    y_samples, hn_samples, hs_samples, an_samples, as_samples, other_samples):
    """Generate README.md with summary statistics."""

    # Date range
    all_min = all_max = None
    for sample, mtypes in sample_stats.items():
        for mt, info in mtypes.items():
            if info['min_date']:
                if all_min is None or info['min_date'] < all_min:
                    all_min = info['min_date']
            if info['max_date']:
                if all_max is None or info['max_date'] > all_max:
                    all_max = info['max_date']

    lines = []
    lines.append("# LDRD FFA@CEBAF Magnet Measurement Data — Cleaned & Merged")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("This directory contains deduplicated, merged magnet measurement data from the")
    lines.append("LDRD permanent magnet radiation study at CEBAF. Data spans from pre-deployment")
    lines.append(f"baselines through post-run measurements ({all_min} to {all_max}).")
    lines.append("")
    lines.append("Generated by `merge_script.py` — see that script for full provenance details.")
    lines.append("")
    lines.append("## Data Format")
    lines.append("")
    lines.append("All files are tab-separated `.dat` files with two possible row formats:")
    lines.append("")
    lines.append("**Helmholtz (old format, early pre-deployment):**")
    lines.append("```")
    lines.append(" YYYY-MM-DD-HH:MM:SS\\t\\t\\t<value> kT")
    lines.append("```")
    lines.append("Note: 'kT' units appear in only ~7 very early rows (May 2024). These may")
    lines.append("reflect an early DAQ configuration before standardization.")
    lines.append("")
    lines.append("**Helmholtz (standard format, most data):**")
    lines.append("```")
    lines.append(" YYYY-MM-DD\\tHH:MM:SS\\t<dosimeter_serial>\\t<rod_id>\\t<value> mWC")
    lines.append("```")
    lines.append("")
    lines.append("**Teslameter (readings in mT):**")
    lines.append("```")
    lines.append(" YYYY-MM-DD-HH:MM:SS\\t<serial>\\t<rod>\\t<field1>\\t<field2>\\t<field3>\\t<temp>")
    lines.append("```")
    lines.append("or with separate date/time tabs in newer data.")
    lines.append("Fields 1-3 are magnetic field components in mT; field 4 is temperature in °C.")
    lines.append("")
    lines.append("## Sentinel Values")
    lines.append("")
    lines.append("Rows with `1337` readings have been **excluded**. These indicate no measurement")
    lines.append("was taken (dosimetry swap or testing in progress), NOT instrument failure.")
    lines.append("")
    lines.append("## Directory Structure")
    lines.append("")
    lines.append("```")
    lines.append("Cleanup_Claude/")
    lines.append("├── Y_Plates/")
    lines.append("│   ├── Helmholtz/     # Y-plate Helmholtz measurements")
    lines.append("│   └── Teslameter/    # Y-plate Teslameter measurements (front/side/top)")
    lines.append("├── Pair_Assemblies/")
    lines.append("│   ├── Helmholtz/     # H-plate and A-magnet Helmholtz measurements")
    lines.append("│   └── Teslameter/    # A-magnet Teslameter measurements")
    lines.append("├── Lab_Measurements/")
    lines.append("│   ├── 2025-12-17_AdamR/   # Lab Helmholtz reference measurements")
    lines.append("│   └── Upstairs_2026/      # Upstairs lab Helmholtz (Jan-Mar 2026)")
    lines.append("├── Dosimetry/")
    lines.append("│   ├── OSL_Area/           # OSL area dosimeter xlsx files")
    lines.append("│   ├── Optichromic_Rods/   # Optichromic rod dosimetry xlsx")
    lines.append("│   └── Integrated_Doses/   # NDX gamma+neutron integrated doses")
    lines.append("├── Materials_Arrangements.xlsx  # Sample material/location assignments")
    lines.append("├── merge_script.py         # This merge script (for reproducibility)")
    lines.append("├── naming_log.txt          # Log of naming normalizations and flags")
    lines.append("├── conflicts_log.txt       # Timestamp conflict details (if any)")
    lines.append("├── sample_stats.json       # Machine-readable per-sample statistics")
    lines.append("└── README.md               # This file")
    lines.append("```")
    lines.append("")
    lines.append("## Sample Counts")
    lines.append("")
    lines.append(f"| Type | Count |")
    lines.append(f"|------|-------|")
    lines.append(f"| Y-plate samples | {len(y_samples)} |")
    lines.append(f"| Hn (NdFeB pair plates) | {len(hn_samples)} |")
    lines.append(f"| Hs (SmCo pair plates) | {len(hs_samples)} |")
    lines.append(f"| An (NdFeB pair magnets) | {len(an_samples)} |")
    lines.append(f"| As (SmCo pair magnets) | {len(as_samples)} |")
    if other_samples:
        lines.append(f"| Other/ambiguous | {len(other_samples)} |")
    lines.append("")

    lines.append("## File Counts")
    lines.append("")
    lines.append(f"| Category | Files |")
    lines.append(f"|----------|-------|")
    lines.append(f"| Y-plate Helmholtz | {stats['Y_helmholtz']} |")
    lines.append(f"| Y-plate Teslameter | {stats['Y_teslameter']} |")
    lines.append(f"| Pair Assembly Helmholtz | {stats['Pair_helmholtz']} |")
    lines.append(f"| Pair Assembly Teslameter | {stats['Pair_teslameter']} |")
    lines.append(f"| **Total merged rows** | **{stats['total_rows']}** |")
    lines.append("")

    lines.append(f"## Date Range")
    lines.append("")
    lines.append(f"- **Earliest measurement:** {all_min}")
    lines.append(f"- **Latest measurement:** {all_max}")
    lines.append("")

    # Per-sample row counts (compact table)
    lines.append("## Per-Sample Summary (Helmholtz row counts)")
    lines.append("")
    lines.append("### Y-Plates")
    lines.append("")
    lines.append("| Sample | Helmholtz Rows | Date Range |")
    lines.append("|--------|---------------|------------|")
    for s in sorted(y_samples, key=lambda x: (int(re.search(r'Y-(\d+)', x).group(1)), int(re.search(r'Y-\d+-(\d+)', x).group(1)))):
        if 'helmholtz' in sample_stats.get(s, {}):
            info = sample_stats[s]['helmholtz']
            lines.append(f"| {s} | {info['rows']} | {info['min_date'][:10]} to {info['max_date'][:10]} |")
    lines.append("")

    lines.append("### Pair Assembly Plates (Hn/Hs)")
    lines.append("")
    lines.append("| Sample | Helmholtz Rows | Date Range |")
    lines.append("|--------|---------------|------------|")
    for s in sorted(list(hn_samples) + list(hs_samples)):
        if 'helmholtz' in sample_stats.get(s, {}):
            info = sample_stats[s]['helmholtz']
            lines.append(f"| {s} | {info['rows']} | {info['min_date'][:10]} to {info['max_date'][:10]} |")
    lines.append("")

    if all_conflicts:
        lines.append(f"## Conflicts")
        lines.append("")
        lines.append(f"{len(all_conflicts)} timestamp conflicts were found where different sources")
        lines.append(f"had different readings for the same (sample, datetime). See `conflicts_log.txt`.")
        lines.append("")

    if other_samples:
        lines.append("## Ambiguous/Non-standard Sample Names")
        lines.append("")
        lines.append("The following samples have non-standard names (missing plate numbers,")
        lines.append("ambiguous prefixes, etc.). See `naming_log.txt` for details.")
        lines.append("")
        for s in sorted(other_samples):
            lines.append(f"- `{s}`")
        lines.append("")

    lines.append("## Data Sources (in merge order)")
    lines.append("")
    lines.append("### Pre-deployment accumulated folders:")
    for f in PREDEPLOYMENT_FOLDERS:
        lines.append(f"- `{f}/`")
    lines.append("")
    lines.append("### Baseline folder:")
    lines.append(f"- `{BASELINE_FOLDER}/`")
    lines.append("")
    lines.append("### Campaign folders:")
    for f in CAMPAIGN_FOLDERS:
        lines.append(f"- `{f}/`")
    lines.append("")
    lines.append("### Campaign zips:")
    for f in CAMPAIGN_ZIPS:
        lines.append(f"- `{f}`")
    lines.append("")
    lines.append("### Lab measurement zips:")
    for f in LAB_ZIPS:
        lines.append(f"- `{f}`")
    lines.append("")
    lines.append("### Upstairs measurement zips:")
    for f in UPSTAIRS_ZIPS:
        lines.append(f"- `{f}`")
    lines.append("")

    lines.append("## Deduplication Method")
    lines.append("")
    lines.append("1. All versions of each sample file collected from all sources")
    lines.append("2. Each row parsed for datetime key (normalized across old/new date formats)")
    lines.append("3. Rows with `1337` sentinel values excluded")
    lines.append("4. Rows with empty/missing readings excluded")
    lines.append("5. Union of all unique (datetime) rows, sorted chronologically")
    lines.append("6. On timestamp conflict (different readings), longer/more-complete row kept")
    lines.append("")

    readme_path = os.path.join(OUT_DIR, "README.md")
    with open(readme_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"  README: {readme_path}")


if __name__ == '__main__':
    main()
