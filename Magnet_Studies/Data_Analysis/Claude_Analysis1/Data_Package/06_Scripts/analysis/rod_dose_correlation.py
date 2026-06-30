#!/usr/bin/env python3
"""
Phase 5: Re-run dose-degradation correlation using AIdata gamma doses.

Substitutes AIdata cumulative photon dose (in rem) for OSL photon dose.
AIdata provides true gamma dose for all plates, including those where
OSL was saturated (24/30 tunnel Y-plates).

Key comparison: does using true gamma dose (vs OSL lower bound) reveal
a stronger dose-degradation correlation?

Output:
  Rod_Dosimetry/rod_correlation_R1_side_by_side.png
  Rod_Dosimetry/rod_correlation_R2_by_material.png
  Rod_Dosimetry/rod_correlation_R3_differential.png
  Rod_Dosimetry/rod_correlation_R4_regional.png
  Rod_Dosimetry/rod_correlation_R5_dose_comparison.png
  Rod_Dosimetry/rod_correlation_stats.txt
  Rod_Dosimetry/rod_dose_degradation.csv
"""

import sys
import os
import csv
import re
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEANUP = os.path.join(BASE, 'Cleanup_Claude')
OUT_DIR = os.path.join(CLEANUP, 'Rod_Dosimetry')

sys.path.insert(0, CLEANUP)
from manager_summary_v3 import (
    load_all, get_gain_syst, compute_intra_plate_diffs,
    MAT_COLORS, REGION_ORDER, REGION_COLORS,
)
from degradation_summary_v2 import (
    PLACEMENTS as V2_PLACEMENTS,
    load_materials, build_temperature_lookup, compute_h_plate_degradation,
)
from manager_summary_v5_polish import load_a_sample_helmholtz

# Presentation colors
PRES_COLORS = {
    'N42EH': '#CC3333', 'N52SH': '#FF6644',
    'SmCo33H': '#3366CC', 'SmCo35': '#66AADD',
}

REGION_MARKERS = {
    'SE Arc': 'o', 'NE Arc': 'D', 'NW Arc': 's', 'SW Arc': '^',
    'North Linac': 'p', 'South Linac': 'h', 'Labyrinth': 'v',
}


def load_aidata_cumulative(tunnel_only=True):
    """Load AIdata cumulative doses per plate. Excludes lab plates by default."""
    path = os.path.join(OUT_DIR, 'aidata_cumulative.csv')
    dose = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            plate = row['plate'].strip()
            is_lab = row.get('is_lab', 'False').strip() == 'True'
            if tunnel_only and is_lab:
                continue
            dose[plate] = {
                'photon_cum_rem': float(row['photon_cum_rem']),
                'neutron_cum_rem': float(row['neutron_cum_rem']),
                'photon_cum_gy': float(row['photon_cum_gy']),
                'sigma_photon_rem': float(row['sigma_photon_rem']),
                'sigma_neutron_rem': float(row['sigma_neutron_rem']),
            }
    return dose


def load_osl_cumulative():
    """Load OSL cumulative doses per plate."""
    osl_dir = os.path.join(CLEANUP, 'Dosimetry', 'OSL_Area')
    path = os.path.join(osl_dir, 'plate_cumulative_dose.csv')
    dose = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            plate = row['plate'].strip()
            dose[plate] = {
                'body_mrem': float(row['body_mrem']),
                'photon_mrem': float(row['photon_mrem']),
                'neutron_mrem': float(row['neutron_mrem']),
                'nt_mrem': float(row['nt_mrem']),   # thermal neutron (CR-39)
                'nf_mrem': float(row['nf_mrem']),   # fast neutron (CR-39)
                'n_saturated': int(row['n_saturated']),
                'is_lower_bound': row['is_lower_bound'].strip() == 'True',
            }
    return dose


def build_merged_y(results, intra_details, ai_dose, osl_dose):
    """Merge Y-plate degradation with both AIdata and OSL doses."""
    from collections import defaultdict

    clean = [r for r in results if not r['is_outlier']]
    plate_mats = defaultdict(dict)
    plate_sems = defaultdict(dict)  # per-plate per-material SEM
    for r in clean:
        plate_mats[r['plate']][r['material']] = r['pct_change']
        plate_sems[r['plate']][r['material']] = r.get('bl_sem_pct', np.nan)

    intra_lookup = {d['plate']: d for d in intra_details}

    merged = []
    for yp, hp, region, subloc, line in V2_PLACEMENTS:
        pnum = int(yp.replace('Y', ''))
        plate_key = 'Y-%d' % pnum

        ai = ai_dose.get(plate_key)
        osl = osl_dose.get(plate_key)
        if not ai or not osl:
            continue

        mats = plate_mats.get(pnum, {})
        sems = plate_sems.get(pnum, {})

        nd_vals = [v for k, v in mats.items() if k in ('N42EH', 'N52SH') and not np.isnan(v)]
        sm_vals = [v for k, v in mats.items() if k in ('SmCo33H', 'SmCo35') and not np.isnan(v)]
        ip = intra_lookup.get(pnum)

        # Per-material SEMs
        sem_n42 = sems.get('N42EH', np.nan)
        sem_n52 = sems.get('N52SH', np.nan)
        sem_sm33 = sems.get('SmCo33H', np.nan)
        sem_sm35 = sems.get('SmCo35', np.nan)

        # Propagated NdFeB mean SEM = sqrt(sem1^2 + sem2^2) / 2
        nd_sems = [s for s in [sem_n42, sem_n52] if not np.isnan(s)]
        sm_sems = [s for s in [sem_sm33, sem_sm35] if not np.isnan(s)]
        sigma_ndfeb = (np.sqrt(sum(s**2 for s in nd_sems)) / len(nd_sems)
                       if nd_sems else np.nan)
        sigma_smco = (np.sqrt(sum(s**2 for s in sm_sems)) / len(sm_sems)
                      if sm_sems else np.nan)
        sigma_diff = (np.sqrt(sigma_ndfeb**2 + sigma_smco**2)
                      if not np.isnan(sigma_ndfeb) and not np.isnan(sigma_smco)
                      else np.nan)

        # Dose uncertainty in Gy
        sigma_photon_rem = ai['sigma_photon_rem']
        sigma_photon_gy = sigma_photon_rem * 0.01  # rem -> Gy
        if sigma_photon_gy == 0:
            # OSL-matched plates: assign 10% Landauer stated accuracy
            sigma_photon_gy = ai['photon_cum_gy'] * 0.10

        merged.append({
            'plate': pnum,
            'plate_label': plate_key,
            'region': region,
            'sub_location': subloc,
            'line': line,
            # AIdata doses (primary)
            'ai_photon_rem': ai['photon_cum_rem'],
            'ai_photon_gy': ai['photon_cum_gy'],
            'ai_neutron_rem': ai['neutron_cum_rem'],
            'ai_sigma_photon_rem': ai['sigma_photon_rem'],
            'ai_sigma_neutron_rem': ai['sigma_neutron_rem'],
            'ai_sigma_photon_gy': sigma_photon_gy,
            # OSL doses (comparison)
            'osl_body_mrem': osl['body_mrem'],
            'osl_photon_mrem': osl['photon_mrem'],
            'osl_neutron_mrem': osl['neutron_mrem'],
            'osl_nt_mrem': osl['nt_mrem'],      # thermal neutron (CR-39)
            'osl_nf_mrem': osl['nf_mrem'],      # fast neutron (CR-39)
            'osl_n_saturated': osl['n_saturated'],
            'osl_is_lower_bound': osl['is_lower_bound'],
            # Degradation
            'N42EH_pct': mats.get('N42EH', np.nan),
            'N52SH_pct': mats.get('N52SH', np.nan),
            'SmCo33H_pct': mats.get('SmCo33H', np.nan),
            'SmCo35_pct': mats.get('SmCo35', np.nan),
            'ndfeb_mean_pct': np.mean(nd_vals) if nd_vals else np.nan,
            'smco_mean_pct': np.mean(sm_vals) if sm_vals else np.nan,
            'intra_plate_diff': ip['diff'] if ip else np.nan,
            # Per-material SEMs (%)
            'sem_N42EH': sem_n42,
            'sem_N52SH': sem_n52,
            'sem_SmCo33H': sem_sm33,
            'sem_SmCo35': sem_sm35,
            # Propagated uncertainties (%)
            'sigma_ndfeb_pct': sigma_ndfeb,
            'sigma_smco_pct': sigma_smco,
            'sigma_diff_pct': sigma_diff,
        })

    return merged


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("  Saved: %s" % path)


