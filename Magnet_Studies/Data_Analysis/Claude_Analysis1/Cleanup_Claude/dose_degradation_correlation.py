#!/usr/bin/env python3
"""
dose_degradation_correlation.py — Correlate area dosimetry with magnet degradation.

Merges per-plate cumulative dose (OSL area dosimeters) with Helmholtz degradation
data to test whether dose predicts degradation magnitude.

Outputs:
  - dose_vs_degradation.csv    (merged table)
  - dose_vs_degradation_scatter.png   (4-panel scatter by material)
  - dose_by_region.png                (regional dose vs degradation)
  - dose_vs_line_position.png         (arc pass-number trend)
  - dose_vs_differential.png          (gain-immune metric vs dose)
  - dose_timeline_overlay.png         (representative plate time series)
"""

import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict
from scipy import stats

from manager_summary_v3 import (
    load_all, get_gain_syst, compute_intra_plate_diffs,
    MAT_COLORS, FLAGGED, PLACEMENTS, REGION_ORDER, REGION_COLORS,
)
from degradation_summary_v2 import (
    PLACEMENTS as V2_PLACEMENTS, Y_PLACEMENT, H_PLACEMENT,
    load_materials, build_temperature_lookup, compute_h_plate_degradation,
)
from manager_summary_v5_polish import load_a_sample_helmholtz

BASE = os.path.dirname(os.path.abspath(__file__))
DOSE_DIR = os.path.join(BASE, 'Dosimetry', 'OSL_Area')
PLOT_DIR = DOSE_DIR  # output plots alongside dose CSVs
os.makedirs(PLOT_DIR, exist_ok=True)

GAIN_SYST = 0.248  # ±% gain systematic — updated dynamically in main()

# ── Unit conversions ──────────────────────────────────────────────────────────
#
# Landauer reports dose EQUIVALENT (H) in mrem.
#   H [Sv] = Q × D [Gy]   →   D [Gy] = H [Sv] / Q
#
# Quality factors (Q) used here:
#   Photons/gamma:  Q = 1     (exact, by definition)
#   Beta/electrons: Q = 1     (exact, by definition)
#   Fast neutrons:  Q = 10    (ICRP 60 w_R for 0.1–2 MeV; Landauer calibrates
#                               CR-39 with Am-Be source, ~4.5 MeV avg)
#   Thermal neutrons: Q = 2.5 (ICRP 103 continuous w_R function at thermal;
#                               10 CFR 20 step function gives w_R = 5)
#
# IMPORTANT: Landauer applies their own Q internally when converting CR-39
# track counts to mrem. The Q they use may differ slightly from our assumed
# values. This introduces ~factor-of-2 uncertainty in neutron absorbed dose.
# Dose equivalent (Sv) is the as-reported value with no assumptions.
#
# For material damage studies, absorbed dose (Gy) is more physically relevant
# than dose equivalent (Sv), since Q is a biological weighting factor.
# However, displacement damage (DDD/NIEL) depends on particle type and energy
# in ways not captured by simple Q conversion.
# ─────────────────────────────────────────────────────────────────────────────
MREM_TO_MSV = 0.01   # mrem → mSv (dose equivalent, always exact)
MREM_TO_SV  = 1e-5   # mrem → Sv  (dose equivalent, always exact)

# Quality factors for absorbed dose conversion
Q_PHOTON  = 1.0
Q_BETA    = 1.0
Q_FAST_N  = 10.0   # ICRP 60, ~1 MeV neutrons
Q_THERM_N = 2.5    # ICRP 103 continuous w_R at thermal energy

# Derived conversion factors: mrem → Gy (absorbed dose)
MREM_TO_GY_PHOTON = MREM_TO_SV / Q_PHOTON    # = 1e-5
MREM_TO_GY_BETA   = MREM_TO_SV / Q_BETA      # = 1e-5
MREM_TO_GY_FAST_N = MREM_TO_SV / Q_FAST_N    # = 1e-6
MREM_TO_GY_THERM_N = MREM_TO_SV / Q_THERM_N  # = 4e-6

# Presentation colors (NdFeB warm, SmCo cool)
PRES_COLORS = {
    'N42EH': '#CC3333', 'N52SH': '#FF6644',
    'SmCo33H': '#3366CC', 'SmCo35': '#66AADD',
}


def dose_dual(mrem, kind='body'):
    """Format dose in dual units: mrem + SI.

    kind='photon'/'beta': show Gy (Q=1, so rem=rad)
    kind='neutron'/'body': show Sv (dose equivalent only; Q≠1 for neutrons)
    """
    if kind in ('photon', 'beta'):
        gy = mrem * MREM_TO_GY_PHOTON
        if gy >= 1.0:
            return '{:,.0f} mrem ({:.1f} Gy)'.format(mrem, gy)
        elif gy >= 0.01:
            return '{:,.0f} mrem ({:.0f} mGy)'.format(mrem, gy * 1000)
        else:
            return '{:,.0f} mrem ({:.1f} mGy)'.format(mrem, gy * 1000)
    else:
        sv = mrem * MREM_TO_SV
        if sv >= 1.0:
            return '{:,.0f} mrem ({:.1f} Sv)'.format(mrem, sv)
        elif sv >= 0.01:
            return '{:,.0f} mrem ({:.0f} mSv)'.format(mrem, sv * 1000)
        else:
            return '{:,.0f} mrem ({:.1f} mSv)'.format(mrem, sv * 1000)


def _add_secondary_axis(ax, factor, label, axis='x'):
    """Add a secondary axis with a linear mrem→unit conversion."""
    fwd = lambda x, f=factor: x * f
    inv = lambda x, f=factor: x / f
    if axis == 'x':
        secax = ax.secondary_xaxis('top', functions=(fwd, inv))
        secax.set_xlabel(label, fontsize=9, color='#666666')
    else:
        secax = ax.secondary_yaxis('right', functions=(fwd, inv))
        secax.set_ylabel(label, fontsize=9, color='#666666')
    secax.tick_params(labelsize=8, colors='#666666')
    return secax


def add_sv_axis(ax, axis='x', label='Dose equivalent (Sv)'):
    """Add secondary axis: mrem → Sv (dose equivalent, no Q assumptions)."""
    return _add_secondary_axis(ax, MREM_TO_SV, label, axis)


def add_gy_axis(ax, axis='x', label=None):
    """Add secondary axis: mrem → Gy for photon (Q=1)."""
    if label is None:
        label = 'Absorbed dose (Gy) [Q=%g]' % Q_PHOTON
    return _add_secondary_axis(ax, MREM_TO_GY_PHOTON, label, axis)


# Mapping from dose column to (conversion_factor, axis_label)
DOSE_COL_AXIS = {
    'cum_photon_mrem': (MREM_TO_GY_PHOTON,
                        'Absorbed dose (Gy) [Q=%g]' % Q_PHOTON),
    'cum_beta_mrem':   (MREM_TO_GY_BETA,
                        'Absorbed dose (Gy) [Q=%g]' % Q_BETA),
    'cum_nf_mrem':     (MREM_TO_GY_FAST_N,
                        'Absorbed dose (Gy) [Q=%g]' % Q_FAST_N),
    'cum_nt_mrem':     (MREM_TO_GY_THERM_N,
                        'Absorbed dose (Gy) [Q=%g]' % Q_THERM_N),
    'cum_neutron_mrem': (MREM_TO_GY_FAST_N,
                         'Abs. dose (Gy) [Q≈%g, fast-dominated]' % Q_FAST_N),
    'cum_body_mrem':   (MREM_TO_SV,
                        'Dose equivalent (Sv) [mixed radiation]'),
}

# SI conversion for primary plot axes (mrem → SI at plot time; raw data unchanged)
DOSE_PLOT_CONV = {
    'cum_body_mrem':    (MREM_TO_SV,  'Sv'),   # 80k–12M mrem → 0.8–120 Sv
    'cum_photon_mrem':  (MREM_TO_MSV, 'mSv'),
    'cum_beta_mrem':    (MREM_TO_MSV, 'mSv'),
    'cum_neutron_mrem': (MREM_TO_MSV, 'mSv'),  # 120–52k mrem → 1.2–520 mSv
    'cum_nf_mrem':      (MREM_TO_MSV, 'mSv'),  # 1.7k–52k mrem → 17–520 mSv
    'cum_nt_mrem':      (MREM_TO_MSV, 'mSv'),  # 120–3.8k mrem → 1.2–38 mSv
}


