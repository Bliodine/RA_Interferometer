'''This script is used to test the correlation of two cantennas in the field.'''

#imports 
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import argparse
import astropy.units as u  

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
    parser.add_argument("file1", type=str, help="Name of file 1")
    parser.add_argument("file2", type=str, help="Name of file 2")
    parser.add_argument("-w", '--window', type=int, help="Window of correlation plot")
    args = parser.parse_args()
    
    config = vars(args)
    file1 = np.fromfile(config['file1'], dtype=np.complex64)[:3000000]
    file2 = np.fromfile(config['file2'], dtype=np.complex64)[:3000000]

    # Sample interval calculation
    delta_freq = 1e6  # Replace with actual delta frequency value
    sample_interval = (1 / (2 * delta_freq)).to(u.s)

    # Set the window for the plot
    if config['window'] is None:
        w = 100000
    else:
        w = config['window']

    # Correlation coefficient calculation
    corrcoeff = np.corrcoef(file1, file2)[0, 1]
    cross = simple_real_cross_power(file1 * 10, file2 * 10, nrbits=4)

    print(f"The cross-correlation coefficient of the data is: {np.real(corrcoeff):.3f}")
    
    # Plotting the cross-correlation
    plot_real_xc(cross, w, sample_interval)

if __name__ == "__main__":
    main()

