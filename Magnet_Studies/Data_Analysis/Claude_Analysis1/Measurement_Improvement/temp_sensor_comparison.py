#!/usr/bin/env python3
"""
Temperature Sensor Cross-Calibration: Arduino AM2302 vs Teslameter Probe
========================================================================

Parses all *_helmholtzTemp.dat files from the June 2-3, 2026 Helmholtz
measurement campaign, matches each with the closest Teslameter top-face
reading (same sample, within 5 minutes), and produces:

  TC1: Arduino vs Teslameter scatter plot (1:1 line)
  TC2: Residual (Teslameter - Arduino) vs Arduino temperature
  TC3: Time-of-day comparison
  TC4: Humidity effect on temperature disagreement

Also produces:
  temp_comparison_results.csv   -- per-sample matched pairs
  temp_comparison_summary.txt   -- fleet statistics

Usage:
  python3 Measurement_Improvement/temp_sensor_comparison.py

Data sources:
  Arduino:     2026_Data_Run/2026-6-3-Helmholtz/*_helmholtzTemp.dat
  Teslameter:  2026_Data_Run/2026-06-02_Teslameter/*_top.dat
               2026_Data_Run/2026-06-03_Teslameter/*_top.dat

AM2302 specs: +/-0.5 C accuracy, +/-2-3% RH, 0.1 C resolution, ~2s response.
Teslameter probe: integrated CMOS sensor, reads probe junction temperature.
"""

import os
import re
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from collections import defaultdict

# ---- Paths ----------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = SCRIPT_DIR  # output plots and CSV to Measurement_Improvement/

HELM_DIR = os.path.join(PROJECT_DIR, '2026_Data_Run', '2026-6-3-Helmholtz')
TESLA_DIRS = [
    os.path.join(PROJECT_DIR, '2026_Data_Run', '2026-06-02_Teslameter'),
    os.path.join(PROJECT_DIR, '2026_Data_Run', '2026-06-03_Teslameter'),
]

MAX_TIME_GAP = timedelta(minutes=5)  # max allowed time gap for matching

# ---- Parsers --------------------------------------------------------------

def parse_helmholtz_temp(filepath):
    """Parse a *_helmholtzTemp.dat file.

    Returns list of dicts with keys:
      datetime, dosimeter, rod, arduino_temp_C, humidity_pct
    """
    rows = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Format: date\ttime\tdosimeter\trod\ttemp degC\thumidity %
            # Sometimes leading space
            m = re.match(
                r'(\d{4}-\d{2}-\d{2})\t(\d{2}:\d{2}:\d{2})\t'
                r'(\S+)\t(\S+)\t'
                r'([\d.]+)\s*degC\t'
                r'([\d.]+)\s*%',
                line
            )
            if m:
                dt = datetime.strptime(
                    '%s %s' % (m.group(1), m.group(2)),
                    '%Y-%m-%d %H:%M:%S'
                )
                rows.append({
                    'datetime': dt,
                    'dosimeter': m.group(3),
                    'rod': m.group(4),
                    'arduino_temp_C': float(m.group(5)),
                    'humidity_pct': float(m.group(6)),
                })
    return rows


def parse_teslameter_top(filepath):
    """Parse a Teslameter *_top.dat file.

    Returns list of dicts with keys:
      datetime, dosimeter, rod, Bx, By, Bz, tesla_temp_C
    """
    rows = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Format: date\ttime\tdosimeter\trod\tBx\tBy\tBz\ttemp
            # Sometimes date-time (hyphen instead of tab)
            m = re.match(
                r'(\d{4}-\d{2}-\d{2})[\t-](\d{2}:\d{2}:\d{2})\t'
                r'(\S+)\t(\S+)\t'
                r'(-?[\d.]+)\t(-?[\d.]+)\t(-?[\d.]+)\t([\d.]+)',
                line
            )
            if m:
                dt = datetime.strptime(
                    '%s %s' % (m.group(1), m.group(2)),
                    '%Y-%m-%d %H:%M:%S'
                )
                rows.append({
                    'datetime': dt,
                    'dosimeter': m.group(3),
                    'rod': m.group(4),
                    'Bx': float(m.group(5)),
                    'By': float(m.group(6)),
                    'Bz': float(m.group(7)),
                    'tesla_temp_C': float(m.group(8)),
                })
    return rows


# ---- Data Loading ---------------------------------------------------------