def save(fig, name):
    path = os.path.join(PLOT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("  Saved: %s" % path)


# ═══════════════════════════════════════════════════════════════════════════════
# Data Loading
# ═══════════════════════════════════════════════════════════════════════════════

def load_dose_cumulative():
    """Load plate_cumulative_dose.csv → dict keyed by plate string (e.g. 'Y-3')."""
    path = os.path.join(DOSE_DIR, 'plate_cumulative_dose.csv')
    dose = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            plate = row['plate'].strip()
            dose[plate] = {
                'plate_type': row['plate_type'].strip(),
                'body_mrem': float(row['body_mrem']),
                'photon_mrem': float(row['photon_mrem']),
                'beta_mrem': float(row['beta_mrem']),
                'neutron_mrem': float(row['neutron_mrem']),
                'nt_mrem': float(row['nt_mrem']),
                'nf_mrem': float(row['nf_mrem']),
                'n_saturated': int(row['n_saturated']),
                'is_lower_bound': row['is_lower_bound'].strip() == 'True',
            }
    return dose


def load_dose_timeline():
    """Load plate_dose_timeline.csv → dict of plate -> list of (date, cum_body)."""
    path = os.path.join(DOSE_DIR, 'plate_dose_timeline.csv')
    timeline = defaultdict(list)
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            plate = row['plate'].strip()
            date = datetime.strptime(row['collection_date'].strip(), '%Y-%m-%d')
            timeline[plate].append({
                'date': date,
                'cum_body': float(row['cum_body_mrem']),
                'cum_neutron': float(row['cum_neutron_mrem']),
                'status': row['this_dose_status'].strip(),
                'is_lower_bound': row['is_lower_bound'].strip() == 'True',
            })
    # Sort by date
    for plate in timeline:
        timeline[plate].sort(key=lambda x: x['date'])
    return dict(timeline)


# ═══════════════════════════════════════════════════════════════════════════════
# Merge degradation + dose
# ═══════════════════════════════════════════════════════════════════════════════

def merge_data(results, intra_details, dose_cum):
    """Merge Y-plate degradation with dose data.

    Returns list of dicts, one per Y-plate (30 plates).
    """
    clean = [r for r in results if not r['is_outlier']]

    # Build per-plate material pct_change lookup
    plate_mats = defaultdict(dict)
    for r in clean:
        plate_mats[r['plate']][r['material']] = r['pct_change']

    # Build intra-plate diff lookup
    intra_lookup = {d['plate']: d for d in intra_details}

    # Build placement lookup from v2
    merged = []
    for yp, hp, region, subloc, line in V2_PLACEMENTS:
        pnum = int(yp.replace('Y', ''))
        dose_key = 'Y-%d' % pnum

        if dose_key not in dose_cum:
            print("  WARNING: No dose data for %s" % dose_key)
            continue

        d = dose_cum[dose_key]
        mats = plate_mats.get(pnum, {})

        row = {
            'plate': pnum,
            'plate_label': dose_key,
            'region': region,
            'sub_location': subloc,
            'line': line,
            'cum_body_mrem': d['body_mrem'],
            'cum_photon_mrem': d['photon_mrem'],
            'cum_beta_mrem': d['beta_mrem'],
            'cum_neutron_mrem': d['neutron_mrem'],
            'cum_nt_mrem': d['nt_mrem'],
            'cum_nf_mrem': d['nf_mrem'],
            'is_lower_bound': d['is_lower_bound'],
            'n_saturated': d['n_saturated'],
            'N42EH_pct': mats.get('N42EH', np.nan),
            'N52SH_pct': mats.get('N52SH', np.nan),
            'SmCo33H_pct': mats.get('SmCo33H', np.nan),
            'SmCo35_pct': mats.get('SmCo35', np.nan),
        }

        # Compute mean NdFeB and SmCo
        nd_vals = [v for k, v in mats.items() if k in ('N42EH', 'N52SH') and not np.isnan(v)]
        sm_vals = [v for k, v in mats.items() if k in ('SmCo33H', 'SmCo35') and not np.isnan(v)]
        row['ndfeb_mean_pct'] = np.mean(nd_vals) if nd_vals else np.nan
        row['smco_mean_pct'] = np.mean(sm_vals) if sm_vals else np.nan

        # Intra-plate diff
        ip = intra_lookup.get(pnum)
        row['intra_plate_diff'] = ip['diff'] if ip else np.nan

        merged.append(row)

    return merged


def merge_h_plate_data(h_results, dose_cum):
    """Merge H-plate pair assembly degradation with dose data.

    Each H-plate pair (e.g., Hn-6-1) maps to its parent plate (Hn-6) for dose.
    Returns list of dicts, one per H-plate pair assembly.
    """
    merged = []
    for r in h_results:
        if r['is_outlier']:
            continue
        ns = 'n' if r['material'] == 'NdFeB' else 's'
        dose_key = 'H%s-%d' % (ns, r['plate'])
        if dose_key not in dose_cum:
            continue
        d = dose_cum[dose_key]
        merged.append({
            'sample': r['sample'],
            'plate': r['plate'],
            'slot': r['slot'],
            'material': r['material'],
            'config': r.get('config', ''),
            'region': r['region'],
            'sub_location': r.get('sub_location', ''),
            'line': r['line'],
            'pct_change': r['pct_change'],
            'cum_body_mrem': d['body_mrem'],
            'cum_photon_mrem': d['photon_mrem'],
            'cum_neutron_mrem': d['neutron_mrem'],
            'cum_nf_mrem': d['nf_mrem'],
            'cum_nt_mrem': d['nt_mrem'],
            'cum_beta_mrem': d['beta_mrem'],
            'is_lower_bound': d['is_lower_bound'],
            'n_saturated': d['n_saturated'],
            'sample_type': 'H',
        })
    return merged


def merge_a_sample_data(a_results, dose_cum):
    """Merge A-sample Helmholtz degradation with dose data.

    Each A-sample (An-XX-Y-Z) maps to parent H-plate (Hn-XX) for dose.
    Returns list of dicts, one per A-sample.
    """
    merged = []
    for r in a_results:
        if r['is_outlier']:
            continue
        ns = 'n' if r['material'] == 'NdFeB' else 's'
        dose_key = 'H%s-%d' % (ns, r['plate'])
        if dose_key not in dose_cum:
            continue
        d = dose_cum[dose_key]
        merged.append({
            'sample': r['sample'],
            'plate': r['plate'],
            'pair_slot': r['pair_slot'],
            'magnet_idx': r['magnet_idx'],
            'material': r['material'],
            'region': r['region'],
            'line': r['line'],
            'pct_change': r['pct_change'],
            'temp_corrected': r['temp_corrected'],
            'n_baseline': r['n_baseline'],
            'cum_body_mrem': d['body_mrem'],
            'cum_photon_mrem': d['photon_mrem'],
            'cum_neutron_mrem': d['neutron_mrem'],
            'cum_nf_mrem': d['nf_mrem'],
            'cum_nt_mrem': d['nt_mrem'],
            'cum_beta_mrem': d['beta_mrem'],
            'is_lower_bound': d['is_lower_bound'],
            'n_saturated': d['n_saturated'],
            'sample_type': 'A',
        })
    return merged


def print_h_plate_summary(h_merged):
    """Print H-plate dose-degradation summary table."""
    print("\n" + "="*80)
    print("H-PLATE PAIR ASSEMBLY DOSE-DEGRADATION TABLE")
    print("  Note: H-plates have FULL ±0.248% gain systematic (no intra-plate differential)")
    print("="*80)

    # Group by parent plate
    by_plate = defaultdict(list)
    for m in h_merged:
        ns = 'n' if m['material'] == 'NdFeB' else 's'
        parent = 'H%s-%d' % (ns, m['plate'])
        by_plate[parent].append(m)

    print("%-10s %-8s %-6s %-14s %5s %14s %8s %8s %s" % (
        'Sample', 'Material', 'Config', 'Region', 'Line',
        'Body(mrem)', 'Body(Sv)', 'Pct%', 'Sat?'))
    print("-" * 100)

    for parent in sorted(by_plate.keys(),
                         key=lambda x: (x[0:2], int(x.split('-')[1]))):
        entries = sorted(by_plate[parent], key=lambda x: x['slot'])
        for m in entries:
            sat = '>' if m['is_lower_bound'] else ' '
            print("%-10s %-8s %-6s %-14s %5d %s%13s %8.1f %+7.3f" % (
                m['sample'], m['material'], m['config'], m['region'],
                m['line'], sat,
                '{:,.0f}'.format(m['cum_body_mrem']),
                m['cum_body_mrem'] * MREM_TO_SV,
                m['pct_change']))

    # Summary stats by material
    for mat in ('NdFeB', 'SmCo'):
        vals = [m['pct_change'] for m in h_merged if m['material'] == mat]
        if vals:
            mean = np.mean(vals)
            sem = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0
            print("\n  H-plate %s (N=%d): mean=%.3f%% ± %.3f%%" %
                  (mat, len(vals), mean, sem))


def print_a_sample_summary(a_merged):
    """Print A-sample dose-degradation summary."""
    print("\n" + "="*80)
    print("A-SAMPLE DOSE-DEGRADATION SUMMARY")
    print("  Note: A-samples = pairs (2 magnets in enclosure, measured together on Helmholtz)")
    print("  Same dose as parent H-plate (co-located dosimeter)")
    print("="*80)

    for mat in ('NdFeB', 'SmCo'):
        sub = [m for m in a_merged if m['material'] == mat]
        tc = [m for m in sub if m['temp_corrected']]
        vals = [m['pct_change'] for m in tc]
        if vals:
            mean = np.mean(vals)
            sem = np.std(vals, ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0
            print("\n  A-sample %s (N=%d temp-corrected): mean=%.3f%% ± %.3f%%" %
                  (mat, len(vals), mean, sem))

    # Regional breakdown
    print("\n  Regional breakdown (temp-corrected only):")
    print("  %-14s %5s %5s %10s %10s" % ('Region', 'NdFeB', 'SmCo', 'NdFeB%', 'SmCo%'))
    regions_seen = set(m['region'] for m in a_merged)
    for reg in REGION_ORDER:
        if reg not in regions_seen:
            continue
        for mat in ('NdFeB', 'SmCo'):
            vals = [m['pct_change'] for m in a_merged
                    if m['region'] == reg and m['material'] == mat and m['temp_corrected']]
        nd = [m['pct_change'] for m in a_merged
              if m['region'] == reg and m['material'] == 'NdFeB' and m['temp_corrected']]
        sm = [m['pct_change'] for m in a_merged
              if m['region'] == reg and m['material'] == 'SmCo' and m['temp_corrected']]
        if nd or sm:
            print("  %-14s %5d %5d %10s %10s" % (
                reg, len(nd), len(sm),
                '%.3f' % np.mean(nd) if nd else '—',
                '%.3f' % np.mean(sm) if sm else '—'))


def plot_h_a_dose_scatter(h_merged, a_merged, y_merged):
    """Combined scatter: Y + H + A samples, dose vs degradation, NdFeB only."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
    fig.suptitle('Dose vs NdFeB Degradation — Y-plates, H-plates, A-samples',
                 fontsize=14, fontweight='bold', y=1.02)

    region_markers = {
        'SE Arc': 'o', 'NE Arc': 'o', 'NW Arc': 'o', 'SW Arc': 'o',
        'North Linac': 's', 'South Linac': 's', 'Labyrinth': '^',
    }

    datasets = [
        ('Y-plates (Helmholtz)', y_merged, '#CC3333'),
        ('H-plates (Helmholtz)', h_merged, '#3366CC'),
        ('A-samples (Helmholtz)', a_merged, '#228B22'),
    ]

    for ax, (title, data, color) in zip(axes, datasets):
        ax.axhspan(-GAIN_SYST, GAIN_SYST, color='gray', alpha=0.12, zorder=0)
        ax.axhline(0, color='gray', linewidth=0.5, zorder=1)

        # Extract NdFeB only
        if title.startswith('Y'):
            nd_data = [(m['cum_body_mrem'] * MREM_TO_SV, m['ndfeb_mean_pct'],
                        m['is_lower_bound'], m['region'],
                        m['plate_label']) for m in data
                       if not np.isnan(m.get('ndfeb_mean_pct', np.nan))]
        else:
            nd_data = [(m['cum_body_mrem'] * MREM_TO_SV, m['pct_change'],
                        m['is_lower_bound'], m['region'],
                        m['sample']) for m in data
                       if m['material'] == 'NdFeB']

        xs_all, ys_all = [], []
        for dose, pct, is_lb, region, label in nd_data:
            if dose <= 0:
                continue
            marker = region_markers.get(region, 'o')
            ec = 'black' if is_lb else color
            ax.scatter(dose, pct, marker=marker, c=color, edgecolors=ec,
                       s=40, linewidths=1.0, zorder=3, alpha=0.7)
            if is_lb:
                ax.annotate('', xy=(dose * 1.4, pct), xytext=(dose, pct),
                            arrowprops=dict(arrowstyle='->', color='black', lw=0.8))
            xs_all.append(dose)
            ys_all.append(pct)

        # Correlation
        if len(xs_all) >= 4:
            r_s, p_s = stats.spearmanr(np.log10(xs_all), ys_all)
            ax.text(0.03, 0.97,
                    'ρ=%.2f (p=%.3f)\nN=%d' % (r_s, p_s, len(xs_all)),
                    transform=ax.transAxes, fontsize=9, va='top',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='gray', alpha=0.8))

        # Mean line
        if ys_all:
            mean_pct = np.mean(ys_all)
            ax.axhline(mean_pct, color=color, linewidth=1, linestyle='--', alpha=0.7)
            ax.text(0.97, mean_pct, '%.2f%%' % mean_pct,
                    transform=ax.get_yaxis_transform(), fontsize=8,
                    va='bottom', ha='right', color=color)

        ax.set_xscale('log')
        ax.set_title(title, fontsize=12, fontweight='bold', color=color)
        ax.set_xlabel('Cumulative body dose equivalent (Sv)', fontsize=10)
        ax.grid(True, alpha=0.3)

    axes[0].set_ylabel('NdFeB % change', fontsize=11)

    fig.tight_layout()
    save(fig, 'dose_vs_degradation_YHA.png')


def write_csv(merged):
    """Write merged table to CSV."""
    path = os.path.join(DOSE_DIR, 'dose_vs_degradation.csv')
    fields = [
        'plate', 'region', 'sub_location', 'line',
        'cum_body_mrem', 'cum_photon_mrem', 'cum_beta_mrem',
        'cum_neutron_mrem', 'cum_nt_mrem', 'cum_nf_mrem',
        'is_lower_bound', 'n_saturated',
        'N42EH_pct', 'N52SH_pct', 'SmCo33H_pct', 'SmCo35_pct',
        'ndfeb_mean_pct', 'smco_mean_pct', 'intra_plate_diff',
    ]
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for row in merged:
            writer.writerow(row)
    print("  Wrote: %s (%d rows)" % (path, len(merged)))


# ═══════════════════════════════════════════════════════════════════════════════
# Statistics
# ═══════════════════════════════════════════════════════════════════════════════

def print_correlations(merged):
    """Print Pearson and Spearman correlations for each material and differential."""
    print("\n" + "="*70)
    print("DOSE-DEGRADATION CORRELATIONS")
    print("="*70)

    # Use log(body dose) for correlations — more natural scale
    # Separate unsaturated vs all
    for label, subset in [("All 30 plates", merged),
                          ("Unsaturated only", [m for m in merged if not m['is_lower_bound']])]:
        n_lb = sum(1 for m in subset if m['is_lower_bound'])
        lb_note = " (%d/%d are LOWER BOUNDS from saturated OSL)" % (n_lb, len(subset)) if n_lb else ""
        print("\n--- %s (N=%d)%s ---" % (label, len(subset), lb_note))
        if len(subset) < 4:
            print("  Too few plates for correlation")
            continue

        doses = np.array([m['cum_body_mrem'] for m in subset])
        log_doses = np.log10(np.clip(doses, 1, None))

        for col, name in [('ndfeb_mean_pct', 'NdFeB mean'),
                          ('smco_mean_pct', 'SmCo mean'),
                          ('intra_plate_diff', 'NdFeB-SmCo diff'),
                          ('N42EH_pct', 'N42EH'),
                          ('N52SH_pct', 'N52SH'),
                          ('SmCo33H_pct', 'SmCo33H'),
                          ('SmCo35_pct', 'SmCo35')]:
            vals = np.array([m[col] for m in subset])
            mask = ~np.isnan(vals)
            if mask.sum() < 4:
                continue
            x, y = log_doses[mask], vals[mask]
            r_p, p_p = stats.pearsonr(x, y)
            r_s, p_s = stats.spearmanr(x, y)
            print("  %-18s  Pearson r=%.3f (p=%.3f)  Spearman ρ=%.3f (p=%.3f)" %
                  (name, r_p, p_p, r_s, p_s))

    # Also try neutron dose (always available, no saturation)
    print("\n--- Neutron dose only (all 30 plates) ---")
    neutron = np.array([m['cum_neutron_mrem'] for m in merged])
    log_n = np.log10(np.clip(neutron, 1, None))
    for col, name in [('ndfeb_mean_pct', 'NdFeB mean'),
                      ('smco_mean_pct', 'SmCo mean'),
                      ('intra_plate_diff', 'NdFeB-SmCo diff')]:
        vals = np.array([m[col] for m in merged])
        mask = ~np.isnan(vals)
        if mask.sum() < 4:
            continue
        x, y = log_n[mask], vals[mask]
        r_p, p_p = stats.pearsonr(x, y)
        r_s, p_s = stats.spearmanr(x, y)
        print("  %-18s  Pearson r=%.3f (p=%.3f)  Spearman ρ=%.3f (p=%.3f)" %
              (name, r_p, p_p, r_s, p_s))


def print_summary_table(merged):
    """Print summary table to stdout."""
    print("\n" + "="*80)
    print("MERGED DOSE-DEGRADATION TABLE (sorted by body dose)")
    print("  Body dose in Sv (dose equivalent); 1 mrem = 0.01 mSv = 10 μSv")
    print("  Neutron: dose equivalent (mrem/Sv), NOT absorbed dose — Q ≈ 5–20")
    print("="*80)
    print("%-6s %-14s %5s %14s %8s %12s %8s %8s %8s %s" % (
        'Plate', 'Region', 'Line', 'Body(mrem)', 'Body(Sv)',
        'Neut(mrem)', 'NdFeB%', 'SmCo%', 'Diff%', 'Sat?'))
    print("-" * 115)
    for m in sorted(merged, key=lambda x: x['cum_body_mrem'], reverse=True):
        sat = '>' if m['is_lower_bound'] else ' '
        nd = '%.3f' % m['ndfeb_mean_pct'] if not np.isnan(m['ndfeb_mean_pct']) else '  —  '
        sm = '%.3f' % m['smco_mean_pct'] if not np.isnan(m['smco_mean_pct']) else '  —  '
        diff = '%.3f' % m['intra_plate_diff'] if not np.isnan(m['intra_plate_diff']) else '  —  '
        body_sv = m['cum_body_mrem'] * MREM_TO_SV
        print("Y-%-4d %-14s %5d %s%13s %8.1f %12s %8s %8s %8s" % (
            m['plate'], m['region'], m['line'], sat,
            '{:,.0f}'.format(m['cum_body_mrem']),
            body_sv,
            '{:,.0f}'.format(m['cum_neutron_mrem']),
            nd, sm, diff))


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 1: Dose vs Degradation Scatter (4 panels by material)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_scatter(merged):
    """4-panel scatter: dose vs % change, one per material grade."""
    materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
    col_map = {'N42EH': 'N42EH_pct', 'N52SH': 'N52SH_pct',
               'SmCo33H': 'SmCo33H_pct', 'SmCo35': 'SmCo35_pct'}

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=True)
    fig.suptitle('Cumulative Dose vs Magnet Degradation by Material Grade',
                 fontsize=14, fontweight='bold', y=0.98)

    # Region shape mapping
    region_markers = {
        'SE Arc': 'o', 'NE Arc': 'o', 'NW Arc': 'o', 'SW Arc': 'o',
        'North Linac': 's', 'South Linac': 's',
        'Labyrinth': '^',
    }
    region_type = {}
    for r in REGION_ORDER:
        if 'Arc' in r:
            region_type[r] = 'Arc'
        elif 'Linac' in r:
            region_type[r] = 'Linac'
        else:
            region_type[r] = 'Labyrinth'

    for ax, mat in zip(axes.flat, materials):
        col = col_map[mat]
        color = PRES_COLORS[mat]

        # Gain systematic band
        ax.axhspan(-GAIN_SYST, GAIN_SYST, color='gray', alpha=0.12, zorder=0)
        ax.axhline(0, color='gray', linewidth=0.5, zorder=1)

        for m in merged:
            val = m[col]
            if np.isnan(val):
                continue
            dose = m['cum_body_mrem'] * MREM_TO_SV
            marker = region_markers.get(m['region'], 'o')
            ec = 'black' if m['is_lower_bound'] else color
            fc = color

            ax.scatter(dose, val, marker=marker, c=fc, edgecolors=ec,
                       s=60, linewidths=1.2, zorder=3, alpha=0.85)

            # Right arrow for lower bounds (saturated)
            if m['is_lower_bound']:
                ax.annotate('', xy=(dose * 1.5, val),
                            xytext=(dose, val),
                            arrowprops=dict(arrowstyle='->', color='black',
                                            lw=1.2))

            # Label plate number
            ax.annotate('Y-%d' % m['plate'], (dose, val),
                        fontsize=6, ha='left', va='bottom',
                        xytext=(3, 2), textcoords='offset points',
                        color='gray')

        # Correlation (unsaturated only for cleaner signal)
        unsat = [(m['cum_body_mrem'] * MREM_TO_SV, m[col]) for m in merged
                 if not np.isnan(m[col]) and not m['is_lower_bound']]
        if len(unsat) >= 4:
            xv, yv = zip(*unsat)
            xlog = np.log10(np.array(xv))
            yv = np.array(yv)
            r_s, p_s = stats.spearmanr(xlog, yv)
            ax.text(0.03, 0.97, 'ρ=%.2f (p=%.3f)\nN=%d unsat' % (r_s, p_s, len(unsat)),
                    transform=ax.transAxes, fontsize=9, va='top', ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='gray', alpha=0.8))

        ax.set_xscale('log')
        ax.set_title(mat, fontsize=12, fontweight='bold', color=color)
        ax.set_ylabel('% change')
        ax.set_xlabel('Cumulative body dose equivalent (Sv)')
        ax.grid(True, alpha=0.3)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
               markersize=8, label='Arc'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='gray',
               markersize=8, label='Linac'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='gray',
               markersize=8, label='Labyrinth'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
               markeredgecolor='black', markersize=8, linewidth=1.5,
               label='Saturated (→ = lower bound)'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=4,
               fontsize=9, frameon=True, bbox_to_anchor=(0.5, 0.0))

    fig.tight_layout(rect=[0, 0.05, 1, 0.96])
    save(fig, 'dose_vs_degradation_scatter.png')


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 2: Dose by Region (bars + degradation overlay)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_by_region(merged):
    """Grouped bars: mean dose and mean NdFeB degradation by region."""
    # Group by region
    region_data = defaultdict(lambda: {'doses': [], 'ndfeb': [], 'smco': [], 'diffs': []})
    for m in merged:
        r = m['region']
        region_data[r]['doses'].append(m['cum_body_mrem'] * MREM_TO_SV)
        if not np.isnan(m['ndfeb_mean_pct']):
            region_data[r]['ndfeb'].append(m['ndfeb_mean_pct'])
        if not np.isnan(m['smco_mean_pct']):
            region_data[r]['smco'].append(m['smco_mean_pct'])
        if not np.isnan(m['intra_plate_diff']):
            region_data[r]['diffs'].append(m['intra_plate_diff'])

    # Combine arcs
    regions = ['Arcs (all)', 'North Linac', 'South Linac', 'Labyrinth']
    combined = defaultdict(lambda: {'doses': [], 'ndfeb': [], 'smco': [], 'diffs': []})
    for r, data in region_data.items():
        key = 'Arcs (all)' if 'Arc' in r else r
        for k in ('doses', 'ndfeb', 'smco', 'diffs'):
            combined[key][k].extend(data[k])

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    x = np.arange(len(regions))
    width = 0.35

    # Dose bars (left axis)
    dose_means = []
    dose_notes = []
    for r in regions:
        vals = combined[r]['doses']
        dose_means.append(np.mean(vals) if vals else 0)
        n_lb = sum(1 for m in merged
                   if m['is_lower_bound'] and
                   (('Arc' in m['region'] and r == 'Arcs (all)') or m['region'] == r))
        dose_notes.append('%d/%d sat' % (n_lb, len(vals)) if n_lb > 0 else '')

    bars1 = ax1.bar(x - width/2, dose_means, width, color='#AAAADD',
                    edgecolor='#555588', linewidth=0.8, label='Mean body dose', zorder=2)

    # Annotate saturation
    for i, note in enumerate(dose_notes):
        if note:
            ax1.text(i - width/2, dose_means[i], note,
                     ha='center', va='bottom', fontsize=8, color='#555588',
                     fontweight='bold')

    # NdFeB degradation bars (right axis)
    nd_means = [np.mean(combined[r]['ndfeb']) if combined[r]['ndfeb'] else 0 for r in regions]
    nd_sems = [np.std(combined[r]['ndfeb'], ddof=1) / np.sqrt(len(combined[r]['ndfeb']))
               if len(combined[r]['ndfeb']) > 1 else 0 for r in regions]

    bars2 = ax2.bar(x + width/2, nd_means, width, color='#DD6666',
                    edgecolor='#883333', linewidth=0.8, label='Mean NdFeB % change',
                    yerr=nd_sems, capsize=5, error_kw={'linewidth': 1.2}, zorder=2)

    # Gain band on right axis
    ax2.axhspan(-GAIN_SYST, GAIN_SYST, color='gray', alpha=0.08, zorder=0)

    ax1.set_xlabel('Region', fontsize=12)
    ax1.set_ylabel('Cumulative body dose equivalent (Sv)', fontsize=11, color='#555588')
    ax2.set_ylabel('NdFeB mean % change', fontsize=11, color='#883333')
    ax1.set_xticks(x)
    ax1.set_xticklabels(regions, fontsize=10)
    ax1.set_title('Dose and NdFeB Degradation by Region', fontsize=13, fontweight='bold')

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

    ax1.grid(True, axis='y', alpha=0.3)
    fig.tight_layout()
    save(fig, 'dose_by_region.png')

    # Print region summary
    print("\n--- Regional dose vs degradation ---")
    print("%-16s %12s %8s %10s %10s %10s" % (
        'Region', 'Dose(mrem)', 'Dose(Sv)', 'NdFeB%', 'SmCo%', 'Diff%'))
    for r in regions:
        d = combined[r]
        mean_d = np.mean(d['doses']) if d['doses'] else 0
        print("%-16s %12s %8.1f %10.3f %10.3f %10.3f" % (
            r,
            '{:,.0f}'.format(mean_d),
            mean_d * MREM_TO_SV,
            np.mean(d['ndfeb']) if d['ndfeb'] else np.nan,
            np.mean(d['smco']) if d['smco'] else np.nan,
            np.mean(d['diffs']) if d['diffs'] else np.nan,
        ))


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 3: Dose vs Line Position (arcs only)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_line_position(merged):
    """Arc plates only: dose and degradation vs line position (1-5)."""
    arc = [m for m in merged if m['line'] > 0]
    if not arc:
        print("  No arc plates with line > 0, skipping line position plot")
        return

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    # Group by line
    line_data = defaultdict(lambda: {'doses': [], 'ndfeb': [], 'diffs': []})
    for m in arc:
        line_data[m['line']]['doses'].append(m['cum_body_mrem'] * MREM_TO_SV)
        if not np.isnan(m['ndfeb_mean_pct']):
            line_data[m['line']]['ndfeb'].append(m['ndfeb_mean_pct'])
        if not np.isnan(m['intra_plate_diff']):
            line_data[m['line']]['diffs'].append(m['intra_plate_diff'])

    lines = sorted(line_data.keys())
    x = np.array(lines)

    # Individual plate scatter (dose)
    for m in arc:
        marker = 'v' if m['is_lower_bound'] else 'o'
        ax1.scatter(m['line'], m['cum_body_mrem'] * MREM_TO_SV, c='#7777BB', marker=marker,
                    s=40, alpha=0.5, zorder=2)

    # Mean dose per line
    mean_doses = [np.mean(line_data[l]['doses']) for l in lines]
    ax1.plot(x, mean_doses, 'o-', color='#4444AA', markersize=10, linewidth=2,
             label='Mean body dose', zorder=3)

    # NdFeB degradation per line
    mean_nd = [np.mean(line_data[l]['ndfeb']) if line_data[l]['ndfeb'] else np.nan
               for l in lines]
    sem_nd = [np.std(line_data[l]['ndfeb'], ddof=1) / np.sqrt(len(line_data[l]['ndfeb']))
              if len(line_data[l]['ndfeb']) > 1 else 0 for l in lines]
    ax2.errorbar(x, mean_nd, yerr=sem_nd, fmt='s-', color='#CC3333', markersize=10,
                 linewidth=2, capsize=5, label='Mean NdFeB % change', zorder=3)

    # Intra-plate diff
    mean_diff = [np.mean(line_data[l]['diffs']) if line_data[l]['diffs'] else np.nan
                 for l in lines]
    ax2.plot(x, mean_diff, 'D--', color='#228B22', markersize=8, linewidth=1.5,
             label='NdFeB−SmCo diff', zorder=3)

    ax2.axhspan(-GAIN_SYST, GAIN_SYST, color='gray', alpha=0.08, zorder=0)
    ax2.axhline(0, color='gray', linewidth=0.5, zorder=1)

    ax1.set_xlabel('Line Position (1=top/lowest E, 5=bottom/highest E)', fontsize=11)
    ax1.set_ylabel('Cumulative body dose equivalent (Sv)', fontsize=11, color='#4444AA')
    ax2.set_ylabel('% change', fontsize=11, color='#CC3333')
    ax1.set_xticks(lines)
    ax1.set_title('Dose & Degradation vs Arc Line Position', fontsize=13, fontweight='bold')

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='lower left', fontsize=9)

    ax1.grid(True, alpha=0.3)
    fig.tight_layout()
    save(fig, 'dose_vs_line_position.png')

    # Print line-position table
    print("\n--- Line position (arcs only, N=4 stacks per line) ---")
    print("Line  MeanDose(mrem) Dose(Sv)   NdFeB%    Diff%    N_plates")
    for l in lines:
        mean_d = np.mean(line_data[l]['doses'])
        print("  %d   %13s  %7.1f   %7.3f   %7.3f   %d" % (
            l,
            '{:,.0f}'.format(mean_d),
            mean_d * MREM_TO_SV,
            np.mean(line_data[l]['ndfeb']) if line_data[l]['ndfeb'] else np.nan,
            np.mean(line_data[l]['diffs']) if line_data[l]['diffs'] else np.nan,
            len(line_data[l]['doses'])))


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 4: Dose vs Intra-plate Differential (gain-immune)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_differential(merged):
    """Scatter: cumulative body dose vs NdFeB-SmCo intra-plate differential."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Separate saturated vs unsaturated
    for m in merged:
        diff = m['intra_plate_diff']
        if np.isnan(diff):
            continue
        dose = m['cum_body_mrem'] * MREM_TO_SV
        is_lb = m['is_lower_bound']
        region = m['region']

        # Color by region type
        if 'Arc' in region:
            c = '#CC4444'
        elif 'Linac' in region:
            c = '#4444CC'
        else:
            c = '#888888'

        marker = 'o'
        ec = 'black' if is_lb else c
        ax.scatter(dose, diff, c=c, marker=marker, edgecolors=ec,
                   s=70, linewidths=1.2, zorder=3, alpha=0.85)

        if is_lb:
            ax.annotate('', xy=(dose * 1.5, diff), xytext=(dose, diff),
                        arrowprops=dict(arrowstyle='->', color='black', lw=1.2))

        ax.annotate('Y-%d' % m['plate'], (dose, diff),
                    fontsize=7, ha='left', va='bottom',
                    xytext=(3, 2), textcoords='offset points', color='gray')

    # Mean differential line
    diffs = [m['intra_plate_diff'] for m in merged if not np.isnan(m['intra_plate_diff'])]
    if diffs:
        mean_diff = np.mean(diffs)
        sem_diff = np.std(diffs, ddof=1) / np.sqrt(len(diffs))
        ax.axhline(mean_diff, color='green', linewidth=1.5, linestyle='--',
                   label='Mean = %.3f%% ± %.3f%%' % (mean_diff, sem_diff))
        ax.axhspan(mean_diff - sem_diff, mean_diff + sem_diff,
                   color='green', alpha=0.1)

    ax.axhline(0, color='gray', linewidth=0.5)
    ax.set_xscale('log')
    ax.set_xlabel('Cumulative body dose equivalent (Sv)', fontsize=11)
    ax.set_ylabel('NdFeB − SmCo intra-plate differential (%)', fontsize=11)
    ax.set_title('Gain-Immune Differential vs Dose', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # Correlation
    valid = [(m['cum_body_mrem'] * MREM_TO_SV, m['intra_plate_diff']) for m in merged
             if not np.isnan(m['intra_plate_diff'])]
    if len(valid) >= 4:
        xv, yv = zip(*valid)
        r_s, p_s = stats.spearmanr(np.log10(np.array(xv)), np.array(yv))
        ax.text(0.03, 0.03, 'All plates: ρ=%.2f (p=%.3f, N=%d)' % (r_s, p_s, len(valid)),
                transform=ax.transAxes, fontsize=10, va='bottom',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='gray', alpha=0.8))

        # Also unsaturated only
        valid_u = [(m['cum_body_mrem'] * MREM_TO_SV, m['intra_plate_diff']) for m in merged
                   if not np.isnan(m['intra_plate_diff']) and not m['is_lower_bound']]
        if len(valid_u) >= 4:
            xv2, yv2 = zip(*valid_u)
            r_s2, p_s2 = stats.spearmanr(np.log10(np.array(xv2)), np.array(yv2))
            ax.text(0.03, 0.10, 'Unsaturated: ρ=%.2f (p=%.3f, N=%d)' %
                    (r_s2, p_s2, len(valid_u)),
                    transform=ax.transAxes, fontsize=10, va='bottom',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='gray', alpha=0.8))

    # Region legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#CC4444',
               markersize=8, label='Arc'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#4444CC',
               markersize=8, label='Linac'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#888888',
               markersize=8, label='Labyrinth'),
    ]
    ax.legend(handles=legend_elements + ax.get_legend_handles_labels()[0][:1],
              labels=['Arc', 'Linac', 'Labyrinth',
                      'Mean = %.3f%%' % mean_diff if diffs else ''],
              loc='upper right', fontsize=9)

    fig.tight_layout()
    save(fig, 'dose_vs_differential.png')


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 5: Timeline Overlay (representative plates)
# ═══════════════════════════════════════════════════════════════════════════════

