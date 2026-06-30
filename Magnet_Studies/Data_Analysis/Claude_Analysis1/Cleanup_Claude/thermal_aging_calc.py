#!/usr/bin/env python3
"""
Worst-case thermal aging calculation for NdFeB permanent magnets.

Context: Dave M. proposed that the observed -0.208% NdFeB-SmCo differential
in Campaign 1 could be explained by thermal aging ("magnetic viscosity" /
"creep") rather than radiation damage. This script computes the maximum
expected thermal aging under worst-case assumptions.

Assumptions (ALL conservative, i.e., FAVORING Dave's hypothesis):
  1. Temperature: 45C for full 12 months (45C was an outlier; typical 30-35C)
  2. No pre-stabilization assumed (magnets not thermally "knocked down")
  3. Reference: emagnetsUK vendor data at 100C (generic NdFeB grade)
  4. Activation energy range: 0.5-1.5 eV (0.5 is unrealistically low for NdFeB)

Author: Bodenstein / Claude analysis
Date: 2026-05-30
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# Output directory
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Thermal_Aging_Calc')
os.makedirs(OUTDIR, exist_ok=True)

# ==========================================================================
# Constants
# ==========================================================================
kB = 8.617e-5  # Boltzmann constant, eV/K

# ==========================================================================
# Reference data: vendor curve at 100C (read from emagnetsUK figure)
# ==========================================================================
# Data points digitized from the image. The y-axis is "%Br" (remaining).
# The x-axis is "Hours at 100C" on a log scale from 1 to 10,000.
# Grade: unknown, almost certainly standard (N35-N42, Hci ~12 kOe, max ~80C)
t_ref_hrs = np.array([1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000])
pct_Br    = np.array([98.85, 98.70, 98.55, 98.48, 98.42, 98.38, 98.35,
                       98.30, 98.27, 98.25, 98.22, 98.18, 98.15])
loss_at_100C = 100.0 - pct_Br  # irreversible % loss

T_ref_K = 373.15  # 100C

# ==========================================================================
# Our conditions
# ==========================================================================
T_worst_K    = 318.15  # 45C (worst case, outlier)
T_typical_K  = 305.15  # 32C (realistic tunnel average)
T_lab_K      = 294.15  # 21C (lab controls)
duration_hrs = 8760    # 12 months

# ==========================================================================
# Material properties (from Allstar datasheets)
# ==========================================================================
materials = {
    'Generic NdFeB': {
        'Hci_20C_kOe': 12,   'beta_Hci_pctC': -0.60,
        'T_max_C': 80,       'T_curie_K': 588,
        'note': 'Vendor curve reference grade'
    },
    'N42EH': {
        'Hci_20C_kOe': 30,   'beta_Hci_pctC': -0.50,
        'T_max_C': 190,      'T_curie_K': 588,
        'note': '1-2% Dy, extra-high coercivity'
    },
    'N52SH': {
        'Hci_20C_kOe': 19,   'beta_Hci_pctC': -0.60,
        'T_max_C': 140,      'T_curie_K': 588,
        'note': '0% Dy, super-high coercivity'
    },
    'SmCo33H': {
        'Hci_20C_kOe': 25,   'beta_Hci_pctC': -0.20,
        'T_max_C': 350,      'T_curie_K': 1093,
        'note': 'Sm2Co17, high coercivity'
    },
    'SmCo35': {
        'Hci_20C_kOe': 18,   'beta_Hci_pctC': -0.25,
        'T_max_C': 300,      'T_curie_K': 1093,
        'note': 'Sm2Co17, standard'
    },
}

# Observed Campaign 1 results (temp-corrected, Tref=20C)
obs = {
    'N42EH':   -0.252,  # +/- 0.036 stat
    'N52SH':   -0.170,  # +/- 0.036 stat
    'SmCo33H': +0.037,  # +/- 0.031 stat
    'SmCo35':  -0.044,  # +/- 0.031 stat
    'NdFeB_avg': -0.211,
    'SmCo_avg':  -0.004,
    'differential': -0.208,  # +/- 0.028 stat (7.6 sigma)
}


# ==========================================================================
# Helper functions
# ==========================================================================
def arrhenius_scale(T_K, T_ref_K, Ea_eV):
    """Time-scaling factor: t_ref_equiv = t_at_T * scale."""
    return np.exp((-Ea_eV / kB) * (1.0/T_K - 1.0/T_ref_K))


def Hci_at_T(Hci_20, beta_pct, T_C):
    """Intrinsic coercivity at temperature T_C (Celsius)."""
    return Hci_20 * (1.0 + (beta_pct / 100.0) * (T_C - 20.0))


def interp_loss(t_equiv, t_data, loss_data):
    """
    Interpolate reference loss curve (in log-time space).
    Extrapolates logarithmically beyond data range.
    """
    if t_equiv <= 0:
        return 0.0
    log_t = np.log10(t_equiv)
    log_t_data = np.log10(t_data)
    if log_t <= log_t_data[0]:
        # Below first point: linear in log-space from (0,0)
        return loss_data[0] * (log_t / log_t_data[0]) if log_t_data[0] > 0 else loss_data[0]
    elif log_t >= log_t_data[-1]:
        # Beyond last point: extrapolate from last two decades
        slope = (loss_data[-1] - loss_data[-4]) / (log_t_data[-1] - log_t_data[-4])
        return loss_data[-1] + slope * (log_t - log_t_data[-1])
    else:
        return float(np.interp(log_t, log_t_data, loss_data))


# ==========================================================================
# Main calculation
# ==========================================================================
lines = []   # collect output for text file

def out(s=''):
    print(s)
    lines.append(s)


out('=' * 80)
out('WORST-CASE THERMAL AGING CALCULATION')
out('=' * 80)
out()
out('Context: Testing whether thermal aging at tunnel temperatures can explain')
out('the observed -0.208% +/- 0.028% NdFeB-SmCo differential from Campaign 1.')
out()
out('Reference: emagnetsUK vendor curve, 100C, generic NdFeB (likely N35-N42)')
out('Worst-case: 45C for full 12 months (8,760 hours)')
out('Note: 45C was a single outlier reading; typical tunnel temp is 30-35C.')
out()

# ------------------------------------------------------------------
# PART 1: Arrhenius scaling (generic grade, no correction)
# ------------------------------------------------------------------
out('-' * 80)
out('PART 1: Arrhenius Scaling from 100C to 45C (Generic NdFeB, No Grade Correction)')
out('-' * 80)
out()
out('The thermal aging rate follows Arrhenius: rate ~ exp(-Ea / kT)')
out('12 months at 45C is equivalent to X hours at 100C, where X depends on Ea.')
out()
out('{:>8s}  {:>14s}  {:>16s}  {:>16s}'.format(
    'Ea (eV)', 'Scale factor', 'Equiv 100C hrs', 'Generic loss (%)'))
out('-' * 58)

Ea_values = [0.5, 0.7, 1.0, 1.25, 1.5]
generic_45C = {}
for Ea in Ea_values:
    sc = arrhenius_scale(T_worst_K, T_ref_K, Ea)
    t_eq = duration_hrs * sc
    loss = interp_loss(t_eq, t_ref_hrs, loss_at_100C)
    generic_45C[Ea] = {'scale': sc, 't_equiv': t_eq, 'loss': loss}
    out('{:>8.2f}  {:>14.6f}  {:>16.1f}  {:>16.4f}'.format(Ea, sc, t_eq, loss))

out()
out('Interpretation:')
out('  Ea = 0.5 eV is unrealistically low (gives ~600 equiv hours, well into')
out('  the logarithmic regime of the 100C curve).')
out('  Ea = 1.0-1.5 eV is typical for NdFeB domain relaxation.')
out('  At Ea = 1.0 eV, 12 months at 45C = 40 hours at 100C for the GENERIC grade.')
out()

# ------------------------------------------------------------------
# PART 2: Coercivity at operating temperature
# ------------------------------------------------------------------
out('-' * 80)
out('PART 2: Intrinsic Coercivity at Operating Temperature')
out('-' * 80)
out()
out('The coercivity Hci(T) determines the energy barrier for domain relaxation.')
out('Higher Hci = deeper energy wells = exponentially less thermal aging.')
out()

# Reference point: generic grade at 100C (this is what the vendor curve represents)
Hci_gen_100 = Hci_at_T(12, -0.60, 100)

out('{:>15s}  {:>10s}  {:>8s}  {:>10s}  {:>8s}  {:>10s}'.format(
    'Grade', 'Hci(20C)', 'beta', 'Hci(45C)', 'T/Tmax', 'vs generic'))
out('-' * 67)
for name, m in materials.items():
    h45 = Hci_at_T(m['Hci_20C_kOe'], m['beta_Hci_pctC'], 45)
    ratio_Tmax = 45.0 / m['T_max_C']
    ratio_Hci = h45 / Hci_gen_100
    out('{:>15s}  {:>8.0f} kOe  {:>6.2f}  {:>8.1f} kOe  {:>8.2f}  {:>8.1f}x'.format(
        name, m['Hci_20C_kOe'], m['beta_Hci_pctC'], h45, ratio_Tmax, ratio_Hci))

out()
out('Reference: Generic NdFeB at 100C has Hci = {:.1f} kOe'.format(Hci_gen_100))
out('Key: Our N42EH at 45C has 4.2x the coercivity of the vendor curve grade at 100C.')
out('     Our N52SH at 45C has 2.6x the coercivity.')
out('     SmCo grades: negligible aging at 45C (Tc = 820C, T/Tmax = 0.13-0.15).')
out()

# ------------------------------------------------------------------
# PART 3: Grade-corrected estimates
# ------------------------------------------------------------------
out('-' * 80)
out('PART 3: Grade-Corrected Aging Estimates')
out('-' * 80)
out()
out('The domain relaxation rate scales exponentially with the energy barrier,')
out('which is proportional to Hci. A CONSERVATIVE (i.e., favorable to Dave)')
out('correction uses (Hci_ref / Hci_grade)^2. The physical scaling is')
out('exponential and would give much stronger suppression.')
out()
out('All values: 45C for 12 months, Ea = 1.0 eV (nominal for NdFeB).')
out()

Ea_nom = 1.0
sc_nom = arrhenius_scale(T_worst_K, T_ref_K, Ea_nom)
t_eq_nom = duration_hrs * sc_nom
loss_gen_nom = interp_loss(t_eq_nom, t_ref_hrs, loss_at_100C)

out('{:>15s}  {:>10s}  {:>12s}  {:>14s}'.format(
    'Grade', 'Hci(45C)', 'Correction', 'Aging (%)'))
out('-' * 55)

grade_aging = {}
for name, m in materials.items():
    h45 = Hci_at_T(m['Hci_20C_kOe'], m['beta_Hci_pctC'], 45)
    if 'SmCo' in name:
        corr = 0.0
        aging = 0.0
    elif name == 'Generic NdFeB':
        corr = 1.0
        aging = loss_gen_nom
    else:
        corr = (Hci_gen_100 / h45) ** 2
        aging = loss_gen_nom * corr
    grade_aging[name] = aging
    out('{:>15s}  {:>8.1f} kOe  {:>12.5f}  {:>14.4f}'.format(name, h45, corr, aging))

out()
ndfeb_avg = (grade_aging['N42EH'] + grade_aging['N52SH']) / 2.0
smco_avg = 0.0
diff_pred = ndfeb_avg - smco_avg

out('Expected NdFeB average aging:              {:.4f}%'.format(ndfeb_avg))
out('Expected SmCo average aging:               {:.4f}%'.format(smco_avg))
out('Expected NdFeB-SmCo differential (aging):  {:.4f}%'.format(diff_pred))
out('Observed NdFeB-SmCo differential:          -0.208 +/- 0.028%')
if diff_pred > 0:
    out('Ratio (observed / predicted):              {:.1f}x'.format(
        abs(obs['differential']) / diff_pred))
out()

# ------------------------------------------------------------------
# PART 4: Full sensitivity table
# ------------------------------------------------------------------
out('-' * 80)
out('PART 4: Sensitivity to Activation Energy')
out('-' * 80)
out()
out('Grade-corrected (conservative Hci^-2), 45C, 12 months.')
out()
out('{:>6s}  {:>10s}  {:>10s}  {:>10s}  {:>10s}  {:>12s}'.format(
    'Ea', 'Generic', 'N42EH', 'N52SH', 'Diff', 'vs 0.208%'))
out('-' * 62)

Hci_n42eh_45 = Hci_at_T(30, -0.50, 45)
Hci_n52sh_45 = Hci_at_T(19, -0.60, 45)
corr_n42eh = (Hci_gen_100 / Hci_n42eh_45) ** 2
corr_n52sh = (Hci_gen_100 / Hci_n52sh_45) ** 2

for Ea in Ea_values:
    sc = arrhenius_scale(T_worst_K, T_ref_K, Ea)
    t_eq = duration_hrs * sc
    lg = interp_loss(t_eq, t_ref_hrs, loss_at_100C)
    l42 = lg * corr_n42eh
    l52 = lg * corr_n52sh
    d = (l42 + l52) / 2.0
    ratio_str = '{:.1f}x'.format(abs(obs['differential']) / d) if d > 1e-6 else 'inf'
    out('{:>6.2f}  {:>9.4f}%  {:>9.4f}%  {:>9.4f}%  {:>9.4f}%  {:>12s}'.format(
        Ea, lg, l42, l52, d, ratio_str))

out()

# ------------------------------------------------------------------
# PART 5: The Dy Inversion (strongest counter-argument)
# ------------------------------------------------------------------
out('-' * 80)
out('PART 5: The Dysprosium Inversion Test')
out('-' * 80)
out()
out('If thermal aging drives the signal, the grade with LOWER coercivity')
out('and LOWER max operating temperature should age MORE:')
out()
out('  Thermal aging prediction:')
out('    N42EH (Hci=30, max 190C): LESS aging')
out('    N52SH (Hci=19, max 140C): MORE aging')
out()
out('  Observation:')
out('    N42EH: -0.252 +/- 0.036%  (MORE degradation!)')
out('    N52SH: -0.170 +/- 0.036%  (LESS degradation)')
out('    Difference: 0.082% in the WRONG direction for thermal aging')
out()
out('  Radiation hypothesis (Dy neutron capture):')
out('    N42EH contains 1-2% Dy (sigma = 994 barn)')
out('    N52SH contains 0% Dy')
out('    Dy captures neutrons -> local lattice damage -> explains inversion')
out()
out('  This inversion CANNOT be explained by thermal aging regardless of')
out('  the assumed activation energy or grade correction model.')
out()

# ------------------------------------------------------------------
# PART 6: Temperature sensitivity
# ------------------------------------------------------------------
out('-' * 80)
out('PART 6: Temperature Sensitivity')
out('-' * 80)
out()
out('45C was a single outlier reading. How does the prediction change')
out('at more realistic temperatures? (Ea = 1.0 eV, grade-corrected)')
out()
out('{:>8s}  {:>14s}  {:>16s}  {:>12s}  {:>12s}'.format(
    'Temp (C)', 'Scale', 'Equiv 100C hrs', 'N42EH (%)', 'N52SH (%)'))
out('-' * 66)

for T_C in [20, 25, 30, 35, 40, 45]:
    T_K = T_C + 273.15
    sc = arrhenius_scale(T_K, T_ref_K, 1.0)
    t_eq = duration_hrs * sc
    lg = interp_loss(t_eq, t_ref_hrs, loss_at_100C)
    out('{:>8d}  {:>14.8f}  {:>16.4f}  {:>12.5f}  {:>12.5f}'.format(
        T_C, sc, t_eq, lg * corr_n42eh, lg * corr_n52sh))

out()
out('Note: these values include the initial knock-down from the vendor curve.')
out('At 30C, predicted N42EH aging is ~0.08% and N52SH is ~0.22% (generic curve,')
out('grade-corrected). BUT see Part 7b for why these absolute numbers overstate')
out('the effect when compared to our tunnel-vs-lab measurement design.')
out()

# ------------------------------------------------------------------
# PART 7: Lab controls consistency check
# ------------------------------------------------------------------
out('-' * 80)
out('PART 7: Lab Controls Consistency Check')
out('-' * 80)
out()

sc_lab = arrhenius_scale(T_lab_K, T_ref_K, 1.0)
t_eq_lab = duration_hrs * sc_lab
loss_lab_gen = interp_loss(t_eq_lab, t_ref_hrs, loss_at_100C)

out('Lab temperature: ~21C (294 K)')
out('Equivalent 100C time (Ea=1.0): {:.4f} hours'.format(t_eq_lab))
out('Expected generic aging: {:.6f}%'.format(loss_lab_gen))
out()
out('If Dave is right that aging at 45C causes -0.208%, then at 21C:')
sc_ratio = sc_lab / arrhenius_scale(T_worst_K, T_ref_K, 1.0)
expected_lab_aging = 0.208 * sc_ratio
out('  Expected lab aging = 0.208% x {:.6f} = {:.4f}%'.format(sc_ratio, expected_lab_aging))
out('  Observed lab differential: -0.007 +/- 0.038%')
out('  The predicted lab aging ({:.4f}%) is small enough to be consistent'.format(expected_lab_aging))
out('  with the observation, so this test has limited discriminating power.')
out('  However, the grade-corrected model (Part 3) predicts LARGER lab')
out('  aging (~0.13% NdFeB avg at 21C), which IS in tension with the')
out('  observation at ~2 sigma. See Part 7b for the proper comparison.')
out()

# ------------------------------------------------------------------
# PART 7b: Tunnel-vs-Lab Differential (the proper comparison)
# ------------------------------------------------------------------
out('-' * 80)
out('PART 7b: Tunnel-vs-Lab Differential Aging (Critical Refinement)')
out('-' * 80)
out()
out('Our measurement compares tunnel plates (at elevated temp) to lab plates')
out('(at room temp). BOTH sets undergo the initial knock-down. The relevant')
out('quantity is not the absolute aging but the EXCESS aging at tunnel temp')
out('vs lab temp.')
out()
out('Pre-measurement was done before deployment. Then:')
out('  - Tunnel magnets: sit at ~45C for 12 months')
out('  - Lab magnets: sit at ~21C for 12 months')
out()
out('Tunnel NdFeB-SmCo diff captures NdFeB aging at tunnel temp (SmCo ~ 0).')
out('Lab NdFeB-SmCo diff captures NdFeB aging at lab temp (SmCo ~ 0).')
out('Tunnel-Lab difference = EXCESS aging from elevated temperature.')
out()

# Compute aging at both temperatures for each grade
out('{:>15s}  {:>14s}  {:>14s}  {:>14s}'.format(
    'Grade', 'Aging @45C (%)', 'Aging @21C (%)', 'Excess (%)'))
out('-' * 62)

sc_45 = arrhenius_scale(T_worst_K, T_ref_K, Ea_nom)
sc_21 = arrhenius_scale(T_lab_K, T_ref_K, Ea_nom)

excess_list = {}
for name in ['Generic NdFeB', 'N42EH', 'N52SH']:
    t_eq_45 = duration_hrs * sc_45
    t_eq_21 = duration_hrs * sc_21
    loss_45 = interp_loss(t_eq_45, t_ref_hrs, loss_at_100C)
    loss_21 = interp_loss(t_eq_21, t_ref_hrs, loss_at_100C)

    if name == 'Generic NdFeB':
        corr = 1.0
    else:
        h45 = Hci_at_T(materials[name]['Hci_20C_kOe'],
                       materials[name]['beta_Hci_pctC'], 45)
        corr = (Hci_gen_100 / h45) ** 2

    aging_45 = loss_45 * corr
    aging_21 = loss_21 * corr
    excess = aging_45 - aging_21
    excess_list[name] = excess
    out('{:>15s}  {:>14.4f}  {:>14.4f}  {:>14.4f}'.format(
        name, aging_45, aging_21, excess))

ndfeb_excess = (excess_list['N42EH'] + excess_list['N52SH']) / 2.0

out()
out('NdFeB avg excess aging (45C vs 21C):    {:.4f}%'.format(ndfeb_excess))
out('Observed tunnel-lab differential:       -0.201%  (= -0.208 - (-0.007))')
if ndfeb_excess > 0:
    out('Ratio (observed / predicted excess):    {:.1f}x'.format(0.201 / ndfeb_excess))
out()
out('CRITICAL FINDING: The predicted excess aging is {:.4f}%,'.format(ndfeb_excess))
out('{:.0f}x too small to explain the observed 0.201% tunnel-lab difference.'.format(
    0.201 / ndfeb_excess if ndfeb_excess > 0 else float('inf')))
out()
out('Furthermore, the model predicts that lab NdFeB should ALSO show aging')
out('({:.3f}% for N42EH, {:.3f}% for N52SH at 21C). But the observed lab'.format(
    interp_loss(duration_hrs * sc_21, t_ref_hrs, loss_at_100C) * corr_n42eh,
    interp_loss(duration_hrs * sc_21, t_ref_hrs, loss_at_100C) * corr_n52sh))
out('NdFeB-SmCo differential is -0.007 +/- 0.038%, consistent with zero.')
out('This means the grade correction is actually TOO CONSERVATIVE, and the')
out('true aging at these temperatures is even smaller than predicted here.')
out()

# ------------------------------------------------------------------
# PART 8: What if NO grade correction? (most favorable to Dave)
# ------------------------------------------------------------------
out('-' * 80)
out('PART 8: No Grade Correction (Most Favorable Scenario for Dave)')
out('-' * 80)
out()
out('If we ignore the grade difference entirely and apply the generic vendor')
out('curve directly to our magnets (clearly wrong, but maximum steel-man):')
out()
out('{:>8s}  {:>16s}  {:>16s}  {:>16s}'.format(
    'Ea (eV)', 'Generic Loss (%)', 'NdFeB-SmCo Diff', 'vs Observed'))
out('-' * 60)

for Ea in Ea_values:
    sc = arrhenius_scale(T_worst_K, T_ref_K, Ea)
    t_eq = duration_hrs * sc
    lg = interp_loss(t_eq, t_ref_hrs, loss_at_100C)
    # SmCo still ~zero aging
    sign = 'matches' if abs(lg - 0.208) < 0.1 else ('too large' if lg > 0.208 else 'too small')
    out('{:>8.2f}  {:>16.4f}  {:>16.4f}  {:>16s}'.format(Ea, lg, lg, sign))

out()
out('Key finding: without grade correction, the generic curve at low Ea')
out('can produce losses exceeding 0.208%. But this is for a STANDARD grade')
out('(Hci ~12 kOe, max temp ~80C) that is far less thermally stable than')
out('our EH/SH grades (Hci 19-30 kOe, max temp 140-190C).')
out()
out('Even in this most favorable scenario, the Dy inversion remains:')
out('  -> If aging causes 0.208%, N52SH should show MORE than N42EH')
out('  -> We observe the OPPOSITE.')
out('  -> Thermal aging alone cannot explain the data.')
out()

# ------------------------------------------------------------------
# PART 9: Haavisto T_0 Framework (peer-reviewed, strongest argument)
# ------------------------------------------------------------------
out('-' * 80)
out('PART 9: The Haavisto T_0 Framework')
out('-' * 80)
out()
out('Haavisto & Paju (2009, IEEE Trans. Magn. 45(12), 5277-5280) established')
out('that sintered NdFeB with a square J-H curve is thermally stable below a')
out('critical temperature T_0, above which irreversible losses suddenly appear.')
out('T_0 depends on Hci and the permeance coefficient (Pc).')
out()
out('For high-coercivity material (Hci ~25-30 kOe), T_0 is approximately')
out('120-150C for typical geometries (Pc > 1).')
out()
out('Haavisto et al. (2014, Adv. Mater. Sci. Eng. 2014, 760584) showed that')
out('the estimated flux loss after 30 YEARS is approximately 2x the loss')
out('measured after just 1 HOUR. This is a consequence of the logarithmic')
out('time dependence: delta_J = S * ln(t/t0).')
out()
out('Application to our magnets:')
out()
out('{:>12s}  {:>10s}  {:>12s}  {:>20s}'.format(
    'Grade', 'Hci(20C)', 'T_operating', 'T_0 (estimated)'))
out('-' * 58)
out('{:>12s}  {:>8d} kOe  {:>10d} C  {:>18s}'.format('N42EH', 30, 45, '~150C'))
out('{:>12s}  {:>8d} kOe  {:>10d} C  {:>18s}'.format('N52SH', 19, 45, '~100-120C'))
out('{:>12s}  {:>8d} kOe  {:>10d} C  {:>18s}'.format('SmCo33H', 25, 45, '>>200C'))
out('{:>12s}  {:>8d} kOe  {:>10d} C  {:>18s}'.format('SmCo35', 18, 45, '>>200C'))
out()
out('All our grades operate far below their respective T_0 values.')
out('According to the Haavisto framework, time-dependent flux losses')
out('below T_0 are negligible even on multi-decade timescales.')
out()
out('Haavisto et al. (2013, EPJ Web Conf. 40, 06001) further showed that')
out('magnets with square J-H curves (characteristic of high-Hci grades)')
out('do NOT benefit from pre-stabilization treatment, because they are')
out('already stable below T_0. This suggests that even if our magnets were')
out('not pre-stabilized, the initial knock-down for EH/SH grades at 45C')
out('would be negligible.')
out()

# ------------------------------------------------------------------
# PART 10: Sensitivity to Hci Correction Exponent
# ------------------------------------------------------------------
out('-' * 80)
out('PART 10: Sensitivity to Hci Correction Exponent')
out('-' * 80)
out()
out('The Hci^-n correction in Parts 3-4 uses n=2. This exponent is motivated')
out('by the Stoner-Wohlfarth model for coherent rotation, where the energy')
out('barrier scales as E_b ~ K*V*(1-H/Hci)^2 (Kronmuller & Fahnle, 2003;')
out('Givord et al., 1988, IEEE Trans. Magn. 24(2), 1921-1923). For')
out('nucleation-type reversal (the dominant mechanism in sintered NdFeB),')
out('the exponent is >= 2. The physical scaling is actually exponential')
out('through the Boltzmann factor: rate ~ exp(-Hci*V_act/kT).')
out()
out('Sensitivity of the excess aging (tunnel-vs-lab) to the exponent:')
out()
out('{:>10s}  {:>10s}  {:>10s}  {:>12s}  {:>10s}'.format(
    'Exponent', 'N42EH (%)', 'N52SH (%)', 'Avg Excess', 'Shortfall'))
out('-' * 55)

for n_exp in [1.0, 1.5, 2.0, 3.0]:
    c42 = (Hci_gen_100 / Hci_n42eh_45) ** n_exp
    c52 = (Hci_gen_100 / Hci_n52sh_45) ** n_exp
    e42 = (interp_loss(duration_hrs * sc_45, t_ref_hrs, loss_at_100C) * c42 -
           interp_loss(duration_hrs * sc_21, t_ref_hrs, loss_at_100C) * c42)
    e52 = (interp_loss(duration_hrs * sc_45, t_ref_hrs, loss_at_100C) * c52 -
           interp_loss(duration_hrs * sc_21, t_ref_hrs, loss_at_100C) * c52)
    avg = (e42 + e52) / 2.0
    sf = 0.201 / avg if avg > 1e-6 else float('inf')
    out('{:>10.1f}  {:>9.4f}%  {:>9.4f}%  {:>11.4f}%  {:>9.1f}x'.format(
        n_exp, e42, e52, avg, sf))

out()
out('Even with the most favorable exponent (n=1, linear scaling), the')
out('excess aging shortfall is still substantial. With the physically')
out('motivated n=2, the shortfall is 6x. With n=3 (more realistic for')
out('nucleation), the shortfall grows further.')
out()
out('Note: the true physical scaling (exponential) would give correction')
out('factors orders of magnitude smaller than any power-law model,')
out('making the shortfall even larger.')
out()

# ------------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------------
out('=' * 80)
out('SUMMARY')
out('=' * 80)
out()
out('1. QUANTITATIVE: Under worst-case assumptions (45C, 12 months, Ea=1.0 eV,')
out('   conservative Hci^-2 grade correction):')
out('   - Absolute NdFeB aging at 45C: ~{:.3f}% (vs observed -0.208%)'.format(diff_pred))
out('   - But the proper comparison is tunnel-vs-lab EXCESS aging: ~{:.4f}%'.format(ndfeb_excess))
out('   - This is {:.0f}x too small to explain the observed 0.201% tunnel-lab'.format(
    0.201 / ndfeb_excess if ndfeb_excess > 0 else float('inf')))
out('     difference. Both tunnel and lab magnets undergo the initial knock-down;')
out('     only the slow creep rate differs between temperatures.')
out()
out('2. HAAVISTO T_0: Peer-reviewed aging studies (Haavisto & Paju, 2009) show')
out('   that high-Hci NdFeB is stable below a critical temperature T_0 (~120-')
out('   150C for our grades). At 45C, our magnets are far below T_0, where')
out('   time-dependent losses are negligible even on multi-decade timescales.')
out()
out('3. QUALITATIVE: The Dy inversion (N42EH > N52SH) is strongly suggestive')
out('   of radiation damage (1.6 sigma, with quantitative Dy neutron capture')
out('   explanation) and runs counter to any thermal aging prediction.')
out()
out('4. CONTROLS: Lab plates at 21C show no NdFeB-SmCo differential (-0.007 +/-')
out('   0.038%), consistent with negligible aging at room temperature.')
out()
out('5. DOSE CORRELATION: Degradation correlates with neutron dose (rho=0.389,')
out('   p=0.03) but not gamma dose (rho=0.21, p=0.27). Temperature does not')
out('   selectively produce neutron-correlated effects.')
out()
out('6. COOL ZONES: Labyrinth plates (near ambient, N=2) show NdFeB-specific')
out('   degradation, consistent with scattered radiation reaching those')
out('   locations (confirmed by rod dosimetry).')
out()
out('CONCLUSION: Thermal aging alone is unlikely to explain the observed signal.')
out('  - Quantitatively: the tunnel-vs-lab excess aging is {:.0f}x too small'.format(
    0.201 / ndfeb_excess if ndfeb_excess > 0 else float('inf')))
out('  - Peer-reviewed Haavisto T_0 framework confirms our magnets operate')
out('    far below the threshold for significant time-dependent flux loss')
out('  - Multiple converging lines of evidence (Dy inversion, neutron')
out('    correlation, material specificity) point to radiation, not temperature')
out('  - Campaign 2 data will provide independent confirmation')
out()


# ==========================================================================
# PLOTS
# ==========================================================================

fig, axes = plt.subplots(1, 4, figsize=(20, 5.5))

# --- Panel (a): Vendor curve + Arrhenius markers ---
ax = axes[0]
ax.semilogx(t_ref_hrs, loss_at_100C, 'k-o', markersize=4, linewidth=2,
            label='Vendor data (100C, generic NdFeB)')

colors_Ea = {0.5: '#e74c3c', 1.0: '#2980b9', 1.5: '#27ae60'}
for Ea in [0.5, 1.0, 1.5]:
    sc = arrhenius_scale(T_worst_K, T_ref_K, Ea)
    t_eq = duration_hrs * sc
    loss = interp_loss(t_eq, t_ref_hrs, loss_at_100C)
    ax.axvline(t_eq, color=colors_Ea[Ea], ls='--', alpha=0.6)
    ax.plot(t_eq, loss, 's', color=colors_Ea[Ea], ms=10, zorder=5,
            label='12 mo @ 45C, Ea={:.1f} eV\n  ({:.0f} equiv hrs, {:.2f}% loss)'.format(
                Ea, t_eq, loss))

ax.set_xlabel('Equivalent Hours at 100C', fontsize=11)
ax.set_ylabel('Irreversible Br Loss (%)', fontsize=11)
ax.set_title('(a) Vendor Curve + Arrhenius Scaling', fontsize=12, fontweight='bold')
ax.legend(fontsize=7.5, loc='lower right')
ax.set_xlim(0.5, 50000)
ax.set_ylim(0, 2.5)
ax.grid(True, alpha=0.3)

# --- Panel (b): Grade-corrected bar chart ---
ax = axes[1]
grades = ['Generic\nNdFeB', 'N42EH', 'N52SH', 'SmCo33H', 'SmCo35']
aging_vals = [grade_aging[k] for k in
              ['Generic NdFeB', 'N42EH', 'N52SH', 'SmCo33H', 'SmCo35']]
bar_colors = ['#95a5a6', '#e74c3c', '#3498db', '#2ecc71', '#27ae60']

bars = ax.bar(grades, aging_vals, color=bar_colors, edgecolor='black', lw=0.5)
ax.axhline(0.208, color='red', ls='--', lw=2, label='Observed differential (0.208%)')

# value labels
for bar, val in zip(bars, aging_vals):
    if val > 0.0005:
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.015,
                '{:.3f}%'.format(val), ha='center', va='bottom', fontsize=9,
                fontweight='bold')
    else:
        ax.text(bar.get_x() + bar.get_width()/2, 0.01,
                '~0', ha='center', va='bottom', fontsize=9, color='gray')

ax.set_ylabel('Expected Irreversible Loss (%)', fontsize=11)
ax.set_title('(b) Grade-Corrected Aging\n(Ea=1.0 eV, 45C, 12 mo)', fontsize=12,
             fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, axis='y')
ax.set_ylim(0, max(aging_vals) * 1.4)

# --- Panel (c): Dy inversion ---
ax = axes[2]
x = np.arange(2)
width = 0.35

# Thermal prediction (grade-corrected): N52SH > N42EH
thermal = [grade_aging['N52SH'], grade_aging['N42EH']]  # N52SH first (more aging predicted)
observed_abs = [abs(obs['N52SH']), abs(obs['N42EH'])]

bars1 = ax.bar(x - width/2, thermal, width, label='Thermal aging prediction',
               color='#bdc3c7', edgecolor='black', lw=0.5)
bars2 = ax.bar(x + width/2, observed_abs, width, label='Observed degradation',
               color=['#3498db', '#e74c3c'], edgecolor='black', lw=0.5)

ax.set_xticks(x)
ax.set_xticklabels(['N52SH\n(Hci=19, 0% Dy)', 'N42EH\n(Hci=30, 1-2% Dy)'])
ax.set_ylabel('Degradation (%)', fontsize=11)
ax.set_title('(c) Dy Inversion Test', fontsize=12, fontweight='bold')
ax.legend(fontsize=9, loc='upper left')
ax.grid(True, alpha=0.3, axis='y')

# annotations
ax.annotate('Thermal aging predicts\nN52SH > N42EH\n(lower Hci = more aging)',
            xy=(0.5, max(thermal)*2), fontsize=8, ha='center',
            style='italic', color='#7f8c8d')
ax.annotate('Observed:\nN42EH > N52SH\nINVERSION',
            xy=(0.5, 0.20), fontsize=9, ha='center',
            fontweight='bold', color='#c0392b',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fadbd8', alpha=0.8))

ax.set_ylim(0, max(observed_abs) * 1.5)

# --- Panel (d): Tunnel-vs-Lab Excess Aging ---
ax = axes[3]

# Compute values for the bar chart
categories = ['N42EH\nexcess', 'N52SH\nexcess', 'NdFeB avg\nexcess', 'Observed\ntunnel-lab']
excess_vals = [excess_list['N42EH'], excess_list['N52SH'], ndfeb_excess, 0.201]
bar_cols = ['#e74c3c', '#3498db', '#8e44ad', '#2c3e50']

bars_d = ax.bar(categories, excess_vals, color=bar_cols, edgecolor='black', lw=0.5)

for bar, val in zip(bars_d, excess_vals):
    ax.text(bar.get_x() + bar.get_width()/2, val + 0.005,
            '{:.4f}%'.format(val) if val < 0.1 else '{:.3f}%'.format(val),
            ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_ylabel('NdFeB-SmCo Differential (%)', fontsize=11)
ax.set_title('(d) Excess Aging: 45C vs 21C\n(Ea=1.0 eV, grade-corrected)',
             fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Add ratio annotation
ax.annotate('{:.0f}x\nshortfall'.format(0.201/ndfeb_excess),
            xy=(2.5, (ndfeb_excess + 0.201)/2), fontsize=14,
            ha='center', fontweight='bold', color='#c0392b',
            arrowprops=dict(arrowstyle='<->', color='#c0392b', lw=2),
            xytext=(2.5, 0.12))

plt.tight_layout()
fig_path = os.path.join(OUTDIR, 'thermal_aging_calculation.png')
plt.savefig(fig_path, dpi=150, bbox_inches='tight')
plt.close()
out('Plot saved: {}'.format(fig_path))

# Save text summary
txt_path = os.path.join(OUTDIR, 'thermal_aging_summary.txt')
with open(txt_path, 'w') as f:
    f.write('\n'.join(lines))
print('\nText summary saved: {}'.format(txt_path))
