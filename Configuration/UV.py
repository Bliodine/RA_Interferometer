# This code calculates relevant data products in the uv space for a given antenna configuration.

# Importing all the needed modules and packages
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# Set desired font style for matplotlib plots
plt.rcParams.update({"font.family": 'serif'})                # Use serif fonts


# Define system-specific variables
paint_can_diameter = 0.183          # Paint can diameter in meters (representing antenna size)
max_distance = 5/np.sqrt(2)         # Maximal distance between antennas (based on array configuration)

scale_factor = max_distance         # Scale factor for plotting, based on maximum antenna separation

min_distance = paint_can_diameter / max_distance    # Minimum distance between antennas based on paint can size

'''
u_v_space
This function calculates the u-v coverage for a given set of antennas.
In interferometry, the u-v plane represents spatial frequency coverage based on antenna separations.
Inputs:
    antennas: A 2D NumPy array of shape (n_antennas, 2), where each row represents the (x, y) coordinates of an antenna.
Outputs:
    u, v: Two lists representing the u and v coordinates in the u-v plane.
'''

def u_v_space(antennas):
    print("Calculating u-v space based on antenna configuration...")

    u, v = [], []                       # Initialize lists for u and v coordinates in the u-v plane
    num_antennas = len(antennas)

    for i in range(len(antennas)):
        x1, y1 = antennas[i][0], antennas[i][1]         # Coordinates of the first antenna in the pair
        for j in range(i+1, len(antennas)):
            x2, y2 = antennas[j][0], antennas[j][1]     # Coordinates of the second antenna in the pair
            u.append((x1 - x2))         # Calculate u as the difference in x-coordinates
            v.append((y1 - y2))         # Calculate v as the difference in y-coordinates

    print(f"u-v space calculated for {num_antennas} antennas.")
    return u, v                         # Return lists of u and v values

'''
plot_uv
This function plots the u-v space for a given antenna configuration.
It visualizes the spatial frequency coverage of the antenna array.
Inputs:
    u: A list of u coordinates (spatial frequencies along the x-axis).
    v: A list of v coordinates (spatial frequencies along the y-axis).
    save: Boolean flag to decide if the plot should be saved to a file (default: False).
    filename: The name of the file to save the plot if save is True (default: False).
Outputs:
    None (Displays the plot and optionally saves it to a file).
'''


def plot_uv(u, v, save=False, filename=False):
    print("Plotting u-v space...")

    # Create a square plot to visualize the u-v coverage
    plt.figure(figsize=(3, 3))

    # Plot each u-v point as a scatter plot
    for i in range(len(u)):
        plt.scatter(u[i]*scale_factor, v[i]*scale_factor, color='k', zorder=5)      # Scale points and plot in black

    # Set aspect ratio and axis labels
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')

    plt.title('uv plane')           # Title of the plot
    plt.xlabel(r'$u$ [m]')          # Label for the u-axis (in meters)
    plt.ylabel(r'$v$ [m]')          # Label for the v-axis (in meters)

    # Set x and y ticks for better visibility
    plt.xticks(np.arange(-4, 4, 1))
    plt.yticks(np.arange(-4, 4, 1))

    # Set limits for the x and y axes
    plt.xlim(-scale_factor, scale_factor)
    plt.ylim(-scale_factor, scale_factor)

    # Display a grid for visual reference
    plt.grid(True)

    # Optionally save the plot to a file if the save flag is set
    if save:
        plt.savefig(filename, bbox_inches='tight')

    plt.show()
    print("u-v space plotting completed.")