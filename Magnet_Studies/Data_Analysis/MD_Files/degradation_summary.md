# Preliminary Degradation Summary

**Status**: Preliminary — more data collection and error analysis pending
**Generated**: 2026-03-10
**Reference temperature**: 20.0 °C

## Error Bar Methodology

Each reported % change carries a combined uncertainty computed from two independent sources added in quadrature:

1. **Baseline uncertainty (σ_baseline)**: The standard error on the mean of pre-deployment temperature-corrected readings. With N baseline measurements, σ_baseline = std(baseline readings) / √N. This captures how well we know the starting value.

2. **Temperature correction uncertainty (σ_temp)**: Propagated from the spread of the 3 Teslameter face temperatures (front, side, top) on the measurement date. The correction formula B_corr = B_raw / (1 + α(T−20°C)) introduces uncertainty when T varies across faces. This is computed as |B_raw × α × σ_T / (1 + α(T−20))²|.

3. **Combined**: σ_total = √(σ_baseline² + σ_temp²), expressed as % of baseline.

For group averages (by region or material), the reported uncertainty is the **larger** of:
- The standard error of the mean across samples (SEM = σ/√N), or
- The mean per-sample measurement uncertainty

This ensures we do not underestimate uncertainty when sample scatter is small but individual measurements have significant error bars.

## Y-Plate Summary by Material

| Material | N | Mean Δ (%) | ± Unc (%) | Min (%) | Max (%) |
|----------|---|-----------|-----------|---------|---------|
| N42EH | 30 | -0.333 | ±0.034 | -0.855 | -0.113 |
| N52SH | 30 | +0.118 | ±0.379 | -0.676 | +11.072 |
| SmCo33H | 30 | -0.193 | ±0.209 | -6.206 | +0.376 |
| SmCo35 | 30 | -0.077 | ±0.031 | -0.500 | +0.394 |

## Y-Plate Summary by Region

| Region | N | Mean Δ (%) | ± Unc (%) | Min (%) | Max (%) |
|--------|---|-----------|-----------|---------|---------|
| SE Arc | 20 | -0.427 | ±0.305 | -6.206 | +0.074 |
| NE Arc | 20 | -0.295 | ±0.062 | -0.855 | +0.376 |
| NW Arc | 20 | +0.401 | ±0.564 | -0.453 | +11.072 |
| SW Arc | 20 | -0.273 | ±0.057 | -0.806 | +0.048 |
| North Linac | 16 | -0.039 | ±0.047 | -0.414 | +0.394 |
| South Linac | 16 | -0.051 | ±0.040 | -0.269 | +0.369 |
| Labyrinth | 8 | -0.151 | ±0.044 | -0.287 | +0.052 |

## Y-Plate Summary by Region × Material

| Region | Material | N | Mean Δ (%) | ± Unc (%) |
|--------|----------|---|-----------|-----------|
| SE Arc | N42EH | 5 | -0.223 | ±0.050 |
| SE Arc | N52SH | 5 | -0.182 | ±0.029 |
| SE Arc | SmCo33H | 5 | -1.251 | ±1.239 |
| SE Arc | SmCo35 | 5 | -0.052 | ±0.042 |
| NE Arc | N42EH | 5 | -0.508 | ±0.088 |
| NE Arc | N52SH | 5 | -0.469 | ±0.082 |
| NE Arc | SmCo33H | 5 | +0.033 | ±0.089 |
| NE Arc | SmCo35 | 5 | -0.238 | ±0.054 |
| NW Arc | N42EH | 5 | -0.370 | ±0.027 |
| NW Arc | N52SH | 5 | +1.953 | ±2.280 |
| NW Arc | SmCo33H | 5 | +0.099 | ±0.082 |
| NW Arc | SmCo35 | 5 | -0.078 | ±0.042 |
| SW Arc | N42EH | 5 | -0.439 | ±0.124 |
| SW Arc | N52SH | 5 | -0.379 | ±0.117 |
| SW Arc | SmCo33H | 5 | -0.083 | ±0.069 |
| SW Arc | SmCo35 | 5 | -0.191 | ±0.090 |
| North Linac | N42EH | 4 | -0.254 | ±0.068 |
| North Linac | N52SH | 4 | -0.053 | ±0.025 |
| North Linac | SmCo33H | 4 | -0.008 | ±0.028 |
| North Linac | SmCo35 | 4 | +0.158 | ±0.093 |
| South Linac | N42EH | 4 | -0.176 | ±0.024 |
| South Linac | N52SH | 4 | -0.112 | ±0.055 |
| South Linac | SmCo33H | 4 | +0.091 | ±0.119 |
| South Linac | SmCo35 | 4 | -0.009 | ±0.023 |
| Labyrinth | N42EH | 2 | -0.280 | ±0.008 |
| Labyrinth | N52SH | 2 | -0.208 | ±0.011 |
| Labyrinth | SmCo33H | 2 | -0.054 | ±0.107 |
| Labyrinth | SmCo35 | 2 | -0.061 | ±0.066 |

