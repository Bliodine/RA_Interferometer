import numpy as np
import matplotlib.pyplot as plt
import scipy.fft as sp
from scipy.signal import correlate as correlate
from stationprocessing import fir_filter_coefficients, channelize_ppf_contiguous_block

end = 35_000_000

IQ0_full = np.fromfile("THUR_TEST/A0", dtype="complex64")[:end]
IQ1_full = np.fromfile("THUR_TEST/airspy0", dtype="complex64")[:end]

channels = 512
taps = 16
sample_rate = 2.5e6

fir = fir_filter_coefficients(channels, taps)

freq = [1420 - 1.25, 1420 + 1.25]
x = np.linspace(freq[0], freq[1], channels)

for offset in np.arange(-50, 50, 1, dtype='int'):
    IQ0 = IQ0_full[:]
    IQ1 = IQ1_full[749823 + offset:]
    
    #### changing length to a multiple of channels
    len0 = (len(IQ0)//channels) * channels
    len1 = (len(IQ1)//channels) * channels
    shortest = np.min((len0, len1))
    
    IQ0 = IQ0[:shortest]
    IQ1 = IQ1[:shortest]
    
    time_len = len(IQ0) / sample_rate
    print(len(IQ0), time_len) 
    
    #### reshaping into channels
    IQ0 = IQ0.reshape((-1, channels))
    IQ1 = IQ1.reshape((-1, channels)) 
    
    #### the actual FFT
    IQ0 = channelize_ppf_contiguous_block(IQ0, fir)
    IQ1 = channelize_ppf_contiguous_block(IQ1, fir)
    
    #### crosscorrelation, both phase and abs
    cross_ang = np.angle(IQ0 * np.conj(IQ1))
    cross_abs = np.abs(IQ0 * np.conj(IQ1))

    ext = [freq[0], freq[1], 0, time_len]
    asp = IQ0.shape[0] / time_len * (freq[1] - freq[0]) / channels / 256 *4
    
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)#, figsize=(7, 9))\
    p1 = ax1.imshow(cross_ang, aspect=asp, vmin=-np.pi, vmax=np.pi, cmap='seismic', extent=ext, origin='lower', interpolation='none')
    p2 = ax2.imshow(cross_abs, aspect=asp, extent=ext, vmax = 2 * np.mean(cross_abs), origin='lower')
    plt.colorbar(p1, ax=ax1)
    plt.colorbar(p2, ax=ax2)
    ax1.set_xlabel("Frequency (MHz)")
    ax2.set_xlabel("Frequency (MHz)")
    ax1.set_ylabel("Time (s)")
    ax1.set_title("Phase")
    ax2.set_title("Magnitude")
    plt.suptitle("Offset: -1345 + "+str(offset)+"\nPhase and magnitude of the crosscorrelation\nof the shifted resistor observation")
    plt.tight_layout()
    plt.savefig("plots/IntrLap_"+str(offset)+".png", dpi=150, bbox_inches='tight')
    plt.show()
    
    #### summed
    # fig, (ax1, ax2) = plt.subplots(1, 2)
    # ax1.plot(x, cross_ang.mean(axis=0))
    # ax2.plot(x, cross_abs.mean(axis=0))
    # ax1.set_xlabel("Frequency (MHz)")
    # ax2.set_xlabel("Frequency (MHz)")
    # ax1.set_ylabel("Phase")
    # ax2.set_ylabel("Magnitude")
    # ax1.set_title("Phase")
    # ax2.set_title("Magnitude")
    # ax1.tick_params(rotation=30)
    # ax2.tick_params(rotation=30)
    # plt.suptitle("Offset: -1345 + "+str(offset)+"\nMean phase and magnitude of the crosscorrelation\nof the shifted resistor observation")
    # plt.tight_layout()
    # #plt.savefig("plots/sum_"+str(offset)+".png", dpi=200)
    # plt.show()