def plot_timeline_overlay(merged, results, dose_timeline):
    """Dual panel: degradation + dose time series for representative plates."""
    # Pick representative plates: high/med/low dose, mix of saturated/not
    # Sort merged by dose, pick 6 spread across range
    sorted_m = sorted(merged, key=lambda x: x['cum_body_mrem'])

    # Pick: lowest dose, labyrinth, mid-low linac, mid arc, high arc, highest saturated
    candidates = []
    # Lowest dose (unsaturated)
    for m in sorted_m:
        if not m['is_lower_bound']:
            candidates.append(m)
            break
    # Labyrinth
    for m in sorted_m:
        if m['region'] == 'Labyrinth' and m not in candidates:
            candidates.append(m)
            break
    # Mid-range linac (unsaturated)
    linac_unsat = [m for m in sorted_m if 'Linac' in m['region'] and not m['is_lower_bound']
                   and m not in candidates]
    if linac_unsat:
        candidates.append(linac_unsat[len(linac_unsat)//2])
    # Mid-range arc (unsaturated)
    arc_unsat = [m for m in sorted_m if 'Arc' in m['region'] and not m['is_lower_bound']
                 and m not in candidates]
    if arc_unsat:
        candidates.append(arc_unsat[len(arc_unsat)//2])
    # High arc (unsaturated)
    for m in reversed(sorted_m):
        if 'Arc' in m['region'] and not m['is_lower_bound'] and m not in candidates:
            candidates.append(m)
            break
    # Highest saturated
    for m in reversed(sorted_m):
        if m['is_lower_bound'] and m not in candidates:
            candidates.append(m)
            break

    if len(candidates) < 3:
        print("  Too few candidate plates for timeline overlay")
        return

    # Build degradation time series lookup from results
    clean = [r for r in results if not r['is_outlier']]
    plate_deg_ts = defaultdict(list)
    for r in clean:
        for dt, pct in r['date_pcts']:
            plate_deg_ts[r['plate']].append((dt, pct, r['material']))

    fig, (ax_deg, ax_dose) = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    fig.suptitle('Dose & Degradation Time Series — Representative Plates',
                 fontsize=13, fontweight='bold')

    colors_cycle = ['#CC3333', '#3366CC', '#FF8800', '#228B22', '#9933CC', '#666666']

    for i, m in enumerate(candidates):
        pnum = m['plate']
        dose_sv = m['cum_body_mrem'] * MREM_TO_SV
        label = 'Y-%d (%s, %s)' % (pnum, m['region'],
                                     '≥%.1f Sv' % dose_sv
                                     if m['is_lower_bound']
                                     else '%.1f Sv' % dose_sv)
        color = colors_cycle[i % len(colors_cycle)]

        # Degradation: average across materials for this plate per date
        ts = plate_deg_ts.get(pnum, [])
        if ts:
            date_vals = defaultdict(list)
            for dt, pct, mat in ts:
                date_vals[dt].append(pct)
            dates_sorted = sorted(date_vals.keys())
            means = [np.mean(date_vals[d]) for d in dates_sorted]
            ax_deg.plot(dates_sorted, means, 'o-', color=color, label=label,
                        markersize=5, linewidth=1.5)

        # Dose timeline
        dose_key = 'Y-%d' % pnum
        dtl = dose_timeline.get(dose_key, [])
        if dtl:
            # Filter out NO_MATCH with zero dose at end
            dtl_plot = [d for d in dtl if d['cum_body'] > 0 or d['status'] != 'NO_MATCH']
            if dtl_plot:
                dates_d = [d['date'] for d in dtl_plot]
                cum_d = [d['cum_body'] * MREM_TO_SV for d in dtl_plot]
                ax_dose.plot(dates_d, cum_d, 'o-', color=color, markersize=5,
                             linewidth=1.5, label=label)
                # Mark lower-bound points
                for d in dtl_plot:
                    if d['is_lower_bound']:
                        ax_dose.scatter([d['date']], [d['cum_body']], marker='v',
                                        color=color, s=30, zorder=4)

    ax_deg.axhspan(-GAIN_SYST, GAIN_SYST, color='gray', alpha=0.08)
    ax_deg.axhline(0, color='gray', linewidth=0.5)
    ax_deg.set_ylabel('Mean % change (all materials)', fontsize=11)
    ax_deg.legend(fontsize=8, loc='lower left')
    ax_deg.grid(True, alpha=0.3)
    ax_deg.set_title('Helmholtz Degradation', fontsize=11)

    ax_dose.set_ylabel('Cumulative body dose equivalent (Sv)', fontsize=11)
    ax_dose.set_xlabel('Date', fontsize=11)
    ax_dose.set_yscale('log')
    ax_dose.legend(fontsize=8, loc='upper left')
    ax_dose.grid(True, alpha=0.3)
    ax_dose.set_title('OSL Area Dosimetry', fontsize=11)
    ax_dose.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax_dose.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    fig.autofmt_xdate()

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save(fig, 'dose_timeline_overlay.png')


# ═══════════════════════════════════════════════════════════════════════════════
# Plot 6: Radiation Type Breakdown — NdFeB degradation vs each dose component
# ═══════════════════════════════════════════════════════════════════════════════

# Dose types to analyze. photon_mrem can be 0 when all badges saturated,
# so we track which are "clean" (unsaturated + photon > 0).
DOSE_TYPES = [
    ('cum_photon_mrem', 'Photon', '#CC6600'),
    ('cum_neutron_mrem', 'Neutron (total)', '#006699'),
    ('cum_nf_mrem', 'Fast neutron', '#0088BB'),
    ('cum_nt_mrem', 'Thermal neutron', '#44AACC'),
    ('cum_beta_mrem', 'Beta', '#999900'),
    ('cum_body_mrem', 'Total body', '#666666'),
]


def print_per_type_correlations(merged):
    """Print correlations broken down by radiation type."""
    print("\n" + "="*70)
    print("CORRELATIONS BY RADIATION TYPE")
    print("="*70)

    for dose_col, dose_label, _ in DOSE_TYPES:
        # For photon: skip plates where photon=0 (saturated OSL, no photon reading)
        if dose_col == 'cum_photon_mrem':
            subset = [m for m in merged if m[dose_col] > 0]
            note = "(excluding photon-saturated)"
        elif dose_col == 'cum_beta_mrem':
            subset = [m for m in merged if m[dose_col] > 0]
            note = "(plates with beta > 0 only)"
        else:
            subset = list(merged)
            note = ""

        print("\n--- %s dose %s (N=%d) ---" % (dose_label, note, len(subset)))
        if len(subset) < 4:
            print("  Too few plates")
            continue

        doses = np.array([m[dose_col] for m in subset])
        # Skip if all zeros
        if doses.max() == 0:
            print("  All zero — skipping")
            continue
        log_doses = np.log10(np.clip(doses, 1, None))

        for deg_col, deg_label in [('ndfeb_mean_pct', 'NdFeB mean'),
                                    ('smco_mean_pct', 'SmCo mean'),
                                    ('intra_plate_diff', 'NdFeB−SmCo diff')]:
            vals = np.array([m[deg_col] for m in subset])
            mask = ~np.isnan(vals)
            if mask.sum() < 4:
                continue
            x, y = log_doses[mask], vals[mask]
            r_p, p_p = stats.pearsonr(x, y)
            r_s, p_s = stats.spearmanr(x, y)
            sig = '*' if p_s < 0.05 else ' '
            print("  %-18s  Pearson r=%+.3f (p=%.3f)  Spearman ρ=%+.3f (p=%.3f) %s" %
                  (deg_label, r_p, p_p, r_s, p_s, sig))


def plot_radiation_type_scatter(merged):
    """6-panel scatter: one per radiation dose type, NdFeB degradation on y-axis."""
    # Filter to types that have data
    active_types = []
    for dose_col, label, color in DOSE_TYPES:
        vals = [m[dose_col] for m in merged]
        if max(vals) > 0:
            active_types.append((dose_col, label, color))

    n = len(active_types)
    ncols = 3
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(16, 5 * nrows))
    if nrows == 1:
        axes = axes.reshape(1, -1)
    fig.suptitle('NdFeB Degradation vs Dose by Radiation Type',
                 fontsize=14, fontweight='bold', y=0.99)

    region_markers = {
        'SE Arc': 'o', 'NE Arc': 'o', 'NW Arc': 'o', 'SW Arc': 'o',
        'North Linac': 's', 'South Linac': 's',
        'Labyrinth': '^',
    }

    for idx, (dose_col, dose_label, dose_color) in enumerate(active_types):
        ax = axes[idx // ncols, idx % ncols]
        conv_factor, conv_unit = DOSE_PLOT_CONV.get(dose_col, (MREM_TO_MSV, 'mSv'))

        ax.axhspan(-GAIN_SYST, GAIN_SYST, color='gray', alpha=0.10, zorder=0)
        ax.axhline(0, color='gray', linewidth=0.5, zorder=1)

        # For photon, skip plates with 0 (saturated)
        skip_zero = dose_col in ('cum_photon_mrem', 'cum_beta_mrem')

        xs_all, ys_all = [], []
        xs_clean, ys_clean = [], []  # unsaturated only

        for m in merged:
            nd = m['ndfeb_mean_pct']
            if np.isnan(nd):
                continue
            dose_val = m[dose_col] * conv_factor
            if skip_zero and m[dose_col] <= 0:
                continue
            if m[dose_col] <= 0:
                continue  # can't log(0)

            marker = region_markers.get(m['region'], 'o')
            ec = 'black' if m['is_lower_bound'] else dose_color
            ax.scatter(dose_val, nd, marker=marker, c=dose_color,
                       edgecolors=ec, s=50, linewidths=1.0, zorder=3, alpha=0.8)

            if m['is_lower_bound']:
                ax.annotate('', xy=(dose_val * 1.4, nd), xytext=(dose_val, nd),
                            arrowprops=dict(arrowstyle='->', color='black', lw=1.0))

            xs_all.append(dose_val)
            ys_all.append(nd)
            if not m['is_lower_bound']:
                xs_clean.append(dose_val)
                ys_clean.append(nd)

        # Correlation stats
        lines_text = []
        if len(xs_all) >= 4:
            r_s, p_s = stats.spearmanr(np.log10(xs_all), ys_all)
            lines_text.append('All: ρ=%.2f (p=%.3f, N=%d)' % (r_s, p_s, len(xs_all)))
        if len(xs_clean) >= 4:
            r_s2, p_s2 = stats.spearmanr(np.log10(xs_clean), ys_clean)
            lines_text.append('Unsat: ρ=%.2f (p=%.3f, N=%d)' % (r_s2, p_s2, len(xs_clean)))
        if lines_text:
            ax.text(0.03, 0.97, '\n'.join(lines_text),
                    transform=ax.transAxes, fontsize=8, va='top',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='gray', alpha=0.8))

        ax.set_xscale('log')
        ax.set_title(dose_label, fontsize=12, fontweight='bold', color=dose_color)
        ax.set_xlabel('%s dose equivalent (%s)' % (dose_label, conv_unit), fontsize=9)
        ax.set_ylabel('NdFeB mean % change', fontsize=9)
        ax.grid(True, alpha=0.3)

    # Hide unused axes
    for idx in range(n, nrows * ncols):
        axes[idx // ncols, idx % ncols].set_visible(False)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save(fig, 'dose_by_radiation_type_ndfeb.png')


def plot_radiation_type_differential(merged):
    """6-panel scatter: each radiation type vs gain-immune NdFeB-SmCo differential."""
    active_types = []
    for dose_col, label, color in DOSE_TYPES:
        vals = [m[dose_col] for m in merged]
        if max(vals) > 0:
            active_types.append((dose_col, label, color))

    n = len(active_types)
    ncols = 3
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(16, 5 * nrows))
    if nrows == 1:
        axes = axes.reshape(1, -1)
    fig.suptitle('Intra-Plate Differential (NdFeB−SmCo) vs Dose by Radiation Type',
                 fontsize=14, fontweight='bold', y=0.99)

    for idx, (dose_col, dose_label, dose_color) in enumerate(active_types):
        ax = axes[idx // ncols, idx % ncols]
        conv_factor, conv_unit = DOSE_PLOT_CONV.get(dose_col, (MREM_TO_MSV, 'mSv'))
        ax.axhline(0, color='gray', linewidth=0.5, zorder=1)

        skip_zero = dose_col in ('cum_photon_mrem', 'cum_beta_mrem')

        xs_all, ys_all = [], []
        xs_clean, ys_clean = [], []

        for m in merged:
            diff = m['intra_plate_diff']
            if np.isnan(diff):
                continue
            dose_val = m[dose_col] * conv_factor
            if skip_zero and m[dose_col] <= 0:
                continue
            if m[dose_col] <= 0:
                continue

            # Color by region
            if 'Arc' in m['region']:
                c = '#CC4444'
            elif 'Linac' in m['region']:
                c = '#4444CC'
            else:
                c = '#888888'

            ec = 'black' if m['is_lower_bound'] else c
            ax.scatter(dose_val, diff, c=c, edgecolors=ec,
                       s=50, linewidths=1.0, zorder=3, alpha=0.8)

            if m['is_lower_bound']:
                ax.annotate('', xy=(dose_val * 1.4, diff), xytext=(dose_val, diff),
                            arrowprops=dict(arrowstyle='->', color='black', lw=1.0))

            ax.annotate('Y-%d' % m['plate'], (dose_val, diff),
                        fontsize=6, ha='left', va='bottom',
                        xytext=(2, 1), textcoords='offset points', color='gray')

            xs_all.append(dose_val)
            ys_all.append(diff)
            if not m['is_lower_bound']:
                xs_clean.append(dose_val)
                ys_clean.append(diff)

        # Mean diff line
        diffs_all = [m['intra_plate_diff'] for m in merged
                     if not np.isnan(m['intra_plate_diff'])]
        if diffs_all:
            ax.axhline(np.mean(diffs_all), color='green', linewidth=1, linestyle='--',
                       alpha=0.7, label='Mean %.3f%%' % np.mean(diffs_all))

        # Correlation
        lines_text = []
        if len(xs_all) >= 4:
            r_s, p_s = stats.spearmanr(np.log10(xs_all), ys_all)
            lines_text.append('All: ρ=%.2f (p=%.3f, N=%d)' % (r_s, p_s, len(xs_all)))
        if len(xs_clean) >= 4:
            r_s2, p_s2 = stats.spearmanr(np.log10(xs_clean), ys_clean)
            lines_text.append('Unsat: ρ=%.2f (p=%.3f, N=%d)' % (r_s2, p_s2, len(xs_clean)))
        if lines_text:
            ax.text(0.03, 0.97, '\n'.join(lines_text),
                    transform=ax.transAxes, fontsize=8, va='top',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor='gray', alpha=0.8))

        ax.set_xscale('log')
        ax.set_title(dose_label, fontsize=12, fontweight='bold', color=dose_color)
        ax.set_xlabel('%s dose equivalent (%s)' % (dose_label, conv_unit), fontsize=9)
        ax.set_ylabel('NdFeB−SmCo diff (%)', fontsize=9)
        ax.grid(True, alpha=0.3)

    for idx in range(n, nrows * ncols):
        axes[idx // ncols, idx % ncols].set_visible(False)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save(fig, 'dose_by_radiation_type_differential.png')


def plot_regional_dose_breakdown(merged):
    """Stacked bar: dose composition (photon/neutron/beta) by region."""
    regions = ['Arcs (all)', 'North Linac', 'South Linac', 'Labyrinth']
    combined = defaultdict(lambda: {'photon': [], 'neutron': [], 'beta': [],
                                     'nf': [], 'nt': [], 'ndfeb': []})
    for m in merged:
        key = 'Arcs (all)' if 'Arc' in m['region'] else m['region']
        # For photon: use 0 when saturated (photon is unknown)
        combined[key]['photon'].append(m['cum_photon_mrem'])
        combined[key]['neutron'].append(m['cum_neutron_mrem'])
        combined[key]['beta'].append(m['cum_beta_mrem'])
        combined[key]['nf'].append(m['cum_nf_mrem'])
        combined[key]['nt'].append(m['cum_nt_mrem'])
        if not np.isnan(m['ndfeb_mean_pct']):
            combined[key]['ndfeb'].append(m['ndfeb_mean_pct'])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6),
                                    gridspec_kw={'width_ratios': [2, 1]})
    fig.suptitle('Dose Composition by Region and Neutron Breakdown',
                 fontsize=13, fontweight='bold')

    x = np.arange(len(regions))
    width = 0.55

    # Left panel: stacked photon + neutron + beta
    photon_means = [np.mean(combined[r]['photon']) * MREM_TO_MSV for r in regions]
    neutron_means = [np.mean(combined[r]['neutron']) * MREM_TO_MSV for r in regions]
    beta_means = [np.mean(combined[r]['beta']) * MREM_TO_MSV for r in regions]

    ax1.bar(x, photon_means, width, label='Photon (OSL)', color='#CC6600',
            edgecolor='#884400', linewidth=0.8)
    ax1.bar(x, neutron_means, width, bottom=photon_means,
            label='Neutron (CR-39)', color='#006699',
            edgecolor='#003344', linewidth=0.8)
    bottoms2 = [p + n for p, n in zip(photon_means, neutron_means)]
    ax1.bar(x, beta_means, width, bottom=bottoms2,
            label='Beta', color='#999900',
            edgecolor='#666600', linewidth=0.8)

    # Annotate N_saturated
    for i, r in enumerate(regions):
        n_sat = sum(1 for m in merged
                    if m['is_lower_bound'] and
                    (('Arc' in m['region'] and r == 'Arcs (all)') or m['region'] == r))
        n_tot = len(combined[r]['photon'])
        if n_sat > 0:
            total = photon_means[i] + neutron_means[i] + beta_means[i]
            ax1.text(i, total, '%d/%d\nsat' % (n_sat, n_tot),
                     ha='center', va='bottom', fontsize=8, color='#884400',
                     fontweight='bold')

    ax1.set_xticks(x)
    ax1.set_xticklabels(regions, fontsize=10)
    ax1.set_ylabel('Mean cumulative dose equivalent (mSv)', fontsize=11)
    ax1.legend(fontsize=9)
    ax1.grid(True, axis='y', alpha=0.3)
    ax1.set_title('Dose Composition', fontsize=11)

    # Right panel: neutron breakdown (fast vs thermal) — always readable
    nf_means = [np.mean(combined[r]['nf']) * MREM_TO_MSV for r in regions]
    nt_means = [np.mean(combined[r]['nt']) * MREM_TO_MSV for r in regions]

    ax2.bar(x, nf_means, width, label='Fast neutron', color='#0088BB',
            edgecolor='#005577', linewidth=0.8)
    ax2.bar(x, nt_means, width, bottom=nf_means,
            label='Thermal neutron', color='#44AACC',
            edgecolor='#227799', linewidth=0.8)

    # Overlay NdFeB degradation on twin axis
    ax2r = ax2.twinx()
    nd_means = [np.mean(combined[r]['ndfeb']) if combined[r]['ndfeb'] else 0 for r in regions]
    ax2r.plot(x, nd_means, 's-', color='#CC3333', markersize=10, linewidth=2,
              label='NdFeB % change', zorder=5)
    ax2r.axhline(0, color='gray', linewidth=0.5)
    ax2r.set_ylabel('NdFeB mean % change', fontsize=10, color='#CC3333')

    ax2.set_xticks(x)
    ax2.set_xticklabels(regions, fontsize=9)
    ax2.set_ylabel('Mean neutron dose equivalent (mSv)', fontsize=10)
    ax2.set_title('Neutron Breakdown + NdFeB', fontsize=11)

    # Combined legend
    h1, l1 = ax2.get_legend_handles_labels()
    h2, l2 = ax2r.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, fontsize=8, loc='upper left')
    ax2.grid(True, axis='y', alpha=0.3)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, 'dose_regional_composition.png')

    # Print table
    print("\n--- Regional dose composition ---")
    print("  All values: dose equiv (mrem) → absorbed dose (Gy) using Q factors:")
    print("  Photon Q=%.0f, Beta Q=%.0f, Fast n Q=%.0f, Thermal n Q=%.1f" %
          (Q_PHOTON, Q_BETA, Q_FAST_N, Q_THERM_N))
    print("%-16s %16s %16s %16s %8s" % (
        'Region', 'Photon (Gy)', 'Fast n (mGy)', 'Therm n (mGy)', 'NdFeB%'))
    for r in regions:
        d = combined[r]
        ph = np.mean(d['photon'])
        nf = np.mean(d['nf'])
        nt = np.mean(d['nt'])
        nd = np.mean(d['ndfeb']) if d['ndfeb'] else np.nan
        ph_gy = ph * MREM_TO_GY_PHOTON
        nf_gy = nf * MREM_TO_GY_FAST_N
        nt_gy = nt * MREM_TO_GY_THERM_N
        print("%-16s %8s / %5.1fGy %8s / %4.1fmGy %8s / %4.2fmGy %8.3f" % (
            r,
            '{:,.0f}'.format(ph), ph_gy,
            '{:,.0f}'.format(nf), nf_gy * 1000,
            '{:,.0f}'.format(nt), nt_gy * 1000,
            nd,
        ))
    # Also show total absorbed dose estimate
    print("\n  Estimated total absorbed dose (Gy) = photon + fast_n + therm_n + beta:")
    for r in regions:
        d = combined[r]
        ph_gy = np.mean(d['photon']) * MREM_TO_GY_PHOTON
        nf_gy = np.mean(d['nf']) * MREM_TO_GY_FAST_N
        nt_gy = np.mean(d['nt']) * MREM_TO_GY_THERM_N
        bt_gy = np.mean(d['beta']) * MREM_TO_GY_BETA
        total_gy = ph_gy + nf_gy + nt_gy + bt_gy
        print("  %-16s  %.2f Gy  (photon %.2f + fast_n %.4f + therm_n %.5f + beta %.3f)" %
              (r, total_gy, ph_gy, nf_gy, nt_gy, bt_gy))


