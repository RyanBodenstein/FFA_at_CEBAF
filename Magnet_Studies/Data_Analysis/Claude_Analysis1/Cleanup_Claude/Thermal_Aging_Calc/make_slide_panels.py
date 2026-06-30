#!/usr/bin/env python3
"""
Generate standalone slide-ready panels for thermal aging defense backup slides.
Extracted from thermal_aging_calc.py with larger fonts and fixed annotations.

Output:
  slide_vendor_curve.png     - Panel (a): vendor curve + Arrhenius scaling
  slide_excess_aging.png     - Panel (d): tunnel-vs-lab excess aging, 6x shortfall
  slide_dy_inversion.png     - Panel (c): Dy inversion test
  slide_hci_sensitivity.png  - Hci exponent sensitivity table
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

OUTDIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================================================
# Replicate necessary data from thermal_aging_calc.py
# ==========================================================================
kB = 8.617e-5  # eV/K

# Vendor curve data (100C, generic NdFeB)
t_ref_hrs = np.array([1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000])
pct_Br    = np.array([98.85, 98.70, 98.55, 98.48, 98.42, 98.38, 98.35,
                       98.30, 98.27, 98.25, 98.22, 98.18, 98.15])
loss_at_100C = 100.0 - pct_Br

T_ref_K = 373.15   # 100C
T_worst_K = 318.15  # 45C
T_lab_K = 294.15    # 21C
duration_hrs = 8760  # 12 months

materials = {
    'Generic NdFeB': {'Hci_20C_kOe': 12, 'beta_Hci_pctC': -0.60},
    'N42EH':         {'Hci_20C_kOe': 30, 'beta_Hci_pctC': -0.50},
    'N52SH':         {'Hci_20C_kOe': 19, 'beta_Hci_pctC': -0.60},
    'SmCo33H':       {'Hci_20C_kOe': 25, 'beta_Hci_pctC': -0.20},
    'SmCo35':        {'Hci_20C_kOe': 18, 'beta_Hci_pctC': -0.25},
}

obs = {
    'N42EH': -0.252,
    'N52SH': -0.170,
}

Ea_nominal = 1.0
n_exponent = 2  # Stoner-Wohlfarth

# Reference Hci: generic NdFeB at 100C (the condition under which vendor curve was measured)
Hci_gen_100 = 12 * (1.0 + (-0.60 / 100.0) * (100.0 - 20.0))  # = 6.24 kOe

def arrhenius_scale(T_K, T_ref_K, Ea_eV):
    return np.exp((-Ea_eV / kB) * (1.0/T_K - 1.0/T_ref_K))

def Hci_at_T(Hci_20, beta_pct, T_C):
    return Hci_20 * (1.0 + (beta_pct / 100.0) * (T_C - 20.0))

def interp_loss(t_equiv, t_data, loss_data):
    if t_equiv <= 0:
        return 0.0
    log_t = np.log10(t_equiv)
    log_t_data = np.log10(t_data)
    if log_t <= log_t_data[0]:
        return loss_data[0] * (log_t / log_t_data[0]) if log_t_data[0] > 0 else loss_data[0]
    elif log_t >= log_t_data[-1]:
        slope = (loss_data[-1] - loss_data[-4]) / (log_t_data[-1] - log_t_data[-4])
        return loss_data[-1] + slope * (log_t - log_t_data[-1])
    else:
        return float(np.interp(log_t, log_t_data, loss_data))

def compute_excess_aging(grade_name, Ea=Ea_nominal, n=n_exponent):
    """
    Compute EXCESS aging (45C vs 21C) for a grade.
    Uses same Hci correction factor (at 45C) for both temperatures,
    which is conservative (overestimates lab aging, shrinks excess).
    This matches the original thermal_aging_calc.py logic.
    """
    mat = materials[grade_name]

    if 'SmCo' in grade_name:
        return 0.0, 0.0, 0.0

    # Arrhenius scaling at each temperature
    sc_45 = arrhenius_scale(T_worst_K, T_ref_K, Ea)
    sc_21 = arrhenius_scale(T_lab_K, T_ref_K, Ea)
    loss_45 = interp_loss(duration_hrs * sc_45, t_ref_hrs, loss_at_100C)
    loss_21 = interp_loss(duration_hrs * sc_21, t_ref_hrs, loss_at_100C)

    # Hci correction: use Hci at 45C for BOTH (conservative)
    Hci_grade_45 = Hci_at_T(mat['Hci_20C_kOe'], mat['beta_Hci_pctC'], 45.0)
    corr = (Hci_gen_100 / Hci_grade_45) ** n

    aging_45 = loss_45 * corr
    aging_21 = loss_21 * corr
    excess = aging_45 - aging_21
    return aging_45, aging_21, excess

# Compute excess aging
aging_45_n42eh, aging_21_n42eh, excess_n42eh = compute_excess_aging('N42EH')
aging_45_n52sh, aging_21_n52sh, excess_n52sh = compute_excess_aging('N52SH')
ndfeb_excess = (excess_n42eh + excess_n52sh) / 2.0
observed_tunnel_lab = 0.201

print("Excess aging (45C vs 21C):")
print("  N42EH: {:.4f}%".format(excess_n42eh))
print("  N52SH: {:.4f}%".format(excess_n52sh))
print("  NdFeB avg: {:.4f}%".format(ndfeb_excess))
print("  Observed: {:.3f}%".format(observed_tunnel_lab))
print("  Shortfall: {:.1f}x".format(observed_tunnel_lab / ndfeb_excess))

# ==========================================================================
# PANEL (a): Vendor Curve + Arrhenius Scaling
# ==========================================================================
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

ax.semilogx(t_ref_hrs, loss_at_100C, 'k-o', markersize=5, linewidth=2,
            label='Vendor data (100C, generic NdFeB)')

colors_Ea = {0.5: '#e74c3c', 1.0: '#2980b9', 1.5: '#27ae60'}
for Ea in [0.5, 1.0, 1.5]:
    sc = arrhenius_scale(T_worst_K, T_ref_K, Ea)
    t_eq = duration_hrs * sc
    loss = interp_loss(t_eq, t_ref_hrs, loss_at_100C)
    ax.axvline(t_eq, color=colors_Ea[Ea], ls='--', alpha=0.6)
    ax.plot(t_eq, loss, 's', color=colors_Ea[Ea], ms=12, zorder=5,
            label='12 mo @ 45C, Ea={:.1f} eV\n  ({:.0f} equiv hrs, {:.2f}% loss)'.format(
                Ea, t_eq, loss))

ax.set_xlabel('Equivalent Hours at 100C', fontsize=13)
ax.set_ylabel('Irreversible Br Loss (%)', fontsize=13)
ax.set_title('Vendor Curve + Arrhenius Scaling to 45°C', fontsize=14, fontweight='bold')
ax.legend(fontsize=10, loc='lower right')
ax.set_xlim(0.5, 50000)
ax.set_ylim(0, 2.5)
ax.grid(True, alpha=0.3)
ax.tick_params(axis='both', labelsize=12)

# Context note
ax.text(0.02, 0.97, 'Vendor curve: generic NdFeB (Hci ~12 kOe, max ~80C)\n'
        'Our grades: N42EH (Hci=30), N52SH (Hci=19)\n'
        'Grade correction applied separately (see next slide)',
        transform=ax.transAxes, fontsize=10, va='top', ha='left',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
path_a = os.path.join(OUTDIR, 'slide_vendor_curve.png')
plt.savefig(path_a, dpi=150, bbox_inches='tight')
plt.close()
print("Saved: {}".format(path_a))

# ==========================================================================
# PANEL (d): Excess Aging (fixed arrow)
# ==========================================================================
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

categories = ['N42EH\nexcess', 'N52SH\nexcess', 'NdFeB avg\nexcess', 'Observed\ntunnel-lab']
excess_vals = [excess_n42eh, excess_n52sh, ndfeb_excess, observed_tunnel_lab]
bar_cols = ['#e74c3c', '#3498db', '#8e44ad', '#2c3e50']

bars = ax.bar(categories, excess_vals, color=bar_cols, edgecolor='black', lw=0.8, width=0.6)

# Value labels
for bar, val in zip(bars, excess_vals):
    label = '{:.4f}%'.format(val) if val < 0.1 else '{:.3f}%'.format(val)
    ax.text(bar.get_x() + bar.get_width()/2, val + 0.006,
            label, ha='center', va='bottom', fontsize=13, fontweight='bold')

# Double-headed arrow showing the shortfall
shortfall = observed_tunnel_lab / ndfeb_excess
ax.annotate('', xy=(3, observed_tunnel_lab - 0.005),
            xytext=(3, ndfeb_excess + 0.005),
            arrowprops=dict(arrowstyle='<->', color='#c0392b', lw=2.5))
ax.text(3.42, (ndfeb_excess + observed_tunnel_lab) / 2, '{:.0f}x\nshortfall'.format(shortfall),
        fontsize=16, fontweight='bold', color='#c0392b', ha='left', va='center')

ax.set_ylabel('NdFeB-SmCo Differential (%)', fontsize=14)
ax.set_title('Excess Aging at 45°C vs 21°C\n(Ea = 1.0 eV, Hci$^{-2}$ grade correction, 12 months)',
             fontsize=14, fontweight='bold')
ax.set_ylim(0, 0.26)
ax.grid(True, alpha=0.3, axis='y')
ax.tick_params(axis='both', labelsize=12)

# Context note
ax.text(0.02, 0.97, 'Worst case: 45°C steady-state for full year\n'
        'Both tunnel & lab undergo initial knock-down;\n'
        'only slow creep rate differs between temperatures.',
        transform=ax.transAxes, fontsize=10, va='top', ha='left',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
path_d = os.path.join(OUTDIR, 'slide_excess_aging.png')
plt.savefig(path_d, dpi=150, bbox_inches='tight')
plt.close()
print("Saved: {}".format(path_d))

# ==========================================================================
# PANEL (c): Dy Inversion — matching original order (N52SH first, N42EH second)
# ==========================================================================
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

x = np.arange(2)
width = 0.35

# Original order: N52SH first (more aging predicted), N42EH second
thermal_pred = [aging_45_n52sh, aging_45_n42eh]
observed_abs = [abs(obs['N52SH']), abs(obs['N42EH'])]

bars1 = ax.bar(x - width/2, thermal_pred, width, label='Thermal aging prediction',
               color='#bdc3c7', edgecolor='black', lw=0.8)
# Plot observed bars individually for separate legend entries
bar_n52sh = ax.bar(x[0] + width/2, observed_abs[0], width, label='Observed: N52SH',
                   color='#3498db', edgecolor='black', lw=0.8)
bar_n42eh = ax.bar(x[1] + width/2, observed_abs[1], width, label='Observed: N42EH',
                   color='#e74c3c', edgecolor='black', lw=0.8)

# Value labels
for bar, val in zip(bars1, thermal_pred):
    ax.text(bar.get_x() + bar.get_width()/2, val + 0.005,
            '{:.3f}%'.format(val), ha='center', va='bottom', fontsize=12)
for bar_group, val in zip([bar_n52sh, bar_n42eh], observed_abs):
    b = bar_group[0]
    ax.text(b.get_x() + b.get_width()/2, val + 0.005,
            '{:.3f}%'.format(val), ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(['N52SH\n(Hci = 19 kOe, 0% Dy)', 'N42EH\n(Hci = 30 kOe, 1-2% Dy)'],
                   fontsize=12)
ax.set_ylabel('Degradation (%)', fontsize=14)
ax.set_title('Grade Comparison Contradicts Thermal Aging', fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='upper left')
ax.grid(True, alpha=0.3, axis='y')
ax.tick_params(axis='y', labelsize=12)

ax.set_ylim(0, max(max(thermal_pred), max(observed_abs)) * 1.5)

# Inversion annotation — upper right, clear of all bars
ax.text(0.97, 0.97, 'Thermal aging predicts:\n  N52SH (lower Hci) > N42EH\n'
        'Observed:\n  N42EH > N52SH  (INVERSION)\n'
        'Dy neutron capture ($\\sigma$ = 994 b)\n  explains inversion',
        transform=ax.transAxes, fontsize=11, ha='right', va='top',
        fontweight='bold', color='#c0392b',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#fadbd8', alpha=0.8))

plt.tight_layout()
path_c = os.path.join(OUTDIR, 'slide_dy_inversion.png')
plt.savefig(path_c, dpi=150, bbox_inches='tight')
plt.close()
print("Saved: {}".format(path_c))

# ==========================================================================
# Hci sensitivity table (fixed formatting)
# ==========================================================================
fig, ax = plt.subplots(1, 1, figsize=(8, 3.5))
ax.axis('off')

# Compute sensitivity table
exponents = [1.0, 1.5, 2.0, 3.0]
rows = []
for n in exponents:
    exc_list = []
    for grade in ['N42EH', 'N52SH']:
        _, _, exc = compute_excess_aging(grade, Ea=Ea_nominal, n=n)
        exc_list.append(exc)

    avg_exc = np.mean(exc_list)
    sf = observed_tunnel_lab / avg_exc if avg_exc > 0 else float('inf')
    rows.append(['{:.1f}'.format(n) if n != int(n) else '{:.0f}'.format(n),
                 '{:.4f}%'.format(exc_list[0]),
                 '{:.4f}%'.format(exc_list[1]),
                 '{:.4f}%'.format(avg_exc),
                 '{:.1f}x'.format(sf)])

col_labels = ['Hci\nexponent (n)', 'N42EH\nexcess', 'N52SH\nexcess',
              'Avg excess\naging', 'Shortfall\nvs observed']
table = ax.table(cellText=rows, colLabels=col_labels,
                 cellLoc='center', loc='upper center',
                 colWidths=[0.14, 0.17, 0.17, 0.17, 0.17])
table.auto_set_font_size(False)
table.set_fontsize(13)
table.scale(1.3, 2.0)

# Style header
for j in range(5):
    table[0, j].set_facecolor('#34495e')
    table[0, j].set_text_props(color='white', fontweight='bold', fontsize=12)

# Highlight the n=2 row (our primary estimate, row index 3)
for j in range(5):
    table[3, j].set_facecolor('#fadbd8')

ax.set_title('Sensitivity to Hci Correction Exponent\n'
             '(n=2: Stoner-Wohlfarth; physical scaling is exponential)',
             fontsize=13, fontweight='bold', pad=5)

plt.tight_layout(pad=0.5)
path_table = os.path.join(OUTDIR, 'slide_hci_sensitivity.png')
plt.savefig(path_table, dpi=150, bbox_inches='tight')
plt.close()
print("Saved: {}".format(path_table))

print("\nDone. All slide figures saved to: {}".format(OUTDIR))
