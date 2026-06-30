#!/usr/bin/env python3
"""Generate IPAC26 Figure 4: dose correlation (gamma null vs neutron signal)."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import csv, os

# --- load data ---
csv_path = os.path.join(os.path.dirname(__file__),
                        '..', 'Cleanup_Claude', 'Rod_Dosimetry',
                        'rod_dose_degradation.csv')
rows = []
with open(csv_path) as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

gamma_gy    = np.array([float(r['ai_photon_gy']) for r in rows])
neutron_rem = np.array([float(r['ai_neutron_rem']) for r in rows])
neutron_sv  = neutron_rem * 0.01  # rem -> Sv
diff        = np.array([float(r['intra_plate_diff']) for r in rows])
diff_err    = np.array([float(r['sigma_diff_pct']) for r in rows])
gamma_err   = np.array([float(r['ai_sigma_photon_gy']) for r in rows])
neutron_err = np.array([float(r['ai_sigma_neutron_rem']) for r in rows]) * 0.01
regions     = [r['region'] for r in rows]

# region colors
region_colors = {
    'NE Arc': '#e41a1c', 'NW Arc': '#984ea3', 'SE Arc': '#ff7f00',
    'SW Arc': '#377eb8', 'North Linac': '#4daf4a', 'South Linac': '#a65628',
    'Labyrinth': '#999999'
}
region_markers = {
    'NE Arc': 'D', 'NW Arc': 's', 'SE Arc': 'o',
    'SW Arc': '^', 'North Linac': 'v', 'South Linac': 'p',
    'Labyrinth': '*'
}

# assign 10% for plates with zero sigma
gamma_err_plot = np.where(gamma_err == 0, gamma_gy * 0.10, gamma_err)
neutron_err_plot = np.where(neutron_err == 0, neutron_sv * 0.10, neutron_err)

# --- correlations ---
rho_g, p_g = stats.spearmanr(gamma_gy, diff)
rho_n, p_n = stats.spearmanr(neutron_sv, diff)

# --- plot ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(3.4, 3.6), sharex=False, sharey=True)

# Short region labels for legend
region_short = {
    'NE Arc': 'NE Arc', 'NW Arc': 'NW Arc', 'SE Arc': 'SE Arc',
    'SW Arc': 'SW Arc', 'North Linac': 'N Linac', 'South Linac': 'S Linac',
    'Labyrinth': 'Labyrinth'
}

panels = [
    (ax1, gamma_gy, rho_g, p_g, 'Gamma Dose (Gy)', '(a)'),
    (ax2, neutron_sv, rho_n, p_n, 'Neutron Dose (Sv)', '(b)'),
]

for ax, xdata, rho, p, xlabel, panel_label in panels:
    ax.axhline(0, color='k', lw=0.5, ls='-', alpha=0.3)
    ax.axhline(np.mean(diff), color='navy', lw=0.7, ls='--', alpha=0.4)

    plotted_regions = set()
    for i in range(len(xdata)):
        reg = regions[i]
        c = region_colors.get(reg, 'gray')
        m = region_markers.get(reg, 'o')
        lbl = region_short[reg] if reg not in plotted_regions else None
        plotted_regions.add(reg)
        ax.scatter(xdata[i], diff[i], marker=m, c=c, s=22, zorder=3,
                   edgecolors='k', linewidths=0.2, label=lbl)

    ax.set_xscale('log')
    ax.set_xlabel(xlabel, fontsize=7.5)

    # stats box
    pstr = '%.2f' % p if p >= 0.01 else '%.1e' % p
    sig = 'n.s.' if p > 0.05 else 'sig.'
    ax.text(0.03, 0.05,
            '%s  $\\rho$ = %.2f, $p$ = %s (%s)' % (panel_label, rho, pstr, sig),
            transform=ax.transAxes, fontsize=6.5,
            verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='wheat', alpha=0.7))

ax1.set_ylabel('NdFeB$-$SmCo\nDifferential (%)', fontsize=7.5)
ax2.set_ylabel('NdFeB$-$SmCo\nDifferential (%)', fontsize=7.5)
ax1.tick_params(labelsize=6.5)
ax2.tick_params(labelsize=6.5)

# legend on top panel
ax1.legend(fontsize=5, loc='lower right', framealpha=0.7,
           ncol=2, handletextpad=0.2, columnspacing=0.4,
           markerscale=0.7, borderpad=0.3)

fig.tight_layout(h_pad=0.8)

out = os.path.join(os.path.dirname(__file__), 'IPAC26_f4.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
print('Saved %s' % out)
print('Gamma:   rho=%.3f, p=%.4f' % (rho_g, p_g))
print('Neutron: rho=%.3f, p=%.4f' % (rho_n, p_n))