def extract_sample_id(filename):
    """Extract sample ID from filename like Y-20-1_helmholtzTemp.dat."""
    base = os.path.basename(filename)
    # Remove suffix
    for suffix in ('_helmholtzTemp.dat', '_top.dat', '_front.dat', '_side.dat'):
        if base.endswith(suffix):
            return base[:-len(suffix)]
    return base.rsplit('.', 1)[0]


def load_all_arduino():
    """Load all Arduino helmholtzTemp readings from June Helmholtz dir.

    Returns dict: sample_id -> list of parsed rows
    """
    data = defaultdict(list)
    pattern = os.path.join(HELM_DIR, '*_helmholtzTemp.dat')
    import glob as g
    for fp in sorted(g.glob(pattern)):
        sid = extract_sample_id(fp)
        rows = parse_helmholtz_temp(fp)
        data[sid].extend(rows)
    return data


def load_all_teslameter():
    """Load all Teslameter top-face readings from June Teslameter dirs.

    Returns dict: sample_id -> list of parsed rows (only June 2026 dates)
    """
    data = defaultdict(list)
    import glob as g
    for tdir in TESLA_DIRS:
        for fp in sorted(g.glob(os.path.join(tdir, '*_top.dat'))):
            sid = extract_sample_id(fp)
            rows = parse_teslameter_top(fp)
            # Keep only June 2026 rows
            june_rows = [r for r in rows
                         if r['datetime'].year == 2026 and r['datetime'].month == 6]
            data[sid].extend(june_rows)
    # Deduplicate (June 3 dir often contains same data as June 2 dir)
    for sid in data:
        seen = set()
        unique = []
        for r in data[sid]:
            key = (r['datetime'], r['tesla_temp_C'])
            if key not in seen:
                seen.add(key)
                unique.append(r)
        data[sid] = unique
    return data


# ---- Matching -------------------------------------------------------------

def match_readings(arduino_data, tesla_data):
    """Match Arduino and Teslameter readings by sample ID and timestamp.

    For each Arduino reading, find the closest Teslameter reading for the
    same sample within MAX_TIME_GAP. If multiple Teslameter readings exist
    (e.g., from repeated Y-14 measurements), match to the closest in time.

    Returns list of matched dicts.
    """
    matched = []
    n_unmatched = 0

    for sid in sorted(arduino_data.keys()):
        ard_rows = arduino_data[sid]
        tes_rows = tesla_data.get(sid, [])

        if not tes_rows:
            n_unmatched += len(ard_rows)
            continue

        for ar in ard_rows:
            # Find closest Teslameter reading
            best = None
            best_gap = None
            for tr in tes_rows:
                gap = abs((tr['datetime'] - ar['datetime']).total_seconds())
                if gap <= MAX_TIME_GAP.total_seconds():
                    if best is None or gap < best_gap:
                        best = tr
                        best_gap = gap

            if best is not None:
                matched.append({
                    'sample_id': sid,
                    'date': ar['datetime'].strftime('%Y-%m-%d'),
                    'arduino_time': ar['datetime'].strftime('%H:%M:%S'),
                    'tesla_time': best['datetime'].strftime('%H:%M:%S'),
                    'time_gap_sec': best_gap,
                    'arduino_temp_C': ar['arduino_temp_C'],
                    'tesla_temp_C': best['tesla_temp_C'],
                    'residual_C': best['tesla_temp_C'] - ar['arduino_temp_C'],
                    'humidity_pct': ar['humidity_pct'],
                    'hour_of_day': ar['datetime'].hour + ar['datetime'].minute / 60.0,
                    'Bx': best['Bx'],
                    'By': best['By'],
                    'Bz': best['Bz'],
                })
            else:
                n_unmatched += 1

    print("  Matched: %d pairs" % len(matched))
    print("  Unmatched Arduino readings (no Teslameter within 5 min): %d" % n_unmatched)
    return matched


# ---- Analysis & Plots -----------------------------------------------------

