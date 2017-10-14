from scipy.fftpack import fft
import matplotlib.pyplot as plt
import numpy as np
import time

NFFT_max = 100000
# for NFFT in range(1, step):

# step = 1000
# NFFT = np.arange(1, NFFT_max + 1, step)
# FFT_time = np.zeros(NFFT_max // step)


# for i, nfft_i in enumerate(NFFT):
#     y = np.random.rand(nfft_i)
#     t0 = time.time()
#     a = fft(y)
#     t1 = time.time()
#     FFT_time[i] = t1 - t0
#     # if i % step == 0:
#     print(nfft_i, t1 - t0)

# plt.plot(NFFT, FFT_time)
# plt.show()


NFFT = 100000

y = np.random.rand(NFFT)
t0 = time.time()
a = fft(y)
t1 = time.time()
print(t1 - t0)



# TODO
# 1. fft only
# 2. fft + other calcs in updateplot()
