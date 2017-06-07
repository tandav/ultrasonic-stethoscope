import matplotlib.pyplot as plt
from math import sin
import numpy as np



y = np.fromfile('signal.dat', dtype=np.float32)

record_time = y[-2]
rate = y[-1]
print('record_time: ', record_time, 'rate: ', rate)

y = y[:-2]
n = len(y) # length of the signal


t = np.linspace(0, record_time, n) # time vector

# ff = 5;   # frequency of the signal
# # y = np.sin(2*np.pi*ff*t)

k = np.arange(n)
T = n / rate
frq = k / T # two sides frequency range
frq = frq[range(n // 2 + 1)] # one side frequency range

Y = np.fft.fft(y) / n # fft computing and normalization
Y = Y[range(n // 2 + 1)]

print('len(t):\t\t'   , len(t)  )
print('len(signal):\t', len(y)  )
print('len(frq):\t'   , len(frq))
print('len(fft):\t'   , len(Y)  )

fig, ax = plt.subplots(2, 1)
# ax[0].plot(t, y)
ax[0].plot(t[::100], y[::100])
ax[0].set_xlabel('Time')
# ax[1].set_xlim([0,t])
ax[0].set_ylabel('Amplitude')
# ax[1].plot(frq, abs(Y),'r') # plotting the spectrum

right = len(frq) // 16
step = 1

ax[1].loglog(frq[:right:step], abs(Y)[:right:step],'r') # plotting the spectrum
ax[1].set_xlabel('Freq (Hz)')
ax[1].set_ylabel('|Y(freq)|')
ax[1].set_xlim([1,1e4])
ax[1].set_ylim([1e-6,1e-3])

plt.show()