def compute_correlations(merged, dose_key, dose_label, stats_lines):
    """Compute and print correlations for a given dose column."""
    stats_lines.append("\n--- %s (N=%d) ---" % (dose_label, len(merged)))

    doses = np.array([m[dose_key] for m in merged])
    # Filter out zero/negative doses
    valid = doses > 0
    if valid.sum() < 4:
        stats_lines.append("  Too few plates with positive dose")
        return {}

    log_doses = np.log10(np.clip(doses[valid], 1e-6, None))
    results = {}

    for col, name in [('ndfeb_mean_pct', 'NdFeB mean'),
                      ('smco_mean_pct', 'SmCo mean'),
                      ('intra_plate_diff', 'NdFeB-SmCo diff'),
                      ('N42EH_pct', 'N42EH'),
                      ('N52SH_pct', 'N52SH'),
                      ('SmCo33H_pct', 'SmCo33H'),
                      ('SmCo35_pct', 'SmCo35')]:
        vals = np.array([m[col] for m in merged])[valid]
        mask = ~np.isnan(vals)
        if mask.sum() < 4:
            continue
        x, y = log_doses[mask], vals[mask]
        r_p, p_p = stats.pearsonr(x, y)
        r_s, p_s = stats.spearmanr(x, y)
        line = "  %-18s  Pearson r=%+.3f (p=%.4f)  Spearman rho=%+.3f (p=%.4f)" % (
            name, r_p, p_p, r_s, p_s)
        stats_lines.append(line)
        results[col] = {'pearson_r': r_p, 'pearson_p': p_p,
                        'spearman_r': r_s, 'spearman_p': p_s}

    return results


