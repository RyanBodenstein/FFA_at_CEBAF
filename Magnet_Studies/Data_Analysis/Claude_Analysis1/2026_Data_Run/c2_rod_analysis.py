#!/usr/bin/env python3
"""
Campaign 2 Rod Dosimetry: Raw Reading Analysis
Reads Rods_read_051526_Isurumali_Raw.xlsx and summarizes.

Two rod populations in this file:
  - R-681 to R-740: C1 "final" rods installed Jan 2026, integrating shutdown + early C2
  - R-741 to R-800: New C2 rods installed between Apr 20 and May 15, 2026

NOTE: These are RAW readings, not processed by Kirsten.
      Most readings are below the FWT-70 valid range.
"""

import numpy as np
import os
import csv

try:
    import openpyxl
except ImportError:
    print("ERROR: openpyxl required")
    raise

# ── Configuration ──────────────────────────────────────────────────────────
BASE = "/Users/ryanmb/Documents/LDRD/Claude_Analysis1"
RAW_FILE = os.path.join(BASE, "Radiation Info/Dosimetry Reports/Rods",
                        "Rods_read_051526_Isurumali_Raw.xlsx")
ROD_MAP_FILE = os.path.join(BASE, "Cleanup_Claude/Rod_Dosimetry/rod_plate_map.csv")
C2_ROD_MAP_FILE = os.path.join(BASE, "2026_Data_Run/Analysis/c2_rod_plate_map.csv")
C1_DOSE_FILE = os.path.join(BASE, "Data_Package/03_Dosimetry/merged_dose_final.csv")
OUT_DIR = os.path.join(BASE, "2026_Data_Run/Analysis")
os.makedirs(OUT_DIR, exist_ok=True)

# FWT-70 validity ranges (krad)
VALID_LOW_600 = (2.0, 39.0)
VALID_LOW_656 = (30.0, None)
VALID_HIGH_600 = (12.0, 300.0)
VALID_HIGH_656 = (132.0, None)

