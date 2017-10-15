import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('classic')
from math import sin
import numpy as np
from scipy.fftpack import fft
from scipy.io import wavfile
from scipy.signal import welch
import os

data_dir = 'data-temp/'
fileprefix = 'lungs-'
fileindex = '2'

fs, y = wavfile.read(data_dir + fileprefix + fileindex + '.wav')

n = len(y) # length of the signal
record_time = n / fs

t = np.linspace(0, record_time, n) # time vector

f = np.fft.rfftfreq(n - 1, d=1./fs)
a = fft(y)[:n//2] # fft + chose only real part
a = np.abs(a / n) # normalisation
a = 20 * np.log10(a)

fig, ax = plt.subplots(3, 1)
ax[0].plot(t, y, 'b')
# ax[0].plot(t[::100], y[::100], 'b')
ax[0].set_xlabel('Time: {0}seconds'.format(record_time))
ax[0].set_ylabel('Amplitude')
ax[0].grid()


ax[1].semilogx(f, a,'r') # plotting the spectrum
ax[1].set_xlabel('Freq (Hz)')
ax[1].set_ylabel('Magnitude')
# ax[1].set_xlim([1,4e4])
ax[1].grid()


f_psd, Pxx_den = welch(y, fs, nperseg=n)
Pxx_den = 20*np.log10(np.abs(Pxx_den)**2)

ax[1].semilogx(f_psd, Pxx_den,'k') # plotting the spectrum


# spectrogram
ax[2].specgram(y, Fs=fs, NFFT=1024*40)
ax[2].set_ylim([1,1e3])
# ax[2].set_yscale('log')

plt.show()


# ================================================

# y = np.fromfile(data_dir + fileprefix + fileindex + '.dat', dtype=np.float32)

# record_time = y[0]
# rate = y[1]
# print('record_time: ', record_time, 'rate: ', rate)

# y = y[2:]
# n = len(y) # length of the signal


# t = np.linspace(0, record_time, n) # time vector

# f = np.fft.rfftfreq(n - 1, d=1./rate)
# a = fft(y)[:n//2] # fft + chose only real part
# a = np.abs(a / n) # normalisation

# print('len(t):\t\t'   , len(t)  )
# print('len(signal):\t', len(y)  )
# print('len(frq):\t'   , len(f))
# print('len(fft):\t'   , len(a)  )

# fig, ax = plt.subplots(1, 1)
# ax[0].plot(t, y, 'b')
# # ax[0].plot(t[::100], y[::100], 'b')
# ax[0].set_xlabel('Time')
# # ax[1].set_xlim([0,t])
# ax[0].set_ylabel('Amplitude')
# ax[0].grid()

# # ax[1].plot(frq, abs(Y),'r') # plotting the spectrum

# # right = len(frq) // 16
# # step = 1


# # ax[1].loglog(f[:right:step], a[:right:step],'r') # plotting the spectrum
# ax[1].loglog(f, a,'r') # plotting the spectrum
# ax[1].set_xlabel('Freq (Hz)')
# ax[1].set_ylabel('|Y(freq)|')
# ax[1].set_xlim([1,4e4])
# ax[1].grid()

# # ax[1].set_ylim([1e-6,1e-3])

# if not os.path.exists(data_dir + '/images'):
#     os.makedirs(data_dir + '/images')

# plt.savefig(data_dir + 'images/' + fileprefix + fileindex + '.png', dpi=100)
