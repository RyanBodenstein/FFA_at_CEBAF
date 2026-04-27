#!/usr/bin/env python3
"""
Extract neutron thermal/fast breakdowns from Landauer PDF dose reports.

The xlsx files only have combined "Neutron Dose". The PDFs break neutrons into:
  - NT (thermal neutron)
  - NF (fast neutron)

This script parses all PDF reports and outputs a CSV with the breakdown,
which can be joined with master_doses.csv on (report_date, part_nbr).

Output: Dosimetry/OSL_Area/neutron_breakdown.csv
"""

import os
import re
import csv

import PyPDF2

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREAS_DIR = os.path.join(BASE, 'Radiation Info', 'Dosimetry Reports', 'Areas')
BN_DIR = os.path.join(AREAS_DIR, 'BetterNaming')
OSL_DIR = os.path.join(BASE, 'Cleanup_Claude', 'Dosimetry', 'OSL_Area')

# PDF sources: (report_date, filepath)
PDF_SOURCES = [
    ('20250227', os.path.join(BN_DIR, '20250227.pdf')),
    ('20250306', os.path.join(BN_DIR, '20250306.pdf')),
    ('20250331', os.path.join(BN_DIR, '20250331.pdf')),
    ('20250502', os.path.join(BN_DIR, '20250502.pdf')),
    ('20250516', os.path.join(BN_DIR, '20250516.pdf')),
    ('20250624', os.path.join(BN_DIR, '20250624.pdf')),
    ('20250804', os.path.join(BN_DIR, '20250804.pdf')),
    ('20250819', os.path.join(BN_DIR, '20250819.pdf')),
    ('20250915', os.path.join(BN_DIR, '20250915.pdf')),
    ('20250930', os.path.join(BN_DIR, '20250930.pdf')),
    # Oct 2025 (same data as Sep 30, but include for completeness)
    ('20251024', os.path.join(AREAS_DIR,
        'DoseReport_Account738211 _Created2025-10-23_AWO2526801163.pdf')),
]


def parse_pdf_neutrons(filepath, report_date):
    """Extract Part# -> (NT_mrem, NF_mrem) from a Landauer PDF."""
    results = []

    try:
        pdf = PyPDF2.PdfReader(filepath)
    except Exception as e:
        print(f"  ERROR reading {filepath}: {e}")
        return results

    # Concatenate all page text
    all_text = ''
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            all_text += text + '\n'

    # Strategy: find each dosimeter entry by Part Number, then look for
    # neutron thermal (T suffix) and fast (F suffix) lines.
    #
    # Pattern for Part# line: 5-digit number at start, followed by dose or M
    # e.g. "00219 11570 L02TN WHBODY ..."
    #
    # Neutron lines follow the pattern:
    #   "730T 730 730                     *N"  (thermal)
    #   "10840F 10840 10840                     *N" (fast)
    #   "MT M M                     *N" (below minimum)

    lines = all_text.split('\n')

    current_part = None
    nt_val = None
    nf_val = None
    neutron_exceeded = False

    def flush():
        nonlocal current_part, nt_val, nf_val, neutron_exceeded
        if current_part is not None:
            results.append({
                'report_date': report_date,
                'part_nbr': current_part,
                'nt_mrem': nt_val if nt_val is not None else 0,
                'nf_mrem': nf_val if nf_val is not None else 0,
                'nt_is_M': nt_val is None,  # below minimum
                'nf_is_M': nf_val is None,
                'neutron_exceeded': neutron_exceeded,
            })
        current_part = None
        nt_val = None
        nf_val = None
        neutron_exceeded = False

    for line in lines:
        line_stripped = line.strip()

        # Match part number line: starts with 5-digit number followed by dose/M and L02TN
        part_match = re.match(r'^(\d{5})\s+(\d+|M)\s+L02TN\s+WHBODY', line_stripped)
        if part_match:
            flush()
            current_part = int(part_match.group(1))
            continue

        if current_part is None:
            # Check for neutron exceeded note (can appear without a new part match)
            if 'Neutron component has exceeded' in line_stripped:
                # This belongs to previous entry — but we already flushed.
                # Try to update last result
                if results and results[-1]['report_date'] == report_date:
                    results[-1]['neutron_exceeded'] = True
            continue

        # Neutron thermal line: number followed by T (or MT for M)
        # Pattern: "730T 730 730" or "MT M M"
        nt_match = re.match(r'^(\d+|M)T\s', line_stripped)
        if nt_match:
            val = nt_match.group(1)
            nt_val = int(val) if val != 'M' else None
            continue

        # Neutron fast line: number followed by F
        nf_match = re.match(r'^(\d+|M)F\s', line_stripped)
        if nf_match:
            val = nf_match.group(1)
            nf_val = int(val) if val != 'M' else None
            continue

        # Check for neutron exceeded note
        if 'Neutron component has exceeded' in line_stripped:
            neutron_exceeded = True
            continue

        # New Part# might not match our pattern exactly (some have spaces)
        # Also catch lines that start the next dosimeter
        alt_match = re.match(r'^(\d{5})\s+(L02TN|M\s+L02TN)', line_stripped)
        if alt_match:
            flush()
            current_part = int(alt_match.group(1))

    flush()  # Don't forget the last entry

    return results


