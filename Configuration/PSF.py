# This script calculates the point-spread function (PSF) of a given antenna configuration

# Import necessary Python packages and modules for calculations and plotting
from scipy import constants as const        # Import physical constants
import matplotlib.pyplot as plt             # Plotting package for visualizations
from astropy import units as u              # Astropy's units for handling physical units and constants
import numpy as np                          # NumPy for array manipulation and numerical operations
from tqdm import tqdm                                 # TQDM for progress bars during calculations

# Set desired font style for matplotlib plots
plt.rcParams.update({"font.family": 'serif'})                 # Use serif fonts


'''
pixel_brightness_faster
This function calculates the brightness of a given pixel in the PSF.
Inputs:
    acm_single_pol: The antenna correlation matrix (ACM) for a single polarization (2D NumPy array)
    l: l-coordinate (direction cosines along the X-axis of the sky plane in radians)
    m: m-coordinate (direction cosines along the Y-axis of the sky plane in radians)
    uv: UV coordinates (baseline coordinates between pairs of antennas in meters)
    frequency: Observation frequency (in Hz)
    
Outputs:
    brightness/num_vis: Average brightness of the pixel (float)
'''

def pixel_brightness_faster(acm_single_pol, l, m, uv, frequency):
    # Status update
    # print(f"Calculating pixel brightness for pixel with l={l} and m={m}...")

    # Convert antenna correlation matrix to complex 64-bit values
    a = acm_single_pol.astype(np.complex64)

    # Convert frequency to Hz
    f = frequency.to(u.Hz).value

    # Convert UV coordinates to meters and scale by frequency and the speed of light
    uv_l = uv * f/const.c

    brightness = 0.0            # Initialize brightness accumulator
    num_vis = 0                 # Count of visibility measurements

    # Convert l and m coordinates to radians (for sky pixel directions)
    ll = l.to(u.rad).value.astype(np.float32)
    mm = m.to(u.rad).value.astype(np.float32)

    # Loop over pairs of antennas (2D array now)
    for idx, (u_val, v_val) in enumerate(uv_l):
        brightness += (a[idx // acm_single_pol.shape[0], idx % acm_single_pol.shape[0]] *
                       np.exp(2j * np.pi * (u_val * ll + v_val * mm))).real
        num_vis += 1

    # Return average brightness per visibility
    return brightness/num_vis

'''
make_image
This function generates the PSF image based on the input antenna configuration and UV coordinates.
Inputs:
    acm: The antenna correlation matrix (ACM), a square 2D NumPy array representing visibility measurements
    num_pix: Number of pixels in each dimension of the image (square image of size num_pix x num_pix)
    uv: UV coordinates (baseline coordinates between antenna pairs)
    frequency: Observation frequency (in Hz)
    l_range: Range of l-coordinates to generate the image (default: -1 to 1)
    m_range: Range of m-coordinates to generate the image (default: -1 to 1)
Outputs:
    img: Generated PSF image (2D NumPy array)
    img_extent: Coordinate extent of the image, used for plotting (tuple of 4 values)
'''


def make_image(acm, num_pix, uv, frequency, l_range=(1.0, -1.0), m_range=(-1.0, 1.0)):
    # Status update
    print(f"Generating PSF image with {num_pix}x{num_pix} pixels...")

    # Initialize an empty image array with dimensions num_pix x num_pix
    img = np.zeros((num_pix, num_pix), dtype=np.float32)

    # Create l and m coordinates (direction cosines) with given range
    l_coor = np.linspace(*l_range, num_pix)*u.rad
    m_coor = np.linspace(*m_range, num_pix)*u.rad

    # Loop through each pixel coordinate (l, m) to compute brightness
    for m_ix, m in enumerate(tqdm(m_coor)):         # tqdm for progress bar
        for l_ix, l in enumerate(l_coor):
            # Calculate pixel brightness using the pixel_brightness_faster function
            img[m_ix, l_ix] = pixel_brightness_faster(acm, l, m, uv, frequency)

    # Calculate pixel separation for the extent of the image in l and m
    pixel_sep = m_coor[1] - m_coor[0]
    half = pixel_sep.to(u.rad).value/2.0

    # Define image extent for correct axis scaling in the plot
    img_extent = (l_coor[0].to(u.rad).value + half, m_coor[0].to(u.rad).value - half,
                  l_coor[-1].to(u.rad).value - half, m_coor[-1].to(u.rad).value + half)

    # Status update
    print("PSF image generation complete.")
    return img, img_extent


'''
subband_frequency
This function calculates the frequency of a chosen subband in a radio interferometer.
Inputs:
    subband_number: The index of the subband (integer, typically between 0 and 512)
    clock_frequency: The clock frequency of the system (default: 200 MHz)
Outputs:
    sb_freq: The frequency of the subband in Hz (Astropy quantity with units)
'''

def subband_frequency(subband_number, clock_frequency=200*u.MHz):
    # Status update
    print(f"Calculating frequency for subband {subband_number}...")

    # Calculate subband frequency based on the given clock frequency
    sb_freq = (subband_number/512) * clock_frequency/2

    return sb_freq

'''
calc_npix
This function calculates the number of pixels needed to oversample the FWHM resolution
of the instrument by at least a factor of 2.5.
Inputs:
    None
Outputs:
    num_pix: Number of pixels required for the PSF image (rounded)
'''

def calc_npix():
    # Status update
    print("Calculating the number of pixels required for PSF image...")

    over_sampling = 2.5         # Oversampling factor

    # Calculate the pixel separation using the speed of light, frequency, and antenna separation
    pixel_separation = (const.c*u.m/u.s/subband_frequency(290)/(80*u.m)).to(u.dimensionless_unscaled)/over_sampling

    # Calculate the number of pixels for the PSF
    num_pix = 2.0 / pixel_separation

    # Status update
    print(f"Number of pixels calculated: {np.round(num_pix, 0)}")

    # Return rounded number of pixels
    return np.round(num_pix, 0)

'''
plot_psf
This function plots the generated PSF image using matplotlib's imshow function.
Inputs:
    psf: The 2D PSF image to be plotted (NumPy array)
    psf_extent: The extent of the PSF image (for correct axis scaling)
Outputs:
    None (The image is plotted and saved to a file)
'''

def plot_psf(psf, psf_extent):
    # Status update
    print("Plotting PSF image...")

    # Set the figure size and resolution for the PSF plot
    scale = 0.5

    fig, ax = plt.subplots((1, 1), figsize=(8, 4.5), dpi=scale * 1920/8)

    # Plot the PSF image with appropriate extent and scaling
    ax.imshow(psf, origin='lower', extent=psf_extent)
    plt.show()

    # Save the plot as 'psf.png'
    plt.savefig(f'psf.png', bbox_inches='tight')
    # Status update
    print("PSF image saved as 'psf.png'.")

# Main script execution


# Define the number of antennas in the array
n_ant = 9


# Calculate the number of pixels needed for oversampling the PSF
num_pix = calc_npix()

# Define the central observation frequency (1.42 GHz for hydrogen line observations)
# freq = 1.42*u.GHz

# Generate the PSF image using the make_image function
# psf, psf_extent = make_image(np.ones_like((n_ant, n_ant)), num_pix, uv*u.m, freq)

# Plot the PSF using the plot_psf function
# plot_psf(psf, psf_extent)

# Status update
print("PSF calculation and plotting completed.")
