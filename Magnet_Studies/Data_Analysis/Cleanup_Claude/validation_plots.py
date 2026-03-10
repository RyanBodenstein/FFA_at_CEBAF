#!/usr/bin/env python3
"""
Validation plots for the Cleanup_Claude merged data.
Produces:
  1. Helmholtz time-series for selected Y-plate samples (full timeline)
  2. Aug 26 vs Aug 27 comparison to match the prior Compare_Lab_Tunnel plot
"""

import os
import re
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.join(BASE, 'Validation_Plots')
os.makedirs(PLOT_DIR, exist_ok=True)

# Colorblind-safe palette
CB = ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377', '#BBBBBB', '#000000']


def parse_helmholtz_file(filepath):
    """Parse a helmholtz .dat file. Returns list of (datetime, value_mWC)."""
    rows = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Try new format: YYYY-MM-DD\tHH:MM:SS\t...
            m = re.match(r'(\d{4}-\d{2}-\d{2})\t(\d{2}:\d{2}:\d{2})\t(.*)', line)
            if m:
                dt = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M:%S")
                rest = m.group(3)
            else:
                # Old format: YYYY-MM-DD-HH:MM:SS\t...
                m = re.match(r'(\d{4}-\d{2}-\d{2})-(\d{2}:\d{2}:\d{2})\t(.*)', line)
                if m:
                    dt = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M:%S")
                    rest = m.group(3)
                else:
                    continue

            # Extract numeric value
            val_match = re.search(r'([+-]?\d+\.?\d*)\s*(mWC|kT|kBG)', rest)
            if val_match:
                value = float(val_match.group(1))
                unit = val_match.group(2)
                rows.append((dt, value, unit))

    return rows


def parse_teslameter_file(filepath):
    """Parse a teslameter .dat file. Returns list of (datetime, [f1, f2, f3], temp)."""
    rows = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Try new format
            m = re.match(r'(\d{4}-\d{2}-\d{2})\t(\d{2}:\d{2}:\d{2})\t(.*)', line)
            if m:
                dt = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M:%S")
                rest = m.group(3)
            else:
                # Old format
                m = re.match(r'(\d{4}-\d{2}-\d{2})-(\d{2}:\d{2}:\d{2})\t(.*)', line)
                if m:
                    dt = datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H:%M:%S")
                    rest = m.group(3)
                else:
                    continue

            # Extract numeric fields (skip serial/rod text fields)
            nums = re.findall(r'(-?\d+\.\d+)', rest)
            if len(nums) >= 4:
                fields = [float(x) for x in nums[:3]]
                temp = float(nums[3])
                rows.append((dt, fields, temp))
            elif len(nums) >= 3:
                fields = [float(x) for x in nums[:3]]
                rows.append((dt, fields, None))

    return rows


# ─── Plot 1: Helmholtz Time-Series ──────────────────────────────────────────

def plot_helmholtz_timeseries():
    """Plot full Helmholtz time-series for selected Y-plate samples."""
    # Pick a spread of samples across plates
    samples = ['Y-1-1', 'Y-8-1', 'Y-15-1', 'Y-22-4', 'Y-30-1']

    fig, axes = plt.subplots(len(samples), 1, figsize=(14, 3.5 * len(samples)),
                              sharex=True)
    if len(samples) == 1:
        axes = [axes]

    for ax, sample in zip(axes, samples):
        fpath = os.path.join(BASE, 'Y_Plates', 'Helmholtz', f'{sample}_helmholtz.dat')
        if not os.path.exists(fpath):
            ax.text(0.5, 0.5, f'{sample}: file not found', transform=ax.transAxes,
                    ha='center', fontsize=12)
            ax.set_ylabel(sample)
            continue

        rows = parse_helmholtz_file(fpath)
        # Filter to mWC only for consistent comparison
        mwc_rows = [(dt, val) for dt, val, unit in rows if unit == 'mWC']

        if not mwc_rows:
            ax.text(0.5, 0.5, f'{sample}: no mWC readings', transform=ax.transAxes,
                    ha='center', fontsize=12)
            ax.set_ylabel(sample)
            continue

        dates, vals = zip(*mwc_rows)
        ax.plot(dates, vals, 'o-', color=CB[0], markersize=5, linewidth=1.2)
        ax.set_ylabel('mWC', fontsize=11)
        ax.set_title(f'{sample} Helmholtz', fontsize=12, fontweight='bold', loc='left')
        ax.grid(True, alpha=0.3)

        # Annotate key dates
        for dt, val in mwc_rows:
            if dt.month == 7 and dt.year == 2025 and dt.day <= 17:
                ax.axvline(dt, color=CB[1], alpha=0.3, linestyle='--')
            if dt.month == 1 and dt.year == 2026:
                ax.axvline(dt, color=CB[2], alpha=0.3, linestyle='--')

    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)
    fig.suptitle('Helmholtz Time-Series (mWC) — Validation Check', fontsize=14, fontweight='bold')
    fig.tight_layout()

    outpath = os.path.join(PLOT_DIR, 'validation_helmholtz_timeseries.png')
    plt.savefig(outpath, dpi=200)
    print(f"Saved: {outpath}")
    plt.close()


# ─── Plot 2: Aug 26 vs Aug 27 Comparison (matches prior plot) ───────────────