## Arc Degradation by Line Position

Line position in arc stacks (1=top to 5=bottom) corresponds to different beam energy passes and potentially different radiation levels.

| Line | N | Mean Δ (%) | ± Unc (%) | Min (%) | Max (%) |
|------|---|-----------|-----------|---------|---------|
| 1 | 16 | -0.315 | ±0.091 | -0.855 | +0.376 |
| 2 | 16 | -0.231 | ±0.053 | -0.566 | +0.069 |
| 3 | 16 | -0.182 | ±0.048 | -0.542 | +0.291 |
| 4 | 16 | -0.152 | ±0.040 | -0.459 | +0.074 |
| 5 | 16 | +0.137 | ±0.821 | -6.206 | +11.072 |

## H-Plate (Pair Assembly) Summary

### By Material

| Material | N | Mean Δ (%) | ± Unc (%) | Min (%) | Max (%) |
|----------|---|-----------|-----------|---------|---------|
| NdFeB | 42 | +1.182 | ±0.229 | -0.053 | +2.339 |
| SmCo | 48 | +0.372 | ±0.162 | -0.336 | +1.000 |

### By Assembly Configuration

| Config | N | Mean Δ (%) | ± Unc (%) | Notes |
|--------|---|-----------|-----------|-------|
| Alpha | 30 | +0.757 | ±0.170 |  |
| Gamma | 30 | +0.666 | ±0.219 |  |
| Delta | 30 | +0.827 | ±0.191 |  |

### By Region

| Region | N | Mean Δ (%) | ± Unc (%) |
|--------|---|-----------|-----------|
| SE Arc | 15 | +1.129 | ±0.339 |
| NE Arc | 15 | +0.378 | ±0.166 |
| NW Arc | 15 | +1.326 | ±0.143 |
| SW Arc | 15 | +0.223 | ±0.191 |
| North Linac | 12 | +0.877 | ±0.156 |
| South Linac | 12 | +0.697 | ±0.242 |
| Labyrinth | 6 | +0.463 | ±0.109 |

## Individual Y-Plate Results (All Samples)

