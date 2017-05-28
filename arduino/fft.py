import matplotlib.pyplot as plt
from math import sin
import numpy as np

# Fs = 1500.0  # sampling rate
# Ts = 1.0 / Fs; # sampling interval
# t = np.arange(0, 10, Ts) # time vector

# ff = 5;   # frequency of the signal
# # y = np.sin(2*np.pi*ff*t)
# y = sum([1/i*np.sin(i*np.pi*ff*t) for i in range(1, 100)])

# n = len(y) # length of the signal
# k = np.arange(n)
# T = n / Fs
# frq = k / T # two sides frequency range
# frq = frq[range(n // 2)] # one side frequency range

# Y = np.fft.fft(y) / n # fft computing and normalization
# Y = Y[range(n // 2)]

# fig, ax = plt.subplots(2, 1)
# ax[0].plot(t, y)
# ax[0].set_xlabel('Time')
# ax[0].set_ylabel('Amplitude')
# ax[1].plot(frq, abs(Y),'r') # plotting the spectrum
# ax[1].set_xlabel('Freq (Hz)')
# ax[1].set_ylabel('|Y(freq)|')

# y = np.fromfile('signal.dat', dtype=np.float32)[::]

# t = 37
# i = t*10000
# j = i + 20000
y = np.fromfile('signal.dat', dtype=np.float32)
print ('len of signal:', len(y))
# print (y[-4], y[-3], y[-2], y[-1])
y = y[::100]
plt.plot(y)
plt.show()
