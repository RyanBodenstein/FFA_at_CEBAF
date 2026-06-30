import os
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Colorblind-safe color palette
CB_COLORS = ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377', '#BBBBBB']

def percent_difference(initial, final):
    """Calculates the percent difference between two values."""
    if initial == 0:
        return float('inf') if final != 0 else 0.0
    return ((final - initial) / abs(initial)) * 100

def parse_line(line, is_helmholtz):
    """Parses a single line from a data file."""
    parts = line.split()
    dt_str = f"{parts[0]} {parts[1]}"
    timestamp = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    
    if is_helmholtz:
        value = float(parts[4])
        return timestamp, [value]
    else:
        if len(parts) > 7 and parts[2].isalpha():
             values = [float(p) for p in parts[4:7]]
        else:
             values = [float(p) for p in parts[2:5]]
        return timestamp, values

def process_files(filenames, measurement_type):
    """
    Processes files to get percent differences and raw data.
    Returns two lists: one for percent diff results, one for raw results.
    """
    is_helmholtz = (measurement_type == 'helmholtz')
    all_diff_results = []
    all_raw_results = []

    for filename in filenames:
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()

            if len(lines) < 2:
                print(f"Warning: Not enough data in {filename}. Skipping.")
                continue

            initial_values, final_values = None, None
            for line in lines:
                clean_line = line.strip()
                if not clean_line:
                    continue
                try:
                    if clean_line.startswith('2025-08-26'):
                        _, initial_values = parse_line(clean_line, is_helmholtz)
                    elif clean_line.startswith('2025-08-27'):
                        _, final_values = parse_line(clean_line, is_helmholtz)
                except Exception as e:
                    print(f"Warning: Could not parse line '{clean_line}' in {filename}. Skipping. Error: {e}")
                    continue
            
            if initial_values is None or final_values is None:
                print(f"Warning: Missing data for required dates in {filename}. Skipping.")
                continue

            diffs = [percent_difference(i, f) for i, f in zip(initial_values, final_values)]
            base_name = os.path.basename(filename)
            sample_name = base_name.replace(f'_{measurement_type}.dat', '')
            all_diff_results.append((sample_name, *diffs))
            all_raw_results.append((sample_name, *initial_values, *final_values))

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    sort_order = {'Y': 0, 'Hs': 1, 'As': 2}
    def sort_key(item):
        sample_name = item[0]
        parts = sample_name.split('-')
        type_prefix = parts[0]
        numeric_parts = [int(p) for p in parts[1:] if p.isdigit()]
        order = sort_order.get(type_prefix, 99)
        return (order, numeric_parts)

    all_diff_results.sort(key=sort_key)
    all_raw_results.sort(key=sort_key)
    
    return all_diff_results, all_raw_results

def plot_percent_difference(m_type, data):
    """Generates and saves a percent difference bar chart using matplotlib."""
    if not data:
        print(f"No data to plot for {m_type} percent difference.")
        return

    labels = [row[0] for row in data]
    x = np.arange(len(labels))
    
    fig, ax = plt.subplots(figsize=(20, 15))
    
    def autolabel_staggered(rects, ax, color, level):
        """Attach a text label with a staggered vertical offset."""
        for rect in rects:
            height = rect.get_height()
            
            base_offset = 5 # Increased base offset
            stagger = 15 * level # Stagger by 15 points for each level
            
            if height >= 0:
                va = 'bottom'
                y_offset = base_offset + stagger
            else:
                va = 'top'
                y_offset = -base_offset - stagger
            
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, y_offset),
                        textcoords="offset points",
                        ha='center', va=va,
                        fontsize=9, color=color, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.7, ec='none'))

    if m_type == 'helmholtz':
        values = [row[1] for row in data]
        bars = ax.bar(x, values, width=0.6, label='Percent Difference', color=CB_COLORS[0])
        ax.set_ylabel('Percent Difference (%)', fontsize=20)
        ax.set_title(f'Percent Difference in {m_type.capitalize()} Measurements', fontsize=26)
        autolabel_staggered(bars, ax, CB_COLORS[0], 0)
    else:
        x_vals = [row[1] for row in data]
        y_vals = [row[2] for row in data]
        z_vals = [row[3] for row in data]
        width = 0.25
        
        rects1 = ax.bar(x - width, x_vals, width, label='X-axis', color=CB_COLORS[0])
        rects2 = ax.bar(x, y_vals, width, label='Y-axis', color=CB_COLORS[1])
        rects3 = ax.bar(x + width, z_vals, width, label='Z-axis', color=CB_COLORS[2])
        
        ax.set_ylabel('Percent Difference (%)', fontsize=20)
        ax.set_title(f'Percent Difference in {m_type.capitalize()} Measurements', fontsize=26)
        ax.legend(fontsize=16)

        autolabel_staggered(rects1, ax, CB_COLORS[0], 0) # Level 0
        autolabel_staggered(rects2, ax, CB_COLORS[1], 1) # Level 1
        autolabel_staggered(rects3, ax, CB_COLORS[2], 2) # Level 2
        
        all_vals = x_vals + y_vals + z_vals
        if all_vals:
            min_val, max_val = min(all_vals), max(all_vals)
            range_val = max_val - min_val
            padding = range_val * 0.25 # Increased padding for more space
            ax.set_ylim(min_val - padding, max_val + padding)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=14)
    ax.tick_params(axis='y', labelsize=14)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    fig.tight_layout()
    
    filename = f'plot_diff_{m_type}.png'
    plt.savefig(filename, dpi=300) 
    print(f"Saved plot to {filename}")
    plt.close(fig)

