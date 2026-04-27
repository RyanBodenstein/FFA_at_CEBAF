#!/usr/bin/env python3
"""Generate IPAC26 Figure 2: two-panel differential vs gamma and neutron dose."""
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

gamma_gy   = np.array([float(r['ai_photon_gy']) for r in rows])
neutron_rem = np.array([float(r['ai_neutron_rem']) for r in rows])
neutron    = neutron_rem * 0.01  # rem -> Sv (1 rem = 0.01 Sv)
diff       = np.array([float(r['intra_plate_diff']) for r in rows])
diff_err   = np.array([float(r['sigma_diff_pct']) for r in rows])
gamma_err  = np.array([float(r['ai_sigma_photon_gy']) for r in rows])
neutron_err = np.array([float(r['ai_sigma_neutron_rem']) for r in rows]) * 0.01  # rem -> Sv
regions    = [r['region'] for r in rows]
labels     = [r['plate_label'] for r in rows]

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

# assign 10% for plates with zero sigma (OSL-matched)
gamma_err_plot = np.where(gamma_err == 0, gamma_gy * 0.10, gamma_err)
neutron_err_plot = np.where(neutron_err == 0, neutron * 0.10, neutron_err)  # already in Sv

# --- correlations ---
# gamma
rho_g, p_g = stats.spearmanr(gamma_gy, diff)
# neutron
rho_n, p_n = stats.spearmanr(neutron, diff)

# --- plot ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)

for ax, xdata, xerr, rho, p, xlabel, title in [
    (ax1, gamma_gy, gamma_err_plot, rho_g, p_g, 'Gamma Dose (Gy)', 'vs. Gamma Dose'),
    (ax2, neutron, neutron_err_plot, rho_n, p_n, 'Neutron Dose (Sv)', 'vs. Neutron Dose'),
]:
    # zero line
    ax.axhline(0, color='k', lw=0.5, ls='-', alpha=0.3)
    # mean line
    mean_diff = np.mean(diff)
    ax.axhline(mean_diff, color='navy', lw=1, ls='--', alpha=0.5)

    # plot by region
    plotted_regions = set()
    for i in range(len(xdata)):
        reg = regions[i]
        c = region_colors.get(reg, 'gray')
        m = region_markers.get(reg, 'o')
        lbl = reg if reg not in plotted_regions else None
        plotted_regions.add(reg)
        ax.errorbar(xdata[i], diff[i], xerr=xerr[i], yerr=diff_err[i],
                    fmt='none', ecolor='gray', elinewidth=0.6, capsize=1.5, alpha=0.4, zorder=2)
        ax.scatter(xdata[i], diff[i], marker=m, c=c, s=40, zorder=3,
                   edgecolors='k', linewidths=0.3, label=lbl)

    ax.set_xscale('log')
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_title(title, fontsize=11)

    # stats box
    pstr = f'{p:.2f}' if p >= 0.01 else f'{p:.1e}'
    ax.text(0.05, 0.05,
            f'Spearman $\\rho$ = {rho:.2f}\n$p$ = {pstr}\n$N$ = {len(xdata)}',
            transform=ax.transAxes, fontsize=8,
            verticalalignment='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='wheat', alpha=0.7))

ax1.set_ylabel('NdFeB $-$ SmCo Differential (% change)', fontsize=10)
ax2.legend(fontsize=7, loc='upper right', framealpha=0.7)

fig.suptitle('NdFeB$-$SmCo Differential vs. Dose', fontsize=12, y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.95])

out = os.path.join(os.path.dirname(__file__), 'IPAC26_f2.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
print(f'Saved {out}')
print(f'Gamma:   rho={rho_g:.3f}, p={p_g:.4f}')
print(f'Neutron: rho={rho_n:.3f}, p={p_n:.4f}')
