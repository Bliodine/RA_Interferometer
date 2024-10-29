import numpy
import scipy.fftpack as fft
import scipy.signal as signal

def fir_filter_coefficients(num_chan, num_taps, cal_factor=1./50.0):
    raw_coefficients = signal.firwin((num_taps)*num_chan, 1/(num_chan), width=0.5/(num_chan))
    auto_fftshift = raw_coefficients*(-1)**numpy.arange(num_taps*num_chan)
    coefficients = numpy.array(auto_fftshift*(num_chan**0.5), dtype=numpy.float32)
    coefficients *= cal_factor
    return coefficients.reshape((num_taps, num_chan))

def channelize_ppf(timeseries_taps, fir_coefficients):
    return (fft.fft((timeseries_taps*fir_coefficients).sum(axis=0)))

def channelize_ppf_contiguous_block(timeseries_taps, fir_coefficients):
    num_taps, num_chan = fir_coefficients.shape
    num_ts_blocks = timeseries_taps.shape[0]
    num_spectra = num_ts_blocks -(num_taps-1)
    output_spectra = numpy.zeros((num_spectra, num_chan),dtype=numpy.complex64)
    for sp in range(num_spectra):
        output_spectra[sp,:] += channelize_ppf(timeseries_taps[sp:sp+num_taps,:],fir_coefficients)
    return output_spectra