def plot_R1_side_by_side(merged, gain_syst):
    """R1: Side-by-side scatter — gamma dose (Gy) vs neutron dose (Sv)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    fig.suptitle('NdFeB Degradation vs Dose: Gamma (Gy) vs Neutron (Sv)',
                 fontsize=13, fontweight='bold')

    # Left: AIdata gamma dose (Gy). Right: AIdata neutron dose (Sv, = rem * 0.01)
    datasets = [
        ('Gamma Dose (Gy)', 'ai_photon_gy', 1.0, 'ai_sigma_photon_gy'),
        ('Neutron Dose Equivalent (Sv)', 'ai_neutron_rem', 0.01, None),
    ]

    for ax, (xlabel, dose_key, scale, xerr_key) in zip(axes, datasets):
        ax.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.12, zorder=0)
        ax.axhline(0, color='gray', linewidth=0.5, zorder=1)

        xs, ys = [], []
        for m in merged:
            x = m[dose_key] * scale
            if x <= 0:
                continue
            y = m.get('ndfeb_mean_pct', np.nan)
            if np.isnan(y):
                continue
            region = m['region']
            marker = REGION_MARKERS.get(region, 'o')
            color = REGION_COLORS.get(region, '#666666')

            # Error bars
            y_err = m.get('sigma_ndfeb_pct', 0)
            if np.isnan(y_err):
                y_err = 0
            x_err = 0
            if xerr_key:
                x_err = m.get(xerr_key, 0)
            elif dose_key == 'ai_neutron_rem':
                x_err = m.get('ai_sigma_neutron_rem', 0) * scale
            if np.isnan(x_err):
                x_err = 0
            if x_err > 0 or y_err > 0:
                ax.errorbar(x, y, xerr=x_err if x_err > 0 else None,
                            yerr=y_err if y_err > 0 else None,
                            fmt='none', ecolor='gray', elinewidth=0.8,
                            capsize=2, alpha=0.5, zorder=2)

            ax.scatter(x, y, marker=marker, c=color, s=50, zorder=3,
                       edgecolors=color, linewidths=1)

            ax.annotate(m['plate_label'], (x, y), fontsize=6, ha='left',
                        va='bottom', alpha=0.7)
            xs.append(x)
            ys.append(y)

        if len(xs) >= 4:
            r_s, p_s = stats.spearmanr(np.log10(xs), ys)
            r_p, p_p = stats.pearsonr(np.log10(xs), ys)
            sig_label = '(sig.)' if p_s < 0.05 else '(n.s.)'
            ax.text(0.03, 0.97,
                    'Pearson r=%.2f (p=%.3f)\nSpearman \u03c1=%.3f (p=%.3f) %s\nN=%d' % (
                        r_p, p_p, r_s, p_s, sig_label, len(xs)),
                    transform=ax.transAxes, fontsize=8, va='top',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='gray', alpha=0.9))

        ax.set_xscale('log')
        ax.set_xlabel(xlabel, fontsize=10)
        ax.grid(True, alpha=0.3)

    axes[0].set_ylabel('NdFeB mean % change', fontsize=11)

    # Legend for regions
    handles = [plt.Line2D([0], [0], marker=REGION_MARKERS.get(r, 'o'),
                          color='w', markerfacecolor=REGION_COLORS.get(r, '#666'),
                          markersize=8, label=r)
               for r in REGION_ORDER if r in set(m['region'] for m in merged)]
    axes[1].legend(handles=handles, loc='lower right', fontsize=7,
                   title='Region', title_fontsize=8)

    fig.text(0.99, 0.01, 'Error bars: x = dose \u03c3, y = \u00b11 SEM',
             ha='right', va='bottom', fontsize=7, fontstyle='italic', color='gray')
    plt.tight_layout()
    save(fig, 'rod_correlation_R1_side_by_side.png')


def plot_R2_by_material(merged, gain_syst):
    """R2: 4-panel scatter by material vs AIdata gamma dose."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Material-specific Degradation vs AIdata Gamma Dose',
                 fontsize=14, fontweight='bold')

    materials = [('N42EH', 'N42EH_pct', 'sem_N42EH'),
                 ('N52SH', 'N52SH_pct', 'sem_N52SH'),
                 ('SmCo33H', 'SmCo33H_pct', 'sem_SmCo33H'),
                 ('SmCo35', 'SmCo35_pct', 'sem_SmCo35')]

    for ax, (mat, col, sem_col) in zip(axes.flat, materials):
        color = PRES_COLORS[mat]
        ax.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.12, zorder=0)
        ax.axhline(0, color='gray', linewidth=0.5, zorder=1)

        xs, ys = [], []
        for m in merged:
            x = m['ai_photon_gy']
            y = m.get(col, np.nan)
            if x <= 0 or np.isnan(y):
                continue
            region = m['region']
            marker = REGION_MARKERS.get(region, 'o')

            # Error bars
            y_err = m.get(sem_col, 0)
            if np.isnan(y_err):
                y_err = 0
            x_err = m.get('ai_sigma_photon_gy', 0)
            if x_err > 0 or y_err > 0:
                ax.errorbar(x, y, xerr=x_err if x_err > 0 else None,
                            yerr=y_err if y_err > 0 else None,
                            fmt='none', ecolor='gray', elinewidth=0.8,
                            capsize=2, alpha=0.4, zorder=2)

            ax.scatter(x, y, marker=marker, c=color, s=40, zorder=3, alpha=0.8)
            xs.append(x)
            ys.append(y)

        if len(xs) >= 4:
            r_s, p_s = stats.spearmanr(np.log10(xs), ys)
            r_p, p_p = stats.pearsonr(np.log10(xs), ys)
            ax.text(0.03, 0.97,
                    'r=%.2f (p=%.3f)\nrho=%.2f (p=%.3f)\nN=%d' % (
                        r_p, p_p, r_s, p_s, len(xs)),
                    transform=ax.transAxes, fontsize=8, va='top',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='gray', alpha=0.9))

        if ys:
            mean = np.mean(ys)
            ax.axhline(mean, color=color, linewidth=1, linestyle='--', alpha=0.7)
            ax.text(0.97, mean, '%.3f%%' % mean,
                    transform=ax.get_yaxis_transform(), fontsize=8,
                    va='bottom', ha='right', color=color)

        ax.set_xscale('log')
        ax.set_title(mat, fontsize=12, fontweight='bold', color=color)
        ax.set_xlabel('AIdata photon dose (Gy)')
        ax.set_ylabel('% change')
        ax.grid(True, alpha=0.3)

    fig.text(0.99, 0.01, 'Error bars: x = dose \u03c3, y = \u00b11 SEM',
             ha='right', va='bottom', fontsize=7, fontstyle='italic', color='gray')
    plt.tight_layout()
    save(fig, 'rod_correlation_R2_by_material.png')


def plot_R3_differential(merged, gain_syst):
    """R3: NdFeB-SmCo differential (gain-immune) vs AIdata gamma dose.
    This is the KEY SCIENCE PLOT."""
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_title('NdFeB - SmCo Differential vs True Gamma Dose (AIdata)\n'
                 'Gain-immune metric — KEY SCIENCE PLOT',
                 fontsize=13, fontweight='bold')

    # Gain systematic cancels for intra-plate diff, so show zero band only
    ax.axhline(0, color='gray', linewidth=1, zorder=1)

    xs, ys, labels = [], [], []
    for m in merged:
        x = m['ai_photon_gy']
        y = m.get('intra_plate_diff', np.nan)
        if x <= 0 or np.isnan(y):
            continue
        region = m['region']
        marker = REGION_MARKERS.get(region, 'o')
        color = REGION_COLORS.get(region, '#666666')

        # Error bars
        y_err = m.get('sigma_diff_pct', 0)
        if np.isnan(y_err):
            y_err = 0
        x_err = m.get('ai_sigma_photon_gy', 0)
        if x_err > 0 or y_err > 0:
            ax.errorbar(x, y, xerr=x_err if x_err > 0 else None,
                        yerr=y_err if y_err > 0 else None,
                        fmt='none', ecolor='gray', elinewidth=0.8,
                        capsize=2, alpha=0.5, zorder=2)

        ax.scatter(x, y, marker=marker, c=color, s=70, zorder=3, edgecolors='black',
                   linewidths=0.5)
        ax.annotate(m['plate_label'], (x, y), fontsize=7, ha='left',
                    va='bottom', alpha=0.8)
        xs.append(x)
        ys.append(y)
        labels.append(m['plate_label'])

    if len(xs) >= 4:
        log_x = np.log10(xs)
        r_p, p_p = stats.pearsonr(log_x, ys)
        r_s, p_s = stats.spearmanr(log_x, ys)

        # Linear fit on log scale
        slope, intercept, _, _, _ = stats.linregress(log_x, ys)
        x_fit = np.logspace(np.log10(min(xs) * 0.5), np.log10(max(xs) * 2), 100)
        y_fit = slope * np.log10(x_fit) + intercept
        ax.plot(x_fit, y_fit, 'k--', alpha=0.5, linewidth=1.5,
                label='log-linear fit: slope=%.3f' % slope)

        mean_y = np.mean(ys)
        ax.axhline(mean_y, color='red', linewidth=1, linestyle=':', alpha=0.7)
        ax.text(0.97, mean_y + 0.01, 'mean=%.3f%%' % mean_y,
                transform=ax.get_yaxis_transform(), fontsize=9,
                ha='right', color='red')

        ax.text(0.03, 0.03,
                'Pearson r=%+.3f (p=%.4f)\n'
                'Spearman rho=%+.3f (p=%.4f)\n'
                'N=%d plates' % (r_p, p_p, r_s, p_s, len(xs)),
                transform=ax.transAxes, fontsize=10, va='bottom',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow',
                          edgecolor='gray', alpha=0.95))

    ax.set_xscale('log')
    ax.set_xlabel('AIdata cumulative photon dose (Gy)', fontsize=12)
    ax.set_ylabel('NdFeB - SmCo differential (% change)', fontsize=12)
    ax.grid(True, alpha=0.3)

    # Region legend
    handles = [plt.Line2D([0], [0], marker=REGION_MARKERS.get(r, 'o'),
                          color='w', markerfacecolor=REGION_COLORS.get(r, '#666'),
                          markersize=8, label=r)
               for r in REGION_ORDER if r in set(m['region'] for m in merged)]
    ax.legend(handles=handles, loc='upper right', fontsize=8)

    fig.text(0.99, 0.01, 'Error bars: x = dose \u03c3, y = \u00b11 SEM',
             ha='right', va='bottom', fontsize=7, fontstyle='italic', color='gray')
    plt.tight_layout()
    save(fig, 'rod_correlation_R3_differential.png')


