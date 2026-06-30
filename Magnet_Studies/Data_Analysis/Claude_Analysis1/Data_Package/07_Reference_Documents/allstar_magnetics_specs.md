# Allstar Magnetics — Material Specifications

Verified from manufacturer datasheets (Allstar Magnetics). All four grades
are used in this study with randomized slot assignments.

## Magnetic Properties

| Parameter | N42EH | N52SH | SmCo33H (Sm2Co17) | SmCo35 (Sm2Co17) |
|-----------|-------|-------|---------------------|---------------------|
| Br (kGs) | 12.8-13.2 | 14.2-14.5 | 11.2-11.5 | 11.6-12.0 |
| Hc (kOe) | >= 11.4 | >= 13.0 | 10.2-10.7 | 10.5-11.2 |
| Hci (kOe) | >= 30 | >= 19 | >= 25 | >= 18 |
| BHmax (MGOe) | 40-43 | 48-52 | 30-33 | 32-35 |
| Max Temp (C) | 190 | 140 | 350 | 300 |

## Temperature Coefficients

| Coefficient | N42EH | N52SH | SmCo33H | SmCo35 |
|-------------|-------|-------|---------|--------|
| alpha(Br) (%/C) | -0.10 | -0.11 | -0.040 | -0.040 |
| alpha(Hc) (%/C) | -0.50 | -0.60 | -0.20 | -0.25 |

alpha(Br) is used for temperature correction of Helmholtz readings.
alpha(Hc) governs coercivity reduction at elevated temperature.

## Physical Properties

| Property | NdFeB | SmCo (Sm2Co17) |
|----------|-------|----------------|
| Curie Temperature (C) | 310-350 | 700-850 |
| Density (g/cm3) | 7.2-7.8 | 8.2-8.5 |
| Thermal Conductivity (W/m C) | 6-8 | 11.6-12.8 |

## Grade Designations
- **N42EH**: NdFeB, BHmax class 42, E = elevated temp, H = high coercivity.
  Uses heavy Dy addition (~6-10 wt%) for high Hci.
- **N52SH**: NdFeB, BHmax class 52, S = standard temp, H = high coercivity.
  Less Dy (~0-3 wt%), highest Br of the four grades.
- **SmCo33H**: Samarium-cobalt (Sm2Co17), BHmax 33, H = high coercivity.
  Most radiation-resistant grade in this study.
- **SmCo35**: Samarium-cobalt (Sm2Co17), BHmax 35, standard coercivity.
  Higher Br but lower Hci than SmCo33H.

## Radiation Resistance (Predicted)

Critical temperature rise (delta_T_crit) at which coercivity drops to the
operating point, calculated from Hci and alpha(Hc). Higher = more resistant.

| Grade | delta_T_crit @ 5 kOe load | delta_T_crit @ 15 kOe load |
|-------|---------------------------|----------------------------|
| SmCo33H | 400 C | 200 C |
| SmCo35 | 289 C | 67 C |
| N42EH | 167 C | 100 C |
| N52SH | 123 C | 35 C |

Predicted ranking (most to least resistant): SmCo33H > SmCo35 > N42EH > N52SH.
Observed: SmCo33H and SmCo35 both near zero change; N42EH degraded more than
N52SH (inverted from prediction, possibly due to higher Dy content in N42EH).
