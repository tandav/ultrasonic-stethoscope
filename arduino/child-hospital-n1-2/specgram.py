import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('classic')
from math import sin
import numpy as np
from scipy.fftpack import fft
import os




y = np.fromfile('14-yo/lungs-LE-12.dat', dtype=np.float32)

record_time = y[0]
rate = y[1]
print('record_time: ', record_time, 'rate: ', rate)

y = y[2:]
n = len(y) # length of the signal


t = np.linspace(0, record_time, n) # time vector

f = np.fft.rfftfreq(n - 1, d=1./rate)
a = fft(y)[:n//2] # fft + chose only real part
a = np.abs(a / n) # normalisation

print('len(t):\t\t'   , len(t)  )
print('len(signal):\t', len(y)  )
print('len(frq):\t'   , len(f))
print('len(fft):\t'   , len(a)  )

fig, ax = plt.subplots(1, 1)



ax.specgram(y, Fs=rate, NFFT=1024*64)
ax.set_ylim([1,1e3])
ax.set_yscale('log')

# ax[1].set_ylim([1e-6,1e-3])

# if not os.path.exists(data_dir + '/images'):
    # os.makedirs(data_dir + '/images')

# plt.savefig(data_dir + 'images/' + fileprefix + fileindex + '.png', dpi=100)
plt.show()
