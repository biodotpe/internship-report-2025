import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

def load_intensity_data(csv_path):
    """Load and process intensity data from a CSV file."""
    df = pd.read_csv(csv_path)
    # Add time points in minutes (0, 20, 40, ...)
    df['TimePoint'] = df.index * 20
    return df

def plot_multiple_intensity(csv_paths, labels=None, output_file=None, time_interval=20, show_median=True, 
                         start_time=None, end_time=None, time_unit='minutes', show_sd=True, colors=None):
    """
    Plot intensity over time from multiple CSV files on the same plot.
    
    Args:
        csv_paths (list): List of paths to CSV files
        labels (list, optional): List of labels for the legend. If None, filenames will be used.
        output_file (str or Path, optional): Path to save the plot.
        time_interval (int): Time interval in minutes between data points (default: 20)
        show_median (bool): Whether to plot median intensity (default: True)
        start_time (float, optional): Start time in the specified time_unit
        end_time (float, optional): End time in the specified time_unit
        time_unit (str): Unit for start/end times ('minutes' or 'hours')
    """
    if not labels:
        labels = [Path(path).stem for path in csv_paths]
    
    # Set up colors
    if colors is None:
        colors = plt.cm.tab10(np.linspace(0, 1, len(csv_paths)))
    elif len(colors) < len(csv_paths):
        # If not enough colors provided, cycle through the given colors
        colors = [colors[i % len(colors)] for i in range(len(csv_paths))]

    # Convert time range to minutes if needed
    if start_time is not None and time_unit == 'hours':
        start_time *= 60
    if end_time is not None and time_unit == 'hours':
        end_time *= 60
    
    # Create figure and axis
    plt.figure(figsize=(12, 6))
    
    # Color cycle for multiple plots
    # colors = plt.cm.tab10(np.linspace(0, 1, len(csv_paths)))
    
    # Track min/max time for x-axis
    min_time = float('inf')
    max_time = -float('inf')
    
    # Plot each dataset
    for i, (csv_path, label, color) in enumerate(zip(csv_paths, labels, colors)):
        try:
            df = load_intensity_data(csv_path)
            
            # Filter data by time range
            if start_time is not None:
                df = df[df['TimePoint'] >= start_time]
            if end_time is not None:
                df = df[df['TimePoint'] <= end_time]
            
            if len(df) == 0:
                print(f"Warning: No data in range for {csv_path}")
                continue
                
            # Update time range
            min_time = min(min_time, df['TimePoint'].min())
            max_time = max(max_time, df['TimePoint'].max())
            
            # Plot mean intensity with error bars
            if 'MeanIntensity' in df.columns:
                if show_sd and 'StdDev' in df.columns:
                    plt.errorbar(
                        df['TimePoint'],
                        df['MeanIntensity'],
                        yerr=df['StdDev'].fillna(0),
                        marker='o',
                        linestyle='-',
                        capsize=3,
                        label=f'{label} (Mean ± SD)',
                        color=color,
                        alpha=0.9,
                        markersize=5,
                        linewidth=1.2,
                        markeredgecolor='white',
                        markeredgewidth=0.5,
                        elinewidth=1
                    )
                else:
                    plt.plot(
                        df['TimePoint'],
                        df['MeanIntensity'],
                        marker='o',
                        linestyle='-',
                        label=f'{label} (Mean)',
                        color=color,
                        alpha=0.9,
                        markersize=5,
                        linewidth=1.2,
                        markeredgecolor='white',
                        markeredgewidth=0.5
                    )
            
            # Plot median intensity
            if show_median and 'MedianIntensity' in df.columns:
                plt.plot(
                    df['TimePoint'],
                    df['MedianIntensity'],
                    marker='s',
                    linestyle='--',
                    label=f'{label} (Median)',
                    color=color,
                    alpha=0.8,
                    markersize=4,
                    linewidth=1,
                    markeredgecolor='white',
                    markeredgewidth=0.5
                )
                
        except Exception as e:
            print(f"Error processing {csv_path}: {str(e)}")
    
    # Set plot title and labels
    plt.title('Fluorescence Intensity Over Time', fontsize=18, fontweight='bold')
    plt.xlabel('Time (minutes)', fontsize=16)
    plt.ylabel('Integrated Density (IntDen)', fontsize=16)
    
    # Set x-ticks
    if min_time != float('inf') and max_time != -float('inf'):
        plt.xlim(left=start_time, right=end_time)
        plt.xticks(np.arange(
            max(0, (min_time // time_interval) * time_interval),
            max_time + time_interval,
            time_interval
        ))
    
    # Add grid for better readability
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Add legend outside the plot
    plt.legend(loc='upper left')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save or show the plot
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {output_file}")
        
        # Create and save hours plot
        hours_output = str(Path(output_file).with_stem(f"{Path(output_file).stem}_hours"))
        convert_to_hours_plot(csv_paths, labels, hours_output, time_interval, show_median, 
                            start_time, end_time, time_unit, show_sd, colors)
    else:
        plt.show()
        plt.figure()
        convert_to_hours_plot(csv_paths, labels, None, time_interval, show_median,
                            start_time, end_time, time_unit, show_sd, colors)

def convert_to_hours_plot(csv_paths, labels, output_file, time_interval, show_median=True, 
                        start_time=None, end_time=None, time_unit='minutes', show_sd=True, colors=None):
    """
    Create a plot with time in hours.
    
    Args:
        csv_paths (list): List of paths to CSV files
        labels (list): List of labels for the legend.
        output_file (str or None): Path to save the plot.
        time_interval (int): Time interval in minutes between data points.
        show_median (bool): Whether to plot median intensity (default: True)
        start_time (float, optional): Start time in the specified time_unit
        end_time (float, optional): End time in the specified time_unit
        time_unit (str): Unit for start/end times ('minutes' or 'hours')
    """
    # Create figure and axis
    plt.figure(figsize=(12, 8))

    # Set up colors if not provided
    if colors is None:
        colors = plt.cm.tab10(np.linspace(0, 1, len(csv_paths)))
    elif len(colors) < len(csv_paths):
        # If not enough colors provided, cycle through the given colors
        colors = [colors[i % len(colors)] for i in range(len(csv_paths))]
        
    # Color cycle for multiple plots
    # colors = plt.cm.tab10(np.linspace(0, 1, len(csv_paths)))
    
    # Track time range for x-axis
    min_hours = float('inf')
    max_hours = -float('inf')
    
    # Convert time range to hours if needed
    plot_start = start_time / 60 if (start_time is not None and time_unit == 'minutes') else start_time
    plot_end = end_time / 60 if (end_time is not None and time_unit == 'minutes') else end_time
    
    # Plot each dataset
    for i, (csv_path, label, color) in enumerate(zip(csv_paths, labels, colors)):
        try:
            df = load_intensity_data(csv_path)
            df['TimePoint'] = df['TimePoint'] / 60  # Convert minutes to hours
            
            # Filter data by time range
            if plot_start is not None:
                df = df[df['TimePoint'] >= plot_start]
            if plot_end is not None:
                df = df[df['TimePoint'] <= plot_end]
            
            if len(df) == 0:
                print(f"Warning: No data in range for {csv_path}")
                continue
                
            # Update time range
            min_hours = min(min_hours, df['TimePoint'].min())
            max_hours = max(max_hours, df['TimePoint'].max())
            
            # Plot mean intensity with error bars
            if 'MeanIntensity' in df.columns:
                if show_sd and 'StdDev' in df.columns:
                    plt.errorbar(
                        df['TimePoint'],
                        df['MeanIntensity'],
                        yerr=df['StdDev'].fillna(0),
                        marker='o',
                        linestyle='-',
                        capsize=3,
                        label=f'{label} (Mean ± SD)',
                        color=color,
                        alpha=0.9,
                        markersize=5,
                        linewidth=1.2,
                        markeredgecolor='white',
                        markeredgewidth=0.5,
                        elinewidth=1
                    )
                else:
                    plt.plot(
                        df['TimePoint'],
                        df['MeanIntensity'],
                        marker='o',
                        linestyle='-',
                        label=f'{label} (Mean)',
                        color=color,
                        alpha=0.9,
                        markersize=5,
                        linewidth=1.2,
                        markeredgecolor='white',
                        markeredgewidth=0.5
                    )
                
            # Plot median intensity
            if show_median and 'MedianIntensity' in df.columns:
                plt.plot(
                    df['TimePoint'],
                    df['MedianIntensity'],
                    marker='s',
                    linestyle='--',
                    label=f'{label} (Median)',
                    color=color,
                    alpha=0.8,
                    markersize=4,
                    linewidth=1,
                    markeredgecolor='white',
                    markeredgewidth=0.5
                )
                
        except Exception as e:
            print(f"Error processing {csv_path}: {str(e)}")
    
    # Set plot title and labels
    plt.title('Fluorescence Intensity Over Time', fontsize=18, fontweight='bold')
    plt.xlabel('Time (hours)', fontsize=18)
    plt.ylabel('Integrated Density (IntDen)', fontsize=18)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    # Set x-ticks and limits
    tick_interval = 1  # 1 hour intervals
    
    # Calculate x-axis limits
    x_min = plot_start if plot_start is not None else 0
    x_max = plot_end if plot_end is not None else (max_hours if max_hours != -float('inf') else 24)
    
    # Ensure we have a reasonable range
    if x_min == x_max:
        x_min = max(0, x_min - 1)
        x_max += 1
    
    plt.xlim(left=x_min, right=x_max)
    plt.xticks(np.arange(
        np.floor(x_min),
        np.ceil(x_max) + tick_interval,
        tick_interval
    ))
    
    # Add grid for better readability
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Add legend inside the plot
    plt.legend(loc='upper left')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save or show the plot
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Hours plot saved to {output_file}")
    else:
        plt.show()

if __name__ == "__main__":
    # import argparse
    
    # # Set up argument parsing
    # parser = argparse.ArgumentParser(description='Plot intensity over time from multiple CSV files')
    # parser.add_argument('csv_files', nargs='+', help='One or more CSV files to plot')
    # parser.add_argument('--labels', nargs='+', help='Labels for each dataset (optional)')
    # parser.add_argument('-o', '--output', help='Path to save the output plot (optional)')
    # parser.add_argument('--interval', type=int, default=20, 
    #                    help='Time interval in minutes between data points (default: 20)')
    # parser.add_argument('--no-median', action='store_false', dest='show_median',
    #                    help='Exclude median intensity from the plot')
    # parser.add_argument('--start', type=float, help='Start time in the specified time unit')
    # parser.add_argument('--end', type=float, help='End time in the specified time unit')
    # parser.add_argument('--time-unit', choices=['minutes', 'hours'], default='minutes',
    #                    help='Time unit for --start and --end (default: minutes)')
    
    # args = parser.parse_args()
    
    # if args.labels and len(args.labels) != len(args.csv_files):
    #     print("Error: Number of labels must match number of CSV files")
    #     exit(1)
    
    # plot_multiple_intensity(
    #     args.csv_files,
    #     labels=args.labels,
    #     output_file=args.output,
    #     time_interval=args.interval,
    #     show_median=args.show_median,
    #     start_time=args.start,
    #     end_time=args.end,
    #     time_unit=args.time_unit
    # )

    # Plot data from two CSV files, save as 'intensity_plot.png'
    colors = ['blue', 'orange']
    plot_multiple_intensity(
        csv_paths=['intensity_30um.csv', 'intensity_25um.csv'],
        labels=['30 um', '25 um'],
        output_file='intensity_plot.png',
        time_interval=20,  # 20 minutes between points
        show_median=False,
        show_sd=True,
        start_time=0,      # Start at 0 minutes
        end_time=420,     # End at 24 hours (1440 minutes)
        time_unit='minutes',
        colors=colors
    )
