from scipy.fftpack import fft
from time import time
import numpy as np
# import matplotlib.pyplot as plt

iterations = 10


img_array = np.zeros((1024, 1024)) # rename to (plot_width, plot_height)

NFFT_arr = np.arange(2**11, 2**17, 1024)
times = np.zeros(len(NFFT_arr))
print(len(NFFT_arr))
for k, NFFT in enumerate(NFFT_arr):
    avg_t = 0
    for i in range(iterations):
        t0 = time()
        y = np.random.rand(NFFT)
        
        a = (fft(y * np.hanning(NFFT)) / NFFT)[:NFFT//2] # fft + chose only real part
        rate = 44100
        f = np.fft.rfftfreq(NFFT - 1, d=1./rate)

        try:
            a = np.abs(a) # magnitude
            # a = np.log(a) # часто ошибка - сделать try, else
            a = 20 * np.log10(a) # часто ошибка - сделать try, else
        except Exception as e:
            print('log(0) error', e)


        # spectrogram
        img_array = np.roll(img_array, -1, 0)
        img_array[-1] = a[:1024]

        t1 = time()
        avg_t += t1 - t0
    avg_t /= iterations
    times[k] = avg_t
    print(k, avg_t)

# np.savetxt('intel.txt', times)
np.savetxt('idp.txt', times)

# plt.plot(times)
# plt.show()
