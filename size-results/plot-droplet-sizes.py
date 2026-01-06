import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-whitegrid')

def plot_droplet_size_distribution(csv_path, size_category, x_range=None, y_range=None):
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Calculate statistics
    feret = df['Feret']
    mean_size = feret.mean()
    std_dev = feret.std()
    cv = (std_dev / mean_size) * 100  # Coefficient of variation in percentage
    
    # Plot histogram
    n, bins, patches = ax.hist(feret, bins=30, color='#1f77b4', edgecolor='black', alpha=0.7, density=False)
    
    # Add a vertical line at the mean
    ax.axvline(mean_size, color='#d62728', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_size:.2f} µm')
    
    # Set axis ranges if provided
    if x_range:
        ax.set_xlim(x_range)
    if y_range:
        ax.set_ylim(y_range)
    
    # Add labels and title
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.set_xlabel('Droplet Size (µm)', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title(f'Droplet Size Distribution - Target Size: {size_category} (n = {len(df)})', 
                fontsize=14, pad=15)

    # Add grid and legend
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Add text with statistics
    stats_text = (f'Mean: {mean_size:.2f} µm\n'
                 f'Median: {feret.median():.2f} µm\n'
                 f'Std Dev: {std_dev:.2f} µm\n'
                 f'CV: {cv:.1f}%\n'
                 f'Min: {feret.min():.2f} µm\n'
                 f'Max: {feret.max():.2f} µm')
    
    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes, 
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray',
                boxstyle='round,pad=0.5'), fontsize=10,
                verticalalignment='top', horizontalalignment='right')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save in multiple formats
    base_filename = f'droplet_distribution_{size_category}'
    for ext in ['.png', '.pdf']:
        output_file = base_filename + ext
        plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0.1)
    
    plt.close()

    return f'{base_filename}.png', f'{base_filename}.pdf', ax.get_xlim(), ax.get_ylim()

# Process both CSV files
csv_files = {
    '25 µm': 'Results_25um.csv',
    '30 µm': 'Results_30um.csv'
}

output_files = []
x_range = None
y_range = None

# First pass to get the maximum ranges
for size, filename in csv_files.items():
    if os.path.exists(filename):
        _, _, current_xlim, current_ylim = plot_droplet_size_distribution(filename, size)
        if x_range is None:
            x_range = list(current_xlim)
            y_range = list(current_ylim)
        else:
            x_range[0] = min(x_range[0], current_xlim[0])
            x_range[1] = max(x_range[1], current_xlim[1])
            y_range[1] = max(y_range[1], current_ylim[1])

# Second pass to create final plots with consistent ranges
for size, filename in csv_files.items():
    if os.path.exists(filename):
        png_file, pdf_file, _, _ = plot_droplet_size_distribution(filename, size, x_range, y_range)
        print(f"Created {png_file} and {pdf_file}")
    else:
        print(f"Warning: {filename} not found")