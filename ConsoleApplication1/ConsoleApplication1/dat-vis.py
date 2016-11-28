import numpy as np
import matplotlib.pyplot as plt
myarray = np.fromfile('adc001.dat',dtype=int)
plt.plot(myarray)
plt.show()
print(myarray)

# gcc-4.2 -std=c99 -fopenmp FFT_parallel.c && ./a.out
