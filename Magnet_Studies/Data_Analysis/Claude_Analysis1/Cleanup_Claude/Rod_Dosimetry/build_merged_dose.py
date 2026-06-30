#!/usr/bin/env python3
"""
Phase 6: Build merged dose file.

Combines:
  - AIdata photon (primary gamma dose, in rem) — true gamma for all plates
  - AIdata neutron (in rem) — true for 8 high-dose plates, same as OSL for rest
  - OSL neutron (from CR-39, in mrem) — fallback/comparison
  - OSL beta (in mrem)

Flags:
  - ai_photon_source: 'osl_match' (unsaturated) or 'rod_derived' (saturated)
  - ai_neutron_source: 'osl_match' or 'independently_derived'
  - is_osl_saturated: True if any OSL badges were saturated

Output:
  Rod_Dosimetry/merged_dose_final.csv — one row per plate, authoritative doses
"""

import os
import csv
import re

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEANUP = os.path.join(BASE, 'Cleanup_Claude')
OUT_DIR = os.path.join(CLEANUP, 'Rod_Dosimetry')
OSL_DIR = os.path.join(CLEANUP, 'Dosimetry', 'OSL_Area')

# Unit conversions
REM_TO_MREM = 1000.0
REM_TO_GY_PHOTON = 0.01   # photon: Q=1, 1 rem = 0.01 Gy
REM_TO_GY_NEUTRON = 0.001  # neutron: Q≈10, 1 rem ≈ 0.001 Gy (approximate)

# Lab Y-plates (from Materials_Arrangements_Spreadsheet.xlsx)
LAB_Y_PLATES = {8, 14, 27, 28, 29, 31, 33, 35, 37}


