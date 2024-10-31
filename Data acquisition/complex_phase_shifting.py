import numpy as np
import matplotlib.pyplot as plt
import scipy.fft as sp

end = 10_000_000
channels = 512
sample_rate = 2.5e6
central_freq = 1.42e9

IQ0_full = np.fromfile("THUR_TEST/A0", dtype="complex64")[:end]
IQ1_full = np.fromfile("THUR_TEST/airspy0", dtype="complex64")[:end]

freq = [1420 - 1.25, 1420 + 1.25]
x = np.linspace(freq[0], freq[1], channels)

for delay in np.linspace(-2e-07, 2e-07, 5001):
    IQ0 = IQ0_full
    IQ1 = IQ1_full[749823:]
    
    #### changing length to a multiple of channels
    len0 = (len(IQ0)//channels) * channels
    len1 = (len(IQ1)//channels) * channels
    shortest = np.min((len0, len1))
    
    #d = np.linspace(0, delay, shortest)
    phase_rot = np.exp(-np.pi * 2j * sample_rate * delay)
    
    IQ0 = IQ0[:shortest]  * phase_rot
    IQ1 = IQ1[:shortest]
    
    l = len(IQ0) / channels
    time_len = len(IQ0) / sample_rate
    
    #### reshaping into channels
    # w =  np.blackman(channels).astype('float32')
    IQ0 = (IQ0.reshape((-1, channels))).astype('complex64')
    IQ1 = (IQ1.reshape((-1, channels))).astype('complex64') 
    
    #### the actual FFT
    IQ0 = sp.fftshift(sp.fft2(IQ0)) / l
    IQ1 = sp.fftshift(sp.fft2(IQ1)) / l 

    cross_ang = np.angle(IQ0 * np.conj(IQ1))   
    s = round(delay * 1e10, 2)    
    
    ext = [freq[0], freq[1], 0, time_len]
    asp = IQ0.shape[0] / time_len * (freq[1] - freq[0]) / channels / 256 * 32 * 2.5
    
    fig, (ax1, ax2) = plt.subplots(1, 2)#, figsize=(7, 9))\
    p1 = ax1.imshow(cross_ang, aspect=asp, vmin=-np.pi, vmax=np.pi, cmap='seismic', extent=ext, origin='lower')#, interpolation='none')
    ax2.plot(x, cross_ang.mean(axis=0))
    plt.colorbar(p1, ax=ax1)
    ax1.set_xlabel("Frequency (MHz)")
    ax2.set_xlabel("Frequency (MHz)")
    ax1.set_ylabel("Time (s)")
    ax1.set_title("Phase")
    ax2.set_title("Mean phase")
    ax1.tick_params(rotation=30)
    ax2.tick_params(rotation=30)
    ax1.axvline(1419.25, color='red', ls='--')
    ax1.axvline(1420.7, color='red', ls='--')
    ax2.axvline(1419.25, color='red', ls='--')
    ax2.axvline(1420.7, color='red', ls='--')
    plt.suptitle("Sub-Offset: "+str(s)+"\nPhase of the crosscorrelation\nof the shifted resistor observation")
    plt.tight_layout()
    #plt.savefig("plots/tiny_region/phase_around_"+str(s)+".png", dpi=200)
    plt.show()