| Sample | Material | Region | Line | Baseline (mWC) | Latest (mWC) | Δ (%) | ± (%) | Date |
|--------|----------|--------|------|----------------|--------------|-------|-------|------|
| Y-40-4 | SmCo33H | SE Arc | 5 | 1.1109 | 1.0419 | -6.206 | ±0.001 | 2026-01-08 |
| Y-39-1 | N42EH | NE Arc | 1 | 1.1843 | 1.1742 | -0.855 | ±0.020 | 2026-01-08 |
| Y-13-4 | N42EH | SW Arc | 1 | 1.1749 | 1.1654 | -0.806 | ±0.008 | 2026-01-12 |
| Y-39-3 | N52SH | NE Arc | 1 | 1.3136 | 1.3047 | -0.676 | ±0.022 | 2026-01-08 |
| Y-13-2 | N52SH | SW Arc | 1 | 1.3124 | 1.3035 | -0.675 | ±0.012 | 2026-01-12 |
| Y-9-2 | N52SH | NE Arc | 5 | 1.3181 | 1.3100 | -0.614 | ±0.001 | 2026-01-08 |
| Y-32-1 | N52SH | SW Arc | 2 | 1.3120 | 1.3045 | -0.566 | ±0.001 | 2026-01-12 |
| Y-19-1 | N42EH | SW Arc | 3 | 1.1783 | 1.1719 | -0.542 | ±0.001 | 2026-01-12 |
| Y-32-3 | N42EH | SW Arc | 2 | 1.1773 | 1.1711 | -0.522 | ±0.003 | 2026-01-12 |
| Y-13-3 | SmCo35 | SW Arc | 1 | 1.0819 | 1.0764 | -0.500 | ±0.003 | 2026-01-12 |
| Y-7-3 | N52SH | NE Arc | 2 | 1.3127 | 1.3065 | -0.473 | ±0.003 | 2026-01-08 |
| Y-21-4 | N42EH | NE Arc | 4 | 1.1810 | 1.1756 | -0.459 | ±0.002 | 2026-01-08 |
| Y-38-4 | N52SH | NW Arc | 1 | 1.3114 | 1.3055 | -0.453 | ±0.004 | 2026-01-08 |
| Y-7-1 | N42EH | NE Arc | 2 | 1.1758 | 1.1705 | -0.452 | ±0.000 | 2026-01-08 |
| Y-6-2 | N42EH | NW Arc | 2 | 1.1731 | 1.1679 | -0.443 | ±0.002 | 2025-10-23 |
| Y-19-3 | N52SH | SW Arc | 3 | 1.3101 | 1.3045 | -0.429 | ±0.006 | 2026-01-12 |
| Y-15-1 | N42EH | SE Arc | 1 | 1.1840 | 1.1790 | -0.421 | ±0.007 | 2026-01-08 |
| Y-4-3 | N42EH | North Linac | — | 1.1902 | 1.1853 | -0.414 | ±0.005 | 2026-01-12 |
| Y-9-4 | N42EH | NE Arc | 5 | 1.1777 | 1.1729 | -0.406 | ±0.002 | 2026-01-08 |
| Y-25-4 | N42EH | NW Arc | 4 | 1.1789 | 1.1744 | -0.385 | ±0.004 | 2026-01-08 |
| Y-38-2 | N42EH | NW Arc | 1 | 1.1842 | 1.1798 | -0.373 | ±0.006 | 2026-01-08 |
| Y-34-2 | N42EH | NW Arc | 5 | 1.1852 | 1.1808 | -0.372 | ±0.002 | 2026-01-08 |
| Y-18-2 | N42EH | NE Arc | 3 | 1.1756 | 1.1712 | -0.369 | ±0.000 | 2026-01-08 |
| Y-39-4 | SmCo35 | NE Arc | 1 | 1.0823 | 1.0783 | -0.366 | ±0.014 | 2026-01-08 |
| Y-21-2 | N52SH | NE Arc | 4 | 1.3106 | 1.3059 | -0.353 | ±0.002 | 2026-01-08 |
| Y-25-2 | N52SH | NW Arc | 4 | 1.3129 | 1.3083 | -0.351 | ±0.003 | 2026-01-08 |
| Y-13-1 | SmCo33H | SW Arc | 1 | 1.0409 | 1.0374 | -0.336 | ±0.019 | 2026-01-12 |
| Y-18-1 | SmCo35 | NE Arc | 3 | 1.0814 | 1.0779 | -0.320 | ±0.001 | 2026-01-08 |
| Y-17-4 | N42EH | North Linac | — | 1.1777 | 1.1739 | -0.319 | ±0.005 | 2026-01-12 |
| Y-20-3 | N42EH | Labyrinth | — | 1.1753 | 1.1719 | -0.287 | ±0.004 | 2026-01-12 |
| Y-36-3 | N42EH | NW Arc | 3 | 1.1846 | 1.1813 | -0.277 | ±0.006 | 2026-01-08 |
| Y-32-2 | SmCo35 | SW Arc | 2 | 1.0813 | 1.0783 | -0.273 | ±0.001 | 2026-01-12 |
| Y-12-3 | N42EH | Labyrinth | — | 1.1844 | 1.1812 | -0.272 | ±0.005 | 2026-01-12 |
| Y-1-2 | N52SH | South Linac | — | 1.3121 | 1.3086 | -0.269 | ±0.007 | 2026-01-12 |
| Y-36-1 | N52SH | NW Arc | 3 | 1.3129 | 1.3094 | -0.264 | ±0.006 | 2026-01-08 |
| Y-9-3 | SmCo35 | NE Arc | 5 | 1.0795 | 1.0767 | -0.261 | ±0.000 | 2026-01-08 |
| Y-3-3 | N52SH | SE Arc | 2 | 1.3130 | 1.3097 | -0.251 | ±0.014 | 2026-01-08 |
| Y-40-1 | N52SH | SE Arc | 5 | 1.3144 | 1.3112 | -0.243 | ±0.008 | 2026-01-08 |
| Y-6-4 | N52SH | NW Arc | 2 | 1.3102 | 1.3070 | -0.240 | ±0.005 | 2026-01-08 |
| Y-18-4 | N52SH | NE Arc | 3 | 1.3097 | 1.3067 | -0.229 | ±0.004 | 2026-01-08 |
| Y-30-2 | N42EH | South Linac | — | 1.1827 | 1.1800 | -0.227 | ±0.007 | 2026-01-12 |
| Y-25-3 | SmCo35 | NW Arc | 4 | 1.0827 | 1.0804 | -0.220 | ±0.008 | 2026-01-08 |
| Y-20-1 | N52SH | Labyrinth | — | 1.3144 | 1.3115 | -0.219 | ±0.008 | 2026-01-12 |
| Y-40-3 | N42EH | SE Arc | 5 | 1.1867 | 1.1843 | -0.202 | ±0.003 | 2026-01-08 |
| Y-12-1 | N52SH | Labyrinth | — | 1.3144 | 1.3118 | -0.197 | ±0.013 | 2026-01-12 |
| Y-24-3 | N42EH | South Linac | — | 1.1852 | 1.1830 | -0.190 | ±0.012 | 2026-01-12 |
| Y-7-4 | SmCo35 | NE Arc | 2 | 1.0825 | 1.0805 | -0.185 | ±0.003 | 2026-01-08 |
| Y-5-4 | N42EH | South Linac | — | 1.1809 | 1.1789 | -0.173 | ±0.008 | 2026-01-12 |
| Y-15-3 | N52SH | SE Arc | 1 | 1.3122 | 1.3099 | -0.173 | ±0.006 | 2026-01-08 |
| Y-3-1 | N42EH | SE Arc | 2 | 1.1750 | 1.1730 | -0.170 | ±0.009 | 2026-01-08 |
| Y-23-1 | N42EH | SE Arc | 3 | 1.1777 | 1.1757 | -0.170 | ±0.006 | 2026-01-08 |
| Y-30-3 | SmCo33H | South Linac | — | 1.0390 | 1.0373 | -0.169 | ±0.002 | 2026-01-12 |
| Y-10-2 | N42EH | SW Arc | 4 | 1.1740 | 1.1720 | -0.168 | ±0.044 | 2026-01-12 |
| Y-3-4 | SmCo35 | SE Arc | 2 | 1.0813 | 1.0795 | -0.167 | ±0.002 | 2026-01-08 |
| Y-11-3 | N52SH | SW Arc | 5 | 1.3136 | 1.3115 | -0.165 | ±0.012 | 2026-01-12 |
| Y-12-4 | SmCo33H | Labyrinth | — | 1.0399 | 1.0382 | -0.161 | ±0.005 | 2026-01-12 |
| Y-22-2 | N42EH | North Linac | — | 1.1779 | 1.1761 | -0.157 | ±0.010 | 2026-01-12 |
| Y-11-1 | N42EH | SW Arc | 5 | 1.1775 | 1.1757 | -0.155 | ±0.023 | 2026-01-12 |
| Y-26-2 | N42EH | SE Arc | 4 | 1.1784 | 1.1766 | -0.153 | ±0.001 | 2026-01-08 |
| Y-26-4 | N52SH | SE Arc | 4 | 1.3116 | 1.3098 | -0.137 | ±0.006 | 2026-01-08 |
| Y-20-2 | SmCo35 | Labyrinth | — | 1.0798 | 1.0785 | -0.127 | ±0.002 | 2026-01-12 |
| Y-16-3 | N42EH | North Linac | — | 1.1747 | 1.1733 | -0.126 | ±0.006 | 2026-01-12 |
| Y-34-3 | SmCo33H | NW Arc | 5 | 1.0413 | 1.0400 | -0.123 | ±0.001 | 2026-01-08 |
| Y-19-4 | SmCo35 | SW Arc | 3 | 1.0812 | 1.0799 | -0.119 | ±0.001 | 2026-01-12 |
| Y-21-1 | SmCo33H | NE Arc | 4 | 1.0396 | 1.0384 | -0.118 | ±0.001 | 2026-01-08 |
| Y-19-2 | SmCo33H | SW Arc | 3 | 1.0413 | 1.0401 | -0.118 | ±0.000 | 2026-01-12 |
| Y-1-4 | N42EH | South Linac | — | 1.1782 | 1.1769 | -0.113 | ±0.006 | 2026-01-12 |
| Y-22-4 | N52SH | North Linac | — | 1.3103 | 1.3089 | -0.110 | ±0.010 | 2026-01-12 |
| Y-15-4 | SmCo35 | SE Arc | 1 | 1.0798 | 1.0787 | -0.107 | ±0.002 | 2026-01-08 |
| Y-23-3 | N52SH | SE Arc | 3 | 1.3133 | 1.3119 | -0.106 | ±0.007 | 2026-01-08 |
| Y-7-2 | SmCo33H | NE Arc | 2 | 1.0401 | 1.0391 | -0.099 | ±0.003 | 2026-01-08 |
| Y-36-2 | SmCo35 | NW Arc | 3 | 1.0844 | 1.0834 | -0.095 | ±0.001 | 2026-01-08 |
| Y-24-1 | N52SH | South Linac | — | 1.3117 | 1.3105 | -0.089 | ±0.014 | 2026-01-12 |
| Y-34-1 | SmCo35 | NW Arc | 5 | 1.0861 | 1.0852 | -0.086 | ±0.008 | 2026-01-08 |
| Y-23-2 | SmCo33H | SE Arc | 3 | 1.0399 | 1.0390 | -0.086 | ±0.001 | 2026-01-08 |
| Y-5-2 | N52SH | South Linac | — | 1.3135 | 1.3124 | -0.082 | ±0.009 | 2026-01-12 |
| Y-17-2 | N52SH | North Linac | — | 1.3120 | 1.3109 | -0.080 | ±0.013 | 2026-01-12 |
| Y-26-3 | SmCo33H | SE Arc | 4 | 1.0377 | 1.0370 | -0.071 | ±0.001 | 2026-01-08 |
| Y-23-4 | SmCo35 | SE Arc | 3 | 1.0804 | 1.0796 | -0.069 | ±0.001 | 2026-01-08 |
| Y-11-4 | SmCo35 | SW Arc | 5 | 1.0850 | 1.0843 | -0.065 | ±0.001 | 2026-01-12 |
| Y-4-4 | SmCo33H | North Linac | — | 1.0414 | 1.0407 | -0.062 | ±0.000 | 2026-01-12 |
| Y-10-4 | N52SH | SW Arc | 4 | 1.3052 | 1.3044 | -0.062 | ±0.008 | 2026-01-12 |
| Y-30-1 | SmCo35 | South Linac | — | 1.0812 | 1.0806 | -0.058 | ±0.001 | 2026-01-12 |
| Y-21-3 | SmCo35 | NE Arc | 4 | 1.0834 | 1.0828 | -0.057 | ±0.002 | 2026-01-08 |
| Y-17-3 | SmCo35 | North Linac | — | 1.0804 | 1.0799 | -0.048 | ±0.002 | 2026-01-12 |
| Y-22-3 | SmCo33H | North Linac | — | 1.0428 | 1.0424 | -0.041 | ±0.003 | 2026-01-12 |
| Y-24-4 | SmCo33H | South Linac | — | 1.0392 | 1.0390 | -0.027 | ±0.004 | 2026-01-12 |
| Y-38-1 | SmCo35 | NW Arc | 1 | 1.0813 | 1.0810 | -0.025 | ±0.002 | 2026-01-08 |
| Y-5-3 | SmCo35 | South Linac | — | 1.0806 | 1.0804 | -0.024 | ±0.004 | 2026-01-12 |
| Y-4-1 | N52SH | North Linac | — | 1.3113 | 1.3110 | -0.024 | ±0.016 | 2026-01-12 |
| Y-25-1 | SmCo33H | NW Arc | 4 | 1.0450 | 1.0448 | -0.024 | ±0.001 | 2026-01-08 |
| Y-30-4 | N52SH | South Linac | — | 1.3056 | 1.3055 | -0.009 | ±0.004 | 2026-01-12 |
| Y-32-4 | SmCo33H | SW Arc | 2 | 1.0414 | 1.0413 | -0.008 | ±0.001 | 2026-01-12 |
| Y-18-3 | SmCo33H | NE Arc | 3 | 1.0403 | 1.0403 | -0.005 | ±0.001 | 2026-01-08 |
| Y-1-3 | SmCo35 | South Linac | — | 1.0858 | 1.0857 | -0.003 | ±0.002 | 2026-01-12 |
| Y-11-2 | SmCo33H | SW Arc | 5 | 1.0408 | 1.0408 | +0.001 | ±0.002 | 2026-01-12 |
| Y-16-1 | N52SH | North Linac | — | 1.3131 | 1.3131 | +0.001 | ±0.013 | 2026-01-12 |
| Y-10-1 | SmCo35 | SW Arc | 4 | 1.0845 | 1.0846 | +0.004 | ±0.003 | 2026-01-12 |
| Y-12-2 | SmCo35 | Labyrinth | — | 1.0813 | 1.0813 | +0.005 | ±0.002 | 2026-01-12 |
| Y-17-1 | SmCo33H | North Linac | — | 1.0440 | 1.0441 | +0.006 | ±0.001 | 2026-01-12 |
| Y-40-2 | SmCo35 | SE Arc | 5 | 1.0842 | 1.0842 | +0.007 | ±0.002 | 2026-01-08 |
| Y-9-1 | SmCo33H | NE Arc | 5 | 1.0374 | 1.0375 | +0.013 | ±0.004 | 2026-01-08 |
| Y-6-1 | SmCo35 | NW Arc | 2 | 1.0831 | 1.0835 | +0.035 | ±0.001 | 2026-01-08 |
| Y-3-2 | SmCo33H | SE Arc | 2 | 1.0378 | 1.0382 | +0.043 | ±0.002 | 2026-01-08 |
| Y-10-3 | SmCo33H | SW Arc | 4 | 1.0354 | 1.0359 | +0.048 | ±0.170 | 2026-01-12 |
| Y-24-2 | SmCo35 | South Linac | — | 1.0799 | 1.0804 | +0.049 | ±0.003 | 2026-01-12 |
| Y-20-4 | SmCo33H | Labyrinth | — | 1.0419 | 1.0424 | +0.052 | ±0.002 | 2026-01-12 |
| Y-16-4 | SmCo33H | North Linac | — | 1.0410 | 1.0416 | +0.063 | ±0.003 | 2026-01-12 |
| Y-15-2 | SmCo33H | SE Arc | 1 | 1.0383 | 1.0390 | +0.064 | ±0.002 | 2026-01-08 |
| Y-6-3 | SmCo33H | NW Arc | 2 | 1.0427 | 1.0435 | +0.069 | ±0.001 | 2026-01-08 |
| Y-26-1 | SmCo35 | SE Arc | 4 | 1.0814 | 1.0822 | +0.074 | ±0.001 | 2026-01-08 |
| Y-16-2 | SmCo35 | North Linac | — | 1.0821 | 1.0831 | +0.090 | ±0.002 | 2026-01-12 |
| Y-1-1 | SmCo33H | South Linac | — | 1.0379 | 1.0399 | +0.193 | ±0.006 | 2026-01-12 |
| Y-22-1 | SmCo35 | North Linac | — | 1.0805 | 1.0826 | +0.195 | ±0.004 | 2026-01-12 |
| Y-38-3 | SmCo33H | NW Arc | 1 | 1.0363 | 1.0392 | +0.280 | ±0.003 | 2026-01-08 |
| Y-36-4 | SmCo33H | NW Arc | 3 | 1.0366 | 1.0396 | +0.291 | ±0.000 | 2026-01-08 |
| Y-5-1 | SmCo33H | South Linac | — | 1.0380 | 1.0418 | +0.369 | ±0.004 | 2026-01-12 |
| Y-39-2 | SmCo33H | NE Arc | 1 | 1.0342 | 1.0381 | +0.376 | ±0.005 | 2026-01-08 |
| Y-4-2 | SmCo35 | North Linac | — | 1.0772 | 1.0815 | +0.394 | ±0.003 | 2026-01-12 |
| Y-34-4 | N52SH | NW Arc | 5 | 1.1797 | 1.3103 | +11.072 | ±0.007 | 2026-01-08 |

## Key Observations

- **Largest degradation**: Y-40-4 (SmCo33H, SE Arc) at -6.206 ± 0.001%
- **Largest positive shift**: Y-34-4 (N52SH, NW Arc) at +11.072 ± 0.007%
- **Samples with degradation exceeding 1σ**: 95 / 120
- **Samples with >0.5% degradation**: 10 / 120

## Caveats

- These are **preliminary** results. More measurements are being collected.
- Radiation dose data is not yet complete; dose-response correlation pending.
- The temperature coefficient α(Br) carries its own systematic uncertainty (not included in error bars — it would shift all values of a given material grade together).
- Pre-deployment Teslameter data used the broken Hall probe; only Helmholtz baselines with temperature correction from working probe dates are used.
- Beta (antiparallel) pair assembly Helmholtz readings are known to be unreliable due to multipole field character.
- Lab-based control comparisons are not yet included (data still being collected).
