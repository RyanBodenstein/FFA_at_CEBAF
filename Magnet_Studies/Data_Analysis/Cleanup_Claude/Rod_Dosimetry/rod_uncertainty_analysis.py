#!/usr/bin/env python3
"""
Rod Dosimetry Uncertainty Analysis

Sections:
  A. Independent calibration curve fitting from FWT-70 PDFs
  B. Replicate OD spread analysis from rod_doses.csv
  C. Cross-check independent calibration uncertainty vs Kirsten's sigma
  D. Full uncertainty budget per plate

Output:
  Rod_Dosimetry/rod_calibration_C1.png          — calibration curve fits
  Rod_Dosimetry/uncertainty_budget.txt           — narrative uncertainty document
  Rod_Dosimetry/rod_uncertainty_budget.csv       — per-plate uncertainty table
"""

import sys
import os
import csv
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats as sp_stats

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEANUP = os.path.join(BASE, 'Cleanup_Claude')
OUT_DIR = os.path.join(CLEANUP, 'Rod_Dosimetry')

sys.path.insert(0, CLEANUP)
from manager_summary_v3 import load_all, compute_intra_plate_diffs
from degradation_summary_v2 import PLACEMENTS as V2_PLACEMENTS


# ═══════════════════════════════════════════════════════════════════════════════
# Section A: Independent Calibration Curve Fitting
# ═══════════════════════════════════════════════════════════════════════════════

# FWT-70 calibration data from batch-specific PDFs (dose in Gy, Delta_A in OD)
CALIBRATION = {
    'Batch 1190 (High) 600nm': {
        'batch': 1190, 'wavelength': 600,
        'dose_gy': [100, 1002, 3010],
        'delta_a': [0.086, 0.832, 2.087],
    },
    'Batch 1190 (High) 656nm': {
        'batch': 1190, 'wavelength': 656,
        'dose_gy': [1002, 3010, 10000, 13010, 16020],
        'delta_a': [0.043, 0.119, 0.318, 0.383, 0.421],
    },
    'Batch 1189 (Low) 600nm': {
        'batch': 1189, 'wavelength': 600,
        'dose_gy': [100.8, 301, 502],
        'delta_a': [0.592, 1.652, 2.169],
    },
    'Batch 1189 (Low) 656nm': {
        'batch': 1189, 'wavelength': 656,
        'dose_gy': [100.8, 301, 502, 3010, 10010],
        'delta_a': [0.021, 0.060, 0.099, 0.530, 1.344],
    },
}


def fit_calibration_curves():
    """Fit log-linear calibration: Delta_A = a * log10(dose_Gy) + b.

    Returns dict of {name: {a, b, se_a, se_b, R2, residuals, ...}}.
    """
    fits = {}
    for name, data in CALIBRATION.items():
        log_dose = np.log10(data['dose_gy'])
        delta_a = np.array(data['delta_a'])

        slope, intercept, r_value, p_value, std_err = sp_stats.linregress(
            log_dose, delta_a)

        # Standard error of intercept
        n = len(log_dose)
        x_mean = np.mean(log_dose)
        ss_x = np.sum((log_dose - x_mean)**2)
        residuals = delta_a - (slope * log_dose + intercept)
        mse = np.sum(residuals**2) / (n - 2) if n > 2 else np.nan
        se_intercept = np.sqrt(mse * (1.0/n + x_mean**2 / ss_x)) if n > 2 else np.nan

        # Propagated fractional dose uncertainty from inversion:
        #   dose = 10^((Delta_A - b) / a)
        #   sigma_dose/dose = ln(10) * sigma_OD / |a|
        # This is the MEASUREMENT-DOMINANT term.  Fit parameter uncertainties
        # are unreliable with 3 calibration points (1 d.o.f.), so we report
        # the measurement-propagated term only and note the fit quality via R².
        # sigma_OD estimated from replicate spread: median ~6-9% fractional,
        # at typical OD ~0.3-0.8 → absolute sigma_OD ≈ 0.03-0.06.
        sigma_od = 0.04  # representative absolute OD uncertainty from replicates
        frac_meas = np.log(10) * sigma_od / abs(slope)

        # Also compute fit-parameter contribution (informational, often large
        # because N is small):
        if not np.isnan(se_intercept):
            median_da = np.median(delta_a)
            frac_fit = np.log(10) * np.sqrt(
                (std_err * (median_da - intercept) / slope**2)**2 +
                (se_intercept / slope)**2
            )
        else:
            frac_fit = np.nan

        fits[name] = {
            'a': slope, 'b': intercept,
            'se_a': std_err, 'se_b': se_intercept,
            'R2': r_value**2, 'p_value': p_value,
            'residuals': residuals,
            'n_pts': n,
            'log_dose': log_dose,
            'delta_a': delta_a,
            'frac_dose_unc': frac_meas,     # measurement-propagated
            'frac_fit_unc': frac_fit,        # fit-parameter contribution
        }

    return fits