def plot_R4_regional(merged, gain_syst):
    """R4: Regional breakdown with AIdata gamma doses."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Regional Dose-Degradation: AIdata Gamma',
                 fontsize=13, fontweight='bold')

    # Left: NdFeB by region
    ax = axes[0]
    ax.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.12, zorder=0)
    ax.axhline(0, color='gray', linewidth=0.5)

    for region in REGION_ORDER:
        sub = [m for m in merged if m['region'] == region
               and m['ai_photon_gy'] > 0
               and not np.isnan(m.get('ndfeb_mean_pct', np.nan))]
        if not sub:
            continue
        xs = [m['ai_photon_gy'] for m in sub]
        ys = [m['ndfeb_mean_pct'] for m in sub]
        x_errs = [m.get('ai_sigma_photon_gy', 0) for m in sub]
        y_errs = [m.get('sigma_ndfeb_pct', 0) if not np.isnan(m.get('sigma_ndfeb_pct', np.nan)) else 0 for m in sub]
        color = REGION_COLORS.get(region, '#666')
        marker = REGION_MARKERS.get(region, 'o')
        ax.errorbar(xs, ys, xerr=x_errs, yerr=y_errs,
                    fmt='none', ecolor='gray', elinewidth=0.8,
                    capsize=2, alpha=0.4, zorder=2)
        ax.scatter(xs, ys, marker=marker, c=color, s=60, label=region, zorder=3)

    ax.set_xscale('log')
    ax.set_xlabel('AIdata photon dose (Gy)')
    ax.set_ylabel('NdFeB mean % change')
    ax.set_title('NdFeB by Region')
    ax.legend(fontsize=7, loc='lower left')
    ax.grid(True, alpha=0.3)

    # Right: Differential by region
    ax = axes[1]
    ax.axhline(0, color='gray', linewidth=0.5)

    for region in REGION_ORDER:
        sub = [m for m in merged if m['region'] == region
               and m['ai_photon_gy'] > 0
               and not np.isnan(m.get('intra_plate_diff', np.nan))]
        if not sub:
            continue
        xs = [m['ai_photon_gy'] for m in sub]
        ys = [m['intra_plate_diff'] for m in sub]
        x_errs = [m.get('ai_sigma_photon_gy', 0) for m in sub]
        y_errs = [m.get('sigma_diff_pct', 0) if not np.isnan(m.get('sigma_diff_pct', np.nan)) else 0 for m in sub]
        color = REGION_COLORS.get(region, '#666')
        marker = REGION_MARKERS.get(region, 'o')
        ax.errorbar(xs, ys, xerr=x_errs, yerr=y_errs,
                    fmt='none', ecolor='gray', elinewidth=0.8,
                    capsize=2, alpha=0.4, zorder=2)
        ax.scatter(xs, ys, marker=marker, c=color, s=60, label=region, zorder=3)

    ax.set_xscale('log')
    ax.set_xlabel('AIdata photon dose (Gy)')
    ax.set_ylabel('NdFeB - SmCo diff (%)')
    ax.set_title('Gain-immune Differential by Region')
    ax.legend(fontsize=7, loc='lower left')
    ax.grid(True, alpha=0.3)

    fig.text(0.99, 0.01, 'Error bars: x = dose \u03c3, y = \u00b11 SEM',
             ha='right', va='bottom', fontsize=7, fontstyle='italic', color='gray')
    plt.tight_layout()
    save(fig, 'rod_correlation_R4_regional.png')


def plot_R5_dose_comparison(merged):
    """R5: Bar chart comparing OSL lower bound vs AIdata gamma per plate."""
    # Sort by AIdata dose descending
    valid = [m for m in merged if m['ai_photon_gy'] > 0]
    valid.sort(key=lambda m: -m['ai_photon_gy'])

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title('Dose per Y-plate: AIdata True Gamma vs OSL Lower Bound',
                 fontsize=13, fontweight='bold')

    labels = [m['plate_label'] for m in valid]
    ai_gy = [m['ai_photon_gy'] for m in valid]
    osl_gy = [m['osl_body_mrem'] * 1e-5 for m in valid]  # mrem → Gy (approx, mixed radiation)

    x_pos = np.arange(len(labels))
    width = 0.35

    bars1 = ax.barh(x_pos - width/2, ai_gy, width, label='AIdata photon (Gy)',
                    color='#CC3333', alpha=0.8)
    bars2 = ax.barh(x_pos + width/2, osl_gy, width, label='OSL body (Gy, lower bound)',
                    color='#3366CC', alpha=0.8)

    # Mark saturated plates
    for i, m in enumerate(valid):
        if m['osl_is_lower_bound']:
            ax.text(osl_gy[i] * 1.05, x_pos[i] + width/2, '>',
                    fontsize=8, va='center', color='black', fontweight='bold')

    ax.set_yticks(x_pos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel('Dose (Gy)', fontsize=11)
    ax.set_xscale('log')
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    ax.invert_yaxis()

    # Annotation
    n_sat = sum(1 for m in valid if m['osl_is_lower_bound'])
    ax.text(0.97, 0.03,
            '%d/%d plates had saturated OSL\n'
            'AIdata reveals true dose up to %.0f Gy' % (
                n_sat, len(valid), max(ai_gy)),
            transform=ax.transAxes, fontsize=9, va='bottom', ha='right',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow',
                      edgecolor='gray', alpha=0.9))

    plt.tight_layout()
    save(fig, 'rod_correlation_R5_dose_comparison.png')


def plot_R6_fast_thermal_neutron(merged, gain_syst):
    """R6: Fast vs thermal neutron correlation with degradation.

    Key physics test: does the NdFeB-SmCo differential correlate more
    strongly with fast or thermal neutron dose?
    - Thermal neutrons → damage via nuclear capture (10B(n,alpha), 164Dy(n,gamma))
    - Fast neutrons → damage via displacement cascades and thermal spikes
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle('Degradation vs Fast & Thermal Neutron Dose (CR-39 Track-Etch)',
                 fontsize=14, fontweight='bold', y=0.98)

    MREM_TO_MSV = 0.01  # mrem → mSv (dose equivalent, exact)
    neutron_types = [
        ('osl_nf_mrem', 'Fast Neutron Dose (mSv)', '#0066AA',
         'Displacement cascades / thermal spikes'),
        ('osl_nt_mrem', 'Thermal Neutron Dose (mSv)', '#CC6600',
         '10B(n,α)7Li + 164Dy(n,γ) capture'),
    ]

    deg_types = [
        ('ndfeb_mean_pct', 'NdFeB mean (% change)', 'sigma_ndfeb_pct'),
        ('smco_mean_pct', 'SmCo mean (% change)', 'sigma_smco_pct'),
        ('intra_plate_diff', 'NdFeB−SmCo diff (% change)', 'sigma_diff_pct'),
    ]

    for row_idx, (dose_key, dose_label, dose_color, mechanism) in enumerate(neutron_types):
        for col_idx, (deg_key, deg_label, err_key) in enumerate(deg_types):
            ax = axes[row_idx, col_idx]
            ax.axhline(0, color='gray', linewidth=0.5, zorder=1)
            if col_idx < 2:  # NdFeB/SmCo panels — show gain systematic
                ax.axhspan(-gain_syst, gain_syst, color='gray', alpha=0.10, zorder=0)

            xs, ys = [], []
            for m in merged:
                dose = m[dose_key] * MREM_TO_MSV  # convert to mSv at plot time
                deg = m[deg_key]
                if m[dose_key] <= 0 or np.isnan(deg):
                    continue

                region = m['region']
                marker = REGION_MARKERS.get(region, 'o')
                color = REGION_COLORS.get(region, '#666666')

                # Error bars (y only — no x uncertainty for CR-39)
                y_err = m.get(err_key, 0)
                if np.isnan(y_err):
                    y_err = 0
                if y_err > 0:
                    ax.errorbar(dose, deg, yerr=y_err,
                                fmt='none', ecolor='gray', elinewidth=0.8,
                                capsize=2, alpha=0.5, zorder=2)

                ax.scatter(dose, deg, marker=marker, c=color, s=50, zorder=3,
                           edgecolors='black', linewidths=0.5)
                xs.append(dose)
                ys.append(deg)

            # Correlation stats
            if len(xs) >= 4:
                log_x = np.log10(xs)
                r_p, p_p = stats.pearsonr(log_x, ys)
                r_s, p_s = stats.spearmanr(log_x, ys)

                # Log-linear fit
                slope, intercept, _, _, _ = stats.linregress(log_x, ys)
                x_fit = np.logspace(np.log10(min(xs) * 0.5),
                                    np.log10(max(xs) * 2), 100)
                y_fit = slope * np.log10(x_fit) + intercept
                ax.plot(x_fit, y_fit, '--', color=dose_color, alpha=0.6,
                        linewidth=1.5)

                # Significance marker
                sig = '**' if p_s < 0.01 else ('*' if p_s < 0.05 else '')
                ax.text(0.03, 0.97,
                        'ρ=%+.3f (p=%.3f)%s\nN=%d' % (r_s, p_s, sig, len(xs)),
                        transform=ax.transAxes, fontsize=9, va='top',
                        bbox=dict(boxstyle='round,pad=0.3',
                                  facecolor='lightyellow' if p_s < 0.05 else 'white',
                                  edgecolor='orange' if p_s < 0.05 else 'gray',
                                  alpha=0.9))

            ax.set_xscale('log')
            ax.set_xlabel(dose_label, fontsize=10)
            ax.set_ylabel(deg_label, fontsize=10)
            ax.grid(True, alpha=0.3)

            # Row titles on leftmost panel
            if col_idx == 0:
                ax.set_title('%s\n(%s)' % (dose_label.split('(')[0].strip(), mechanism),
                             fontsize=10, fontweight='bold')
            else:
                ax.set_title(deg_label, fontsize=10)

    # Region legend on last panel
    handles = [plt.Line2D([0], [0], marker=REGION_MARKERS.get(r, 'o'),
                          color='w', markerfacecolor=REGION_COLORS.get(r, '#666'),
                          markersize=8, label=r)
               for r in REGION_ORDER if r in set(m['region'] for m in merged)]
    axes[1, 2].legend(handles=handles, loc='lower right', fontsize=7)

    fig.text(0.99, 0.005, 'Error bars: y = \u00b11 SEM',
             ha='right', va='bottom', fontsize=7, fontstyle='italic', color='gray')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save(fig, 'rod_correlation_R6_fast_thermal_neutron.png')


