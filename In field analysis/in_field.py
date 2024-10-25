'''This script is used to test the correlation of two cantennas in the field.'''

#imports 
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import argparse
import astropy.units as u  
import os
import glob

def hdfig(subplots_def=None, scale=0.5):
    fig = plt.figure(figsize=(8, 4.5), dpi=scale * 1920 / 8)
    if subplots_def is None:
        return fig
    else:
        return fig, fig.subplots(*subplots_def)

def digitize(real_sequence: np.ndarray, nrbits: int = 8):
    result = np.rint(real_sequence).astype(int)
    maxpos = 2 ** (nrbits - 1) - 1
    maxneg = -(2 ** (nrbits - 1))
    result[result < maxneg] = maxneg
    result[result > maxpos] = maxpos
    return result

def simple_real_cross_power(ant_1_voltage, ant_2_voltage, nrbits: int = 4):
    s1 = digitize(ant_1_voltage, nrbits=nrbits)
    s2 = digitize(ant_2_voltage, nrbits=nrbits)
    return sp.signal.correlate(s1, s2, mode='same') / s1.shape[0]

def plot_real_xc(xc: np.ndarray, width: int, sample_interval, caption=None):
    fig, ax = hdfig((1, 1))
    m = xc.shape[0] // 2
    lw = width // 2
    hw = width - lw
    delay = np.arange(-lw, hw) * sample_interval
    ax.plot(delay, xc[m - lw: m + hw])
    ax.set_xlabel(f'Delay [{sample_interval.unit}]')
    if caption:
        ax.set_title(caption)
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Calculating correlation as an in-field test",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("folder", type=str, help="Folder with all files")
    parser.add_argument("-w", '--window', type=int, help="Window of correlation plot")
    args = parser.parse_args()
    
    config = vars(args)
    
    measurement_path = os.path.join(os.path.dirname(__file__), config['folder'])
    files = glob.glob(os.path.join(measurement_path, '*')) 
    data = np.concatenate([np.fromfile(file, dtype=np.float64) for file in files])

    # Sample interval calculation
    delta_freq = 10e6 
    sample_interval = (1 / (2 * delta_freq)).to(u.s)

    # Set the window for the plot
    if config['window'] is None:
        w = 100000
    else:
        w = config['window']

    # Correlation coefficient calculation
    for i in data:
        for j in data:
            # perform the cross-correlation
            corrcoeff = np.corrcoef(i, j)[0, 1]
            cross = simple_real_cross_power(i * 10, j * 10, nrbits=4)
            print(f"The cross-correlation coefficient of entry {i+1} and {j+1} is: {np.real(corrcoeff):.3f}")
            plot_real_xc(cross, w, sample_interval, caption=f"Cross-correlation of entry {i+1} and {j+1}")

if __name__ == "__main__":
    main()

