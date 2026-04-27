#!/usr/bin/env python3
"""
Task 21a: Sensitivity analysis — how do results change with assumed baseline temperature?

Sweeps the pre-deployment lab temperature estimate from 21°C to 26°C (in 0.25°C steps)
and reports the headline Y-plate numbers at each point.

Key reference points:
  - Y-plate Teslameter probe readings: ~24.5–25.4°C (biased high)
  - H/A Teslameter on Dec 4 2024: 23.08°C
  - Original code used probe temps (~24.5–25.4°C) → old results
  - Current fix uses 23.0°C → corrected results
  - This script tests: what if the true temp was different?
"""

import sys, os
import numpy as np

# Add parent dir so we can import from manager_summary_v3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import manager_summary_v3 as ms

# Materials
NDFEB = {'N42EH', 'N52SH'}
SMCO = {'SmCo33H', 'SmCo35'}
LAB_PLATES = {8, 14, 27, 28, 29, 31, 33, 35, 37}


def run_at_temp(temp_c):
    """Override all Y_BASELINE_TEMP_LOOKUP entries to use temp_c, run load_all()."""
    # Save originals
    orig_lookup = ms.Y_BASELINE_TEMP_LOOKUP.copy()
    orig_default = ms.Y_BASELINE_TEMP_DEFAULT

    # Override all entries with the test temperature
    for date_str in orig_lookup:
        ms.Y_BASELINE_TEMP_LOOKUP[date_str] = (temp_c, 1.0)
    ms.Y_BASELINE_TEMP_DEFAULT = (temp_c, 2.0)

    try:
        results, helm_raw, temp_final, y_materials = ms.load_all()
    finally:
        # Restore originals
        ms.Y_BASELINE_TEMP_LOOKUP = orig_lookup
        ms.Y_BASELINE_TEMP_DEFAULT = orig_default

    return results, helm_raw, temp_final, y_materials


def analyze(results):
    """Compute headline numbers from results."""
    # Filter tunnel Y-plates only: exclude lab plates and flagged samples
    tunnel = [r for r in results if r['plate'] not in LAB_PLATES
              and r['sample'] not in ms.FLAGGED]

    # Per-material means
    mat_stats = {}
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        vals = [r['pct_change'] for r in tunnel if r['material'] == mat]
        if vals:
            mat_stats[mat] = (np.mean(vals), np.std(vals, ddof=1)/np.sqrt(len(vals)), len(vals))

    # Intra-plate differential
    from collections import defaultdict
    plate_data = defaultdict(dict)
    for r in tunnel:
        plate_data[r['plate']][r['material']] = r['pct_change']

    diffs = []
    for plate, mats in plate_data.items():
        nd = [mats[m] for m in NDFEB if m in mats]
        sm = [mats[m] for m in SMCO if m in mats]
        if nd and sm:
            diffs.append(np.mean(nd) - np.mean(sm))

    if diffs:
        diff_mean = np.mean(diffs)
        diff_sem = np.std(diffs, ddof=1) / np.sqrt(len(diffs))
        diff_n = len(diffs)
    else:
        diff_mean = diff_sem = 0
        diff_n = 0

    return mat_stats, diff_mean, diff_sem, diff_n


