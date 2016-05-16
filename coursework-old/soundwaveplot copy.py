import matplotlib.pyplot as plt
import numpy as np
import wave
import scipy.fftpack

soundwave = wave.open('sawtooth.wav')
signal = soundwave.readframes(-1)
signal = np.fromstring(signal, 'Int16')

#If Stereo
if soundwave.getnchannels() == 2:
    print 'Just mono files'


# Number of samplepoints
N = 600
# sample spacing
T = 1.0 / 800.0
x = np.linspace(0.0, N*T, N)
yf = scipy.fftpack.fft(signal)
xf = np.linspace(0.0, 1.0/(2.0*T), N/2)

fig, ax = plt.subplots()
ax.plot(xf, 2.0/N * np.abs(yf[0:N/2]))

# print signal

# thefile = open('textdata.txt', 'w')
# for x in signal:
#   print >> thefile, x
plt.grid()
# plt.plot(signal)
plt.show()