def write_csv(matched, outpath):
    """Write matched pairs to CSV."""
    if not matched:
        print("  No matched data to write.")
        return
    fields = ['sample_id', 'date', 'arduino_time', 'tesla_time',
              'time_gap_sec', 'arduino_temp_C', 'tesla_temp_C',
              'residual_C', 'humidity_pct', 'hour_of_day']
    with open(outpath, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for row in matched:
            w.writerow(row)
    print("  Wrote %s (%d rows)" % (os.path.basename(outpath), len(matched)))


def plot_tc1_scatter(matched, outpath):
    """TC1: Arduino vs Teslameter scatter plot with 1:1 line."""
    ard = np.array([m['arduino_temp_C'] for m in matched])
    tes = np.array([m['tesla_temp_C'] for m in matched])

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.scatter(ard, tes, alpha=0.3, s=15, c='steelblue', edgecolors='none')

    # 1:1 line
    lo = min(ard.min(), tes.min()) - 1
    hi = max(ard.max(), tes.max()) + 1
    ax.plot([lo, hi], [lo, hi], 'k--', linewidth=1, label='1:1 line')

    # Linear fit
    coeffs = np.polyfit(ard, tes, 1)
    xfit = np.linspace(lo, hi, 100)
    yfit = np.polyval(coeffs, xfit)
    ax.plot(xfit, yfit, 'r-', linewidth=1.5,
            label='Fit: T_tesla = %.3f * T_ard + %.2f' % (coeffs[0], coeffs[1]))

    ax.set_xlabel('Arduino AM2302 Temperature (C)', fontsize=12)
    ax.set_ylabel('Teslameter Probe Temperature (C)', fontsize=12)
    ax.set_title('TC1: Temperature Sensor Cross-Comparison\nJune 2-3, 2026 (%d matched pairs)' % len(matched),
                 fontsize=13)
    ax.legend(fontsize=10, loc='upper left')
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    # Stats annotation
    residuals = tes - ard
    stats_text = (
        'Mean residual: %.2f C\n'
        'Std residual: %.2f C\n'
        'Median residual: %.2f C\n'
        'N = %d pairs'
    ) % (np.mean(residuals), np.std(residuals, ddof=1),
         np.median(residuals), len(matched))
    ax.text(0.98, 0.05, stats_text, transform=ax.transAxes,
            fontsize=9, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    print("  Saved %s" % os.path.basename(outpath))


def plot_tc2_residual(matched, outpath):
    """TC2: Residual (Teslameter - Arduino) vs Arduino temperature."""
    ard = np.array([m['arduino_temp_C'] for m in matched])
    res = np.array([m['residual_C'] for m in matched])

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(ard, res, alpha=0.3, s=15, c='steelblue', edgecolors='none')
    ax.axhline(0, color='k', linewidth=0.5, linestyle='--')

    # Bin by temperature (2 C bins)
    bins = np.arange(np.floor(ard.min()), np.ceil(ard.max()) + 2, 2)
    bin_centers = []
    bin_means = []
    bin_stds = []
    for i in range(len(bins) - 1):
        mask = (ard >= bins[i]) & (ard < bins[i+1])
        if mask.sum() >= 3:
            bin_centers.append((bins[i] + bins[i+1]) / 2)
            bin_means.append(np.mean(res[mask]))
            bin_stds.append(np.std(res[mask], ddof=1))

    if bin_centers:
        ax.errorbar(bin_centers, bin_means, yerr=bin_stds, fmt='ro-',
                     markersize=8, linewidth=2, capsize=4,
                     label='Binned mean +/- std (2 C bins)')

    # Linear fit to residual
    if len(ard) > 2:
        coeffs = np.polyfit(ard, res, 1)
        xfit = np.linspace(ard.min(), ard.max(), 100)
        yfit = np.polyval(coeffs, xfit)
        ax.plot(xfit, yfit, 'g--', linewidth=1.5,
                label='Linear fit: slope = %.3f C/C' % coeffs[0])

    ax.set_xlabel('Arduino AM2302 Temperature (C)', fontsize=12)
    ax.set_ylabel('Teslameter - Arduino (C)', fontsize=12)
    ax.set_title('TC2: Temperature Residual vs Arduino Temperature\n'
                 'Positive = Teslameter reads higher', fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # Mark AM2302 accuracy band
    ax.axhspan(-0.5, 0.5, color='lightgreen', alpha=0.15,
               label='AM2302 spec (+/-0.5 C)')
    ax.legend(fontsize=10)

    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    print("  Saved %s" % os.path.basename(outpath))


def plot_tc3_timeofday(matched, outpath):
    """TC3: Time-of-day comparison of both sensors."""
    hours = np.array([m['hour_of_day'] for m in matched])
    ard = np.array([m['arduino_temp_C'] for m in matched])
    tes = np.array([m['tesla_temp_C'] for m in matched])
    res = np.array([m['residual_C'] for m in matched])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), sharex=True)

    # Top: both temperatures vs time
    ax1.scatter(hours, ard, alpha=0.3, s=15, c='blue', label='Arduino AM2302')
    ax1.scatter(hours, tes, alpha=0.3, s=15, c='red', label='Teslameter probe')
    ax1.set_ylabel('Temperature (C)', fontsize=12)
    ax1.set_title('TC3: Temperature Sensors vs Time of Day\nJune 2-3, 2026',
                  fontsize=13)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Bottom: residual vs time
    ax2.scatter(hours, res, alpha=0.3, s=15, c='steelblue', edgecolors='none')
    ax2.axhline(0, color='k', linewidth=0.5, linestyle='--')

    # Bin by hour
    hour_bins = np.arange(np.floor(hours.min()), np.ceil(hours.max()) + 1, 1)
    hbin_centers = []
    hbin_means = []
    hbin_stds = []
    for i in range(len(hour_bins) - 1):
        mask = (hours >= hour_bins[i]) & (hours < hour_bins[i+1])
        if mask.sum() >= 3:
            hbin_centers.append((hour_bins[i] + hour_bins[i+1]) / 2)
            hbin_means.append(np.mean(res[mask]))
            hbin_stds.append(np.std(res[mask], ddof=1))

    if hbin_centers:
        ax2.errorbar(hbin_centers, hbin_means, yerr=hbin_stds, fmt='ro-',
                     markersize=8, linewidth=2, capsize=4,
                     label='Hourly mean +/- std')

    ax2.set_xlabel('Hour of Day', fontsize=12)
    ax2.set_ylabel('Teslameter - Arduino (C)', fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    print("  Saved %s" % os.path.basename(outpath))


def plot_tc4_humidity(matched, outpath):
    """TC4: Humidity effect on temperature disagreement."""
    hum = np.array([m['humidity_pct'] for m in matched])
    res = np.array([m['residual_C'] for m in matched])
    ard = np.array([m['arduino_temp_C'] for m in matched])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: residual vs humidity
    sc1 = ax1.scatter(hum, res, alpha=0.3, s=15, c=ard, cmap='coolwarm',
                      edgecolors='none')
    ax1.axhline(0, color='k', linewidth=0.5, linestyle='--')
    cb1 = fig.colorbar(sc1, ax=ax1, label='Arduino Temp (C)')
    ax1.set_xlabel('Relative Humidity (%)', fontsize=12)
    ax1.set_ylabel('Teslameter - Arduino (C)', fontsize=12)
    ax1.set_title('Temperature Residual vs Humidity', fontsize=13)
    ax1.grid(True, alpha=0.3)

    # Correlation
    if len(hum) > 2:
        from scipy import stats as sp_stats
        rho, pval = sp_stats.spearmanr(hum, res)
        ax1.text(0.02, 0.98,
                 'Spearman rho = %.3f\np = %.3f' % (rho, pval),
                 transform=ax1.transAxes, fontsize=10, va='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Right: humidity vs temperature (context)
    ax2.scatter(ard, hum, alpha=0.3, s=15, c='steelblue', edgecolors='none')
    ax2.set_xlabel('Arduino Temperature (C)', fontsize=12)
    ax2.set_ylabel('Relative Humidity (%)', fontsize=12)
    ax2.set_title('Humidity vs Temperature', fontsize=13)
    ax2.grid(True, alpha=0.3)

    fig.suptitle('TC4: Humidity Effects on Sensor Agreement\nJune 2-3, 2026',
                 fontsize=14, y=1.02)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  Saved %s" % os.path.basename(outpath))


def write_summary(matched, outpath):
    """Write summary statistics text file."""
    if not matched:
        with open(outpath, 'w') as f:
            f.write("No matched data available.\n")
        return

    ard = np.array([m['arduino_temp_C'] for m in matched])
    tes = np.array([m['tesla_temp_C'] for m in matched])
    res = np.array([m['residual_C'] for m in matched])
    hum = np.array([m['humidity_pct'] for m in matched])
    gaps = np.array([m['time_gap_sec'] for m in matched])

    # Per-date breakdown
    dates = sorted(set(m['date'] for m in matched))

    with open(outpath, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("Temperature Sensor Cross-Calibration Summary\n")
        f.write("Arduino AM2302 vs Teslameter Probe (SENIS 3MH6-E)\n")
        f.write("June 2-3, 2026 Measurement Campaign\n")
        f.write("=" * 70 + "\n\n")

        f.write("FLEET STATISTICS (%d matched pairs)\n" % len(matched))
        f.write("-" * 40 + "\n")
        f.write("Arduino temperature range:    %.1f - %.1f C\n" % (ard.min(), ard.max()))
        f.write("Teslameter temperature range: %.1f - %.1f C\n" % (tes.min(), tes.max()))
        f.write("Humidity range:               %.1f - %.1f %%\n" % (hum.min(), hum.max()))
        f.write("Time gap (Arduino-Tesla):     median %.0f sec, max %.0f sec\n\n"
                % (np.median(gaps), gaps.max()))

        f.write("RESIDUAL (Teslameter - Arduino)\n")
        f.write("-" * 40 + "\n")
        f.write("Mean:   %+.3f C\n" % np.mean(res))
        f.write("Std:    %.3f C\n" % np.std(res, ddof=1))
        f.write("Median: %+.3f C\n" % np.median(res))
        f.write("Min:    %+.3f C\n" % res.min())
        f.write("Max:    %+.3f C\n" % res.max())
        f.write("IQR:    %.3f C (Q1=%.3f, Q3=%.3f)\n\n"
                % (np.percentile(res, 75) - np.percentile(res, 25),
                   np.percentile(res, 25), np.percentile(res, 75)))

        f.write("LINEAR FIT: T_tesla = a * T_arduino + b\n")
        f.write("-" * 40 + "\n")
        coeffs = np.polyfit(ard, tes, 1)
        f.write("a (slope):     %.4f\n" % coeffs[0])
        f.write("b (intercept): %.3f C\n" % coeffs[1])
        residuals_fit = tes - np.polyval(coeffs, ard)
        f.write("Fit residual std: %.3f C\n\n" % np.std(residuals_fit, ddof=1))

        f.write("PER-DATE BREAKDOWN\n")
        f.write("-" * 40 + "\n")
        for d in dates:
            dm = [m for m in matched if m['date'] == d]
            d_ard = np.array([m['arduino_temp_C'] for m in dm])
            d_tes = np.array([m['tesla_temp_C'] for m in dm])
            d_res = np.array([m['residual_C'] for m in dm])
            d_hum = np.array([m['humidity_pct'] for m in dm])
            f.write("\n  %s (N=%d)\n" % (d, len(dm)))
            f.write("    Arduino:  %.1f - %.1f C (mean %.1f)\n"
                    % (d_ard.min(), d_ard.max(), d_ard.mean()))
            f.write("    Tesla:    %.1f - %.1f C (mean %.1f)\n"
                    % (d_tes.min(), d_tes.max(), d_tes.mean()))
            f.write("    Residual: mean %+.3f, std %.3f C\n"
                    % (d_res.mean(), np.std(d_res, ddof=1) if len(d_res) > 1 else 0))
            f.write("    Humidity: %.1f - %.1f %%\n"
                    % (d_hum.min(), d_hum.max()))

        # Y-14 calibration plate detail
        y14_matches = [m for m in matched if m['sample_id'].startswith('Y-14')]
        if y14_matches:
            f.write("\n\nY-14 CALIBRATION PLATE DETAIL\n")
            f.write("-" * 40 + "\n")
            f.write("%-12s %-10s %-10s %8s %8s %8s %8s\n" %
                    ('Sample', 'Date', 'Ard.Time', 'Ard(C)', 'Tes(C)',
                     'Res(C)', 'RH(%)'))
            for m in sorted(y14_matches, key=lambda x: x['arduino_time']):
                f.write("%-12s %-10s %-10s %8.1f %8.1f %8.2f %8.1f\n" % (
                    m['sample_id'], m['date'], m['arduino_time'],
                    m['arduino_temp_C'], m['tesla_temp_C'],
                    m['residual_C'], m['humidity_pct'],
                ))
            y14_res = np.array([m['residual_C'] for m in y14_matches])
            f.write("\n  Y-14 residual: mean %+.3f, std %.3f, range %.3f C\n"
                    % (y14_res.mean(), np.std(y14_res, ddof=1) if len(y14_res) > 1 else 0,
                       y14_res.max() - y14_res.min()))

        # Temperature-dependent bias analysis
        f.write("\n\nTEMPERATURE-DEPENDENT BIAS ANALYSIS\n")
        f.write("-" * 40 + "\n")
        lo_mask = ard < 24
        hi_mask = ard >= 27
        if lo_mask.sum() >= 3 and hi_mask.sum() >= 3:
            f.write("Low temp (<24 C):  N=%d, mean residual = %+.3f C\n"
                    % (lo_mask.sum(), res[lo_mask].mean()))
            f.write("High temp (>=27 C): N=%d, mean residual = %+.3f C\n"
                    % (hi_mask.sum(), res[hi_mask].mean()))
            f.write("Difference: %.3f C (Teslameter converges at high T)\n"
                    % (res[lo_mask].mean() - res[hi_mask].mean()))
        else:
            f.write("Insufficient data in low or high temp bins for comparison.\n")

        # Humidity correlation
        f.write("\n\nHUMIDITY CORRELATION\n")
        f.write("-" * 40 + "\n")
        try:
            from scipy import stats as sp_stats
            rho, pval = sp_stats.spearmanr(hum, res)
            f.write("Spearman rho (humidity vs residual): %.3f (p = %.3f)\n" % (rho, pval))
            rho2, pval2 = sp_stats.spearmanr(ard, hum)
            f.write("Spearman rho (arduino temp vs humidity): %.3f (p = %.3f)\n" % (rho2, pval2))
            f.write("Note: humidity and temperature are strongly anticorrelated in these data,\n")
            f.write("so humidity-residual correlation may be confounded by temperature.\n")
        except ImportError:
            f.write("scipy not available; skipping Spearman correlation.\n")

        f.write("\n\nIMPLICATIONS FOR TEMPERATURE CORRECTION\n")
        f.write("-" * 40 + "\n")
        f.write("Current differential temp sensitivity: 0.066%%/C\n")
        f.write("Mean residual (%.3f C) -> differential bias: %.4f%%\n"
                % (np.mean(res), 0.066 * np.mean(res)))
        f.write("Residual std (%.3f C) -> differential uncertainty: +/-%.4f%%\n"
                % (np.std(res, ddof=1), 0.066 * np.std(res, ddof=1)))
        f.write("\nNOTE: Neither sensor directly measures the sample's internal temperature.\n")
        f.write("  - Arduino AM2302: measures ambient air (may be affected by drafts,\n")
        f.write("    laptop fans, HVAC airflow; +/-0.5 C spec accuracy)\n")
        f.write("  - Teslameter probe: in contact with sample surface (may include\n")
        f.write("    self-heating bias, but physically closer to sample temperature)\n")
        f.write("  - Which is the better proxy for the temperature correction is an\n")
        f.write("    OPEN QUESTION to be resolved by the summer cross-calibration study.\n")
        f.write("  - AM2302 advantage: synchronous with Helmholtz measurement time\n")
        f.write("  - Teslameter advantage: in thermal contact with the actual sample\n")
        f.write("  - Target: reduce temperature uncertainty to +/-0.3 C by understanding\n")
        f.write("    and modeling the offset, regardless of which sensor is primary.\n")

    print("  Wrote %s" % os.path.basename(outpath))


# ---- Main -----------------------------------------------------------------

def main():
    print("=" * 60)
    print("Temperature Sensor Cross-Calibration")
    print("Arduino AM2302 vs Teslameter Probe")
    print("June 2-3, 2026")
    print("=" * 60)

    print("\nLoading Arduino (helmholtzTemp) data...")
    arduino_data = load_all_arduino()
    n_ard = sum(len(v) for v in arduino_data.values())
    print("  %d samples, %d total readings" % (len(arduino_data), n_ard))

    print("\nLoading Teslameter (top face) data...")
    tesla_data = load_all_teslameter()
    n_tes = sum(len(v) for v in tesla_data.values())
    print("  %d samples, %d June readings" % (len(tesla_data), n_tes))

    print("\nMatching readings (max gap = %d sec)..." % MAX_TIME_GAP.total_seconds())
    matched = match_readings(arduino_data, tesla_data)

    if not matched:
        print("\nERROR: No matched pairs found. Check data directories.")
        return

    print("\nWriting results...")
    write_csv(matched, os.path.join(OUTPUT_DIR, 'temp_comparison_results.csv'))

    print("\nGenerating plots...")
    plot_tc1_scatter(matched, os.path.join(OUTPUT_DIR, 'TC1_temp_scatter.png'))
    plot_tc2_residual(matched, os.path.join(OUTPUT_DIR, 'TC2_residual_vs_temp.png'))
    plot_tc3_timeofday(matched, os.path.join(OUTPUT_DIR, 'TC3_timeofday.png'))
    plot_tc4_humidity(matched, os.path.join(OUTPUT_DIR, 'TC4_humidity_effect.png'))

    print("\nWriting summary...")
    write_summary(matched, os.path.join(OUTPUT_DIR, 'temp_comparison_summary.txt'))

    print("\nDone. All outputs in %s" % OUTPUT_DIR)


if __name__ == '__main__':
    main()
