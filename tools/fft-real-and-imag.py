import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('classic')
from math import sin
import numpy as np
from scipy.fftpack import fft
from scipy.io import wavfile
from scipy.signal import welch, cwt, morlet, periodogram
import os


import scipy
import scipy.fftpack
import pylab
from scipy import pi

data_dir = 'data-temp/'
fileprefix = 'heart-oldmic-low-'
fileindex = '3'

fs, y = wavfile.read(data_dir + fileprefix + fileindex + '.wav')
n = len(y) # length of the signal
record_time = n / fs

t = np.linspace(0, record_time, n) # time vector

signal = y

FFT = abs(scipy.fft(signal))
freqs = scipy.fftpack.fftfreq(signal.size, t[1]-t[0])

A = 20*scipy.log10(FFT)[:n//2]
B = -20*scipy.log10(FFT)[n//2:]

# print(np.allclose(A, B))
print(A - B)


plt.subplot(211)
plt.plot(t, signal)
plt.subplot(212)
plt.plot(freqs, 20*scipy.log10(FFT), 'r')
plt.show()



# print('opening file')





# t = np.linspace(0, record_time, n) # time vector
# print('processing FFT')

# f = np.fft.fftfreq(n, d=1./fs)
# # a = fft(y)[:n//2] # fft + chose only real part
# a = fft(y) # fft + chose only real part
# ac = a
# a = np.abs(a / n) # normalisation
# a = 20 * np.log10(a)


# fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 9))

# # signal
# ax1.plot(t, y, 'b')
# # ax[0].plot(t[::100], y[::100], 'b')
# ax1.set_xlabel('Time: {0}seconds'.format(record_time))
# ax1.set_ylabel('Amplitude')
# ax1.grid()

# # spectrum and PSD
# ax2.semilogx(f, a,'r')
# ax2.set_xlabel('Frequency, Hz')
# ax2.set_ylabel('Magnitude')
# ax2.grid()


# # spectrum and PSD
# ax3.semilogx(f, ac,'r')
# ax3.set_xlabel('')
# ax3.set_ylabel('')
# ax3.grid()


# plt.tight_layout()
# # plt.show()
# # plt.savefig(data_dir + fileprefix + fileindex + '.png')
# plt.savefig(fileprefix + fileindex + '.png')
# os.system('open ' + fileprefix + fileindex + '.png')