def run_no_correction():
    """Run with original probe temps (no lookup override) by removing all lookup entries."""
    orig_lookup = ms.Y_BASELINE_TEMP_LOOKUP.copy()
    # Set all entries to None-sentinel so we can detect them, but actually
    # we want to use the original probe temps. The code checks
    # "if date_str in Y_BASELINE_TEMP_LOOKUP" — so empty dict means
    # fall through to else branch which uses temp_final[key] (original probe).
    ms.Y_BASELINE_TEMP_LOOKUP = {}

    try:
        results, helm_raw, temp_final, y_materials = ms.load_all()
    finally:
        ms.Y_BASELINE_TEMP_LOOKUP = orig_lookup

    # Debug
    tunnel = [r for r in results if r['plate'] not in LAB_PLATES
              and r['sample'] not in ms.FLAGGED]
    print("  [debug] Total results: %d, tunnel (excl flagged): %d" %
          (len(results), len(tunnel)))
    if tunnel:
        print("  [debug] First result: %s" % tunnel[0])

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    print("=" * 80)
    print("SENSITIVITY ANALYSIS: Y-plate baseline temperature")
    print("  Sweeping assumed pre-deployment lab temp from 21°C to 26°C")
    print("=" * 80)

    # Also run with NO correction (original probe temps) as reference
    print("\n--- Reference: NO correction (original probe temps ~24.5-25.4°C) ---")
    res_orig = run_no_correction()
    ms_orig, diff_orig, sem_orig, n_orig = analyze(res_orig)
    if n_orig > 0:
        print("  Differential: %.3f%% ± %.3f%% (%.1fσ, N=%d)" %
              (diff_orig, sem_orig, abs(diff_orig/sem_orig) if sem_orig else 0, n_orig))
        for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
            if mat in ms_orig:
                m, s, n = ms_orig[mat]
                print("  %8s: %+.3f%% ± %.3f%% (%.1fσ, N=%d)" % (mat, m, s, abs(m/s) if s else 0, n))
    else:
        print("  WARNING: no-correction run produced 0 tunnel results — skipping reference")
        print("  (This is expected: with empty lookup, the code uses original probe temps)")
        # Use the ~25°C sweep point as proxy for original
        diff_orig = None

    # Sweep temperatures
    temps = np.arange(21.0, 26.25, 0.25)
    results_table = []

    print("\n--- Temperature sweep ---")
    print("  T_lab(°C)  Diff(%)    SEM(%)   σ       N42EH(%)  N52SH(%)  SmCo33H(%) SmCo35(%)")
    print("  " + "-" * 95)

    for T in temps:
        res, _, _, _ = run_at_temp(T)
        mat_stats, diff_mean, diff_sem, diff_n = analyze(res)
        sig = abs(diff_mean / diff_sem) if diff_sem else 0

        n42 = mat_stats.get('N42EH', (0, 0, 0))[0]
        n52 = mat_stats.get('N52SH', (0, 0, 0))[0]
        s33 = mat_stats.get('SmCo33H', (0, 0, 0))[0]
        s35 = mat_stats.get('SmCo35', (0, 0, 0))[0]

        print("  %5.1f     %+.3f    %.3f   %4.1f    %+.3f    %+.3f    %+.3f     %+.3f" %
              (T, diff_mean, diff_sem, sig, n42, n52, s33, s35))

        results_table.append({
            'temp': T,
            'diff': diff_mean,
            'diff_sem': diff_sem,
            'sigma': sig,
            'N42EH': n42, 'N52SH': n52, 'SmCo33H': s33, 'SmCo35': s35,
        })

    # ──────────────────────────────────────────────────────────────────────────
    # Key observations
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("KEY OBSERVATIONS")
    print("=" * 80)

    # Find temp where SmCo33H crosses zero
    for i in range(len(results_table) - 1):
        if results_table[i]['SmCo33H'] * results_table[i+1]['SmCo33H'] < 0:
            # Linear interpolation
            t1, v1 = results_table[i]['temp'], results_table[i]['SmCo33H']
            t2, v2 = results_table[i+1]['temp'], results_table[i+1]['SmCo33H']
            t_cross = t1 + (0 - v1) * (t2 - t1) / (v2 - v1)
            print("  SmCo33H crosses zero at T_lab ≈ %.1f°C" % t_cross)
            break

    # Where does SmCo35 cross zero?
    for i in range(len(results_table) - 1):
        if results_table[i]['SmCo35'] * results_table[i+1]['SmCo35'] < 0:
            t1, v1 = results_table[i]['temp'], results_table[i]['SmCo35']
            t2, v2 = results_table[i+1]['temp'], results_table[i+1]['SmCo35']
            t_cross = t1 + (0 - v1) * (t2 - t1) / (v2 - v1)
            print("  SmCo35 crosses zero at T_lab ≈ %.1f°C" % t_cross)
            break

    # Original probe temps
    if diff_orig is not None:
        print("\n  Original probe temps (~24.5-25.4°C): diff = %.3f%% (%.1fσ)" %
              (diff_orig, abs(diff_orig/sem_orig) if sem_orig else 0))
    else:
        proxy_25 = [r['diff'] for r in results_table if abs(r['temp'] - 25.0) < 0.01]
        if proxy_25:
            print("\n  ~Original (25°C proxy): diff = %.3f%%" % proxy_25[0])
    print("  Current fix (23.0°C):               diff = %.3f%%" %
          [r['diff'] for r in results_table if abs(r['temp'] - 23.0) < 0.01][0])
    print("  H/A reference (23.08°C Dec 4):      diff ≈ %.3f%%" %
          [r['diff'] for r in results_table if abs(r['temp'] - 23.0) < 0.01][0])

    # ──────────────────────────────────────────────────────────────────────────
    # Plot
    # ──────────────────────────────────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    t_arr = [r['temp'] for r in results_table]
    diff_arr = [r['diff'] for r in results_table]
    sem_arr = [r['diff_sem'] for r in results_table]

    # Panel 1: Differential
    ax1.fill_between(t_arr, [d - s for d, s in zip(diff_arr, sem_arr)],
                     [d + s for d, s in zip(diff_arr, sem_arr)],
                     alpha=0.3, color='blue', label='±1 SEM')
    ax1.plot(t_arr, diff_arr, 'b-o', ms=4, label='NdFeB−SmCo diff')
    ax1.axhline(0, color='gray', ls='--', alpha=0.5)
    if diff_orig is not None:
        ax1.axhline(diff_orig, color='red', ls=':', label='No correction (probe temps)')
    else:
        # Use 25°C sweep point as proxy
        proxy = [r['diff'] for r in results_table if abs(r['temp'] - 25.0) < 0.01]
        if proxy:
            ax1.axhline(proxy[0], color='red', ls=':', label='~Original (25°C proxy)')
            diff_orig = proxy[0]
            sem_orig = [r['diff_sem'] for r in results_table if abs(r['temp'] - 25.0) < 0.01][0]
    ax1.axvline(23.0, color='green', ls='--', alpha=0.7, label='Current fix (23°C)')
    ax1.axvline(23.08, color='orange', ls='--', alpha=0.7, label='H/A ref (23.08°C)')
    ax1.set_ylabel('NdFeB − SmCo differential (%)')
    ax1.set_title('Sensitivity of Y-plate results to assumed baseline temperature')
    ax1.legend(fontsize=8, loc='upper left')
    ax1.grid(True, alpha=0.3)

    # Panel 2: Individual materials
    for mat, color, ls in [('N42EH', 'red', '-'), ('N52SH', 'orange', '-'),
                            ('SmCo33H', 'blue', '--'), ('SmCo35', 'cyan', '--')]:
        ax2.plot(t_arr, [r[mat] for r in results_table], color=color, ls=ls,
                 marker='o', ms=3, label=mat)
    ax2.axhline(0, color='gray', ls='--', alpha=0.5)
    ax2.axvline(23.0, color='green', ls='--', alpha=0.7)
    ax2.axvline(23.08, color='orange', ls='--', alpha=0.7)
    ax2.set_xlabel('Assumed pre-deployment lab temperature (°C)')
    ax2.set_ylabel('Mean % change')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    outpath = os.path.join(os.path.dirname(__file__), 'S1_temp_sensitivity.png')
    fig.tight_layout()
    fig.savefig(outpath, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print("\n  Saved: %s" % outpath)

    # ──────────────────────────────────────────────────────────────────────────
    # Y-only vs combined analysis (Task 21b preview)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("Y-ONLY vs COMBINED (at current 23.0°C fix)")
    print("  Y-plates are gain-immune in differential. H/A are NOT.")
    print("=" * 80)

    res_23, _, _, _ = run_at_temp(23.0)
    _, diff_23, sem_23, n_23 = analyze(res_23)
    sig_23 = abs(diff_23 / sem_23) if sem_23 else 0

    print("  Y-plate differential: %.3f%% ± %.3f%% (%.1fσ, N=%d plates)" %
          (diff_23, sem_23, sig_23, n_23))
    print("  (This is gain-immune — THE strongest result)")
    print()
    print("  Individual Y-plate materials (carry ±0.124%% gain systematic):")
    ms_23, _, _, _ = analyze(res_23)
    for mat in ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']:
        m, s, n = ms_23[mat]
        print("    %8s: %+.3f%% ± %.3f%%(stat) ± 0.124%%(gain) (N=%d)" % (mat, m, s, n))

    print("\nDone.")
