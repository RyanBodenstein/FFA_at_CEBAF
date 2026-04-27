# ORIGINAL Results — BEFORE Temperature Correction Fix
# Saved 2026-03-31 as reference/backup
# These are the values from manager_summary_v3.py BEFORE any changes to load_all()

## Original Headline Numbers (biased Teslameter probe temps ~24.5-25.4°C)
| Material | Mean ± SEM | Significance | N |
|----------|-----------|-------------|---|
| N42EH | -0.333% ± 0.034% | 9.8σ | 30 |
| N52SH | -0.260% ± 0.037% | 7.1σ | 29 |
| SmCo33H | +0.012% ± 0.030% | 0.4σ | 29 |
| SmCo35 | -0.077% ± 0.031% | 2.5σ | 30 |

## Original Gain-Immune Differential
NdFeB − SmCo: -0.266% ± 0.027% (9.7σ, N=30 plates)

## Original Gain Systematic
- Cleaned: ±0.1239%
- Uncleaned: ±0.2483%

## Original Double Ratio (Aug 27 → Jan 12)
+0.067% ± 0.039% (1.7σ, N=15 plates)

## Original Teslameter Field Summary
- N42EH: -0.085% ± 0.103% (0.8σ, N=30)
- N52SH: +0.205% ± 0.091% (2.2σ, N=29)
- SmCo33H: -0.012% ± 0.070% (0.2σ, N=29)
- SmCo35: -0.174% ± 0.116% (1.5σ, N=30)

## Original Session Offsets (raw, relative to Nov 5 2024)
- 2025-04-23: -0.552% ± 0.059% (N=27)
- 2025-05-07: -0.563% ± 0.052% (N=69)
- 2025-05-21: -0.497% ± 0.053% (N=56)
- 2025-06-11: -0.654% ± 0.068% (N=32)
- 2025-06-17: -0.744% ± 0.098% (N=22)

## How to reproduce these numbers
Revert the Y_BASELINE_TEMP_LOOKUP changes in manager_summary_v3.py load_all().
Specifically, change the pre-deployment branch back to:
```python
for dt, h_raw in mwc:
    key = (sample, dt.strftime('%Y-%m-%d'))
    if key not in temp_final:
        continue
    t_mean, _ = temp_final[key]
    h_corr = h_raw / (1 + alpha * (t_mean - T_REF))
    if dt < TUNNEL_START:
        pre_corr.append(h_corr)
    else:
        tunnel_series.append((dt, h_corr))
```
(i.e., use the raw Teslameter temps for pre-deployment dates, no lookup override)
