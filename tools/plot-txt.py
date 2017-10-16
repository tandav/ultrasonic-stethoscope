import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('classic')
from math import sin
import numpy as np
from scipy.fftpack import fft
import os

data_dir = 'child-hospital-n1/'
fileprefix = 'fio-disease-'
fileindex = '0'

y = np.loadtxt(data_dir + fileprefix + fileindex + '.txt')

# y = np.fromfile('signal.dat', dtype=np.float32)

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

fig, ax = plt.subplots(2, 1)
ax[0].plot(t, y, 'b')
# ax[0].plot(t[::100], y[::100], 'b')
ax[0].set_xlabel('Time')
# ax[1].set_xlim([0,t])
ax[0].set_ylabel('Amplitude')
ax[0].grid()

# ax[1].plot(frq, abs(Y),'r') # plotting the spectrum

# right = len(frq) // 16
# step = 1


# ax[1].loglog(f[:right:step], a[:right:step],'r') # plotting the spectrum
ax[1].loglog(f, a,'r') # plotting the spectrum
ax[1].set_xlabel('Freq (Hz)')
ax[1].set_ylabel('|Y(freq)|')
ax[1].set_xlim([1,4e4])
ax[1].grid()

# ax[1].set_ylim([1e-6,1e-3])

if not os.path.exists(data_dir + '/images'):
    os.makedirs(data_dir + '/images')

plt.savefig(data_dir + 'images/' + fileprefix + fileindex + '.png', dpi=100)
plt.show()
