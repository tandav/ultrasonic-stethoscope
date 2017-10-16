import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('classic')
from math import sin
import numpy as np
from scipy.fftpack import fft
from scipy.io import wavfile
from scipy.signal import welch, cwt, morlet
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

f_psd, Pxx_den = welch(y, fs, nperseg=n)
Pxx_den = 20 * np.log10(np.abs(Pxx_den)**2)


fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 9))

# signal
ax1.plot(t, y, 'b')
# ax[0].plot(t[::100], y[::100], 'b')
ax1.set_xlabel('Time: {0}seconds'.format(record_time))
ax1.set_ylabel('Amplitude')
ax1.grid()

# spectrum and PSD
ax2.semilogx(f, a,'r')
ax2.semilogx(f_psd, Pxx_den,'k')
ax2.set_xlabel('Freq (Hz)')
ax2.set_ylabel('Magnitude')
# ax[1].set_xlim([1,4e4])
ax2.grid()

# spectrogram
ax3.specgram(y, Fs=fs, NFFT=1024*40)
ax3.set_ylim([1,1e3])
# ax[2].set_yscale('log')
ax4.set_title('Spectrogram')


# wavelet
w_low = 1
w_high = 10
widths = np.arange(w_low, w_high)
cwtmatr = cwt(y, morlet, widths)
ax4.imshow(cwtmatr, extent=[-1, 1, w_high, w_low], aspect='auto', vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())
ax4.set_title('Wavelet Transform: Morlet [{0}, {1}]'.format(w_low, w_high))

plt.tight_layout()
# plt.show()
plt.savefig(data_dir + fileprefix + fileindex + '.png')
# os.system(data_dir + fileprefix + fileindex + '.png')