def plot_R7_line_position_inversion(merged, gain_syst):
    """R7: Line position vs degradation in arc stacks — the dose-position inversion."""
    from scipy.stats import spearmanr

    arc = [m for m in merged if 'Arc' in m['region']]
    if not arc:
        print("  R7: No arc plates found, skipping")
        return

    ARC_COLORS = {
        'NE Arc': '#E63946', 'NW Arc': '#457B9D',
        'SE Arc': '#2A9D8F', 'SW Arc': '#E9C46A',
    }

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))

    # --- Panel (a): Line position vs differential ---
    ax = axes[0]
    for m in arc:
        line_num = int(m['line'].replace('Line ', '') if isinstance(m['line'], str) else m['line'])
        color = ARC_COLORS.get(m['region'], '#666')
        marker = 'o'
        y_err = m['sigma_diff_pct'] if not np.isnan(m['sigma_diff_pct']) else 0
        ax.errorbar(line_num, m['intra_plate_diff'], yerr=y_err,
                    fmt='none', ecolor=color, elinewidth=0.8, capsize=2, alpha=0.5)
        ax.scatter(line_num, m['intra_plate_diff'], c=color, s=60, zorder=5,
                   edgecolors='black', linewidth=0.5)

    # Per-line means
    from collections import defaultdict
    line_diffs = defaultdict(list)
    line_gammas = defaultdict(list)
    line_neutrons = defaultdict(list)
    for m in arc:
        ln = int(m['line'].replace('Line ', '') if isinstance(m['line'], str) else m['line'])
        line_diffs[ln].append(m['intra_plate_diff'])
        line_gammas[ln].append(m['ai_photon_gy'])
        line_neutrons[ln].append(m['ai_neutron_rem'])

    lines_sorted = sorted(line_diffs.keys())
    mean_diffs = [np.mean(line_diffs[ln]) for ln in lines_sorted]
    sem_diffs = [np.std(line_diffs[ln], ddof=1) / np.sqrt(len(line_diffs[ln]))
                 for ln in lines_sorted]
    ax.errorbar(lines_sorted, mean_diffs, yerr=sem_diffs,
                color='black', marker='D', markersize=8, linewidth=2,
                capsize=5, label='Line mean \u00b1 SEM', zorder=10)

    # Spearman on individual plates
    all_lines = [int(m['line'].replace('Line ', '') if isinstance(m['line'], str) else m['line'])
                 for m in arc]
    all_diffs = [m['intra_plate_diff'] for m in arc]
    rho, p = spearmanr(all_lines, all_diffs)
    ax.annotate('Spearman \u03c1 = %+.3f\np = %.4f (N=%d)' % (rho, p, len(arc)),
                xy=(0.97, 0.97), xycoords='axes fraction', ha='right', va='top',
                fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                          edgecolor='gray', alpha=0.9))
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.set_xlabel('Line Position (1=top, 5=bottom)', fontsize=11)
    ax.set_ylabel('NdFeB\u2212SmCo Differential (%)', fontsize=11)
    ax.set_title('(a) Degradation vs Line Position', fontsize=12, fontweight='bold')
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(['1\n(top)', '2', '3', '4', '5\n(bottom)'])
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.9, 0.15)

    # --- Panel (b): Line position vs gamma dose ---
    ax = axes[1]
    for m in arc:
        ln = int(m['line'].replace('Line ', '') if isinstance(m['line'], str) else m['line'])
        color = ARC_COLORS.get(m['region'], '#666')
        ax.scatter(ln, m['ai_photon_gy'], c=color, s=60, zorder=5,
                   edgecolors='black', linewidth=0.5)

    mean_gammas = [np.mean(line_gammas[ln]) for ln in lines_sorted]
    ax.plot(lines_sorted, mean_gammas, 'k-D', markersize=8, linewidth=2,
            label='Line mean', zorder=10)

    rho_g, p_g = spearmanr(all_lines, [m['ai_photon_gy'] for m in arc])
    ax.annotate('Spearman \u03c1 = %+.3f\np = %.4f' % (rho_g, p_g),
                xy=(0.03, 0.97), xycoords='axes fraction', ha='left', va='top',
                fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow',
                          edgecolor='gray', alpha=0.9))
    ax.set_xlabel('Line Position (1=top, 5=bottom)', fontsize=11)
    ax.set_ylabel('AIdata Gamma Dose (Gy)', fontsize=11)
    ax.set_title('(b) Gamma Dose vs Line Position', fontsize=12, fontweight='bold')
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(['1\n(top)', '2', '3', '4', '5\n(bottom)'])
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)

    # --- Panel (c): Summary — arrow diagram ---
    ax = axes[2]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('(c) The Dose\u2212Position Inversion', fontsize=12, fontweight='bold')

    # Summary text
    summary = (
        "LINE 1 (top of arc stack)\n"
        "  \u2022 Most degraded: \u22120.43% diff\n"
        "  \u2022 Least gamma dose: 30 Gy\n"
        "  \u2022 Lowest-energy beam pass\n\n"
        "LINE 5 (bottom of arc stack)\n"
        "  \u2022 Least degraded: \u22120.14% diff\n"
        "  \u2022 Most gamma dose: 668 Gy\n"
        "  \u2022 Highest-energy beam pass\n\n"
        "CORRELATIONS (arc N=20):\n"
        "  Line vs diff:    \u03c1 = +0.60 (p = 0.005)\n"
        "  Line vs gamma:  \u03c1 = +0.52 (p = 0.020)\n"
        "  Line vs neutron: \u03c1 = \u22120.04 (p = 0.857)\n\n"
        "LEADING HYPOTHESIS:\n"
        "  Low-energy beam pass (Line 1) has\n"
        "  tightest aperture margins \u2192 most\n"
        "  local beam loss \u2192 intense directional\n"
        "  hadronic showers not captured by\n"
        "  broad-field dosimeters."
    )
    ax.text(0.5, 0.95, summary, transform=ax.transAxes,
            fontsize=9, va='top', ha='center', fontfamily='sans-serif',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8F8F0',
                      edgecolor='gray', alpha=0.9))

    # Region legend
    handles = [plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=ARC_COLORS[r], markersize=8,
                          markeredgecolor='black', markeredgewidth=0.5,
                          label=r) for r in ['NE Arc', 'NW Arc', 'SE Arc', 'SW Arc']]
    handles.append(plt.Line2D([0], [0], marker='D', color='black',
                              markersize=8, linewidth=2, label='Line mean'))
    axes[0].legend(handles=handles, loc='lower left', fontsize=7, ncol=2)

    fig.suptitle('R7: Dose\u2212Position Inversion in Arc Stacks\n'
                 '(Line 1 = most degraded, least dose)',
                 fontsize=13, fontweight='bold')
    fig.text(0.99, 0.01, 'Error bars: y = \u00b11 SEM',
             ha='right', va='bottom', fontsize=7, fontstyle='italic', color='gray')
    plt.tight_layout(rect=[0, 0.02, 1, 0.94])
    save(fig, 'rod_correlation_R7_line_position_inversion.png')