def main():
    print("=" * 70)
    print("PDF Neutron Thermal/Fast Breakdown Extractor")
    print("=" * 70)

    all_results = []

    for report_date, filepath in PDF_SOURCES:
        if not os.path.exists(filepath):
            print(f"  {report_date}: FILE NOT FOUND - {filepath}")
            continue

        results = parse_pdf_neutrons(filepath, report_date)
        print(f"  {report_date}: {len(results)} dosimeters parsed")

        # Count how many have non-zero NT or NF
        has_nt = sum(1 for r in results if r['nt_mrem'] > 0)
        has_nf = sum(1 for r in results if r['nf_mrem'] > 0)
        exceeded = sum(1 for r in results if r['neutron_exceeded'])
        print(f"    NT>0: {has_nt}, NF>0: {has_nf}, neutron exceeded: {exceeded}")

        all_results.extend(results)

    print(f"\nTotal entries: {len(all_results)}")

    # Summary
    has_any = [r for r in all_results if r['nt_mrem'] > 0 or r['nf_mrem'] > 0]
    print(f"Entries with any neutron: {len(has_any)}")

    if has_any:
        max_nt = max(has_any, key=lambda r: r['nt_mrem'])
        max_nf = max(has_any, key=lambda r: r['nf_mrem'])
        print(f"Max thermal neutron: {max_nt['nt_mrem']} mrem "
              f"(Part {max_nt['part_nbr']}, {max_nt['report_date']})")
        print(f"Max fast neutron: {max_nf['nf_mrem']} mrem "
              f"(Part {max_nf['part_nbr']}, {max_nf['report_date']})")

    # NT fraction analysis
    fracs = []
    for r in has_any:
        total_n = r['nt_mrem'] + r['nf_mrem']
        if total_n > 0:
            fracs.append(r['nt_mrem'] / total_n)
    if fracs:
        fracs.sort()
        print(f"\nThermal/Total neutron fraction:")
        print(f"  Median: {fracs[len(fracs)//2]:.3f}")
        print(f"  Mean: {sum(fracs)/len(fracs):.3f}")
        print(f"  Range: {min(fracs):.3f} - {max(fracs):.3f}")

    # Write CSV
    out_csv = os.path.join(OSL_DIR, 'neutron_breakdown.csv')
    fieldnames = ['report_date', 'part_nbr', 'nt_mrem', 'nf_mrem',
                  'nt_is_M', 'nf_is_M', 'neutron_exceeded']
    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in sorted(all_results, key=lambda x: (x['report_date'], x['part_nbr'])):
            writer.writerow(r)

    print(f"\nWritten: {out_csv} ({len(all_results)} rows)")

    # Validation: compare with xlsx neutron totals
    print("\n--- Validation: NT+NF vs xlsx Neutron Dose ---")
    master_csv = os.path.join(OSL_DIR, 'master_doses.csv')
    if os.path.exists(master_csv):
        xlsx_data = {}
        with open(master_csv) as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row['report_date'], int(row['part_nbr']))
                xlsx_data[key] = int(row['neutron_mrem'])

        matches = 0
        mismatches = 0
        close = 0
        for r in all_results:
            key = (r['report_date'], r['part_nbr'])
            if key in xlsx_data:
                xlsx_n = xlsx_data[key]
                pdf_n = r['nt_mrem'] + r['nf_mrem']
                if xlsx_n == pdf_n:
                    matches += 1
                elif abs(xlsx_n - pdf_n) <= 10:
                    close += 1
                else:
                    mismatches += 1
                    if mismatches <= 10:
                        print(f"  Mismatch: Part {r['part_nbr']} ({r['report_date']}): "
                              f"xlsx={xlsx_n}, pdf NT+NF={pdf_n} "
                              f"(NT={r['nt_mrem']}, NF={r['nf_mrem']})")

        print(f"\n  Exact match: {matches}")
        print(f"  Close (within 10 mrem): {close}")
        print(f"  Mismatch: {mismatches}")

    print("\nDone.")


if __name__ == '__main__':
    main()
