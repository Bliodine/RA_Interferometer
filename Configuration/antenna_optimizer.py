# This script is meant to allow for manual testing and checking different antenna layouts,
# making use of an interactive drag and drop window.
# It calls other scripts, that will display the uv coverage and point spread function

# import all the necessary modules
import os
import numpy as np
import tkinter as tk
from astropy import units as unit
import matplotlib.pyplot as plt
from Array import plot_locations            # Import real-plane plotting function
from UV import u_v_space, plot_uv           # Import UV calculation and plotting functions
from tkinter import Canvas, Button, ttk, Spinbox
from PSF import make_image, plot_psf        # Import PSF calculation and plotting functions
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

# Constants
num_antennas = 9
antenna_labels = [f'A{i+1}' for i in range(num_antennas)]
grid_size = 2                                      # Define size of the ground in meters (10x10m)
export_count = 0                                   # Counter for exported CSV files

# Create a list to store the positions of antennas in the grid, now centered around (0, 0)
antenna_positions = np.random.uniform(-grid_size / 2, grid_size / 2, size=(num_antennas, 2))

# Initialize the Tkinter GUI window
root = tk.Tk()
root.title("Antenna Configuration Optimizer")

# Create a frame to organize the canvas and control elements side by side
main_frame = tk.Frame(root)
main_frame.pack()

# Set up Canvas for antenna positioning
canvas_width = 600
canvas_height = 600
canvas_frame = tk.Frame(main_frame)
canvas_frame.pack(side=tk.LEFT)

canvas = Canvas(canvas_frame, width=canvas_width, height=canvas_height)
canvas.pack()

# Function to convert real-world coordinates (centered at 0, 0) to canvas coordinates
def real_to_canvas(x, y):
    screen_x = canvas_width // 2 + int(x / grid_size * canvas_width)
    screen_y = canvas_height // 2 - int(y / grid_size * canvas_height)  # Invert y for canvas
    return screen_x, screen_y

# Create grid on the canvas with axis labels in meters (centered at 0, 0)
grid_spacing = 0.5  # 0.5 meter grid line spacing for readability
for i in range(0, canvas_width, int((canvas_width / grid_size) * grid_spacing)):
    canvas.create_line([(i, 0), (i, canvas_height)], fill='gray', tags='grid_line')
    # Move x-axis labels to the bottom
    canvas.create_text(i, canvas_height - 10, text=f'{(i - canvas_width // 2) / canvas_width * grid_size:.1f} m')

# Adjust y-axis labels and move them to the right side to avoid cropping
for i in range(0, canvas_height, int((canvas_height / grid_size) * grid_spacing)):
    canvas.create_line([(0, i), (canvas_width, i)], fill='gray', tags='grid_line')
    canvas.create_text(canvas_width - 10, i, text=f'{(canvas_height // 2 - i) / canvas_height * grid_size:.1f} m',
                       anchor=tk.E)

# Label each antenna in the dot itself (center origin)
antenna_items = []
for i in range(num_antennas):
    x, y = antenna_positions[i]
    screen_x, screen_y = real_to_canvas(x, y)
    antenna_item = canvas.create_oval(screen_x - 10, screen_y - 10, screen_x + 10, screen_y + 10, fill='blue',
                                      tags=f'antenna_{i}')
    antenna_label = canvas.create_text(screen_x, screen_y, text=antenna_labels[i], fill='white')
    antenna_items.append((antenna_item, antenna_label))

# Add X and Y axis labels
canvas.create_text(canvas_width / 2, canvas_height - 30, text='X Position (m)', font=('Arial', 12))
canvas.create_text(canvas_width - 30, canvas_height / 2, text='Y Position (m)', font=('Arial', 12), angle=90)

# Frame for antenna selection and spinbox controls (on the right side of the grid)
control_frame = tk.Frame(main_frame)
control_frame.pack(side=tk.RIGHT, padx=20)

# Dropdown and input fields for antenna selection and position input
selected_antenna = tk.StringVar(control_frame)
selected_antenna.set(antenna_labels[0])             # Set default antenna

# Antenna selection dropdown menu
antenna_menu = ttk.Combobox(control_frame, textvariable=selected_antenna, values=antenna_labels)
antenna_menu.pack(pady=5)

# X and Y coordinate inputs with spinbox for up/down adjustments
x_label = tk.Label(control_frame, text='X Position (m):')
x_label.pack()
x_spinbox = Spinbox(control_frame, from_=-grid_size/2, to=grid_size/2, increment=0.05)
x_spinbox.pack()

y_label = tk.Label(control_frame, text="Y Position (m):")
y_label.pack()
y_spinbox = Spinbox(control_frame, from_=-grid_size/2, to=grid_size/2, increment=0.05)
y_spinbox.pack()