def plot_raw_data(m_type, data):
    """Generates and saves a raw data line chart using matplotlib."""
    if not data:
        print(f"No data to plot for {m_type} raw data.")
        return

    labels = [row[0] for row in data]
    x = np.arange(len(labels))
    
    fig, ax = plt.subplots(figsize=(20, 15))

    if m_type == 'helmholtz':
        initial = [row[1] for row in data]
        final = [row[2] for row in data]
        ax.plot(x, initial, 'o-', color=CB_COLORS[0], label='Initial (2025-08-26)')
        ax.plot(x, final, 's-', color=CB_COLORS[1], label='Final (2025-08-27)')
        ax.set_ylabel('Measurement (mWC)', fontsize=20)
        ax.set_title(f'Raw {m_type.capitalize()} Measurements', fontsize=26)
    else:
        ax.plot(x, [r[1] for r in data], 'o-', color=CB_COLORS[0], label='X-axis Initial')
        ax.plot(x, [r[4] for r in data], 's--', color=CB_COLORS[0], label='X-axis Final')
        ax.plot(x, [r[2] for r in data], 'o-', color=CB_COLORS[1], label='Y-axis Initial')
        ax.plot(x, [r[5] for r in data], 's--', color=CB_COLORS[1], label='Y-axis Final')
        ax.plot(x, [r[3] for r in data], 'o-', color=CB_COLORS[2], label='Z-axis Initial')
        ax.plot(x, [r[6] for r in data], 's--', color=CB_COLORS[2], label='Z-axis Final')
        ax.set_ylabel('Magnetic Field (mT)', fontsize=20)
        ax.set_title(f'Raw {m_type.capitalize()} Measurements', fontsize=26)
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=14)
    ax.tick_params(axis='y', labelsize=14)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(fontsize=16)
    fig.tight_layout()

    filename = f'plot_raw_{m_type}.png'
    plt.savefig(filename, dpi=300)
    print(f"Saved plot to {filename}")
    plt.close(fig)

def main():
    """Main function to find, group, process, and write data files."""
    all_files = glob.glob('*.dat')
    input_files = [f for f in all_files if not f.startswith(('percent_difference_', 'raw_measurements_'))]
    
    final_groups = {}
    for f in input_files:
        try:
            measurement_type = os.path.basename(f).split('_')[-1].replace('.dat', '')
            if measurement_type not in final_groups:
                final_groups[measurement_type] = []
            final_groups[measurement_type].append(f)
        except IndexError:
            print(f"Could not determine measurement type for {f}. Skipping.")

    for m_type, filenames in final_groups.items():
        print(f"\nProcessing {m_type} files...")
        diff_results, raw_results = process_files(filenames, m_type)
        
        if diff_results:
            diff_output_filename = f'percent_difference_{m_type}.dat'
            with open(diff_output_filename, 'w') as out_f:
                for result in diff_results:
                    out_f.write('\t'.join([str(r) for r in result]) + '\n')
            print(f"Wrote sorted data to {diff_output_filename}")
            plot_percent_difference(m_type, diff_results)

        if raw_results:
            raw_output_filename = f'raw_measurements_{m_type}.dat'
            with open(raw_output_filename, 'w') as out_f:
                for result in raw_results:
                    out_f.write('\t'.join([str(r) for r in result]) + '\n')
            print(f"Wrote sorted data to {raw_output_filename}")
            plot_raw_data(m_type, raw_results)

if __name__ == '__main__':
    main()