# ── Load C1 rod-to-plate map ──────────────────────────────────────────────
rod_to_plate = {}
# Load C1 rod-to-plate mapping (R-1 through R-680)
if os.path.exists(ROD_MAP_FILE):
    with open(ROD_MAP_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = row.get("rod_id", "").strip()
            plate = row.get("plate", "").strip()
            if rid and plate:
                rod_to_plate[rid] = plate

# Load C2 rod-to-plate mapping (R-681-800 from April 2026 Teslameter .dat files)
if os.path.exists(C2_ROD_MAP_FILE):
    with open(C2_ROD_MAP_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            plate = row.get("plate", "").strip()
            # January rods (C1-final)
            jan_rod = row.get("jan_rod", "").strip()
            if jan_rod and plate:
                rod_to_plate[jan_rod] = plate
            # April rods (C2-new)
            apr_rod = row.get("apr_rod", "").strip()
            if apr_rod and plate:
                rod_to_plate[apr_rod] = plate

# ── Load C1 cumulative doses for comparison ───────────────────────────────
c1_doses = {}  # plate -> {gamma_gy, neutron_rem}
if os.path.exists(C1_DOSE_FILE):
    with open(C1_DOSE_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            plate = row.get("plate", "").strip()
            try:
                gamma = float(row.get("gamma_dose_gy", 0))
                neutron = float(row.get("neutron_dose_rem", 0))
                c1_doses[plate] = {"gamma_gy": gamma, "neutron_rem": neutron}
            except (ValueError, TypeError):
                pass

# ── Parse raw spreadsheet ─────────────────────────────────────────────────
wb = openpyxl.load_workbook(RAW_FILE, data_only=True)
ws = wb["Sheet1"]

# Column mapping (0-indexed):
# 0:ProjectNumber, 1:LocationNumber, 2:Range, 3:DateRead,
# 4:600nm-1, 5:656nm-1, 6:600nm-2, 7:656nm-2,
# 8:Notes, 9:600_slope, 10:600_intercept, 11:656_slope, 12:656_intercept,
# 13:600_rad-1, 14:656_rad-1, 15:600_rad-2, 16:656_rad-2

import re
rod_id_pattern = re.compile(r'R[-=]?(\d+)', re.IGNORECASE)

# Store parsed data: rod_id -> list of readings
rods = {}

for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i == 0:  # header
        continue

    notes = str(row[8]).strip() if row[8] else ""
    range_type = str(row[2]).strip() if row[2] else ""
    date_read = str(row[3]).strip() if row[3] else ""

    # Skip empty rows (blank re-entry artifacts)
    if not notes and row[4] is None:
        continue

    # Extract rod ID
    match = rod_id_pattern.search(notes)
    if not match:
        continue
    rod_num = int(match.group(1))

    # Handle obvious typos
    if rod_num == 979:
        rod_num = 797  # R-979 likely R-797 (adjacent to R-797 entry)
    if rod_num == 7051:
        rod_num = 705  # R-7051 likely R-705

    rod_id = f"R-{rod_num}"

    # Skip partial rows (first attempt before re-entry): if only 1st
    # replicate exists and the rod has a later complete entry, skip this one.
    # Detected by: od_600_2 is None (incomplete)
    is_partial = row[4] is not None and row[6] is None

    # ── Resolve Range column vs Notes conflicts ──────────────────────────
    # Trust Notes + OD values over Range column when they disagree.
    od_600_1_val = row[4] if row[4] is not None else 0

    if range_type == "High" and "Low" in notes and "High" not in notes:
        # Notes says Low, Range says High. Check OD to confirm.
        if od_600_1_val > 0.2:  # Low-range ODs are typically 0.28-0.52
            range_type = "Low"  # Trust Notes
    elif range_type == "Low" and "High" in notes and "Low" not in notes:
        # Notes says High, Range says Low. Check OD to confirm.
        if od_600_1_val < 0.18:  # High-range ODs are typically 0.10-0.15
            range_type = "High"  # Trust Notes

    # ── Handle R-685 first High replicate (accidental Low rod re-read) ───
    # OD 0.373 matches the Low readings (0.379, 0.371); only use 2nd replicate
    if rod_id == "R-685" and range_type == "High":
        if row[4] is not None and row[4] > 0.25:
            # First replicate is a Low rod re-read; null it out
            row = list(row)
            row[4] = None
            row[5] = None
            row[13] = None
            row[14] = None
            row = tuple(row)

    # Get calibrated dose values (krad)
    # For corrected Range, recalculate using the correct calibration
    if range_type == "Low":
        slope_600, intercept_600 = 21.28, 6.0912
        slope_656, intercept_656 = 536, 18.667
    else:
        slope_600, intercept_600 = 118.24, 4.6745
        slope_656, intercept_656 = 1793, 24.221

    def calc_dose(od, slope, intercept):
        if od is None:
            return None
        return od * slope - intercept

    rad_600_1 = calc_dose(row[4], slope_600, intercept_600)
    rad_656_1 = calc_dose(row[5], slope_656, intercept_656)
    rad_600_2 = calc_dose(row[6], slope_600, intercept_600)
    rad_656_2 = calc_dose(row[7], slope_656, intercept_656)

    # Raw OD values
    od_600_1 = row[4] if row[4] is not None else None
    od_656_1 = row[5] if row[5] is not None else None
    od_600_2 = row[6] if row[6] is not None else None
    od_656_2 = row[7] if row[7] is not None else None

    if rod_id not in rods:
        rods[rod_id] = {"rod_num": rod_num, "readings": []}

    rods[rod_id]["readings"].append({
        "range": range_type,
        "date": date_read,
        "od_600_1": od_600_1, "od_656_1": od_656_1,
        "od_600_2": od_600_2, "od_656_2": od_656_2,
        "rad_600_1": rad_600_1, "rad_656_1": rad_656_1,
        "rad_600_2": rad_600_2, "rad_656_2": rad_656_2,
        "notes": notes,
        "is_partial": is_partial
    })

# ── De-duplicate: if a rod has both partial and complete entries for the
#    same range, keep only the complete one ─────────────────────────────────
for rid, data in rods.items():
    by_range = {}
    for r in data["readings"]:
        rng = r["range"]
        if rng not in by_range:
            by_range[rng] = []
        by_range[rng].append(r)
    # If multiple entries for same range, prefer complete over partial
    cleaned = []
    for rng, entries in by_range.items():
        complete = [e for e in entries if not e.get("is_partial", False)]
        partial = [e for e in entries if e.get("is_partial", False)]
        if complete:
            cleaned.extend(complete)
        else:
            cleaned.extend(partial)  # keep partial only if no complete exists
    data["readings"] = cleaned

# ── Categorize rods ───────────────────────────────────────────────────────
c1_final_rods = {}   # R-681 to R-740
c2_new_rods = {}     # R-741 to R-800
other_rods = {}      # anything else

for rid, data in rods.items():
    n = data["rod_num"]
    if 681 <= n <= 740:
        c1_final_rods[rid] = data
    elif 741 <= n <= 800:
        c2_new_rods[rid] = data
    else:
        other_rods[rid] = data

# ── Compute best-estimate dose per rod (Low@600nm average) ────────────────
def compute_dose_estimate(rod_data):
    """
    For each rod, get the Low-range 600nm readings (most sensitive).
    Average the two replicates. Return krad value.
    Also flag if reading is in-range or below detection.
    """
    low_readings = []
    high_readings = []
    for r in rod_data["readings"]:
        if r["range"] == "Low":
            vals = []
            if r["rad_600_1"] is not None and r["rad_600_1"] > 0:
                vals.append(r["rad_600_1"])
            if r["rad_600_2"] is not None and r["rad_600_2"] > 0:
                vals.append(r["rad_600_2"])
            low_readings.extend(vals)
        elif r["range"] == "High":
            vals = []
            if r["rad_600_1"] is not None and r["rad_600_1"] > 0:
                vals.append(r["rad_600_1"])
            if r["rad_600_2"] is not None and r["rad_600_2"] > 0:
                vals.append(r["rad_600_2"])
            high_readings.extend(vals)

    low_mean = np.mean(low_readings) if low_readings else None
    high_mean = np.mean(high_readings) if high_readings else None

    # Determine validity
    in_range = False
    best_krad = None
    if low_mean is not None:
        best_krad = low_mean
        if VALID_LOW_600[0] <= low_mean <= VALID_LOW_600[1]:
            in_range = True
    elif high_mean is not None:
        best_krad = high_mean
        if VALID_HIGH_600[0] <= high_mean <= VALID_HIGH_600[1]:
            in_range = True

    return {
        "low_600_krad": low_mean,
        "high_600_krad": high_mean,
        "best_krad": best_krad,
        "in_range": in_range,
        "n_low": len(low_readings),
        "n_high": len(high_readings)
    }

# ── Analyze each population ───────────────────────────────────────────────
def analyze_population(rod_dict, label):
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"  N = {len(rod_dict)} rods")
    print(f"{'='*70}")

    results = []
    for rid in sorted(rod_dict.keys(), key=lambda x: rod_dict[x]["rod_num"]):
        data = rod_dict[rid]
        dose = compute_dose_estimate(data)
        plate = rod_to_plate.get(rid, "")
        results.append((rid, plate, dose))

    # Summary statistics on Low@600nm
    valid_doses = [r[2]["low_600_krad"] for r in results
                   if r[2]["low_600_krad"] is not None]
    in_range = [r for r in results if r[2]["in_range"]]

    if valid_doses:
        arr = np.array(valid_doses)
        print(f"\n  Low@600nm dose (krad): all {len(valid_doses)} rods")
        print(f"    Min:    {arr.min():.2f}")
        print(f"    Max:    {arr.max():.2f}")
        print(f"    Median: {np.median(arr):.2f}")
        print(f"    Mean:   {arr.mean():.2f}")
        print(f"    Std:    {arr.std():.2f}")
        print(f"\n  In valid range (2-39 krad Low@600): {len(in_range)}/{len(results)}")
        below = [d for d in valid_doses if d < VALID_LOW_600[0]]
        print(f"  Below detection ({len(below)}/{len(valid_doses)}): "
              f"these readings are noise, not real dose")

    # Print per-rod table
    print(f"\n  {'Rod':<8} {'Plate':<8} {'Low@600':>10} {'High@600':>10} "
          f"{'Valid?':>7} {'C1 gamma':>10} {'C1 neut':>10}")
    print(f"  {'-'*8} {'-'*8} {'-'*10} {'-'*10} {'-'*7} {'-'*10} {'-'*10}")

    for rid, plate, dose in results:
        low = f"{dose['low_600_krad']:.2f}" if dose['low_600_krad'] is not None else "---"
        high = f"{dose['high_600_krad']:.2f}" if dose['high_600_krad'] is not None else "---"
        valid = "YES" if dose['in_range'] else "no"
        c1g = ""
        c1n = ""
        if plate and plate in c1_doses:
            c1g = f"{c1_doses[plate]['gamma_gy']:.0f}"
            c1n = f"{c1_doses[plate]['neutron_rem']:.0f}"
        print(f"  {rid:<8} {plate:<8} {low:>10} {high:>10} {valid:>7} "
              f"{c1g:>10} {c1n:>10}")

    # Highlight anything above detection
    if in_range:
        print(f"\n  ** Rods with readings IN the valid range:")
        for rid, plate, dose in in_range:
            low = dose['low_600_krad']
            # Convert krad to Gy: 1 krad = 10 Gy
            gy = low * 10 if low else 0
            c1info = ""
            if plate and plate in c1_doses:
                c1info = (f" (C1: {c1_doses[plate]['gamma_gy']:.0f} Gy gamma, "
                         f"{c1_doses[plate]['neutron_rem']:.0f} rem neutron)")
            print(f"    {rid} -> {plate or '?'}: {low:.1f} krad = {gy:.0f} Gy{c1info}")

    return results


print("Campaign 2 Rod Dosimetry: Raw Reading Summary")
print(f"Source: {os.path.basename(RAW_FILE)}")
print(f"Total rows (excl header): {sum(len(d['readings']) for d in rods.values())}")
print(f"Unique rod IDs parsed: {len(rods)}")
print(f"  C1-final (R-681 to R-740): {len(c1_final_rods)}")
print(f"  C2-new   (R-741 to R-800): {len(c2_new_rods)}")
print(f"  Other:                      {len(other_rods)}")
if other_rods:
    print(f"    Other IDs: {sorted(other_rods.keys())}")

# Analyze each population
c1f_results = analyze_population(c1_final_rods,
    "C1-FINAL RODS (R-681 to R-740)\n"
    "  Installed Jan 2026, integrating shutdown + early C2 beam\n"
    "  (Sep 2025 shutdown -> Mar 2026 restore -> low-E physics)")

c2n_results = analyze_population(c2_new_rods,
    "C2-NEW RODS (R-741 to R-800)\n"
    "  Installed between Apr 20 and May 15, 2026\n"
    "  Very short exposure at 0.69 GeV/pass, expect noise-floor")

if other_rods:
    other_results = analyze_population(other_rods,
        "OTHER RODS (outside 681-800 range)")

# ── Key finding: compare populations ──────────────────────────────────────
print(f"\n{'='*70}")
print("  COMPARISON: C1-final vs C2-new rod populations")
print(f"{'='*70}")

c1f_doses = [compute_dose_estimate(d)["low_600_krad"]
             for d in c1_final_rods.values()
             if compute_dose_estimate(d)["low_600_krad"] is not None]
c2n_doses = [compute_dose_estimate(d)["low_600_krad"]
             for d in c2_new_rods.values()
             if compute_dose_estimate(d)["low_600_krad"] is not None]

if c1f_doses and c2n_doses:
    c1f_arr = np.array(c1f_doses)
    c2n_arr = np.array(c2n_doses)
    print(f"\n  {'Metric':<25} {'C1-final':>12} {'C2-new':>12}")
    print(f"  {'-'*25} {'-'*12} {'-'*12}")
    print(f"  {'N rods':<25} {len(c1f_arr):>12} {len(c2n_arr):>12}")
    print(f"  {'Median Low@600 (krad)':<25} {np.median(c1f_arr):>12.2f} {np.median(c2n_arr):>12.2f}")
    print(f"  {'Mean Low@600 (krad)':<25} {c1f_arr.mean():>12.2f} {c2n_arr.mean():>12.2f}")
    print(f"  {'Std Low@600 (krad)':<25} {c1f_arr.std():>12.2f} {c2n_arr.std():>12.2f}")
    print(f"  {'Min (krad)':<25} {c1f_arr.min():>12.2f} {c2n_arr.min():>12.2f}")
    print(f"  {'Max (krad)':<25} {c1f_arr.max():>12.2f} {c2n_arr.max():>12.2f}")
    print(f"  {'In valid range (>=2)':<25} "
          f"{sum(1 for d in c1f_doses if d >= 2.0):>12} "
          f"{sum(1 for d in c2n_doses if d >= 2.0):>12}")

# ── Interpret ─────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("  INTERPRETATION")
print(f"{'='*70}")
print("""
  1. MOST READINGS ARE BELOW THE FWT-70 DETECTION THRESHOLD (2 krad at Low@600nm).
     This is expected:
     - C1-final rods (R-681-740): installed Jan 2026, sat through shutdown
       (no beam Sep 2025-Mar 2026), then low-energy restore/physics at
       0.69 GeV/pass. Minimal dose accumulation.
     - C2-new rods (R-741-800): installed late Apr/early May 2026,
       only days-to-weeks of exposure at 0.69 GeV/pass.

  2. ANY RODS IN THE VALID RANGE likely correspond to HIGH-DOSE LOCATIONS
     (linac NDX positions), where even short beam-on periods at low energy
     accumulate measurable dose.

  3. PLATE MAPPING for all rods is now available:
     - C1-final rods (R-681-740): from C1 measurement .dat files
     - C2-new rods (R-741-800): from April 2026 Teslameter .dat files
     See c2_rod_plate_map.csv for the full mapping.

  4. These raw readings have NOT been processed through Kirsten's AIdata
     pipeline. The calibrated krad values use a simple linear model
     (dose = OD * slope - intercept). Kirsten's methodology applies
     additional validity checks, cross-wavelength averaging, and
     OSL integration.

  5. UNIT NOTE: Spreadsheet columns say "rad" but C1 convention established
     these are krad. 1 krad = 10 Gy.
""")

# ── Save CSV summary ──────────────────────────────────────────────────────
csv_path = os.path.join(OUT_DIR, "c2_rod_raw_summary.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["rod_id", "rod_num", "population", "plate",
                     "low_600_krad", "high_600_krad", "in_valid_range",
                     "n_low_readings", "n_high_readings",
                     "c1_gamma_gy", "c1_neutron_rem"])

    all_results = []
    for rid, data in sorted(rods.items(), key=lambda x: x[1]["rod_num"]):
        dose = compute_dose_estimate(data)
        n = data["rod_num"]
        if 681 <= n <= 740:
            pop = "C1-final"
        elif 741 <= n <= 800:
            pop = "C2-new"
        else:
            pop = "other"
        plate = rod_to_plate.get(rid, "")
        c1g = c1_doses.get(plate, {}).get("gamma_gy", "")
        c1n = c1_doses.get(plate, {}).get("neutron_rem", "")

        writer.writerow([
            rid, n, pop, plate,
            f"{dose['low_600_krad']:.3f}" if dose['low_600_krad'] is not None else "",
            f"{dose['high_600_krad']:.3f}" if dose['high_600_krad'] is not None else "",
            "yes" if dose['in_range'] else "no",
            dose['n_low'], dose['n_high'],
            f"{c1g:.1f}" if isinstance(c1g, float) else "",
            f"{c1n:.1f}" if isinstance(c1n, float) else ""
        ])

print(f"\n  CSV saved: {csv_path}")
print(f"  Done.")
