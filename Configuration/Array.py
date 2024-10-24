# This script handles everything regarding the positions of the antennas in an array.
# This includes calculating distances between antennas, plotting configurations, and saving plots if needed.

# Importing all the necessary modules and packages
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# Set desired font style for matplotlib plots
plt.rcParams.update({"font.family": 'serif'})                 # Use serif fonts

# Define system-specific variables
paint_can_diameter = 0.183          # Paint can diameter in meters (represents the size of the antennas)
max_distance = 5/np.sqrt(2)         # Maximum distance between antennas (based on array configuration)
scale_factor = max_distance         # Scale factor for plotting, based on maximum separation
min_distance = paint_can_diameter / max_distance  # Minimum allowable distance between antennas based on size


'''
calc_dist
This function calculates the pairwise distances between antennas.
It returns an array of distances between each pair of antennas, calculated based on their (x, y) coordinates.
Inputs:
    antennas: A 2D NumPy array of shape (n_antennas, 2), where each row represents the (x, y) coordinates of an antenna.
Outputs:
    dist: A 1D NumPy array containing the distances between every pair of antennas.
'''

def calc_dist(antennas):
    print("Calculating distances between antennas...")

    dist = []           # Initialize an empty list to store distances
    num_antennas = len(antennas)

    # Loop over each pair of antennas
    for i in range(num_antennas):
        x1, y1 = antennas[i][0], antennas[i][1]             # Coordinates of the first antenna in the pair
        for j in range(i+1, len(antennas)):
            x2, y2 = antennas[j][0], antennas[j][1]         # Coordinates of the second antenna in the pair
            # Calculate the Euclidean distance between the two antennas and append to the list
            dist.append(np.sqrt((x1-x2)**2 + (y1 - y2)**2))

    print(f"Distance calculation complete for {num_antennas} antennas.")

    # Return the distances as a NumPy array
    return np.array(dist)


'''
plot_locations
This function plots the locations of the antennas in the array based on their (x, y) coordinates.
Inputs:
    antennas: A 2D NumPy array of shape (n_antennas, 2), where each row represents the (x, y) coordinates of an antenna.
    save: Boolean flag to save the plot to a file (default: False).
    filename: The name of the file to save the plot if save is True (default: False).
Outputs:
    None (Displays the plot and optionally saves it to a file).
'''

def plot_locations(antennas, save=False, filename=False):
    print("Plotting antenna locations...")

    # Create a square figure for plotting the antenna locations
    plt.figure(figsize=(3, 3))
    x = np.linspace(0, 1, 10)

    # Plot each antenna's location as a scatter point
    for antenna in antennas:
        plt.scatter(antenna[0]*scale_factor, antenna[1]*scale_factor, color='k', zorder=5)

    # Set aspect ratio and axis labels
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    plt.title('Antenna locations')              # Title of the plot
    plt.xlabel(r'$x$ [m]')                      # Label for the x-axis (in meters)
    plt.ylabel(r'$y$ [m]')                      # Label for the y-axis (in meters)

    # Set ticks and grid for better visualization
    plt.xticks(np.arange(0, 3.5, 0.5))
    plt.yticks(np.arange(0, 3.5, 0.5))

    # Set limits for the x and y axes based on the scale factor
    plt.xlim(0, scale_factor)
    plt.ylim(0, scale_factor)

    plt.grid(True)          # Show gridlines

    # Optionally save the plot to a file if the save flag is set
    if save:
        plt.savefig(filename, bbox_inches='tight')
        print(f"Antenna location plot saved as '{filename}.png'.")

    # Display the plot
    plt.show()

    print("Antenna location plotting completed.")
    return