# ═══════════════════════════════════════════════════════════════════════════════
# Verification checks
# ═══════════════════════════════════════════════════════════════════════════════

def verify(merged):
    """Run verification checks."""
    print("\n" + "="*70)
    print("VERIFICATION CHECKS")
    print("="*70)

    # Check merge count
    print("\n1. Merge count: %d Y-plates" % len(merged))

    # Check saturated NDX plates
    ndx_plates = [16, 17, 22]
    print("\n2. NDX linac plates (should be saturated + high degradation):")
    for pnum in ndx_plates:
        m = next((x for x in merged if x['plate'] == pnum), None)
        if m:
            print("   Y-%d: dose=%s mrem (sat=%s), NdFeB=%.3f%%" % (
                pnum, '{:,.0f}'.format(m['cum_body_mrem']),
                m['is_lower_bound'],
                m['ndfeb_mean_pct'] if not np.isnan(m['ndfeb_mean_pct']) else float('nan')))

    # Arc vs linac dose ranking
    arc_doses = [m['cum_body_mrem'] for m in merged if 'Arc' in m['region']]
    linac_doses = [m['cum_body_mrem'] for m in merged if 'Linac' in m['region']]
    print("\n3. Dose ranking (arc vs linac):")
    print("   Arc mean:   %s mrem = %.1f Sv (N=%d)" % (
        '{:,.0f}'.format(np.mean(arc_doses)), np.mean(arc_doses) * MREM_TO_SV, len(arc_doses)))
    print("   Linac mean: %s mrem = %.1f Sv (N=%d)" % (
        '{:,.0f}'.format(np.mean(linac_doses)), np.mean(linac_doses) * MREM_TO_SV, len(linac_doses)))
    print("   Arc/Linac ratio: %.1f" % (np.mean(arc_doses) / np.mean(linac_doses))
          if np.mean(linac_doses) > 0 else "   Division by zero")

    arc_nd = [m['ndfeb_mean_pct'] for m in merged
              if 'Arc' in m['region'] and not np.isnan(m['ndfeb_mean_pct'])]
    linac_nd = [m['ndfeb_mean_pct'] for m in merged
                if 'Linac' in m['region'] and not np.isnan(m['ndfeb_mean_pct'])]
    print("   Arc NdFeB mean:   %.3f%%" % np.mean(arc_nd))
    print("   Linac NdFeB mean: %.3f%%" % np.mean(linac_nd))
    print("   Both higher dose AND more degradation in arcs? %s" %
          ('YES' if np.mean(arc_doses) > np.mean(linac_doses) and
           np.mean(arc_nd) < np.mean(linac_nd) else 'CHECK'))


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    global GAIN_SYST
    print("Loading degradation data...")
    results, helm_raw, temp_final, y_materials = load_all()
    clean = [r for r in results if not r['is_outlier']]
    gain_result = get_gain_syst(helm_raw)
    gain_syst = gain_result[0]
    GAIN_SYST = gain_syst  # update module-level for all plot functions
    intra_diffs, intra_details = compute_intra_plate_diffs(clean)
    print("  %d clean Y-plate samples, %d intra-plate diffs" %
          (len(clean), len(intra_diffs)))
    print("  Gain systematic (cleaned): ±%.4f%%" % gain_syst)
    gain_syst_raw = getattr(gain_result, 'gain_syst_raw', None)
    if gain_syst_raw is not None:
        print("  Gain systematic (uncleaned): ±%.4f%%" % gain_syst_raw)

    # Load H-plate degradation
    print("\nLoading H-plate degradation...")
    y_mats, pair_arrangements = load_materials()
    temp_lookup = build_temperature_lookup()
    h_results, h_excluded = compute_h_plate_degradation(pair_arrangements, temp_lookup)
    h_clean = [r for r in h_results if not r['is_outlier']]
    print("  %d H-plate pair assemblies (%d clean, %d outliers, %d excluded)" %
          (len(h_results), len(h_clean), len(h_results) - len(h_clean), len(h_excluded)))

    # Load A-sample degradation
    print("\nLoading A-sample degradation...")
    a_results = load_a_sample_helmholtz(temp_lookup)
    a_clean = [r for r in a_results if not r['is_outlier']]
    a_tc = [r for r in a_clean if r['temp_corrected']]
    print("  %d A-samples (%d clean, %d temp-corrected)" %
          (len(a_results), len(a_clean), len(a_tc)))

    print("\nLoading dose data...")
    dose_cum = load_dose_cumulative()
    dose_tl = load_dose_timeline()
    y_doses = {k: v for k, v in dose_cum.items() if v['plate_type'] == 'Y'}
    print("  %d Y-plate cumulative dose records" % len(y_doses))
    print("  %d total plates in dose data" % len(dose_cum))
    print("  %d plates in timeline" % len(dose_tl))

    # --- Y-plate merge (existing) ---
    print("\nMerging Y-plates...")
    merged = merge_data(results, intra_details, dose_cum)
    print("  Merged %d Y-plates" % len(merged))

    write_csv(merged)
    print_summary_table(merged)
    print_correlations(merged)
    print_per_type_correlations(merged)
    verify(merged)

    # --- H-plate merge ---
    print("\nMerging H-plates...")
    h_merged = merge_h_plate_data(h_results, dose_cum)
    print("  Merged %d H-plate pair assemblies with dose data" % len(h_merged))
    print_h_plate_summary(h_merged)

    # --- A-sample merge ---
    print("\nMerging A-samples...")
    a_merged = merge_a_sample_data(a_results, dose_cum)
    print("  Merged %d A-samples with dose data" % len(a_merged))
    print_a_sample_summary(a_merged)

    # --- Combined Y+H+A comparison ---
    print("\n" + "="*70)
    print("COMBINED Y + H + A NdFeB DOSE-DEGRADATION COMPARISON")
    print("="*70)
    for label, data, mat_key in [
        ('Y-plate NdFeB (intra-plate)',
         [(m['cum_body_mrem'], m['ndfeb_mean_pct'], m['is_lower_bound'])
          for m in merged if not np.isnan(m.get('ndfeb_mean_pct', np.nan))],
         None),
        ('H-plate NdFeB (pair assembly)',
         [(m['cum_body_mrem'], m['pct_change'], m['is_lower_bound'])
          for m in h_merged if m['material'] == 'NdFeB'],
         None),
        ('A-sample NdFeB (temp-corrected)',
         [(m['cum_body_mrem'], m['pct_change'], m['is_lower_bound'])
          for m in a_merged if m['material'] == 'NdFeB' and m['temp_corrected']],
         None),
    ]:
        if not data:
            print("  %s: no data" % label)
            continue
        doses, pcts, lbs = zip(*data)
        pcts = np.array(pcts)
        mean = np.mean(pcts)
        sem = np.std(pcts, ddof=1) / np.sqrt(len(pcts)) if len(pcts) > 1 else 0
        # Correlation
        log_d = np.log10(np.clip(doses, 1, None))
        r_s, p_s = stats.spearmanr(log_d, pcts)
        print("  %s (N=%d):" % (label, len(pcts)))
        print("    Mean: %.3f%% ± %.3f%%  |  Spearman ρ=%.3f (p=%.3f)" %
              (mean, sem, r_s, p_s))

    # --- Plots ---
    print("\nGenerating plots...")
    plot_scatter(merged)
    plot_by_region(merged)
    plot_line_position(merged)
    plot_differential(merged)
    plot_timeline_overlay(merged, results, dose_tl)
    plot_radiation_type_scatter(merged)
    plot_radiation_type_differential(merged)
    plot_regional_dose_breakdown(merged)
    plot_h_a_dose_scatter(h_merged, a_merged, merged)

    print("\nDone! All outputs in: %s" % DOSE_DIR)


if __name__ == '__main__':
    main()
