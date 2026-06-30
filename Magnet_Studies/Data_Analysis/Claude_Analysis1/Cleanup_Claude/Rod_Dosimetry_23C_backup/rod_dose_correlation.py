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
                'n_saturated': int(row['n_saturated']),
                'is_lower_bound': row['is_lower_bound'].strip() == 'True',
            }
    return dose


def build_merged_y(results, intra_details, ai_dose, osl_dose):
    """Merge Y-plate degradation with both AIdata and OSL doses."""
    from collections import defaultdict

    clean = [r for r in results if not r['is_outlier']]
    plate_mats = defaultdict(dict)
    for r in clean:
        plate_mats[r['plate']][r['material']] = r['pct_change']

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

        nd_vals = [v for k, v in mats.items() if k in ('N42EH', 'N52SH') and not np.isnan(v)]
        sm_vals = [v for k, v in mats.items() if k in ('SmCo33H', 'SmCo35') and not np.isnan(v)]
        ip = intra_lookup.get(pnum)

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
            # OSL doses (comparison)
            'osl_body_mrem': osl['body_mrem'],
            'osl_photon_mrem': osl['photon_mrem'],
            'osl_neutron_mrem': osl['neutron_mrem'],
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
    """R1: Side-by-side scatter — OSL body dose vs AIdata gamma dose."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    fig.suptitle('NdFeB Degradation vs Dose: OSL (lower bound) vs AIdata (true gamma)',
                 fontsize=13, fontweight='bold')

    datasets = [
        ('OSL Body Dose (mrem)', 'osl_body_mrem', 'osl_is_lower_bound', 1.0),
        ('AIdata Photon Dose (Gy)', 'ai_photon_gy', None, 1.0),
    ]

    for ax, (xlabel, dose_key, lb_key, scale) in zip(axes, datasets):
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
            is_lb = m.get(lb_key, False) if lb_key else False

            ax.scatter(x, y, marker=marker, c=color, s=50, zorder=3,
                       edgecolors='black' if is_lb else color, linewidths=1)
            if is_lb:
                ax.annotate('', xy=(x * 1.5, y), xytext=(x, y),
                            arrowprops=dict(arrowstyle='->', color='black', lw=0.7))

            ax.annotate(m['plate_label'], (x, y), fontsize=6, ha='left',
                        va='bottom', alpha=0.7)
            xs.append(x)
            ys.append(y)

        if len(xs) >= 4:
            r_s, p_s = stats.spearmanr(np.log10(xs), ys)
            r_p, p_p = stats.pearsonr(np.log10(xs), ys)
            ax.text(0.03, 0.97,
                    'Pearson r=%.2f (p=%.3f)\nSpearman rho=%.2f (p=%.3f)\nN=%d' % (
                        r_p, p_p, r_s, p_s, len(xs)),
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

    plt.tight_layout()
    save(fig, 'rod_correlation_R1_side_by_side.png')


def plot_R2_by_material(merged, gain_syst):
    """R2: 4-panel scatter by material vs AIdata gamma dose."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Material-specific Degradation vs AIdata Gamma Dose',
                 fontsize=14, fontweight='bold')

    materials = [('N42EH', 'N42EH_pct'), ('N52SH', 'N52SH_pct'),
                 ('SmCo33H', 'SmCo33H_pct'), ('SmCo35', 'SmCo35_pct')]

    for ax, (mat, col) in zip(axes.flat, materials):
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
        color = REGION_COLORS.get(region, '#666')
        marker = REGION_MARKERS.get(region, 'o')
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
        color = REGION_COLORS.get(region, '#666')
        marker = REGION_MARKERS.get(region, 'o')
        ax.scatter(xs, ys, marker=marker, c=color, s=60, label=region, zorder=3)

    ax.set_xscale('log')
    ax.set_xlabel('AIdata photon dose (Gy)')
    ax.set_ylabel('NdFeB - SmCo diff (%)')
    ax.set_title('Gain-immune Differential by Region')
    ax.legend(fontsize=7, loc='lower left')
    ax.grid(True, alpha=0.3)

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
        'ai_sigma_photon_rem',
        'osl_body_mrem', 'osl_photon_mrem', 'osl_neutron_mrem',
        'osl_n_saturated', 'osl_is_lower_bound',
        'N42EH_pct', 'N52SH_pct', 'SmCo33H_pct', 'SmCo35_pct',
        'ndfeb_mean_pct', 'smco_mean_pct', 'intra_plate_diff',
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
