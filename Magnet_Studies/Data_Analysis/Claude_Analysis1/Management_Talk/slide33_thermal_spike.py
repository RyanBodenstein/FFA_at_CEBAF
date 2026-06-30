#!/usr/bin/env python3
"""
slide33_thermal_spike.py -- Presentation-quality 2-panel thermal spike comparison.

Simplified version of Rod_Dosimetry/thermal_spike_comparison.py for slide use.
Panel (a): Radiation resistance parameters (Curie temp, anisotropy field)
Panel (b): Measured % change by grade with error bars

Output: slide33_thermal_spike.png (200 dpi)
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(OUT_DIR, 'slide33_thermal_spike.png')

# =============================================================================
# Data
# =============================================================================

grades = ['N42EH', 'N52SH', 'SmCo33H', 'SmCo35']

# Radiation resistance parameters
Tc_K  = [588,   588,   1093,  1093]    # Curie temperature (K)
Ha_T  = [7.3,   7.3,   26.0,  26.0]    # Anisotropy field (T)

# Measured % change (Campaign 1, temp-corrected)
pct_change = [-0.252, -0.170, +0.037, -0.044]
pct_err    = [ 0.036,  0.036,  0.031,  0.031]   # statistical only

# Color scheme: NdFeB in reds/corals, SmCo in blues
colors_ndfeb = ['#D94040', '#E87070']   # darker red, lighter coral
colors_smco  = ['#3060B0', '#5090D0']   # darker blue, lighter blue
bar_colors = [colors_ndfeb[0], colors_ndfeb[1], colors_smco[0], colors_smco[1]]

# =============================================================================
# Figure
# =============================================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))
fig.subplots_adjust(wspace=0.35, left=0.07, right=0.97, top=0.86, bottom=0.12)

# ---- Panel (a): Radiation Resistance Parameters ----------------------------

x = np.arange(len(grades))
bar_w = 0.35

# Curie temperature bars
bars_tc = ax1.bar(x - bar_w/2, Tc_K, bar_w, color=bar_colors, edgecolor='black',
                  linewidth=0.8, alpha=0.85)

# Anisotropy field bars (secondary y-axis)
ax1b = ax1.twinx()
bars_ha = ax1b.bar(x + bar_w/2, Ha_T, bar_w, color=bar_colors, edgecolor='black',
                   linewidth=0.8, alpha=0.50, hatch='///')

# Annotate Tc values above bars (inside bar for tall ones, above for short)
for i, (bar, val) in enumerate(zip(bars_tc, Tc_K)):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
             f'{val} K', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Annotate Ha values above bars
for i, (bar, val) in enumerate(zip(bars_ha, Ha_T)):
    ax1b.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
              f'{val} T', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax1.set_ylabel('Curie Temperature (K)', fontsize=13)
ax1b.set_ylabel('Anisotropy Field (T)', fontsize=13)
ax1.set_ylim(0, 1400)
ax1b.set_ylim(0, 36)
ax1.set_xticks(x)
ax1.set_xticklabels(grades, fontsize=12)
ax1.set_title('(a) Radiation Resistance Parameters', fontsize=14, fontweight='bold')

# Legend
legend_elements = [
    Patch(facecolor='gray', edgecolor='black', alpha=0.85, label='Curie temp (K)'),
    Patch(facecolor='gray', edgecolor='black', alpha=0.50, hatch='///',
          label='Anisotropy field (T)'),
]
ax1.legend(handles=legend_elements, loc='upper left', fontsize=10, framealpha=0.9,
           bbox_to_anchor=(0.0, 0.98))

# Family labels above the data
ax1.text(0.5, 1320, 'NdFeB', ha='center', fontsize=12, fontstyle='italic',
         color='#B03030', fontweight='bold', zorder=10)
ax1.text(2.5, 1320, 'SmCo', ha='center', fontsize=12, fontstyle='italic',
         color='#2050A0', fontweight='bold', zorder=10)

# Dividing line between NdFeB and SmCo
ax1.axvline(x=1.5, color='gray', linewidth=1.0, linestyle='--', alpha=0.5)

# Annotation box at bottom of panel
annot_text = (
    "SmCo: 1.9x higher Curie temp, 3.6x higher anisotropy\n"
    r"$\rightarrow$ ~7x more radiation resistant (thermal spike model)"
)
ax1.text(0.50, 0.02, annot_text, transform=ax1.transAxes,
         fontsize=10, ha='center', va='bottom',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow',
                   edgecolor='gray', alpha=0.95))

# ---- Panel (b): Measured % Change ------------------------------------------

bars_meas = ax2.bar(x, pct_change, 0.55, yerr=pct_err, color=bar_colors,
                    edgecolor='black', linewidth=0.8, capsize=5,
                    error_kw=dict(linewidth=1.5, capthick=1.5))

ax2.axhline(y=0, color='black', linewidth=1.0, linestyle='-')

# Annotate each bar with its value
for i, (xi, val, err) in enumerate(zip(x, pct_change, pct_err)):
    sign = '+' if val > 0 else ''
    y_offset = -0.018 if val < 0 else 0.018
    va_align = 'top' if val < 0 else 'bottom'
    ax2.text(xi, val + y_offset, f'{sign}{val:.3f}%', ha='center', va=va_align,
             fontsize=11, fontweight='bold')

ax2.set_ylabel('Measured Change (%)', fontsize=13)
ax2.set_xticks(x)
ax2.set_xticklabels(grades, fontsize=12)
ax2.set_ylim(-0.48, 0.22)
ax2.set_title('(b) Measured vs Predicted Ranking', fontsize=14, fontweight='bold')

# Annotation: NdFeB significant degradation
ax2.text(0.5, -0.38, 'NdFeB: significant\ndegradation', fontsize=10.5,
         ha='center', va='top', color='#B03030', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFEEEE',
                   edgecolor='#D94040', alpha=0.9))

# Annotation: SmCo consistent with zero
ax2.text(2.5, 0.14, 'SmCo: consistent\nwith zero', fontsize=10.5,
         ha='center', va='bottom', color='#2050A0', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#EEF2FF',
                   edgecolor='#3060B0', alpha=0.9))

# Dividing line
ax2.axvline(x=1.5, color='gray', linewidth=1.0, linestyle='--', alpha=0.5)

# Error bar label
ax2.text(0.98, 0.02, 'Error bars: stat. only', transform=ax2.transAxes,
         fontsize=9, ha='right', va='bottom', fontstyle='italic', color='gray')

# ---- Save ------------------------------------------------------------------

fig.suptitle('Thermal Spike Model: Material Properties vs Measured Degradation',
             fontsize=15, fontweight='bold', y=0.96)

plt.savefig(OUT_PATH, dpi=200, bbox_inches='tight', facecolor='white')
print(f"Saved: {OUT_PATH}")
plt.close()
