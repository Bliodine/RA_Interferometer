# RA_Interferometer
For sharing code for the interferometer project of Radio Astronomy 2024

For a tutorial on using git: https://people.irisa.fr/Anthony.Baire/git/git-for-beginners-handout.pdf

There are also good videos on YouTube available :)



Antenna Configuration Optimizer

A graphical interface for designing and testing antenna configurations for a 9-antenna interferometer. The tool allows for interactive adjustments to antenna positions, visualization of UV coverage, and PSF calculation.

Features:

Antenna Positioning Grid:

  Visual grid (2.5m x 2.5m) with axes centered at (0, 0).
  Precise coordinate entry for antenna positions.
  
Control Panel Options:

  Antenna Selection: Dropdown to select an antenna and update its coordinates.
  Preset Loading: Load configurations (circle, Y, etc.) from a dropdown.
  Randomize Configuration: Automatically set random positions for all antennas.
  Export Positions: Save the current configuration as antenna_positions_#.csv, where # auto-increments to avoid overwriting.

Visualization:

  UV Coverage Plot: Generates a UV plane plot for the selected configuration.
  PSF Plot: Displays the Point Spread Function based on current positions.

Usage Instructions:

  1. Setup: Install dependencies (numpy, matplotlib, astropy, tkinter, tqdm).
  2. Running: Run the script antenna_optimizer.py to open the GUI.
  3. Configuring Antennas: Use the dropdown and spinboxes for custom setups, load presets, or generate random configurations.
  4. Plotting: Click Export & Plot to visualize UV and PSF plots in real time.