def plot_aug26_vs_aug27():
    """Reproduce the prior Compare_Lab_Tunnel Helmholtz comparison."""
    # Samples from the prior plot
    samples = [
        'Y-8-1', 'Y-8-2', 'Y-8-3', 'Y-8-4',
        'Hs-29-1', 'Hs-29-2', 'Hs-29-3', 'Hs-29-4',
        'As-29-1-1', 'As-29-1-2', 'As-29-2-1', 'As-29-2-2',
        'As-29-3-1', 'As-29-3-2', 'As-29-4-1', 'As-29-4-2',
    ]

    initial_vals = []
    final_vals = []
    valid_samples = []

    for sample in samples:
        # Try Y_Plates first, then Pair_Assemblies
        if sample.startswith('Y-'):
            fpath = os.path.join(BASE, 'Y_Plates', 'Helmholtz', f'{sample}_helmholtz.dat')
        else:
            fpath = os.path.join(BASE, 'Pair_Assemblies', 'Helmholtz', f'{sample}_helmholtz.dat')

        if not os.path.exists(fpath):
            print(f"  {sample}: not found, skipping")
            continue

        rows = parse_helmholtz_file(fpath)

        init = None
        final = None
        for dt, val, unit in rows:
            if dt.strftime('%Y-%m-%d') == '2025-08-26':
                init = val
            elif dt.strftime('%Y-%m-%d') == '2025-08-27':
                final = val

        if init is not None and final is not None:
            initial_vals.append(init)
            final_vals.append(final)
            valid_samples.append(sample)
        else:
            print(f"  {sample}: missing Aug 26 or Aug 27 data")

    if not valid_samples:
        print("No samples with both Aug 26 and Aug 27 data found.")
        return

    # Raw comparison plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    x = np.arange(len(valid_samples))
    ax1.plot(x, initial_vals, 'o-', color=CB[0], label='Initial (2025-08-26)', markersize=6)
    ax1.plot(x, final_vals, 's-', color=CB[1], label='Final (2025-08-27)', markersize=6)
    ax1.set_xticks(x)
    ax1.set_xticklabels(valid_samples, rotation=45, ha='right', fontsize=10)
    ax1.set_ylabel('Measurement (mWC)', fontsize=12)
    ax1.set_title('Raw Helmholtz Measurements', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Percent difference
    pct_diff = [((f - i) / abs(i)) * 100 if i != 0 else 0
                for i, f in zip(initial_vals, final_vals)]

    colors = [CB[0] if d >= 0 else CB[1] for d in pct_diff]
    bars = ax2.bar(x, pct_diff, width=0.6, color=colors)
    for bar, d in zip(bars, pct_diff):
        ax2.annotate(f'{d:.1f}%',
                     xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     xytext=(0, 5 if d >= 0 else -12),
                     textcoords='offset points',
                     ha='center', va='bottom' if d >= 0 else 'top',
                     fontsize=9, fontweight='bold')

    ax2.set_xticks(x)
    ax2.set_xticklabels(valid_samples, rotation=45, ha='right', fontsize=10)
    ax2.set_ylabel('Percent Difference (%)', fontsize=12)
    ax2.set_title('Percent Difference in Helmholtz (Aug 26 → Aug 27)', fontsize=14, fontweight='bold')
    ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax2.grid(axis='y', alpha=0.3)

    fig.tight_layout()
    outpath = os.path.join(PLOT_DIR, 'validation_aug26_vs_aug27.png')
    plt.savefig(outpath, dpi=200)
    print(f"Saved: {outpath}")
    plt.close()


# ─── Plot 3: Teslameter spot-check ──────────────────────────────────────────

def plot_teslameter_spotcheck():
    """Plot teslameter front readings for a few samples as spot-check."""
    samples = ['Y-1-1', 'Y-22-4', 'An-10-1-1']

    fig, axes = plt.subplots(len(samples), 1, figsize=(14, 3.5 * len(samples)),
                              sharex=True)

    for ax, sample in zip(axes, samples):
        if sample.startswith('Y-'):
            fpath = os.path.join(BASE, 'Y_Plates', 'Teslameter', f'{sample}_front.dat')
        else:
            fpath = os.path.join(BASE, 'Pair_Assemblies', 'Teslameter', f'{sample}_front.dat')

        if not os.path.exists(fpath):
            ax.text(0.5, 0.5, f'{sample}: not found', transform=ax.transAxes, ha='center')
            ax.set_ylabel(sample)
            continue

        rows = parse_teslameter_file(fpath)
        if not rows:
            ax.text(0.5, 0.5, f'{sample}: no valid rows', transform=ax.transAxes, ha='center')
            continue

        dates = [r[0] for r in rows]
        # Plot the three field components
        f1 = [r[1][0] for r in rows]
        f2 = [r[1][1] for r in rows]
        f3 = [r[1][2] for r in rows]

        ax.plot(dates, f1, 'o-', color=CB[0], markersize=4, label='Field 1', linewidth=1)
        ax.plot(dates, f2, 's-', color=CB[1], markersize=4, label='Field 2', linewidth=1)
        ax.plot(dates, f3, '^-', color=CB[2], markersize=4, label='Field 3', linewidth=1)
        ax.set_ylabel('mT', fontsize=11)
        ax.set_title(f'{sample} Front Teslameter', fontsize=12, fontweight='bold', loc='left')
        ax.legend(fontsize=9, ncol=3)
        ax.grid(True, alpha=0.3)

    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)
    fig.suptitle('Teslameter Front — Validation Check', fontsize=14, fontweight='bold')
    fig.tight_layout()

    outpath = os.path.join(PLOT_DIR, 'validation_teslameter_spotcheck.png')
    plt.savefig(outpath, dpi=200)
    print(f"Saved: {outpath}")
    plt.close()


if __name__ == '__main__':
    print("Generating validation plots...\n")
    plot_helmholtz_timeseries()
    plot_aug26_vs_aug27()
    plot_teslameter_spotcheck()
    print("\nAll validation plots saved to Validation_Plots/")