def main():
    print("=" * 70)
    print("Phase 6: Build Merged Dose File")
    print("=" * 70)

    # Load AIdata cumulative (include lab plates — they'll be flagged)
    ai = {}
    with open(os.path.join(OUT_DIR, 'aidata_cumulative.csv')) as f:
        for row in csv.DictReader(f):
            ai[row['plate']] = row

    # Load OSL cumulative
    osl = {}
    with open(os.path.join(OSL_DIR, 'plate_cumulative_dose.csv')) as f:
        for row in csv.DictReader(f):
            osl[row['plate']] = row

    # Determine source classification for each plate
    # By checking if AI values match OSL values (within 1%)
    all_plates = sorted(set(list(ai.keys()) + list(osl.keys())),
                        key=lambda x: (x[0], int(re.search(r'\d+', x).group())))

    rows = []
    for plate in all_plates:
        a = ai.get(plate)
        o = osl.get(plate)

        if not a and not o:
            continue

        # Flag lab vs tunnel
        is_lab = False
        if plate.startswith('Y-'):
            pnum = int(plate.split('-')[1])
            is_lab = pnum in LAB_Y_PLATES

        row = {'plate': plate, 'is_lab': is_lab}

        # AIdata photon
        if a:
            ai_phot_rem = float(a['photon_cum_rem'])
            ai_phot_gy = float(a['photon_cum_gy'])
            ai_neut_rem = float(a['neutron_cum_rem'])
            ai_sigma_p = float(a['sigma_photon_rem'])
            ai_sigma_n = float(a['sigma_neutron_rem'])
            ai_days = float(a['days_since_install'])
            ai_n_meas = int(a['n_measurements'])
        else:
            ai_phot_rem = 0
            ai_phot_gy = 0
            ai_neut_rem = 0
            ai_sigma_p = 0
            ai_sigma_n = 0
            ai_days = 0
            ai_n_meas = 0

        # OSL data
        if o:
            osl_body = float(o['body_mrem'])
            osl_photon = float(o['photon_mrem'])
            osl_beta = float(o['beta_mrem'])
            osl_neutron = float(o['neutron_mrem'])
            osl_n_sat = int(o['n_saturated'])
            osl_is_lb = o['is_lower_bound'].strip() == 'True'
        else:
            osl_body = 0
            osl_photon = 0
            osl_beta = 0
            osl_neutron = 0
            osl_n_sat = 0
            osl_is_lb = False

        # Classify photon source
        ai_phot_mrem = ai_phot_rem * REM_TO_MREM
        if osl_photon > 0 and ai_phot_mrem > 0:
            ratio = ai_phot_mrem / osl_photon
            if abs(ratio - 1.0) < 0.05:  # within 5%
                photon_source = 'osl_match'
            elif osl_is_lb:
                photon_source = 'rod_derived'
            else:
                photon_source = 'supplemented'  # AI slightly different from OSL
        elif ai_phot_rem > 0:
            photon_source = 'rod_derived'
        else:
            photon_source = 'no_aidata'

        # Classify neutron source
        osl_neut_rem = osl_neutron / REM_TO_MREM  # convert to rem for comparison
        if osl_neut_rem > 0 and ai_neut_rem > 0:
            n_ratio = ai_neut_rem / osl_neut_rem
            if abs(n_ratio - 1.0) < 0.05:
                neutron_source = 'osl_match'
            else:
                neutron_source = 'independently_derived'
        elif ai_neut_rem > 0:
            neutron_source = 'independently_derived'
        else:
            neutron_source = 'osl_only'

        row.update({
            # Primary gamma dose (AIdata)
            'gamma_dose_rem': '%.2f' % ai_phot_rem,
            'gamma_dose_gy': '%.2f' % ai_phot_gy,
            'gamma_sigma_rem': '%.2f' % ai_sigma_p,
            'gamma_source': photon_source,
            # Neutron dose (AIdata or OSL)
            'neutron_dose_rem': '%.2f' % ai_neut_rem if ai_neut_rem > 0 else '%.2f' % osl_neut_rem,
            'neutron_sigma_rem': '%.2f' % ai_sigma_n,
            'neutron_source': neutron_source,
            # OSL beta (AIdata doesn't have this separately)
            'beta_dose_mrem': '%.0f' % osl_beta,
            # OSL reference values
            'osl_body_mrem': '%.0f' % osl_body,
            'osl_photon_mrem': '%.0f' % osl_photon,
            'osl_neutron_mrem': '%.0f' % osl_neutron,
            'osl_n_saturated': osl_n_sat,
            'osl_is_lower_bound': osl_is_lb,
            # AIdata metadata
            'ai_days_since_install': '%.0f' % ai_days,
            'ai_n_measurements': ai_n_meas,
        })

        rows.append(row)

    # Write output
    out_csv = os.path.join(OUT_DIR, 'merged_dose_final.csv')
    fields = [
        'plate', 'is_lab',
        'gamma_dose_rem', 'gamma_dose_gy', 'gamma_sigma_rem', 'gamma_source',
        'neutron_dose_rem', 'neutron_sigma_rem', 'neutron_source',
        'beta_dose_mrem',
        'osl_body_mrem', 'osl_photon_mrem', 'osl_neutron_mrem',
        'osl_n_saturated', 'osl_is_lower_bound',
        'ai_days_since_install', 'ai_n_measurements',
    ]

    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print("  Wrote: %s (%d plates)" % (out_csv, len(rows)))

    # Summary
    y_rows = [r for r in rows if r['plate'].startswith('Y-')]
    h_rows = [r for r in rows if r['plate'].startswith('H')]

    print("\n--- Summary ---")
    print("  Total plates: %d (Y=%d, H=%d)" % (len(rows), len(y_rows), len(h_rows)))

    for source_type, label in [('gamma_source', 'Gamma'), ('neutron_source', 'Neutron')]:
        from collections import Counter
        counts = Counter(r[source_type] for r in y_rows)
        print("\n  Y-plate %s source:" % label)
        for src, n in counts.most_common():
            print("    %-25s: %d" % (src, n))

    # Dose range for Y-plates
    gy_vals = [float(r['gamma_dose_gy']) for r in y_rows if float(r['gamma_dose_gy']) > 0]
    if gy_vals:
        print("\n  Y-plate gamma dose range: %.1f – %.0f Gy" % (min(gy_vals), max(gy_vals)))

    print("\nDone.")


if __name__ == '__main__':
    main()
