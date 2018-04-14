import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft
from scipy import signal
from scipy.io import wavfile
from scipy.signal import decimate


data_dir = 'data-temp/'
fileprefix = 'lungs-'
fileindex = '2'

fs, y = wavfile.read(data_dir + fileprefix + fileindex + '.wav')

# y = decimate(y, 4)


n = len(y) # length of the signal
record_time = n / fs

t = np.linspace(0, record_time, n) # time vector

# f = np.fft.rfftfreq(n - 1, d=1./fs)
# a = fft(y)[:n//2] # fft + chose only real part
# a = np.abs(a / n) # normalisation
# a = 20 * np.log10(a)


# widths = np.arange(1, 31)
widths = np.arange(1, 20)
cwtmatr = signal.cwt(y, signal.morlet, widths)
# plt.imshow(cwtmatr, extent=[-1, 1, 31, 1], cmap='PRGn', aspect='auto',
plt.imshow(cwtmatr, extent=[-1, 1, 31, 1], aspect='auto',
           vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())

# plt.show()
plt.savefig('wavelet.png')
