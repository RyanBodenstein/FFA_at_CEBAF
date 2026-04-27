#!/usr/bin/env python3
"""
Phase 3: Parse AIdata (Kirsten's pre-integrated cumulative doses).

Reads AIdata_260112.zip containing 1,931 .dat files with cumulative
photon and neutron doses per sample per measurement date.

Units: REM (dose equivalent).
  Confirmed by unsaturated plate crosscheck:
    Y-13 AIdata photon = 2998.4 rem, OSL photon = 2,998,359 mrem → exact match
    Y-15 AIdata photon = 1174.0 rem, OSL photon = 1,173,990 mrem → exact match

Two file formats (per 00_contents.txt):
  Helmholtz (7 cols): date, measurement(mWC), neutron_cum_rem, σ_n_rem,
                      photon_cum_rem, σ_p_rem, days_since_install
  Teslameter (10 cols): date, x(T), y(T), z(T), temp(C), neutron_cum_rem,
                         σ_n_rem, photon_cum_rem, σ_p_rem, days_since_install

Output:
  Rod_Dosimetry/aidata_cumulative.csv — final cumulative per plate
  Rod_Dosimetry/aidata_timeline.csv   — date-by-date cumulative per plate
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

AIDATA_ZIP = os.path.join(BASE, 'Radiation Info', 'Dosimetry Reports', 'Rods',
                          'AIdata_260112.zip')

# Unit conversions
REM_TO_MREM = 1000.0
REM_TO_GY_PHOTON = 0.01  # 1 rem = 0.01 Sv, and for photons Q=1, so 1 rem = 0.01 Gy

# Lab Y-plates (from Materials_Arrangements_Spreadsheet.xlsx 'Lab - Y Materials')
# These should NOT be included in tunnel dose analysis
LAB_Y_PLATES = {8, 14, 27, 28, 29, 31, 33, 35, 37}


def parse_aidata_file(lines, file_type):
    """Parse a single AIdata .dat file.

    Args:
        lines: list of text lines
        file_type: 'helmholtz' or 'teslameter'

    Returns: list of dicts with keys:
        date, neutron_cum_rem, sigma_n_rem, photon_cum_rem, sigma_p_rem,
        days_since_install
    """
    results = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')

        try:
            date_str = parts[0].strip()[:10]
            if not re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                continue

            if file_type == 'helmholtz' and len(parts) >= 7:
                # date, mWC, neutron, σ_n, photon, σ_p, days
                neutron = float(parts[2])
                sigma_n = float(parts[3])
                photon = float(parts[4])
                sigma_p = float(parts[5])
                days = float(parts[6])
            elif file_type == 'teslameter' and len(parts) >= 10:
                # date, x, y, z, temp, neutron, σ_n, photon, σ_p, days
                neutron = float(parts[5])
                sigma_n = float(parts[6])
                photon = float(parts[7])
                sigma_p = float(parts[8])
                days = float(parts[9])
            else:
                continue

            results.append({
                'date': date_str,
                'neutron_cum_rem': neutron,
                'sigma_n_rem': sigma_n,
                'photon_cum_rem': photon,
                'sigma_p_rem': sigma_p,
                'days_since_install': days,
            })
        except (ValueError, IndexError):
            continue

    return results


def sample_to_plate(sample):
    """Convert sample name to plate name.
    Y-1-1 -> Y-1, An-10-1-1 -> Hn-10, Hn-6-1 -> Hn-6
    """
    ym = re.match(r'(Y-\d+)-\d+', sample)
    if ym:
        return ym.group(1)
    am = re.match(r'A([ns])-(\d+)-\d+-\d+', sample)
    if am:
        return 'H%s-%s' % (am.group(1), am.group(2))
    hm = re.match(r'(H[ns]-\d+)-\d+', sample)
    if hm:
        return hm.group(1)
    return None


def main():
    print("=" * 70)
    print("Phase 3: Parse AIdata Zip")
    print("=" * 70)

    if not os.path.exists(AIDATA_ZIP):
        print("ERROR: AIdata zip not found: %s" % AIDATA_ZIP)
        return

    zf = zipfile.ZipFile(AIDATA_ZIP, 'r')
    names = [n for n in zf.namelist() if n.endswith('.dat') and '00_contents' not in n]
    print("  Total .dat files in zip: %d" % len(names))

    # Parse all files, using _helmholtz as primary (most complete timeline)
    # Only use _top for teslameter data to avoid duplicates
    plate_data = defaultdict(list)  # plate -> list of measurement dicts
    file_counts = {'helmholtz': 0, 'teslameter': 0, 'skipped': 0}

    for name in sorted(names):
        bname = os.path.basename(name)

        # Determine file type
        if '_helmholtz.dat' in bname:
            file_type = 'helmholtz'
            sample = bname.replace('_helmholtz.dat', '')
        elif '_top.dat' in bname:
            file_type = 'teslameter'
            sample = bname.replace('_top.dat', '')
        else:
            # Skip _front.dat and _side.dat to avoid duplicate counting
            file_counts['skipped'] += 1
            continue

        plate = sample_to_plate(sample)
        if plate is None:
            continue

        data = zf.read(name).decode('utf-8', errors='replace')
        lines = data.strip().split('\n')
        measurements = parse_aidata_file(lines, file_type)

        if measurements:
            file_counts[file_type] += 1
            # For each plate, merge measurements from helmholtz and teslameter
            # Helmholtz preferred (typically more measurement dates)
            for m in measurements:
                m['source_file'] = bname
                m['sample'] = sample
                m['plate'] = plate
                plate_data[plate].append(m)

    zf.close()

    print("  Helmholtz files parsed: %d" % file_counts['helmholtz'])
    print("  Teslameter files parsed: %d" % file_counts['teslameter'])
    print("  Skipped (front/side): %d" % file_counts['skipped'])
    print("  Plates with data: %d" % len(plate_data))

    # Deduplicate: for each plate+date, take the measurement with the highest
    # photon dose (usually helmholtz and teslameter agree, but helmholtz is
    # more complete)
    deduped = {}
    for plate, measurements in plate_data.items():
        by_date = defaultdict(list)
        for m in measurements:
            by_date[m['date']].append(m)

        best_timeline = []
        for date in sorted(by_date.keys()):
            entries = by_date[date]
            # Pick entry with highest photon dose (most complete integration)
            best = max(entries, key=lambda e: e['photon_cum_rem'])
            best_timeline.append(best)

        deduped[plate] = best_timeline

    # Build cumulative summary (final measurement per plate)
    cumulative = {}
    for plate, timeline in sorted(deduped.items()):
        if not timeline:
            continue
        final = timeline[-1]

        # Flag lab Y-plates
        is_lab = False
        if plate.startswith('Y-'):
            pnum = int(plate.split('-')[1])
            is_lab = pnum in LAB_Y_PLATES

        cumulative[plate] = {
            'plate': plate,
            'final_date': final['date'],
            'days_since_install': final['days_since_install'],
            'photon_cum_rem': final['photon_cum_rem'],
            'sigma_photon_rem': final['sigma_p_rem'],
            'neutron_cum_rem': final['neutron_cum_rem'],
            'sigma_neutron_rem': final['sigma_n_rem'],
            'photon_cum_gy': final['photon_cum_rem'] * REM_TO_GY_PHOTON,
            'n_measurements': len(timeline),
            'is_lab': is_lab,
        }

    # Write cumulative CSV
    cum_csv = os.path.join(OUT_DIR, 'aidata_cumulative.csv')
    cum_fields = [
        'plate', 'is_lab', 'final_date', 'days_since_install',
        'photon_cum_rem', 'sigma_photon_rem',
        'neutron_cum_rem', 'sigma_neutron_rem',
        'photon_cum_gy', 'n_measurements',
    ]
    cum_rows = []
    for plate in sorted(cumulative.keys(),
                        key=lambda x: (x[0], int(re.search(r'\d+', x).group()))):
        cum_rows.append(cumulative[plate])

    with open(cum_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cum_fields)
        writer.writeheader()
        writer.writerows(cum_rows)
    print("\n  Wrote %s (%d plates)" % (cum_csv, len(cum_rows)))

    # Write timeline CSV
    tl_csv = os.path.join(OUT_DIR, 'aidata_timeline.csv')
    tl_fields = [
        'plate', 'date', 'photon_cum_rem', 'sigma_p_rem',
        'neutron_cum_rem', 'sigma_n_rem', 'days_since_install',
    ]
    tl_rows = []
    for plate in sorted(deduped.keys(),
                        key=lambda x: (x[0], int(re.search(r'\d+', x).group()))):
        for m in deduped[plate]:
            tl_rows.append({
                'plate': plate,
                'date': m['date'],
                'photon_cum_rem': m['photon_cum_rem'],
                'sigma_p_rem': m['sigma_p_rem'],
                'neutron_cum_rem': m['neutron_cum_rem'],
                'sigma_n_rem': m['sigma_n_rem'],
                'days_since_install': m['days_since_install'],
            })

    with open(tl_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=tl_fields)
        writer.writeheader()
        writer.writerows(tl_rows)
    print("  Wrote %s (%d rows)" % (tl_csv, len(tl_rows)))

    # Print summary
    print("\n--- AIdata Cumulative Summary ---")
    y_plates = {k: v for k, v in cumulative.items() if k.startswith('Y-')}
    hn_plates = {k: v for k, v in cumulative.items() if k.startswith('Hn-')}
    hs_plates = {k: v for k, v in cumulative.items() if k.startswith('Hs-')}
    print("  Y-plates: %d" % len(y_plates))
    print("  Hn-plates: %d" % len(hn_plates))
    print("  Hs-plates: %d" % len(hs_plates))

    # Separate tunnel and lab counts
    tunnel_y = {k: v for k, v in y_plates.items() if not v.get('is_lab', False)}
    lab_y = {k: v for k, v in y_plates.items() if v.get('is_lab', False)}
    print("  Y-plates (tunnel): %d" % len(tunnel_y))
    print("  Y-plates (lab): %d" % len(lab_y))

    print("\n%-8s %5s %14s %10s %10s %10s" % (
        'Plate', 'Type', 'Photon(rem)', 'Photon(Gy)', 'Neutr(rem)', 'Days'))
    print("-" * 65)
    for plate in sorted(y_plates.keys(), key=lambda x: int(x.split('-')[1])):
        c = cumulative[plate]
        ptype = 'LAB' if c.get('is_lab', False) else 'TUN'
        print("%-8s %5s %14.1f %10.1f %10.1f %10.0f" % (
            plate, ptype, c['photon_cum_rem'], c['photon_cum_gy'],
            c['neutron_cum_rem'], c['days_since_install']))

    # Dose range
    photon_vals = [c['photon_cum_rem'] for c in cumulative.values()]
    print("\n  Photon dose range: %.1f – %.1f rem" % (min(photon_vals), max(photon_vals)))
    print("  Photon dose range: %.2f – %.0f Gy" % (
        min(photon_vals) * REM_TO_GY_PHOTON,
        max(photon_vals) * REM_TO_GY_PHOTON))

    # Beam-off verification: check that dose didn't increase Oct→Jan
    print("\n--- Beam-off verification (Oct → Jan) ---")
    beamoff_ok = 0
    beamoff_fail = 0
    for plate, timeline in deduped.items():
        if not plate.startswith('Y-'):
            continue
        # Skip lab plates
        pnum = int(plate.split('-')[1])
        if pnum in LAB_Y_PLATES:
            continue
        dates = {m['date']: m for m in timeline}
        # Find Oct and Jan dates
        oct_dates = [d for d in dates if d.startswith('2025-10')]
        jan_dates = [d for d in dates if d.startswith('2026-01')]
        if oct_dates and jan_dates:
            oct_photon = dates[max(oct_dates)]['photon_cum_rem']
            jan_photon = dates[min(jan_dates)]['photon_cum_rem']
            delta = jan_photon - oct_photon
            if abs(delta) < 0.1:
                beamoff_ok += 1
            else:
                beamoff_fail += 1
                print("  WARNING: %s photon increased by %.2f rem (Oct→Jan)" % (
                    plate, delta))

    print("  Beam-off verified (photon unchanged): %d plates" % beamoff_ok)
    if beamoff_fail:
        print("  FAILED beam-off check: %d plates" % beamoff_fail)
    else:
        print("  All Y-plates pass beam-off check.")

    print("\nDone.")
    return cumulative, deduped


if __name__ == '__main__':
    cumulative, deduped = main()
