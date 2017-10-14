import numpy as np
import matplotlib.pyplot as plt

intel = np.loadtxt('idp.txt') * 1000
default = np.loadtxt('default.txt') * 1000

NFFT_arr = np.arange(2**11, 2**17, 1024)

diff = default - intel

plt.plot(NFFT_arr, intel, 'b')
plt.plot(NFFT_arr, default, 'r')
plt.plot(NFFT_arr, diff, 'g')
plt.xlabel('FFT size, ms')
plt.ylabel('time, ms')
plt.grid()
# plt.show()
plt.savefig('1.png')