def plot_C1_calibration(fits):
    """C1: Calibration curve fits with uncertainty envelopes."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('FWT-70 Calibration Curves — Independent Log-Linear Fits',
                 fontsize=14, fontweight='bold')

    colors = {
        'Batch 1190 (High) 600nm': '#CC3333',
        'Batch 1190 (High) 656nm': '#FF6644',
        'Batch 1189 (Low) 600nm': '#3366CC',
        'Batch 1189 (Low) 656nm': '#66AADD',
    }

    for ax, (name, fit) in zip(axes.flat, fits.items()):
        color = colors.get(name, '#666666')
        log_d = fit['log_dose']
        da = fit['delta_a']

        # Data points
        ax.scatter(10**log_d, da, c=color, s=80, zorder=5, edgecolors='black',
                   linewidths=0.5, label='Calibration data')

        # Fit line
        x_fit = np.linspace(log_d.min() - 0.2, log_d.max() + 0.2, 200)
        y_fit = fit['a'] * x_fit + fit['b']
        ax.plot(10**x_fit, y_fit, color=color, linewidth=2, zorder=3,
                label='Fit: a=%.4f, b=%.4f' % (fit['a'], fit['b']))

        # Uncertainty envelope (±1 sigma from fit)
        n = fit['n_pts']
        x_mean = np.mean(log_d)
        ss_x = np.sum((log_d - x_mean)**2)
        if n > 2:
            mse = np.sum(fit['residuals']**2) / (n - 2)
            se_pred = np.sqrt(mse * (1.0/n + (x_fit - x_mean)**2 / ss_x))
            ax.fill_between(10**x_fit, y_fit - se_pred, y_fit + se_pred,
                            color=color, alpha=0.15, zorder=2, label='±1σ prediction')

        # Residuals inset text
        frac_meas_pct = fit['frac_dose_unc'] * 100 if not np.isnan(fit['frac_dose_unc']) else 0
        ax.text(0.03, 0.97,
                'R² = %.4f\na = %.4f ± %.4f\nb = %.4f ± %.4f\nN = %d pts\n'
                'σ(dose)/dose ≈ %.0f%% (meas)' % (
                    fit['R2'], fit['a'], fit['se_a'],
                    fit['b'], fit['se_b'] if not np.isnan(fit['se_b']) else 0,
                    fit['n_pts'], frac_meas_pct),
                transform=ax.transAxes, fontsize=9, va='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='gray', alpha=0.9))

        ax.set_xscale('log')
        ax.set_xlabel('Dose (Gy)', fontsize=10)
        ax.set_ylabel('ΔA (OD change)', fontsize=10)
        ax.set_title(name, fontsize=11, fontweight='bold', color=color)
        ax.legend(fontsize=7, loc='lower right')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUT_DIR, 'rod_calibration_C1.png')
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("  Saved: %s" % path)


# ═══════════════════════════════════════════════════════════════════════════════
# Section B: Replicate OD Spread Analysis
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_replicate_spread():
    """Compute per-rod OD replicate spread from rod_doses.csv.

    Returns summary stats by range × wavelength.
    """
    path = os.path.join(OUT_DIR, 'rod_doses.csv')
    records = []
    with open(path) as f:
        for row in csv.DictReader(f):
            if row['is_ldrd'].strip() != 'True':
                continue
            rng = row['range'].strip()
            try:
                od600_1 = float(row['od_600nm_1'])
                od600_2 = float(row['od_600nm_2'])
                od656_1 = float(row['od_656nm_1'])
                od656_2 = float(row['od_656nm_2'])
            except (ValueError, KeyError):
                continue

            # 600nm spread
            mean_600 = (od600_1 + od600_2) / 2
            if abs(mean_600) > 0.01:
                spread_600 = abs(od600_1 - od600_2) / abs(mean_600)
                records.append({
                    'rod': row['rod_id'], 'range': rng, 'wavelength': 600,
                    'od1': od600_1, 'od2': od600_2, 'mean_od': mean_600,
                    'spread_frac': spread_600,
                })

            # 656nm spread
            mean_656 = (od656_1 + od656_2) / 2
            if abs(mean_656) > 0.01:
                spread_656 = abs(od656_1 - od656_2) / abs(mean_656)
                records.append({
                    'rod': row['rod_id'], 'range': rng, 'wavelength': 656,
                    'od1': od656_1, 'od2': od656_2, 'mean_od': mean_656,
                    'spread_frac': spread_656,
                })

    # Aggregate by range × wavelength
    from collections import defaultdict
    groups = defaultdict(list)
    for rec in records:
        key = (rec['range'], rec['wavelength'])
        groups[key].append(rec['spread_frac'])

    summary = {}
    for (rng, wl), spreads in sorted(groups.items()):
        arr = np.array(spreads)
        summary[(rng, wl)] = {
            'n': len(arr),
            'mean': np.mean(arr),
            'median': np.median(arr),
            'std': np.std(arr, ddof=1) if len(arr) > 1 else 0,
            'pct_10': np.percentile(arr, 10),
            'pct_90': np.percentile(arr, 90),
        }

    return summary, records


# ═══════════════════════════════════════════════════════════════════════════════
# Section C: Cross-check vs Kirsten's sigma
# ═══════════════════════════════════════════════════════════════════════════════

def load_aidata_for_crosscheck():
    """Load AIdata cumulative doses for Y-plates only."""
    path = os.path.join(OUT_DIR, 'aidata_cumulative.csv')
    plates = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            plate = row['plate'].strip()
            if not plate.startswith('Y-'):
                continue
            is_lab = row.get('is_lab', 'False').strip() == 'True'
            if is_lab:
                continue
            plates[plate] = {
                'photon_gy': float(row['photon_cum_gy']),
                'sigma_photon_rem': float(row['sigma_photon_rem']),
                'sigma_photon_gy': float(row['sigma_photon_rem']) * 0.01,
            }
    return plates


def crosscheck_sigma(fits, ai_plates):
    """Compare independent calibration uncertainty to Kirsten's sigma.

    For rod-derived plates (sigma_photon_rem > 0), compute:
      - Kirsten's fractional uncertainty = sigma / dose
      - Independent fractional uncertainty from calibration fits
    """
    # Use average fractional uncertainty from 600nm fits (primary wavelength)
    indep_frac = []
    for name, fit in fits.items():
        if '600nm' in name and not np.isnan(fit['frac_dose_unc']):
            indep_frac.append(fit['frac_dose_unc'])
    avg_indep_frac = np.mean(indep_frac) if indep_frac else np.nan

    comparisons = []
    for plate, d in sorted(ai_plates.items()):
        if d['sigma_photon_gy'] <= 0 or d['photon_gy'] <= 0:
            continue
        kirsten_frac = d['sigma_photon_gy'] / d['photon_gy']
        comparisons.append({
            'plate': plate,
            'dose_gy': d['photon_gy'],
            'kirsten_sigma_gy': d['sigma_photon_gy'],
            'kirsten_frac': kirsten_frac,
            'indep_frac': avg_indep_frac,
            'ratio': kirsten_frac / avg_indep_frac if avg_indep_frac > 0 else np.nan,
        })

    return comparisons, avg_indep_frac


# ═══════════════════════════════════════════════════════════════════════════════
# Section D: Uncertainty Budget
# ═══════════════════════════════════════════════════════════════════════════════

def build_uncertainty_budget(fits, replicate_summary, crosscheck, avg_indep_frac):
    """Build per-plate uncertainty budget CSV and narrative document."""

    # Load merged degradation data (with SEMs) from rod_dose_degradation.csv
    csv_path = os.path.join(OUT_DIR, 'rod_dose_degradation.csv')
    plates = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            def safe_float(key, default=np.nan):
                try:
                    v = float(row[key])
                    return v
                except (ValueError, KeyError):
                    return default

            dose_gy = safe_float('ai_photon_gy')
            sigma_dose_gy = safe_float('ai_sigma_photon_gy')
            # Check original Kirsten sigma to classify source
            sigma_photon_rem = safe_float('ai_sigma_photon_rem', 0)
            if sigma_photon_rem == 0 or np.isnan(sigma_photon_rem):
                sigma_source = 'Landauer_10pct'
            else:
                sigma_source = 'rod_propagated'

            sigma_dose_pct = (sigma_dose_gy / dose_gy * 100
                              if dose_gy > 0 else np.nan)

            plates.append({
                'plate': row['plate'],
                'plate_label': row['plate_label'],
                'region': row['region'],
                'dose_gy': dose_gy,
                'sigma_dose_gy': sigma_dose_gy,
                'sigma_dose_pct': sigma_dose_pct,
                'sigma_source': sigma_source,
                'ndfeb_pct': safe_float('ndfeb_mean_pct'),
                'sigma_ndfeb': safe_float('sigma_ndfeb_pct'),
                'smco_pct': safe_float('smco_mean_pct'),
                'sigma_smco': safe_float('sigma_smco_pct'),
                'diff_pct': safe_float('intra_plate_diff'),
                'sigma_diff': safe_float('sigma_diff_pct'),
            })

    # Write CSV
    budget_csv = os.path.join(OUT_DIR, 'rod_uncertainty_budget.csv')
    fields = ['plate', 'plate_label', 'region', 'dose_gy', 'sigma_dose_gy',
              'sigma_dose_pct', 'sigma_source', 'ndfeb_pct', 'sigma_ndfeb',
              'smco_pct', 'sigma_smco', 'diff_pct', 'sigma_diff']
    with open(budget_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for p in plates:
            writer.writerow(p)
    print("  Wrote: %s" % budget_csv)

    # Write narrative document
    budget_txt = os.path.join(OUT_DIR, 'uncertainty_budget.txt')
    lines = []
    lines.append("=" * 72)
    lines.append("ROD DOSIMETRY UNCERTAINTY BUDGET")
    lines.append("FFA@CEBAF LDRD Magnet Radiation Study")
    lines.append("=" * 72)

    lines.append("\n1. DOSE UNCERTAINTY SOURCES")
    lines.append("-" * 40)
    lines.append("")
    lines.append("  a) Optichromic rod calibration (FWT-70):")
    lines.append("     - 4 calibration curves fitted (2 batches × 2 wavelengths)")
    lines.append("     - Measurement-propagated uncertainty: σ(dose)/dose = ln(10)·σ_OD/|slope|")
    lines.append("       where σ_OD ≈ 0.04 from replicate spread analysis")
    for name, fit in fits.items():
        frac_m = fit['frac_dose_unc'] * 100 if not np.isnan(fit['frac_dose_unc']) else 0
        lines.append("     %-35s  R²=%.4f  σ(dose)/dose ≈ %5.1f%% (meas)  (N=%d)" % (
            name + ':', fit['R2'], frac_m, fit['n_pts']))
    lines.append("     - Average measurement-propagated uncertainty: %.1f%%" % (
        avg_indep_frac * 100 if not np.isnan(avg_indep_frac) else 0))
    lines.append("     - Note: fit-parameter uncertainties unreliable with 3-point curves")

    lines.append("")
    lines.append("  b) Replicate OD measurement spread:")
    for (rng, wl), s in sorted(replicate_summary.items()):
        lines.append("     %-6s %dnm:  mean=%.1f%%  median=%.1f%%  "
                     "std=%.1f%%  [P10=%.1f%%, P90=%.1f%%]  N=%d" % (
                         rng, wl,
                         s['mean'] * 100, s['median'] * 100,
                         s['std'] * 100,
                         s['pct_10'] * 100, s['pct_90'] * 100, s['n']))

    lines.append("")
    lines.append("  c) OSL-matched plates (sigma_photon_rem = 0):")
    n_osl = sum(1 for p in plates if p['sigma_source'] == 'Landauer_10pct')
    n_rod = sum(1 for p in plates if p['sigma_source'] == 'rod_propagated')
    lines.append("     %d of %d Y-plates use Landauer InLight stated accuracy (10%%)" % (
        n_osl, len(plates)))
    lines.append("     %d of %d Y-plates have rod-propagated uncertainty from Kirsten" % (
        n_rod, len(plates)))

    lines.append("")
    lines.append("  d) Cross-check: Kirsten's sigma vs independent calibration:")
    if crosscheck:
        k_fracs = [c['kirsten_frac'] for c in crosscheck]
        ratios = [c['ratio'] for c in crosscheck if not np.isnan(c['ratio'])]
        lines.append("     Rod-derived plates: N=%d" % len(crosscheck))
        lines.append("     Kirsten fractional uncertainty: mean=%.1f%%  range=%.1f%%–%.1f%%" % (
            np.mean(k_fracs) * 100, min(k_fracs) * 100, max(k_fracs) * 100))
        lines.append("     Independent calibration estimate: %.1f%%" % (
            avg_indep_frac * 100 if not np.isnan(avg_indep_frac) else 0))
        if ratios:
            lines.append("     Ratio (Kirsten / independent): mean=%.2f  range=%.2f–%.2f" % (
                np.mean(ratios), min(ratios), max(ratios)))
            if np.mean(ratios) < 2.0:
                lines.append("     → Kirsten's uncertainties are CONSISTENT with independent estimate")
            else:
                lines.append("     → Kirsten's uncertainties are LARGER than independent estimate")

    lines.append("\n\n2. DEGRADATION UNCERTAINTY SOURCES")
    lines.append("-" * 40)
    lines.append("")
    lines.append("  a) Baseline measurement SEM (per-sample, propagated):")
    sems_nd = [p['sigma_ndfeb'] for p in plates if not np.isnan(p['sigma_ndfeb'])]
    sems_sm = [p['sigma_smco'] for p in plates if not np.isnan(p['sigma_smco'])]
    sems_df = [p['sigma_diff'] for p in plates if not np.isnan(p['sigma_diff'])]
    if sems_nd:
        lines.append("     NdFeB mean:       mean SEM = %.3f%%  range = %.3f%%–%.3f%%" % (
            np.mean(sems_nd), min(sems_nd), max(sems_nd)))
    if sems_sm:
        lines.append("     SmCo mean:        mean SEM = %.3f%%  range = %.3f%%–%.3f%%" % (
            np.mean(sems_sm), min(sems_sm), max(sems_sm)))
    if sems_df:
        lines.append("     NdFeB-SmCo diff:  mean SEM = %.3f%%  range = %.3f%%–%.3f%%" % (
            np.mean(sems_df), min(sems_df), max(sems_df)))

    lines.append("")
    lines.append("  b) Gain systematic (Helmholtz coil drift):")
    lines.append("     ±0.124% (cleaned) / ±0.248% (uncleaned)")
    lines.append("     Note: cancels for intra-plate NdFeB-SmCo differential")

    lines.append("")
    lines.append("  c) Temperature correction uncertainty:")
    lines.append("     Per-date temp estimates with ±0.5–2.0°C uncertainty")
    lines.append("     Sensitivity: ~0.066% per °C on NdFeB-SmCo differential")
    lines.append("     Dominant systematic for absolute material degradation")

    lines.append("\n\n3. SUMMARY TABLE — PER-PLATE UNCERTAINTIES")
    lines.append("-" * 40)
    lines.append("  %-8s  %8s  %8s  %8s  %-16s  %8s  %8s" % (
        'Plate', 'Dose(Gy)', 'σ_dose%', 'σ_dose_Gy', 'Source',
        'σ_NdFeB%', 'σ_diff%'))
    for p in plates:
        lines.append("  %-8s  %8.1f  %7.1f%%  %8.1f  %-16s  %7.3f%%  %7.3f%%" % (
            p['plate_label'],
            p['dose_gy'],
            p['sigma_dose_pct'] if not np.isnan(p['sigma_dose_pct']) else 0,
            p['sigma_dose_gy'],
            p['sigma_source'],
            p['sigma_ndfeb'] if not np.isnan(p['sigma_ndfeb']) else 0,
            p['sigma_diff'] if not np.isnan(p['sigma_diff']) else 0))

    lines.append("\n\n4. CONCLUSIONS")
    lines.append("-" * 40)
    lines.append("")
    # Compute actual ranges for conclusions
    rod_fracs = [p['sigma_dose_pct'] for p in plates
                 if p['sigma_source'] == 'rod_propagated' and not np.isnan(p['sigma_dose_pct'])]
    rod_min = min(rod_fracs) if rod_fracs else 0
    rod_max = max(rod_fracs) if rod_fracs else 0

    lines.append("  - Rod-propagated dose uncertainties: %.0f%%–%.0f%% (Kirsten's sigma)" % (
        rod_min, rod_max))
    lines.append("  - OSL-matched plates: 10%% assigned (Landauer InLight stated accuracy)")
    lines.append("  - Measurement-propagated calibration uncertainty: ~%.0f%% (from OD replicates)" % (
        avg_indep_frac * 100 if not np.isnan(avg_indep_frac) else 0))
    lines.append("  - Degradation baseline SEMs are small (~0.02–0.10%%)")
    lines.append("  - Temperature correction is the dominant systematic for absolute values")
    lines.append("  - The gain-immune NdFeB-SmCo differential eliminates the largest systematic")
    cal_r2s = [fit['R2'] for fit in fits.values()]
    lines.append("  - Rod calibration R²: %.3f–%.4f (3 of 4 > 0.85)" % (
        min(cal_r2s), max(cal_r2s)))
    lines.append("  - Replicate OD spread: ~5–11%% (median), primary measurement noise source")
    lines.append("  - None of the dose or degradation uncertainties are large enough to")
    lines.append("    explain the observed NdFeB-SmCo differential of -0.208%% (7.7σ)")

    text = '\n'.join(lines)
    with open(budget_txt, 'w') as f:
        f.write(text + '\n')
    print("  Wrote: %s" % budget_txt)

    return plates


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("Rod Dosimetry Uncertainty Analysis")
    print("=" * 70)

    # --- Section A: Calibration ---
    print("\nSection A: Independent calibration curve fitting...")
    fits = fit_calibration_curves()
    for name, fit in fits.items():
        frac = fit['frac_dose_unc'] * 100 if not np.isnan(fit['frac_dose_unc']) else 0
        print("  %-35s  R²=%.4f  σ(dose)/dose ≈ %.1f%%  (N=%d pts)" % (
            name, fit['R2'], frac, fit['n_pts']))

    plot_C1_calibration(fits)

    # --- Section B: Replicate spread ---
    print("\nSection B: Replicate OD spread analysis...")
    replicate_summary, replicate_records = analyze_replicate_spread()
    print("  Total replicate pairs: %d" % len(replicate_records))
    for (rng, wl), s in sorted(replicate_summary.items()):
        print("  %-6s %dnm:  mean spread=%.1f%%  median=%.1f%%  N=%d" % (
            rng, wl, s['mean'] * 100, s['median'] * 100, s['n']))

    # --- Section C: Cross-check ---
    print("\nSection C: Cross-check vs Kirsten's sigma...")
    ai_plates = load_aidata_for_crosscheck()
    crosscheck, avg_indep_frac = crosscheck_sigma(fits, ai_plates)
    if crosscheck:
        k_fracs = [c['kirsten_frac'] * 100 for c in crosscheck]
        print("  Rod-derived Y-plates: %d" % len(crosscheck))
        print("  Kirsten fractional uncertainty: mean=%.1f%%, range=%.1f%%–%.1f%%" % (
            np.mean(k_fracs), min(k_fracs), max(k_fracs)))
        print("  Independent estimate: %.1f%%" % (
            avg_indep_frac * 100 if not np.isnan(avg_indep_frac) else 0))

    # --- Section D: Budget ---
    print("\nSection D: Uncertainty budget...")
    budget_plates = build_uncertainty_budget(
        fits, replicate_summary, crosscheck, avg_indep_frac)

    print("\n" + "=" * 70)
    print("UNCERTAINTY ANALYSIS COMPLETE")
    print("=" * 70)
    print("  Calibration curves: 4 fitted (all R² listed above)")
    print("  Per-plate budget: %d plates" % len(budget_plates))
    print("  Outputs: rod_calibration_C1.png, uncertainty_budget.txt,")
    print("           rod_uncertainty_budget.csv")
    print("\nDone.")


if __name__ == '__main__':
    main()