# Function to update the spinboxes based on the selected antenna's position
def update_spinboxes(*args):
    antenna_index = antenna_labels.index(selected_antenna.get())
    x, y = antenna_positions[antenna_index]

    # Update spinbox values to reflect the selected antenna's current position
    x_spinbox.delete(0, 'end')
    x_spinbox.insert(0, str(x))

    y_spinbox.delete(0, 'end')
    y_spinbox.insert(0, str(y))

# Function to update the selected antenna's position based on input fields
def update_antenna_position(*args):
    antenna_index = antenna_labels.index(selected_antenna.get())
    x = float(x_spinbox.get())
    y = float(y_spinbox.get())

    # Update antenna position
    screen_x, screen_y = real_to_canvas(x, y)
    canvas.coords(antenna_items[antenna_index][0], screen_x - 10, screen_y - 10, screen_x + 10, screen_y + 10)
    canvas.coords(antenna_items[antenna_index][1], screen_x, screen_y)  # Move label as well

    # Store updated positions in the antenna_positions array
    antenna_positions[antenna_index] = [x, y]
    print('Updated {} to X: {}, Y: {}'.format(selected_antenna.get(), x, y))

# Bind the antenna dropdown to update the spinboxes with current antenna positions
antenna_menu.bind('<<ComboboxSelected>>', update_spinboxes)

# Update antenna position in real-time as spinbox values change
x_spinbox.bind("<KeyRelease>", update_antenna_position)
x_spinbox.bind("<ButtonRelease-1>", update_antenna_position)
y_spinbox.bind("<KeyRelease>", update_antenna_position)
y_spinbox.bind("<ButtonRelease-1>", update_antenna_position)

# Compass to indicate North
def add_compass():
    canvas.create_line(550, 100, 550, 50, arrow=tk.LAST, width=2)
    canvas.create_text(550, 40, text='N', font=('Arial, 12'))

add_compass()

# Export position to a CSV file
def export_positions():
    global export_count
    export_count += 1
    filename = f'antenna_positions_{export_count}.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Antenna', 'X (m)', 'Y (m)'])
        for i, pos in enumerate(antenna_positions):
            writer.writerow([antenna_labels[i], pos[0], pos[1]])
    print(f"Antenna positions exported to '{filename}'.")

# Button to export antenna positions to CSV
export_button = Button(control_frame, text="Export Positions", command=export_positions)
export_button.pack(pady=10)

# Load antenna positions from a CSV file
def load_preset(preset_file):
    global antenna_positions
    with open(preset_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)            # Skip header
        for i, row in enumerate(reader):
            antenna_positions[i] = [float(row[1]), float(row[2])]

    # Update the canvas positions
    for i in range(num_antennas):
        x, y = antenna_positions[i]
        screen_x, screen_y = real_to_canvas(x, y)
        canvas.coords(antenna_items[i][0], screen_x -10, screen_y -10, screen_x +10, screen_y +10)
        canvas.coords(antenna_items[i][1], screen_x, screen_y)              # Move label as well
        print(f"Loaded preset from '{preset_file}'.")

# Preset loading dropdown menu
preset_files = [f'presets/{f}' for f in os.listdir('presets') if f.endswith('.csv')]
selected_preset = tk.StringVar(root)
selected_preset.set(preset_files[0])            # Set default preset

preset_menu = ttk.Combobox(control_frame, textvariable=selected_preset, values=preset_files)
preset_menu.pack(pady=5)

# Button to load the selected preset
load_preset_button = Button(control_frame, text='Load Preset', command=lambda: load_preset(selected_preset.get()))
load_preset_button.pack(pady=10)

# Function to generate and apply a random configuration
def randomize_configuration():
    global antenna_positions
    min_distance = 0.185                # Minimum allowable distance between antennas

    # Repeatedly generate random positions until they meet the distance constraint
    valid_positions = False
    while not valid_positions:
        # Generate random positions within grid boundaries
        antenna_positions = np.round(np.random.uniform(-grid_size/2, grid_size/2, size=(num_antennas, 2)), 2)

        # Check all pairwise distances to ensure they exceed the minimum distance
        valid_positions = True
        for i in range(num_antennas):
            for j in range(i+1, num_antennas):
                distance = np.linalg.norm(antenna_positions[i] - antenna_positions[j])
                if distance < min_distance:
                    valid_positions = False
                    break
            if not valid_positions:
                break

    # Update the canvas positions
    for i in range(num_antennas):
        x, y = antenna_positions[i]
        screen_x, screen_y = real_to_canvas(x, y)
        canvas.coords(antenna_items[i][0], screen_x - 10, screen_y - 10, screen_x + 10, screen_y + 10)
        canvas.coords(antenna_items[i][1], screen_x, screen_y)  # Move label as well

    # Update spinbox values for the currently selected antenna
    update_spinboxes()

# Add the 'Randomize Configuration' button to the control frame
randomize_button = Button(control_frame, text='Randomize Array', command=randomize_configuration)
randomize_button.pack(pady=10)