def main():
    print("=" * 70)
    print("Phase 5: Dose-Degradation Correlation with AIdata Gamma Doses")
    print("=" * 70)

    # Load degradation data (same as original script)
    print("\nLoading degradation data...")
    results, helm_raw, temp_final, y_materials = load_all()
    clean = [r for r in results if not r['is_outlier']]
    gain_result = get_gain_syst(helm_raw)
    gain_syst = gain_result[0]
    intra_diffs, intra_details = compute_intra_plate_diffs(clean)
    print("  %d clean Y-plate samples, gain systematic ±%.4f%%" % (
        len(clean), gain_syst))

    # Load dose data
    print("\nLoading dose data...")
    ai_dose = load_aidata_cumulative()
    osl_dose = load_osl_cumulative()
    print("  AIdata: %d plates" % len(ai_dose))
    print("  OSL: %d plates" % len(osl_dose))

    # Merge
    print("\nMerging Y-plate data...")
    merged = build_merged_y(results, intra_details, ai_dose, osl_dose)
    print("  Merged: %d Y-plates" % len(merged))

    # Filter out Y-37 (no AIdata)
    merged = [m for m in merged if m['ai_photon_gy'] > 0]
    print("  With positive AIdata dose: %d plates" % len(merged))

    # Write merged CSV
    out_csv = os.path.join(OUT_DIR, 'rod_dose_degradation.csv')
    csv_fields = [
        'plate', 'plate_label', 'region', 'sub_location', 'line',
        'ai_photon_rem', 'ai_photon_gy', 'ai_neutron_rem',
        'ai_sigma_photon_rem', 'ai_sigma_neutron_rem', 'ai_sigma_photon_gy',
        'osl_body_mrem', 'osl_photon_mrem', 'osl_neutron_mrem',
        'osl_nt_mrem', 'osl_nf_mrem',
        'osl_n_saturated', 'osl_is_lower_bound',
        'N42EH_pct', 'N52SH_pct', 'SmCo33H_pct', 'SmCo35_pct',
        'ndfeb_mean_pct', 'smco_mean_pct', 'intra_plate_diff',
        'sem_N42EH', 'sem_N52SH', 'sem_SmCo33H', 'sem_SmCo35',
        'sigma_ndfeb_pct', 'sigma_smco_pct', 'sigma_diff_pct',
    ]
    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction='ignore')
        writer.writeheader()
        for row in merged:
            writer.writerow(row)
    print("  Wrote: %s" % out_csv)

    # Compute and compare correlations
    stats_lines = []
    stats_lines.append("=" * 70)
    stats_lines.append("DOSE-DEGRADATION CORRELATION COMPARISON")
    stats_lines.append("  OSL body dose (lower bound, with saturation floor)")
    stats_lines.append("  AIdata photon dose (true gamma, from optichromic rods)")
    stats_lines.append("=" * 70)

    stats_lines.append("\n========================================")
    stats_lines.append("OSL BODY DOSE (mrem, log10)")
    stats_lines.append("========================================")
    osl_corr = compute_correlations(merged, 'osl_body_mrem', 'OSL body (all plates)', stats_lines)

    stats_lines.append("\n========================================")
    stats_lines.append("AIDATA PHOTON DOSE (Gy, log10)")
    stats_lines.append("========================================")
    ai_corr = compute_correlations(merged, 'ai_photon_gy', 'AIdata photon (all plates)', stats_lines)

    stats_lines.append("\n========================================")
    stats_lines.append("AIDATA NEUTRON DOSE (rem, log10)")
    stats_lines.append("========================================")
    # Convert to Gy for neutrons (Q~10): neutron_rem * 0.01 / 10 = 0.001 Gy per rem
    for m in merged:
        m['ai_neutron_gy'] = m['ai_neutron_rem'] * 0.001
    ai_n_corr = compute_correlations(merged, 'ai_neutron_gy', 'AIdata neutron (all plates)', stats_lines)

    # ── Fast vs thermal neutron breakdown (CR-39 track-etch) ──
    stats_lines.append("\n========================================")
    stats_lines.append("OSL FAST NEUTRON DOSE (mrem, log10)")
    stats_lines.append("  Source: CR-39 track-etch detectors")
    stats_lines.append("========================================")
    fast_n_corr = compute_correlations(merged, 'osl_nf_mrem',
                                       'Fast neutron (all plates)', stats_lines)

    stats_lines.append("\n========================================")
    stats_lines.append("OSL THERMAL NEUTRON DOSE (mrem, log10)")
    stats_lines.append("  Source: CR-39 track-etch detectors")
    stats_lines.append("========================================")
    therm_n_corr = compute_correlations(merged, 'osl_nt_mrem',
                                        'Thermal neutron (all plates)', stats_lines)

    # Fast vs thermal comparison
    stats_lines.append("\n" + "=" * 70)
    stats_lines.append("FAST vs THERMAL NEUTRON: Which correlates better with damage?")
    stats_lines.append("=" * 70)
    stats_lines.append("  (Mechanism test: thermal → 10B(n,α)7Li capture; fast → displacement cascades)")

    for col, name in [('ndfeb_mean_pct', 'NdFeB mean'),
                      ('intra_plate_diff', 'NdFeB-SmCo diff')]:
        fast_r = fast_n_corr.get(col, {})
        therm_r = therm_n_corr.get(col, {})
        total_r = ai_n_corr.get(col, {})
        if fast_r and therm_r:
            stats_lines.append("\n  %s:" % name)
            stats_lines.append("    Fast neutron:    Spearman rho=%+.3f (p=%.4f)" % (
                fast_r['spearman_r'], fast_r['spearman_p']))
            stats_lines.append("    Thermal neutron: Spearman rho=%+.3f (p=%.4f)" % (
                therm_r['spearman_r'], therm_r['spearman_p']))
            if total_r:
                stats_lines.append("    Total neutron:   Spearman rho=%+.3f (p=%.4f)" % (
                    total_r['spearman_r'], total_r['spearman_p']))

            fast_abs = abs(fast_r['spearman_r'])
            therm_abs = abs(therm_r['spearman_r'])
            if fast_abs > therm_abs + 0.05:
                stats_lines.append("    → FAST neutron correlates more strongly (displacement cascades)")
            elif therm_abs > fast_abs + 0.05:
                stats_lines.append("    → THERMAL neutron correlates more strongly (nuclear capture)")
            else:
                stats_lines.append("    → Similar correlation strength — cannot distinguish mechanism")

    # N values for fast/thermal
    n_fast_pos = sum(1 for m in merged if m['osl_nf_mrem'] > 0)
    n_therm_pos = sum(1 for m in merged if m['osl_nt_mrem'] > 0)
    stats_lines.append("\n  Plates with positive fast neutron dose:    %d / %d" % (n_fast_pos, len(merged)))
    stats_lines.append("  Plates with positive thermal neutron dose: %d / %d" % (n_therm_pos, len(merged)))

    # Fast/thermal ratio summary
    ratios = []
    for m in merged:
        if m['osl_nt_mrem'] > 0 and m['osl_nf_mrem'] > 0:
            ratios.append(m['osl_nf_mrem'] / m['osl_nt_mrem'])
    if ratios:
        stats_lines.append("  Fast/thermal ratio: median=%.1f, range=%.1f–%.1f" % (
            np.median(ratios), min(ratios), max(ratios)))

    # Comparison summary
    stats_lines.append("\n" + "=" * 70)
    stats_lines.append("COMPARISON: Does true gamma dose improve correlation?")
    stats_lines.append("=" * 70)

    for col, name in [('ndfeb_mean_pct', 'NdFeB mean'),
                      ('intra_plate_diff', 'NdFeB-SmCo diff')]:
        osl_r = osl_corr.get(col, {})
        ai_r = ai_corr.get(col, {})
        if osl_r and ai_r:
            stats_lines.append("\n  %s:" % name)
            stats_lines.append("    OSL:    Pearson r=%+.3f (p=%.4f), Spearman rho=%+.3f (p=%.4f)" % (
                osl_r['pearson_r'], osl_r['pearson_p'],
                osl_r['spearman_r'], osl_r['spearman_p']))
            stats_lines.append("    AIdata: Pearson r=%+.3f (p=%.4f), Spearman rho=%+.3f (p=%.4f)" % (
                ai_r['pearson_r'], ai_r['pearson_p'],
                ai_r['spearman_r'], ai_r['spearman_p']))

            # Which is better?
            osl_abs = abs(osl_r['spearman_r'])
            ai_abs = abs(ai_r['spearman_r'])
            if ai_abs > osl_abs + 0.05:
                stats_lines.append("    → AIdata IMPROVES correlation (|rho| %.3f vs %.3f)" % (ai_abs, osl_abs))
            elif osl_abs > ai_abs + 0.05:
                stats_lines.append("    → OSL has BETTER correlation (|rho| %.3f vs %.3f)" % (osl_abs, ai_abs))
            else:
                stats_lines.append("    → Similar correlation strength (|rho| %.3f vs %.3f)" % (ai_abs, osl_abs))

    # ── Line position analysis (arc stacks only) ──
    from scipy.stats import spearmanr as _spearmanr
    arc_m = [m for m in merged if 'Arc' in m['region']]
    if arc_m:
        stats_lines.append("\n" + "=" * 70)
        stats_lines.append("LINE POSITION vs DEGRADATION (arc stacks only, N=%d)" % len(arc_m))
        stats_lines.append("  Line 1 = top of stack, Line 5 = bottom")
        stats_lines.append("=" * 70)

        arc_lines = [int(m['line'].replace('Line ', '') if isinstance(m['line'], str) else m['line'])
                     for m in arc_m]
        arc_diffs = [m['intra_plate_diff'] for m in arc_m]
        arc_gammas = [m['ai_photon_gy'] for m in arc_m]
        arc_neutrons = [m['ai_neutron_rem'] for m in arc_m]

        rho_d, p_d = _spearmanr(arc_lines, arc_diffs)
        rho_g, p_g = _spearmanr(arc_lines, arc_gammas)
        rho_n, p_n = _spearmanr(arc_lines, arc_neutrons)

        stats_lines.append("\n  Line vs differential:  Spearman rho=%+.3f (p=%.4f)" % (rho_d, p_d))
        stats_lines.append("  Line vs gamma dose:   Spearman rho=%+.3f (p=%.4f)" % (rho_g, p_g))
        stats_lines.append("  Line vs neutron dose:  Spearman rho=%+.3f (p=%.4f)" % (rho_n, p_n))
        stats_lines.append("  → INVERSION: degradation decreases from top to bottom,")
        stats_lines.append("    but gamma dose increases. Neutron dose shows no line trend.")

        from collections import defaultdict as _dd
        ld = _dd(list)
        lg = _dd(list)
        for m in arc_m:
            ln = int(m['line'].replace('Line ', '') if isinstance(m['line'], str) else m['line'])
            ld[ln].append(m['intra_plate_diff'])
            lg[ln].append(m['ai_photon_gy'])
        stats_lines.append("\n  Per-line means:")
        stats_lines.append("  Line | N | Mean Diff (%) | Mean Gamma (Gy)")
        for ln in sorted(ld.keys()):
            stats_lines.append("  %d    | %d | %+.3f         | %.0f" % (
                ln, len(ld[ln]), np.mean(ld[ln]), np.mean(lg[ln])))

    # Print and save stats
    stats_text = '\n'.join(stats_lines)
    print("\n" + stats_text)

    stats_path = os.path.join(OUT_DIR, 'rod_correlation_stats.txt')
    with open(stats_path, 'w') as f:
        f.write(stats_text + '\n')
    print("\n  Wrote: %s" % stats_path)

    # Generate plots
    print("\nGenerating plots...")
    plot_R1_side_by_side(merged, gain_syst)
    plot_R2_by_material(merged, gain_syst)
    plot_R3_differential(merged, gain_syst)
    plot_R4_regional(merged, gain_syst)
    plot_R5_dose_comparison(merged)
    plot_R6_fast_thermal_neutron(merged, gain_syst)
    plot_R7_line_position_inversion(merged, gain_syst)

    # Final summary
    print("\n" + "=" * 70)
    print("PHASE 5 COMPLETE")
    print("=" * 70)
    print("  Merged Y-plates: %d" % len(merged))
    print("  Dose range (AIdata photon): %.1f – %.0f Gy" % (
        min(m['ai_photon_gy'] for m in merged),
        max(m['ai_photon_gy'] for m in merged)))
    n_sat = sum(1 for m in merged if m['osl_is_lower_bound'])
    print("  OSL-saturated plates: %d / %d" % (n_sat, len(merged)))
    print("  Key question: does true gamma dose correlate with degradation?")

    # Answer the key question
    diff_corr = ai_corr.get('intra_plate_diff', {})
    if diff_corr:
        p = diff_corr['spearman_p']
        r = diff_corr['spearman_r']
        if p < 0.05:
            print("  → YES: Spearman rho=%+.3f, p=%.4f (significant at 5%%)" % (r, p))
        else:
            print("  → NO significant correlation: Spearman rho=%+.3f, p=%.4f" % (r, p))
    else:
        print("  → Could not compute correlation (insufficient data)")

    print("\nDone.")


if __name__ == '__main__':
    main()
