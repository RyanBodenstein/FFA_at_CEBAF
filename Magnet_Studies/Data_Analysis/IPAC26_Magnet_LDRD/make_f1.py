#!/usr/bin/env python3
"""Generate IPAC26 Figure 1: compact single-column material comparison."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv, os

# --- load per-plate data ---
csv_path = os.path.join(os.path.dirname(__file__),
                        '..', 'Cleanup_Claude', 'Rod_Dosimetry',
                        'rod_dose_degradation.csv')
rows = []
with open(csv_path) as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

# Per-material percentage changes (30 tunnel plates)
materials = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
mat_vals = {}
for m in materials:
    vals = []
    for r in rows:
        v = r[m + '_pct']
        if v != 'nan' and v != '':
            vals.append(float(v))
    mat_vals[m] = np.array(vals)
diff_vals = np.array([float(r['intra_plate_diff']) for r in rows])

# Statistics
means = [np.mean(mat_vals[m]) for m in materials]
sems = [np.std(mat_vals[m], ddof=1) / np.sqrt(len(mat_vals[m])) for m in materials]
diff_mean = np.mean(diff_vals)
diff_sem = np.std(diff_vals, ddof=1) / np.sqrt(len(diff_vals))
diff_sig = abs(diff_mean / diff_sem)

GAIN_SYST = 0.124  # cleaned gain systematic (%)

# --- colors ---
colors = ['#CC3333', '#FF6644', '#3366CC', '#66AADD', '#8B0000']
xlabels = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35', 'Diff.']

# --- plot ---
fig, ax = plt.subplots(figsize=(3.4, 3.0))

# Material bars (positions 0-3)
x_mat = np.arange(4)
bars = ax.bar(x_mat, means, color=colors[:4], edgecolor='black',
              linewidth=0.6, width=0.6, yerr=sems, capsize=3,
              error_kw={'linewidth': 1.0, 'capthick': 0.8})

# Gain systematic band (material bars only)
ax.axhspan(-GAIN_SYST, GAIN_SYST, xmin=0, xmax=0.72,
           color='gold', alpha=0.18, zorder=0)
ax.plot([x_mat[0] - 0.4, x_mat[3] + 0.4], [GAIN_SYST, GAIN_SYST],
        color='goldenrod', linewidth=0.7, linestyle='--', alpha=0.6)
ax.plot([x_mat[0] - 0.4, x_mat[3] + 0.4], [-GAIN_SYST, -GAIN_SYST],
        color='goldenrod', linewidth=0.7, linestyle='--', alpha=0.6)

# Differential bar (position 5, with gap)
x_diff = 5
ax.bar(x_diff, diff_mean, color=colors[4], edgecolor='black',
       linewidth=0.6, width=0.6, yerr=diff_sem, capsize=3,
       error_kw={'linewidth': 1.0, 'capthick': 0.8})

# Visual separator
ax.axvline(4.3, color='gray', linewidth=0.5, linestyle=':', alpha=0.5)

ax.axhline(0, color='black', linewidth=0.5)

# Value labels
for i, (m, s) in enumerate(zip(means, sems)):
    yoff = -16 if m < 0 else 12
    ax.annotate('%+.3f%%' % m, (i, m),
                textcoords='offset points', xytext=(0, yoff),
                ha='center', fontsize=6.5, fontweight='bold')

ax.annotate('%+.3f%%\n%.1f$\\sigma$' % (diff_mean, diff_sig),
            (x_diff, diff_mean), textcoords='offset points',
            xytext=(0, -20), ha='center', fontsize=6.5,
            fontweight='bold', color='#8B0000')

# Axes
ax.set_xticks(list(x_mat) + [x_diff])
ax.set_xticklabels(['N42EH', 'N52SH', 'SmCo33H', 'SmCo35',
                     'NdFeB$-$SmCo'],
                    fontsize=6.5, rotation=20, ha='right')
ax.set_ylabel('Change in Magnetic Moment (%)', fontsize=8)
ax.set_ylim(-0.50, 0.25)
ax.tick_params(axis='y', labelsize=7)
ax.grid(axis='y', alpha=0.2, linewidth=0.5)

# Legend for gain band
from matplotlib.patches import Patch
ax.legend([Patch(facecolor='gold', alpha=0.3, edgecolor='goldenrod',
                 linestyle='--')],
          ['$\\pm$%.2f%% gain syst.' % GAIN_SYST],
          fontsize=6, loc='lower left', framealpha=0.7)

plt.tight_layout()

out = os.path.join(os.path.dirname(__file__), 'IPAC26_f1.png')
fig.savefig(out, dpi=300, bbox_inches='tight')
print('Saved %s' % out)

# Print summary
for i, m in enumerate(materials):
    print('%s: %+.3f%% +/- %.3f%% (N=%d)' % (m, means[i], sems[i], len(mat_vals[m])))
print('Diff: %+.3f%% +/- %.3f%% (%.1f sigma)' % (diff_mean, diff_sem, diff_sig))