# Function to calculate baseline lengths and plot them as a histogram
def plot_baseline_distribution(antenna_positions):
    baselines = []
    num_antennas = len(antenna_positions)
    for i in range(num_antennas):
        for j in range(i + 1, num_antennas):
            distance = np.linalg.norm(antenna_positions[i] - antenna_positions[j])
            baselines.append(distance)

    return baselines

# Function to calculate average PSF lobes over horizontal, vertical, and diagonal lines
def psf_lobes(psf, num_pix):
    # Define l/m coordinate arrays
    l_coords = np.linspace(-2, 2, num_pix)  # Coordinate array along l-axis
    m_coords = np.linspace(-2, 2, num_pix)  # Coordinate array along m-axis

    # Extract middle cross-sections (horizontal, vertical, and both diagonals)
    y_middle = psf[:, num_pix // 2]                      # Horizontal cross-section (m=0)
    x_middle = psf[num_pix // 2, :]                      # Vertical cross-section (l=0)
    diag_main = np.diagonal(psf)                         # Diagonal from top-left to bottom-right
    diag_secondary = np.diagonal(np.fliplr(psf))         # Diagonal from top-right to bottom-left

    # Calculate the average cross-section intensity
    mean_cross_section = (y_middle + x_middle + diag_main + diag_secondary) / 4

    return l_coords, mean_cross_section

# Function to create a nice image of the psf
def hdfig(subplots_def=None, scale=0.5, figsize=(8, 4.5)):
    fig = plt.figure(figsize=figsize, dpi=scale * 1920 /8)
    if subplots_def is None:
        return fig
    else:
        return fig, fig.subplots(*subplots_def)

# Function to export antenna positions and plot UV and PSF in a single embedded window
def export_and_plot():
    # Export positions
    print("Antenna positions (in meters):")
    print(antenna_positions)

    # Calculate UV coverage and PSF
    u, v = u_v_space(antenna_positions)
    uv = np.array(list(zip(u, v)))  # Combine u and v into an Nx2 array for processing

    print(uv)

    # Clear existing axes before re-plotting
    ax[0].cla()
    ax[1].cla()
    ax[2].cla()
    ax[3].cla()

    baselines = plot_baseline_distribution(antenna_positions)

    # Plot the histogram of baseline lengths on the provided axis
    ax[0].hist(baselines, bins=10, color='skyblue', edgecolor='black')
    ax[0].set_title(f'Baseline Distribution (Total {len(baselines)})')
    ax[0].set_xlabel('Baseline Length (m)')
    ax[0].set_ylabel('Frequency')
    ax[0].set_xlim(0, 3)
    ax[0].grid(True)
    ax[0].set_aspect('equal')

    # Plot the UV coverage in the first subplot
    ax[1].scatter(u, v, color='blue')
    ax[1].set_title('UV coverage')
    ax[1].set_xlabel('u (m)')
    ax[1].set_ylabel('v (m)')
    ax[1].grid(True)
    ax[1].set_aspect('equal')

    # Calculate and plot the PSF in the second subplot
    freq = 1.42 * unit.GHz
    num_pix = 256               # Pixels for the psf image
    psf, psf_extent = make_image(np.ones((num_antennas, num_antennas)), num_pix, uv, freq)

    '''
    fig, ax_psf = hdfig((1, 1))
    ax_psf.imshow(psf, origin='lower', extent=psf_extent)
    plt.show()
    '''
    psf_img = ax[2].imshow(psf, extent=psf_extent, origin='lower', cmap='viridis')
    #ax[1].imshow(psf, extent=psf_extent, origin='lower', cmap='viridis')
    ax[2].set_title('Point Spread Function (PSF)')
    ax[2].set_xlabel('l (rad)')
    ax[2].set_ylabel('m (rad)')
    ax[2].set_aspect('equal')

    # Plot lobe structure of the PSF
    x_cs, y_cs = psf_lobes(psf, num_pix)
    ax[3].plot(x_cs, y_cs, c='k')
    ax[3].set_title('Central lobe')
    ax[3].set_xlabel('l (rad)')
    ax[3].set_ylabel('Intensity')
    ax[3].set_xlim(x_cs[0], x_cs[-1])

    ax[3].axhline(y=0.25, c='r', linestyle='dashed')
    ax[3].set_aspect('equal')

    canvas_plot.draw()

# Button to trigger the export and plot functionality
plot_button = Button(control_frame, text='Plot UV & PSF', command=export_and_plot)
plot_button.pack()

# Set the figure size and resolution scaling for the plots
scale = 0.5

# Create a canvas for matplotlib figure embedding and plotting window using matplotlib (embedded in Tkinter)
fig, ax = plt.subplots(1, 4, figsize=(16, 4.5), dpi=scale * 1920 /8)       # 1row, 2 columns: UV plane and PSF side-by-side
canvas_plot = FigureCanvasTkAgg(fig, master=root)
canvas_plot.get_tk_widget().pack()

# Start the GUI event loop
root.mainloop()